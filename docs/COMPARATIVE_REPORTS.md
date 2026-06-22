# Rapports Comparatifs des Technologies

## 1. Reconnaissance Vocale (STT)
| Solution | Coût (USD/min) | Latence | WER | Langues |
|----------|----------------|---------|-----|---------|
| Google STT | 0,016$ | < 5s/min | ~4.9% | 125+ |
| Amazon Transcribe | 0,024$ | < 5s/min | ~5-6% | 75+ |
| Microsoft Azure | 0,013$ | < 5s/min | ~5.1% | 100+ |
| OpenAI Whisper | Gratuit (OSS) | > 30s/min | < 5% | 99 |
| Deepgram | 0,15$ | 2-3s/min | ~5-6% | 30-50 |

## 2. Traduction (MT)
| Solution | Coût (USD/1M chars) | Qualité | Langues |
|----------|---------------------|---------|---------|
| Google Translate | 20$ | Bonne | 100+ |
| DeepL | 20-25$ | Excellente | 28+ |
| Microsoft | 10$ | Bonne | 90+ |
| LibreTranslate | Gratuit (OSS) | Moyenne | 50+ |

## 3. Synthèse Vocale (TTS)
| Solution | Coût (USD/1M chars) | Latence | Voix/Langues |
|----------|---------------------|---------|--------------|
| Google Cloud | 16$ | < 1s | 300 / 50+ |
| Amazon Polly | 16$ | < 1s | 60 / 29+ |
| Microsoft Azure | 0,06$/h | < 1s | 400 / 140+ |
| ElevenLabs | 300$ | ~1s | 20+ |
| Coqui TTS | Gratuit (OSS) | s/mots | 1100+ |

## 4. Alignement Phonème-Visème
- **Wav2Lip** : Gratuit, multi-langue, très bonne qualité de sync (MIT).
- **Aeneas** : Gratuit, utile pour la synchronisation texte-audio.
- **Gentle** : Gratuit, principalement anglais.

## 5. Stockage et Transfert
- **AWS S3** : 0,023$/GB, haut débit, très sécurisé.
- **Azure Blob** : 0,018$/GB, haut débit.
- **Google Storage** : 0,020$/GB, multi-région.
- **Backblaze B2** : 0,005$/GB, coût réduit.
- **MinIO** : Open Source, compatible S3 pour auto-hébergement.
