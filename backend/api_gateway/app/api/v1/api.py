"""
Main API router for DocQA-MS API Gateway v1
"""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    documents,
    search,
    qa,
    synthesis,
    audit,
    auth,
    deid,
    indexer,
    dashboard,
    users
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["authentication"]
)

api_router.include_router(
    documents.router,
    prefix="/documents",
    tags=["documents"]
)

api_router.include_router(
    deid.router,
    prefix="/deid",
    tags=["de-identification"]
)

api_router.include_router(
    indexer.router,
    prefix="/indexer",
    tags=["semantic-indexing"]
)

api_router.include_router(
    search.router,
    prefix="/search",
    tags=["search"]
)

api_router.include_router(
    qa.router,
    prefix="/qa",
    tags=["question-answering"]
)

api_router.include_router(
    synthesis.router,
    prefix="/synthesis",
    tags=["synthesis"]
)

api_router.include_router(
    audit.router,
    prefix="/audit",
    tags=["audit"]
)

api_router.include_router(
    dashboard.router,
    prefix="/dashboard",
    tags=["dashboard"]
)

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["users"]
)