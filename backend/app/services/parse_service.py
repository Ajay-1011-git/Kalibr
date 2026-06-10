"""
Parse service stub.
Responsible for extracting structured data from uploaded resume files (PDF / DOCX).
"""


async def parse_pdf(file_bytes: bytes) -> dict:
    """Stub: Parse a PDF file and return a StructuredResume dict."""
    raise NotImplementedError("parse_service.parse_pdf is not implemented yet.")


async def parse_docx(file_bytes: bytes) -> dict:
    """Stub: Parse a DOCX file and return a StructuredResume dict."""
    raise NotImplementedError("parse_service.parse_docx is not implemented yet.")


async def fingerprint_pdf(file_bytes: bytes) -> dict:
    """Stub: Compute a PdfFingerprint for a PDF file."""
    raise NotImplementedError("parse_service.fingerprint_pdf is not implemented yet.")


async def fingerprint_docx(file_bytes: bytes) -> dict:
    """Stub: Compute a DocxFingerprint for a DOCX file."""
    raise NotImplementedError("parse_service.fingerprint_docx is not implemented yet.")
