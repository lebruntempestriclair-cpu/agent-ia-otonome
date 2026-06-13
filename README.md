# 🎙️ Multilingual Video Dubbing Platform

High-quality automated video dubbing system integrating STT, MT, TTS, and Lip-Sync specialized services.

## ✨ Features

- 🎙️ **Automated Pipeline** - Sequential STT → MT → TTS → Lip-Sync workflow.
- 📁 **Large Media Support** - Chunked uploads for files up to 700MB+.
- 🌐 **Multilingual** - Support for 100+ languages via top-tier AI providers.
- 👄 **Lip-Sync** - Accurate phoneme-to-viseme alignment (Wav2Lip integration).
- 🔐 **Security & Compliance** - OAuth2, API Keys, and GDPR compliance for biometric data.
- 🚀 **Asynchronous Execution** - Background task processing with real-time status tracking.

## 🚀 Quick Start

### With Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/lebruntempestriclair-cpu/agent-ia-otonome.git
cd agent-ia-otonome

# Configure the environment
cp .env.example .env
# Edit .env with your API keys (DeepL, OpenAI, Google, AWS)

# Start the application
docker-compose up -d

# Check health
curl http://localhost:8000/health
```

## 🔌 API Endpoints

### Health & Monitoring
```bash
GET /health                 # System health check
GET /task/{id}/progress     # Detailed progress & metrics (WER, MOS)
```

### Dubbing Workflow
```bash
POST /task/create           # Create a new dubbing project
GET  /tasks                 # List all projects
POST /execute?task_id=...   # Trigger the dubbing pipeline
```

## 🛠️ Technology Stack

- **FastAPI** - High-performance backend
- **STT** - OpenAI Whisper / Google Cloud Speech
- **MT** - DeepL / Google Translate
- **TTS** - Amazon Polly / Azure Cognitive Services
- **Lip-Sync** - Wav2Lip (MIT)
- **Storage** - S3 / Google Cloud Storage

## 🧪 Quality Metrics

The platform tracks several quality KPIs:
- **WER (Word Error Rate)** - Measures transcription accuracy.
- **MOS (Mean Opinion Score)** - Evaluates synthetic voice quality.
- **Lip-Sync Accuracy** - Visual alignment score.

## ⚖️ GDPR & Compliance

Voice data is considered sensitive biometric data. This platform ensures:
- Explicit user consent before processing.
- Encryption at rest and in transit (TLS 1.2+).
- Automated data deletion after project completion.

---

**Built with ❤️ for high-quality content localization.**
