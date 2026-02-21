# Architecture Document - SEMRAG v3 Final

## System Overview
SEMRAG v3 expands the initial hybrid retrieval with **Enterprise-Grade Graph Intelligence**, including support for ontologies, RDF triple ingestion, and a high-performance interactive dashboard.

## Core Components

### 1. Ontology & RDF Integration (RDFLib)
- **Ontology Loader**: Parses OWL, RDF, and TTL to establish a "Schema-First" graph.
- **RDF Importer**: Directly loads external triples into the Graph Store, mapping identifiers to local entities.
- **Triple Management**: Handles namespace-qualified entities and relationships via the `IGraphStore`.

### 2. Metadata-Enriched Graph Schema (Pydantic)
- **Nodes & Edges**: Every entity and relationship includes:
    - `provenance`: Origin of the data (e.g., "Policy Rule Set v1", "document.pdf").
    - `confidence`: Extraction certainty score (0.0 to 1.0).
    - `namespace`: Logical domain (e.g., "Legal", "Engineering").
    - `uri`: Global unique identifier (for RDF-sourced data).

### 3. Advanced Dashboard (Cytoscape.js)
- **Backend**: FastAPI endpoint providing a JSON representation of the graph.
- **Frontend**: A high-performance visualization layer at `/dashboard` using **Cytoscape.js**.
- **Capabilities**: Zoom, Pan, Drag, and Metadata inspection (Provenance, Namespace, Confidence).

### 4. Reasoning & Deduction Layer
- **Metadata-Aware Retrieval**: The LangGraph pipeline uses `namespace` and `provenance` filters to refine the contextual context.
- **Provenance-Aware Answering**: The context provided to the LLM includes metadata, enabling the model to state its sources and confidence.

## Data Flow (v3)
1.  **Ontology Loading**: `Rule Set (.ttl)` -> `RDFLib` -> `Graph Store` (Schema/Rules established).
2.  **Document Ingestion**: `Doc` -> `LLM` (constrained by ontology) -> `Graph Store` (Contextual triples added).
3.  **Visualization**: `FastAPI /dashboard` -> `Cytoscape.js` -> `Interactive UI`.

## Technology Stack (v3)
- **Ontology Parser**: RDFLib.
- **Dashboard UI**: Cytoscape.js.
- **Metadata Management**: Pydantic.
- **Retrieval**: LangGraph.
