from flask import Flask, render_template, url_for, redirect
import os
import requests

app = Flask(__name__)

# Chemin pour stocker les scripts téléchargés
SCRIPTS_DIR = "scripts/nse"
GITHUB_URL = "https://raw.githubusercontent.com/cldrn/nmap-nse-scripts/master/scripts/"

def download_scripts():
    """Télécharge les scripts NSE depuis GitHub."""
    os.makedirs(SCRIPTS_DIR, exist_ok=True)
    scripts_url = "https://api.github.com/repos/cldrn/nmap-nse-scripts/contents/scripts"
    response = requests.get(scripts_url)
    if response.status_code == 200:
        scripts = response.json()
        for script in scripts:
            if script["name"].endswith(".nse"):
                script_path = os.path.join(SCRIPTS_DIR, script["name"])
                if not os.path.exists(script_path):
                    content = requests.get(script["download_url"]).text
                    with open(script_path, "w") as file:
                        file.write(content)

def get_scripts():
    """Récupère la liste des scripts NSE disponibles localement."""
    if not os.path.exists(SCRIPTS_DIR):
        download_scripts()
    return [{"name": script, "path": f"{SCRIPTS_DIR}/{script}"} for script in os.listdir(SCRIPTS_DIR) if script.endswith(".nse")]

@app.route("/")
def home():
    scripts = get_scripts()
    return render_template("home.html", scripts=scripts)

@app.route("/script/<script_name>")
def script_details(script_name):
    script_path = os.path.join(SCRIPTS_DIR, script_name)
    if not os.path.exists(script_path):
        return "Script introuvable", 404
    with open(script_path, "r") as file:
        content = file.read()
    return render_template("script_details.html", script_name=script_name, content=content)

@app.route("/refresh")
def refresh_scripts():
    """Met à jour la liste des scripts."""
    download_scripts()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
