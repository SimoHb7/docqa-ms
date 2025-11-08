"""
Audit API endpoints for DocQA-MS API Gateway
"""
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Query, Depends
from datetime import datetime, timedelta
import httpx
import json

from app.core.config import settings
from app.core.logging import get_logger
from app.core.database import get_db_pool

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
    Retrieve audit logs with filtering and pagination from database
    """
    try:
        logger.info(
            "Retrieving audit logs from database",
            limit=limit,
            offset=offset,
            action=action,
            resource_type=resource_type
        )

        # Build WHERE clause dynamically
        where_clauses = []
        params = []
        param_count = 1

        if user_id:
            where_clauses.append(f"user_id = ${param_count}")
            params.append(user_id)
            param_count += 1
        
        if action:
            where_clauses.append(f"action = ${param_count}")
            params.append(action)
            param_count += 1
        
        if resource_type:
            where_clauses.append(f"resource_type = ${param_count}")
            params.append(resource_type)
            param_count += 1
        
        if date_from:
            where_clauses.append(f"timestamp >= ${param_count}::timestamptz")
            params.append(f"{date_from} 00:00:00+00")
            param_count += 1
        
        if date_to:
            where_clauses.append(f"timestamp <= ${param_count}::timestamptz")
            params.append(f"{date_to} 23:59:59+00")
            param_count += 1

        where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

        # Get logs from database
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            # Get total count
            count_query = f"SELECT COUNT(*) FROM audit_logs {where_sql}"
            total = await conn.fetchval(count_query, *params)

            # Get paginated logs
            query = f"""
                SELECT user_id, action, resource_type, resource_id, details, timestamp
                FROM audit_logs
                {where_sql}
                ORDER BY timestamp DESC
                LIMIT ${param_count} OFFSET ${param_count + 1}
            """
            params.extend([limit, offset])
            
            rows = await conn.fetch(query, *params)

            logs = []
            for row in rows:
                log_entry = {
                    "user_id": str(row['user_id']) if row['user_id'] else None,
                    "action": row['action'],
                    "resource_type": row['resource_type'],
                    "resource_id": row['resource_id'],
                    "details": json.loads(row['details']) if isinstance(row['details'], str) else row['details'],
                    "timestamp": row['timestamp'].isoformat()
                }
                logs.append(log_entry)

        logger.info("Audit logs retrieved", count=len(logs), total=total)

        return {
            "logs": logs,
            "total": total,
            "limit": limit,
            "offset": offset
        }

    except Exception as e:
        logger.error(
            "Unexpected error retrieving audit logs",
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve audit logs: {str(e)}"
        )


@router.get("/stats")
async def get_audit_statistics(
    days: int = Query(30, description="Number of days to analyze", ge=1, le=365)
):
    """
    Get audit statistics and usage metrics from database
    """
    try:
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        logger.info(
            "Retrieving audit statistics from database",
            days=days,
            date_from=start_date.isoformat(),
            date_to=end_date.isoformat()
        )

        pool = await get_db_pool()
        async with pool.acquire() as conn:
            # Get total events
            total_events = await conn.fetchval("""
                SELECT COUNT(*) FROM audit_logs
                WHERE timestamp >= $1 AND timestamp <= $2
            """, start_date, end_date)

            # Get unique users count
            unique_users = await conn.fetchval("""
                SELECT COUNT(DISTINCT user_id) FROM audit_logs
                WHERE timestamp >= $1 AND timestamp <= $2
                AND user_id IS NOT NULL
            """, start_date, end_date)

            # Get events by action
            action_rows = await conn.fetch("""
                SELECT action, COUNT(*) as count
                FROM audit_logs
                WHERE timestamp >= $1 AND timestamp <= $2
                GROUP BY action
                ORDER BY count DESC
            """, start_date, end_date)

            events_by_action = {row['action']: row['count'] for row in action_rows}

            # Get events by resource type
            resource_rows = await conn.fetch("""
                SELECT resource_type, COUNT(*) as count
                FROM audit_logs
                WHERE timestamp >= $1 AND timestamp <= $2
                GROUP BY resource_type
                ORDER BY count DESC
            """, start_date, end_date)

            events_by_resource_type = {row['resource_type']: row['count'] for row in resource_rows}

            # Get daily activity (last 7 days)
            daily_rows = await conn.fetch("""
                SELECT DATE(timestamp) as date, COUNT(*) as count
                FROM audit_logs
                WHERE timestamp >= $1 AND timestamp <= $2
                GROUP BY DATE(timestamp)
                ORDER BY date DESC
                LIMIT 7
            """, start_date, end_date)

            daily_activity = [
                {"date": row['date'].isoformat(), "events": row['count']}
                for row in daily_rows
            ]

        stats = {
            "period_days": days,
            "total_events": total_events,
            "unique_users": unique_users or 0,
            "events_by_action": events_by_action,
            "events_by_resource_type": events_by_resource_type,
            "daily_activity": daily_activity,
            "compliance_flags": {
                "data_access_without_consent": 0,
                "unauthorized_access_attempts": 0,
                "data_export_events": 0
            }
        }

        logger.info("Audit statistics retrieved", total_events=total_events)
        return stats

    except Exception as e:
        logger.error(
            "Unexpected error retrieving audit statistics",
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve audit statistics: {str(e)}"
        )


@router.get("/export")
async def export_audit_logs(
    format: str = Query("json", description="Export format", regex="^(json|csv)$"),
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    user_id: Optional[str] = Query(None, description="Filter by user ID")
):
    """
    Export audit logs from database for compliance and analysis
    Returns downloadable file in JSON or CSV format
    """
    try:
        from fastapi.responses import StreamingResponse
        import io
        import csv

        logger.info(
            "Exporting audit logs from database",
            format=format,
            user_id=user_id,
            date_from=date_from,
            date_to=date_to
        )

        # Build WHERE clause
        where_clauses = []
        params = []
        param_count = 1

        if user_id:
            where_clauses.append(f"user_id = ${param_count}")
            params.append(user_id)
            param_count += 1
        
        if date_from:
            where_clauses.append(f"timestamp >= ${param_count}::timestamptz")
            params.append(f"{date_from} 00:00:00+00")
            param_count += 1
        
        if date_to:
            where_clauses.append(f"timestamp <= ${param_count}::timestamptz")
            params.append(f"{date_to} 23:59:59+00")
            param_count += 1

        where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

        # Get audit logs
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            query = f"""
                SELECT user_id, action, resource_type, resource_id, details, timestamp
                FROM audit_logs
                {where_sql}
                ORDER BY timestamp DESC
                LIMIT 10000
            """
            rows = await conn.fetch(query, *params)

            logs = []
            for row in rows:
                log_entry = {
                    "user_id": str(row['user_id']) if row['user_id'] else None,
                    "action": row['action'],
                    "resource_type": row['resource_type'],
                    "resource_id": str(row['resource_id']) if row['resource_id'] else None,  # Convert UUID to string
                    "details": json.loads(row['details']) if isinstance(row['details'], str) else row['details'],
                    "timestamp": row['timestamp'].isoformat()
                }
                logs.append(log_entry)

        # Generate file content based on format
        filename = f"audit_logs_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.{format}"
        
        if format == "json":
            content = json.dumps({"logs": logs, "exported_at": datetime.utcnow().isoformat(), "total_records": len(logs)}, indent=2)
            media_type = "application/json"
            output = io.BytesIO(content.encode('utf-8'))
        
        elif format == "csv":
            output = io.StringIO()
            if logs:
                writer = csv.DictWriter(output, fieldnames=["timestamp", "user_id", "action", "resource_type", "resource_id", "details"])
                writer.writeheader()
                for log in logs:
                    writer.writerow({
                        "timestamp": log["timestamp"],
                        "user_id": log["user_id"] or "",
                        "action": log["action"],
                        "resource_type": log["resource_type"],
                        "resource_id": log["resource_id"],
                        "details": json.dumps(log["details"]) if log["details"] else ""
                    })
            media_type = "text/csv"
            output = io.BytesIO(output.getvalue().encode('utf-8'))

        logger.info("Audit logs exported", format=format, records=len(logs))

        return StreamingResponse(
            output,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
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
            detail=f"Failed to export audit logs: {str(e)}"
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