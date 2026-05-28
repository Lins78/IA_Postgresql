@echo off
chcp 65001 >nul
setlocal enableextensions enabledelayedexpansion

rem Inicia a API FastAPI (uvicorn) e mantém rodando 24h
rem Opcional: abre túnel serveo para acesso externo (porta 8002 -> porta local)

cd /d "%~dp0"

if not exist .venv\Scripts\python.exe (
  echo [ERRO] Ambiente .venv nao encontrado. Crie com: python -m venv .venv && .venv\Scripts\activate && pip install -r requirements.txt
  pause
  exit /b 1
)

rem Porta fixa (local) com override por variavel MAMUTE_PORT
set PORTA=%MAMUTE_PORT%
if "%PORTA%"=="" set PORTA=8002

rem Verifica se a porta local já está ocupada (evita erro de parsing no FOR em algumas shells)
netstat -ano | findstr /R /C=":%PORTA% .*LISTENING" >nul 2>nul
if %errorlevel%==0 (
  echo ATENCAO: Porta %PORTA% pode estar em uso.
  choice /t 5 /d N /m "Continuar mesmo assim?"
  if errorlevel 2 exit /b 1
)

set "UVICORN_OPTS=--timeout-keep-alive 120 --limit-concurrency 200 --proxy-headers --forwarded-allow-ips *"
set "UVICORN_CMD=.venv\Scripts\python.exe -m uvicorn web_app:app --host 0.0.0.0 --port %PORTA% --log-level info %UVICORN_OPTS%"
set "SERVICES_CMD=.venv\Scripts\python.exe start_mamute_services.py"

echo Iniciando servidor local em http://localhost:%PORTA% (PORTA=%PORTA%)
start "MAMUTE_LOCAL" cmd /c "%UVICORN_CMD%"

if exist "start_mamute_services.py" (
  echo Iniciando servicos de monitoramento, backup e relatorios...
  start "MAMUTE_SERVICOS" cmd /c "%SERVICES_CMD%"
) else (
  echo [AVISO] start_mamute_services.py nao encontrado; pulando servicos adicionais.
)

rem Default agora é SIM para subir servidor global via ngrok
choice /t 3 /d S /m "Abrir acesso externo via ngrok (http %PORTA%)?"
if errorlevel 2 goto fim

rem Verifica ngrok
where ngrok >nul 2>nul
if errorlevel 1 (
  echo [ERRO] ngrok nao encontrado. Instale em https://ngrok.com/download e garanta que esteja no PATH.
  goto fim
)

rem Usa token do .env se existir e captura API_KEY para aviso
if exist ".env" (
  for /f "usebackq tokens=1,* delims==" %%A in (".env") do (
    if /I "%%A"=="NGROK_AUTH_TOKEN" set NGROK_TOKEN=%%B
    if /I "%%A"=="API_KEY" set MAMUTE_API_KEY=%%B
  )
) else (
  echo [INFO] Arquivo .env nao encontrado; usara variaveis de ambiente NGROK_AUTH_TOKEN e API_KEY se ja estiverem definidas.
)

rem Usa API_KEY do ambiente se nao veio do .env
if not defined MAMUTE_API_KEY if defined API_KEY set MAMUTE_API_KEY=%API_KEY%

if not defined NGROK_TOKEN (
  echo [ERRO] NGROK_AUTH_TOKEN nao definido no .env. Edite .env e preencha seu token.
  goto fim
)

if not defined MAMUTE_API_KEY (
  echo [AVISO] API_KEY nao definida; endpoints protegidos podem recusar requisicoes.
)

echo Abrindo tunel ngrok na porta %PORTA% (forçando loopback IPv4)...
start "MAMUTE_TUNEL" cmd /c "ngrok config add-authtoken %NGROK_TOKEN% && ngrok http 127.0.0.1:%PORTA%"

rem Testa rapidamente o túnel pelo API local do ngrok (porta 4040)
ping -n 3 127.0.0.1 >nul
for /f "usebackq tokens=*" %%U in (`powershell -NoProfile -Command "Start-Sleep 1; try { $t=(Invoke-WebRequest 'http://127.0.0.1:4040/api/tunnels' -UseBasicParsing | ConvertFrom-Json).tunnels; if($t -and $t.Count -gt 0) { $t[0].public_url } } catch { '' }"`) do (
  set URL_TUNEL=%%U
)
if defined URL_TUNEL (
  echo TUNEL NGROK ATIVO: !URL_TUNEL!
) else (
  echo [AVISO] Nao foi possivel ler a URL do ngrok. Verifique a janela MAMUTE_TUNEL.
)

:fim
echo Processos iniciados. Para parar, feche as janelas "MAMUTE_LOCAL", "MAMUTE_SERVICOS" e "MAMUTE_TUNEL".
endlocal
