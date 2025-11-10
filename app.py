from flask import Flask, jsonify
import requests

app = Flask(__name__)

GITHUB_TOKEN = "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"
CODESPACE_NAME = "fuzzy-potato-x54rxp4499wrh9q7v"
BASE_URL = f"https://api.github.com/user/codespaces/{CODESPACE_NAME}"

@app.route("/")
def home():
    return jsonify({"status": "online", "mensagem": "API_NLS está rodando 24h!"})

@app.route("/status")
def status_codespace():
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    r = requests.get(BASE_URL, headers=headers)
    if r.status_code != 200:
        return jsonify({"erro": r.text}), 500
    data = r.json()
    return jsonify({"state": data["state"], "name": data["name"]})

@app.route("/ligar", methods=["POST"])
def ligar_codespace():
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    r = requests.get(BASE_URL, headers=headers)
    if r.status_code != 200:
        return jsonify({"erro": r.text}), 500

    state = r.json().get("state")
    if state == "Available":
        res = requests.post(f"{BASE_URL}/start", headers=headers)
        if res.status_code in (200, 202):
            return jsonify({"status": "ligando", "mensagem": "Codespace sendo iniciado..."})
        return jsonify({"erro": res.text}), 500
    elif state == "Running":
        return jsonify({"status": "ativo", "mensagem": "Codespace já está online!"})
    else:
        return jsonify({"status": state, "mensagem": "Codespace em outro estado."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
