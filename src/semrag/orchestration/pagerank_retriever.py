from typing import List, Dict, Any
import networkx as nx
import jellyfish
from semrag.graph_store.interface import IGraphStore
from semrag.ingestion.extractors.interface import ITripleExtractor


class PageRankRetriever:
    """
    LinearRAG-inspired two-stage retrieval over a Tri-Graph.

    Stage 1: Entity Activation
      - Extract entities from the query using the NER extractor
      - Find matching Entity nodes in the graph via NER + fuzzy matching

    Stage 2: Personalized PageRank
      - Build a local subgraph around activated entities
      - Run personalized PageRank with query entities as seed nodes
      - Rank Passage nodes by aggregated PageRank score
      - Return top-k passages with their sentence texts
    """

    def __init__(
        self,
        graph_store: IGraphStore,
        entity_extractor: ITripleExtractor,
        top_k: int = 5,
        pagerank_alpha: float = 0.85,
        fuzzy_threshold: float = 0.85,
    ):
        self._graph_store = graph_store
        self._extractor = entity_extractor
        self._top_k = top_k
        self._alpha = pagerank_alpha
        self._fuzzy_threshold = fuzzy_threshold

    def retrieve(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        """
        Full two-stage retrieval pipeline.

        Returns list of dicts: [{"passage_id": str, "score": float, "sentences": [str, ...]}]
        """
        top_k = top_k or self._top_k

        # Stage 1: Entity Activation
        query_entities = self._activate_entities(query)
        if not query_entities:
            return []

        # Stage 2: Build local subgraph and run PageRank
        subgraph = self._build_local_subgraph(query_entities)
        if not subgraph.nodes:
            return []

        personalization = {}
        for node in subgraph.nodes:
            personalization[node] = 0.0
        for e in query_entities:
            node_key = f"entity:{e}"
            if node_key in personalization:
                personalization[node_key] = 1.0 / len(query_entities)

        try:
            pr_scores = nx.pagerank(
                subgraph, alpha=self._alpha, personalization=personalization
            )
        except nx.PowerIterationFailedConvergence:
            pr_scores = {n: 0.0 for n in subgraph.nodes}

        # Aggregate scores at passage level
        passage_scores = self._aggregate_passage_scores(pr_scores, subgraph)

        # Sort and return top-k
        ranked = sorted(passage_scores.items(), key=lambda x: x[1], reverse=True)
        results = []
        for passage_id, score in ranked[:top_k]:
            sentences = self._get_passage_sentences(passage_id)
            results.append({
                "passage_id": passage_id,
                "score": round(score, 4),
                "sentences": sentences,
                "content": " ".join(sentences),
            })
        return results

    def _activate_entities(self, query: str) -> List[str]:
        """
        Extract entity names from the query via NER, then fuzzy-match
        against existing graph Entity nodes.
        """
        extracted = self._extractor.extract_entities(query)
        query_ent_names = [e["text"] for e in extracted]

        if not query_ent_names:
            return []

        # Fetch all entity names from graph
        results = self._graph_store.query("MATCH (e:Entity) RETURN e.name as name")
        graph_names = [r["name"] for r in results if r.get("name")]

        activated = set()
        for q_name in query_ent_names:
            for g_name in graph_names:
                score = jellyfish.jaro_winkler_similarity(
                    q_name.lower(), g_name.lower()
                )
                if score >= self._fuzzy_threshold:
                    activated.add(g_name)

        return list(activated)

    def _build_local_subgraph(self, entity_names: List[str]) -> nx.DiGraph:
        """
        Build a NetworkX subgraph around the activated entities.
        Includes 2-hop neighborhood: entities -> sentences -> passages,
        plus co-occurring entities.
        """
        G = nx.DiGraph()

        for name in entity_names:
            entity_ref = f"entity:{name}"
            G.add_node(entity_ref, type="entity")

            # Entity -> Sentence edges
            cypher = (
                "MATCH (e:Entity {name: $name})-[:APPEARS_IN]->(s:Sentence) "
                "RETURN s.id as sid, s.text as text"
            )
            results = self._graph_store.query(cypher, {"name": name})
            for r in results:
                sid = r["sid"]
                G.add_node(sid, type="sentence", text=r.get("text", ""))
                G.add_edge(entity_ref, sid, rel="APPEARS_IN")

                # Sentence -> Passage edges
                cypher2 = (
                    "MATCH (s:Sentence {id: $sid})-[:PART_OF]->(p:Passage) "
                    "RETURN p.id as pid"
                )
                passages = self._graph_store.query(cypher2, {"sid": sid})
                for p in passages:
                    pid = p["pid"]
                    G.add_node(pid, type="passage")
                    G.add_edge(sid, pid, rel="PART_OF")

            # Co-occurring entities (bridge to related entities)
            cypher3 = (
                "MATCH (e:Entity {name: $name})-[:CO_OCCURS]-(e2:Entity) "
                "RETURN e2.name as name2"
            )
            co_entities = self._graph_store.query(cypher3, {"name": name})
            for ce in co_entities:
                co_ref = f"entity:{ce['name2']}"
                if co_ref not in G:
                    G.add_node(co_ref, type="entity")
                G.add_edge(entity_ref, co_ref, rel="CO_OCCURS")
                G.add_edge(co_ref, entity_ref, rel="CO_OCCURS")

        return G

    def _aggregate_passage_scores(self, pr_scores: Dict[str, float], graph: nx.DiGraph) -> Dict[str, float]:
        """Aggregate PageRank scores of sentences/entities into their parent passages."""
        passage_scores: Dict[str, float] = {}

        for node, score in pr_scores.items():
            if node.startswith("passage:"):
                passage_scores[node] = passage_scores.get(node, 0.0) + score
            elif node.startswith("sentence:"):
                # Find parent passage via graph edges
                for _, target, data in graph.out_edges(node, data=True):
                    if target.startswith("passage:"):
                        passage_scores[target] = passage_scores.get(target, 0.0) + score

        return passage_scores

    def _get_passage_sentences(self, passage_id: str) -> List[str]:
        """Retrieve all sentence texts belonging to a passage, ordered by index."""
        cypher = (
            "MATCH (s:Sentence)-[:PART_OF]->(p:Passage {id: $pid}) "
            "RETURN s.text as text ORDER BY s.index"
        )
        results = self._graph_store.query(cypher, {"pid": passage_id})
        return [r["text"] for r in results if r.get("text")]
