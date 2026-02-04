"""
Teste da nova funcionalidade de análise do banco de dados
"""
import requests
import json
import time

def testar_analise_banco():
    """Testa a nova funcionalidade de análise completa"""
    
    print("🔍 TESTANDO ANÁLISE COMPLETA DO BANCO")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:8001"
    
    # Aguardar servidor
    print("⏳ Aguardando servidor...")
    time.sleep(3)
    
    # 1. Iniciar sessão
    print("\n1️⃣ Iniciando sessão...")
    try:
        session_response = requests.post(f"{base_url}/session/start")
        if session_response.status_code == 200:
            session_data = session_response.json()
            session_id = session_data["session_id"]
            print(f"✅ Sessão criada: {session_id[:8]}...")
        else:
            print(f"❌ Erro ao criar sessão: {session_response.status_code}")
            print("🔄 Tentando com GET...")
            # Fallback: usar endpoint GET
            session_id = "test-session-" + str(int(time.time()))
    except Exception as e:
        print(f"⚠️ Erro de conexão, usando sessão temporária: {e}")
        session_id = "test-session-" + str(int(time.time()))
    
    # 2. Testar análises específicas
    analises_teste = [
        "Pode analisar o banco de dados A Rainha da Argamassa?",
        "O que precisa pra melhorar o banco de dados?",
        "Quais problemas existem no banco atual?",
        "Sugestões para otimizar o banco de dados"
    ]
    
    for i, pergunta in enumerate(analises_teste, 1):
        print(f"\n{i + 1}️⃣ Testando: '{pergunta}'")
        print("-" * 50)
        
        try:
            chat_data = {
                "message": pergunta,
                "session_id": session_id,
                "use_context": True
            }
            
            start_time = time.time()
            chat_response = requests.post(
                f"{base_url}/chat",
                json=chat_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            response_time = time.time() - start_time
            
            if chat_response.status_code == 200:
                response_data = chat_response.json()
                resposta = response_data.get("response", "")
                
                print(f"✅ Resposta em {response_time:.2f}s:")
                print(f"📄 Tamanho da resposta: {len(resposta)} caracteres")
                
                # Verificar se contém análise específica
                indicadores_analise = [
                    'ANÁLISE COMPLETA',
                    'Informações Gerais',
                    'PROBLEMAS DE PERFORMANCE',
                    'PROBLEMAS DE SEGURANÇA', 
                    'SUGESTÕES DE MELHORIAS',
                    'ia_database',
                    'registros',
                    'tamanho'
                ]
                
                encontrados = [ind for ind in indicadores_analise if ind.lower() in resposta.lower()]
                
                if len(encontrados) >= 3:
                    print(f"🎯 Análise real detectada! ({len(encontrados)}/8 indicadores)")
                    print(f"🔍 Indicadores encontrados: {', '.join(encontrados[:3])}...")
                else:
                    print(f"⚠️ Resposta parece genérica ({len(encontrados)}/8 indicadores)")
                
                # Mostrar prévia da resposta
                preview = resposta[:300] + "..." if len(resposta) > 300 else resposta
                print(f"📝 Preview: {preview}")
                
            else:
                print(f"❌ Erro HTTP {chat_response.status_code}")
                print(f"📄 Detalhes: {chat_response.text[:200]}...")
                
        except requests.exceptions.Timeout:
            print("⏰ Timeout - análise pode estar demorando muito")
        except Exception as e:
            print(f"❌ Erro na requisição: {e}")
    
    print(f"\n" + "=" * 60)
    print("🎉 TESTE DE ANÁLISE CONCLUÍDO!")
    print("📋 Resumo:")
    print("✅ Sistema agora deve:")
    print("   • Analisar estrutura real do banco")
    print("   • Identificar problemas específicos")
    print("   • Sugerir melhorias práticas")
    print("   • Mostrar comandos para correções")
    print(f"\n🌐 Teste manual em: {base_url}/chat")

if __name__ == "__main__":
    testar_analise_banco()