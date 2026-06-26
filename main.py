#!/usr/bin/env python3
"""
Agent IA Autonome - Main Application
Autonomous AI Agent capable of executing tasks on demand
"""

import os
import logging
import re
import secrets
import json
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, Security, Response, BackgroundTasks, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional, List
import yaml
import aiofiles
from src.orchestrator import DubbingOrchestrator
from src.storage import LocalStorageService
from dotenv import load_dotenv
import uvicorn

# Load environment variables from .env
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_config(config_path="config.yaml"):
    """Load configuration from YAML with environment variable substitution"""
    if not os.path.exists(config_path):
        return {}

    with open(config_path, 'r') as f:
        content = f.read()

    # Replace ${VAR:default} or ${VAR} with environment variables
    pattern = re.compile(r'\${(\w+)(?::([^}]*))?}')

    def replace_match(match):
        var_name = match.group(1)
        default_value = match.group(2) if match.group(2) is not None else ""
        return os.getenv(var_name, default_value)

    content = pattern.sub(replace_match, content)
    return yaml.safe_load(content)

# ============ Settings ============

class Settings:
    """Cached settings from config.yaml and environment variables"""
    def __init__(self):
        config = load_config()
        app_config = config.get("app", {})
        server_config = config.get("server", {})
        security_config = config.get("security", {})

        self.DEPLOYMENT_ENV = os.getenv("DEPLOYMENT_ENV", app_config.get("environment", "development"))
        self.API_HOST = os.getenv("API_HOST", server_config.get("host", "0.0.0.0"))
        self.API_PORT = int(os.getenv("API_PORT", server_config.get("port", 8000)))
        self.API_WORKERS = int(os.getenv("API_WORKERS", server_config.get("workers", 1)))

        self.REQUIRE_API_KEY = os.getenv("REQUIRE_API_KEY", str(security_config.get("require_api_key", "false"))).lower() == "true"
        self.API_KEY = os.getenv("API_KEY", "default_secret_key")

settings = Settings()

# ============ Security ============

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

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

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Mock OAuth2/JWT verification system"""
    if not token and settings.DEPLOYMENT_ENV == "production":
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # In a real implementation, we would verify the JWT token here
    return {"user_id": "user_123", "email": "user@example.com"}

# ============ App Setup ============

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
storage_service = LocalStorageService(UPLOAD_DIR)
orchestrator = DubbingOrchestrator(storage_service)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Modern lifespan management for startup and shutdown"""
    logger.info("Multilingual Voice Dubbing Platform starting...")
    # TODO: Initialize connections, load models, etc.
    yield
    logger.info("Multilingual Voice Dubbing Platform shutting down...")
    # TODO: Close connections, save state, etc.

# Initialize FastAPI app
app = FastAPI(
    title="Multilingual Voice Dubbing Platform",
    description="Microservices-based pipeline for STT, MT, TTS, and LipSync",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,  # Security: must be False when allow_origins is ["*"]
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

# ============ Pre-rendered Responses ============

HEALTH_RESPONSE_JSON = json.dumps({
    "status": "healthy",
    "version": "1.0.0",
    "environment": settings.DEPLOYMENT_ENV
})

# ============ Routes ============

@app.get("/health", responses={200: {"model": HealthResponse}})
async def health_check():
    """Optimized health check endpoint returning pre-rendered JSON"""
    return Response(
        content=HEALTH_RESPONSE_JSON,
        media_type="application/json"
    )

@app.post("/task/create", response_model=TaskResponse, dependencies=[Depends(verify_api_key), Depends(get_current_user)])
async def create_task(task: Task):
    """Create a new task for the agent"""
    try:
        logger.info(f"Creating task: {task.title}")
        # TODO: Implement task creation logic
        return TaskResponse(
            success=True,
            message="Task created successfully",
            task_id="task_123",
            status="pending"
        )
    except Exception:
        logger.exception("Error creating task")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/task/{task_id}", dependencies=[Depends(verify_api_key), Depends(get_current_user)])
async def get_task(task_id: str):
    """Get task status"""
    try:
        logger.info(f"Fetching task: {task_id}")
        # TODO: Implement task retrieval logic
        return {
            "task_id": task_id,
            "status": "pending",
            "progress": 0
        }
    except Exception:
        logger.exception(f"Error retrieving task: {task_id}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/tasks", dependencies=[Depends(verify_api_key), Depends(get_current_user)])
async def list_tasks():
    """List all tasks"""
    try:
        logger.info("Listing all tasks")
        # TODO: Implement tasks listing logic
        return {
            "tasks": [],
            "total": 0
        }
    except Exception:
        logger.exception("Error listing tasks")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/execute", dependencies=[Depends(verify_api_key), Depends(get_current_user)])
async def execute_task(task_id: str):
    """Execute a task"""
    try:
        logger.info(f"Executing task: {task_id}")
        # TODO: Implement task execution logic
        return {
            "success": True,
            "message": "Task execution started",
            "task_id": task_id
        }
    except Exception:
        logger.exception(f"Error executing task: {task_id}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/dub", dependencies=[Depends(verify_api_key), Depends(get_current_user)])
async def dub_media(
    background_tasks: BackgroundTasks,
    file: UploadFile,
    target_language: str = Form(...),
    gdpr_consent: bool = Form(...)
):
    """Dubbing endpoint - handles large file uploads and initiates the pipeline"""
    if not gdpr_consent:
        raise HTTPException(status_code=400, detail="GDPR consent is mandatory for biometric data processing")

    # Validate file extension
    allowed_extensions = {".mp4", ".avi", ".mp3", ".wav"}
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Unsupported file extension: {file_ext}")

    # Generate unique ID for the dubbing job
    job_id = str(uuid.uuid4())
    file_ext = os.path.splitext(file.filename)[1].lower()
    safe_filename = f"{job_id}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    output_path = os.path.join(UPLOAD_DIR, f"dubbed_{safe_filename}")

    try:
        # Save file using aiofiles for non-blocking I/O
        async with aiofiles.open(file_path, 'wb') as out_file:
            # Check file size (700MB limit)
            size = 0
            while content := await file.read(1024 * 1024):  # Read in chunks
                size += len(content)
                if size > 700 * 1024 * 1024:
                    raise HTTPException(status_code=413, detail="File too large (max 700MB)")
                await out_file.write(content)

        # Offload pipeline processing to BackgroundTasks
        background_tasks.add_task(
            orchestrator.run_pipeline,
            file_path,
            target_language,
            output_path
        )

        return {
            "success": True,
            "message": "Dubbing process initiated",
            "job_id": job_id,
            "status": "processing"
        }
    except HTTPException:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise
    except Exception as e:
        logger.error(f"Error initiating dubbing: {str(e)}")
        if os.path.exists(file_path):
            os.remove(file_path)
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
