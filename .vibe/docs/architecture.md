# Architecture Document - SEMRAG v2 Final

## System Overview
The SEMRAG v2 system is a multi-provider, multi-source Knowledge Retrieval Augmentation (RAG) platform. It expands the initial vector-graph hybrid retrieval with **LiteLLM** for model standardization, **fsspec** for broad ingestion, and an **OpenAI-compatible API** for third-party integration (e.g., **Open WebUI**).

## Core Components

### 1. Model Abstraction Layer (LiteLLM)
- **Role**: Provides a single interface (`ChatLiteLLM`, `LiteLLMEmbeddings`) for 100+ LLM providers.
- **Dynamic Configuration**: Supports switching between local (Ollama) and cloud (OpenAI, Anthropic) models via environment variables.

### 2. Multi-Source Ingestion Engine (fsspec)
- **Protocols**: Natively handles `local://`, `s3://`, `http(s)://`, and more.
- **Recursive Processing**: Scans directories recursively for supported file types (`.pdf`, `.docx`, `.xlsx`, `.pptx`, `.md`).
- **Unified Logic**: Integrates with the existing `IngestionEngine` to process text chunks and extract semantic links.

### 3. OpenAI-Compatible FastAPI Wrapper
- **API**: Implements the standard OpenAI `/v1/chat/completions` and `/v1/models` endpoints.
- **Integration**: Allows OpenAI-compatible clients like **Open WebUI** to use SEMRAG as a backend model.
- **Orchestration**: Directs incoming chat requests to the **LangGraph** retrieval pipeline.

### 4. Vector-Graph Visualization (Pyvis)
- **Interface**: Generates an interactive HTML dashboard (`semrag_dashboard.html`).
- **Data Model**: Displays entity nodes (Graph Store) and document chunks (Vector Store) in a single unified view.

## Data Flow
1.  **Ingestion**: `fsspec` scans source -> `IngestionEngine` chunks & extracts -> `Qdrant` + `Neo4j/FalkorDB`.
2.  **Query**: `Open WebUI` -> `FastAPI` -> `LangGraph` -> `LiteLLM` (retrieval & generation) -> `Response`.

## Deployment
- **Containerization**: Fully Dockerized for local development and Kubernetes deployment.
- **Services**: Qdrant, Neo4j, FalkorDB, Ollama, and the SEMRAG API.
