# 🎙️ Plateforme de Doublage Vocal Multilingue

Solution de doublage automatisé haute performance intégrant la transcription (STT), la traduction (MT), la synthèse vocale (TTS) et la synchronisation labiale (Lip-Sync).

## ✨ Fonctionnalités Clés

- 📁 **Chargement Multimédia Haute Capacité** : Supporte les fichiers volumineux (jusqu'à 700 Mo+) via un système d'upload par chunks.
- 🔐 **Authentification Sécurisée** : Connexion via OAuth (Google, Facebook, Apple) et gestion des profils.
- 🌍 **Pipeline IA de Doublage** :
    - **STT** (Speech-to-Text) : Transcription précise du contenu original.
    - **MT** (Machine Translation) : Traduction contextuelle haute qualité.
    - **TTS** (Text-to-Speech) : Synthèse vocale naturelle avec gestion des émotions et de la prosodie.
    - **Lip-Sync** : Synchronisation labiale avancée (alignement phonème-visème).
- 🎬 **Montage Automatisé** : Réintégration de la piste audio doublée dans la vidéo via FFmpeg.
- 🛠️ **Édition & Prévisualisation** : Interface pour ajuster manuellement le texte ou le timing.
- ⚖️ **Conformité RGPD** : Gestion rigoureuse des données biométriques (voix) et consentement explicite.

## 🚀 Démarrage Rapide

### Avec Docker

```bash
# Cloner le repository
git clone https://github.com/lebruntempestriclair-cpu/agent-ia-otonome.git
cd agent-ia-otonome

# Configurer l'environnement
cp .env.example .env
# Éditer .env avec vos clés API (Google Cloud, DeepL, etc.)

# Démarrer l'application
docker-compose up -d
```

### Installation Locale

```bash
# Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
python main.py
```

## 📚 Documentation Technique

- [**ARCHITECTURE.md**](./ARCHITECTURE.md) - Schémas d'architecture et flux de données.
- [**DPIA.md**](./DPIA.md) - Analyse d'impact relative à la protection des données (RGPD).
- [**DEPLOYMENT.md**](./DEPLOYMENT.md) - Guide de déploiement Cloud (AWS/GCP/Azure).

## 🔌 API Endpoints Principaux

### Gestion des Projets de Doublage
```bash
POST /task/create          # Créer un nouveau projet de doublage
GET  /task/{task_id}       # Suivi de l'avancement du projet
POST /execute?task_id=...  # Lancer le pipeline de traitement
```

### Upload de Médias Volumineux
```bash
POST /upload/chunk         # Upload segmenté pour fichiers > 700Mo
```

## 🛠️ Stack Technique

- **Backend** : FastAPI (Python 3.12)
- **Traitement Vidéo** : FFmpeg
- **IA/ML** : OpenAI Whisper, DeepL API, Google Cloud TTS, Wav2Lip
- **Infrastructure** : Docker, Kubernetes, Redis (Queue de tâches)
- **Stockage** : S3 / Azure Blob Storage

## 📊 Métriques de Qualité

Nous suivons rigoureusement la qualité de nos traitements via :
- **WER** (Word Error Rate) pour la transcription.
- **MOS** (Mean Opinion Score) pour le naturel de la voix.
- **LSE-D** pour la précision de la synchronisation labiale.

## 🤝 Contribution

Consultez [CONTRIBUTING.md](./CONTRIBUTING.md) pour rejoindre l'aventure !

---
**Développé avec passion pour briser les barrières linguistiques.** 🌍🎤
