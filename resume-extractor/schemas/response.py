from enum import Enum

from pydantic import BaseModel, Field


class ExperienceLevel(str, Enum):
    INTERN = "Intern"
    JUNIOR = "Junior"
    MID = "Mid"
    SENIOR = "Senior"
    LEAD = "Lead"
    UNKNOWN = "Unknown"


class ResumeResponse(BaseModel):
    skills: list[str] = Field(
        description="Technical skills found in the resume"
    )

    experience_level: ExperienceLevel

    years_of_experience: int = Field(
        ge=0,
        le=50
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0
    )

    needs_review: bool