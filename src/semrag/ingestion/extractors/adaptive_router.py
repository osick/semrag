from typing import List, Tuple, Dict, Any
from semrag.ingestion.extractors.interface import ITripleExtractor


class AdaptiveExtractionRouter(ITripleExtractor):
    """
    Routes text to the optimal extraction strategy based on complexity scoring.
    Fast NLP pipeline for simple/medium text, LLM for complex passages.

    Complexity is scored via: sentence length, entity density,
    dependency tree depth, passive voice ratio, and conjunction density.
    """

    def __init__(
        self,
        nlp_extractor: ITripleExtractor,
        llm_extractor: ITripleExtractor,
        complexity_threshold: float = 0.6,
        chunk_size: int = 1000,
    ):
        self._nlp_extractor = nlp_extractor
        self._llm_extractor = llm_extractor
        self._complexity_threshold = complexity_threshold
        self._chunk_size = chunk_size
        self._analyzer = None  # Lazy-loaded lightweight spaCy for scoring

    def _ensure_analyzer_loaded(self) -> None:
        if self._analyzer is None:
            import spacy
            self._analyzer = spacy.load("en_core_web_sm")

    def score_complexity(self, text: str) -> float:
        """
        Scores text complexity on a 0.0-1.0 scale.

        Factors (each normalized to 0-1, weighted average):
          1. avg_sentence_length   (0.25) - long sentences are harder to parse
          2. entity_density        (0.20) - many entities = more potential relations
          3. subordination_depth   (0.25) - deep dep trees = complex structure
          4. passive_voice_ratio   (0.15) - passive voice inverts SVO
          5. conjunction_density   (0.15) - conjunctions create ambiguous attachments
        """
        self._ensure_analyzer_loaded()
        doc = self._analyzer(text)

        sentences = list(doc.sents)
        if not sentences:
            return 0.0

        token_count = len(doc)
        if token_count == 0:
            return 0.0

        # Factor 1: Average sentence length (normalized: 40+ words = 1.0)
        avg_sent_len = token_count / len(sentences)
        f_sent_len = min(avg_sent_len / 40.0, 1.0)

        # Factor 2: Entity density (entities per 100 tokens)
        entity_count = len(doc.ents)
        f_entity_density = min((entity_count / token_count) * 10, 1.0)

        # Factor 3: Max dependency tree depth (normalized: depth 10+ = 1.0)
        max_depth = 0
        for token in doc:
            depth = 0
            current = token
            while current.head != current:
                depth += 1
                current = current.head
                if depth > 20:
                    break
            max_depth = max(max_depth, depth)
        f_sub_depth = min(max_depth / 10.0, 1.0)

        # Factor 4: Passive voice ratio
        passive_count = sum(1 for t in doc if t.dep_ in ("nsubjpass", "auxpass"))
        verb_count = sum(1 for t in doc if t.pos_ == "VERB") or 1
        f_passive = min(passive_count / verb_count, 1.0)

        # Factor 5: Conjunction density (coordinating + subordinating)
        conj_count = sum(1 for t in doc if t.dep_ in ("cc", "mark", "advcl", "relcl"))
        f_conj = min(conj_count / len(sentences), 1.0)

        score = (
            0.25 * f_sent_len
            + 0.20 * f_entity_density
            + 0.25 * f_sub_depth
            + 0.15 * f_passive
            + 0.15 * f_conj
        )
        return round(min(score, 1.0), 3)

    def extract_triples(self, text: str, doc_name: str = "") -> List[Tuple[str, str, str]]:
        """
        Splits text into chunks, scores each, and routes to NLP or LLM extractor.
        """
        chunks = self._split_text(text)
        all_triples = []

        for chunk in chunks:
            complexity = self.score_complexity(chunk)
            if complexity >= self._complexity_threshold:
                triples = self._llm_extractor.extract_triples(chunk, doc_name)
            else:
                triples = self._nlp_extractor.extract_triples(chunk, doc_name)
            all_triples.extend(triples)

        return all_triples

    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Entity extraction always uses the NLP extractor (fast path)."""
        return self._nlp_extractor.extract_entities(text)

    def _split_text(self, text: str) -> List[str]:
        """Split text into paragraph-sized chunks for per-segment routing."""
        paragraphs = text.split("\n\n")
        chunks = []
        current = ""
        for para in paragraphs:
            if len(current) + len(para) > self._chunk_size:
                if current:
                    chunks.append(current.strip())
                current = para
            else:
                current = current + "\n\n" + para if current else para
        if current.strip():
            chunks.append(current.strip())
        return chunks or [text]
