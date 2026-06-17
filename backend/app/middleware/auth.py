"""
Firebase ID-token verification dependency.

All protected routes depend on `get_current_user`.  It extracts the Bearer
token, verifies it with Firebase Admin SDK, and returns the decoded token
claims dict (which contains at minimum `uid` and `email`).

Error responses always use the shape:
    {"error": {"code": "ERROR_CODE", "message": "Human-readable description"}}
"""

import firebase_admin.auth
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

_bearer = HTTPBearer(auto_error=False)


def _auth_error(code: str, message: str) -> HTTPException:
    """Build an HTTPException whose detail matches the project error envelope."""
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"error": {"code": code, "message": message}},
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> dict:
    """
    FastAPI dependency — verifies the Firebase Bearer token.

    Returns:
        Decoded Firebase token claims dict, e.g.
        {"uid": "abc123", "email": "user@example.com", ...}

    Raises:
        HTTPException 401 AUTH_TOKEN_MISSING    — no Authorization header
        HTTPException 401 AUTH_TOKEN_EXPIRED    — token has expired
        HTTPException 401 AUTH_TOKEN_INVALID    — token is malformed / revoked
    """
    if credentials is None:
        raise _auth_error("AUTH_TOKEN_MISSING", "Authorization header is required.")

    token = credentials.credentials

    try:
        decoded = firebase_admin.auth.verify_id_token(token, check_revoked=True)
    except firebase_admin.auth.ExpiredIdTokenError:
        raise _auth_error("AUTH_TOKEN_EXPIRED", "The Firebase ID token has expired.")
    except firebase_admin.auth.RevokedIdTokenError:
        raise _auth_error("AUTH_TOKEN_INVALID", "The Firebase ID token has been revoked.")
    except firebase_admin.auth.InvalidIdTokenError:
        raise _auth_error("AUTH_TOKEN_INVALID", "The Firebase ID token is invalid.")
    except Exception:
        raise _auth_error("AUTH_TOKEN_INVALID", "Could not validate credentials.")

    return decoded
