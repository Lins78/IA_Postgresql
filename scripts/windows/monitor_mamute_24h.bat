@echo off
title Monitor Mamute 24h
:loop
echo %time% - Verificando Mamute...
netstat -an | findstr ":8001" >nul
if %errorlevel% neq 0 (
    echo %time% - Mamute offline! Reiniciando...
    cd /d "c:\Users\carlo\Desktop\Projetos\IA_Postgresql\"
    start /b python mamute_definitivo_sempre_online.py
    timeout 10 >nul
) else (
    echo %time% - Mamute online ✅
)
timeout 30 >nul
goto loop
