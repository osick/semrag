# DevOps Guide

This guide covers the deployment, monitoring, and performance auditing of the SEMRAG platform in production environments.

## Deployment Architecture

### 1. Kubernetes Setup
The SEMRAG platform is designed for containerized deployment on a Kubernetes cluster.
- **StatefulSets**: For Qdrant and the Graph Store (Neo4j/FalkorDB).
- **Deployments**: For the SEMRAG API and the Ollama service.
- **ConfigMaps**: To manage the environment variables and LiteLLM configurations.
- **Secrets**: For database credentials and LLM provider API keys.

### 2. Resource Requirements
- **Vector DB**: High memory requirement (depending on the number of points and dimensions).
- **Graph DB**: High memory requirement for large-scale traversal.
- **LLM (Ollama)**: Requires GPU access (NVIDIA/AMD) for performant local execution.

## Choosing Your Graph Database

SEMRAG v4 supports both **Neo4j** and **FalkorDB** via a unified adapter pattern. Your choice depends on your performance requirements and existing infrastructure.

### Comparison Table

| Feature | Neo4j | FalkorDB |
| :--- | :--- | :--- |
| **Backend** | Native Graph Engine | Redis-based (In-memory) |
| **Query Language** | Cypher (Full Support) | Cypher (Optimized Subset) |
| **Performance** | Excellent for deep traversals | Ultra-low latency (In-memory) |
| **Resource Usage** | Higher (JVM-based) | Minimal (C-based Redis module) |
| **Ecosystem** | Rich (Bloom, GDS, APOC) | Lightweight, specialized for GraphRAG |

### Configuration
To switch between databases, update your `.env` file:

```bash
# For Neo4j (Default)
GRAPH_DB_TYPE=neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# For FalkorDB (Low Latency)
GRAPH_DB_TYPE=falkordb
FALKORDB_HOST=localhost
FALKORDB_PORT=6379
```

## Caching Strategy (Redis)

### Response & Embedding Caching
We use Redis to store query results and text embeddings to reduce latency and costs.
- **Configuration**: Set `REDIS_HOST` and `REDIS_PORT` in the `.env` file.
- **Purging**: You can purge the cache by running `redis-cli flushdb`.

## Observability (Structured Logging)

### Logging with structlog
The system uses `structlog` to provide JSON-formatted query traces.
- **Log Format**: Every retrieval step includes:
    - `timestamp`: Execution time (ISO format).
    - `vector_latency`: Time taken for similarity search.
    - `graph_hits`: Number of relationships retrieved.
    - `provenance`: Sources used in the final response.
    - `llm_cost`: Estimated cost of the generation call (if applicable).

### Monitoring
Integrate the JSON logs with standard monitoring stacks:
- **ELK Stack**: Elasticsearch, Logstash, Kibana.
- **Grafana Loki**: For log aggregation and querying.

## Performance Auditing

### Retrieval Latency
The `structlog` output provides detailed latency statistics for each pipeline stage.

### Answer Quality (RAGAS / DeepEval)
To audit the quality of the system, we recommend integrating **RAGAS** for LLM-as-a-judge scoring on:
- **Faithfulness**: (No hallucinations).
- **Answer Relevancy**.
- **Context Precision**.

## Scalability
- **Horizontal Scaling**: Scale the SEMRAG API pods to handle high query volume.
- **Vertical Scaling**: Scale the GPU/Memory for Ollama and the Vector/Graph DBs.
- **Partitioning**: Use Qdrant's collections and Graph DB partitioning for large datasets.
