@echo off
echo 🚀 Iniciando Mamute 24h automaticamente...
cd /d "%~dp0"

:: Verificar se já está rodando

set PORTA=8002
netstat -an | findstr ":%PORTA%" >nul
if %errorlevel% equ 0 (
    echo ✅ Mamute já está rodando!
    echo 🌐 Acesso: http://localhost:%PORTA%
) else (
    echo 🔧 Iniciando Mamute...
    start /b python ..\..\src\apps\mamute_definitivo_sempre_online.py
    timeout 3 >nul
    echo ✅ Mamute iniciado! 
    echo 🌐 Acesso: http://localhost:%PORTA%
)

pause