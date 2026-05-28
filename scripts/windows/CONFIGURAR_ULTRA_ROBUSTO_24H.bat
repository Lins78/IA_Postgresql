@echo off
title Mamute 24h Ultra Robusto - Configuração Definitiva
echo.
echo ████████████████████████████████████████████
echo ██  🚀 CONFIGURAÇÃO ULTRA ROBUSTA 24H     ██
echo ████████████████████████████████████████████
echo.

cd /d "%~dp0"

echo 🎯 MÉTODO 1: Configuração automática (SEM privilégios)
echo.
set /p method="🤔 Usar método automático? (s/n): "
if /i "%method%"=="n" goto manual_config

echo.
echo 🔧 CONFIGURANDO AUTOMATICAMENTE...

:: 1. Configurar energia para máxima performance
echo 📋 1. Configurando energia...
powercfg /change standby-timeout-ac 0
powercfg /change standby-timeout-dc 0
powercfg /change hibernate-timeout-ac 0
powercfg /change hibernate-timeout-dc 0
powercfg /change disk-timeout-ac 0
powercfg /change disk-timeout-dc 0

:: 2. Desabilitar suspensão USB
echo 📋 2. Desabilitando suspensão USB...
for /f "tokens=*" %%i in ('wmic path Win32_USBHub get DeviceID /value ^| find "="') do powercfg /devicedisablewake "%%i" >nul 2>&1

:: 3. Configurar network adapter para não desligar
echo 📋 3. Configurando adaptador de rede...
for /f "skip=1" %%i in ('wmic path Win32_NetworkAdapter where "NetEnabled=true" get PNPDeviceID /value ^| find "="') do powercfg /devicedisablewake "%%i" >nul 2>&1

:: 4. Desativar fast startup
echo 📋 4. Desativando fast startup...
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Power" /v HiberbootEnabled /t REG_DWORD /d 0 /f >nul 2>&1

:: 5. Configurar para sempre ativo
echo 📋 5. Configurando para sempre ativo...
reg add "HKCU\Control Panel\Desktop" /v ScreenSaveActive /t REG_SZ /d 0 /f >nul 2>&1

echo.
echo ✅ Configurações básicas aplicadas!
echo.

echo 🚀 6. Criando sistema de monitoramento...

:: Criar script de monitoramento
(
echo @echo off
echo title Monitor Mamute 24h
echo :loop
echo echo %%time%% - Verificando Mamute...
echo netstat -an ^| findstr ":8001" ^>nul
echo if %%errorlevel%% neq 0 ^(
echo     echo %%time%% - Mamute offline! Reiniciando...
echo     cd /d "%~dp0"
echo     start /b python mamute_definitivo_sempre_online.py
echo     timeout 10 ^>nul
echo ^) else ^(
echo     echo %%time%% - Mamute online ✅
echo ^)
echo timeout 30 ^>nul
echo goto loop
) > monitor_mamute_24h.bat

echo ✅ Monitor criado: monitor_mamute_24h.bat

:: 6. Reiniciar Mamute com configurações otimizadas
echo.
echo 🔄 7. Reiniciando Mamute com configurações otimizadas...

:: Parar processo existente
taskkill /f /im python.exe >nul 2>&1
timeout 2 >nul

:: Iniciar Mamute
start /b python mamute_definitivo_sempre_online.py

:: Iniciar monitor
start /min monitor_mamute_24h.bat

timeout 5 >nul

echo.
echo ✅ MAMUTE CONFIGURADO PARA 24H REAL!
echo.
echo 🌐 TESTE AGORA:
echo   Local: http://localhost:8001
echo   Rede:  http://192.168.1.70:8001
echo.
echo 📊 Status:
netstat -an | findstr ":8001"
echo.

echo 🎯 PARA ACESSO EXTERNO REAL (Manual):
echo   1. Abra Windows Defender Firewall
echo   2. Clique "Permitir aplicativo"  
echo   3. Adicione Python.exe
echo   4. Marque "Público" e "Privado"
echo   5. OK
echo.

goto end

:manual_config
echo.
echo 📋 CONFIGURAÇÃO MANUAL:
echo.
echo 1. 🔥 Firewall:
echo    - Windows Security ^> Firewall ^> Allow app
echo    - Add Python.exe  
echo    - Check Public ^& Private
echo.
echo 2. 💻 Energia:
echo    - Control Panel ^> Power Options
echo    - High Performance
echo    - Advanced: Never sleep
echo.
echo 3. 🌐 Router:
echo    - Port forwarding 8001 -^> 192.168.1.70
echo    - Para acesso externo real
echo.
echo 4. 🚀 Iniciar:
echo    - Execute: python mamute_definitivo_sempre_online.py
echo.

:end
echo.
echo 💡 DICA EXTRA - Acesso global real:
echo   Use ngrok: ngrok http 8001
echo   Ou CloudFlare Tunnel (gratuito)
echo.
echo 📋 Logs: mamute_definitivo.log
echo 🔍 Monitor: monitor_mamute_24h.bat
echo.
pause