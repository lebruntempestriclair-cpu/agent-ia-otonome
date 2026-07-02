import logging
import os
from src.services import TranscodingService, STTService, MTService, TTSService, LipSyncService

logger = logging.getLogger(__name__)

class DubbingOrchestrator:
    def __init__(self):
        self.transcoder = TranscodingService()
        self.stt = STTService()
        self.mt = MTService()
        self.tts = TTSService()
        self.lipsync = LipSyncService()

    async def run_pipeline(self, video_path: str, target_lang: str, voice_id: str, job_id: str):
        """Run the full dubbing pipeline."""
        logger.info(f"Starting pipeline for job {job_id}")

        base_dir = os.path.dirname(video_path)
        source_audio = os.path.join(base_dir, f"{job_id}_src.wav")
        translated_audio = os.path.join(base_dir, f"{job_id}_translated.wav")
        final_video = os.path.join(base_dir, f"{job_id}_final.mp4")

        try:
            # 1. Extract audio
            await self.transcoder.extract_audio(video_path, source_audio)

            # 2. Transcribe
            transcript = await self.stt.transcribe(source_audio)

            # 3. Translate
            translated_text = await self.mt.translate(transcript, target_lang)

            # 4. Synthesize
            await self.tts.synthesize(translated_text, voice_id, translated_audio)

            # 5. Lip-Sync
            await self.lipsync.sync(video_path, translated_audio, final_video)

            logger.info(f"Pipeline completed for job {job_id}. Output: {final_video}")
            return final_video

        except Exception as e:
            logger.error(f"Pipeline failed for job {job_id}: {str(e)}")
            raise e
