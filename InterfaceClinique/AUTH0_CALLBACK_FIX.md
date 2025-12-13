# Fix Auth0 Callback URL Mismatch

## Error:
```
Callback URL mismatch.
The provided redirect_uri is not in the list of allowed callback URLs.
```

## Solution:

### Step 1: Go to Auth0 Dashboard
1. Open: https://manage.auth0.com/
2. Login with your Auth0 account

### Step 2: Navigate to Your Application
1. Go to **Applications** → **Applications**
2. Click on your application: **InterfaceClinique** (Client ID: `AIBzK6asmE87FiBVaYFaCNOBFiX4w9XX`)

### Step 3: Add Allowed Callback URLs
In the **Application URIs** section, add these URLs:

**Allowed Callback URLs:**
```
http://localhost:3000,
http://localhost:3000/callback,
https://your-production-domain.com,
https://your-production-domain.com/callback
```

**Allowed Logout URLs:**
```
http://localhost:3000,
https://your-production-domain.com
```

**Allowed Web Origins:**
```
http://localhost:3000,
https://your-production-domain.com
```

**Allowed Origins (CORS):**
```
http://localhost:3000,
https://your-production-domain.com
```

### Step 4: Save Changes
Click **Save Changes** at the bottom of the page.

### Step 5: Test
1. Refresh your application: `http://localhost:3000`
2. Click "Continuer avec Google"
3. Should work now! ✅

## Google Connection Setup (If Not Already Done)

### Enable Google Social Connection:
1. In Auth0 Dashboard, go to **Authentication** → **Social**
2. Click **+ Create Connection**
3. Select **Google**
4. Enable the connection
5. Add your application to the connection
6. Save

## Notes:
- Make sure your frontend is running on `http://localhost:3000`
- If using a different port, update the callback URLs accordingly
- For production, replace `localhost:3000` with your actual domain

## Current Configuration:
- **Auth0 Domain**: `dev-rwicnayrjuhx63km.us.auth0.com`
- **Client ID**: `AIBzK6asmE87FiBVaYFaCNOBFiX4w9XX`
- **Audience**: `https://api.interfaceclinique.com`
