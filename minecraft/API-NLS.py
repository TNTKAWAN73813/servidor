from flask import Flask, jsonify
from flask_cors import CORS
import subprocess
import time
import re
import os

app = Flask(__name__)
CORS(app)

PLAYIT_WAIT_SECONDS = 15
CRAFTY_SCRIPT = "/workspaces/servidor/minecraft/run_crafty.sh"
PLAYIT_LOG = "/tmp/playit.log"

def start_background(cmd):
    full_cmd = f"nohup {cmd} > /tmp/bg_process.log 2>&1 &"
    return subprocess.Popen(["bash", "-c", full_cmd])

@app.post("/start-server")
def start_server():
    if not os.path.exists(CRAFTY_SCRIPT):
        return jsonify({"status": "error", "message": f"Script não encontrado: {CRAFTY_SCRIPT}"}), 404

    start_background(f"bash {CRAFTY_SCRIPT}")  # inicia Minecraft
    start_background("playit")  # inicia Playit

    ip_text = "Aguardando endereço do Playit..."
    for _ in range(PLAYIT_WAIT_SECONDS):
        time.sleep(1)
        if os.path.exists(PLAYIT_LOG):
            try:
                log = open(PLAYIT_LOG, "r", encoding="utf-8", errors="ignore").read()
                m = re.search(r"([\w\.-]+\.playit\.gg:\d+)", log)
                if m:
                    ip_text = m.group(1)
                    break
            except Exception:
                pass

    return jsonify({"status": "ok", "message": "Servidor iniciado!", "ip": ip_text})

@app.get("/status")
def status():
    try:
        out = subprocess.check_output(
            ["bash", "-lc", "ps aux | grep -v grep | grep -E 'crafty|run_crafty' || true"],
            shell=False, universal_newlines=True
        )
        running = bool(out.strip())
    except Exception:
        running = False

    ip = ""
    if os.path.exists(PLAYIT_LOG):
        try:
            log = open(PLAYIT_LOG, "r", encoding="utf-8", errors="ignore").read()
            m = re.search(r"([\w\.-]+\.playit\.gg:\d+)", log)
            if m:
                ip = m.group(1)
        except Exception:
            pass

    return jsonify({"running": running, "ip": ip})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
