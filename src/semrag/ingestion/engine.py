import os
from typing import List, Dict, Any, Tuple
from unstructured.partition.auto import partition
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from semrag.graph_store.interface import IGraphStore
from semrag.vector_store.qdrant_wrapper import QdrantVectorStore

class IngestionEngine:
    """
    Core engine for multi-format document ingestion.
    Supports PDF, Office (DOCX, XLSX, PPTX), and Markdown.
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
        """Ingests a file from the filesystem."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # 1. Extraction (unstructured)
        elements = partition(filename=file_path)
        text = "\n\n".join([str(el) for el in elements])
        doc_name = os.path.basename(file_path)
        
        # 2. Chunking
        chunks = self._text_splitter.split_text(text)
        
        # 3. Embedding & Vector Storage
        embeddings = self._embedding_model.embed_documents(chunks)
        metadata = [{"source": doc_name} for _ in chunks]
        self._vector_store.add_chunks(chunks, embeddings, metadata)

        # 4. Entity & Relationship Extraction (Graph Store)
        # Using the LLM-based triple extraction logic
        self._populate_graph_from_text(text)

    def _populate_graph_from_text(self, text: str) -> None:
        """Extracts triples using an LLM and adds them to the graph store."""
        if self._llm:
            triples = self._extract_triples_with_llm(text)
            if triples:
                self._graph_store.add_triples(triples)

    def _extract_triples_with_llm(self, text: str) -> List[Tuple[str, str, str]]:
        """
        Uses an LLM to extract (subject, predicate, object) triples.
        """
        prompt_template = PromptTemplate(
            template="""
            Extract semantic entities and their relationships from the following text as triples.
            Format your response as a JSON list of objects with "subject", "predicate", and "object" keys.
            
            Example:
            Text: "Apple was founded by Steve Jobs."
            Output: [{"subject": "Apple", "predicate": "FOUNDED_BY", "object": "Steve Jobs"}]
            
            Text: {text}
            Output:""",
            input_variables=["text"],
        )
        
        # Construct the chain
        chain = prompt_template | self._llm | JsonOutputParser()
        
        try:
            # Limit the text to avoid context window issues
            results = chain.invoke({"text": text[:2000]})
            return [(r["subject"], r["predicate"], r["object"]) for r in results if all(k in r for k in ("subject", "predicate", "object"))]
        except Exception as e:
            print(f"Error during triple extraction: {e}")
            return []
