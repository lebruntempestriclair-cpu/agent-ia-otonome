import logging

logger = logging.getLogger(__name__)

class STTService:
    """Speech-to-Text Service with support for multiple providers (Whisper, Google, etc.)"""
    def __init__(self, provider: str = "whisper"):
        self.provider = provider

    async def transcribe(self, audio_path: str) -> str:
        logger.info(f"Transcribing audio using {self.provider}: {audio_path}")
        if not audio_path:
            raise ValueError("Audio path is required")

        # Mock implementation
        return "This is a transcribed text from the audio using " + self.provider
