from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple, Optional
from semrag.api.models import GraphNode, GraphEdge, EnrichedTriple

class IGraphStore(ABC):
    """
    Enhanced Interface for Graph Database Adapters (v4).
    Includes Analytics and Resolution support.
    """
    
    @abstractmethod
    def query(self, cypher_query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def add_enriched_triple(self, triple: EnrichedTriple) -> None:
        pass

    @abstractmethod
    def merge_nodes(self, canonical_name: str, alias_name: str) -> None:
        """
        Merges two nodes by moving all edges from alias to canonical and deleting alias.
        """
        pass

    @abstractmethod
    def get_all_triples(self) -> List[Tuple[str, str, str]]:
        """Retrieves the entire graph as triples for analytics."""
        pass

    @abstractmethod
    def clear(self) -> None:
        pass

    @abstractmethod
    def close(self) -> None:
        pass
