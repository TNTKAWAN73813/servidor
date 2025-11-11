#!/bin/bash
# ====== Script Inteligente de Inicialização do Minecraft ======
echo "🚀 Iniciando configuração automática..."

# 1️⃣ Mata instâncias antigas do Crafty Controller
echo "🛑 Encerrando instâncias antigas do Crafty Controller..."
pkill -f run_crafty.sh 2>/dev/null || true

# 2️⃣ Tornar a porta 8080 pública
if [ ! -z "$CODESPACE_NAME" ]; then
  echo "🌍 Tornando a porta 8080 pública..."
  gh codespace ports visibility 8080:public -c $CODESPACE_NAME
else
  echo "⚠️ Variável CODESPACE_NAME não encontrada."
fi

# 3️⃣ Iniciar API Flask (NLS)
echo "🧩 Iniciando NLS API do painel..."
python3 /workspaces/servidor/minecraft/api.py > /tmp/api.log 2>&1 &
API_PID=$!
echo "📌 API PID: $API_PID"

# 4️⃣ Esperar NLS subir
echo "⏳ Aguardando NLS/API responder..."
TRIES=0
until curl -s http://127.0.0.1:8080/status > /dev/null; do
  sleep 3
  TRIES=$((TRIES+1))
  if [ $TRIES -gt 30 ]; then
    echo "❌ NLS não respondeu após 90s"
    exit 1
  fi
done
echo "✅ NLS/API está ativa!"

# 5️⃣ Iniciar Playit (túnel externo)
echo "🌐 Iniciando Playit..."
playit > /tmp/playit.log 2>&1 &
PLAYIT_PID=$!
echo "📌 Playit PID: $PLAYIT_PID"

# 6️⃣ Espera Playit/NLS inicializarem
sleep 15  # tempo estimado para criar túnel

# 7️⃣ Iniciar Crafty Controller (Minecraft)
echo "🔧 Iniciando Crafty Controller..."
bash /workspaces/servidor/minecraft/run_crafty.sh > /tmp/run_crafty.log 2>&1 &
CRAFTY_PID=$!
echo "📌 Crafty PID: $CRAFTY_PID"

# 8️⃣ Mensagem final
echo "✅ Todos os serviços foram iniciados!"
echo "📜 Logs disponíveis em:"
echo " - /tmp/run_crafty.log"
echo " - /tmp/playit.log"
echo " - /tmp/api.log"
echo "Use 'ps aux | grep crafty' para verificar o Crafty Controller."
