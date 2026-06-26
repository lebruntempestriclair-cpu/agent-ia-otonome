# 🎙️ Multilingual Voice Dubbing Platform

Microservices-based platform for automated, high-quality voice dubbing with lip-sync synchronization.

## ✨ Features

- 🌍 **Multilingual STT/MT/TTS** - Transcription, Translation, and Synthesis pipeline
- 👄 **Lip-Sync Synchronization** - AI-powered viseme alignment (e.g., Wav2Lip)
- 🚀 **Asynchronous Processing** - Background pipeline execution for large media
- 🛡️ **GDPR Compliant** - Explicit consent for biometric data and secure storage
- 📦 **Large File Support** - Handles uploads up to 700MB via chunked processing
- 🐳 **Microservices Architecture** - Modular and scalable design

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repo_url>
cd voice-dubbing-platform

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env

# Run the platform
python main.py
```

## 🔌 API Endpoints

### Health & Monitoring
```bash
GET /health
```

### Dubbing Pipeline
```bash
POST /dub
# multipart/form-data
# file: <media_file>
# target_language: "fr"
# gdpr_consent: true
```

## 🏗️ Architecture

The platform uses a modular pipeline:
1. **STT Service**: Transcribes audio source to text.
2. **MT Service**: Translates text to target language.
3. **TTS Service**: Synthesizes translated text to audio with prosody adjustment.
4. **Lip-Sync Service**: Aligns phonemes to video visemes for realistic synchronization.

## 🧪 Testing

```bash
python3 -m pytest tests/
```

## 🌳 Structure

```
.
├── main.py                 # API Gateway and Orchestration
├── src/
│   ├── stt.py              # Speech-to-Text service
│   ├── mt.py               # Machine Translation service
│   ├── tts.py              # Text-to-Speech service
│   ├── lipsync.py          # Lip-sync service
│   └── orchestrator.py     # Pipeline orchestrator
├── tests/                  # Integration and unit tests
├── uploads/                # Temporary storage for processing
└── config.yaml             # System configuration
```

---
**Powered by AI Microservices** 🚀
