@echo off
:: 🗑️ DESINSTALADOR DO SERVIÇO WINDOWS MAMUTE

echo.
echo ==========================================
echo 🗑️ DESINSTALADOR SERVIÇO MAMUTE 24H
echo ==========================================
echo.

:: Verificar se está rodando como administrador
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERRO: Execute como Administrador!
    pause
    exit /b 1
)

set "SERVICE_NAME=MamuteIA24h"
set "PROJECT_DIR=%~dp0"

echo 🛑 Parando serviço...
sc stop "%SERVICE_NAME%"

echo 🗑️ Removendo serviço...
sc delete "%SERVICE_NAME%"

echo 📂 Limpando arquivos temporários...
if exist "%PROJECT_DIR%mamute_service_wrapper.bat" del "%PROJECT_DIR%mamute_service_wrapper.bat"
if exist "%PROJECT_DIR%mamute.pid" del "%PROJECT_DIR%mamute.pid"
if exist "%PROJECT_DIR%nssm.exe" del "%PROJECT_DIR%nssm.exe"

echo.
echo ✅ Serviço Mamute removido com sucesso!
echo.
echo 📋 Para usar novamente:
echo    Execute: install_mamute_service.bat
echo.
pause