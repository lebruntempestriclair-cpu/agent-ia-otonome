import asyncio
import logging
import ffmpeg
import shutil
import os

logger = logging.getLogger(__name__)

class TranscodingService:
    def _is_ffmpeg_available(self):
        return shutil.which("ffmpeg") is not None

    async def extract_audio(self, video_path: str, output_audio_path: str):
        """Extract audio from video using ffmpeg."""
        logger.info(f"Extracting audio from {video_path} to {output_audio_path}")

        if not self._is_ffmpeg_available():
            logger.warning("ffmpeg not found, simulating audio extraction")
            with open(output_audio_path, 'wb') as f:
                f.write(b"MOCK_EXTRACTED_AUDIO")
            return

        try:
            (
                ffmpeg
                .input(video_path)
                .output(output_audio_path, acodec='pcm_s16le', ac=1, ar='16k')
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
        except ffmpeg.Error as e:
            logger.error(f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}")
            raise Exception("Failed to extract audio")

    async def merge_audio_video(self, video_path: str, audio_path: str, output_path: str):
        """Merge new audio with original video."""
        logger.info(f"Merging {audio_path} into {video_path}")

        if not self._is_ffmpeg_available():
            logger.warning("ffmpeg not found, simulating audio/video merge")
            shutil.copy(video_path, output_path)
            return

        try:
            video = ffmpeg.input(video_path)
            audio = ffmpeg.input(audio_path)
            (
                ffmpeg
                .output(video.video, audio.audio, output_path, vcodec='copy', acodec='aac', strict='experimental')
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
        except ffmpeg.Error as e:
            logger.error(f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}")
            raise Exception("Failed to merge audio and video")

class STTService:
    async def transcribe(self, audio_path: str) -> str:
        """Simulate Speech-to-Text transcription."""
        logger.info(f"Transcribing {audio_path}")
        await asyncio.sleep(0.1)  # Simulate processing
        return "Ceci est une transcription de test."

class MTService:
    async def translate(self, text: str, target_lang: str) -> str:
        """Simulate Machine Translation."""
        logger.info(f"Translating text to {target_lang}")
        await asyncio.sleep(0.1)  # Simulate processing
        if target_lang == "en":
            return "This is a test transcription."
        return f"Translated text in {target_lang}"

class TTSService:
    async def synthesize(self, text: str, voice_id: str, output_path: str):
        """Simulate Text-to-Speech synthesis."""
        logger.info(f"Synthesizing voice {voice_id} to {output_path}")
        await asyncio.sleep(0.1)  # Simulate processing
        # Create a dummy audio file
        with open(output_path, 'wb') as f:
            f.write(b"MOCK_AUDIO_DATA")
        return output_path

class LipSyncService:
    async def sync(self, video_path: str, audio_path: str, output_path: str):
        """Simulate Lip-Sync alignment (Wav2Lip style)."""
        logger.info(f"Lip-syncing {video_path} with {audio_path}")
        await asyncio.sleep(0.2)  # Simulate processing
        # In a real scenario, this would call Wav2Lip
        shutil.copy(video_path, output_path)
        return output_path
