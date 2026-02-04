// JavaScript para interface do Mamute
class MamuteClient {
    constructor() {
        this.sessionId = null;
        this.isConnected = false;
        this.messageQueue = [];
        this.init();
    }

    async init() {
        await this.startSession();
        this.setupEventListeners();
    }

    async startSession() {
        try {
            const response = await fetch('/session/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({})
            });
            
            const data = await response.json();
            this.sessionId = data.session_id;
            this.isConnected = true;
            
            this.updateStatus('online', 'Conectado');
            this.addMessage('🐘 Mamute: Olá! Sou o Mamute, sua IA especialista em PostgreSQL. Como posso ajudar você hoje?', 'mamute');
            
            // Habilitar interface
            document.getElementById('messageInput').disabled = false;
            document.getElementById('sendButton').disabled = false;
            
        } catch (error) {
            console.error('Erro ao iniciar sessão:', error);
            this.updateStatus('offline', 'Erro de conexão');
            this.addMessage('❌ Erro ao conectar com Mamute: ' + error.message, 'system');
        }
    }

    async sendMessage(message) {
        if (!message.trim() || !this.sessionId) return;

        // Adicionar mensagem do usuário
        this.addMessage('👤 Você: ' + message, 'user');
        
        // Desabilitar input temporariamente
        const input = document.getElementById('messageInput');
        const button = document.getElementById('sendButton');
        
        input.value = '';
        button.disabled = true;
        button.innerHTML = '<span class="loading"></span> Pensando...';

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: message,
                    session_id: this.sessionId,
                    use_context: true
                })
            });

            if (!response.ok) {
                throw new Error(`Erro ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            
            // Adicionar resposta do Mamute
            this.addMessage('🐘 Mamute: ' + data.response, 'mamute');
            
            // Mostrar estatísticas se disponíveis
            if (data.tokens_used) {
                this.addMessage(
                    `📊 Tokens: ${data.tokens_used} | ⏱️ Tempo: ${data.response_time.toFixed(2)}s`, 
                    'system'
                );
            }
            
            // Mostrar documentos relevantes se houver
            if (data.relevant_documents && data.relevant_documents.length > 0) {
                this.addMessage('📄 Documentos relevantes encontrados:', 'system');
                data.relevant_documents.forEach(doc => {
                    this.addMessage(
                        `• ${doc.title} (similaridade: ${doc.similarity.toFixed(3)})`, 
                        'system'
                    );
                });
            }
            
        } catch (error) {
            console.error('Erro ao enviar mensagem:', error);
            this.addMessage('❌ Erro: ' + error.message, 'system');
        } finally {
            // Reabilitar interface
            button.disabled = false;
            button.innerHTML = 'Enviar';
            input.focus();
        }
    }

    addMessage(text, type) {
        const messagesContainer = document.getElementById('chatMessages');
        if (!messagesContainer) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        
        // Converter quebras de linha para HTML e preservar formatação
        const formattedText = text
            .replace(/\n/g, '<br>')
            .replace(/\t/g, '&nbsp;&nbsp;&nbsp;&nbsp;')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')  // **bold**
            .replace(/\*(.*?)\*/g, '<em>$1</em>')              // *italic*
            .replace(/`(.*?)`/g, '<code>$1</code>');           // `code`
        
        messageDiv.innerHTML = formattedText;
        
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    updateStatus(status, text) {
        const statusElement = document.getElementById('connectionStatus');
        if (statusElement) {
            statusElement.className = `status ${status}`;
            statusElement.textContent = text;
        }
    }

    setupEventListeners() {
        // Enter para enviar mensagem
        const input = document.getElementById('messageInput');
        if (input) {
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage(input.value);
                }
            });
        }

        // Botão enviar
        const button = document.getElementById('sendButton');
        if (button) {
            button.addEventListener('click', () => {
                this.sendMessage(input.value);
            });
        }

        // Auto-focus no input
        if (input) {
            input.focus();
        }
    }
}

// Utilitários para dashboard
class DashboardUtils {
    static async loadHealthStatus() {
        try {
            const response = await fetch('/health');
            const data = await response.json();
            
            this.updateHealthDisplay(data);
            
        } catch (error) {
            console.error('Erro ao carregar status:', error);
        }
    }

    static updateHealthDisplay(data) {
        // Atualizar status do sistema
        const statusElement = document.getElementById('systemStatus');
        if (statusElement) {
            statusElement.className = `status ${data.status === 'healthy' ? 'online' : 'warning'}`;
            statusElement.textContent = data.status === 'healthy' ? 'Sistema OK' : 'Atenção';
        }

        // Atualizar status do banco
        const dbElement = document.getElementById('dbStatus');
        if (dbElement) {
            dbElement.className = `status ${data.database_connected ? 'online' : 'offline'}`;
            dbElement.textContent = data.database_connected ? 'Conectado' : 'Desconectado';
        }

        // Atualizar informações do banco
        document.getElementById('dbHost').textContent = data.postgres_host || 'N/A';
        document.getElementById('dbName').textContent = data.postgres_db || 'N/A';
    }

    static async executeQuery(query) {
        if (!query.trim()) {
            alert('Por favor, digite uma consulta SQL');
            return;
        }

        if (!query.trim().toUpperCase().startsWith('SELECT')) {
            alert('Apenas consultas SELECT são permitidas');
            return;
        }

        try {
            const response = await fetch('/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query })
            });

            const data = await response.json();
            
            if (response.ok) {
                this.displayQueryResults(data);
            } else {
                alert('Erro na consulta: ' + data.detail);
            }
            
        } catch (error) {
            alert('Erro ao executar consulta: ' + error.message);
        }
    }

    static displayQueryResults(data) {
        const resultsDiv = document.getElementById('queryResults');
        if (!resultsDiv) return;

        if (!data.results || data.results.length === 0) {
            resultsDiv.innerHTML = '<p>Nenhum resultado encontrado.</p>';
            return;
        }

        // Criar tabela HTML
        let html = `<h3>Resultados (${data.row_count} linhas):</h3><table class="results-table"><thead><tr>`;
        
        // Cabeçalhos
        Object.keys(data.results[0]).forEach(key => {
            html += `<th>${key}</th>`;
        });
        html += '</tr></thead><tbody>';

        // Dados
        data.results.forEach(row => {
            html += '<tr>';
            Object.values(row).forEach(value => {
                html += `<td>${value !== null ? value : 'NULL'}</td>`;
            });
            html += '</tr>';
        });

        html += '</tbody></table>';
        resultsDiv.innerHTML = html;
    }
}

// Inicializar quando DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    // Inicializar cliente de chat se estiver na página de chat
    if (document.getElementById('chatMessages')) {
        window.mamuteClient = new MamuteClient();
    }
    
    // Inicializar dashboard se estiver na página principal
    if (document.getElementById('systemStatus')) {
        DashboardUtils.loadHealthStatus();
        // Atualizar a cada 30 segundos
        setInterval(() => DashboardUtils.loadHealthStatus(), 30000);
    }
});

// Exportar para uso global
window.MamuteClient = MamuteClient;
window.DashboardUtils = DashboardUtils;