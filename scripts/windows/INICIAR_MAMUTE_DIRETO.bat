@echo off
title MAMUTE - INICIO DIRETO
color 0A
cls

echo.
echo ============================================================
echo   🐘 MAMUTE - INICIO DIRETO (MODO SIMPLES)
echo ============================================================
echo   🚀 Iniciando sistema diretamente...
echo ============================================================
echo.

REM Navegar para o diretório do script
cd /d "%~dp0"

REM Verificar se Python está instalado
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ ERRO: Python não encontrado!
    echo    Baixe e instale Python de: https://python.org
    echo    IMPORTANTE: Marque "Add to PATH" durante a instalação
    echo.
    pause
    exit /b 1
)

echo ✅ Python OK

REM Verificar se arquivo principal existe
if not exist "mamute_definitivo_sempre_online.py" (
    echo ❌ ERRO: Arquivo principal não encontrado!
    echo    Certifique-se de estar no diretório correto do projeto
    echo.
    pause
    exit /b 1
)

echo ✅ Arquivo principal encontrado

REM Instalar dependências rapidamente se necessário
echo.
echo 📦 Verificando dependências essenciais...
python -c "import psycopg2" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo 🔧 Instalando psycopg2-binary...
    pip install psycopg2-binary
)

python -c "import fastapi" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo 🔧 Instalando fastapi...
    pip install fastapi
)

python -c "import uvicorn" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo 🔧 Instalando uvicorn...
    pip install uvicorn[standard]
)

python -c "import requests" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo 🔧 Instalando requests...
    pip install requests
)

python -c "import psutil" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo 🔧 Instalando psutil...
    pip install psutil
)

echo ✅ Dependências OK

echo.
echo ============================================================
echo   🚀 INICIANDO MAMUTE DEFINITIVO...
echo ============================================================
echo.

REM Definir variáveis de ambiente
set POSTGRES_HOST=localhost
set POSTGRES_PORT=5432
set POSTGRES_DB=ia_database
set POSTGRES_USER=postgres
set POSTGRES_PASSWORD=postgres@
set DATABASE_URL=postgresql://postgres:postgres%%40@localhost:5432/ia_database
set AI_NAME=Mamute

REM Iniciar sistema
python mamute_definitivo_sempre_online.py

echo.
echo ============================================================
echo   Sistema finalizado.
echo   Pressione qualquer tecla para fechar...
echo ============================================================
pause >nul