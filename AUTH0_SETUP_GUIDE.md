# Auth0 Integration Setup Guide for InterfaceClinique

## Overview
This guide will help you configure Auth0 authentication for the InterfaceClinique application and set up the database for user management.

## ✅ What Has Been Configured

### 1. Frontend (InterfaceClinique)
- ✅ Auth0 React SDK installed (`@auth0/auth0-react`)
- ✅ Auth0Provider configured in `src/main.tsx`
- ✅ Login page with Auth0 integration (`src/pages/Login.tsx`)
- ✅ Environment variables configured (`.env`)
- ✅ Auth0 setup guide component for first-time setup

### 2. Backend (API Gateway)
- ✅ Auth0 JWT verification endpoint (`/api/v1/auth/me`)
- ✅ User creation/sync with database on first login
- ✅ Protected route dependency (`get_current_user`)
- ✅ Audit logging for authentication events

### 3. Database
- ✅ Users table created in schema
- ✅ Migration script for existing databases
- ✅ Foreign key relationships updated
- ✅ Default test users created

---

## 🚀 Step-by-Step Setup

### Step 1: Configure Auth0 Account

#### 1.1 Your Current Auth0 Configuration
```
Domain: dev-rwicnayrjuhx63km.us.auth0.com
Client ID: AIBzK6asmE87FiBVaYFaCNOBFiX4w9XX
```

#### 1.2 Configure Auth0 Application Settings
1. Go to [Auth0 Dashboard](https://manage.auth0.com)
2. Navigate to **Applications** → **Applications**
3. Select your application
4. Configure the following settings:

**Allowed Callback URLs:**
```
http://localhost:5173,
http://localhost:5173/callback,
http://localhost:3000,
http://localhost:3000/callback
```

**Allowed Logout URLs:**
```
http://localhost:5173,
http://localhost:3000
```

**Allowed Web Origins:**
```
http://localhost:5173,
http://localhost:3000
```

**Allowed Origins (CORS):**
```
http://localhost:5173,
http://localhost:3000,
http://localhost:8000
```

#### 1.3 Create Auth0 API (Optional but Recommended)
1. Go to **Applications** → **APIs**
2. Click **+ Create API**
3. Name: `InterfaceClinique API`
4. Identifier: `https://api.interfaceclinique.com`
5. Signing Algorithm: RS256

---

### Step 2: Configure Environment Variables

#### 2.1 Frontend Environment (InterfaceClinique/.env)
Your `.env` file has been updated:
```bash
# Auth0 Configuration (Development)
VITE_AUTH0_DOMAIN=dev-rwicnayrjuhx63km.us.auth0.com
VITE_AUTH0_CLIENT_ID=AIBzK6asmE87FiBVaYFaCNOBFiX4w9XX
VITE_AUTH0_AUDIENCE=https://api.interfaceclinique.com
```

#### 2.2 Backend Environment (backend/api_gateway/.env)
Create a `.env` file in `backend/api_gateway/` with:
```bash
# Auth0 Configuration
AUTH0_DOMAIN=dev-rwicnayrjuhx63km.us.auth0.com
AUTH0_CLIENT_ID=AIBzK6asmE87FiBVaYFaCNOBFiX4w9XX
AUTH0_AUDIENCE=https://api.interfaceclinique.com
FRONTEND_URL=http://localhost:5173

# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=docqa_ms
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# API Configuration
DEBUG=True
API_V1_STR=/api/v1
```

---

### Step 3: Setup Database

#### 3.1 If Starting Fresh (New Database)
```powershell
# Navigate to backend directory
cd c:\docqa-ms\backend\database

# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE docqa_ms;

# Connect to the database
\c docqa_ms

# Run the schema
\i schema.sql

# Verify tables were created
\dt
```

#### 3.2 If Updating Existing Database
```powershell
# Navigate to migrations directory
cd c:\docqa-ms\backend\database\migrations

# Connect to your database
psql -U postgres -d docqa_ms

# Run the migration
\i 002_add_users_table.sql

# Verify the users table
\d users
```

#### 3.3 Verify Database Setup
```sql
-- Check if users table exists
SELECT * FROM users;

-- Check if test users were created
SELECT email, role, is_active FROM users;
```

You should see:
- admin@interfaceclinique.com (admin role)
- clinician@interfaceclinique.com (clinician role)
- legacy@interfaceclinique.com (for migrated records)

---

### Step 4: Install Backend Dependencies

```powershell
cd c:\docqa-ms\backend\api_gateway

# Create virtual environment (if not already created)
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

---

### Step 5: Start the Services

#### 5.1 Start Backend API Gateway
```powershell
cd c:\docqa-ms\backend\api_gateway
.\venv\Scripts\Activate.ps1
python -m app.main
```

The API should start on `http://localhost:8000`

#### 5.2 Start Frontend
```powershell
cd c:\docqa-ms\InterfaceClinique
npm run dev
```

The app should start on `http://localhost:5173`

---

### Step 6: Test Authentication

#### 6.1 Test Login Flow
1. Open `http://localhost:5173` in your browser
2. You should see the login page
3. Click **"Se connecter avec Auth0"**
4. You'll be redirected to Auth0 login
5. Sign up or log in with your credentials
6. After authentication, you'll be redirected back to the dashboard

#### 6.2 Verify User Was Created
```sql
-- Connect to database
psql -U postgres -d docqa_ms

-- Check if your user was created
SELECT auth0_sub, email, name, role, last_login 
FROM users 
ORDER BY created_at DESC 
LIMIT 5;
```

#### 6.3 Test API Endpoints
```powershell
# Get Auth0 access token from browser (Developer Tools → Application → Local Storage)
$token = "YOUR_ACCESS_TOKEN_HERE"

# Test the /me endpoint
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/me" `
  -Method Get `
  -Headers @{Authorization="Bearer $token"}

# Test the verify endpoint
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/verify" `
  -Method Post `
  -Headers @{Authorization="Bearer $token"}
```

---

## 🔍 Troubleshooting

### Issue 1: "Unable to find appropriate key"
**Solution:** Check that your Auth0 domain is correct in both frontend and backend .env files.

### Issue 2: "Invalid token claims"
**Solution:** Make sure the AUDIENCE setting matches in both:
- Frontend `.env`: `VITE_AUTH0_AUDIENCE`
- Backend `.env`: `AUTH0_AUDIENCE`
- Auth0 API identifier in dashboard

### Issue 3: Database Connection Failed
**Solution:**
```powershell
# Check if PostgreSQL is running
Get-Service -Name postgresql*

# Start PostgreSQL if not running
Start-Service -Name postgresql-x64-14  # Adjust version as needed

# Test connection
psql -U postgres -d docqa_ms -c "SELECT 1;"
```

### Issue 4: CORS Errors
**Solution:** Add your frontend URL to:
1. Auth0 Dashboard → Application Settings → Allowed Origins (CORS)
2. Backend config.py → BACKEND_CORS_ORIGINS

### Issue 5: Users Table Doesn't Exist
**Solution:** Run the migration script:
```powershell
cd c:\docqa-ms\backend\database\migrations
psql -U postgres -d docqa_ms -f 002_add_users_table.sql
```

---

## 📊 Database Schema

### Users Table Structure
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    auth0_sub VARCHAR(255) UNIQUE NOT NULL,  -- Auth0 user ID
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    nickname VARCHAR(100),
    picture VARCHAR(500),
    role VARCHAR(50) DEFAULT 'clinician',
    permissions JSONB DEFAULT '[]'::jsonb,
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP WITH TIME ZONE,
    email_verified BOOLEAN DEFAULT FALSE,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### User Roles
- **admin**: Full access to all features, user management, audit logs
- **clinician**: Standard user, can upload documents and ask questions
- **researcher**: Read-only access to documents and Q&A

### User Permissions
- `read_documents`: View documents
- `upload_documents`: Upload new documents
- `ask_questions`: Interact with Q&A system
- `manage_users`: Create/edit/delete users (admin only)
- `view_audit_logs`: Access audit logs (admin only)

---

## 🔐 Security Best Practices

1. **Never commit `.env` files** - They contain sensitive credentials
2. **Use different Auth0 applications** for development and production
3. **Enable MFA** in Auth0 for production
4. **Regularly rotate secrets** in production
5. **Use HTTPS** in production (Auth0 requires it)
6. **Review Auth0 logs** regularly for suspicious activity

---

## 🎯 Next Steps

### 1. Add Role-Based Access Control (RBAC)
Update protected routes to check user roles:
```python
async def require_role(required_role: str):
    async def role_checker(user: dict = Depends(get_current_user)):
        if user["role"] != required_role and user["role"] != "admin":
            raise HTTPException(403, "Insufficient permissions")
        return user
    return role_checker

# Usage in endpoints
@router.post("/admin-only")
async def admin_endpoint(user: dict = Depends(require_role("admin"))):
    return {"message": "Admin access granted"}
```

### 2. Add User Profile Management
Create endpoints for users to update their profiles:
- Change name/nickname
- Update preferences
- View login history

### 3. Implement Token Refresh
Add logic to refresh Auth0 tokens before they expire.

### 4. Add Social Login
Configure Google, Microsoft, etc. in Auth0 dashboard.

---

## 📚 Additional Resources

- [Auth0 Documentation](https://auth0.com/docs)
- [Auth0 React SDK](https://auth0.com/docs/libraries/auth0-react)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

## ✅ Verification Checklist

- [ ] Auth0 application created and configured
- [ ] Callback URLs and CORS settings configured in Auth0
- [ ] Frontend `.env` file updated with Auth0 credentials
- [ ] Backend `.env` file created with Auth0 and database settings
- [ ] Database created and schema applied
- [ ] Users table created (via schema or migration)
- [ ] Backend dependencies installed
- [ ] Backend API Gateway running on port 8000
- [ ] Frontend running on port 5173
- [ ] Can successfully log in with Auth0
- [ ] User record created in database after login
- [ ] Can access protected API endpoints with token

---

---

## 🎉 CURRENT STATUS (October 28, 2025)

### ✅ What's Already Running:

1. **Backend API**: ✅ Running on http://localhost:8000
   - Health check: http://localhost:8000/health/
   - API docs: http://localhost:8000/docs

2. **Frontend**: ✅ Running on http://localhost:3000
   - Open in browser to test login

3. **Database**: ✅ Running in Docker
   - Users table created with 3 test users
   - Auth0 integration ready

### 🔧 IMMEDIATE ACTION REQUIRED:

**Go to Auth0 Dashboard NOW and add these URLs:**

1. Login to: https://manage.auth0.com
2. Go to: Applications → Applications → InterfaceClinique
3. Add these URLs:

**Allowed Callback URLs:**
```
http://localhost:3000,
http://localhost:3000/callback
```

**Allowed Logout URLs:**
```
http://localhost:3000
```

**Allowed Web Origins:**
```
http://localhost:3000,
http://localhost:8000
```

**Allowed Origins (CORS):**
```
http://localhost:3000,
http://localhost:8000
```

4. Click **Save Changes**

### 🧪 Then Test Login:

1. Go to http://localhost:3000 (already open in your browser)
2. Click "Se connecter avec Auth0"
3. Complete the Auth0 login
4. You should be redirected to the dashboard

### 🔍 Verify User Creation:

After logging in, run this command to see your new user in the database:

```powershell
docker exec docqa-ms-postgres-1 psql -U user -d docqa_db -c "SELECT auth0_sub, email, name, role, last_login FROM users ORDER BY created_at DESC LIMIT 5;"
```

---

**Last Updated:** October 28, 2025
**Status:** ✅ Backend & Frontend Running - Configure Auth0 URLs to Test Login
