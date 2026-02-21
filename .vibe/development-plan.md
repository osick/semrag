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
- [ ] Define the enterprise ontology ingestion strategy (OWL/RDF/TTL).
- [ ] Research Cytoscape.js vs Sigma.js for the `/dashboard` implementation.
- [ ] Design the structural metadata schema for graph nodes and edges.
- [ ] Map out the reasoning/deduction logic based on added metadata.

## Architecture
### Phase Entrance Criteria:
- [ ] Ontology and RDF strategy are defined.
- [ ] Dashboard tech stack (Cytoscape/Sigma) is selected.
- [ ] Metadata schema is finalized.

### Tasks
- [ ] *To be added when this phase becomes active*

## Plan
### Phase Entrance Criteria:
- [ ] System architecture for ontology-driven RAG is documented.
- [ ] Dashboard UI/UX requirements are finalized.

### Tasks
- [ ] *To be added when this phase becomes active*

## Code
### Phase Entrance Criteria:
- [ ] Detailed implementation plan for RDF and Advanced Dashboard is finalized.

### Tasks
- [ ] *To be added when this phase becomes active*

## Finalize
### Phase Entrance Criteria:
- [ ] Ontology-driven ingestion is verified.
- [ ] Dynamic dashboard is functional and navigable.
- [ ] Metadata-based deduction/filtering is working.

### Tasks
- [ ] *To be added when this phase becomes active*
