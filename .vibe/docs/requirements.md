# Requirements Document - SEMRAG v5

## Functional Requirements

### 1. Unified Ingestion
- **Local & Remote Push/Pull**: Support for local file uploads (Push), remote URL ingestion (Pull), and directory scanning.
- **Multi-Format Support**: Native partitioning for PDF, Markdown, Plain Text, and Office files (DOCX, XLSX, PPTX).
- **Enterprise Ontology**: Support for loading OWL/RDF/TTL rule sets to drive schema-first graph construction.

### 2. Intelligent Retrieval
- **Hybrid Search**: Advanced LangGraph workflow combining vector similarity (Qdrant) and graph-based traversal (Neo4j/FalkorDB).
- **Metadata-Enriched Extraction**: Automatic extraction of entities and relationships with provenance, confidence, and namespace metadata.
- **Global Summarization**: Leiden-based community detection for high-level dataset insights.

### 3. Connectivity & Integration
- **Standardized MCP**: Expose tools via a streamable HTTP Model Context Protocol (MCP) server (FastMCP).
- **Open WebUI Compatibility**: OpenAI-compatible API for seamless integration with third-party chat interfaces.
- **Visualization**: Dynamic Cytoscape.js dashboard for knowledge graph exploration.

## Non-Functional Requirements

### 1. Performance & Lifecycle
- **Ultra-Fast Builds**: Deterministic project management and fast installs via `uv`.
- **Latency Optimization**: Redis-backed caching for embeddings and retrieval context.
- **Scalability**: Designed for containerized deployment on Kubernetes.

### 2. Security & Observability
- **Local-First or Hybrid**: Flexible deployment allowing for fully local (Ollama) or secure cloud (OpenAI/Anthropic) model usage.
- **Structured Logging**: JSON-formatted auditing of every retrieval step.

## Scope

### In-Scope
- Core SEMRAG engine with LangGraph orchestration.
- Standardized FastMCP server.
- Push-to-Ingest (Upload) and Pull (fsspec) engines.
- Advanced visualization dashboard.
- `uv` based lifecycle management.

### Out-of-Scope
- Multi-tenant user authentication.
- Real-time collaborative graph editing.
