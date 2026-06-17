# Architecture - Multilingual Voice Dubbing Platform

## Overview
The platform uses a microservices-based architecture to provide automated video translation and dubbing. The system is designed to be scalable, secure, and GDPR-compliant.

## Dubbing Pipeline Flow
The following diagram illustrates the end-to-end processing of a video file.

```mermaid
graph TD
    User[User/Client] -->|1. Upload Media in Chunks| Gateway[API Gateway / FastAPI]
    Gateway -->|2. Reassemble File| Storage[(Object Storage / S3)]
    Gateway -->|3. Trigger Pipeline| Pipeline[Pipeline Orchestrator]

    subgraph "Dubbing Pipeline"
    Pipeline -->|4. Transcription| STT[STT Service]
    STT -->|Text| MT[MT Service]
    MT -->|Translated Text| TTS[TTS Service]
    TTS -->|Target Audio| Sync[Lip-Sync / Wav2Lip]
    Sync -->|Final Video| Merge[Merge/Transcode]
    end

    Merge -->|5. Store Result| Storage
    Pipeline -->|6. Update Status| DB[(PostgreSQL/Redis)]
    User -->|7. Poll Status / Download| Gateway
```

## Cloud Infrastructure (AWS Example)
The platform is designed to run in a containerized environment with auto-scaling capabilities.

```mermaid
graph LR
    User -->|HTTPS| CF[CloudFront CDN]
    CF --> ALB[Application Load Balancer]

    subgraph "VPC / Kubernetes (EKS)"
    ALB --> GatewaySvc[API Gateway Svc]
    GatewaySvc --> PipelineSvc[Pipeline Worker Svc]
    end

    PipelineSvc -->|IAM| S3[(Amazon S3)]
    PipelineSvc -->|Query| RDS[(Amazon RDS - PostgreSQL)]
    PipelineSvc -->|State| ElastiCache[(Amazon ElastiCache - Redis)]

    subgraph "External AI APIs"
    PipelineSvc -.-> Google[Google Cloud STT/TTS]
    PipelineSvc -.-> DeepL[DeepL API]
    PipelineSvc -.-> Azure[Azure Speech Services]
    end
```

## Key Components

### 1. API Gateway (FastAPI)
- Handles authentication (OAuth/JWT).
- Manages chunked uploads for large files (up to 700MB+).
- Enforces security headers and CORS.
- Provides project management and status tracking.

### 2. Chunked Upload System
- `init`: Generates a unique `upload_id`.
- `chunk`: Receives and stores individual file segments.
- `complete`: Merges chunks into a final file and triggers processing.

### 3. Dubbing Pipeline
- **STT (Speech-to-Text)**: Extracts text from the source audio.
- **MT (Machine Translation)**: Translates the extracted text to the target language.
- **TTS (Text-to-Speech)**: Generates a natural-sounding voice in the target language.
- **Lip-Sync (Wav2Lip)**: Synchronizes the video's lip movements with the new audio.

### 4. GDPR Compliance
- Explicit consent is required for biometric data processing (voice).
- Data retention policies are enforced (auto-deletion after X days).
- Support for "Right to be Forgotten" (data deletion on request).

## Metrics and Quality Control
- **WER (Word Error Rate)**: Measures transcription accuracy.
- **MOS (Mean Opinion Score)**: Evaluates synthetic voice quality.
- **LSE-D (Lip Sync Error - Distance)**: Measures the quality of lip synchronization.
- **Latence**: Targeted at <30s per minute of audio.
