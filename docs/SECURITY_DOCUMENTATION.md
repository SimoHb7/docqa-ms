# 🔐 DocQA-MS Security & Authentication Documentation

**Version**: 2.0  
**Last Updated**: December 11, 2025  
**Security Level**: Production-Ready

---

## 📋 Table of Contents

1. [Security Overview](#security-overview)
2. [Authentication with Auth0](#authentication-with-auth0)
3. [JWT Token Management](#jwt-token-management)
4. [Authorization & Access Control](#authorization--access-control)
5. [API Security](#api-security)
6. [Data Security](#data-security)
7. [Network Security](#network-security)
8. [Security Best Practices](#security-best-practices)
9. [Threat Model](#threat-model)
10. [Compliance](#compliance)

---

## 🛡️ Security Overview

### **Security Architecture Layers**

```mermaid
graph TB
    subgraph "Layer 1: Client Security"
        HTTPS[HTTPS/TLS<br/>Encrypted Transport]
        CSP[Content Security Policy<br/>XSS Protection]
        CORS[CORS Policy<br/>Origin Validation]
    end
    
    subgraph "Layer 2: Authentication"
        Auth0[Auth0 Service<br/>OAuth 2.0 + OIDC]
        JWT[JWT Tokens<br/>RS256 Signature]
        Refresh[Token Refresh<br/>Automatic Renewal]
    end
    
    subgraph "Layer 3: Authorization"
        RBAC[Role-Based Access Control<br/>Admin/Doctor/Researcher]
        Permissions[Permission Checks<br/>Fine-grained Access]
        Scopes[OAuth Scopes<br/>API Permissions]
    end
    
    subgraph "Layer 4: API Security"
        Gateway[API Gateway<br/>Request Validation]
        RateLimit[Rate Limiting<br/>DDoS Protection]
        InputVal[Input Validation<br/>Sanitization]
    end
    
    subgraph "Layer 5: Data Security"
        Encryption[Data Encryption<br/>At Rest & Transit]
        PII[PII Anonymization<br/>DeID Service]
        Backup[Secure Backups<br/>Encrypted Storage]
    end
    
    subgraph "Layer 6: Infrastructure"
        Docker[Container Isolation<br/>Docker Security]
        Network[Network Segmentation<br/>Private Networks]
        Logs[Audit Logging<br/>Security Monitoring]
    end
    
    HTTPS --> Auth0
    CSP --> Auth0
    CORS --> Auth0
    
    Auth0 --> RBAC
    JWT --> RBAC
    Refresh --> RBAC
    
    RBAC --> Gateway
    Permissions --> Gateway
    Scopes --> Gateway
    
    Gateway --> Encryption
    RateLimit --> Encryption
    InputVal --> Encryption
    
    Encryption --> Docker
    PII --> Docker
    Backup --> Docker
    
    style Auth0 fill:#fff3e0,stroke:#f57c00,stroke-width:3px
    style JWT fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    style RBAC fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    style Gateway fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
```

---

## 🔑 Authentication with Auth0

### **1. Auth0 Configuration**

#### **Application Settings**

```yaml
Application Type: Single Page Application (SPA)
Token Endpoint Authentication: None (PKCE)
Grant Types:
  - Authorization Code
  - Refresh Token
  - Implicit (Legacy, disabled)

Allowed Callback URLs:
  - http://localhost:3000
  - http://localhost:3000/callback
  - https://yourdomain.com
  - https://yourdomain.com/callback

Allowed Logout URLs:
  - http://localhost:3000
  - https://yourdomain.com

Allowed Web Origins:
  - http://localhost:3000
  - https://yourdomain.com

CORS:
  - http://localhost:3000
  - https://yourdomain.com
```

#### **Auth0 Connection Settings**

```yaml
Connections Enabled:
  - Username-Password-Authentication (Database)
  - google-oauth2 (Google Social Login)
  - github (GitHub Social Login) - Optional

Password Policy:
  - Minimum Length: 8 characters
  - Requires: Lowercase, Uppercase, Numbers, Symbols
  - Password History: 5 previous passwords
  - Brute Force Protection: Enabled
  - Max Login Attempts: 10
  - Lockout Duration: 30 minutes
```

---

### **2. Frontend Authentication Implementation**

#### **Auth0 Provider Setup** (`src/main.tsx`)

```typescript
import { Auth0Provider } from '@auth0/auth0-react';

<Auth0Provider
  domain={import.meta.env.VITE_AUTH0_DOMAIN}
  clientId={import.meta.env.VITE_AUTH0_CLIENT_ID}
  authorizationParams={{
    redirect_uri: window.location.origin,
    audience: import.meta.env.VITE_AUTH0_AUDIENCE,
    scope: 'openid profile email read:documents write:documents admin:all',
  }}
  cacheLocation="memory" // Secure: tokens not stored in localStorage
  useRefreshTokens={true}
  useRefreshTokensFallback={true}
>
  <App />
</Auth0Provider>
```

**Security Features:**
- ✅ `cacheLocation="memory"` - Tokens stored in memory, not localStorage (XSS protection)
- ✅ `useRefreshTokens={true}` - Automatic token refresh
- ✅ PKCE flow - Prevents authorization code interception
- ✅ Audience parameter - API-specific tokens

---

#### **Authentication Hook** (`src/hooks/useAuth.ts`)

```typescript
import { useAuth0 } from '@auth0/auth0-react';

export const useAuth = () => {
  const {
    isAuthenticated,
    isLoading,
    user,
    loginWithRedirect,
    logout,
    getAccessTokenSilently,
    getIdTokenClaims,
  } = useAuth0();

  const getToken = async (): Promise<string> => {
    try {
      const token = await getAccessTokenSilently({
        authorizationParams: {
          audience: import.meta.env.VITE_AUTH0_AUDIENCE,
          scope: 'openid profile email read:documents write:documents',
        },
      });
      return token;
    } catch (error) {
      console.error('Error getting access token:', error);
      throw error;
    }
  };

  return {
    isAuthenticated,
    isLoading,
    user,
    login: loginWithRedirect,
    logout: () => logout({ logoutParams: { returnTo: window.location.origin } }),
    getToken,
  };
};
```

---

#### **Protected Route Component** (`src/App.tsx`)

```typescript
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading, loginWithRedirect } = useAuth0();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      loginWithRedirect();
    }
  }, [isAuthenticated, isLoading, loginWithRedirect]);

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  return isAuthenticated ? <>{children}</> : null;
};
```

---

### **3. Authentication Flow Diagram**

```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant React as React App
    participant Auth0 as Auth0 Service
    participant Gateway as API Gateway
    
    User->>Browser: Navigate to app
    Browser->>React: Load application
    
    React->>React: Check auth state
    
    alt Not Authenticated
        React->>Auth0: Redirect to /authorize
        Note over Auth0: PKCE: Generate code_verifier<br/>& code_challenge
        Auth0-->>User: Show login page
        
        User->>Auth0: Enter credentials
        Auth0->>Auth0: Validate credentials
        Auth0->>Auth0: Create session
        
        Auth0-->>React: Redirect with authorization code
        React->>Auth0: POST /oauth/token<br/>code + code_verifier
        
        Auth0->>Auth0: Verify PKCE
        Auth0->>Auth0: Generate tokens
        
        Auth0-->>React: {<br/>  access_token (JWT),<br/>  id_token (JWT),<br/>  refresh_token,<br/>  expires_in: 3600<br/>}
        
        React->>React: Store tokens in memory
        React->>Auth0: GET /userinfo<br/>Bearer {access_token}
        Auth0-->>React: User profile
        
        React-->>User: Show dashboard
    end
    
    User->>React: Make API request
    React->>React: Get access_token
    
    alt Token Valid
        React->>Gateway: API request<br/>Authorization: Bearer {token}
        Gateway->>Gateway: Verify JWT signature
        Gateway->>Gateway: Check expiration
        Gateway->>Gateway: Extract claims
        Gateway-->>React: API response
        React-->>User: Display result
    else Token Expired
        React->>Auth0: POST /oauth/token<br/>refresh_token
        Auth0->>Auth0: Validate refresh token
        Auth0-->>React: New access_token
        React->>Gateway: Retry API request
        Gateway-->>React: API response
    end
    
    User->>React: Click logout
    React->>Auth0: GET /v2/logout
    Auth0->>Auth0: Terminate session
    Auth0-->>React: Redirect to returnTo
    React->>React: Clear tokens from memory
    React-->>User: Show login page
```

---

## 🎫 JWT Token Management

### **1. JWT Token Structure**

#### **Access Token (JWT)**

```json
{
  "header": {
    "alg": "RS256",
    "typ": "JWT",
    "kid": "abc123xyz"
  },
  "payload": {
    "iss": "https://your-tenant.auth0.com/",
    "sub": "auth0|507f1f77bcf86cd799439011",
    "aud": [
      "https://api.docqa-ms.com",
      "https://your-tenant.auth0.com/userinfo"
    ],
    "iat": 1702310400,
    "exp": 1702314000,
    "azp": "YOUR_CLIENT_ID",
    "scope": "openid profile email read:documents write:documents",
    "permissions": [
      "read:documents",
      "write:documents",
      "delete:documents"
    ],
    "https://docqa-ms.com/roles": ["doctor", "user"],
    "https://docqa-ms.com/email": "user@example.com"
  },
  "signature": "..." // RS256 signature
}
```

**Token Properties:**
- **Algorithm**: RS256 (RSA + SHA-256)
- **Issuer**: Auth0 tenant
- **Subject**: User ID
- **Audience**: API identifier
- **Expiration**: 1 hour (3600 seconds)
- **Scope**: OAuth 2.0 scopes
- **Custom Claims**: Roles, permissions, email

---

#### **ID Token (JWT)**

```json
{
  "header": {
    "alg": "RS256",
    "typ": "JWT"
  },
  "payload": {
    "iss": "https://your-tenant.auth0.com/",
    "sub": "auth0|507f1f77bcf86cd799439011",
    "aud": "YOUR_CLIENT_ID",
    "iat": 1702310400,
    "exp": 1702314000,
    "nonce": "random_nonce_value",
    "name": "John Doe",
    "nickname": "john.doe",
    "picture": "https://gravatar.com/avatar/...",
    "email": "john.doe@example.com",
    "email_verified": true,
    "https://docqa-ms.com/roles": ["doctor"]
  }
}
```

**Purpose**: Contains user profile information for the frontend.

---

#### **Refresh Token**

```
Opaque token (not JWT)
Format: Encrypted string
Expiration: 30 days (rotating)
Purpose: Obtain new access_token without re-authentication
Storage: Secure HTTP-only cookie (production) or memory (development)
```

---

### **2. Token Validation in Backend**

#### **API Gateway JWT Validation** (`backend/api_gateway/app/core/security.py`)

```python
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import httpx
from functools import lru_cache

security = HTTPBearer()

# Auth0 configuration
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_AUDIENCE = os.getenv("AUTH0_AUDIENCE")
ALGORITHMS = ["RS256"]

@lru_cache()
async def get_jwks():
    """Fetch Auth0 public keys (cached)"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://{AUTH0_DOMAIN}/.well-known/jwks.json")
        return response.json()

async def verify_token(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> dict:
    """
    Verify JWT token from Auth0
    
    Steps:
    1. Extract token from Authorization header
    2. Decode header to get 'kid'
    3. Fetch JWKS and find matching public key
    4. Verify signature with RS256
    5. Validate claims (iss, aud, exp)
    6. Return decoded payload
    """
    token = credentials.credentials
    
    try:
        # Decode token header (unverified)
        unverified_header = jwt.get_unverified_header(token)
        
        # Get JWKS (public keys)
        jwks = await get_jwks()
        
        # Find matching key
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
            raise HTTPException(status_code=401, detail="Unable to find appropriate key")
        
        # Verify and decode token
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=ALGORITHMS,
            audience=AUTH0_AUDIENCE,
            issuer=f"https://{AUTH0_DOMAIN}/"
        )
        
        return payload
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTClaimsError:
        raise HTTPException(status_code=401, detail="Invalid token claims")
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token validation error: {str(e)}")

# Dependency for protected routes
async def get_current_user(token_payload: dict = Depends(verify_token)) -> dict:
    """Extract user information from verified token"""
    return {
        "user_id": token_payload.get("sub"),
        "email": token_payload.get("https://docqa-ms.com/email"),
        "roles": token_payload.get("https://docqa-ms.com/roles", []),
        "permissions": token_payload.get("permissions", [])
    }
```

---

#### **Protected Endpoint Example**

```python
from fastapi import APIRouter, Depends
from app.core.security import get_current_user

router = APIRouter()

@router.get("/api/documents")
async def list_documents(
    current_user: dict = Depends(get_current_user),
    limit: int = 20,
    offset: int = 0
):
    """
    List documents (authenticated users only)
    
    Security:
    - Requires valid JWT token
    - Extracts user_id from token
    - Filters documents by user
    """
    user_id = current_user["user_id"]
    
    # Query documents belonging to user
    documents = await db.fetch_documents(user_id, limit, offset)
    
    return {
        "data": documents,
        "total": len(documents),
        "user": current_user["email"]
    }
```

---

### **3. Token Refresh Flow**

```mermaid
sequenceDiagram
    participant React
    participant Auth0
    participant Gateway
    
    Note over React: User makes API request
    React->>React: Get access_token from memory
    React->>Gateway: API request with token
    
    Gateway->>Gateway: Verify token
    
    alt Token Expired
        Gateway-->>React: 401 Unauthorized
        
        React->>React: Get refresh_token
        React->>Auth0: POST /oauth/token<br/>{<br/>  grant_type: 'refresh_token',<br/>  refresh_token: '...',<br/>  client_id: '...'<br/>}
        
        Auth0->>Auth0: Validate refresh_token
        
        alt Refresh Token Valid
            Auth0-->>React: {<br/>  access_token: 'new_token',<br/>  expires_in: 3600<br/>}
            React->>React: Update token in memory
            React->>Gateway: Retry API request
            Gateway-->>React: Success response
        else Refresh Token Invalid/Expired
            Auth0-->>React: 401 Unauthorized
            React->>Auth0: Redirect to login
        end
    else Token Valid
        Gateway-->>React: Success response
    end
```

---

## 🔐 Authorization & Access Control

### **1. Role-Based Access Control (RBAC)**

#### **Defined Roles**

```typescript
// src/types/index.ts
export type UserRole = 'admin' | 'doctor' | 'researcher' | 'quality_manager';

export interface User {
  id: string;
  email: string;
  name: string;
  picture?: string;
  role: UserRole;
  organization?: string;
  permissions: string[];
  createdAt: string;
  lastLogin?: string;
}
```

#### **Role Permissions Matrix**

| Permission | Admin | Doctor | Researcher | Quality Manager |
|------------|-------|--------|------------|-----------------|
| **read:documents** | ✅ | ✅ | ✅ | ✅ |
| **write:documents** | ✅ | ✅ | ✅ | ❌ |
| **delete:documents** | ✅ | ✅ | ❌ | ❌ |
| **read:qa** | ✅ | ✅ | ✅ | ✅ |
| **write:qa** | ✅ | ✅ | ✅ | ❌ |
| **read:synthesis** | ✅ | ✅ | ✅ | ✅ |
| **write:synthesis** | ✅ | ✅ | ✅ | ❌ |
| **read:ml_analytics** | ✅ | ✅ | ✅ | ✅ |
| **admin:users** | ✅ | ❌ | ❌ | ❌ |
| **admin:settings** | ✅ | ❌ | ❌ | ❌ |
| **admin:all** | ✅ | ❌ | ❌ | ❌ |

---

#### **Auth0 RBAC Setup**

**1. Create Roles in Auth0 Dashboard:**

```
User Management > Roles > Create Role

Role: admin
Description: Full system access
Permissions:
  - read:documents
  - write:documents
  - delete:documents
  - read:qa
  - write:qa
  - admin:users
  - admin:settings
  - admin:all

Role: doctor
Description: Medical staff access
Permissions:
  - read:documents
  - write:documents
  - delete:documents
  - read:qa
  - write:qa
  - read:synthesis
  - write:synthesis
  - read:ml_analytics

Role: researcher
Description: Research and analysis access
Permissions:
  - read:documents
  - write:documents
  - read:qa
  - write:qa
  - read:synthesis
  - write:synthesis
  - read:ml_analytics

Role: quality_manager
Description: Quality assurance access
Permissions:
  - read:documents
  - read:qa
  - read:synthesis
  - read:ml_analytics
```

**2. Assign Roles to Users:**
```
User Management > Users > Select User > Roles > Assign Role
```

**3. Add Roles to Tokens (Auth0 Rule):**

```javascript
// Auth0 Dashboard > Auth Pipeline > Rules > Create Rule

function addRolesToTokens(user, context, callback) {
  const namespace = 'https://docqa-ms.com/';
  const assignedRoles = (context.authorization || {}).roles || [];
  
  // Add roles to access token
  context.accessToken[namespace + 'roles'] = assignedRoles;
  
  // Add email to access token
  context.accessToken[namespace + 'email'] = user.email;
  
  // Add roles to ID token
  context.idToken[namespace + 'roles'] = assignedRoles;
  
  callback(null, user, context);
}
```

---

### **2. Permission Checks in Backend**

```python
from fastapi import HTTPException, Depends
from typing import List

def require_permissions(required_permissions: List[str]):
    """
    Decorator to check user permissions
    
    Usage:
        @router.delete("/api/documents/{id}")
        async def delete_document(
            id: str,
            current_user: dict = Depends(require_permissions(["delete:documents"]))
        ):
            ...
    """
    async def permission_checker(
        current_user: dict = Depends(get_current_user)
    ) -> dict:
        user_permissions = current_user.get("permissions", [])
        
        # Admin has all permissions
        if "admin:all" in user_permissions:
            return current_user
        
        # Check if user has required permissions
        for permission in required_permissions:
            if permission not in user_permissions:
                raise HTTPException(
                    status_code=403,
                    detail=f"Insufficient permissions. Required: {', '.join(required_permissions)}"
                )
        
        return current_user
    
    return permission_checker

# Usage example
@router.delete("/api/documents/{document_id}")
async def delete_document(
    document_id: str,
    current_user: dict = Depends(require_permissions(["delete:documents"]))
):
    """Delete document (requires delete:documents permission)"""
    await db.delete_document(document_id, current_user["user_id"])
    return {"message": "Document deleted successfully"}
```

---

### **3. Frontend Permission Checks**

```typescript
// src/hooks/usePermissions.ts
import { useAuth0 } from '@auth0/auth0-react';

export const usePermissions = () => {
  const { user } = useAuth0();
  
  const hasPermission = (permission: string): boolean => {
    const userPermissions = user?.['https://docqa-ms.com/permissions'] || [];
    return userPermissions.includes(permission) || userPermissions.includes('admin:all');
  };
  
  const hasRole = (role: string): boolean => {
    const userRoles = user?.['https://docqa-ms.com/roles'] || [];
    return userRoles.includes(role);
  };
  
  const canDelete = hasPermission('delete:documents');
  const canUpload = hasPermission('write:documents');
  const isAdmin = hasRole('admin');
  
  return {
    hasPermission,
    hasRole,
    canDelete,
    canUpload,
    isAdmin,
  };
};

// Usage in component
const DocumentActions: React.FC = () => {
  const { canDelete } = usePermissions();
  
  return (
    <Box>
      {canDelete && (
        <Button onClick={handleDelete}>
          Delete Document
        </Button>
      )}
    </Box>
  );
};
```

---

## 🌐 API Security

### **1. CORS Configuration**

```python
# backend/api_gateway/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Development
        "https://docqa-ms.com",    # Production
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "Accept",
        "Origin",
        "X-Requested-With",
    ],
    expose_headers=["Content-Length", "X-Total-Count"],
    max_age=3600,  # Cache preflight requests for 1 hour
)
```

---

### **2. Rate Limiting**

```python
from fastapi import Request
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import redis.asyncio as redis

# Initialize rate limiter
@app.on_event("startup")
async def startup():
    redis_client = await redis.from_url("redis://localhost:6379")
    await FastAPILimiter.init(redis_client)

# Apply rate limit to endpoints
@router.post("/api/qa/ask")
@limiter.limit("10/minute")  # 10 requests per minute
async def ask_question(
    request: Request,
    question: str,
    current_user: dict = Depends(get_current_user)
):
    """Rate-limited Q&A endpoint"""
    # Process question
    pass
```

---

### **3. Input Validation & Sanitization**

```python
from pydantic import BaseModel, Field, validator
from typing import Optional
import bleach

class DocumentUploadRequest(BaseModel):
    """Validated document upload request"""
    
    filename: str = Field(..., min_length=1, max_length=255)
    file_type: str = Field(..., regex="^(pdf|png|jpg|jpeg|docx)$")
    patient_id: Optional[str] = Field(None, max_length=100)
    document_type: Optional[str] = Field(None, max_length=100)
    
    @validator('filename')
    def sanitize_filename(cls, v):
        """Remove potentially harmful characters"""
        # Allow only alphanumeric, dash, underscore, dot
        return bleach.clean(v, tags=[], strip=True)
    
    @validator('patient_id', 'document_type')
    def sanitize_strings(cls, v):
        """Sanitize text inputs"""
        if v:
            return bleach.clean(v, tags=[], strip=True)
        return v

# Usage
@router.post("/api/documents/upload")
async def upload_document(
    request: DocumentUploadRequest,
    current_user: dict = Depends(get_current_user)
):
    # Request is validated and sanitized
    pass
```

---

### **4. SQL Injection Protection**

```python
# Using SQLAlchemy ORM (parameterized queries)
from sqlalchemy import select
from app.models import Document

# ✅ SAFE: SQLAlchemy handles parameterization
async def get_documents(user_id: str, search: str):
    query = select(Document).where(
        Document.uploaded_by == user_id,
        Document.filename.ilike(f"%{search}%")
    )
    result = await session.execute(query)
    return result.scalars().all()

# ❌ UNSAFE: Never do this!
# query = f"SELECT * FROM documents WHERE filename LIKE '%{search}%'"
```

---

## 🔒 Data Security

### **1. PII Anonymization**

**DeID Service Implementation:**

```python
# backend/deid/app/services/deid_service.py
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from transformers import pipeline

class DeIDService:
    def __init__(self):
        # Presidio for PII detection
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()
        
        # BioBERT for medical NER
        self.ner_pipeline = pipeline(
            "ner",
            model="dmis-lab/biobert-base-cased-v1.1",
            aggregation_strategy="simple"
        )
    
    def detect_pii(self, text: str) -> List[dict]:
        """
        Detect PII entities:
        - PERSON (names)
        - LOCATION (addresses)
        - PHONE_NUMBER
        - EMAIL_ADDRESS
        - DATE_TIME
        - MEDICAL_LICENSE
        - CREDIT_CARD
        """
        results = self.analyzer.analyze(
            text=text,
            language="fr",  # French
            entities=[
                "PERSON", "LOCATION", "PHONE_NUMBER",
                "EMAIL_ADDRESS", "DATE_TIME", "MEDICAL_LICENSE"
            ]
        )
        return results
    
    def anonymize(self, text: str) -> str:
        """
        Anonymize PII:
        - Names → <PERSON_1>, <PERSON_2>
        - Addresses → <LOCATION_1>
        - Phone → <PHONE_1>
        - Email → <EMAIL_1>
        - Dates → <DATE_1>
        """
        pii_entities = self.detect_pii(text)
        
        anonymized = self.anonymizer.anonymize(
            text=text,
            analyzer_results=pii_entities,
            operators={
                "PERSON": {"type": "replace", "new_value": "<PERSON>"},
                "LOCATION": {"type": "replace", "new_value": "<LOCATION>"},
                "PHONE_NUMBER": {"type": "replace", "new_value": "<PHONE>"},
                "EMAIL_ADDRESS": {"type": "replace", "new_value": "<EMAIL>"},
                "DATE_TIME": {"type": "replace", "new_value": "<DATE>"},
            }
        )
        
        return anonymized.text
```

**Example:**
```
Original:
"Patient Jean Dupont, né le 15/03/1980, habite au 123 Rue de Paris.
Tel: 0612345678, Email: jean.dupont@email.com"

Anonymized:
"Patient <PERSON>, né le <DATE>, habite au <LOCATION>.
Tel: <PHONE>, Email: <EMAIL>"
```

---

### **2. Data Encryption**

#### **At Rest (Database)**

```yaml
# PostgreSQL encryption
postgresql:
  ssl_mode: require
  encryption: AES-256
  
# Environment variables encryption
.env encryption with git-crypt or AWS Secrets Manager
```

#### **In Transit (HTTPS/TLS)**

```nginx
# Production Nginx config
server {
    listen 443 ssl http2;
    server_name docqa-ms.com;
    
    ssl_certificate /etc/letsencrypt/live/docqa-ms.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/docqa-ms.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # HSTS (HTTP Strict Transport Security)
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

### **3. Secure File Upload**

```python
from fastapi import UploadFile, HTTPException
import magic
import hashlib

ALLOWED_MIME_TYPES = {
    'application/pdf',
    'image/png',
    'image/jpeg',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
}

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

async def validate_file(file: UploadFile) -> bool:
    """
    Validate uploaded file:
    1. Check MIME type
    2. Check file size
    3. Scan for malware (optional: ClamAV)
    4. Calculate hash for deduplication
    """
    # Read file content
    content = await file.read()
    await file.seek(0)  # Reset file pointer
    
    # Check size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(400, "File too large")
    
    # Verify MIME type (magic number, not extension)
    mime = magic.from_buffer(content, mime=True)
    if mime not in ALLOWED_MIME_TYPES:
        raise HTTPException(400, f"Invalid file type: {mime}")
    
    # Calculate SHA-256 hash
    file_hash = hashlib.sha256(content).hexdigest()
    
    # Check for duplicates
    existing = await db.get_document_by_hash(file_hash)
    if existing:
        raise HTTPException(409, "File already exists")
    
    return True

@router.post("/api/documents/upload")
async def upload_document(
    file: UploadFile,
    current_user: dict = Depends(get_current_user)
):
    """Secure file upload"""
    await validate_file(file)
    
    # Save file securely
    secure_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = f"/secure/storage/{secure_filename}"
    
    # Save with restricted permissions (chmod 600)
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    os.chmod(file_path, 0o600)  # Owner read/write only
    
    return {"message": "File uploaded successfully"}
```

---

## 🚨 Security Best Practices

### **1. Environment Variables**

```bash
# .env (NEVER commit to Git!)
# Use .env.example for template

# Auth0
AUTH0_DOMAIN=your-tenant.auth0.com
AUTH0_CLIENT_ID=your_client_id
AUTH0_CLIENT_SECRET=your_client_secret  # Backend only
AUTH0_AUDIENCE=https://api.docqa-ms.com

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/docqa
DATABASE_ENCRYPTION_KEY=your_32_character_encryption_key

# API Keys
OPENAI_API_KEY=sk-...
CLAUDE_API_KEY=sk-...

# Security
JWT_SECRET_KEY=your_jwt_secret_key_minimum_32_chars
SECRET_KEY=your_app_secret_key_minimum_32_chars

# Production: Use AWS Secrets Manager, Azure Key Vault, or HashiCorp Vault
```

**Loading in Backend:**

```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    auth0_domain: str
    auth0_audience: str
    database_url: str
    jwt_secret_key: str
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

---

### **2. Logging & Monitoring**

```python
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/docqa/security.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Security event logging
async def log_security_event(event_type: str, user_id: str, details: dict):
    """Log security-relevant events"""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "user_id": user_id,
        "ip_address": request.client.host,
        "user_agent": request.headers.get("user-agent"),
        "details": details
    }
    
    logger.warning(f"SECURITY_EVENT: {json.dumps(log_entry)}")
    
    # Store in database for auditing
    await db.create_audit_log(log_entry)

# Usage
@router.post("/api/documents/{id}/delete")
async def delete_document(id: str, current_user: dict = Depends(get_current_user)):
    await log_security_event(
        event_type="document_deleted",
        user_id=current_user["user_id"],
        details={"document_id": id}
    )
    
    await db.delete_document(id)
    return {"message": "Document deleted"}
```

---

### **3. Security Headers**

```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.sessions import SessionMiddleware

# Add security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "docqa-ms.com", "*.docqa-ms.com"]
)

# Secure session cookies
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key,
    session_cookie="docqa_session",
    max_age=3600,
    same_site="lax",
    https_only=True  # Production only
)

# Add security headers to all responses
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    
    # CSP (Content Security Policy)
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.auth0.com; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self' data:; "
        "connect-src 'self' https://your-tenant.auth0.com https://api.docqa-ms.com"
    )
    
    return response
```

---

## 🎯 Threat Model

### **Identified Threats & Mitigations**

| Threat | Impact | Likelihood | Mitigation |
|--------|--------|------------|------------|
| **XSS (Cross-Site Scripting)** | High | Medium | React auto-escaping, CSP headers, input sanitization |
| **SQL Injection** | Critical | Low | SQLAlchemy ORM, parameterized queries |
| **CSRF (Cross-Site Request Forgery)** | Medium | Low | SameSite cookies, CORS policy, token-based auth |
| **Token Theft** | High | Medium | Memory storage (not localStorage), HTTPS only, short expiration |
| **Brute Force Login** | Medium | High | Auth0 rate limiting, account lockout, MFA |
| **File Upload Attacks** | High | Medium | MIME validation, size limits, malware scanning |
| **DDoS** | High | Medium | Rate limiting, CDN (Cloudflare), load balancing |
| **Man-in-the-Middle** | Critical | Low | HTTPS/TLS, certificate pinning, HSTS |
| **Data Breach** | Critical | Low | Encryption at rest, PII anonymization, access logs |
| **Privilege Escalation** | High | Low | RBAC, permission checks, audit logging |

---

## 📜 Compliance

### **GDPR Compliance**

- ✅ **Data Minimization**: Only collect necessary data
- ✅ **Right to Access**: Users can download their data
- ✅ **Right to Deletion**: Users can request data deletion
- ✅ **Data Portability**: Export functionality
- ✅ **Consent Management**: Clear consent for data processing
- ✅ **Data Breach Notification**: Logging and alerting system
- ✅ **Privacy by Design**: PII anonymization by default

### **HIPAA Compliance** (Medical Data)

- ✅ **PHI Protection**: Anonymization of Protected Health Information
- ✅ **Access Controls**: Role-based access, audit logs
- ✅ **Encryption**: At rest (AES-256) and in transit (TLS 1.3)
- ✅ **Audit Trails**: All access to medical documents logged
- ✅ **Data Backup**: Secure encrypted backups
- ✅ **Disaster Recovery**: Backup and restore procedures

---

## 🔍 Security Checklist

### **Pre-Production Checklist**

- [ ] All environment variables secured (not in Git)
- [ ] HTTPS/TLS enabled with valid certificate
- [ ] Auth0 configured with production domain
- [ ] Rate limiting enabled on all endpoints
- [ ] CORS restricted to production domain
- [ ] Database encryption enabled
- [ ] PII anonymization tested
- [ ] Security headers configured
- [ ] Audit logging enabled
- [ ] Backup and recovery tested
- [ ] Penetration testing completed
- [ ] Security documentation reviewed
- [ ] Incident response plan defined
- [ ] Monitoring and alerting configured

---

## 📞 Security Contact

**Security Team**: security@docqa-ms.com  
**Responsible Disclosure**: https://docqa-ms.com/security  
**PGP Key**: [Available on request]

---

**Last Updated**: December 11, 2025  
**Next Review**: March 11, 2026  
**Document Owner**: Security Team
