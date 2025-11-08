"""
Database connection utilities for API Gateway
"""
import asyncpg
from typing import Optional
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_pool: Optional[asyncpg.Pool] = None


async def get_db_pool() -> asyncpg.Pool:
    """Get or create database connection pool"""
    global _pool
    
    if _pool is None:
        try:
            _pool = await asyncpg.create_pool(
                settings.DATABASE_URL,
                min_size=2,
                max_size=10,
                command_timeout=60
            )
            logger.info("Database connection pool created")
        except Exception as e:
            logger.error("Failed to create database pool", error=str(e))
            raise
    
    return _pool


async def close_db_pool():
    """Close database connection pool"""
    global _pool
    
    if _pool is not None:
        await _pool.close()
        _pool = None
        logger.info("Database connection pool closed")


async def execute_query(query: str, *args):
    """Execute a database query"""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        return await conn.fetch(query, *args)


async def execute_one(query: str, *args):
    """Execute a query and return one result"""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        return await conn.fetchrow(query, *args)


async def execute_insert(query: str, *args):
    """Execute an insert query"""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        return await conn.execute(query, *args)
