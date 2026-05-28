@echo off
title IA PostgreSQL - Setup e Execucao

echo.
echo ========================================
echo    IA CONECTADA AO POSTGRESQL
echo ========================================
echo.
echo PostgreSQL detectado em: C:\PostgreSql\bin

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
    echo 🔧 Execute a opção 4 para configurar as credenciais
    echo.
)

echo.
echo Escolha uma opcao:
echo.
echo 1. 🚀 Executar sistema principal
echo 2. 🌐 Abrir interface web (Streamlit)
echo 3. 📝 Executar exemplos básicos
echo 4. 🔐 Configurar credenciais PostgreSQL
echo 5. 🧪 Testar conexão PostgreSQL
echo 6. ⚙️ Configurar banco de dados completo
echo 7. 📦 Instalar dependências
echo.

set /p opcao="Digite sua opcao (1-7): "

if "%opcao%"=="1" (
    echo.
    echo Iniciando sistema principal...
    python main.py
) else if "%opcao%"=="2" (
    echo.
    echo Abrindo interface web...
    echo 🌐 Acesse: http://localhost:8501
    streamlit run examples\streamlit_app.py
) else if "%opcao%"=="3" (
    echo.
    echo Executando exemplos básicos...
    python examples\exemplo_basico.py
) else if "%opcao%"=="4" (
    echo.
    echo Configurando credenciais PostgreSQL...
    python configure_credentials.py
) else if "%opcao%"=="5" (
    echo.
    echo Testando conexão PostgreSQL...
    python test_connection.py
) else if "%opcao%"=="6" (
    echo.
    echo Configurando banco de dados completo...
    python setup_postgres.py
) else if "%opcao%"=="7" (
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