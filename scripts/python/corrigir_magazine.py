#!/usr/bin/env python3
"""
🔧 DIAGNÓSTICO E CORREÇÃO - BANCO MAGAZINE
Verifica e corrige conexão com banco Magazine
"""

import psycopg2
import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT_DIR / "src"
APPS_DIR = SRC_DIR / "apps"

def verificar_bancos_disponiveis():
    """Verifica todos os bancos disponíveis"""
    print("🔍 VERIFICANDO BANCOS DISPONÍVEIS")
    print("=" * 50)
    
    load_dotenv()
    
    try:
        # Conectar ao postgres padrão para listar bancos
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=os.getenv("POSTGRES_PORT", "5432"),
            database="postgres",  # Base padrão
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "postgres@")
        )
        
        cursor = conn.cursor()
        
        # Listar todos os bancos
        cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false")
        bancos = cursor.fetchall()
        
        print("📋 Bancos disponíveis:")
        for banco in bancos:
            print(f"   • {banco[0]}")
            
        # Verificar se magazine existe
        magazine_existe = any('magazine' in str(banco[0]).lower() for banco in bancos)
        
        if magazine_existe:
            print("\n✅ Banco 'magazine' encontrado!")
            return True, bancos
        else:
            print("\n❌ Banco 'magazine' NÃO encontrado")
            return False, bancos
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False, []

def testar_conexao_magazine():
    """Testa conexão específica com Magazine"""
    print("\n🧪 TESTANDO CONEXÃO COM MAGAZINE")
    print("=" * 50)
    
    load_dotenv()
    
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=os.getenv("POSTGRES_PORT", "5432"),
            database="magazine",
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "postgres@")
        )
        
        cursor = conn.cursor()
        
        # Testar consulta básica
        cursor.execute("SELECT current_database(), current_user, version()")
        resultado = cursor.fetchone()
        
        print("✅ CONEXÃO COM MAGAZINE ESTABELECIDA!")
        print(f"   📋 Banco: {resultado[0]}")
        print(f"   👤 Usuário: {resultado[1]}")
        print(f"   🔧 Versão: {resultado[2][:50]}...")
        
        # Listar tabelas
        cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
        """)
        
        tabelas = cursor.fetchall()
        
        print(f"\n📊 Tabelas encontradas ({len(tabelas)}):")
        for tabela in tabelas[:10]:  # Mostrar só as primeiras 10
            print(f"   • {tabela[0]}")
            
        if len(tabelas) > 10:
            print(f"   ... e mais {len(tabelas) - 10} tabelas")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False

def corrigir_permissoes_magazine():
    """Corrige permissões do banco Magazine"""
    print("\n🔧 CORRIGINDO PERMISSÕES DO MAGAZINE")
    print("=" * 50)
    
    load_dotenv()
    
    try:
        # Conectar como superuser
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=os.getenv("POSTGRES_PORT", "5432"),
            database="postgres",
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "postgres@")
        )
        
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Dar permissões ao usuário postgres no Magazine
        cursor.execute("GRANT ALL PRIVILEGES ON DATABASE magazine TO postgres")
        print("✅ Permissões concedidas")
        
        # Tentar conectar novamente ao Magazine
        cursor.close()
        conn.close()
        
        # Testar conexão
        conn_magazine = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=os.getenv("POSTGRES_PORT", "5432"),
            database="magazine",
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "postgres@")
        )
        
        cursor_mag = conn_magazine.cursor()
        
        # Dar permissões em todas as tabelas
        cursor_mag.execute("GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres")
        cursor_mag.execute("GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres")
        
        print("✅ Permissões nas tabelas concedidas")
        
        cursor_mag.close()
        conn_magazine.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def testar_analise_magazine():
    """Testa análise do banco Magazine"""
    print("\n📊 TESTANDO ANÁLISE DO MAGAZINE")
    print("=" * 50)
    
    try:
        import sys
        if str(SRC_DIR) not in sys.path:
            sys.path.insert(0, str(SRC_DIR))
        if str(APPS_DIR) not in sys.path:
            sys.path.insert(0, str(APPS_DIR))

        from main import IAPostgreSQL
        
        # Inicializar Mamute
        ia = IAPostgreSQL()
        ia.setup_database()
        
        # Criar sessão
        session_id = ia.start_conversation("usuario_magazine")
        
        # Testar análise do Magazine
        resposta = ia.chat("Analise o banco de dados Magazine", session_id)
        
        if resposta and 'response' in resposta:
            print("✅ ANÁLISE FUNCIONANDO!")
            print(f"🐘 Resposta: {resposta['response'][:200]}...")
            return True
        else:
            print(f"❌ Erro na análise: {resposta}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Executar diagnóstico completo"""
    print("🔧 DIAGNÓSTICO COMPLETO - BANCO MAGAZINE")
    print("🎯 Verificando e corrigindo conexão")
    print("=" * 70)
    
    # Passo 1: Verificar bancos
    magazine_existe, bancos = verificar_bancos_disponiveis()
    
    if not magazine_existe:
        print("\n❌ Magazine não encontrado!")
        print("💡 Bancos disponíveis para análise:")
        for banco in bancos:
            if banco[0] not in ['postgres', 'template0', 'template1']:
                print(f"   🗄️ {banco[0]}")
        return
    
    # Passo 2: Testar conexão
    if testar_conexao_magazine():
        print("\n✅ Conexão OK!")
    else:
        print("\n🔧 Tentando corrigir permissões...")
        if corrigir_permissoes_magazine():
            print("✅ Permissões corrigidas!")
            
            # Testar novamente
            if testar_conexao_magazine():
                print("✅ Conexão funcionando após correção!")
            else:
                print("❌ Ainda há problemas na conexão")
                return
        else:
            print("❌ Falha ao corrigir permissões")
            return
    
    # Passo 3: Testar análise
    if testar_analise_magazine():
        print("\n🎉 MAGAZINE TOTALMENTE FUNCIONAL!")
        print("=" * 70)
        print("✅ Banco acessível")
        print("✅ Permissões corretas") 
        print("✅ Análise funcionando")
        print()
        print("🐘 Agora o Mamute pode analisar o Magazine!")
    else:
        print("\n❌ Problema na análise")

if __name__ == "__main__":
    main()