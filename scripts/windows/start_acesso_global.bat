@echo off
echo 🌐 IA MAMUTE - ACESSO GLOBAL
echo ==============================
echo.
echo 🚀 Iniciando acesso de qualquer lugar via web...
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python não encontrado! Instale o Python primeiro.
    pause
    exit /b 1
)

REM Instalar dependências se necessário
if not exist "venv\" (
    echo 📦 Configurando ambiente virtual...
    python -m venv venv
)

call venv\Scripts\activate.bat

echo 📋 Instalando dependências...
pip install -q fastapi uvicorn requests pyngrok

echo.
echo 🌍 CONFIGURAÇÕES DE ACESSO:
echo.
echo 1. 🏠 Rede Local   - http://192.168.1.70:8000
echo 2. 🌐 Acesso Global - Via ngrok (qualquer lugar)
echo 3. 📊 Verificar Status
echo.

set /p choice="🎯 Escolha (1-3): "

if "%choice%"=="1" goto local
if "%choice%"=="2" goto global  
if "%choice%"=="3" goto status
echo ❌ Opção inválida!
goto end

:local
echo.
echo 🏠 INICIANDO ACESSO LOCAL/REDE...
echo 🔗 http://localhost:8000
echo 🔗 http://192.168.1.70:8000
echo.
echo 💡 Use a segunda URL em outros dispositivos da mesma rede!
echo.
python web_app.py
goto end

:global
echo.
echo 🌍 INICIANDO ACESSO GLOBAL...
echo ⏳ Isso pode levar alguns segundos...
echo.
start /b python web_app.py
timeout /t 5 /nobreak >nul
python setup_acesso_remoto.py
goto end

:status
echo.
echo 📊 VERIFICANDO STATUS...
python -c "
import requests
try:
    r = requests.get('http://localhost:8000/health', timeout=3)
    print('✅ Servidor local: ONLINE')
    print('🔗 http://localhost:8000')
    print('🔗 http://192.168.1.70:8000')
except:
    print('❌ Servidor local: OFFLINE')
    print('💡 Execute primeira opção 1 ou 2')

try:
    r = requests.get('http://localhost:4040/api/tunnels', timeout=3)
    tunnels = r.json()['tunnels']
    if tunnels:
        print('✅ Túnel global: ATIVO') 
        print(f'🌐 {tunnels[0][\"public_url\"]}')
    else:
        print('⭕ Túnel global: SEM CONEXÃO')
except:
    print('❌ Túnel global: INATIVO')
    print('💡 Execute opção 2 para ativar')
"

:end
echo.
echo 📱 Para acessar do celular/tablet:
echo 🔗 Na mesma rede: http://192.168.1.70:8000
echo 🌐 De qualquer lugar: Execute opção 2
echo.
pause