"""
Text chunking utilities for document processing
"""
import re
from typing import List, Dict, Any, Optional
import nltk
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class TextChunker:
    """Intelligent text chunking for document processing"""

    def __init__(self):
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP
        self.min_chunk_length = settings.MIN_CHUNK_LENGTH

        # Download NLTK punkt if not available
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)

    def chunk_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Split text into overlapping chunks with metadata

        Args:
            text: Full text to chunk
            metadata: Additional metadata for chunks

        Returns:
            List of chunk dictionaries with content and metadata
        """
        if not text or len(text.strip()) < self.min_chunk_length:
            return []

        # Clean and normalize text
        text = self._clean_text(text)

        # Split into sentences first
        sentences = nltk.sent_tokenize(text)

        # Create chunks with overlap
        chunks = []
        current_chunk = ""
        chunk_sentences = []
        chunk_index = 0

        for sentence in sentences:
            # Check if adding this sentence would exceed chunk size
            potential_chunk = current_chunk + " " + sentence if current_chunk else sentence

            if len(potential_chunk) > self.chunk_size and current_chunk:
                # Save current chunk
                if len(current_chunk.strip()) >= self.min_chunk_length:
                    chunks.append(self._create_chunk(
                        content=current_chunk.strip(),
                        index=chunk_index,
                        sentences=chunk_sentences,
                        metadata=metadata
                    ))
                    chunk_index += 1

                # Start new chunk with overlap
                overlap_sentences = self._get_overlap_sentences(chunk_sentences)
                current_chunk = " ".join(overlap_sentences) + " " + sentence
                chunk_sentences = overlap_sentences + [sentence]
            else:
                # Add sentence to current chunk
                current_chunk = potential_chunk
                chunk_sentences.append(sentence)

        # Add final chunk
        if current_chunk and len(current_chunk.strip()) >= self.min_chunk_length:
            chunks.append(self._create_chunk(
                content=current_chunk.strip(),
                index=chunk_index,
                sentences=chunk_sentences,
                metadata=metadata
            ))

        logger.debug("Text chunked successfully", original_length=len(text), chunks=len(chunks))
        return chunks

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text.strip())

        # Remove page breaks and special characters
        text = re.sub(r'\f|\v|\r\n|\r', '\n', text)
        text = re.sub(r'\n+', ' ', text)

        return text

    def _get_overlap_sentences(self, sentences: List[str]) -> List[str]:
        """Get sentences for overlap based on character count"""
        overlap_text = ""
        overlap_sentences = []

        # Work backwards from the end
        for sentence in reversed(sentences):
            if len(overlap_text) + len(sentence) <= self.chunk_overlap:
                overlap_text = sentence + " " + overlap_text
                overlap_sentences.insert(0, sentence)
            else:
                break

        return overlap_sentences

    def _create_chunk(self, content: str, index: int, sentences: List[str],
                      metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a chunk dictionary"""
        chunk_metadata = {
            "chunk_index": index,
            "sentence_count": len(sentences),
            "character_count": len(content),
            "word_count": len(content.split()),
        }

        if metadata:
            chunk_metadata.update(metadata)

        return {
            "index": index,
            "content": content,
            "sentences": sentences,
            "metadata": chunk_metadata
        }

    def estimate_chunks(self, text: str) -> Dict[str, int]:
        """Estimate number of chunks for a given text"""
        if not text:
            return {"estimated_chunks": 0, "total_characters": 0}

        total_chars = len(text)
        avg_chars_per_chunk = self.chunk_size - (self.chunk_overlap / 2)

        estimated_chunks = max(1, int(total_chars / avg_chars_per_chunk))

        return {
            "estimated_chunks": estimated_chunks,
            "total_characters": total_chars,
            "avg_chunk_size": self.chunk_size,
            "overlap_size": self.chunk_overlap
        }


# Global chunker instance
text_chunker = TextChunker()