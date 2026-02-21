# Development Plan: SEMRAG v3 (Enterprise Graph & Advanced Dashboard)

*Workflow: [greenfield](https://mrsimpson.github.io/responsible-vibe-mcp/workflows/greenfield)*

## Goal
Expand SEMRAG with enterprise ontology support, RDF triple ingestion, and a dynamic, high-performance visualization dashboard integrated into the FastAPI service.

## Key Decisions
- **Ontology Framework**: RDFLib for formal triple management and ontology loading.
- **Data Model**: Schema-first extraction (pre-loading ontologies/rule sets).
- **Interface**: FastAPI endpoint for the dashboard (`/dashboard`) using **Cytoscape.js**.
- **Metadata**: Add structural metadata (provenance, confidence, namespace) to every node/edge.
- **Ingestion Order**: Graph-first (ontologies) then documents (contextual triples).

## Ideation
### Tasks
- [x] Define the enterprise ontology ingestion strategy (OWL/RDF/TTL).
- [x] Research Cytoscape.js vs Sigma.js for the `/dashboard` implementation.
- [x] Design the structural metadata schema for graph nodes and edges.
- [x] Map out the reasoning/deduction logic based on added metadata.

## Architecture
### Phase Entrance Criteria:
- [x] Ontology and RDF strategy are defined.
- [x] Dashboard tech stack (Cytoscape/Sigma) is selected.
- [x] Metadata schema is finalized.

### Tasks
- [x] Design the `OntologyLoader` for OWL/RDF/TTL file ingestion.
- [x] Specify the metadata enrichment schema (provenance, confidence, namespace).
- [x] Design the dynamic `/dashboard` endpoint using **Cytoscape.js**.
- [x] Specify the Cypher query logic for metadata-based deduction/filtering.
- [x] Update the Graph Store interface for RDF-compatible triple management.
- [x] Design the reasoning/deduction layer using the added metadata.

## Plan
### Phase Entrance Criteria:
- [x] System architecture for ontology-driven RAG is documented.
- [x] Dashboard UI/UX requirements are finalized.

### Tasks
- [x] Initialize `requirements.txt` with `rdflib` and `pydantic`.
- [x] Map out the `src/semrag/graph_store/ontology_loader.py` structure.
- [x] Design the `src/semrag/api/dashboard_service.py` with the Cytoscape.js frontend.
- [x] Define the metadata schema (Pydantic models) for nodes and edges.
- [x] Create the initial "Deduction" test cases for metadata-based retrieval.
- [x] Define the TDD test cases for ontology-driven triple extraction.

## Code
### Phase Entrance Criteria:
- [x] Detailed implementation plan for RDF and Advanced Dashboard is finalized.

### Tasks
- [x] Implement `src/semrag/graph_store/ontology/loader.py` using rdflib.
- [x] Implement `src/semrag/api/models.py` with Pydantic for metadata.
- [x] Update `IGraphStore` and adapters for metadata enrichment.
- [x] Implement `src/semrag/api/dashboard.py` and the Cytoscape.js frontend.
- [x] Implement metadata-based deduction logic in `SEMRAGGraph`.
- [x] Create behavioral tests for ontology loading and triple extraction.
- [x] Verify the system with the new dashboard and RDF integration.

## Finalize
### Phase Entrance Criteria:
- [x] Ontology-driven ingestion is verified.
- [x] Dynamic dashboard is functional and navigable.
- [x] Metadata-based deduction/filtering is working.

### Tasks
- [x] Finalize Architecture Document (`architecture.md`).
- [x] Update `README.md` with Ontology, RDF, and Dashboard setup instructions.
- [x] Create a sample `.ttl` ontology for testing.
- [x] Run final end-to-end tests for all v3 features.
- [x] Finalize the dashboard's filtering and navigation frontend logic.

### Completed
- [x] Finalized all project documentation and behavioral tests for SEMRAG v3.
- [x] Created `README.md` with Ontology and Dashboard setup.
- [x] Verified code quality and cleanup.
