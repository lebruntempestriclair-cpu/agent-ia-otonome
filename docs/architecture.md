# Architecture du Système

```mermaid
graph TD
    User((Utilisateur)) --> WebFront[Frontend React/Vue]
    WebFront --> APIGateway[API Gateway / NGINX]
    APIGateway --> Auth[Service Auth OAuth/JWT]
    APIGateway --> Upload[Service Upload Chunked]
    Upload --> S3[(Stockage Objet S3/Blob)]

    subgraph Pipeline_IA
        STT[Service STT - Whisper/Google]
        MT[Service MT - DeepL/Google]
        TTS[Service TTS - Azure/Polly]
        LipSync[Service Lip-sync - Wav2Lip]
    end

    Upload --> Queue[File d'attente RabbitMQ/Kafka]
    Queue --> STT
    STT --> MT
    MT --> TTS
    TTS --> LipSync
    LipSync --> VideoMerge[Montage FFmpeg]
    VideoMerge --> S3

    VideoMerge --> Notification[Service Notification]
    Notification --> User
```

## Composants Clés
- **Stockage** : PostgreSQL (Métadonnées), Redis (Cache), S3 (Médias).
- **CDN** : CloudFront pour la distribution.
- **Monitoring** : Prometheus & Grafana.
