# Railway Deployment Configuration

This file helps Railway understand your monorepo structure and deploy multiple services.

## Service Configuration

### 1. PostgreSQL Database
- **Type**: Database
- **Service**: PostgreSQL
- **Version**: 15
- **Storage**: 512MB (free tier)
- **Auto-generates**: `DATABASE_URL`

### 2. RabbitMQ
- **Type**: Database
- **Service**: RabbitMQ
- **Version**: 3
- **Auto-generates**: `RABBITMQ_URL`

### 3. API Gateway
- **Root Directory**: `backend/api_gateway`
- **Build**: Dockerfile
- **Port**: 8000
- **Health Check**: `/health`
- **Environment Variables**:
  ```
  DATABASE_URL=${{Postgres.DATABASE_URL}}
  RABBITMQ_URL=${{RabbitMQ.RABBITMQ_URL}}
  DOC_INGESTOR_URL=http://doc-ingestor.railway.internal:8001
  DEID_URL=http://deid.railway.internal:8002
  INDEXER_SEMANTIQUE_URL=http://indexer-semantique.railway.internal:8003
  LLM_QA_URL=http://llm-qa.railway.internal:8004
  GROQ_API_KEY=<your-key>
  AUTH0_DOMAIN=<your-domain>
  AUTH0_AUDIENCE=<your-audience>
  DEBUG=False
  ```

### 4. Document Ingestor
- **Root Directory**: `backend/doc_ingestor`
- **Build**: Dockerfile
- **Port**: 8001
- **Environment Variables**:
  ```
  DATABASE_URL=${{Postgres.DATABASE_URL}}
  RABBITMQ_URL=${{RabbitMQ.RABBITMQ_URL}}
  ```

### 5. De-identification Service
- **Root Directory**: `backend/deid`
- **Build**: Dockerfile
- **Port**: 8002
- **Environment Variables**:
  ```
  DATABASE_URL=${{Postgres.DATABASE_URL}}
  RABBITMQ_URL=${{RabbitMQ.RABBITMQ_URL}}
  ```

### 6. Semantic Indexer
- **Root Directory**: `backend/indexer_semantique`
- **Build**: Dockerfile
- **Port**: 8003
- **Environment Variables**:
  ```
  DATABASE_URL=${{Postgres.DATABASE_URL}}
  RABBITMQ_URL=${{RabbitMQ.RABBITMQ_URL}}
  TRANSFORMERS_CACHE=/app/model_cache
  HF_HOME=/app/model_cache
  ```
- **Volumes**: Persist model cache

### 7. LLM QA Service
- **Root Directory**: `backend/llm_qa`
- **Build**: Dockerfile
- **Port**: 8004
- **Environment Variables**:
  ```
  DATABASE_URL=${{Postgres.DATABASE_URL}}
  RABBITMQ_URL=${{RabbitMQ.RABBITMQ_URL}}
  GROQ_API_KEY=<your-key>
  ```

## Deployment Steps

### Initial Setup

1. **Create Railway Project**
   ```bash
   railway login
   railway init
   ```

2. **Add PostgreSQL**
   - Dashboard → New → Database → PostgreSQL

3. **Add RabbitMQ**
   - Dashboard → New → Database → RabbitMQ

4. **Deploy Services**
   ```bash
   # Deploy all services
   railway up
   ```

### Configuration

1. **Link Services**
   - Railway automatically creates internal DNS: `service-name.railway.internal`
   - Use these URLs for inter-service communication

2. **Generate Public Domain**
   - Select API Gateway service
   - Settings → Networking → Generate Domain
   - Use this URL as your `VITE_API_BASE_URL`

3. **Set Environment Variables**
   - For each service, go to Settings → Variables
   - Add required environment variables
   - Use `${{ServiceName.VARIABLE}}` syntax to reference other services

### Database Initialization

Railway will automatically run `schema.sql` on first deploy:
- Located: `backend/database/schema.sql`
- Creates all tables and initial data
- Run migrations manually if needed:
  ```bash
  railway run psql $DATABASE_URL -f backend/database/schema.sql
  ```

## Resource Limits (Free Tier)

- **Memory**: 512MB per service
- **CPU**: Shared
- **Storage**: 1GB per service
- **Database**: 512MB PostgreSQL
- **Bandwidth**: Unlimited
- **Build Time**: 10 minutes max

## Optimization Tips

1. **Reduce Services**
   - Combine smaller services if hitting limits
   - Use monorepo deployment

2. **Cache Models**
   - Mount volumes for ML models
   - Reduces cold start time

3. **Use Railway's Internal Network**
   - Services communicate via `.railway.internal`
   - No public URLs needed for internal services

4. **Enable Health Checks**
   - Add `/health` endpoints
   - Railway auto-restarts unhealthy services

5. **Monitor Usage**
   - Dashboard shows resource usage
   - $5 credit should last ~1 month for this project

## Troubleshooting

### Service Won't Start
- Check logs: `railway logs`
- Verify environment variables are set
- Check Dockerfile is valid

### Database Connection Failed
- Verify `DATABASE_URL` is set
- Check database is running
- Try: `railway run psql $DATABASE_URL`

### Out of Memory
- Reduce number of concurrent services
- Optimize Docker images
- Consider Railway Pro ($20/mo)

### Build Timeout
- Optimize Dockerfile
- Use multi-stage builds
- Cache dependencies

## Cost Monitoring

Free tier includes $5/month credit:
- **~$0.01/hour** per service running
- **~$2-3/month** for this project (7 services)
- **$5/month** covers typical student usage

### Cost Reduction Strategies:
1. Stop non-essential services during development
2. Use GitHub Actions keep-alive only for API Gateway
3. Apply for GitHub Student Pack (extends free tier)

## CLI Commands

```bash
# Login
railway login

# Link project
railway link

# Deploy
railway up

# View logs
railway logs

# Run command in Railway environment
railway run [command]

# Open dashboard
railway open

# Check status
railway status

# Environment variables
railway variables
```

## Security

- ✅ All secrets in environment variables
- ✅ No hardcoded credentials
- ✅ Internal network for service communication
- ✅ HTTPS automatic for public domains
- ✅ Regular security updates

## Support

- **Railway Docs**: https://docs.railway.app
- **Discord**: https://discord.gg/railway
- **Status**: https://railway.app/status
- **Pricing**: https://railway.app/pricing
