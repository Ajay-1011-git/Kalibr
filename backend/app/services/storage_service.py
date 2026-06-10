"""
Supabase Storage service.

Wraps the supabase-py storage client for the private "kalibr-files" bucket.

Storage path conventions
─────────────────────────
  users/{firebase_uid}/resumes/{resume_id}/original.{ext}
  users/{firebase_uid}/resumes/{resume_id}/rewrite_{rewrite_id}.docx
  users/{firebase_uid}/resumes/{resume_id}/rewrite_{rewrite_id}.pdf
  users/{firebase_uid}/cover_letters/{cover_letter_id}.docx
  users/{firebase_uid}/screenshots/{queue_id}.png

All paths are rooted inside the "kalibr-files" bucket which is private
(no public access). Callers must use get_signed_url() to produce
time-limited pre-signed URLs for client download.
"""


class StorageService:
    BUCKET = "kalibr-files"

    def __init__(self, supabase_client) -> None:
        """
        Args:
            supabase_client: An initialised supabase-py Client instance.
        """
        self.client = supabase_client
        self.bucket = self.BUCKET

    # ── Write ──────────────────────────────────────────────────────────────────

    def upload(self, path: str, file_bytes: bytes, content_type: str) -> str:
        """
        Upload *file_bytes* to *path* inside the bucket.

        Args:
            path: Storage path relative to the bucket root, e.g.
                  "users/uid123/resumes/res456/original.pdf"
            file_bytes: Raw file content to upload.
            content_type: MIME type string, e.g. "application/pdf".

        Returns:
            The storage *path* on success (use get_signed_url() to produce a
            download URL).

        Raises:
            Exception: Re-raises any supabase-py storage error.
        """
        self.client.storage.from_(self.bucket).upload(
            path,
            file_bytes,
            {"content-type": content_type, "upsert": "false"},
        )
        return path

    # ── Read ───────────────────────────────────────────────────────────────────

    def get_signed_url(self, path: str, expires_in: int = 900) -> str:
        """
        Generate a time-limited signed URL for *path*.

        Args:
            path: Storage path relative to the bucket root.
            expires_in: URL lifetime in seconds (default 15 minutes).

        Returns:
            The signed URL string.
        """
        response = self.client.storage.from_(self.bucket).create_signed_url(
            path, expires_in
        )
        return response["signedURL"]

    # ── Delete ─────────────────────────────────────────────────────────────────

    def delete(self, path: str) -> None:
        """
        Permanently delete the object at *path* from the bucket.

        Args:
            path: Storage path relative to the bucket root.
        """
        self.client.storage.from_(self.bucket).remove([path])
