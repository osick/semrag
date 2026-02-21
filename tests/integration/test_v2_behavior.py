import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from src.semrag.api.openai_wrapper import app, graph
from src.semrag.ingestion.loaders.multi_source_ingestor import MultiSourceIngestor

class TestSEMRAGv2Behavior:
    """
    TDD Chicago Style Behavioral Test for SEMRAG v2 Features.
    """

    @pytest.fixture
    def client(self):
        return TestClient(app)

    @pytest.fixture
    def mock_graph(self):
        mock = MagicMock()
        mock.run.return_value = {"answer": "This is a SEMRAG response."}
        return mock

    @pytest.fixture
    def mock_ingestion_engine(self):
        return MagicMock()

    @patch("src.semrag.api.openai_wrapper.get_graph")
    def test_openai_compatible_chat_completion(self, mock_get_graph, client, mock_graph):
        """
        Behavior: The API should respond to OpenAI-compatible chat requests.
        """
        mock_get_graph.return_value = mock_graph
        
        # Given: An OpenAI-style chat completion request
        request_data = {
            "model": "semrag-v2",
            "messages": [{"role": "user", "content": "Tell me about Apple."}],
            "stream": False
        }
        
        # When: The request is sent to the API
        response = client.post("/v1/chat/completions", json=request_data)
        
        # Then: The response should follow the OpenAI format
        assert response.status_code == 200
        data = response.json()
        assert data["object"] == "chat.completion"
        assert data["choices"][0]["message"]["content"] == "This is a SEMRAG response."
        
    @patch("fsspec.core.url_to_fs")
    def test_multi_source_ingestion_scans_recursive(self, mock_url_to_fs, mock_ingestion_engine):
        """
        Behavior: The MultiSourceIngestor should recursively scan directories using fsspec.
        """
        # Mock fsspec filesystem
        mock_fs = MagicMock()
        mock_fs.isdir.side_effect = lambda path: path == "s3://bucket/data"
        mock_fs.find.return_value = ["s3://bucket/data/doc1.pdf", "s3://bucket/data/doc2.docx"]
        mock_url_to_fs.return_value = (mock_fs, "s3://bucket/data")
        
        # Given: A MultiSourceIngestor
        ingestor = MultiSourceIngestor(ingestion_engine=mock_ingestion_engine)
        
        # When: Ingesting an S3 directory
        with patch.object(MultiSourceIngestor, "_ingest_single_file") as mock_ingest_single:
            ingestor.ingest_url("s3://bucket/data")
        
        # Then: It should find and ingest the files recursively
        mock_fs.find.assert_called_once_with("s3://bucket/data")
        assert mock_ingest_single.call_count == 2
