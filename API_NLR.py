import os
import requests
from flask import Flask, jsonify
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)  # Permite que seu site chame a API

# Pega o token do GitHub da variável de ambiente
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
REPO = "TNTKAWAN73813/servidor"
BRANCH = "main"

# Tempo de espera para o Codespace iniciar (segundos)
WAIT_SECONDS = 20

@app.post("/start-codespace")
def start_codespace():
    """Inicia o Codespace usando GitHub API"""
    if not GITHUB_TOKEN:
        return jsonify({"success": False, "error": "Token não configurado"}), 500

    url = "https://api.github.com/user/codespaces"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    data = {
        "repository": REPO,
        "ref": BRANCH
    }

    try:
        resp = requests.post(url, headers=headers, json=data)
        if resp.status_code in [200, 201]:
            # Opcional: esperar alguns segundos para o Codespace iniciar
            time.sleep(WAIT_SECONDS)
            return jsonify({"success": True, "message": "Codespace iniciado!"})
        else:
            return jsonify({"success": False, "error": resp.json()})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.get("/status-codespace")
def status_codespace():
    """Retorna status dos Codespaces existentes no repositório"""
    if not GITHUB_TOKEN:
        return jsonify({"success": False, "error": "Token não configurado"}), 500

    url = f"https://api.github.com/repos/{REPO}/codespaces"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    try:
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            running = len(data.get("codespaces", [])) > 0
            return jsonify({"success": True, "running": running, "codespaces": data.get("codespaces", [])})
        else:
            return jsonify({"success": False, "error": resp.json()})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == "__main__":
    # Porta 100% compatível com Render
    app.run(host="0.0.0.0", port=10000)
