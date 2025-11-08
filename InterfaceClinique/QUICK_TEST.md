# Quick Test - Upload Feature

## What Changed
✅ **Removed Vite proxy** - Was causing 404 errors  
✅ **Direct backend connection** - Frontend now calls `http://localhost:8000/api/v1` directly  
✅ **CORS already configured** - Backend allows all origins in development  

## Test Now

### 1. Check Dev Server Restarted
The Vite dev server should have automatically restarted when we changed `.env`.

**Look for in terminal:**
```
.env changed, restarting server...
```

### 2. Open Browser Console
1. Open browser at: `http://localhost:3000/upload`
2. Open DevTools (F12)
3. Go to Console tab

**You should see:**
```
🔧 API Configuration: {
  mode: 'development',
  baseURL: 'http://localhost:8000/api/v1',
  isDev: true,
  fullURL: 'http://localhost:8000/api/v1/documents/upload'
}
```

### 3. Upload a Test File

**Steps:**
1. Click "Browse files" or drag & drop any file
2. Fill in metadata:
   - **Patient ID**: `TEST_001`
   - **Document Type**: Select "Medical Report"
3. Click "Upload"

### 4. Check Network Tab
**Expected Request:**
- **URL**: `http://localhost:8000/api/v1/documents/upload`
- **Method**: `POST`
- **Status**: `200 OK`
- **Response**: 
  ```json
  {
    "document_id": "xxx-xxx-xxx",
    "status": "uploaded"
  }
  ```

### 5. If You See CORS Error
**This means backend CORS is working!** The browser is now making cross-origin requests (from localhost:3000 to localhost:8000).

**Backend should have this (already configured):**
```python
allow_origins=["*"]  # Allows all origins
```

**Check backend logs:**
```powershell
docker logs -f docqa-ms-api-gateway-1
```

You should see:
```
Request started | method=POST url=http://localhost:8000/api/v1/documents/upload
```

---

## If It Still Doesn't Work

### Check 1: Backend Running?
```powershell
docker ps
```
All containers should be "Up" and "healthy"

### Check 2: Backend Accessible?
```powershell
$response = Invoke-WebRequest -Uri "http://localhost:8000/health/" -Method GET
$response.Content
```
Should return: `{"status":"healthy",...}`

### Check 3: Dev Server Running?
Terminal should show:
```
VITE v7.x.x  ready in xxx ms
➜  Local:   http://localhost:3000/
```

### Check 4: Console Errors?
Look in browser console for any errors. Copy and share them.

---

## Expected Flow

```
Browser (localhost:3000)
    ↓
    POST http://localhost:8000/api/v1/documents/upload
    ↓
API Gateway (validates, saves file)
    ↓
    POST to doc-ingestor (localhost:8001)
    ↓
    Document Ingestor (processes file)
    ↓
    Sends to RabbitMQ queue
    ↓
    Response back to browser
```

---

## Success Indicators ✅

- [x] Console shows correct baseURL
- [ ] Network request goes to `localhost:8000/api/v1/documents/upload`
- [ ] Status `200 OK`
- [ ] Success notification appears
- [ ] File appears in upload history
- [ ] Document ID is generated

---

**Try uploading now and tell me what you see!** 🚀
