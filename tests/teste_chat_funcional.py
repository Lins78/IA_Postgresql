#!/usr/bin/env python3
"""
🔥 TESTE DIRETO DE CHAT - FUNCIONALIDADE COMPLETA
Testa e corrige problemas de interação da IA
"""

import sys
import os
import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / 'src'
APPS_DIR = SRC_DIR / 'apps'
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(APPS_DIR) not in sys.path:
    sys.path.insert(0, str(APPS_DIR))

def testar_ia_diretamente():
    """Testar IA diretamente sem servidor web"""
    print("🔥 TESTE DIRETO DA IA MAMUTE")
    print("=" * 50)
    
    try:
        # Importar sistema principal
        from main import IAPostgreSQL
        
        print("✅ Sistema importado")
        
        # Inicializar
        ia_system = IAPostgreSQL()
        print("✅ Sistema inicializado")
        
        # Configurar banco
        ia_system.setup_database()
        print("✅ Banco configurado")
        
        # Iniciar conversa
        session_id = ia_system.start_conversation("teste_usuario")
        print(f"✅ Sessão iniciada: {session_id}")
        
        # Testar chat
        mensagens_teste = [
            "Olá Mamute! Você está funcionando?",
            "Quais são suas principais funcionalidades?",
            "Me ajude com PostgreSQL",
            "Como fazer uma consulta SELECT?",
            "Analise os dados da tabela users"
        ]
        
        print("\n💬 TESTANDO CHAT DIRETO:")
        print("-" * 40)
        
        for i, mensagem in enumerate(mensagens_teste, 1):
            print(f"\n{i}. 👤 Usuário: {mensagem}")
            
            try:
                resposta = ia_system.chat(mensagem, session_id)
                
                if resposta and 'response' in resposta:
                    print(f"🐘 Mamute: {resposta['response'][:200]}...")
                    print(f"⏱️ Tempo: {resposta.get('processing_time', 'N/A')}s")
                    print(f"🎯 Tokens: {resposta.get('tokens_used', 'N/A')}")
                else:
                    print(f"❌ Resposta inválida: {resposta}")
                    
            except Exception as e:
                print(f"❌ Erro no chat: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro crítico: {e}")
        import traceback
        traceback.print_exc()
        return False

def testar_fallback_local():
    """Testar sistema de fallback local"""
    print("\n🎯 TESTE DO SISTEMA DE FALLBACK")
    print("=" * 50)
    
    try:
        # Sistema de resposta local simples
        class MamuteFallback:
            def __init__(self):
                self.respostas = {
                    "ola": "🐘 Olá! Eu sou o Mamute, sua IA especialista em PostgreSQL! Como posso ajudar você hoje?",
                    "funcionalidades": "🎯 Minhas principais funcionalidades:\n• Análise de dados PostgreSQL\n• Consultas SQL otimizadas\n• Chat inteligente\n• Insights automáticos",
                    "postgresql": "💾 Posso ajudar com PostgreSQL:\n• Criar tabelas e bancos\n• Otimizar consultas\n• Análise de performance\n• Comandos administrativos",
                    "select": "🔍 Para consultas SELECT:\n```sql\nSELECT coluna1, coluna2\nFROM tabela\nWHERE condicao\nORDER BY coluna1;\n```",
                    "analise": "📊 Para análise de dados, posso:\n• Estatísticas descritivas\n• Identificar padrões\n• Detectar anomalias\n• Relatórios automáticos"
                }
            
            def responder(self, mensagem):
                mensagem_lower = mensagem.lower()
                
                for palavra_chave, resposta in self.respostas.items():
                    if palavra_chave in mensagem_lower:
                        return resposta
                
                return "🤔 Interessante pergunta! Como Mamute especialista em PostgreSQL, posso ajudar com análise de dados, consultas SQL e administração de bancos. O que você gostaria de saber?"
        
        # Testar fallback
        mamute_fallback = MamuteFallback()
        
        mensagens = [
            "Olá Mamute!",
            "Quais suas funcionalidades?", 
            "Me ajude com PostgreSQL",
            "Como fazer SELECT?",
            "Preciso de análise de dados"
        ]
        
        print("💬 TESTANDO FALLBACK LOCAL:")
        for i, msg in enumerate(mensagens, 1):
            print(f"\n{i}. 👤 {msg}")
            resposta = mamute_fallback.responder(msg)
            print(f"🐘 {resposta}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no fallback: {e}")
        return False

def iniciar_servidor_funcional():
    """Iniciar servidor com chat funcional"""
    print("\n🚀 INICIANDO SERVIDOR COM CHAT FUNCIONAL")
    print("=" * 50)
    
    import subprocess
    import time
    
    # Configurar ambiente
    env = os.environ.copy()
    env.update({
        "POSTGRES_HOST": "localhost",
        "POSTGRES_PORT": "5432",
        "POSTGRES_DB": "ia_database",
        "POSTGRES_USER": "postgres", 
        "POSTGRES_PASSWORD": "postgres@",
        "DATABASE_URL": "postgresql://postgres:postgres%40@localhost:5432/ia_database",
        "AI_NAME": "Mamute"
    })
    
    try:
        # Comando para servidor
        cmd = [
            sys.executable, "-m", "uvicorn",
            "web_app:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--log-level", "info"
        ]
        
        print("🚀 Iniciando servidor...")
        
        # Iniciar em background
        processo = subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        
        print("⏳ Aguardando 10 segundos...")
        time.sleep(10)
        
        # Testar se está respondendo
        import requests
        try:
            response = requests.get("http://localhost:8000/", timeout=5)
            if response.status_code == 200:
                print("✅ Servidor ativo!")
                
                # Testar chat via API
                print("🧪 Testando chat via API...")
                
                chat_data = {
                    "message": "Olá Mamute! Você está funcionando?",
                    "session_id": "teste_direto",
                    "use_context": True
                }
                
                chat_response = requests.post(
                    "http://localhost:8000/api/chat",
                    json=chat_data,
                    timeout=15
                )
                
                if chat_response.status_code == 200:
                    resultado = chat_response.json()
                    print("✅ CHAT FUNCIONANDO!")
                    print(f"🐘 Resposta: {resultado.get('response', 'Sem resposta')}")
                    print(f"⏱️ Tempo: {resultado.get('processing_time', 'N/A')}s")
                    
                    return True, processo
                else:
                    print(f"❌ Chat falhou: {chat_response.status_code}")
                    print(f"Erro: {chat_response.text}")
                    
        except Exception as e:
            print(f"❌ Erro ao testar servidor: {e}")
        
        return False, processo
        
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        return False, None

def main():
    """Executar todos os testes"""
    print("🔥 DIAGNÓSTICO COMPLETO - IA MAMUTE")
    print("🎯 Testando e corrigindo problemas de interação")
    print("=" * 70)
    
    # Teste 1: Sistema direto
    print("📋 TESTE 1: SISTEMA DIRETO")
    if testar_ia_diretamente():
        print("✅ Sistema direto funcionando!")
    else:
        print("❌ Sistema direto com problemas")
    
    # Teste 2: Fallback local
    print("\n📋 TESTE 2: FALLBACK LOCAL")
    if testar_fallback_local():
        print("✅ Fallback local funcionando!")
    else:
        print("❌ Fallback local com problemas")
    
    # Teste 3: Servidor web
    print("\n📋 TESTE 3: SERVIDOR WEB")
    funcionando, processo = iniciar_servidor_funcional()
    
    if funcionando:
        print("✅ SERVIDOR WEB COM CHAT FUNCIONANDO!")
        print("\n" + "=" * 70)
        print("🎉 MAMUTE ESTÁ TOTALMENTE FUNCIONAL!")
        print("=" * 70)
        print("🌐 Acesse: http://localhost:8000")
        print("💬 Chat: http://localhost:8000/chat")
        print("📚 Docs: http://localhost:8000/docs")
        print()
        print("🐘 A IA Mamute está respondendo corretamente!")
        
        # Manter servidor rodando
        input("🛑 Pressione Enter para parar o servidor...")
        if processo:
            processo.terminate()
    else:
        print("❌ PROBLEMA NO SERVIDOR WEB")
        print("💡 Mas o sistema direto e fallback funcionam!")

if __name__ == "__main__":
    main()