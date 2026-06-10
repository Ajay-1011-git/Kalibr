"""
Resume domain models using Pydantic v2.
"""

from typing import Optional
from pydantic import BaseModel, Field


class ContactInfo(BaseModel):
    name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    linkedin: str = ""
    github: str = ""
    portfolio: str = ""


class WorkExperience(BaseModel):
    company: str = ""
    title: str = ""
    location: str = ""
    start_date: str = ""
    end_date: Optional[str] = None
    current: bool = False
    bullets: list[str] = Field(default_factory=list)


class Education(BaseModel):
    institution: str = ""
    degree: str = ""
    field_of_study: str = ""
    start_date: str = ""
    end_date: Optional[str] = None
    gpa: Optional[float] = None


class Project(BaseModel):
    name: str = ""
    description: str = ""
    tech_stack: list[str] = Field(default_factory=list)
    url: str = ""


class Certification(BaseModel):
    name: str = ""
    issuer: str = ""
    issued_date: str = ""
    expiry_date: Optional[str] = None


class StructuredResume(BaseModel):
    """
    Fully parsed and normalised representation of a resume.
    Produced by parse_service and stored in Supabase.
    """

    id: str = ""
    user_id: str = ""
    raw_text: str = ""
    contact: ContactInfo = Field(default_factory=ContactInfo)
    summary: str = ""
    work_experience: list[WorkExperience] = Field(default_factory=list)
    education: list[Education] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    projects: list[Project] = Field(default_factory=list)
    certifications: list[Certification] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""
