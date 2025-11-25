# Security Audit & Recommendations
**Date**: November 25, 2025
**Project**: DocQA-MS (InterfaceClinique)

## ✅ Current Security Implementation

### Strong Points
1. **Authentication & Authorization**
   - ✅ Auth0 integration with RS256 JWT
   - ✅ JWKS-based signature verification
   - ✅ All endpoints protected with JWT validation
   - ✅ Automatic token refresh on expiration
   - ✅ User auto-creation on first login

2. **Data Isolation**
   - ✅ Strict user-based filtering (`WHERE user_id = $1`)
   - ✅ No cross-user data access
   - ✅ Database queries use parameterized statements
   - ✅ UUID-based user IDs

3. **SQL Injection Prevention**
   - ✅ Parameterized queries throughout
   - ✅ No string concatenation in SQL
   - ✅ asyncpg library with proper escaping

## ⚠️ Critical Improvements Needed

### 1. Token Storage (CRITICAL - XSS Vulnerability)

**Current Implementation:**
```typescript
// src/hooks/useAuthToken.ts
localStorage.setItem('access_token', token);
```

**Issue**: localStorage is accessible by any JavaScript, making tokens vulnerable to XSS attacks.

**Recommended Solution A - Memory Storage (Best for SPA):**
```typescript
// Create secure token store
class SecureTokenStore {
  private token: string | null = null;
  
  setToken(token: string) {
    this.token = token;
  }
  
  getToken(): string | null {
    return this.token;
  }
  
  clearToken() {
    this.token = null;
  }
}

export const tokenStore = new SecureTokenStore();
```

**Recommended Solution B - httpOnly Cookies (If backend supports):**
```typescript
// Store refresh token in httpOnly cookie (backend sets)
// Store access token in memory only
// This prevents JavaScript access to tokens
```

**Implementation Priority**: HIGH
**Effort**: Medium (2-3 hours)

### 2. Environment Variables Security

**Current Risk**: Auth0 secrets in .env files

**Recommendations:**
```bash
# .env file should NEVER contain:
# - Auth0 Client Secret (backend only, use secrets manager)
# - Database passwords (use AWS Secrets Manager, Azure Key Vault, etc.)

# Frontend .env should only contain public values:
VITE_AUTH0_DOMAIN=dev-rwicnayrjuhx63km.us.auth0.com
VITE_AUTH0_CLIENT_ID=<client_id>
VITE_AUTH0_AUDIENCE=https://api.interfaceclinique.com
VITE_API_URL=http://localhost:8000/api/v1

# Backend should use secrets manager
```

**Add to .gitignore:**
```
.env
.env.local
.env.production
*.key
*.pem
```

### 3. CORS Configuration (HIGH PRIORITY)

**Check Current CORS:**
```python
# backend/api_gateway/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # ✅ Specific origin
    # NOT: allow_origins=["*"]  # ❌ Never use in production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Authorization", "Content-Type"],
)
```

**Action**: Verify CORS is not using wildcard `*`

### 4. Rate Limiting (MEDIUM PRIORITY)

**Add to API Gateway:**
```python
# Install: pip install slowapi
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Apply to sensitive endpoints
@router.post("/documents/upload")
@limiter.limit("10/minute")  # Max 10 uploads per minute
async def upload_document(...):
    ...

@router.post("/qa/ask")
@limiter.limit("30/minute")  # Max 30 questions per minute
async def ask_question(...):
    ...
```

**Implementation Priority**: MEDIUM
**Effort**: Low (1-2 hours)

### 5. Content Security Policy (MEDIUM PRIORITY)

**Add CSP Headers:**
```python
# backend/api_gateway/app/main.py
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self' data:; "
        "connect-src 'self' https://*.auth0.com; "
        "frame-ancestors 'none';"
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
```

### 6. Production Logging (MEDIUM PRIORITY)

**Remove Debug Logs:**
```typescript
// Remove from api.ts interceptor (production only)
console.log('Making request to:', ...);
console.log('Request config:', ...);

// Add environment check
if (import.meta.env.DEV) {
  console.log('Making request to:', ...);
}
```

**Sanitize Backend Logs:**
```python
# Never log tokens or sensitive data
logger.info("User login", user_id=user_id)  # ✅ OK
logger.info("Token:", token)  # ❌ NEVER DO THIS
```

### 7. Input Validation (MEDIUM PRIORITY)

**Add to Backend:**
```python
from pydantic import BaseModel, validator, Field

class DocumentUploadRequest(BaseModel):
    patient_id: str = Field(..., min_length=1, max_length=100)
    document_type: str = Field(..., regex="^[a-zA-Z_]+$")
    
    @validator('patient_id')
    def validate_patient_id(cls, v):
        # Prevent injection attacks
        if any(char in v for char in ['<', '>', '"', "'", ';']):
            raise ValueError('Invalid patient_id format')
        return v
```

### 8. Session Management (LOW PRIORITY)

**Current**: No session timeout beyond token expiration

**Recommendation**: Add idle timeout
```typescript
// Logout after 30 minutes of inactivity
let lastActivity = Date.now();

window.addEventListener('click', () => lastActivity = Date.now());
window.addEventListener('keypress', () => lastActivity = Date.now());

setInterval(() => {
  if (Date.now() - lastActivity > 30 * 60 * 1000) {
    logout();
  }
}, 60000); // Check every minute
```

## 🔐 Production Deployment Checklist

- [ ] Move tokens from localStorage to memory storage
- [ ] Verify CORS origins are restricted (no wildcards)
- [ ] Add rate limiting to all public endpoints
- [ ] Implement CSP headers
- [ ] Remove all console.log statements with sensitive data
- [ ] Use environment-specific logging (debug only in dev)
- [ ] Enable HTTPS only (HSTS headers)
- [ ] Add input validation with Pydantic models
- [ ] Implement session timeout/idle logout
- [ ] Use secrets manager for sensitive config
- [ ] Enable audit logging for all mutations
- [ ] Add monitoring and alerting for auth failures
- [ ] Regular security updates (dependabot)
- [ ] Penetration testing before production

## 📊 Current Security Score: 7.5/10

**Strong**: Authentication, Authorization, SQL Injection Protection, User Isolation
**Needs Work**: Token storage, Rate limiting, CSP headers, Production logging

## Priority Order

1. **Immediate (Before Production)**:
   - Fix token storage (move from localStorage)
   - Verify CORS configuration
   - Remove debug logging

2. **High Priority (Within 1 week)**:
   - Add rate limiting
   - Implement CSP headers
   - Add input validation

3. **Medium Priority (Within 1 month)**:
   - Session timeout
   - Comprehensive audit logging
   - Monitoring and alerting

## Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Auth0 Security Best Practices](https://auth0.com/docs/secure/security-guidance)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
