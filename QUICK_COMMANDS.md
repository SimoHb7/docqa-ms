# 🎯 Quick Command Reference

## 🚀 Start/Stop Services

```powershell
# Start all services
docker-compose up -d

# Start with rebuild (after code changes)
docker-compose up -d --build

# Start specific service
docker-compose up -d api-gateway

# Stop all services
docker-compose down

# Stop and remove volumes (CAUTION: deletes data!)
docker-compose down -v

# Restart a service
docker-compose restart indexer-semantique
```

## 🔍 Monitoring

```powershell
# Check service status
docker-compose ps

# View logs (all services)
docker-compose logs

# View logs (specific service)
docker-compose logs api-gateway
docker-compose logs deid
docker-compose logs indexer-semantique

# Follow logs in real-time
docker-compose logs -f llm-qa

# Check resource usage
docker stats

# Check disk space
docker system df
```

## 🧪 Testing

```powershell
# Run complete end-to-end test
.\test_e2e_complete.ps1

# Test health endpoints
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
curl http://localhost:8004/health

# Test specific service via Swagger
# Open http://localhost:8000/docs in browser
```

## 🗄️ Database

```powershell
# Connect to PostgreSQL
docker-compose exec postgres psql -U user -d docqa_db

# View documents
docker-compose exec postgres psql -U user -d docqa_db -c "SELECT id, filename, processing_status FROM documents;"

# View Q&A interactions
docker-compose exec postgres psql -U user -d docqa_db -c "SELECT COUNT(*) FROM qa_interactions;"

# Backup database
docker-compose exec postgres pg_dump -U user docqa_db > backup.sql

# Restore database
cat backup.sql | docker-compose exec -T postgres psql -U user docqa_db
```

## 🐰 RabbitMQ

```powershell
# Access RabbitMQ management UI
# Open http://localhost:15672
# Username: admin
# Password: admin

# Check queues via CLI
docker-compose exec rabbitmq rabbitmqctl list_queues
```

## 🔧 Debugging

```powershell
# Enter container shell
docker-compose exec api-gateway /bin/bash
docker-compose exec deid /bin/sh

# Check environment variables
docker-compose exec api-gateway env

# Test inter-service communication
docker-compose exec api-gateway curl http://deid:8002/health

# Rebuild single service
docker-compose up -d --no-deps --build api-gateway

# View container details
docker inspect docqa-ms-api-gateway-1
```

## 🧹 Cleanup

```powershell
# Remove stopped containers
docker-compose rm

# Remove unused images
docker image prune

# Remove all unused data (CAUTION!)
docker system prune -a

# Clean Docker cache
docker builder prune
```

## 📊 Swagger UI URLs

- **API Gateway**: http://localhost:8000/docs
- **Doc Ingestor**: http://localhost:8001/docs
- **De-identification**: http://localhost:8002/docs
- **Semantic Indexer**: http://localhost:8003/docs
- **LLM Q&A**: http://localhost:8004/docs

## 🔑 API Testing Examples

### Upload Document
```powershell
$boundary = [System.Guid]::NewGuid().ToString()
# ... (see test_e2e_complete.ps1 for full example)
```

### Search
```powershell
$json = @'
{
  "query": "hypertension traitement",
  "limit": 10,
  "threshold": 0.5
}
'@
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/search/" -Method POST -Body $json -ContentType "application/json"
```

### Ask Question
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/qa/ask?question=Quel+est+le+traitement?" -Method POST
```

### Get Statistics
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/indexer/stats" -Method GET
```

## 🆘 Common Issues

### Services Won't Start
```powershell
docker-compose down
docker-compose up -d --build
```

### Port Already in Use
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process (replace PID)
taskkill /PID <PID> /F
```

### Database Connection Error
```powershell
# Check if postgres is running
docker-compose ps postgres

# Restart postgres
docker-compose restart postgres

# Check logs
docker-compose logs postgres
```

### Out of Disk Space
```powershell
# Clean up Docker
docker system prune -a --volumes

# Check Docker disk usage
docker system df
```

### Memory Issues
```powershell
# Restart Docker Desktop
# Increase memory limit in Docker Desktop settings
# Recommended: 8GB minimum
```

## 📝 Development Workflow

```powershell
# 1. Make code changes
# 2. Rebuild affected service
docker-compose up -d --build <service-name>

# 3. Check logs
docker-compose logs -f <service-name>

# 4. Test changes
.\test_e2e_complete.ps1

# 5. Commit changes
git add .
git commit -m "Your message"
git push
```

## 🎓 Learning Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Docker Compose**: https://docs.docker.com/compose/
- **PostgreSQL**: https://www.postgresql.org/docs/
- **FAISS**: https://github.com/facebookresearch/faiss
- **SpaCy**: https://spacy.io/usage

---

**Keep this file handy for daily development!** 🚀
