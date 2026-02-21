import pytest
from unittest.mock import MagicMock, patch
from semrag.graph_store.analytics.communities import CommunityDetectionEngine
from semrag.ingestion.resolution.deduplicator import EntityResolutionModule

class TestSEMRAGv4Behavior:
    """
    TDD Chicago Style Behavioral Test for SEMRAG v4 (Analytics, Resolution, MCP).
    """

    @pytest.fixture
    def mock_graph_store(self):
        return MagicMock()

    @pytest.fixture
    def mock_llm(self):
        return MagicMock()

    def test_community_detection_generates_summaries(self, mock_graph_store, mock_llm):
        """
        Behavior: The CommunityDetectionEngine should identify clusters and store summaries.
        """
        # Given: A Graph Store with triples
        mock_graph_store.get_all_triples.return_value = [
            ("A", "REL", "B"), ("B", "REL", "C"), # Community 1
            ("X", "REL", "Y"), ("Y", "REL", "Z")  # Community 2
        ]
        mock_llm.invoke.return_value = "This is a summary of the community."
        
        engine = CommunityDetectionEngine(graph_store=mock_graph_store, llm=mock_llm)
        
        # When: Global summaries are generated
        summaries = engine.generate_global_summaries()
        
        # Then: Two communities were identified (A,B,C) and (X,Y,Z)
        assert len(summaries) >= 2
        
        # And: Summaries were stored back in the graph
        assert mock_graph_store.query.called
        call_args = mock_graph_store.query.call_args[0][0]
        assert "MERGE (c:Community" in call_args

    @patch("jellyfish.jaro_winkler_similarity", return_value=0.95)
    def test_entity_resolution_merges_nodes(self, mock_fuzzy, mock_graph_store, mock_llm):
        """
        Behavior: The EntityResolutionModule should identify similar nodes and merge them.
        """
        # Given: A Graph Store with similar nodes
        mock_graph_store.query.return_value = [{"name": "Apple Inc."}, {"name": "Apple"}]
        mock_llm.invoke.return_value = "Yes" # LLM confirms they are the same
        
        resolution = EntityResolutionModule(graph_store=mock_graph_store, llm=mock_llm)
        
        # When: Resolution is run
        merges = resolution.resolve_duplicates()
        
        # Then: The nodes were merged in the store
        mock_graph_store.merge_nodes.assert_called_once_with("Apple Inc.", "Apple")
        assert ("Apple Inc.", "Apple") in merges
