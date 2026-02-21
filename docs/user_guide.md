# User Guide

This guide will help you get started with the SEMRAG system for knowledge retrieval, document ingestion, and graph visualization.

## Getting Started

### 1. Installation
Install the required dependencies:
```bash
pip install -r requirements.txt
```

### 2. Initializing the Stack
Ensure you have Docker and Docker Compose installed.
Start the databases and services:
```bash
docker-compose up -d
```
This starts:
- **Qdrant** (Vector Store)
- **Neo4j** (Graph Store)
- **FalkorDB** (Graph Store)
- **Ollama** (Local LLM)
- **Redis** (Cache)
- **SEMRAG API** (OpenAI-Compatible & Dashboard)

## Ingesting Documents
The `IngestionEngine` and `MultiSourceIngestor` allow for multi-format, multi-source ingestion.

### 1. Local Directory Ingestion
```python
from semrag.ingestion.loaders.multi_source_ingestor import MultiSourceIngestor
from semrag.factory import create_semrag_stack

ingestor, _ = create_semrag_stack()
multi_ingestor = MultiSourceIngestor(ingestor)

# Ingest from local directory
multi_ingestor.ingest_url("./data", recursive=True)
```

### 2. Remote URL/S3 Ingestion
```python
# Ingest from S3
multi_ingestor.ingest_url("s3://my-bucket/documents", recursive=True)
```

## Querying the Knowledge Base
You can query SEMRAG via the API, the CLI, or the MCP server.

### 1. Hybrid Retrieval Query
```python
from semrag.orchestration.graph import SEMRAGGraph
# Initialize the graph orchestrator
graph = SEMRAGGraph(vector_store, graph_store, llm, embedding_model)
result = graph.run("Who founded Apple Inc.?")
print(result["answer"])
```

### 2. Global Graph Summary Query
If you have generated global summaries, you can query for themes:
```python
# Use a specific tool or query node in the dashboard
# To be expanded in future versions
```

## API Usage (FastAPI)

SEMRAG v4 exposes an OpenAI-compatible API for seamless integration with external clients.

### 1. Chat Completion (Non-Streaming)
```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "semrag-v2",
    "messages": [{"role": "user", "content": "Tell me about Steve Jobs."}],
    "stream": false
  }'
```

### 2. List Available Models
```bash
curl http://localhost:8000/v1/models
```

### 3. Dashboard Data Access
To retrieve the full graph as Cytoscape-compatible JSON:
```bash
curl http://localhost:8000/dashboard/data
```

## Visualization
Open your browser to `http://localhost:8000/dashboard` to view the **Cytoscape.js** interactive graph.
- **Pan & Zoom**: Standard mouse controls.
- **Inspect**: Click a node to view full metadata (Provenance, Namespace, Confidence).
- **Filter**: Filter by namespace or provenance (in the dashboard UI).

## Model Configuration
Change your LLM and embedding providers in the `.env` file using the LiteLLM model syntax (e.g., `ollama/llama3`, `openai/gpt-4o`).
