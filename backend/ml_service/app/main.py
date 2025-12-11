"""
ML Service Main Application
FastAPI application for ML model inference
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.api.endpoints import router as api_router
from app.services.model_manager import ModelManager

# Setup logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global model manager
model_manager = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: load models on startup"""
    global model_manager
    
    logger.info("Starting ML Service...")
    
    # Initialize model manager
    model_manager = ModelManager(
        classifier_path=settings.CLASSIFIER_MODEL_PATH if not settings.CLASSIFIER_USE_PRETRAINED else None,
        classifier_pretrained=settings.CLASSIFIER_PRETRAINED_MODEL,
        classifier_use_pretrained=settings.CLASSIFIER_USE_PRETRAINED,
        ner_path=settings.NER_MODEL_PATH if not settings.NER_USE_PRETRAINED else None,
        ner_pretrained=settings.NER_PRETRAINED_MODEL,
        ner_use_pretrained=settings.NER_USE_PRETRAINED,
        device=settings.DEVICE
    )
    
    # Store in app state
    app.state.model_manager = model_manager
    
    logger.info("ML Service started successfully")
    
    yield
    
    # Cleanup
    logger.info("Shutting down ML Service...")


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on environment
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "models_loaded": model_manager is not None
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "DocQA-MS ML Service",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health"
    }


# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
