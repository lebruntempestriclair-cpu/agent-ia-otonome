# 🎙️ Multilingual Dubbing Platform

Plateforme web de doublage vocal multilingue intégrant l'upload de fichiers volumineux, la transcription (STT), la traduction (MT), la synthèse vocale (TTS) et la synchronisation labiale (Lip-sync).

## ✨ Fonctionnalités

- 🎥 **Traitement Vidéo & Audio** - Support des fichiers MP4, AVI, MP3, WAV (>700 Mo)
- 🧩 **Upload Chunké** - Chargement fiable des fichiers volumineux par segments
- 🗣️ **Pipeline IA Complet** - Intégration STT (Whisper), MT (DeepL), TTS (Azure/Polly)
- 👄 **Lip-Sync** - Synchronisation labiale automatique (Wav2Lip)
- 🌍 **Multilingue** - Support de plus de 100 langues et styles de voix
- ⚖️ **Conformité RGPD** - Gestion rigoureuse des données biométriques (voix)
- 🚀 **Architecture Microservices** - Scalabilité horizontale avec Docker/Kubernetes

## 🚀 Démarrage Rapide

### Avec Docker (Recommandé)

```bash
# Cloner le repository
git clone https://github.com/lebruntempestriclair-cpu/agent-ia-otonome.git
cd agent-ia-otonome

# Configurer l'environnement
cp .env.example .env
# Éditer .env avec vos clés API

# Démarrer l'application
docker-compose up -d

# Accéder à l'API
curl http://localhost:8000/health
```

### Installation Locale

```bash
# Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt

# Configurer l'environnement
cp .env.example .env

# Lancer l'application
python main.py
```

## 📚 Documentation

- [**DEPLOYMENT.md**](./DEPLOYMENT.md) - Guide de déploiement complet (Docker, Heroku, AWS, Linux)
- [**CONTRIBUTING.md**](./CONTRIBUTING.md) - Guide de contribution et standards de code
- [**config.yaml**](./config.yaml) - Configuration de l'application

## 🔌 API Endpoints

### Santé de l'application
```bash
GET /health
```

### Gestion des tâches
```bash
POST /task/create          # Créer une nouvelle tâche
GET  /task/{task_id}       # Récupérer une tâche
GET  /tasks                # Lister toutes les tâches
POST /execute?task_id=...  # Exécuter une tâche
```

## 🛠️ Technologies

- **FastAPI** - Framework web moderne
- **Python 3.11** - Language de programmation
- **Docker** - Containerisation
- **Redis** - Cache et state management
- **OpenAI/Anthropic** - Modèles IA
- **SQLite/PostgreSQL** - Base de données

## 📋 Structure du Projet

```
agent-ia-otonome/
├── main.py                 # Application principale
├── config.yaml             # Configuration
├── requirements.txt        # Dépendances Python
├── Dockerfile              # Configuration Docker
├── docker-compose.yml      # Orchestration services
├── tests/                  # Tests unitaires
├── DEPLOYMENT.md           # Guide de déploiement
├── CONTRIBUTING.md         # Guide de contribution
└── .github/
    └── workflows/
        └── deploy.yml      # Workflow CI/CD (à créer manuellement)
```

## 🔐 Configuration

Voir le fichier `.env.example` pour les variables d'environnement requises:

```bash
DEPLOYMENT_ENV=production
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
REDIS_URL=redis://localhost:6379/0
DATABASE_URL=sqlite:///./agent.db
```

## 🧪 Tests

```bash
# Exécuter tous les tests
pytest tests/ -v

# Avec couverture de code
pytest tests/ --cov=. --cov-report=html
```

## 🌳 Branches

- **main** - Production (déploiement automatique)
- **develop** - Développement
- **feature/*** - Nouvelles fonctionnalités
- **bugfix/*** - Corrections de bugs

## 📊 Monitoring

L'application expose des métriques Prometheus sur le port `9090`:
```bash
curl http://localhost:9090/metrics
```

## 🆘 Dépannage

### L'application ne démarre pas
```bash
# Vérifier les logs
docker-compose logs agent

# Vérifier la configuration
cat .env
```

### Erreur de connexion Redis
```bash
# Redémarrer Redis
docker-compose restart redis
```

## 📝 Logs

Les logs sont stockés dans `logs/agent.log` et affichés en temps réel:
```bash
docker-compose logs -f agent
```

## 🤝 Contribuer

Nous accueillons les contributions! Consultez [CONTRIBUTING.md](./CONTRIBUTING.md) pour:
- Comment fork le projet
- Créer des branches
- Soumettre des pull requests
- Standards de code

## 📄 Licence

Ce projet est open source. Consultez les détails de licence.

## 🙋 Support

Pour toute question ou problème:
1. Vérifiez la [documentation](./DEPLOYMENT.md)
2. Consultez les [issues existantes](https://github.com/lebruntempestriclair-cpu/agent-ia-otonome/issues)
3. Créez une nouvelle issue avec une description détaillée

## 🎯 Roadmap

- [ ] Implémentation complète de la logique d'exécution
- [ ] Support multi-modèles IA
- [ ] Interface web de gestion
- [ ] Système de plugins
- [ ] Analytics avancée
- [ ] Support natif Android/iOS

---

**Créé avec ❤️ par lebruntempestriclair-cpu**

Prêt pour le déploiement! 🚀
