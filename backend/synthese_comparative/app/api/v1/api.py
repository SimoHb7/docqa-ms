"""
API v1 router for Synthese Comparative Service
"""
from fastapi import APIRouter

from app.api.v1.endpoints import synthesis

api_router = APIRouter()
api_router.include_router(synthesis.router, prefix="/synthesis", tags=["synthesis"])