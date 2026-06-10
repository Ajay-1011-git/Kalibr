"""
Rewrite domain models using Pydantic v2.
"""

from enum import Enum
from pydantic import BaseModel, Field


class ChangeType(str, Enum):
    """Type of change applied during a resume rewrite."""

    BULLET_ENHANCED = "bullet_enhanced"
    KEYWORD_INSERTED = "keyword_inserted"
    SECTION_REORDERED = "section_reordered"
    SKILL_ADDED = "skill_added"
    SUMMARY_REWRITTEN = "summary_rewritten"
    QUANTIFICATION_ADDED = "quantification_added"


class RewriteChange(BaseModel):
    """A single tracked change produced during rewriting."""

    change_type: ChangeType
    original: str = ""
    revised: str = ""
    section: str = ""
    rationale: str = ""


class AtsScore(BaseModel):
    """ATS compatibility score before and after rewrite."""

    before: float = Field(0.0, ge=0.0, le=100.0)
    after: float = Field(0.0, ge=0.0, le=100.0)
    keyword_hits: list[str] = Field(default_factory=list)
    keyword_misses: list[str] = Field(default_factory=list)


class RewriteResult(BaseModel):
    """
    Full output of a resume rewrite task.
    Contains the revised resume text, diff changes, and ATS scoring.
    """

    task_id: str = ""
    resume_id: str = ""
    job_id: str = ""
    revised_text: str = ""
    changes: list[RewriteChange] = Field(default_factory=list)
    ats_score: AtsScore = Field(default_factory=AtsScore)
    created_at: str = ""
