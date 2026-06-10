"""
Export service stub.
Converts a StructuredResume back to DOCX or PDF for download.
"""


async def export_to_docx(resume_id: str) -> bytes:
    """Stub: Render a StructuredResume as a formatted .docx file."""
    raise NotImplementedError("export_service.export_to_docx is not implemented yet.")


async def export_to_pdf(resume_id: str) -> bytes:
    """Stub: Render a StructuredResume as a PDF using Playwright."""
    raise NotImplementedError("export_service.export_to_pdf is not implemented yet.")
