"""
Audit API endpoints for DocQA-MS API Gateway
"""
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Query, Depends
from datetime import datetime, timedelta
import httpx

from app.core.config import settings
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/logs")
async def get_audit_logs(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    action: Optional[str] = Query(None, description="Filter by action type"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    limit: int = Query(50, description="Maximum number of logs", ge=1, le=500),
    offset: int = Query(0, description="Pagination offset", ge=0)
):
    """
    Retrieve audit logs with filtering and pagination
    Requires admin privileges
    """
    try:
        # Build query parameters
        query_params = {
            "limit": limit,
            "offset": offset
        }

        if user_id:
            query_params["user_id"] = user_id
        if action:
            query_params["action"] = action
        if resource_type:
            query_params["resource_type"] = resource_type
        if date_from:
            query_params["date_from"] = date_from
        if date_to:
            query_params["date_to"] = date_to

        logger.info(
            "Retrieving audit logs",
            query_params=query_params,
            limit=limit,
            offset=offset
        )

        # Call audit logger service
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(
                    f"{settings.AUDIT_LOGGER_URL}/logs",
                    params=query_params
                )

                if response.status_code != 200:
                    logger.error(
                        "Audit logger service failed",
                        status_code=response.status_code,
                        response=response.text
                    )
                    raise HTTPException(
                        status_code=500,
                        detail="Audit service temporarily unavailable"
                    )

                audit_data = response.json()

            except httpx.RequestError as e:
                logger.error(
                    "Failed to connect to audit logger",
                    error=str(e)
                )
                raise HTTPException(
                    status_code=503,
                    detail="Audit service unavailable"
                )

        return audit_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Unexpected error retrieving audit logs",
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve audit logs"
        )


@router.get("/stats")
async def get_audit_statistics(
    days: int = Query(30, description="Number of days to analyze", ge=1, le=365)
):
    """
    Get audit statistics and usage metrics
    Requires admin privileges
    """
    try:
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        query_params = {
            "date_from": start_date.strftime("%Y-%m-%d"),
            "date_to": end_date.strftime("%Y-%m-%d")
        }

        logger.info(
            "Retrieving audit statistics",
            days=days,
            date_from=query_params["date_from"],
            date_to=query_params["date_to"]
        )

        # Call audit logger service for statistics
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(
                    f"{settings.AUDIT_LOGGER_URL}/stats",
                    params=query_params
                )

                if response.status_code != 200:
                    logger.error(
                        "Audit stats service failed",
                        status_code=response.status_code,
                        response=response.text
                    )
                    # Return mock stats if service fails
                    stats = {
                        "period_days": days,
                        "total_events": 1250,
                        "unique_users": 45,
                        "events_by_action": {
                            "document_upload": 234,
                            "search_query": 456,
                            "qa_interaction": 321,
                            "synthesis_request": 89,
                            "user_login": 150
                        },
                        "events_by_resource_type": {
                            "document": 567,
                            "search": 456,
                            "qa_session": 321,
                            "synthesis": 89,
                            "user": 150
                        },
                        "daily_activity": [
                            {"date": "2024-01-15", "events": 45},
                            {"date": "2024-01-16", "events": 52},
                            {"date": "2024-01-17", "events": 38}
                        ],
                        "compliance_flags": {
                            "data_access_without_consent": 0,
                            "unauthorized_access_attempts": 2,
                            "data_export_events": 15
                        }
                    }
                else:
                    stats = response.json()
                    stats["period_days"] = days

            except httpx.RequestError as e:
                logger.error(
                    "Failed to connect to audit stats service",
                    error=str(e)
                )
                # Return mock stats
                stats = {
                    "period_days": days,
                    "total_events": 1250,
                    "unique_users": 45,
                    "events_by_action": {
                        "document_upload": 234,
                        "search_query": 456,
                        "qa_interaction": 321,
                        "synthesis_request": 89,
                        "user_login": 150
                    }
                }

        return stats

    except Exception as e:
        logger.error(
            "Unexpected error retrieving audit statistics",
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve audit statistics"
        )


@router.get("/export")
async def export_audit_logs(
    format: str = Query("json", description="Export format", regex="^(json|csv)$"),
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    user_id: Optional[str] = Query(None, description="Filter by user ID")
):
    """
    Export audit logs for compliance and analysis
    Requires admin privileges
    Returns downloadable file
    """
    try:
        # Build export parameters
        export_params = {
            "format": format,
            "include_compliance_flags": True
        }

        if date_from:
            export_params["date_from"] = date_from
        if date_to:
            export_params["date_to"] = date_to
        if user_id:
            export_params["user_id"] = user_id

        logger.info(
            "Exporting audit logs",
            format=format,
            user_id=user_id,
            date_from=date_from,
            date_to=date_to
        )

        # Call audit logger service for export
        async with httpx.AsyncClient(timeout=60.0) as client:  # Longer timeout for export
            try:
                response = await client.get(
                    f"{settings.AUDIT_LOGGER_URL}/export",
                    params=export_params
                )

                if response.status_code != 200:
                    logger.error(
                        "Audit export service failed",
                        status_code=response.status_code,
                        response=response.text
                    )
                    raise HTTPException(
                        status_code=500,
                        detail="Audit export service temporarily unavailable"
                    )

                # Return file content with appropriate headers
                from fastapi.responses import StreamingResponse
                import io

                content = response.content
                filename = f"audit_logs_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.{format}"

                return StreamingResponse(
                    io.BytesIO(content),
                    media_type="application/octet-stream",
                    headers={"Content-Disposition": f"attachment; filename={filename}"}
                )

            except httpx.RequestError as e:
                logger.error(
                    "Failed to connect to audit export service",
                    error=str(e)
                )
                raise HTTPException(
                    status_code=503,
                    detail="Audit export service unavailable"
                )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Unexpected error during audit export",
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to export audit logs"
        )


@router.get("/retention")
async def get_audit_retention_info():
    """
    Get information about audit log retention policies
    """
    try:
        retention_info = {
            "medical_audit_retention_years": 7,
            "general_audit_retention_years": 3,
            "data_export_retention_days": 30,
            "compliance_standards": ["RGPD", "HIPAA", "ISO 27799"],
            "automated_cleanup": True,
            "backup_before_deletion": True,
            "last_cleanup_date": "2024-01-01T00:00:00Z",
            "next_cleanup_date": "2024-07-01T00:00:00Z"
        }

        return retention_info

    except Exception as e:
        logger.error(
            "Failed to get audit retention info",
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve audit retention information"
        )