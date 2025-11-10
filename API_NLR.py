from flask import Flask, jsonify
from flask_cors import CORS
import subprocess
import time
import re
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # ✅ libera acesso de qualquer origem

# ⚙️ Configurações
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
CODESPACE_NAME = "fuzzy-potato-x54rxp4499wrh9q7v"  # nome exato do seu Codespace
NLS_URL = "https://fuzzy-potato-x54rxp4499wrh9q7v-8080.app.github.dev/status"  # URL do NLS dentro do Codespace

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}


def start_codespace_and_nls():
    # 1️⃣ Liga o Codespace pelo GitHub API
    start_url = f"https://api.github.com/user/codespaces/{CODESPACE_NAME}/start"
    r = requests.post(start_url, headers=HEADERS)
    if r.status_code not in (200, 201, 204):
        return False, r.json()

    # 2️⃣ Espera alguns segundos até o Codespace iniciar e rodar o NLS
    time.sleep(20)

    # 3️⃣ Retorna a URL da NLS (que já estará rodando)
    return True, {"nls_url": NLS_URL}


@app.post("/start-codespace")
def start_codespace_endpoint():
    if not GITHUB_TOKEN:
        return jsonify({"success": False, "error": "Token não configurado"}), 400

    success, info = start_codespace_and_nls()
    if success:
        return jsonify({"success": True, "nls_url": info["nls_url"]})
    else:
        return jsonify({"success": False, "error": info})


@app.get("/")
def home():
    return jsonify({"status": "ok", "message": "API-NLR ativa!"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
