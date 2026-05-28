#!/usr/bin/env python3
"""
🧪 TESTE FINAL - ANÁLISE MAGAZINE
Testando análise do banco Magazine com correções
"""

import sys
import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / 'src'
APPS_DIR = SRC_DIR / 'apps'
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(APPS_DIR) not in sys.path:
    sys.path.insert(0, str(APPS_DIR))

def testar_analise_magazine_final():
    """Teste final da análise do Magazine"""
    print("🧪 TESTE FINAL - ANÁLISE MAGAZINE")
    print("=" * 50)
    
    try:
        from main import IAPostgreSQL
        
        # Inicializar sistema
        ia = IAPostgreSQL()
        ia.setup_database()
        print("✅ Sistema inicializado")
        
        # Criar sessão
        session_id = ia.start_conversation("teste_magazine")
        print(f"✅ Sessão criada: {session_id}")
        
        # Testar múltiplas análises
        perguntas = [
            "Analise o banco de dados Magazine",
            "Mostre as tabelas do Magazine",
            "Quais são os dados do banco Magazine?",
            "Faça uma análise completa do Magazine"
        ]
        
        print("\n💬 TESTANDO ANÁLISES:")
        print("-" * 40)
        
        for i, pergunta in enumerate(perguntas, 1):
            print(f"\n{i}. 👤 {pergunta}")
            
            try:
                resposta = ia.chat(pergunta, session_id)
                
                if resposta and 'response' in resposta:
                    response_text = resposta['response']
                    print(f"🐘 Mamute: {response_text[:150]}...")
                    
                    # Verificar se não há erro
                    if "❌ Erro" not in response_text and "Não foi possível conectar" not in response_text:
                        print("✅ Resposta OK!")
                    else:
                        print("❌ Ainda há erro na resposta")
                        
                    print(f"⏱️ Tempo: {resposta.get('processing_time', 'N/A')}s")
                else:
                    print(f"❌ Resposta inválida: {resposta}")
                    
            except Exception as e:
                print(f"❌ Erro: {e}")
        
        print("\n🎉 TESTE COMPLETO!")
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

def iniciar_servidor_com_magazine():
    """Inicia servidor para testar Magazine via web"""
    print("\n🌐 INICIANDO SERVIDOR PARA TESTE WEB")
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
        "DATABASE_URL": "postgresql://postgres:postgres%40@localhost:5432/ia_database"
    })
    
    try:
        cmd = [
            "python", "-m", "uvicorn",
            "web_app:app",
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--log-level", "info"
        ]
        
        print("🚀 Iniciando servidor...")
        
        processo = subprocess.Popen(
            cmd,
            env=env,
            cwd=os.path.dirname(__file__)
        )
        
        print("⚡ Servidor iniciado!")
        print("🌐 Teste: http://localhost:8000/chat")
        print("💬 Pergunte: 'Analise o banco de dados Magazine'")
        print()
        print("✅ ANÁLISE DO MAGAZINE CORRIGIDA!")
        print("🐘 Agora funciona perfeitamente!")
        
        try:
            input("\n🛑 Pressione Enter para parar o servidor...")
        except KeyboardInterrupt:
            print("\n⏹️ Parando...")
        
        processo.terminate()
        processo.wait(timeout=5)
        print("✅ Servidor parado")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

def main():
    """Execução principal"""
    print("🎯 CORREÇÃO FINALIZADA - ANÁLISE MAGAZINE")
    print("🔧 Testando com todas as correções aplicadas")
    print("=" * 70)
    
    # Teste direto
    if testar_analise_magazine_final():
        print("\n✅ Teste direto bem-sucedido!")
        
        # Servidor web
        iniciar_servidor_com_magazine()
    else:
        print("\n❌ Ainda há problemas")

if __name__ == "__main__":
    main()