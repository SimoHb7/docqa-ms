"""
Semantic Indexer API endpoints for DocQA-MS API Gateway
Proxies requests to the IndexeurSémantique microservice
"""
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, Field
import httpx

from app.core.config import settings
from app.core.logging import get_logger
from app.core.dependencies import get_or_create_user

router = APIRouter()
logger = get_logger(__name__)


# Pydantic models matching IndexerSemantique service
class DocumentChunk(BaseModel):
    """Document chunk model"""
    index: int
    content: str = Field(..., min_length=1)
    sentences: List[str] = []
    metadata: Dict[str, Any] = {}


class IndexRequest(BaseModel):
    """Document indexing request"""
    document_id: str = Field(..., description="Unique document identifier")
    chunks: List[DocumentChunk] = Field(..., description="Document chunks to index")


class IndexResponse(BaseModel):
    """Indexing response"""
    document_id: str
    chunks_processed: int
    vectors_added: int
    processing_time_ms: int
    status: str = "completed"


@router.post("/", response_model=IndexResponse)
async def index_document(
    request: IndexRequest,
    current_user: Dict[str, Any] = Depends(get_or_create_user)
):
    """
    Index document chunks in the vector store (Protected - requires JWT)
    
    This endpoint processes document chunks, generates semantic embeddings,
    and stores them in the FAISS vector database for semantic search.
    
    **Process**:
    1. Receives document chunks with content and metadata
    2. Generates 384-dimensional embeddings using sentence-transformers
    3. Stores vectors in FAISS index with metadata
    4. Returns indexing statistics
    
    **Parameters**:
    - **document_id**: Unique identifier for the document
    - **chunks**: List of document chunks with content and metadata
    
    **Returns**:
    - **document_id**: The document identifier
    - **chunks_processed**: Number of chunks processed
    - **vectors_added**: Number of vectors added to index
    - **processing_time_ms**: Processing time in milliseconds
    """
    try:
        logger.info(
            "Forwarding document indexing request",
            document_id=request.document_id,
            chunks=len(request.chunks)
        )

        # Forward request to IndexerSemantique microservice
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    f"{settings.INDEXER_SEMANTIQUE_URL}/api/v1/index/",
                    json=request.dict()
                )

                if response.status_code != 200:
                    logger.error(
                        "Indexer service failed",
                        document_id=request.document_id,
                        status_code=response.status_code,
                        response=response.text
                    )
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Indexing service error: {response.text}"
                    )

                result = response.json()

            except httpx.RequestError as e:
                logger.error(
                    "Failed to connect to indexer service",
                    document_id=request.document_id,
                    error=str(e)
                )
                raise HTTPException(
                    status_code=503,
                    detail="Indexing service unavailable"
                )

        logger.info(
            "Document indexing completed",
            document_id=request.document_id,
            chunks_processed=result.get("chunks_processed", 0),
            processing_time_ms=result.get("processing_time_ms", 0)
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Unexpected error during indexing",
            document_id=request.document_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail="Indexing failed due to internal error"
        )


@router.get("/status/{document_id}")
async def get_indexing_status(
    document_id: str,
    current_user: Dict[str, Any] = Depends(get_or_create_user)
):
    """
    Get indexing status for a document (Protected - requires JWT)
    """
    logger.info("Indexer status check", user_id=current_user["id"], document_id=document_id)
    """
    
    Returns the current indexing status and progress information.
    
    **Parameters**:
    - **document_id**: The unique identifier of the document
    
    **Returns**:
    - Indexing status including progress and statistics
    """
    try:
        logger.info("Retrieving indexing status", document_id=document_id)

        # Forward request to IndexerSemantique microservice
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(
                    f"{settings.INDEXER_SEMANTIQUE_URL}/api/v1/index/status/{document_id}"
                )

                if response.status_code == 404:
                    raise HTTPException(
                        status_code=404,
                        detail=f"No indexing record found for document {document_id}"
                    )

                if response.status_code != 200:
                    logger.error(
                        "Indexer service failed",
                        document_id=document_id,
                        status_code=response.status_code
                    )
                    raise HTTPException(
                        status_code=response.status_code,
                        detail="Failed to retrieve indexing status"
                    )

                return response.json()

            except httpx.RequestError as e:
                logger.error(
                    "Failed to connect to indexer service",
                    document_id=document_id,
                    error=str(e)
                )
                raise HTTPException(
                    status_code=503,
                    detail="Indexing service unavailable"
                )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Unexpected error retrieving indexing status",
            document_id=document_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve indexing status"
        )


@router.delete("/{document_id}")
async def delete_document_index(
    document_id: str,
    current_user: Dict[str, Any] = Depends(get_or_create_user)
):
    """
    Delete all indexed chunks for a document (Protected - requires JWT)
    """
    logger.info("Delete document index", user_id=current_user["id"], document_id=document_id)
    """
    
    This removes all vectors and metadata associated with the document
    from the vector store.
    
    **Parameters**:
    - **document_id**: The unique identifier of the document to delete
    
    **Returns**:
    - Deletion confirmation with statistics
    """
    try:
        logger.info("Deleting document index", document_id=document_id)

        # Forward request to IndexerSemantique microservice
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.delete(
                    f"{settings.INDEXER_SEMANTIQUE_URL}/api/v1/index/{document_id}"
                )

                if response.status_code == 404:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Document {document_id} not found in index"
                    )

                if response.status_code != 200:
                    logger.error(
                        "Indexer service failed",
                        document_id=document_id,
                        status_code=response.status_code
                    )
                    raise HTTPException(
                        status_code=response.status_code,
                        detail="Failed to delete document index"
                    )

                result = response.json()

            except httpx.RequestError as e:
                logger.error(
                    "Failed to connect to indexer service",
                    document_id=document_id,
                    error=str(e)
                )
                raise HTTPException(
                    status_code=503,
                    detail="Indexing service unavailable"
                )

        logger.info(
            "Document index deleted",
            document_id=document_id,
            chunks_deleted=result.get("chunks_deleted", 0)
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Unexpected error deleting document index",
            document_id=document_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to delete document index"
        )


@router.get("/stats")
async def get_indexer_statistics(
    current_user: Dict[str, Any] = Depends(get_or_create_user)
):
    """
    Get vector store and indexing statistics (Protected - requires JWT)
    """
    logger.info("Indexer stats accessed", user_id=current_user["id"])
    """
    
    Returns information about the vector store size, embedding model,
    and search configuration.
    
    **Returns**:
    - **vector_store**: Total vectors, chunks, dimension, index type
    - **embedding_model**: Model name, dimension, device, status
    - **search_config**: Max results, similarity threshold, timeout
    """
    try:
        logger.debug("Retrieving indexer statistics")

        # Forward request to IndexerSemantique microservice
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(
                    f"{settings.INDEXER_SEMANTIQUE_URL}/api/v1/search/stats"
                )

                if response.status_code != 200:
                    logger.error(
                        "Indexer service failed",
                        status_code=response.status_code
                    )
                    raise HTTPException(
                        status_code=response.status_code,
                        detail="Failed to retrieve indexer statistics"
                    )

                return response.json()

            except httpx.RequestError as e:
                logger.error(
                    "Failed to connect to indexer service",
                    error=str(e)
                )
                raise HTTPException(
                    status_code=503,
                    detail="Indexing service unavailable"
                )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Unexpected error retrieving indexer statistics", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve indexer statistics"
        )
