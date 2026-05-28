"""
Script de configuração e integração com PostgreSQL
Configurado para PostgreSQL em C:\PostgreSql\bin
"""
import os
import sys
import subprocess
import glob
from pathlib import Path

# Adicionar o diretório src ao path
ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / 'src'
APPS_DIR = SRC_DIR / 'apps'
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(APPS_DIR) not in sys.path:
    sys.path.insert(0, str(APPS_DIR))

from src.utils.config import Config
from src.utils.logger import setup_logger

def find_postgresql():
    """Encontra a instalação do PostgreSQL no Windows"""
    
    # Localização específica informada pelo usuário
    user_postgresql_path = "C:\\PostgreSql\\bin"
    
    # Possíveis localizações do PostgreSQL no Windows
    possible_paths = [
        user_postgresql_path,  # Prioridade para a localização do usuário
        "C:\\Program Files\\PostgreSQL\\*\\bin",
        "C:\\Program Files (x86)\\PostgreSQL\\*\\bin", 
        "C:\\PostgreSQL\\*\\bin",
        "C:\\psql\\bin",
    ]
    
    postgresql_path = None
    
    for path_pattern in possible_paths:
        # Se contém *, expandir com glob
        if "*" in path_pattern:
            matching_paths = glob.glob(path_pattern)
            if matching_paths:
                # Pegar a versão mais recente (última na lista)
                postgresql_path = matching_paths[-1]
                break
        else:
            # Verificar se o caminho existe diretamente
            if os.path.exists(path_pattern):
                postgresql_path = path_pattern
                break
    
    return postgresql_path

def check_postgresql_service():
    """Verifica se o serviço PostgreSQL está rodando"""
    try:
        # Verificar serviços do PostgreSQL
        result = subprocess.run(
            ["sc", "query", "postgresql"], 
            capture_output=True, 
            text=True,
            shell=True
        )
        
        if "RUNNING" in result.stdout:
            return True, "PostgreSQL está rodando"
        elif "STOPPED" in result.stdout:
            return False, "PostgreSQL está parado"
        else:
            # Tentar outros nomes de serviço
            for service_name in ["postgresql-x64-16", "postgresql-x64-15", "postgresql-x64-14"]:
                result = subprocess.run(
                    ["sc", "query", service_name], 
                    capture_output=True, 
                    text=True,
                    shell=True
                )
                if "RUNNING" in result.stdout:
                    return True, f"PostgreSQL ({service_name}) está rodando"
                    
            return False, "Serviço PostgreSQL não encontrado"
            
    except Exception as e:
        return False, f"Erro ao verificar serviço: {e}"

def start_postgresql_service():
    """Tenta iniciar o serviço PostgreSQL"""
    try:
        # Tentar nomes comuns de serviço PostgreSQL
        service_names = ["postgresql", "postgresql-x64-16", "postgresql-x64-15", "postgresql-x64-14"]
        
        for service_name in service_names:
            try:
                result = subprocess.run(
                    ["net", "start", service_name],
                    capture_output=True,
                    text=True,
                    shell=True
                )
                
                if result.returncode == 0:
                    return True, f"Serviço {service_name} iniciado com sucesso"
                    
            except Exception:
                continue
                
        return False, "Não foi possível iniciar o serviço PostgreSQL automaticamente"
        
    except Exception as e:
        return False, f"Erro ao iniciar serviço: {e}"

def test_database_connection():
    """Testa a conexão com o banco de dados"""
    try:
        config = Config()
        
        # Importar aqui para evitar erro se psycopg2 não estiver disponível
        import psycopg2
        
        # Tentar conectar primeiro sem especificar banco (para criar se necessário)
        try:
            conn = psycopg2.connect(
                host=config.postgres_host,
                port=config.postgres_port,
                user=config.postgres_user,
                password=config.postgres_password,
                database="postgres"  # Conectar ao banco padrão primeiro
            )
            conn.close()
            
            print(f"✅ Conexão com PostgreSQL bem-sucedida!")
            print(f"   Host: {config.postgres_host}")
            print(f"   Porta: {config.postgres_port}")
            print(f"   Usuário: {config.postgres_user}")
            
            return True, "Conexão bem-sucedida"
            
        except psycopg2.OperationalError as e:
            error_msg = str(e).lower()
            
            if "authentication failed" in error_msg:
                return False, "Erro de autenticação - verifique usuário e senha no .env"
            elif "connection refused" in error_msg:
                return False, "Conexão recusada - PostgreSQL pode não estar rodando"
            elif "does not exist" in error_msg:
                return False, "Banco de dados não existe - será criado automaticamente"
            else:
                return False, f"Erro de conexão: {e}"
                
    except ImportError:
        return False, "psycopg2 não está instalado. Execute: pip install psycopg2-binary"
    except Exception as e:
        return False, f"Erro inesperado: {e}"

def create_database():
    """Cria o banco de dados se não existir"""
    try:
        config = Config()
        import psycopg2
        from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
        
        # Conectar ao banco postgres padrão
        conn = psycopg2.connect(
            host=config.postgres_host,
            port=config.postgres_port,
            user=config.postgres_user,
            password=config.postgres_password,
            database="postgres"
        )
        
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Verificar se o banco já existe
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (config.postgres_db,)
        )
        
        if cursor.fetchone():
            print(f"✅ Banco de dados '{config.postgres_db}' já existe")
            return True, "Banco já existe"
        else:
            # Criar o banco de dados
            cursor.execute(f'CREATE DATABASE "{config.postgres_db}"')
            print(f"✅ Banco de dados '{config.postgres_db}' criado com sucesso")
            return True, "Banco criado"
            
    except Exception as e:
        return False, f"Erro ao criar banco: {e}"
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def setup_postgresql():
    """Configuração completa do PostgreSQL"""
    logger = setup_logger("PostgreSQL_Setup")
    
    print("🔧 CONFIGURAÇÃO DO POSTGRESQL")
    print("=" * 40)
    print()
    
    # 1. Verificar instalação do PostgreSQL
    print("1️⃣ Verificando instalação do PostgreSQL...")
    postgresql_path = find_postgresql()
    
    if postgresql_path:
        print(f"   ✅ PostgreSQL encontrado em: {postgresql_path}")
        
        # Adicionar ao PATH se necessário
        if postgresql_path not in os.environ.get("PATH", ""):
            os.environ["PATH"] = postgresql_path + ";" + os.environ.get("PATH", "")
            print(f"   ✅ Caminho adicionado ao PATH temporariamente")
    else:
        print("   ❌ PostgreSQL não encontrado!")
        print("   💡 Instale o PostgreSQL ou verifique o caminho de instalação")
        return False
    
    # 2. Verificar serviço
    print("\n2️⃣ Verificando serviço PostgreSQL...")
    is_running, service_msg = check_postgresql_service()
    print(f"   {service_msg}")
    
    if not is_running:
        print("   🔄 Tentando iniciar o serviço...")
        started, start_msg = start_postgresql_service()
        if started:
            print(f"   ✅ {start_msg}")
        else:
            print(f"   ⚠️ {start_msg}")
            print("   💡 Inicie manualmente: 'net start postgresql' (como administrador)")
    
    # 3. Verificar arquivo .env
    print("\n3️⃣ Verificando configurações...")
    env_file = ".env"
    
    if not os.path.exists(env_file):
        print("   ❌ Arquivo .env não encontrado!")
        print("   💡 Copie .env.example para .env e configure as credenciais")
        return False
    
    try:
        config = Config()
        config.validate()
        print("   ✅ Configurações válidas")
    except Exception as e:
        print(f"   ❌ Erro na configuração: {e}")
        return False
    
    # 4. Testar conexão
    print("\n4️⃣ Testando conexão com banco de dados...")
    connected, conn_msg = test_database_connection()
    
    if connected:
        print(f"   ✅ {conn_msg}")
    else:
        print(f"   ❌ {conn_msg}")
        
        if "does not exist" in conn_msg.lower():
            print("   🔄 Tentando criar banco de dados...")
            created, create_msg = create_database()
            if created:
                print(f"   ✅ {create_msg}")
            else:
                print(f"   ❌ {create_msg}")
                return False
        else:
            return False
    
    # 5. Configurar tabelas
    print("\n5️⃣ Configurando tabelas...")
    try:
        from src.apps.main import IAPostgreSQL
        ia_system = IAPostgreSQL()
        ia_system.setup_database()
        print("   ✅ Tabelas criadas/verificadas com sucesso")
    except Exception as e:
        print(f"   ❌ Erro ao configurar tabelas: {e}")
        return False
    
    print("\n🎉 CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 40)
    print("✅ PostgreSQL configurado e funcionando")
    print("✅ Banco de dados criado")
    print("✅ Tabelas configuradas")
    print("\n💡 Agora você pode executar:")
    print("   • python main.py")
    print("   • streamlit run examples/streamlit_app.py")
    
    return True

def main():
    """Função principal"""
    try:
        success = setup_postgresql()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\n❌ Configuração interrompida pelo usuário")
        return 1
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        return 1

if __name__ == "__main__":
    exit(main())