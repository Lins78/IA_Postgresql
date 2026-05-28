@echo off
title MAMUTE - Instalacao Rapida

echo 🚀 MAMUTE - INSTALAÇÃO RÁPIDA
echo ==============================
echo.
echo 📦 Instalando dependências...
echo ⚙️ Configurando sistema...
echo 🐘 Preparando PostgreSQL...
echo.

REM Ir para o diretório do projeto
cd /d "%~dp0"

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    py --version >nul 2>&1
    if errorlevel 1 (
        echo ❌ Python não encontrado!
        echo.
        echo 💡 INSTALE PYTHON PRIMEIRO:
        echo   1. Vá para: https://python.org/downloads
        echo   2. Baixe e instale Python 3.11+
        echo   3. Marque "Add to PATH" durante instalação
        echo   4. Execute este script novamente
        echo.
        pause
        exit /b 1
    ) else (
        set PYTHON_CMD=py
    )
) else (
    set PYTHON_CMD=python
)

echo ✅ Python encontrado!
echo.

REM Atualizar pip
echo 📦 Atualizando pip...
%PYTHON_CMD% -m pip install --upgrade pip

REM Instalar dependências
echo 📦 Instalando dependências...
%PYTHON_CMD% -m pip install -r requirements.txt

REM Verificar se instalação foi bem-sucedida
if errorlevel 1 (
    echo.
    echo ❌ Erro na instalação das dependências
    echo.
    echo 💡 SOLUÇÕES:
    echo   1. Verificar conexão com internet
    echo   2. Executar como administrador
    echo   3. Instalar manualmente: pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo ✅ Dependências instaladas!
echo.

REM Configurar sistema automaticamente
echo ⚙️ Configurando sistema automaticamente...
%PYTHON_CMD% configurar_automatico.py

if errorlevel 1 (
    echo.
    echo ⚠️ Configuração automática com problemas
    echo 💡 Continue mesmo assim - sistema pode funcionar
    echo.
)

echo.
echo ✅ INSTALAÇÃO CONCLUÍDA!
echo ======================
echo.
echo 🚀 Para iniciar o sistema:
echo   Duplo-clique em: INICIAR_MAMUTE.bat
echo.
echo 📋 Ou execute:
echo   python iniciar_mamute.py
echo.
echo 🔧 Para reconfigurar:
echo   python configurar_automatico.py
echo.

pause