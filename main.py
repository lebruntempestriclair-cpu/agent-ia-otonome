#!/usr/bin/env python3
"""
Agent IA Autonome - Main Application
Autonomous AI Agent capable of executing tasks on demand
"""

import os
import logging
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, Security, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
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
        self.DEPLOYMENT_ENV = os.getenv("DEPLOYMENT_ENV", "development")
        self.API_HOST = os.getenv("API_HOST", "0.0.0.0")
        self.API_PORT = int(os.getenv("API_PORT", 8000))
        self.API_WORKERS = int(os.getenv("API_WORKERS", 1))

settings = Settings()

# Pre-render health response for performance
HEALTH_RESPONSE_JSON = json.dumps({
    "status": "healthy",
    "version": "1.0.0",
    "environment": settings.DEPLOYMENT_ENV
})

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

# ============ Routes ============

@app.get("/health", responses={200: {"model": HealthResponse}})
async def health_check():
    """Health check endpoint - optimized by returning pre-rendered JSON"""
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

# ============ Main ============

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        workers=settings.API_WORKERS,
        reload=settings.DEPLOYMENT_ENV == "development"
    )
