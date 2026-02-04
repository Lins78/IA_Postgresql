@echo off
title IA PostgreSQL - Setup e Execucao

echo.
echo ========================================
echo    IA CONECTADA AO POSTGRESQL
echo ========================================
echo.

REM Verificar se o ambiente virtual existe
if not exist ".venv" (
    echo Criando ambiente virtual...
    python -m venv .venv
    echo.
)

REM Ativar ambiente virtual
echo Ativando ambiente virtual...
call .venv\Scripts\activate.bat

REM Verificar se o arquivo .env existe
if not exist ".env" (
    echo.
    echo ⚠️  ATENÇÃO: Arquivo .env não encontrado!
    echo Executando configuração automática...
    python setup_postgresql.py
    echo.
    if errorlevel 1 (
        echo ❌ Falha na configuração. Verifique o PostgreSQL.
        pause
        exit /b 1
    )
)

echo.
echo Escolha uma opcao:
echo.
echo 1. 🔧 Configurar PostgreSQL
echo 2. 🧪 Testar conexão com banco
echo 3. 🚀 Executar sistema principal
echo 4. 🌐 Abrir interface web (Streamlit)
echo 5. 📝 Executar exemplos básicos
echo 6. 📦 Instalar dependências
echo.

set /p opcao="Digite sua opcao (1-6): "

if "%opcao%"=="1" (
    echo.
    echo Configurando PostgreSQL...
    python setup_postgresql.py
) else if "%opcao%"=="2" (
    echo.
    echo Testando conexão...
    python test_database.py
) else if "%opcao%"=="3" (
    echo.
    echo Iniciando sistema principal...
    python main.py
) else if "%opcao%"=="4" (
    echo.
    echo Abrindo interface web...
    echo 🌐 Acesse: http://localhost:8501
    streamlit run examples\streamlit_app.py
) else if "%opcao%"=="5" (
    echo.
    echo Executando exemplos básicos...
    python examples\exemplo_basico.py
) else if "%opcao%"=="6" (
    echo.
    echo Instalando dependências...
    pip install -r requirements.txt
    echo ✅ Dependências instaladas!
) else (
    echo.
    echo ❌ Opção inválida!
)

echo.
pause