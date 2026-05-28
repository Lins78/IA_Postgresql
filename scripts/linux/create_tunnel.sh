#!/bin/bash
echo "🌍 CRIANDO TÚNEL NGROK PARA IA MAMUTE ULTRA-SEGURA"
echo "================================================="
echo ""

# Verificar se ngrok está instalado
if ! command -v ngrok &> /dev/null; then
    echo "⬇️ Baixando e instalando ngrok..."
    
    # Download para Windows
    curl -o ngrok.zip https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip
    
    # Extrair
    powershell -Command "Expand-Archive -Path ngrok.zip -DestinationPath . -Force"
    
    # Limpar
    rm ngrok.zip
    
    echo "✅ Ngrok instalado!"
else
    echo "✅ Ngrok já está disponível"
fi

echo ""
echo "🚀 Criando túnel público..."
echo "🔗 Conectando porta 8000 à internet..."
echo ""

# Criar túnel
ngrok http 8001