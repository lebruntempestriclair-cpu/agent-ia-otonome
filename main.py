#!/usr/bin/env python3
"""
Agent IA Autonome - Main Application
Autonomous AI Agent capable of executing tasks on demand
"""

import os
import logging
import secrets
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, Security, Header, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from fastapi.responses import Response
from typing import Optional, List, Dict
import uvicorn
import json

from src.models import (
    Task, TaskResponse, HealthResponse, DubbingRequest, DubbingJob,
    UploadSession, GDPRConsent, UserData
)
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
        self.API_WORKERS = int(os.getenv("API_WORKERS", 4))

        # Production safeguard
        if self.DEPLOYMENT_ENV == "production" and self.REQUIRE_API_KEY and self.API_KEY == "default_secret_key":
            raise ValueError("API_KEY must be changed from default in production environment")

settings = Settings()

# ============ Security ============

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def verify_api_key(header_value: str = Security(api_key_header)):
    """Validate the API key from the header if required using constant-time comparison"""
    if settings.REQUIRE_API_KEY:
        if not header_value or not secrets.compare_digest(header_value, settings.API_KEY):
            logger.warning("Invalid or missing API key provided")
            raise HTTPException(
                status_code=403,
                detail="Could not validate credentials"
            )
    return header_value

async def get_active_user(authorization: Optional[str] = Header(None), api_key: str = Depends(verify_api_key)):
    """
    Simulates multi-user isolation by parsing Authorization header.
    Falls back to a default user if only API Key is present.
    """
    if authorization and authorization.startswith("Bearer "):
        # In a real app, verify JWT here
        token = authorization.split(" ")[1]
        return f"user_{token[:8]}"
    return "default_user"

# ============ Services ============

storage_manager = StorageManager()
orchestrator = DubbingOrchestrator()

# ============ App Setup ============

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Modern lifespan management for startup and shutdown"""
    logger.info(f"Agent IA Autonome starting in {settings.DEPLOYMENT_ENV} mode...")
    yield
    logger.info("Agent IA Autonome shutting down...")

# Initialize FastAPI app
app = FastAPI(
    title="Agent IA Autonome",
    description="Multilingual voice dubbing platform with AI pipeline",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware with production-aware origins
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in ALLOWED_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Inject security headers into all responses"""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

# Pre-rendered health response for performance
HEALTH_DATA = json.dumps({
    "status": "healthy",
    "version": "1.0.0",
    "environment": settings.DEPLOYMENT_ENV
})

# ============ Upload State (In-memory for prototype) ============
upload_sessions: Dict[str, UploadSession] = {}

# ============ Routes ============

@app.get("/health", responses={200: {"model": HealthResponse}})
async def health_check():
    """Health check endpoint - optimized with pre-rendered JSON"""
    return Response(content=HEALTH_DATA, media_type="application/json")

@app.post("/task/create", response_model=TaskResponse, dependencies=[Depends(verify_api_key)])
async def create_task(task: Task):
    """Create a new task for the agent"""
    try:
        logger.info(f"Creating task: {task.title}")
        return TaskResponse(
            success=True,
            message="Task created successfully",
            task_id=task.id,
            status="pending"
        )
    except Exception:
        logger.exception("Error creating task")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/task/{task_id}", dependencies=[Depends(verify_api_key)])
async def get_task(task_id: str):
    """Get task status"""
    try:
        logger.info(f"Fetching task: {task_id}")
        return {
            "task_id": task_id,
            "status": "pending",
            "progress": 0
        }
    except Exception:
        logger.exception(f"Error retrieving task: {task_id}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/tasks", dependencies=[Depends(verify_api_key)])
async def list_tasks():
    """List all tasks"""
    try:
        logger.info("Listing all tasks")
        return {
            "tasks": [],
            "total": 0
        }
    except Exception:
        logger.exception("Error listing tasks")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/execute", dependencies=[Depends(verify_api_key)])
async def execute_task(task_id: str):
    """Execute a task"""
    try:
        logger.info(f"Executing task: {task_id}")
        return {
            "success": True,
            "message": "Task execution started",
            "task_id": task_id
        }
    except Exception:
        logger.exception(f"Error executing task: {task_id}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ============ Upload Endpoints ============

@app.post("/upload/start", response_model=UploadSession)
async def start_upload(
    filename: str,
    total_size: int,
    chunk_size: int,
    user_id: str = Depends(get_active_user)
):
    """Initialize a chunked upload session"""
    total_chunks = (total_size + chunk_size - 1) // chunk_size
    session = UploadSession(
        filename=filename,
        total_size=total_size,
        chunk_size=chunk_size,
        total_chunks=total_chunks,
        user_id=user_id
    )
    upload_sessions[session.upload_id] = session
    logger.info(f"Started upload {session.upload_id} for user {user_id}")
    return session

@app.post("/upload/chunk/{upload_id}/{chunk_index}")
async def upload_chunk(
    upload_id: str,
    chunk_index: int,
    request: Request,
    user_id: str = Depends(get_active_user)
):
    """Upload a single file chunk"""
    if upload_id not in upload_sessions:
        raise HTTPException(status_code=404, detail="Upload session not found")

    session = upload_sessions[upload_id]
    if session.user_id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized upload access")

    chunk_data = await request.body()
    await storage_manager.save_chunk(upload_id, chunk_index, chunk_data)

    if chunk_index not in session.uploaded_chunks:
        session.uploaded_chunks.append(chunk_index)

    return {"message": f"Chunk {chunk_index} uploaded"}

@app.post("/upload/complete/{upload_id}")
async def complete_upload(upload_id: str, user_id: str = Depends(get_active_user)):
    """Finalize chunked upload and assemble file"""
    if upload_id not in upload_sessions:
        raise HTTPException(status_code=404, detail="Upload session not found")

    session = upload_sessions[upload_id]
    if len(session.uploaded_chunks) != session.total_chunks:
        raise HTTPException(status_code=400, detail="Missing chunks")

    file_path = await storage_manager.assemble_file(
        user_id, upload_id, session.filename, session.total_chunks
    )

    # Cleanup session
    del upload_sessions[upload_id]

    return {"message": "Upload complete", "file_path": file_path}

# ============ GDPR & User Data Endpoints ============

@app.get("/user/data", response_model=UserData)
async def get_user_data(user_id: str = Depends(get_active_user)):
    """Retrieve all data associated with the user (GDPR Right of Access)"""
    files = storage_manager.list_user_files(user_id)
    jobs = [job_id for job_id, job in orchestrator.jobs.items() if job.user_id == user_id]
    return UserData(user_id=user_id, files=files, jobs=jobs)

@app.delete("/user/data")
async def delete_user_data(user_id: str = Depends(get_active_user)):
    """Delete all user data (GDPR Right to be Forgotten)"""
    storage_manager.delete_user_data(user_id)
    # Clear jobs from orchestrator memory
    jobs_to_delete = [job_id for job_id, job in orchestrator.jobs.items() if job.user_id == user_id]
    for job_id in jobs_to_delete:
        del orchestrator.jobs[job_id]

    return {"message": f"All data for user {user_id} has been deleted"}

@app.post("/user/consent")
async def update_consent(consent: GDPRConsent, user_id: str = Depends(get_active_user)):
    """Update user consent for biometric data processing"""
    if consent.user_id != user_id:
         raise HTTPException(status_code=403, detail="Cannot update consent for another user")
    logger.info(f"Consent updated for user {user_id}: {consent.consent_given}")
    return {"message": "Consent updated successfully"}

# ============ Dubbing Pipeline Endpoints ============

@app.post("/dub", response_model=DubbingJob)
async def create_dubbing_job(
    request: DubbingRequest,
    background_tasks: BackgroundTasks,
    filename: str,
    user_id: str = Depends(get_active_user)
):
    """Start a new dubbing job for an already uploaded file"""
    if not request.gdpr_consent:
        raise HTTPException(status_code=400, detail="GDPR consent for biometric data is required")

    # Check if file exists in user directory
    user_files = storage_manager.list_user_files(user_id)
    if filename not in user_files:
         raise HTTPException(status_code=404, detail="Input file not found in your storage")

    input_file_path = str(storage_manager._get_user_dir(user_id) / filename)

    job = DubbingJob(
        user_id=user_id,
        input_file=input_file_path,
        target_language=request.target_language,
        voice_model=request.voice_model
    )

    orchestrator.jobs[job.job_id] = job

    # Run pipeline in background
    background_tasks.add_task(orchestrator.run_pipeline, job)

    return job

@app.get("/dub/{job_id}", response_model=DubbingJob)
async def get_dubbing_status(job_id: str, user_id: str = Depends(get_active_user)):
    """Retrieve status and metrics for a dubbing job"""
    if job_id not in orchestrator.jobs:
        raise HTTPException(status_code=404, detail="Dubbing job not found")

    job = orchestrator.jobs[job_id]
    if job.user_id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized job access")

    return job

# ============ Main ============

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        workers=settings.API_WORKERS,
        reload=settings.DEPLOYMENT_ENV == "development"
    )
