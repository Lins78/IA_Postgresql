#!/usr/bin/env python3
"""
🧪 TESTE DO SISTEMA DE MELHORIAS AUTOMÁTICAS NO CHAT
Teste para verificar se o sistema detecta e aplica melhorias quando solicitado via chat
"""

import requests
import json
import time

def testar_melhorias_automaticas():
    """Testa se o sistema aplica melhorias quando solicitado"""
    
    # URL do servidor
    base_url = "http://localhost:8001"
    
    # Verificar se servidor está ativo
    try:
        health_response = requests.get(f"{base_url}/health", timeout=5)
        if health_response.status_code != 200:
            print("❌ Servidor não está respondendo")
            return False
    except:
        print("❌ Não foi possível conectar ao servidor")
        return False
    
    print("✅ Servidor está online")
    
    # Mensagens para testar detecção de melhorias
    mensagens_teste = [
        "Aplique as melhorias no banco de dados autoprime",
        "Execute as sugestões de otimização",
        "Aplique as melhorias automáticas",
        "Execute vacuum analyze no banco",
        "Faça backup do banco de dados"
    ]
    
    for i, mensagem in enumerate(mensagens_teste, 1):
        print(f"\n🧪 Teste {i}/5: {mensagem}")
        
        # Enviar mensagem de chat
        chat_data = {
            "message": mensagem,
            "session_id": f"teste_melhorias_{int(time.time())}"
        }
        
        try:
            response = requests.post(
                f"{base_url}/chat", 
                json=chat_data, 
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                resposta = result.get("response", "")
                
                # Verificar se melhorias foram aplicadas
                if any(palavra in resposta.lower() for palavra in 
                      ["melhorias aplicadas", "vacuum", "backup", "otimizadas", "sucesso"]):
                    print(f"✅ Melhorias detectadas e aplicadas!")
                    print(f"   Resposta: {resposta[:100]}...")
                else:
                    print(f"⚠️ Resposta sem indicação de melhorias aplicadas")
                    print(f"   Resposta: {resposta[:100]}...")
                    
            else:
                print(f"❌ Erro na requisição: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Erro ao enviar mensagem: {e}")
        
        time.sleep(2)
    
    # Teste do endpoint direto de melhorias
    print(f"\n🧪 Teste do endpoint direto de melhorias")
    try:
        response = requests.post(
            f"{base_url}/apply-improvements", 
            json={"database": "ia_database"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Endpoint de melhorias funcionando!")
            print(f"   Status: {result.get('status', 'N/A')}")
            print(f"   Melhorias: {result.get('melhorias_aplicadas', 'N/A')}")
        else:
            print(f"❌ Erro no endpoint de melhorias: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro ao testar endpoint: {e}")
    
    print("\n🏁 Teste concluído!")

if __name__ == "__main__":
    print("🚀 INICIANDO TESTE DE MELHORIAS AUTOMÁTICAS")
    print("=" * 60)
    testar_melhorias_automaticas()