# Design Document - SEMRAG v3 Implementation Final

## 1. Ontology Loader (RDFLib)
The `OntologyLoader` parses and ingests enterprise rule sets.
- **Library**: `rdflib`.
- **Method**: `load_ontology(url: str, format: str, namespace: str)` parses files and creates class/property nodes.
- **RDF Importer**: `extract_rdf_triples` directly loads triples into the Graph Store.

## 2. Metadata-Enriched Schema (Pydantic)
Every graph interaction is governed by a Pydantic model.
- **`GraphNode`**: `id`, `name`, `type`, `uri`, `provenance`, `confidence`, `namespace`.
- **`GraphEdge`**: `subject`, `predicate`, `object`, `provenance`, `confidence`, `namespace`.
- **Enriched Triple**: Combines nodes and edges into a single ingestion unit.

## 3. Advanced Dashboard (Cytoscape.js)
The dashboard is a dynamic, interactive visualization served by FastAPI.
- **Endpoint**: `GET /dashboard` renders the Cytoscape.js frontend.
- **Data Endpoint**: `GET /dashboard/data` returns graph JSON with metadata.
- **Features**: Pan, Zoom, Drag, and Metadata detail sidebar on click.

## 4. Graph Store Interface Updates
The `IGraphStore` interface includes new methods for metadata-enriched triples.
- **`add_enriched_triple`**: Merges nodes and creates relationships with metadata.
- **`query_by_metadata`**: Filters nodes/edges based on `namespace`, `provenance`, or `confidence`.

## 5. Deployment manifests
- **Dockerfile**: Includes system-level dependencies for `unstructured` and `rdflib`.
- **docker-compose.yaml**: Adds the SEMRAG API service (port 8000).
