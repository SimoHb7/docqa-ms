"""
DeID endpoints for document anonymization
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import json

from app.main import anonymize_document, get_anonymization_status
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.post("/anonymize")
async def anonymize_endpoint(request: Dict[str, Any]):
    """
    Anonymize document content
    """
    try:
        # Validate required fields
        if "document_id" not in request:
            raise HTTPException(status_code=400, detail="document_id is required")
        if "content" not in request:
            raise HTTPException(status_code=400, detail="content is required")

        # Create anonymization request
        from pydantic import BaseModel
        class AnonRequest(BaseModel):
            document_id: str
            content: str
            language: str = "fr"

        anon_request = AnonRequest(**request)

        # Call anonymization function
        result = await anonymize_document(anon_request)

        return {
            "success": True,
            "document_id": result.document_id,
            "anonymized_content": result.anonymized_content,
            "pii_entities_found": len(result.pii_entities),
            "processing_time_ms": result.processing_time_ms
        }

    except Exception as e:
        logger.error(f"Error in anonymize endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Anonymization failed: {str(e)}")

@router.get("/status/{document_id}")
async def status_endpoint(document_id: str):
    """
    Get anonymization status for a document
    """
    try:
        result = await get_anonymization_status(document_id)
        return result

    except Exception as e:
        logger.error(f"Error getting status for {document_id}: {e}")
        raise HTTPException(status_code=500, detail="Status check failed")

@router.post("/batch-anonymize")
async def batch_anonymize_endpoint(request: Dict[str, Any]):
    """
    Anonymize multiple documents in batch
    """
    try:
        if "documents" not in request:
            raise HTTPException(status_code=400, detail="documents array is required")

        documents = request["documents"]
        results = []

        for doc in documents:
            try:
                # Create anonymization request for each document
                from pydantic import BaseModel
                class AnonRequest(BaseModel):
                    document_id: str
                    content: str
                    language: str = "fr"

                anon_request = AnonRequest(**doc)
                result = await anonymize_document(anon_request)

                results.append({
                    "document_id": result.document_id,
                    "success": True,
                    "pii_entities_found": len(result.pii_entities),
                    "processing_time_ms": result.processing_time_ms
                })

            except Exception as e:
                logger.error(f"Error anonymizing document {doc.get('document_id', 'unknown')}: {e}")
                results.append({
                    "document_id": doc.get("document_id", "unknown"),
                    "success": False,
                    "error": str(e)
                })

        return {
            "total_documents": len(documents),
            "successful": len([r for r in results if r["success"]]),
            "failed": len([r for r in results if not r["success"]]),
            "results": results
        }

    except Exception as e:
        logger.error(f"Error in batch anonymize endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Batch anonymization failed: {str(e)}")