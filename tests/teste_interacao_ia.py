#!/usr/bin/env python3
"""
🔬 TESTE DE INTERAÇÃO COM A IA MAMUTE
Teste completo das funcionalidades de interação
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# Adicionar o diretório src ao path
ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / 'src'
APPS_DIR = SRC_DIR / 'apps'
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(APPS_DIR) not in sys.path:
    sys.path.insert(0, str(APPS_DIR))

def teste_sistema_basico():
    """Teste básico do sistema"""
    print("🔬 INICIANDO TESTE DE INTERAÇÃO COM MAMUTE")
    print("=" * 50)
    
    try:
        # Importar sistema principal
        from main import IAPostgreSQL
        
        print("✅ Sistema importado com sucesso")
        
        # Inicializar sistema
        ia_system = IAPostgreSQL()
        print("✅ Sistema inicializado")
        
        return ia_system
        
    except Exception as e:
        print(f"❌ Erro na inicialização: {e}")
        return None

def teste_chat_fallback():
    """Teste do sistema de chat com fallback local"""
    print("\n🎯 TESTANDO SISTEMA DE CHAT FALLBACK")
    print("-" * 40)
    
    try:
        from src.ai.fallback_chat import FallbackChatManager
        
        # Inicializar chat fallback
        fallback_chat = FallbackChatManager()
        print("✅ Sistema de fallback inicializado")
        
        # Testar conversas
        perguntas = [
            "Olá Mamute! Como você está?",
            "Quais são suas principais funcionalidades?",
            "Como você pode me ajudar com PostgreSQL?",
            "Explique sobre análise de dados"
        ]
        
        print("\n💬 CONVERSAS DE TESTE:")
        for i, pergunta in enumerate(perguntas, 1):
            print(f"\n{i}. 👤 Usuário: {pergunta}")
            
            try:
                resposta = fallback_chat.generate_response(pergunta)
                print(f"   🐘 Mamute: {resposta}")
                
            except Exception as e:
                print(f"   ❌ Erro: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no chat fallback: {e}")
        return False

def teste_conhecimento_local():
    """Teste da base de conhecimento local"""
    print("\n📚 TESTANDO BASE DE CONHECIMENTO")
    print("-" * 40)
    
    try:
        # Importar sistema de conhecimento
        from mamute_completo import MamuteCompleteAI
        
        mamute = MamuteCompleteAI()
        print("✅ Base de conhecimento carregada")
        
        # Mostrar algumas categorias disponíveis
        if hasattr(mamute, 'knowledge_base'):
            kb = mamute.knowledge_base
            print("\n📋 Categorias de conhecimento disponíveis:")
            for categoria in kb.keys():
                print(f"   • {categoria}")
                
            # Teste de consulta PostgreSQL
            if 'postgresql' in kb:
                print(f"\n🔍 Comandos PostgreSQL disponíveis:")
                pg_kb = kb['postgresql']
                for tipo, comandos in pg_kb.items():
                    print(f"   📁 {tipo}: {len(comandos) if isinstance(comandos, dict) else 'N/A'} itens")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na base de conhecimento: {e}")
        return False

def teste_funcionalidades_web():
    """Teste das funcionalidades web básicas"""
    print("\n🌐 TESTANDO FUNCIONALIDADES WEB")
    print("-" * 40)
    
    try:
        from web_app import app
        print("✅ App FastAPI carregado")
        
        # Verificar se as rotas existem
        rotas_esperadas = ["/", "/chat", "/api/chat", "/docs", "/health"]
        rotas_app = [route.path for route in app.routes if hasattr(route, 'path')]
        
        print("📍 Rotas disponíveis:")
        for rota in rotas_app[:10]:  # Mostrar primeiras 10
            status = "✅" if rota in rotas_esperadas else "📄"
            print(f"   {status} {rota}")
            
        if len(rotas_app) > 10:
            print(f"   ... e mais {len(rotas_app) - 10} rotas")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no sistema web: {e}")
        return False

def teste_metricas_sistema():
    """Teste das métricas do sistema"""
    print("\n📊 MÉTRICAS DO SISTEMA")
    print("-" * 40)
    
    print(f"🕐 Hora atual: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python: {sys.version.split()[0]}")
    print(f"📁 Diretório: {os.getcwd()}")
    
    # Verificar arquivos principais
    arquivos_principais = [
        "main.py", "web_app.py", "requirements.txt", 
        ".env", "README.md", "mamute_completo.py"
    ]
    
    print("\n📄 Arquivos do sistema:")
    for arquivo in arquivos_principais:
        if os.path.exists(arquivo):
            size = os.path.getsize(arquivo)
            print(f"   ✅ {arquivo} ({size:,} bytes)")
        else:
            print(f"   ❌ {arquivo} (não encontrado)")

def main():
    """Execução principal do teste"""
    print("🚀 INICIANDO BATERIA DE TESTES COMPLETA")
    print("=" * 60)
    
    resultados = {
        "sistema_basico": False,
        "chat_fallback": False,
        "conhecimento": False,
        "funcionalidades_web": False
    }
    
    # Executar testes
    resultados["chat_fallback"] = teste_chat_fallback()
    resultados["conhecimento"] = teste_conhecimento_local()
    resultados["funcionalidades_web"] = teste_funcionalidades_web()
    teste_metricas_sistema()
    
    # Relatório final
    print("\n" + "=" * 60)
    print("📋 RELATÓRIO FINAL DOS TESTES")
    print("=" * 60)
    
    testes_passaram = 0
    total_testes = len(resultados)
    
    for teste, resultado in resultados.items():
        status = "✅ PASSOU" if resultado else "❌ FALHOU"
        print(f"   {teste.replace('_', ' ').title()}: {status}")
        if resultado:
            testes_passaram += 1
    
    print(f"\n🎯 RESULTADO: {testes_passaram}/{total_testes} testes passaram")
    
    if testes_passaram == total_testes:
        print("🎉 TODOS OS TESTES PASSARAM! Sistema funcionando perfeitamente.")
    elif testes_passaram > 0:
        print("⚠️  Sistema parcialmente funcional. Alguns recursos estão operacionais.")
    else:
        print("🚫 Sistema com problemas. Verificar configurações.")
    
    print("\n🔧 PRÓXIMOS PASSOS:")
    if not resultados["sistema_basico"]:
        print("   1. Verificar conexão PostgreSQL")
    print("   2. Configurar chave OpenAI para IA completa")
    print("   3. Executar: python web_app.py para interface web")
    print("   4. Acessar: http://localhost:8000 para dashboard")

if __name__ == "__main__":
    main()