"""
Rewrite service stub.
Calls the NVIDIA NIM (OpenAI-compatible) API to produce a tailored resume rewrite.
Returns a RewriteResult with change tracking and ATS scoring.
"""


async def rewrite_resume(resume_id: str, job_id: str) -> dict:
    """
    Stub: Generate a rewritten resume tailored to the target job.
    Calls NVIDIA NIM via the openai SDK pointed at the NIM base URL.
    Returns a RewriteResult dict.
    """
    raise NotImplementedError("rewrite_service.rewrite_resume is not implemented yet.")


async def score_ats(resume_text: str, job_description: str) -> dict:
    """Stub: Score a resume against a job description for ATS compatibility."""
    raise NotImplementedError("rewrite_service.score_ats is not implemented yet.")
