#!/usr/bin/env python3
"""
Agent IA Autonome - Main Application
Autonomous AI Agent capable of executing tasks on demand
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, Security, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import Optional, List, Dict
import uvicorn
import json
import secrets
import tempfile
import time

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

        # CORS Origins parsing
        cors_raw = os.getenv("CORS_ORIGINS", "*")
        self.CORS_ORIGINS = [o.strip() for o in cors_raw.split(",")] if cors_raw else ["*"]

settings = Settings()

# ============ Storage & Persistence ============

TASKS_FILE = "tasks.json"

class StorageService:
    """Simulates interaction with Object Storage (S3/GCS)"""
    def __init__(self):
        self.storage = {}

    def upload_file(self, file_content: bytes, filename: str) -> str:
        """Simulate a multipart/chunked file upload"""
        file_id = f"file_{secrets.token_hex(4)}"
        self.storage[file_id] = {
            "filename": filename,
            "content_size": len(file_content)
        }
        logger.info(f"File {filename} uploaded to storage as {file_id}")
        return f"https://storage.example.com/{file_id}"

storage_service = StorageService()

def load_tasks() -> Dict[str, dict]:
    """Load tasks from the persistent JSON file"""
    if not os.path.exists(TASKS_FILE):
        return {}
    try:
        with open(TASKS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        logger.exception("Error loading tasks from file")
        return {}

def save_tasks(tasks: Dict[str, dict]):
    """Save tasks to the persistent JSON file using atomic write"""
    try:
        fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(TASKS_FILE)))
        with os.fdopen(fd, 'w') as f:
            json.dump(tasks, f, indent=4)
        os.replace(temp_path, TASKS_FILE)
    except Exception:
        logger.exception("Error saving tasks to file")

# Initialize tasks database in memory for fast access
tasks_db = load_tasks()

# ============ Security ============

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def verify_api_key(header_value: str = Security(api_key_header)):
    """Validate the API key from the header if required using constant-time comparison"""
    if settings.REQUIRE_API_KEY:
        # Securely fail if API_KEY is not set but required
        if not settings.API_KEY or settings.API_KEY == "default_secret_key":
            logger.critical("REQUIRE_API_KEY is True but API_KEY is not properly configured")
            raise HTTPException(status_code=500, detail="Internal server error")

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
# Starlette's CORSMiddleware raises RuntimeError if allow_credentials=True and origins include '*'
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials="*" not in settings.CORS_ORIGINS,
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
    source_language: Optional[str] = None
    target_language: Optional[str] = None
    voice_id: Optional[str] = None
    file_url: Optional[str] = None

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
    try:
        return {
            "status": "healthy",
            "version": "1.0.0",
            "environment": settings.DEPLOYMENT_ENV
        }
    except HTTPException:
        raise
    except Exception:
        logger.exception("Health check failed")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/task/create", responses={200: {"model": TaskResponse}}, dependencies=[Depends(verify_api_key)])
async def create_task(task: Task):
    """Create a new task for the agent - optimized to return raw dict"""
    try:
        logger.info(f"Creating task: {task.title}")
        task_id = f"task_{secrets.token_hex(4)}"

        task_dict = task.model_dump()
        task_dict["id"] = task_id
        task_dict["progress"] = 0
        tasks_db[task_id] = task_dict
        save_tasks(tasks_db)

        return {
            "success": True,
            "message": "Task created successfully",
            "task_id": task_id,
            "status": "pending"
        }
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
        if task_id not in tasks_db:
            raise HTTPException(status_code=404, detail="Task not found")
        return tasks_db[task_id]
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
            "tasks": list(tasks_db.values()),
            "total": len(tasks_db)
        }
    except HTTPException:
        raise
    except Exception:
        logger.exception("Error listing tasks")
        raise HTTPException(status_code=500, detail="Internal server error")

def run_dubbing_pipeline(task_id: str):
    """Simulates a sequential dubbing pipeline as a background process"""
    try:
        if task_id not in tasks_db:
            logger.error(f"Background task failed: Task {task_id} not found")
            return

        task = tasks_db[task_id]
        stages = [
            ("STT (Transcription)", 25),
            ("MT (Translation)", 50),
            ("TTS (Synthesis)", 75),
            ("LipSync (Synchronization)", 100)
        ]

        task["status"] = "processing"

        for stage_name, progress in stages:
            logger.info(f"Task {task_id}: Starting {stage_name}...")
            task["progress"] = progress
            task["current_stage"] = stage_name
            save_tasks(tasks_db)
            time.sleep(0.5)  # Simulate some processing time

        task["status"] = "completed"
        save_tasks(tasks_db)
        logger.info(f"Task {task_id} pipeline completed")
    except Exception:
        logger.exception(f"Error in background pipeline for task {task_id}")
        if task_id in tasks_db:
            tasks_db[task_id]["status"] = "failed"
            save_tasks(tasks_db)

@app.post("/execute", dependencies=[Depends(verify_api_key)])
async def execute_task(task_id: str, background_tasks: BackgroundTasks):
    """Execute a task - simulates an asynchronous dubbing pipeline"""
    try:
        logger.info(f"Executing task: {task_id}")
        if task_id not in tasks_db:
            raise HTTPException(status_code=404, detail="Task not found")

        if tasks_db[task_id]["status"] == "processing":
            return {
                "success": False,
                "message": "Task is already being processed",
                "task_id": task_id
            }

        background_tasks.add_task(run_dubbing_pipeline, task_id)

        return {
            "success": True,
            "message": "Task execution started in background",
            "task_id": task_id,
            "status": "processing"
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
