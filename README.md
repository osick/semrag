# SEMRAG v5: Modern Enterprise Semantic RAG

**The most powerful local-first Semantic RAG, now with ultra-fast lifecycle management and standardized MCP connectivity.**

SEMRAG v5 integrates **unstructured vector similarity** (Qdrant) with **structured graph intelligence** (Neo4j/FalkorDB), featuring a standardized **FastMCP** server and a high-performance **Push-to-Ingest** architecture.

---

## 🚀 Key v5 Features
- **⚡ uv Powered**: Ultra-fast dependency resolution and deterministic builds using `uv`.
- **📡 Standardized FastMCP**: Streamable HTTP MCP server for effortless integration with any AI client.
- **📥 Push-to-Ingest**: New Upload API (`POST /v1/ingest/upload`) for remote ingestion of local files.
- **🧬 Hybrid Intelligence**: Stateful LangGraph workflow blending Vector and Graph contexts.
- **📁 Multi-Source Ingestion**: Support for Local Push (Multipart), Remote Pull (fsspec), and RDF/Ontology loading.
- **📊 Advanced Dashboard**: Interactive Cytoscape.js visualization at `http://localhost:8000/dashboard`.

---

## 🛠️ Installation & Setup (uv)

SEMRAG v5 utilizes **uv** for high-performance Python management.

1. **Install uv**:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Initialize Environment**:
   ```bash
   uv sync
   docker-compose up -d
   ```

3. **Configure Models**:
   Update your `.env` file with your **LiteLLM** compatible models (e.g., `ollama/llama3`).

---

## 📖 Modern Usage

### 1. Push-to-Ingest (Local Files to Remote Server)
Ingest a local document to your remote SEMRAG server instantly:
```bash
curl -X POST http://localhost:8000/v1/ingest/upload \
  -F "file=@/path/to/your/local_document.pdf"
```

### 2. FastMCP Tool Connectivity
Standardized MCP connectivity for your AI agents (Claude, IDEs):
- **Server URL**: `http://localhost:8000/mcp/sse` (conceptually)
- **Tools**: `query_semrag`, `ingest_url`, `inspect_graph`.

### 3. Interactive Dashboard
Explore your knowledge base at `http://localhost:8000/dashboard`.

---

## 📚 Documentation
- **[📖 User Guide](./docs/user_guide.md)**: v5 updated instructions.
- **[📡 MCP Server](./docs/mcp_server.md)**: FastMCP integration details.
- **[DevOps Guide](./docs/devops_guide.md)**: uv and Kubernetes deployment.

---

## 📜 License
Apache License 2.0
