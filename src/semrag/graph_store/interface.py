from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple

class IGraphStore(ABC):
    """
    Interface for Graph Database Adapters.
    Designed to be compatible with Cypher-based query engines.
    """
    
    @abstractmethod
    def query(self, cypher_query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Execute a Cypher query and return the results as a list of dictionaries."""
        pass

    @abstractmethod
    def add_triples(self, triples: List[Tuple[str, str, str]]) -> None:
        """
        Add (subject, predicate, object) triples to the graph.
        This handles the node creation and edge establishing logic.
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """Wipe the graph for testing or reset purposes."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the database connection."""
        pass
