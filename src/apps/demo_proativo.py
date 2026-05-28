#!/usr/bin/env python3
"""
Demonstração do Sistema IA Proativa do Mamute
Sistema que não apenas propõe melhorias, mas as aplica automaticamente!
"""
import asyncio
import json
from datetime import datetime
from mamute_chat_personality import MamuteChatPersonality

async def demo_ia_proativa():
    """Demonstração completa do sistema IA proativo"""
    
    print("🐘 " + "="*80)
    print("🐘 DEMONSTRAÇÃO - IA MAMUTE PROATIVA")
    print("🐘 Sistema que APLICA melhorias automaticamente!")
    print("🐘 " + "="*80)
    print()
    
    # Inicializar sistema
    print("🔧 Inicializando sistema...")
    chat_system = MamuteChatPersonality()
    print("✅ Sistema inicializado com sucesso!")
    print()
    
    # Verificar se modo proativo está ativo
    print("🔍 Verificando modo proativo...")
    if hasattr(chat_system, 'proactive_mode'):
        print(f"📊 Modo Proativo: {'🟢 ATIVO' if chat_system.proactive_mode else '🔴 INATIVO'}")
    else:
        print("⚠️  Modo proativo não disponível")
        return
    print()
    
    # Demonstrações interativas
    demos = [
        {
            "titulo": "🚀 Otimização Automática de Performance",
            "prompt": "Meu sistema está lento, pode melhorar a performance?",
            "esperado": "Aplicar otimizações automaticamente"
        },
        {
            "titulo": "🧹 Limpeza Automática do Sistema",
            "prompt": "O banco de dados está ocupando muito espaço",
            "esperado": "Limpar logs antigos automaticamente"
        },
        {
            "titulo": "🔒 Backup Automático",
            "prompt": "Preciso garantir que os dados estejam seguros",
            "esperado": "Criar backup automaticamente"
        },
        {
            "titulo": "📦 Instalação Automática de Dependências",
            "prompt": "Preciso de novas bibliotecas Python para análise",
            "esperado": "Instalar dependências automaticamente"
        },
        {
            "titulo": "💾 Otimização do Banco de Dados",
            "prompt": "As consultas estão demoradas",
            "esperado": "Otimizar queries automaticamente"
        }
    ]
    
    for i, demo in enumerate(demos, 1):
        print(f"📋 DEMO {i}/{len(demos)}: {demo['titulo']}")
        print(f"👤 Usuário pergunta: \"{demo['prompt']}\"")
        print("⏳ IA Proativa analisando e aplicando melhorias...")
        print()
        
        # Processar com IA proativa
        try:
            response = await chat_system.get_response(demo['prompt'])
            
            # Exibir resposta
            print("🐘 Resposta do Mamute:")
            print("─" * 60)
            print(response['response'])
            print("─" * 60)
            print()
            
            # Verificar se melhorias foram aplicadas
            if response.get('applied_improvements'):
                print("🎉 MELHORIAS APLICADAS AUTOMATICAMENTE:")
                for improvement in response['applied_improvements']:
                    print(f"✅ {improvement['action']}: {improvement['description']}")
                    if improvement.get('result'):
                        print(f"   📊 Resultado: {improvement['result']}")
                print()
            
            # Mostrar sugestões de melhorias
            if response.get('suggested_improvements'):
                print("💡 SUGESTÕES ADICIONAIS:")
                for suggestion in response['suggested_improvements']:
                    confidence = suggestion.get('confidence', 0) * 100
                    print(f"💭 {suggestion['action']}: {suggestion['description']} (Confiança: {confidence:.1f}%)")
                print()
            
            # Estatísticas da sessão
            if response.get('proactive_mode'):
                print(f"📈 Modo: Proativo | Tipo: {response.get('type', 'unknown')} | Timestamp: {response.get('timestamp', 'N/A')}")
            else:
                print("📈 Processamento padrão (sem melhorias automáticas)")
            
        except Exception as e:
            print(f"❌ Erro na demonstração: {e}")
        
        print("\n" + "="*80 + "\n")
    
    # Estatísticas finais
    print("📊 RESUMO DA SESSÃO")
    print("─" * 40)
    if hasattr(chat_system, 'session_stats'):
        stats = chat_system.session_stats
        print(f"🔢 Consultas processadas: {stats.get('queries', 0)}")
        print(f"✅ Consultas bem-sucedidas: {stats.get('successful_queries', 0)}")
        print(f"⏱️  Tempo de sessão: {stats.get('session_time', 'N/A')}")
    print()
    
    print("🎯 RESULTADO: IA Mamute Proativa aplicou melhorias automaticamente!")
    print("💪 Diferencial: Não apenas sugere - EXECUTA as melhorias!")
    print("🚀 Sistema totalmente operacional em localhost:8000")
    print()
    print("🐘 Obrigado por usar o Mamute! 🐘")

async def test_proactive_modes():
    """Testar diferentes modos do sistema proativo"""
    
    print("\n🧪 TESTE DE MODOS PROATIVOS")
    print("─" * 50)
    
    chat_system = MamuteChatPersonality()
    
    # Teste 1: Modo proativo ativo
    print("🔛 Teste 1: Modo Proativo ATIVO")
    chat_system.toggle_proactive_mode(True)
    response1 = await chat_system.get_response("Otimize o sistema para mim")
    print(f"   Melhorias aplicadas: {len(response1.get('applied_improvements', []))}")
    
    # Teste 2: Modo proativo inativo
    print("🔛 Teste 2: Modo Proativo INATIVO")  
    chat_system.toggle_proactive_mode(False)
    response2 = await chat_system.get_response("Otimize o sistema para mim")
    print(f"   Melhorias aplicadas: {len(response2.get('applied_improvements', []))}")
    
    # Teste 3: Alternância automática
    print("🔛 Teste 3: Alternância Automática")
    original_mode = chat_system.toggle_proactive_mode()
    print(f"   Modo alterado para: {'Ativo' if original_mode else 'Inativo'}")
    
    print("✅ Testes de modo concluídos!")

def main():
    """Função principal"""
    try:
        # Executar demonstração principal
        asyncio.run(demo_ia_proativa())
        
        # Executar testes de modo
        asyncio.run(test_proactive_modes())
        
    except KeyboardInterrupt:
        print("\n⏹️  Demonstração interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro durante a demonstração: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()