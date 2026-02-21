from typing import List, Dict, Any, Tuple
import redis
from .interface import IGraphStore

class FalkorDBGraphStore(IGraphStore):
    """
    FalkorDB implementation of the IGraphStore interface.
    Uses the redis-py driver with Cypher commands over Redis protocol.
    """
    
    def __init__(self, host: str, port: int, graph_id: str = "semrag_graph"):
        self._redis = redis.Redis(host=host, port=port, decode_responses=True)
        self._graph_id = graph_id

    def query(self, cypher_query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Executes a Cypher query on FalkorDB.
        FalkorDB expects queries via 'GRAPH.QUERY [graph_id] [query]'.
        Note: FalkorDB params are passed as part of the query string or serialized separately.
        """
        # Simplistic implementation for initial TDD
        # In a production setting, use a library or properly formatted params.
        command = f"GRAPH.QUERY {self._graph_id} '{cypher_query}'"
        result = self._redis.execute_command(command)
        return self._format_result(result)

    def add_triples(self, triples: List[Tuple[str, str, str]]) -> None:
        """
        Adds (subject, predicate, object) triples.
        Standardizes the Cypher command to work for FalkorDB.
        """
        for s, p, o in triples:
            cypher = f"MERGE (s:Entity {{name: '{s}'}}) MERGE (o:Entity {{name: '{o}'}}) MERGE (s)-[:{p}]->(o)"
            command = f"GRAPH.QUERY {self._graph_id} '{cypher}'"
            self._redis.execute_command(command)

    def _format_result(self, raw_result: List[Any]) -> List[Dict[str, Any]]:
        # Basic formatter for demonstration
        # FalkorDB raw responses are complex and vary based on query type.
        return [{"raw": raw_result}]

    def clear(self) -> None:
        self._redis.execute_command(f"GRAPH.DELETE {self._graph_id}")

    def close(self) -> None:
        self._redis.close()
