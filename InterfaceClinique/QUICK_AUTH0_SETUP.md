# 🔐 Quick Auth0 Setup Guide - InterfaceClinique

## 🚀 Step 1: Create Auth0 Account (5 minutes)

1. **Go to Auth0**: https://auth0.com
2. Click **"Sign Up"** (top right)
3. Choose **"Sign up with GitHub"** or email
4. Select region closest to you (e.g., US, EU)
5. Complete account setup

## 📱 Step 2: Create Application (3 minutes)

1. In Auth0 Dashboard, go to **Applications** → **Applications**
2. Click **"+ Create Application"**
3. Enter details:
   - **Name**: `InterfaceClinique`
   - **Type**: Select **"Single Page Web Applications"**
4. Click **"Create"**
5. Select **"React"** as the technology
6. Click **"Continue to Quickstart"** (optional, or skip)

## ⚙️ Step 3: Configure Application Settings (5 minutes)

### In the "Settings" tab of your new application:

1. **Copy these values** (you'll need them later):
   - **Domain** (e.g., `dev-xxxxx.us.auth0.com`)
   - **Client ID** (long alphanumeric string)

2. **Scroll down and add these URLs**:

   **Allowed Callback URLs**:
   ```
   http://localhost:3000
   ```

   **Allowed Logout URLs**:
   ```
   http://localhost:3000
   ```

   **Allowed Web Origins**:
   ```
   http://localhost:3000
   ```

3. **Scroll to bottom** and click **"Save Changes"** ✅

## 🔑 Step 4: Create API (Optional but Recommended) (3 minutes)

1. Go to **Applications** → **APIs**
2. Click **"+ Create API"**
3. Enter:
   - **Name**: `InterfaceClinique API`
   - **Identifier**: `https://api.interfaceclinique.com`
   - **Signing Algorithm**: RS256 (default)
4. Click **"Create"**

## 📝 Step 5: Configure Environment Variables (2 minutes)

1. **Open** `InterfaceClinique/.env` file
2. **Replace** these values with your Auth0 credentials:

```env
# Auth0 Configuration
VITE_AUTH0_DOMAIN=dev-xxxxx.us.auth0.com           # ← YOUR Domain from Step 3
VITE_AUTH0_CLIENT_ID=your-client-id-here           # ← YOUR Client ID from Step 3
VITE_AUTH0_AUDIENCE=https://api.interfaceclinique.com  # ← From Step 4 (or leave as-is)
```

3. **Save** the file

## ✅ Step 6: Test Authentication (2 minutes)

### Start the application:

```powershell
# Terminal 1 - Start Frontend
cd C:\docqa-ms\InterfaceClinique
npm run dev
```

### Test login:

1. Open browser: http://localhost:3000
2. Click **"Se connecter avec Auth0"** button
3. You'll be redirected to Auth0 login page
4. **Sign up** with email or social provider
5. After login, you'll be redirected back to the dashboard

## 🎉 You're Done!

The app is now secured with Auth0 authentication!

---

## 🔧 Troubleshooting

### ❌ "Invalid state" error
**Solution**: Clear browser cache and cookies, restart dev server

### ❌ "Callback URL mismatch" error
**Solution**: Check that you added `http://localhost:5173` to Allowed Callback URLs in Auth0

### ❌ "Unable to verify credentials"
**Solution**: Double-check your `.env` file has correct DOMAIN and CLIENT_ID

### ❌ Login works but API calls fail
**Solution**: Make sure you created the API in Step 4 and set the correct AUDIENCE

---

## 📚 What Happens Next?

✅ Users can **sign up** and **log in** with Auth0  
✅ Protected routes require authentication  
✅ API requests include authentication tokens  
✅ User profile is displayed in the sidebar  
✅ Logout works correctly  

---

## 🔐 Production Deployment (Future)

When deploying to production:

1. Create a **new Auth0 Application** for production
2. Update callback URLs to your production domain
3. Enable **MFA** (Multi-Factor Authentication)
4. Set up **custom domains** for Auth0
5. Configure **Social Connections** (Google, Microsoft, etc.)

---

**Need Help?** Check the full guide: `AUTH0_SETUP_GUIDE.md`

**Auth0 Dashboard**: https://manage.auth0.com
