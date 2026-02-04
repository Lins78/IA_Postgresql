"""
Sistema de Chat IA Mamute com Personalidade Avançada
===================================================
Interface amigável e interativa similar ao GitHub Copilot
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

from src.database.connection import DatabaseManager
from src.utils.config import Config
from src.utils.logger import setup_logger
from src.ai.embeddings import EmbeddingManager
from src.ai.agent import AIAgent
from src.ai.fallback_chat import FallbackChatSystem
from mamute_personality import MamutePersonality

class MamuteChatIA:
    """Sistema de Chat IA Mamute com personalidade avançada"""
    
    def __init__(self, config_file: str = ".env"):
        """Inicializar sistema de chat personalizado"""
        self.config = Config(config_file)
        self.logger = setup_logger("MamuteChatIA")
        
        # Componentes principais
        self.db_manager = DatabaseManager(self.config)
        self.embedding_manager = EmbeddingManager(self.config)
        self.ai_agent = AIAgent(self.config)
        self.fallback_system = FallbackChatSystem()
        
        # Sistema de personalidade
        self.personality = MamutePersonality()
        
        # Estado da sessão
        self.session_start = datetime.now()
        self.conversation_history: List[Dict] = []
        self.user_preferences = {}
        
        # Estatísticas da sessão
        self.session_stats = {
            'queries': 0,
            'successful_queries': 0,
            'documents_found': 0,
            'favorite_topics': [],
            'session_time': timedelta(0)
        }
        
        self.logger.info("🚀 Sistema de Chat IA Mamute inicializado com personalidade avançada!")
    
    def get_welcome_message(self) -> Dict[str, Any]:
        """Gerar mensagem de boas-vindas personalizada"""
        greeting = self.personality.get_greeting()
        
        # Adicionar estatísticas se disponíveis
        stats_msg = ""
        try:
            doc_count = self.get_document_count()
            if doc_count > 0:
                stats_emoji = self.personality.get_emoji('data')
                stats_msg = f"\n\nTenho acesso a {doc_count:,} documentos prontos para explorar! {stats_emoji}"
        except Exception as e:
            self.logger.warning(f"Erro ao obter contagem de documentos: {e}")
        
        # Dicas úteis personalizadas
        tips_emoji = self.personality.get_emoji('info')
        help_emoji = self.personality.get_emoji('help')
        
        tips = f"\n\n{tips_emoji} **O que posso fazer por você:**\n" + \
               "• Responder perguntas sobre seus dados 🤔\n" + \
               "• Buscar informações específicas 🔍\n" + \
               "• Criar análises e resumos 📊\n" + \
               "• Gerar gráficos e visualizações 📈\n" + \
               "• Conversar naturalmente sobre qualquer tópico 💬\n\n" + \
               f"Digite 'ajuda' a qualquer momento! {help_emoji}"
        
        # Adicionar starter de conversa ocasional
        conversation_starter = ""
        if self.session_stats['queries'] == 0:  # Primeira interação
            conversation_starter = f"\n\n{self.personality.get_conversation_starter()}"
        
        return {
            'response': greeting + stats_msg + tips + conversation_starter,
            'type': 'welcome',
            'timestamp': datetime.now().isoformat(),
            'session_id': id(self),
            'personality_mode': True
        }
    
    async def get_response(self, user_input: str, context: Dict = None) -> Dict[str, Any]:
        """Gerar resposta com personalidade avançada"""
        try:
            # Atualizar estatísticas
            self.session_stats['queries'] += 1
            self.session_stats['session_time'] = datetime.now() - self.session_start
            
            # Adicionar à história da conversa
            self.conversation_history.append({
                'user': user_input,
                'timestamp': datetime.now().isoformat(),
                'type': 'user_input'
            })
            
            # Analisar tipo de consulta
            query_type = self._analyze_query_type(user_input)
            
            # Log personalizado
            thinking_emoji = self.personality.get_emoji('thinking')
            self.logger.info(f"{thinking_emoji} Processando [{query_type}]: {user_input[:50]}...")
            
            # Processar consulta baseado no tipo
            if query_type == 'greeting':
                response = self._handle_greeting()
            elif query_type == 'help':
                response = self._handle_help_request()
            elif query_type == 'compliment':
                response = self._handle_compliment(user_input)
            elif query_type == 'stats':
                response = self._handle_stats_request()
            elif query_type in ['search', 'question']:
                response = await self._handle_search_query(user_input, context)
            elif query_type == 'analysis':
                response = await self._handle_analysis_request(user_input)
            else:
                response = await self._handle_general_query(user_input, context)
            
            # Adicionar toque de personalidade
            if 'response' in response and response['type'] != 'welcome':
                response['response'] = self.personality.add_personality_touch(response['response'])
            
            # Adicionar à história
            self.conversation_history.append({
                'assistant': response['response'],
                'timestamp': response['timestamp'],
                'type': response['type']
            })
            
            return response
            
        except Exception as e:
            error_emoji = self.personality.get_emoji('error')
            self.logger.error(f"Erro no processamento: {e}")
            
            error_response = self.personality.format_error_response(
                str(e), 
                "Tente reformular sua pergunta ou me pergunte algo diferente!"
            )
            
            return {
                'response': error_response,
                'type': 'error',
                'timestamp': datetime.now().isoformat(),
                'personality_mode': True
            }
    
    def _analyze_query_type(self, query: str) -> str:
        """Analisar tipo de consulta com melhor detecção"""
        query_lower = query.lower().strip()
        
        # Saudações expandidas
        greetings = ['oi', 'olá', 'ola', 'hey', 'bom dia', 'boa tarde', 'boa noite', 
                    'e aí', 'fala aí', 'como vai', 'tudo bem', 'hello', 'hi']
        if any(greeting in query_lower for greeting in greetings):
            return 'greeting'
        
        # Elogios/Feedback positivo
        compliments = ['obrigado', 'obrigada', 'valeu', 'legal', 'muito bom', 'excelente',
                      'perfeito', 'adorei', 'gostei', 'incrível', 'top', 'show']
        if any(compliment in query_lower for compliment in compliments):
            return 'compliment'
        
        # Pedidos de ajuda
        help_terms = ['ajuda', 'help', 'socorro', 'como', 'comandos', 'o que você faz',
                     'que você pode fazer', 'funcionalidades', 'opções']
        if any(term in query_lower for term in help_terms):
            return 'help'
        
        # Análises
        analysis_terms = ['analisar', 'analise', 'análise', 'gráfico', 'grafico', 'chart',
                         'resumir', 'resumo', 'comparar', 'comparação', 'insights']
        if any(term in query_lower for term in analysis_terms):
            return 'analysis'
        
        # Busca/Pesquisa
        search_terms = ['buscar', 'procurar', 'encontrar', 'pesquisar', 'search', 'find',
                       'onde está', 'tem informação sobre', 'sabe sobre']
        if any(term in query_lower for term in search_terms):
            return 'search'
        
        # Estatísticas
        stats_terms = ['estatísticas', 'estatisticas', 'stats', 'números', 'quantos',
                      'total', 'contagem', 'dados da sessão']
        if any(term in query_lower for term in stats_terms):
            return 'stats'
        
        # Perguntas (contém '?')
        if '?' in query:
            return 'question'
        
        return 'general'
    
    def _handle_greeting(self) -> Dict[str, Any]:
        """Lidar com saudações"""
        # Saudações variadas baseadas no histórico
        if len(self.conversation_history) > 2:
            responses = [
                f"Oi de novo! {self.personality.get_emoji('greeting')}",
                f"Olá! Que bom que voltou! {self.personality.get_emoji('love')}",
                f"E aí! Pronto para mais descobertas? {self.personality.get_emoji('celebration')}"
            ]
            import random
            greeting = random.choice(responses)
        else:
            greeting = self.personality.get_greeting()
        
        return {
            'response': greeting,
            'type': 'greeting',
            'timestamp': datetime.now().isoformat(),
            'personality_mode': True
        }
    
    def _handle_compliment(self, user_input: str) -> Dict[str, Any]:
        """Lidar com elogios e feedback positivo"""
        compliment_responses = [
            f"Que bom que gostou! {self.personality.get_emoji('love')} Fico feliz em ajudar!",
            f"Obrigado! {self.personality.get_emoji('love')} Adoro quando consigo ser útil!",
            f"Fico muito feliz com isso! {self.personality.get_emoji('celebration')} Vamos continuar explorando!",
            f"Que alegria! {self.personality.get_emoji('love')} É um prazer trabalhar com você!"
        ]
        
        import random
        response = random.choice(compliment_responses)
        
        # Adicionar motivação
        motivation = self.personality.get_motivational()
        response += f"\n\n{motivation}"
        
        return {
            'response': response,
            'type': 'compliment_response',
            'timestamp': datetime.now().isoformat(),
            'personality_mode': True
        }
    
    def _handle_help_request(self) -> Dict[str, Any]:
        """Lidar com pedidos de ajuda"""
        return {
            'response': self.personality.format_help_response(),
            'type': 'help',
            'timestamp': datetime.now().isoformat(),
            'personality_mode': True
        }
    
    def _handle_stats_request(self) -> Dict[str, Any]:
        """Lidar com pedidos de estatísticas"""
        try:
            # Coletar estatísticas reais
            stats = {
                'documents': self.get_document_count(),
                'session_queries': self.session_stats['queries'],
                'successful_queries': self.session_stats['successful_queries'],
                'documents_found': self.session_stats['documents_found'],
                'session_time': str(self.session_stats['session_time']).split('.')[0],
                'start_time': self.session_start.strftime('%H:%M:%S')
            }
            
            return {
                'response': self.personality.format_stats_response(stats),
                'type': 'stats',
                'timestamp': datetime.now().isoformat(),
                'stats': stats,
                'personality_mode': True
            }
            
        except Exception as e:
            error_response = self.personality.format_error_response(
                "Erro ao coletar estatísticas",
                "Mas posso tentar outras coisas! Que tal uma busca?"
            )
            return {
                'response': error_response,
                'type': 'stats_error',
                'timestamp': datetime.now().isoformat(),
                'personality_mode': True
            }
    
    async def _handle_search_query(self, query: str, context: Dict = None) -> Dict[str, Any]:
        """Lidar com consultas de busca"""
        try:
            # Resposta inicial de busca
            search_msg = self.personality.get_response('search_start')
            
            # Realizar busca semântica
            search_results = await self.embedding_manager.search_documents(
                query, 
                limit=self.config.search_limit if hasattr(self.config, 'search_limit') else 5
            )
            
            if search_results:
                self.session_stats['successful_queries'] += 1
                self.session_stats['documents_found'] += len(search_results)
                
                # Gerar resposta contextualizada
                context_response = await self.ai_agent.generate_response(
                    query, search_results, context
                )
                
                # Formatar resposta de sucesso
                response_text = self.personality.format_success_response(
                    context_response, 
                    len(search_results)
                )
                
                return {
                    'response': response_text,
                    'documents': search_results,
                    'type': 'search_success',
                    'count': len(search_results),
                    'timestamp': datetime.now().isoformat(),
                    'personality_mode': True
                }
            else:
                # Sem resultados - resposta empática
                no_results_response = self.personality.get_response('no_results')
                
                # Tentar fallback
                fallback_response = await self.fallback_system.get_response(query)
                if fallback_response:
                    response_text = f"{no_results_response}\n\n💡 **Tentativa alternativa:**\n{fallback_response}"
                else:
                    response_text = f"{no_results_response}\n\n🎯 **Sugestões:**\n" + \
                                  "• Tente termos mais gerais\n" + \
                                  "• Use sinônimos\n" + \
                                  "• Reformule a pergunta\n" + \
                                  "• Ou me pergunte sobre outro assunto!"
                
                return {
                    'response': response_text,
                    'type': 'search_no_results',
                    'timestamp': datetime.now().isoformat(),
                    'personality_mode': True
                }
                
        except Exception as e:
            error_response = self.personality.format_error_response(
                f"Problema na busca: {str(e)}",
                "Que tal tentar uma pergunta diferente?"
            )
            
            return {
                'response': error_response,
                'type': 'search_error',
                'timestamp': datetime.now().isoformat(),
                'personality_mode': True
            }
    
    async def _handle_analysis_request(self, query: str) -> Dict[str, Any]:
        """Lidar com pedidos de análise"""
        try:
            analysis_msg = self.personality.get_response('analysis')
            
            # Simular análise (aqui você integraria com seus sistemas de análise)
            analysis_result = f"Análise para: {query}\n\n" + \
                            "📊 **Resultados da Análise:**\n" + \
                            "• Processamento concluído\n" + \
                            "• Dados analisados com sucesso\n" + \
                            "• Insights gerados\n\n" + \
                            "💡 **Próximos passos:** Que tal explorar aspectos específicos?"
            
            response_text = self.personality.format_analysis_response(analysis_result)
            
            return {
                'response': response_text,
                'type': 'analysis_success',
                'timestamp': datetime.now().isoformat(),
                'personality_mode': True
            }
            
        except Exception as e:
            error_response = self.personality.format_error_response(
                f"Erro na análise: {str(e)}",
                "Mas posso tentar de outra forma! Me dê mais detalhes?"
            )
            
            return {
                'response': error_response,
                'type': 'analysis_error', 
                'timestamp': datetime.now().isoformat(),
                'personality_mode': True
            }
    
    async def _handle_general_query(self, query: str, context: Dict = None) -> Dict[str, Any]:
        """Lidar com consultas gerais"""
        try:
            thinking_response = self.personality.get_response('thinking_response')
            
            # Tentar com fallback primeiro
            fallback_response = await self.fallback_system.get_response(query)
            
            if fallback_response:
                response_text = f"{thinking_response}\n\n{fallback_response}"
            else:
                # Resposta padrão empática
                response_text = f"{thinking_response}\n\n" + \
                              "Não tenho uma resposta específica para isso, mas adoraria ajudar! " + \
                              f"{self.personality.get_emoji('help')}\n\n" + \
                              "🎯 **Posso ajudar com:**\n" + \
                              "• Buscar informações nos documentos\n" + \
                              "• Fazer análises de dados\n" + \
                              "• Responder perguntas específicas\n" + \
                              "• Criar resumos e insights\n\n" + \
                              "Me dê mais detalhes sobre o que você precisa!"
            
            return {
                'response': response_text,
                'type': 'general_response',
                'timestamp': datetime.now().isoformat(),
                'personality_mode': True
            }
            
        except Exception as e:
            error_response = self.personality.format_error_response(
                f"Problema no processamento: {str(e)}",
                "Mas estou aqui para ajudar! Tente uma pergunta diferente?"
            )
            
            return {
                'response': error_response,
                'type': 'general_error',
                'timestamp': datetime.now().isoformat(),
                'personality_mode': True
            }
    
    def get_document_count(self) -> int:
        """Obter número total de documentos"""
        try:
            with self.db_manager.get_connection() as conn:
                result = conn.execute("SELECT COUNT(*) FROM documents")
                return result.fetchone()[0]
        except Exception as e:
            self.logger.warning(f"Erro ao obter contagem de documentos: {e}")
            return 0
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Obter resumo da sessão"""
        session_time = datetime.now() - self.session_start
        
        summary_emoji = self.personality.get_emoji('data')
        celebration_emoji = self.personality.get_emoji('celebration')
        
        summary = {
            'session_duration': str(session_time).split('.')[0],
            'total_queries': self.session_stats['queries'],
            'successful_queries': self.session_stats['successful_queries'],
            'documents_found': self.session_stats['documents_found'],
            'conversation_turns': len(self.conversation_history),
            'start_time': self.session_start.strftime('%H:%M:%S'),
            'end_time': datetime.now().strftime('%H:%M:%S')
        }
        
        summary_text = f"Resumo da nossa conversa! {summary_emoji}\n\n" + \
                      f"⏰ **Duração:** {summary['session_duration']}\n" + \
                      f"💬 **Conversas:** {summary['conversation_turns']} mensagens\n" + \
                      f"🔍 **Consultas:** {summary['total_queries']}\n" + \
                      f"✅ **Sucessos:** {summary['successful_queries']}\n" + \
                      f"📄 **Documentos encontrados:** {summary['documents_found']}\n\n" + \
                      f"Foi um prazer conversar! {celebration_emoji}"
        
        return {
            'summary': summary,
            'formatted_summary': summary_text,
            'timestamp': datetime.now().isoformat()
        }