from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# ============ Upload Models ============

class UploadInitRequest(BaseModel):
    filename: str
    total_size: int
    content_type: str

class UploadInitResponse(BaseModel):
    upload_id: str
    chunk_size: int = 5 * 1024 * 1024  # 5MB default

class UploadChunkResponse(BaseModel):
    success: bool
    received_index: int

class UploadCompleteRequest(BaseModel):
    upload_id: str
    total_chunks: int

class UploadCompleteResponse(BaseModel):
    success: bool
    filepath: str

# ============ Project Models ============

class ProjectCreate(BaseModel):
    name: str
    source_language: str
    target_language: str
    voice_id: str
    # GDPR Consent
    consent_given: bool = Field(..., description="Explicit consent for biometric data processing")

class Project(BaseModel):
    id: str
    name: str
    status: str = "pending"
    source_language: str
    target_language: str
    voice_id: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    progress: float = 0.0
    output_url: Optional[str] = None

class ProjectResponse(BaseModel):
    success: bool
    project: Project

# ============ User & GDPR Models ============

class User(BaseModel):
    id: str
    email: str
    full_name: str
    gdpr_consent: bool = False
    consent_date: Optional[datetime] = None

class GDPRStatusResponse(BaseModel):
    user_id: str
    has_consented: bool
    consent_date: Optional[datetime]
    data_retention_period_days: int = 30

class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
