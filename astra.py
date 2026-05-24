import os
import json
import subprocess
import platform
import shutil
from datetime import datetime

class ProjectManager:
    """Gère la création de structures de projets pour Astra."""

    @staticmethod
    def create_web_scaffold(project_name):
        base_path = os.path.join("projects", project_name)
        os.makedirs(os.path.join(base_path, "src", "css"), exist_ok=True)
        os.makedirs(os.path.join(base_path, "src", "js"), exist_ok=True)

        with open(os.path.join(base_path, "index.html"), "w") as f:
            f.write("<!DOCTYPE html><html><head><title>" + project_name + "</title></head><body><h1>Projet Astra</h1></body></html>")

        print(f"[*] Projet Web '{project_name}' échafaudé dans {base_path}")
        return base_path

    @staticmethod
    def create_python_scaffold(project_name):
        base_path = os.path.join("projects", project_name)
        os.makedirs(base_path, exist_ok=True)
        with open(os.path.join(base_path, "main.py"), "w") as f:
            f.write("def main():\n    print('Hello from Astra!')\n\nif __name__ == '__main__':\n    main()")

        with open(os.path.join(base_path, "requirements.txt"), "w") as f:
            f.write("")

        print(f"[*] Projet Python '{project_name}' échafaudé dans {base_path}")
        return base_path

class SystemGuard:
    """Fournit une couche de sécurité pour les commandes système."""

    FORBIDDEN_KEYWORDS = ["rm -rf /", "mkfs", "shutdown", ":(){ :|:& };:"]

    @classmethod
    def is_safe(cls, command):
        for keyword in cls.FORBIDDEN_KEYWORDS:
            if keyword in command:
                return False
        return True

class HardwareManager:
    """Interface avec les capteurs et le matériel (priorité Android)."""

    @staticmethod
    def get_battery_info():
        if "ANDROID_ROOT" in os.environ:
            res = subprocess.run(["termux-battery-status"], capture_output=True, text=True)
            return json.loads(res.stdout) if res.returncode == 0 else {"error": "Termux:API non disponible"}
        return {"error": "Non disponible sur ce système"}

    @staticmethod
    def get_location():
        if "ANDROID_ROOT" in os.environ:
            res = subprocess.run(["termux-location"], capture_output=True, text=True)
            return json.loads(res.stdout) if res.returncode == 0 else {"error": "Localisation non disponible"}
        return {"error": "Non disponible sur ce système"}

class AstraAgent:
    def __init__(self, state_file="astra_state.json"):
        self.state_file = state_file
        self.state = self.load_state()
        self.system_info = self.get_system_info()

    def load_state(self):
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "history": [],
            "tasks": [],
            "memory": {},
            "last_backup": None
        }

    def save_state(self):
        self.state["last_backup"] = datetime.now().isoformat()
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=4, ensure_ascii=False)
        print(f"[*] État sauvegardé à {self.state['last_backup']}")

    def get_system_info(self):
        return {
            "os": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "is_android": "ANDROID_ROOT" in os.environ
        }

    def speak(self, text):
        print(f"Astra: {text}")
        if self.system_info["is_android"]:
            # Tentative d'utilisation de Termux-TTS
            subprocess.run(["termux-tts-speak", text], capture_output=True)
        else:
            # Sur PC, on pourrait utiliser pyttsx3 ici
            pass

    def execute_command(self, command):
        if not SystemGuard.is_safe(command):
            return {"error": "Commande bloquée par SystemGuard pour des raisons de sécurité."}
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "code": result.returncode
            }
        except Exception as e:
            return {"error": str(e)}

    def run_task(self, task_description):
        print(f"[!] Exécution de la tâche : {task_description}")
        # Ici, normalement, on appellerait l'LLM pour décider quoi faire.
        # Pour cette implémentation, nous simulons une réponse.
        self.state["tasks"].append({
            "description": task_description,
            "timestamp": datetime.now().isoformat(),
            "status": "completed"
        })
        self.save_state()

    def main_loop(self):
        self.speak("Système Astra initialisé. Comment puis-je vous aider ?")
        while True:
            try:
                user_input = input("\nVous > ")
                if user_input.lower() in ['exit', 'quitter', 'stop']:
                    self.speak("Arrêt du système. À bientôt.")
                    break

                # Logique simplifiée pour l'exemple
                if "crée" in user_input.lower() and "fichier" in user_input.lower():
                    filename = "nouveau_projet.txt"
                    with open(filename, "w") as f:
                        f.write("Projet créé par Astra.")
                    self.speak(f"J'ai créé le fichier {filename}.")
                else:
                    self.run_task(user_input)
                    self.speak("Tâche traitée et sauvegardée.")

            except KeyboardInterrupt:
                break

if __name__ == "__main__":
    agent = AstraAgent()
    agent.main_loop()
