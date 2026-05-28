"""
Script para criar o banco de dados ia_database
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_database():
    """Cria o banco de dados ia_database"""
    print("🔨 CRIANDO BANCO DE DADOS")
    print("=" * 30)
    
    try:
        # Conectar ao banco postgres (padrão)
        print("📡 Conectando ao PostgreSQL...")
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="postgres",  # Banco padrão
            user="postgres",
            password="postgres@"
        )
        
        # Configurar autocommit
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Verificar se o banco já existe
        print("🔍 Verificando se o banco ia_database já existe...")
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'ia_database'")
        
        if cursor.fetchone():
            print("✅ Banco de dados 'ia_database' já existe!")
        else:
            # Criar o banco
            print("🏗️ Criando banco de dados 'ia_database'...")
            cursor.execute("CREATE DATABASE ia_database")
            print("✅ Banco de dados 'ia_database' criado com sucesso!")
        
        cursor.close()
        conn.close()
        
        print("\\n🎉 Banco configurado e pronto para uso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    if create_database():
        print("\\nExecute agora: python test_database.py")
    else:
        print("\\n❌ Falha na criação do banco")