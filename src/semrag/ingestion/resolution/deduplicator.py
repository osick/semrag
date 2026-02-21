from typing import List, Dict, Any, Tuple
import jellyfish # Using jellyfish for fuzzy matching
from semrag.graph_store.interface import IGraphStore

class EntityResolutionModule:
    """
    Automated LLM-based entity resolution (de-duplication).
    Identifies similar nodes and merges them into a canonical node.
    """
    
    def __init__(self, graph_store: IGraphStore, llm: Any, similarity_threshold: float = 0.85):
        self._graph_store = graph_store
        self._llm = llm
        self._threshold = similarity_threshold

    def resolve_duplicates(self) -> List[Tuple[str, str]]:
        """
        1. Fetches all node names from the graph.
        2. Identifies similar node names using fuzzy matching.
        3. Prompts the LLM to decide if they are the same entity.
        4. Merges nodes in the Graph Store.
        """
        # 1. Fetch all nodes
        cypher = "MATCH (n:Entity) RETURN n.name as name"
        results = self._graph_store.query(cypher)
        names = [r['name'] for r in results]
        
        merges = []
        
        # 2. Fuzzy matching (Levenshtein distance)
        for i, name1 in enumerate(names):
            for j, name2 in enumerate(names[i+1:]):
                score = jellyfish.jaro_winkler_similarity(name1, name2)
                
                if score >= self._threshold:
                    # 3. Prompt LLM to verify
                    if self._verify_with_llm(name1, name2):
                        print(f"Merging entities: {name1} and {name2} (Score: {score:.2f})")
                        self._graph_store.merge_nodes(name1, name2)
                        merges.append((name1, name2))
        
        return merges

    def _verify_with_llm(self, name1: str, name2: str) -> bool:
        """
        Prompts the LLM to decide if two entity names refer to the same entity.
        """
        prompt = (
            f"Are the following two entity names referring to the same person, place, or thing?\n\n"
            f"1. {name1}\n2. {name2}\n\n"
            f"Answer only 'Yes' or 'No'."
        )
        response = self._llm.invoke(prompt)
        return "yes" in response.lower()
