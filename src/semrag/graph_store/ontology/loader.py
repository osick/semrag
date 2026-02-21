import rdflib
from typing import List, Tuple, Dict, Any
from rdflib import Graph, RDF, RDFS, OWL
from semrag.graph_store.interface import IGraphStore
from semrag.api.models import GraphNode, EnrichedTriple

class OntologyLoader:
    """
    Parses and ingests enterprise ontologies (OWL, RDF, TTL).
    Establishes the schema and rule sets in the Graph Store.
    """
    
    def __init__(self, graph_store: IGraphStore):
        self._graph_store = graph_store
        self._rdf_graph = Graph()

    def load_ontology(self, file_path: str, format: str = "turtle", namespace: str = "Enterprise") -> None:
        """
        Parses an ontology file and creates class/property nodes in the Graph Store.
        """
        print(f"Parsing ontology: {file_path}")
        self._rdf_graph.parse(file_path, format=format)
        
        # 1. Extract Classes (Entity Types)
        classes = self._rdf_graph.subjects(RDF.type, OWL.Class)
        for cls in classes:
            name = str(cls).split("/")[-1].split("#")[-1]
            node = GraphNode(id=name, name=name, type="Class", uri=str(cls), provenance=file_path, namespace=namespace)
            # Create a "Class" node in the graph
            self._graph_store.add_triples([(name, "TYPE_OF", "OwlClass")], provenance=file_path, namespace=namespace)

        # 2. Extract Subclass relationships (Hierarchies)
        subclasses = self._rdf_graph.subject_objects(RDFS.subClassOf)
        for sub, sup in subclasses:
            sub_name = str(sub).split("/")[-1].split("#")[-1]
            sup_name = str(sup).split("/")[-1].split("#")[-1]
            self._graph_store.add_triples([(sub_name, "SUBCLASS_OF", sup_name)], provenance=file_path, namespace=namespace)

        # 3. Extract ObjectProperties (Relationships)
        properties = self._rdf_graph.subjects(RDF.type, OWL.ObjectProperty)
        for prop in properties:
            name = str(prop).split("/")[-1].split("#")[-1]
            self._graph_store.add_triples([(name, "TYPE_OF", "ObjectProperty")], provenance=file_path, namespace=namespace)

    def extract_rdf_triples(self, file_path: str, format: str = "turtle", namespace: str = "Enterprise") -> None:
        """
        Directly loads external RDF triples into the Graph Store.
        """
        temp_graph = Graph()
        temp_graph.parse(file_path, format=format)
        
        triples = []
        for s, p, o in temp_graph:
            s_name = str(s).split("/")[-1].split("#")[-1]
            p_name = str(p).split("/")[-1].split("#")[-1]
            o_name = str(o).split("/")[-1].split("#")[-1]
            triples.append((s_name, p_name, o_name))
        
        self._graph_store.add_triples(triples, provenance=file_path, namespace=namespace)
