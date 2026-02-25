from typing import List, Tuple, Dict, Any, Optional, Set
from semrag.ingestion.extractors.interface import ITripleExtractor


class SpaCyGLiNERExtractor(ITripleExtractor):
    """
    LLM-free triple extraction using spaCy NER + dependency parsing,
    enhanced with GLiNER for zero-shot domain-adaptive NER.

    Pipeline:
      1. GLiNER (or spaCy NER) detects entities
      2. spaCy dependency parsing finds syntactic arcs connecting entities
      3. Subject-Verb-Object patterns are extracted as triples
    """

    def __init__(
        self,
        spacy_model: str = "en_core_web_sm",
        gliner_model: str = "urchade/gliner_medium-v2.1",
        entity_labels: List[str] = None,
        use_gliner: bool = True,
        confidence_threshold: float = 0.5,
    ):
        """
        Args:
            spacy_model: spaCy model name for dependency parsing + NER.
            gliner_model: GLiNER model name for zero-shot NER.
            entity_labels: REQUIRED list of domain-specific entity types for GLiNER.
                           No defaults — caller must specify labels for their domain.
            use_gliner: Whether to use GLiNER for NER (True) or spaCy-only (False).
            confidence_threshold: Minimum confidence for GLiNER entity predictions.
        """
        if entity_labels is None:
            raise ValueError(
                "entity_labels must be provided for domain-specific NER. "
                "Example: ['Person', 'Organization', 'Technology', 'Product']"
            )
        self._spacy_model_name = spacy_model
        self._gliner_model_name = gliner_model
        self._entity_labels = entity_labels
        self._use_gliner = use_gliner
        self._confidence_threshold = confidence_threshold
        self._nlp = None
        self._gliner = None

    def _ensure_models_loaded(self) -> None:
        """Lazy-load models on first use to avoid import-time overhead."""
        if self._nlp is None:
            import spacy
            self._nlp = spacy.load(self._spacy_model_name)
        if self._use_gliner and self._gliner is None:
            from gliner import GLiNER
            self._gliner = GLiNER.from_pretrained(self._gliner_model_name)

    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract entities using GLiNER (if enabled) merged with spaCy NER.
        GLiNER provides zero-shot domain-adaptive NER.
        spaCy provides dependency-aware NER as complement/fallback.
        """
        self._ensure_models_loaded()
        entities = []

        # Phase 1: GLiNER zero-shot NER
        if self._use_gliner and self._gliner is not None:
            gliner_results = self._gliner.predict_entities(
                text, self._entity_labels, threshold=self._confidence_threshold
            )
            for ent in gliner_results:
                entities.append({
                    "text": ent["text"],
                    "label": ent["label"],
                    "start": ent["start"],
                    "end": ent["end"],
                    "score": ent.get("score", 1.0),
                    "source": "gliner",
                })

        # Phase 2: spaCy NER
        doc = self._nlp(text)
        for ent in doc.ents:
            entities.append({
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char,
                "score": 1.0,
                "source": "spacy",
            })

        return self._deduplicate_entities(entities)

    def extract_triples(self, text: str, doc_name: str = "") -> List[Tuple[str, str, str]]:
        """
        Full pipeline: entities + dependency parsing -> SVO triples.

        Strategy:
          1. Extract entities via GLiNER + spaCy
          2. Parse dependency tree with spaCy
          3. For each sentence, find Subject-Verb-Object patterns
             where S and O overlap with detected entities
          4. Return (entity_subject, verb_lemma, entity_object) triples
        """
        self._ensure_models_loaded()
        doc = self._nlp(text)
        entities = self.extract_entities(text)
        entity_spans = {(e["start"], e["end"]): e["text"] for e in entities}

        triples = []
        for sent in doc.sents:
            sent_triples = self._extract_svo_from_sentence(sent, entity_spans)
            triples.extend(sent_triples)

        return triples

    def _extract_svo_from_sentence(
        self, sent, entity_spans: Dict[Tuple[int, int], str]
    ) -> List[Tuple[str, str, str]]:
        """
        Extract Subject-Verb-Object triples from a spaCy Span using dependency arcs.

        Walks the dependency tree:
          - nsubj / nsubjpass -> subject
          - ROOT verb -> predicate
          - dobj / attr / pobj -> object
        Maps token spans back to detected entity texts where possible.
        """
        triples = []
        for token in sent:
            if token.dep_ == "ROOT" and token.pos_ == "VERB":
                subjects = self._find_dependents(token, {"nsubj", "nsubjpass"})
                objects = self._find_dependents(token, {"dobj", "attr", "pobj"})

                # Also look for objects via prepositions attached to the verb
                for child in token.children:
                    if child.dep_ == "prep":
                        prep_objects = self._find_dependents(child, {"pobj"})
                        objects.extend(prep_objects)

                for subj in subjects:
                    subj_entity = self._resolve_to_entity(subj, entity_spans)
                    for obj in objects:
                        obj_entity = self._resolve_to_entity(obj, entity_spans)
                        if subj_entity and obj_entity and subj_entity != obj_entity:
                            predicate = self._build_predicate(token)
                            triples.append((subj_entity, predicate, obj_entity))
        return triples

    def _find_dependents(self, token, dep_labels: Set[str]) -> list:
        """Find direct children with given dependency labels."""
        results = []
        for child in token.children:
            if child.dep_ in dep_labels:
                results.append(child)
        return results

    def _resolve_to_entity(self, token, entity_spans: Dict[Tuple[int, int], str]) -> Optional[str]:
        """
        Map a dependency-tree token back to a named entity span.
        If the token's character offsets overlap with any entity span, return entity text.
        Otherwise, return the noun chunk text as fallback.
        """
        # Get span from subtree for better coverage
        subtree_tokens = list(token.subtree)
        if subtree_tokens:
            span_start = subtree_tokens[0].idx
            span_end = subtree_tokens[-1].idx + len(subtree_tokens[-1].text)
        else:
            span_start = token.idx
            span_end = token.idx + len(token.text)

        for (es, ee), entity_text in entity_spans.items():
            # Check overlap
            if span_start <= es < span_end or es <= span_start < ee:
                return entity_text

        # Fallback: return noun phrase from subtree
        phrase = " ".join([t.text for t in subtree_tokens]).strip()
        return phrase if phrase else None

    @staticmethod
    def _build_predicate(verb_token) -> str:
        """Build predicate string from verb + auxiliary/preposition children."""
        parts = []
        for child in verb_token.children:
            if child.dep_ in ("aux", "auxpass"):
                parts.append(child.lemma_)
        parts.append(verb_token.lemma_)
        for child in verb_token.children:
            if child.dep_ == "prep":
                parts.append(child.text)
        return "_".join(parts).upper()

    @staticmethod
    def _deduplicate_entities(entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Deduplicate entities from GLiNER and spaCy by span overlap.
        Prefer GLiNER results when spans overlap (higher specificity from zero-shot labels).
        """
        sorted_ents = sorted(entities, key=lambda e: (e["start"], -e.get("score", 0)))
        deduped = []
        last_end = -1
        for ent in sorted_ents:
            if ent["start"] >= last_end:
                deduped.append(ent)
                last_end = ent["end"]
        return deduped
