#!/usr/bin/env python3
"""
Plateforme de Doublage Vocal Multilingue - API Principale
Autonomous Dubbing Platform with STT, MT, TTS, and Lip-Sync
"""

import os
import uuid
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, Security, UploadFile, File, Form, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import aiofiles

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
        self.UPLOAD_DIR = "uploads"

        # Ensure upload directory exists
        if not os.path.exists(self.UPLOAD_DIR):
            os.makedirs(self.UPLOAD_DIR)

settings = Settings()

# ============ Security ============

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def verify_api_key(header_value: str = Security(api_key_header)):
    """Validate the API key from the header if required"""
    if settings.REQUIRE_API_KEY:
        if not header_value or header_value != settings.API_KEY:
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
    logger.info("Plateforme de Doublage starts...")
    # Initialize background workers or database connections here
    yield
    logger.info("Plateforme de Doublage shutting down...")

# Initialize FastAPI app
app = FastAPI(
    title="Plateforme de Doublage Vocal Multilingue",
    description="API pour le doublage automatique de vidéos via IA",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False, # Security improvement for wildcard origins
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ Models ============

class DubbingTask(BaseModel):
    id: Optional[str] = None
    title: str
    source_language: str
    target_language: str
    voice_style: str = "neutral"
    media_url: Optional[str] = None
    status: str = "pending"

class DubbingTaskResponse(BaseModel):
    success: bool
    message: str
    task_id: Optional[str] = None
    status: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str

# In-memory storage for demonstration
db_tasks = {}

# ============ Routes ============

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.DEPLOYMENT_ENV
    }

@app.post("/task/create", response_model=DubbingTaskResponse, dependencies=[Depends(verify_api_key)])
async def create_task(task: DubbingTask):
    """Create a new dubbing project"""
    try:
        task_id = str(uuid.uuid4())
        task.id = task_id
        task.status = "pending"
        db_tasks[task_id] = task

        logger.info(f"Creating dubbing task: {task.title} ({task_id})")
        return DubbingTaskResponse(
            success=True,
            message="Dubbing task created successfully",
            task_id=task_id,
            status="pending"
        )
    except Exception:
        logger.exception("Error creating dubbing task")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/task/{task_id}", dependencies=[Depends(verify_api_key)])
async def get_task(task_id: str):
    """Get project status and details"""
    if task_id not in db_tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    return db_tasks[task_id]

@app.get("/tasks", dependencies=[Depends(verify_api_key)])
async def list_tasks():
    """List all projects"""
    return {
        "tasks": list(db_tasks.values()),
        "total": len(db_tasks)
    }

@app.post("/execute", dependencies=[Depends(verify_api_key)])
async def execute_task(task_id: str):
    """Execute the dubbing pipeline for a project"""
    if task_id not in db_tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    try:
        logger.info(f"Executing pipeline for task: {task_id}")
        db_tasks[task_id].status = "processing"
        # In a real app, this would trigger a Celery task
        return {
            "success": True,
            "message": "Dubbing pipeline started",
            "task_id": task_id
        }
    except Exception:
        logger.exception(f"Error executing task: {task_id}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def reassemble_file(task_id: str, total_chunks: int):
    """Background task to reassemble chunks into the final media file"""
    try:
        task_dir = os.path.join(settings.UPLOAD_DIR, task_id)
        final_path = os.path.join(settings.UPLOAD_DIR, f"{task_id}_final.mp4")

        logger.info(f"Reassembling {total_chunks} chunks for task {task_id}...")

        async with aiofiles.open(final_path, 'wb') as final_file:
            for i in range(total_chunks):
                chunk_path = os.path.join(task_dir, f"chunk_{i}")
                async with aiofiles.open(chunk_path, 'rb') as cp:
                    # Stream in chunks of 1MB to avoid loading the whole chunk in RAM
                    while chunk := await cp.read(1024 * 1024):
                        await final_file.write(chunk)

        if task_id in db_tasks:
            db_tasks[task_id].media_url = final_path
            db_tasks[task_id].status = "ready"

        logger.info(f"Reassembly complete for task {task_id}. Final file: {final_path}")
    except Exception:
        logger.exception(f"Critical error during reassembly for task {task_id}")
        if task_id in db_tasks:
            db_tasks[task_id].status = "failed"

@app.post("/upload/chunk", dependencies=[Depends(verify_api_key)])
async def upload_chunk(
    background_tasks: BackgroundTasks,
    task_id: str = Form(...),
    chunk_index: int = Form(...),
    total_chunks: int = Form(...),
    file: UploadFile = File(...)
):
    """Upload a chunk of a media file"""
    if task_id not in db_tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    try:
        task_dir = os.path.join(settings.UPLOAD_DIR, task_id)
        if not os.path.exists(task_dir):
            os.makedirs(task_dir)

        chunk_filename = f"chunk_{chunk_index}"
        chunk_path = os.path.join(task_dir, chunk_filename)

        # Save chunk
        async with aiofiles.open(chunk_path, 'wb') as f:
            while chunk := await file.read(1024 * 1024):
                await f.write(chunk)

        logger.info(f"Received chunk {chunk_index}/{total_chunks} for task {task_id}")

        # Robust check: verify all expected chunk files exist
        all_present = True
        for i in range(total_chunks):
            if not os.path.exists(os.path.join(task_dir, f"chunk_{i}")):
                all_present = False
                break

        if all_present:
            logger.info(f"All chunks verified for task {task_id}. Scheduling reassembly...")
            db_tasks[task_id].status = "assembling"
            background_tasks.add_task(reassemble_file, task_id, total_chunks)

        return {"success": True, "chunk_index": chunk_index}

    except Exception:
        logger.exception(f"Error uploading chunk {chunk_index} for task {task_id}")
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
