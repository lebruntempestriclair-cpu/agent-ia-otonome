from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ProjectBase(BaseModel):
    title: str
    source_language: str
    target_language: str
    voice_id: str
    consent_given: bool = False

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: str
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    media_path: Optional[str] = None
    output_path: Optional[str] = None
    wer_score: Optional[float] = None
    mos_score: Optional[float] = None

class User(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    is_active: bool = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
