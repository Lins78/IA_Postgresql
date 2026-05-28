@echo off
title Servidor Mamute - localhost:8000
echo ==========================================
echo 🐘 INICIANDO SERVIDOR MAMUTE
echo ==========================================
echo.
echo 🌐 Servidor será iniciado em: http://localhost:8000
echo 💬 Chat disponível em: http://localhost:8000/chat
echo 📚 API Docs em: http://localhost:8000/docs
echo.
echo ⚠️  NÃO FECHE ESTA JANELA ENQUANTO USAR O MAMUTE
echo 🛑 Para parar, pressione Ctrl+C
echo.
echo Iniciando servidor...
echo.

REM Definir variáveis de ambiente
set POSTGRES_HOST=localhost
set POSTGRES_PORT=5432
set POSTGRES_DB=ia_database
set POSTGRES_USER=postgres
set POSTGRES_PASSWORD=postgres@
set DATABASE_URL=postgresql://postgres:postgres%%40@localhost:5432/ia_database
set AI_NAME=Mamute

REM Iniciar servidor
python -m uvicorn web_app:app --host 0.0.0.0 --port 8000 --reload

pause