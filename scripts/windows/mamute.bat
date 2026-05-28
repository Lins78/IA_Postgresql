@echo off
:: 🚀 INSTALLER DO SERVIÇO WINDOWS MAMUTE
:: Configura a IA para rodar automaticamente 24h
setlocal enabledelayedexpansion

echo.
echo ==========================================
echo 🐘 INSTALADOR SERVIÇO MAMUTE 24H
echo ==========================================
echo.
echo 🎯 Este script vai configurar sua IA para rodar automaticamente
echo    sempre que o Windows iniciar, funcionando 24h por dia!
echo.

:: Verificar se está rodando como administrador
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERRO: Execute como Administrador!
    echo.
    echo 👉 Clique com botão direito no arquivo e escolha "Executar como administrador"
    pause
    exit /b 1
)

echo ✅ Privilégios administrativos confirmados
echo.

:: Definir variáveis
set "PROJECT_DIR=%~dp0"
set "SERVICE_NAME=MamuteIA24h"
set "SERVICE_DISPLAY=IA Mamute 24h Service"
set "SERVICE_DESC=Serviço da IA Mamute rodando 24h com acesso remoto"
set "PYTHON_EXE=%PROJECT_DIR%venv\Scripts\python.exe"
set "SERVICE_SCRIPT=%PROJECT_DIR%mamute_service_manager.py"
set "BATCH_WRAPPER=%PROJECT_DIR%mamute_service_wrapper.bat"

echo 🔧 Preparando ambiente Python...

:: Criar venv automaticamente se não existir
if not exist "%PYTHON_EXE%" (
    echo ⏳ Criando ambiente virtual (venv)...
    python -m venv "%PROJECT_DIR%venv"
)

:: Revalidar após tentativa de criação
if not exist "%PYTHON_EXE%" (
    echo ❌ Não consegui criar o ambiente virtual.
    echo 📋 Instale o Python 3.10+ e rode novamente este instalador.
    pause
    exit /b 1
)

echo 📦 Instalando dependências...
"%PYTHON_EXE%" -m pip install --upgrade pip >nul
"%PYTHON_EXE%" -m pip install -r "%PROJECT_DIR%requirements.txt"

echo 🔧 Criando wrapper do serviço...

:: Criar wrapper batch para o serviço
echo @echo off > "%BATCH_WRAPPER%"
echo cd /d "%PROJECT_DIR%" >> "%BATCH_WRAPPER%"
echo "%PYTHON_EXE%" "%SERVICE_SCRIPT%" start >> "%BATCH_WRAPPER%"

echo ✅ Wrapper criado: %BATCH_WRAPPER%

:: Parar serviço existente se houver
echo 🛑 Removendo serviço anterior (se existir)...
sc stop "%SERVICE_NAME%" >nul 2>&1
sc delete "%SERVICE_NAME%" >nul 2>&1

:: Instalar dependência para serviços Windows
echo 📦 Instalando NSSM (Non-Sucking Service Manager)...

:: Baixar NSSM se não existir
if not exist "%PROJECT_DIR%nssm.exe" (
    echo 🌐 Baixando NSSM...
    powershell -Command "(New-Object System.Net.WebClient).DownloadFile('https://nssm.cc/ci/nssm-2.24-101-g897c7ad.zip', '%PROJECT_DIR%nssm.zip')"
    
    echo 📂 Extraindo NSSM...
    powershell -Command "Expand-Archive -Path '%PROJECT_DIR%nssm.zip' -DestinationPath '%PROJECT_DIR%temp' -Force"
    copy "%PROJECT_DIR%temp\nssm-2.24-101-g897c7ad\win64\nssm.exe" "%PROJECT_DIR%nssm.exe" >nul
    rmdir /s /q "%PROJECT_DIR%temp"
    del "%PROJECT_DIR%nssm.zip"
    echo ✅ NSSM instalado com sucesso!
)

:: Criar serviço
echo 🔧 Criando serviço Windows...
"%PROJECT_DIR%nssm.exe" install "%SERVICE_NAME%" "%BATCH_WRAPPER%"

:: Configurar serviço
echo ⚙️ Configurando serviço...
"%PROJECT_DIR%nssm.exe" set "%SERVICE_NAME%" DisplayName "%SERVICE_DISPLAY%"
"%PROJECT_DIR%nssm.exe" set "%SERVICE_NAME%" Description "%SERVICE_DESC%"
"%PROJECT_DIR%nssm.exe" set "%SERVICE_NAME%" Start SERVICE_AUTO_START
"%PROJECT_DIR%nssm.exe" set "%SERVICE_NAME%" AppStdout "%PROJECT_DIR%logs\service.log"
"%PROJECT_DIR%nssm.exe" set "%SERVICE_NAME%" AppStderr "%PROJECT_DIR%logs\service.log"
"%PROJECT_DIR%nssm.exe" set "%SERVICE_NAME%" AppDirectory "%PROJECT_DIR%"

:: Configurar recuperação automática
echo 🔄 Configurando recuperação automática...
sc failure "%SERVICE_NAME%" reset= 86400 actions= restart/5000/restart/10000/restart/20000

:: Criar diretório de logs
if not exist "%PROJECT_DIR%logs\" mkdir "%PROJECT_DIR%logs"

:: Iniciar serviço
echo 🚀 Iniciando serviço...
sc start "%SERVICE_NAME%"

if %errorlevel% equ 0 (
    echo.
    echo ==========================================
    echo ✅ INSTALAÇÃO CONCLUÍDA COM SUCESSO!
    echo ==========================================
    echo.
    echo 🎉 Sua IA Mamute agora roda automaticamente 24h!
    echo.
    echo 📋 INFORMAÇÕES DO SERVIÇO:
    echo    Nome: %SERVICE_NAME%
    echo    Status: RODANDO
    echo    Início: Automático (com Windows)
    echo    Logs: %PROJECT_DIR%logs\
    echo.
    echo 🌐 ACESSOS:
    echo    Local: http://localhost:8001
    echo    Rede: http://192.168.1.70:8001
    echo    Global: Verifique logs para URL do túnel
    echo.
    echo 📊 COMANDOS ÚTEIS:
    echo    Ver status: sc query %SERVICE_NAME%
    echo    Parar: sc stop %SERVICE_NAME%
    echo    Iniciar: sc start %SERVICE_NAME%
    echo    Logs: type "%PROJECT_DIR%logs\service.log"
    echo.
    echo 🔧 DESINSTALAR (se necessário):
    echo    Execute: uninstall_mamute_service.bat
    echo.
) else (
    echo ❌ Erro ao iniciar serviço!
    echo 📋 Verifique os logs em: %PROJECT_DIR%logs\
)

echo.
echo Pressione qualquer tecla para continuar...
pause >nul