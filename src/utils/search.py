"""
Sistema de Busca Inteligente para Mamute
Busca semântica avançada com filtros e categorização
"""
import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import json
from dataclasses import dataclass, asdict
from enum import Enum

from ..database.connection import DatabaseManager
from ..ai.embeddings import EmbeddingManager
from ..utils.config import Config
from ..utils.logger import setup_logger

class SearchType(Enum):
    """Tipos de busca disponíveis"""
    SEMANTIC = "semantic"  # Busca semântica por embeddings
    KEYWORD = "keyword"    # Busca por palavras-chave
    SQL = "sql"           # Busca em resultados de SQL
    HYBRID = "hybrid"     # Busca híbrida (semântica + keyword)

class ContentType(Enum):
    """Tipos de conteúdo"""
    DOCUMENT = "document"
    CONVERSATION = "conversation"
    QUERY_RESULT = "query_result"
    TABLE_DATA = "table_data"
    LOG_ENTRY = "log_entry"

@dataclass
class SearchFilter:
    """Filtros para busca"""
    content_type: Optional[ContentType] = None
    category: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    source: Optional[str] = None
    min_similarity: float = 0.5
    max_results: int = 20

@dataclass
class SearchResult:
    """Resultado individual de busca"""
    id: str
    title: str
    content: str
    content_type: ContentType
    similarity: float
    source: Optional[str] = None
    category: Optional[str] = None
    timestamp: Optional[datetime] = None
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        result = asdict(self)
        # Converter enums para strings
        result['content_type'] = self.content_type.value
        # Converter datetime para ISO string
        if self.timestamp:
            result['timestamp'] = self.timestamp.isoformat()
        return result

class IntelligentSearchEngine:
    """Motor de busca inteligente"""
    
    def __init__(self, db_manager: DatabaseManager, embedding_manager: EmbeddingManager, config: Config):
        self.db_manager = db_manager
        self.embedding_manager = embedding_manager
        self.config = config
        self.logger = setup_logger(__name__, config.log_level)
        
        # Cache para resultados frequentes
        self.search_cache = {}
        self.cache_ttl = 300  # 5 minutos
        
        # Indexação automática
        self.auto_index = True
        self.last_index_update = None
        
    def search(self, query: str, search_type: SearchType = SearchType.HYBRID, 
              filters: Optional[SearchFilter] = None) -> List[SearchResult]:
        """
        Busca inteligente principal
        
        Args:
            query: Termo de busca
            search_type: Tipo de busca a ser realizada
            filters: Filtros opcionais
            
        Returns:
            Lista de resultados ordenados por relevância
        """
        if not query.strip():
            return []
            
        if not filters:
            filters = SearchFilter()
            
        try:
            # Verificar cache
            cache_key = self._generate_cache_key(query, search_type, filters)
            cached_result = self._get_cached_result(cache_key)
            if cached_result:
                return cached_result
            
            # Executar busca baseada no tipo
            if search_type == SearchType.SEMANTIC:
                results = self._semantic_search(query, filters)
            elif search_type == SearchType.KEYWORD:
                results = self._keyword_search(query, filters)
            elif search_type == SearchType.SQL:
                results = self._sql_search(query, filters)
            elif search_type == SearchType.HYBRID:
                results = self._hybrid_search(query, filters)
            else:
                raise ValueError(f"Tipo de busca não suportado: {search_type}")
            
            # Aplicar filtros finais
            results = self._apply_filters(results, filters)
            
            # Ordenar por relevância
            results = self._rank_results(results, query)
            
            # Limitar resultados
            results = results[:filters.max_results]
            
            # Cache do resultado
            self._cache_result(cache_key, results)
            
            self.logger.info(f"Busca '{query}' retornou {len(results)} resultados")
            return results
            
        except Exception as e:
            self.logger.error(f"Erro na busca '{query}': {e}")
            return []
    
    def _semantic_search(self, query: str, filters: SearchFilter) -> List[SearchResult]:
        """Busca semântica usando embeddings"""
        results = []
        
        try:
            # Buscar documentos similares
            similar_docs = self.embedding_manager.search_similar_documents(
                query, 
                limit=filters.max_results * 2,  # Buscar mais para filtrar depois
                threshold=filters.min_similarity
            )
            
            for doc in similar_docs:
                result = SearchResult(
                    id=doc.get('id', ''),
                    title=doc.get('title', 'Documento'),
                    content=doc.get('content', ''),
                    content_type=ContentType.DOCUMENT,
                    similarity=doc.get('similarity', 0.0),
                    source=doc.get('source'),
                    category=doc.get('category'),
                    timestamp=doc.get('created_at'),
                    metadata=doc.get('metadata', {})
                )
                results.append(result)
                
        except Exception as e:
            self.logger.error(f"Erro na busca semântica: {e}")
            
        return results
    
    def _keyword_search(self, query: str, filters: SearchFilter) -> List[SearchResult]:
        """Busca por palavras-chave"""
        results = []
        
        try:
            # Extrair keywords da query
            keywords = self._extract_keywords(query)
            
            # Buscar em documentos
            doc_results = self._search_documents_by_keywords(keywords, filters)
            results.extend(doc_results)
            
            # Buscar em conversas
            conv_results = self._search_conversations_by_keywords(keywords, filters)
            results.extend(conv_results)
            
            # Buscar em logs de queries
            query_results = self._search_query_logs_by_keywords(keywords, filters)
            results.extend(query_results)
            
        except Exception as e:
            self.logger.error(f"Erro na busca por palavras-chave: {e}")
            
        return results
    
    def _sql_search(self, query: str, filters: SearchFilter) -> List[SearchResult]:
        """Busca em dados de tabelas SQL"""
        results = []
        
        try:
            # Verificar se a query é segura (apenas SELECT)
            if not self._is_safe_sql_query(query):
                self.logger.warning(f"Query SQL não segura rejeitada: {query}")
                return results
            
            # Executar query
            sql_results = self.db_manager.execute_query(query)
            
            if sql_results:
                for i, row in enumerate(sql_results):
                    # Converter resultado em texto pesquisável
                    content = self._row_to_searchable_text(row)
                    
                    result = SearchResult(
                        id=f"sql_result_{i}",
                        title=f"Resultado SQL {i+1}",
                        content=content,
                        content_type=ContentType.QUERY_RESULT,
                        similarity=1.0,  # Resultado direto
                        source="sql_query",
                        timestamp=datetime.now(),
                        metadata={"original_query": query, "row_data": row}
                    )
                    results.append(result)
                    
        except Exception as e:
            self.logger.error(f"Erro na busca SQL: {e}")
            
        return results
    
    def _hybrid_search(self, query: str, filters: SearchFilter) -> List[SearchResult]:
        """Busca híbrida combinando semântica e keywords"""
        # Buscar com ambos os métodos
        semantic_results = self._semantic_search(query, filters)
        keyword_results = self._keyword_search(query, filters)
        
        # Combinar resultados
        all_results = {}
        
        # Adicionar resultados semânticos com peso maior
        for result in semantic_results:
            key = self._generate_result_key(result)
            all_results[key] = result
            # Boost para resultados semânticos
            all_results[key].similarity = min(1.0, result.similarity * 1.2)
        
        # Adicionar resultados de keywords
        for result in keyword_results:
            key = self._generate_result_key(result)
            if key in all_results:
                # Combinar pontuações se já existe
                existing = all_results[key]
                combined_score = (existing.similarity + result.similarity) / 2
                all_results[key].similarity = min(1.0, combined_score * 1.1)
            else:
                all_results[key] = result
        
        return list(all_results.values())
    
    def _search_documents_by_keywords(self, keywords: List[str], filters: SearchFilter) -> List[SearchResult]:
        """Busca documentos por palavras-chave"""
        results = []
        
        try:
            # Construir query SQL para busca em documentos
            keywords_condition = " OR ".join([
                f"(title ILIKE %s OR content ILIKE %s)" for _ in keywords
            ])
            
            query = f"""
                SELECT id, title, content, source, category, created_at, metadata
                FROM documents 
                WHERE {keywords_condition}
                ORDER BY created_at DESC
                LIMIT %s
            """
            
            # Preparar parâmetros (cada keyword aparece 2 vezes)
            params = []
            for keyword in keywords:
                params.extend([f"%{keyword}%", f"%{keyword}%"])
            params.append(filters.max_results)
            
            docs = self.db_manager.execute_query(query, params)
            
            for doc in docs:
                # Calcular similarity baseada na frequência das palavras
                similarity = self._calculate_keyword_similarity(doc['content'], keywords)
                
                result = SearchResult(
                    id=str(doc['id']),
                    title=doc['title'],
                    content=doc['content'],
                    content_type=ContentType.DOCUMENT,
                    similarity=similarity,
                    source=doc['source'],
                    category=doc['category'],
                    timestamp=doc['created_at'],
                    metadata=doc.get('metadata', {})
                )
                results.append(result)
                
        except Exception as e:
            self.logger.error(f"Erro na busca de documentos: {e}")
            
        return results
    
    def _search_conversations_by_keywords(self, keywords: List[str], filters: SearchFilter) -> List[SearchResult]:
        """Busca conversas por palavras-chave"""
        results = []
        
        try:
            keywords_condition = " OR ".join([
                f"(user_message ILIKE %s OR ai_response ILIKE %s)" for _ in keywords
            ])
            
            query = f"""
                SELECT id, session_id, user_message, ai_response, timestamp, metadata
                FROM conversations 
                WHERE {keywords_condition}
                ORDER BY timestamp DESC
                LIMIT %s
            """
            
            params = []
            for keyword in keywords:
                params.extend([f"%{keyword}%", f"%{keyword}%"])
            params.append(filters.max_results)
            
            conversations = self.db_manager.execute_query(query, params)
            
            for conv in conversations:
                # Combinar mensagem do usuário e resposta da IA
                content = f"Usuário: {conv['user_message']}\\n\\nMamute: {conv['ai_response']}"
                similarity = self._calculate_keyword_similarity(content, keywords)
                
                result = SearchResult(
                    id=f"conv_{conv['id']}",
                    title=f"Conversa {conv['session_id'][:8]}",
                    content=content,
                    content_type=ContentType.CONVERSATION,
                    similarity=similarity,
                    source="chat_history",
                    timestamp=conv['timestamp'],
                    metadata=conv.get('metadata', {})
                )
                results.append(result)
                
        except Exception as e:
            self.logger.error(f"Erro na busca de conversas: {e}")
            
        return results
    
    def _search_query_logs_by_keywords(self, keywords: List[str], filters: SearchFilter) -> List[SearchResult]:
        """Busca logs de queries por palavras-chave"""
        results = []
        
        try:
            keywords_condition = " OR ".join([
                f"(sql_query ILIKE %s OR result_summary ILIKE %s)" for _ in keywords
            ])
            
            query = f"""
                SELECT id, sql_query, result_summary, execution_time, timestamp, metadata
                FROM queries 
                WHERE {keywords_condition}
                ORDER BY timestamp DESC
                LIMIT %s
            """
            
            params = []
            for keyword in keywords:
                params.extend([f"%{keyword}%", f"%{keyword}%"])
            params.append(filters.max_results)
            
            query_logs = self.db_manager.execute_query(query, params)
            
            for log in query_logs:
                content = f"Query: {log['sql_query']}\\n\\nResultado: {log.get('result_summary', 'N/A')}"
                similarity = self._calculate_keyword_similarity(content, keywords)
                
                result = SearchResult(
                    id=f"query_{log['id']}",
                    title=f"Query SQL ({log['execution_time']:.2f}ms)",
                    content=content,
                    content_type=ContentType.LOG_ENTRY,
                    similarity=similarity,
                    source="query_logs",
                    timestamp=log['timestamp'],
                    metadata=log.get('metadata', {})
                )
                results.append(result)
                
        except Exception as e:
            self.logger.error(f"Erro na busca de logs: {e}")
            
        return results
    
    def add_to_search_index(self, content_type: ContentType, title: str, content: str, 
                           source: str = None, category: str = None, metadata: Dict = None):
        """Adiciona conteúdo ao índice de busca"""
        try:
            if content_type == ContentType.DOCUMENT:
                # Adicionar documento
                self.embedding_manager.add_document(
                    title=title,
                    content=content,
                    source=source,
                    category=category,
                    metadata=metadata or {}
                )
            else:
                # Para outros tipos, armazenar em tabelas específicas
                self._store_searchable_content(content_type, title, content, source, category, metadata)
                
        except Exception as e:
            self.logger.error(f"Erro ao adicionar ao índice: {e}")
    
    def get_search_suggestions(self, partial_query: str, limit: int = 10) -> List[str]:
        """Gera sugestões de busca baseadas na query parcial"""
        suggestions = []
        
        try:
            # Buscar sugestões em títulos de documentos
            doc_suggestions = self._get_document_title_suggestions(partial_query, limit // 2)
            suggestions.extend(doc_suggestions)
            
            # Buscar sugestões em queries anteriores
            query_suggestions = self._get_query_history_suggestions(partial_query, limit // 2)
            suggestions.extend(query_suggestions)
            
            # Remover duplicatas e ordenar
            suggestions = list(set(suggestions))
            suggestions.sort(key=lambda x: len(x))
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar sugestões: {e}")
            
        return suggestions[:limit]
    
    def get_search_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do sistema de busca"""
        try:
            stats = {
                'total_documents': self._count_searchable_content(ContentType.DOCUMENT),
                'total_conversations': self._count_searchable_content(ContentType.CONVERSATION),
                'total_query_logs': self._count_searchable_content(ContentType.LOG_ENTRY),
                'cache_size': len(self.search_cache),
                'last_index_update': self.last_index_update.isoformat() if self.last_index_update else None
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Erro ao obter estatísticas: {e}")
            return {}
    
    # Métodos auxiliares
    def _extract_keywords(self, query: str) -> List[str]:
        """Extrai palavras-chave da query"""
        # Remove pontuação e divide em palavras
        words = re.findall(r'\\b\\w+\\b', query.lower())
        
        # Remove palavras muito curtas e palavras de parada
        stop_words = {'de', 'da', 'do', 'das', 'dos', 'e', 'ou', 'o', 'a', 'os', 'as', 'um', 'uma', 'uns', 'umas'}
        keywords = [word for word in words if len(word) > 2 and word not in stop_words]
        
        return keywords
    
    def _calculate_keyword_similarity(self, text: str, keywords: List[str]) -> float:
        """Calcula similaridade baseada na frequência de palavras-chave"""
        text_lower = text.lower()
        total_score = 0
        
        for keyword in keywords:
            # Contar ocorrências da palavra
            count = text_lower.count(keyword.lower())
            if count > 0:
                # Score baseado na frequência e tamanho da palavra
                score = min(1.0, count * 0.1) * (len(keyword) / 10)
                total_score += score
        
        # Normalizar pelo número de keywords
        if keywords:
            return min(1.0, total_score / len(keywords))
        
        return 0.0
    
    def _is_safe_sql_query(self, query: str) -> bool:
        """Verifica se a query SQL é segura (apenas SELECT)"""
        query_clean = query.strip().upper()
        
        # Permitir apenas SELECT
        if not query_clean.startswith('SELECT'):
            return False
            
        # Verificar palavras proibidas
        forbidden_words = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE', 'TRUNCATE']
        
        for word in forbidden_words:
            if word in query_clean:
                return False
                
        return True
    
    def _row_to_searchable_text(self, row: Dict) -> str:
        """Converte linha de resultado SQL em texto pesquisável"""
        text_parts = []
        
        for key, value in row.items():
            if value is not None:
                text_parts.append(f"{key}: {value}")
        
        return " | ".join(text_parts)
    
    def _apply_filters(self, results: List[SearchResult], filters: SearchFilter) -> List[SearchResult]:
        """Aplica filtros aos resultados"""
        filtered = results
        
        # Filtro por tipo de conteúdo
        if filters.content_type:
            filtered = [r for r in filtered if r.content_type == filters.content_type]
        
        # Filtro por categoria
        if filters.category:
            filtered = [r for r in filtered if r.category == filters.category]
        
        # Filtro por data
        if filters.date_from:
            filtered = [r for r in filtered if r.timestamp and r.timestamp >= filters.date_from]
        
        if filters.date_to:
            filtered = [r for r in filtered if r.timestamp and r.timestamp <= filters.date_to]
        
        # Filtro por source
        if filters.source:
            filtered = [r for r in filtered if r.source == filters.source]
        
        # Filtro por similaridade mínima
        filtered = [r for r in filtered if r.similarity >= filters.min_similarity]
        
        return filtered
    
    def _rank_results(self, results: List[SearchResult], query: str) -> List[SearchResult]:
        """Ordena resultados por relevância"""
        # Ordenar por similarity score descrescente
        return sorted(results, key=lambda r: r.similarity, reverse=True)
    
    def _generate_cache_key(self, query: str, search_type: SearchType, filters: SearchFilter) -> str:
        """Gera chave única para cache"""
        filter_hash = hash(str(asdict(filters)))
        return f"{query}_{search_type.value}_{filter_hash}"
    
    def _get_cached_result(self, cache_key: str) -> Optional[List[SearchResult]]:
        """Recupera resultado do cache se ainda válido"""
        if cache_key in self.search_cache:
            timestamp, results = self.search_cache[cache_key]
            if (datetime.now() - timestamp).total_seconds() < self.cache_ttl:
                return results
        return None
    
    def _cache_result(self, cache_key: str, results: List[SearchResult]) -> None:
        """Armazena resultado no cache"""
        self.search_cache[cache_key] = (datetime.now(), results)
    
    def _generate_result_key(self, result: SearchResult) -> str:
        """Gera chave única para resultado (para deduplicação)"""
        return f"{result.content_type.value}_{result.title}_{hash(result.content[:100])}"
    
    # Métodos de sugestões e estatísticas (implementação simplificada)
    def _get_document_title_suggestions(self, partial: str, limit: int) -> List[str]:
        """Busca sugestões em títulos de documentos"""
        try:
            query = "SELECT DISTINCT title FROM documents WHERE title ILIKE %s LIMIT %s"
            results = self.db_manager.execute_query(query, (f"%{partial}%", limit))
            return [r['title'] for r in results]
        except:
            return []
    
    def _get_query_history_suggestions(self, partial: str, limit: int) -> List[str]:
        """Busca sugestões em histórico de queries"""
        try:
            query = "SELECT DISTINCT sql_query FROM queries WHERE sql_query ILIKE %s LIMIT %s"
            results = self.db_manager.execute_query(query, (f"%{partial}%", limit))
            return [r['sql_query'] for r in results]
        except:
            return []
    
    def _count_searchable_content(self, content_type: ContentType) -> int:
        """Conta conteúdo pesquisável por tipo"""
        try:
            if content_type == ContentType.DOCUMENT:
                query = "SELECT COUNT(*) as count FROM documents"
            elif content_type == ContentType.CONVERSATION:
                query = "SELECT COUNT(*) as count FROM conversations"
            elif content_type == ContentType.LOG_ENTRY:
                query = "SELECT COUNT(*) as count FROM queries"
            else:
                return 0
            
            result = self.db_manager.execute_query(query)
            return result[0]['count'] if result else 0
        except:
            return 0
    
    def _store_searchable_content(self, content_type: ContentType, title: str, content: str,
                                 source: str, category: str, metadata: Dict) -> None:
        """Armazena conteúdo pesquisável em tabelas específicas"""
        # Implementação simplificada - pode ser expandida conforme necessário
        pass