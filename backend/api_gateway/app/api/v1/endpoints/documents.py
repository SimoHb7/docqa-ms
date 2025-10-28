"""
Documents API endpoints for DocQA-MS API Gateway
"""
import os
import uuid
from typing import List, Optional
import aiofiles
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
import httpx

from app.core.config import settings
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    patient_id: Optional[str] = Form(None),
    document_type: Optional[str] = Form(None)
):
    """
    Upload a document for processing
    """
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
                    'document_id': document_id  # Pass the document ID
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
    offset: int = 0
):
    """
    List documents with filtering and pagination
    """
    try:
        # Build query parameters
        params = {
            "limit": limit,
            "offset": offset
        }
        if status:
            params["status"] = status
        if document_type:
            params["document_type"] = document_type
        if patient_id:
            params["patient_id"] = patient_id

        # Forward request to document ingestor service
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.DOC_INGESTOR_URL}/api/v1/documents/",
                params=params,
                timeout=30.0
            )

            if response.status_code != 200:
                logger.error(
                    "Document ingestor list failed",
                    status_code=response.status_code,
                    response=response.text
                )
                raise HTTPException(
                    status_code=500,
                    detail="Failed to retrieve documents"
                )

            return response.json()

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to list documents", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve documents"
        )


@router.get("/{document_id}")
async def get_document(document_id: str):
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


@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """
    Delete a document and all associated data
    """
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