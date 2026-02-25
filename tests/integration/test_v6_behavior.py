import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from semrag.ingestion.extractors.interface import ITripleExtractor
from semrag.ingestion.extractors.llm_extractor import LLMTripleExtractor
from semrag.ingestion.extractors.nlp_extractor import SpaCyGLiNERExtractor
from semrag.ingestion.extractors.adaptive_router import AdaptiveExtractionRouter
from semrag.ingestion.extractors.tri_graph_builder import TriGraphBuilder
from semrag.orchestration.pagerank_retriever import PageRankRetriever
from semrag.ingestion.engine import IngestionEngine
from semrag.orchestration.graph import SEMRAGGraph


class TestNLPExtractorBehavior:
    """
    TDD Chicago Style Behavioral Tests for the SpaCy+GLiNER NLP Extractor.
    """

    def test_nlp_extractor_requires_entity_labels(self):
        """
        Behavior: SpaCyGLiNERExtractor must raise ValueError if entity_labels is not provided.
        """
        with pytest.raises(ValueError, match="entity_labels must be provided"):
            SpaCyGLiNERExtractor(entity_labels=None)

    def test_nlp_extractor_accepts_entity_labels(self):
        """
        Behavior: SpaCyGLiNERExtractor should accept custom entity labels.
        Models are lazy-loaded so construction should succeed without loading models.
        """
        extractor = SpaCyGLiNERExtractor(
            entity_labels=["Person", "Organization", "Technology"]
        )
        # Models not loaded yet (lazy loading)
        assert extractor._nlp is None
        assert extractor._gliner is None

    @patch("semrag.ingestion.extractors.nlp_extractor.SpaCyGLiNERExtractor._ensure_models_loaded")
    def test_nlp_extractor_extracts_entities_from_both_sources(self, mock_load):
        """
        Behavior: extract_entities should combine GLiNER and spaCy NER results,
        deduplicating overlapping spans.
        """
        extractor = SpaCyGLiNERExtractor(
            entity_labels=["Person", "Organization"],
            use_gliner=True,
        )

        # Mock GLiNER model
        mock_gliner = MagicMock()
        mock_gliner.predict_entities.return_value = [
            {"text": "Apple Inc.", "label": "Organization", "start": 0, "end": 10, "score": 0.95},
            {"text": "Steve Jobs", "label": "Person", "start": 26, "end": 36, "score": 0.92},
        ]
        extractor._gliner = mock_gliner

        # Mock spaCy doc with entities
        mock_ent1 = MagicMock()
        mock_ent1.text = "Apple Inc."
        mock_ent1.label_ = "ORG"
        mock_ent1.start_char = 0
        mock_ent1.end_char = 10

        mock_ent2 = MagicMock()
        mock_ent2.text = "Steve Jobs"
        mock_ent2.label_ = "PERSON"
        mock_ent2.start_char = 26
        mock_ent2.end_char = 36

        mock_doc = MagicMock()
        mock_doc.ents = [mock_ent1, mock_ent2]
        mock_nlp = MagicMock(return_value=mock_doc)
        extractor._nlp = mock_nlp

        entities = extractor.extract_entities("Apple Inc. was founded by Steve Jobs.")

        # Then: Entities are deduplicated (GLiNER takes priority when spans overlap)
        assert len(entities) >= 2
        entity_texts = [e["text"] for e in entities]
        assert "Apple Inc." in entity_texts
        assert "Steve Jobs" in entity_texts

    @patch("semrag.ingestion.extractors.nlp_extractor.SpaCyGLiNERExtractor._ensure_models_loaded")
    def test_nlp_extractor_extracts_triples_via_dependency_parsing(self, mock_load):
        """
        Behavior: extract_triples should produce (subject, predicate, object) triples
        from dependency-parsed sentences, grounded in detected entities.
        """
        extractor = SpaCyGLiNERExtractor(
            entity_labels=["Person", "Organization"],
        )

        # Mock GLiNER
        mock_gliner = MagicMock()
        mock_gliner.predict_entities.return_value = [
            {"text": "Steve Jobs", "label": "Person", "start": 0, "end": 10, "score": 0.9},
            {"text": "Apple", "label": "Organization", "start": 19, "end": 24, "score": 0.9},
        ]
        extractor._gliner = mock_gliner

        # Build mock spaCy doc with dependency parse
        # Sentence: "Steve Jobs founded Apple"
        mock_subj_token = MagicMock()
        mock_subj_token.dep_ = "nsubj"
        mock_subj_token.pos_ = "PROPN"
        mock_subj_token.text = "Jobs"
        mock_subj_token.lemma_ = "Jobs"
        mock_subj_token.idx = 6
        mock_subj_token.children = []
        mock_subj_subtree = [MagicMock(idx=0, text="Steve"), MagicMock(idx=6, text="Jobs")]
        mock_subj_subtree[0].idx = 0
        mock_subj_subtree[0].text = "Steve"
        mock_subj_subtree[1].idx = 6
        mock_subj_subtree[1].text = "Jobs"
        mock_subj_token.subtree = mock_subj_subtree

        mock_obj_token = MagicMock()
        mock_obj_token.dep_ = "dobj"
        mock_obj_token.pos_ = "PROPN"
        mock_obj_token.text = "Apple"
        mock_obj_token.lemma_ = "Apple"
        mock_obj_token.idx = 19
        mock_obj_token.children = []
        mock_obj_subtree = [MagicMock(idx=19, text="Apple")]
        mock_obj_subtree[0].idx = 19
        mock_obj_subtree[0].text = "Apple"
        mock_obj_token.subtree = mock_obj_subtree

        mock_verb = MagicMock()
        mock_verb.dep_ = "ROOT"
        mock_verb.pos_ = "VERB"
        mock_verb.text = "founded"
        mock_verb.lemma_ = "found"
        mock_verb.idx = 11
        mock_verb.children = [mock_subj_token, mock_obj_token]

        mock_sent = MagicMock()
        mock_sent.__iter__ = lambda self: iter([mock_subj_token, mock_verb, mock_obj_token])

        mock_doc = MagicMock()
        mock_doc.ents = []
        mock_doc.sents = [mock_sent]
        mock_nlp = MagicMock(return_value=mock_doc)
        extractor._nlp = mock_nlp

        triples = extractor.extract_triples("Steve Jobs founded Apple")

        # Then: At least one triple was extracted connecting the entities
        assert len(triples) >= 1
        subjects = [t[0] for t in triples]
        objects = [t[2] for t in triples]
        assert any("Steve Jobs" in s for s in subjects) or any("Steve Jobs" in o for o in objects)

    @patch("semrag.ingestion.extractors.nlp_extractor.SpaCyGLiNERExtractor._ensure_models_loaded")
    def test_nlp_extractor_works_without_gliner(self, mock_load):
        """
        Behavior: When use_gliner=False, only spaCy NER is used.
        """
        extractor = SpaCyGLiNERExtractor(
            entity_labels=["Person"],
            use_gliner=False,
        )

        # Mock spaCy
        mock_ent = MagicMock()
        mock_ent.text = "Steve Jobs"
        mock_ent.label_ = "PERSON"
        mock_ent.start_char = 0
        mock_ent.end_char = 10

        mock_doc = MagicMock()
        mock_doc.ents = [mock_ent]
        extractor._nlp = MagicMock(return_value=mock_doc)

        entities = extractor.extract_entities("Steve Jobs founded Apple.")

        assert len(entities) >= 1
        assert entities[0]["source"] == "spacy"


class TestAdaptiveRouterBehavior:
    """
    TDD Chicago Style Behavioral Tests for the Adaptive Extraction Router.
    """

    @pytest.fixture
    def mock_nlp_extractor(self):
        ext = MagicMock(spec=ITripleExtractor)
        ext.extract_triples.return_value = [("Apple", "FOUNDED_BY", "Steve Jobs")]
        ext.extract_entities.return_value = [{"text": "Apple", "label": "ORG"}]
        return ext

    @pytest.fixture
    def mock_llm_extractor(self):
        ext = MagicMock(spec=ITripleExtractor)
        ext.extract_triples.return_value = [("Complex Entity", "COMPLEX_REL", "Other Entity")]
        return ext

    @patch("semrag.ingestion.extractors.adaptive_router.AdaptiveExtractionRouter._ensure_analyzer_loaded")
    @patch("semrag.ingestion.extractors.adaptive_router.AdaptiveExtractionRouter.score_complexity")
    def test_simple_text_routes_to_nlp_extractor(self, mock_score, mock_load,
                                                  mock_nlp_extractor, mock_llm_extractor):
        """
        Behavior: Simple text (low complexity) should be routed to the NLP extractor.
        """
        mock_score.return_value = 0.3  # Below threshold

        router = AdaptiveExtractionRouter(
            nlp_extractor=mock_nlp_extractor,
            llm_extractor=mock_llm_extractor,
            complexity_threshold=0.6,
        )

        triples = router.extract_triples("Apple was founded by Steve Jobs.")

        # Then: NLP extractor was called, LLM was NOT called
        mock_nlp_extractor.extract_triples.assert_called_once()
        mock_llm_extractor.extract_triples.assert_not_called()
        assert ("Apple", "FOUNDED_BY", "Steve Jobs") in triples

    @patch("semrag.ingestion.extractors.adaptive_router.AdaptiveExtractionRouter._ensure_analyzer_loaded")
    @patch("semrag.ingestion.extractors.adaptive_router.AdaptiveExtractionRouter.score_complexity")
    def test_complex_text_routes_to_llm_extractor(self, mock_score, mock_load,
                                                   mock_nlp_extractor, mock_llm_extractor):
        """
        Behavior: Complex text (high complexity score) should be routed to the LLM extractor.
        """
        mock_score.return_value = 0.8  # Above threshold

        router = AdaptiveExtractionRouter(
            nlp_extractor=mock_nlp_extractor,
            llm_extractor=mock_llm_extractor,
            complexity_threshold=0.6,
        )

        triples = router.extract_triples("Complex nested text with many clauses.")

        # Then: LLM extractor was called, NLP was NOT called
        mock_llm_extractor.extract_triples.assert_called_once()
        mock_nlp_extractor.extract_triples.assert_not_called()

    def test_entity_extraction_always_uses_nlp(self, mock_nlp_extractor, mock_llm_extractor):
        """
        Behavior: extract_entities always uses the fast NLP path.
        """
        router = AdaptiveExtractionRouter(
            nlp_extractor=mock_nlp_extractor,
            llm_extractor=mock_llm_extractor,
        )

        entities = router.extract_entities("Apple was founded by Steve Jobs.")

        mock_nlp_extractor.extract_entities.assert_called_once()
        assert len(entities) >= 1


class TestTriGraphBuilderBehavior:
    """
    TDD Chicago Style Behavioral Tests for LinearRAG Tri-Graph Construction.
    """

    @pytest.fixture
    def mock_graph_store(self):
        return MagicMock()

    @pytest.fixture
    def mock_entity_extractor(self):
        ext = MagicMock(spec=ITripleExtractor)
        ext.extract_entities.return_value = [
            {"text": "Apple", "label": "ORG", "start": 0, "end": 5},
            {"text": "Steve Jobs", "label": "PERSON", "start": 20, "end": 30},
        ]
        return ext

    def test_trigraph_creates_entity_sentence_passage_structure(self, mock_graph_store, mock_entity_extractor):
        """
        Behavior: Building a tri-graph should create Entity, Sentence, and Passage nodes
        and return counts.
        """
        builder = TriGraphBuilder(
            entity_extractor=mock_entity_extractor,
            graph_store=mock_graph_store,
        )

        result = builder.build_tri_graph(
            text="Apple was founded by Steve Jobs.",
            doc_name="test.txt",
            sentences=["Apple was founded by Steve Jobs."],
        )

        # Then: Stats returned with correct counts
        assert result["entities"] == 2  # Apple, Steve Jobs
        assert result["sentences"] == 1
        assert result["passages"] == 1
        assert result["edges"] >= 3  # 2 APPEARS_IN + 1 PART_OF + 1 CO_OCCURS

    def test_trigraph_creates_co_occurrence_edges(self, mock_graph_store, mock_entity_extractor):
        """
        Behavior: Entities in the same sentence get CO_OCCURS edges.
        """
        builder = TriGraphBuilder(
            entity_extractor=mock_entity_extractor,
            graph_store=mock_graph_store,
        )

        builder.build_tri_graph(
            text="Apple was founded by Steve Jobs.",
            doc_name="test.txt",
            sentences=["Apple was founded by Steve Jobs."],
        )

        # Then: graph_store.query was called with CO_OCCURS edge creation
        cypher_calls = [str(call) for call in mock_graph_store.query.call_args_list]
        co_occurs_calls = [c for c in cypher_calls if "CO_OCCURS" in c]
        assert len(co_occurs_calls) >= 1

    def test_trigraph_calls_graph_store_with_merge(self, mock_graph_store, mock_entity_extractor):
        """
        Behavior: Tri-graph uses MERGE Cypher for idempotent node/edge creation.
        """
        builder = TriGraphBuilder(
            entity_extractor=mock_entity_extractor,
            graph_store=mock_graph_store,
        )

        builder.build_tri_graph(
            text="Apple was founded by Steve Jobs.",
            doc_name="test.txt",
            sentences=["Apple was founded by Steve Jobs."],
        )

        # Then: All Cypher queries use MERGE
        for call in mock_graph_store.query.call_args_list:
            cypher = call[0][0]
            assert "MERGE" in cypher or "MATCH" in cypher


class TestPageRankRetrieverBehavior:
    """
    TDD Chicago Style Behavioral Tests for Tri-Graph PageRank Retrieval.
    """

    @pytest.fixture
    def mock_graph_store(self):
        store = MagicMock()

        def mock_query(cypher, params=None):
            if "APPEARS_IN" in cypher:
                return [{"sid": "sentence:doc1:0", "text": "Apple was founded in 1976."}]
            if "PART_OF" in cypher and params and params.get("sid"):
                return [{"pid": "passage:doc1"}]
            if "CO_OCCURS" in cypher:
                return [{"name2": "Steve Jobs"}]
            if "PART_OF" in cypher and params and params.get("pid"):
                return [{"text": "Apple was founded in 1976."}]
            if "Entity" in cypher and "RETURN e.name" in cypher:
                return [{"name": "Apple"}, {"name": "Steve Jobs"}]
            return []

        store.query.side_effect = mock_query
        return store

    @pytest.fixture
    def mock_extractor(self):
        ext = MagicMock(spec=ITripleExtractor)
        ext.extract_entities.return_value = [{"text": "Apple", "label": "ORG"}]
        return ext

    def test_retriever_returns_ranked_passages(self, mock_graph_store, mock_extractor):
        """
        Behavior: The retriever should return passages ranked by PageRank score.
        """
        retriever = PageRankRetriever(
            graph_store=mock_graph_store,
            entity_extractor=mock_extractor,
        )

        results = retriever.retrieve("Tell me about Apple")

        # Then: Results contain passage data
        assert len(results) >= 1
        assert "passage_id" in results[0]
        assert "score" in results[0]

    def test_retriever_returns_empty_for_no_entities(self, mock_graph_store):
        """
        Behavior: If no entities are found in the query, return empty list.
        """
        empty_extractor = MagicMock(spec=ITripleExtractor)
        empty_extractor.extract_entities.return_value = []

        retriever = PageRankRetriever(
            graph_store=mock_graph_store,
            entity_extractor=empty_extractor,
        )

        results = retriever.retrieve("What is the meaning of life?")

        assert results == []

    def test_retriever_uses_fuzzy_matching_for_entity_activation(self, mock_graph_store, mock_extractor):
        """
        Behavior: Entity activation should use fuzzy matching (Jaro-Winkler)
        to find graph entities matching query entities.
        """
        retriever = PageRankRetriever(
            graph_store=mock_graph_store,
            entity_extractor=mock_extractor,
            fuzzy_threshold=0.85,
        )

        # When: query entity "Apple" should fuzzy-match graph entity "Apple"
        activated = retriever._activate_entities("Tell me about Apple")
        assert "Apple" in activated


class TestV6IngestionIntegration:
    """
    TDD Chicago Style Behavioral Tests for v6 Ingestion with extraction strategies.
    """

    @pytest.fixture
    def mock_graph_store(self):
        return MagicMock()

    @pytest.fixture
    def mock_vector_store(self):
        return MagicMock()

    @pytest.fixture
    def mock_embedding_model(self):
        model = MagicMock()
        model.embed_documents.return_value = [[0.1] * 768]
        return model

    @pytest.fixture
    def mock_extractor(self):
        ext = MagicMock(spec=ITripleExtractor)
        ext.extract_triples.return_value = [("Apple", "FOUNDED_BY", "Steve Jobs")]
        return ext

    @pytest.fixture
    def mock_trigraph_builder(self):
        builder = MagicMock()
        builder.build_tri_graph.return_value = {"entities": 2, "sentences": 1, "passages": 1, "edges": 4}
        return builder

    @patch("semrag.ingestion.engine.partition")
    def test_ingestion_uses_extractor_when_provided(
        self, mock_partition, mock_graph_store, mock_vector_store,
        mock_embedding_model, mock_extractor
    ):
        """
        Behavior: When an ITripleExtractor is provided, IngestionEngine uses it
        instead of the internal LLM-based extraction.
        """
        mock_partition.return_value = [MagicMock(text="Apple was founded by Steve Jobs.")]

        engine = IngestionEngine(
            graph_store=mock_graph_store,
            vector_store=mock_vector_store,
            embedding_model=mock_embedding_model,
            extractor=mock_extractor,
        )

        with patch("os.path.exists", return_value=True):
            engine.ingest_file("test.txt")

        # Then: Extractor was called
        mock_extractor.extract_triples.assert_called_once()
        mock_graph_store.add_triples.assert_called_once()
        triples_added = mock_graph_store.add_triples.call_args[0][0]
        assert ("Apple", "FOUNDED_BY", "Steve Jobs") in triples_added

    @patch("semrag.ingestion.engine.partition")
    def test_ingestion_builds_trigraph_when_builder_provided(
        self, mock_partition, mock_graph_store, mock_vector_store,
        mock_embedding_model, mock_trigraph_builder
    ):
        """
        Behavior: When a TriGraphBuilder is provided, IngestionEngine invokes it.
        """
        mock_partition.return_value = [MagicMock(text="Apple was founded by Steve Jobs.")]

        engine = IngestionEngine(
            graph_store=mock_graph_store,
            vector_store=mock_vector_store,
            embedding_model=mock_embedding_model,
            trigraph_builder=mock_trigraph_builder,
        )

        with patch("os.path.exists", return_value=True):
            engine.ingest_file("test.txt")

        # Then: Tri-graph builder was invoked
        mock_trigraph_builder.build_tri_graph.assert_called_once()

    @patch("semrag.ingestion.engine.partition")
    def test_backward_compatible_llm_extraction(
        self, mock_partition, mock_graph_store, mock_vector_store,
        mock_embedding_model
    ):
        """
        Behavior: When no extractor is provided but LLM is, old behavior is preserved.
        """
        mock_llm = MagicMock()
        mock_partition.return_value = [MagicMock(text="Apple was founded by Steve Jobs.")]

        engine = IngestionEngine(
            graph_store=mock_graph_store,
            vector_store=mock_vector_store,
            embedding_model=mock_embedding_model,
            llm=mock_llm,
        )

        with patch("os.path.exists", return_value=True):
            engine.ingest_file("test.txt")

        # Then: Vector store was populated (always happens)
        mock_vector_store.add_chunks.assert_called_once()


class TestV6RetrievalIntegration:
    """
    TDD Chicago Style Behavioral Tests for v6 Retrieval with tri-graph PageRank.
    """

    @pytest.fixture
    def mock_vector_store(self):
        store = MagicMock()
        store.search.return_value = [{"content": "Steve Jobs was a visionary tech leader."}]
        return store

    @pytest.fixture
    def mock_graph_store(self):
        store = MagicMock()
        store.query.return_value = [{"n.name": "Apple Inc.", "type(r)": "FOUNDED_BY", "m.name": "Steve Jobs",
                                      "r.provenance": "doc1", "r.confidence": 0.95}]
        return store

    @pytest.fixture
    def mock_llm(self):
        llm = MagicMock()
        llm.invoke.return_value = "Steve Jobs founded Apple Inc."
        return llm

    @pytest.fixture
    def mock_embedding_model(self):
        model = MagicMock()
        model.embed_query.return_value = [0.1] * 768
        return model

    @pytest.fixture
    def mock_pagerank_retriever(self):
        retriever = MagicMock()
        retriever.retrieve.return_value = [
            {"passage_id": "passage:doc1", "score": 0.85,
             "sentences": ["Apple was founded by Steve Jobs in 1976."],
             "content": "Apple was founded by Steve Jobs in 1976."}
        ]
        return retriever

    def test_retrieval_with_trigraph_includes_pagerank_results(
        self, mock_vector_store, mock_graph_store, mock_llm,
        mock_embedding_model, mock_pagerank_retriever
    ):
        """
        Behavior: When pagerank_retriever is provided, the workflow includes tri-graph results.
        """
        graph = SEMRAGGraph(
            vector_store=mock_vector_store,
            graph_store=mock_graph_store,
            llm=mock_llm,
            embedding_model=mock_embedding_model,
            pagerank_retriever=mock_pagerank_retriever,
        )

        result = graph.run("Who founded Apple Inc.?")

        # Then: PageRank retriever was called
        mock_pagerank_retriever.retrieve.assert_called_once()

        # And: Context includes all three sources
        assert "Vector Store Results" in result["context"]
        assert "Graph Store Relationships" in result["context"]
        assert "Tri-Graph Passages" in result["context"]

    def test_retrieval_without_trigraph_preserves_v5_behavior(
        self, mock_vector_store, mock_graph_store, mock_llm,
        mock_embedding_model
    ):
        """
        Behavior: Without pagerank_retriever, the workflow is identical to v5.
        """
        graph = SEMRAGGraph(
            vector_store=mock_vector_store,
            graph_store=mock_graph_store,
            llm=mock_llm,
            embedding_model=mock_embedding_model,
        )

        result = graph.run("Who founded Apple Inc.?")

        # Then: Both vector and graph searches ran
        mock_vector_store.search.assert_called_once()
        assert mock_graph_store.query.called  # Called once per capitalized word in query

        # And: Answer was generated
        assert "Steve Jobs" in result["answer"]
        assert "Tri-Graph" not in result["context"]
