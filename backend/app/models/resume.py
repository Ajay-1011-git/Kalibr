"""
Resume content models — TRD §4.3.

StructuredResume is the canonical JSON representation of a parsed resume.
It is produced by ParseService.extract_structured() using an LLM and stored
as JSONB in resumes.structured. All fields are nullable / optional so the
LLM can omit fields that are not present in the source document.
"""

from pydantic import BaseModel, Field


class ContactInfo(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    linkedin: str | None = None
    github: str | None = None
    portfolio: str | None = None


class Bullet(BaseModel):
    """A single resume bullet point with extracted numeric metrics."""

    text: str
    metrics: list[str] = Field(
        default_factory=list,
        description="Extracted numeric / quantitative metrics, e.g. ['40%', '$2M'].",
    )


class WorkExperience(BaseModel):
    company: str | None = None
    title: str | None = None
    location: str | None = None
    start_date: str | None = None           # free-form, e.g. "Jan 2021"
    end_date: str | None = None             # None when current=True
    current: bool = False
    bullets: list[Bullet] = Field(default_factory=list)


class Education(BaseModel):
    institution: str | None = None
    degree: str | None = None               # e.g. "Bachelor of Science"
    field_of_study: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    gpa: float | None = None


class Certification(BaseModel):
    name: str | None = None
    issuer: str | None = None
    issued_date: str | None = None
    expiry_date: str | None = None


class Project(BaseModel):
    name: str | None = None
    description: str | None = None
    tech_stack: list[str] = Field(default_factory=list)
    url: str | None = None


class StructuredResume(BaseModel):
    """
    Fully parsed and normalised representation of a resume.

    Produced by ParseService.extract_structured(); stored in resumes.structured.
    The raw_full_text field is populated from the fingerprint's raw text,
    not extracted by the LLM.
    """

    contact: ContactInfo = Field(default_factory=ContactInfo)
    summary: str | None = None
    work_experience: list[WorkExperience] = Field(default_factory=list)
    education: list[Education] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    certifications: list[Certification] = Field(default_factory=list)
    projects: list[Project] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    raw_full_text: str = ""                 # populated after LLM extraction
