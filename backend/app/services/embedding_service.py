"""Embedding service for generating embeddings."""
from typing import List, Optional
# Temporarily disabled due to dependency issues
# from sentence_transformers import SentenceTransformer
import torch

from app.core.config import get_settings
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


class EmbeddingService:
    """Service for generating embeddings."""

    def __init__(self):
        """Initialize embedding service."""
        self.model_name = getattr(settings, 'EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
        self.model = None
        logger.warning("Embedding service temporarily disabled due to dependency issues")

    def _load_model(self):
        """Load the embedding model."""
        # Temporarily disabled
        logger.warning("Embedding model loading temporarily disabled")

    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for a text."""
        # Return a dummy embedding for now
        logger.warning("Returning dummy embedding - service temporarily disabled")
        return [0.0] * 384  # Standard embedding size for all-MiniLM-L6-v2

    def generate_embeddings(self, texts: List[str]) -> List[Optional[List[float]]]:
        """Generate embeddings for multiple texts."""
        # Return dummy embeddings for now
        logger.warning(f"Returning {len(texts)} dummy embeddings - service temporarily disabled")
        return [[0.0] * 384 for _ in texts]


# Global embedding service instance
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    """Get embedding service instance."""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service

