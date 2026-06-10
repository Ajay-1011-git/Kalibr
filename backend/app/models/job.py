"""
Job domain models using Pydantic v2.
"""

from typing import Optional
from pydantic import BaseModel, Field


class SalaryRange(BaseModel):
    min: Optional[int] = None
    max: Optional[int] = None
    currency: str = "USD"
    period: str = "yearly"  # yearly | monthly | hourly


class NormalisedJob(BaseModel):
    """
    Normalised job posting — produced after scraping / Tavily search.
    """

    id: str = ""
    title: str = ""
    company: str = ""
    location: str = ""
    remote: bool = False
    description: str = ""
    requirements: list[str] = Field(default_factory=list)
    nice_to_have: list[str] = Field(default_factory=list)
    salary: Optional[SalaryRange] = None
    employment_type: str = ""  # full-time | part-time | contract | internship
    experience_level: str = ""  # entry | mid | senior | lead
    posted_at: str = ""
    url: str = ""
    source: str = ""  # linkedin | indeed | greenhouse | etc.
