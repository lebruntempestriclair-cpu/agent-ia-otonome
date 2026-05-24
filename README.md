# Agent IA Autonome Astra

Ce projet fournit la base de configuration pour un agent IA autonome capable de s'installer sur Android et PC, peu importe la marque.

## Capacités principales
- **Autonomie complète :** Planification et exécution de tâches complexes.
- **Développement :** Création d'applications (Android/PC) et de sites web.
- **Communication :** Envoi de SMS, gestion d'appels et interaction vocale.
- **Sauvegarde :** Persistance des données et de l'état pour ne jamais perdre le fil.

## Contenu du dépôt
- [SYSTEM_PROMPT.md](./SYSTEM_PROMPT.md) : Le prompt système "astronomique" à donner à votre IA pour activer Astra.
- [INSTALLATION_GUIDE.md](./INSTALLATION_GUIDE.md) : Guide technique pour installer l'environnement nécessaire sur Android et PC.

## Utilisation
1. Suivez le guide d'installation pour préparer votre environnement.
2. Installez les dépendances : `pip install -r requirements.txt`.
3. Lancez l'agent : `python astra.py`.
4. Copiez le contenu de `SYSTEM_PROMPT.md` dans votre interface de chat IA si vous souhaitez configurer une instance personnalisée.

### Commandes Astra
- Tapez vos requêtes normalement.
- Exemple : "Crée un fichier test.py"
- Pour quitter : tapez `exit` ou `quitter`.
