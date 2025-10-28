"""
Search API endpoints for DocQA-MS API Gateway
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
import httpx
import uuid

from app.core.config import settings
from app.core.logging import get_logger
from app.core.database import execute_query, execute_one

router = APIRouter()
logger = get_logger(__name__)


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


@router.post("/")
async def search_documents(request: SearchRequest):
    """
    Perform semantic search across documents
    
    This endpoint performs semantic search using natural language queries
    to find relevant document chunks based on meaning rather than keywords.
    
    **Parameters**:
    - **query**: Natural language search query (minimum 3 characters)
    - **filters**: Optional filters for document_type, patient_id, dates
    - **limit**: Maximum number of results to return (1-100)
    - **threshold**: Minimum similarity score threshold (0.0-1.0)
    
    **Returns**:
    - **search_id**: Unique identifier for this search
    - **query**: The search query
    - **results**: List of matching document chunks with scores
    - **total_results**: Number of results found
    - **execution_time_ms**: Search execution time in milliseconds
    """
    try:
        # Validate query
        if not request.query or len(request.query.strip()) < 3:
            raise HTTPException(
                status_code=400,
                detail="Query must be at least 3 characters long"
            )

        # Generate search ID
        search_id = str(uuid.uuid4())

        # Prepare search request for indexer service
        indexer_request = {
            "query": request.query.strip(),
            "filters": request.filters.dict(exclude_none=True),
            "limit": request.limit,
            "threshold": request.threshold
        }

        logger.info(
            "Performing semantic search",
            search_id=search_id,
            query=request.query,
            filters=request.filters.dict(exclude_none=True)
        )

        # Call semantic indexer service
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{settings.INDEXER_SEMANTIQUE_URL}/api/v1/search/",
                    json=indexer_request
                )

                if response.status_code != 200:
                    logger.error(
                        "Semantic search failed",
                        search_id=search_id,
                        status_code=response.status_code,
                        response=response.text
                    )
                    raise HTTPException(
                        status_code=500,
                        detail="Search service temporarily unavailable"
                    )

                search_results = response.json()

            except httpx.RequestError as e:
                logger.error(
                    "Failed to connect to semantic indexer",
                    search_id=search_id,
                    error=str(e)
                )
                raise HTTPException(
                    status_code=503,
                    detail="Search service unavailable"
                )

        # Log search in audit (this would be done asynchronously)
        audit_data = {
            "user_id": "anonymous",  # Would come from auth context
            "action": "search_query",
            "resource_type": "search",
            "resource_id": search_id,
            "action_details": {
                "query": request.query,
                "filters": request.filters.dict(exclude_none=True),
                "result_count": len(search_results.get("results", []))
            }
        }

        # Send to audit logger (fire and forget)
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                await client.post(
                    f"{settings.AUDIT_LOGGER_URL}/log",
                    json=audit_data
                )
        except Exception as e:
            logger.warning("Failed to log search audit", error=str(e))

        # Format response
        result = {
            "search_id": search_id,
            "query": request.query,
            "filters": request.filters.dict(exclude_none=True),
            "results": search_results.get("results", []),
            "total_results": len(search_results.get("results", [])),
            "execution_time_ms": search_results.get("execution_time_ms", 0)
        }

        logger.info(
            "Search completed successfully",
            search_id=search_id,
            result_count=len(result["results"])
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Unexpected error during search",
            query=request.query,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail="Search failed due to internal error"
        )


@router.get("/suggestions")
async def get_search_suggestions(
    prefix: str = Query(..., description="Search prefix for suggestions", min_length=1),
    limit: int = Query(10, description="Maximum number of suggestions", ge=1, le=50)
):
    """
    Get search suggestions based on prefix from actual search queries
    """
    try:
        # Query database for common search terms that match the prefix
        query = """
            SELECT DISTINCT 
                q.query_text,
                COUNT(*) as frequency
            FROM (
                -- Get queries from QA interactions
                SELECT question as query_text 
                FROM qa_interactions 
                WHERE question ILIKE $1 || '%'
                
                UNION ALL
                
                -- Get common medical terms from document content
                SELECT unnest(regexp_split_to_array(lower(content), '\s+')) as query_text
                FROM documents
                WHERE content ILIKE '%' || $1 || '%'
            ) q
            WHERE length(q.query_text) >= 3
            GROUP BY q.query_text
            ORDER BY frequency DESC, q.query_text
            LIMIT $2
        """
        
        rows = await execute_query(query, prefix.lower(), limit)
        
        if rows:
            suggestions = [row['query_text'] for row in rows]
        else:
            # Fallback to common medical term patterns if no matches
            suggestions = [
                f"{prefix} traitement",
                f"{prefix} diagnostic",
                f"{prefix} résultats",
                f"{prefix} antécédents"
            ][:limit]

        return {
            "suggestions": suggestions,
            "prefix": prefix,
            "limit": limit
        }

    except Exception as e:
        logger.error(
            "Failed to get search suggestions",
            prefix=prefix,
            error=str(e)
        )
        # Return fallback suggestions on error
        return {
            "suggestions": [
                f"{prefix} traitement",
                f"{prefix} diagnostic",
                f"{prefix} résultats"
            ][:limit],
            "prefix": prefix,
            "limit": limit
        }


@router.get("/stats")
async def get_search_statistics():
    """
    Get search usage statistics from database
    """
    try:
        # Get total QA interactions (proxy for searches)
        total_query = """
            SELECT COUNT(*) as total_searches,
                   COUNT(DISTINCT user_id) as unique_users,
                   AVG(CASE WHEN context_documents IS NOT NULL 
                       THEN array_length(context_documents, 1) 
                       ELSE 0 END) as avg_results
            FROM qa_interactions
        """
        total_stats = await execute_one(total_query)
        
        # Get popular queries
        popular_query = """
            SELECT question as query, COUNT(*) as count
            FROM qa_interactions
            GROUP BY question
            ORDER BY count DESC
            LIMIT 10
        """
        popular_rows = await execute_query(popular_query)
        
        # Get time-based trends
        trends_query = """
            SELECT 
                COUNT(CASE WHEN created_at >= NOW() - INTERVAL '7 days' THEN 1 END) as last_7_days,
                COUNT(CASE WHEN created_at >= NOW() - INTERVAL '30 days' THEN 1 END) as last_30_days,
                COUNT(CASE WHEN created_at >= NOW() - INTERVAL '90 days' THEN 1 END) as last_90_days
            FROM qa_interactions
        """
        trends = await execute_one(trends_query)
        
        stats = {
            "total_searches": total_stats['total_searches'] if total_stats else 0,
            "unique_users": total_stats['unique_users'] if total_stats else 0,
            "average_results_per_search": round(float(total_stats['avg_results']) if total_stats and total_stats['avg_results'] else 0, 1),
            "popular_queries": [
                {"query": row['query'], "count": row['count']} 
                for row in popular_rows
            ] if popular_rows else [],
            "search_trends": {
                "last_7_days": trends['last_7_days'] if trends else 0,
                "last_30_days": trends['last_30_days'] if trends else 0,
                "last_90_days": trends['last_90_days'] if trends else 0
            }
        }

        return stats

    except Exception as e:
        logger.error("Failed to get search statistics", error=str(e))
        # Return empty stats on error rather than failing
        return {
            "total_searches": 0,
            "unique_users": 0,
            "average_results_per_search": 0.0,
            "popular_queries": [],
            "search_trends": {
                "last_7_days": 0,
                "last_30_days": 0,
                "last_90_days": 0
            }
        }