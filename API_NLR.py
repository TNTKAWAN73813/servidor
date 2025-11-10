from flask import Flask, request, jsonify
import os
import requests
import time

app = Flask(__name__)

# Token do GitHub (variável de ambiente no Railway)
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
CODESPACE_NAME = "servidor"  # o nome do Codespace no GitHub
REPO = "TNTKAWAN73813/servidor"  # seu repo

# URL da NLS dentro do Codespace
NLS_URL = "https://fuzzy-potato-x54rxp4499wrh9q7v-8080.app.github.dev/"  # exemplo, ajustar conforme NLS


def is_codespace_running():
    """Verifica se o Codespace está ativo via API GitHub"""
    url = f"https://api.github.com/user/codespaces"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return False
    codespaces = response.json().get("codespaces", [])
    for cs in codespaces:
        if cs["repository"]["full_name"] == REPO:
            if cs["state"] == "Available":
                return True
    return False


def start_codespace():
    """Liga o Codespace via GitHub API"""
    url = f"https://api.github.com/user/codespaces"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    data = {
        "repository": REPO
    }
    response = requests.post(url, json=data, headers=headers)
    return response.status_code == 201 or response.status_code == 200


def call_nls():
    """Chama a NLS dentro do Codespace para iniciar Minecraft + túnel"""
    try:
        res = requests.post(NLS_URL, timeout=10)
        if res.status_code == 200:
            return res.json()
        else:
            return {"running": False, "error": "NLS retornou erro"}
    except Exception as e:
        return {"running": False, "error": str(e)}


@app.route("/start-codespace", methods=["POST"])
def start():
    # Verifica se o Codespace já está ligado
    if not is_codespace_running():
        started = start_codespace()
        if not started:
            return jsonify({"success": False, "error": "Falha ao iniciar Codespace"})

        # Aguardar Codespace ficar disponível
        for _ in range(30):  # até 150s
            time.sleep(5)
            if is_codespace_running():
                break
        else:
            return jsonify({"success": False, "error": "Timeout Codespace"})

    # Chama a NLS
    nls_status = call_nls()

    return jsonify({
        "success": True,
        "server_info": nls_status
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
