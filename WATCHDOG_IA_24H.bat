@echo off
REM Watchdog: Reinicia IA automaticamente se cair
:loop
REM Testa se a porta 8002 está ativa
netstat -an | findstr ":8002" | findstr "LISTENING" >nul
if %errorlevel%==0 (
    REM IA está rodando
    timeout /t 30 >nul
    goto loop
) else (
    echo [Watchdog] IA caiu! Reiniciando...
    call INICIAR_TUDO_24H_GLOBAL.bat
    timeout /t 10 >nul
    goto loop
)
