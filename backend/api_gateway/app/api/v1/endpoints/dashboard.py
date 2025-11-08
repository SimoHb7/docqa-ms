"""
Dashboard API endpoints for DocQA-MS API Gateway
Provides statistics and activity data for the frontend dashboard
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
import asyncpg
import json

from app.core.database import get_db_pool
from app.core.logging import get_logger
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter()
logger = get_logger(__name__)


@router.get("/stats")
async def get_dashboard_stats():
    """
    Get dashboard statistics
    """
    try:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            # Get total documents count
            total_docs = await conn.fetchval("SELECT COUNT(*) FROM documents")

            # Get documents by status
            docs_by_status = await conn.fetch("""
                SELECT processing_status, COUNT(*) as count
                FROM documents
                GROUP BY processing_status
            """)

            # Get documents by type (from file extensions)
            docs_by_type = await conn.fetch("""
                SELECT
                    CASE
                        WHEN filename ~ '\\.(pdf)$' THEN 'pdf'
                        WHEN filename ~ '\\.(doc|docx)$' THEN 'docx'
                        WHEN filename ~ '\\.(txt)$' THEN 'txt'
                        WHEN filename ~ '\\.(hl7)$' THEN 'hl7'
                        WHEN filename ~ '\\.(fhir|json)$' THEN 'fhir'
                        ELSE 'other'
                    END as file_type,
                    COUNT(*) as count
                FROM documents
                GROUP BY 1
            """)

            # Get total QA interactions
            total_questions = await conn.fetchval("SELECT COUNT(*) FROM qa_interactions")

            # Get average confidence score
            avg_confidence = await conn.fetchval("""
                SELECT COALESCE(AVG(confidence_score), 0) * 100
                FROM qa_interactions
                WHERE confidence_score IS NOT NULL
            """)

            # Get average response time
            avg_response_time = await conn.fetchval("""
                SELECT COALESCE(AVG(response_time_ms), 0)
                FROM qa_interactions
                WHERE response_time_ms IS NOT NULL
            """)

            # Format the response
            stats = {
                "totalDocuments": total_docs or 0,
                "totalQuestions": total_questions or 0,
                "averageConfidence": avg_confidence or 0,
                "averageResponseTime": avg_response_time or 0,
                "documentsByStatus": {row["processing_status"]: row["count"] for row in docs_by_status},
                "documentsByType": {row["file_type"]: row["count"] for row in docs_by_type}
            }

            logger.info("Dashboard stats retrieved")
            return stats

    except Exception as e:
        logger.error("Failed to get dashboard stats", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve dashboard statistics"
        )


@router.get("/activity")
async def get_recent_activity(limit: int = 10):
    """
    Get recent activity data
    """
    try:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            # Get recent audit logs
            activities = await conn.fetch("""
                SELECT
                    action,
                    resource_type,
                    details,
                    timestamp
                FROM audit_logs
                ORDER BY timestamp DESC
                LIMIT $1
            """, limit)

            # Format activities for frontend
            formatted_activities = []
            for activity in activities:
                activity_type = "complete"  # default
                details = activity["details"]
                formatted_detail = ""
                
                # Parse JSON details if it's a string
                if isinstance(details, str):
                    try:
                        details = json.loads(details)
                    except:
                        details = {}
                elif details is None:
                    details = {}

                if activity["action"] == "document_upload":
                    activity_type = "upload"
                    if isinstance(details, dict):
                        filename = details.get("filename", "Document sans nom")
                        size_bytes = details.get("size", 0)
                        # Convert bytes to KB or MB
                        if size_bytes > 1024 * 1024:
                            size_str = f"{size_bytes / (1024 * 1024):.1f} MB"
                        elif size_bytes > 1024:
                            size_str = f"{size_bytes / 1024:.1f} KB"
                        else:
                            size_str = f"{size_bytes} B"
                        formatted_detail = f"Upload: {filename} ({size_str})"
                    else:
                        formatted_detail = "Upload de document"
                        
                elif activity["action"] == "qa_interaction":
                    activity_type = "question"
                    if isinstance(details, dict):
                        question_length = details.get("question_length", 0)
                        formatted_detail = f"Question posée à l'IA ({question_length} car.)"
                    else:
                        formatted_detail = "Question posée à l'IA"
                        
                elif activity["action"] == "user_login":
                    activity_type = "complete"
                    formatted_detail = "Connexion à l'application"
                    
                else:
                    # For any other action
                    if isinstance(details, dict):
                        formatted_detail = details.get("message", activity["action"])
                    else:
                        formatted_detail = str(details) if details else activity["action"]

                formatted_activities.append({
                    "type": activity_type,
                    "timestamp": activity["timestamp"].isoformat(),
                    "details": formatted_detail
                })

            logger.info("Recent activity retrieved", count=len(formatted_activities))
            return formatted_activities

    except Exception as e:
        logger.error("Failed to get recent activity", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve recent activity"
        )


@router.get("/weekly-activity")
async def get_weekly_activity():
    """
    Get weekly activity data for documents and questions (last 7 days)
    """
    try:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            # Get document uploads for the last 7 days
            documents_by_day = await conn.fetch("""
                SELECT
                    DATE(created_at) as day,
                    COUNT(*) as count
                FROM documents
                WHERE created_at >= CURRENT_DATE - INTERVAL '6 days'
                GROUP BY DATE(created_at)
                ORDER BY day
            """)

            # Get questions asked for the last 7 days
            questions_by_day = await conn.fetch("""
                SELECT
                    DATE(created_at) as day,
                    COUNT(*) as count
                FROM qa_interactions
                WHERE created_at >= CURRENT_DATE - INTERVAL '6 days'
                GROUP BY DATE(created_at)
                ORDER BY day
            """)

            # Create a dict for easy lookup
            docs_dict = {row["day"]: row["count"] for row in documents_by_day}
            questions_dict = {row["day"]: row["count"] for row in questions_by_day}

            # Build arrays for the last 7 days (including days with 0 counts)
            from datetime import date, timedelta
            today = date.today()
            documents_data = []
            questions_data = []

            for i in range(6, -1, -1):
                target_day = today - timedelta(days=i)
                documents_data.append(docs_dict.get(target_day, 0))
                questions_data.append(questions_dict.get(target_day, 0))

            logger.info("Weekly activity retrieved")
            return {
                "documents": documents_data,
                "questions": questions_data
            }

    except Exception as e:
        logger.error("Failed to get weekly activity", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve weekly activity"
        )