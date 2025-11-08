# Upload Feature Test Plan

## Pre-Test Checklist

### 1. Backend Services
```bash
# Check all containers running
docker ps

# Expected containers:
# - docqa-ms-api-gateway-1 (port 8000)
# - docqa-ms-postgres-1 (port 5432)
# - docqa-ms-rabbitmq-1 (port 5672)
# - docqa-ms-doc-ingestor-1 (port 8001)
```

### 2. Frontend Dev Server
```bash
# In InterfaceClinique directory
npm run dev

# Expected output:
# VITE v7.x.x ready in xxx ms
# ➜ Local: http://localhost:3000/
```

### 3. Configuration Check
**File**: `.env`
```env
VITE_API_URL=/api
```

**File**: `vite.config.ts`
```typescript
proxy: {
  '^/api/.*': {
    target: 'http://localhost:8000',
    changeOrigin: true,
    rewrite: (path) => path.replace(/^\/api/, '/api/v1'),
  },
}
```

---

## Test Scenarios

### Scenario 1: Single File Upload with Metadata ✅

**Steps**:
1. Open browser: `http://localhost:3000`
2. Navigate to Upload page
3. Click "Browse files" or drag & drop a file
4. Fill in metadata:
   - Patient ID: `TEST_001`
   - Document Type: Select "Medical Report"
5. Click "Upload"

**Expected Results**:
- ✅ Progress bar shows upload progress
- ✅ Success notification appears
- ✅ File appears in upload history
- ✅ Document ID is displayed

**Browser Console Check**:
```
🔧 API Configuration: {mode: 'development', baseURL: '/api', isDev: true}
Making request to: /api/documents/upload
```

**Vite Terminal Check**:
```
[Proxy] /api/documents/upload -> http://localhost:8000/api/v1/documents/upload
```

**Network Tab Check**:
- Request URL: `http://localhost:3000/api/documents/upload`
- Status: `200 OK`
- Response: `{document_id: "...", status: "uploaded"}`

---

### Scenario 2: Bulk Upload with Shared Metadata ✅

**Steps**:
1. Select multiple files (2-3 test files)
2. Click "Set bulk metadata" button
3. In dialog, fill:
   - Patient ID: `TEST_002`
   - Document Type: "Lab Results"
4. Click "Apply to all files"
5. Click "Upload All"

**Expected Results**:
- ✅ All files show same patient ID and document type
- ✅ Progress bar for each file
- ✅ All files upload successfully
- ✅ Success count matches file count

---

### Scenario 3: File Without Metadata (Error Case) ❌

**Steps**:
1. Select a file
2. Leave Patient ID empty
3. Try to upload

**Expected Results**:
- ❌ Upload button disabled OR
- ❌ Validation error appears
- ⚠️ File not uploaded

---

### Scenario 4: Large File Upload ⏱️

**Steps**:
1. Upload file > 10MB
2. Watch progress bar

**Expected Results**:
- ✅ Progress updates during upload
- ✅ Upload completes
- ⏱️ Timeout doesn't occur (30s configured)

---

## Debugging Guide

### Issue: 404 Error on Upload

**Symptom**: 
```
POST http://localhost:3000/api/documents/upload 404 (Not Found)
```

**Diagnosis**:
1. Check Vite terminal - no `[Proxy]` logs? → Proxy not working
2. Check backend - `docker ps` shows api-gateway stopped? → Backend down
3. Check URL - request to `localhost:8000` directly? → Wrong baseURL

**Solutions**:

**A. Proxy Not Intercepting**
```bash
# Stop dev server (Ctrl+C)
# Check vite.config.ts has proxy configuration
# Restart
npm run dev
```

**B. Backend Not Running**
```bash
docker compose up -d
# Wait 10 seconds for services to start
docker ps  # Verify all services "Up"
```

**C. Wrong Environment**
```bash
# Check .env file
cat .env
# Should have: VITE_API_URL=/api
```

---

### Issue: CORS Error

**Symptom**:
```
Access to XMLHttpRequest blocked by CORS policy
```

**This shouldn't happen in development with proxy**, but if it does:

**Check**:
1. Request going directly to `localhost:8000`? → Proxy not working
2. Backend CORS middleware configured? → Check main.py

**Fix**:
```python
# backend/api_gateway/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Development only!
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### Issue: Patient ID Not Saved

**Symptom**: File uploads but patient_id is null in database

**Check**:
1. FormData includes patient_id?
   ```javascript
   formData.append('patient_id', patientId)
   ```
2. Backend receives it?
   ```bash
   docker logs -f docqa-ms-api-gateway-1
   # Should show: patient_id=TEST_001
   ```

**Fix**: Already implemented in Upload.tsx ✅

---

## API Endpoint Verification

### Direct Backend Test (Bypass Frontend)

```bash
# Test upload endpoint directly
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -F "file=@test.txt" \
  -F "patient_id=CURL_TEST" \
  -F "document_type=test_doc"
```

**Expected Response**:
```json
{
  "document_id": "4dd5c28b-9223-4820-b8f0-0bf93080f723",
  "status": "uploaded",
  "patient_id": "CURL_TEST"
}
```

✅ If this works → Backend is fine, issue is frontend/proxy  
❌ If this fails → Backend issue

---

## Success Criteria

### Minimum Viable (MVP) ✅
- [x] Single file upload works
- [x] Patient ID captured
- [x] Document type captured
- [x] Success/error notifications
- [x] No CORS errors

### Enhanced Features ✨
- [x] Bulk upload
- [x] Shared metadata for bulk
- [x] Progress indicators
- [x] Upload history
- [ ] File preview
- [ ] Drag & drop
- [ ] Duplicate file detection

### Production Ready 🚀
- [ ] Error recovery
- [ ] Retry failed uploads
- [ ] File size validation
- [ ] File type validation
- [ ] Upload cancellation
- [ ] Offline support

---

## Test Results Log

**Date**: ___________  
**Tester**: ___________

| Scenario | Status | Notes |
|----------|--------|-------|
| Single Upload | ⬜ PASS ⬜ FAIL | |
| Bulk Upload | ⬜ PASS ⬜ FAIL | |
| Validation | ⬜ PASS ⬜ FAIL | |
| Large File | ⬜ PASS ⬜ FAIL | |

**Screenshots**:
- [ ] Successful upload
- [ ] Error handling
- [ ] Bulk upload dialog

**Console Logs**:
```
(Paste relevant console output here)
```

**Network Activity**:
```
(Paste network requests/responses here)
```

---

## Next Steps After Upload Works

1. **Search Feature**: Connect search API
2. **Q&A Feature**: Connect LLM Q&A API
3. **Dashboard**: Connect analytics API
4. **Document List**: Fetch uploaded documents
5. **De-identification**: Connect de-id API

**Integration Order** (recommended):
```
Upload → Document List → Search → Q&A → Dashboard → De-ID
```

---

**Ready to Test?** Open http://localhost:3000/upload and follow Scenario 1! 🚀
