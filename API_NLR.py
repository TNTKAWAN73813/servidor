from flask import Flask, jsonify
from flask_cors import CORS
import subprocess
import time
import os
import requests

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Configurações
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
CODESPACE_NAME = "fuzzy-potato-x54rxp4499wrh9q7v"
NLS_URL = "https://fuzzy-potato-x54rxp4499wrh9q7v-8080.app.github.dev"
STARTUP_SCRIPT = "/workspaces/servidor/startup.sh"

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

def start_codespace_and_nls():
    # 1️⃣ Liga o Codespace via GitHub API
    start_url = f"https://api.github.com/user/codespaces/{CODESPACE_NAME}/start"
    r = requests.post(start_url, headers=HEADERS)

    if r.status_code == 409:
        # Codespace já ativo
        print("Codespace já ativo, pulando start...")
    elif r.status_code not in (200, 201, 204):
        return False, r.json()
    else:
        time.sleep(20)  # espera Codespace subir

    # 2️⃣ Executa startup.sh via bash
    try:
        subprocess.Popen(["bash", STARTUP_SCRIPT])
    except Exception as e:
        return False, {"error": f"Erro ao executar startup.sh: {e}"}

    # 3️⃣ Espera NLS/API do Minecraft responder
    print("⏳ Aguardando NLS/API responder...")
    for _ in range(15):  # tenta por ~45s
        try:
            res = requests.get(NLS_URL + "/status", timeout=2)
            if res.ok:
                return True, {"nls_url": NLS_URL}
        except:
            time.sleep(3)

    return False, {"error": "NLS não respondeu após 45s"}

# --- Rotas ---
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
