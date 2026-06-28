"""
Dubbing Orchestrator
Sequences specialized AI services for the dubbing workflow.
"""

import logging
import asyncio
from typing import Dict, Any
from src.services import STTService, MTService, TTSService, LipSyncService

logger = logging.getLogger(__name__)

class DubbingOrchestrator:
    """Orchestrates the STT -> MT -> TTS -> LipSync pipeline"""

    def __init__(self):
        self.stt = STTService()
        self.mt = MTService()
        self.tts = TTSService()
        self.lipsync = LipSyncService()

    async def run_pipeline(self, job_id: str, file_path: str, target_lang: str, options: Dict[str, Any]):
        """Runs the full dubbing pipeline asynchronously"""
        try:
            logger.info(f"Starting pipeline for job {job_id}")

            # 1. STT: Transcribe source
            transcript = await self.stt.transcribe(file_path)
            logger.info(f"Job {job_id} - Transcription complete")

            # 2. MT: Translate to target language
            translated_text = await self.mt.translate(transcript, target_lang)
            logger.info(f"Job {job_id} - Translation complete")

            # 3. TTS: Generate target audio
            voice_id = options.get("voice_id", "default")
            synthetic_audio_path = await self.tts.synthesize(translated_text, target_lang, voice_id)
            logger.info(f"Job {job_id} - TTS complete")

            # 4. LipSync: Align video with new audio
            # Note: For audio-only source, we'd skip this or handle differently
            final_video_path = await self.lipsync.sync(file_path, synthetic_audio_path)
            logger.info(f"Job {job_id} - LipSync complete. Final output: {final_video_path}")

            # TODO: Update job status in DB/Cache
            return final_video_path

        except Exception as e:
            logger.error(f"Pipeline failed for job {job_id}: {str(e)}")
            # TODO: Handle failure state
            raise
