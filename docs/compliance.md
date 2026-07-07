# Conformité et Sécurité

## RGPD (Règlement Général sur la Protection des Données)
- **Données Biométriques** : La voix est une donnée sensible. Consentement explicite requis via une case à cocher spécifique.
- **Droit à l'oubli** : Possibilité de supprimer les fichiers sources et les voix clonées sur demande.
- **Durée de conservation** : Suppression automatique des médias après 30 jours (configurable).
- **DPIA (Data Protection Impact Assessment)** : Analyse d'impact obligatoire pour le traitement automatisé de données biométriques.

## Sécurité
- **Chiffrement** : AES-256 au repos, TLS 1.3 en transit.
- **Sanitisation** : Validation rigoureuse des types de fichiers et des métadonnées.
- **Isolation** : Traitement des médias dans des conteneurs isolés pour prévenir l'exécution de code malveillant.
