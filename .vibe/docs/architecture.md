# Architecture Document - SEMRAG v5 Final

## System Overview
SEMRAG v5 is a state-of-the-art Knowledge Retrieval Augmentation (RAG) platform. It provides a standardized interface for multi-source knowledge ingestion and hybrid retrieval using vector and graph intelligence. V5 focuses on modern developer experience with `uv` and standardized connectivity via `FastMCP`.

## Core Components

### 1. Model & Package Management (uv)
- **Tooling**: Uses `uv` for ultra-fast dependency resolution and deterministic project management.
- **Environment**: Governed by `pyproject.toml` and `uv.lock`.

### 2. Standardized Tool Connectivity (FastMCP)
- **Framework**: `FastMCP` (via `fastmcp` and `mcp`).
- **Transport**: Standardized "Streamable HTTP" transport for tool access.
- **Unified API**: FastMCP is integrated into the main FastAPI application, providing a single entry point for Chat, Dashboard, and Tools.

### 3. Push-to-Ingest Architecture (Upload API)
- **Pattern**: "Push-to-Ingest" allows clients to upload local files directly to the remote server via a multipart POST request.
- **Unified Processing**: The `IngestionEngine` handles both file-system paths and in-memory byte streams from uploads.

### 4. Hybrid Intelligence (LangGraph)
- **Workflow**: Stateful LangGraph orchestrator that merges Vector Search (Qdrant) and Graph Traversal (Neo4j/FalkorDB).
- **Metadata**: Provenance, namespace, and confidence metadata are preserved throughout the retrieval chain.

### 5. Interactive Visualization (Cytoscape.js)
- **Interface**: A dynamic, high-performance dashboard available at `/dashboard`.
- **Data Model**: Visualizes the relationship between document chunks and extracted semantic entities.

## Data Flow
1.  **Ingestion (Push)**: `Client` -> `FastAPI /upload` -> `BytesIO` -> `IngestionEngine` -> `Vector/Graph DB`.
2.  **Ingestion (Pull)**: `Admin` -> `FastMCP ingest_url` -> `fsspec` -> `IngestionEngine` -> `Vector/Graph DB`.
3.  **Retrieval**: `Client` -> `FastAPI /chat` OR `FastMCP query_semrag` -> `LangGraph` -> `LiteLLM` -> `Response`.

## Deployment
- **Containerization**: Optimized Docker builds using `uv sync`.
- **Services**: Qdrant, Neo4j/FalkorDB, Redis (Cache), and the SEMRAG Unified API.
