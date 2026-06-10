"""
Firebase token verification middleware/dependency.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

bearer_scheme = HTTPBearer()


async def verify_firebase_token(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    """
    Dependency that verifies a Firebase ID token from the Authorization header.
    Returns the decoded token claims on success.
    Raises HTTP 401 on failure.
    """
    # TODO: Implement Firebase Admin SDK token verification
    token = credentials.credentials
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authentication token.",
        )
    # Stub: return a placeholder user payload
    return {"uid": "stub-uid", "email": "stub@example.com"}
