"""
Script de teste de conexão com PostgreSQL
Específico para instalação em C:\PostgreSql\bin
"""
import os
import sys
import subprocess

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_postgresql_path():
    """Testa se o PostgreSQL está acessível no caminho especificado"""
    postgresql_bin = "C:\\PostgreSql\\bin"
    
    print("🔍 TESTANDO POSTGRESQL")
    print("=" * 30)
    
    # Verificar se o diretório existe
    if not os.path.exists(postgresql_bin):
        print(f"❌ Diretório não encontrado: {postgresql_bin}")
        return False
    
    print(f"✅ Diretório encontrado: {postgresql_bin}")
    
    # Verificar arquivos essenciais
    essential_files = ["psql.exe", "pg_ctl.exe", "postgres.exe"]
    
    for file in essential_files:
        file_path = os.path.join(postgresql_bin, file)
        if os.path.exists(file_path):
            print(f"✅ Encontrado: {file}")
        else:
            print(f"❌ Não encontrado: {file}")
    
    # Tentar executar psql para verificar versão
    try:
        psql_path = os.path.join(postgresql_bin, "psql.exe")
        if os.path.exists(psql_path):
            result = subprocess.run(
                [psql_path, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print(f"✅ Versão: {result.stdout.strip()}")
                return True
            else:
                print(f"❌ Erro ao executar psql: {result.stderr}")
                return False
        else:
            print("❌ psql.exe não encontrado")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Timeout ao tentar executar psql")
        return False
    except Exception as e:
        print(f"❌ Erro ao testar psql: {e}")
        return False

def test_postgresql_service():
    """Testa o serviço PostgreSQL"""
    print("\n🔧 TESTANDO SERVIÇO")
    print("=" * 20)
    
    try:
        # Verificar se há algum serviço PostgreSQL rodando
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq postgres.exe"],
            capture_output=True,
            text=True,
            shell=True
        )
        
        if "postgres.exe" in result.stdout:
            print("✅ Processo postgres.exe está rodando")
            return True
        else:
            print("❌ Processo postgres.exe não encontrado")
            
            # Tentar listar serviços PostgreSQL
            services_result = subprocess.run(
                ["sc", "query", "type=", "service", "state=", "all"],
                capture_output=True,
                text=True,
                shell=True
            )
            
            if "postgresql" in services_result.stdout.lower():
                print("✅ Serviço PostgreSQL encontrado (mas pode estar parado)")
            else:
                print("❌ Serviço PostgreSQL não encontrado")
                
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar serviço: {e}")
        return False

def test_database_connection():
    """Testa conexão com banco de dados"""
    print("\n💾 TESTANDO CONEXÃO DE BANCO")
    print("=" * 30)
    
    try:
        from src.utils.config import Config
        
        # Verificar se as configurações estão corretas
        config = Config()
        
        print(f"Host: {config.postgres_host}")
        print(f"Porta: {config.postgres_port}")
        print(f"Usuário: {config.postgres_user}")
        print(f"Banco: {config.postgres_db}")
        
        # Tentar importar psycopg2
        try:
            import psycopg2
            print("✅ psycopg2 disponível")
        except ImportError:
            print("❌ psycopg2 não instalado")
            print("💡 Execute: pip install psycopg2-binary")
            return False
        
        # Tentar conectar
        try:
            conn = psycopg2.connect(
                host=config.postgres_host,
                port=config.postgres_port,
                user=config.postgres_user,
                password=config.postgres_password,
                database="postgres",  # Conectar ao banco padrão
                connect_timeout=5
            )
            
            # Testar uma query simples
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            
            print("✅ Conexão bem-sucedida!")
            print(f"📊 Versão do PostgreSQL: {version}")
            
            cursor.close()
            conn.close()
            
            return True
            
        except psycopg2.OperationalError as e:
            error_msg = str(e).lower()
            
            if "password authentication failed" in error_msg:
                print("❌ Erro de autenticação")
                print("💡 Verifique usuário e senha no arquivo .env")
            elif "connection refused" in error_msg:
                print("❌ Conexão recusada")
                print("💡 PostgreSQL pode não estar rodando")
            elif "timeout expired" in error_msg:
                print("❌ Timeout na conexão")
                print("💡 Verifique se PostgreSQL está rodando e acessível")
            else:
                print(f"❌ Erro de conexão: {e}")
                
            return False
            
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def main():
    """Função principal de teste"""
    print("🧪 DIAGNÓSTICO POSTGRESQL")
    print("=" * 40)
    print(f"Testando instalação em: C:\\PostgreSql\\bin")
    print()
    
    # Testes sequenciais
    tests_results = []
    
    # Teste 1: Caminho e arquivos
    tests_results.append(test_postgresql_path())
    
    # Teste 2: Serviço
    tests_results.append(test_postgresql_service())
    
    # Teste 3: Conexão (só se os anteriores passaram)
    if any(tests_results):
        tests_results.append(test_database_connection())
    
    # Resumo
    print("\n📋 RESUMO DOS TESTES")
    print("=" * 20)
    
    test_names = ["Instalação", "Serviço", "Conexão"]
    
    for i, (name, result) in enumerate(zip(test_names, tests_results)):
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{name}: {status}")
    
    success_count = sum(tests_results)
    total_tests = len(tests_results)
    
    print(f"\nResultado: {success_count}/{total_tests} testes passaram")
    
    if success_count == total_tests:
        print("\n🎉 POSTGRESQL ESTÁ FUNCIONANDO CORRETAMENTE!")
        print("Você pode executar o sistema agora.")
    else:
        print("\n⚠️ PROBLEMAS DETECTADOS")
        print("Siga as sugestões acima para resolver os problemas.")
    
    return success_count == total_tests

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)