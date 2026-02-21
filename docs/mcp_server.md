# MCP Server Documentation

The SEMRAG system exposes a standardized **Model Context Protocol (MCP)** server for seamless integration with AI clients like Claude Desktop, IDE extensions, and more.

## Overview
- **Protocol**: HTTP with Server-Sent Events (SSE).
- **Base URL**: `http://localhost:8001/mcp`.
- **Streaming**: Supported via SSE for real-time tool updates.

## Available Tools

### `query_semrag`
Performs a hybrid vector-graph search across the knowledge base.
- **Input**:
  - `query` (string): The user query.
  - `namespace` (string, optional): Filter by namespace (e.g., "Legal").
- **Output**: The combined context and generated response.

### `ingest_url`
Recursively ingests documents from a local or remote URL (S3, HTTP).
- **Input**:
  - `url` (string): The URL to ingest.
- **Output**: Status message of the ingestion.

### `inspect_graph`
Returns a high-level summary of the graph's health and communities.
- **Output**: Statistics and detected communities.

## Tool Call Examples (JSON Payload)

### Querying the Knowledge Base
To perform a hybrid search, send the following payload to the `/mcp/tools/call` endpoint:
```json
{
  "name": "query_semrag",
  "arguments": {
    "query": "Who founded Apple Inc.?",
    "namespace": "Legal"
  }
}
```

### Ingesting a Remote Document
To ingest a document from an S3 bucket:
```json
{
  "name": "ingest_url",
  "arguments": {
    "url": "s3://my-bucket/documents/apple_history.pdf"
  }
}
```

## Connecting to the Server
In your MCP-compliant client (e.g., `claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "semrag": {
      "command": "python",
      "args": ["src/semrag/mcp/server_http.py"]
    }
  }
}
```
Alternatively, for HTTP/SSE:
```json
{
  "mcpServers": {
    "semrag": {
      "url": "http://localhost:8001/mcp/sse"
    }
  }
}
```
