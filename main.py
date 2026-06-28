#!/usr/bin/env python3
"""
Agent IA Autonome - Main Application
Autonomous AI Agent capable of executing tasks on demand
"""

import os
import logging
import re
import yaml
import secrets
import uuid
import aiofiles
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, Security, Header, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import Optional, List, Any
import uvicorn

from src.orchestrator import DubbingOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============ Settings ============

class Settings:
    """Configuration settings with environment variable substitution"""
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)

        # Load core settings from config or env
        security_cfg = self.config.get("security", {})
        self.REQUIRE_API_KEY = str(security_cfg.get("require_api_key", "false")).lower() == "true"
        self.API_KEY = os.getenv("API_KEY", "default_secret_key")

        app_cfg = self.config.get("app", {})
        self.DEPLOYMENT_ENV = os.getenv("DEPLOYMENT_ENV", app_cfg.get("environment", "development"))

        server_cfg = self.config.get("server", {})
        self.API_HOST = os.getenv("API_HOST", server_cfg.get("host", "0.0.0.0"))
        self.API_PORT = int(os.getenv("API_PORT", server_cfg.get("port", 8000)))
        self.API_WORKERS = int(os.getenv("API_WORKERS", server_cfg.get("workers", 1)))

        # Dubbing specific settings
        self.UPLOAD_DIR = "uploads"
        self.MAX_UPLOAD_SIZE = 700 * 1024 * 1024  # 700MB
        self.ALLOWED_EXTENSIONS = {".mp4", ".avi", ".mp3", ".wav"}

        # Security validation
        if self.DEPLOYMENT_ENV == "production" and self.REQUIRE_API_KEY and self.API_KEY == "default_secret_key":
            raise ValueError("Insecure API_KEY 'default_secret_key' is not allowed in production")

    def _load_config(self, path: str) -> dict:
        """Load YAML config and substitute environment variables"""
        if not os.path.exists(path):
            logger.warning(f"Config file not found at {path}, using defaults")
            return {}

        with open(path, "r") as f:
            content = f.read()

        # Substitute ${VAR:default}
        pattern = re.compile(r'\${(\w+):?([^}]*)}')

        def replace(match):
            var_name = match.group(1)
            default_value = match.group(2)
            return os.getenv(var_name, default_value)

        content = pattern.sub(replace, content)
        return yaml.safe_load(content) or {}

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

async def get_current_user(authorization: Optional[str] = Header(None)):
    """Mock OAuth2/JWT verification system"""
    if not authorization:
        # In a real app, we might raise 401 here if we want to force Auth
        # For now, we simulate a guest user if no token provided
        return {"user": "guest", "id": "anonymous"}

    # Mock token validation
    if authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        if token == "valid_token":
            return {"user": "authenticated_user", "id": "user_123"}

    raise HTTPException(status_code=401, detail="Invalid authentication credentials")

# ============ App Setup ============

orchestrator = DubbingOrchestrator()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Modern lifespan management for startup and shutdown"""
    logger.info(f"Agent IA Autonome starting in {settings.DEPLOYMENT_ENV} environment...")
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    yield
    logger.info("Agent IA Autonome shutting down...")

# Initialize FastAPI app
app = FastAPI(
    title="Agent IA Autonome",
    description="Autonomous AI agent capable of executing tasks",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware - Ensure allow_credentials=False when using wildcard origins
cors_origins = settings.config.get("security", {}).get("cors_origins", ["*"])
allow_all_origins = "*" in cors_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=not allow_all_origins, # Security rule: credentials not allowed with wildcard
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

# ============ Routes ============

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint - optimized to return raw dict if needed"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.DEPLOYMENT_ENV
    }

@app.post("/dub", dependencies=[Depends(verify_api_key)])
async def dub_media(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    target_lang: str = Form(...),
    voice_id: str = Form("default"),
    gdpr_consent: bool = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Dubbing pipeline endpoint.
    Handles large file uploads, GDPR consent, and offloads processing to background tasks.
    """
    if not gdpr_consent:
        raise HTTPException(status_code=400, detail="GDPR consent is mandatory for biometric data processing")

    # Validate file extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file extension. Allowed: {settings.ALLOWED_EXTENSIONS}"
        )

    # Generate unique Job ID
    job_id = str(uuid.uuid4())
    safe_filename = f"{job_id}{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)

    try:
        # Save file in chunks using aiofiles to prevent event loop stalls
        async with aiofiles.open(file_path, 'wb') as out_file:
            size = 0
            while content := await file.read(1024 * 1024):  # 1MB chunks
                size += len(content)
                if size > settings.MAX_UPLOAD_SIZE:
                    raise HTTPException(status_code=413, detail="File too large")
                await out_file.write(content)

        logger.info(f"File saved to {file_path} for job {job_id} (size: {size} bytes)")

        # Trigger the pipeline in background
        options = {"voice_id": voice_id, "user_id": current_user["id"]}
        background_tasks.add_task(orchestrator.run_pipeline, job_id, file_path, target_lang, options)

        return {
            "success": True,
            "message": "Dubbing job started",
            "job_id": job_id,
            "status": "processing"
        }

    except HTTPException:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise
    except Exception:
        logger.exception(f"Error initiating dubbing job for {file.filename}")
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/task/create", response_model=TaskResponse, dependencies=[Depends(verify_api_key)])
async def create_task(task: Task, current_user: dict = Depends(get_current_user)):
    """Create a new task for the agent"""
    try:
        logger.info(f"User {current_user['id']} creating task: {task.title}")
        # TODO: Implement task creation logic
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
async def get_task(task_id: str, current_user: dict = Depends(get_current_user)):
    """Get task status"""
    try:
        logger.info(f"User {current_user['id']} fetching task: {task_id}")
        # TODO: Implement task retrieval logic
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
async def list_tasks(current_user: dict = Depends(get_current_user)):
    """List all tasks"""
    try:
        logger.info(f"User {current_user['id']} listing all tasks")
        # TODO: Implement tasks listing logic
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
async def execute_task(task_id: str, current_user: dict = Depends(get_current_user)):
    """Execute a task"""
    try:
        logger.info(f"User {current_user['id']} executing task: {task_id}")
        # TODO: Implement task execution logic
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
