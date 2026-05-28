@echo off
:: 📊 MONITOR STATUS MAMUTE
:: Verifica status do serviço e exibe informações

echo.
echo ==========================================
echo 📊 MONITOR STATUS MAMUTE 24H
echo ==========================================
echo.

cd /d "%~dp0"

:: Verificar serviço do Windows
echo 🔍 VERIFICANDO SERVIÇO WINDOWS:
sc query "MamuteIA24h" 2>nul
if %errorlevel% equ 0 (
    echo ✅ Serviço Windows está registrado
    sc query "MamuteIA24h" | findstr "STATE"
) else (
    echo ⚠️ Serviço Windows não está instalado
)

echo.
echo 🔍 VERIFICANDO PROCESSO PYTHON:

:: Verificar se existe PID file
if exist "mamute.pid" (
    set /p PID=<mamute.pid
    echo 📋 PID encontrado: %PID%
    
    :: Verificar se processo ainda existe
    tasklist /FI "PID eq %PID%" 2>nul | findstr /R "\<%PID%\>" >nul
    if %errorlevel% equ 0 (
        echo ✅ Processo está rodando
    ) else (
        echo ❌ Processo não está mais rodando
    )
) else (
    echo ⚠️ Arquivo PID não encontrado
)

echo.
echo 🔍 VERIFICANDO PORTA 8000:
netstat -an | findstr ":8000" >nul
if %errorlevel% equ 0 (
    echo ✅ Porta 8000 está em uso
    netstat -ano | findstr ":8000"
) else (
    echo ❌ Porta 8000 não está em uso
)

echo.
echo 🔍 VERIFICANDO TÚNEL NGROK:
tasklist /FI "IMAGENAME eq ngrok.exe" 2>nul | findstr "ngrok.exe" >nul
if %errorlevel% equ 0 (
    echo ✅ Ngrok está rodando
    tasklist /FI "IMAGENAME eq ngrok.exe"
) else (
    echo ❌ Ngrok não está rodando
)

echo.
echo 📋 LOGS RECENTES:
if exist "logs\service.log" (
    echo ✅ Últimas 10 linhas do log:
    powershell "Get-Content 'logs\service.log' -Tail 10"
) else (
    echo ⚠️ Log não encontrado
)

echo.
echo ==========================================
echo 🛠️ COMANDOS ÚTEIS:
echo.
echo 🚀 Iniciar modo standalone:  start_mamute_24h.bat
echo 🔧 Instalar serviço Windows: install_mamute_service.bat
echo 📊 Status detalhado:         python mamute_service_manager.py status
echo 🛑 Parar serviço:           python mamute_service_manager.py stop
echo.
echo ==========================================

pause