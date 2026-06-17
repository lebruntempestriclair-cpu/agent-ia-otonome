#!/usr/bin/env python3
"""
Multilingual Voice Dubbing Platform - API Gateway
Automated high-quality video translation and dubbing pipeline.
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, Security, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
        self.CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

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
    logger.info("Multilingual Voice Dubbing Platform starting...")
    # Initialize storage directories
    os.makedirs("uploads", exist_ok=True)
    yield
    logger.info("Multilingual Voice Dubbing Platform shutting down...")

# Initialize FastAPI app
app = FastAPI(
    title="Multilingual Voice Dubbing Platform",
    description="Automated high-quality video translation using STT, MT, TTS, and Lip-Sync microservices.",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Security Headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    # Allow 'unsafe-inline' for Swagger UI compatibility as per memory
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "img-src 'self' data: https://fastapi.tiangolo.com; "
    )
    return response

from models.schemas import (
    UploadInitRequest, UploadInitResponse, UploadChunkResponse,
    UploadCompleteRequest, UploadCompleteResponse,
    ProjectCreate, Project, ProjectResponse,
    HealthResponse
)
from utils import upload_handler
from services import pipeline
from fastapi import UploadFile, File, Form, BackgroundTasks
import uuid


# ============ Routes ============

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint - optimized performance"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.DEPLOYMENT_ENV
    }

# ============ Upload Routes ============

@app.post("/upload/init", response_model=UploadInitResponse, dependencies=[Depends(verify_api_key)])
async def init_chunked_upload(req: UploadInitRequest):
    """Initialize a chunked upload process"""
    try:
        upload_id = upload_handler.init_upload(
            req.filename, req.total_size, req.content_type
        )
        return UploadInitResponse(upload_id=upload_id)
    except Exception as e:
        logger.error(f"Failed to init upload: {e}")
        raise HTTPException(status_code=500, detail="Failed to initialize upload")

@app.post("/upload/chunk", response_model=UploadChunkResponse, dependencies=[Depends(verify_api_key)])
async def upload_chunk(
    upload_id: str = Form(...),
    chunk_index: int = Form(...),
    file: UploadFile = File(...)
):
    """Upload a single chunk of a file"""
    try:
        chunk_data = await file.read()
        success = await upload_handler.save_chunk(upload_id, chunk_index, chunk_data)
        if not success:
            raise HTTPException(status_code=400, detail="Invalid upload_id or chunk")
        return UploadChunkResponse(success=True, received_index=chunk_index)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload chunk {chunk_index} for {upload_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to save chunk")

@app.post("/upload/complete", response_model=UploadCompleteResponse, dependencies=[Depends(verify_api_key)])
async def complete_chunked_upload(req: UploadCompleteRequest):
    """Complete a chunked upload and trigger reassembly"""
    try:
        filepath = upload_handler.complete_upload(req.upload_id, req.total_chunks)
        return UploadCompleteResponse(success=True, filepath=filepath)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to complete upload {req.upload_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to complete upload")

# ============ Project Routes ============

@app.post("/project/create", response_model=ProjectResponse, dependencies=[Depends(verify_api_key)])
async def create_project(
    req: ProjectCreate,
    background_tasks: BackgroundTasks,
    video_path: str
):
    """Create a new dubbing project and start the pipeline"""
    if not req.consent_given:
        raise HTTPException(
            status_code=400,
            detail="Explicit consent for biometric data processing is required"
        )

    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video file not found")

    project_id = str(uuid.uuid4())
    project = Project(
        id=project_id,
        name=req.name,
        source_language=req.source_language,
        target_language=req.target_language,
        voice_id=req.voice_id
    )

    pipeline.projects[project_id] = project

    # Start the background pipeline
    background_tasks.add_task(pipeline.run_dubbing_pipeline, project_id, video_path)

    return ProjectResponse(success=True, project=project)

@app.get("/project/{project_id}", response_model=Project, dependencies=[Depends(verify_api_key)])
async def get_project_status(project_id: str):
    """Get the status and progress of a project"""
    if project_id not in pipeline.projects:
        raise HTTPException(status_code=404, detail="Project not found")
    return pipeline.projects[project_id]

@app.get("/projects", response_model=List[Project], dependencies=[Depends(verify_api_key)])
async def list_projects():
    """List all projects"""
    return list(pipeline.projects.values())

# ============ Main ============

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        workers=settings.API_WORKERS,
        reload=settings.DEPLOYMENT_ENV == "development"
    )
