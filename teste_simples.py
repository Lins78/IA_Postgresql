"""
Teste simples da API Mamute - sem interromper servidor
"""
import requests
import json
import time

def teste_simples():
    """Teste básico que não interfere com o servidor"""
    base_url = "http://localhost:8000"
    
    print("🔍 VERIFICANDO SERVIDOR MAMUTE...")
    
    try:
        # 1. Health check
        print("1. Testando conexão...")
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data['status']}")
            print(f"✅ Mamute: {data['mamute_name']}")
            print(f"✅ Database: {'Conectado' if data['database_connected'] else 'Desconectado'}")
        else:
            print(f"❌ Health check falhou: {response.status_code}")
            return False
            
        # 2. Testar página principal
        print("\\n2. Testando página principal...")
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ Página principal acessível")
        else:
            print(f"❌ Página principal falhou: {response.status_code}")
            
        # 3. Testar página de chat
        print("\\n3. Testando página de chat...")
        response = requests.get(f"{base_url}/chat", timeout=5)
        if response.status_code == 200:
            print("✅ Página de chat acessível")
        else:
            print(f"❌ Página de chat falhou: {response.status_code}")
            
        print("\\n" + "=" * 50)
        print("🎉 SERVIDOR MAMUTE FUNCIONANDO!")
        print("🌐 Acesse: http://localhost:8000")
        print("💬 Chat: http://localhost:8000/chat")
        print("📖 Docs: http://localhost:8000/docs")
        print("=" * 50)
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Servidor não está rodando em http://localhost:8000")
        print("💡 Execute: python servidor_estavel.py")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    teste_simples()