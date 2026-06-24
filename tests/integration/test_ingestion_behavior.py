import os
import pytest
from unittest.mock import MagicMock, patch
from semrag.ingestion.engine import IngestionEngine

class TestIngestionBehavior:
    """
    TDD Chicago Style Behavioral Test for Ingestion.
    Focuses on the end-to-end outcome of ingestion.
    """

    @pytest.fixture
    def mock_graph_store(self):
        return MagicMock()

    @pytest.fixture
    def mock_vector_store(self):
        return MagicMock()

    @pytest.fixture
    def mock_llm(self):
        # Mock LLM to return a JSON list of triples
        llm = MagicMock()
        # Ensure it returns something that looks like an AIMessage if needed, 
        # or just a string if the parser handles it.
        # Most LangChain parsers expect an AIMessage or a string.
        json_response = '[{"subject": "Apple Inc.", "predicate": "FOUNDED_BY", "object": "Steve Jobs"}, {"subject": "Steve Jobs", "predicate": "BORN_IN", "object": "San Francisco"}]'
        
        # We need to simulate the .content attribute or the direct return
        mock_response = MagicMock()
        mock_response.content = json_response
        llm.invoke.return_value = mock_response
        return llm

    @pytest.fixture
    def mock_embedding_model(self):
        model = MagicMock()
        model.embed_query.return_value = [0.1] * 768
        model.embed_documents.return_value = [[0.1] * 768]
        return model

    @patch("semrag.ingestion.engine.partition")
    def test_ingest_file_populates_both_stores(self, mock_partition, mock_graph_store, mock_vector_store, mock_llm, mock_embedding_model):
        """
        Behavior: Ingesting an Office file should lead to:
        1. Text extraction using 'unstructured'.
        2. Chunks being added to the Vector Store.
        3. Triples being extracted by LLM and added to the Graph Store.
        """
        # Mock unstructured partition to return sample text
        mock_partition.return_value = [MagicMock(text="Apple Inc. was founded by Steve Jobs.")]
        
        # Given: An IngestionEngine with mocked components
        engine = IngestionEngine(
            graph_store=mock_graph_store,
            vector_store=mock_vector_store,
            embedding_model=mock_embedding_model,
            llm=mock_llm
        )
        
        # When: A sample DOCX file is ingested (mocked)
        with patch("os.path.exists", return_value=True):
            with patch.object(engine, "_extract_triples_with_llm") as mock_extract:
                mock_extract.return_value = [("Apple Inc.", "FOUNDED_BY", "Steve Jobs"), ("Steve Jobs", "BORN_IN", "San Francisco")]
                engine.ingest_file("sample.docx")

        # Then: 'partition' was called with the correct file
        mock_partition.assert_called_once_with(filename="sample.docx")

        # And: Chunks were added to Vector Store
        mock_vector_store.add_chunks.assert_called_once()
        
        # And: Triples were extracted and added to Graph Store
        # (Apple Inc, FOUNDED_BY, Steve Jobs) was added
        mock_graph_store.add_triples.assert_called_once()
        
        # Verify the triples logic (simplistic extraction check)
        # Check if the extracted triples match what the mock LLM returned.
        triples_added = mock_graph_store.add_triples.call_args[0][0]
        assert ("Apple Inc.", "FOUNDED_BY", "Steve Jobs") in triples_added
        assert ("Steve Jobs", "BORN_IN", "San Francisco") in triples_added
