# Open WebUI Integration Documentation

The SEMRAG system exposes an OpenAI-compatible API to integrate seamlessly with the Open WebUI platform.

## Configuration

### 1. Start the SEMRAG API
Ensure the `semrag-api` service is running (Port 8000).
```bash
docker-compose up semrag-api
```

### 2. Configure Open WebUI
1. In Open WebUI, navigate to **Settings > Connections > OpenAI API**.
2. Click **+** to add a new connection.
3. **API Base URL**: `http://localhost:8000/v1` (or your Kubernetes service URL).
4. **API Key**: `semrag-key` (any non-empty string).
5. Click **Verify**.

### 3. Using the Model
1. Your SEMRAG model will appear as `semrag-v2`.
2. Select it from the model dropdown in the chat interface.
3. Your queries will now trigger the Hybrid Vector-Graph retrieval pipeline.

## Capabilities

### Hybrid Retrieval
Every query to `semrag-v2` triggers a multi-step retrieval:
1.  **Vector Search**: Finds the most similar text chunks.
2.  **Graph Traversal**: Finds related entities and relationships.
3.  **Context Construction**: Combines both contexts into a single prompt for the LLM.

### Namespace Filtering
To filter by namespace in Open WebUI, you can pass the namespace as part of the query or use a custom tool.
*(Note: Advanced filtering will be expanded in future versions).*

## Troubleshooting

### Connection Errors
Ensure the SEMRAG API is accessible from the Open WebUI container. Check the network bridge or Kubernetes service/ingress configuration.

### Model Discovery
If `semrag-v2` does not appear, verify the `/v1/models` endpoint:
```bash
curl http://localhost:8000/v1/models
```
It should return a JSON response with the model ID.
