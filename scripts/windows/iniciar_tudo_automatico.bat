@echo off
title Mamute - Servidores Automáticos (Local + Global)
color 0A
echo.
echo ████████████████████████████████████████████████████████████
echo   🐘 MAMUTE - SISTEMA DE SERVIDORES AUTOMÁTICOS
echo ████████████████████████████████████████████████████████████
echo.
echo 🚀 Iniciando servidores local e global automaticamente...
echo 🔧 Monitoramento contínuo e restart automático ativados
echo.
echo 📍 URLs que serão criados:
echo    🏠 Local:  http://localhost:8000
echo    🌍 Global: Será exibido quando ngrok conectar
echo.
echo ⚠️  MANTENHA ESTA JANELA ABERTA
echo 🛑 Para parar tudo: Ctrl+C
echo.
echo ════════════════════════════════════════════════════════════
echo.

REM Configurar variáveis de ambiente
set POSTGRES_HOST=localhost
set POSTGRES_PORT=5432
set POSTGRES_DB=ia_database
set POSTGRES_USER=postgres
set POSTGRES_PASSWORD=postgres@
set DATABASE_URL=postgresql://postgres:postgres%%40@localhost:5432/ia_database
set AI_NAME=Mamute

REM Iniciar sistema automático
echo 🚀 Iniciando sistema completo...
python mamute_servidor_automatico.py

echo.
echo ════════════════════════════════════════════════════════════
echo 🛑 Servidores parados
echo ════════════════════════════════════════════════════════════
pause