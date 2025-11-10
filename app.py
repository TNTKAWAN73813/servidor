import os
import requests

GITHUB_TOKEN = os.getenv("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")
CODESPACE_NAME = os.getenv("fuzzy-potato-x54rxp4499wrh9q7v")
NLS_URL = os.getenv("https://fuzzy-potato-x54rxp4499wrh9q7v-8080.app.github.dev")

def start_codespace():
    url = f"https://api.github.com/user/codespaces/{CODESPACE_NAME}/start"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    r = requests.post(url, headers=headers)
    if r.status_code not in [202, 204]:
        raise Exception(f"Erro ao iniciar Codespace: {r.status_code} {r.text}")
