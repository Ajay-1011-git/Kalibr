"""Interview prep router stub."""
from fastapi import APIRouter

router = APIRouter()


@router.post("/")
async def generate_interview_prep() -> dict:
    """Stub: Generate interview prep questions and answers for a job."""
    return {"message": "interview_prep.generate_interview_prep — not implemented"}


@router.get("/{session_id}")
async def get_interview_prep(session_id: str) -> dict:
    """Stub: Retrieve a previously generated interview prep session."""
    return {"message": f"interview_prep.get_interview_prep({session_id}) — not implemented"}
