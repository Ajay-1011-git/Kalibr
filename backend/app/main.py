"""
Kalibr Backend — FastAPI application entry point.
Configures CORS, mounts middleware, and registers all routers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

app = FastAPI(
    title="Kalibr API",
    version="0.1.0",
    description="AI-powered resume tailoring and job application platform.",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(resumes.router, prefix="/api/resumes", tags=["resumes"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(match.router, prefix="/api/match", tags=["match"])
app.include_router(rewrite.router, prefix="/api/rewrite", tags=["rewrite"])
app.include_router(cover_letters.router, prefix="/api/cover-letters", tags=["cover_letters"])
app.include_router(applications.router, prefix="/api/applications", tags=["applications"])
app.include_router(auto_apply.router, prefix="/api/auto-apply", tags=["auto_apply"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])
app.include_router(interview_prep.router, prefix="/api/interview-prep", tags=["interview_prep"])


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
