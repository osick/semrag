from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple, Optional
from semrag.api.models import GraphNode, GraphEdge, EnrichedTriple

class IGraphStore(ABC):
    """
    Enhanced Interface for Graph Database Adapters.
    Designed for v3 Enterprise Metadata and Ontologies.
    """
    
    @abstractmethod
    def query(self, cypher_query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Execute a Cypher query and return results."""
        pass

    @abstractmethod
    def add_enriched_triple(self, triple: EnrichedTriple) -> None:
        """
        Adds a triple with full metadata enrichment (provenance, namespace, confidence).
        """
        pass

    @abstractmethod
    def add_triples(self, triples: List[Tuple[str, str, str]], provenance: str = "Unknown", namespace: str = "Default") -> None:
        """Adds simple triples with global provenance/namespace."""
        pass

    @abstractmethod
    def query_by_metadata(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Retrieves nodes/edges filtered by metadata (e.g., namespace, provenance).
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """Wipe the graph."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close connections."""
        pass
