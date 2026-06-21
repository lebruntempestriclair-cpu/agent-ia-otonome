"""
Service de traduction automatique (MT)
"""
import logging

logger = logging.getLogger(__name__)

async def translate_text(text: str, source_lang: str, target_lang: str):
    """
    Simule la traduction d'un texte.
    En production, utilise DeepL API ou Google Translate.
    """
    logger.info(f"Translating from {source_lang} to {target_lang}...")
    return f"[Translated to {target_lang}]: {text}"
