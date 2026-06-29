import logging
from .services import STTService, MTService, TTSService, LipSyncService, TranscodingService

logger = logging.getLogger(__name__)

class DubbingOrchestrator:
    def __init__(self):
        self.stt = STTService()
        self.mt = MTService()
        self.tts = TTSService()
        self.lipsync = LipSyncService()
        self.transcoder = TranscodingService()

    async def run_pipeline(self, job_id: str, file_path: str, target_lang: str):
        """
        Sequences the dubbing pipeline: Transcode -> STT -> MT -> TTS -> LipSync -> Final Merge.
        """
        try:
            logger.info(f"Starting pipeline for job {job_id}")

            # 1. Transcoding / Audio Extraction
            audio_source = await self.transcoder.extract_audio(file_path)
            logger.info(f"[{job_id}] Audio extraction complete")

            # 2. STT
            transcription = await self.stt.transcribe(audio_source)
            logger.info(f"[{job_id}] Transcription complete")

            # 3. MT
            translation = await self.mt.translate(transcription, target_lang)
            logger.info(f"[{job_id}] Translation complete")

            # 4. TTS
            dubbed_audio = await self.tts.synthesize(translation, "voice_01")
            logger.info(f"[{job_id}] TTS complete")

            # 5. LipSync
            synchronized_video = await self.lipsync.sync(file_path, dubbed_audio)
            logger.info(f"[{job_id}] Lip-sync complete")

            # 6. Final Transcoding / Merge
            final_video = await self.transcoder.merge_audio_video(synchronized_video, dubbed_audio)
            logger.info(f"[{job_id}] Pipeline complete. Final video at {final_video}")

            # Update job status in DB (Mocked)
            logger.info(f"[{job_id}] Job completed successfully")

        except Exception as e:
            logger.error(f"[{job_id}] Pipeline failed: {str(e)}")
            # Handle failure, cleanup, etc.
