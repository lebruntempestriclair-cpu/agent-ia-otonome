import logging
from datetime import datetime
from typing import Dict
from models.schemas import Project
from services.stt_mt import stt_service, mt_service
from services.tts_sync import tts_service, lipsync_service

logger = logging.getLogger(__name__)

# Project store in memory for prototype
projects: Dict[str, Project] = {}

async def run_dubbing_pipeline(project_id: str, video_path: str):
    """Orchestrate the dubbing pipeline steps"""
    if project_id not in projects:
        logger.error(f"Project {project_id} not found in store")
        return

    project = projects[project_id]

    try:
        # Step 1: STT
        project.status = "transcribing"
        project.progress = 10.0
        project.updated_at = datetime.now()
        text = await stt_service.transcribe(video_path, project.source_language)

        # Step 2: MT
        project.status = "translating"
        project.progress = 30.0
        project.updated_at = datetime.now()
        translated_text = await mt_service.translate(text, project.target_language)

        # Step 3: TTS
        project.status = "synthesizing"
        project.progress = 60.0
        project.updated_at = datetime.now()
        audio_path = await tts_service.synthesize(
            translated_text, project.voice_id, project.target_language
        )

        # Step 4: Lip-Sync
        project.status = "syncing"
        project.progress = 80.0
        project.updated_at = datetime.now()
        final_video_path = await lipsync_service.sync(video_path, audio_path)

        # Complete
        project.status = "completed"
        project.progress = 100.0
        project.output_url = final_video_path
        project.updated_at = datetime.now()
        logger.info(f"Pipeline completed for project {project_id}")

    except Exception as e:
        logger.error(f"Pipeline failed for project {project_id}: {e}")
        project.status = "failed"
        project.updated_at = datetime.now()
