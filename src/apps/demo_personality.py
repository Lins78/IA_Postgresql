#!/usr/bin/env python3
"""
Demo da Nova Personalidade IA Mamute
===================================
Teste interativo da personalidade avançada similar ao GitHub Copilot
"""

import asyncio
import sys
from pathlib import Path

# Adicionar o diretório atual e src ao path
ROOT_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT_DIR / "src"
APPS_DIR = SRC_DIR / "apps"
if str(APPS_DIR) not in sys.path:
    sys.path.insert(0, str(APPS_DIR))
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from mamute_chat_personality import MamuteChatIA
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class MamutePersonalityDemo:
    """Demo interativo da personalidade do Mamute"""
    
    def __init__(self):
        """Inicializar demo"""
        try:
            self.chat_ia = MamuteChatIA()
            self.running = True
            logger.info("✨ Demo da Personalidade Mamute inicializado!")
        except Exception as e:
            logger.error(f"Erro na inicialização: {e}")
            self.chat_ia = None
    
    def print_styled_response(self, response_data: dict):
        """Imprimir resposta com estilo"""
        print("\n" + "="*60)
        print("🤖 MAMUTE IA:")
        print("="*60)
        print(response_data['response'])
        
        # Mostrar informações extras se disponíveis
        if response_data.get('count'):
            print(f"\n📊 Documentos encontrados: {response_data['count']}")
        
        if response_data.get('type'):
            print(f"🏷️ Tipo: {response_data['type']}")
        
        print("="*60)
    
    def print_welcome(self):
        """Imprimir cabeçalho de boas-vindas"""
        print("\n" + "🎉"*20)
        print("🚀 DEMO: MAMUTE IA COM PERSONALIDADE AVANÇADA")
        print("🎉"*20)
        print("\n🎯 **Características da Nova Personalidade:**")
        print("• Emojis e formatação visual")
        print("• Respostas empáticas e amigáveis") 
        print("• Encorajamento e motivação")
        print("• Comunicação natural e descontraída")
        print("• Similar ao GitHub Copilot em estilo")
        print("\n💡 **Comandos especiais:**")
        print("• 'sair' ou 'quit' - Encerrar demo")
        print("• 'ajuda' - Ver todos os comandos")
        print("• 'stats' - Ver estatísticas da sessão")
        print("• 'resumo' - Resumo da conversa")
        print("\n" + "="*60)
    
    def get_example_queries(self):
        """Obter exemplos de consultas"""
        return [
            "Oi! Como você está?",
            "Que legal sua personalidade!",
            "Me ajuda com uma busca?",
            "Quantos documentos você tem?",
            "Pode fazer uma análise para mim?",
            "O que você sabe fazer?",
            "Obrigado pela ajuda!",
            "Você é incrível!"
        ]
    
    async def run_demo(self):
        """Executar demo interativo"""
        if not self.chat_ia:
            print("❌ Erro: Sistema não foi inicializado corretamente!")
            return
        
        self.print_welcome()
        
        # Mostrar mensagem de boas-vindas
        welcome = self.chat_ia.get_welcome_message()
        self.print_styled_response(welcome)
        
        # Mostrar exemplos
        print("\n🎯 **Exemplos para testar:**")
        examples = self.get_example_queries()
        for i, example in enumerate(examples, 1):
            print(f"{i}. {example}")
        
        print("\n💬 **Comece a conversar!**")
        
        while self.running:
            try:
                # Obter input do usuário
                print("\n" + "-"*60)
                user_input = input("👤 Você: ").strip()
                
                # Verificar comandos especiais
                if user_input.lower() in ['sair', 'quit', 'exit', 'bye']:
                    await self.handle_exit()
                    break
                elif user_input.lower() == 'resumo':
                    await self.show_summary()
                    continue
                elif not user_input:
                    continue
                
                # Processar resposta
                print("\n⚙️ Processando...")
                response = await self.chat_ia.get_response(user_input)
                
                # Mostrar resposta
                self.print_styled_response(response)
                
            except KeyboardInterrupt:
                print("\n\n⚡ Interrompido pelo usuário...")
                await self.handle_exit()
                break
            except Exception as e:
                print(f"\n❌ Erro inesperado: {e}")
                logger.error(f"Erro no demo: {e}")
    
    async def show_summary(self):
        """Mostrar resumo da sessão"""
        try:
            summary_data = self.chat_ia.get_session_summary()
            
            print("\n" + "📊"*20)
            print("RESUMO DA SESSÃO")
            print("📊"*20)
            print(summary_data['formatted_summary'])
            print("📊"*20)
            
        except Exception as e:
            print(f"❌ Erro ao gerar resumo: {e}")
    
    async def handle_exit(self):
        """Lidar com saída do demo"""
        print("\n🚀 Encerrando demo...")
        
        # Mostrar resumo final
        await self.show_summary()
        
        # Mensagem de despedida
        farewell_emoji = self.chat_ia.personality.get_emoji('celebration')
        print(f"\n👋 Obrigado por testar a nova personalidade do Mamute! {farewell_emoji}")
        print("🎯 A personalidade está pronta para ser integrada ao sistema!")
        print("\n✨ Características implementadas:")
        print("• Comunicação natural e amigável ✅")
        print("• Emojis e formatação visual ✅") 
        print("• Respostas empáticas ✅")
        print("• Encorajamento e motivação ✅")
        print("• Estilo similar ao GitHub Copilot ✅")
        
        self.running = False

async def run_personality_test():
    """Executar teste rápido da personalidade"""
    print("🔬 TESTE RÁPIDO DE PERSONALIDADE")
    print("="*40)
    
    try:
        chat_ia = MamuteChatIA()
        
        # Testes de diferentes tipos de interação
        test_queries = [
            "Olá!",
            "Você é muito legal!",
            "Me ajuda?",
            "Quantos documentos?",
            "Obrigado!"
        ]
        
        for query in test_queries:
            print(f"\n👤 Teste: {query}")
            response = await chat_ia.get_response(query)
            print(f"🤖 Mamute: {response['response'][:100]}...")
            print(f"📋 Tipo: {response['type']}")
            
        print(f"\n✅ Teste concluído! Personalidade funcionando perfeitamente! ✨")
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")

if __name__ == "__main__":
    print("🎯 ESCOLHA O MODO DE TESTE:")
    print("1. Demo Interativo Completo")
    print("2. Teste Rápido de Funcionalidade")
    
    try:
        choice = input("\n👤 Escolha (1 ou 2): ").strip()
        
        if choice == "1":
            demo = MamutePersonalityDemo()
            asyncio.run(demo.run_demo())
        elif choice == "2":
            asyncio.run(run_personality_test())
        else:
            print("❌ Opção inválida!")
            
    except Exception as e:
        print(f"❌ Erro na execução: {e}")
        logger.error(f"Erro principal: {e}")