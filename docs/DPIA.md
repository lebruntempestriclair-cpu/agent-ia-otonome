# DPIA - Analyse d'Impact sur la Protection des Données (RGPD)

Ce document évalue les risques et les mesures de protection concernant le traitement des données biométriques (voix) dans le cadre de la plateforme de doublage.

## ⚖️ Nature du Traitement

- **Données Collectées** : Voix originale (audio), Image/Visage (vidéo), Nom, Email (OAuth).
- **Sensibilité** : La voix est considérée comme une **donnée biométrique** selon le RGPD lorsqu'elle permet l'identification unique d'une personne.
- **Finalité** : Doublage vocal automatisé et synchronisation labiale pour la production multimédia.

## 🔒 Mesures de Sécurité et de Conformité

### 1. Consentement Explicite
- Un formulaire de consentement doit être validé avant tout upload.
- Information claire sur l'usage de l'IA pour traiter la voix et l'image.

### 2. Droits des Personnes
- **Droit d'accès et de portabilité** : L'utilisateur peut télécharger ses données sources et résultats.
- **Droit à l'oubli** : Suppression automatique des fichiers temporaires après traitement et sur demande pour les projets archivés.
- **Droit de rectification** : Possibilité d'éditer le script généré.

### 3. Protection Technique
- **Chiffrement** : Données chiffrées au repos (AES-256) et en transit (TLS 1.2+).
- **Sandboxing** : Isolation des processus de traitement ML pour éviter les fuites de données.
- **Localisation** : Priorité au stockage des données en Union Européenne pour les utilisateurs européens.

### 4. Conservation des Données
- Fichiers sources : Supprimés 48h après la finalisation du projet (configurable).
- Modèles de voix (si clonage) : Stockage sécurisé avec clé unique, supprimable instantanément par l'utilisateur.

## 🚨 Analyse des Risques

| Risque | Impact | Probabilité | Mesure d'Atténuation |
| :--- | :--- | :--- | :--- |
| Usurpation d'identité (Deepfake) | Haut | Faible | Vérification des droits sur le contenu, filigranage des sorties. |
| Fuite de données biométriques | Critique | Très Faible | Chiffrement strict, accès restreint (IAM), audits réguliers. |
| Traitement non autorisé | Moyen | Faible | Logging exhaustif et monitoring des accès API. |

## 👨‍💼 Responsabilité

- **DPO (Data Protection Officer)** : Nommé pour superviser la conformité.
- **Registre des traitements** : Maintenu à jour pour chaque service de la plateforme.
