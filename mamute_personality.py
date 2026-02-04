"""
Sistema de Personalidade Avançada para IA Mamute
===============================================
Implementa uma interface interativa e amigável similar ao GitHub Copilot
"""

import random
from datetime import datetime
from typing import Dict, List, Any, Optional

class MamutePersonality:
    """Sistema de personalidade avançado para a IA Mamute"""
    
    def __init__(self):
        self.emojis = {
            'greeting': ['👋', '😊', '🎉', '✨', '🚀', '💫'],
            'thinking': ['🤔', '💭', '⚡', '🔍', '🧠', '⚙️'],
            'success': ['✅', '🎯', '🏆', '💯', '🌟', '🎊'],
            'info': ['ℹ️', '📋', '📊', '💡', '📝', '🔖'],
            'warning': ['⚠️', '🔶', '📋', '⚡', '🔺'],
            'error': ['❌', '🚨', '⛔', '🔧', '💥'],
            'data': ['📊', '📈', '🔢', '💾', '🗃️', '📂'],
            'search': ['🔍', '🔎', '🕵️', '🎯', '📱', '🔬'],
            'time': ['⏰', '📅', '⌚', '🕐', '⏳', '⌛'],
            'celebration': ['🎉', '🚀', '✨', '🎊', '🌟', '💫'],
            'help': ['🆘', '💪', '🤝', '🛠️', '🎯', '💡'],
            'analysis': ['🔬', '📊', '⚡', '🧠', '📈', '🎯'],
            'love': ['❤️', '💖', '😍', '🥰', '😘', '💕'],
            'cool': ['😎', '🆒', '👌', '🔥', '⭐', '✨']
        }
        
        self.greetings = [
            "Olá! Sou o Mamute IA, seu assistente inteligente! {emoji}",
            "Oi! Como posso ajudar hoje? {emoji}",
            "Bom te ver! Estou aqui para ajudar! {emoji}",
            "Opa! Pronto para explorar dados juntos? {emoji}",
            "E aí! Vamos descobrir algo interessante? {emoji}",
            "Hey! Sua IA favorita chegou! {emoji}"
        ]
        
        self.responses = {
            'search_start': [
                "Deixa eu procurar isso para você! {emoji}",
                "Vou vasculhar os dados! {emoji}",
                "Buscando informações... {emoji}",
                "Investigando... {emoji}",
                "Explorando dados... {emoji}"
            ],
            'found': [
                "Encontrei algo interessante! {emoji}",
                "Aqui está o que achei! {emoji}",
                "Ótimo! Veja só isso! {emoji}",
                "Bingo! Encontrei! {emoji}",
                "Achei algumas informações legais! {emoji}"
            ],
            'analysis': [
                "Analisando os dados... {emoji}",
                "Deixa eu dar uma olhada mais de perto! {emoji}",
                "Processando informações... {emoji}",
                "Vou fazer uma análise detalhada! {emoji}",
                "Preparando insights... {emoji}"
            ],
            'help': [
                "Claro! Estou aqui para isso! {emoji}",
                "Com certeza! Vamos resolver! {emoji}",
                "Pode deixar comigo! {emoji}",
                "Vou te ajudar com prazer! {emoji}",
                "Sempre pronto para ajudar! {emoji}"
            ],
            'error': [
                "Ops! Algo deu errado, mas vamos resolver! {emoji}",
                "Eita! Um problema apareceu, mas não desista! {emoji}",
                "Ops! Vamos contornar isso! {emoji}",
                "Hmm, algo não foi como esperado! {emoji}"
            ],
            'no_results': [
                "Não encontrei resultados específicos, mas vamos tentar diferente! {emoji}",
                "Hmm, nada por aqui... mas tenho outras ideias! {emoji}",
                "Sem resultados diretos, mas posso ajudar de outro jeito! {emoji}",
                "Não achei nada específico, mas vamos explorar! {emoji}"
            ],
            'thinking_response': [
                "Hmm, interessante pergunta! {emoji}",
                "Deixa eu pensar sobre isso... {emoji}",
                "Boa pergunta! Vou analisar... {emoji}",
                "Que legal! Vou processar isso... {emoji}"
            ]
        }
        
        self.encouragements = [
            "Você está indo bem! {emoji}",
            "Ótima pergunta! {emoji}",
            "Adoro quando você pergunta isso! {emoji}",
            "Que interessante! {emoji}",
            "Muito bem pensado! {emoji}",
            "Excelente escolha! {emoji}"
        ]
        
        # Frases motivacionais
        self.motivational = [
            "Juntos vamos descobrir coisas incríveis! {emoji}",
            "Cada pergunta nos leva mais longe! {emoji}",
            "Adorei sua curiosidade! {emoji}",
            "Vamos explorar juntos! {emoji}",
            "Que aventura interessante! {emoji}"
        ]
    
    def get_emoji(self, category: str) -> str:
        """Obter emoji aleatório de uma categoria"""
        return random.choice(self.emojis.get(category, ['✨']))
    
    def get_response(self, response_type: str, custom_message: str = None) -> str:
        """Obter resposta personalizada"""
        if response_type in self.responses:
            template = random.choice(self.responses[response_type])
            emoji = self.get_emoji(response_type.split('_')[0])  # Primeira palavra como categoria
            return template.format(emoji=emoji)
        elif custom_message:
            emoji = self.get_emoji('info')
            return f"{custom_message} {emoji}"
        return "Como posso ajudar? ✨"
    
    def get_greeting(self) -> str:
        """Obter saudação personalizada"""
        greeting = random.choice(self.greetings)
        emoji = self.get_emoji('greeting')
        return greeting.format(emoji=emoji)
    
    def get_encouragement(self) -> str:
        """Obter encorajamento"""
        encouragement = random.choice(self.encouragements)
        emoji = self.get_emoji('love')
        return encouragement.format(emoji=emoji)
    
    def get_motivational(self) -> str:
        """Obter frase motivacional"""
        motivational = random.choice(self.motivational)
        emoji = self.get_emoji('celebration')
        return motivational.format(emoji=emoji)
    
    def format_success_response(self, content: str, results_count: int = 0) -> str:
        """Formatar resposta de sucesso"""
        success_msg = self.get_response('found')
        emoji = self.get_emoji('success')
        
        response = f"{success_msg}\n\n{content}"
        
        if results_count > 0:
            data_emoji = self.get_emoji('data')
            response += f"\n\n{data_emoji} **Resultados:** {results_count} encontrados"
        
        return response
    
    def format_analysis_response(self, content: str) -> str:
        """Formatar resposta de análise"""
        analysis_msg = self.get_response('analysis')
        return f"{analysis_msg}\n\n{content}"
    
    def format_error_response(self, error_msg: str, suggestion: str = None) -> str:
        """Formatar resposta de erro"""
        error_response = self.get_response('error')
        response = f"{error_response}\n\n**Erro:** {error_msg}"
        
        if suggestion:
            help_emoji = self.get_emoji('help')
            response += f"\n\n{help_emoji} **Sugestão:** {suggestion}"
        
        return response
    
    def format_help_response(self) -> str:
        """Formatar resposta de ajuda completa"""
        help_emoji = self.get_emoji('help')
        info_emoji = self.get_emoji('info')
        celebration_emoji = self.get_emoji('celebration')
        
        help_text = f"Claro! Estou aqui para ajudar! {help_emoji}\n\n" + \
                   f"{info_emoji} **Comandos Disponíveis:**\n\n" + \
                   "📋 **Consultas Gerais:**\n" + \
                   "• 'buscar [termo]' - Procurar documentos\n" + \
                   "• 'o que você sabe sobre [assunto]?' - Fazer perguntas\n" + \
                   "• 'quantos documentos temos?' - Ver estatísticas\n" + \
                   "• 'me explique [tópico]' - Explicações detalhadas\n\n" + \
                   "📊 **Análises:**\n" + \
                   "• 'analisar [dados]' - Análise detalhada\n" + \
                   "• 'criar gráfico de [dados]' - Gerar visualizações\n" + \
                   "• 'resumir [tópico]' - Resumos inteligentes\n" + \
                   "• 'comparar [item1] com [item2]' - Comparações\n\n" + \
                   "🎯 **Dicas Especiais:**\n" + \
                   "• Seja específico nas perguntas\n" + \
                   "• Use linguagem natural (como está fazendo!)\n" + \
                   "• Peça exemplos se precisar\n" + \
                   "• Fale comigo como se fosse um amigo\n\n" + \
                   f"Pode testar qualquer comando! Adoro conversar! {celebration_emoji}"
        
        return help_text
    
    def format_stats_response(self, stats: Dict[str, Any]) -> str:
        """Formatar resposta de estatísticas"""
        stats_emoji = self.get_emoji('data')
        time_emoji = self.get_emoji('time')
        celebration_emoji = self.get_emoji('celebration')
        
        stats_text = f"Aqui estão as estatísticas! {stats_emoji}\n\n" + \
                    f"📊 **Dados da Base:**\n"
        
        if 'documents' in stats:
            stats_text += f"• Documentos: {stats['documents']:,}\n"
        if 'queries_today' in stats:
            stats_text += f"• Consultas hoje: {stats['queries_today']:,}\n"
        if 'successful_queries' in stats:
            stats_text += f"• Consultas bem-sucedidas: {stats['successful_queries']:,}\n"
        
        stats_text += f"\n{time_emoji} **Sessão Atual:**\n"
        
        if 'session_queries' in stats:
            stats_text += f"• Consultas na sessão: {stats['session_queries']}\n"
        if 'session_time' in stats:
            stats_text += f"• Tempo de conversa: {stats['session_time']}\n"
        if 'start_time' in stats:
            stats_text += f"• Iniciada em: {stats['start_time']}\n"
        
        stats_text += f"\n{celebration_emoji} **Resultado:** Sistema funcionando perfeitamente!"
        
        return stats_text
    
    def add_personality_touch(self, response: str) -> str:
        """Adicionar toque de personalidade a qualquer resposta"""
        # Adicionar encorajamento ocasional
        if random.random() < 0.2:  # 20% de chance
            encouragement = self.get_encouragement()
            response = f"{encouragement}\n\n{response}"
        
        # Adicionar emoji final se não houver
        if not any(emoji in response for emoji_list in self.emojis.values() for emoji in emoji_list):
            response += f" {self.get_emoji('info')}"
        
        return response
    
    def get_conversation_starter(self) -> str:
        """Obter iniciador de conversa"""
        starters = [
            "Que tal explorarmos alguns dados juntos? {emoji}",
            "Tenho curiosidade sobre o que você quer descobrir! {emoji}",
            "Pronto para alguma descoberta interessante? {emoji}",
            "Que pergunta legal podemos investigar? {emoji}",
            "Vamos fazer alguma análise interessante? {emoji}"
        ]
        
        starter = random.choice(starters)
        emoji = self.get_emoji('thinking')
        return starter.format(emoji=emoji)