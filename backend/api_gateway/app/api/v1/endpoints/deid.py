"""
De-identification (DeID) API endpoints for DocQA-MS API Gateway
Proxies requests to the DeID microservice
"""
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
import httpx
import uuid

from app.core.config import settings
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


# Pydantic models matching DeID service
class AnonymizationRequest(BaseModel):
    document_id: str
    content: str
    language: Optional[str] = "fr"


class AnonymizationResponse(BaseModel):
    document_id: str
    original_content: str
    anonymized_content: str
    pii_entities: list
    processing_time_ms: int


@router.post("/anonymize", response_model=AnonymizationResponse)
async def anonymize_document(request: AnonymizationRequest):
    """
    Anonymize a document by removing or replacing PII (Personally Identifiable Information)
    
    This endpoint forwards the request to the DeID microservice which uses Presidio
    and spaCy to detect and anonymize sensitive information in medical documents.
    
    **Detected Entity Types:**
    - PERSON: Names of individuals
    - LOCATION: Places, addresses
    - DATE_TIME: Dates and times
    - PHONE_NUMBER: Phone numbers
    - EMAIL_ADDRESS: Email addresses
    - CREDIT_CARD: Credit card numbers
    
    **Parameters:**
    - **document_id**: Unique identifier for the document
    - **content**: The text content to anonymize
    - **language**: Language code (default: "fr" for French)
    
    **Returns:**
    - **document_id**: The document identifier
    - **original_content**: Original text content
    - **anonymized_content**: Text with PII replaced by placeholders (e.g., <PERSON>)
    - **pii_entities**: List of detected PII entities with confidence scores
    - **processing_time_ms**: Processing time in milliseconds
    """
    try:
        logger.info(
            "Processing anonymization request",
            document_id=request.document_id,
            content_length=len(request.content),
            language=request.language
        )

        # Forward request to DeID microservice
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{settings.DEID_URL}/anonymize",
                    json={
                        "document_id": request.document_id,
                        "content": request.content,
                        "language": request.language
                    }
                )

                if response.status_code != 200:
                    logger.error(
                        "DeID service failed",
                        document_id=request.document_id,
                        status_code=response.status_code,
                        response=response.text
                    )
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Anonymization service error: {response.text}"
                    )

                result = response.json()

            except httpx.RequestError as e:
                logger.error(
                    "Failed to connect to DeID service",
                    document_id=request.document_id,
                    error=str(e)
                )
                raise HTTPException(
                    status_code=503,
                    detail="Anonymization service unavailable"
                )

        # Log anonymization completion
        logger.info(
            "Anonymization completed",
            document_id=request.document_id,
            pii_entities_count=len(result.get("pii_entities", [])),
            processing_time_ms=result.get("processing_time_ms", 0)
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Unexpected error during anonymization",
            document_id=request.document_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail="Anonymization failed due to internal error"
        )


@router.get("/anonymize/status/{document_id}")
async def get_anonymization_status(document_id: str):
    """
    Get the anonymization status and results for a specific document
    
    Retrieves the stored anonymization result from the database through the DeID service.
    
    **Parameters:**
    - **document_id**: The unique identifier of the document
    
    **Returns:**
    - Anonymization result including original and anonymized content, detected entities
    """
    try:
        logger.info("Retrieving anonymization status", document_id=document_id)

        # Forward request to DeID microservice
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(
                    f"{settings.DEID_URL}/anonymize/status/{document_id}"
                )

                if response.status_code == 404:
                    raise HTTPException(
                        status_code=404,
                        detail=f"No anonymization record found for document {document_id}"
                    )

                if response.status_code != 200:
                    logger.error(
                        "DeID service failed",
                        document_id=document_id,
                        status_code=response.status_code
                    )
                    raise HTTPException(
                        status_code=response.status_code,
                        detail="Failed to retrieve anonymization status"
                    )

                return response.json()

            except httpx.RequestError as e:
                logger.error(
                    "Failed to connect to DeID service",
                    document_id=document_id,
                    error=str(e)
                )
                raise HTTPException(
                    status_code=503,
                    detail="Anonymization service unavailable"
                )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Unexpected error retrieving anonymization status",
            document_id=document_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve anonymization status"
        )
