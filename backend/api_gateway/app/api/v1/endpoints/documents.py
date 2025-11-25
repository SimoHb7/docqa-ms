"""
Documents API endpoints for DocQA-MS API Gateway
"""
import os
import uuid
import json
from typing import List, Optional, Dict, Any
import aiofiles
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
import httpx

from app.core.config import settings
from app.core.logging import get_logger
from app.core.database import get_db_pool
from app.core.dependencies import get_or_create_user, UserContext

router = APIRouter()
logger = get_logger(__name__)


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    patient_id: Optional[str] = Form(None),
    document_type: Optional[str] = Form(None),
    current_user: Dict[str, Any] = Depends(get_or_create_user)
):
    """
    Upload a document for processing (Protected - requires JWT token)
    """
    logger.info("Document upload started", user_id=current_user["id"], filename=file.filename)
    try:
        # Validate file type
        if file.filename:
            file_extension = file.filename.split('.')[-1].lower()
            if file_extension not in settings.ALLOWED_FILE_TYPES:
                raise HTTPException(
                    status_code=400,
                    detail=f"File type not allowed. Allowed types: {', '.join(settings.ALLOWED_FILE_TYPES)}"
                )

        # Validate file size
        file_content = await file.read()
        file_size_mb = len(file_content) / (1024 * 1024)
        if file_size_mb > settings.MAX_UPLOAD_SIZE_MB:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE_MB}MB"
            )

        # Generate document ID
        document_id = str(uuid.uuid4())

        # Save file temporarily
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        file_path = os.path.join(settings.UPLOAD_DIR, f"{document_id}_{file.filename}")

        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)

        # Prepare metadata
        metadata = {
            "filename": file.filename,
            "content_type": file.content_type,
            "size": len(file_content),
            "patient_id": patient_id,
            "document_type": document_type
        }

        # Send to document ingestor service
        async with httpx.AsyncClient() as client:
            try:
                # Prepare multipart form data for file upload
                files = {
                    'file': (file.filename, file_content, file.content_type)
                }
                data = {
                    'document_id': document_id,  # Pass the document ID
                    'user_id': current_user["id"]  # Pass the user ID for ownership
                }
                if patient_id:
                    data['patient_id'] = patient_id
                if document_type:
                    data['document_type'] = document_type

                response = await client.post(
                    f"{settings.DOC_INGESTOR_URL}/api/v1/documents/upload",
                    files=files,
                    data=data,
                    timeout=30.0
                )

                if response.status_code != 200:
                    logger.error(
                        "Document ingestor failed",
                        document_id=document_id,
                        status_code=response.status_code,
                        response=response.text
                    )
                    raise HTTPException(
                        status_code=500,
                        detail="Document processing failed"
                    )

            except httpx.RequestError as e:
                logger.error(
                    "Failed to connect to document ingestor",
                    document_id=document_id,
                    error=str(e)
                )
                raise HTTPException(
                    status_code=503,
                    detail="Document processing service unavailable"
                )

        logger.info(
            "Document uploaded successfully",
            document_id=document_id,
            filename=file.filename,
            size=len(file_content)
        )

        # Log to audit_logs table
        try:
            from uuid import UUID
            pool = await get_db_pool()
            async with pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO audit_logs (
                        user_id, action, resource_type, resource_id, details
                    )
                    VALUES ($1, $2, $3, $4, $5::jsonb)
                """,
                    UUID(current_user["id"]),  # Current user ID
                    "document_upload",
                    "document",
                    document_id,
                    json.dumps({
                        "filename": file.filename,
                        "size": len(file_content),
                        "content_type": file.content_type,
                        "patient_id": patient_id,
                        "document_type": document_type
                    })
                )
        except Exception as e:
            logger.warning("Failed to log audit", error=str(e))

        return {
            "document_id": document_id,
            "status": "uploaded",
            "message": "Document uploaded successfully and queued for processing"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Unexpected error during document upload",
            error=str(e),
            filename=file.filename if file else None
        )
        raise HTTPException(
            status_code=500,
            detail="Internal server error during document upload"
        )


@router.get("/")
async def list_documents(
    status: Optional[str] = None,
    document_type: Optional[str] = None,
    patient_id: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: Dict[str, Any] = Depends(get_or_create_user),
    db = Depends(get_db_pool)
):
    """
    List documents with filtering and pagination (Protected - requires JWT)
    Shows only documents uploaded by current user
    """
    logger.info("List documents", user_id=current_user["id"])
    try:
        from uuid import UUID
        user_uuid = UUID(current_user["id"])
        
        # Build WHERE clause dynamically - strict user isolation
        where_clauses = ["user_id = $1"]  # All users see only their own documents
        params = [user_uuid]
        param_count = 2
        
        if status:
            where_clauses.append(f"processing_status = ${param_count}")
            params.append(status)
            param_count += 1
        
        if document_type:
            where_clauses.append(f"file_type = ${param_count}")
            params.append(document_type)
            param_count += 1
        
        if patient_id:
            where_clauses.append(f"metadata->>'patient_id' = ${param_count}")
            params.append(patient_id)
            param_count += 1
        
        where_clause = " AND ".join(where_clauses)
        
        # Get documents from database
        async with db.acquire() as conn:
            # Get total count
            count_query = f"""
                SELECT COUNT(*) as total
                FROM documents
                WHERE {where_clause}
            """
            count_result = await conn.fetchrow(count_query, *params)
            total = count_result["total"] if count_result else 0
            
            # Get documents
            query = f"""
                SELECT 
                    id::text,
                    filename,
                    file_type,
                    file_size,
                    upload_date,
                    processing_status,
                    is_anonymized,
                    indexed_at,
                    metadata,
                    created_at
                FROM documents
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT ${param_count} OFFSET ${param_count + 1}
            """
            params.extend([limit, offset])
            
            rows = await conn.fetch(query, *params)
            
            documents = []
            for row in rows:
                doc = dict(row)
                # Convert UUID to string
                if doc.get("id"):
                    doc["id"] = str(doc["id"])
                # Extract patient_id from metadata to top level for frontend convenience
                if doc.get("metadata") and isinstance(doc["metadata"], dict):
                    doc["patient_id"] = doc["metadata"].get("patient_id")
                    doc["document_type"] = doc["metadata"].get("document_type")
                documents.append(doc)
            
            logger.info(
                "Documents retrieved", 
                user_id=current_user["id"],
                count=len(documents),
                total=total
            )
            
            return {
                "data": documents,  # Changed from "documents" to "data" for frontend compatibility
                "total": total,
                "limit": limit,
                "offset": offset
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to list documents", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve documents: {str(e)}"
        )


@router.get("/{document_id}")
async def get_document(
    document_id: str,
    current_user: Dict[str, Any] = Depends(get_or_create_user)
):
    """
    Get document details (Protected - requires JWT)
    """
    logger.info("Get document", user_id=current_user["id"], document_id=document_id)
    """
    Get detailed information about a specific document
    """
    try:
        # Forward request to document ingestor service
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.DOC_INGESTOR_URL}/api/v1/documents/{document_id}",
                timeout=30.0
            )

            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="Document not found")
            elif response.status_code != 200:
                logger.error(
                    "Document ingestor get failed",
                    document_id=document_id,
                    status_code=response.status_code,
                    response=response.text
                )
                raise HTTPException(
                    status_code=500,
                    detail="Failed to retrieve document"
                )

            return response.json()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to get document",
            document_id=document_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve document"
        )


@router.get("/{document_id}/download")
async def download_document(
    document_id: str,
    current_user: Dict[str, Any] = Depends(get_or_create_user)
):
    """
    Download the original document file content (Protected - requires JWT)
    """
    logger.info("Download document", user_id=current_user["id"], document_id=document_id)
    try:
        # Forward request to document ingestor service
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.DOC_INGESTOR_URL}/api/v1/documents/{document_id}/download",
                timeout=30.0
            )

            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="Document not found")
            elif response.status_code != 200:
                logger.error(
                    "Document download failed",
                    document_id=document_id,
                    status_code=response.status_code,
                    response=response.text
                )
                raise HTTPException(
                    status_code=500,
                    detail="Failed to download document"
                )

            # Return the file content with appropriate headers
            from fastapi.responses import Response
            return Response(
                content=response.content,
                media_type=response.headers.get('content-type', 'application/octet-stream'),
                headers={
                    'Content-Disposition': response.headers.get('content-disposition', f'attachment; filename="document_{document_id}"')
                }
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to download document",
            document_id=document_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to download document"
        )


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: Dict[str, Any] = Depends(get_or_create_user)
):
    """
    Delete a document and all associated data (Protected - requires JWT)
    """
    logger.info("Delete document", user_id=current_user["id"], document_id=document_id)
    try:
        # Forward request to document ingestor service
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{settings.DOC_INGESTOR_URL}/api/v1/documents/{document_id}",
                timeout=30.0
            )

            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="Document not found")
            elif response.status_code != 200:
                logger.error(
                    "Document ingestor delete failed",
                    document_id=document_id,
                    status_code=response.status_code,
                    response=response.text
                )
                raise HTTPException(
                    status_code=500,
                    detail="Failed to delete document"
                )

            return response.json()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to delete document",
            document_id=document_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to delete document"
        )