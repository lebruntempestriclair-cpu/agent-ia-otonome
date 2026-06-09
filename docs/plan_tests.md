# Plan de Tests et Métriques de Qualité

## Stratégie de Test
1. **Tests Unitaires** : Validation des composants individuels (STT, MT, TTS, FFmpeg wrapper).
2. **Tests d'Intégration** : Vérification du pipeline complet STT -> MT -> TTS -> LipSync.
3. **Tests de Charge** : Simulation d'uploads simultanés de fichiers volumineux (700 Mo+) via k6 ou JMeter.
4. **Tests de Sécurité** : Scans SAST/DAST, validation des tokens OAuth et des limites de taille de fichier.

## Métriques de Qualité
- **WER (Word Error Rate)** : Pour la transcription (cible < 10%).
- **MOS (Mean Opinion Score)** : Pour la qualité de la synthèse vocale (cible > 4.0).
- **LSE-D (Lip Sync Error - Distance)** : Pour la synchronisation labiale (via outils comme Wav2Lip metrics).
- **Latence de Traitement** : Cible < 30s de traitement par minute de média.

## Scénarios de Test de Charge
| Scénario | Utilisateurs Simultanés | Taille Fichier | Résultat Attendu |
| :--- | :--- | :--- | :--- |
| Basique | 10 | 10 Mo | Pas d'erreur, latence stable |
| Intense | 50 | 100 Mo | Auto-scaling déclenché |
| Limite | 5 | 700 Mo+ | Upload chunké robuste, pas de timeout |
