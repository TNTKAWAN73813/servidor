from flask import Flask, jsonify
import subprocess
import requests
import time

app = Flask(__name__)

# Configurações
CODESPACE_API = "https://servidor-or05.onrender.com/start-server"
CODESPACE_STATUS_API = "https://fuzzy-potato-x54rxp4499wrh9q7v-8080.app.github.dev/status"
CODESPACE_START_CMD = "gh codespace start -R SEU_USUARIO/SEU_REPOSITORIO"
MAX_WAIT_SECONDS = 60
CHECK_INTERVAL = 5

@app.route("/start-codespace", methods=["POST"])
def start_codespace():
    # Verifica se Codespace já está online
    try:
        status_res = requests.get(CODESPACE_STATUS_API, timeout=3)
        status_res.raise_for_status()
        status = status_res.json()
        if status.get("running"):
            # Minecraft já rodando, retorna info
            return jsonify({"success": True, "server_info": status})
    except requests.exceptions.RequestException:
        pass  # Codespace desligado, precisa ligar

    # Liga Codespace
    try:
        subprocess.run(CODESPACE_START_CMD, shell=True, check=True)
    except subprocess.CalledProcessError:
        return jsonify({"success": False, "error": "Falha ao iniciar Codespace"}), 500

    # Espera Codespace ficar online
    start_time = time.time()
    while True:
        try:
            status_res = requests.get(CODESPACE_STATUS_API, timeout=3)
            if status_res.status_code == 200:
                break
        except requests.exceptions.RequestException:
            pass

        if time.time() - start_time > MAX_WAIT_SECONDS:
            return jsonify({"success": False, "error": "Timeout ao esperar Codespace"}), 504

        time.sleep(CHECK_INTERVAL)

    # Chama NLS para iniciar Minecraft
    try:
        start_res = requests.post(CODESPACE_API, timeout=10)
        server_info = start_res.json()
        return jsonify({"success": True, "server_info": server_info})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
