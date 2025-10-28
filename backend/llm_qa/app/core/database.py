"""
Database operations for LLM Q&A service
"""
import asyncpg
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class DatabaseManager:
    """Database connection and operations manager"""
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self):
        """Create database connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                settings.DATABASE_URL,
                min_size=2,
                max_size=10,
                command_timeout=60
            )
            logger.info("Database connection pool created")
        except Exception as e:
            logger.error("Failed to create database pool", error=str(e))
            raise
    
    async def disconnect(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")
    
    async def save_qa_interaction(
        self,
        user_id: str,
        question: str,
        answer: str,
        context_documents: List[str],
        confidence_score: float,
        response_time_ms: int,
        llm_model: str,
        sources: List[Dict[str, Any]] = None
    ) -> str:
        """
        Save a Q&A interaction to the database
        
        Returns the interaction ID (UUID)
        """
        try:
            async with self.pool.acquire() as conn:
                # Convert document IDs to PostgreSQL UUID array format
                doc_array = context_documents if context_documents else []
                
                # Save interaction
                interaction_id = await conn.fetchval(
                    """
                    INSERT INTO qa_interactions 
                    (user_id, question, answer, context_documents, confidence_score, 
                     response_time_ms, llm_model)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                    RETURNING id
                    """,
                    user_id,
                    question,
                    answer,
                    doc_array,
                    round(confidence_score, 2),
                    response_time_ms,
                    llm_model
                )
                
                logger.info("Saved Q&A interaction",
                           interaction_id=str(interaction_id),
                           user_id=user_id,
                           question_length=len(question),
                           answer_length=len(answer))
                
                return str(interaction_id)
                
        except Exception as e:
            logger.error("Failed to save Q&A interaction",
                        user_id=user_id,
                        error=str(e))
            raise
    
    async def get_qa_history(
        self,
        user_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get Q&A interaction history"""
        try:
            async with self.pool.acquire() as conn:
                if user_id:
                    rows = await conn.fetch(
                        """
                        SELECT id, user_id, question, answer, confidence_score, 
                               llm_model, created_at
                        FROM qa_interactions
                        WHERE user_id = $1
                        ORDER BY created_at DESC
                        LIMIT $2
                        """,
                        user_id,
                        limit
                    )
                else:
                    rows = await conn.fetch(
                        """
                        SELECT id, user_id, question, answer, confidence_score,
                               llm_model, created_at
                        FROM qa_interactions
                        ORDER BY created_at DESC
                        LIMIT $1
                        """,
                        limit
                    )
                
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error("Failed to get Q&A history", error=str(e))
            return []
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get Q&A statistics"""
        try:
            async with self.pool.acquire() as conn:
                stats = await conn.fetchrow(
                    """
                    SELECT 
                        COUNT(*) as total_questions,
                        COUNT(DISTINCT user_id) as unique_users,
                        AVG(confidence_score) as avg_confidence,
                        AVG(response_time_ms) as avg_response_time
                    FROM qa_interactions
                    """
                )
                
                return {
                    "total_questions": stats['total_questions'],
                    "unique_users": stats['unique_users'],
                    "avg_confidence": float(stats['avg_confidence']) if stats['avg_confidence'] else 0.0,
                    "avg_response_time_ms": float(stats['avg_response_time']) if stats['avg_response_time'] else 0.0
                }
                
        except Exception as e:
            logger.error("Failed to get stats", error=str(e))
            return {
                "total_questions": 0,
                "unique_users": 0,
                "avg_confidence": 0.0,
                "avg_response_time_ms": 0.0
            }


# Global database manager instance
db_manager = DatabaseManager()
