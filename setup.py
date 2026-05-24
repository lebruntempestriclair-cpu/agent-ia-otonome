import os
import sys
import subprocess

def run_command(command):
    print(f"[*] Exécution : {command}")
    try:
        subprocess.check_call(command, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"[!] Erreur lors de l'exécution de {command}: {e}")
        return False
    return True

def setup():
    print("=== Configuration de l'Agent Astra ===")

    # 1. Vérification de Python
    print(f"[*] Version de Python détectée : {sys.version}")

    # 2. Création des répertoires nécessaires
    if not os.path.exists("projects"):
        os.makedirs("projects")
        print("[+] Répertoire 'projects' créé.")

    # 3. Installation des dépendances
    if os.path.exists("requirements.txt"):
        print("[*] Installation des dépendances...")
        if run_command(f"{sys.executable} -m pip install -r requirements.txt"):
            print("[+] Dépendances installées avec succès.")
        else:
            print("[!] Échec de l'installation des dépendances.")

    # 4. Initialisation du fichier .env
    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write("OPENAI_API_KEY=votre_cle_ici\n")
            f.write("ANTHROPIC_API_KEY=votre_cle_ici\n")
        print("[+] Fichier .env créé. N'oubliez pas d'y ajouter vos clés API.")

    # 5. Spécificités Android (Termux)
    if "ANDROID_ROOT" in os.environ:
        print("[*] Environnement Android détecté. Installation des outils Termux:API...")
        run_command("pkg install termux-api -y")

    print("\n=== Configuration terminée ! ===")
    print("Pour lancer l'agent, tapez : python astra.py")

if __name__ == "__main__":
    setup()
