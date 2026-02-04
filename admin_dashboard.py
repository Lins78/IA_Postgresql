"""
Dashboard de Administração Avançado do Mamute
Sistema completo para gerenciamento e monitoramento
"""
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio
import os
import sys
import json
import datetime
from pathlib import Path

# Tentar importar psutil, usar fallback se não disponível
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None

# Adicionar o diretório principal ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import IAPostgreSQL
from src.utils.logger import setup_logger
from src.utils.config import Config

# Configurar templates
templates = Jinja2Templates(directory="web/templates")

class AdminDashboard:
    """Classe para gerenciar o dashboard de administração"""
    
    def __init__(self):
        """Inicializar dashboard admin"""
        self.config = Config()
        self.logger = setup_logger("AdminDashboard")
        self.ia_system = None
        
    async def initialize(self):
        """Inicializar sistema IA"""
        try:
            self.ia_system = IAPostgreSQL()
            self.ia_system.setup_database()
            return True
        except Exception as e:
            self.logger.error(f"Erro ao inicializar sistema: {e}")
            return False
    
    def get_system_info(self) -> Dict[str, Any]:
        """Coletar informações do sistema"""
        try:
            if not PSUTIL_AVAILABLE:
                return {
                    'cpu_usage': 0,
                    'memory': {'total': 0, 'available': 0, 'percent': 0},
                    'disk': {'total': 0, 'free': 0, 'percent': 0},
                    'uptime': datetime.timedelta(0),
                    'warning': 'psutil não disponível - instale com: pip install psutil'
                }
            
            return {
                'cpu_usage': psutil.cpu_percent(interval=1),
                'memory': {
                    'total': psutil.virtual_memory().total,
                    'available': psutil.virtual_memory().available,
                    'percent': psutil.virtual_memory().percent
                },
                'disk': {
                    'total': psutil.disk_usage('/').total,
                    'free': psutil.disk_usage('/').free,
                    'percent': psutil.disk_usage('/').percent
                },
                'uptime': datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time())
            }
        except Exception as e:
            self.logger.error(f"Erro ao coletar info sistema: {e}")
            return {}
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Coletar estatísticas do banco de dados"""
        try:
            if not self.ia_system:
                return {}
            
            db_manager = self.ia_system.db_manager
            
            # Estatísticas das tabelas
            tables_info = []
            tables = ['documents', 'conversations', 'chat_sessions', 'embeddings', 'analysis_cache']
            
            for table in tables:
                try:
                    count_result = db_manager.execute_query(f"SELECT COUNT(*) as count FROM {table}")
                    count = count_result[0]['count'] if count_result else 0
                    
                    size_result = db_manager.execute_query(f"""
                        SELECT pg_total_relation_size('{table}') as size
                    """)
                    size = size_result[0]['size'] if size_result else 0
                    
                    tables_info.append({
                        'name': table,
                        'count': count,
                        'size': size,
                        'size_mb': round(size / (1024*1024), 2)
                    })
                except Exception as e:
                    self.logger.warning(f"Erro ao obter stats da tabela {table}: {e}")
                    tables_info.append({
                        'name': table,
                        'count': 0,
                        'size': 0,
                        'size_mb': 0
                    })
            
            # Informações gerais do banco
            db_info = db_manager.execute_query("""
                SELECT 
                    pg_database_size(current_database()) as db_size,
                    current_database() as db_name,
                    version() as pg_version
            """)
            
            return {
                'tables': tables_info,
                'database_info': db_info[0] if db_info else {},
                'total_documents': sum(t['count'] for t in tables_info if t['name'] == 'documents'),
                'total_conversations': sum(t['count'] for t in tables_info if t['name'] == 'conversations'),
                'connection_status': 'healthy' if db_manager.test_connection() else 'error'
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar stats do banco: {e}")
            return {}
    
    def get_recent_activity(self) -> List[Dict[str, Any]]:
        """Obter atividade recente do sistema"""
        try:
            if not self.ia_system:
                return []
            
            db_manager = self.ia_system.db_manager
            
            # Conversas recentes
            recent_conversations = db_manager.execute_query("""
                SELECT 
                    user_message,
                    ai_response,
                    created_at,
                    session_id
                FROM conversations 
                ORDER BY created_at DESC 
                LIMIT 10
            """)
            
            # Documentos adicionados recentemente
            recent_documents = db_manager.execute_query("""
                SELECT 
                    title,
                    category,
                    created_at,
                    SUBSTRING(content, 1, 100) as preview
                FROM documents 
                ORDER BY created_at DESC 
                LIMIT 5
            """)
            
            activity = []
            
            # Adicionar conversas
            for conv in recent_conversations:
                activity.append({
                    'type': 'conversation',
                    'description': f"Chat: {conv['user_message'][:50]}...",
                    'timestamp': conv['created_at'],
                    'session': conv['session_id']
                })
            
            # Adicionar documentos
            for doc in recent_documents:
                activity.append({
                    'type': 'document',
                    'description': f"Documento adicionado: {doc['title']}",
                    'timestamp': doc['created_at'],
                    'category': doc['category']
                })
            
            # Ordenar por timestamp
            activity.sort(key=lambda x: x['timestamp'], reverse=True)
            
            return activity[:15]  # Últimas 15 atividades
            
        except Exception as e:
            self.logger.error(f"Erro ao obter atividade recente: {e}")
            return []
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Obter métricas de performance"""
        try:
            if not self.ia_system:
                return {}
            
            db_manager = self.ia_system.db_manager
            
            # Consultas mais lentas
            slow_queries = db_manager.execute_query("""
                SELECT 
                    query,
                    calls,
                    total_time,
                    mean_time,
                    rows
                FROM pg_stat_statements 
                ORDER BY total_time DESC 
                LIMIT 5
            """) or []
            
            # Cache hit ratio
            cache_hit = db_manager.execute_query("""
                SELECT 
                    sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) * 100 as cache_hit_ratio
                FROM pg_statio_user_tables
            """) or [{'cache_hit_ratio': 0}]
            
            # Índices não utilizados
            unused_indexes = db_manager.execute_query("""
                SELECT 
                    indexname,
                    tablename,
                    pg_size_pretty(pg_relation_size(indexrelid)) as size
                FROM pg_stat_user_indexes 
                WHERE idx_tup_read = 0
                ORDER BY pg_relation_size(indexrelid) DESC
                LIMIT 10
            """) or []
            
            return {
                'slow_queries': slow_queries,
                'cache_hit_ratio': float(cache_hit[0]['cache_hit_ratio'] or 0),
                'unused_indexes': unused_indexes,
                'query_count': len(slow_queries)
            }
            
        except Exception as e:
            self.logger.warning(f"Erro ao obter métricas de performance: {e}")
            return {
                'slow_queries': [],
                'cache_hit_ratio': 0,
                'unused_indexes': [],
                'query_count': 0
            }
    
    def get_security_info(self) -> Dict[str, Any]:
        """Obter informações de segurança"""
        try:
            if not self.ia_system:
                return {}
            
            db_manager = self.ia_system.db_manager
            
            # Conexões ativas
            active_connections = db_manager.execute_query("""
                SELECT 
                    state,
                    application_name,
                    client_addr,
                    backend_start,
                    COUNT(*) as count
                FROM pg_stat_activity 
                WHERE state IS NOT NULL
                GROUP BY state, application_name, client_addr, backend_start
                ORDER BY backend_start DESC
            """) or []
            
            # Verificar permissões
            permissions_check = db_manager.execute_query("""
                SELECT 
                    usename,
                    usesuper,
                    usecreatedb,
                    usebypassrls
                FROM pg_user
                WHERE usename = current_user
            """) or []
            
            return {
                'active_connections': len(active_connections),
                'connections_detail': active_connections[:10],
                'current_user_permissions': permissions_check[0] if permissions_check else {},
                'ssl_enabled': 'N/A',  # Seria preciso verificar configuração
                'last_security_check': datetime.datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao obter info de segurança: {e}")
            return {}
    
    def cleanup_old_data(self, days: int = 30) -> Dict[str, int]:
        """Limpar dados antigos"""
        try:
            if not self.ia_system:
                return {}
            
            db_manager = self.ia_system.db_manager
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
            
            # Limpar conversas antigas
            conversations_deleted = db_manager.execute_query(f"""
                DELETE FROM conversations 
                WHERE created_at < '{cutoff_date}'
                RETURNING id
            """) or []
            
            # Limpar sessões antigas
            sessions_deleted = db_manager.execute_query(f"""
                DELETE FROM chat_sessions 
                WHERE created_at < '{cutoff_date}'
                RETURNING id
            """) or []
            
            return {
                'conversations_deleted': len(conversations_deleted),
                'sessions_deleted': len(sessions_deleted),
                'cleanup_date': cutoff_date.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Erro na limpeza de dados: {e}")
            return {}

# Criar instância global
admin_dashboard = AdminDashboard()

async def get_admin_dashboard_data():
    """Obter todos os dados do dashboard admin"""
    if not admin_dashboard.ia_system:
        await admin_dashboard.initialize()
    
    return {
        'system_info': admin_dashboard.get_system_info(),
        'database_stats': admin_dashboard.get_database_stats(),
        'recent_activity': admin_dashboard.get_recent_activity(),
        'performance_metrics': admin_dashboard.get_performance_metrics(),
        'security_info': admin_dashboard.get_security_info(),
        'timestamp': datetime.datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    
    # Criar app FastAPI simples para testes
    app = FastAPI(title="Mamute Admin Dashboard")
    
    @app.get("/admin/data")
    async def admin_data():
        """Endpoint para dados do dashboard admin"""
        return await get_admin_dashboard_data()
    
    @app.get("/admin/cleanup/{days}")
    async def cleanup_data(days: int):
        """Endpoint para limpeza de dados"""
        if not admin_dashboard.ia_system:
            await admin_dashboard.initialize()
        
        result = admin_dashboard.cleanup_old_data(days)
        return {"success": True, "result": result}
    
    print("🐘 Iniciando Dashboard Admin do Mamute...")
    print("📊 URL: http://localhost:8001/admin/data")
    uvicorn.run(app, host="0.0.0.0", port=8001)