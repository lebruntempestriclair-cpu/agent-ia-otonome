#!/usr/bin/env python3
"""
Agent IA Autonome - Main Application
Autonomous AI Agent capable of executing tasks on demand
"""

import os
import json
import logging
import uuid
import tempfile
import secrets
import shutil
import base64
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, Security, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional, List
import uvicorn

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
        self.OAUTH2_SIMULATED_TOKEN = os.getenv("OAUTH2_SIMULATED_TOKEN", "simulated_valid_token")
        self.DEPLOYMENT_ENV = os.getenv("DEPLOYMENT_ENV", "development")
        self.API_HOST = os.getenv("API_HOST", "0.0.0.0")
        self.API_PORT = int(os.getenv("API_PORT", 8000))
        self.API_WORKERS = int(os.getenv("API_WORKERS", 1))

settings = Settings()

# ============ Models ============

class ChunkUpload(BaseModel):
    session_id: str
    chunk_index: int
    data: str  # Base64 encoded or raw string for simulation

class FinalizeUpload(BaseModel):
    session_id: str
    file_name: str

class Task(BaseModel):
    id: Optional[str] = None
    title: str
    description: str
    source_language: Optional[str] = None
    target_language: Optional[str] = None
    voice_id: Optional[str] = None
    file_url: Optional[str] = None
    priority: int = 1
    status: str = "pending"
    progress: int = 0
    wer: Optional[float] = None  # Word Error Rate (STT quality)
    mos: Optional[float] = None  # Mean Opinion Score (TTS quality)

class TaskResponse(BaseModel):
    success: bool
    message: str
    task_id: Optional[str] = None
    status: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str

# ============ Services ============

class StorageService:
    """Simulated Object Storage Service using disk to handle large chunked uploads"""
    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = upload_dir
        self.stored_files = {}     # {file_id: metadata}
        os.makedirs(self.upload_dir, exist_ok=True)

    def _get_session_dir(self, session_id: str) -> str:
        # Sanitize session_id to prevent path traversal
        safe_session_id = os.path.basename(session_id)
        return os.path.join(self.upload_dir, safe_session_id)

    def add_chunk(self, session_id: str, chunk_index: int, data: bytes):
        session_dir = self._get_session_dir(session_id)
        os.makedirs(session_dir, exist_ok=True)
        chunk_path = os.path.join(session_dir, f"chunk_{chunk_index:05d}")
        with open(chunk_path, "wb") as f:
            f.write(data)
        logger.info(f"Chunk {chunk_index} saved to {chunk_path}")

    def finalize_upload(self, session_id: str, file_name: str) -> str:
        session_dir = self._get_session_dir(session_id)
        if not os.path.exists(session_dir):
            raise ValueError("Invalid session ID or no chunks uploaded")

        # Sanitize identifiers to prevent path traversal
        safe_session_id = os.path.basename(session_id)
        safe_file_name = os.path.basename(file_name)

        file_id = f"file_{safe_session_id}"
        final_path = os.path.join(self.upload_dir, f"{file_id}_{safe_file_name}")

        # Reassemble chunks
        chunk_files = sorted(os.listdir(session_dir))
        file_size = 0
        with open(final_path, "wb") as outfile:
            for cf in chunk_files:
                chunk_path = os.path.join(session_dir, cf)
                with open(chunk_path, "rb") as infile:
                    chunk_data = infile.read()
                    outfile.write(chunk_data)
                    file_size += len(chunk_data)

        # Cleanup session directory
        shutil.rmtree(session_dir)

        self.stored_files[file_id] = {
            "name": file_name,
            "size": file_size,
            "url": f"s3://bucket/{file_id}/{file_name}",
            "local_path": final_path
        }
        logger.info(f"File {file_name} finalized on disk. Total size: {file_size} bytes")
        return self.stored_files[file_id]["url"]

storage_service = StorageService()

# ============ Persistence ============

TASKS_FILE = "tasks.json"
tasks_db = {}  # {task_id: Task}

def load_tasks():
    """Load tasks from JSON file at startup"""
    global tasks_db
    if os.path.exists(TASKS_FILE):
        try:
            with open(TASKS_FILE, "r") as f:
                data = json.load(f)
                tasks_db = {tid: Task(**tval) for tid, tval in data.items()}
            logger.info(f"Loaded {len(tasks_db)} tasks from {TASKS_FILE}")
        except Exception:
            logger.exception(f"Error loading {TASKS_FILE}")
            tasks_db = {}
    else:
        logger.info(f"{TASKS_FILE} not found, starting with empty DB")

def save_tasks():
    """Save tasks to JSON file using atomic write"""
    try:
        data = {tid: task.model_dump() for tid, task in tasks_db.items()}
        fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(TASKS_FILE)) or ".")
        with os.fdopen(fd, 'w') as f:
            json.dump(data, f, indent=4)
        os.replace(temp_path, TASKS_FILE)
    except Exception:
        logger.exception("Error saving tasks")

async def _simulate_stt(task: Task):
    logger.info(f"Task {task.id}: STT processing...")
    task.status = "transcribing"
    task.progress = 15
    save_tasks()
    await asyncio.sleep(2)

async def _simulate_mt(task: Task):
    logger.info(f"Task {task.id}: Translating text to {task.target_language}...")
    task.status = "translating"
    task.progress = 40
    save_tasks()
    await asyncio.sleep(1)

async def _simulate_tts(task: Task):
    logger.info(f"Task {task.id}: Synthesizing voice (ID: {task.voice_id})...")
    task.status = "synthesizing"
    task.progress = 70
    save_tasks()
    await asyncio.sleep(2)

async def _simulate_lipsync(task: Task):
    logger.info(f"Task {task.id}: Performing lip-sync synchronization...")
    task.status = "synchronizing"
    task.progress = 90
    save_tasks()
    await asyncio.sleep(3)

async def _calculate_metrics(task: Task):
    logger.info(f"Task {task.id}: Calculating quality metrics (WER/MOS)...")
    task.wer = round(secrets.SystemRandom().uniform(0.02, 0.08), 4)
    task.mos = round(secrets.SystemRandom().uniform(3.8, 4.8), 1)
    save_tasks()

async def run_dubbing_pipeline(task_id: str):
    """Sequential dubbing pipeline using modular simulated services"""
    if task_id not in tasks_db:
        return

    task = tasks_db[task_id]
    try:
        await _simulate_stt(task)
        await _simulate_mt(task)
        await _simulate_tts(task)
        await _simulate_lipsync(task)
        await _calculate_metrics(task)

        task.status = "completed"
        task.progress = 100
        save_tasks()
        logger.info(f"Task {task_id}: Dubbing pipeline successfully finished")

    except Exception:
        logger.exception(f"Error in dubbing pipeline for task {task_id}")
        task.status = "failed"
        save_tasks()

# ============ Security ============

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

async def verify_api_key(
    header_value: str = Security(api_key_header),
    token: str = Security(oauth2_scheme)
):
    """Hybrid authentication: validates API Key or simulated JWT token"""
    if not settings.REQUIRE_API_KEY:
        return True

    # 1. Check API Key
    if header_value and secrets.compare_digest(header_value, settings.API_KEY):
        return header_value

    # 2. Check simulated JWT (for OAuth2 simulation)
    if token == settings.OAUTH2_SIMULATED_TOKEN:
        return "oauth_user"

    logger.warning("Invalid or missing credentials provided")
    raise HTTPException(
        status_code=403,
        detail="Could not validate credentials"
    )

# ============ App Setup ============

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Modern lifespan management for startup and shutdown"""
    logger.info("Agent IA Autonome starting...")
    load_tasks()
    yield
    logger.info("Agent IA Autonome shutting down...")
    save_tasks()

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

# ============ Routes ============

@app.post("/upload/chunk", dependencies=[Depends(verify_api_key)])
async def upload_chunk(chunk: ChunkUpload):
    """Upload a file chunk (Base64 encoded)"""
    try:
        # Expecting Base64 for safety with binary data over JSON
        decoded_data = base64.b64decode(chunk.data)
        storage_service.add_chunk(chunk.session_id, chunk.chunk_index, decoded_data)
        return {"success": True, "message": f"Chunk {chunk.chunk_index} received"}
    except Exception:
        logger.exception("Error uploading chunk")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/upload/finalize", dependencies=[Depends(verify_api_key)])
async def finalize_upload(payload: FinalizeUpload):
    """Finalize chunked upload and get file URL"""
    try:
        file_url = storage_service.finalize_upload(payload.session_id, payload.file_name)
        return {"success": True, "file_url": file_url}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        logger.exception("Error finalizing upload")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health", responses={200: {"model": HealthResponse}})
async def health_check():
    """Health check endpoint - optimized by returning raw dict to bypass Pydantic overhead"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.DEPLOYMENT_ENV
    }

@app.post("/task/create", response_model=TaskResponse, dependencies=[Depends(verify_api_key)])
async def create_task(task: Task):
    """Create a new task for the agent"""
    try:
        task_id = str(uuid.uuid4())
        task.id = task_id
        tasks_db[task_id] = task
        save_tasks()
        logger.info(f"Created task: {task_id} - {task.title}")
        return {
            "success": True,
            "message": "Task created successfully",
            "task_id": task_id,
            "status": task.status
        }
    except Exception:
        logger.exception("Error creating task")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/task/{task_id}", dependencies=[Depends(verify_api_key)])
async def get_task(task_id: str):
    """Get task status"""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")

    task = tasks_db[task_id]
    return {
        "task_id": task.id,
        "title": task.title,
        "status": task.status,
        "progress": task.progress,
        "source_language": task.source_language,
        "target_language": task.target_language,
        "voice_id": task.voice_id,
        "file_url": task.file_url
    }

@app.get("/tasks", dependencies=[Depends(verify_api_key)])
async def list_tasks():
    """List all tasks"""
    try:
        return {
            "tasks": [t.model_dump() for t in tasks_db.values()],
            "total": len(tasks_db)
        }
    except Exception:
        logger.exception("Error listing tasks")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/execute", dependencies=[Depends(verify_api_key)])
async def execute_task(task_id: str, background_tasks: BackgroundTasks):
    """Execute the dubbing pipeline for a task"""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")

    task = tasks_db[task_id]
    if task.status == "completed":
        return {"success": True, "message": "Task already completed", "task_id": task_id}

    if task.status != "pending" and task.status != "failed":
        return {"success": True, "message": "Task already in progress", "task_id": task_id}

    background_tasks.add_task(run_dubbing_pipeline, task_id)
    return {
        "success": True,
        "message": "Dubbing pipeline execution started",
        "task_id": task_id
    }

# ============ Main ============

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        workers=settings.API_WORKERS,
        reload=settings.DEPLOYMENT_ENV == "development"
    )
