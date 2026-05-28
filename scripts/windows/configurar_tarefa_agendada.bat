@echo off
title Configurar Tarefa Agendada - Mamute 24h
echo.
echo ========================================
echo 🕐 CONFIGURANDO TAREFA AGENDADA 24H
echo ========================================
echo.

cd /d "%~dp0"

echo 🛠️ Criando tarefa agendada para iniciar com Windows...
echo.

:: Criar tarefa que roda mesmo quando usuário não está logado
schtasks /create /tn "MamuteIA24h" /tr "\"%~dp0mamute_definitivo_sempre_online.py\"" /sc onstart /ru System /f

if %errorlevel% equ 0 (
    echo ✅ Tarefa agendada criada com sucesso!
    echo 🔄 O Mamute agora iniciará automaticamente com o Windows
    echo 💻 Funcionará mesmo com o notebook fechado
    echo.
    echo 📋 Para remover:
    echo    schtasks /delete /tn "MamuteIA24h" /f
) else (
    echo ❌ Erro ao criar tarefa agendada
    echo 💡 Execute como administrador
)

echo.
echo 🚀 Iniciando Mamute agora para testar...
start /b python mamute_definitivo_sempre_online.py

echo.
pause