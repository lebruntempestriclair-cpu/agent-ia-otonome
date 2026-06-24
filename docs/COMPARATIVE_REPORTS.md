# Rapports Comparatifs des Solutions Technologiques

## 1. Reconnaissance Vocale (STT)

| Solution | Coût (USD/min) | Latence | WER | Langues |
| :--- | :--- | :--- | :--- | :--- |
| **Google Cloud STT** | 0,016$ | < 5s | ~4.9% | 125+ |
| **Amazon Transcribe** | 0,024$ | < 5s | ~5-6% | 75+ |
| **Azure Speech** | 0,013$ | < 5s | ~5.1% | 100+ |
| **OpenAI Whisper (OSS)**| Gratuit* | > 30s | < 5% | 99 |

\* Hors coûts d'infrastructure GPU.

## 2. Traduction Automatique (MT)

| Solution | Coût (USD/1M chars) | Qualité | Langues |
| :--- | :--- | :--- | :--- |
| **Google Translate** | ~20$ | Bonne | 100+ |
| **DeepL API** | 20-25$ | Excellente | 28+ |
| **Microsoft Translator**| 10$ | Bonne | 90+ |
| **LibreTranslate (OSS)**| Gratuit | Moyenne | 50 |

## 3. Synthèse Vocale (TTS)

| Solution | Coût (USD/1M chars) | Latence | Voix/Langues |
| :--- | :--- | :--- | :--- |
| **Google Cloud TTS** | 16$ | < 1s | 300+ / 50+ |
| **Amazon Polly** | 16$ | < 1s | 60+ / 29 |
| **Azure TTS** | 16$ | < 1s | 400+ / 140+ |
| **ElevenLabs (Premium)**| 300$ | ~1s | Custom / 20+ |
| **Coqui TTS (OSS)** | Gratuit | Secs | 1100+ |

## 4. Alignement et Lip-Sync

- **Wav2Lip** : Solution de référence open-source (MIT). Excellente qualité visuelle.
- **Aeneas** : Synchronisation texte/audio pour le timing.
- **Gentle** : Forced alignment (principalement anglais).
