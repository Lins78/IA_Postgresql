@echo off
title SOLUCAO RAPIDA 24H - Mamute IA
echo.
echo ████████████████████████████████████████████████
echo ██  🚀 SOLUÇÃO RÁPIDA 24H - 100% FUNCIONAL   ██
echo ████████████████████████████████████████████████
echo.

cd /d "%~dp0"

echo 🎯 MÉTODO 1: Executar como Administrador
echo.
echo PASSO A PASSO DETALHADO:
echo.
echo 1. 🖱️  FECHE esta janela
echo 2. 💻 Abra "Prompt de Comando como ADMINISTRADOR":
echo    - Aperte Windows + R
echo    - Digite: cmd
echo    - Aperte Ctrl+Shift+Enter (abre como admin)
echo.
echo 3. 📁 Cole este comando exato:
echo    cd /d "C:\Users\carlo\Desktop\Projetos\IA_Postgresql"
echo.
echo 4. 🚀 Execute o instalador:
echo    install_mamute_service.bat
echo.
echo ════════════════════════════════════════════════
echo.
echo 🎯 MÉTODO 2: Solução Automática (MAIS SIMPLES)
echo.
set /p escolha="Quer que eu configure automaticamente? (s/n): "

if /i "%escolha%"=="s" goto metodo_automatico
if /i "%escolha%"=="n" goto metodo_manual
echo Opção inválida!
goto end

:metodo_automatico
echo.
echo 🔧 CONFIGURANDO AUTOMATICAMENTE...
echo.

:: Criar tarefa agendada que roda com privilégios
echo 📋 Criando tarefa automática...
echo.

:: Script PowerShell para criar tarefa com privilégios elevados
(
echo $Action = New-ScheduledTaskAction -Execute "python.exe" -Argument "%~dp0mamute_definitivo_sempre_online.py" -WorkingDirectory "%~dp0"
echo $Trigger = New-ScheduledTaskTrigger -AtStartup
echo $Principal = New-ScheduledTaskPrincipal -UserID "NT AUTHORITY\SYSTEM" -LogonType "ServiceAccount" -RunLevel "Highest"
echo $Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
echo Register-ScheduledTask -Action $Action -Trigger $Trigger -Principal $Principal -Settings $Settings -TaskName "MamuteIA24h" -Description "IA Mamute rodando 24h automaticamente"
) > temp_task.ps1

powershell -ExecutionPolicy Bypass -File temp_task.ps1

if %errorlevel% equ 0 (
    echo ✅ CONFIGURADO COM SUCESSO!
    echo.
    echo 🚀 Iniciando Mamute agora...
    start /b python mamute_definitivo_sempre_online.py
    
    echo.
    echo ✅ MAMUTE AGORA RODA 24H!
    echo.
    echo 📋 VERIFICAR:
    echo • Status: schtasks /query /tn "MamuteIA24h"
    echo • Acesso: http://localhost:8001
    echo • Logs: mamute_definitivo.log
    echo.
    echo 🔄 A IA reiniciará automaticamente com Windows!
    
    del temp_task.ps1 >nul 2>&1
) else (
    echo ❌ Erro! Tente o Método 1 acima
    del temp_task.ps1 >nul 2>&1
)

goto end

:metodo_manual
echo.
echo 📋 OK! Use o MÉTODO 1 acima
echo.
goto end

:end
echo.
echo 💡 DEPOIS DE CONFIGURAR:
echo • Feche o notebook completamente
echo • Teste em outro dispositivo: http://192.168.1.70:8001
echo • Se abrir = Está 24h online! 🎉
echo.
pause