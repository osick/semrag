# SEMRAG v3: Enterprise-Grade Graph Intelligence

A high-performance Semantic Retrieval-Augmented Generation (SEMRAG) platform with support for enterprise ontologies, RDF integration, and metadata-enriched graph reasoning.

## New Features (v3)
- **Enterprise Ontology Support**: Ingest OWL, RDF, and TTL rule sets to establish a schema-first knowledge graph.
- **Metadata Enrichment**: Track `provenance`, `confidence`, and `namespace` for every node and relationship.
- **Advanced Dashboard**: Dynamic, interactive graph visualization using **Cytoscape.js** (Port 8000/dashboard).
- **Metadata-Aware Retrieval**: Use metadata filters to refine context and perform deduction-based answering.

## Getting Started

### 1. Setup Environment
Initialize the local database services using Docker Compose:
```bash
docker-compose up -d
```

### 2. Configure Models and Databases
Ensure your `.env` file is set up for your chosen LLM and Graph DB (Neo4j/FalkorDB).

### 3. Usage

**Loading an Enterprise Ontology:**
```python
from semrag.graph_store.ontology.loader import OntologyLoader
from semrag.factory import create_semrag_stack

_, graph_orchestrator = create_semrag_stack()
loader = OntologyLoader(graph_orchestrator._graph_store)

# Load enterprise rule set
loader.load_ontology("data/legal_schema.ttl", format="turtle", namespace="Legal")
```

**Metadata-Aware Querying:**
```python
# Query with a namespace filter for legal deduction
result = graph_orchestrator.run("What rules govern Contract_A?", namespace_filter="Legal")
print(result["answer"])
```

**Advanced Dashboard:**
1. Start the API: `docker-compose up semrag-api`
2. Open your browser to `http://localhost:8000/dashboard`.
3. Interact with the graph: Zoom, Pan, and Click nodes to see metadata (Provenance, Namespace, Confidence).

## Project Structure
- `src/semrag/graph_store/ontology/`: Ontology and RDF loading logic.
- `src/semrag/api/dashboard.py`: FastAPI endpoints for the Cytoscape.js dashboard.
- `src/semrag/api/models.py`: Pydantic models for metadata-enriched entities.

## Testing
Run the behavioral integration suite for v3 features:
```bash
pytest tests/integration/test_v3_behavior.py
```
