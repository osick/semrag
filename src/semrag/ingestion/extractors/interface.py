from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Any


class ITripleExtractor(ABC):
    """
    Abstract interface for entity/triple extraction from text.
    All extraction strategies (LLM-based, NLP-based, hybrid) implement this.
    """

    @abstractmethod
    def extract_triples(self, text: str, doc_name: str = "") -> List[Tuple[str, str, str]]:
        """
        Extracts (subject, predicate, object) triples from text.
        Returns a list of string 3-tuples.
        """
        pass

    @abstractmethod
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Extracts named entities from text.
        Returns list of dicts with at minimum {"text": str, "label": str, "start": int, "end": int}.
        """
        pass
