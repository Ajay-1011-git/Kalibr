"""
Match domain models using Pydantic v2.
"""

from pydantic import BaseModel, Field


class SkillGapAnalysis(BaseModel):
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    bonus_skills: list[str] = Field(default_factory=list)


class MatchResult(BaseModel):
    """
    Result of matching a StructuredResume against a NormalisedJob.
    Produced by match_service and potentially the rewrite Celery task.
    """

    id: str = ""
    resume_id: str = ""
    job_id: str = ""
    overall_score: float = Field(0.0, ge=0.0, le=1.0, description="0–1 cosine similarity score.")
    skill_gap: SkillGapAnalysis = Field(default_factory=SkillGapAnalysis)
    keyword_coverage: float = Field(0.0, ge=0.0, le=1.0)
    experience_match: float = Field(0.0, ge=0.0, le=1.0)
    title_match: float = Field(0.0, ge=0.0, le=1.0)
    summary: str = ""
    created_at: str = ""
