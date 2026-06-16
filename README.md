# 🎙️ Plateforme de Doublage Vocal Multilingue

Solution de pointe pour le doublage automatique de contenus vidéo et audio utilisant l'IA.

## ✨ Fonctionnalités

- 📤 **Upload Volumineux & Chunké** - Support des fichiers de 10 Mo à 700 Mo+ avec reprise sur erreur.
- 🗣️ **Transcription (STT)** - Extraction précise du texte via Whisper ou services Cloud.
- 🌍 **Traduction (MT)** - Traduction contextuelle haute qualité (DeepL, Google).
- 🎙️ **Synthèse Vocale (TTS)** - Voix naturelles avec contrôle de la prosodie et SSML.
- 👄 **Synchronisation Labiale** - Alignement automatique (Wav2Lip) pour un rendu réaliste.
- ⚡ **Pipeline Asynchrone** - Architecture microservices scalable.
- 🔐 **Sécurité & RGPD** - Authentification OAuth, chiffrement TLS et gestion des données sensibles.

## 🚀 Démarrage Rapide

### Avec Docker (Recommandé)

```bash
# Cloner le repository
git clone https://github.com/lebruntempestriclair-cpu/dubbing-platform.git
cd dubbing-platform

# Configurer l'environnement
cp .env.example .env
# Éditer .env avec vos clés API (OpenAI, DeepL, etc.)

# Démarrer l'application
docker-compose up -d

# Accéder à l'API
curl http://localhost:8000/health
```

### Installation Locale

```bash
# Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Configurer l'environnement
cp .env.example .env

# Lancer l'application
python main.py
```

## 📚 Documentation

- [**ARCHITECTURE.md**](./ARCHITECTURE.md) - Architecture détaillée du pipeline
- [**DEPLOYMENT.md**](./DEPLOYMENT.md) - Guide de déploiement Cloud
- [**CONTRIBUTING.md**](./CONTRIBUTING.md) - Standards de développement

## 🔌 API Principale

- `POST /upload` - Upload de média par chunks
- `POST /projects` - Création d'un projet de doublage
- `GET /projects/{id}` - Suivi de l'avancement
- `GET /results/{id}` - Prévisualisation et métriques (WER, MOS)

## 🛠️ Technologies

- **FastAPI** (Backend)
- **Redis** (Queue & Cache)
- **FFmpeg** (Traitement Vidéo)
- **Wav2Lip** (Lip-Sync)
- **Docker/K8s** (Orchestration)

## 📊 Métriques de Qualité

Le système collecte automatiquement :
- **WER** (Word Error Rate) pour la transcription.
- **MOS** (Mean Opinion Score) pour la synthèse vocale.
- **Latence de traitement** par minute de média.

## ⚖️ Conformité RGPD

La voix est une donnée biométrique. Le système inclut :
- Consentement explicite à l'upload.
- Chiffrement au repos (AES-256).
- Suppression automatique après traitement.

---

**Développé pour l'excellence en doublage IA.** 🚀
