"""
Semantic search endpoints
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
import time

from app.core.embeddings import embedding_service
from app.core.vector_store import vector_store
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


class SearchFilter(BaseModel):
    """Search filter model"""
    document_type: Optional[str] = None
    patient_id: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    document_id: Optional[str] = None


class SearchRequest(BaseModel):
    """Semantic search request"""
    query: str = Field(..., min_length=1, description="Search query in natural language")
    filters: SearchFilter = Field(default_factory=SearchFilter)
    limit: int = Field(20, ge=1, le=100, description="Maximum number of results")
    threshold: float = Field(0.0, ge=0.0, le=1.0, description="Minimum similarity threshold")


class SearchResult(BaseModel):
    """Individual search result"""
    chunk_id: str
    document_id: str
    score: float = Field(..., ge=0.0, le=1.0)
    content: str
    metadata: Dict[str, Any] = {}


class SearchResponse(BaseModel):
    """Search response"""
    query: str
    results: List[SearchResult]
    total_results: int
    execution_time_ms: int
    filters_applied: SearchFilter


@router.post("/", response_model=SearchResponse)
async def semantic_search(request: SearchRequest):
    """
    Perform semantic search across indexed documents

    This endpoint converts the natural language query to embeddings
    and finds the most similar document chunks using vector similarity.
    """
    start_time = time.time()

    try:
        logger.info("Starting semantic search",
                   query=request.query[:50] + "..." if len(request.query) > 50 else request.query,
                   limit=request.limit,
                   threshold=request.threshold)

        # Generate embedding for the query
        query_embedding = embedding_service.generate_single_embedding(request.query)

        # Perform vector search
        search_results = vector_store.search(
            query_vector=query_embedding,
            k=request.limit,
            threshold=request.threshold
        )

        # Convert to response format with deduplication
        results = []
        seen_chunks = set()  # Track unique chunk_ids to prevent duplicates
        
        for chunk_id, score, metadata in search_results:
            # Skip if we've already seen this chunk
            if chunk_id in seen_chunks:
                logger.debug("Skipping duplicate chunk", chunk_id=chunk_id)
                continue
            
            # Extract document_id from chunk_id (format: "doc_id_chunk_index")
            document_id = chunk_id.rsplit('_chunk_', 1)[0] if '_chunk_' in chunk_id else chunk_id

            # Apply filters if specified
            if request.filters.document_type and metadata.get('document_type') != request.filters.document_type:
                continue
            if request.filters.patient_id and metadata.get('patient_id') != request.filters.patient_id:
                continue
            if request.filters.document_id and document_id != request.filters.document_id:
                continue

            result = SearchResult(
                chunk_id=chunk_id,
                document_id=document_id,
                score=round(float(score), 4),
                content=metadata.get('content', ''),  # Content might be stored in metadata
                metadata=metadata
            )
            results.append(result)
            seen_chunks.add(chunk_id)  # Mark this chunk as seen

        execution_time = int((time.time() - start_time) * 1000)

        response = SearchResponse(
            query=request.query,
            results=results,
            total_results=len(results),
            execution_time_ms=execution_time,
            filters_applied=request.filters
        )

        logger.info("Semantic search completed",
                   query_length=len(request.query),
                   results_found=len(results),
                   execution_time_ms=execution_time)

        return response

    except Exception as e:
        execution_time = int((time.time() - start_time) * 1000)
        logger.error("Semantic search failed",
                    query=request.query[:50],
                    error=str(e),
                    execution_time_ms=execution_time)
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/stats")
async def get_search_stats():
    """
    Get search and indexing statistics

    Returns information about the vector store and search performance.
    """
    try:
        vector_stats = vector_store.get_stats()
        embedding_info = embedding_service.get_model_info()

        stats = {
            "vector_store": vector_stats,
            "embedding_model": embedding_info,
            "search_config": {
                "max_results": settings.MAX_SEARCH_RESULTS,
                "similarity_threshold": settings.SIMILARITY_THRESHOLD,
                "search_timeout": settings.SEARCH_TIMEOUT
            }
        }

        logger.debug("Search stats retrieved")
        return stats

    except Exception as e:
        logger.error("Failed to get search stats", error=str(e))
        raise HTTPException(status_code=500, detail=f"Stats retrieval failed: {str(e)}")


@router.post("/hybrid")
async def hybrid_search(request: SearchRequest):
    """
    Perform hybrid search combining semantic and keyword search

    This is a placeholder for future implementation of hybrid search
    that combines vector similarity with traditional keyword matching.
    """
    # For now, delegate to semantic search
    # Future implementation would combine semantic + keyword scores
    return await semantic_search(request)


@router.get("/suggest")
async def get_search_suggestions(q: str = Query(..., min_length=1, description="Partial query for suggestions")):
    """
    Get search suggestions based on partial query

    This endpoint provides autocomplete suggestions for search queries.
    """
    try:
        # This is a simplified implementation
        # In production, this could use a separate index or NLP model
        suggestions = [
            f"{q} traitement",
            f"{q} diagnostic",
            f"{q} évolution",
            f"{q} complications"
        ]

        logger.debug("Search suggestions generated", query=q, suggestions=len(suggestions))

        return {
            "query": q,
            "suggestions": suggestions[:5]  # Limit to 5 suggestions
        }

    except Exception as e:
        logger.error("Failed to generate search suggestions", query=q, error=str(e))
        raise HTTPException(status_code=500, detail=f"Suggestions failed: {str(e)}")