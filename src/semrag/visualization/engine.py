from pyvis.network import Network
from typing import List, Dict, Any, Tuple
import os

class VisualizationEngine:
    """
    Generates an interactive HTML dashboard using Pyvis.
    Visualizes the entities (Graph) and chunks (Vector) in one view.
    """
    
    def __init__(self, output_path: str = "semrag_dashboard.html"):
        self._output_path = output_path
        self._net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white", notebook=False)
        self._net.barnes_hut()

    def add_graph_data(self, triples: List[Tuple[str, str, str]]) -> None:
        """Adds (subject, predicate, object) triples to the Pyvis network."""
        for s, p, o in triples:
            self._net.add_node(s, label=s, title=f"Entity: {s}", color="#97c2fc")
            self._net.add_node(o, label=o, title=f"Entity: {o}", color="#97c2fc")
            self._net.add_edge(s, o, label=p, title=p, color="#97c2fc")

    def add_vector_data(self, chunks: List[Dict[str, Any]]) -> None:
        """Adds semantic chunks from the Vector Store as nodes."""
        for i, chunk in enumerate(chunks):
            node_id = f"chunk_{i}"
            content = chunk.get("content", "No content")
            source = chunk.get("source", "Unknown")
            
            self._net.add_node(
                node_id, 
                label=f"Chunk {i}", 
                title=f"Source: {source}

{content[:200]}...",
                color="#fb7e81",
                shape="square"
            )
            
            # Optionally add similarity edges between chunks (if weights are available)
            # This is a bit more complex as it requires pairwise distance.

    def generate(self) -> str:
        """Generates the final HTML file and returns the path."""
        self._net.save_graph(self._output_path)
        print(f"Visualization dashboard generated at: {os.path.abspath(self._output_path)}")
        return self._output_path
