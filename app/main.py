from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from app.models.schemas import TranslationPair, PromptResponse, StammeringResponse
from app.db.vector_store import VectorStore
from app.utils.stammering import detect_stammer

app = FastAPI(
    title="RAG Translation Backend",
    description="REST API for Retrieval-Augmented Generation translation prompts using semantic similarity search",
    version="1.0.0"
)

# Initialize vector store
vector_store = VectorStore()


@app.get("/")
def root():
    """Root endpoint."""
    return {"status": "ok", "message": "RAG Translation API"}


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/pairs")
def add_translation_pair(pair: TranslationPair):
    """Add a new translation pair to the database.

    Args:
        pair: Translation pair containing source language, target language,
              source sentence, and translation

    Returns:
        Simple success response
    """
    try:
        vector_store.add_pair(
            source_language=pair.source_language,
            target_language=pair.target_language,
            sentence=pair.sentence,
            translation=pair.translation
        )
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add pair: {str(e)}")


@app.get("/prompt", response_model=PromptResponse)
def get_translation_prompt(
    source_language: str,
    target_language: str,
    query_sentence: str
) -> PromptResponse:
    """Get a translation prompt with similar example pairs.

    Args:
        source_language: ISO 639-1 code for source language
        target_language: ISO 639-1 code for target language
        query_sentence: The sentence to translate

    Returns:
        Formatted translation prompt including similar examples
    """
    try:
        # Search for similar pairs
        similar_pairs = vector_store.search_similar(
            query_sentence=query_sentence,
            source_language=source_language,
            target_language=target_language,
            n_results=4
        )

        # Get full language names (simple mapping for common ones)
        lang_names = {
            "en": "English",
            "it": "Italian",
            "de": "German",
            "fr": "French",
            "es": "Spanish"
        }
        source_name = lang_names.get(source_language, source_language.upper())
        target_name = lang_names.get(target_language, target_language.upper())

        # Format the prompt
        prompt_parts = [f"You are a translator from {source_name} to {target_name}."]

        if similar_pairs:
            prompt_parts.append("\nHere are some similar translation examples:")
            for pair in similar_pairs:
                prompt_parts.append(f'- "{pair["sentence"]}" → "{pair["translation"]}"')

        prompt_parts.append(f'\nNow translate: "{query_sentence}"')

        prompt = "\n".join(prompt_parts)
        return PromptResponse(prompt=prompt)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate prompt: {str(e)}")


@app.get("/stammering", response_model=StammeringResponse)
def detect_stammering(
    source_sentence: str,
    translated_sentence: str
) -> StammeringResponse:
    """Detect stammering in a translated sentence.

    Stammering refers to non-natural repetition of text parts in the
    translated output, resulting in awkward or nonsensical sentences.

    Args:
        source_sentence: The original source sentence
        translated_sentence: The translated sentence to analyze

    Returns:
        Boolean indicating whether stammering was detected
    """
    try:
        has_stammer = detect_stammer(source_sentence, translated_sentence)
        return StammeringResponse(has_stammer=has_stammer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to detect stammering: {str(e)}")
