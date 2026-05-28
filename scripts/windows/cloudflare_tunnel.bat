@echo off
echo 🌐 CLOUDFLARE TUNNEL - ACESSO GLOBAL SEM CONTA
echo ============================================
echo.
echo ⬇️ Baixando Cloudflare Tunnel...

REM Baixar cloudflared
curl -L -o cloudflared.exe "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"

echo ✅ Cloudflare Tunnel baixado!
echo.
echo 🚀 Criando túnel público...
echo 🔗 Sua IA ficará acessível globalmente!
echo.

REM Criar túnel
cloudflared.exe tunnel --url http://localhost:8000