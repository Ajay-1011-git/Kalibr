#!/usr/bin/env python3
"""
Verification script — StorageService smoke test.

Usage (from /backend):
    pip install -e "."
    # Ensure SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are set in .env
    python3 scripts/verify_storage.py

What it does:
  1. Creates a Supabase client from .env credentials.
  2. Uploads a small text file to the kalibr-files bucket.
  3. Retrieves a signed URL for it (15-minute TTL).
  4. Deletes the test object.
  5. Prints PASS or FAIL for each step.

NOTE: The kalibr-files bucket must already exist in your Supabase project
      (Storage → New bucket → name "kalibr-files", uncheck "Public bucket").
"""

import sys
from dotenv import load_dotenv
from supabase import create_client
from app.config import settings
from app.services.storage_service import StorageService

load_dotenv()

TEST_PATH = "test/verify_storage_smoke_test.txt"
TEST_CONTENT = b"kalibr storage smoke test"
TEST_CONTENT_TYPE = "text/plain"


def main() -> None:
    if not settings.supabase_url or not settings.supabase_service_role_key:
        print("SKIP — SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY not set in .env")
        sys.exit(0)

    client = create_client(settings.supabase_url, settings.supabase_service_role_key)
    storage = StorageService(client)

    # ── Upload ─────────────────────────────────────────────────────────────────
    try:
        returned_path = storage.upload(TEST_PATH, TEST_CONTENT, TEST_CONTENT_TYPE)
        assert returned_path == TEST_PATH
        print(f"  PASS  upload → {returned_path}")
    except Exception as exc:
        print(f"  FAIL  upload: {exc}")
        sys.exit(1)

    # ── Signed URL ─────────────────────────────────────────────────────────────
    try:
        signed_url = storage.get_signed_url(TEST_PATH, expires_in=60)
        assert signed_url.startswith("https://")
        print(f"  PASS  get_signed_url → {signed_url[:80]}…")
    except Exception as exc:
        print(f"  FAIL  get_signed_url: {exc}")
        storage.delete(TEST_PATH)   # clean up even on failure
        sys.exit(1)

    # ── Delete ─────────────────────────────────────────────────────────────────
    try:
        storage.delete(TEST_PATH)
        print(f"  PASS  delete → {TEST_PATH}")
    except Exception as exc:
        print(f"  FAIL  delete: {exc}")
        sys.exit(1)

    print("\nAll StorageService checks passed ✓")


if __name__ == "__main__":
    main()
