# Design Document - SEMRAG v5 Implementation Final

## 1. FastMCP "Streamable HTTP" Server
The MCP server is implemented using the `fastmcp` framework.
- **`query_semrag`**: Tool that triggers the LangGraph hybrid retrieval pipeline.
- **`ingest_url`**: Tool that uses `fsspec` to pull remote documents.
- **`inspect_graph`**: Resource that provides graph health metrics.
- **Transport**: Standardized streamable HTTP integrated into the FastAPI application.

## 2. Push-to-Ingest (Upload API)
The upload API enables remote ingestion of local files.
- **Route**: `POST /v1/ingest/upload`.
- **Implementation**: Uses `FastAPI.UploadFile` to receive multipart data.
- **Buffering**: Content is streamed into `ingestion_engine.ingest_stream` without large temporary disk writes where possible.

## 3. Unified Ingestion Engine
The `IngestionEngine` provides a common interface for all document sources.
- **`ingest_file`**: Handles local file-system paths.
- **`ingest_stream`**: Handles `IO[bytes]` objects (e.g., from uploads or memory buffers).
- **Partitioning**: Both methods utilize `unstructured.partition` for multi-format support (PDF, DOCX, etc.).

## 4. Modern Lifecycle (uv)
The project has been migrated to `uv`.
- **`pyproject.toml`**: Defines project metadata and a flat dependency list.
- **`uv.lock`**: Ensures reproducible environments across development and production.
- **Dockerfile**: Replaces `pip install` with `uv sync` for significant build speedups.

## 5. Deployment manifests
- **docker-compose.yaml**: Orchestrates Qdrant, Neo4j/FalkorDB, Redis, and the SEMRAG Unified API (port 8000).
- **FastMCP Access**: Standardized tool discovery and execution via the `/mcp` sub-path.
