"""
Script para configurar credenciais do PostgreSQL
"""
import getpass
import sys
from pathlib import Path

# Adicionar o diretório src ao path
ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / 'src'
APPS_DIR = SRC_DIR / 'apps'
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(APPS_DIR) not in sys.path:
    sys.path.insert(0, str(APPS_DIR))

def update_env_file():
    """Atualiza o arquivo .env com as credenciais corretas"""
    
    print("🔐 CONFIGURAÇÃO DE CREDENCIAIS POSTGRESQL")
    print("=" * 45)
    print()
    print("PostgreSQL detectado em: C:\\PostgreSql\\bin")
    print("Versão: PostgreSQL 9.4.26")
    print("Serviço: ✅ Rodando")
    print()
    
    # Obter credenciais do usuário
    print("Digite as credenciais do PostgreSQL:")
    print("(Pressione Enter para manter os valores padrão)")
    print()
    
    # Host
    host = input("Host [localhost]: ").strip() or "localhost"
    
    # Porta
    port_input = input("Porta [5432]: ").strip()
    port = port_input if port_input else "5432"
    
    # Usuário
    user = input("Usuário [postgres]: ").strip() or "postgres"
    
    # Senha
    password = getpass.getpass("Senha do PostgreSQL: ").strip()
    
    if not password:
        print("❌ Senha é obrigatória!")
        return False
    
    # Nome do banco
    database = input("Nome do banco [ia_database]: ").strip() or "ia_database"
    
    # Chave OpenAI (opcional por enquanto)
    print("\nChave da API OpenAI (opcional, pode configurar depois):")
    openai_key = input("OpenAI API Key [deixar vazio]: ").strip()
    if not openai_key:
        openai_key = "your_openai_api_key_here"
    
    print("\n📝 Atualizando arquivo .env...")
    
    # Criar conteúdo do .env
    env_content = f"""# Configurações da IA conectada ao PostgreSQL
OPENAI_API_KEY={openai_key}

# Configurações do PostgreSQL (C:\\PostgreSql\\bin)
POSTGRES_HOST={host}
POSTGRES_PORT={port}
POSTGRES_DB={database}
POSTGRES_USER={user}
POSTGRES_PASSWORD={password}
DATABASE_URL=postgresql://{user}:{password}@{host}:{port}/{database}

# Configurações da aplicação
DEBUG=True
LOG_LEVEL=INFO
MAX_TOKENS=4000
TEMPERATURE=0.7"""
    
    # Salvar arquivo .env
    try:
        with open(".env", "w", encoding="utf-8") as f:
            f.write(env_content)
        
        print("✅ Arquivo .env atualizado com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao salvar .env: {e}")
        return False

def test_connection_with_new_credentials():
    """Testa a conexão com as novas credenciais"""
    print("\n🧪 Testando conexão com novas credenciais...")
    
    try:
        from src.utils.config import Config
        import psycopg2
        
        config = Config()
        
        # Tentar conectar ao banco postgres primeiro
        conn = psycopg2.connect(
            host=config.postgres_host,
            port=config.postgres_port,
            user=config.postgres_user,
            password=config.postgres_password,
            database="postgres",
            connect_timeout=5
        )
        
        print("✅ Conexão com PostgreSQL bem-sucedida!")
        
        # Verificar se o banco da aplicação existe
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (config.postgres_db,)
        )
        
        if cursor.fetchone():
            print(f"✅ Banco '{config.postgres_db}' já existe")
        else:
            print(f"💡 Banco '{config.postgres_db}' será criado automaticamente")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False

def main():
    """Função principal"""
    try:
        # Atualizar credenciais
        if not update_env_file():
            return 1
        
        # Testar conexão
        if test_connection_with_new_credentials():
            print("\n🎉 CONFIGURAÇÃO CONCLUÍDA!")
            print("=" * 30)
            print("✅ Credenciais configuradas")
            print("✅ Conexão testada e funcionando")
            print()
            print("🚀 Próximos passos:")
            print("   1. python setup_postgres.py  (configurar banco e tabelas)")
            print("   2. python main.py  (executar sistema)")
            print("   3. streamlit run examples/streamlit_app.py  (interface web)")
            return 0
        else:
            print("\n❌ Falha na conexão")
            print("💡 Verifique as credenciais e tente novamente")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n❌ Configuração cancelada pelo usuário")
        return 1
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        return 1

if __name__ == "__main__":
    exit(main())