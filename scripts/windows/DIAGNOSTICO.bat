@echo off
title MAMUTE - DIAGNOSTICO DO SISTEMA
color 0E

echo.
echo ============================================================
echo   🔍 MAMUTE - DIAGNOSTICO COMPLETO DO SISTEMA
echo ============================================================
echo.

cd /d "%~dp0"

echo 1. VERIFICANDO PYTHON...
echo ----------------------------------------
python --version
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Python NAO encontrado!
    echo    Baixe de: https://python.org
    echo    Marque "Add to PATH" na instalacao
    goto :final_diagnostico
) else (
    echo ✅ Python OK
)

echo.
echo 2. VERIFICANDO ARQUIVOS PRINCIPAIS...
echo ----------------------------------------
if exist "mamute_definitivo_sempre_online.py" (
    echo ✅ mamute_definitivo_sempre_online.py
) else (
    echo ❌ mamute_definitivo_sempre_online.py NAO ENCONTRADO
)

if exist "web_app.py" (
    echo ✅ web_app.py
) else (
    echo ❌ web_app.py NAO ENCONTRADO
)

if exist "main.py" (
    echo ✅ main.py
) else (
    echo ❌ main.py NAO ENCONTRADO
)

if exist "requirements.txt" (
    echo ✅ requirements.txt
) else (
    echo ❌ requirements.txt NAO ENCONTRADO
)

echo.
echo 3. VERIFICANDO DEPENDENCIAS PYTHON...
echo ----------------------------------------

python -c "import psycopg2; print('✅ psycopg2 OK')" 2>nul || echo ❌ psycopg2 FALTANDO
python -c "import fastapi; print('✅ fastapi OK')" 2>nul || echo ❌ fastapi FALTANDO  
python -c "import uvicorn; print('✅ uvicorn OK')" 2>nul || echo ❌ uvicorn FALTANDO
python -c "import requests; print('✅ requests OK')" 2>nul || echo ❌ requests FALTANDO
python -c "import psutil; print('✅ psutil OK')" 2>nul || echo ❌ psutil FALTANDO

echo.
echo 4. TESTANDO CONEXAO POSTGRESQL...
echo ----------------------------------------
python -c "import psycopg2; conn = psycopg2.connect(host='localhost', port='5432', database='ia_database', user='postgres', password='postgres@'); print('✅ PostgreSQL OK'); conn.close()" 2>nul || echo ❌ PostgreSQL NAO ACESSIVEL

echo.
echo 5. VERIFICANDO PORTAS...
echo ----------------------------------------
netstat -an | findstr ":8000" >nul
if %ERRORLEVEL% EQU 0 (
    echo ⚠️ Porta 8000 JA EM USO
) else (
    echo ✅ Porta 8000 LIVRE
)

echo.
echo 6. ESTRUTURA DE PASTAS...
echo ----------------------------------------
echo Pasta atual: %CD%
echo Arquivos encontrados:
dir /b *.py 2>nul || echo Nenhum arquivo Python encontrado
dir /b *.bat 2>nul || echo Nenhum arquivo batch encontrado

:final_diagnostico
echo.
echo ============================================================
echo   DIAGNOSTICO CONCLUIDO
echo ============================================================
echo.
echo PROXIMOS PASSOS:
echo 1. Se Python nao foi encontrado: Instale Python
echo 2. Se arquivos estao faltando: Verifique a pasta
echo 3. Se dependencias faltam: Execute pip install -r requirements.txt
echo 4. Se PostgreSQL nao conecta: Configure banco de dados
echo.
pause