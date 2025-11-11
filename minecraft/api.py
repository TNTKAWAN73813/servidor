from flask import Flask, jsonify
from flask_cors import CORS
import subprocess
import socket
import threading
import time
import os
import json

app = Flask(__name__)
CORS(app)

SERVER_NAME = "Fsntjava"
MINECRAFT_PORT = 25565
TUNNEL_FILE = "/workspaces/servidor/minecraft/tunnel.json"
CHECK_INTERVAL = 2  # segundos entre checagens

# Status global
status_data = {
    "crafty_running": False,
    "minecraft_online": False,
    "tunnel_ready": False,
    "ip": "",
    "message": "Carregando status..."
}

# --- Funções ---
def is_crafty_running():
    try:
        output = subprocess.check_output("pgrep -f crafty", shell=True)
        return bool(output)
    except subprocess.CalledProcessError:
        return False

def is_minecraft_online():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect(("127.0.0.1", MINECRAFT_PORT))
        s.close()
        return True
    except:
        return False

def get_tunnel_ip():
    if os.path.exists(TUNNEL_FILE):
        try:
            with open(TUNNEL_FILE) as f:
                data = json.load(f)
            return data.get('host', '')
        except:
            pass
    return ""

def monitor_status():
    while True:
        crafty = is_crafty_running()
        minecraft_online = is_minecraft_online() if crafty else False
        tunnel_ip = get_tunnel_ip()
        tunnel_ready = bool(tunnel_ip)

        if crafty and minecraft_online:
            message = "Servidor Minecraft Online ✅"
        elif crafty:
            message = "Crafty Online 🌟\nLigando Minecraft... ⏳"
        else:
            message = "Crafty Controller desligado ❌"

        status_data['crafty_running'] = crafty
        status_data['minecraft_online'] = minecraft_online
        status_data['tunnel_ready'] = tunnel_ready
        status_data['ip'] = f"{tunnel_ip}:{MINECRAFT_PORT}" if tunnel_ready else ""
        status_data['message'] = message

        time.sleep(CHECK_INTERVAL)

# Endpoint de status
@app.route("/status")
def status():
    return jsonify({
        "running": status_data['minecraft_online'],
        "server_name": SERVER_NAME,
        "ip": status_data['ip'] or "127.0.0.1:25565",
        "message": status_data['message']
    })

# Inicia monitoramento
threading.Thread(target=monitor_status, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
