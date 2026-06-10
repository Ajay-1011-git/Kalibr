"""Cover letters router stub."""
from fastapi import APIRouter

router = APIRouter()


@router.post("/")
async def generate_cover_letter() -> dict:
    """Stub: Generate a cover letter for a given resume and job."""
    return {"message": "cover_letters.generate_cover_letter — not implemented"}


@router.get("/{cover_letter_id}")
async def get_cover_letter(cover_letter_id: str) -> dict:
    """Stub: Retrieve a generated cover letter."""
    return {"message": f"cover_letters.get_cover_letter({cover_letter_id}) — not implemented"}
