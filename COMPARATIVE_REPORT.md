# Rapport Comparatif des Services IA

Ce document compare les différentes solutions pour les composants clés du pipeline de doublage.

## 1. Speech-to-Text (STT)

| Solution | Coût (USD/min) | Latence | WER | Langues |
| :--- | :--- | :--- | :--- | :--- |
| Google Cloud STT | 0.016$ | < 5s | ~4.9% | 125+ |
| Amazon Transcribe | 0.024$ | < 5s | ~5-6% | 75+ |
| OpenAI Whisper (OSS) | Gratuit | Var (GPU) | < 5% | 99 |
| Deepgram | ~0.015$ | **< 2s** | ~5% | 30+ |

**Recommandation** : **OpenAI Whisper** pour la précision (état de l'art) ou **Deepgram** pour la latence ultra-faible.

## 2. Traduction Automatique (MT)

| Solution | Coût / 1M chars | Qualité | Langues |
| :--- | :--- | :--- | :--- |
| Google Translate | ~20$ | Bonne | 100+ |
| **DeepL API** | **~25$** | **Excellente** | 28+ |
| Microsoft Translator | ~10$ | Bonne | 90+ |

**Recommandation** : **DeepL** pour la qualité naturelle des traductions, particulièrement en Europe.

## 3. Synthèse Vocale (TTS)

| Solution | Coût / 1M chars | Qualité | Support SSML |
| :--- | :--- | :--- | :--- |
| Google Cloud TTS | 16$ | Très Bonne | Oui |
| Amazon Polly | 16$ | Bonne | Oui |
| **ElevenLabs** | **~300$** | **Ultra-Réaliste** | Limité |
| Microsoft Azure TTS | 16$ | Très Bonne | Oui |

**Recommandation** : **ElevenLabs** pour des projets haut de gamme (clonage vocal) ou **Azure/Google** pour le rapport coût/performance.

## 4. Synchronisation Labiale (LipSync)

| Solution | Type | Licence | Qualité |
| :--- | :--- | :--- | :--- |
| **Wav2Lip** | GAN | MIT | Excellente |
| Gentle | Forced Align | MIT | Bonne (EN only) |
| Aeneas | Forced Align | BSD | Bonne (Multi) |

**Recommandation** : **Wav2Lip** est le standard actuel pour un rendu visuel convaincant.
