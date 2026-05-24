# Guide de Déploiement - Agent IA Autonome

## 🚀 Déploiement Rapide

### Prérequis
- Docker et Docker Compose
- Python 3.11+ (pour développement local)
- Git

### Déploiement Local avec Docker

```bash
# 1. Cloner le repository
git clone https://github.com/lebruntempestriclair-cpu/agent-ia-otonome.git
cd agent-ia-otonome

# 2. Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos clés API

# 3. Démarrer les services
docker-compose up -d

# 4. Vérifier le statut
docker-compose ps

# 5. Vérifier la santé de l'application
curl http://localhost:8000/health
```

### Déploiement sur Linux/Raspberry Pi

```bash
# Installation des dépendances
sudo apt-get update
sudo apt-get install -y python3.11 python3-pip python3-venv

# Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Configurer l'environnement
cp .env.example .env
# Éditer .env

# Lancer l'application
python main.py
```

### Déploiement sur Heroku

```bash
# 1. Installer Heroku CLI
curl https://cli.heroku.com/install.sh | sh

# 2. Se connecter à Heroku
heroku login

# 3. Créer une application
heroku create agent-ia-otonome

# 4. Ajouter les variables d'environnement
heroku config:set OPENAI_API_KEY=your_key
heroku config:set DEPLOYMENT_ENV=production

# 5. Déployer
git push heroku main
```

### Déploiement sur AWS (EC2)

```bash
# 1. Se connecter à l'instance EC2
ssh -i your-key.pem ubuntu@your-ec2-ip

# 2. Installer Docker
sudo apt-get update
sudo apt-get install -y docker.io docker-compose

# 3. Cloner et démarrer
git clone https://github.com/lebruntempestriclair-cpu/agent-ia-otonome.git
cd agent-ia-otonome
docker-compose up -d
```

## 📊 Monitorer l'Application

### Logs en temps réel
```bash
docker-compose logs -f agent
```

### Vérifier les conteneurs
```bash
docker-compose ps
```

### Accéder à l'API Documentation
```
http://localhost:8000/docs
```

## 🔧 Configuration en Production

### Variables d'environnement requises
```bash
DEPLOYMENT_ENV=production
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=...
DATABASE_URL=postgresql://user:pass@host/db
REDIS_URL=redis://host:6379/0
```

### Optimisations Performance
- Augmenter `API_WORKERS` selon le nombre de CPU
- Configurer Redis pour le caching
- Utiliser une base de données PostgreSQL en production
- Mettre en place un reverse proxy (Nginx)

## 🛡️ Sécurité

- Générer des clés API fortes
- Utiliser HTTPS en production
- Mettre à jour régulièrement les dépendances
- Monitorer les logs de sécurité
- Implémenter rate limiting

## 📝 Maintenance

### Mise à jour de l'application
```bash
git pull origin main
docker-compose down
docker-compose build
docker-compose up -d
```

### Sauvegarder les données
```bash
docker-compose exec redis redis-cli BGSAVE
```

## 🆘 Dépannage

### Application ne démarre pas
```bash
# Vérifier les logs
docker-compose logs agent

# Vérifier la configuration
cat .env
```

### Problèmes de connexion Redis
```bash
# Vérifier Redis
docker-compose logs redis

# Redémarrer Redis
docker-compose restart redis
```

## 📞 Support
Pour toute aide, créez une issue sur le repository GitHub.
