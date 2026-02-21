# Graph Algorithms Documentation

The SEMRAG system utilizes advanced graph algorithms for knowledge discovery, summarization, and entity resolution.

## 1. Global Graph Summarization (Community Detection)

### Algorithm: Leiden
The Leiden algorithm is used to detect clusters or "communities" in the knowledge graph.
- **Why**: Leiden is faster and produces more stable communities than the Louvain algorithm.
- **Implementation**: Uses the `cdlib` Python library with `networkx`.
- **Process**:
    1.  The entire graph is loaded into memory as a NetworkX graph.
    2.  Leiden is applied to identify clusters.
    3.  For each cluster, the LLM generates a "Global Summary."
    4.  Summaries are stored back in the graph as special `CommunitySummary` nodes.

## 2. Automated Entity Resolution (De-duplication)

### Algorithm: Fuzzy Matching + LLM Verification
Entity resolution identifies and merges similar nodes (e.g., "Apple Inc." and "Apple").
- **Mechanism**:
    1.  **Fuzzy Matching**: Uses **Jaro-Winkler** similarity (via `jellyfish`) to find candidate duplicate pairs.
    2.  **LLM Verification**: A prompt is sent to the LLM: "Are these two entities the same person, place, or thing?"
    3.  **Merging**: Uses the `apoc.refactor.mergeNodes` Neo4j procedure to canonicalize the graph.

## 3. Metadata-Aware Retrieval

### Reasoning via Metadata
The system performs multi-hop reasoning by filtering retrieval steps by:
- **Namespace**: (e.g., "Legal", "Technical").
- **Provenance**: (e.g., "Manual_v1.pdf", "Legal_RuleSet.ttl").
- **Confidence**: Ensuring only high-confidence extractions reach the final prompt.

## 4. RDF & Ontology Support
- **Ontology Loading**: Parses OWL/RDF/TTL into the Graph Store to establish a formal "Schema-First" model.
- **Deduction**: Basic rule-based deduction (e.g., `SubClassOf`) is implemented using Cypher.

### RDF/Triple Query Example (Cypher)
To find all entities from the 'Legal' namespace and their relationships:
```cypher
MATCH (n:Entity)-[r]->(m:Entity)
WHERE n.namespace = 'Legal' AND r.confidence > 0.8
RETURN n.name, type(r), m.name, r.provenance
```

This query will return only high-confidence legal relationships along with their original source (provenance).

