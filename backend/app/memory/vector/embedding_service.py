"""Embedding generation service using Hugging Face sentence-transformers.

Completely free and runs locally — no API keys needed.
Uses all-MiniLM-L6-v2 (80MB, fast CPU inference, 384-dim vectors).
"""

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Generates vector embeddings for memory entries and user queries.

    Uses sentence-transformers (all-MiniLM-L6-v2) running locally.
    This is completely free with no API calls or keys required.
    """

    EMBEDDING_DIMENSION = 384  # all-MiniLM-L6-v2 output dimensions

    def __init__(self) -> None:
        self._model = None
        self._available: Optional[bool] = None

    def _get_model(self):
        """Lazily load the sentence-transformer model."""
        if self._model is None and self._available is not False:
            try:
                # Inject HF_TOKEN into the environment so HuggingFace Hub
                # can authenticate downloads (higher rate limits, faster).
                from app.config.settings import settings

                if settings.HF_TOKEN and not os.environ.get("HF_TOKEN"):
                    os.environ["HF_TOKEN"] = settings.HF_TOKEN

                from sentence_transformers import SentenceTransformer

                self._model = SentenceTransformer("all-MiniLM-L6-v2")
                self._available = True
                logger.info(
                    "Loaded embedding model: all-MiniLM-L6-v2 (%d dims)",
                    self.EMBEDDING_DIMENSION,
                )
            except Exception as e:
                logger.warning(
                    "Cannot load sentence-transformers model: %s. "
                    "Semantic search will be unavailable.",
                    e,
                )
                self._available = False
        return self._model

    def is_available(self) -> bool:
        """Return True if the embedding model is ready to use."""
        self._get_model()
        return self._available is True

    async def embed_text(self, text: str) -> Optional[list[float]]:
        """Generate an embedding vector for a single piece of text."""
        model = self._get_model()
        if model is None:
            return None

        import asyncio

        try:
            loop = asyncio.get_running_loop()

            def _encode():
                return model.encode(text).tolist()

            return await loop.run_in_executor(None, _encode)
        except Exception as e:
            logger.error("Embedding generation failed: %s", e)
            return None


# Singleton instance
embedding_service = EmbeddingService()
