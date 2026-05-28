@echo off
title MAMUTE - Sistema Inteligente Sempre Online

echo 🐘 MAMUTE - SISTEMA INTELIGENTE SEMPRE ONLINE
echo =============================================
echo.
echo 🚀 Iniciando sistema definitivo...
echo ✅ Configuração automática
echo ✅ Conexão local robusta  
echo ✅ Túneis globais múltiplos
echo ✅ Recovery automático
echo ✅ Monitor 24/7
echo.

REM Ir para o diretório do projeto
cd /d "%~dp0"

REM Executar script Python principal
python iniciar_mamute.py

REM Se o Python falhou, tentar com py
if errorlevel 1 (
    echo.
    echo ⚠️ Tentando com 'py' em vez de 'python'...
    py iniciar_mamute.py
)

REM Se ainda falhou, mostrar ajuda
if errorlevel 1 (
    echo.
    echo ❌ ERRO: Python não encontrado
    echo.
    echo 💡 SOLUÇÕES:
    echo   1. Instalar Python: https://python.org/downloads
    echo   2. Adicionar Python ao PATH
    echo   3. Executar manualmente: python iniciar_mamute.py
    echo.
    pause
)