"""
Embedding generation and management for semantic search
"""
import numpy as np
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
import torch
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class EmbeddingService:
    """Service for generating and managing text embeddings"""

    def __init__(self):
        self.model = None
        self.device = settings.DEVICE
        self.model_name = settings.EMBEDDING_MODEL
        self.dimension = settings.EMBEDDING_DIMENSION
        self.max_seq_length = settings.MAX_SEQ_LENGTH
        self.batch_size = settings.BATCH_SIZE

        self._initialize_model()

    def _initialize_model(self):
        """Initialize the sentence transformer model"""
        try:
            logger.info("Initializing embedding model", model=self.model_name, device=self.device)

            # Set device
            if self.device == "cuda" and not torch.cuda.is_available():
                logger.warning("CUDA requested but not available, falling back to CPU")
                self.device = "cpu"

            # Load model
            self.model = SentenceTransformer(
                self.model_name,
                device=self.device,
                cache_folder="/app/data/models"
            )

            # Set max sequence length
            self.model.max_seq_length = self.max_seq_length

            logger.info(
                "Embedding model initialized successfully",
                dimension=self.dimension,
                device=self.device
            )

        except Exception as e:
            logger.error("Failed to initialize embedding model", error=str(e))
            raise

    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a list of texts

        Args:
            texts: List of text strings to embed

        Returns:
            numpy array of shape (len(texts), embedding_dimension)
        """
        if not self.model:
            raise RuntimeError("Embedding model not initialized")

        if not texts:
            return np.array([])

        try:
            logger.debug("Generating embeddings", count=len(texts), batch_size=self.batch_size)

            # Process in batches to manage memory
            all_embeddings = []

            for i in range(0, len(texts), self.batch_size):
                batch_texts = texts[i:i + self.batch_size]

                # Generate embeddings for batch
                batch_embeddings = self.model.encode(
                    batch_texts,
                    convert_to_numpy=True,
                    normalize_embeddings=True,  # L2 normalization for cosine similarity
                    show_progress_bar=False
                )

                all_embeddings.append(batch_embeddings)

            # Concatenate all batches
            embeddings = np.vstack(all_embeddings) if len(all_embeddings) > 1 else all_embeddings[0]

            logger.debug("Embeddings generated successfully", shape=embeddings.shape)
            return embeddings

        except Exception as e:
            logger.error("Failed to generate embeddings", error=str(e), text_count=len(texts))
            raise

    def generate_single_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text

        Args:
            text: Text string to embed

        Returns:
            numpy array of shape (embedding_dimension,)
        """
        embeddings = self.generate_embeddings([text])
        return embeddings[0] if len(embeddings) > 0 else np.array([])

    def cosine_similarity(self, query_embedding: np.ndarray, document_embeddings: np.ndarray) -> np.ndarray:
        """
        Calculate cosine similarity between query and document embeddings

        Args:
            query_embedding: Single query embedding
            document_embeddings: Multiple document embeddings

        Returns:
            Similarity scores array
        """
        # Cosine similarity = dot product for normalized vectors
        similarities = np.dot(document_embeddings, query_embedding)
        return similarities

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        if not self.model:
            return {"status": "not_initialized"}

        return {
            "model_name": self.model_name,
            "dimension": self.dimension,
            "device": self.device,
            "max_seq_length": self.max_seq_length,
            "batch_size": self.batch_size,
            "status": "ready"
        }


# Global embedding service instance
embedding_service = EmbeddingService()