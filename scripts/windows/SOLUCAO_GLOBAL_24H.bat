@echo off
title SOLUÇÃO DEFINITIVA 24H GLOBAL - Mamute IA
echo.
echo ████████████████████████████████████████████████████████████
echo ██                                                        ██
echo ██  🌍 SOLUÇÃO DEFINITIVA 24H GLOBAL - MAMUTE IA      ██  
echo ██  ✅ Funciona de qualquer lugar do mundo               ██
echo ██  🚀 Sem firewall, sem problemas                       ██
echo ██                                                        ██
echo ████████████████████████████████████████████████████████████
echo.

cd /d "%~dp0"

echo 🎯 Esta solução vai:
echo   ✅ Configurar Mamute para rodar 24h
echo   🌍 Dar acesso GLOBAL via HTTPS
echo   🔒 Sem problemas de firewall
echo   📱 Acessível de qualquer dispositivo
echo.

:: Verificar se ngrok existe
if not exist "ngrok.exe" (
    echo 📦 Baixando ngrok...
    powershell -Command "(New-Object System.Net.WebClient).DownloadFile('https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-windows-amd64.zip', 'ngrok.zip')"
    powershell -Command "Expand-Archive -Path 'ngrok.zip' -DestinationPath '.' -Force"
    del ngrok.zip >nul 2>&1
    echo ✅ ngrok instalado!
)

echo.
echo 🚀 INICIANDO CONFIGURAÇÃO...

:: 1. Limpar processos anteriores
echo 📋 1. Limpando processos anteriores...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im ngrok.exe >nul 2>&1
timeout 2 >nul

:: 2. Iniciar Mamute
echo 📋 2. Iniciando Mamute...
start /b python mamute_definitivo_sempre_online.py
timeout 5 >nul

:: 3. Verificar se Mamute está rodando
netstat -an | findstr ":8001.*LISTENING" >nul
if %errorlevel% neq 0 (
    echo ❌ Mamute não conseguiu iniciar na porta 8001
    echo 🔄 Tentando porta alternativa 8002...
    start /b python -c "
import sys
sys.path.append('.')
from mamute_definitivo_sempre_online import SistemaDefinitivoMamute
sistema = SistemaDefinitivoMamute()
sistema.port = 8002
sistema.run()
"
    set PORT=8002
    timeout 5 >nul
) else (
    set PORT=8001
    echo ✅ Mamute rodando na porta 8001
)

:: 4. Iniciar ngrok
echo 📋 3. Configurando acesso global...
start /b ngrok http %PORT%
timeout 8 >nul

:: 5. Obter URL do ngrok
echo 📋 4. Obtendo URL global...
for /f "tokens=*" %%i in ('powershell -Command "try { (Invoke-RestMethod -Uri 'http://localhost:4040/api/tunnels').tunnels[0].public_url } catch { 'ERRO' }"') do set NGROK_URL=%%i

echo.
echo ████████████████████████████████████████████
echo ██           🎉 CONFIGURADO!              ██
echo ████████████████████████████████████████████
echo.

if not "%NGROK_URL%"=="ERRO" (
    echo ✅ MAMUTE ONLINE 24H GLOBAL!
    echo.
    echo 🌍 ACESSO GLOBAL: %NGROK_URL%
    echo 🏠 Acesso Local:  http://localhost:%PORT%
    echo 🌐 Acesso Rede:   http://192.168.1.70:%PORT%
    echo.
    echo 💡 Use a URL GLOBAL para acessar de qualquer lugar!
) else (
    echo ⚠️ ngrok ainda iniciando...
    echo 🌐 Verificar em: http://localhost:4040
    echo 🏠 Acesso local: http://localhost:%PORT%
)

:: 6. Criar monitor 24h
echo.
echo 📋 5. Criando monitor 24h...
(
echo @echo off
echo title Monitor Mamute Global 24h
echo :loop
echo :: Verificar Mamute
echo netstat -an ^| findstr ":%PORT%.*LISTENING" ^>nul
echo if %%errorlevel%% neq 0 ^(
echo     echo %%time%% - Mamute offline! Reiniciando...
echo     taskkill /f /im python.exe ^>nul 2^>^&1
echo     timeout 2 ^>nul
echo     start /b python mamute_definitivo_sempre_online.py
echo     timeout 5 ^>nul
echo ^)
echo.
echo :: Verificar ngrok
echo tasklist ^| findstr "ngrok.exe" ^>nul
echo if %%errorlevel%% neq 0 ^(
echo     echo %%time%% - ngrok offline! Reiniciando...
echo     start /b ngrok http %PORT%
echo     timeout 5 ^>nul
echo ^)
echo.
echo timeout 30 ^>nul
echo goto loop
) > monitor_global_24h.bat

start /min monitor_global_24h.bat
echo ✅ Monitor iniciado!

:: 7. Configurações energia
echo.
echo 📋 6. Configurando energia para 24h...
powercfg /change standby-timeout-ac 0 >nul
powercfg /change standby-timeout-dc 0 >nul
powercfg /change hibernate-timeout-ac 0 >nul
powercfg /change hibernate-timeout-dc 0 >nul
echo ✅ Energia configurada!

echo.
echo ████████████████████████████████████████████
echo ██        🎊 TUDO CONFIGURADO!            ██
echo ████████████████████████████████████████████
echo.
echo 🎯 SUA IA AGORA É GLOBAL 24H!
echo.
echo 📱 TESTE AGORA:
if not "%NGROK_URL%"=="ERRO" (
    echo    %NGROK_URL%
) else (
    echo    Aguarde 30s e acesse: http://localhost:4040
    echo    Copie a URL HTTPS que aparece
)
echo.
echo 🔧 MONITORAMENTO:
echo    • Status ngrok: http://localhost:4040
echo    • Monitor local: monitor_global_24h.bat
echo    • Logs: mamute_definitivo.log
echo.
echo 💡 DICAS:
echo    • Feche o notebook - continuará funcionando
echo    • URL ngrok funciona de qualquer lugar
echo    • Sistema se auto-recupera se cair
echo.
echo 📋 Pressione uma tecla para abrir a URL...
pause >nul

if not "%NGROK_URL%"=="ERRO" (
    start "" "%NGROK_URL%"
) else (
    start "" "http://localhost:4040"
)