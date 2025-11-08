"""
FAISS index synchronization with database
"""
import json
import numpy as np
import faiss
from datetime import datetime

from app.core.logging import get_logger
from app.core.vector_store import vector_store
from app.core.database import db_manager

logger = get_logger(__name__)


async def sync_index_with_database(force: bool = False):
    """
    Synchronize FAISS index with database embeddings
    
    This function checks if the FAISS index is in sync with the database.
    If not (or if force=True), it rebuilds the index from database embeddings.
    
    Args:
        force: Force rebuild even if counts match
    
    Returns:
        Dict with sync results
    """
    start_time = datetime.utcnow()
    
    try:
        logger.info("Starting FAISS index synchronization check")
        
        # Get count of embeddings in database
        async with db_manager.pool.acquire() as conn:
            db_count = await conn.fetchval("""
                SELECT COUNT(*)
                FROM document_embeddings de
                JOIN documents d ON de.document_id = d.id
                WHERE d.processing_status = 'indexed'
            """)
        
        # Get count in FAISS index
        faiss_count = vector_store.index.ntotal if vector_store.index else 0
        
        logger.info(f"Index sync check: DB has {db_count} embeddings, FAISS has {faiss_count} vectors")
        
        # Check if sync is needed
        needs_sync = force or (db_count != faiss_count) or (faiss_count == 0 and db_count > 0)
        
        if not needs_sync:
            logger.info("FAISS index is in sync with database, no rebuild needed")
            return {
                "status": "in_sync",
                "db_embeddings": db_count,
                "faiss_vectors": faiss_count,
                "sync_performed": False,
                "processing_time_ms": 0
            }
        
        # Perform sync/rebuild
        logger.warning(f"FAISS index out of sync! DB: {db_count}, FAISS: {faiss_count}. Starting rebuild...")
        
        # Get all document embeddings from database
        async with db_manager.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT 
                    de.id,
                    de.document_id,
                    de.chunk_index,
                    de.embedding,
                    de.chunk_text,
                    d.filename,
                    d.file_type,
                    d.metadata
                FROM document_embeddings de
                JOIN documents d ON de.document_id = d.id
                WHERE d.processing_status = 'indexed'
                ORDER BY de.document_id, de.chunk_index
            """)
        
        if not rows:
            logger.warning("No embeddings found in database to sync")
            return {
                "status": "no_embeddings",
                "db_embeddings": 0,
                "faiss_vectors": 0,
                "sync_performed": False,
                "processing_time_ms": int((datetime.utcnow() - start_time).total_seconds() * 1000)
            }
        
        logger.info(f"Found {len(rows)} embeddings in database, rebuilding FAISS index...")
        
        # Clear existing index and create new one
        vector_store.index = faiss.IndexFlatIP(vector_store.dimension)
        vector_store.metadata = {}
        vector_store.id_mapping = {}
        
        # Process embeddings
        vectors_list = []
        chunk_ids = []
        metadata_list = []
        documents_seen = set()
        
        for row in rows:
            document_id = str(row['document_id'])
            chunk_index = row['chunk_index']
            chunk_id = f"{document_id}_chunk_{chunk_index}"
            
            # Parse embedding (assuming it's stored as array)
            embedding = row['embedding']
            if isinstance(embedding, str):
                embedding = json.loads(embedding)
            embedding_array = np.array(embedding, dtype=np.float32)
            
            # Prepare metadata
            doc_metadata = row['metadata']
            if isinstance(doc_metadata, str):
                try:
                    doc_metadata = json.loads(doc_metadata)
                except:
                    doc_metadata = {}
            elif not isinstance(doc_metadata, dict):
                doc_metadata = {}
            
            metadata = {
                'document_id': document_id,
                'chunk_index': chunk_index,
                'content': row['chunk_text'],
                'filename': row['filename'],
                'file_type': row['file_type']
            }
            # Merge document metadata
            if doc_metadata:
                for key, value in doc_metadata.items():
                    if key not in metadata:
                        metadata[key] = value
            
            vectors_list.append(embedding_array)
            chunk_ids.append(chunk_id)
            metadata_list.append(metadata)
            documents_seen.add(document_id)
        
        # Convert to numpy array
        vectors = np.vstack(vectors_list)
        
        # Add all vectors to the new index
        logger.info(f"Adding {len(vectors)} vectors to new FAISS index")
        vector_store.add_vectors(vectors, chunk_ids, metadata_list)
        
        # Save the rebuilt index
        vector_store.save_index()
        
        processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        logger.info("FAISS index synchronized successfully",
                   vectors=len(vectors),
                   documents=len(documents_seen),
                   processing_time_ms=processing_time)
        
        return {
            "status": "synced",
            "db_embeddings": db_count,
            "faiss_vectors": len(vectors),
            "documents_processed": len(documents_seen),
            "sync_performed": True,
            "processing_time_ms": processing_time
        }
        
    except Exception as e:
        processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        logger.error("Failed to synchronize FAISS index with database",
                    error=str(e),
                    processing_time_ms=processing_time)
        raise
