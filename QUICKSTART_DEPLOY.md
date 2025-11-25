# 🎓 Student Deployment Quickstart

This guide helps you deploy DocQA-MS for **FREE** as a student!

## ⚡ TL;DR - Quick Deploy (30 minutes)

### 1. Get Free Accounts (5 min)
```bash
# Sign up with your GitHub account:
1. Vercel: https://vercel.com/signup
2. Railway: https://railway.app/login
3. Apply for GitHub Student Pack: https://education.github.com/pack
```

### 2. Fix Build Issues (10 min)
```bash
cd InterfaceClinique
npm install
npm run build  # Fix any TypeScript errors that appear
```

### 3. Deploy Frontend to Vercel (5 min)
```bash
# Install Vercel CLI
npm i -g vercel

# Login and deploy
cd InterfaceClinique
vercel login
vercel  # Follow prompts

# Set environment variables in Vercel dashboard:
# - VITE_AUTH0_DOMAIN
# - VITE_AUTH0_CLIENT_ID  
# - VITE_AUTH0_AUDIENCE
# - VITE_API_BASE_URL (Railway URL - add after step 4)
```

### 4. Deploy Backend to Railway (10 min)
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link to project (creates new project)
railway link

# Deploy
railway up

# Generate domain for API Gateway
# Go to Railway dashboard → API Gateway → Settings → Generate Domain
# Copy the URL and add it to Vercel env as VITE_API_BASE_URL
```

### 5. Update Auth0 URLs
```
Add your Vercel URL to Auth0 dashboard:
- Allowed Callback URLs: https://your-app.vercel.app/callback
- Allowed Logout URLs: https://your-app.vercel.app
- Allowed Web Origins: https://your-app.vercel.app
```

### 6. Test Your Deployment 🎉
```bash
# Open your Vercel URL
open https://your-app.vercel.app

# Test:
1. Login with Auth0 ✓
2. Upload a document ✓
3. Ask a question ✓
4. Check dashboard ✓
```

---

## 💰 Free Tier Limits

### Vercel (100% Free)
- ✅ Unlimited personal projects
- ✅ 100GB bandwidth/month
- ✅ Automatic HTTPS
- ✅ Preview deployments for PRs

### Railway (Free with Student Pack)
- ✅ $5/month credit (enough for hobby project)
- ✅ 512MB PostgreSQL database
- ✅ All services on shared CPU
- ⚠️ Services sleep after 12 hours inactivity
- 💡 Use GitHub Actions keep-alive workflow (included)

### GitHub Actions
- ✅ 2,000 CI/CD minutes/month
- ✅ Unlimited for public repos

---

## 🚨 Common Issues

### "Command failed with exit code 1" on build
**Fix**: Run `npm run build` locally, fix TypeScript errors

### "CORS error" from frontend
**Fix**: Add your Vercel URL to backend CORS config

### "502 Bad Gateway" from Railway
**Fix**: Wait 2-3 minutes for services to start, check Railway logs

### "Auth0 callback error"
**Fix**: Update Auth0 allowed URLs with production domains

### Railway services sleeping
**Fix**: Enable the `keep-alive.yml` workflow (updates URL first!)

---

## 📊 Monitor Your Deployment

### Check Frontend Status
```bash
vercel ls  # List deployments
vercel logs  # View logs
```

### Check Backend Status
```bash
railway status  # Service status
railway logs  # View logs
```

### Check Costs
- Vercel Dashboard: https://vercel.com/dashboard
- Railway Dashboard: https://railway.app/dashboard
  - Shows usage: $X.XX / $5.00 credit

---

## 🔐 Security Checklist

Before going live:
- [ ] All `.env` files in `.gitignore` ✓
- [ ] Secrets configured in Vercel/Railway (not in code) ✓
- [ ] Auth0 URLs updated for production ✓
- [ ] HTTPS enabled (automatic) ✓
- [ ] Security headers active ✓
- [ ] CORS configured for your domains ✓

---

## 🎯 Next Steps

1. **Custom Domain** (Optional)
   - Add custom domain in Vercel settings
   - Update Auth0 URLs accordingly

2. **Enable Analytics**
   - Vercel Analytics (free)
   - Railway metrics dashboard

3. **Set Up Alerts**
   - Railway: Settings → Notifications
   - Vercel: Settings → Notifications

4. **Database Backups**
   - Railway auto-backs up PostgreSQL
   - Download backups: Railway dashboard → Database → Backups

---

## 📚 Need Help?

- **Full Guide**: See `DEPLOYMENT_PLAN.md`
- **Vercel Docs**: https://vercel.com/docs
- **Railway Docs**: https://docs.railway.app
- **Railway Discord**: https://discord.gg/railway
- **GitHub Student Pack**: https://education.github.com/pack

---

## ✅ Success Checklist

After deployment:
- [ ] Frontend loads at Vercel URL
- [ ] Can login with Auth0
- [ ] Can upload documents
- [ ] Can ask questions and get answers
- [ ] Dashboard shows real data
- [ ] No errors in browser console
- [ ] No errors in Railway logs
- [ ] GitHub Actions workflows passing

**You're live! 🚀 Share your project!**

---

**Estimated Total Time**: 30-45 minutes  
**Total Cost**: $0/month (with student accounts)  
**Difficulty**: ⭐⭐⚪⚪⚪ (Easy-Medium)
