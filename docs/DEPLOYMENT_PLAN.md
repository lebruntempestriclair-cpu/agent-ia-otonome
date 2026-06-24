# Plan de Déploiement et d'Infrastructure

## 1. Environnement de Développement (Docker)

Le projet utilise `docker-compose` pour orchestrer les services locaux :
- **App** : FastAPI (Python 3.11).
- **Redis** : Gestion des queues et du cache.
- **PostgreSQL** : Persistance des données.
- **Worker** : Exécution du pipeline lourd (GPU requis pour production).

## 2. Déploiement Cloud (Production)

### Infrastructure as Code (Terraform)
- **Réseau** : VPC, Subnets publics/privés.
- **Compute** : Amazon EKS (Kubernetes) ou ECS (Fargate pour l'API, EC2 G5 pour les workers IA).
- **Stockage** : Amazon S3 (Buckets pour médias sources et finis).
- **Base de données** : Amazon RDS (PostgreSQL).

### Pipeline CI/CD (GitHub Actions)
1. **Lint & Test** : Exécution de `pytest` et `flake8`.
2. **Build Docker** : Construction des images et push sur Amazon ECR.
3. **Deploy** : Mise à jour du cluster Kubernetes via `kubectl` ou Helm.

## 3. Mise à l'échelle (Auto-scaling)
- Basé sur la taille de la queue (RabbitMQ/SQS).
- Provisionnement dynamique d'instances GPU lors des pics de charge.

## 4. Monitoring et Alerting
- **Prometheus & Grafana** : Visualisation des métriques techniques et métier.
- **ELK Stack** : Centralisation des logs.
- **Sentry** : Suivi des erreurs applicatives.
