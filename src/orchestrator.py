import logging
import os
from src.stt import STTService
from src.mt import MTService
from src.tts import TTSService
from src.lipsync import LipSyncService

logger = logging.getLogger(__name__)

class DubbingOrchestrator:
    """Orchestrates the full dubbing pipeline: STT -> MT -> TTS -> LipSync"""

    def __init__(self, config=None):
        self.stt = STTService()
        self.mt = MTService()
        self.tts = TTSService()
        self.lipsync = LipSyncService()

    async def run_pipeline(self, video_path: str, target_lang: str, upload_id: str):
        """Runs the asynchronous pipeline"""
        try:
            logger.info(f"Starting pipeline for upload {upload_id}")

            # 1. STT: Transcription
            transcription = await self.stt.transcribe(video_path)
            source_text = transcription["text"]

            # 2. MT: Translation
            translated_text = await self.mt.translate(source_text, target_lang)

            # 3. TTS: Synthesis
            audio_output_path = f"uploads/{upload_id}_translated.wav"
            await self.tts.synthesize(translated_text, "neural_voice_01", audio_output_path)

            # 4. Lip-Sync & Final Rendering
            final_output_path = f"uploads/{upload_id}_final.mp4"
            await self.lipsync.synchronize(video_path, audio_output_path, final_output_path)

            logger.info(f"Pipeline completed for upload {upload_id}. Final output: {final_output_path}")
            return final_output_path

        except Exception:
            logger.exception(f"Pipeline failed for upload {upload_id}")
            raise
