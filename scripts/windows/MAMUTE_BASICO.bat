@echo off
title MAMUTE - MODO BASICO
color 0A

echo 🐘 MAMUTE - INICIANDO...

REM Ir para pasta do projeto
cd /d "%~dp0"

REM Verificar Python
python --version
if %ERRORLEVEL% NEQ 0 (
    echo ERRO: Python nao encontrado!
    echo Instale Python de: https://python.org
    pause
    exit
)

REM Instalar dependencias basicas
echo Instalando dependencias...
pip install psycopg2-binary fastapi uvicorn requests psutil python-dotenv

REM Configurar ambiente
set POSTGRES_HOST=localhost
set POSTGRES_PORT=5432
set POSTGRES_DB=ia_database
set POSTGRES_USER=postgres
set POSTGRES_PASSWORD=postgres@

echo.
echo Iniciando Mamute...
echo.

REM Iniciar servidor basico se o arquivo principal nao existir
if exist "mamute_definitivo_sempre_online.py" (
    python mamute_definitivo_sempre_online.py
) else if exist "web_app.py" (
    python -m uvicorn web_app:app --host 0.0.0.0 --port 8001
) else if exist "main.py" (
    python main.py
) else (
    echo ERRO: Nenhum arquivo principal encontrado!
    echo Verifique se esta na pasta correta do projeto
)

pause