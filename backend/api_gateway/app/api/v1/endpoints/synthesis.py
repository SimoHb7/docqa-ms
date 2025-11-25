"""
Synthesis API endpoints for DocQA-MS API Gateway
"""
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Depends
import httpx
import uuid

from app.core.config import settings
from app.core.logging import get_logger
from app.core.dependencies import get_or_create_user

router = APIRouter()
logger = get_logger(__name__)


@router.post("/")
async def create_synthesis(
    synthesis_type: str = Query(..., description="Type of synthesis", regex="^(patient_timeline|comparison|summary)$"),
    patient_id: Optional[str] = Query(None, description="Patient ID for patient-specific synthesis"),
    document_ids: Optional[str] = Query(None, description="Comma-separated list of document IDs"),
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    custom_parameters: Optional[str] = Query(None, description="Additional JSON parameters"),
    current_user: Dict[str, Any] = Depends(get_or_create_user)
):
    """
    Generate structured synthesis or comparison from documents (Protected - requires JWT)
    """
    try:
        from uuid import UUID
        from app.core.database import get_db_pool
        
        # Validate required parameters based on synthesis type
        if synthesis_type in ["patient_timeline", "summary"] and not patient_id:
            raise HTTPException(
                status_code=400,
                detail=f"patient_id is required for synthesis type '{synthesis_type}'"
            )

        if synthesis_type == "comparison" and not document_ids:
            raise HTTPException(
                status_code=400,
                detail="document_ids is required for synthesis type 'comparison'"
            )

        # Generate synthesis ID
        synthesis_id = str(uuid.uuid4())

        # Parse document IDs
        doc_ids = []
        
        # If patient_id is provided, fetch documents from database for that patient (user-filtered)
        if patient_id:
            user_uuid = UUID(current_user["id"])
            pool = await get_db_pool()
            async with pool.acquire() as conn:
                query = """
                    SELECT id::text as doc_id, filename, created_at
                    FROM documents
                    WHERE user_id = $1 
                      AND metadata->>'patient_id' = $2
                    ORDER BY created_at ASC
                """
                
                # Add date filtering if provided
                if date_from and date_to:
                    query = """
                        SELECT id::text as doc_id, filename, created_at
                        FROM documents
                        WHERE user_id = $1 
                          AND metadata->>'patient_id' = $2
                          AND created_at >= $3::date
                          AND created_at <= $4::date
                        ORDER BY created_at ASC
                    """
                    rows = await conn.fetch(query, user_uuid, patient_id, date_from, date_to)
                elif date_from:
                    query = """
                        SELECT id::text as doc_id, filename, created_at
                        FROM documents
                        WHERE user_id = $1 
                          AND metadata->>'patient_id' = $2
                          AND created_at >= $3::date
                        ORDER BY created_at ASC
                    """
                    rows = await conn.fetch(query, user_uuid, patient_id, date_from)
                elif date_to:
                    query = """
                        SELECT id::text as doc_id, filename, created_at
                        FROM documents
                        WHERE user_id = $1 
                          AND metadata->>'patient_id' = $2
                          AND created_at <= $3::date
                        ORDER BY created_at ASC
                    """
                    rows = await conn.fetch(query, user_uuid, patient_id, date_to)
                else:
                    rows = await conn.fetch(query, user_uuid, patient_id)
                
                if not rows:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Aucun document trouvé pour le patient \"{patient_id}\". Assurez-vous que les documents ont le bon patient_id dans les métadonnées."
                    )
                
                doc_ids = [row['doc_id'] for row in rows]
                logger.info(f"Found {len(doc_ids)} documents for patient {patient_id}")
        
        elif document_ids:
            doc_ids = [doc_id.strip() for doc_id in document_ids.split(",") if doc_id.strip()]

        # Parse custom parameters
        custom_params = {}
        if custom_parameters:
            try:
                import json
                custom_params = json.loads(custom_parameters)
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid JSON in custom_parameters"
                )

        # Build synthesis parameters
        parameters = {
            "synthesis_type": synthesis_type,
            "patient_id": patient_id,
            "document_ids": doc_ids,
            "date_range": {
                "start": date_from,
                "end": date_to
            } if date_from or date_to else None,
            **custom_params
        }

        # Remove None values
        parameters = {k: v for k, v in parameters.items() if v is not None}

        synthesis_request = {
            "synthesis_id": synthesis_id,
            "type": synthesis_type,
            "parameters": parameters
        }

        logger.info(
            "Creating synthesis request",
            synthesis_id=synthesis_id,
            synthesis_type=synthesis_type,
            patient_id=patient_id,
            document_count=len(doc_ids)
        )

        # Call synthesis service
        async with httpx.AsyncClient(timeout=120.0) as client:  # Longer timeout for synthesis
            try:
                response = await client.post(
                    f"{settings.SYNTHESE_COMPARATIVE_URL}/generate",
                    json=synthesis_request
                )

                if response.status_code != 200:
                    logger.error(
                        "Synthesis service failed",
                        synthesis_id=synthesis_id,
                        status_code=response.status_code,
                        response=response.text
                    )
                    raise HTTPException(
                        status_code=500,
                        detail="Synthesis service temporarily unavailable"
                    )

                synthesis_response = response.json()

            except httpx.RequestError as e:
                logger.error(
                    "Failed to connect to synthesis service",
                    synthesis_id=synthesis_id,
                    error=str(e)
                )
                raise HTTPException(
                    status_code=503,
                    detail="Synthesis service unavailable"
                )

        # Log synthesis in audit
        audit_data = {
            "user_id": "anonymous",  # Would come from auth context
            "action": "synthesis_request",
            "resource_type": "synthesis",
            "resource_id": synthesis_id,
            "action_details": {
                "synthesis_type": synthesis_type,
                "parameters": parameters
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
            logger.warning("Failed to log synthesis audit", error=str(e))

        # Format response
        result = {
            "synthesis_id": synthesis_id,
            "type": synthesis_type,
            "status": synthesis_response.get("status", "processing"),
            "parameters": parameters,
            "result": synthesis_response.get("result"),
            "generated_at": synthesis_response.get("generated_at"),
            "execution_time_ms": synthesis_response.get("execution_time_ms", 0)
        }

        logger.info(
            "Synthesis request completed",
            synthesis_id=synthesis_id,
            status=result["status"]
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Unexpected error during synthesis",
            synthesis_type=synthesis_type,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail="Synthesis failed due to internal error"
        )


@router.get("/{synthesis_id}")
async def get_synthesis(
    synthesis_id: str,
    current_user: Dict[str, Any] = Depends(get_or_create_user)
):
    """
    Get synthesis result by ID (Protected - requires JWT)
    """
    logger.info("Get synthesis", user_id=current_user["id"], synthesis_id=synthesis_id)
    try:
        # This would query the database for synthesis status/result
        # For now, return mock data
        synthesis = {
            "synthesis_id": synthesis_id,
            "type": "patient_timeline",
            "status": "completed",
            "parameters": {
                "patient_id": "ANON_PAT_001",
                "date_range": {
                    "start": "2024-01-01",
                    "end": "2024-12-31"
                }
            },
            "result": {
                "title": "Chronologie du patient ANON_PAT_001",
                "content": "# Chronologie du patient\n\n## Janvier 2024\n- Consultation cardiologique - Hypertension bien contrôlée\n- Analyses biologiques - Glycémie normale\n\n## Évolution\nStabilité clinique avec bonne observance thérapeutique.",
                "sections": [
                    {
                        "title": "Janvier 2024",
                        "content": "Consultation cardiologique - Hypertension bien contrôlée sous irbesartan 150mg/j"
                    }
                ]
            },
            "generated_at": "2024-01-15T14:30:00Z",
            "execution_time_ms": 2340
        }

        return synthesis

    except Exception as e:
        logger.error(
            "Failed to get synthesis",
            synthesis_id=synthesis_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve synthesis"
        )


@router.get("/")
async def list_syntheses(
    synthesis_type: Optional[str] = Query(None, description="Filter by synthesis type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(20, description="Maximum number of results", ge=1, le=100),
    offset: int = Query(0, description="Pagination offset", ge=0),
    current_user: Dict[str, Any] = Depends(get_or_create_user)
):
    """
    List syntheses with filtering and pagination (Protected - requires JWT)
    """
    logger.info("List syntheses", user_id=current_user["id"])
    try:
        # This would query the database for syntheses
        # For now, return mock data
        syntheses = [
            {
                "synthesis_id": "synth-1",
                "type": "patient_timeline",
                "status": "completed",
                "created_at": "2024-01-15T14:30:00Z",
                "parameters": {"patient_id": "ANON_PAT_001"}
            },
            {
                "synthesis_id": "synth-2",
                "type": "comparison",
                "status": "processing",
                "created_at": "2024-01-20T10:15:00Z",
                "parameters": {"document_ids": ["doc-1", "doc-2"]}
            }
        ]

        # Apply filters
        filtered_syntheses = syntheses
        if synthesis_type:
            filtered_syntheses = [s for s in filtered_syntheses if s["type"] == synthesis_type]
        if status:
            filtered_syntheses = [s for s in filtered_syntheses if s["status"] == status]

        return {
            "syntheses": filtered_syntheses[offset:offset+limit],
            "total": len(filtered_syntheses),
            "limit": limit,
            "offset": offset
        }

    except Exception as e:
        logger.error("Failed to list syntheses", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve syntheses"
        )


@router.delete("/{synthesis_id}")
async def delete_synthesis(
    synthesis_id: str,
    current_user: Dict[str, Any] = Depends(get_or_create_user)
):
    """
    Delete a synthesis (Protected - requires JWT)
    """
    logger.info("Delete synthesis", user_id=current_user["id"], synthesis_id=synthesis_id)
    try:
        # This would delete synthesis data from database
        logger.info("Synthesis deleted", synthesis_id=synthesis_id)

        return {
            "message": "Synthesis deleted successfully",
            "synthesis_id": synthesis_id
        }

    except Exception as e:
        logger.error(
            "Failed to delete synthesis",
            synthesis_id=synthesis_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to delete synthesis"
        )