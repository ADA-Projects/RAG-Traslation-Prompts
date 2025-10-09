import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict, Optional
import uuid


class VectorStore:
    """Manages translation pair storage and retrieval using ChromaDB with sentence transformers."""

    def __init__(self, persist_directory: str = "./chroma_db"):
        """Initialize ChromaDB client and collection."""
        self.client = chromadb.PersistentClient(path=persist_directory)

        # Use sentence-transformers embedding function
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="translation_pairs",
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"}  # Use cosine similarity
        )

    def add_pair(
        self,
        source_language: str,
        target_language: str,
        sentence: str,
        translation: str
    ) -> None:
        """Add a translation pair to the database.

        Args:
            source_language: ISO 639-1 code for source language
            target_language: ISO 639-1 code for target language
            sentence: Source sentence
            translation: Translated sentence
        """
        # Generate unique ID
        doc_id = str(uuid.uuid4())

        # Store with metadata for filtering
        self.collection.add(
            ids=[doc_id],
            documents=[sentence],  # Embed the source sentence
            metadatas=[{
                "source_language": source_language,
                "target_language": target_language,
                "sentence": sentence,
                "translation": translation
            }]
        )

    def search_similar(
        self,
        query_sentence: str,
        source_language: str,
        target_language: str,
        n_results: int = 4
    ) -> List[Dict[str, str]]:
        """Search for similar translation pairs.

        Args:
            query_sentence: The sentence to find similar translations for
            source_language: ISO 639-1 code for source language
            target_language: ISO 639-1 code for target language
            n_results: Number of results to return (default 4)

        Returns:
            List of dictionaries containing similar translation pairs
        """
        # Query with language pair filtering
        results = self.collection.query(
            query_texts=[query_sentence],
            n_results=n_results,
            where={
                "$and": [
                    {"source_language": {"$eq": source_language}},
                    {"target_language": {"$eq": target_language}}
                ]
            }
        )

        # Extract translation pairs from results
        pairs = []
        if results['metadatas'] and results['metadatas'][0]:
            for metadata in results['metadatas'][0]:
                pairs.append({
                    "sentence": metadata["sentence"],
                    "translation": metadata["translation"]
                })

        return pairs
