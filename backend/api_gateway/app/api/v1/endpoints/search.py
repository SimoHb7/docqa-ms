"""
Search API endpoints for DocQA-MS API Gateway
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query
import httpx
import uuid

from app.core.config import settings
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/")
async def search_documents(
    query: str = Query(..., description="Search query in natural language"),
    document_type: Optional[str] = Query(None, description="Filter by document type"),
    patient_id: Optional[str] = Query(None, description="Filter by patient ID"),
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    limit: int = Query(20, description="Maximum number of results", ge=1, le=100)
):
    """
    Perform semantic search across documents
    """
    try:
        # Validate query
        if not query or len(query.strip()) < 3:
            raise HTTPException(
                status_code=400,
                detail="Query must be at least 3 characters long"
            )

        # Generate search ID
        search_id = str(uuid.uuid4())

        # Build search filters
        filters = {}
        if document_type:
            filters["document_type"] = document_type
        if patient_id:
            filters["patient_id"] = patient_id
        if date_from or date_to:
            filters["date_range"] = {
                "start": date_from,
                "end": date_to
            }

        # Prepare search request
        search_request = {
            "query": query.strip(),
            "filters": filters,
            "limit": limit,
            "search_id": search_id
        }

        logger.info(
            "Performing semantic search",
            search_id=search_id,
            query=query,
            filters=filters
        )

        # Call semantic indexer service
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{settings.INDEXER_SEMANTIQUE_URL}/search",
                    json=search_request
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
                "query": query,
                "filters": filters,
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
            "query": query,
            "filters": filters,
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
            query=query,
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
    Get search suggestions based on prefix
    """
    try:
        # This would typically query an index of common terms
        # For now, return mock suggestions
        suggestions = [
            f"{prefix} traitement",
            f"{prefix} diagnostic",
            f"{prefix} résultats",
            f"{prefix} antécédents",
            f"{prefix} évolution"
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
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve suggestions"
        )


@router.get("/stats")
async def get_search_statistics():
    """
    Get search usage statistics
    """
    try:
        # This would aggregate search statistics from the database
        # For now, return mock statistics
        stats = {
            "total_searches": 1250,
            "unique_users": 45,
            "average_results_per_search": 8.5,
            "popular_queries": [
                {"query": "hypertension", "count": 45},
                {"query": "diabète", "count": 38},
                {"query": "traitement anticoagulant", "count": 29}
            ],
            "search_trends": {
                "last_7_days": 156,
                "last_30_days": 623,
                "last_90_days": 1250
            }
        }

        return stats

    except Exception as e:
        logger.error("Failed to get search statistics", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve search statistics"
        )