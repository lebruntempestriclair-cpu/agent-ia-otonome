import os
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any
from src.models import DubbingJob
from src.services import TranscodingService, STTService, MTService, TTSService, LipSyncService

logger = logging.getLogger(__name__)

class DubbingOrchestrator:
    def __init__(self):
        self.transcoder = TranscodingService()
        self.stt = STTService()
        self.mt = MTService()
        self.tts = TTSService()
        self.lipsync = LipSyncService()
        self.jobs: Dict[str, DubbingJob] = {}

    async def run_pipeline(self, job: DubbingJob):
        """Sequences the dubbing workflow: Transcode -> STT -> MT -> TTS -> LipSync -> Final Merge"""
        try:
            job.status = "processing"
            job.progress = 0.1
            self.jobs[job.job_id] = job
            logger.info(f"Starting pipeline for job {job.job_id}")

            # 1. Transcoding: Extract Audio
            audio_ext = "mp3"
            base_path = os.path.splitext(job.input_file)[0]
            original_audio = f"{base_path}_original.{audio_ext}"

            if not await self.transcoder.extract_audio(job.input_file, original_audio):
                raise Exception("Audio extraction failed")
            job.progress = 0.2

            # 2. STT: Transcription
            stt_result = await self.stt.transcribe(original_audio)
            job.metrics["wer"] = stt_result["wer"]
            job.progress = 0.4

            # 3. MT: Translation
            translated_text = await self.mt.translate(stt_result["text"], job.target_language)
            job.progress = 0.5

            # 4. TTS: Synthesis
            translated_audio = f"{base_path}_translated.{audio_ext}"
            tts_result = await self.tts.synthesize(translated_text, job.voice_model, translated_audio)
            job.metrics["mos"] = tts_result["mos"]
            job.progress = 0.7

            # 5. LipSync & Merge
            output_video = f"{base_path}_dubbed.mp4"
            # In a real pipeline, we might use LipSyncService here
            # For simplicity, we merge the translated audio back
            if not await self.transcoder.merge_audio_video(job.input_file, translated_audio, output_video):
                 raise Exception("Final merge failed")

            job.status = "completed"
            job.progress = 1.0
            job.completed_at = datetime.now()
            job.output_url = output_video
            logger.info(f"Pipeline completed for job {job.job_id}")

        except Exception as e:
            job.status = "failed"
            logger.exception(f"Pipeline failed for job {job.job_id}: {e}")
            job.metrics["error"] = str(e)
        finally:
            self.jobs[job.job_id] = job
