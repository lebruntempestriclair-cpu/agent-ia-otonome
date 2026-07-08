#!/usr/bin/env python3
"""
Agent IA Autonome - Main Application
Autonomous AI Agent capable of executing tasks on demand
"""

import os
import re
import yaml
import json
import logging
import asyncio
import aiofiles
import secrets
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, Security, Response, BackgroundTasks, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import Optional, List, Dict
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============ Settings ============

class Settings:
    """Cached environment variables and YAML config to reduce syscall overhead"""
    def __init__(self, config_path: str = "config.yaml"):
        self.DEPLOYMENT_ENV = os.getenv("DEPLOYMENT_ENV", "development")
        self.config = self._load_config(config_path)

        # Security
        security = self.config.get("security", {})
        config_val = security.get("require_api_key")
        env_val = os.getenv("REQUIRE_API_KEY", "false")
        self.REQUIRE_API_KEY = str(config_val if config_val is not None else env_val).lower() == "true"
        self.API_KEY = os.getenv("API_KEY", "default_secret_key")

        # In production, require an API key to be set
        if self.DEPLOYMENT_ENV == "production" and self.REQUIRE_API_KEY and self.API_KEY == "default_secret_key":
            raise ValueError("API_KEY must be set in production environment")

        # Server
        server = self.config.get("server", {})
        self.API_HOST = server.get("host", os.getenv("API_HOST", "0.0.0.0"))
        self.API_PORT = int(server.get("port", os.getenv("API_PORT", 8000)))
        # Maintain at 1 worker per session constraints
        self.API_WORKERS = int(os.getenv("API_WORKERS", 1))

        # Storage
        self.UPLOAD_DIR = "data/uploads"
        self.DB_PATH = os.path.join(self.UPLOAD_DIR, "db.json")
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)

    def _load_config(self, path: str) -> Dict:
        if not os.path.exists(path):
            return {}

        with open(path, "r") as f:
            content = f.read()

        # Environment variable substitution: ${VAR:default}
        pattern = re.compile(r"\${(\w+):?([^}]*)}")

        def replace_env(match):
            var_name = match.group(1)
            default_value = match.group(2)
            return os.getenv(var_name, default_value)

        content = pattern.sub(replace_env, content)
        return yaml.safe_load(content) or {}

settings = Settings()

# Global lock for DB updates
db_lock = asyncio.Lock()

# ============ Security ============

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def verify_api_key(header_value: str = Security(api_key_header)):
    """Validate the API key from the header if required"""
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
    allow_credentials=False, # Wildcard origins cannot be used with credentials
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ DB Management ============

async def get_db() -> Dict:
    if not os.path.exists(settings.DB_PATH):
        return {"uploads": {}, "tasks": {}}
    async with aiofiles.open(settings.DB_PATH, mode='r') as f:
        content = await f.read()
        return json.loads(content)

async def save_db(db: Dict):
    """Save DB state to file - lock should be handled by caller for atomicity"""
    async with aiofiles.open(settings.DB_PATH, mode='w') as f:
        await f.write(json.dumps(db, indent=2))

# ============ Pipeline ============

async def process_dubbing(task_id: str, file_path: str, target_lang: str):
    """Asynchronous dubbing pipeline: STT -> MT -> TTS -> Lip-sync"""
    try:
        async with db_lock:
            db = await get_db()
            db["tasks"][task_id]["status"] = "processing"
            await save_db(db)

        logger.info(f"Starting STT for {task_id}")
        await asyncio.sleep(0.1) # Simulate processing

        logger.info(f"Starting MT for {task_id}")
        await asyncio.sleep(0.1)

        logger.info(f"Starting TTS for {task_id}")
        await asyncio.sleep(0.1)

        logger.info(f"Starting Lip-sync for {task_id}")
        await asyncio.sleep(0.1)

        async with db_lock:
            db = await get_db()
            db["tasks"][task_id]["status"] = "completed"
            db["tasks"][task_id]["progress"] = 100
            db["tasks"][task_id]["result_url"] = f"/downloads/{task_id}_dubbed.mp4"
            await save_db(db)
        logger.info(f"Dubbing completed for {task_id}")
    except Exception as e:
        logger.error(f"Error in dubbing pipeline for {task_id}: {str(e)}")
        async with db_lock:
            db = await get_db()
            db["tasks"][task_id]["status"] = "failed"
            db["tasks"][task_id]["error"] = str(e)
            await save_db(db)

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

# Pre-rendered health response for performance
HEALTH_DATA = json.dumps({
    "status": "healthy",
    "version": "1.0.0",
    "environment": settings.DEPLOYMENT_ENV
}).encode("utf-8")

@app.get("/health", responses={200: {"model": HealthResponse}})
async def health_check():
    """Health check endpoint - optimized to return raw Response"""
    return Response(content=HEALTH_DATA, media_type="application/json")

@app.post("/upload/chunk", dependencies=[Depends(verify_api_key)])
async def upload_chunk(
    upload_id: str = Form(...),
    chunk_index: int = Form(...),
    total_chunks: int = Form(...),
    file: UploadFile = File(...)
):
    """Handle chunked file uploads"""
    try:
        # Prevent path traversal
        upload_id = os.path.basename(upload_id)
        chunk_dir = os.path.join(settings.UPLOAD_DIR, upload_id)
        os.makedirs(chunk_dir, exist_ok=True)

        chunk_path = os.path.join(chunk_dir, f"chunk_{chunk_index}")
        async with aiofiles.open(chunk_path, mode='wb') as f:
            await f.write(await file.read())

        async with db_lock:
            db = await get_db()
            if upload_id not in db["uploads"]:
                db["uploads"][upload_id] = {"received_chunks": [], "total_chunks": total_chunks}

            if chunk_index not in db["uploads"][upload_id]["received_chunks"]:
                db["uploads"][upload_id]["received_chunks"].append(chunk_index)
            await save_db(db)

        return {"success": True, "chunk_index": chunk_index}
    except Exception as e:
        logger.exception("Error uploading chunk")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload/complete", dependencies=[Depends(verify_api_key)])
async def complete_upload(
    background_tasks: BackgroundTasks,
    upload_id: str = Form(...),
    filename: str = Form(...),
    target_lang: str = Form("en")
):
    """Assemble chunks and trigger dubbing pipeline"""
    try:
        upload_id = os.path.basename(upload_id)
        filename = os.path.basename(filename)
        chunk_dir = os.path.join(settings.UPLOAD_DIR, upload_id)

        async with db_lock:
            db = await get_db()
            if upload_id not in db["uploads"]:
                raise HTTPException(status_code=404, detail="Upload session not found")

            info = db["uploads"][upload_id]
        if len(info["received_chunks"]) < info["total_chunks"]:
            raise HTTPException(status_code=400, detail="Not all chunks received")

        final_path = os.path.join(settings.UPLOAD_DIR, f"{upload_id}_{filename}")

        async with aiofiles.open(final_path, mode='wb') as outfile:
            for i in range(info["total_chunks"]):
                chunk_path = os.path.join(chunk_dir, f"chunk_{i}")
                async with aiofiles.open(chunk_path, mode='rb') as infile:
                    await outfile.write(await infile.read())

        # Cleanup chunks
        for i in range(info["total_chunks"]):
            os.remove(os.path.join(chunk_dir, f"chunk_{i}"))
        os.rmdir(chunk_dir)

        # Create task
        task_id = f"task_{upload_id}"
        async with db_lock:
            db = await get_db()
            db["tasks"][task_id] = {
                "id": task_id,
                "title": f"Dubbing {filename}",
                "status": "pending",
                "progress": 0,
                "file_path": final_path
            }
            await save_db(db)

        # Trigger pipeline
        background_tasks.add_task(process_dubbing, task_id, final_path, target_lang)

        return {"success": True, "task_id": task_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error completing upload")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/task/create", response_model=TaskResponse, dependencies=[Depends(verify_api_key)])
async def create_task(task: Task):
    """Create a new task for the agent"""
    try:
        logger.info(f"Creating task: {task.title}")
        task_id = f"task_{secrets.token_hex(4)}"
        task.id = task_id

        async with db_lock:
            db = await get_db()
            db["tasks"][task_id] = task.model_dump()
            await save_db(db)

        return TaskResponse(
            success=True,
            message="Task created successfully",
            task_id=task_id,
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
        db = await get_db()
        if task_id not in db["tasks"]:
            raise HTTPException(status_code=404, detail="Task not found")
        return db["tasks"][task_id]
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
        db = await get_db()
        tasks = list(db["tasks"].values())
        return {
            "tasks": tasks,
            "total": len(tasks)
        }
    except Exception:
        logger.exception("Error listing tasks")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/execute", dependencies=[Depends(verify_api_key)])
async def execute_task(task_id: str, background_tasks: BackgroundTasks):
    """Execute a task"""
    try:
        logger.info(f"Executing task: {task_id}")
        db = await get_db()
        if task_id not in db["tasks"]:
            raise HTTPException(status_code=404, detail="Task not found")

        task = db["tasks"][task_id]
        if task["status"] == "completed":
             return {"success": True, "message": "Task already completed", "task_id": task_id}

        background_tasks.add_task(process_dubbing, task_id, task.get("file_path", ""), "en")

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
