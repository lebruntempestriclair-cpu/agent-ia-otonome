# 🎥 Plateforme de Doublage Vocal Multilingue

Solution autonome de doublage vocal intégrant transcription, traduction et synthèse vocale avec synchronisation labiale.

## ✨ Fonctionnalités

- 🎙️ **Transcription Automatique (STT)** - Conversion audio en texte via Whisper/Google.
- 🌍 **Traduction Multilingue (MT)** - Traduction contextuelle via DeepL/Google.
- 🗣️ **Synthèse Vocale (TTS)** - Génération de voix naturelles avec SSML.
- 👄 **Synchronisation Labiale** - Alignement visuel via Wav2Lip.
- 📦 **Upload Volumineux** - Support de fichiers >700 Mo via upload chunké.
- 🛡️ **Conformité RGPD** - Protection stricte des données biométriques vocales.

## 🚀 Démarrage Rapide

### Avec Docker (Recommandé)

```bash
# Cloner le repository
git clone https://github.com/lebruntempestriclair-cpu/agent-ia-otonome.git
cd agent-ia-otonome

# Configurer l'environnement
cp .env.example .env
# Éditer .env avec vos clés API (OpenAI, DeepL, Azure, etc.)

# Démarrer l'application
docker-compose up -d

# Accéder à l'API
curl http://localhost:8000/health
```

## 📚 Documentation

- [**Spécifications**](./docs/specifications.md) - Détails fonctionnels et techniques
- [**Architecture**](./docs/architecture.md) - Schémas et pipeline
- [**Comparatif Tech**](./docs/comparatif_tech.md) - Étude des solutions STT/MT/TTS
- [**Conformité RGPD**](./docs/rgpd_dpia.md) - Gestion des données sensibles

## 🔌 API Endpoints (Principaux)

### Santé et Statut
```bash
GET /health
```

### Gestion du Doublage
```bash
POST /task/create          # Lancer un nouveau projet de doublage
POST /upload/chunk         # Upload sécurisé de gros fichiers
GET  /projects             # Liste des projets en cours
GET  /task/{task_id}       # Statut et métriques (WER/MOS)
```

## 📋 Roadmap

- [x] Phase 1 : Spécifications et Architecture
- [ ] Phase 2 : Prototype ML (STT, MT, TTS, LipSync)
- [ ] Phase 3 : Backend (Upload chunking, Pipeline)
- [ ] Phase 4 : Frontend & UX (React, OAuth)
- [ ] Phase 5 : Intégration et Tests de Charge
- [ ] Phase 6 : Déploiement Cloud & CDN

## 🛡️ Sécurité et Confidentialité

Ce projet traite des données biométriques. Nous appliquons les principes de "Privacy by Design" et assurons une transparence totale sur le traitement des données vocales conformément au RGPD.

---
**Développé pour la révolution du contenu multilingue.**
