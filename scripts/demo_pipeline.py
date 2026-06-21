#!/usr/bin/env python3
"""
Script de démonstration du pipeline de doublage
Simule un flux complet : Création -> Upload -> Exécution -> Résultat
"""

import asyncio
import sys
import os

# Add parent directory to path to import services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services import stt, mt, tts, video

async def run_demo():
    print("🚀 Démarrage de la démonstration du pipeline de doublage...")

    # 1. Configuration du projet
    project = {
        "title": "Conférence IA 2024",
        "source_lang": "fr",
        "target_lang": "en",
        "voice_style": "professional"
    }
    print(f"--- Projet : {project['title']} ({project['source_lang']} -> {project['target_lang']}) ---")

    # 2. Transcription (STT)
    print("\n[Étape 1] Transcription de l'audio original...")
    transcript = await stt.transcribe_audio("original_video.mp4", project['source_lang'])
    print(f"Resultat STT : {transcript}")

    # 3. Traduction (MT)
    print("\n[Étape 2] Traduction du texte vers la langue cible...")
    translated_text = await mt.translate_text(transcript, project['source_lang'], project['target_lang'])
    print(f"Resultat MT : {translated_text}")

    # 4. Synthèse Vocale (TTS)
    print("\n[Étape 3] Génération de la nouvelle piste vocale...")
    audio_dubbed_path = await tts.generate_speech(translated_text, project['target_lang'], project['voice_style'])
    print(f"Resultat TTS : Fichier généré à {audio_dubbed_path}")

    # 5. Lip-Sync & Montage (Video)
    print("\n[Étape 4] Synchronisation labiale et montage final...")
    final_video_path = await video.apply_lip_sync("original_video.mp4", audio_dubbed_path)
    print(f"✨ Succès ! Vidéo finale disponible à : {final_video_path}")

    print("\n✅ Démonstration terminée avec succès.")

if __name__ == "__main__":
    asyncio.run(run_demo())
