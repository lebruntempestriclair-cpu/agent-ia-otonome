# Conformité RGPD et Protection des Données

## 1. Nature des Données
La voix humaine est considérée comme une **donnée biométrique sensible** sous le RGPD lorsqu'elle est utilisée à des fins d'identification ou qu'elle révèle des caractéristiques uniques.

## 2. Principes Clés

### Consentement Explicite
- Un formulaire de consentement doit être présenté avant toute collecte de voix.
- L'utilisateur doit être informé de l'usage précis (doublage, clonage éventuel).

### Limitation des Finalités
- Les données vocales ne doivent être utilisées que pour le service de doublage demandé par l'utilisateur.

### Durée de Conservation
- Les fichiers sources et intermédiaires doivent être supprimés après une période définie (ex: 30 jours) ou dès la fin du traitement si l'utilisateur le souhaite.

### Sécurité
- Chiffrement AES-256 au repos.
- Chiffrement TLS en transit.
- Contrôle d'accès strict (IAM).

## 3. Droits des Personnes
- **Accès** : Fournir l'historique des traitements.
- **Suppression** : Bouton "Supprimer mon compte et mes données".
- **Portabilité** : Export des projets en formats standards.

## 4. Gouvernance
- Désignation d'un DPO (Data Protection Officer).
- Réalisation d'une **DPIA (Data Protection Impact Assessment)** ou AIPD en français.
