"""
Service de reconnaissance vocale (STT)
"""
import logging

logger = logging.getLogger(__name__)

async def transcribe_audio(file_path: str, language: str):
    """
    Simule la transcription d'un fichier audio.
    En production, utilise OpenAI Whisper ou Google STT.
    """
    logger.info(f"Transcribing {file_path} in {language}...")
    return f"Ceci est une transcription simulée du fichier {file_path}."
