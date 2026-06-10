"""
Application configuration — reads all environment variables via pydantic-settings.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── Firebase (Auth only — Storage is Supabase) ────────────────────────────
    firebase_project_id: str = ""
    firebase_private_key: str = ""
    firebase_client_email: str = ""

    # ── Supabase ──────────────────────────────────────────────────────────────
    supabase_url: str = ""
    supabase_service_role_key: str = ""

    # ── NVIDIA NIM ────────────────────────────────────────────────────────────
    nvidia_api_key: str = ""

    # ── Tavily ────────────────────────────────────────────────────────────────
    tavily_api_key: str = ""

    # ── Redis ─────────────────────────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"

    # ── Encryption ────────────────────────────────────────────────────────────
    fernet_key: str = ""

    # ── Email ─────────────────────────────────────────────────────────────────
    resend_api_key: str = ""

    # ── App ───────────────────────────────────────────────────────────────────
    environment: str = "development"
    allowed_origins: list[str] = ["http://localhost:5173"]


settings = Settings()
