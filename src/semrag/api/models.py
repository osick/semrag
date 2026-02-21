from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class GraphNode(BaseModel):
    """
    Pydantic model for an enriched Graph Node.
    """
    id: str = Field(..., description="Unique identifier for the node")
    name: str = Field(..., description="Display name of the entity")
    type: str = Field("Entity", description="Type of the node (e.g., Entity, Class, Chunk)")
    uri: Optional[str] = Field(None, description="Global URI from an ontology/RDF")
    provenance: str = Field("Unknown", description="Origin of the data (Source file or Ontology)")
    confidence: float = Field(1.0, description="Confidence score of the extraction (0.0 - 1.0)")
    namespace: str = Field("Default", description="Logical domain or namespace (e.g., Legal, Engineering)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional arbitrary properties")

class GraphEdge(BaseModel):
    """
    Pydantic model for an enriched Graph Edge (Relationship).
    """
    subject: str = Field(..., description="ID of the source node")
    predicate: str = Field(..., description="Type of relationship")
    object: str = Field(..., description="ID of the target node")
    provenance: str = Field("Unknown", description="Origin of the data")
    confidence: float = Field(1.0, description="Confidence score")
    namespace: str = Field("Default", description="Logical namespace")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional properties")

class EnrichedTriple(BaseModel):
    """
    A single enriched triple for ingestion.
    """
    subject: GraphNode
    predicate: str
    object: GraphNode
    provenance: str
    namespace: str
    confidence: float = 1.0
