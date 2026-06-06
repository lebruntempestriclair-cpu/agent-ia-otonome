#!/usr/bin/env python3
"""
Agent IA Autonome - Main Application
Autonomous AI Agent capable of executing tasks on demand
"""

import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from dotenv import load_dotenv
import uvicorn

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Settings:
    """Application settings managed via environment variables"""
    def __init__(self):
        self.deployment_env = os.getenv("DEPLOYMENT_ENV", "development")
        self.api_host = os.getenv("API_HOST", "0.0.0.0")

        # Robust integer parsing for API configuration
        try:
            self.api_port = int(os.getenv("API_PORT", "8000"))
        except (ValueError, TypeError):
            logger.warning("Invalid API_PORT, falling back to 8000")
            self.api_port = 8000

        try:
            self.api_workers = int(os.getenv("API_WORKERS", "1"))
        except (ValueError, TypeError):
            logger.warning("Invalid API_WORKERS, falling back to 1")
            self.api_workers = 1

        # Parse CORS origins
        cors_origins_raw = os.getenv("CORS_ORIGINS", "")
        if not cors_origins_raw or cors_origins_raw == "*":
            # If development, allow all, but be careful with credentials
            self.cors_origins = ["*"] if self.deployment_env == "development" else []
        else:
            self.cors_origins = [origin.strip() for origin in cors_origins_raw.split(",") if origin.strip()]

# Initialize settings
settings = Settings()

# Post-processing settings for security
if settings.cors_origins == ["*"]:
    # allow_origins=["*"] is incompatible with allow_credentials=True in Starlette
    # To be safe, we disable wildcard when credentials are allowed.
    # In development, we could echo the Origin, but for Sentinel,
    # we prefer explicit configuration.
    logger.warning("CORS: Wildcard origin detected. Resetting to empty list for security.")
    settings.cors_origins = []

# Initialize FastAPI app
app = FastAPI(
    title="Agent IA Autonome",
    description="Autonomous AI agent capable of executing tasks",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
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

# ============ Routes ============

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        environment=settings.deployment_env
    )

@app.post("/task/create", response_model=TaskResponse)
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
        logger.error("Error creating task", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/task/{task_id}")
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
        logger.error(f"Error retrieving task", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/tasks")
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
        logger.error("Error listing tasks", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/execute")
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
        logger.error("Error executing task", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

# ============ Startup/Shutdown ============

@app.on_event("startup")
async def startup_event():
    """Initialize agent on startup"""
    logger.info("Agent IA Autonome starting...")
    # TODO: Initialize connections, load models, etc.

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Agent IA Autonome shutting down...")
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
