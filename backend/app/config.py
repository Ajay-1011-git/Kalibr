"""
Application configuration — reads all environment variables via pydantic-settings.
"""

from pydantic import computed_field, field_validator
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
    # Two keys because the caller provided separate keys per model family.
    nvidia_api_key_nemotron: str = ""  # nvidia/nemotron-* models
    nvidia_api_key_mistral: str = ""   # mistralai/mistral-nemotron
    nvidia_nim_base_url: str = "https://integrate.api.nvidia.com/v1"

    @field_validator("nvidia_api_key_nemotron", "nvidia_api_key_mistral")
    @classmethod
    def validate_nvidia_key(cls, v: str) -> str:
        if v and not v.startswith("nvapi-"):
            raise ValueError('NVIDIA API keys must start with "nvapi-"')
        return v

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
    allowed_origins_str: str = "http://localhost:5173"

    @computed_field  # type: ignore[misc]
    @property
    def allowed_origins(self) -> list[str]:
        """Parse ALLOWED_ORIGINS from comma-separated string to list."""
        return [origin.strip() for origin in self.allowed_origins_str.split(",") if origin.strip()]


settings = Settings()

# ── NVIDIA NIM — model registry ───────────────────────────────────────────────
# Single source of truth for all model strings used in NIM API calls.
# Import these constants (never hardcode model strings elsewhere).

NIM_MODELS: dict[str, str] = {
    "rewrite":     "nvidia/nemotron-3-ultra-550b-a55b",
    "extract":     "mistralai/mistral-nemotron",
    "coverletter": "nvidia/nemotron-3-ultra-550b-a55b",
    "interview":   "nvidia/nemotron-3-ultra-550b-a55b",
    "match":       "mistralai/mistral-nemotron",
}

NIM_TEMPERATURES: dict[str, float] = {
    "rewrite":     0.2,
    "extract":     0.1,
    "coverletter": 0.5,
    "interview":   0.6,
    "match":       0.1,
}

# Maps each task to the API key that authenticates its model.
# Usage: NIM_API_KEYS[task]  →  the correct nvapi-... string
NIM_API_KEYS: dict[str, str] = {
    "rewrite":     settings.nvidia_api_key_nemotron,
    "extract":     settings.nvidia_api_key_mistral,
    "coverletter": settings.nvidia_api_key_nemotron,
    "interview":   settings.nvidia_api_key_nemotron,
    "match":       settings.nvidia_api_key_mistral,
}
