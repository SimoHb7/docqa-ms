"""
Question-Answering API endpoints for DocQA-MS API Gateway
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query
import httpx
import uuid

from app.core.config import settings
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/ask")
async def ask_question(
    question: str = Query(..., description="Question in natural language"),
    context_documents: Optional[List[str]] = Query(None, description="Specific document IDs to search in"),
    session_id: Optional[str] = Query(None, description="QA session ID for conversation continuity")
):
    """
    Ask a question and get AI-powered answer from documents
    """
    try:
        # Validate question
        if not question or len(question.strip()) < 5:
            raise HTTPException(
                status_code=400,
                detail="Question must be at least 5 characters long"
            )

        # Generate interaction ID
        interaction_id = str(uuid.uuid4())

        # Create or use session
        if not session_id:
            session_id = str(uuid.uuid4())

        # Prepare QA request
        qa_request = {
            "question": question.strip(),
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
                    json=qa_request
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

        # Log interaction in audit
        audit_data = {
            "user_id": "anonymous",  # Would come from auth context
            "session_id": session_id,
            "action": "qa_interaction",
            "resource_type": "qa_session",
            "resource_id": session_id,
            "action_details": {
                "question": question,
                "response_length": len(qa_response.get("answer", "")),
                "sources_count": len(qa_response.get("sources", [])),
                "confidence_score": qa_response.get("confidence_score")
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
            logger.warning("Failed to log QA audit", error=str(e))

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
    offset: int = Query(0, description="Pagination offset", ge=0)
):
    """
    List user's QA sessions
    """
    try:
        # This would query the database for user sessions
        # For now, return mock data
        sessions = [
            {
                "session_id": "session-1",
                "title": "Consultation hypertension",
                "created_at": "2024-01-15T10:30:00Z",
                "last_activity": "2024-01-15T11:45:00Z",
                "interaction_count": 5,
                "total_tokens": 1250
            },
            {
                "session_id": "session-2",
                "title": "Suivi diabète",
                "created_at": "2024-01-20T14:15:00Z",
                "last_activity": "2024-01-20T15:30:00Z",
                "interaction_count": 3,
                "total_tokens": 890
            }
        ]

        return {
            "sessions": sessions[offset:offset+limit],
            "total": len(sessions),
            "limit": limit,
            "offset": offset
        }

    except Exception as e:
        logger.error("Failed to list QA sessions", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve QA sessions"
        )


@router.get("/sessions/{session_id}")
async def get_qa_session(session_id: str):
    """
    Get conversation history for a QA session
    """
    try:
        # This would query the database for session interactions
        # For now, return mock data
        interactions = [
            {
                "interaction_id": "int-1",
                "timestamp": "2024-01-15T10:35:00Z",
                "question": "Quel est le traitement actuel de l'hypertension?",
                "answer": "Le patient suit un traitement par irbesartan 150mg...",
                "confidence_score": 0.91,
                "sources": ["doc-1"],
                "execution_time_ms": 1250
            },
            {
                "interaction_id": "int-2",
                "timestamp": "2024-01-15T11:45:00Z",
                "question": "Y a-t-il des effets secondaires rapportés?",
                "answer": "Aucun effet secondaire significatif n'a été rapporté...",
                "confidence_score": 0.88,
                "sources": ["doc-1"],
                "execution_time_ms": 980
            }
        ]

        return {
            "session_id": session_id,
            "title": "Consultation hypertension",
            "created_at": "2024-01-15T10:30:00Z",
            "interactions": interactions,
            "total_interactions": len(interactions)
        }

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
async def delete_qa_session(session_id: str):
    """
    Delete a QA session and all its interactions
    """
    try:
        # This would delete session data from database
        logger.info("QA session deleted", session_id=session_id)

        return {
            "message": "QA session deleted successfully",
            "session_id": session_id
        }

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