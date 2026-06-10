"""Search router stub."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/jobs")
async def search_jobs() -> dict:
    """Stub: Search for jobs using Tavily."""
    return {"message": "search.search_jobs — not implemented"}


@router.get("/jobs/saved")
async def get_saved_jobs() -> dict:
    """Stub: Return saved jobs for current user."""
    return {"message": "search.get_saved_jobs — not implemented"}


@router.post("/jobs/{job_id}/save")
async def save_job(job_id: str) -> dict:
    """Stub: Save a job for the current user."""
    return {"message": f"search.save_job({job_id}) — not implemented"}
