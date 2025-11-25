"""
Question-Answering API endpoints for DocQA-MS API Gateway
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Depends
import httpx
import uuid
import json
from datetime import datetime

from app.core.config import settings
from app.core.logging import get_logger
from app.core.database import execute_query, execute_one, execute_insert, get_db_pool
from app.core.dependencies import get_or_create_user

router = APIRouter()
logger = get_logger(__name__)


@router.post("/ask")
async def ask_question(
    question: str = Query(..., description="Question in natural language"),
    context_documents: Optional[List[str]] = Query(None, description="Specific document IDs to search in"),
    session_id: Optional[str] = Query(None, description="QA session ID for conversation continuity"),
    current_user: Dict[str, Any] = Depends(get_or_create_user)
):
    """
    Ask a question and get AI-powered answer from documents (Protected - requires JWT token)
    """
    logger.info("QA request", user_id=current_user["id"], question_length=len(question))
    try:
        # Validate question
        question_trimmed = question.strip() if question else ""
        if not question_trimmed:
            raise HTTPException(
                status_code=400,
                detail="Question cannot be empty"
            )
        
        if len(question_trimmed) < 5:
            raise HTTPException(
                status_code=400,
                detail=f"Question must be at least 5 characters long (currently {len(question_trimmed)} characters)"
            )

        # Generate interaction ID
        interaction_id = str(uuid.uuid4())

        # Create or use session
        if not session_id:
            session_id = str(uuid.uuid4())

        # Prepare QA request
        qa_request = {
            "question": question_trimmed,
            "context_documents": context_documents or [],
            "session_id": session_id,
            "interaction_id": interaction_id
        }

        logger.info(
            "Processing QA request",
            interaction_id=interaction_id,
            session_id=session_id,
            question_length=len(question),
            context_docs=len(context_documents) if context_documents else 0
        )

        # Call LLM QA service
        async with httpx.AsyncClient(timeout=60.0) as client:  # Longer timeout for LLM
            try:
                response = await client.post(
                    f"{settings.LLM_QA_URL}/qa/ask",
                    json={"question": question.strip(), "context_documents": context_documents or [], "session_id": session_id}
                )

                if response.status_code != 200:
                    logger.error(
                        "LLM QA service failed",
                        interaction_id=interaction_id,
                        status_code=response.status_code,
                        response=response.text
                    )
                    raise HTTPException(
                        status_code=500,
                        detail="Question answering service temporarily unavailable"
                    )

                qa_response = response.json()

            except httpx.RequestError as e:
                logger.error(
                    "Failed to connect to LLM QA service",
                    interaction_id=interaction_id,
                    error=str(e)
                )
                raise HTTPException(
                    status_code=503,
                    detail="Question answering service unavailable"
                )

        # Save QA interaction to database for analytics and audit
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            # Insert into qa_interactions table (matching actual schema)
            await conn.execute("""
                INSERT INTO qa_interactions (
                    id, user_id, question, answer, context_documents, 
                    confidence_score, response_time_ms, llm_model
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """, 
                interaction_id,
                current_user["id"],  # Add user_id
                question,
                qa_response.get("answer", ""),
                context_documents or [],
                qa_response.get("confidence_score", 0.0),
                qa_response.get("execution_time_ms", 0),
                qa_response.get("model_used", "llama3.1:8b")
            )
            
            # Insert audit log
            await conn.execute("""
                INSERT INTO audit_logs (
                    user_id, action, resource_type, resource_id, details
                )
                VALUES ($1, $2, $3, $4, $5::jsonb)
            """,
                current_user["id"],  # Add user_id for audit log
                "qa_interaction",
                "qa_session",
                str(interaction_id),
                json.dumps({
                    "question_length": len(question),
                    "response_length": len(qa_response.get("answer", "")),
                    "sources_count": len(qa_response.get("sources", [])),
                    "confidence_score": qa_response.get("confidence_score", 0.0),
                    "session_id": session_id
                })
            )

        # Format response
        result = {
            "interaction_id": interaction_id,
            "session_id": session_id,
            "question": question,
            "answer": qa_response.get("answer", ""),
            "sources": qa_response.get("sources", []),
            "confidence_score": qa_response.get("confidence_score", 0.0),
            "execution_time_ms": qa_response.get("execution_time_ms", 0),
            "model_used": qa_response.get("model_used", "unknown")
        }

        logger.info(
            "QA interaction completed",
            interaction_id=interaction_id,
            confidence_score=result["confidence_score"],
            sources_count=len(result["sources"])
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Unexpected error during QA",
            question=question[:100],  # Truncate for logging
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail="Question answering failed due to internal error"
        )


@router.get("/sessions")
async def list_qa_sessions(
    limit: int = Query(20, description="Maximum number of sessions", ge=1, le=100),
    offset: int = Query(0, description="Pagination offset", ge=0),
    current_user: Dict[str, Any] = Depends(get_or_create_user)
):
    """
    List user's QA sessions from database (Protected - requires JWT)
    """
    logger.info("List QA sessions", user_id=current_user["id"])
    try:
        # Get distinct sessions from QA interactions
        # Note: We're grouping by user_id since we don't have a sessions table yet
        query = """
            SELECT 
                user_id as session_id,
                MIN(created_at) as created_at,
                MAX(created_at) as last_activity,
                COUNT(*) as interaction_count,
                STRING_AGG(DISTINCT LEFT(question, 50), ' | ') as title_preview
            FROM qa_interactions
            WHERE user_id IS NOT NULL
            GROUP BY user_id
            ORDER BY MAX(created_at) DESC
            LIMIT $1 OFFSET $2
        """
        
        count_query = """
            SELECT COUNT(DISTINCT user_id) as total
            FROM qa_interactions
            WHERE user_id IS NOT NULL
        """
        
        rows = await execute_query(query, limit, offset)
        count_result = await execute_one(count_query)
        
        sessions = []
        for row in rows:
            sessions.append({
                "session_id": row['session_id'],
                "title": row['title_preview'] or "Untitled Session",
                "created_at": row['created_at'].isoformat() if row['created_at'] else None,
                "last_activity": row['last_activity'].isoformat() if row['last_activity'] else None,
                "interaction_count": row['interaction_count'],
                "total_tokens": 0  # Would need to track tokens
            })

        return {
            "sessions": sessions,
            "total": count_result['total'] if count_result else 0,
            "limit": limit,
            "offset": offset
        }

    except Exception as e:
        logger.error("Failed to list QA sessions", error=str(e))
        # Return empty list on error
        return {
            "sessions": [],
            "total": 0,
            "limit": limit,
            "offset": offset
        }


@router.get("/sessions/{session_id}")
async def get_qa_session(
    session_id: str,
    current_user: Dict[str, Any] = Depends(get_or_create_user)
):
    """
    Get conversation history for a QA session from database (Protected - requires JWT)
    """
    logger.info("Get QA session", user_id=current_user["id"], session_id=session_id)
    try:
        # Get interactions for this session (using user_id as session_id)
        query = """
            SELECT 
                id::text as interaction_id,
                created_at,
                question,
                answer,
                confidence_score,
                context_documents,
                response_time_ms,
                llm_model
            FROM qa_interactions
            WHERE user_id = $1
            ORDER BY created_at ASC
        """
        
        rows = await execute_query(query, session_id)
        
        if not rows:
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found"
            )
        
        interactions = []
        for row in rows:
            interactions.append({
                "interaction_id": row['interaction_id'],
                "timestamp": row['created_at'].isoformat() if row['created_at'] else None,
                "question": row['question'],
                "answer": row['answer'],
                "confidence_score": float(row['confidence_score']) if row['confidence_score'] else None,
                "sources": [str(doc_id) for doc_id in row['context_documents']] if row['context_documents'] else [],
                "execution_time_ms": row['response_time_ms'],
                "llm_model": row['llm_model']
            })
        
        # Use first question as title
        title = interactions[0]['question'][:50] + "..." if interactions else "Untitled"

        return {
            "session_id": session_id,
            "title": title,
            "created_at": interactions[0]['timestamp'] if interactions else None,
            "interactions": interactions,
            "total_interactions": len(interactions)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to get QA session",
            session_id=session_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve QA session"
        )


@router.delete("/sessions/{session_id}")
async def delete_qa_session(
    session_id: str,
    current_user: Dict[str, Any] = Depends(get_or_create_user)
):
    """
    Delete a QA session and all its interactions from database (Protected - requires JWT)
    """
    logger.info("Delete QA session", user_id=current_user["id"], session_id=session_id)
    try:
        # Delete all interactions for this user/session
        query = """
            DELETE FROM qa_interactions
            WHERE user_id = $1
            RETURNING id
        """
        
        result = await execute_query(query, session_id)
        deleted_count = len(result) if result else 0
        
        if deleted_count == 0:
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found"
            )
        
        logger.info("QA session deleted", session_id=session_id, interactions_deleted=deleted_count)

        return {
            "message": "QA session deleted successfully",
            "session_id": session_id,
            "interactions_deleted": deleted_count
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to delete QA session",
            session_id=session_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to delete QA session"
        )