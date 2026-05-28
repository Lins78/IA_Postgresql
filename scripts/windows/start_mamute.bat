@echo off
title 🐘 MAMUTE - SERVIDOR SEMPRE ATIVO
color 0A
cls
echo.
echo ████████████████████████████████████████████████████
echo   🐘 MAMUTE - SERVIDOR AUTOMÁTICO SEMPRE ATIVO
echo ████████████████████████████████████████████████████
echo.
echo 🚀 Iniciando sistema completo...
echo.

REM Configurar variáveis de ambiente
set POSTGRES_HOST=localhost
set POSTGRES_PORT=5432
set POSTGRES_DB=ia_database
set POSTGRES_USER=postgres
set POSTGRES_PASSWORD=postgres@
set DATABASE_URL=postgresql://postgres:postgres%%40@localhost:5432/ia_database
set AI_NAME=Mamute
set PYTHONPATH=%CD%

echo ⚙️ Configurações definidas
echo 📍 PostgreSQL: localhost:5432/ia_database
echo 🤖 IA: Mamute
echo.

echo 🚀 Iniciando servidor web...
echo 🌐 URL será: http://localhost:8000
echo 💬 Chat em: http://localhost:8000/chat
echo 📚 Docs em: http://localhost:8000/docs
echo.
echo ⚠️  MANTENHA ESTA JANELA ABERTA
echo 🛑 Para parar: Ctrl+C
echo.
echo Aguarde... Iniciando Mamute...
echo.

REM Iniciar servidor com configuração completa
python -m uvicorn web_app:app --host 0.0.0.0 --port 8000 --reload --log-level info

echo.
echo ════════════════════════════════════════════════════════
echo 🛑 Servidor Mamute parado
echo ════════════════════════════════════════════════════════
pause