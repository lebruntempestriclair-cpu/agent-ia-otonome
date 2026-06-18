#!/usr/bin/env python3
"""
Multilingual Voice Dubbing Platform - Main Application
"""

import os
import uuid
import logging
import yaml
from contextlib import asynccontextmanager
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Depends, Security, UploadFile, File, Form, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette.middleware.base import BaseHTTPMiddleware
import uvicorn

from models.schemas import Project, ProjectCreate, HealthResponse
from utils.upload_handler import save_chunk, assemble_chunks
from services.pipeline import run_dubbing_pipeline

from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Load config
with open("config.yaml", "r") as f:
    config_raw = f.read()
    # Basic env var substitution for the config
    for key, value in os.environ.items():
        config_raw = config_raw.replace(f"${{{key}}}", value)
    config = yaml.safe_load(config_raw)

# Simple fallback for env vars that weren't replaced (use defaults if specified in config)
def resolve_config(config_dict):
    for key, value in config_dict.items():
        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            # Extract default if present: ${VAR:default}
            parts = value[2:-1].split(":", 1)
            env_val = os.getenv(parts[0], parts[1] if len(parts) > 1 else "")
            config_dict[key] = env_val
        elif isinstance(value, dict):
            resolve_config(value)

resolve_config(config)

# Configure logging
log_level = config['logging']['level']
if not hasattr(logging, log_level):
    log_level = "INFO"

logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============ Settings ============

class Settings:
    def __init__(self):
        self.REQUIRE_API_KEY = str(config['security']['require_api_key']).lower() == "true"
        self.API_KEY = os.getenv("API_KEY", "default_secret_key")
        self.DEPLOYMENT_ENV = config['app']['environment']
        self.API_HOST = config['server']['host']
        self.API_PORT = int(config['server']['port'])
        self.API_WORKERS = int(config['server']['workers'])
        self.TEMP_DIR = config['upload']['temp_dir']
        self.FINAL_DIR = config['upload']['final_dir']

settings = Settings()

# ============ Security ============

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def verify_api_key(header_value: str = Security(api_key_header)):
    if settings.REQUIRE_API_KEY:
        if not header_value or header_value != settings.API_KEY:
            logger.warning("Invalid or missing API key provided")
            raise HTTPException(
                status_code=403,
                detail="Could not validate credentials"
            )
    return header_value

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        return response

# ============ App Setup ============

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Dubbing Platform starting...")
    os.makedirs(settings.TEMP_DIR, exist_ok=True)
    os.makedirs(settings.FINAL_DIR, exist_ok=True)
    yield
    logger.info("Dubbing Platform shutting down...")

app = FastAPI(
    title=config['app']['name'],
    description=config['app']['description'],
    version=config['app']['version'],
    lifespan=lifespan
)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=config['security']['cors_origins'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ Routes ============

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return {
        "status": "healthy",
        "version": config['app']['version'],
        "environment": settings.DEPLOYMENT_ENV
    }

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Placeholder for OAuth2 login (e.g. Gmail integration)"""
    logger.info(f"Login attempt for user: {form_data.username}")
    return {"access_token": "mock_token", "token_type": "bearer"}

@app.post("/upload/init", dependencies=[Depends(verify_api_key)])
async def init_upload():
    upload_id = str(uuid.uuid4())
    return {"upload_id": upload_id}

@app.post("/upload/chunk", dependencies=[Depends(verify_api_key)])
async def upload_chunk(
    upload_id: str = Form(...),
    chunk_index: int = Form(...),
    file: UploadFile = File(...)
):
    try:
        content = await file.read()
        await save_chunk(upload_id, chunk_index, content, settings.TEMP_DIR)
        return {"status": "success", "chunk_index": chunk_index}
    except Exception as e:
        logger.error(f"Error saving chunk {chunk_index} for {upload_id}: {e}")
        raise HTTPException(status_code=500, detail="Error saving chunk")

@app.post("/upload/complete", dependencies=[Depends(verify_api_key)])
async def complete_upload(
    background_tasks: BackgroundTasks,
    upload_id: str = Form(...),
    total_chunks: int = Form(...),
    filename: str = Form(...),
    title: str = Form(...),
    source_language: str = Form(...),
    target_language: str = Form(...),
    voice_id: str = Form(...),
    consent_given: bool = Form(...)
):
    if not consent_given:
        raise HTTPException(status_code=400, detail="GDPR consent is required for biometric processing")

    try:
        final_path = await assemble_chunks(upload_id, total_chunks, settings.TEMP_DIR, settings.FINAL_DIR, filename)

        project_id = str(uuid.uuid4())
        background_tasks.add_task(run_dubbing_pipeline, project_id, final_path, target_language, voice_id)

        return {
            "status": "processing",
            "project_id": project_id,
            "file_path": final_path
        }
    except Exception as e:
        logger.error(f"Error completing upload {upload_id}: {e}")
        raise HTTPException(status_code=500, detail="Error assembling chunks")

@app.get("/project/{project_id}", dependencies=[Depends(verify_api_key)])
async def get_project(project_id: str):
    return {
        "id": project_id,
        "status": "processing",
        "progress": 10
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
