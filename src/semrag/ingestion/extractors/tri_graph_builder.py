import re
from typing import List, Dict, Any, Tuple, Optional
from semrag.ingestion.extractors.interface import ITripleExtractor
from semrag.graph_store.interface import IGraphStore


class TriGraphBuilder:
    """
    LinearRAG-inspired Tri-Graph builder (ICLR 2026).

    Constructs a heterogeneous graph with three node types:
      - Entity nodes (extracted via NER)
      - Sentence nodes (each sentence is a node)
      - Passage nodes (each chunk/passage is a node)

    Edges are structural, NOT relational:
      - Entity --APPEARS_IN--> Sentence
      - Sentence --PART_OF--> Passage
      - Entity --CO_OCCURS--> Entity (within same sentence)

    No LLM calls required. No relation extraction.
    Graph construction cost is purely NER + sentence splitting.
    """

    def __init__(
        self,
        entity_extractor: ITripleExtractor,
        graph_store: IGraphStore,
    ):
        self._extractor = entity_extractor
        self._graph_store = graph_store

    def build_tri_graph(self, text: str, doc_name: str, sentences: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Builds the tri-graph for a document.

        Returns:
            Dict with counts: {"entities": int, "sentences": int, "passages": int, "edges": int}
        """
        if sentences is None:
            sentences = self._split_sentences(text)

        # Create passage node
        passage_id = f"passage:{doc_name}"
        self._create_passage_node(passage_id, doc_name, text[:500])

        edge_count = 0
        all_entity_names = set()

        for idx, sentence in enumerate(sentences):
            if not sentence.strip():
                continue

            # Create sentence node
            sentence_id = f"sentence:{doc_name}:{idx}"
            self._create_sentence_node(sentence_id, sentence, doc_name, idx)

            # Link sentence -> passage
            self._create_edge("Sentence", "id", sentence_id, "PART_OF", "Passage", "id", passage_id)
            edge_count += 1

            # Extract entities from this sentence
            entities = self._extractor.extract_entities(sentence)
            entity_names_in_sent = []

            for ent in entities:
                entity_name = ent["text"]
                entity_label = ent.get("label", "UNKNOWN")
                all_entity_names.add(entity_name)
                entity_names_in_sent.append(entity_name)

                # Create entity node (MERGE = idempotent)
                self._create_entity_node(entity_name, entity_label, doc_name)

                # Link entity -> sentence
                self._create_edge("Entity", "name", entity_name, "APPEARS_IN", "Sentence", "id", sentence_id)
                edge_count += 1

            # Co-occurrence edges between entities in same sentence
            for i, e1 in enumerate(entity_names_in_sent):
                for e2 in entity_names_in_sent[i + 1:]:
                    if e1 != e2:
                        self._create_edge("Entity", "name", e1, "CO_OCCURS", "Entity", "name", e2)
                        edge_count += 1

        return {
            "entities": len(all_entity_names),
            "sentences": len([s for s in sentences if s.strip()]),
            "passages": 1,
            "edges": edge_count,
        }

    def _create_passage_node(self, passage_id: str, doc_name: str, preview: str) -> None:
        cypher = (
            "MERGE (p:Passage {id: $id}) "
            "SET p.doc_name = $doc_name, p.preview = $preview"
        )
        self._graph_store.query(cypher, {"id": passage_id, "doc_name": doc_name, "preview": preview})

    def _create_sentence_node(self, sentence_id: str, text: str, doc_name: str, index: int) -> None:
        cypher = (
            "MERGE (s:Sentence {id: $id}) "
            "SET s.text = $text, s.doc_name = $doc_name, s.index = $index"
        )
        self._graph_store.query(cypher, {
            "id": sentence_id, "text": text[:500], "doc_name": doc_name, "index": index
        })

    def _create_entity_node(self, name: str, label: str, doc_name: str) -> None:
        cypher = (
            "MERGE (e:Entity {name: $name}) "
            "SET e.label = $label, e.provenance = $doc_name"
        )
        self._graph_store.query(cypher, {"name": name, "label": label, "doc_name": doc_name})

    def _create_edge(
        self,
        src_label: str, src_key: str, src_val: str,
        rel_type: str,
        tgt_label: str, tgt_key: str, tgt_val: str,
    ) -> None:
        """Creates a typed edge using MERGE for idempotency."""
        cypher = (
            f"MATCH (s:{src_label} {{{src_key}: $s_val}}), (t:{tgt_label} {{{tgt_key}: $t_val}}) "
            f"MERGE (s)-[:{rel_type}]->(t)"
        )
        self._graph_store.query(cypher, {"s_val": src_val, "t_val": tgt_val})

    @staticmethod
    def _split_sentences(text: str) -> List[str]:
        """Split text on sentence boundaries."""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
