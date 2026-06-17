import asyncio
import logging

logger = logging.getLogger(__name__)

class TTSService:
    """Mock Text-to-Speech Service"""
    async def synthesize(self, text: str, voice_id: str, language: str) -> str:
        logger.info(f"Synthesizing speech with voice {voice_id} (Lang: {language})")
        # Simulate processing time
        await asyncio.sleep(3)
        return f"uploads/mock_output_{voice_id}.mp3"

class LipSyncService:
    """Mock Lip-Sync Service (Wav2Lip)"""
    async def sync(self, video_path: str, audio_path: str) -> str:
        logger.info(f"Syncing video {video_path} with audio {audio_path}")
        # Simulate processing time
        await asyncio.sleep(5)
        return f"uploads/mock_final_video.mp4"

# Singleton instances
tts_service = TTSService()
lipsync_service = LipSyncService()
