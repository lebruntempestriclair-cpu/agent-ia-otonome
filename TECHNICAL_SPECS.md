# Spécifications Techniques

## Objectifs Fonctionnels

1.  **Chargement multimédia** : Support des fichiers MP4, AVI, MP3, WAV jusqu'à 700 Mo via upload chunké.
2.  **Authentification** : Gestion des accès via OAuth/JWT et clés API.
3.  **Transcription/Traduction** : Pipeline STT -> MT multilingue.
4.  **Synthèse vocale** : Génération audio via TTS avec support SSML.
5.  **Synchronisation** : Alignement labial (LipSync) et time-stretching.
6.  **Conformité RGPD** : Gestion du consentement, droit à l'oubli et accès aux données.

## Exigences Non-Fonctionnelles

- **Latence** : Traitement asynchrone via BackgroundTasks. Cible < 30s de traitement par minute de média.
- **Scalabilité** : Architecture microservices prête pour Kubernetes.
- **Sécurité** :
    - Chiffrement TLS.
    - Headers de sécurité (X-Frame-Options, HSTS, etc.).
    - Isolation des données utilisateurs.
    - Validation constante des clés API.
- **Fiabilité** : Mécanisme de reprise sur erreur dans l'orchestrateur. Simulation de fallback si FFmpeg est absent.

## Conformité RGPD

La voix est une donnée biométrique sensible. La plateforme implémente :
- **Consentement Explicite** : Requis pour chaque job de doublage.
- **Droit à l'oubli** : Endpoint `DELETE /user/data` pour supprimer toutes les traces.
- **Portabilité** : Endpoint `GET /user/data` pour l'export des données.
- **Durée de conservation** : Suppression automatique des fichiers temporaires (chunks) après traitement.

## Pile Technologique

- **Backend** : FastAPI (Python 3.11)
- **Traitement Média** : FFmpeg
- **IA** : Stubs pour OpenAI Whisper (STT), DeepL (MT), ElevenLabs/Google (TTS).
- **Stockage** : Système de fichiers local (extensible vers S3).
