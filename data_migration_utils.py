"""
Utilitários de Migração de Dados para o Mamute
Sistema para importar/exportar dados de diferentes fontes
"""
import os
import sys
import json
import csv
import pandas as pd
import sqlite3
import psycopg2
from pathlib import Path

# Tentar importar mysql.connector, usar fallback se não disponível
try:
    import mysql.connector
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    mysql = None
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import xml.etree.ElementTree as ET

# Adicionar o diretório principal ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.utils.config import Config
from src.utils.logger import setup_logger
from src.database.connection import DatabaseManager

class DataMigrationUtilities:
    """Utilitários completos para migração de dados"""
    
    def __init__(self, config_file: str = ".env"):
        """Inicializar utilitários de migração"""
        self.config = Config(config_file)
        self.logger = setup_logger("DataMigration")
        self.db_manager = DatabaseManager(self.config)
        
        # Diretório para arquivos de migração
        self.migration_dir = Path("migrations")
        self.migration_dir.mkdir(exist_ok=True)
        
        # Diretórios específicos
        self.import_dir = self.migration_dir / "import"
        self.export_dir = self.migration_dir / "export"
        self.temp_dir = self.migration_dir / "temp"
        
        for dir_path in [self.import_dir, self.export_dir, self.temp_dir]:
            dir_path.mkdir(exist_ok=True)
        
        self.logger.info("Utilitários de migração de dados inicializados")
    
    def import_csv_documents(self, csv_file: str, mapping: Dict[str, str] = None) -> Dict[str, Any]:
        """Importar documentos de arquivo CSV"""
        try:
            csv_path = Path(csv_file)
            if not csv_path.exists():
                raise FileNotFoundError(f"Arquivo CSV não encontrado: {csv_file}")
            
            # Mapeamento padrão de colunas
            default_mapping = {
                'title': 'title',
                'content': 'content',
                'source': 'source',
                'category': 'category'
            }
            
            if mapping:
                default_mapping.update(mapping)
            
            self.logger.info(f"Importando documentos de CSV: {csv_file}")
            
            # Ler CSV
            df = pd.read_csv(csv_file, encoding='utf-8')
            imported_count = 0
            errors = []
            
            for index, row in df.iterrows():
                try:
                    # Mapear colunas
                    doc_data = {}
                    for mamute_col, csv_col in default_mapping.items():
                        if csv_col in row.index and pd.notna(row[csv_col]):
                            doc_data[mamute_col] = str(row[csv_col])
                    
                    # Validar dados obrigatórios
                    if 'title' not in doc_data or 'content' not in doc_data:
                        errors.append(f"Linha {index + 1}: título ou conteúdo faltando")
                        continue
                    
                    # Adicionar documento ao banco
                    doc_id = self.db_manager.execute_query("""
                        INSERT INTO documents (title, content, source, category, created_at)
                        VALUES (%(title)s, %(content)s, %(source)s, %(category)s, NOW())
                        RETURNING id
                    """, {
                        'title': doc_data.get('title'),
                        'content': doc_data.get('content'),
                        'source': doc_data.get('source', f"CSV Import: {csv_path.name}"),
                        'category': doc_data.get('category', 'imported')
                    })
                    
                    if doc_id:
                        imported_count += 1
                        self.logger.debug(f"Documento importado: {doc_data['title']}")
                    
                except Exception as e:
                    error_msg = f"Linha {index + 1}: {str(e)}"
                    errors.append(error_msg)
                    self.logger.warning(error_msg)
            
            result = {
                'source_file': str(csv_path),
                'total_rows': len(df),
                'imported_count': imported_count,
                'error_count': len(errors),
                'errors': errors,
                'mapping_used': default_mapping,
                'import_date': datetime.now().isoformat(),
                'status': 'completed' if imported_count > 0 else 'failed'
            }
            
            self.logger.info(f"Importação CSV concluída: {imported_count}/{len(df)} documentos importados")
            
            return result
            
        except Exception as e:
            error_msg = f"Erro na importação CSV: {str(e)}"
            self.logger.error(error_msg)
            return {
                'source_file': csv_file,
                'status': 'failed',
                'error': error_msg,
                'import_date': datetime.now().isoformat()
            }
    
    def import_json_documents(self, json_file: str, structure: str = "array") -> Dict[str, Any]:
        """Importar documentos de arquivo JSON"""
        try:
            json_path = Path(json_file)
            if not json_path.exists():
                raise FileNotFoundError(f"Arquivo JSON não encontrado: {json_file}")
            
            self.logger.info(f"Importando documentos de JSON: {json_file}")
            
            # Ler JSON
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            imported_count = 0
            errors = []
            
            # Processar diferentes estruturas JSON
            if structure == "array" and isinstance(data, list):
                documents = data
            elif structure == "object" and isinstance(data, dict):
                documents = data.get('documents', data.get('data', [data]))
            else:
                documents = [data] if isinstance(data, dict) else []
            
            for idx, doc in enumerate(documents):
                try:
                    if not isinstance(doc, dict):
                        errors.append(f"Item {idx}: formato inválido")
                        continue
                    
                    # Extrair campos
                    title = doc.get('title', doc.get('name', f"Document {idx + 1}"))
                    content = doc.get('content', doc.get('text', doc.get('body', '')))
                    
                    if not title or not content:
                        errors.append(f"Item {idx}: título ou conteúdo faltando")
                        continue
                    
                    # Metadados adicionais
                    metadata = {
                        'original_json': json.dumps(doc, ensure_ascii=False)[:1000],  # Primeiros 1000 chars
                        'import_source': str(json_path.name),
                        'import_index': idx
                    }
                    
                    # Adicionar documento
                    doc_id = self.db_manager.execute_query("""
                        INSERT INTO documents (title, content, source, category, meta_data, created_at)
                        VALUES (%(title)s, %(content)s, %(source)s, %(category)s, %(meta_data)s, NOW())
                        RETURNING id
                    """, {
                        'title': title,
                        'content': content,
                        'source': doc.get('source', f"JSON Import: {json_path.name}"),
                        'category': doc.get('category', 'imported'),
                        'meta_data': json.dumps(metadata)
                    })
                    
                    if doc_id:
                        imported_count += 1
                        self.logger.debug(f"Documento JSON importado: {title}")
                
                except Exception as e:
                    error_msg = f"Item {idx}: {str(e)}"
                    errors.append(error_msg)
                    self.logger.warning(error_msg)
            
            result = {
                'source_file': str(json_path),
                'structure_type': structure,
                'total_items': len(documents),
                'imported_count': imported_count,
                'error_count': len(errors),
                'errors': errors,
                'import_date': datetime.now().isoformat(),
                'status': 'completed' if imported_count > 0 else 'failed'
            }
            
            self.logger.info(f"Importação JSON concluída: {imported_count}/{len(documents)} documentos importados")
            
            return result
            
        except Exception as e:
            error_msg = f"Erro na importação JSON: {str(e)}"
            self.logger.error(error_msg)
            return {
                'source_file': json_file,
                'status': 'failed',
                'error': error_msg,
                'import_date': datetime.now().isoformat()
            }
    
    def import_from_database(self, db_config: Dict[str, Any], query: str, mapping: Dict[str, str] = None) -> Dict[str, Any]:
        """Importar dados de outro banco de dados"""
        try:
            db_type = db_config.get('type', 'postgresql').lower()
            
            self.logger.info(f"Importando de banco {db_type}: {db_config.get('host', 'local')}")
            
            # Conectar ao banco de origem
            if db_type == 'postgresql':
                conn = psycopg2.connect(
                    host=db_config['host'],
                    port=db_config.get('port', 5432),
                    database=db_config['database'],
                    user=db_config['user'],
                    password=db_config['password']
                )
            elif db_type == 'mysql':
                if not MYSQL_AVAILABLE:
                    raise ValueError("MySQL connector não disponível - instale com: pip install mysql-connector-python")
                conn = mysql.connector.connect(
                    host=db_config['host'],
                    port=db_config.get('port', 3306),
                    database=db_config['database'],
                    user=db_config['user'],
                    password=db_config['password']
                )
            elif db_type == 'sqlite':
                conn = sqlite3.connect(db_config['database'])
                conn.row_factory = sqlite3.Row
            else:
                raise ValueError(f"Tipo de banco não suportado: {db_type}")
            
            # Executar consulta
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            
            # Mapeamento de colunas
            default_mapping = {
                'title': 'title',
                'content': 'content',
                'source': 'source',
                'category': 'category'
            }
            
            if mapping:
                default_mapping.update(mapping)
            
            imported_count = 0
            errors = []
            
            for idx, row in enumerate(rows):
                try:
                    # Converter row para dict
                    if db_type == 'sqlite':
                        row_dict = dict(row)
                    else:
                        # PostgreSQL ou MySQL
                        columns = [desc[0] for desc in cursor.description]
                        row_dict = dict(zip(columns, row))
                    
                    # Mapear colunas
                    doc_data = {}
                    for mamute_col, source_col in default_mapping.items():
                        if source_col in row_dict and row_dict[source_col] is not None:
                            doc_data[mamute_col] = str(row_dict[source_col])
                    
                    # Validar dados obrigatórios
                    if 'title' not in doc_data or 'content' not in doc_data:
                        errors.append(f"Registro {idx + 1}: título ou conteúdo faltando")
                        continue
                    
                    # Metadados da migração
                    metadata = {
                        'original_db_type': db_type,
                        'original_query': query,
                        'migration_date': datetime.now().isoformat(),
                        'source_row_data': json.dumps({k: str(v)[:100] for k, v in row_dict.items()}, ensure_ascii=False)
                    }
                    
                    # Adicionar documento
                    doc_id = self.db_manager.execute_query("""
                        INSERT INTO documents (title, content, source, category, meta_data, created_at)
                        VALUES (%(title)s, %(content)s, %(source)s, %(category)s, %(meta_data)s, NOW())
                        RETURNING id
                    """, {
                        'title': doc_data.get('title'),
                        'content': doc_data.get('content'),
                        'source': doc_data.get('source', f"DB Migration: {db_type}"),
                        'category': doc_data.get('category', 'migrated'),
                        'meta_data': json.dumps(metadata)
                    })
                    
                    if doc_id:
                        imported_count += 1
                        self.logger.debug(f"Registro migrado: {doc_data['title']}")
                
                except Exception as e:
                    error_msg = f"Registro {idx + 1}: {str(e)}"
                    errors.append(error_msg)
                    self.logger.warning(error_msg)
            
            # Fechar conexão
            conn.close()
            
            result = {
                'source_database': {
                    'type': db_type,
                    'host': db_config.get('host', 'local'),
                    'database': db_config['database']
                },
                'query_used': query,
                'mapping_used': default_mapping,
                'total_rows': len(rows),
                'imported_count': imported_count,
                'error_count': len(errors),
                'errors': errors,
                'migration_date': datetime.now().isoformat(),
                'status': 'completed' if imported_count > 0 else 'failed'
            }
            
            self.logger.info(f"Migração de banco concluída: {imported_count}/{len(rows)} registros migrados")
            
            return result
            
        except Exception as e:
            error_msg = f"Erro na migração de banco: {str(e)}"
            self.logger.error(error_msg)
            return {
                'source_database': db_config,
                'status': 'failed',
                'error': error_msg,
                'migration_date': datetime.now().isoformat()
            }
    
    def get_supported_formats(self) -> List[str]:
        """Retornar lista de formatos suportados"""
        return ['CSV', 'JSON', 'Excel', 'PostgreSQL', 'MySQL', 'SQLite']
    
    def export_to_csv(self, output_file: str, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Exportar documentos para CSV"""
        try:
            output_path = self.export_dir / output_file
            
            self.logger.info(f"Exportando documentos para CSV: {output_path}")
            
            # Construir query com filtros
            where_conditions = []
            params = {}
            
            if filters:
                if 'category' in filters:
                    where_conditions.append("category = %(category)s")
                    params['category'] = filters['category']
                
                if 'source' in filters:
                    where_conditions.append("source LIKE %(source)s")
                    params['source'] = f"%{filters['source']}%"
                
                if 'date_from' in filters:
                    where_conditions.append("created_at >= %(date_from)s")
                    params['date_from'] = filters['date_from']
                
                if 'date_to' in filters:
                    where_conditions.append("created_at <= %(date_to)s")
                    params['date_to'] = filters['date_to']
            
            where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
            
            query = f"""
                SELECT 
                    id,
                    title,
                    content,
                    source,
                    category,
                    created_at,
                    meta_data
                FROM documents 
                {where_clause}
                ORDER BY created_at DESC
            """
            
            # Executar query
            documents = self.db_manager.execute_query(query, params) or []
            
            if not documents:
                return {
                    'output_file': str(output_path),
                    'exported_count': 0,
                    'status': 'no_data',
                    'export_date': datetime.now().isoformat()
                }
            
            # Criar DataFrame e exportar
            df = pd.DataFrame(documents)
            df.to_csv(output_path, index=False, encoding='utf-8')
            
            file_size = output_path.stat().st_size
            
            result = {
                'output_file': str(output_path),
                'filters_applied': filters or {},
                'exported_count': len(documents),
                'file_size_bytes': file_size,
                'file_size_mb': round(file_size / (1024*1024), 2),
                'export_date': datetime.now().isoformat(),
                'status': 'completed'
            }
            
            self.logger.info(f"Exportação CSV concluída: {len(documents)} documentos exportados")
            
            return result
            
        except Exception as e:
            error_msg = f"Erro na exportação CSV: {str(e)}"
            self.logger.error(error_msg)
            return {
                'output_file': output_file,
                'status': 'failed',
                'error': error_msg,
                'export_date': datetime.now().isoformat()
            }
    
    def export_to_json(self, output_file: str, filters: Dict[str, Any] = None, include_metadata: bool = True) -> Dict[str, Any]:
        """Exportar documentos para JSON"""
        try:
            output_path = self.export_dir / output_file
            
            self.logger.info(f"Exportando documentos para JSON: {output_path}")
            
            # Usar mesma lógica de filtros do CSV
            where_conditions = []
            params = {}
            
            if filters:
                if 'category' in filters:
                    where_conditions.append("category = %(category)s")
                    params['category'] = filters['category']
                
                if 'source' in filters:
                    where_conditions.append("source LIKE %(source)s")
                    params['source'] = f"%{filters['source']}%"
                
                if 'date_from' in filters:
                    where_conditions.append("created_at >= %(date_from)s")
                    params['date_from'] = filters['date_from']
                
                if 'date_to' in filters:
                    where_conditions.append("created_at <= %(date_to)s")
                    params['date_to'] = filters['date_to']
            
            where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
            
            query = f"""
                SELECT 
                    id,
                    title,
                    content,
                    source,
                    category,
                    created_at,
                    meta_data
                FROM documents 
                {where_clause}
                ORDER BY created_at DESC
            """
            
            # Executar query
            documents = self.db_manager.execute_query(query, params) or []
            
            if not documents:
                export_data = {'documents': [], 'export_info': {}}
            else:
                # Processar documentos
                processed_docs = []
                for doc in documents:
                    processed_doc = {
                        'id': doc['id'],
                        'title': doc['title'],
                        'content': doc['content'],
                        'source': doc['source'],
                        'category': doc['category'],
                        'created_at': doc['created_at'].isoformat() if doc['created_at'] else None
                    }
                    
                    # Incluir metadata se solicitado
                    if include_metadata and doc.get('meta_data'):
                        try:
                            if isinstance(doc['meta_data'], str):
                                processed_doc['metadata'] = json.loads(doc['meta_data'])
                            else:
                                processed_doc['metadata'] = doc['meta_data']
                        except:
                            processed_doc['metadata'] = {'raw': str(doc['meta_data'])}
                    
                    processed_docs.append(processed_doc)
                
                export_data = {
                    'documents': processed_docs,
                    'export_info': {
                        'total_count': len(processed_docs),
                        'filters_applied': filters or {},
                        'include_metadata': include_metadata,
                        'export_date': datetime.now().isoformat(),
                        'exported_by': 'Mamute Data Migration Utilities',
                        'version': '1.0'
                    }
                }
            
            # Salvar JSON
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
            
            file_size = output_path.stat().st_size
            
            result = {
                'output_file': str(output_path),
                'filters_applied': filters or {},
                'exported_count': len(documents),
                'include_metadata': include_metadata,
                'file_size_bytes': file_size,
                'file_size_mb': round(file_size / (1024*1024), 2),
                'export_date': datetime.now().isoformat(),
                'status': 'completed'
            }
            
            self.logger.info(f"Exportação JSON concluída: {len(documents)} documentos exportados")
            
            return result
            
        except Exception as e:
            error_msg = f"Erro na exportação JSON: {str(e)}"
            self.logger.error(error_msg)
            return {
                'output_file': output_file,
                'status': 'failed',
                'error': error_msg,
                'export_date': datetime.now().isoformat()
            }
    
    def create_migration_report(self, operations: List[Dict[str, Any]]) -> str:
        """Criar relatório de migração"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = self.migration_dir / f"migration_report_{timestamp}.json"
            
            total_imported = sum(op.get('imported_count', 0) for op in operations)
            total_exported = sum(op.get('exported_count', 0) for op in operations)
            total_errors = sum(op.get('error_count', 0) for op in operations)
            
            report = {
                'migration_report': {
                    'created_at': datetime.now().isoformat(),
                    'summary': {
                        'total_operations': len(operations),
                        'total_imported': total_imported,
                        'total_exported': total_exported,
                        'total_errors': total_errors,
                        'successful_operations': len([op for op in operations if op.get('status') == 'completed']),
                        'failed_operations': len([op for op in operations if op.get('status') == 'failed'])
                    },
                    'operations': operations
                }
            }
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"Relatório de migração criado: {report_file}")
            
            return str(report_file)
            
        except Exception as e:
            self.logger.error(f"Erro ao criar relatório de migração: {e}")
            return ""

def main():
    """Função principal para demonstrar utilitários de migração"""
    print("🐘 UTILITÁRIOS DE MIGRAÇÃO DO MAMUTE")
    print("=" * 50)
    
    try:
        migration_utils = DataMigrationUtilities()
        operations = []
        
        print("\\n📥 Exemplo de importação de CSV")
        # Exemplo de importação seria aqui
        print("💡 Para importar CSV: migration_utils.import_csv_documents('arquivo.csv')")
        
        print("\\n📤 Exemplo de exportação para JSON")
        # Exemplo de exportação
        export_result = migration_utils.export_to_json(
            'mamute_export_example.json',
            filters={'category': 'imported'}
        )
        operations.append(export_result)
        
        print(f"✅ Exportação: {export_result.get('status', 'unknown')}")
        if export_result.get('exported_count', 0) > 0:
            print(f"📊 Documentos exportados: {export_result['exported_count']}")
        
        # Criar relatório
        if operations:
            report_file = migration_utils.create_migration_report(operations)
            if report_file:
                print(f"\\n📋 Relatório criado: {Path(report_file).name}")
        
        print("\\n✅ Utilitários de migração configurados!")
        print("💡 Execute funções individuais conforme necessário")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()