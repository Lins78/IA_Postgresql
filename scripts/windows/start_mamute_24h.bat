@echo off
:: 🚀 QUICK START - MAMUTE 24H
:: Inicia o serviço Mamute de forma rápida

echo.
echo ==========================================
echo 🐘 QUICK START MAMUTE 24H
echo ==========================================
echo.

cd /d "%~dp0"

:: Verificar se arquivo existe
if not exist "mamute_service_manager.py" (
    echo ❌ Arquivo mamute_service_manager.py não encontrado!
    pause
    exit /b 1
)

:: Verificar se Python está instalado
if not exist "venv\Scripts\python.exe" (
    echo ❌ Ambiente virtual não encontrado!
    echo 📋 Execute primeiro: install_requirements.bat
    pause
    exit /b 1
)

echo 🔧 Iniciando Mamute em modo standalone...
echo.
echo ✅ Características:
echo    - Recuperação automática se crashar
echo    - Túnel automático (ngrok)
echo    - Acesso 24h local e global
echo    - Logs detalhados
echo.
echo 🛑 Para parar: Pressione Ctrl+C
echo.
echo ==========================================

venv\Scripts\python.exe mamute_service_manager.py start

pause