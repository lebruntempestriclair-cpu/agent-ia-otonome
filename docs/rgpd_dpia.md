# Conformité RGPD et Protection des Données

## Nature des Données
La voix humaine est considérée comme une **donnée biométrique sensible** selon le RGPD lorsqu'elle permet l'identification unique d'une personne.

## Principes de Protection
1. **Consentement Explicite** : Recueillir l'accord de l'utilisateur avant tout traitement vocal (clonage ou analyse).
2. **DPIA (Étude d'impact)** : Réaliser une analyse d'impact relative à la protection des données (AIPD) dès la conception.
3. **Limitation de la Finalité** : Les données ne sont traitées que pour le doublage demandé.
4. **Minimisation** : Ne collecter que le nécessaire.
5. **Durée de Conservation** : Définir une période de rétention limitée (ex: suppression après 30 jours).
6. **Droit à l'oubli** : Permettre la suppression totale des fichiers et modèles vocaux sur demande.

## Mesures de Sécurité
- Chiffrement au repos (AES-256).
- Chiffrement en transit (TLS 1.2+).
- Anonymisation/Pseudonymisation des métadonnées.
- Contrôle d'accès strict (IAM, OAuth).
