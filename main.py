#!/usr/bin/env python3
"""
Agent IA Autonome - Main Application
Autonomous AI Agent capable of executing tasks on demand
Now enhanced with Multilingual Dubbing Platform features.
"""

import os
import logging
import secrets
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, Security, UploadFile, File, Form, BackgroundTasks
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

        # Security Safeguard: Prevent default API key in production
        if self.DEPLOYMENT_ENV == "production" and self.REQUIRE_API_KEY and self.API_KEY == "default_secret_key":
            raise ValueError("SECURITY ALERT: Default API key cannot be used in production environment.")

settings = Settings()

# ============ Security ============

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def verify_api_key(header_value: str = Security(api_key_header)):
    """Validate the API key from the header if required - uses constant-time comparison"""
    if settings.REQUIRE_API_KEY:
        if not header_value or not secrets.compare_digest(header_value, settings.API_KEY):
            logger.warning("Invalid or missing API key provided")
            raise HTTPException(
                status_code=403,
                detail="Could not validate credentials"
            )
    return header_value

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
    description="Multilingual voice dubbing platform with AI microservices integration.",
    version="1.1.0",
    lifespan=lifespan
)

# Add CORS middleware - Restricted in production
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
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
    message: str
    job_id: str

# ============ Routes ============

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.1.0",
        "environment": settings.DEPLOYMENT_ENV
    }

@app.post("/dub", response_model=DubbingResponse, dependencies=[Depends(verify_api_key)])
async def start_dubbing(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    target_lang: str = Form(...),
    voice_id: str = Form("default"),
    gdpr_consent: bool = Form(...)
):
    """
    Start the dubbing pipeline for an uploaded media file.
    Enforces GDPR consent and handles large files via chunked storage.
    """
    if not gdpr_consent:
        raise HTTPException(status_code=400, detail="GDPR consent is mandatory for biometric voice processing.")

    # Validate file size (example: 700MB limit)
    # Note: Real size check usually happens at proxy level or by reading headers

    job_id = storage_manager.generate_job_id()

    try:
        # Save file to disk in chunks
        file_path = await storage_manager.save_upload(file, job_id)

        # Offload pipeline processing to background tasks
        background_tasks.add_task(
            orchestrator.run_pipeline,
            job_id,
            file_path,
            target_lang,
            voice_id
        )

        return DubbingResponse(
            success=True,
            message="Dubbing pipeline initiated successfully.",
            job_id=job_id
        )
    except Exception as e:
        logger.exception("Error starting dubbing job")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.delete("/user/data", dependencies=[Depends(verify_api_key)])
async def delete_user_data():
    """GDPR 'Right to be forgotten' - Clears all uploaded media."""
    try:
        storage_manager.clear_user_data()
        return {"success": True, "message": "All user media data has been cleared."}
    except Exception as e:
        logger.exception("Error deleting user data")
        raise HTTPException(status_code=500, detail="Internal server error")

# ============ Original Task Routes ============

@app.post("/task/create", response_model=TaskResponse, dependencies=[Depends(verify_api_key)])
async def create_task(task: Task):
    """Create a new task for the agent"""
    try:
        logger.info(f"Creating task: {task.title}")
        return TaskResponse(
            success=True,
            message="Task created successfully",
            task_id="task_123",
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

# ============ Main ============

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        workers=settings.API_WORKERS,
        reload=settings.DEPLOYMENT_ENV == "development"
    )
