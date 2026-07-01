import logging
from src.services import TranscodingService, STTService, MTService, TTSService, LipSyncService

logger = logging.getLogger(__name__)

class DubbingOrchestrator:
    """Orchestrates the dubbing pipeline."""

    def __init__(self):
        self.transcoding = TranscodingService()
        self.stt = STTService()
        self.mt = MTService()
        self.tts = TTSService()
        self.lipsync = LipSyncService()

    async def run_pipeline(self, job_id: str, input_path: str, target_lang: str, voice_id: str):
        """
        Executes the sequential dubbing pipeline:
        Transcoding -> STT -> MT -> TTS -> LipSync
        """
        try:
            logger.info(f"Starting pipeline for job {job_id}")

            # 1. Transcoding
            transcoded_path = await self.transcoding.process(input_path)

            # 2. STT
            transcript = await self.stt.transcribe(transcoded_path)

            # 3. MT
            translated_text = await self.mt.translate(transcript, target_lang)

            # 4. TTS
            dubbed_audio_path = await self.tts.synthesize(translated_text, voice_id)

            # 5. Lip Sync
            final_video_path = await self.lipsync.align(transcoded_path, dubbed_audio_path)

            logger.info(f"Pipeline completed for job {job_id}. Final output: {final_video_path}")

        except Exception as e:
            logger.error(f"Pipeline failed for job {job_id}: {str(e)}")
            # In a real app, we would update job status in a DB here
