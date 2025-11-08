"""
Audit endpoints for DocQA-MS Audit Logger
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query
import psycopg2
import psycopg2.extras
import structlog
from pydantic import BaseModel

from app.core.config import settings

router = APIRouter()
logger = structlog.get_logger(__name__)


class AuditEvent(BaseModel):
    """Audit event model"""
    id: Optional[int] = None
    timestamp: datetime
    user_id: str
    action: str
    resource: str
    resource_id: Optional[str] = None
    details: Dict[str, Any]
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    response_time_ms: Optional[int] = None


class AuditLogRequest(BaseModel):
    """Request model for logging audit events"""
    user_id: str
    action: str
    resource: str
    resource_id: Optional[str] = None
    details: Dict[str, Any]
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    response_time_ms: Optional[int] = None


def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(
        host=settings.DATABASE_HOST,
        port=settings.DATABASE_PORT,
        user=settings.DATABASE_USER,
        password=settings.DATABASE_PASSWORD,
        database=settings.DATABASE_NAME,
    )


@router.post("/log")
async def log_audit_event(request: AuditLogRequest):
    """Log an audit event"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # Insert audit event
                cursor.execute("""
                    INSERT INTO audit_logs (
                        timestamp, user_id, action, resource, resource_id,
                        details, ip_address, user_agent, session_id, response_time_ms
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """, (
                    datetime.utcnow(),
                    request.user_id,
                    request.action,
                    request.resource,
                    request.resource_id,
                    psycopg2.extras.Json(request.details),
                    request.ip_address,
                    request.user_agent,
                    request.session_id,
                    request.response_time_ms,
                ))
                conn.commit()

        logger.info(
            "Audit event logged",
            user_id=request.user_id,
            action=request.action,
            resource=request.resource,
        )

        return {"status": "logged", "message": "Audit event recorded successfully"}

    except Exception as e:
        logger.error("Failed to log audit event", error=str(e), user_id=request.user_id)
        raise HTTPException(status_code=500, detail="Failed to log audit event")


@router.get("/logs")
async def get_audit_logs(
    user_id: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    resource: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(100, le=1000),
    offset: int = Query(0),
):
    """Retrieve audit logs with optional filtering"""
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                # Build query with filters
                query = """
                    SELECT id, timestamp, user_id, action, resource, resource_id,
                           details, ip_address, user_agent, session_id, response_time_ms
                    FROM audit_logs
                    WHERE 1=1
                """
                params = []

                if user_id:
                    query += " AND user_id = %s"
                    params.append(user_id)

                if action:
                    query += " AND action = %s"
                    params.append(action)

                if resource:
                    query += " AND resource = %s"
                    params.append(resource)

                if start_date:
                    query += " AND timestamp >= %s"
                    params.append(start_date)

                if end_date:
                    query += " AND timestamp <= %s"
                    params.append(end_date)

                query += " ORDER BY timestamp DESC LIMIT %s OFFSET %s"
                params.extend([limit, offset])

                cursor.execute(query, params)
                logs = cursor.fetchall()

                # Convert to list of dicts
                result = []
                for log in logs:
                    log_dict = dict(log)
                    # Ensure details is properly parsed
                    if isinstance(log_dict['details'], str):
                        import json
                        log_dict['details'] = json.loads(log_dict['details'])
                    result.append(log_dict)

        return {
            "logs": result,
            "total": len(result),
            "limit": limit,
            "offset": offset
        }

    except Exception as e:
        logger.error("Failed to retrieve audit logs", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve audit logs")


@router.get("/stats")
async def get_audit_statistics(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
):
    """Get audit statistics"""
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                # Default to last 30 days if no dates provided
                if not start_date:
                    start_date = datetime.utcnow() - timedelta(days=30)
                if not end_date:
                    end_date = datetime.utcnow()

                # Get action counts
                cursor.execute("""
                    SELECT action, COUNT(*) as count
                    FROM audit_logs
                    WHERE timestamp BETWEEN %s AND %s
                    GROUP BY action
                    ORDER BY count DESC
                """, (start_date, end_date))
                action_stats = cursor.fetchall()

                # Get user activity
                cursor.execute("""
                    SELECT user_id, COUNT(*) as activity_count
                    FROM audit_logs
                    WHERE timestamp BETWEEN %s AND %s
                    GROUP BY user_id
                    ORDER BY activity_count DESC
                    LIMIT 10
                """, (start_date, end_date))
                user_stats = cursor.fetchall()

                # Get total events
                cursor.execute("""
                    SELECT COUNT(*) as total_events
                    FROM audit_logs
                    WHERE timestamp BETWEEN %s AND %s
                """, (start_date, end_date))
                total_events = cursor.fetchone()['total_events']

        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "total_events": total_events,
            "action_breakdown": dict(action_stats),
            "top_users": dict(user_stats)
        }

    except Exception as e:
        logger.error("Failed to get audit statistics", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get audit statistics")


@router.get("/retention")
async def get_audit_retention_info():
    """Get audit log retention information"""
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                # Get oldest and newest records
                cursor.execute("""
                    SELECT
                        MIN(timestamp) as oldest_record,
                        MAX(timestamp) as newest_record,
                        COUNT(*) as total_records
                    FROM audit_logs
                """)
                retention_info = cursor.fetchone()

        return {
            "oldest_record": retention_info['oldest_record'].isoformat() if retention_info['oldest_record'] else None,
            "newest_record": retention_info['newest_record'].isoformat() if retention_info['newest_record'] else None,
            "total_records": retention_info['total_records'],
            "retention_policy": "90 days"  # Configurable in future
        }

    except Exception as e:
        logger.error("Failed to get retention info", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get retention info")