#!/bin/bash
# Test script for resume upload functionality
# Usage: ./test_resume_upload.sh <firebase_token>

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if token provided
if [ -z "$1" ]; then
    echo -e "${RED}Error: Firebase auth token required${NC}"
    echo "Usage: $0 <firebase_token>"
    echo ""
    echo "To get your token:"
    echo "1. Open http://localhost:5173"
    echo "2. Login with Google"
    echo "3. Open DevTools → Application → Local Storage"
    echo "4. Find and copy the Firebase auth token"
    exit 1
fi

TOKEN="$1"
API_URL="http://localhost:8000"
RESUME_FILE="/Users/ajay_macm5/Documents/potfoliio/ajay-portfolio/dist/Ajay_M_Resume.pdf"

# Check if resume file exists
if [ ! -f "$RESUME_FILE" ]; then
    echo -e "${RED}Error: Resume file not found: $RESUME_FILE${NC}"
    echo "Please update RESUME_FILE variable in this script"
    exit 1
fi

echo -e "${GREEN}=== Resume Upload Test ===${NC}"
echo ""

# Step 1: Upload resume
echo -e "${YELLOW}Step 1: Uploading resume...${NC}"
UPLOAD_RESPONSE=$(curl -s -X POST "$API_URL/v1/resumes/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@$RESUME_FILE" \
  -F "display_name=Test Resume")

echo "Response: $UPLOAD_RESPONSE"

# Extract resume_id and task_id
RESUME_ID=$(echo $UPLOAD_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('resume_id', ''))" 2>/dev/null || echo "")
TASK_ID=$(echo $UPLOAD_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('task_id', ''))" 2>/dev/null || echo "")

if [ -z "$RESUME_ID" ] || [ -z "$TASK_ID" ]; then
    echo -e "${RED}Error: Failed to extract resume_id or task_id${NC}"
    echo "Full response: $UPLOAD_RESPONSE"
    exit 1
fi

echo -e "${GREEN}✓ Upload successful${NC}"
echo "  Resume ID: $RESUME_ID"
echo "  Task ID: $TASK_ID"
echo ""

# Step 2: Monitor task status
echo -e "${YELLOW}Step 2: Monitoring task status...${NC}"
echo "Waiting for parse to complete (this may take 30-60 seconds)..."

MAX_WAIT=120  # Maximum wait time in seconds
WAITED=0
STATUS="pending"

while [ "$STATUS" != "done" ] && [ "$STATUS" != "failed" ] && [ $WAITED -lt $MAX_WAIT ]; do
    sleep 2
    WAITED=$((WAITED + 2))
    
    # Get current status from database
    DB_STATUS=$(docker compose exec -T backend python3 -c "
from app.db import supabase_client
result = supabase_client.table('resumes').select('parse_status').eq('id', '$RESUME_ID').single().execute()
print(result.data['parse_status'])
" 2>/dev/null || echo "unknown")
    
    if [ "$DB_STATUS" != "$STATUS" ]; then
        STATUS="$DB_STATUS"
        echo "  Status: $STATUS (${WAITED}s elapsed)"
    fi
done

if [ "$STATUS" == "done" ]; then
    echo -e "${GREEN}✓ Parse completed successfully${NC}"
elif [ "$STATUS" == "failed" ]; then
    echo -e "${RED}✗ Parse failed${NC}"
    echo "Check worker logs: docker compose logs worker --tail=50"
    exit 1
else
    echo -e "${YELLOW}⚠ Parse still in progress after ${WAITED}s${NC}"
    echo "Status: $STATUS"
fi
echo ""

# Step 3: List resumes
echo -e "${YELLOW}Step 3: Listing resumes...${NC}"
LIST_RESPONSE=$(curl -s "$API_URL/v1/resumes" \
  -H "Authorization: Bearer $TOKEN")

echo "$LIST_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$LIST_RESPONSE"
echo -e "${GREEN}✓ List successful${NC}"
echo ""

# Step 4: Get resume details
echo -e "${YELLOW}Step 4: Getting resume details...${NC}"
DETAILS_RESPONSE=$(curl -s "$API_URL/v1/resumes/$RESUME_ID" \
  -H "Authorization: Bearer $TOKEN")

# Check if structured data exists
HAS_STRUCTURED=$(echo $DETAILS_RESPONSE | python3 -c "import sys, json; data=json.load(sys.stdin); print('yes' if data.get('structured') else 'no')" 2>/dev/null || echo "no")

if [ "$HAS_STRUCTURED" == "yes" ]; then
    echo -e "${GREEN}✓ Structured data extracted${NC}"
    
    # Show summary of extracted data
    echo "$DETAILS_RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
structured = data.get('structured', {})
print('  Contact Name:', structured.get('contact', {}).get('name', 'N/A'))
print('  Contact Email:', structured.get('contact', {}).get('email', 'N/A'))
print('  Work Experience:', len(structured.get('work_experience', [])), 'entries')
print('  Education:', len(structured.get('education', [])), 'entries')
print('  Skills:', len(structured.get('skills', [])), 'skills')
print('  Projects:', len(structured.get('projects', [])), 'projects')

fingerprint = data.get('fingerprint', {})
if fingerprint:
    print('  Fingerprint Type:', 'PDF' if 'pages' in fingerprint else 'DOCX')
    if 'pages' in fingerprint:
        print('    Pages:', fingerprint.get('pages'))
        print('    Text Blocks:', len(fingerprint.get('text_blocks', [])))
    else:
        print('    Paragraphs:', fingerprint.get('total_paragraphs'))
        print('    Bullets:', fingerprint.get('bullet_count'))
    
    linguistic = fingerprint.get('linguistic', {})
    if linguistic:
        print('    Dominant Tense:', linguistic.get('dominant_tense'))
        print('    Verb First:', linguistic.get('verb_first'))
" 2>/dev/null
else
    echo -e "${RED}✗ No structured data found${NC}"
fi
echo ""

# Step 5: Optional cleanup
echo -e "${YELLOW}Step 5: Cleanup (optional)${NC}"
read -p "Delete test resume? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    curl -s -X DELETE "$API_URL/v1/resumes/$RESUME_ID" \
      -H "Authorization: Bearer $TOKEN"
    echo -e "${GREEN}✓ Resume deleted${NC}"
else
    echo "Resume kept: $RESUME_ID"
fi
echo ""

echo -e "${GREEN}=== Test Complete ===${NC}"
echo ""
echo "Summary:"
echo "  Resume ID: $RESUME_ID"
echo "  Parse Status: $STATUS"
echo "  Structured Data: $HAS_STRUCTURED"
echo ""
echo "To view logs:"
echo "  docker compose logs worker --tail=100"
echo "  docker compose logs backend --tail=100"
