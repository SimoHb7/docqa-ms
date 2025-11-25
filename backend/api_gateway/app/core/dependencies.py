"""
FastAPI dependencies for user context and database access
"""
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
import structlog
from uuid import UUID
import json

from app.core.security import get_current_user
from app.core.database import get_db_connection

logger = structlog.get_logger(__name__)


async def get_or_create_user(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db = Depends(get_db_connection)
) -> Dict[str, Any]:
    """
    Get or create user in database based on Auth0 token
    
    This dependency:
    1. Validates JWT token (via get_current_user)
    2. Checks if user exists in database
    3. Creates user if first login
    4. Updates last_login timestamp
    5. Returns full user record from database
    """
    auth0_sub = current_user.get("sub")
    # Try different locations for email (Auth0 can put it in different claims)
    email = (
        current_user.get("email") or 
        current_user.get("https://api.interfaceclinique.com/email") or
        current_user.get("name")  # Sometimes name contains email
    )
    name = current_user.get("name")
    nickname = current_user.get("nickname")
    picture = current_user.get("picture")
    email_verified = current_user.get("email_verified", False)
    
    if not auth0_sub:
        logger.error("Token missing sub claim", token_claims=list(current_user.keys()))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing sub claim"
        )
    
    # If email is still missing, use auth0_sub as email (fallback)
    if not email:
        logger.warning("Token missing email, using sub as identifier", auth0_sub=auth0_sub)
        email = f"{auth0_sub}@auth0.user"
    
    try:
        # Check if user exists
        query = """
            SELECT id, auth0_sub, email, name, nickname, picture, role, 
                   permissions, is_active, metadata
            FROM users
            WHERE auth0_sub = $1
        """
        user = await db.fetchrow(query, auth0_sub)
        
        if user:
            # Update last_login
            update_query = """
                UPDATE users
                SET last_login = NOW(), updated_at = NOW()
                WHERE auth0_sub = $1
                RETURNING *
            """
            user = await db.fetchrow(update_query, auth0_sub)
            logger.info("User login", user_id=str(user["id"]), email=email)
        else:
            # Create new user (first login)
            insert_query = """
                INSERT INTO users (
                    auth0_sub, email, name, nickname, picture,
                    email_verified, role, permissions, is_active,
                    last_login, metadata
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, NOW(), $10)
                RETURNING *
            """
            user = await db.fetchrow(
                insert_query,
                auth0_sub,
                email,
                name,
                nickname,
                picture,
                email_verified,
                "clinician",  # Default role
                json.dumps([]),  # Default permissions (JSONB)
                True,  # is_active
                json.dumps({})  # metadata (JSONB)
            )
            logger.info("New user created", user_id=str(user["id"]), email=email)
        
        # Convert to dict
        user_dict = dict(user)
        user_dict["id"] = str(user_dict["id"])  # Convert UUID to string
        
        return user_dict
    
    except Exception as e:
        logger.error("Error getting/creating user", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing user authentication"
        )


async def get_user_documents(
    user: Dict[str, Any] = Depends(get_or_create_user),
    db = Depends(get_db_connection)
):
    """
    Get documents accessible by current user
    
    For now, returns all documents, but you can add:
    - User-specific document ownership
    - Organization-based access control
    - Role-based filtering
    """
    user_id = UUID(user["id"])
    
    # TODO: Add user-specific filtering when you add user_id to documents table
    # For now, return all documents
    query = """
        SELECT id, filename, file_type, upload_date, processing_status,
               is_anonymized, metadata, created_at
        FROM documents
        ORDER BY created_at DESC
    """
    
    documents = await db.fetch(query)
    
    return [dict(doc) for doc in documents]


class UserContext:
    """
    User context for database operations
    Ensures all queries are scoped to current user
    """
    
    def __init__(
        self,
        user: Dict[str, Any] = Depends(get_or_create_user),
        db = Depends(get_db_connection)
    ):
        self.user = user
        self.db = db
        self.user_id = UUID(user["id"])
        self.role = user.get("role", "clinician")
        self.permissions = user.get("permissions", [])
    
    async def get_documents(self, limit: int = 100, offset: int = 0):
        """Get user's documents"""
        # TODO: Add WHERE user_id = $1 when you add user_id column
        query = """
            SELECT id, filename, file_type, upload_date, processing_status,
                   is_anonymized, metadata
            FROM documents
            ORDER BY created_at DESC
            LIMIT $1 OFFSET $2
        """
        documents = await self.db.fetch(query, limit, offset)
        return [dict(doc) for doc in documents]
    
    async def get_qa_history(self, limit: int = 50, offset: int = 0):
        """Get user's Q&A history"""
        # TODO: Add WHERE user_id = $1 when you add user_id column
        query = """
            SELECT id, question, answer, document_ids, model_used,
                   confidence_score, created_at
            FROM qa_interactions
            ORDER BY created_at DESC
            LIMIT $1 OFFSET $2
        """
        history = await self.db.fetch(query, limit, offset)
        return [dict(item) for item in history]
    
    async def log_audit(
        self, 
        action: str, 
        resource_type: str,
        resource_id: Optional[str] = None,
        details: Optional[Dict] = None
    ):
        """Log user action for audit trail"""
        query = """
            INSERT INTO audit_logs (
                user_id, action, resource_type, resource_id, details
            )
            VALUES ($1, $2, $3, $4, $5)
        """
        await self.db.execute(
            query,
            self.user_id,
            action,
            resource_type,
            resource_id,
            details or {}
        )
        
        logger.info(
            "Audit log created",
            user_id=str(self.user_id),
            action=action,
            resource_type=resource_type
        )
