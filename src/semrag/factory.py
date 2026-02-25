from typing import List, Optional
from langchain_community.chat_models import ChatLiteLLM
from langchain_ollama import OllamaEmbeddings
from semrag.ingestion.engine import IngestionEngine
from semrag.orchestration.graph import SEMRAGGraph
from semrag.graph_store.neo4j_adapter import Neo4jGraphStore
from semrag.graph_store.falkordb_adapter import FalkorDBGraphStore
from semrag.vector_store.qdrant_wrapper import QdrantVectorStore
import os

def create_semrag_stack(
    llm_model: str = "ollama/llama3",
    embed_model: str = "ollama/nomic-embed-text",
    graph_db_type: str = "falkordb",
    extraction_strategy: str = "llm",
    entity_labels: Optional[List[str]] = None,
    spacy_model: str = "en_core_web_sm",
    gliner_model: str = "urchade/gliner_medium-v2.1",
    complexity_threshold: float = 0.6,
    enable_trigraph: bool = False,
):
    """
    Factory function to create the complete SEMRAG stack (v6).

    Args:
        extraction_strategy: "llm" (default, v5 behavior), "nlp" (spaCy+GLiNER),
                             "adaptive" (complexity-routed NLP+LLM hybrid).
        entity_labels: Required for "nlp", "adaptive", and trigraph strategies.
                       Domain-specific entity types for GLiNER zero-shot NER.
        enable_trigraph: If True, builds LinearRAG-inspired tri-graph alongside
                         standard extraction and enables PageRank retrieval.
    """
    # 1. Models (LiteLLM for chat, Ollama for embeddings)
    llm = ChatLiteLLM(model=llm_model)
    embeddings = OllamaEmbeddings(model=embed_model)

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

    # 3. Extraction Strategy
    extractor = None
    trigraph_builder = None
    pagerank_retriever = None

    if extraction_strategy == "nlp":
        from semrag.ingestion.extractors.nlp_extractor import SpaCyGLiNERExtractor
        extractor = SpaCyGLiNERExtractor(
            spacy_model=spacy_model,
            gliner_model=gliner_model,
            entity_labels=entity_labels,
        )
    elif extraction_strategy == "adaptive":
        from semrag.ingestion.extractors.nlp_extractor import SpaCyGLiNERExtractor
        from semrag.ingestion.extractors.llm_extractor import LLMTripleExtractor
        from semrag.ingestion.extractors.adaptive_router import AdaptiveExtractionRouter
        nlp_ext = SpaCyGLiNERExtractor(
            spacy_model=spacy_model,
            gliner_model=gliner_model,
            entity_labels=entity_labels,
        )
        llm_ext = LLMTripleExtractor(llm=llm)
        extractor = AdaptiveExtractionRouter(
            nlp_extractor=nlp_ext,
            llm_extractor=llm_ext,
            complexity_threshold=complexity_threshold,
        )

    if enable_trigraph:
        from semrag.ingestion.extractors.nlp_extractor import SpaCyGLiNERExtractor
        from semrag.ingestion.extractors.tri_graph_builder import TriGraphBuilder
        from semrag.orchestration.pagerank_retriever import PageRankRetriever
        entity_extractor = SpaCyGLiNERExtractor(
            spacy_model=spacy_model,
            gliner_model=gliner_model,
            entity_labels=entity_labels,
        )
        trigraph_builder = TriGraphBuilder(
            entity_extractor=entity_extractor,
            graph_store=graph_store,
        )
        pagerank_retriever = PageRankRetriever(
            graph_store=graph_store,
            entity_extractor=entity_extractor,
        )

    # 4. Engines
    ingestion_engine = IngestionEngine(
        graph_store, vector_store, embeddings, llm,
        extractor=extractor,
        trigraph_builder=trigraph_builder,
    )
    graph_orchestrator = SEMRAGGraph(
        vector_store, graph_store, llm, embeddings,
        pagerank_retriever=pagerank_retriever,
    )

    return ingestion_engine, graph_orchestrator
