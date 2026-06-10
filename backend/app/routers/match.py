"""Match router stub."""
from fastapi import APIRouter

router = APIRouter()


@router.post("/")
async def match_resume_to_job() -> dict:
    """Stub: Match a resume against a job description and return a MatchResult."""
    return {"message": "match.match_resume_to_job — not implemented"}


@router.get("/{match_id}")
async def get_match_result(match_id: str) -> dict:
    """Stub: Retrieve a previously computed MatchResult."""
    return {"message": f"match.get_match_result({match_id}) — not implemented"}
