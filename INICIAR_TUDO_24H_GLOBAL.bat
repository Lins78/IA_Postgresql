@echo off
REM Script mestre: Inicia IA local, túnel global e watchdog 24/7

REM Ativar ambiente virtual
call .venv\Scripts\activate

REM Iniciar servidor IA (em background)
start "IA Mamute" cmd /k "python -m uvicorn web_app:app --host 0.0.0.0 --port 8002 --reload"

REM Aguardar alguns segundos para garantir que o servidor subiu
ping 127.0.0.1 -n 6 > nul

REM Iniciar túnel global (Cloudflare Tunnel ou ngrok)
REM Descomente a linha do serviço que preferir:
REM start "ngrok" cmd /k "ngrok http 8002"
REM start "Cloudflare Tunnel" cmd /k "cloudflared tunnel run <NOME_DO_TUNEL>"

REM Iniciar watchdog/monitoramento (reinício automático)
start "Watchdog" cmd /k "call monitor_global_24h.bat"

REM Diagnóstico automático
start "Diagnóstico" cmd /k "python diagnostico_ia.py"

echo Tudo iniciado! IA disponível local e global 24/7.
pause
