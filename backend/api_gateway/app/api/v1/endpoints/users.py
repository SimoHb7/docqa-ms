"""
User profile and management endpoints
"""
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
import structlog

from app.core.dependencies import get_or_create_user, UserContext
from app.core.database import get_db_connection

router = APIRouter()
logger = structlog.get_logger(__name__)


class UserProfile(BaseModel):
    """User profile response"""
    id: str
    auth0_sub: str
    email: EmailStr
    name: Optional[str] = None
    nickname: Optional[str] = None
    picture: Optional[str] = None
    role: str
    permissions: List[str] = []
    is_active: bool
    email_verified: bool
    last_login: Optional[str] = None
    created_at: str


class UpdateUserProfile(BaseModel):
    """Update user profile request"""
    name: Optional[str] = None
    nickname: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@router.get("/me", response_model=UserProfile)
async def get_my_profile(
    current_user: Dict[str, Any] = Depends(get_or_create_user)
):
    """
    Get current user's profile
    """
    logger.info("Profile accessed", user_id=current_user["id"])
    
    return UserProfile(
        id=current_user["id"],
        auth0_sub=current_user["auth0_sub"],
        email=current_user["email"],
        name=current_user.get("name"),
        nickname=current_user.get("nickname"),
        picture=current_user.get("picture"),
        role=current_user["role"],
        permissions=current_user.get("permissions", []),
        is_active=current_user["is_active"],
        email_verified=current_user.get("email_verified", False),
        last_login=str(current_user.get("last_login")) if current_user.get("last_login") else None,
        created_at=str(current_user["created_at"])
    )


@router.patch("/me")
async def update_my_profile(
    update_data: UpdateUserProfile,
    current_user: Dict[str, Any] = Depends(get_or_create_user),
    db = Depends(get_db_connection)
):
    """
    Update current user's profile
    """
    try:
        user_id = current_user["id"]
        
        # Build update query dynamically
        updates = []
        values = []
        param_count = 1
        
        if update_data.name is not None:
            updates.append(f"name = ${param_count}")
            values.append(update_data.name)
            param_count += 1
        
        if update_data.nickname is not None:
            updates.append(f"nickname = ${param_count}")
            values.append(update_data.nickname)
            param_count += 1
        
        if update_data.metadata is not None:
            updates.append(f"metadata = ${param_count}")
            values.append(update_data.metadata)
            param_count += 1
        
        if not updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        updates.append("updated_at = NOW()")
        values.append(user_id)
        
        query = f"""
            UPDATE users
            SET {', '.join(updates)}
            WHERE id = ${param_count}
            RETURNING *
        """
        
        updated_user = await db.fetchrow(query, *values)
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        logger.info("Profile updated", user_id=user_id)
        
        return {
            "success": True,
            "message": "Profile updated successfully",
            "user": dict(updated_user)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error updating profile", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating profile"
        )


@router.get("/me/stats")
async def get_my_stats(
    user_context: UserContext = Depends(UserContext)
):
    """
    Get current user's usage statistics
    """
    try:
        # Count documents (TODO: filter by user_id when column added)
        doc_query = "SELECT COUNT(*) as count FROM documents"
        doc_result = await user_context.db.fetchrow(doc_query)
        document_count = doc_result["count"] if doc_result else 0
        
        # Count QA interactions (TODO: filter by user_id when column added)
        qa_query = "SELECT COUNT(*) as count FROM qa_interactions"
        qa_result = await user_context.db.fetchrow(qa_query)
        qa_count = qa_result["count"] if qa_result else 0
        
        # Count audit logs
        audit_query = """
            SELECT COUNT(*) as count 
            FROM audit_logs 
            WHERE user_id = $1
        """
        audit_result = await user_context.db.fetchrow(audit_query, user_context.user_id)
        audit_count = audit_result["count"] if audit_result else 0
        
        logger.info("Stats retrieved", user_id=str(user_context.user_id))
        
        return {
            "user_id": str(user_context.user_id),
            "email": user_context.user["email"],
            "role": user_context.role,
            "stats": {
                "documents_uploaded": document_count,
                "questions_asked": qa_count,
                "actions_logged": audit_count
            }
        }
    
    except Exception as e:
        logger.error("Error getting stats", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving statistics"
        )


@router.get("/me/documents")
async def get_my_documents(
    limit: int = 50,
    offset: int = 0,
    user_context: UserContext = Depends(UserContext)
):
    """
    Get current user's documents
    """
    try:
        documents = await user_context.get_documents(limit=limit, offset=offset)
        
        logger.info(
            "Documents retrieved",
            user_id=str(user_context.user_id),
            count=len(documents)
        )
        
        return {
            "documents": documents,
            "count": len(documents),
            "limit": limit,
            "offset": offset
        }
    
    except Exception as e:
        logger.error("Error getting documents", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving documents"
        )


@router.get("/me/qa-history")
async def get_my_qa_history(
    limit: int = 50,
    offset: int = 0,
    user_context: UserContext = Depends(UserContext)
):
    """
    Get current user's Q&A history
    """
    try:
        history = await user_context.get_qa_history(limit=limit, offset=offset)
        
        logger.info(
            "QA history retrieved",
            user_id=str(user_context.user_id),
            count=len(history)
        )
        
        return {
            "history": history,
            "count": len(history),
            "limit": limit,
            "offset": offset
        }
    
    except Exception as e:
        logger.error("Error getting QA history", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving Q&A history"
        )
