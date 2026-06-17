"""
Supabase client singleton.

Uses the service-role key so the backend has full read/write access
regardless of RLS policies (the backend is the only trusted writer).
"""

from supabase import Client, create_client

from app.config import settings

supabase_client: Client = create_client(
    settings.supabase_url or "http://localhost",          # fallback keeps import safe
    settings.supabase_service_role_key or "placeholder",  # replaced at runtime
)
