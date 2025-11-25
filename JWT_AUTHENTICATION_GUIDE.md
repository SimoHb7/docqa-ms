# 🔐 JWT Authentication & User Management Guide

## Overview

InterfaceClinique now uses **Auth0 JWT tokens** for authentication and user-specific database access. Every user has their own data isolation with role-based access control.

## 🏗️ Architecture

```
Frontend (React) 
    ↓ Login with Auth0
Auth0 (generates JWT token)
    ↓ Token in Authorization header
API Gateway (validates JWT + creates/loads user)
    ↓ User context attached to all requests
Database (user-specific queries)
```

## 🔑 How It Works

### 1. User Login Flow

```typescript
// Frontend: User clicks "Login"
const { loginWithRedirect } = useAuth0();
await loginWithRedirect();

// Auth0 handles authentication
// User is redirected back with authorization code

// Frontend: Get access token
const { getAccessTokenSilently } = useAuth0();
const token = await getAccessTokenSilently();

// Frontend: Send token with API requests
axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
```

### 2. Backend JWT Validation

```python
# API Gateway: Validate JWT token
from app.core.dependencies import get_or_create_user

@router.post("/documents/upload")
async def upload_document(
    file: UploadFile,
    current_user: Dict = Depends(get_or_create_user)  # ← JWT validation happens here
):
    # current_user contains:
    # - id: UUID (database user ID)
    # - auth0_sub: Auth0 user ID
    # - email: User's email
    # - role: User's role
    # - permissions: List of permissions
    
    user_id = current_user["id"]
    # ... save document with user_id
```

### 3. Database User Isolation

```python
# Get only current user's documents
@router.get("/users/me/documents")
async def get_my_documents(
    user_context: UserContext = Depends(UserContext)
):
    # UserContext automatically filters by current user
    documents = await user_context.get_documents()
    return documents
```

## 📋 Implementation Checklist

### ✅ Already Implemented

- [x] Auth0 JWT validation with JWKS
- [x] User auto-creation on first login
- [x] Token verification with RS256 algorithm
- [x] User profile endpoints (`/api/v1/users/me`)
- [x] User stats endpoint (`/api/v1/users/me/stats`)
- [x] Protected document upload
- [x] Protected Q&A endpoints
- [x] UserContext for database operations
- [x] Audit logging with user_id

### 🔄 Migration Required

Run this migration to add user_id columns:

```bash
# PowerShell
docker exec -i docqa-postgres psql -U user -d docqa_db < backend/database/migrations/002_add_user_ownership.sql
```

### 📝 Update Your Code

After running the migration, update these endpoints to save user_id:

#### Documents Upload

```python
# backend/api_gateway/app/api/v1/endpoints/documents.py

@router.post("/upload")
async def upload_document(
    file: UploadFile,
    current_user: Dict = Depends(get_or_create_user),
    db = Depends(get_db_connection)
):
    # Save document with user_id
    insert_query = """
        INSERT INTO documents (
            id, filename, file_type, content, file_size,
            user_id, metadata  -- ← ADD user_id
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7)
    """
    await db.execute(
        insert_query,
        document_id,
        filename,
        file_type,
        content,
        file_size,
        UUID(current_user["id"]),  # ← Pass user_id
        metadata
    )
```

#### Q&A Interaction

```python
# backend/api_gateway/app/api/v1/endpoints/qa.py

# Save QA interaction with user_id
insert_query = """
    INSERT INTO qa_interactions (
        id, question, answer, document_ids, model_used,
        confidence_score, user_id, created_at  -- ← ADD user_id
    )
    VALUES ($1, $2, $3, $4, $5, $6, $7, NOW())
"""
await db.execute(
    insert_query,
    interaction_id,
    question,
    answer,
    document_ids,
    model_used,
    confidence_score,
    UUID(current_user["id"])  # ← Pass user_id
)
```

## 🔐 Security Features

### JWT Token Validation

- **Algorithm**: RS256 (RSA + SHA-256)
- **JWKS**: Public keys fetched from Auth0
- **Validation**: Signature, expiration, audience, issuer
- **Caching**: JWKS keys cached for performance

### User Isolation

```python
# Users can only see their own data
@router.get("/users/me/documents")
async def get_my_documents(user_context: UserContext = Depends(UserContext)):
    # Automatically filtered by user_id
    query = """
        SELECT * FROM documents 
        WHERE user_id = $1  -- ← User isolation
        ORDER BY created_at DESC
    """
    return await user_context.db.fetch(query, user_context.user_id)
```

### Role-Based Access Control

```python
from app.core.security import require_role

# Only admins can access this endpoint
@router.get("/admin/users", dependencies=[Depends(require_role("admin"))])
async def list_all_users():
    # Admin-only endpoint
    pass
```

### Permission-Based Access

```python
from app.core.security import require_permission

# Require specific permission
@router.delete("/documents/{doc_id}", dependencies=[Depends(require_permission("delete:documents"))])
async def delete_document(doc_id: str):
    # Only users with "delete:documents" permission can access
    pass
```

## 📊 Available Endpoints

### User Profile

```bash
# Get current user profile
GET /api/v1/users/me
Authorization: Bearer <jwt_token>

# Response:
{
  "id": "uuid",
  "auth0_sub": "auth0|123456",
  "email": "user@example.com",
  "name": "MOhamed Lahbari",
  "role": "clinician",
  "permissions": [],
  "is_active": true,
  "created_at": "2025-11-24T..."
}
```

### User Stats

```bash
# Get user statistics
GET /api/v1/users/me/stats
Authorization: Bearer <jwt_token>

# Response:
{
  "user_id": "uuid",
  "email": "user@example.com",
  "role": "clinician",
  "stats": {
    "documents_uploaded": 15,
    "questions_asked": 47,
    "actions_logged": 120
  }
}
```

### User Documents

```bash
# Get user's documents
GET /api/v1/users/me/documents?limit=50&offset=0
Authorization: Bearer <jwt_token>

# Response:
{
  "documents": [...],
  "count": 15,
  "limit": 50,
  "offset": 0
}
```

### User Q&A History

```bash
# Get user's Q&A history
GET /api/v1/users/me/qa-history?limit=50&offset=0
Authorization: Bearer <jwt_token>

# Response:
{
  "history": [...],
  "count": 47,
  "limit": 50,
  "offset": 0
}
```

## 🧪 Testing JWT Authentication

### 1. Get Access Token (Frontend)

```javascript
import { useAuth0 } from '@auth0/auth0-react';

function MyComponent() {
  const { getAccessTokenSilently } = useAuth0();
  
  const callAPI = async () => {
    try {
      const token = await getAccessTokenSilently();
      
      const response = await fetch('http://localhost:8000/api/v1/users/me', {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      const data = await response.json();
      console.log('User profile:', data);
    } catch (error) {
      console.error('Error:', error);
    }
  };
  
  return <button onClick={callAPI}>Get Profile</button>;
}
```

### 2. Test with cURL

```bash
# First, get your JWT token from the browser (F12 → Application → Local Storage)
TOKEN="your-jwt-token-here"

# Test user profile
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:8000/api/v1/users/me

# Test user stats
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:8000/api/v1/users/me/stats

# Test document upload
curl -X POST \
     -H "Authorization: Bearer $TOKEN" \
     -F "file=@test.pdf" \
     http://localhost:8000/api/v1/documents/upload
```

### 3. Test with Postman

1. Set **Authorization Type**: Bearer Token
2. Paste your JWT token
3. Send requests to protected endpoints

## 🚨 Error Handling

### 401 Unauthorized

```json
{
  "detail": "Could not validate credentials"
}
```

**Causes:**
- Missing Authorization header
- Invalid token
- Expired token
- Wrong audience/issuer

**Solution:** Get a fresh token with `getAccessTokenSilently()`

### 403 Forbidden

```json
{
  "detail": "Permission denied. Required: delete:documents"
}
```

**Causes:**
- User doesn't have required permission
- User doesn't have required role

**Solution:** Request admin to grant permission

## 🔧 Configuration

### Backend (.env)

```env
# Auth0 Configuration
AUTH0_DOMAIN=dev-rwicnayrjuhx63km.us.auth0.com
AUTH0_AUDIENCE=https://api.interfaceclinique.com
```

### Frontend (.env)

```env
VITE_AUTH0_DOMAIN=dev-rwicnayrjuhx63km.us.auth0.com
VITE_AUTH0_CLIENT_ID=your-client-id
VITE_AUTH0_AUDIENCE=https://api.interfaceclinique.com
```

## 📚 Next Steps

1. **Run the migration** to add user_id columns
2. **Update document upload** to save user_id
3. **Update Q&A endpoints** to save user_id
4. **Test user isolation** - create 2 users and verify they can't see each other's data
5. **Add role management** in Auth0 dashboard
6. **Configure permissions** for fine-grained access control

## 🎓 Learn More

- [Auth0 JWT Documentation](https://auth0.com/docs/secure/tokens/json-web-tokens)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [JWT.io](https://jwt.io) - Decode and inspect JWT tokens

---

**🎉 Your app is now fully secured with JWT authentication!**

Users can:
- ✅ Login with Auth0 (Google, email, etc.)
- ✅ Access only their own documents
- ✅ View their own Q&A history
- ✅ Get personalized statistics
- ✅ Have role-based permissions
