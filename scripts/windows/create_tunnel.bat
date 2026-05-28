@echo off
echo 🌍 CRIANDO TUNNEL NGROK PARA IA MAMUTE ULTRA-SEGURA
echo ==================================================
echo.

REM Verificar se ngrok existe
where ngrok >nul 2>nul
if %errorlevel% neq 0 (
    echo ⬇️ Baixando ngrok...
    
    REM Baixar ngrok para Windows
    curl -L -o ngrok.zip "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip"
    
    REM Extrair
    echo 📦 Extraindo...
    powershell -Command "Expand-Archive -Path ngrok.zip -DestinationPath . -Force"
    
    REM Limpar
    del ngrok.zip
    
    echo ✅ Ngrok instalado!
) else (
    echo ✅ Ngrok já disponível
)

echo.
echo 🚀 Criando túnel público para porta 8001...
echo 🔗 Sua IA ficará acessível globalmente!
echo.
echo ⚠️ IMPORTANTE:
echo • Mantenha esta janela aberta
echo • O túnel ficará ativo enquanto este comando rodar
echo • Para parar, pressione Ctrl+C
echo.

REM Criar túnel
ngrok http 8001