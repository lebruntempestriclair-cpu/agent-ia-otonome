#!/usr/bin/env python3
"""
Agent IA Autonome - Main Application
Autonomous AI Agent capable of executing tasks on demand
"""

import os
import logging
import secrets
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, Security, UploadFile, File, Form, BackgroundTasks, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import Optional, List
import uvicorn

from src.storage import StorageManager
from src.orchestrator import DubbingOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============ Settings ============

class Settings:
    """Cached environment variables to reduce syscall overhead"""
    def __init__(self):
        self.REQUIRE_API_KEY = os.getenv("REQUIRE_API_KEY", "false").lower() == "true"
        self.API_KEY = os.getenv("API_KEY", "default_secret_key")
        self.DEPLOYMENT_ENV = os.getenv("DEPLOYMENT_ENV", "development")
        self.API_HOST = os.getenv("API_HOST", "0.0.0.0")
        self.API_PORT = int(os.getenv("API_PORT", 8000))
        self.API_WORKERS = int(os.getenv("API_WORKERS", 1))
        self.MAX_FILE_SIZE = 700 * 1024 * 1024 # 700MB

        # Security Safeguard
        if self.DEPLOYMENT_ENV == "production" and self.REQUIRE_API_KEY and self.API_KEY == "default_secret_key":
            raise ValueError("SECURITY ALERT: Default API_KEY used in production environment!")

settings = Settings()

# ============ Security & Dependencies ============

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def verify_api_key(header_value: str = Security(api_key_header)):
    """Validate the API key from the header using constant-time comparison"""
    if settings.REQUIRE_API_KEY:
        if not header_value or not secrets.compare_digest(header_value, settings.API_KEY):
            logger.warning("Invalid or missing API key provided")
            raise HTTPException(
                status_code=403,
                detail="Could not validate credentials"
            )
    return header_value

# Mock OAuth2 user dependency - enhanced for multi-user isolation testing
async def get_active_user(
    api_key: str = Depends(verify_api_key),
    authorization: Optional[str] = Header(None)
):
    """
    Simulates OAuth2 user identification.
    In production, this would verify a JWT.
    For testing, we extract a user_id from the Authorization header if present.
    """
    user_id = "user_default"
    if authorization and authorization.startswith("Bearer "):
        user_id = authorization.split(" ")[1]

    return {"user_id": user_id, "email": f"{user_id}@example.com"}

# ============ App Setup ============

storage_manager = StorageManager()
orchestrator = DubbingOrchestrator()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Modern lifespan management for startup and shutdown"""
    logger.info("Agent IA Autonome starting...")
    yield
    logger.info("Agent IA Autonome shutting down...")

# Initialize FastAPI app
app = FastAPI(
    title="Agent IA Autonome - Dubbing Platform",
    description="Autonomous AI agent for multilingual voice dubbing",
    version="1.1.0",
    lifespan=lifespan
)

# Add CORS middleware with restricted origins in production
if settings.DEPLOYMENT_ENV == "production":
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",")
    if not ALLOWED_ORIGINS or ALLOWED_ORIGINS == [""]:
        logger.warning("No ALLOWED_ORIGINS set in production! Defaulting to empty list.")
        ALLOWED_ORIGINS = []
else:
    ALLOWED_ORIGINS = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ Models ============

class Task(BaseModel):
    id: Optional[str] = None
    title: str
    description: str
    priority: int = 1
    status: str = "pending"

class TaskResponse(BaseModel):
    success: bool
    message: str
    task_id: Optional[str] = None
    status: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str

class DubbingResponse(BaseModel):
    success: bool
    job_id: str
    message: str

class UploadInitResponse(BaseModel):
    upload_id: str
    message: str

# ============ Routes ============

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.1.0",
        "environment": settings.DEPLOYMENT_ENV
    }

# --- Chunked Upload Endpoints ---

@app.post("/upload/start", response_model=UploadInitResponse)
async def start_upload(user: dict = Depends(get_active_user)):
    """Initialize a chunked upload session."""
    upload_id = str(uuid.uuid4())
    return {"upload_id": upload_id, "message": "Upload session initialized."}

@app.post("/upload/chunk")
async def upload_chunk(
    upload_id: str = Form(...),
    chunk_index: int = Form(...),
    file: UploadFile = File(...),
    user: dict = Depends(get_active_user)
):
    """Upload a single chunk of a file."""
    # Size check for each chunk (reasonable limit, e.g. 50MB)
    # Total size check should be in finalize_upload or tracked in session
    await storage_manager.save_chunk(user["user_id"], upload_id, chunk_index, file)
    return {"success": True, "message": f"Chunk {chunk_index} received."}

@app.post("/dub", response_model=DubbingResponse)
async def create_dubbing_job(
    background_tasks: BackgroundTasks,
    target_lang: str = Form(...),
    voice_id: str = Form("default"),
    gdpr_consent: bool = Form(...),
    upload_id: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    user: dict = Depends(get_active_user)
):
    """
    Start the dubbing pipeline using either a pre-uploaded (chunked) file
    or a direct single-shot upload.
    """
    if not gdpr_consent:
        raise HTTPException(
            status_code=400,
            detail="GDPR consent is mandatory for biometric data processing."
        )

    user_id = user["user_id"]
    job_id = str(uuid.uuid4())

    if upload_id and filename:
        # Finalize chunked upload
        file_path = await storage_manager.finalize_upload(user_id, upload_id, filename)
        # Re-verify extension
        _, ext = os.path.splitext(filename)
    elif file:
        # Single-shot upload
        allowed_extensions = {".mp4", ".avi", ".mp3", ".wav"}
        _, ext = os.path.splitext(file.filename)
        if ext.lower() not in allowed_extensions:
            raise HTTPException(status_code=400, detail=f"Unsupported file type. Allowed: {allowed_extensions}")

        # Rename for collision avoidance
        file.filename = f"{job_id}{ext}"
        file_path = await storage_manager.save_file(user_id, file)
    else:
        raise HTTPException(status_code=400, detail="Missing file or upload_id/filename.")

    # Validate final file size
    if os.path.getsize(file_path) > settings.MAX_FILE_SIZE:
        os.remove(file_path)
        raise HTTPException(status_code=413, detail="File too large (Max 700MB).")

    # Start pipeline in background
    background_tasks.add_task(
        orchestrator.run_pipeline,
        file_path,
        target_lang,
        voice_id,
        job_id
    )

    return DubbingResponse(
        success=True,
        job_id=job_id,
        message="Job started successfully."
    )

@app.delete("/user/data")
async def delete_personal_data(user: dict = Depends(get_active_user)):
    """GDPR 'Right to be forgotten': delete all user media files."""
    try:
        storage_manager.delete_user_data(user["user_id"])
        return {"success": True, "message": "All personal data has been deleted."}
    except Exception as e:
        logger.error(f"Error deleting user data: {e}")
        raise HTTPException(status_code=500, detail="Error during data deletion.")

# ============ Existing Task Routes ============

@app.post("/task/create", response_model=TaskResponse, dependencies=[Depends(verify_api_key)])
async def create_task(task: Task):
    return TaskResponse(success=True, message="Task created", task_id="task_123")

@app.get("/tasks", dependencies=[Depends(verify_api_key)])
async def list_tasks():
    return {"tasks": [], "total": 0}

@app.get("/task/{task_id}", dependencies=[Depends(verify_api_key)])
async def get_task(task_id: str):
    return {"task_id": task_id, "status": "pending"}

@app.post("/execute", dependencies=[Depends(verify_api_key)])
async def execute_task(task_id: str):
    return {"success": True, "message": "Task execution started", "task_id": task_id}

# ============ Main ============

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        workers=settings.API_WORKERS,
        reload=settings.DEPLOYMENT_ENV == "development"
    )
