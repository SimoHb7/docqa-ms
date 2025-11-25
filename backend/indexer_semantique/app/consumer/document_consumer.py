"""
RabbitMQ consumer for processing document indexing tasks
"""
import json
import pika
import asyncio
from typing import Dict, Any
import httpx
import asyncpg

from app.core.config import settings
from app.core.logging import get_logger
from app.core.embeddings import embedding_service
from app.core.vector_store import vector_store

logger = get_logger(__name__)


class DocumentConsumer:
    """Consumer for document processing messages from RabbitMQ"""
    
    def __init__(self):
        self.connection = None
        self.channel = None
        self.should_stop = False
        
    def connect(self):
        """Establish connection to RabbitMQ"""
        try:
            logger.info("Connecting to RabbitMQ", url=settings.RABBITMQ_URL)
            self.connection = pika.BlockingConnection(
                pika.URLParameters(settings.RABBITMQ_URL)
            )
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue='document_processing', durable=True)
            self.channel.basic_qos(prefetch_count=1)
            logger.info("Connected to RabbitMQ successfully")
        except Exception as e:
            logger.error("Failed to connect to RabbitMQ", error=str(e))
            raise
    
    async def process_document(self, document_data: Dict[str, Any]):
        """Process a document for semantic indexing"""
        document_id = document_data.get('document_id')
        conn = None
        
        try:
            logger.info("Processing document for indexing", document_id=document_id)
            
            # Create a new database connection for this operation
            conn = await asyncpg.connect(settings.DATABASE_URL)
            
            # Get document content from database
            doc = await conn.fetchrow("""
                SELECT id, filename, content
                FROM documents
                WHERE id = $1
            """, document_id)
            
            if not doc:
                logger.warning("Document not found in database", document_id=document_id)
                return
            
            text_content = doc['content']
            
            if not text_content or len(text_content.strip()) < 10:
                logger.warning("Document has insufficient text content", document_id=document_id)
                # Update status anyway
                await conn.execute("""
                    UPDATE documents 
                    SET processing_status = 'indexed', indexed_at = NOW()
                    WHERE id = $1
                """, document_id)
                return
            
            # Generate embeddings
            logger.info("Generating embeddings", document_id=document_id, content_length=len(text_content))
            try:
                embedding_array = embedding_service.generate_single_embedding(text_content)
                logger.info("Embeddings generated successfully", document_id=document_id, dimension=len(embedding_array))
            except Exception as e:
                logger.error("Failed to generate embeddings", document_id=document_id, error=str(e), error_type=type(e).__name__)
                raise
            
            # Store embeddings in database (convert to JSON)
            import json
            try:
                embeddings_json = embedding_array.tolist()
                await conn.execute("""
                    INSERT INTO document_embeddings (document_id, embedding, chunk_text, chunk_index)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (document_id, chunk_index) DO UPDATE 
                    SET embedding = EXCLUDED.embedding, chunk_text = EXCLUDED.chunk_text
                """, document_id, json.dumps(embeddings_json), text_content[:1000], 0)
                logger.info("Embeddings stored in database", document_id=document_id)
            except Exception as e:
                logger.error("Failed to store embeddings", document_id=document_id, error=str(e), error_type=type(e).__name__)
                raise
            
            # Also store in FAISS vector store for fast search (use numpy array)
            try:
                import numpy as np
                chunk_id = f"{document_id}_chunk_0"
                metadata = {
                    'document_id': str(document_id),
                    'content': text_content[:1000],
                    'filename': doc['filename']
                }
                # FAISS expects shape (n_vectors, dimension), so reshape if needed
                vectors_2d = embedding_array.reshape(1, -1)
                vector_store.add_vectors(vectors_2d, [chunk_id], [metadata])
                logger.info("Embeddings added to FAISS index", document_id=document_id, chunk_id=chunk_id)
            except Exception as e:
                logger.error("Failed to add embeddings to FAISS", document_id=document_id, error=str(e), error_type=type(e).__name__)
                # Don't raise - database storage is primary, FAISS is for performance
            
            # Update document status
            await conn.execute("""
                UPDATE documents 
                SET processing_status = 'indexed', indexed_at = NOW()
                WHERE id = $1
            """, document_id)
            
            logger.info("Document indexed successfully", document_id=document_id)
                
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            logger.error("Failed to process document", 
                        document_id=document_id, 
                        error=str(e), 
                        error_type=type(e).__name__,
                        traceback=error_details)
            # Update status to failed
            if conn:
                try:
                    await conn.execute("""
                        UPDATE documents 
                        SET processing_status = 'failed'
                        WHERE id = $1
                    """, document_id)
                except:
                    pass
        finally:
            # Always close the connection
            if conn:
                await conn.close()
    
    def callback(self, ch, method, properties, body):
        """Callback for processing messages from queue"""
        try:
            message = json.loads(body)
            document_id = message.get('document_id')
            
            logger.info("Received message from queue", document_id=document_id)
            
            # Process document in async context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.process_document(message))
            loop.close()
            
            # Acknowledge message
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info("Message processed and acknowledged", document_id=document_id)
            
        except Exception as e:
            logger.error("Error processing message", error=str(e))
            # Reject and requeue message
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    def start_consuming(self):
        """Start consuming messages from queue"""
        try:
            logger.info("Starting to consume messages from document_processing queue")
            self.channel.basic_consume(
                queue='document_processing',
                on_message_callback=self.callback
            )
            
            logger.info("Consumer started, waiting for messages...")
            self.channel.start_consuming()
            
        except KeyboardInterrupt:
            logger.info("Consumer stopped by user")
            self.stop()
        except Exception as e:
            logger.error("Error in consumer", error=str(e))
            raise
    
    def stop(self):
        """Stop consuming and close connection"""
        try:
            if self.channel and self.channel.is_open:
                self.channel.stop_consuming()
            if self.connection and self.connection.is_open:
                self.connection.close()
            logger.info("Consumer stopped")
        except Exception as e:
            logger.error("Error stopping consumer", error=str(e))


# Global consumer instance
consumer = DocumentConsumer()
