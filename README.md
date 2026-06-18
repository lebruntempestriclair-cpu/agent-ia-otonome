# 🎙️ Multilingual Voice Dubbing Platform

Automated, high-quality video translation and voice dubbing platform using AI-powered microservices.

## ✨ Features

- 📹 **Multimedia Loading** - Supports MP4, AVI, MP3, WAV, etc., with chunked uploads for files >700MB.
- 🔐 **OAuth Authentication** - Secure login via Google/Gmail and other providers.
- 🌍 **STT & MT Pipeline** - Automated Speech-to-Text (STT) and Machine Translation (MT) for 100+ languages.
- 🗣️ **Neural TTS** - High-quality synthesis with prosody adjustment and emotion support.
- 👄 **Lip-Syncing** - Phoneme-viseme alignment using models like Wav2Lip for realistic results.
- ⚖️ **GDPR Compliant** - Explicit biometric consent management and secure data handling.
- 🚀 **Asynchronous Processing** - Scalable background pipeline for video transcoding and dubbing.

## 🚀 Quick Start

### With Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/lebruntempestriclair-cpu/agent-ia-otonome.git
cd agent-ia-otonome

# Configure the environment
cp .env.example .env
# Edit .env with your API keys (OpenAI, DeepL, etc.)

# Start the application
docker-compose up -d

# Access the API Health
curl http://localhost:8000/health
```

### Local Installation

```bash
# Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Launch the application
python main.py
```

## 🔌 API Endpoints

- `GET /health` - Service health status
- `POST /upload/init` - Initialize chunked upload
- `POST /upload/chunk` - Upload a media chunk
- `POST /upload/complete` - Complete upload and start pipeline
- `GET /project/{id}` - Get project status and results

## 🛠️ Tech Stack

- **FastAPI** - Backend framework
- **Whisper/Google STT** - Speech-to-Text
- **DeepL/Google Translate** - Machine Translation
- **Azure/Amazon Polly** - Text-to-Speech
- **Wav2Lip** - Lip Synchronization
- **FFmpeg** - Media processing
- **Redis** - Task queuing

---

**Built for high-quality automated video localization.**
