import pytest
import io
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from semrag.api.openai_wrapper import app
from semrag.api import ingestion

class TestSEMRAGv5Behavior:
    """
    TDD Chicago Style Behavioral Test for SEMRAG v5 Features (FastMCP, Upload API, uv).
    """

    @pytest.fixture
    def client(self):
        return TestClient(app)

    @pytest.fixture
    def mock_ingestion_engine(self):
        return MagicMock()

    def test_push_to_ingest_upload_api(self, client, mock_ingestion_engine):
        """
        Behavior: The system should accept multipart file uploads and trigger stream-based ingestion.
        """
        # Inject mock
        ingestion.ingestion_engine = mock_ingestion_engine
        
        # Given: A fake file stream
        file_content = b"Apple Inc. was founded by Steve Jobs."
        file_name = "test.txt"
        files = {"file": (file_name, io.BytesIO(file_content), "text/plain")}
        
        # When: The file is POSTed to the upload endpoint
        response = client.post("/v1/ingest/upload", files=files)
        
        # Then: The response is successful
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        
        # And: The ingestion engine was called with the stream
        mock_ingestion_engine.ingest_stream.assert_called_once()

    @patch("semrag.mcp.server_fastmcp.graph_orchestrator")
    def test_fastmcp_tool_execution_logic(self, mock_graph):
        """
        Behavior: FastMCP tools should correctly wrap the SEMRAG orchestration logic.
        """
        from semrag.mcp.server_fastmcp import query_semrag
        
        # Given: A query and a mocked graph result
        mock_graph.run.return_value = {"answer": "Steve Jobs founded Apple."}
        
        # When: The FastMCP tool is called directly
        result = query_semrag("Who founded Apple?")
        
        # Then: It returns the expected answer
        assert result == "Steve Jobs founded Apple."
        mock_graph.run.assert_called_once()
