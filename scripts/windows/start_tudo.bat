@echo off
echo 🚀 INICIANDO IA MAMUTE + NGROK EM PARALELO
echo ==========================================
echo.

echo 🐘 Iniciando servidor IA Mamute...
start /b python mamute_seguro_corrigido.py

echo ⏳ Aguardando servidor inicializar...
timeout /t 3 /nobreak >nul

echo 🌍 Criando túnel ngrok...
start /b ngrok http 8000

echo ⏳ Aguardando túnel conectar...
timeout /t 5 /nobreak >nul

echo.
echo ✅ AMBOS ATIVOS!
echo 🌐 URL Global: https://fernando-loving-agelessly.ngrok-free.dev
echo 🔒 Admin Local: http://localhost:8000/admin
echo.
echo ⚠️ Para parar tudo: Ctrl+C neste terminal
echo.

:loop
echo 📊 Status: IA + Ngrok rodando...
timeout /t 10 /nobreak >nul
goto loop