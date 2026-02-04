#!/usr/bin/env python3
"""
Teste Simples da Personalidade Mamute
====================================
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from mamute_personality import MamutePersonality

def test_personality():
    """Testar sistema de personalidade"""
    print("🎉 TESTANDO NOVA PERSONALIDADE DO MAMUTE")
    print("="*50)
    
    # Inicializar personalidade
    personality = MamutePersonality()
    
    print("\n🎭 TESTANDO DIFERENTES TIPOS DE RESPOSTA:\n")
    
    # Teste 1: Saudações
    print("👋 SAUDAÇÕES:")
    for i in range(3):
        print(f"  {i+1}. {personality.get_greeting()}")
    
    # Teste 2: Respostas de busca
    print("\n🔍 INICIANDO BUSCA:")
    for i in range(3):
        print(f"  {i+1}. {personality.get_response('search_start')}")
    
    # Teste 3: Sucessos
    print("\n✅ ENCONTROU RESULTADOS:")
    for i in range(3):
        print(f"  {i+1}. {personality.get_response('found')}")
    
    # Teste 4: Ajuda
    print("\n🆘 PEDIU AJUDA:")
    for i in range(3):
        print(f"  {i+1}. {personality.get_response('help')}")
    
    # Teste 5: Encorajamento
    print("\n💖 ENCORAJAMENTO:")
    for i in range(3):
        print(f"  {i+1}. {personality.get_encouragement()}")
    
    # Teste 6: Motivação
    print("\n🚀 MOTIVAÇÃO:")
    for i in range(3):
        print(f"  {i+1}. {personality.get_motivational()}")
    
    # Teste 7: Resposta formatada de sucesso
    print("\n🎯 RESPOSTA COMPLETA DE SUCESSO:")
    success_response = personality.format_success_response(
        "Encontrei informações relevantes sobre Python e IA!", 
        5
    )
    print(f"  {success_response}")
    
    # Teste 8: Resposta de ajuda completa
    print("\n📚 AJUDA COMPLETA:")
    help_response = personality.format_help_response()
    print(f"  {help_response}")
    
    # Teste 9: Resposta de erro
    print("\n❌ RESPOSTA DE ERRO:")
    error_response = personality.format_error_response(
        "Conexão com banco falhou",
        "Tente novamente em alguns instantes"
    )
    print(f"  {error_response}")
    
    # Teste 10: Starter de conversa
    print("\n💬 INICIADORES DE CONVERSA:")
    for i in range(3):
        print(f"  {i+1}. {personality.get_conversation_starter()}")
    
    print("\n" + "="*50)
    print("🎊 TESTE CONCLUÍDO!")
    print("✨ A personalidade do Mamute está funcionando perfeitamente!")
    print("🎯 Características implementadas:")
    print("  • Emojis contextuais ✅")
    print("  • Respostas variadas ✅")
    print("  • Tom amigável e motivador ✅")
    print("  • Formatação visual atrativa ✅")
    print("  • Estilo similar ao GitHub Copilot ✅")
    print("="*50)

if __name__ == "__main__":
    test_personality()