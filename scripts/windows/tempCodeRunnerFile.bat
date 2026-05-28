echo off
title MAMUTE - INSTALACAO E INICIO AUTOMATICO
color 0A
cls

echo.
echo ============================================================
echo   🐘 MAMUTE - INSTALACAO E INICIO AUTOMATICO
echo ============================================================
echo   🔧 Verificando e instalando dependencias...
echo   🚀 Iniciando sistema automaticamente...
echo ============================================================
echo.

cd /d "%~dp0"

echo 🔍 Executando verificacao de dependencias...
python verificar_dependencias.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Erro na verificacao de dependencias!
    echo    Tente executar manualmente: python verificar_dependencias.py
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   ✅ Dependencias verificadas com sucesso!
echo   🚀 Iniciando Mamute Definitivo...
echo ============================================================
echo.

python mamute_definitivo_sempre_online.py

echo.
echo ============================================================
echo   Sistema encerrado. Pressione qualquer tecla para sair...
echo ============================================================
pause >nul