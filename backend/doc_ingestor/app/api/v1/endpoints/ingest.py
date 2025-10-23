"""
Document ingestion endpoints for DocQA-MS Document Ingestor
"""
import os
import uuid
from typing import Dict, Any
import aiofiles
from fastapi import APIRouter, HTTPException
import pika
import json

from app.core.config import settings
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


def publish_to_queue(document_id: str, file_path: str, metadata: Dict[str, Any]) -> None:
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


@router.post("/")
async def ingest_document(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ingest and process a document
    """
    try:
        document_id = data.get("document_id")
        file_path = data.get("file_path")
        metadata = data.get("metadata", {})

        if not document_id or not file_path:
            raise HTTPException(
                status_code=400,
                detail="document_id and file_path are required"
            )

        # Validate file exists
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=404,
                detail=f"File not found: {file_path}"
            )

        # Get file size
        file_size = os.path.getsize(file_path)
        file_size_mb = file_size / (1024 * 1024)

        if file_size_mb > settings.MAX_UPLOAD_SIZE_MB:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE_MB}MB"
            )

        # Extract basic text content (placeholder - would implement full text extraction)
        text_content = f"Document {document_id} - placeholder text extraction"

        # Publish to processing queue
        publish_to_queue(document_id, file_path, metadata)

        logger.info(
            "Document ingested successfully",
            document_id=document_id,
            file_path=file_path,
            file_size=file_size
        )

        return {
            "document_id": document_id,
            "status": "ingested",
            "message": "Document ingested and queued for processing",
            "file_size": file_size,
            "text_preview": text_content[:200] + "..." if len(text_content) > 200 else text_content
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Unexpected error during document ingestion",
            error=str(e),
            document_id=data.get("document_id")
        )
        raise HTTPException(
            status_code=500,
            detail="Internal server error during document ingestion"
        )
