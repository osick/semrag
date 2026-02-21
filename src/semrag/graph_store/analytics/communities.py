import networkx as nx
from cdlib import algorithms
from typing import List, Dict, Any, Tuple
from semrag.graph_store.interface import IGraphStore

class CommunityDetectionEngine:
    """
    Identifies communities in the knowledge graph using the Leiden algorithm.
    Used for global graph summarization.
    """
    
    def __init__(self, graph_store: IGraphStore, llm: Any):
        self._graph_store = graph_store
        self._llm = llm

    def generate_global_summaries(self) -> List[Dict[str, Any]]:
        """
        1. Loads the entire graph.
        2. Detects communities.
        3. Generates summaries for each community using the LLM.
        4. Stores summaries back in the graph.
        """
        # 1. Fetch all triples
        triples = self._graph_store.get_all_triples()
        if not triples:
            return []

        # 2. Build NetworkX graph
        G = nx.Graph()
        for s, p, o in triples:
            G.add_edge(s, o, label=p)

        # 3. Community Detection (Leiden)
        comms = algorithms.leiden(G)
        summaries = []

        # 4. Summarize each community
        for i, community in enumerate(comms.communities):
            # Extract subgraph context for the community
            context = "\n".join([f"{n1} -[{G[n1][n2]['label']}]-> {n2}" for n1, n2 in G.edges(community)])
            
            prompt = (
                f"Summarize the following group of related entities and relationships. "
                f"Focus on the main themes and importance of this cluster.\n\n"
                f"Context:\n{context[:2000]}"
            )
            summary_text = self._llm.invoke(prompt)
            
            summary_node = {
                "community_id": f"community_{i}",
                "summary": summary_text,
                "entities": community
            }
            summaries.append(summary_node)
            
            # 5. Store summary in the graph (simplified)
            self._graph_store.query(
                "MERGE (c:Community {id: $id}) SET c.summary = $summary",
                {"id": f"community_{i}", "summary": summary_text}
            )

        return summaries
