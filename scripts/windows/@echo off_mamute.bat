@echo off
title Mamute 24h - Script Unificado
chcp 65001 >nul

echo 🚀 Mamute 24h - Script Unificado
echo ---------------------------------
echo 1. Instalar como Serviço Windows
echo 2. Criar Tarefa Agendada
echo 3. Rodar em Loop Local (monitoramento)
echo 4. Configurar Energia (não hibernar)
echo 5. Verificar Status
echo ---------------------------------
set /p choice="Digite sua escolha (1-5): "

if "%choice%"=="1" goto servico
if "%choice%"=="2" goto tarefa
if "%choice%"=="3" goto loop_local
if "%choice%"=="4" goto energia
if "%choice%"=="5" goto status
goto end

:servico
echo 🏠 Instalando como serviço...
:: aqui você chamaria seu instalador ou NSSM
pause
goto end

:tarefa
echo 🕐 Criando tarefa agendada...
schtasks /create /tn "MamuteIA24h" /tr "\"%~dp0mamute_definitivo_sempre_online.py\"" /sc onstart /ru System /f
pause
goto end

:loop_local
echo 🔄 Rodando Mamute em loop local...
cd /d "%~dp0"
:loop
netstat -an | findstr ":8001" >nul
if %errorlevel% neq 0 (
    echo 🔧 Reiniciando Mamute...
    start /b python mamute_definitivo_sempre_online.py
)
timeout /t 60 >nul
goto loop

:energia
echo 💻 Configurando energia para não hibernar...
powercfg /setacvalueindex SCHEME_CURRENT 4f971e89-eebd-4455-a8de-9e59040e7347 5ca83367-6e45-459f-a27b-476b1d01c936 0
powercfg /setdcvalueindex SCHEME_CURRENT 4f971e89-eebd-4455-a8de-9e59040e7347 5ca83367-6e45-459f-a27b-476b1d01c936 0
powercfg /setactive SCHEME_CURRENT
pause
goto end

:status
echo 📊 Verificando status...
sc query MamuteIA24h
tasklist /fi "imagename eq python.exe" | findstr python
pause
goto end

:end
echo ✅ Fim do script
pause