#!/usr/bin/env python3
"""
Multilingual Dubbing Platform - Main Application
Web platform for automated voice dubbing and lip-sync
"""

import os
import logging
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, Security, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field
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
    """Cached environment variables and configuration"""
    def __init__(self):
        self.REQUIRE_API_KEY = os.getenv("REQUIRE_API_KEY", "false").lower() == "true"
        self.API_KEY = os.getenv("API_KEY", "default_secret_key")
        self.DEPLOYMENT_ENV = os.getenv("DEPLOYMENT_ENV", "development")
        self.API_HOST = os.getenv("API_HOST", "0.0.0.0")
        self.API_PORT = int(os.getenv("API_PORT", 8000))
        self.API_WORKERS = int(os.getenv("API_WORKERS", 1))
        self.UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./data/uploads")

settings = Settings()

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

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
    logger.info("Multilingual Dubbing Platform starting...")
    yield
    logger.info("Multilingual Dubbing Platform shutting down...")

# Initialize FastAPI app
app = FastAPI(
    title="Multilingual Dubbing Platform",
    description="Web platform for automated voice dubbing and lip-sync",
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

class VoiceSettings(BaseModel):
    language_code: str = Field(..., description="Target language code (e.g., 'en-US')")
    gender: Optional[str] = "neutral"
    accent: Optional[str] = None
    emotion: Optional[str] = "neutral"
    clone_voice: bool = False

class ProjectCreate(BaseModel):
    title: str
    voice_settings: VoiceSettings

class Project(BaseModel):
    id: str
    title: str
    status: str = "created"
    progress: float = 0.0
    voice_settings: VoiceSettings
    media_path: Optional[str] = None
    output_path: Optional[str] = None
    received_chunks: List[int] = Field(default_factory=list)

class UploadInitResponse(BaseModel):
    upload_id: str
    chunk_size: int

class TaskResponse(BaseModel):
    success: bool
    message: str
    project_id: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str

import json

# ============ Persistence (POC) ============
DB_FILE = os.path.join(settings.UPLOAD_DIR, "db.json")

def load_projects() -> Dict[str, Project]:
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                data = json.load(f)
                return {k: Project(**v) for k, v in data.items()}
        except Exception as e:
            logger.error(f"Error loading projects: {e}")
    return {}

def save_projects(proj_dict: Dict[str, Project]):
    try:
        with open(DB_FILE, "w") as f:
            json.dump({k: v.model_dump() for k, v in proj_dict.items()}, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving projects: {e}")

# Load initial state
projects: Dict[str, Project] = load_projects()

# ============ Routes ============

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.DEPLOYMENT_ENV
    }

# --- Project Management ---

@app.post("/project/create", response_model=Project, dependencies=[Depends(verify_api_key)])
async def create_project(project_in: ProjectCreate):
    """Create a new dubbing project"""
    project_id = str(uuid.uuid4())
    project = Project(
        id=project_id,
        title=project_in.title,
        voice_settings=project_in.voice_settings
    )
    projects[project_id] = project
    save_projects(projects)
    logger.info(f"Project created: {project_id}")
    return project

@app.get("/project/{project_id}", response_model=Project, dependencies=[Depends(verify_api_key)])
async def get_project(project_id: str):
    """Get project details and status"""
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")
    return projects[project_id]

@app.get("/projects", response_model=List[Project], dependencies=[Depends(verify_api_key)])
async def list_projects():
    """List all projects"""
    return list(projects.values())

# --- Media Upload (Chunked) ---

@app.post("/upload/init", response_model=UploadInitResponse, dependencies=[Depends(verify_api_key)])
async def initialize_upload(filename: str = Form(...), total_size: int = Form(...)):
    """Initialize a chunked upload session"""
    upload_id = str(uuid.uuid4())
    logger.info(f"Initializing upload {upload_id} for {filename} ({total_size} bytes)")
    # In a real app, we would track the upload in a DB/Redis
    return {
        "upload_id": upload_id,
        "chunk_size": 5 * 1024 * 1024  # 5MB chunks
    }

def validate_uuid(val: str):
    try:
        uuid.UUID(val)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

@app.post("/upload/chunk", dependencies=[Depends(verify_api_key)])
async def upload_chunk(
    upload_id: str = Form(...),
    chunk_index: int = Form(...),
    total_chunks: int = Form(...),
    project_id: str = Form(...),
    file: UploadFile = File(...)
):
    """Upload a specific chunk of the media file"""
    validate_uuid(upload_id)
    validate_uuid(project_id)

    if project_id not in projects:
         raise HTTPException(status_code=404, detail="Project not found")

    project = projects[project_id]
    logger.info(f"Received chunk {chunk_index}/{total_chunks} for upload {upload_id}")

    # Save individual chunk
    chunk_path = os.path.join(settings.UPLOAD_DIR, f"{upload_id}_{chunk_index}.chunk")
    with open(chunk_path, "wb") as f:
        f.write(await file.read())

    if chunk_index not in project.received_chunks:
        project.received_chunks.append(chunk_index)

    # If all chunks are present, assemble them
    if len(project.received_chunks) == total_chunks:
        safe_filename = os.path.basename(file.filename)
        final_path = os.path.join(settings.UPLOAD_DIR, f"{upload_id}_{safe_filename}")

        with open(final_path, "wb") as final_file:
            for i in range(total_chunks):
                chunk_file = os.path.join(settings.UPLOAD_DIR, f"{upload_id}_{i}.chunk")
                with open(chunk_file, "rb") as cf:
                    final_file.write(cf.read())
                os.remove(chunk_file) # Clean up chunk

        project.status = "uploaded"
        project.media_path = final_path
        logger.info(f"Upload {upload_id} completed and assembled for project {project_id}")

    save_projects(projects)
    return {"status": "chunk_received", "received": len(project.received_chunks)}

# --- Pipeline Execution ---

import asyncio

async def run_mock_pipeline(project_id: str):
    """Simulate a long-running dubbing pipeline"""
    steps = ["stt", "mt", "tts", "lip-sync", "merging"]
    project = projects[project_id]

    for i, step in enumerate(steps):
        project.status = f"processing_{step}"
        project.progress = (i / len(steps)) * 100
        save_projects(projects)
        logger.info(f"Project {project_id} step: {step}")
        await asyncio.sleep(2) # Simulate work

    project.status = "completed"
    project.progress = 100.0
    project.output_path = project.media_path.replace(".mp4", "_dubbed.mp4")
    save_projects(projects)
    logger.info(f"Project {project_id} completed")

@app.post("/project/{project_id}/process", dependencies=[Depends(verify_api_key)])
async def start_processing(project_id: str):
    """Start the dubbing pipeline (STT -> MT -> TTS -> LipSync)"""
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects[project_id]
    if project.status != "uploaded":
        raise HTTPException(status_code=400, detail="Media not uploaded yet")

    project.status = "processing"
    save_projects(projects)

    # Start background task
    asyncio.create_task(run_mock_pipeline(project_id))

    logger.info(f"Started background processing for project {project_id}")
    return {"message": "Processing started in background", "project_id": project_id}

# ============ Main ============

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        workers=settings.API_WORKERS,
        reload=settings.DEPLOYMENT_ENV == "development"
    )
