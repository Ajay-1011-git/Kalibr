"""
Kalibr Backend — FastAPI application entry point.

Startup tasks (via lifespan):
  - Initialise Firebase Admin SDK from env vars
  - All routers registered under /v1 prefix
"""

from contextlib import asynccontextmanager
from typing import AsyncIterator

import firebase_admin
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from firebase_admin import credentials

from app.config import settings
from app.routers import (
    alerts,
    applications,
    auth,
    auto_apply,
    cover_letters,
    interview_prep,
    match,
    resumes,
    rewrite,
    search,
    users,
)


# ── Lifespan ──────────────────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Initialise Firebase Admin SDK once at startup."""
    if (
        settings.firebase_project_id
        and settings.firebase_client_email
        and settings.firebase_private_key
        and not firebase_admin._apps
    ):
        cred = credentials.Certificate(
            {
                "type": "service_account",
                "project_id": settings.firebase_project_id,
                # Env vars store literal \n — convert to real newlines
                "private_key": settings.firebase_private_key.replace("\\n", "\n"),
                "client_email": settings.firebase_client_email,
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        )
        firebase_admin.initialize_app(cred)

    yield  # application runs here

    # (shutdown: nothing to tear down for Firebase Admin)


# ── App ───────────────────────────────────────────────────────────────────────


app = FastAPI(
    title="Kalibr API",
    version="0.1.0",
    description="AI-powered resume tailoring and job application platform.",
    lifespan=lifespan,
)


# ── CORS ──────────────────────────────────────────────────────────────────────


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Custom exception handler (structured error envelope) ──────────────────────


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Return error responses in the project envelope:
        {"error": {"code": "...", "message": "..."}}

    If the exception detail is already in this format, pass it through directly.
    Otherwise wrap it in a generic error object.
    """
    detail = exc.detail
    if isinstance(detail, dict) and "error" in detail:
        content = detail
    else:
        content = {"error": {"code": "ERROR", "message": str(detail)}}

    return JSONResponse(
        status_code=exc.status_code,
        content=content,
        headers=getattr(exc, "headers", None) or {},
    )


# ── Health check ──────────────────────────────────────────────────────────────


@app.get("/v1/health", tags=["health"])
async def health_check() -> dict[str, str]:
    """Health check endpoint for Docker healthcheck."""
    return {"status": "healthy", "service": "kalibr-backend"}


# ── Routers (all under /v1) ───────────────────────────────────────────────────


app.include_router(auth.router,           prefix="/v1/auth",           tags=["auth"])
app.include_router(users.router,          prefix="/v1/users",          tags=["users"])
app.include_router(resumes.router,        prefix="/v1/resumes",        tags=["resumes"])
app.include_router(search.router,         prefix="/v1/search",         tags=["search"])
app.include_router(match.router,          prefix="/v1/match",          tags=["match"])
app.include_router(rewrite.router,        prefix="/v1/rewrite",        tags=["rewrite"])
app.include_router(cover_letters.router,  prefix="/v1/cover-letters",  tags=["cover_letters"])
app.include_router(applications.router,   prefix="/v1/applications",   tags=["applications"])
app.include_router(auto_apply.router,     prefix="/v1/auto-apply",     tags=["auto_apply"])
app.include_router(alerts.router,         prefix="/v1/alerts",         tags=["alerts"])
app.include_router(interview_prep.router, prefix="/v1/interview-prep", tags=["interview_prep"])

