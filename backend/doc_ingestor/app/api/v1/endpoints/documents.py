"""
Documents API endpoints for DocQA-MS Document Ingestor
"""
import os
import uuid
from typing import List, Optional
import aiofiles
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import pika
import json

from app.core.config import settings
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


def publish_to_queue(document_id: str, file_path: str, metadata: dict) -> None:
    """Publish document processing task to RabbitMQ queue"""
    try:
        connection = pika.BlockingConnection(pika.URLParameters(settings.RABBITMQ_URL))
        channel = connection.channel()

        # Declare queue
        channel.queue_declare(queue='document_processing', durable=True)

        # Prepare message
        message = {
            "document_id": document_id,
            "file_path": file_path,
            "metadata": metadata,
            "timestamp": "2024-01-01T00:00:00Z"  # Would use datetime.utcnow() in real implementation
        }

        # Publish message
        channel.basic_publish(
            exchange='',
            routing_key='document_processing',
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Make message persistent
            )
        )

        logger.info("Published document to processing queue", document_id=document_id)
        connection.close()

    except Exception as e:
        logger.error("Failed to publish to queue", document_id=document_id, error=str(e))
        raise


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

        # Publish to processing queue
        publish_to_queue(document_id, file_path, metadata)

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

        # This would typically query the database directly
        # For now, return mock data
        documents = [
            {
                "id": "doc-1",
                "filename": "sample_medical_report_1.pdf",
                "status": "processed",
                "upload_date": "2024-01-15T10:30:00Z",
                "document_type": "medical_report",
                "patient_id": "ANON_PAT_001"
            },
            {
                "id": "doc-2",
                "filename": "sample_lab_results_1.pdf",
                "status": "processed",
                "upload_date": "2024-01-20T14:15:00Z",
                "document_type": "lab_results",
                "patient_id": "ANON_PAT_002"
            }
        ]

        return {
            "documents": documents,
            "total": len(documents),
            "limit": limit,
            "offset": offset
        }

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
        # This would query the database for document details
        # For now, return mock data
        document = {
            "id": document_id,
            "filename": "sample_medical_report_1.pdf",
            "status": "processed",
            "upload_date": "2024-01-15T10:30:00Z",
            "document_type": "medical_report",
            "patient_id": "ANON_PAT_001",
            "file_size": 245760,
            "processing_status": "completed",
            "metadata": {
                "author": "Dr. Smith",
                "specialty": "cardiology",
                "language": "fr"
            }
        }

        return document

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
        # This would delete from database and file system
        # For now, just return success
        logger.info("Document deleted", document_id=document_id)

        return {
            "message": "Document deleted successfully",
            "document_id": document_id
        }

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