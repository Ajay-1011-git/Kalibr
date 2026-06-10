"""
Match service stub.
Computes semantic similarity between a StructuredResume and a NormalisedJob.
Uses sentence-transformers embeddings and returns a MatchResult.
"""


async def match_resume_to_job(resume_id: str, job_id: str) -> dict:
    """Stub: Embed resume and job, compute cosine similarity, return MatchResult dict."""
    raise NotImplementedError("match_service.match_resume_to_job is not implemented yet.")


async def get_skill_gap(resume_id: str, job_id: str) -> dict:
    """Stub: Compute SkillGapAnalysis for a resume/job pair."""
    raise NotImplementedError("match_service.get_skill_gap is not implemented yet.")
