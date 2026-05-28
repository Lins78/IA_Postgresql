@echo off
REM Diagnóstico rápido da IA Mamute

REM Testa se a porta 8002 está ativa
netstat -an | findstr ":8002" | findstr "LISTENING" >nul
if %errorlevel%==0 (
    echo [OK] IA Mamute está ONLINE na porta 8002.
) else (
    echo [ERRO] IA Mamute NAO está online na porta 8002.
)

REM Testa acesso local
curl http://localhost:8002/docs >nul 2>&1
if %errorlevel%==0 (
    echo [OK] Interface web acessível em /docs.
) else (
    echo [ERRO] Interface web NAO acessível em /docs.
)

REM Testa acesso global (se túnel ativo)
REM Exemplo: curl https://SEU_TUNEL.ngrok.io/docs
REM Adapte a linha abaixo com o endereço do seu túnel, se desejar
REM curl https://SEU_TUNEL.ngrok.io/docs >nul 2>&1
REM if %errorlevel%==0 (
REM     echo [OK] Interface global acessível.
REM ) else (
REM     echo [ERRO] Interface global NAO acessível.
REM )

echo Diagnóstico concluído.
pause
