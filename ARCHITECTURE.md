# Architecture du Système

Ce document décrit l'architecture technique de la plateforme de doublage vocal IA.

## Vue d'ensemble de l'Architecture

La solution repose sur une architecture en couches facilitant la scalabilité et la maintenance.

```mermaid
graph TD
    User((Utilisateur))
    C[Interface Web - React]
    API[API Gateway - FastAPI]

    subgraph "Services Backend"
        S1[Storage Manager]
        S2[Dubbing Orchestrator]
    end

    subgraph "Pipeline IA"
        T[Transcoding - FFmpeg]
        STT[Speech-to-Text]
        MT[Machine Translation]
        TTS[Text-to-Speech]
        LS[LipSync]
    end

    User --> C
    C --> API
    API --> S1
    API --> S2
    S2 --> T
    S2 --> STT
    S2 --> MT
    S2 --> TTS
    S2 --> LS
    S1 --> Disk[(Stockage Local/S3)]
```

## Flux de Données - Pipeline de Doublage

Le diagramme suivant illustre le cheminement d'un fichier média à travers le pipeline de traitement.

```mermaid
sequenceDiagram
    participant U as Utilisateur
    participant A as API / Orchestrator
    participant S as Storage
    participant IA as Services IA

    U->>A: Upload en Chunks
    A->>S: Sauvegarde des chunks
    S-->>A: Fichier assemblé
    A->>IA: Extraction Audio (FFmpeg)
    IA-->>A: Piste audio brute
    A->>IA: Transcription (STT)
    IA-->>A: Texte source
    A->>IA: Traduction (MT)
    IA-->>A: Texte cible
    A->>IA: Synthèse Vocale (TTS)
    IA-->>A: Nouvelle piste audio
    A->>IA: Fusion & Sync (FFmpeg/LipSync)
    IA-->>A: Vidéo Doublée
    A-->>U: Résultat prêt
```

## Composants Techniques

- **FastAPI** : Framework principal pour l'API asynchrone.
- **FFmpeg** : Outil de traitement média pour le transcodage et le multiplexage.
- **Storage Manager** : Gère l'isolation des données par utilisateur et le cycle de vie des fichiers.
- **Orchestrator** : Gère la machine à états des jobs de doublage.
- **Pydantic** : Validation des schémas de données.

## Évolutivité et Persistance (Production)

Dans un environnement de production (ex. Kubernetes), les états en mémoire (`upload_sessions` et `orchestrator.jobs`) doivent être déportés vers des systèmes de stockage distribués :
- **Redis** : Pour la gestion des sessions d'upload et le caching.
- **Base de données (PostgreSQL/SQLite)** : Pour la persistance à long terme des jobs et des métadonnées utilisateurs.
- **File d'attente (RabbitMQ/Celery)** : Pour le traitement asynchrone robuste des fichiers volumineux.

## Sécurité et Conformité

- **Isolation** : Chaque utilisateur dispose d'un répertoire dédié `uploads/{user_id}`.
- **RGPD** : Endpoints dédiés pour le droit à l'oubli et l'accès aux données. Consentement explicite requis pour le traitement biométrique.
- **Auth** : Validation par clé API et simulation de jetons OAuth.
