"""
Teste das correções do sistema de consultas do Mamute
"""
import requests
import json

def testar_consultas_banco():
    """Testa consultas específicas ao banco de dados"""
    
    print("🐘 TESTANDO CONSULTAS REAIS AO BANCO")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8001"
    
    # 1. Iniciar sessão
    print("1️⃣ Iniciando sessão...")
    try:
        session_response = requests.post(f"{base_url}/session/start")
        if session_response.status_code == 200:
            session_data = session_response.json()
            session_id = session_data["session_id"]
            print(f"✅ Sessão criada: {session_id[:8]}...")
        else:
            print(f"❌ Erro ao criar sessão: {session_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False
    
    # 2. Testar consultas específicas
    consultas_teste = [
        "Quantos bancos de dados existem no postgresql e quais os nomes?",
        "Quais tabelas existem no banco atual?", 
        "Qual o tamanho das tabelas?",
        "Estrutura da tabela documents"
    ]
    
    for i, consulta in enumerate(consultas_teste, 1):
        print(f"\\n{i + 1}️⃣ Testando: '{consulta}'")
        
        try:
            chat_data = {
                "message": consulta,
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
                
                print(f"✅ Resposta em {tempo_resposta:.2f}s:")
                print(f"📝 {resposta[:200]}...")
                
                # Verificar se contém dados reais do banco
                if any(keyword in resposta.lower() for keyword in ['ia_database', 'documents', 'conversations']):
                    print("🎯 Contém dados reais do banco!")
                else:
                    print("⚠️ Resposta parece genérica")
                
            else:
                print(f"❌ Erro na resposta: {chat_response.status_code}")
                
        except Exception as e:
            print(f"❌ Erro na requisição: {e}")
    
    print(f"\\n" + "=" * 50)
    print("🎉 TESTE DE CONSULTAS CONCLUÍDO!")

if __name__ == "__main__":
    testar_consultas_banco()