from typing import TypedDict, List, Dict, Any, Union
from langgraph.graph import StateGraph, END
from semrag.vector_store.qdrant_wrapper import QdrantVectorStore
from semrag.graph_store.interface import IGraphStore

class AgentState(TypedDict):
    """
    State definition for the SEMRAG LangGraph workflow.
    """
    query: str
    chunks: List[Dict[str, Any]]
    entities: List[Dict[str, Any]]
    context: str
    answer: str

class SEMRAGGraph:
    """
    Orchestrates the Hybrid Retrieval workflow using LangGraph.
    """
    
    def __init__(self, vector_store: QdrantVectorStore, graph_store: IGraphStore, llm: Any, embedding_model: Any):
        self._vector_store = vector_store
        self._graph_store = graph_store
        self._llm = llm
        self._embedding_model = embedding_model
        self._workflow = self._setup_workflow()

    def _setup_workflow(self) -> StateGraph:
        """Define the nodes and edges of the retrieval graph."""
        workflow = StateGraph(AgentState)
        
        # 1. Add Nodes
        workflow.add_node("retrieve_vector", self.retrieve_vector)
        workflow.add_node("retrieve_graph", self.retrieve_graph)
        workflow.add_node("augment_context", self.augment_context)
        workflow.add_node("generate_answer", self.generate_answer)
        
        # 2. Add Edges (Simple linear workflow for now)
        workflow.set_entry_point("retrieve_vector")
        workflow.add_edge("retrieve_vector", "retrieve_graph")
        workflow.add_edge("retrieve_graph", "augment_context")
        workflow.add_edge("augment_context", "generate_answer")
        workflow.add_edge("generate_answer", END)
        
        return workflow.compile()

    def retrieve_vector(self, state: AgentState) -> Dict[str, Any]:
        """Retrieves top-k similar chunks from Qdrant."""
        query_vector = self._embedding_model.embed_query(state["query"])
        chunks = self._vector_store.search(query_vector, top_k=5)
        return {"chunks": chunks}

    def retrieve_graph(self, state: AgentState) -> Dict[str, Any]:
        """Retrieves related entities and relationships from the graph store."""
        # Simple extraction logic: find all relationships for entities in query
        # This will be replaced by more sophisticated Cypher traversal.
        query_entities = [word.strip(",") for word in state["query"].split() if word[0].isupper()]
        entities = []
        for entity in query_entities:
            cypher = f"MATCH (n:Entity {{name: '{entity}'}})-[r]->(m) RETURN n.name, type(r), m.name"
            entities.extend(self._graph_store.query(cypher))
        return {"entities": entities}

    def augment_context(self, state: AgentState) -> Dict[str, Any]:
        """Blends vector and graph context."""
        context_parts = []
        if state["chunks"]:
            context_parts.append("Vector Store Results:
" + "
".join([c["content"] for c in state["chunks"]]))
        if state["entities"]:
            context_parts.append("Graph Store Relationships:
" + "
".join([str(e) for e in state["entities"]]))
        
        return {"context": "

".join(context_parts)}

    def generate_answer(self, state: AgentState) -> Dict[str, Any]:
        """Generates the final response using the augmented context."""
        prompt = f"Using the following context, answer the query: {state['query']}

Context:
{state['context']}"
        answer = self._llm.invoke(prompt)
        return {"answer": answer}

    def run(self, query: str) -> Dict[str, Any]:
        """Executes the SEMRAG workflow for a given query."""
        initial_state = {
            "query": query,
            "chunks": [],
            "entities": [],
            "context": "",
            "answer": ""
        }
        return self._workflow.invoke(initial_state)
