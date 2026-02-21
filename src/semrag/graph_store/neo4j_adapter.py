from typing import List, Dict, Any, Tuple
from neo4j import GraphDatabase
from .interface import IGraphStore

class Neo4jGraphStore(IGraphStore):
    """
    Neo4j implementation of the IGraphStore interface.
    Uses the official neo4j Python driver.
    """
    
    def __init__(self, uri: str, user: str, password: str):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def query(self, cypher_query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        with self._driver.session() as session:
            result = session.run(cypher_query, params or {})
            return [record.data() for record in result]

    def add_triples(self, triples: List[Tuple[str, str, str]]) -> None:
        """
        Adds (subject, predicate, object) triples.
        Standardizes the Cypher command to work for Neo4j.
        """
        cypher = """
        UNWIND $triples AS triple
        MERGE (s:Entity {name: triple[0]})
        MERGE (o:Entity {name: triple[2]})
        WITH s, o, triple
        CALL apoc.merge.relationship(s, triple[1], {}, {}, o) YIELD rel
        RETURN count(rel)
        """
        with self._driver.session() as session:
            session.run(cypher, triples=triples)

    def clear(self) -> None:
        with self._driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")

    def close(self) -> None:
        self._driver.close()
