# SEMRAG: Local-First Semantic RAG

A local-first, containerized Semantic Retrieval-Augmented Generation (SEMRAG) platform that combines unstructured vector similarity with structured graph-based relationships.

## Features
- **Hybrid Retrieval**: Combines Qdrant (Vector) and Neo4j/FalkorDB (Graph) for enhanced context.
- **Multi-Format Support**: Ingest PDF, DOCX, XLSX, and PPTX via the `unstructured` library.
- **Local-First Execution**: Fully runs on a local Kubernetes cluster or Docker Compose using Ollama.
- **Cypher-Compatible Graph Abstraction**: Easily switch between Neo4j and FalkorDB for evaluation.

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Python 3.12+
- Ollama (running locally or in a container)

### 1. Setup Environment
Initialize the local database services using Docker Compose:
```bash
docker-compose up -d
```
This starts Qdrant, Neo4j, FalkorDB, and Ollama.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Usage
**Ingesting a Document:**
```python
from semrag.ingestion.engine import IngestionEngine
# Initialize with your DB adapters and Ollama model
engine = IngestionEngine(graph_store, vector_store, embedding_model, llm)
engine.ingest_file("data/sample.docx")
```

**Querying the Hybrid Search:**
```python
from semrag.orchestration.graph import SEMRAGGraph
# Initialize the graph orchestrator
graph = SEMRAGGraph(vector_store, graph_store, llm, embedding_model)
result = graph.run("Who founded Apple Inc.?")
print(result["answer"])
```

## Project Structure
- `src/semrag/`: Core source code (ingestion, retrieval, graph_store, vector_store, orchestration).
- `tests/`: TDD behavioral tests (integration and unit).
- `docker-compose.yaml`: Local development services.
- `.vibe/docs/`: Detailed requirements, architecture, and design documentation.

## Testing
Run the behavioral integration tests to verify the end-to-end loops:
```bash
pytest tests/integration
```

## License
MIT
