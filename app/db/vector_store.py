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
            model_name="paraphrase-multilingual-MiniLM-L12-v2"
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
        """Search for similar translation pairs with bidirectional matching.

        Translation pairs are considered bidirectional. For example, if the database
        has en→it pairs, they can also be used for it→en queries by swapping the
        source and target.

        Args:
            query_sentence: The sentence to find similar translations for
            source_language: ISO 639-1 code for source language
            target_language: ISO 639-1 code for target language
            n_results: Number of results to return (default 4)

        Returns:
            List of dictionaries containing similar translation pairs
        """
        # Try direct match first
        direct_results = self.collection.query(
            query_texts=[query_sentence],
            n_results=n_results * 2,  # Get more to have options after filtering
            where={
                "$and": [
                    {"source_language": {"$eq": source_language}},
                    {"target_language": {"$eq": target_language}}
                ]
            }
        )

        # Try reverse match (swap source and target languages)
        reverse_results = self.collection.query(
            query_texts=[query_sentence],
            n_results=n_results * 2,
            where={
                "$and": [
                    {"source_language": {"$eq": target_language}},
                    {"target_language": {"$eq": source_language}}
                ]
            }
        )

        # Combine results, prioritizing direct matches
        pairs = []
        seen_pairs = set()

        # Add direct matches
        if direct_results['metadatas'] and direct_results['metadatas'][0]:
            for metadata in direct_results['metadatas'][0]:
                pair_key = (metadata["sentence"], metadata["translation"])
                if pair_key not in seen_pairs:
                    pairs.append({
                        "sentence": metadata["sentence"],
                        "translation": metadata["translation"]
                    })
                    seen_pairs.add(pair_key)
                if len(pairs) >= n_results:
                    break

        # Add reverse matches (swapped) if we need more
        if len(pairs) < n_results and reverse_results['metadatas'] and reverse_results['metadatas'][0]:
            for metadata in reverse_results['metadatas'][0]:
                # Swap source and translation for reverse pairs
                pair_key = (metadata["translation"], metadata["sentence"])
                if pair_key not in seen_pairs:
                    pairs.append({
                        "sentence": metadata["translation"],  # Swapped
                        "translation": metadata["sentence"]  # Swapped
                    })
                    seen_pairs.add(pair_key)
                if len(pairs) >= n_results:
                    break

        return pairs[:n_results]
