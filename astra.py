import os
import json
import subprocess
import platform
from datetime import datetime

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
