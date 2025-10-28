"""
API router definitions for Semantic Indexer service
"""
from fastapi import APIRouter
from app.api.v1.endpoints import indexer, search

# Create main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(
    indexer.router,
    prefix="/index",
    tags=["indexing"]
)

api_router.include_router(
    search.router,
    prefix="/search",
    tags=["search"]
)