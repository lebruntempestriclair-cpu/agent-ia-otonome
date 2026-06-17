# 🌍 Multilingual Voice Dubbing Platform

Automated high-quality video translation and dubbing platform using state-of-the-art AI services.

## ✨ Key Features

- 📽️ **Large File Upload** - Support for files up to 700MB+ via chunked uploads.
- 🗣️ **AI-Powered Pipeline** - STT → MT → TTS → Lip-Sync (Wav2Lip).
- 🌐 **Multilingual Support** - Seamless translation across 50+ languages.
- 🛡️ **GDPR Compliant** - Explicit biometric consent management and data retention policies.
- 🚀 **Scalable Architecture** - Microservices-ready design for cloud deployment.
- 🔒 **Security First** - TLS, security headers, and API Key authentication.

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/lebruntempestriclair-cpu/agent-ia-otonome.git
cd agent-ia-otonome

# Install dependencies
pip install -r requirements.txt
pip install pytest pytest-asyncio httpx==0.24.1  # For testing

# Run the platform
python main.py
```

### API Documentation
Once running, access the interactive documentation at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 📚 Documentation

- [**ARCHITECTURE.md**](./ARCHITECTURE.md) - Deep dive into the pipeline and cloud infrastructure.
- [**DEPLOYMENT.md**](./DEPLOYMENT.md) - Guide for Docker, AWS, and production setup.
- [**CONTRIBUTING.md**](./CONTRIBUTING.md) - Code standards and contribution guidelines.

## 🔌 Core API Endpoints

### Chunked Upload
```bash
POST /upload/init      # Initialize upload
POST /upload/chunk     # Upload file chunk
POST /upload/complete  # Finalize and merge chunks
```

### Project Management
```bash
POST /project/create   # Create a dubbing project
GET  /project/{id}     # Get project status/progress
GET  /projects         # List all projects
```

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python 3.11+)
- **Storage**: S3-compatible Object Storage
- **AI Services**: OpenAI Whisper, DeepL, Google TTS, Wav2Lip
- **Containerization**: Docker & Kubernetes
- **Monitoring**: Prometheus & Grafana

## 🧪 Testing

```bash
# Run all tests
python3 -m pytest
```

## 🛡️ Security & Privacy

This platform handles sensitive biometric data (voice). We ensure:
- **Consent**: Explicit user consent before processing.
- **Encryption**: Data encrypted at rest and in transit.
- **Retention**: Limited data storage duration as per GDPR.

---

**Built with ❤️ for global communication.**
