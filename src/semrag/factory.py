from langchain_community.chat_models import ChatLiteLLM
from langchain_community.embeddings import LiteLLMEmbeddings
from semrag.ingestion.engine import IngestionEngine
from semrag.orchestration.graph import SEMRAGGraph
from semrag.graph_store.neo4j_adapter import Neo4jGraphStore
from semrag.graph_store.falkordb_adapter import FalkorDBGraphStore
from semrag.vector_store.qdrant_wrapper import QdrantVectorStore
import os

def create_semrag_stack(
    llm_model: str = "ollama/llama3",
    embed_model: str = "ollama/nomic-embed-text",
    graph_db_type: str = "falkordb"
):
    """
    Factory function to create the complete SEMRAG stack using LiteLLM.
    """
    # 1. Models (LiteLLM)
    llm = ChatLiteLLM(model=llm_model)
    embeddings = LiteLLMEmbeddings(model=embed_model)

    # 2. Databases
    vector_store = QdrantVectorStore(
        host=os.getenv("QDRANT_HOST", "localhost"),
        port=int(os.getenv("QDRANT_PORT", 6333))
    )
    
    if graph_db_type == "neo4j":
        graph_store = Neo4jGraphStore(
            uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            user=os.getenv("NEO4J_USER", "neo4j"),
            password=os.getenv("NEO4J_PASSWORD", "password")
        )
    else:
        graph_store = FalkorDBGraphStore(
            host=os.getenv("FALKORDB_HOST", "localhost"),
            port=int(os.getenv("FALKORDB_PORT", 6379))
        )

    # 3. Engines
    ingestion_engine = IngestionEngine(graph_store, vector_store, embeddings, llm)
    graph_orchestrator = SEMRAGGraph(vector_store, graph_store, llm, embeddings)

    return ingestion_engine, graph_orchestrator
