@echo off
title Monitor Mamute Global 24h
:loop
:: Verificar Mamute
netstat -an | findstr ":8001.*LISTENING" >nul
if %errorlevel% neq 0 (
    echo %time% - Mamute offline! Reiniciando...
    taskkill /f /im python.exe >nul 2>&1
    timeout 2 >nul
    start /b python mamute_definitivo_sempre_online.py
    timeout 5 >nul
)

:: Verificar ngrok
tasklist | findstr "ngrok.exe" >nul
if %errorlevel% neq 0 (
    echo %time% - ngrok offline! Reiniciando...
    start /b ngrok http 8001
    timeout 5 >nul
)

timeout 30 >nul
goto loop
