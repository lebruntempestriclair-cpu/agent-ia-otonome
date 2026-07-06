# Plan de Tests et Métriques de Qualité

Ce document définit la stratégie de test et les indicateurs de performance clés (KPI) pour la plateforme.

## 📏 Métriques de Qualité (IA)

Le succès du doublage est mesuré par les indicateurs suivants :

| Composant | Métrique | Description | Cible |
| :--- | :--- | :--- | :--- |
| **STT** (Transcription) | **WER** (Word Error Rate) | Taux d'erreur par mot. | < 5% |
| **MT** (Traduction) | **BLEU / METEOR** | Qualité de la traduction par rapport à une référence. | N/A (Qualitatif) |
| **TTS** (Voix) | **MOS** (Mean Opinion Score) | Note de 1 à 5 sur le naturel de la voix. | > 4.0 |
| **Lip-Sync** | **LSE-D / LSE-C** | Distance/Confiance de l'alignement labial. | < 7.0 (LSE-D) |
| **Système** | **Latence** | Temps de traitement par minute de média. | < 30s / min |

## 🧪 Stratégie de Test

### 1. Tests Unitaires (Pytest)
- Validation des modèles Pydantic.
- Test des utilitaires de découpage de fichiers (chunks).
- Mocking des APIs externes (DeepL, AWS, Azure).

### 2. Tests d'Intégration
- Flux complet : Upload -> Queue -> Traitement -> Stockage.
- Vérification des interactions entre microservices.

### 3. Tests de Charge (k6 / JMeter)
- Simulation d'uploads simultanés de fichiers volumineux (> 700 Mo).
- Test de la scalabilité horizontale des workers STT/TTS.

### 4. Tests de Sécurité (SAST/DAST)
- Scan de vulnérabilités sur les dépendances.
- Vérification de l'isolation des processus (Sandboxing).

## 🚀 Pipeline CI/CD (GitHub Actions)

- **Linting** : Flake8 pour le code Python.
- **Automated Tests** : Exécution de `pytest` à chaque commit.
- **Security Scan** : Scan Docker pour les vulnérabilités d'images.
- **Reporting** : Publication des rapports de couverture de code.

## 🛠️ Outils de Supervision

- **Prometheus** : Collecte des métriques système et business.
- **Grafana** : Tableaux de bord en temps réel.
- **OpenTelemetry** : Traçage distribué pour identifier les goulots d'étranglement dans le pipeline.
