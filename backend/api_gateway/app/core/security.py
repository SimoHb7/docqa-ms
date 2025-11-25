"""
Auth0 JWT Token Validation and Security
"""
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import httpx
import structlog
from functools import lru_cache
from datetime import datetime

from app.core.config import settings

logger = structlog.get_logger(__name__)

# Security scheme
security = HTTPBearer()


class Auth0JWKSClient:
    """Auth0 JWKS (JSON Web Key Set) client for token verification"""
    
    def __init__(self, domain: str):
        self.domain = domain
        self.jwks_url = f"https://{domain}/.well-known/jwks.json"
        self._jwks_cache: Optional[Dict] = None
    
    async def get_jwks(self) -> Dict:
        """Fetch JWKS from Auth0 (cached)"""
        if self._jwks_cache:
            return self._jwks_cache
        
        async with httpx.AsyncClient() as client:
            response = await client.get(self.jwks_url)
            response.raise_for_status()
            self._jwks_cache = response.json()
            return self._jwks_cache
    
    async def get_signing_key(self, token: str) -> str:
        """Get the signing key from JWKS"""
        try:
            # Decode header without verification to get kid
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get("kid")
            
            if not kid:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token is missing key ID (kid)"
                )
            
            # Get JWKS
            jwks = await self.get_jwks()
            
            # Find the key with matching kid
            for key in jwks.get("keys", []):
                if key.get("kid") == kid:
                    # Return the key as PEM format
                    from jose.backends import RSAKey
                    rsa_key = RSAKey(key, algorithm="RS256")
                    return rsa_key
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unable to find appropriate signing key"
            )
        
        except Exception as e:
            logger.error("Error getting signing key", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unable to verify token signature"
            )


# Initialize Auth0 JWKS client
auth0_jwks_client = Auth0JWKSClient(settings.AUTH0_DOMAIN)


async def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify Auth0 JWT token and return decoded payload
    """
    try:
        # Get signing key
        signing_key = await auth0_jwks_client.get_signing_key(token)
        
        # Verify and decode token
        payload = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            audience=settings.AUTH0_AUDIENCE,
            issuer=f"https://{settings.AUTH0_DOMAIN}/",
        )
        
        logger.info("Token verified successfully", sub=payload.get("sub"))
        return payload
    
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    except jwt.JWTClaimsError as e:
        logger.warning("Invalid token claims", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token claims (audience or issuer mismatch)",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    except JWTError as e:
        logger.error("JWT validation error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    except Exception as e:
        logger.error("Unexpected error verifying token", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Dependency to get current authenticated user from JWT token
    
    Returns the token payload with user info:
    - sub: Auth0 user ID (e.g., "auth0|123456")
    - email: User's email
    - name: User's name (if available)
    - permissions: List of permissions (if configured)
    """
    token = credentials.credentials
    payload = await verify_token(token)
    return payload


async def get_current_active_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Dependency to get current active user
    Additional checks can be added here (e.g., is_active flag)
    """
    # You can add additional checks here, like:
    # - Check if user exists in database
    # - Check if user is active
    # - Load user permissions from database
    
    return current_user


def require_permission(permission: str):
    """
    Dependency to require specific permission
    
    Usage:
        @app.get("/admin", dependencies=[Depends(require_permission("admin"))])
        async def admin_endpoint():
            ...
    """
    async def permission_checker(
        current_user: Dict[str, Any] = Depends(get_current_user)
    ):
        user_permissions = current_user.get("permissions", [])
        
        if permission not in user_permissions:
            logger.warning(
                "Permission denied",
                user=current_user.get("sub"),
                required_permission=permission,
                user_permissions=user_permissions
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Required: {permission}"
            )
        
        return current_user
    
    return permission_checker


def require_role(role: str):
    """
    Dependency to require specific role
    
    Usage:
        @app.get("/admin", dependencies=[Depends(require_role("admin"))])
        async def admin_endpoint():
            ...
    """
    async def role_checker(
        current_user: Dict[str, Any] = Depends(get_current_user)
    ):
        user_roles = current_user.get("https://api.interfaceclinique.com/roles", [])
        
        if role not in user_roles:
            logger.warning(
                "Role denied",
                user=current_user.get("sub"),
                required_role=role,
                user_roles=user_roles
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role denied. Required: {role}"
            )
        
        return current_user
    
    return role_checker
