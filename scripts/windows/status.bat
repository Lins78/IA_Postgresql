@echo off
chcp 65001 >nul
title 📊 Status dos Servidores - IA Mamute

echo.
echo ████████████████████████████████████████████████████████████
echo ██                                                        ██
echo ██        📊 STATUS DOS SERVIDORES - IA MAMUTE           ██
echo ██        Verificação em Tempo Real                      ██
echo ██                                                        ██
echo ████████████████████████████████████████████████████████████
echo.

cd /d "%~dp0"

:: Verificar se Python está disponível
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python não encontrado! 
    echo 📋 Instale o Python primeiro
    pause
    exit /b 1
)

:: Executar verificador
python verificar_status_servidores.py

echo.
pause