import logging

logger = logging.getLogger(__name__)

async def transcribe_audio(file_path: str, provider: str = "whisper"):
    """
    Transcribe audio file to text using the specified provider.
    """
    logger.info(f"Transcribing audio from {file_path} using {provider}")
    # Stub implementation
    return {
        "text": "Ceci est une transcription de test.",
        "language": "fr",
        "wer": 0.05
    }
