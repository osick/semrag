from typing import List, Tuple, Dict, Any
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from semrag.ingestion.extractors.interface import ITripleExtractor


class LLMTripleExtractor(ITripleExtractor):
    """
    Extracts triples using an LLM (existing v5 behavior, refactored).
    Expensive but handles complex/ambiguous text well.
    """

    def __init__(self, llm: Any, max_chars: int = 2000):
        self._llm = llm
        self._max_chars = max_chars

    def extract_triples(self, text: str, doc_name: str = "") -> List[Tuple[str, str, str]]:
        prompt_template = PromptTemplate(
            template="""Extract semantic entities and their relationships from the following text as triples.
Format your response as a JSON list of objects with "subject", "predicate", and "object" keys.

Text: {text}
Output:""",
            input_variables=["text"],
        )
        chain = prompt_template | self._llm | JsonOutputParser()
        try:
            results = chain.invoke({"text": text[:self._max_chars]})
            return [(r["subject"], r["predicate"], r["object"]) for r in results]
        except Exception:
            return []

    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        prompt_template = PromptTemplate(
            template="""Extract all named entities from the following text.
Format your response as a JSON list of objects with "text", "label", "start", and "end" keys.

Text: {text}
Output:""",
            input_variables=["text"],
        )
        chain = prompt_template | self._llm | JsonOutputParser()
        try:
            return chain.invoke({"text": text[:self._max_chars]})
        except Exception:
            return []
