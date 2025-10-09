from pydantic import BaseModel, Field


class TranslationPair(BaseModel):
    """Model for adding a translation pair to the database."""
    source_language: str = Field(..., description="ISO 639-1 two-letter code (e.g., 'en', 'it')")
    target_language: str = Field(..., description="ISO 639-1 two-letter code")
    sentence: str = Field(..., description="Source sentence")
    translation: str = Field(..., description="Translated sentence")


class PromptResponse(BaseModel):
    """Response model for translation prompt requests."""
    prompt: str = Field(..., description="Formatted translation prompt with examples")


class StammeringResponse(BaseModel):
    """Response model for stammering detection."""
    has_stammer: bool = Field(..., description="Whether stammering was detected in the translation")
