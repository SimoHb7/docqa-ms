# GitHub Secrets Setup Guide

This guide shows you how to add the required secrets to your GitHub repository for CI/CD deployment.

## 📝 Required Secrets

You need to add these secrets to deploy automatically via GitHub Actions:

### For Vercel (Frontend)
1. `VERCEL_TOKEN` - Your Vercel authentication token
2. `VERCEL_ORG_ID` - Your Vercel organization ID
3. `VERCEL_PROJECT_ID` - Your Vercel project ID

### For Railway (Backend)
4. `RAILWAY_TOKEN` - Your Railway authentication token

### For Application
5. `VITE_AUTH0_DOMAIN` - Your Auth0 domain (e.g., `your-domain.auth0.com`)
6. `VITE_AUTH0_CLIENT_ID` - Your Auth0 client ID
7. `VITE_AUTH0_AUDIENCE` - Your Auth0 API audience (e.g., `https://docqa-api`)
8. `VITE_API_BASE_URL` - Your Railway backend URL (e.g., `https://your-app.up.railway.app`)

---

## 🔑 How to Get Each Secret

### 1. VERCEL_TOKEN

**Steps:**
1. Go to https://vercel.com/account/tokens
2. Click "Create Token"
3. Name it "GitHub Actions" or similar
4. Set scope to your account
5. Click "Create"
6. **Copy the token immediately** (you won't see it again!)

### 2. VERCEL_ORG_ID & VERCEL_PROJECT_ID

**Method 1: From Vercel Dashboard**
1. Go to https://vercel.com/dashboard
2. Select your project
3. Go to Settings → General
4. Scroll to "Project ID" - copy this value
5. For Org ID, click on your profile → Settings → General → "Your ID"

**Method 2: Using Vercel CLI**
```bash
cd InterfaceClinique
vercel link  # Link your project
cat .vercel/project.json
```

You'll see:
```json
{
  "projectId": "prj_xxxxxxxxxxxxx",  ← VERCEL_PROJECT_ID
  "orgId": "team_xxxxxxxxxxxxx"      ← VERCEL_ORG_ID
}
```

### 3. RAILWAY_TOKEN

**Steps:**
1. Go to https://railway.app/account/tokens
2. Click "Create New Token"
3. Name it "GitHub Actions"
4. Click "Create Token"
5. **Copy the token immediately**

### 4-7. Auth0 Variables

**Get from Auth0 Dashboard:**
1. Go to https://manage.auth0.com/dashboard
2. Applications → Your Application → Settings
3. Find:
   - **Domain** → `VITE_AUTH0_DOMAIN`
   - **Client ID** → `VITE_AUTH0_CLIENT_ID`
4. APIs → Your API → Settings
   - **Identifier** → `VITE_AUTH0_AUDIENCE`

### 8. VITE_API_BASE_URL

**Get from Railway:**
1. Deploy backend to Railway first (see QUICKSTART_DEPLOY.md)
2. Go to Railway dashboard
3. Select "api-gateway" service
4. Go to Settings → Networking → "Generate Domain"
5. Copy the generated URL (e.g., `https://your-app.up.railway.app`)

---

## 📋 Adding Secrets to GitHub

### Step-by-Step:

1. **Go to your GitHub repository**
   - Navigate to https://github.com/YOUR_USERNAME/docqa-ms

2. **Open Settings**
   - Click "Settings" tab (top right)

3. **Navigate to Secrets**
   - Left sidebar → "Secrets and variables" → "Actions"

4. **Add each secret:**
   - Click "New repository secret"
   - Name: `VERCEL_TOKEN`
   - Value: `[paste your token]`
   - Click "Add secret"
   - Repeat for all 8 secrets

---

## ✅ Verification Checklist

After adding all secrets, verify:

```bash
# You should have these 8 secrets:
□ VERCEL_TOKEN
□ VERCEL_ORG_ID
□ VERCEL_PROJECT_ID
□ RAILWAY_TOKEN
□ VITE_AUTH0_DOMAIN
□ VITE_AUTH0_CLIENT_ID
□ VITE_AUTH0_AUDIENCE
□ VITE_API_BASE_URL
```

---

## 🧪 Test GitHub Actions

After adding secrets:

```bash
# Push a change to trigger deployment
git add .
git commit -m "test: trigger deployment"
git push origin main
```

Then:
1. Go to GitHub → Actions tab
2. You should see workflows running
3. Check logs for any errors

---

## 🔒 Security Notes

- ✅ Never commit secrets to your repository
- ✅ Secrets are encrypted by GitHub
- ✅ Secrets are only visible to you and GitHub Actions
- ✅ Rotate tokens periodically for security
- ⚠️ If you accidentally commit a secret, **revoke it immediately**

---

## 🚨 Troubleshooting

### "Error: Invalid token" in GitHub Actions
**Fix**: Re-create the token and update the secret

### "Error: Project not found"
**Fix**: Verify VERCEL_PROJECT_ID and VERCEL_ORG_ID are correct

### Workflow not triggering
**Fix**: Check that secrets are named exactly as shown (case-sensitive)

### "Unauthorized" error
**Fix**: Make sure tokens have correct permissions:
- Vercel: Full access to your account
- Railway: Full access to your projects

---

## 📚 Additional Resources

- GitHub Secrets Docs: https://docs.github.com/en/actions/security-guides/encrypted-secrets
- Vercel CI/CD: https://vercel.com/docs/concepts/git
- Railway CI/CD: https://docs.railway.app/deploy/github-actions

---

**Next Step**: After adding all secrets, push to `main` branch to trigger automatic deployment! 🚀
