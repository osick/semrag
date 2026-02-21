# Design Document - SEMRAG v2 Implementation Final

## 1. OpenAI-Compatible API (FastAPI)
The FastAPI wrapper implements the standard OpenAI chat completion API.
- **`ChatCompletionRequest`**: Maps OpenAI's message format to the SEMRAG query.
- **`StreamingResponse`**: Supports Server-Sent Events (SSE) for incremental chat updates.
- **`list_models`**: Returns `semrag-v2` as the available model ID.

## 2. Multi-Source Ingestor (fsspec)
The `MultiSourceIngestor` provides a recursive loader for multiple file systems.
- **`ingest_url`**: Uses `fsspec.core.url_to_fs` to resolve the protocol and path.
- **`isdir` / `find`**: Recursively scans directories to extract files.
- **Temporary Buffering**: Downloads remote files (S3, HTTP) to a local `/tmp` buffer for processing by `unstructured`.

## 3. Visualization Engine (Pyvis)
The `VisualizationEngine` generates interactive HTML graphs for semantic mapping.
- **`Network`**: Configured with `barnes_hut` layout and dark mode background.
- **Entity Nodes**: Blue circles for graph entities and relationships.
- **Chunk Nodes**: Red squares for document chunks and their source metadata.
- **Interaction**: Users can hover nodes to see full content or click to reveal details.

## 4. LiteLLM & Factory Integration
The `factory.py` provides a centralized way to initialize the entire SEMRAG stack.
- **`create_semrag_stack`**: Automatically initializes `ChatLiteLLM` and `LiteLLMEmbeddings` based on environment variables.
- **Switching**: Users can switch between `neo4j` and `falkordb` by passing a simple string.

## 5. Deployment manifests
- **Dockerfile**: Includes system-level dependencies for `unstructured` (libreoffice, tesseract, pandoc, etc.).
- **docker-compose.yaml**: Orchestrates the DB services (Qdrant, Neo4j, FalkorDB, Ollama) and the SEMRAG API.
