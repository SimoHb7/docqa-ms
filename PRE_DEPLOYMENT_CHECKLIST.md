# 🚀 Pre-Deployment Checklist

Complete this checklist before deploying to production.

## ✅ Code Readiness

### Frontend (InterfaceClinique)
- [ ] **Build succeeds without errors**
  ```bash
  cd InterfaceClinique
  npm run build
  ```
  - Fix all TypeScript errors (currently 98 errors)
  - Resolve import issues
  - Fix Grid component type issues
  - Fix Chart.js type mismatches

- [ ] **Linting passes**
  ```bash
  npm run lint
  ```

- [ ] **Environment variables configured**
  - [ ] `.env.example` created ✅
  - [ ] Local `.env.local` not committed to git ✅
  - [ ] All required vars listed in `.env.example`

- [ ] **Tests pass** (if any)
  ```bash
  npm run test
  ```

### Backend (All Services)
- [ ] **All services have Dockerfiles** ✅
- [ ] **docker-compose.yml valid** ✅
- [ ] **Database schema up to date** ✅
- [ ] **No hardcoded secrets in code** ✅
- [ ] **Health check endpoints added**
  - [ ] API Gateway: `/health`
  - [ ] Other services: `/health`

---

## 🔐 Security Checklist

- [ ] **Secrets Management**
  - [ ] All `.env` files in `.gitignore` ✅
  - [ ] No API keys in code ✅
  - [ ] No passwords in code ✅
  - [ ] Auth0 credentials in environment variables ✅

- [ ] **Authentication & Authorization**
  - [ ] Auth0 configured correctly ✅
  - [ ] JWT validation working ✅
  - [ ] User isolation by user_id ✅

- [ ] **Security Headers**
  - [ ] CSP configured ✅
  - [ ] HSTS enabled (production) ✅
  - [ ] X-Frame-Options: DENY ✅
  - [ ] X-Content-Type-Options: nosniff ✅
  - [ ] Referrer-Policy set ✅

- [ ] **CORS Configuration**
  - [ ] Production domains whitelisted
  - [ ] No wildcard `*` in production
  - [ ] Credentials enabled for Auth0

- [ ] **Input Validation**
  - [ ] All user inputs validated ✅
  - [ ] File upload restrictions ✅
  - [ ] SQL injection prevention (parameterized queries) ✅

---

## 🌐 Domain & DNS Setup

- [ ] **Accounts Created**
  - [ ] GitHub account ✅
  - [ ] Vercel account
  - [ ] Railway account
  - [ ] Auth0 account ✅

- [ ] **Student Benefits Applied**
  - [ ] GitHub Student Pack requested
  - [ ] Railway student plan activated

- [ ] **Domain Configuration**
  - [ ] Vercel domain generated (or custom domain)
  - [ ] Railway domain generated for API Gateway
  - [ ] DNS records configured (if custom domain)

---

## 🔑 Auth0 Configuration

- [ ] **Application Settings**
  - [ ] Application Type: Single Page Application
  - [ ] Token Endpoint Authentication: None
  - [ ] OIDC Conformant: Enabled

- [ ] **URLs Updated for Production**
  - [ ] Allowed Callback URLs: `https://your-app.vercel.app/callback`
  - [ ] Allowed Logout URLs: `https://your-app.vercel.app`
  - [ ] Allowed Web Origins: `https://your-app.vercel.app`
  - [ ] Allowed Origins (CORS): `https://your-app.vercel.app`

- [ ] **API Configuration**
  - [ ] API created with identifier (e.g., `https://docqa-api`)
  - [ ] Permissions defined
  - [ ] Scopes configured

- [ ] **Advanced Settings**
  - [ ] Grant Types: Authorization Code, Refresh Token, Implicit
  - [ ] Allow Skipping User Consent: Enabled
  - [ ] Refresh Token Rotation: Enabled
  - [ ] Refresh Token Expiration: 30 days

---

## 🐙 GitHub Setup

- [ ] **Repository Ready**
  - [ ] Code pushed to GitHub
  - [ ] `.gitignore` properly configured ✅
  - [ ] No sensitive data in git history
  - [ ] README.md updated

- [ ] **GitHub Secrets Configured**
  - [ ] `VERCEL_TOKEN`
  - [ ] `VERCEL_ORG_ID`
  - [ ] `VERCEL_PROJECT_ID`
  - [ ] `RAILWAY_TOKEN`
  - [ ] `VITE_AUTH0_DOMAIN`
  - [ ] `VITE_AUTH0_CLIENT_ID`
  - [ ] `VITE_AUTH0_AUDIENCE`
  - [ ] `VITE_API_BASE_URL`

- [ ] **GitHub Actions Workflows**
  - [ ] `deploy-frontend.yml` created ✅
  - [ ] `deploy-backend.yml` created ✅
  - [ ] `keep-alive.yml` created ✅
  - [ ] Workflows tested and passing

---

## ☁️ Vercel Setup (Frontend)

- [ ] **Project Created**
  - [ ] Repository imported
  - [ ] Framework: Vite
  - [ ] Root Directory: `InterfaceClinique`
  - [ ] Build Command: `npm run build`
  - [ ] Output Directory: `dist`

- [ ] **Environment Variables Set**
  - [ ] `VITE_AUTH0_DOMAIN`
  - [ ] `VITE_AUTH0_CLIENT_ID`
  - [ ] `VITE_AUTH0_AUDIENCE`
  - [ ] `VITE_API_BASE_URL` (Railway URL)
  - [ ] `VITE_APP_ENV=production`

- [ ] **Deployment Settings**
  - [ ] Auto-deploy on push to main: Enabled
  - [ ] Preview deployments for PRs: Enabled
  - [ ] `vercel.json` configured ✅

---

## 🚂 Railway Setup (Backend)

- [ ] **Services Created**
  - [ ] PostgreSQL database
  - [ ] RabbitMQ
  - [ ] API Gateway
  - [ ] Document Ingestor
  - [ ] De-identification Service
  - [ ] Semantic Indexer
  - [ ] LLM QA Service

- [ ] **Environment Variables Set**
  For each service:
  - [ ] `DATABASE_URL` (from PostgreSQL service)
  - [ ] `RABBITMQ_URL` (from RabbitMQ service)
  - [ ] `GROQ_API_KEY` (for LLM services)
  - [ ] `AUTH0_DOMAIN`
  - [ ] `AUTH0_AUDIENCE`
  - [ ] Service URLs (internal: `.railway.internal`)

- [ ] **Networking Configured**
  - [ ] Public domain generated for API Gateway
  - [ ] Internal networking enabled
  - [ ] Health checks configured

- [ ] **Database Initialized**
  - [ ] Schema deployed: `backend/database/schema.sql`
  - [ ] Test data seeded (optional)
  - [ ] Migrations run (if any)

---

## 🧪 Testing

### Local Testing
- [ ] **All services start locally**
  ```bash
  docker-compose up
  ```

- [ ] **Frontend connects to backend**
  ```bash
  cd InterfaceClinique
  npm run dev
  ```

- [ ] **End-to-end flow works**
  - [ ] User can login
  - [ ] User can upload document
  - [ ] User can ask question
  - [ ] Dashboard shows data

### Production Testing
- [ ] **Frontend loads**
  - Visit: `https://your-app.vercel.app`
  - No console errors
  - All assets load

- [ ] **API responds**
  ```bash
  curl https://your-app.up.railway.app/health
  ```

- [ ] **Auth0 login works**
  - Can login successfully
  - Can logout successfully
  - Token refresh works
  - No redirect loops

- [ ] **Features work**
  - [ ] Document upload
  - [ ] Document listing
  - [ ] Q&A interaction
  - [ ] Synthesis generation
  - [ ] Dashboard analytics
  - [ ] Empty states display

- [ ] **Performance**
  - [ ] LCP < 2.5s
  - [ ] FID < 100ms
  - [ ] CLS < 0.1
  - [ ] No memory leaks

---

## 📊 Monitoring & Logs

- [ ] **Vercel Monitoring**
  - [ ] Real-time logs enabled
  - [ ] Error tracking active
  - [ ] Analytics configured (optional)

- [ ] **Railway Monitoring**
  - [ ] Service logs accessible
  - [ ] Resource usage monitored
  - [ ] Alert notifications set up

- [ ] **Error Tracking** (Optional)
  - [ ] Sentry configured
  - [ ] Error notifications set up

---

## 📚 Documentation

- [ ] **README.md updated**
  - [ ] Deployment instructions
  - [ ] Environment variables documented
  - [ ] Setup guide for new developers

- [ ] **Deployment Guides Created**
  - [ ] `DEPLOYMENT_PLAN.md` ✅
  - [ ] `QUICKSTART_DEPLOY.md` ✅
  - [ ] `GITHUB_SECRETS_GUIDE.md` ✅
  - [ ] `RAILWAY_CONFIG.md` ✅

- [ ] **API Documentation**
  - [ ] Endpoints documented
  - [ ] Authentication explained
  - [ ] Example requests/responses

---

## 🎯 Post-Deployment

- [ ] **Verify All Functionality**
  - [ ] Login/Logout
  - [ ] Document CRUD operations
  - [ ] Q&A interactions
  - [ ] Dashboard data display
  - [ ] Search functionality
  - [ ] Synthesis generation

- [ ] **Check Logs for Errors**
  - Vercel: No JavaScript errors
  - Railway: No service crashes

- [ ] **Monitor Performance**
  - Initial page load time
  - API response times
  - Database query performance

- [ ] **Security Scan** (Optional)
  - [ ] Run Lighthouse audit
  - [ ] Check security headers: https://securityheaders.com
  - [ ] Test CORS configuration
  - [ ] Verify HTTPS everywhere

---

## 💰 Cost Monitoring

- [ ] **Track Usage**
  - [ ] Railway dashboard shows < $5/month
  - [ ] Vercel shows < 100GB bandwidth
  - [ ] No unexpected charges

- [ ] **Set Up Alerts**
  - [ ] Railway: Alert at 80% of credit
  - [ ] Vercel: Alert at 80% bandwidth

---

## 🚀 Launch!

Once all items checked:

```bash
# Final push to trigger deployment
git add .
git commit -m "chore: ready for production deployment"
git push origin main

# Monitor deployments
# - GitHub Actions: Check workflows
# - Vercel: Check deployment status
# - Railway: Check service health
```

---

## 🎉 Success Criteria

- ✅ Frontend accessible at Vercel URL
- ✅ Backend API responding
- ✅ Database connected
- ✅ Auth0 authentication working
- ✅ All features functional
- ✅ No errors in logs
- ✅ Performance metrics good (LCP < 2.5s)
- ✅ Security headers present
- ✅ HTTPS enabled
- ✅ CI/CD pipeline working

---

**Status**: [ ] Not Started | [ ] In Progress | [ ] Completed ✅

**Deployment Date**: ___________

**Deployed By**: ___________

**Production URLs**:
- Frontend: https://___________.vercel.app
- Backend API: https://___________.up.railway.app
