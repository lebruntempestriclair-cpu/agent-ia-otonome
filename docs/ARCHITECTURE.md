# Architecture du Système

Ce document décrit l'architecture technique de la plateforme de doublage.

## 1. Vue d'ensemble du Pipeline

Le pipeline de doublage est conçu comme une suite de microservices orchestrés de manière asynchrone.

```mermaid
graph TD
    A[Utilisateur] -->|Upload Chunked| B(API Gateway)
    B -->|Stockage Temporaire| C[S3 / Blob Storage]
    B -->|Job Queue| D{Message Broker}

    subgraph "Pipeline de Traitement"
    D --> E[Service STT]
    E --> F[Service MT]
    F --> G[Service TTS]
    G --> H[Service Lip-Sync]
    H --> I[Service Montage Vidéo]
    end

    I -->|Vidéo Finie| C
    I -->|Notification| B
    B -->|Preview / Download| A
```

## 2. Architecture Infrastructure (Cloud)

L'infrastructure utilise des services gérés pour garantir la scalabilité et la haute disponibilité.

```mermaid
graph LR
    subgraph "Cloud Provider (AWS/GCP/Azure)"
    CDN(CDN - CloudFront)
    LB(Load Balancer)
    K8S(Kubernetes Cluster)
    S3(Object Storage - S3)
    RDS(Database - PostgreSQL)
    REDIS(Cache - Redis)

    LB --> K8S
    K8S --> S3
    K8S --> RDS
    K8S --> REDIS
    CDN --> S3
    end

    User[Client Web/Mobile] --> LB
    User --> CDN
```

## 3. Flux de Données et Sécurité

1.  **Ingestion :** Les fichiers sont chargés par segments via HTTPS (TLS 1.2+).
2.  **Validation :** Chaque segment est vérifié (somme de contrôle) et validé par l'API Gateway.
3.  **Traitement :** Les microservices communiquent via gRPC ou REST. Les données sensibles sont chiffrées au repos.
4.  **Conformité :** Un service de gestion du consentement vérifie les droits avant de lancer le traitement biométrique (voix).

## 4. Services IA Intégrés

-   **STT :** OpenAI Whisper (self-hosted) ou Google Speech-to-Text.
-   **MT :** DeepL API ou Google Cloud Translate.
-   **TTS :** Google Cloud TTS ou Microsoft Azure Neural TTS.
-   **Lip-Sync :** Wav2Lip (modèle PyTorch).
