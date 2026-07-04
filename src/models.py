from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class Task(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    priority: int = 1
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.now)

class TaskResponse(BaseModel):
    success: bool
    message: str
    task_id: Optional[str] = None
    status: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str

class DubbingRequest(BaseModel):
    target_language: str
    voice_model: str = "default"
    style: str = "neutral"
    gdpr_consent: bool = False

class DubbingJob(BaseModel):
    job_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    input_file: str
    target_language: str
    voice_model: str
    status: str = "queued"
    progress: float = 0.0
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    output_url: Optional[str] = None
    metrics: Dict[str, Any] = Field(default_factory=dict)

class GDPRConsent(BaseModel):
    user_id: str
    consent_given: bool
    timestamp: datetime = Field(default_factory=datetime.now)
    data_types: List[str] = ["voice", "video", "transcript"]

class UploadSession(BaseModel):
    upload_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    total_size: int
    chunk_size: int
    total_chunks: int
    uploaded_chunks: List[int] = Field(default_factory=list)
    user_id: str
    created_at: datetime = Field(default_factory=datetime.now)

class UserData(BaseModel):
    user_id: str
    files: List[str]
    jobs: List[str]
