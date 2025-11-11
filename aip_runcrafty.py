from flask import Flask, jsonify
from flask_cors import CORS
import subprocess
import os
import json
import requests
import time

app = Flask(__name__)
CORS(app)  # libera acesso de qualquer origem

# --- Configurações ---
SERVER_NAME = "Fsntjava"
MINECRAFT_PORT = 25565
TUNNEL_FILE = "/workspaces/servidor/minecraft/tunnel.json"  # arquivo do Playit
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
CODESPACE_NAME = "fuzzy-potato-x54rxp4499wrh9q7v"
NLR_URL = "https://web-production-fefbf.up.railway.app/start-codespace"

# URL inicial do NLS (dentro do Codespace)
nls_url = f"https://{CODESPACE_NAME}-8080.app.github.dev"

