#!/usr/bin/env python3
"""
🧪 Teste da correção de análise geral de bancos de dados
"""
import requests
import json

def testar_analise_geral():
    """Testa se o sistema agora entende pedidos de análise geral"""
    
    url = "http://localhost:8001/chat"
    
    # Teste 1: Análise geral de todos os bancos
    mensagem_teste = "Analise todos os bancos de dados existentes no meu postgresql"
    
    data = {
        "message": mensagem_teste,
        "session_id": "teste_analise_geral"
    }
    
    try:
        print("🧪 Testando análise geral de bancos...")
        print(f"📝 Mensagem: '{mensagem_teste}'")
        
        response = requests.post(url, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            resposta = result.get("response", "")
            
            print("✅ Resposta recebida!")
            print(f"📄 Início da resposta: {resposta[:200]}...")
            
            # Verificar se não está mais tratando como nome de banco específico
            if "não encontrado" in resposta and "todos os bancos de dados existentes no meu postgresql" in resposta:
                print("❌ ERRO: Ainda está interpretando como nome de banco específico!")
                return False
            elif "ANÁLISE COMPLETA DE TODOS OS BANCOS" in resposta or "Total de bancos" in resposta:
                print("✅ SUCESSO: Agora está fazendo análise geral corretamente!")
                return True
            else:
                print("⚠️ Resultado inesperado - verificar resposta completa")
                print(f"Resposta completa: {resposta}")
                return False
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

if __name__ == "__main__":
    print("🚀 TESTANDO CORREÇÃO DA ANÁLISE GERAL")
    print("=" * 50)
    
    sucesso = testar_analise_geral()
    
    print("=" * 50)
    if sucesso:
        print("🎉 TESTE PASSOU! Correção funcionou!")
    else:
        print("😞 TESTE FALHOU! Precisa de mais ajustes.")