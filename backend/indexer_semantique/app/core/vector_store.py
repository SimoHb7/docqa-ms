"""
FAISS vector store management for semantic search
"""
import os
import json
import numpy as np
import faiss
from typing import List, Dict, Any, Optional, Tuple
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class VectorStore:
    """FAISS-based vector store for semantic search"""

    def __init__(self):
        self.index = None
        self.metadata = {}  # chunk_id -> metadata mapping
        self.id_mapping = {}  # faiss_id -> chunk_id mapping
        self.dimension = settings.EMBEDDING_DIMENSION

        # Ensure directories exist
        os.makedirs(os.path.dirname(settings.VECTOR_INDEX_PATH), exist_ok=True)
        os.makedirs(os.path.dirname(settings.VECTOR_METADATA_PATH), exist_ok=True)

        self.index_path = settings.VECTOR_INDEX_PATH
        self.metadata_path = settings.VECTOR_METADATA_PATH

        self._load_or_create_index()

    def _load_or_create_index(self):
        """Load existing index or create new one"""
        try:
            if os.path.exists(self.index_path):
                logger.info("Loading existing FAISS index", path=self.index_path)
                self.index = faiss.read_index(self.index_path)

                # Load metadata
                if os.path.exists(self.metadata_path):
                    with open(self.metadata_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        self.metadata = data.get('metadata', {})
                        self.id_mapping = data.get('id_mapping', {})

                logger.info("FAISS index loaded successfully",
                          vectors=self.index.ntotal,
                          chunks=len(self.metadata))
            else:
                logger.info("Creating new FAISS index", dimension=self.dimension)
                self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity
                logger.info("FAISS index created successfully")

        except Exception as e:
            logger.error("Failed to load/create FAISS index", error=str(e))
            # Create new index as fallback
            self.index = faiss.IndexFlatIP(self.dimension)
            self.metadata = {}
            self.id_mapping = {}

    def save_index(self):
        """Save index and metadata to disk"""
        try:
            if self.index:
                logger.info("Saving FAISS index", path=self.index_path)
                faiss.write_index(self.index, self.index_path)

                # Save metadata
                data = {
                    'metadata': self.metadata,
                    'id_mapping': self.id_mapping,
                    'total_vectors': self.index.ntotal if self.index else 0
                }

                with open(self.metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

                logger.info("FAISS index saved successfully",
                          vectors=self.index.ntotal,
                          metadata_entries=len(self.metadata))

        except Exception as e:
            logger.error("Failed to save FAISS index", error=str(e))
            raise

    def add_vectors(self, vectors: np.ndarray, chunk_ids: List[str],
                   metadata_list: List[Dict[str, Any]]) -> List[int]:
        """
        Add vectors to the index

        Args:
            vectors: numpy array of shape (n, dimension)
            chunk_ids: list of chunk IDs
            metadata_list: list of metadata dictionaries

        Returns:
            List of FAISS IDs assigned to the vectors
        """
        if vectors.size == 0:
            return []

        try:
            # Add vectors to FAISS index
            self.index.add(vectors)

            # Get the IDs assigned by FAISS (last N vectors)
            start_id = self.index.ntotal - len(vectors)
            faiss_ids = list(range(start_id, self.index.ntotal))

            # Update metadata and ID mapping
            for i, (chunk_id, metadata) in enumerate(zip(chunk_ids, metadata_list)):
                faiss_id = faiss_ids[i]
                self.metadata[chunk_id] = metadata
                self.id_mapping[str(faiss_id)] = chunk_id

            logger.info("Vectors added to index",
                       added=len(vectors),
                       total=self.index.ntotal)

            return faiss_ids

        except Exception as e:
            logger.error("Failed to add vectors to index", error=str(e))
            raise

    def search(self, query_vector: np.ndarray, k: int = 10,
              threshold: Optional[float] = None) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        Search for similar vectors

        Args:
            query_vector: query embedding of shape (dimension,)
            k: number of results to return
            threshold: minimum similarity threshold

        Returns:
            List of (chunk_id, similarity_score, metadata) tuples
        """
        if self.index.ntotal == 0:
            return []

        try:
            # Ensure query vector is 2D
            if query_vector.ndim == 1:
                query_vector = query_vector.reshape(1, -1)

            # Search
            scores, indices = self.index.search(query_vector, min(k, self.index.ntotal))

            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx == -1:  # No more results
                    continue

                if threshold and score < threshold:
                    continue

                # Get chunk ID from mapping
                chunk_id = self.id_mapping.get(str(idx))
                if not chunk_id:
                    logger.warning("Chunk ID not found for FAISS index", faiss_id=idx)
                    continue

                # Get metadata
                metadata = self.metadata.get(chunk_id, {})

                results.append((chunk_id, float(score), metadata))

            logger.debug("Vector search completed",
                        query_shape=query_vector.shape,
                        results=len(results))

            return results

        except Exception as e:
            logger.error("Failed to search vectors", error=str(e))
            raise

    def delete_vectors(self, chunk_ids: List[str]) -> int:
        """
        Delete vectors by chunk IDs
        Note: FAISS doesn't support deletion, so we rebuild the index

        Args:
            chunk_ids: list of chunk IDs to delete

        Returns:
            Number of vectors deleted
        """
        try:
            if not chunk_ids:
                return 0

            # Get all vectors except the ones to delete
            remaining_metadata = {}
            remaining_vectors = []
            remaining_chunk_ids = []

            # This is inefficient for large indexes - in production,
            # consider using a different index type or external ID mapping
            for chunk_id, metadata in self.metadata.items():
                if chunk_id not in chunk_ids:
                    # We can't efficiently get the vector back from FAISS
                    # So we need to rebuild from scratch
                    remaining_metadata[chunk_id] = metadata
                    remaining_chunk_ids.append(chunk_id)

            # For now, just update metadata and log warning
            # Full implementation would require storing original vectors
            deleted_count = len(chunk_ids)
            for chunk_id in chunk_ids:
                self.metadata.pop(chunk_id, None)
                # Remove from ID mapping
                self.id_mapping = {k: v for k, v in self.id_mapping.items() if v != chunk_id}

            logger.warning("Vectors marked for deletion",
                         deleted=deleted_count,
                         remaining=len(self.metadata))

            return deleted_count

        except Exception as e:
            logger.error("Failed to delete vectors", error=str(e))
            raise

    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics"""
        return {
            "total_vectors": self.index.ntotal if self.index else 0,
            "total_chunks": len(self.metadata),
            "dimension": self.dimension,
            "index_type": "IndexFlatIP",
            "is_trained": getattr(self.index, 'is_trained', False) if self.index else False
        }

    def clear_index(self):
        """Clear all vectors and metadata"""
        try:
            self.index = faiss.IndexFlatIP(self.dimension)
            self.metadata = {}
            self.id_mapping = {}

            # Remove files
            if os.path.exists(self.index_path):
                os.remove(self.index_path)
            if os.path.exists(self.metadata_path):
                os.remove(self.metadata_path)

            logger.info("Index cleared successfully")

        except Exception as e:
            logger.error("Failed to clear index", error=str(e))
            raise


# Global vector store instance
vector_store = VectorStore()