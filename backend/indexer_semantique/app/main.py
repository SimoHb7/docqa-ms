"""
Main FastAPI application for Semantic Indexer service
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import uuid
import threading

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.core.health import get_health_status
from app.core.database import db_manager
from app.core.sync import sync_index_with_database
from app.api.v1.api import api_router
from app.consumer import consumer

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Semantic Indexer service",
               version=settings.VERSION,
               host=settings.HOST,
               port=settings.PORT)
    
    # Initialize database connection
    try:
        await db_manager.connect()
        logger.info("Database connection established")
    except Exception as e:
        logger.error("Failed to connect to database", error=str(e))
    
    # Synchronize FAISS index with database on startup
    try:
        logger.info("Checking FAISS index synchronization with database...")
        sync_result = await sync_index_with_database(force=False)
        logger.info("FAISS index sync completed", 
                   status=sync_result['status'],
                   db_embeddings=sync_result['db_embeddings'],
                   faiss_vectors=sync_result['faiss_vectors'],
                   sync_performed=sync_result['sync_performed'])
    except Exception as e:
        logger.error("Failed to synchronize FAISS index", error=str(e))
        # Continue startup even if sync fails
    
    # Start RabbitMQ consumer in background thread
    try:
        consumer.connect()
        consumer_thread = threading.Thread(target=consumer.start_consuming, daemon=True)
        consumer_thread.start()
        logger.info("RabbitMQ consumer started in background thread")
    except Exception as e:
        logger.error("Failed to start RabbitMQ consumer", error=str(e))

    yield

    # Shutdown
    logger.info("Shutting down Semantic Indexer service")
    consumer.stop()
    await db_manager.disconnect()


# Create FastAPI application
app = FastAPI(
    title="DocQA-MS Semantic Indexer",
    description="Vector indexing and semantic search service for medical documents",
    version=settings.VERSION,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add request ID to all requests for tracing"""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    start_time = time.time()
    logger.info("Request started",
               method=request.method,
               url=str(request.url),
               request_id=request_id)

    response = await call_next(request)

    process_time = time.time() - start_time
    logger.info("Request completed",
               method=request.method,
               url=str(request.url),
               status_code=response.status_code,
               process_time=f"{process_time:.3f}s",
               request_id=request_id)

    response.headers["X-Request-ID"] = request_id
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    request_id = getattr(request.state, 'request_id', 'unknown')
    logger.error("Unhandled exception",
                error=str(exc),
                request_id=request_id,
                url=str(request.url))

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "request_id": request_id,
            "message": "An unexpected error occurred"
        }
    )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return get_health_status()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": settings.SERVICE_NAME,
        "version": settings.VERSION,
        "status": "running",
        "docs": "/docs"
    }


# Include API routers
app.include_router(
    api_router,
    prefix="/api/v1"
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )