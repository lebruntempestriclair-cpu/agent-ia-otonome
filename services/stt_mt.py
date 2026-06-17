import asyncio
import logging

logger = logging.getLogger(__name__)

class STTService:
    """Mock Speech-to-Text Service"""
    async def transcribe(self, file_path: str, source_language: str) -> str:
        logger.info(f"Transcribing {file_path} (Lang: {source_language})")
        # Simulate processing time
        await asyncio.sleep(2)
        return "This is a mock transcription of the source audio."

class MTService:
    """Mock Machine Translation Service"""
    async def translate(self, text: str, target_language: str) -> str:
        logger.info(f"Translating to {target_language}")
        # Simulate processing time
        await asyncio.sleep(1)
        return f"[Translated to {target_language}]: {text}"

# Singleton instances
stt_service = STTService()
mt_service = MTService()
