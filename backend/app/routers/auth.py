"""
Auth router — public endpoints that don't require a Bearer token.
"""

import firebase_admin.auth
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.db import supabase_client

router = APIRouter()


# ── Request / response models ─────────────────────────────────────────────────


class FirebaseTokenRequest(BaseModel):
    firebase_token: str


class VerifyResponse(BaseModel):
    user_id: str
    is_new_user: bool


# ── Helpers ───────────────────────────────────────────────────────────────────


def _auth_error(code: str, message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"error": {"code": code, "message": message}},
    )


# ── Routes ────────────────────────────────────────────────────────────────────


@router.post("/verify", response_model=VerifyResponse, status_code=200)
async def verify_firebase_token(body: FirebaseTokenRequest) -> VerifyResponse:
    """
    Exchange a Firebase ID token for a Kalibr user record.

    - Verifies the token with Firebase Admin SDK.
    - Looks up the user in the `users` table by `firebase_uid`.
    - If the user doesn't exist, creates a new row.
    - Returns the Supabase `user_id` (UUID) and whether this is a new account.
    """
    # ── 1. Verify the Firebase token ─────────────────────────────────────────
    try:
        decoded = firebase_admin.auth.verify_id_token(body.firebase_token)
    except firebase_admin.auth.ExpiredIdTokenError:
        raise _auth_error("AUTH_TOKEN_EXPIRED", "The Firebase ID token has expired.")
    except firebase_admin.auth.InvalidIdTokenError:
        raise _auth_error("AUTH_TOKEN_INVALID", "The Firebase ID token is invalid.")
    except Exception:
        raise _auth_error("AUTH_TOKEN_INVALID", "Could not validate Firebase token.")

    firebase_uid: str = decoded["uid"]
    email: str = decoded.get("email", "")

    # ── 2. Look up user in Supabase ───────────────────────────────────────────
    existing = (
        supabase_client.table("users")
        .select("id")
        .eq("firebase_uid", firebase_uid)
        .maybe_single()
        .execute()
    )

    if existing.data:
        return VerifyResponse(user_id=existing.data["id"], is_new_user=False)

    # ── 3. First-time user — insert row ──────────────────────────────────────
    inserted = (
        supabase_client.table("users")
        .insert({"firebase_uid": firebase_uid, "email": email})
        .execute()
    )

    if not inserted.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "USER_CREATE_FAILED", "message": "Failed to create user record."}},
        )

    return VerifyResponse(user_id=inserted.data[0]["id"], is_new_user=True)
