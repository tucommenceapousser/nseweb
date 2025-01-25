from flask import Flask, render_template, url_for, redirect
import os
import requests

app = Flask(__name__)

# Chemin pour stocker les scripts téléchargés
SCRIPTS_DIR = "scripts"
GITHUB_REPOS = {
    "cldrn": "https://api.github.com/repos/cldrn/nmap-nse-scripts/contents/scripts",
    "httprecon": "https://api.github.com/repos/scipag/httprecon-nse/contents",
    "psc4re": "https://api.github.com/repos/psc4re/NSE-scripts/contents",
    "r00t-3xp10it": "https://api.github.com/repos/r00t-3xp10it/nmap-nse-modules/contents",
    "Z-0ne": "https://api.github.com/repos/Z-0ne/ScanS2-045-Nmap/contents",
    "aerissecure": "https://api.github.com/repos/aerissecure/nse/contents",
    "dorkerdevil": "https://api.github.com/repos/dorkerdevil/NMAP-BRUTEFORCER-private-script-/contents",
    "mmpx12": "https://api.github.com/repos/mmpx12/nse-country-scan/contents",
}

def download_scripts():
    """Télécharge les scripts NSE depuis chaque dépôt GitHub configuré."""
    os.makedirs(SCRIPTS_DIR, exist_ok=True)
    for repo_name, repo_url in GITHUB_REPOS.items():
        repo_dir = os.path.join(SCRIPTS_DIR, repo_name)
        os.makedirs(repo_dir, exist_ok=True)
        response = requests.get(repo_url)
        if response.status_code == 200:
            scripts = response.json()
            for script in scripts:
                if script.get("name", "").endswith(".nse"):
                    script_path = os.path.join(repo_dir, script["name"])
                    if not os.path.exists(script_path):
                        content = requests.get(script["download_url"]).text
                        with open(script_path, "w") as file:
                            file.write(content)

def get_scripts():
    """Récupère les scripts NSE téléchargés par dépôt."""
    scripts = {}
    if not os.path.exists(SCRIPTS_DIR):
        download_scripts()
    for repo_name in os.listdir(SCRIPTS_DIR):
        repo_path = os.path.join(SCRIPTS_DIR, repo_name)
        if os.path.isdir(repo_path):
            scripts[repo_name] = [
                {"name": script, "path": f"{repo_path}/{script}"}
                for script in os.listdir(repo_path) if script.endswith(".nse")
            ]
    return scripts

@app.route("/")
def home():
    scripts = get_scripts()
    return render_template("home.html", scripts=scripts)

@app.route("/script/<repo_name>/<script_name>")
def script_details(repo_name, script_name):
    script_path = os.path.join(SCRIPTS_DIR, repo_name, script_name)
    if not os.path.exists(script_path):
        return "Script introuvable", 404
    with open(script_path, "r") as file:
        content = file.read()
    return render_template("script_details.html", repo_name=repo_name, script_name=script_name, content=content)

@app.route("/refresh")
def refresh_scripts():
    """Met à jour tous les scripts des dépôts."""
    download_scripts()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
