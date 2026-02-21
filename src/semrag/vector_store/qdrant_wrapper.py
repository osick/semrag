from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.http import models

class QdrantVectorStore:
    """
    Wrapper for Qdrant vector database.
    Handles embedding-based search and point insertion.
    """
    
    def __init__(self, host: str, port: int, collection_name: str = "semrag_chunks"):
        self._client = QdrantClient(host=host, port=port)
        self._collection_name = collection_name
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        """Create the collection if it doesn't exist."""
        # Note: Size (1536 for OpenAI-like or 768/384 for Ollama models) should be dynamic.
        # For initial TDD, using a default size of 768 (Ollama/Nomic).
        if not self._client.collection_exists(self._collection_name):
            self._client.create_collection(
                collection_name=self._collection_name,
                vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE),
            )

    def add_chunks(self, chunks: List[str], embeddings: List[List[float]], metadata: List[Dict[str, Any]]) -> None:
        """Add semantic chunks and their embeddings to Qdrant."""
        points = [
            models.PointStruct(
                id=idx,
                vector=emb,
                payload={"content": chunk, **meta}
            )
            for idx, (chunk, emb, meta) in enumerate(zip(chunks, embeddings, metadata))
        ]
        self._client.upsert(collection_name=self._collection_name, points=points)

    def search(self, query_vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """Perform similarity search on the stored chunks."""
        results = self._client.search(
            collection_name=self._collection_name,
            query_vector=query_vector,
            limit=top_k
        )
        return [hit.payload for hit in results]

    def clear(self) -> None:
        """Delete the collection for testing/reset."""
        self._client.delete_collection(self._collection_name)
        self._ensure_collection()
