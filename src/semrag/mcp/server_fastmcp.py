from fastmcp import FastMCP
from typing import Optional
from semrag.orchestration.graph import SEMRAGGraph
from semrag.ingestion.engine import IngestionEngine

# Initialize FastMCP
mcp = FastMCP("semrag")

# Dependencies (to be injected at runtime)
graph_orchestrator: Optional[SEMRAGGraph] = None
ingestion_engine: Optional[IngestionEngine] = None

@mcp.tool()
def query_semrag(query: str, namespace: str = "Default") -> str:
    """
    Performs a hybrid vector-graph search to answer complex queries.
    
    Args:
        query: The natural language question to ask.
        namespace: Optional metadata filter (e.g., 'Legal', 'Engineering').
    """
    if graph_orchestrator is None:
        return "Error: SEMRAG Graph not initialized"
    
    result = graph_orchestrator.run(query, namespace_filter=namespace)
    return result["answer"]

@mcp.tool()
def ingest_url(url: str) -> str:
    """
    Ingests a document from a local or remote URL (S3, HTTP, etc.) into the knowledge base.
    
    Args:
        url: The full URL or path to the document/directory.
    """
    if ingestion_engine is None:
        return "Error: Ingestion Engine not initialized"
    
    # In a real v5 implementation, we'd use the MultiSourceIngestor here
    # For now, we trigger the core engine
    try:
        # Note: This tool currently assumes a single file for simplicity in the tool signature
        ingestion_engine.ingest_file(url)
        return f"Successfully ingested: {url}"
    except Exception as e:
        return f"Ingestion failed: {str(e)}"

@mcp.resource("graph://stats")
def get_graph_stats() -> str:
    """Returns high-level statistics about the SEMRAG Knowledge Graph."""
    if graph_orchestrator is None:
        return "Graph not initialized"
    
    # Mock stats for v5 demonstration
    return "Nodes: 150, Edges: 420, Communities: 12"
