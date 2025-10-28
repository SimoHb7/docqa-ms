"""
Main API router for DocQA-MS Audit Logger v1
"""
from fastapi import APIRouter

from app.api.v1.endpoints import audit

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    audit.router,
    prefix="/audit",
    tags=["audit"]
)