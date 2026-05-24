# Guide d'Installation de l'Agent Astra

Ce guide explique comment mettre en place l'agent IA autonome Astra sur Android et PC.

## 1. Installation sur Android (Toutes marques)

Pour qu'une IA soit réellement autonome sur Android, elle a besoin d'un environnement d'exécution et d'accès aux APIs du système.

### Méthode recommandée : Termux + Python + Tasker

1.  **Installez Termux** (depuis F-Droid de préférence pour les dernières mises à jour).
2.  **Mettez à jour les paquets :**
    ```bash
    pkg update && pkg upgrade
    ```
3.  **Installez Python et les dépendances nécessaires :**
    ```bash
    pkg install python python-pip git
    pip install openai langchain requests
    ```
4.  **Accès aux fonctionnalités du téléphone (SMS, Appels, Voice) :**
    - Installez **Termux:API** depuis F-Droid.
    - Installez le paquet dans Termux : `pkg install termux-api`.
    - Vous pouvez maintenant utiliser des commandes comme `termux-sms-send` ou `termux-telephony-call`.
5.  **Automatisation avec Tasker :**
    - Utilisez Tasker pour déclencher des scripts Python dans Termux en fonction d'événements (réception d'un SMS, heure précise, commande vocale via Google Assistant).

---

## 2. Installation sur PC (Windows, Mac, Linux)

Sur PC, l'agent a plus de puissance pour la création d'applications et de sites web.

### Méthode recommandée : Python & Environnement Virtuel

1.  **Installez Python** (version 3.10 ou supérieure).
2.  **Clonez ou créez votre script d'agent :**
    ```bash
    mkdir astra-agent
    cd astra-agent
    python -m venv venv
    source venv/bin/activate  # Sur Windows: venv\Scripts\activate
    ```
3.  **Installez les bibliothèques d'autonomie :**
    ```bash
    pip install openai langchain chromadb Playwright
    ```
    - *Playwright* permet à l'IA de naviguer sur le web et de créer des sites en testant le rendu en temps réel.
4.  **Configuration des clés API :**
    - Créez un fichier `.env` et ajoutez vos clés (OpenAI, Anthropic, etc.).

---

## 3. Mise en œuvre de la Sauvegarde Autonome

L'agent doit utiliser un système de fichiers local ou une base de données vectorielle (comme ChromaDB) pour :
- Sauvegarder l'historique des conversations.
- Stocker l'état d'avancement des projets de code.
- Maintenir une mémoire à long terme de vos préférences.

## 4. Activation de la Voix

- **Sur Android :** Utilisez `termux-tts-speak`.
- **Sur PC :** Utilisez des bibliothèques comme `pyttsx3` ou des APIs de Text-to-Speech de haute qualité (ElevenLabs).
