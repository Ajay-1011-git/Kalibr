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
    def __init__(self, supabase_client):
        self.client = supabase_client
        self.bucket = "kalibr-files"

    def upload(self, path: str, file_bytes: bytes, content_type: str) -> str:
        self.client.storage.from_(self.bucket).upload(
            path, file_bytes, {"content-type": content_type, "upsert": "false"}
        )
        return path

    def get_signed_url(self, path: str, expires_in: int = 900) -> str:
        response = self.client.storage.from_(self.bucket).create_signed_url(
            path, expires_in
        )
        return response["signedURL"]

    def delete(self, path: str) -> None:
        self.client.storage.from_(self.bucket).remove([path])
