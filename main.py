#!/usr/bin/env python3
"""
Agent IA Autonome - Main Application
Autonomous AI Agent capable of executing tasks on demand
"""

import os
import re
import yaml
import logging
import secrets
import asyncio
import aiofiles
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, Security, Response, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import Optional, List
import uvicorn

from dotenv import load_dotenv
from src.orchestrator import DubbingOrchestrator

# Load environment variables from .env
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============ Settings ============

def load_config(path: str = "config.yaml"):
    """Load config from YAML with environment variable substitution"""
    if not os.path.exists(path):
        logger.warning(f"Config file {path} not found, using defaults")
        return {}

    with open(path, 'r') as f:
        content = f.read()

    # Replace ${VAR:default} or ${VAR} with environment variables
    pattern = re.compile(r'\$\{(\w+)(?::([^}]*))?\}')

    def replace_env_var(match):
        var_name = match.group(1)
        default_value = match.group(2)
        return os.getenv(var_name, default_value if default_value is not None else match.group(0))

    content = pattern.sub(replace_env_var, content)
    return yaml.safe_load(content)

class Settings:
    """Cached environment variables and config to reduce syscall overhead"""
    def __init__(self):
        config = load_config()

        # Security settings
        security_cfg = config.get("security", {})
        self.REQUIRE_API_KEY = os.getenv("REQUIRE_API_KEY",
                                         str(security_cfg.get("require_api_key", "false"))).lower() == "true"
        self.API_KEY = os.getenv("API_KEY", "default_secret_key")

        # App settings
        app_cfg = config.get("app", {})
        self.DEPLOYMENT_ENV = os.getenv("DEPLOYMENT_ENV", app_cfg.get("environment", "development"))

        # Server settings
        server_cfg = config.get("server", {})
        self.API_HOST = os.getenv("API_HOST", server_cfg.get("host", "0.0.0.0"))
        self.API_PORT = int(os.getenv("API_PORT", server_cfg.get("port", 8000)))
        self.API_WORKERS = int(os.getenv("API_WORKERS", server_cfg.get("workers", 1)))

settings = Settings()
orchestrator = DubbingOrchestrator()

# ============ Security ============

async def get_current_user(header_value: str = Security(APIKeyHeader(name="Authorization", auto_error=False))):
    """
    Mock OAuth2/JWT verification.
    In production, this would validate the token against Google/GCP/Auth0.
    """
    if header_value and header_value.startswith("Bearer "):
        # Mock successful token validation
        return {"email": "user@example.com", "name": "Test User"}
    return None

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

# ============ App Setup ============

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Modern lifespan management for startup and shutdown"""
    logger.info("Agent IA Autonome starting...")
    # TODO: Initialize connections, load models, etc.
    yield
    logger.info("Agent IA Autonome shutting down...")
    # TODO: Close connections, save state, etc.

# Initialize FastAPI app
app = FastAPI(
    title="Agent IA Autonome",
    description="Autonomous AI agent capable of executing tasks",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

class DubResponse(BaseModel):
    success: bool
    message: str
    upload_id: str
    filename: str

# ============ Routes ============

import json
HEALTH_RESPONSE_JSON = json.dumps({
    "status": "healthy",
    "version": "1.0.0",
    "environment": settings.DEPLOYMENT_ENV
})

@app.get("/health", responses={200: {"model": HealthResponse}})
async def health_check():
    """Health check endpoint - optimized to bypass Pydantic using pre-rendered JSON"""
    return Response(content=HEALTH_RESPONSE_JSON, media_type="application/json")

@app.post("/task/create", response_model=TaskResponse, dependencies=[Depends(verify_api_key)])
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

@app.get("/task/{task_id}", dependencies=[Depends(verify_api_key)])
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

@app.get("/tasks", dependencies=[Depends(verify_api_key)])
async def list_tasks(current_user: dict = Depends(get_current_user)):
    """List all tasks - supports optional OAuth user identification"""
    try:
        if current_user:
            logger.info(f"Listing tasks for user: {current_user['email']}")
        else:
            logger.info("Listing all tasks (unauthenticated user)")

        # TODO: Implement tasks listing logic
        return {
            "tasks": [],
            "total": 0,
            "user": current_user["email"] if current_user else "guest"
        }
    except Exception:
        logger.exception("Error listing tasks")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/execute", dependencies=[Depends(verify_api_key)])
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

MAX_FILE_SIZE = 700 * 1024 * 1024  # 700MB
ALLOWED_EXTENSIONS = {".mp4", ".avi", ".mp3", ".wav"}

@app.post("/dub", response_model=DubResponse, dependencies=[Depends(verify_api_key)])
async def dub_media(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    gdpr_consent: bool = Form(...),
    target_language: str = Form(...)
):
    """
    Handle media upload for dubbing with chunked support and GDPR consent.
    This endpoint stores the media and initiates the dubbing pipeline.
    """
    if not gdpr_consent:
        raise HTTPException(
            status_code=400,
            detail="GDPR consent is mandatory for biometric data processing (voice)."
        )

    # Extension validation
    _, ext = os.path.splitext(file.filename)
    if ext.lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file extension. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    try:
        upload_id = secrets.token_hex(8)
        # Sanitize filename
        safe_filename = os.path.basename(file.filename)
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)

        file_path = os.path.join(upload_dir, f"{upload_id}_{safe_filename}")

        # Save file using aiofiles for non-blocking I/O
        total_size = 0
        async with aiofiles.open(file_path, 'wb') as out_file:
            while content := await file.read(1024 * 1024):  # 1MB chunks
                total_size += len(content)
                if total_size > MAX_FILE_SIZE:
                    # Clean up and abort
                    await out_file.close()
                    os.remove(file_path)
                    raise HTTPException(
                        status_code=413,
                        detail=f"File too large. Maximum allowed size is {MAX_FILE_SIZE / (1024*1024)}MB"
                    )
                await out_file.write(content)

        logger.info(f"File {safe_filename} ({total_size} bytes) uploaded successfully. ID: {upload_id}")

        # Trigger the asynchronous dubbing pipeline
        background_tasks.add_task(
            orchestrator.run_pipeline,
            file_path,
            target_language,
            upload_id
        )

        return DubResponse(
            success=True,
            message="Media uploaded and dubbing pipeline initiated.",
            upload_id=upload_id,
            filename=safe_filename
        )
    except Exception:
        logger.exception("Error during media upload/dubbing initiation")
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
