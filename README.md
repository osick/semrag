# SEMRAG v2: Enterprise-Ready Semantic RAG

A high-performance, local-first Semantic Retrieval-Augmented Generation (SEMRAG) platform. It integrates unstructured vector similarity (Qdrant) with structured graph-based relationships (Neo4j/FalkorDB), utilizing **LiteLLM** for multi-provider model orchestration.

## Features
- **LiteLLM Integration**: Single entry point for 100+ LLM and Embedding providers (OpenAI, Ollama, Anthropic, Bedrock, etc.).
- **Hybrid Retrieval**: Stateful LangGraph workflow blending Vector and Graph contexts.
- **Multi-Source Ingestion**: Recursive loading from Local, S3, HTTP, and more via `fsspec`.
- **OpenAI-Compatible API**: Seamless integration with **Open WebUI** via a standard FastAPI wrapper.
- **Semantic Visualization**: Interactive Pyvis-based dashboards for mapping the vector-graph knowledge base.

---

## 1. Installation & Configuration

### Prerequisites
- **Docker & Docker Compose**
- **Python 3.12+**
- **Ollama** (optional, for fully local execution)

### Step-by-Step Setup
1. **Clone and Initialize Environment**:
   ```bash
   git clone <repository_url>
   cd semrag
   cp .env.example .env  # If provided, or create manually
   ```

2. **Configure Models and Backends (`.env`)**:
   Edit your `.env` file to select your models and database backends:
   ```bash
   # LLM & Embeddings (LiteLLM Syntax)
   LLM_MODEL=ollama/llama3
   EMBED_MODEL=ollama/nomic-embed-text
   
   # Graph Database Selection (neo4j OR falkordb)
   GRAPH_DB_TYPE=falkordb
   
   # Database Credentials
   QDRANT_HOST=localhost
   NEO4J_PASSWORD=password
   OLLAMA_BASE_URL=http://localhost:11434
   ```

3. **Start Infrastructure**:
   ```bash
   docker-compose up -d
   ```
   This initializes Qdrant, your selected Graph DB, and the SEMRAG API.

4. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## 2. Usage with Open WebUI

SEMRAG v2 exposes an OpenAI-compatible API, allowing it to function as an "External Model" in Open WebUI.

1. **Verify API Status**:
   Ensure the `semrag-api` service is running (Port 8000).
2. **Configure Open WebUI**:
   - Navigate to **Settings > Connections > OpenAI API**.
   - Click **+** to add a new connection.
   - **API Base URL**: `http://localhost:8000/v1`
   - **API Key**: `semrag-key` (any non-empty string).
3. **Chatting**:
   Select the `semrag-v2` model from the model dropdown. Your queries will now trigger the Hybrid Vector-Graph retrieval pipeline.

---

## 3. Visualization Dashboard

The system includes a `VisualizationEngine` to render your knowledge base as an interactive HTML graph.

### Generating the Dashboard
Use the following snippet to generate the `semrag_dashboard.html`:

```python
from semrag.factory import create_semrag_stack
from semrag.visualization.engine import VisualizationEngine

# 1. Initialize Stack
_, graph_orchestrator = create_semrag_stack()

# 2. Extract Data (Example)
# In a real scenario, you'd pull data from your DB adapters
sample_triples = [("Apple", "FOUNDED_BY", "Steve Jobs")]
sample_chunks = [{"content": "Steve Jobs founded Apple in Cupertino.", "source": "history.pdf"}]

# 3. Render
viz = VisualizationEngine(output_path="semrag_dashboard.html")
viz.add_graph_data(sample_triples)
viz.add_vector_data(sample_chunks)
viz.generate()
```

### Viewing
Open `semrag_dashboard.html` in any modern web browser. 
- **Blue Nodes**: Entities and relationships from the Graph Store.
- **Red Nodes**: Semantic text chunks from the Vector Store.
- **Interactivity**: Zoom, drag nodes, and hover to view full text or metadata.

---

## Testing
Execute the behavioral integration suite to verify the end-to-end v2 loops:
```bash
pytest tests/integration/test_v2_behavior.py
```

## License
MIT
