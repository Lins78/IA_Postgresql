@echo off
chcp 65001 >nul
title 🚀 IA MAMUTE - SERVIDORES AUTOMÁTICOS

echo.
echo ██████████████████████████████████████████████████████████████████
echo ██                                                              ██
echo ██        🚀 IA MAMUTE - SERVIDORES AUTOMÁTICOS                ██
echo ██        Acesso Local + Global Sempre Ativo                   ██
echo ██                                                              ██
echo ██████████████████████████████████████████████████████████████████
echo.

cd /d "%~dp0"

:: Verificar se Python está disponível
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python não encontrado! 
    echo 📋 Instale o Python primeiro: https://python.org
    echo.
    pause
    exit /b 1
)

:: Verificar arquivo principal
if not exist "iniciar_servidores_automatico.py" (
    echo ❌ Arquivo iniciar_servidores_automatico.py não encontrado!
    echo 📋 Execute este script na pasta do projeto
    echo.
    pause
    exit /b 1
)

:: Instalar dependências automaticamente
echo 📦 Verificando dependências...
pip install -q fastapi uvicorn requests pyngrok psutil >nul 2>&1

echo.
echo 🔧 CONFIGURAÇÕES AUTOMÁTICAS:
echo ┌─────────────────────────────────────────────────────────────────┐
echo │ ✅ Servidor Local:  http://localhost:8000                      │
echo │ ✅ Servidor Global: Via túnel automático                       │
echo │ 🔄 Recuperação:     Automática se parar                        │
echo │ 📊 Monitoramento:   A cada 30 segundos                         │
echo │ 🛑 Para parar:      Pressione Ctrl+C                          │
echo └─────────────────────────────────────────────────────────────────┘
echo.

echo 🚀 Iniciando servidores automáticos...
echo.

:: Executar script Python
python iniciar_servidores_automatico.py

echo.
echo ✅ Servidores finalizados
pause