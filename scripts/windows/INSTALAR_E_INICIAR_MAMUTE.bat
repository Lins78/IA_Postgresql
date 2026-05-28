@echo off
title MAMUTE - INSTALACAO E INICIO AUTOMATICO
color 0A
cls

echo.
echo ============================================================
echo   🐘 MAMUTE - INSTALACAO E INICIO AUTOMATICO
echo ============================================================
echo   🔧 Verificando sistema e dependencias...
echo   🚀 Iniciando automaticamente...
echo ============================================================
echo.

REM Navegar para o diretório do script
cd /d "%~dp0"
echo 📁 Pasta atual: %CD%

REM Verificar se Python está instalado
echo.
echo 🔍 Verificando Python...
python --version
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ ERRO: Python não encontrado!
    echo.
    echo 🔧 SOLUÇÃO:
    echo    1. Baixe Python de: https://python.org
    echo    2. Durante instalação, marque "Add Python to PATH"
    echo    3. Reinicie o computador após instalação
    echo    4. Execute este script novamente
    echo.
    pause
    exit /b 1
)

echo ✅ Python encontrado

REM Verificar se arquivos necessários existem
echo.
echo 📂 Verificando arquivos necessários...

set ARQUIVOS_OK=1

if not exist "mamute_definitivo_sempre_online.py" (
    echo ❌ ERRO: mamute_definitivo_sempre_online.py não encontrado!
    set ARQUIVOS_OK=0
)

if not exist "web_app.py" (
    echo ❌ ERRO: web_app.py não encontrado!
    set ARQUIVOS_OK=0
)

if %ARQUIVOS_OK% EQU 0 (
    echo.
    echo 🔧 SOLUÇÃO:
    echo    1. Certifique-se de estar na pasta correta do projeto Mamute
    echo    2. Verifique se todos os arquivos foram baixados/criados
    echo    3. Pasta atual: %CD%
    echo.
    echo 📋 Arquivos encontrados nesta pasta:
    dir /b *.py 2>nul
    echo.
    pause
    exit /b 1
)

echo ✅ Arquivos principais encontrados

REM Instalar dependências essenciais
echo.
echo 📦 Instalando dependências essenciais...
pip install psycopg2-binary fastapi uvicorn requests psutil python-dotenv --upgrade --quiet

REM Verificar se o arquivo de verificação existe, senão pular
if exist "verificar_dependencias.py" (
    echo.
    echo 🔍 Executando verificação completa de dependências...
    echo    (Isso pode demorar alguns minutos na primeira vez)
    echo.
    
    python verificar_dependencias.py
    set VERIFICACAO_RESULT=%ERRORLEVEL%
    
    if %VERIFICACAO_RESULT% NEQ 0 (
        echo.
        echo ⚠️ Verificação encontrou problemas, mas continuando...
    )
) else (
    echo ⚠️ Verificador de dependências não encontrado, continuando sem verificação completa...
)

echo.
echo ============================================================
echo   ✅ Sistema preparado!
echo   🚀 Iniciando Mamute Definitivo...
echo ============================================================
echo.

REM Configurar variáveis de ambiente
set POSTGRES_HOST=localhost
set POSTGRES_PORT=5432
set POSTGRES_DB=ia_database
set POSTGRES_USER=postgres
set POSTGRES_PASSWORD=postgres@
set DATABASE_URL=postgresql://postgres:postgres%%40@localhost:5432/ia_database
set AI_NAME=Mamute

REM Iniciar o sistema definitivo
python mamute_definitivo_sempre_online.py

echo.
echo ============================================================
echo   Sistema encerrado.
echo   📋 Logs salvos em: mamute_definitivo.log
echo   🔧 Para diagnóstico: Execute DIAGNOSTICO.bat
echo   Pressione qualquer tecla para sair...
echo ============================================================
pause >nul