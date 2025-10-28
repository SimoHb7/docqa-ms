"""
API v1 router for DocQA-MS DeID Service
"""
from fastapi import APIRouter

from app.api.v1.endpoints import deid

api_router = APIRouter()
api_router.include_router(deid.router, prefix="/deid", tags=["deid"])