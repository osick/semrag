import pytest
from unittest.mock import MagicMock, patch
from semrag.graph_store.ontology.loader import OntologyLoader
from semrag.orchestration.graph import SEMRAGGraph

class TestSEMRAGv3Behavior:
    """
    TDD Chicago Style Behavioral Test for SEMRAG v3 (Ontologies & Metadata).
    """

    @pytest.fixture
    def mock_graph_store(self):
        return MagicMock()

    @pytest.fixture
    def mock_vector_store(self):
        return MagicMock()

    @pytest.fixture
    def mock_llm(self):
        return MagicMock()

    @pytest.fixture
    def mock_embedding_model(self):
        return MagicMock()

    @patch("rdflib.Graph.parse")
    def test_ontology_loading_populates_schema(self, mock_rdf_parse, mock_graph_store):
        """
        Behavior: Loading an ontology file should populate the graph store with class hierarchies.
        """
        loader = OntologyLoader(graph_store=mock_graph_store)
        
        # Mock internal graph to return at least one class
        from rdflib import URIRef
        loader._rdf_graph.subjects = MagicMock(return_value=[URIRef("http://example.org/Contract")])
        loader._rdf_graph.subject_objects = MagicMock(return_value=[])
        
        # When: An ontology file is loaded
        loader.load_ontology("enterprise_rules.ttl", format="turtle", namespace="Legal")
        
        # Then: Graph store was updated
        assert mock_graph_store.add_triples.called

    def test_hybrid_retrieval_with_metadata_filter(self, mock_vector_store, mock_graph_store, mock_llm, mock_embedding_model):
        """
        Behavior: Hybrid retrieval should use metadata filters (namespace) to refine context.
        """
        # Mock graph query with metadata filtering
        mock_graph_store.query.return_value = [{
            "n.name": "Contract_A", "type(r)": "GOVERNED_BY", "m.name": "Rule_X", 
            "r.provenance": "policy.ttl", "r.confidence": 1.0
        }]
        
        # Given: A SEMRAGGraph v3
        graph = SEMRAGGraph(
            vector_store=mock_vector_store,
            graph_store=mock_graph_store,
            llm=mock_llm,
            embedding_model=mock_embedding_model
        )
        
        # When: A query is run with a specific namespace filter
        query = "What rules govern Contract_A?"
        result = graph.run(query, namespace_filter="Legal")

        # Then: Graph store was queried with metadata-aware Cypher
        cypher_call = mock_graph_store.query.call_args[0][0]
        assert "WHERE r.namespace = $namespace" in cypher_call
        assert mock_graph_store.query.call_args[0][1]["namespace"] == "Legal"
        
        # And: The context includes metadata provenance
        assert "Source: policy.ttl" in result["context"]
        assert "Confidence: 1.0" in result["context"]
