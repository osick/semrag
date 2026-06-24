import pytest
from unittest.mock import MagicMock
from semrag.orchestration.graph import SEMRAGGraph

class TestRetrievalBehavior:
    """
    TDD Chicago Style Behavioral Test for Hybrid Retrieval.
    Focuses on the end-to-end outcome of a query.
    """

    @pytest.fixture
    def mock_vector_store(self):
        store = MagicMock()
        # Mock finding a chunk related to Steve Jobs
        store.search.return_value = [{"content": "Steve Jobs was a visionary tech leader."}]
        return store

    @pytest.fixture
    def mock_graph_store(self):
        store = MagicMock()
        # Mock finding a relationship from the graph store
        store.query.return_value = [{
            "n.name": "Apple Inc.", "type(r)": "FOUNDED_BY", "m.name": "Steve Jobs",
            "r.provenance": "history.txt", "r.confidence": 1.0
        }]
        return store

    @pytest.fixture
    def mock_llm(self):
        llm = MagicMock()
        llm.invoke.return_value = "Steve Jobs founded Apple Inc. and was a visionary leader."
        return llm

    @pytest.fixture
    def mock_embedding_model(self):
        model = MagicMock()
        model.embed_query.return_value = [0.1] * 768
        return model

    def test_hybrid_retrieval_produces_answer(self, mock_vector_store, mock_graph_store, mock_llm, mock_embedding_model):
        """
        Behavior: A query should trigger both vector and graph searches, and the results should be used by the LLM.
        """
        # Given: A SEMRAGGraph with mocked components
        graph = SEMRAGGraph(
            vector_store=mock_vector_store,
            graph_store=mock_graph_store,
            llm=mock_llm,
            embedding_model=mock_embedding_model
        )
        
        # When: A query is executed
        query = "Who founded Apple Inc.?"
        result = graph.run(query)

        # Then: Vector search was called
        mock_vector_store.search.assert_called_once()
        
        # And: Graph store was queried
        assert mock_graph_store.query.called
        
        # And: The final answer is correct (mocked)
        assert "Steve Jobs" in result["answer"]
        assert "Apple Inc." in result["answer"]
        
        # And: The context contains both vector and graph data
        assert "Vector Store Results" in result["context"]
        assert "Graph Store Relationships" in result["context"]
