#!/usr/bin/env python3
"""
Agent IA Autonome - Main Application
Autonomous AI Agent capable of executing tasks on demand
"""

import logging
import secrets
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
import uvicorn

# ============ Configuration ============

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    app_name: str = "Agent IA Autonome"
    version: str = "1.0.0"
    deployment_env: str = "development"

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 1

    # Security
    cors_origins: List[str] = ["*"]
    require_api_key: bool = False
    api_key: Optional[str] = None

settings = Settings()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Autonomous AI agent capable of executing tasks",
    version=settings.version
)

# ============ Security ============

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key(api_key_header_value: str = Security(api_key_header)):
    """Dependency to validate API key if required"""
    if not settings.require_api_key:
        return None

    if not settings.api_key:
        logger.error("REQUIRE_API_KEY is True but API_KEY is not set")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

    if api_key_header_value and secrets.compare_digest(api_key_header_value, settings.api_key):
        return api_key_header_value

    raise HTTPException(
        status_code=403,
        detail="Could not validate API key"
    )

# Add CORS middleware
cors_origins = settings.cors_origins
allow_credentials = True

# Security: FastAPI CORSMiddleware does not allow wildcard "*" with credentials
if "*" in cors_origins and allow_credentials:
    if settings.deployment_env == "production":
        logger.warning("Wildcard CORS with credentials not allowed in production. Disabling credentials.")
        allow_credentials = False
    else:
        # In development/test, we also need to avoid the crash
        logger.warning("Wildcard CORS with credentials not allowed. Disabling credentials to prevent crash.")
        allow_credentials = False

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=allow_credentials,
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
    """Health check endpoint - Public"""
    return HealthResponse(
        status="healthy",
        version=settings.version,
        environment=settings.deployment_env
    )

@app.post("/task/create", response_model=TaskResponse, dependencies=[Depends(get_api_key)])
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
    except Exception as e:
        # Security: Do not leak exception details in the response
        logger.error(f"Error creating task: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/task/{task_id}", dependencies=[Depends(get_api_key)])
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
    except Exception as e:
        # Security: Do not leak exception details in the response
        logger.error(f"Error retrieving task: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/tasks", dependencies=[Depends(get_api_key)])
async def list_tasks():
    """List all tasks"""
    try:
        logger.info("Listing all tasks")
        # TODO: Implement tasks listing logic
        return {
            "tasks": [],
            "total": 0
        }
    except Exception as e:
        # Security: Do not leak exception details in the response
        logger.error(f"Error listing tasks: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/execute", dependencies=[Depends(get_api_key)])
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
    except Exception as e:
        # Security: Do not leak exception details in the response
        logger.error(f"Error executing task: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

# ============ Startup/Shutdown ============

@app.on_event("startup")
async def startup_event():
    """Initialize agent on startup"""
    logger.info(f"{settings.app_name} starting...")
    # TODO: Initialize connections, load models, etc.

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info(f"{settings.app_name} shutting down...")
    # TODO: Close connections, save state, etc.

# ============ Main ============

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        workers=settings.api_workers,
        reload=settings.deployment_env == "development"
    )
