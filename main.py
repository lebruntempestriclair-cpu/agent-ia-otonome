#!/usr/bin/env python3
"""
Agent IA Autonome - Main Application
Autonomous AI Agent capable of executing tasks on demand
"""

import os
import logging
import secrets
from typing import Optional
from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import uvicorn
from starlette.status import HTTP_403_FORBIDDEN

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Settings:
    """Application settings cached from environment variables"""
    def __init__(self):
        self.require_api_key = os.getenv("REQUIRE_API_KEY", "false").lower() == "true"
        self.api_key = os.getenv("API_KEY")
        self.deployment_env = os.getenv("DEPLOYMENT_ENV", "development")
        if self.require_api_key and not self.api_key:
            logger.warning("REQUIRE_API_KEY is true but API_KEY is not set!")

settings = Settings()
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key(api_key_value: str = Security(api_key_header)):
    """Dependency to validate API Key"""
    if not settings.require_api_key: return None
    if not settings.api_key:
        logger.error("API_KEY environment variable is missing while REQUIRE_API_KEY is true")
        raise HTTPException(status_code=500, detail="Internal server error")
    if api_key_value and secrets.compare_digest(api_key_value, settings.api_key):
        return api_key_value
    raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials")

# Initialize FastAPI app
app = FastAPI(title="Agent IA Autonome", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.deployment_env == "development" else [os.getenv("ALLOWED_ORIGINS", "")],
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
    """Health check endpoint (public)"""
    return HealthResponse(status="healthy", version="1.0.0", environment=settings.deployment_env)

@app.post("/task/create", response_model=TaskResponse, dependencies=[Depends(get_api_key)])
async def create_task(task: Task):
    """Create a new task for the agent"""
    try:
        logger.info(f"Creating task: {task.title}")
        return TaskResponse(success=True, message="Task created successfully", task_id="task_123", status="pending")
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/task/{task_id}", dependencies=[Depends(get_api_key)])
async def get_task(task_id: str):
    """Get task status"""
    try:
        logger.info(f"Fetching task: {task_id}")
        return {"task_id": task_id, "status": "pending", "progress": 0}
    except Exception as e:
        logger.error(f"Error retrieving task: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/tasks", dependencies=[Depends(get_api_key)])
async def list_tasks():
    """List all tasks"""
    try:
        logger.info("Listing all tasks")
        return {"tasks": [], "total": 0}
    except Exception as e:
        logger.error(f"Error listing tasks: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/execute", dependencies=[Depends(get_api_key)])
async def execute_task(task_id: str):
    """Execute a task"""
    try:
        logger.info(f"Executing task: {task_id}")
        return {"success": True, "message": "Task execution started", "task_id": task_id}
    except Exception as e:
        logger.error(f"Error executing task: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

# ============ Startup/Shutdown ============

@app.on_event("startup")
async def startup_event():
    logger.info("Agent IA Autonome starting...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Agent IA Autonome shutting down...")

# ============ Main ============

if __name__ == "__main__":
    uvicorn.run("main:app", host=os.getenv("API_HOST", "0.0.0.0"),
                port=int(os.getenv("API_PORT", 8000)),
                workers=int(os.getenv("API_WORKERS", 1)),
                reload=settings.deployment_env == "development")
