#!/usr/bin/env python3
"""
🔧 VERIFICADOR E INSTALADOR AUTOMÁTICO DE DEPENDÊNCIAS - MAMUTE
Garante que todas as dependências estejam instaladas e funcionando
"""

import subprocess
import sys
import os
import importlib
import json
from pathlib import Path

def check_python_version():
    """Verificar versão do Python"""
    version = sys.version_info
    print(f"🐍 Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ ERRO: Python 3.8+ é necessário!")
        print("   Faça download em: https://python.org")
        return False
    
    print("✅ Versão do Python OK")
    return True

def install_package(package_name, import_name=None):
    """Instalar pacote Python"""
    if import_name is None:
        import_name = package_name
    
    try:
        importlib.import_module(import_name)
        print(f"✅ {package_name} já instalado")
        return True
    except ImportError:
        print(f"📦 Instalando {package_name}...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", package_name, "--upgrade"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"✅ {package_name} instalado com sucesso")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao instalar {package_name}: {e}")
            return False

def check_postgresql():
    """Verificar se PostgreSQL está acessível"""
    try:
        import psycopg2
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="ia_database",
            user="postgres",
            password="postgres@",
            connect_timeout=3
        )
        conn.close()
        print("✅ PostgreSQL conectado com sucesso")
        return True
    except Exception as e:
        print(f"⚠️ PostgreSQL não acessível: {e}")
        print("   Verifique se o PostgreSQL está rodando")
        print("   Usuário: postgres | Senha: postgres@ | Banco: ia_database")
        return False

def check_tunnel_tools():
    """Verificar ferramentas de túnel"""
    tools = {
        "ngrok": "ngrok",
        "cloudflared": "cloudflare tunnel"
    }
    
    available_tools = []
    
    for tool, description in tools.items():
        try:
            result = subprocess.run(
                [tool, "--version"], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            if result.returncode == 0:
                print(f"✅ {description} disponível")
                available_tools.append(tool)
            else:
                print(f"⚠️ {description} não encontrado")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print(f"⚠️ {description} não encontrado")
    
    if not available_tools:
        print("📝 DICA: Instale ngrok ou cloudflared para acesso remoto")
        print("   ngrok: https://ngrok.com/download")
        print("   cloudflared: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/")
    
    return available_tools

def create_env_file():
    """Criar arquivo .env se não existir"""
    env_file = Path(".env")
    
    if not env_file.exists():
        print("📝 Criando arquivo .env...")
        env_content = """# Configurações do Mamute
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ia_database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres@
DATABASE_URL=postgresql://postgres:postgres%40@localhost:5432/ia_database
AI_NAME=Mamute
"""
        
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print("✅ Arquivo .env criado")
    else:
        print("✅ Arquivo .env existe")

def check_web_app():
    """Verificar se web_app.py existe e é válido"""
    web_app = Path("web_app.py")
    
    if not web_app.exists():
        print("❌ Arquivo web_app.py não encontrado!")
        return False
    
    try:
        with open(web_app, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Verificar imports essenciais
        required_imports = ["FastAPI", "uvicorn"]
        missing_imports = []
        
        for imp in required_imports:
            if imp not in content:
                missing_imports.append(imp)
        
        if missing_imports:
            print(f"⚠️ Imports faltando no web_app.py: {missing_imports}")
            return False
        
        print("✅ web_app.py OK")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar web_app.py: {e}")
        return False

def main():
    """Verificação principal"""
    print("🔧 VERIFICADOR DE DEPENDÊNCIAS - MAMUTE")
    print("="*50)
    
    success = True
    
    # 1. Verificar Python
    if not check_python_version():
        success = False
    
    print("\n📦 VERIFICANDO DEPENDÊNCIAS PYTHON...")
    print("-"*40)
    
    # 2. Dependências essenciais
    essential_packages = [
        ("psycopg2-binary", "psycopg2"),
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("python-dotenv", "dotenv"),
        ("requests", "requests"),
        ("psutil", "psutil"),
        ("openai", "openai"),
    ]
    
    for package, import_name in essential_packages:
        if not install_package(package, import_name):
            success = False
    
    print("\n🗄️ VERIFICANDO BANCO DE DADOS...")
    print("-"*40)
    
    # 3. PostgreSQL
    check_postgresql()
    
    print("\n🌐 VERIFICANDO FERRAMENTAS DE TÚNEL...")
    print("-"*40)
    
    # 4. Ferramentas de túnel
    check_tunnel_tools()
    
    print("\n📁 VERIFICANDO ARQUIVOS...")
    print("-"*40)
    
    # 5. Arquivos
    create_env_file()
    
    if not check_web_app():
        success = False
    
    print("\n" + "="*50)
    
    if success:
        print("✅ TODAS AS VERIFICAÇÕES PASSARAM!")
        print("🚀 Sistema pronto para uso!")
        print("\n💡 Para iniciar o Mamute:")
        print("   🐘 Execute: START_MAMUTE_DEFINITIVO.bat")
        print("   📜 Ou: python mamute_definitivo_sempre_online.py")
    else:
        print("⚠️ ALGUMAS VERIFICAÇÕES FALHARAM")
        print("🔧 Corrija os problemas e execute novamente")
    
    print("="*50)
    input("\nPressione Enter para continuar...")

if __name__ == "__main__":
    main()