"""
Gerenciador de embeddings e busca semântica
"""
import numpy as np
from typing import List, Dict, Any, Optional
import json

from ..database.connection import DatabaseManager
from ..database.models import Document
from ..utils.config import Config
from ..utils.logger import setup_logger

class EmbeddingManager:
    """Gerenciador de embeddings para busca semântica"""
    
    def __init__(self, config: Config, db_manager: DatabaseManager):
        """
        Inicializa o gerenciador de embeddings
        
        Args:
            config: Configuração da aplicação
            db_manager: Gerenciador do banco de dados
        """
        self.config = config
        self.db_manager = db_manager
        self.logger = setup_logger(__name__, config.log_level)
        
        # Configurar OpenAI para embeddings
        try:
            import openai
            self.client = openai.OpenAI(api_key=config.openai_api_key)
            self.embedding_model = "text-embedding-ada-002"
        except ImportError:
            self.logger.warning("OpenAI não disponível para embeddings")
            self.client = None
    
    def create_embedding(self, text: str) -> List[float]:
        """
        Cria embedding para um texto
        
        Args:
            text: Texto para criar embedding
        
        Returns:
            List[float]: Vetor de embedding
        """
        if not self.client:
            raise ValueError("Cliente OpenAI não configurado")
        
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            embedding = response.data[0].embedding
            self.logger.debug(f"Embedding criado para texto de {len(text)} caracteres")
            return embedding
            
        except Exception as e:
            self.logger.error(f"Erro ao criar embedding: {e}")
            raise
    
    def add_document(self, title: str, content: str, file_path: Optional[str] = None, 
                    file_type: Optional[str] = None, metadata: Optional[Dict] = None) -> int:
        """
        Adiciona um documento com embedding ao banco
        
        Args:
            title: Título do documento
            content: Conteúdo do documento
            file_path: Caminho do arquivo (opcional)
            file_type: Tipo do arquivo (opcional)
            metadata: Metadados adicionais (opcional)
        
        Returns:
            int: ID do documento criado
        """
        try:
            # Criar embedding do conteúdo
            embedding = self.create_embedding(content)
            
            # Salvar no banco de dados
            with self.db_manager.get_session() as session:
                document = Document(
                    title=title,
                    content=content,
                    file_path=file_path,
                    file_type=file_type,
                    embedding=embedding,
                    meta_data=metadata or {}
                )
                session.add(document)
                session.flush()
                document_id = document.id
                session.commit()
            
            self.logger.info(f"Documento adicionado: ID {document_id}")
            return document_id
            
        except Exception as e:
            self.logger.error(f"Erro ao adicionar documento: {e}")
            raise
    
    def search_similar_documents(self, query: str, limit: int = 5, threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        Busca documentos similares usando busca semântica
        
        Args:
            query: Consulta de busca
            limit: Número máximo de resultados
            threshold: Limiar de similaridade (0-1)
        
        Returns:
            List[Dict]: Documentos similares ordenados por relevância
        """
        try:
            # Criar embedding da consulta
            query_embedding = self.create_embedding(query)
            
            # Buscar documentos similares
            # Nota: Esta implementação usa similaridade de cosseno simples
            # Para produção, considere usar pg_vector ou similar
            
            documents_query = """
            SELECT id, title, content, file_path, meta_data, embedding
            FROM documents
            WHERE is_active = true
            """
            documents = self.db_manager.execute_query(documents_query)
            
            results = []
            for doc in documents:
                if doc['embedding']:
                    # Calcular similaridade de cosseno
                    doc_embedding = np.array(doc['embedding'])
                    query_emb = np.array(query_embedding)
                    
                    similarity = np.dot(query_emb, doc_embedding) / (
                        np.linalg.norm(query_emb) * np.linalg.norm(doc_embedding)
                    )
                    
                    if similarity >= threshold:
                        results.append({
                            'id': doc['id'],
                            'title': doc['title'],
                            'content': doc['content'][:500] + '...' if len(doc['content']) > 500 else doc['content'],
                            'file_path': doc['file_path'],
                            'metadata': doc['meta_data'],
                            'similarity': float(similarity)
                        })
            
            # Ordenar por similaridade
            results.sort(key=lambda x: x['similarity'], reverse=True)
            
            self.logger.info(f"Busca semântica: {len(results)} documentos encontrados")
            return results[:limit]
            
        except Exception as e:
            self.logger.error(f"Erro na busca semântica: {e}")
            return []
    
    def get_document_by_id(self, document_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtém um documento por ID
        
        Args:
            document_id: ID do documento
        
        Returns:
            Dict: Dados do documento ou None se não encontrado
        """
        try:
            query = """
            SELECT id, title, content, file_path, file_type, meta_data, created_at
            FROM documents
            WHERE id = %(id)s AND is_active = true
            """
            result = self.db_manager.execute_query(query, {"id": document_id})
            
            if result:
                return result[0]
            return None
            
        except Exception as e:
            self.logger.error(f"Erro ao buscar documento {document_id}: {e}")
            return None
    
    def update_document(self, document_id: int, title: Optional[str] = None, 
                       content: Optional[str] = None, metadata: Optional[Dict] = None) -> bool:
        """
        Atualiza um documento existente
        
        Args:
            document_id: ID do documento
            title: Novo título (opcional)
            content: Novo conteúdo (opcional)
            metadata: Novos metadados (opcional)
        
        Returns:
            bool: True se atualizado com sucesso
        """
        try:
            updates = []
            params = {"id": document_id}
            
            if title:
                updates.append("title = %(title)s")
                params["title"] = title
            
            if content:
                # Recriar embedding se o conteúdo mudou
                embedding = self.create_embedding(content)
                updates.append("content = %(content)s")
                updates.append("embedding = %(embedding)s")
                params["content"] = content
                params["embedding"] = json.dumps(embedding)
            
            if metadata:
                updates.append("meta_data = %(meta_data)s")
                params["meta_data"] = json.dumps(metadata)
            
            if not updates:
                return True  # Nada para atualizar
            
            updates.append("updated_at = NOW()")
            
            query = f"""
            UPDATE documents 
            SET {', '.join(updates)}
            WHERE id = %(id)s AND is_active = true
            """
            
            affected_rows = self.db_manager.execute_command(query, params)
            
            success = affected_rows > 0
            if success:
                self.logger.info(f"Documento {document_id} atualizado")
            else:
                self.logger.warning(f"Documento {document_id} não encontrado para atualização")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Erro ao atualizar documento {document_id}: {e}")
            return False
    
    def delete_document(self, document_id: int, hard_delete: bool = False) -> bool:
        """
        Remove um documento
        
        Args:
            document_id: ID do documento
            hard_delete: Se True, remove fisicamente; se False, marca como inativo
        
        Returns:
            bool: True se removido com sucesso
        """
        try:
            if hard_delete:
                query = "DELETE FROM documents WHERE id = %(id)s"
            else:
                query = "UPDATE documents SET is_active = false WHERE id = %(id)s"
            
            affected_rows = self.db_manager.execute_command(query, {"id": document_id})
            
            success = affected_rows > 0
            action = "removido" if hard_delete else "desativado"
            
            if success:
                self.logger.info(f"Documento {document_id} {action}")
            else:
                self.logger.warning(f"Documento {document_id} não encontrado para remoção")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Erro ao remover documento {document_id}: {e}")
            return False