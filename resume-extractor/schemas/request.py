from pydantic import BaseModel, Field


class ResumeRequest(BaseModel):
    resume_text: str = Field(
        ...,
        min_length=50,
        max_length=10000,
        description="Raw resume text"
    )