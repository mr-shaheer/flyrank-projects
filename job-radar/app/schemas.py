import datetime as dt
from pydantic import BaseModel, EmailStr, ConfigDict


# ---------- Auth ----------
class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    created_at: dt.datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- Resume ----------
class ResumeCreate(BaseModel):
    content_text: str


class ResumeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    content_text: str
    created_at: dt.datetime


# ---------- Job ----------
class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    company: str | None
    location: str | None
    url: str | None
    source: str
    scraped_at: dt.datetime


# ---------- Match ----------
class MatchOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    job_id: int
    score: float
    reasoning: str | None
    created_at: dt.datetime
    job: JobOut


# ---------- Application ----------
class ApplicationCreate(BaseModel):
    job_id: int
    status: str = "saved"
    notes: str | None = None


class ApplicationUpdate(BaseModel):
    status: str | None = None
    notes: str | None = None


class ApplicationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    job_id: int
    status: str
    notes: str | None
    updated_at: dt.datetime
