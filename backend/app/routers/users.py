"""
Users router — authenticated user profile and credential management.

All endpoints require a valid Firebase Bearer token via `get_current_user`.
"""

from datetime import datetime, timezone
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel

from app.db import supabase_client
from app.middleware.auth import get_current_user
from app.services.encryption_service import get_encryption_service

router = APIRouter()

# ── Constants ─────────────────────────────────────────────────────────────────

# Columns exposed on GET /users/me — never returns encrypted credential columns
_USER_PUBLIC_COLUMNS = (
    "id,firebase_uid,email,full_name,phone,address_line,city,country,"
    "nationality,work_auth,notice_period,salary_min,salary_max,"
    "salary_currency,remote_pref,linkedin_url,github_url,portfolio_url,"
    "created_at,updated_at"
)

_ALLOWED_BOARDS = frozenset({
    "linkedin", "indeed", "glassdoor", "monster",
    "wellfound", "ziprecruiter", "upwork",
})

BoardName = Literal[
    "linkedin", "indeed", "glassdoor", "monster",
    "wellfound", "ziprecruiter", "upwork",
]

# ── Request models ────────────────────────────────────────────────────────────


class UserProfilePatch(BaseModel):
    """Whitelisted fields for PATCH /users/me."""
    full_name: str | None = None
    phone: str | None = None
    address_line: str | None = None
    city: str | None = None
    country: str | None = None
    nationality: str | None = None
    work_auth: str | None = None
    notice_period: int | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    salary_currency: str | None = None
    remote_pref: str | None = None
    linkedin_url: str | None = None
    github_url: str | None = None
    portfolio_url: str | None = None


class CredentialRequest(BaseModel):
    board: str
    username: str
    password: str


# ── Helpers ───────────────────────────────────────────────────────────────────


def _get_user_row(firebase_uid: str) -> dict[str, Any]:
    """Fetch the users row for *firebase_uid*, raising 404 if missing."""
    result = (
        supabase_client.table("users")
        .select(_USER_PUBLIC_COLUMNS)
        .eq("firebase_uid", firebase_uid)
        .maybe_single()
        .execute()
    )
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "USER_NOT_FOUND", "message": "User profile not found."}},
        )
    return result.data  # type: ignore[return-value]


def _get_user_id(firebase_uid: str) -> str:
    """Return the Supabase UUID for *firebase_uid*."""
    result = (
        supabase_client.table("users")
        .select("id")
        .eq("firebase_uid", firebase_uid)
        .maybe_single()
        .execute()
    )
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "USER_NOT_FOUND", "message": "User profile not found."}},
        )
    return result.data["id"]  # type: ignore[index]


# ── Routes ────────────────────────────────────────────────────────────────────


@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Return the current user's profile.

    Excludes `username_enc` and `password_enc` columns (stored on
    `board_credentials`, not on `users`).
    """
    return _get_user_row(current_user["uid"])


@router.patch("/me")
async def patch_me(
    body: UserProfilePatch,
    current_user: dict = Depends(get_current_user),
) -> dict:
    """
    Update the current user's profile.

    Accepts any subset of the 15 whitelisted fields.
    Always stamps `updated_at` with the current UTC time.
    """
    updates = body.model_dump(exclude_none=True)
    if not updates:
        # Nothing to update — return the current row unchanged
        return _get_user_row(current_user["uid"])

    updates["updated_at"] = datetime.now(tz=timezone.utc).isoformat()

    result = (
        supabase_client.table("users")
        .update(updates)
        .eq("firebase_uid", current_user["uid"])
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "UPDATE_FAILED", "message": "Failed to update user profile."}},
        )

    return _get_user_row(current_user["uid"])


@router.get("/me/credentials")
async def list_credentials(current_user: dict = Depends(get_current_user)) -> list[dict]:
    """
    List all saved board credentials for the current user.

    Returns board names only — never exposes encrypted values.
    """
    user_id = _get_user_id(current_user["uid"])
    result = (
        supabase_client.table("board_credentials")
        .select("id,board,created_at,updated_at")
        .eq("user_id", user_id)
        .execute()
    )
    return result.data or []


@router.post("/me/credentials", status_code=201)
async def save_credentials(
    body: CredentialRequest,
    current_user: dict = Depends(get_current_user),
) -> dict:
    """
    Encrypt and store job-board credentials.

    `board` must be one of: linkedin, indeed, glassdoor, monster,
    wellfound, ziprecruiter, upwork.

    Upserts on (user_id, board) so re-saving a board replaces the old entry.
    """
    if body.board not in _ALLOWED_BOARDS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": {
                    "code": "INVALID_BOARD",
                    "message": f"board must be one of: {', '.join(sorted(_ALLOWED_BOARDS))}",
                }
            },
        )

    enc = get_encryption_service()
    user_id = _get_user_id(current_user["uid"])
    now = datetime.now(tz=timezone.utc).isoformat()

    (
        supabase_client.table("board_credentials")
        .upsert(
            {
                "user_id": user_id,
                "board": body.board,
                "username_enc": enc.encrypt(body.username),
                "password_enc": enc.encrypt(body.password),
                "updated_at": now,
            },
            on_conflict="user_id,board",
        )
        .execute()
    )

    return {"board": body.board, "saved": True}


@router.delete("/me/credentials/{board}", status_code=204)
async def delete_credentials(
    board: str,
    current_user: dict = Depends(get_current_user),
) -> Response:
    """Delete the saved credentials for *board*. Returns 204 No Content."""
    if board not in _ALLOWED_BOARDS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "INVALID_BOARD", "message": f"Unknown board: {board}"}},
        )

    user_id = _get_user_id(current_user["uid"])

    (
        supabase_client.table("board_credentials")
        .delete()
        .eq("user_id", user_id)
        .eq("board", board)
        .execute()
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
