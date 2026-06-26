import logging
import os
from .stt import STTService
from .mt import MTService
from .tts import TTSService
from .lipsync import LipSyncService
from .storage import StorageService

logger = logging.getLogger(__name__)

class DubbingOrchestrator:
    """Orchestrates the dubbing pipeline: STT -> MT -> TTS -> LipSync"""

    def __init__(self, storage_service: StorageService):
        self.stt_service = STTService()
        self.mt_service = MTService()
        self.tts_service = TTSService()
        self.lipsync_service = LipSyncService()
        self.storage_service = storage_service

    async def run_pipeline(self, video_path: str, target_lang: str, output_path: str):
        """Execute the full dubbing pipeline"""
        try:
            logger.info(f"Starting dubbing pipeline for {video_path} to {target_lang}")

            # 1. Transcription (STT)
            transcript = await self.stt_service.transcribe(video_path)

            # 2. Translation (MT)
            translated_text = await self.mt_service.translate(transcript, target_lang)

            # 3. Synthesis (TTS)
            audio_output = video_path + ".mp3"
            await self.tts_service.synthesize(translated_text, audio_output)

            # 4. Lip-Sync (Alignment)
            await self.lipsync_service.synchronize(video_path, audio_output, output_path)

            # 5. Upload result to storage
            remote_name = os.path.basename(output_path)
            final_url = await self.storage_service.upload(output_path, remote_name)

            logger.info(f"Dubbing pipeline completed successfully. Final URL: {final_url}")

            # Cleanup intermediate files if necessary
            if os.path.exists(audio_output):
                os.remove(audio_output)

            return output_path

        except Exception as e:
            logger.error(f"Error in dubbing pipeline: {str(e)}")
            raise
