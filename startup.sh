#!/bin/bash
# ====== Início do Script de Inicialização ======
# Este script liga o servidor Minecraft automaticamente
# e garante que a porta 8080 esteja pública no GitHub Codespaces

echo "🚀 Iniciando configuração automática..."

# 1️⃣ Tornar a porta 8080 pública (para o site AlwaysData conseguir acessar)
if [ ! -z "$CODESPACE_NAME" ]; then
  echo "🌍 Tornando a porta 8080 pública..."
  gh codespace ports visibility 8080:public -c $CODESPACE_NAME
else
  echo "⚠️ Variável CODESPACE_NAME não encontrada — talvez não esteja no Codespaces."
fi

# 2️⃣ Iniciar o Crafty Controller
echo "🔧 Iniciando Crafty Controller..."
bash /workspaces/servidor/minecraft/run_crafty.sh > /tmp/run_crafty.log 2>&1 &

# 3️⃣ Iniciar o Playit (para o túnel externo)
echo "🌐 Iniciando Playit..."
playit > /tmp/playit.log 2>&1 &

# 4️⃣ Iniciar a API Flask (para o painel HTML)
echo "🧩 Iniciando NLS API do painel..."
python3 /workspaces/servidor/minecraft/api.py > /tmp/api.log 2>&1 &

echo "✅ Tudo foi iniciado! Acesse seu painel para verificar o status."
echo "📜 Logs disponíveis em:"
echo " - /tmp/run_crafty.log"
echo " - /tmp/playit.log"
echo " - /tmp/api.log"
# ====== Fim do Script ======
