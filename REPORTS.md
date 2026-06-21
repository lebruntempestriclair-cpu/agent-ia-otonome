# 📊 Rapports Comparatifs des Solutions Techniques

Ce document présente une analyse comparative des différents services tiers utilisables pour le pipeline de doublage.

## 1. Speech-to-Text (STT)
| Solution | Coût (USD/min) | WER typique | Langues | Avantages |
| :--- | :---: | :---: | :---: | :--- |
| **OpenAI Whisper (OSS)** | Gratuit* | < 5% | 99 | État de l'art, auto-hébergé. |
| **Google Cloud STT** | 0.016$ | ~4.9% | 125+ | Très rapide, robuste. |
| **Amazon Transcribe** | 0.024$ | ~5-6% | 75+ | Intégration AWS native. |
| **Microsoft Azure Speech** | 0.013$ | ~5.1% | 100+ | Excellente API de streaming. |

*\*Coût d'infrastructure GPU à prévoir pour l'auto-hébergement.*

## 2. Machine Translation (MT)
| Solution | Coût (USD/1M chars) | Qualité | Langues | Note |
| :--- | :---: | :---: | :---: | :--- |
| **DeepL API** | ~20$ | Excellente | 30+ | Leader sur les langues européennes. |
| **Google Translate** | 20$ | Très Bonne | 130+ | Couverture linguistique maximale. |
| **Microsoft Translator** | 10$ | Bonne | 100+ | Économique pour gros volumes. |

## 3. Text-to-Speech (TTS)
| Solution | Coût (USD/1M chars) | Naturel (MOS) | Langues | Personnalisation |
| :--- | :---: | :---: | :---: | :--- |
| **Google Cloud TTS** | 16$ | 4.5/5 | 50+ | Support SSML avancé. |
| **Azure Neural TTS** | 16$ | 4.6/5 | 140+ | Voix personnalisées (Custom Voice). |
| **Amazon Polly** | 16$ | 4.0/5 | 30+ | Fiable et simple. |
| **ElevenLabs** | ~300$ | 4.9/5 | 29 | Qualité bluffante, coûteux. |

## 4. Stockage Objet
| Solution | Coût (GB/mois) | Durabilité | Egress |
| :--- | :---: | :---: | :---: |
| **AWS S3** | 0.023$ | 11 neufs | Payant |
| **Azure Blob** | 0.018$ | 12 neufs | Payant |
| **Google Cloud Storage** | 0.020$ | 11 neufs | Payant |
| **Backblaze B2** | 0.005$ | 11 neufs | Gratuit (via CDN) |

## Conclusion et Recommandation
Pour un prototype haute performance, nous recommandons le stack suivant :
- **STT** : OpenAI Whisper (Modèle Large) pour la précision.
- **MT** : DeepL pour le naturel des dialogues.
- **TTS** : Google Cloud TTS pour le rapport qualité/prix.
- **Lip-Sync** : Wav2Lip (Self-hosted sur GPU).
