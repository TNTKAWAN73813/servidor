from flask import Flask, jsonify
from flask_cors import CORS
import subprocess
import os
import json
import requests
import socket
import time

app = Flask(__name__)
CORS(app)

# --- Configurações ---
SERVER_NAME = "Fsntjava"
TUNNEL_FILE = "/workspaces/servidor/minecraft/tunnel.json"
MINECRAFT_PORT = 25565

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
CODESPACE_NAME = "fuzzy-potato-x54rxp4499wrh9q7v"
NLR_URL = "https://web-production-fefbf.up.railway.app/start-codespace"

# --- Funções ---
def is_crafty_running():
    """Verifica se o Crafty está rodando"""
    try:
        output = subprocess.check_output("pgrep -f crafty", shell=True)
        return bool(output)
    except subprocess.CalledProcessError:
        return False

def is_minecraft_online(ip, port):
    """Tenta conectar no Minecraft para verificar se está realmente online"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect((ip, port))
        s.close()
        return True
    except:
        return False

def get_minecraft_ip():
    """Retorna IP do Minecraft via Playit ou IP público"""
    if os.path.exists(TUNNEL_FILE):
        try:
            with open(TUNNEL_FILE) as f:
                data = json.load(f)
            return data['host']
        except:
            pass
    try:
        return requests.get("https://api.ipify.org").text
    except:
        return ""

def start_codespace_and_nls():
    """Liga o Codespace via NLR caso esteja desligado"""
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    start_url = f"https://api.github.com/user/codespaces/{CODESPACE_NAME}/start"

    try:
        r = requests.post(start_url, headers=headers)
        if r.status_code not in (200, 201, 204):
            return False, r.json()
    except Exception as e:
        return False, str(e)

    # Espera alguns segundos até Codespace e NLS estarem prontos
    time.sleep(20)
    return True, f"https://{CODESPACE_NAME}-8080.app.github.dev"

# --- Endpoints ---
@app.route("/status")
def status():
    crafty_running = is_crafty_running()
    ip = get_minecraft_ip()
    minecraft_online = False

    if crafty_running and ip:
        minecraft_online = is_minecraft_online(ip, MINECRAFT_PORT)

    return jsonify({
        "running": minecraft_online,
        "server_name": SERVER_NAME,
        "ip": f"{ip}:{MINECRAFT_PORT}" if minecraft_online else ""
    })

@app.route("/start-minecraft", methods=["POST"])
def start_minecraft():
    """Liga Codespace/NLS e retorna info inicial"""
    success, data = start_codespace_and_nls()
    if not success:
        return jsonify({"success": False, "error": data}), 500

    return jsonify({
        "success": True,
        "nls_url": data,
        "message": "Codespace/NLS iniciado. Minecraft pode demorar alguns segundos para subir."
    })

# --- Execução ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
