"""
Authentication API endpoints for DocQA-MS API Gateway
Integrated with Auth0 for OAuth2/JWT authentication
"""
from datetime import datetime, timedelta
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
import httpx
import asyncpg

from app.core.config import settings
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)

# HTTP Bearer scheme for Auth0
security = HTTPBearer()

# Auth0 Configuration
AUTH0_DOMAIN = settings.AUTH0_DOMAIN if hasattr(settings, 'AUTH0_DOMAIN') else "dev-rwicnayrjuhx63km.us.auth0.com"
AUTH0_API_AUDIENCE = settings.AUTH0_AUDIENCE if hasattr(settings, 'AUTH0_AUDIENCE') else "https://api.interfaceclinique.com"
AUTH0_ALGORITHMS = ["RS256"]


async def get_db_pool():
    """Get database connection pool"""
    if not hasattr(get_db_pool, "pool"):
        try:
            get_db_pool.pool = await asyncpg.create_pool(
                host=settings.POSTGRES_HOST if hasattr(settings, 'POSTGRES_HOST') else 'localhost',
                port=settings.POSTGRES_PORT if hasattr(settings, 'POSTGRES_PORT') else 5432,
                database=settings.POSTGRES_DB if hasattr(settings, 'POSTGRES_DB') else 'docqa_ms',
                user=settings.POSTGRES_USER if hasattr(settings, 'POSTGRES_USER') else 'postgres',
                password=settings.POSTGRES_PASSWORD if hasattr(settings, 'POSTGRES_PASSWORD') else 'postgres',
                min_size=2,
                max_size=10
            )
            logger.info("Database connection pool created")
        except Exception as e:
            logger.error(f"Failed to create database pool: {e}")
            get_db_pool.pool = None
    return get_db_pool.pool


async def verify_auth0_token(token: str) -> dict:
    """
    Verify Auth0 JWT token
    Returns the decoded token payload if valid
    """
    try:
        # Get Auth0 public key (JWKS)
        jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
        
        async with httpx.AsyncClient() as client:
            jwks_response = await client.get(jwks_url)
            jwks = jwks_response.json()
        
        # Decode the JWT header to get the key ID (kid)
        unverified_header = jwt.get_unverified_header(token)
        
        # Find the correct key from JWKS
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
                break
        
        if not rsa_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unable to find appropriate key"
            )
        
        # Verify and decode the token
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=AUTH0_ALGORITHMS,
            audience=AUTH0_API_AUDIENCE,
            issuer=f"https://{AUTH0_DOMAIN}/"
        )
        
        return payload
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTClaimsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token claims"
        )
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )


async def get_or_create_user(auth0_payload: dict) -> dict:
    """
    Get user from database or create if doesn't exist
    Sync user data with Auth0 profile
    """
    pool = await get_db_pool()
    if not pool:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service unavailable"
        )
    
    auth0_sub = auth0_payload.get("sub")
    email = auth0_payload.get("email", "")
    name = auth0_payload.get("name", "")
    nickname = auth0_payload.get("nickname", "")
    picture = auth0_payload.get("picture", "")
    email_verified = auth0_payload.get("email_verified", False)
    
    try:
        async with pool.acquire() as conn:
            # Try to get existing user
            user = await conn.fetchrow(
                """
                SELECT id, auth0_sub, email, name, role, permissions, is_active
                FROM users
                WHERE auth0_sub = $1
                """,
                auth0_sub
            )
            
            if user:
                # Update last login and profile info
                await conn.execute(
                    """
                    UPDATE users 
                    SET last_login = NOW(),
                        email = $2,
                        name = $3,
                        nickname = $4,
                        picture = $5,
                        email_verified = $6,
                        updated_at = NOW()
                    WHERE auth0_sub = $1
                    """,
                    auth0_sub, email, name, nickname, picture, email_verified
                )
                
                logger.info(f"User logged in: {email}")
                
                return {
                    "id": str(user["id"]),
                    "auth0_sub": user["auth0_sub"],
                    "email": user["email"],
                    "name": user["name"],
                    "role": user["role"],
                    "permissions": user["permissions"],
                    "is_active": user["is_active"]
                }
            else:
                # Create new user
                new_user = await conn.fetchrow(
                    """
                    INSERT INTO users (
                        auth0_sub, email, name, nickname, picture, 
                        role, permissions, email_verified, last_login
                    )
                    VALUES ($1, $2, $3, $4, $5, 'clinician', 
                            '["read_documents", "upload_documents", "ask_questions"]'::jsonb,
                            $6, NOW())
                    RETURNING id, auth0_sub, email, name, role, permissions, is_active
                    """,
                    auth0_sub, email, name, nickname, picture, email_verified
                )
                
                logger.info(f"New user created: {email}")
                
                # Log audit event
                await conn.execute(
                    """
                    INSERT INTO audit_logs (user_id, action, resource_type, details)
                    VALUES ($1, 'user_registration', 'user', $2::jsonb)
                    """,
                    new_user["id"],
                    '{"email": "' + email + '"}'
                )
                
                return {
                    "id": str(new_user["id"]),
                    "auth0_sub": new_user["auth0_sub"],
                    "email": new_user["email"],
                    "name": new_user["name"],
                    "role": new_user["role"],
                    "permissions": new_user["permissions"],
                    "is_active": new_user["is_active"]
                }
                
    except Exception as e:
        logger.error(f"Database error in get_or_create_user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process user information"
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Get current authenticated user from Auth0 JWT token
    This is a dependency that can be used in protected routes
    """
    token = credentials.credentials
    
    # Verify the Auth0 token
    auth0_payload = await verify_auth0_token(token)
    
    # Get or create user in database
    user = await get_or_create_user(auth0_payload)
    
    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not active"
        )
    
    return user


@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get current authenticated user information
    This endpoint is called by the frontend after Auth0 authentication
    """
    return {
        "user": current_user,
        "authenticated": True
    }


@router.post("/verify")
async def verify_token(current_user: dict = Depends(get_current_user)):
    """
    Verify if the provided token is valid
    Returns user info if valid
    """
    return {
        "valid": True,
        "user": current_user
    }


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Logout endpoint
    Auth0 manages sessions, but we log the event
    """
    pool = await get_db_pool()
    
    if pool:
        try:
            async with pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO audit_logs (user_id, action, resource_type)
                    VALUES ($1, 'user_logout', 'auth')
                    """,
                    current_user["id"]
                )
        except Exception as e:
            logger.error(f"Failed to log logout event: {e}")
    
    logger.info(f"User logged out: {current_user['email']}")
    
    return {
        "message": "Successfully logged out",
        "logout_url": f"https://{AUTH0_DOMAIN}/v2/logout?client_id={settings.AUTH0_CLIENT_ID if hasattr(settings, 'AUTH0_CLIENT_ID') else ''}&returnTo={settings.FRONTEND_URL if hasattr(settings, 'FRONTEND_URL') else 'http://localhost:5173'}"
    }


@router.get("/health")
async def auth_health_check():
    """
    Health check for authentication service
    """
    try:
        # Check Auth0 connectivity
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://{AUTH0_DOMAIN}/.well-known/jwks.json", timeout=5.0)
            auth0_status = "ok" if response.status_code == 200 else "error"
        
        # Check database connectivity
        pool = await get_db_pool()
        if pool:
            async with pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            db_status = "ok"
        else:
            db_status = "unavailable"
        
        return {
            "status": "ok" if auth0_status == "ok" and db_status == "ok" else "degraded",
            "auth0": auth0_status,
            "database": db_status,
            "domain": AUTH0_DOMAIN
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "error",
            "error": str(e)
        }
