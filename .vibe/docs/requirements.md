# Requirements Document

## Functional Requirements

### 1. Ingestion
- **Local-First Execution**: The entire stack must run locally (e.g., using Ollama for LLM/Embeddings).
- **Multi-Format Support**: Support for PDF, Markdown, Plain Text, and Office files (DOCX, XLSX, PPTX).
- **Semantic Chunking**: Automatic splitting of text based on semantic boundaries rather than fixed characters.

### 2. Retrieval & Generation
- **Hybrid Search**: Combining vector-based similarity search with graph-based relationship traversal.
- **Entity Extraction**: Automated identification of entities (Nodes) and relationships (Edges) from ingested text using a local LLM.
- **Context Augmentation**: Retrieval results should include both top-k vector matches and relevant graph-traversed nodes.

## Non-Functional Requirements

### 1. Privacy & Security
- **Local Isolation**: No data shall be transmitted to external cloud services.
- **In-Memory/Local Storage**: Persistence must be local to the host machine.

### 2. Performance
- **Low Latency**: Search and retrieval should provide response times acceptable for real-time interaction (e.g., < 2s for typical queries).
- **Scalability**: Capable of handling document collections up to 1GB in size locally.

## Scope

### In-Scope
- Core SEMRAG engine (Python 3).
- Local Vector DB (Qdrant or Chroma).
- Local Graph DB (FalkorDB or Neo4j).
- CLI or simple API for interaction.
- Office document (DOCX, XLSX, PPTX) and PDF ingestion.

### Out-of-Scope
- Cloud-hosted LLM services (OpenAI, Anthropic).
- Multi-user authentication.
- Complex GUI (CLI/Simple API only).
