# Plan de Tests et Métriques de Qualité

## 1. Stratégie de Test

### Tests Unitaires
- **Upload** : Vérifier le stockage des chunks et l'assemblage final.
- **Pipeline** : Tester chaque étape (STT, MT, TTS, Lip-Sync) isolément via des mocks.
- **Utils** : Valider les commandes FFmpeg générées.

### Tests d'Intégration
- Flux complet : Upload d'une vidéo courte -> Pipeline -> Téléchargement du résultat.
- Validation des endpoints API avec `pytest` et `HTTPX`.

### Tests de Charge
- Simulation de 50 uploads simultanés (fichiers de 100 Mo).
- Mesure de la consommation GPU/CPU lors du Lip-Sync.

## 2. Métriques de Qualité (KPI)

### Transcription (STT)
- **WER (Word Error Rate)** : Cible < 5% pour les langues majeures.

### Synthèse Vocale (TTS)
- **MOS (Mean Opinion Score)** : Évaluation humaine ou via modèles (ex: NISQA), cible > 4.0.

### Synchronisation Labiale
- **LSE-D (Lip Sync Error - Distance)** : Distance moyenne entre les lèvres synthétisées et les phonèmes.
- **LSE-C (Lip Sync Error - Confidence)** : Confiance du modèle dans la synchronisation.

### Performance Système
- **RTF (Real Time Factor)** : Temps de traitement / Durée de la vidéo. Cible < 0.5 (traitement 2x plus rapide que le temps réel).
- **Latence d'API** : < 200ms pour les requêtes standard.
