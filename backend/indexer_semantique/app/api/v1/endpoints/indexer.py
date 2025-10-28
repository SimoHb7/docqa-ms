"""
Document indexing endpoints
"""
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
import uuid
from datetime import datetime

from app.core.embeddings import embedding_service
from app.core.chunker import text_chunker
from app.core.vector_store import vector_store
from app.core.database import db_manager
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


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


class IndexStatus(BaseModel):
    """Indexing status response"""
    document_id: str
    status: str  # 'not_found', 'processing', 'completed', 'failed'
    chunks_total: int = 0
    chunks_processed: int = 0
    vectors_added: int = 0
    error_message: str = ""
    created_at: datetime
    updated_at: datetime


@router.post("/", response_model=IndexResponse)
async def index_document(request: IndexRequest, background_tasks: BackgroundTasks):
    """
    Index document chunks in the vector store

    This endpoint processes document chunks, generates embeddings,
    and stores them in the vector database for semantic search.
    """
    start_time = datetime.utcnow()

    try:
        logger.info("Starting document indexing", document_id=request.document_id, chunks=len(request.chunks))

        if not request.chunks:
            raise HTTPException(status_code=400, detail="No chunks provided")

        # Extract texts and metadata
        texts = [chunk.content for chunk in request.chunks]
        chunk_ids = [f"{request.document_id}_chunk_{chunk.index}" for chunk in request.chunks]
        metadata_list = []

        for chunk in request.chunks:
            metadata = chunk.metadata.copy()
            metadata.update({
                "document_id": request.document_id,
                "chunk_index": chunk.index,
                "content": chunk.content,  # Store content in metadata for retrieval
                "content_length": len(chunk.content),
                "sentence_count": len(chunk.sentences)
            })
            metadata_list.append(metadata)

        # Generate embeddings
        logger.debug("Generating embeddings", text_count=len(texts))
        embeddings = embedding_service.generate_embeddings(texts)

        # Add to vector store
        logger.debug("Adding vectors to store", vector_count=len(embeddings))
        faiss_ids = vector_store.add_vectors(embeddings, chunk_ids, metadata_list)

        # Save chunks to database
        logger.debug("Saving chunks to database", chunk_count=len(request.chunks))
        for chunk in request.chunks:
            try:
                await db_manager.save_document_chunk(
                    document_id=request.document_id,
                    chunk_index=chunk.index,
                    content=chunk.content,
                    metadata=chunk.metadata
                )
            except Exception as e:
                logger.error("Failed to save chunk to database",
                           document_id=request.document_id,
                           chunk_index=chunk.index,
                           error=str(e))
                # Continue processing other chunks

        # Save index to disk (background task for performance)
        background_tasks.add_task(vector_store.save_index)

        processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)

        response = IndexResponse(
            document_id=request.document_id,
            chunks_processed=len(request.chunks),
            vectors_added=len(faiss_ids),
            processing_time_ms=processing_time,
            status="completed"
        )

        logger.info("Document indexing completed",
                   document_id=request.document_id,
                   chunks=len(request.chunks),
                   vectors=len(faiss_ids),
                   processing_time_ms=processing_time)

        return response

    except Exception as e:
        processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        logger.error("Document indexing failed",
                    document_id=request.document_id,
                    error=str(e),
                    processing_time_ms=processing_time)
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")


@router.get("/status/{document_id}", response_model=IndexStatus)
async def get_indexing_status(document_id: str):
    """
    Get indexing status for a document

    Returns the current indexing status and progress information.
    """
    try:
        # For now, we check if any chunks exist for this document
        # In a full implementation, this would check a database table
        total_chunks = 0
        processed_chunks = 0

        # Count chunks in vector store metadata
        for chunk_id, metadata in vector_store.metadata.items():
            if chunk_id.startswith(f"{document_id}_chunk_"):
                total_chunks += 1
                processed_chunks += 1  # All chunks in store are processed

        if total_chunks == 0:
            return IndexStatus(
                document_id=document_id,
                status="not_found",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

        return IndexStatus(
            document_id=document_id,
            status="completed",
            chunks_total=total_chunks,
            chunks_processed=processed_chunks,
            vectors_added=processed_chunks,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

    except Exception as e:
        logger.error("Failed to get indexing status", document_id=document_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")


@router.delete("/{document_id}")
async def delete_document_index(document_id: str, background_tasks: BackgroundTasks):
    """
    Delete all indexed chunks for a document

    This removes all vectors and metadata associated with the document.
    """
    try:
        logger.info("Starting document index deletion", document_id=document_id)

        # Find all chunk IDs for this document
        chunk_ids_to_delete = [
            chunk_id for chunk_id in vector_store.metadata.keys()
            if chunk_id.startswith(f"{document_id}_chunk_")
        ]

        if not chunk_ids_to_delete:
            raise HTTPException(status_code=404, detail="Document not found in index")

        # Delete vectors
        deleted_count = vector_store.delete_vectors(chunk_ids_to_delete)

        # Save updated index
        background_tasks.add_task(vector_store.save_index)

        logger.info("Document index deleted",
                   document_id=document_id,
                   chunks_deleted=len(chunk_ids_to_delete),
                   vectors_deleted=deleted_count)

        return {
            "document_id": document_id,
            "chunks_deleted": len(chunk_ids_to_delete),
            "vectors_deleted": deleted_count,
            "status": "deleted"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Document index deletion failed", document_id=document_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")