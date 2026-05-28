@echo off
title MAMUTE - TESTE COMPLETO DO SISTEMA
color 0E

echo.
echo ============================================================
echo   🧪 MAMUTE - TESTE COMPLETO DO SISTEMA
echo ============================================================
echo   🔍 Executando bateria completa de testes...
echo   📊 Verificando funcionamento de todos os componentes...
echo ============================================================
echo.

cd /d "%~dp0"

python testar_sistema_completo.py

echo.
echo ============================================================
echo   Teste finalizado. Pressione qualquer tecla para sair...
echo ============================================================
pause >nul