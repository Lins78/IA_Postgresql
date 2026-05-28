@echo off
chcp 65001 >nul
title 🔧 Configurar Inicialização Automática - IA Mamute

echo.
echo ██████████████████████████████████████████████████████████████████
echo ██                                                              ██
echo ██        🔧 CONFIGURAR INICIALIZAÇÃO AUTOMÁTICA               ██
echo ██        IA Mamute - Servidores sempre ativos                 ██
echo ██                                                              ██
echo ██████████████████████████████████████████████████████████████████
echo.

cd /d "%~dp0"

echo 🎯 OPÇÕES DE INICIALIZAÇÃO AUTOMÁTICA:
echo.
echo 1. ⚡ Inicializar agora (teste único)
echo 2. 🏠 Configurar para iniciar com o Windows
echo 3. 🌍 Apenas túnel global automático
echo 4. 📋 Mostrar status atual
echo 5. 🛑 Parar serviços ativos
echo.

set /p choice="💡 Digite sua escolha (1-5): "

if "%choice%"=="1" goto iniciar_agora
if "%choice%"=="2" goto configurar_boot
if "%choice%"=="3" goto tunnel_automatico
if "%choice%"=="4" goto mostrar_status
if "%choice%"=="5" goto parar_servicos
echo ❌ Opção inválida!
goto end

:iniciar_agora
echo.
echo ⚡ Iniciando servidores automaticamente...
start /b python iniciar_servidores_automatico.py
echo ✅ Servidores iniciados!
echo 📊 Para verificar status: execute status.bat
goto end

:configurar_boot
echo.
echo 🏠 Configurando inicialização automática com Windows...

:: Criar script para o registro
set STARTUP_SCRIPT=%cd%\start_automatico.bat
set STARTUP_REG_KEY="HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run"
set STARTUP_REG_NAME="MamuteIA_AutoStart"

:: Adicionar ao registro do Windows
reg add %STARTUP_REG_KEY% /v %STARTUP_REG_NAME% /t REG_SZ /d "%STARTUP_SCRIPT%" /f >nul 2>&1

if %errorlevel% equ 0 (
    echo ✅ Inicialização automática configurada!
    echo 🔧 A IA Mamute será iniciada automaticamente quando o Windows iniciar
    echo.
    echo 📋 Para remover:
    echo    reg delete %STARTUP_REG_KEY% /v %STARTUP_REG_NAME% /f
) else (
    echo ❌ Erro ao configurar inicialização automática
    echo 💡 Execute como administrador ou configure manualmente
)
goto end

:tunnel_automatico
echo.
echo 🌍 Configurando apenas túnel global automático...
echo 📝 Criando arquivo de configuração personalizada...

:: Criar configuração só para túnel
(
echo {
echo   "servidor_local": {
echo     "ativo": false
echo   },
echo   "servidor_global": {
echo     "ativo": true,
echo     "tunnel_type": "ngrok",
echo     "auto_restart": true
echo   }
echo }
) > config_tunnel_only.json

echo ✅ Configuração criada: config_tunnel_only.json
echo 🚀 Iniciando apenas túnel global...
start /b python iniciar_servidores_automatico.py --config config_tunnel_only.json
goto end

:mostrar_status
echo.
echo 📊 Verificando status atual...
python verificar_status_servidores.py
goto end

:parar_servicos
echo.
echo 🛑 Parando todos os serviços...

:: Matar processos Python relacionados
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im uvicorn.exe >nul 2>&1
taskkill /f /im ngrok.exe >nul 2>&1
taskkill /f /im cloudflared.exe >nul 2>&1

echo ✅ Serviços parados
echo 📊 Para confirmar: execute status.bat
goto end

:end
echo.
echo ──────────────────────────────────────────────────────────────────
echo 💡 COMANDOS ÚTEIS:
echo   start_automatico.bat  - Iniciar servidores automáticos
echo   status.bat            - Verificar status dos servidores  
echo   configurar_boot.bat   - Este menu de configurações
echo ──────────────────────────────────────────────────────────────────
echo.
pause