#!/usr/bin/env python3
"""
🧪 TESTE COMPLETO DO SISTEMA DEFINITIVO MAMUTE
Executa uma bateria completa de testes para verificar funcionamento
"""

import requests
import time
import json
import subprocess
import sys
from pathlib import Path

def test_server_response(port=8000, timeout=30):
    """Testar se o servidor está respondendo"""
    print(f"🌐 Testando servidor na porta {port}...")
    
    for attempt in range(timeout):
        try:
            # Testar health check
            response = requests.get(f"http://localhost:{port}/health", timeout=3)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check OK - Status: {data.get('status', 'unknown')}")
                return True
        except:
            pass
        
        try:
            # Testar rota principal
            response = requests.get(f"http://localhost:{port}/", timeout=3)
            if response.status_code in [200, 404]:
                print(f"✅ Servidor respondendo na porta {port}")
                return True
        except:
            pass
        
        print(f"⏳ Tentativa {attempt + 1}/{timeout}...")
        time.sleep(1)
    
    print(f"❌ Servidor não respondeu na porta {port} após {timeout}s")
    return False

def test_api_endpoints(port=8000):
    """Testar endpoints da API"""
    print("🔍 Testando endpoints da API...")
    
    base_url = f"http://localhost:{port}"
    
    # Endpoints para testar
    endpoints = [
        ("/health", "Health Check"),
        ("/", "Home/Dashboard"),
        ("/docs", "API Documentation"),
        ("/chat", "Chat Interface")
    ]
    
    results = []
    
    for endpoint, description in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code in [200, 404, 422]:  # 422 pode ser normal para alguns endpoints
                print(f"✅ {description} ({endpoint}) - Status: {response.status_code}")
                results.append(True)
            else:
                print(f"⚠️ {description} ({endpoint}) - Status: {response.status_code}")
                results.append(False)
        except Exception as e:
            print(f"❌ {description} ({endpoint}) - Erro: {e}")
            results.append(False)
    
    success_rate = sum(results) / len(results) * 100
    print(f"📊 Taxa de sucesso dos endpoints: {success_rate:.1f}%")
    
    return success_rate > 75  # Considerar sucesso se mais de 75% funcionarem

def test_database_connection():
    """Testar conexão com banco de dados"""
    print("🗄️ Testando conexão com banco de dados...")
    
    try:
        import psycopg2
        conn = psycopg2.connect(
            host="localhost",
            port="5432", 
            database="ia_database",
            user="postgres",
            password="postgres@",
            connect_timeout=5
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        print(f"✅ PostgreSQL conectado - Versão: {version[:50]}...")
        return True
        
    except Exception as e:
        print(f"❌ Erro na conexão com PostgreSQL: {e}")
        return False

def test_config_files():
    """Testar se arquivos de configuração existem"""
    print("📁 Verificando arquivos de configuração...")
    
    required_files = [
        "mamute_definitivo_sempre_online.py",
        "mamute_config_definitivo.json", 
        "web_app.py",
        "requirements.txt"
    ]
    
    missing_files = []
    
    for file_name in required_files:
        file_path = Path(file_name)
        if file_path.exists():
            print(f"✅ {file_name}")
        else:
            print(f"❌ {file_name} não encontrado")
            missing_files.append(file_name)
    
    if missing_files:
        print(f"⚠️ Arquivos faltando: {missing_files}")
        return False
    
    print("✅ Todos os arquivos necessários encontrados")
    return True

def test_chat_functionality(port=8000):
    """Testar funcionalidade básica do chat"""
    print("💬 Testando funcionalidade do chat...")
    
    try:
        # Testar endpoint de chat
        response = requests.post(
            f"http://localhost:{port}/chat",
            json={"message": "teste", "session_id": "test_session"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if "response" in data:
                print("✅ Chat respondendo normalmente")
                return True
            else:
                print("⚠️ Chat retornou resposta sem campo 'response'")
                return False
        else:
            print(f"⚠️ Chat retornou status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar chat: {e}")
        return False

def run_full_test():
    """Executar teste completo do sistema"""
    print("🧪 TESTE COMPLETO DO SISTEMA DEFINITIVO MAMUTE")
    print("="*60)
    
    test_results = []
    
    # 1. Testar arquivos de configuração
    result = test_config_files()
    test_results.append(("Arquivos de Configuração", result))
    
    # 2. Testar banco de dados
    result = test_database_connection()
    test_results.append(("Banco de Dados", result))
    
    # 3. Testar servidor web
    result = test_server_response()
    test_results.append(("Servidor Web", result))
    
    # 4. Se servidor estiver rodando, testar endpoints
    if test_results[-1][1]:  # Se servidor test passou
        result = test_api_endpoints()
        test_results.append(("Endpoints API", result))
        
        result = test_chat_functionality()
        test_results.append(("Funcionalidade Chat", result))
    
    # Resultado final
    print("\n" + "="*60)
    print("📊 RESULTADO DOS TESTES")
    print("="*60)
    
    all_passed = True
    
    for test_name, passed in test_results:
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"{test_name:25} {status}")
        if not passed:
            all_passed = False
    
    print("="*60)
    
    if all_passed:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("🚀 Sistema funcionando perfeitamente!")
        print("\n🌐 Acesse: http://localhost:8000")
    else:
        print("⚠️ ALGUNS TESTES FALHARAM")
        print("🔧 Verifique os erros acima e corrija")
    
    print("="*60)
    
    return all_passed

def main():
    """Função principal"""
    if len(sys.argv) > 1 and sys.argv[1] == "--server-only":
        # Apenas testar servidor se já estiver rodando
        test_server_response()
        test_api_endpoints()
        test_chat_functionality()
    else:
        # Teste completo
        run_full_test()
    
    input("\nPressione Enter para sair...")

if __name__ == "__main__":
    main()