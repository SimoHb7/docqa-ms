# ✅ Pre-Test Checklist

## Before Running the End-to-End Test

### 1. Prerequisites ✓
- [ ] Docker Desktop is running
- [ ] At least 8GB RAM allocated to Docker
- [ ] At least 10GB free disk space
- [ ] Ports 8000-8006, 5432, 5672 are available
- [ ] PowerShell 5.1 or higher

### 2. Services Status ✓
```powershell
# Check if services are running
docker-compose ps
```

Expected output: All services should show "Up (healthy)"
- [ ] postgres
- [ ] rabbitmq
- [ ] api-gateway
- [ ] doc-ingestor
- [ ] deid
- [ ] indexer-semantique
- [ ] llm-qa

### 3. Rebuild API Gateway ✓
```powershell
# Rebuild to include new database code
docker-compose up -d --build api-gateway
```

Wait for completion (1-2 minutes)
- [ ] Build successful
- [ ] Service restarted
- [ ] No errors in logs

### 4. Verify Health Endpoints ✓
```powershell
# Test each service health
curl http://localhost:8000/health  # API Gateway
curl http://localhost:8001/health  # Doc Ingestor
curl http://localhost:8002/health  # De-ID
curl http://localhost:8003/health  # Semantic Indexer
curl http://localhost:8004/health  # LLM Q&A
```

- [ ] All return status: "healthy"
- [ ] No connection errors
- [ ] Response time < 2 seconds each

### 5. Database Check ✓
```powershell
# Verify database is accessible
docker-compose exec postgres psql -U user -d docqa_db -c "\dt"
```

- [ ] Tables listed (documents, document_chunks, qa_interactions, audit_logs)
- [ ] No connection errors

### 6. Check Logs for Errors ✓
```powershell
# Check recent logs for any errors
docker-compose logs --tail=50 api-gateway
docker-compose logs --tail=50 deid
docker-compose logs --tail=50 indexer-semantique
```

- [ ] No critical errors
- [ ] Services initialized properly
- [ ] Models loaded (for indexer-semantique)

### 7. Network Connectivity ✓
```powershell
# Test inter-service communication
docker-compose exec api-gateway curl http://deid:8002/health
docker-compose exec api-gateway curl http://indexer-semantique:8003/health
```

- [ ] All services reachable from API Gateway
- [ ] No connection refused errors

### 8. Environment Variables ✓
```powershell
# Verify critical environment variables
docker-compose exec llm-qa env | grep GROQ_API_KEY
```

- [ ] GROQ_API_KEY is set (for LLM Q&A)
- [ ] DATABASE_URL is correct
- [ ] RABBITMQ_URL is correct

## Ready to Test! 🚀

If all checkboxes above are checked, proceed with:

```powershell
.\test_e2e_complete.ps1
```

## Troubleshooting Pre-Test Issues

### Issue: Service Not Healthy
```powershell
# View logs
docker-compose logs <service-name>

# Restart service
docker-compose restart <service-name>

# Rebuild if needed
docker-compose up -d --build <service-name>
```

### Issue: Database Connection Failed
```powershell
# Restart postgres
docker-compose restart postgres

# Wait 10 seconds
Start-Sleep -Seconds 10

# Test connection
docker-compose exec postgres psql -U user -d docqa_db -c "SELECT 1"
```

### Issue: Port Already in Use
```powershell
# Find process using port
netstat -ano | findstr :8000

# Kill process (replace <PID>)
taskkill /PID <PID> /F

# Restart service
docker-compose up -d
```

### Issue: Out of Memory
```powershell
# Restart Docker Desktop
# Increase memory limit in settings

# Or restart specific service
docker-compose restart <service-name>
```

### Issue: Model Not Loading (Indexer)
```powershell
# Check logs
docker-compose logs indexer-semantique

# First run takes 2-5 minutes to download model
# Wait for: "Model loaded successfully"

# If stuck, restart
docker-compose restart indexer-semantique
```

## Post-Test Verification

After running `.\test_e2e_complete.ps1`, verify:

- [ ] All 10 steps passed
- [ ] No red error messages
- [ ] Total execution time: 2-3 minutes
- [ ] Final summary shows success

## Common Post-Test Checks

### 1. Verify Document Was Indexed
```powershell
curl http://localhost:8000/api/v1/indexer/stats
```

Expected: `total_vectors` and `total_chunks` should be > 0

### 2. Verify Search Works
```powershell
$json = @'
{
  "query": "hypertension",
  "limit": 5
}
'@
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/search/" -Method POST -Body $json -ContentType "application/json"
```

Expected: `total_results` > 0

### 3. Check Database for Q&A Records
```powershell
docker-compose exec postgres psql -U user -d docqa_db -c "SELECT COUNT(*) FROM qa_interactions;"
```

Expected: Count > 0 (if Q&A steps completed)

### 4. Verify No Orphaned Processes
```powershell
docker ps
```

Expected: Only docqa-ms containers running

## If Test Fails

1. **Read the error message carefully**
   - Note which step failed
   - Check the error details

2. **Check logs of related service**
   ```powershell
   docker-compose logs <service-name>
   ```

3. **Verify service is still healthy**
   ```powershell
   curl http://localhost:<port>/health
   ```

4. **Try restart and rerun**
   ```powershell
   docker-compose restart <service-name>
   Start-Sleep -Seconds 10
   .\test_e2e_complete.ps1
   ```

5. **Full reset if needed** (CAUTION: loses data!)
   ```powershell
   docker-compose down -v
   docker-compose up -d --build
   Start-Sleep -Seconds 60
   .\test_e2e_complete.ps1
   ```

## Success! 🎉

When all tests pass, you have:
- ✅ Working PDF upload and processing
- ✅ PII detection and anonymization
- ✅ Semantic indexing and search
- ✅ LLM-powered Q&A
- ✅ No mock data anywhere
- ✅ Production-ready system!

## Next Steps After Success

1. **Try with your own documents**
   - Upload actual PDFs via Swagger UI
   - Test search with real queries
   - Ask domain-specific questions

2. **Optimize parameters**
   - Adjust search thresholds
   - Tune chunk sizes
   - Configure LLM prompts

3. **Monitor performance**
   - Check response times
   - Monitor resource usage
   - Review log quality

4. **Plan production deployment**
   - Add authentication
   - Set up monitoring
   - Configure backups
   - Enable HTTPS

---

**Ready? Let's go!** 🚀

```powershell
docker-compose up -d --build api-gateway
Start-Sleep -Seconds 30
.\test_e2e_complete.ps1
```
