"""
Synthese Comparative Service
Main FastAPI application entry point
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import structlog
import time
from typing import Callable

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.v1.api import api_router
from app.core.health import router as health_router
from app.services.database import test_connection

# Setup structured logging
setup_logging()
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager"""
    logger.info("Starting Synthese Comparative Service")

    # Startup tasks
    # Test database connection
    try:
        db_ok = await test_connection()
        if db_ok:
            logger.info("Database connection verified successfully")
        else:
            logger.warning("Database connection test failed - service may have limited functionality")
    except Exception as e:
        logger.error("Database connection test error", error=str(e))
    
    logger.info("Synthese Comparative Service startup complete")

    yield

    # Shutdown tasks
    logger.info("Shutting down Synthese Comparative Service")


# Create FastAPI application
app = FastAPI(
    title="Synthese Comparative Service",
    description="Medical Document Synthesis and Comparison Service",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Set up middleware
# CORS - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=False,  # Must be False when allow_origins is ["*"]
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS,
    )


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests"""
    start_time = time.time()

    # Log request
    logger.info(
        "Request started",
        method=request.method,
        url=str(request.url),
        client_ip=request.client.host if request.client else None,
    )

    response = await call_next(request)
    process_time = time.time() - start_time

    # Log response
    logger.info(
        "Request completed",
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        process_time=f"{process_time:.3f}s",
    )

    return response


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    logger.warning(
        "HTTP exception",
        status_code=exc.status_code,
        detail=exc.detail,
        url=str(request.url),
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": exc.detail,
                "type": "http_exception"
            }
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(
        "Unhandled exception",
        exc_info=exc,
        url=str(request.url),
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "type": "server_error"
            }
        },
    )


# Include routers
app.include_router(health_router, prefix="", tags=["health"])
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Synthese Comparative Service",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health/"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8005,
        reload=settings.DEBUG,
        log_level="info"
    )