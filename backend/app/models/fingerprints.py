"""
Fingerprint models for tracking document identity.
Used to detect whether a resume file has been modified.
"""

from pydantic import BaseModel, Field


class DocxFingerprint(BaseModel):
    """Fingerprint for a .docx resume file."""

    file_hash: str = Field(..., description="SHA-256 hash of the raw file bytes.")
    paragraph_count: int = Field(..., description="Number of paragraphs in the document.")
    word_count: int = Field(..., description="Total word count.")
    created_at: str = Field(..., description="ISO 8601 creation timestamp.")
    modified_at: str = Field(..., description="ISO 8601 last-modified timestamp.")


class PdfFingerprint(BaseModel):
    """Fingerprint for a .pdf resume file."""

    file_hash: str = Field(..., description="SHA-256 hash of the raw file bytes.")
    page_count: int = Field(..., description="Number of pages in the PDF.")
    word_count: int = Field(..., description="Total word count across all pages.")
    created_at: str = Field(..., description="ISO 8601 creation timestamp.")
    modified_at: str = Field(..., description="ISO 8601 last-modified timestamp.")
