# Auth0 & Database Configuration Summary

## ✅ What Was Done

### 1. **Auth0 Configuration - FIXED ✓**
- **Frontend (.env)**: Added missing `VITE_AUTH0_AUDIENCE=https://api.interfaceclinique.com`
- **Current Settings**:
  - Domain: `dev-rwicnayrjuhx63km.us.auth0.com`
  - Client ID: `AIBzK6asmE87FiBVaYFaCNOBFiX4w9XX`
  - Audience: `https://api.interfaceclinique.com`

### 2. **Database - Users Table Created ✓**
- **New Table**: `users` with Auth0 integration fields
- **Columns**: id, auth0_sub, email, name, role, permissions, is_active, etc.
- **Foreign Keys Updated**: `qa_interactions` and `audit_logs` now reference users table
- **Migration Script**: `backend/database/migrations/002_add_users_table.sql`

### 3. **Backend Auth Integration ✓**
- **File Updated**: `backend/api_gateway/app/api/v1/endpoints/auth.py`
- **Features Added**:
  - Auth0 JWT token verification using JWKS
  - Automatic user creation on first login
  - User profile sync with Auth0
  - Database integration for user management
  - Audit logging for auth events
  
### 4. **Backend Configuration ✓**
- **File Updated**: `backend/api_gateway/app/core/config.py`
- **Added Settings**:
  - AUTH0_DOMAIN
  - AUTH0_CLIENT_ID  
  - AUTH0_AUDIENCE
  - POSTGRES connection settings

### 5. **Documentation Created ✓**
- **AUTH0_SETUP_GUIDE.md**: Complete step-by-step setup guide
- **setup-database.ps1**: Automated database setup script

---

## 🚀 Quick Start Guide

### Option 1: Automated Setup (Recommended)

```powershell
# Run the database setup script
cd c:\docqa-ms
.\setup-database.ps1
```

This will:
- Check PostgreSQL service
- Create database if needed
- Apply schema/migrations
- Create users table
- Verify setup

### Option 2: Manual Setup

#### Step 1: Setup Database
```powershell
# Connect to PostgreSQL
psql -U postgres

# If database doesn't exist, create it
CREATE DATABASE docqa_ms;

# Connect to database
\c docqa_ms

# Apply migration
\i backend/database/migrations/002_add_users_table.sql
```

#### Step 2: Configure Auth0
1. Go to [Auth0 Dashboard](https://manage.auth0.com)
2. Navigate to your application
3. Add these URLs:
   - **Allowed Callback URLs**: `http://localhost:5173, http://localhost:5173/callback`
   - **Allowed Logout URLs**: `http://localhost:5173`
   - **Allowed Web Origins**: `http://localhost:5173, http://localhost:8000`
   - **Allowed Origins (CORS)**: Same as above

#### Step 3: Configure Backend
Create `backend/api_gateway/.env`:
```bash
AUTH0_DOMAIN=dev-rwicnayrjuhx63km.us.auth0.com
AUTH0_CLIENT_ID=AIBzK6asmE87FiBVaYFaCNOBFiX4w9XX
AUTH0_AUDIENCE=https://api.interfaceclinique.com
FRONTEND_URL=http://localhost:5173

POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=docqa_ms
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
```

#### Step 4: Start Services
```powershell
# Terminal 1: Start Backend
cd c:\docqa-ms\backend\api_gateway
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m app.main

# Terminal 2: Start Frontend
cd c:\docqa-ms\InterfaceClinique
npm install  # if not already done
npm run dev
```

#### Step 5: Test Login
1. Open `http://localhost:5173`
2. Click "Se connecter avec Auth0"
3. Login with your credentials
4. You should be redirected to the dashboard

---

## 🔍 Verification

### Check Database
```sql
-- Connect to database
psql -U postgres -d docqa_ms

-- View users table
\d users

-- Check existing users
SELECT email, role, is_active, created_at FROM users;
```

### Check Auth0 Connection
```powershell
# Test Auth0 JWKS endpoint
Invoke-RestMethod -Uri "https://dev-rwicnayrjuhx63km.us.auth0.com/.well-known/jwks.json"
```

### Check Backend Auth Endpoint
```powershell
# After logging in, get your token from browser's localStorage
# Then test the /me endpoint
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/me" `
  -Headers @{Authorization="Bearer YOUR_TOKEN_HERE"}
```

---

## 📋 Database Schema Changes

### New Users Table
```sql
users (
  id UUID PRIMARY KEY,
  auth0_sub VARCHAR(255) UNIQUE NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  name VARCHAR(255),
  role VARCHAR(50) DEFAULT 'clinician',
  permissions JSONB,
  is_active BOOLEAN DEFAULT TRUE,
  last_login TIMESTAMP,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)
```

### Updated Tables
- `qa_interactions.user_id` → Now references `users.id` (UUID)
- `audit_logs.user_id` → Now references `users.id` (UUID)

---

## 🎯 User Roles & Permissions

### Default Roles
- **admin**: Full system access
- **clinician**: Standard user (default)
- **researcher**: Read-only access

### Default Permissions
```json
{
  "clinician": [
    "read_documents",
    "upload_documents", 
    "ask_questions"
  ],
  "admin": [
    "read_documents",
    "upload_documents",
    "ask_questions",
    "manage_users",
    "view_audit_logs"
  ]
}
```

---

## 🛠️ Troubleshooting

### Problem: "Database service unavailable"
**Solution**: 
```powershell
# Check PostgreSQL is running
Get-Service -Name postgresql*
Start-Service -Name postgresql-x64-14  # Adjust version
```

### Problem: "Invalid token claims"
**Solution**: Ensure AUDIENCE matches in:
- Frontend .env: `VITE_AUTH0_AUDIENCE`
- Backend config: `AUTH0_AUDIENCE`
- Auth0 API identifier

### Problem: CORS errors
**Solution**: Add URLs to Auth0 dashboard CORS settings

### Problem: Users table doesn't exist
**Solution**: 
```powershell
cd c:\docqa-ms
.\setup-database.ps1
```

---

## 📚 Files Modified/Created

### Modified
- ✅ `InterfaceClinique/.env`
- ✅ `backend/database/schema.sql`
- ✅ `backend/api_gateway/app/api/v1/endpoints/auth.py`
- ✅ `backend/api_gateway/app/core/config.py`

### Created
- ✅ `backend/database/migrations/002_add_users_table.sql`
- ✅ `AUTH0_SETUP_GUIDE.md`
- ✅ `setup-database.ps1`
- ✅ `AUTH0_CONFIGURATION_SUMMARY.md` (this file)

---

## ✨ Next Steps

1. **Run Database Setup**: `.\setup-database.ps1`
2. **Configure Auth0 URLs** in Auth0 Dashboard
3. **Create Backend .env** file with Auth0 credentials
4. **Start Both Services** (Backend & Frontend)
5. **Test Login** at http://localhost:5173

For detailed instructions, see **AUTH0_SETUP_GUIDE.md**

---

**Status**: ✅ Configuration Complete  
**Date**: January 28, 2025  
**Ready for Testing**: Yes
