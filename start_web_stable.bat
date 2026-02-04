@echo off
echo ============================================================
echo 🐘 INICIANDO MAMUTE WEB - MODO ESTAVEL
echo ============================================================
echo ✅ Sistema: Mamute - IA PostgreSQL
echo ✅ Servidor: FastAPI + Uvicorn  
echo ✅ URL: http://localhost:8000
echo ============================================================

cd /d "c:\Users\carlo\Desktop\Projetos\IA_Postgresql"
echo 🚀 Iniciando servidor web estável...
.venv\Scripts\python.exe -m uvicorn web_app:app --host 0.0.0.0 --port 8000

echo.
echo 🛑 Servidor finalizado
pause