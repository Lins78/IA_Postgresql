// JavaScript para interface do Mamute - Agora com suporte a imagens!
class MamuteClient {
    constructor() {
        this.sessionId = null;
        this.isConnected = false;
        this.messageQueue = [];
        this.currentImage = null; // Para armazenar imagem anexada
        this.init();
    }

    async init() {
        await this.startSession();
        this.setupEventListeners();
        this.setupImageUpload(); // Configurar upload de imagens
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
            this.addMessage('🐘 Mamute: Olá! Sou o Mamute, sua IA especialista em PostgreSQL. 📸 <strong>Agora também posso analisar imagens!</strong> Como posso ajudar você hoje?', 'mamute');
            
            // Habilitar interface
            document.getElementById('messageInput').disabled = false;
            document.getElementById('sendButton').disabled = false;
            
        } catch (error) {
            console.error('Erro ao iniciar sessão:', error);
            this.updateStatus('offline', 'Erro de conexão');
            this.addMessage('❌ Erro ao conectar com Mamute: ' + error.message, 'system');
        }
    }

    setupImageUpload() {
        const attachButton = document.getElementById('attachButton');
        const fileInput = document.getElementById('fileInput');
        
        if (!attachButton || !fileInput) {
            console.log('Botões de imagem não encontrados, usando interface básica');
            return;
        }

        attachButton.addEventListener('click', () => {
            fileInput.click();
        });
        
        fileInput.addEventListener('change', async (e) => {
            const file = e.target.files[0];
            if (!file) return;
            
            if (!file.type.startsWith('image/')) {
                alert('Por favor, selecione apenas arquivos de imagem.');
                return;
            }
            
            if (file.size > 10 * 1024 * 1024) {
                alert('Arquivo muito grande. Máximo 10MB.');
                return;
            }
            
            try {
                const formData = new FormData();
                formData.append('file', file);
                
                const response = await fetch('/upload-image', {
                    method: 'POST',
                    body: formData
                });
                
                if (response.ok) {
                    const data = await response.json();
                    this.currentImage = data;
                    this.showImagePreview(data);
                } else {
                    const error = await response.json();
                    alert('Erro ao fazer upload: ' + error.detail);
                }
            } catch (error) {
                alert('Erro ao fazer upload da imagem.');
                console.error('Erro no upload:', error);
            }
        });
    }

    showImagePreview(imageData) {
        const attachmentArea = document.getElementById('attachmentArea');
        const imagePreview = document.getElementById('imagePreview');
        
        if (!attachmentArea || !imagePreview) return;
        
        imagePreview.innerHTML = `
            <div class="image-preview-container">
                <img src="data:${imageData.content_type};base64,${imageData.base64_data}" class="image-preview">
                <button type="button" class="remove-image" onclick="window.mamuteClient?.removeImage()">&times;</button>
            </div>
            <div class="file-info">📸 ${imageData.original_name} (${Math.round(imageData.size/1024)}KB)</div>
        `;
        
        attachmentArea.style.display = 'block';
    }

    removeImage() {
        this.currentImage = null;
        const attachmentArea = document.getElementById('attachmentArea');
        const imagePreview = document.getElementById('imagePreview');
        const fileInput = document.getElementById('fileInput');
        
        if (attachmentArea) attachmentArea.style.display = 'none';
        if (imagePreview) imagePreview.innerHTML = '';
        if (fileInput) fileInput.value = '';
    }

    async sendMessage(message) {
        if (!message.trim() && !this.currentImage) return;
        if (!this.sessionId) return;

        // Preparar dados da mensagem
        const messageData = {
            message: message || '📸 Imagem enviada',
            session_id: this.sessionId,
            use_context: true
        };

        // Adicionar dados da imagem se houver
        if (this.currentImage) {
            messageData.image_data = this.currentImage.base64_data;
            messageData.image_filename = this.currentImage.filename;
        }

        // Adicionar mensagem do usuário (com imagem se houver)
        let userMessage = '👤 Você: ' + (message || '📸 Imagem enviada');
        if (this.currentImage) {
            userMessage = `<div><img src="${this.currentImage.url}" style="max-width: 300px; max-height: 200px; border-radius: 8px; margin-bottom: 10px; border: 2px solid #007bff;"><br>${userMessage}</div>`;
        }
        this.addMessage(userMessage, 'user');
        
        // Limpar imagem atual
        this.removeImage();

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
                body: JSON.stringify(messageData) // Usar messageData que pode conter imagem
            });

            if (!response.ok) {
                throw new Error(`Erro ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            
            // Adicionar resposta do Mamute
            let mamuteResponse = '🐘 Mamute: ' + data.response;
            if (data.image_processed) {
                mamuteResponse = '🐘 Mamute 📸: ' + data.response;
            }
            this.addMessage(mamuteResponse, 'mamute');
            
            // Mostrar informações do modo proativo se disponível
            if (data.proactive_mode && data.applied_improvements?.length > 0) {
                this.addMessage(
                    `🚀 Modo Proativo: ${data.applied_improvements.length} melhorias aplicadas automaticamente!`,
                    'proactive-success'
                );
                
                data.applied_improvements.forEach(improvement => {
                    this.addMessage(
                        `✅ ${improvement.action}: ${improvement.description}`,
                        'improvement'
                    );
                });
            }
            
            // Mostrar sugestões de melhorias se houver
            if (data.suggested_improvements?.length > 0) {
                this.addMessage('💡 Sugestões de melhorias:', 'system');
                data.suggested_improvements.forEach(suggestion => {
                    this.addMessage(
                        `💭 ${suggestion.action}: ${suggestion.description} (Confiança: ${(suggestion.confidence * 100).toFixed(1)}%)`,
                        'suggestion'
                    );
                });
            }
            
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
            
            // Mostrar inspeção de banco se disponível
            if (data.database_inspection) {
                const di = data.database_inspection;
                const dbHtml = `
                    <div class="db-inspection">
                        <strong>🔎 Informações do Banco</strong><br>
                        <strong>Bancos (${di.database_count || 0}):</strong> ${di.databases && di.databases.length ? di.databases.join(', ') : 'nenhum'}<br>
                        <strong>Banco atual:</strong> ${di.current_database || 'N/D'}<br>
                        <strong>Schemas (${di.schema_count || 0}):</strong> ${di.schemas && di.schemas.length ? di.schemas.join(', ') : 'nenhum'}<br>
                        <strong>Tabelas (${di.table_count || 0}):</strong> ${di.tables && di.tables.length ? di.tables.join(', ') : 'nenhuma'}
                    </div>
                `;
                this.addMessage(dbHtml, 'system');
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
        
        // Controles do modo proativo
        this.setupProactiveControls();
    }
    
    async setupProactiveControls() {
        // Verificar status inicial do modo proativo
        try {
            const response = await fetch('/proactive/status');
            const data = await response.json();
            
            this.updateProactiveDisplay(data.proactive_mode);
        } catch (error) {
            console.warn('Modo proativo não disponível:', error);
        }
    }
    
    async toggleProactiveMode() {
        try {
            const response = await fetch('/proactive/toggle', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            const data = await response.json();
            this.updateProactiveDisplay(data.proactive_mode);
            
            this.addMessage(
                `🔄 ${data.message}`, 
                data.proactive_mode ? 'proactive-success' : 'system'
            );
            
        } catch (error) {
            console.error('Erro ao alterar modo proativo:', error);
            this.addMessage('❌ Erro ao alterar modo proativo: ' + error.message, 'system');
        }
    }
    
    updateProactiveDisplay(enabled) {
        const toggle = document.getElementById('proactiveToggle');
        if (toggle) {
            toggle.checked = enabled;
            toggle.title = enabled ? 'Modo Proativo Ativo' : 'Modo Proativo Inativo';
        }
        
        const status = document.getElementById('proactiveStatus');
        if (status) {
            status.textContent = enabled ? 'Proativo ON' : 'Proativo OFF';
            status.className = `proactive-status ${enabled ? 'active' : 'inactive'}`;
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