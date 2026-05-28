"""
Sistema de Notificações do Mamute
Notificações em tempo real via WebSocket, email e logs
"""
import asyncio
import inspect
import json
import os
import smtplib
import sys
from dataclasses import dataclass, field
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import websockets

# Adicionar o diretório principal ao path
ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"
APPS_DIR = SRC_DIR / "apps"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(APPS_DIR) not in sys.path:
    sys.path.insert(0, str(APPS_DIR))

from src.utils.config import Config
from src.utils.logger import setup_logger
from src.database.connection import DatabaseManager


def _empty_metadata() -> Dict[str, Any]:
    return {}


class NotificationLevel(Enum):
    """Níveis de notificação"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    SUCCESS = "success"

class NotificationChannel(Enum):
    """Canais de notificação"""
    WEBSOCKET = "websocket"
    EMAIL = "email"
    LOG = "log"
    DATABASE = "database"
    CONSOLE = "console"

@dataclass
class Notification:
    """Estrutura de uma notificação"""
    id: str
    title: str
    message: str
    level: NotificationLevel
    timestamp: datetime
    source: str = "Mamute"
    channels: List[NotificationChannel] = field(default_factory=lambda: [NotificationChannel.CONSOLE, NotificationChannel.LOG])
    metadata: Dict[str, Any] = field(default_factory=_empty_metadata)
    read: bool = False

class NotificationSystem:
    """Sistema completo de notificações do Mamute"""

    def __init__(self, config_file: str = ".env"):
        """Inicializar sistema de notificações"""
        self.config = Config(config_file)
        self.logger = setup_logger("NotificationSystem")
        self.db_manager = DatabaseManager(self.config)

        # Configurações de email (opcionais)
        self.email_config: Any = {
            'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('SMTP_PORT', 587)),
            'email_user': os.getenv('EMAIL_USER'),
            'email_password': os.getenv('EMAIL_PASSWORD'),
            'email_from': os.getenv('EMAIL_FROM'),
            'email_to': os.getenv('EMAIL_TO', '').split(',') if os.getenv('EMAIL_TO') else []
        }

        # WebSocket connections
        self.websocket_connections: Any = set()
        self.websocket_server: Any = None

        # Subscribers para notificações programáticas
        self.subscribers: Any = {}

        # Cache de notificações recentes
        self.recent_notifications: List[Notification] = []
        self.max_recent_notifications = 100
        
        # Inicializar tabela de notificações
        self._setup_notifications_table()
        
        self.logger.info("Sistema de notificações do Mamute inicializado")
    
    def _setup_notifications_table(self):
        """Criar tabela de notificações se não existir"""
        try:
            self.db_manager.execute_query("""
                CREATE TABLE IF NOT EXISTS notifications (
                    id VARCHAR(255) PRIMARY KEY,
                    title VARCHAR(500) NOT NULL,
                    message TEXT NOT NULL,
                    level VARCHAR(50) NOT NULL,
                    source VARCHAR(255) DEFAULT 'Mamute',
                    channels JSONB,
                    metadata JSONB,
                    read BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Criar índices
            self.db_manager.execute_query("""
                CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at DESC)
            """)
            
            self.db_manager.execute_query("""
                CREATE INDEX IF NOT EXISTS idx_notifications_level ON notifications(level)
            """)
            
            self.db_manager.execute_query("""
                CREATE INDEX IF NOT EXISTS idx_notifications_read ON notifications(read)
            """)
            
        except Exception as e:
            self.logger.warning(f"Erro ao criar tabela de notificações: {e}")
    
    async def send_notification(self, notification: Notification) -> bool:
        """Enviar notificação através de todos os canais especificados"""
        try:
            success_count = 0

            # Enviar para cada canal especificado
            for channel in notification.channels:
                try:
                    if channel == NotificationChannel.CONSOLE:
                        await self._send_to_console(notification)
                        success_count += 1
                    
                    elif channel == NotificationChannel.LOG:
                        await self._send_to_log(notification)
                        success_count += 1
                    
                    elif channel == NotificationChannel.DATABASE:
                        await self._send_to_database(notification)
                        success_count += 1
                    
                    elif channel == NotificationChannel.WEBSOCKET:
                        await self._send_to_websockets(notification)
                        success_count += 1
                    
                    elif channel == NotificationChannel.EMAIL:
                        await self._send_to_email(notification)
                        success_count += 1
                
                except Exception as e:
                    self.logger.warning(f"Erro ao enviar para canal {channel.value}: {e}")
            
            # Adicionar ao cache de notificações recentes
            self.recent_notifications.append(notification)
            if len(self.recent_notifications) > self.max_recent_notifications:
                self.recent_notifications = self.recent_notifications[-self.max_recent_notifications:]
            
            # Notificar subscribers
            await self._notify_subscribers(notification)
            
            return success_count > 0
            
        except Exception as e:
            self.logger.error(f"Erro ao enviar notificação: {e}")
            return False
    
    async def _send_to_console(self, notification: Notification):
        """Enviar notificação para console"""
        # Emoji baseado no nível
        emoji_map = {
            NotificationLevel.INFO: "ℹ️",
            NotificationLevel.WARNING: "⚠️",
            NotificationLevel.ERROR: "❌",
            NotificationLevel.CRITICAL: "🚨",
            NotificationLevel.SUCCESS: "✅"
        }
        
        emoji = emoji_map.get(notification.level, "📢")
        timestamp_str = notification.timestamp.strftime("%H:%M:%S")
        
        print(f"{emoji} [{timestamp_str}] {notification.title}")
        print(f"   {notification.message}")
        if notification.source != "Mamute":
            print(f"   Fonte: {notification.source}")
        print()
    
    async def _send_to_log(self, notification: Notification):
        """Enviar notificação para logs"""
        log_message = f"{notification.title}: {notification.message}"
        
        if notification.level == NotificationLevel.INFO:
            self.logger.info(log_message)
        elif notification.level == NotificationLevel.WARNING:
            self.logger.warning(log_message)
        elif notification.level == NotificationLevel.ERROR:
            self.logger.error(log_message)
        elif notification.level == NotificationLevel.CRITICAL:
            self.logger.critical(log_message)
        elif notification.level == NotificationLevel.SUCCESS:
            self.logger.info(f"SUCCESS: {log_message}")
    
    async def _send_to_database(self, notification: Notification):
        """Salvar notificação no banco de dados"""
        try:
            self.db_manager.execute_query("""
                INSERT INTO notifications (id, title, message, level, source, channels, metadata, created_at)
                VALUES (%(id)s, %(title)s, %(message)s, %(level)s, %(source)s, %(channels)s, %(metadata)s, %(created_at)s)
            """, {
                'id': notification.id,
                'title': notification.title,
                'message': notification.message,
                'level': notification.level.value,
                'source': notification.source,
                'channels': json.dumps([ch.value for ch in notification.channels]),
                'metadata': json.dumps(notification.metadata),
                'created_at': notification.timestamp
            })
        except Exception as e:
            self.logger.warning(f"Erro ao salvar notificação no banco: {e}")
    
    async def _send_to_websockets(self, notification: Notification):
        """Enviar notificação via WebSocket para clientes conectados"""
        if not self.websocket_connections:
            return

        notification_data: Any = {
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'level': notification.level.value,
            'timestamp': notification.timestamp.isoformat(),
            'source': notification.source,
            'metadata': notification.metadata
        }

        message = json.dumps({
            'type': 'notification',
            'data': notification_data
        })

        # Enviar para todas as conexões ativas
        for websocket in self.websocket_connections.copy():
            try:
                await websocket.send(message)
            except Exception as e:
                self.logger.debug(f"Conexão WebSocket perdida: {e}")
                self.websocket_connections.discard(websocket)

    async def _send_to_email(self, notification: Notification):
        """Enviar notificação por email"""
        try:
            if not self.email_config['email_user'] or not self.email_config['email_to']:
                self.logger.debug("Email não configurado, pulando envio")
                return
            
            # Criar mensagem de email
            msg = MIMEMultipart()
            msg['From'] = self.email_config['email_from'] or self.email_config['email_user']
            msg['To'] = ', '.join(self.email_config['email_to'])
            msg['Subject'] = f"[Mamute {notification.level.value.upper()}] {notification.title}"
            
            # Corpo do email
            body = f"""Notificação do Sistema Mamute

Título: {notification.title}
Nível: {notification.level.value.upper()}
Fonte: {notification.source}
Data/Hora: {notification.timestamp.strftime('%d/%m/%Y %H:%M:%S')}

Mensagem:
{notification.message}

{'-' * 50}
Este é um email automático do sistema Mamute.
"""
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Enviar email
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['email_user'], self.email_config['email_password'])
            
            text = msg.as_string()
            server.sendmail(
                self.email_config['email_user'],
                self.email_config['email_to'],
                text
            )
            server.quit()
            
            self.logger.debug(f"Email de notificação enviado: {notification.title}")
            
        except Exception as e:
            self.logger.warning(f"Erro ao enviar email: {e}")
    
    async def _notify_subscribers(self, notification: Notification):
        """Notificar subscribers programáticos"""
        for event_type, callbacks in self.subscribers.items():
            if event_type == 'all' or event_type == notification.level.value:
                for callback in callbacks:
                    try:
                        result = callback(notification)
                        if inspect.isawaitable(result):
                            await result
                    except Exception as e:
                        self.logger.warning(f"Erro em subscriber callback: {e}")

    def subscribe(self, event_type: str, callback: Any):
        """Inscrever callback para receber notificações"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []

        self.subscribers[event_type].append(callback)
        self.logger.debug(f"Subscriber adicionado para {event_type}")

    def create_notification(
        self,
        title: str,
        message: str,
        level: NotificationLevel = NotificationLevel.INFO,
        channels: Optional[List[NotificationChannel]] = None,
        source: str = "Mamute",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Notification:
        """Criar uma nova notificação"""
        notification_id = f"{source}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(title + message) % 10000}"

        return Notification(
            id=notification_id,
            title=title,
            message=message,
            level=level,
            timestamp=datetime.now(),
            source=source,
            channels=channels or [NotificationChannel.CONSOLE, NotificationChannel.LOG],
            metadata=metadata or {}
        )

    async def notify_info(self, title: str, message: str, **kwargs: Any):
        """Enviar notificação de informação"""
        notification = self.create_notification(title, message, NotificationLevel.INFO, **kwargs)
        return await self.send_notification(notification)

    async def notify_warning(self, title: str, message: str, **kwargs: Any):
        """Enviar notificação de aviso"""
        notification = self.create_notification(title, message, NotificationLevel.WARNING, **kwargs)
        return await self.send_notification(notification)

    async def notify_error(self, title: str, message: str, **kwargs: Any):
        """Enviar notificação de erro"""
        notification = self.create_notification(title, message, NotificationLevel.ERROR, **kwargs)
        return await self.send_notification(notification)

    async def notify_critical(self, title: str, message: str, **kwargs: Any):
        """Enviar notificação crítica"""
        notification = self.create_notification(title, message, NotificationLevel.CRITICAL, **kwargs)
        return await self.send_notification(notification)

    async def notify_success(self, title: str, message: str, **kwargs: Any):
        """Enviar notificação de sucesso"""
        notification = self.create_notification(title, message, NotificationLevel.SUCCESS, **kwargs)
        return await self.send_notification(notification)

    def get_recent_notifications(self, limit: int = 20, level: Optional[NotificationLevel] = None) -> List[Dict[str, Any]]:
        """Obter notificações recentes"""
        notifications = self.recent_notifications
        
        if level:
            notifications = [n for n in notifications if n.level == level]
        
        notifications = sorted(notifications, key=lambda x: x.timestamp, reverse=True)
        
        return [
            {
                'id': n.id,
                'title': n.title,
                'message': n.message,
                'level': n.level.value,
                'timestamp': n.timestamp.isoformat(),
                'source': n.source,
                'read': n.read,
                'metadata': n.metadata
            }
            for n in notifications[:limit]
        ]
    
    def get_notifications_from_db(
        self,
        limit: int = 50,
        level: Optional[str] = None,
        read: Optional[bool] = None,
        hours_ago: int = 24,
    ) -> List[Dict[str, Any]]:
        """Obter notificações do banco de dados"""
        try:
            conditions = ["created_at >= NOW() - INTERVAL '%s hours'" % hours_ago]
            params: Dict[str, Any] = {}

            if level:
                conditions.append("level = %(level)s")
                params['level'] = level

            if read is not None:
                conditions.append("read = %(read)s")
                params['read'] = read

            where_clause = "WHERE " + " AND ".join(conditions)

            query = f"""
                SELECT id, title, message, level, source, metadata, read, created_at
                FROM notifications
                {where_clause}
                ORDER BY created_at DESC
                LIMIT {limit}
            """

            notifications = self.db_manager.execute_query(query, params) or []

            return [
                {
                    'id': n['id'],
                    'title': n['title'],
                    'message': n['message'],
                    'level': n['level'],
                    'source': n['source'],
                    'read': n['read'],
                    'created_at': n['created_at'].isoformat() if n['created_at'] else None,
                    'metadata': json.loads(n['metadata']) if n['metadata'] else {}
                }
                for n in notifications
            ]

        except Exception as e:
            self.logger.error(f"Erro ao buscar notificações do banco: {e}")
            return []

    async def mark_as_read(self, notification_id: str) -> bool:
        """Marcar notificação como lida"""
        try:
            self.db_manager.execute_query(
                "UPDATE notifications SET read = TRUE WHERE id = %(id)s",
                {'id': notification_id}
            )

            # Também atualizar no cache
            for notification in self.recent_notifications:
                if notification.id == notification_id:
                    notification.read = True
                    break

            return True

        except Exception as e:
            self.logger.error(f"Erro ao marcar notificação como lida: {e}")
            return False
    
    async def start_websocket_server(self, host: str = "localhost", port: int = 8765):
        """Iniciar servidor WebSocket para notificações em tempo real"""

        async def handle_websocket(websocket: Any, path: Any):
            """Handler para conexões WebSocket"""
            self.websocket_connections.add(websocket)
            self.logger.info(f"Nova conexão WebSocket: {websocket.remote_address}")

            try:
                # Enviar notificações recentes ao conectar
                recent_notifications = self.get_recent_notifications(10)
                await websocket.send(json.dumps({
                    'type': 'initial_notifications',
                    'data': recent_notifications
                }))

                # Manter conexão viva
                await websocket.wait_closed()
            except Exception as e:
                self.logger.debug(f"Conexão WebSocket encerrada: {e}")
            finally:
                self.websocket_connections.discard(websocket)

        try:
            self.websocket_server = await websockets.serve(handle_websocket, host, port)
            self.logger.info(f"Servidor WebSocket de notificações iniciado em ws://{host}:{port}")
        except Exception as e:
            self.logger.error(f"Erro ao iniciar servidor WebSocket: {e}")

# Instância global do sistema de notificações
notification_system = NotificationSystem()

async def notify_info(title: str, message: str, **kwargs: Any):
    """Função de conveniência para notificações de info"""
    return await notification_system.notify_info(title, message, **kwargs)

async def notify_warning(title: str, message: str, **kwargs: Any):
    """Função de conveniência para notificações de aviso"""
    return await notification_system.notify_warning(title, message, **kwargs)

async def notify_error(title: str, message: str, **kwargs: Any):
    """Função de conveniência para notificações de erro"""
    return await notification_system.notify_error(title, message, **kwargs)

async def notify_critical(title: str, message: str, **kwargs: Any):
    """Função de conveniência para notificações críticas"""
    return await notification_system.notify_critical(title, message, **kwargs)

async def notify_success(title: str, message: str, **kwargs: Any):
    """Função de conveniência para notificações de sucesso"""
    return await notification_system.notify_success(title, message, **kwargs)

def main():
    """Função principal para demonstrar sistema de notificações"""
    print("🐘 SISTEMA DE NOTIFICAÇÕES DO MAMUTE")
    print("=" * 50)
    
    async def demo_notifications():
        """Demo das notificações"""
        # Demonstrar diferentes tipos de notificações
        await notify_info("Sistema Iniciado", "O Mamute foi iniciado com sucesso!")
        await notify_warning("Memória Alta", "Uso de memória acima de 80%")
        await notify_success("Backup Concluído", "Backup automático realizado com sucesso")
        await notify_error("Falha na Conexão", "Erro temporário de conexão com banco")
        
        print("\\n📋 Notificações recentes:")
        recent = notification_system.get_recent_notifications(5)
        for notif in recent:
            print(f"- [{notif['level'].upper()}] {notif['title']}: {notif['message']}")
        
        print("\\n✅ Sistema de notificações configurado!")
        print("💡 Use as funções notify_* para enviar notificações")
    
    # Executar demo
    asyncio.run(demo_notifications())

if __name__ == "__main__":
    main()