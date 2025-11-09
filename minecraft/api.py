from flask import Flask, jsonify
from flask_cors import CORS
import subprocess
import time
import re
import os

app = Flask(__name__)
CORS(app)

# Tempo de espera para o playit criar o túnel
PLAYIT_WAIT_SECONDS = 15


def start_background(cmd):
    """Executa um comando em background com nohup (persiste mesmo se o terminal encerrar)."""
    full_cmd = f"nohup {cmd} > /tmp/bg_process.log 2>&1 &"
    return subprocess.Popen(["bash", "-c", full_cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE)


@app.post("/start")
def start_server():
    try:
        # 1️⃣ Inicia o Crafty Controller
        crafty_script = "/workspaces/servidor/minecraft/run_crafty.sh"
        if not os.path.exists(crafty_script):
            return jsonify({"status": "error", "message": f"Script não encontrado: {crafty_script}"}), 404

        start_background(f"bash {crafty_script}")

        # 2️⃣ Inicia o Playit (mantém em background com nohup)
        start_background("playit")

        # 3️⃣ Aguarda o Playit gerar o túnel
        ip_text = "Aguardando endereço do Playit..."
        for _ in range(PLAYIT_WAIT_SECONDS):
            time.sleep(1)
            if os.path.exists("/tmp/playit.log"):
                with open("/tmp/playit.log", "r", encoding="utf-8", errors="ignore") as f:
                    log = f.read()
                    m = re.search(r"([\w\.-]+\.playit\.gg:\d+)", log)
                    if m:
                        ip_text = m.group(1)
                        break

        return jsonify({"status": "ok", "message": "Servidor iniciado, aguarde alguns segundos...", "ip": ip_text})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.get("/status")
def status():
    try:
        # Verifica se Crafty está rodando
        out = subprocess.check_output(
            ["bash", "-lc", "ps aux | grep -v grep | grep -E 'crafty|run_crafty' || true"],
            shell=False, universal_newlines=True
        )
        running = bool(out.strip())
    except Exception:
        running = False

    # Busca IP do Playit (se já estiver ativo)
    ip = ""
    if os.path.exists("/tmp/playit.log"):
        try:
            log = open("/tmp/playit.log", "r", encoding="utf-8", errors="ignore").read()
            m = re.search(r"([\w\.-]+\.playit\.gg:\d+)", log)
            if m:
                ip = m.group(1)
        except Exception:
            pass

    return jsonify({"running": running, "ip": ip})


if __name__ == "__main__":
    # Garante que o container não pare por inatividade
    print("🌍 API iniciada em http://0.0.0.0:8080")
    app.run(host="0.0.0.0", port=8080)
