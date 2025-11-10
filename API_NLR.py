from flask import Flask, jsonify
from flask_cors import CORS
import requests
import os
import time

app = Flask(__name__)
CORS(app)

# Configurações
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
CODESPACE_NAME = "fuzzy-potato-x54rxp4499wrh9q7v"  # nome do seu Codespace
NLS_URL = "https://fuzzy-potato-x54rxp4499wrh9q7v-8080.app.github.dev"   # URL interna da NLS dentro do Codespace

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

def start_codespace_and_nls():
    # 1️⃣ Liga o Codespace
    start_url = f"https://api.github.com/user/codespaces/{CODESPACE_NAME}/start"
    r = requests.post(start_url, headers=HEADERS)
    if r.status_code not in (200, 201, 204):
        return False, r.json()

    # 2️⃣ Espera o Codespace ficar pronto
    time.sleep(15)  # ajustar se necessário

    # 3️⃣ Executa comando dentro do Codespace para iniciar a NLS
    exec_url = f"https://api.github.com/user/codespaces/{CODESPACE_NAME}/commands"
    data = {
        "command": "bash /workspaces/servidor/start_nls.sh"
    }
    r2 = requests.post(exec_url, headers=HEADERS, json=data)
    if r2.status_code not in (200, 201):
        return False, r2.json()

    # 4️⃣ Retorna sucesso e URL da NLS
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
