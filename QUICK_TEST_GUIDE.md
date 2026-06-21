# Quick Test Guide - Resume Parsing

## Prerequisites ✓
- All services running: `docker compose ps` ✓
- Backend: http://localhost:8000 ✓
- Frontend: http://localhost:5173 ✓

## Get Auth Token (Required)

1. Open http://localhost:5173
2. Login with Google
3. DevTools (F12) → Application tab → Local Storage → http://localhost:5173
4. Find key with Firebase auth data, copy the `idToken` value
5. It looks like: `eyJhbGciOiJSUzI1NiIsImtp...` (long string)

## Quick Test (Option 1 - Automated)

```bash
./test_resume_upload.sh "paste-your-token-here"
```

This script will:
- Upload a test resume
- Monitor parsing progress
- Show extracted data
- Offer cleanup

## Manual Test (Option 2)

### 1. Upload Resume
```bash
# Set your token
export TOKEN="your-firebase-token-here"

# Upload
curl -X POST http://localhost:8000/v1/resumes/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/Users/ajay_macm5/Documents/potfoliio/ajay-portfolio/dist/Ajay_M_Resume.pdf" \
  -F "display_name=Test Resume"
```

Expected response (202):
```json
{
  "resume_id": "123e4567-e89b-12d3-a456-426614174000",
  "task_id": "abc123-def456"
}
```

### 2. Check Status (Wait 20-40 seconds)
```bash
# Get resume_id from step 1
export RESUME_ID="123e4567-e89b-12d3-a456-426614174000"

# Check in database
docker compose exec backend python3 -c "
from app.db import supabase_client
result = supabase_client.table('resumes').select('parse_status, parse_error').eq('id', '$RESUME_ID').single().execute()
print(f'Status: {result.data[\"parse_status\"]}')
if result.data.get('parse_error'):
    print(f'Error: {result.data[\"parse_error\"]}')
"
```

### 3. List Resumes
```bash
curl -s http://localhost:8000/v1/resumes \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### 4. Get Details
```bash
curl -s http://localhost:8000/v1/resumes/$RESUME_ID \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

## Watch Logs in Real-Time

```bash
# Worker (parsing happens here)
docker compose logs worker -f

# Backend (API requests)
docker compose logs backend -f
```

## Verify Implementation

```bash
# Check services
docker compose ps

# Check worker tasks
docker compose exec worker celery -A workers.celery_app inspect registered | grep parse

# Check database table
docker compose exec backend python3 -c "
from app.db import supabase_client
result = supabase_client.table('resumes').select('*').limit(1).execute()
print('✓ Resumes table exists')
"

# Check storage bucket
docker compose exec backend python3 -c "
from app.db import supabase_client
buckets = [b.name for b in supabase_client.storage.list_buckets()]
print('✓ kalibr-files bucket exists' if 'kalibr-files' in buckets else '✗ Bucket missing')
"
```

## Expected Timeline

1. **Upload** (< 1s): File uploaded to Supabase Storage
2. **Task Queued** (< 1s): Celery task created
3. **Worker Picks Up** (1-2s): Worker starts processing
4. **Parse File** (5-10s): Extract text/formatting
5. **LLM Extraction** (10-20s): NVIDIA NIM processes text
6. **Generate Embedding** (2-5s): Create 384-dim vector
7. **Save to DB** (< 1s): Update database
8. **Total**: 15-40 seconds

## Success Indicators

✅ Upload returns 202 with `resume_id` and `task_id`
✅ `parse_status` changes: pending → processing → done
✅ GET `/v1/resumes` shows the resume with `skills_count`
✅ GET `/v1/resumes/{id}` returns `structured` and `fingerprint`
✅ No errors in worker logs

## Common Issues

### "No module named 'workers.tasks'"
**Fixed** - Backend uses `send_task()` instead of direct import

### "ModuleNotFoundError: No module named 'docx'"
**Fixed** - Dependencies in pyproject.toml, rebuilt images

### "StorageError: Bucket not found"
**Check**: Storage bucket exists
```bash
docker compose exec backend python3 -c "from app.db import supabase_client; print([b.name for b in supabase_client.storage.list_buckets()])"
```

### "401 Unauthorized"
**Issue**: Invalid or expired token
**Fix**: Get a fresh token from frontend

### Parse stuck on "pending"
**Check**: Worker logs for errors
```bash
docker compose logs worker --tail=50
```

### "LLM extraction failed"
**Check**: NVIDIA API key
```bash
docker compose exec backend python3 -c "from app.config import settings; print('Key:', settings.nvidia_api_key_mistral[:20])"
```

## Cleanup Test Data

```bash
# Delete a specific resume
curl -X DELETE http://localhost:8000/v1/resumes/$RESUME_ID \
  -H "Authorization: Bearer $TOKEN"

# Check it's deleted (should return 404)
curl http://localhost:8000/v1/resumes/$RESUME_ID \
  -H "Authorization: Bearer $TOKEN"
```

## Files Created

- ✅ `backend/app/services/parse_service.py` - Full parsing logic
- ✅ `workers/tasks/parse.py` - Celery task
- ✅ `backend/app/routers/resumes.py` - API endpoints
- ✅ `backend/app/models/fingerprints.py` - DOCX/PDF models
- ✅ `backend/app/models/resume.py` - Structured resume model
- ✅ `backend/migrations/002_resumes.sql` - Database schema

## Documentation

- `IMPLEMENTATION_SUMMARY.md` - Full implementation details
- `RESUME_PARSING_STATUS.md` - Detailed status & debugging
- `test_resume_upload.sh` - Automated test script
- `QUICK_TEST_GUIDE.md` - This file

---

**Ready to test!** Start with the automated script or follow manual steps above.
