from typing import List, Dict, Any, Tuple
from neo4j import GraphDatabase
from .interface import IGraphStore
from semrag.api.models import EnrichedTriple

class Neo4jGraphStore(IGraphStore):
    """
    Neo4j implementation of the IGraphStore interface with Metadata support.
    """
    
    def __init__(self, uri: str, user: str, password: str):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def query(self, cypher_query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        with self._driver.session() as session:
            result = session.run(cypher_query, params or {})
            return [record.data() for record in result]

    def add_enriched_triple(self, triple: EnrichedTriple) -> None:
        """
        Adds a triple with full metadata enrichment to Neo4j.
        """
        cypher = """
        MERGE (s:Entity {name: $s_name})
        SET s.uri = $s_uri, s.provenance = $s_prov, s.namespace = $s_ns, s.confidence = $s_conf
        MERGE (o:Entity {name: $o_name})
        SET o.uri = $o_uri, o.provenance = $o_prov, o.namespace = $o_ns, o.confidence = $o_conf
        WITH s, o
        CALL apoc.merge.relationship(s, $predicate, {provenance: $p_prov, namespace: $p_ns, confidence: $p_conf}, {}, o) YIELD rel
        RETURN count(rel)
        """
        params = {
            "s_name": triple.subject.name, "s_uri": triple.subject.uri, "s_prov": triple.subject.provenance, 
            "s_ns": triple.subject.namespace, "s_conf": triple.subject.confidence,
            "o_name": triple.object.name, "o_uri": triple.object.uri, "o_prov": triple.object.provenance, 
            "o_ns": triple.object.namespace, "o_conf": triple.object.confidence,
            "predicate": triple.predicate, "p_prov": triple.provenance, "p_ns": triple.namespace, "p_conf": triple.confidence
        }
        with self._driver.session() as session:
            session.run(cypher, **params)

    def add_triples(self, triples: List[Tuple[str, str, str]], provenance: str = "Unknown", namespace: str = "Default") -> None:
        """Adds simple triples with metadata defaults."""
        for s, p, o in triples:
            cypher = f"MERGE (s:Entity {{name: '{s}'}}) SET s.provenance = $prov, s.namespace = $ns " \
                     f"MERGE (o:Entity {{name: '{o}'}}) SET o.provenance = $prov, o.namespace = $ns " \
                     f"WITH s, o CALL apoc.merge.relationship(s, '{p}', {{provenance: $prov, namespace: $ns}}, {{}}, o) YIELD rel RETURN count(rel)"
            with self._driver.session() as session:
                session.run(cypher, prov=provenance, ns=namespace)

    def query_by_metadata(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filters nodes by metadata properties."""
        where_clause = " AND ".join([f"n.{k} = ${k}" for k in filters.keys()])
        cypher = f"MATCH (n) WHERE {where_clause} RETURN n"
        return self.query(cypher, filters)

    def clear(self) -> None:
        with self._driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")

    def close(self) -> None:
        self._driver.close()
