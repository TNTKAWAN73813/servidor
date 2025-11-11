from flask import Flask, jsonify
from flask_cors import CORS
import requests
import os
import subprocess
import time

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
CODESPACE_NAME = "fuzzy-potato-x54rxp4499wrh9q7v"
NLS_URL = "http://127.0.0.1:8080"  # dentro do Codespace

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

def start_codespace():
    """Liga o Codespace via GitHub API"""
    start_url = f"https://api.github.com/user/codespaces/{CODESPACE_NAME}/start"
    r = requests.post(start_url, headers=HEADERS)
    if r.status_code in (200, 201, 204):
        return True
    elif r.status_code == 409:
        # Codespace já estava rodando
        return True
    else:
        return False, r.json()

def run_startup():
    """Executa o startup.sh"""
    cmd = "/workspaces/servidor/startup.sh"
    if os.path.exists(cmd):
        try:
            subprocess.Popen(["bash", cmd])
            return True
        except Exception as e:
            return False, str(e)
    return False, "startup.sh não encontrado"

def wait_nls():
    """Espera NLS/API responder"""
    tries = 0
    while tries < 30:
        try:
            r = requests.get(NLS_URL + "/status", timeout=2)
            if r.ok:
                return True
        except:
            pass
        time.sleep(3)
        tries += 1
    return False

@app.post("/start-codespace")
def start_codespace_endpoint():
    if not GITHUB_TOKEN:
        return jsonify({"success": False, "error": "Token não configurado"}), 400

    success = start_codespace()
    if not success:
        return jsonify({"success": False, "error": "Erro ao iniciar Codespace"}), 500

    run_ok = run_startup()
    if run_ok is not True:
        return jsonify({"success": False, "error": f"Erro ao executar startup.sh: {run_ok[1]}"}), 500

    nls_ok = wait_nls()
    if not nls_ok:
        return jsonify({"success": False, "error": "NLS não respondeu após 90s"}), 500

    return jsonify({"success": True, "nls_url": NLS_URL})

@app.get("/")
def home():
    return jsonify({"status": "ok", "message": "API-NLR ativa!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
