#!/bin/bash

# Script de inicialização para IA PostgreSQL
# Para sistemas Linux/Mac

echo ""
echo "========================================"
echo "    IA CONECTADA AO POSTGRESQL"
echo "========================================"
echo ""

# Verificar se o ambiente virtual existe
if [ ! -d ".venv" ]; then
    echo "Criando ambiente virtual..."
    python3 -m venv .venv
    echo ""
fi

# Ativar ambiente virtual
echo "Ativando ambiente virtual..."
source .venv/bin/activate

# Verificar se o arquivo .env existe
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  ATENÇÃO: Arquivo .env não encontrado!"
    echo "Copiando arquivo de exemplo..."
    cp .env.example .env
    echo ""
    echo "📝 IMPORTANTE: Edite o arquivo .env com suas configurações:"
    echo "   - OPENAI_API_KEY"
    echo "   - Configurações do PostgreSQL"
    echo ""
    read -p "Pressione ENTER para continuar..."
    exit 1
fi

echo ""
echo "Escolha uma opção:"
echo ""
echo "1. 🚀 Executar sistema principal"
echo "2. 🌐 Abrir interface web (Streamlit)"
echo "3. 📝 Executar exemplos básicos"
echo "4. 🔧 Verificar configurações"
echo "5. 📦 Instalar dependências"
echo ""

read -p "Digite sua opção (1-5): " opcao

case $opcao in
    1)
        echo ""
        echo "Iniciando sistema principal..."
        python main.py
        ;;
    2)
        echo ""
        echo "Abrindo interface web..."
        echo "🌐 Acesse: http://localhost:8501"
        streamlit run examples/streamlit_app.py
        ;;
    3)
        echo ""
        echo "Executando exemplos básicos..."
        python examples/exemplo_basico.py
        ;;
    4)
        echo ""
        echo "Verificando configurações..."
        python -c "from src.utils.config import Config; c = Config(); print('✅ Configurações válidas' if c.validate() else '❌ Configurações inválidas')"
        ;;
    5)
        echo ""
        echo "Instalando dependências..."
        pip install -r requirements.txt
        echo "✅ Dependências instaladas!"
        ;;
    *)
        echo ""
        echo "❌ Opção inválida!"
        ;;
esac

echo ""
read -p "Pressione ENTER para continuar..."