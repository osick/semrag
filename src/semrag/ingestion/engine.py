import os
import io
from typing import List, Dict, Any, Tuple, Union, IO
from unstructured.partition.auto import partition
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from semrag.graph_store.interface import IGraphStore
from semrag.vector_store.qdrant_wrapper import QdrantVectorStore

class IngestionEngine:
    """
    Unified engine for multi-format document ingestion (v5).
    Supports local files, remote URLs, and in-memory streams.
    """
    
    def __init__(self, graph_store: IGraphStore, vector_store: QdrantVectorStore, embedding_model: Any, llm: Any = None):
        self._graph_store = graph_store
        self._vector_store = vector_store
        self._embedding_model = embedding_model
        self._llm = llm
        self._text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )

    def ingest_file(self, file_path: str) -> None:
        """Ingests a file from a local filesystem path."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        elements = partition(filename=file_path)
        text = "\n\n".join([str(el) for el in elements])
        self._process_text(text, doc_name=os.path.basename(file_path))

    def ingest_stream(self, file_stream: IO[bytes], file_name: str) -> None:
        """Ingests a document from an in-memory byte stream (e.g., FastAPI UploadFile)."""
        # 'unstructured' partition can handle file-like objects
        elements = partition(file=file_stream)
        text = "\n\n".join([str(el) for el in elements])
        self._process_text(text, doc_name=file_name)

    def _process_text(self, text: str, doc_name: str) -> None:
        """Core logic for chunking, embedding, and triple extraction."""
        # 1. Chunking
        chunks = self._text_splitter.split_text(text)
        
        # 2. Embedding & Vector Storage
        embeddings = self._embedding_model.embed_documents(chunks)
        metadata = [{"source": doc_name} for _ in chunks]
        self._vector_store.add_chunks(chunks, embeddings, metadata)

        # 3. Entity & Relationship Extraction (Graph Store)
        if self._llm:
            triples = self._extract_triples_with_llm(text)
            if triples:
                # v5: Standardized triple addition
                self._graph_store.add_triples(triples, provenance=doc_name)

    def _extract_triples_with_llm(self, text: str) -> List[Tuple[str, str, str]]:
        """Uses an LLM to extract (subject, predicate, object) triples."""
        prompt_template = PromptTemplate(
            template="""Extract semantic entities and their relationships from the following text as triples.
Format your response as a JSON list of objects with "subject", "predicate", and "object" keys.

Text: {text}
Output:""",
            input_variables=["text"],
        )
        chain = prompt_template | self._llm | JsonOutputParser()
        try:
            results = chain.invoke({"text": text[:2000]})
            return [(r["subject"], r["predicate"], r["object"]) for r in results]
        except Exception as e:
            print(f"Extraction error: {e}")
            return []
