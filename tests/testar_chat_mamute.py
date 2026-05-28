"""
Script para testar o sistema de chat do Mamute
"""
import requests
import json

def testar_chat_mamute():
    """Testa o sistema de chat via API"""
    
    print("🐘 TESTANDO SISTEMA DE CHAT DO MAMUTE")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8001"
    
    # 1. Iniciar sessão
    print("1️⃣ Iniciando sessão...")
    try:
        session_response = requests.post(f"{base_url}/session/start")
        if session_response.status_code == 200:
            session_data = session_response.json()
            session_id = session_data["session_id"]
            print(f"✅ Sessão criada: {session_id}")
        else:
            print(f"❌ Erro ao criar sessão: {session_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False
    
    # 2. Testar mensagens
    mensagens_teste = [
        "Oi Mamute!",
        "Como está o tempo em São Paulo?",
        "Como fazer um SELECT no PostgreSQL?", 
        "Explicar JOINs",
        "Quem é você?"
    ]
    
    for i, mensagem in enumerate(mensagens_teste, 1):
        print(f"\\n{i + 1}️⃣ Testando: '{mensagem}'")
        
        try:
            chat_data = {
                "message": mensagem,
                "session_id": session_id,
                "use_context": True
            }
            
            chat_response = requests.post(
                f"{base_url}/chat",
                json=chat_data,
                headers={"Content-Type": "application/json"}
            )
            
            if chat_response.status_code == 200:
                response_data = chat_response.json()
                resposta = response_data.get("response", "")
                tempo_resposta = response_data.get("response_time", 0)
                modo = response_data.get("mode", "normal")
                
                print(f"✅ Resposta ({modo}): {tempo_resposta:.2f}s")
                print(f"📝 {resposta[:100]}...")
                
            else:
                print(f"❌ Erro na resposta: {chat_response.status_code}")
                print(f"📄 Detalhes: {chat_response.text}")
                
        except Exception as e:
            print(f"❌ Erro na requisição: {e}")
    
    print(f"\\n" + "=" * 50)
    print("🎉 TESTE CONCLUÍDO!")
    print(f"🌐 Acesse: {base_url}/chat para testar manualmente")

if __name__ == "__main__":
    testar_chat_mamute()