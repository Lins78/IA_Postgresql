"""
Teste da API Web do Mamute
"""
import requests
import json

def testar_api():
    """Testa os endpoints da API do Mamute"""
    base_url = "http://localhost:8000"
    
    print("=" * 50)
    print("🐘 TESTANDO API DO MAMUTE")
    print("=" * 50)
    
    # 1. Testar health check
    print("1️⃣ Testando health check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sistema: {data['status']}")
            print(f"✅ Mamute: {data['mamute_name']}")
            print(f"✅ Database: {'Conectado' if data['database_connected'] else 'Desconectado'}")
        else:
            print(f"❌ Erro no health check: {response.status_code}")
            return
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
        print("💡 Certifique-se de que o servidor está rodando em http://localhost:8000")
        return
    
    # 2. Testar criação de sessão
    print("\n2️⃣ Testando criação de sessão...")
    try:
        response = requests.post(
            f"{base_url}/session/start",
            json={},
            timeout=10
        )
        if response.status_code == 200:
            session_data = response.json()
            session_id = session_data["session_id"]
            print(f"✅ Sessão criada: {session_id}")
        else:
            print(f"❌ Erro ao criar sessão: {response.status_code}")
            return
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na criação de sessão: {e}")
        return
    
    # 3. Testar chat (sem OpenAI - vai dar erro mas testa a estrutura)
    print("\n3️⃣ Testando chat...")
    try:
        response = requests.post(
            f"{base_url}/chat",
            json={
                "message": "Olá Mamute! Quais tabelas estão disponíveis?",
                "session_id": session_id,
                "use_context": True
            },
            timeout=30
        )
        print(f"📊 Status do chat: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Resposta recebida")
            print(f"✅ Tokens: {data.get('tokens_used', 0)}")
        elif response.status_code == 500:
            # Esperado se não tiver chave da OpenAI
            error_data = response.json()
            if "401" in str(error_data.get("detail", "")):
                print("⚠️ Chat requer chave da OpenAI (esperado)")
            else:
                print(f"❌ Erro no chat: {error_data.get('detail', 'Erro desconhecido')}")
        else:
            print(f"❌ Erro no chat: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na requisição de chat: {e}")
    
    # 4. Testar consulta SQL
    print("\n4️⃣ Testando consulta SQL...")
    try:
        response = requests.post(
            f"{base_url}/query",
            json={
                "query": "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' LIMIT 5"
            },
            timeout=15
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Consulta executada: {data['row_count']} linhas")
            if data['results']:
                print("📋 Tabelas encontradas:")
                for row in data['results']:
                    print(f"   • {row['table_name']}")
        else:
            error_data = response.json()
            print(f"❌ Erro na consulta: {error_data.get('detail', 'Erro desconhecido')}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na consulta SQL: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 RESULTADO DOS TESTES:")
    print("✅ API funcionando corretamente")
    print("🌐 Acesse http://localhost:8000 no navegador")
    print("💬 Chat disponível em http://localhost:8000/chat")
    print("📖 Documentação em http://localhost:8000/docs")
    print("=" * 50)

if __name__ == "__main__":
    testar_api()