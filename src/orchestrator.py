import logging
import asyncio
from src.services import AIServices, TranscodingService

logger = logging.getLogger(__name__)

class DubbingOrchestrator:
    """Sequences the dubbing pipeline steps."""

    def __init__(self):
        self.ai = AIServices()
        self.transcoder = TranscodingService()

    async def run_pipeline(self, job_id: str, file_path: str, target_lang: str, voice_id: str):
        """Executes the full STT -> MT -> TTS -> LipSync pipeline."""
        try:
            logger.info(f"Starting pipeline for job {job_id}")

            # 1. Transcoding / Audio Extraction
            audio_path = await self.transcoder.extract_audio(file_path)

            # 2. STT
            transcript = await self.ai.transcribe(audio_path)

            # 3. MT
            translated_text = await self.ai.translate(transcript, target_lang)

            # 4. TTS
            dubbed_audio_path = await self.ai.synthesize(translated_text, voice_id)

            # 5. LipSync & Final Assembly
            final_video = await self.ai.lip_sync(file_path, dubbed_audio_path)

            logger.info(f"Pipeline completed for job {job_id}: {final_video}")
            return final_video

        except Exception as e:
            logger.error(f"Pipeline failed for job {job_id}: {str(e)}")
            raise
