#!/usr/bin/env python3
"""
Agent IA Autonome - Main Application
Autonomous AI Agent capable of executing tasks on demand
Extended for Multilingual Voice Dubbing Platform
"""

import os
import logging
import secrets
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, Security, UploadFile, File, Form, BackgroundTasks, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import json

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

async def get_current_user():
    """Mock OAuth2/JWT verification system."""
    return {"user_id": "user_456", "email": "user@example.com"}

# ============ App Setup ============

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Modern lifespan management for startup and shutdown"""
    logger.info("Agent IA Autonome starting...")
    # Initialize platform managers
    app.state.storage = StorageManager()
    app.state.orchestrator = DubbingOrchestrator()
    yield
    logger.info("Agent IA Autonome shutting down...")

# Pre-rendered health response for performance
HEALTH_DATA = json.dumps({
    "status": "healthy",
    "version": "1.0.0",
    "environment": settings.DEPLOYMENT_ENV
}).encode("utf-8")

# Initialize FastAPI app
app = FastAPI(
    title="Agent IA Autonome",
    description="Multilingual Voice Dubbing Platform",
    version="1.0.0",
    lifespan=lifespan
)

# Define allowed origins for production
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://agent-ia-otonome.vercel.app",  # Example frontend
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if settings.DEPLOYMENT_ENV == "production" else ["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["X-API-Key", "Content-Type", "Authorization"],
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

# ============ Routes ============

@app.get("/health", responses={200: {"model": HealthResponse}})
async def health_check():
    """Health check endpoint - optimized by returning raw Response object"""
    return Response(content=HEALTH_DATA, media_type="application/json")

@app.post("/dub", dependencies=[Depends(verify_api_key)])
async def dub_media(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    target_lang: str = Form(...),
    voice_id: str = Form(...),
    gdpr_consent: bool = Form(...),
    user: dict = Depends(get_current_user)
):
    """
    Main dubbing endpoint.
    Enforces file size limit, GDPR consent, and offloads processing to background tasks.
    """
    if not gdpr_consent:
        raise HTTPException(status_code=400, detail="GDPR consent is mandatory for biometric data processing")

    allowed_extensions = {'.mp4', '.avi', '.mp3', '.wav'}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Unsupported file extension: {ext}")

    try:
        # Save file using StorageManager (chunked, size-limited)
        file_path = await app.state.storage.save_upload(file, user["user_id"])

        job_id = os.path.basename(file_path).split('.')[0]

        # Offload pipeline to BackgroundTasks
        background_tasks.add_task(
            app.state.orchestrator.run_pipeline,
            job_id, file_path, target_lang, voice_id
        )

        return {
            "success": True,
            "job_id": job_id,
            "message": "Dubbing pipeline started successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=413, detail=str(e))
    except Exception as e:
        logger.exception("Error in dubbing endpoint")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.delete("/user/data", dependencies=[Depends(verify_api_key)])
async def delete_user_data(user: dict = Depends(get_current_user)):
    """GDPR 'Right to be forgotten' implementation."""
    try:
        await app.state.storage.delete_user_data(user["user_id"])
        return {"success": True, "message": "User media data cleared"}
    except Exception as e:
        logger.exception(f"Error deleting data for user {user['user_id']}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ============ Legacy Task Routes ============

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
    except HTTPException:
        raise
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
    except HTTPException:
        raise
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
    except HTTPException:
        raise
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
    except HTTPException:
        raise
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
