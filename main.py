from flask import Flask, render_template, redirect, url_for
import os
import requests

app = Flask(__name__)

# Dossiers GitHub à explorer
BASE_URL = "https://api.github.com/repos/tucommenceapousser/nmap-nse-scripts/contents"
SCRIPT_FOLDERS = ["scripts", "old-scripts"]

# Chemin de stockage local pour les scripts
SCRIPTS_DIR = "downloaded_scripts"

def download_scripts():
    """Télécharge les scripts NSE depuis les deux dossiers définis."""
    os.makedirs(SCRIPTS_DIR, exist_ok=True)
    for folder in SCRIPT_FOLDERS:
        folder_url = f"{BASE_URL}/{folder}"
        response = requests.get(folder_url)
        if response.status_code == 200:
            files = response.json()
            folder_path = os.path.join(SCRIPTS_DIR, folder)
            os.makedirs(folder_path, exist_ok=True)
            for file in files:
                if file.get("name", "").endswith(".nse"):
                    script_path = os.path.join(folder_path, file["name"])
                    if not os.path.exists(script_path):  # Vérifier si le fichier existe déjà
                        print(f"Téléchargement de {file['name']} dans {folder}")
                        content = requests.get(file["download_url"]).text
                        with open(script_path, "w") as f:
                            f.write(content)
                    else:
                        print(f"Le script {file['name']} existe déjà dans {folder}")
        else:
            print(f"Impossible d'accéder au dossier : {folder}")

def get_scripts():
    """Récupère les scripts NSE organisés par dossier."""
    scripts = {}
    if not os.path.exists(SCRIPTS_DIR):
        download_scripts()  # Télécharger les scripts si le répertoire est vide
    for folder in SCRIPT_FOLDERS:
        folder_path = os.path.join(SCRIPTS_DIR, folder)
        if os.path.exists(folder_path):
            scripts[folder] = [
                {"name": script, "path": os.path.join(folder, script)}  # Utiliser le chemin absolu
                for script in os.listdir(folder_path) if script.endswith(".nse")
            ]
    return scripts

@app.route("/")
def home():
    scripts = get_scripts()
    return render_template("home.html", scripts=scripts)

@app.route("/script/<folder>/<script_name>")
def script_details(folder, script_name):
    script_path = os.path.join(SCRIPTS_DIR, folder, script_name)
    if not os.path.exists(script_path):
        return "Script introuvable", 404
    with open(script_path, "r") as file:
        content = file.read()
    return render_template("script_details.html", folder=folder, script_name=script_name, content=content)

@app.route("/refresh")
def refresh_scripts():
    download_scripts()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8000)
