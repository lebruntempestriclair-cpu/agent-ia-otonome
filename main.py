#!/usr/bin/env python3
"""
Agent IA Autonome - Main Application
Autonomous AI Agent capable of executing tasks on demand
"""

import os
import logging
import yaml
import re
import secrets
import json
import uuid
import aiofiles
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, Security, Response, UploadFile, File, Form
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
    """Cached environment variables and config with substitution support"""
    def __init__(self, config_path="config.yaml"):
        # Initial environment check
        self.DEPLOYMENT_ENV = os.getenv("DEPLOYMENT_ENV", "development")

        # Load config file
        config = {}
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                config_str = f.read()
                config_str = self._substitute_env_vars(config_str)
                config = yaml.safe_load(config_str)

        # Extract values with fallbacks
        app_config = config.get("app", {})
        server_config = config.get("server", {})
        security_config = config.get("security", {})

        self.REQUIRE_API_KEY = str(security_config.get("require_api_key", "false")).lower() == "true"
        self.API_KEY = os.getenv("API_KEY", "default_secret_key")
        self.API_HOST = server_config.get("host", "0.0.0.0")
        self.API_PORT = int(server_config.get("port", 8000))
        self.API_WORKERS = int(server_config.get("workers", 1))

        # Media storage
        self.UPLOAD_DIR = "data/uploads"
        self.DB_PATH = os.path.join(self.UPLOAD_DIR, "db.json")

        # Security enforcement for production
        if self.DEPLOYMENT_ENV == "production" and self.REQUIRE_API_KEY:
            if self.API_KEY == "default_secret_key":
                raise ValueError("API_KEY must be set in production when REQUIRE_API_KEY is enabled")

    def _substitute_env_vars(self, content):
        """Replace ${VAR:default} patterns with environment variables"""
        pattern = re.compile(r'\$\{([^:]+)(?::([^}]*))?\}')

        def replace(match):
            var_name = match.group(1)
            default_value = match.group(2) if match.group(2) is not None else ""
            return os.getenv(var_name, default_value)

        return pattern.sub(replace, content)

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

# ============ App Setup ============

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Modern lifespan management for startup and shutdown"""
    logger.info("Agent IA Autonome starting...")
    # Initialize storage
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    if not os.path.exists(settings.DB_PATH):
        with open(settings.DB_PATH, "w") as f:
            json.dump({}, f)
    yield
    logger.info("Agent IA Autonome shutting down...")

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
    allow_credentials=False,  # Security: False for wildcard origins
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

# ============ Optimization ============

# Pre-render health response to avoid Pydantic/JSON overhead in high-frequency checks
HEALTH_DATA = {
    "status": "healthy",
    "version": "1.0.0",
    "environment": settings.DEPLOYMENT_ENV
}
HEALTH_JSON = json.dumps(HEALTH_DATA)

# ============ Routes ============

@app.get("/health", responses={200: {"model": HealthResponse}})
async def health_check():
    """Health check endpoint - optimized with pre-rendered JSON"""
    return Response(
        content=HEALTH_JSON,
        media_type="application/json"
    )

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

# ============ Chunked Upload ============

# Global lock to prevent race conditions on db.json during concurrent chunk uploads
db_lock = asyncio.Lock()

@app.post("/upload/chunk", dependencies=[Depends(verify_api_key)])
async def upload_chunk(
    file: UploadFile = File(...),
    upload_id: str = Form(...),
    chunk_index: int = Form(...),
    total_chunks: int = Form(...),
    filename: str = Form(...)
):
    """
    Handle chunked uploads for large media files.
    Validates IDs and paths to prevent security vulnerabilities.
    """
    try:
        # Validate upload_id (must be UUID)
        uuid.UUID(upload_id)

        # Prevent path traversal
        safe_filename = os.path.basename(filename)
        upload_dir = os.path.join(settings.UPLOAD_DIR, upload_id)
        os.makedirs(upload_dir, exist_ok=True)

        chunk_path = os.path.join(upload_dir, f"chunk_{chunk_index}")

        async with aiofiles.open(chunk_path, 'wb') as f:
            content = await file.read()
            await f.write(content)

        # Update state in DB with locking for concurrency
        async with db_lock:
            async with aiofiles.open(settings.DB_PATH, mode='r') as f:
                content = await f.read()
                db = json.loads(content) if content else {}

            if upload_id not in db:
                db[upload_id] = {
                    "filename": safe_filename,
                    "total_chunks": total_chunks,
                    "received_chunks": []
                }

            if chunk_index not in db[upload_id]["received_chunks"]:
                db[upload_id]["received_chunks"].append(chunk_index)

            async with aiofiles.open(settings.DB_PATH, mode='w') as f:
                await f.write(json.dumps(db))

            # Check if all chunks are present
            received = db[upload_id]["received_chunks"]
            if len(received) == total_chunks:
                # All chunks received (potentially out of order)
                # Verify we have all indices from 0 to total_chunks-1
                if sorted(received) == list(range(total_chunks)):
                    final_path = os.path.join(settings.UPLOAD_DIR, f"{upload_id}_{safe_filename}")
                    async with aiofiles.open(final_path, 'wb') as outfile:
                        for i in range(total_chunks):
                            c_path = os.path.join(upload_dir, f"chunk_{i}")
                            async with aiofiles.open(c_path, 'rb') as infile:
                                await outfile.write(await infile.read())

                    logger.info(f"File {safe_filename} assembled successfully: {upload_id}")
                    return {"status": "completed", "upload_id": upload_id, "file_path": final_path}

        return {"status": "chunk_received", "chunk_index": chunk_index}

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid upload_id format")
    except Exception as e:
        logger.exception("Chunk upload error")
        raise HTTPException(status_code=500, detail=str(e))

# ============ Main ============

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        workers=settings.API_WORKERS,
        reload=settings.DEPLOYMENT_ENV == "development"
    )
