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

# 3️⃣ Iniciar API Flask (painel HTML)
echo "🧩 Iniciando NLS API do painel..."
python3 /workspaces/servidor/minecraft/api.py > /tmp/api.log 2>&1 &
API_PID=$!
echo "📌 API PID: $API_PID"

# 4️⃣ Iniciar Playit (túnel externo)
echo "🌐 Iniciando Playit..."
playit > /tmp/playit.log 2>&1 &
PLAYIT_PID=$!
echo "📌 Playit PID: $PLAYIT_PID"

# 5️⃣ Espera Playit/NLS inicializarem
echo "⏳ Aguardando Playit e NLS ficarem prontos..."
sleep 15  # tempo estimado para criar túnel

# 6️⃣ Iniciar Crafty Controller (servidor Minecraft)
echo "🔧 Iniciando Crafty Controller..."
bash /workspaces/servidor/minecraft/run_crafty.sh > /tmp/run_crafty.log 2>&1 &
CRAFTY_PID=$!
echo "📌 Crafty PID: $CRAFTY_PID"

# 7️⃣ Mensagem final
echo "✅ Todos os serviços foram iniciados!"
echo "📜 Logs disponíveis em:"
echo " - /tmp/run_crafty.log"
echo " - /tmp/playit.log"
echo " - /tmp/api.log"
echo "Use 'ps aux | grep crafty' para verificar o Crafty Controller."
