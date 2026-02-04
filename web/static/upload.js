// JavaScript para Sistema de Upload de Documentos
class DocumentUpload {
    constructor() {
        this.selectedFiles = [];
        this.currentPage = 1;
        this.documentsPerPage = 10;
        this.allDocuments = [];
        this.filteredDocuments = [];
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadDocuments();
    }

    setupEventListeners() {
        // Upload individual
        const uploadForm = document.getElementById('uploadForm');
        if (uploadForm) {
            uploadForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.uploadSingleDocument();
            });
        }

        // Auto-preencher título baseado no nome do arquivo
        const fileInput = document.getElementById('documentFile');
        const titleInput = document.getElementById('documentTitle');
        
        if (fileInput && titleInput) {
            fileInput.addEventListener('change', (e) => {
                const file = e.target.files[0];
                if (file && !titleInput.value) {
                    // Remove extensão e usa como título
                    const title = file.name.split('.').slice(0, -1).join('.');
                    titleInput.value = title;
                }
            });
        }

        // Upload múltiplo - drag and drop
        const dropZone = document.getElementById('dropZone');
        const bulkFiles = document.getElementById('bulkFiles');
        const bulkUploadBtn = document.getElementById('bulkUploadBtn');

        if (dropZone) {
            dropZone.addEventListener('click', () => {
                bulkFiles.click();
            });

            dropZone.addEventListener('dragover', (e) => {
                e.preventDefault();
                dropZone.classList.add('drag-over');
            });

            dropZone.addEventListener('dragleave', (e) => {
                e.preventDefault();
                dropZone.classList.remove('drag-over');
            });

            dropZone.addEventListener('drop', (e) => {
                e.preventDefault();
                dropZone.classList.remove('drag-over');
                
                const files = Array.from(e.dataTransfer.files);
                this.handleBulkFiles(files);
            });
        }

        if (bulkFiles) {
            bulkFiles.addEventListener('change', (e) => {
                const files = Array.from(e.target.files);
                this.handleBulkFiles(files);
            });
        }

        if (bulkUploadBtn) {
            bulkUploadBtn.addEventListener('click', () => {
                this.uploadBulkDocuments();
            });
        }

        // Busca de documentos
        const searchDocuments = document.getElementById('searchDocuments');
        if (searchDocuments) {
            searchDocuments.addEventListener('input', (e) => {
                this.filterDocuments(e.target.value);
            });
        }

        // Atualizar lista de documentos
        const refreshDocuments = document.getElementById('refreshDocuments');
        if (refreshDocuments) {
            refreshDocuments.addEventListener('click', () => {
                this.loadDocuments();
            });
        }
    }

    async uploadSingleDocument() {
        const form = document.getElementById('uploadForm');
        const formData = new FormData(form);

        this.showModal();
        this.updateProgress(0, 'Iniciando upload...');

        try {
            const response = await fetch('/upload/document', {
                method: 'POST',
                body: formData
            });

            this.updateProgress(100, 'Processando...');

            if (response.ok) {
                const result = await response.json();
                
                this.updateProgress(100, 'Upload concluído!');
                
                setTimeout(() => {
                    this.hideModal();
                    this.showSuccess(`Documento "${result.title}" enviado com sucesso!`);
                    form.reset();
                    this.loadDocuments(); // Atualizar lista
                }, 1000);

            } else {
                const error = await response.json();
                throw new Error(error.detail || 'Erro no upload');
            }

        } catch (error) {
            console.error('Erro no upload:', error);
            this.hideModal();
            this.showError(error.message);
        }
    }

    handleBulkFiles(files) {
        // Filtrar tipos de arquivo suportados
        const allowedTypes = ['text/plain', 'text/markdown', 'text/csv', 'application/json'];
        const validFiles = files.filter(file => allowedTypes.includes(file.type));

        if (validFiles.length !== files.length) {
            this.showWarning('Alguns arquivos foram ignorados (tipo não suportado)');
        }

        if (validFiles.length > 10) {
            this.showError('Máximo 10 arquivos por vez');
            return;
        }

        this.selectedFiles = validFiles;
        this.displaySelectedFiles();
    }

    displaySelectedFiles() {
        const container = document.getElementById('selectedFiles');
        const uploadBtn = document.getElementById('bulkUploadBtn');

        if (!container) return;

        if (this.selectedFiles.length === 0) {
            container.innerHTML = '';
            uploadBtn.style.display = 'none';
            return;
        }

        let html = '<h4>📁 Arquivos Selecionados:</h4>';
        
        this.selectedFiles.forEach((file, index) => {
            html += `
                <div class="file-item" data-index="${index}">
                    <div class="file-info">
                        <span class="file-icon">📄</span>
                        <span class="file-name">${file.name}</span>
                        <span class="file-size">(${this.formatFileSize(file.size)})</span>
                    </div>
                    <button class="file-remove" onclick="documentUpload.removeFile(${index})" title="Remover">
                        ×
                    </button>
                </div>
            `;
        });

        container.innerHTML = html;
        uploadBtn.style.display = 'block';
    }

    removeFile(index) {
        this.selectedFiles.splice(index, 1);
        this.displaySelectedFiles();
    }

    async uploadBulkDocuments() {
        if (this.selectedFiles.length === 0) {
            this.showError('Nenhum arquivo selecionado');
            return;
        }

        this.showModal();
        this.updateProgress(0, 'Preparando upload múltiplo...');

        try {
            const formData = new FormData();
            
            this.selectedFiles.forEach(file => {
                formData.append('files', file);
            });

            const response = await fetch('/upload/bulk', {
                method: 'POST',
                body: formData
            });

            this.updateProgress(100, 'Processando arquivos...');

            if (response.ok) {
                const result = await response.json();
                
                setTimeout(() => {
                    this.hideModal();
                    
                    if (result.failed_uploads > 0) {
                        this.showWarning(
                            `Upload concluído! ${result.successful_uploads} sucesso(s), ${result.failed_uploads} erro(s)`
                        );
                    } else {
                        this.showSuccess(`${result.successful_uploads} documentos enviados com sucesso!`);
                    }
                    
                    // Limpar seleção
                    this.selectedFiles = [];
                    this.displaySelectedFiles();
                    document.getElementById('bulkFiles').value = '';
                    
                    this.loadDocuments(); // Atualizar lista
                }, 1000);

            } else {
                const error = await response.json();
                throw new Error(error.detail || 'Erro no upload');
            }

        } catch (error) {
            console.error('Erro no upload múltiplo:', error);
            this.hideModal();
            this.showError(error.message);
        }
    }

    async loadDocuments(page = 1) {
        try {
            const response = await fetch(`/documents?page=${page}&limit=${this.documentsPerPage}`);
            
            if (response.ok) {
                const data = await response.json();
                this.allDocuments = data.documents;
                this.filteredDocuments = [...this.allDocuments];
                this.currentPage = page;
                
                this.displayDocuments();
                this.displayPagination(data.pagination);
            } else {
                throw new Error('Erro ao carregar documentos');
            }

        } catch (error) {
            console.error('Erro ao carregar documentos:', error);
            this.showError('Erro ao carregar lista de documentos');
        }
    }

    filterDocuments(searchTerm) {
        if (!searchTerm.trim()) {
            this.filteredDocuments = [...this.allDocuments];
        } else {
            const term = searchTerm.toLowerCase();
            this.filteredDocuments = this.allDocuments.filter(doc => 
                doc.title.toLowerCase().includes(term) ||
                doc.category?.toLowerCase().includes(term) ||
                doc.source?.toLowerCase().includes(term)
            );
        }
        
        this.displayDocuments();
    }

    displayDocuments() {
        const container = document.getElementById('documentsList');
        if (!container) return;

        if (this.filteredDocuments.length === 0) {
            container.innerHTML = `
                <div class="no-documents">
                    <h3>📄 Nenhum documento encontrado</h3>
                    <p>Envie alguns documentos para começar a usar o sistema de busca do Mamute!</p>
                </div>
            `;
            return;
        }

        let html = '';
        
        this.filteredDocuments.forEach(doc => {
            const createdAt = new Date(doc.created_at).toLocaleString('pt-BR');
            const contentLength = this.formatFileSize(doc.content_length);
            const metadata = doc.metadata ? JSON.parse(doc.metadata) : {};
            
            html += `
                <div class="document-item" data-id="${doc.id}">
                    <div class="document-header">
                        <div class="document-title">📄 ${doc.title}</div>
                        <div class="document-actions">
                            <button class="btn btn-sm btn-danger" onclick="documentUpload.deleteDocument('${doc.id}', '${doc.title}')">
                                🗑️ Deletar
                            </button>
                        </div>
                    </div>
                    <div class="document-meta">
                        <span>📂 ${doc.category || 'Sem categoria'}</span>
                        <span>🔗 ${doc.source || 'Fonte não informada'}</span>
                        <span>📏 ${contentLength}</span>
                        <span>📅 ${createdAt}</span>
                        ${metadata.filename ? `<span>📁 ${metadata.filename}</span>` : ''}
                    </div>
                </div>
            `;
        });

        container.innerHTML = html;
    }

    displayPagination(pagination) {
        const container = document.getElementById('paginationContainer');
        if (!container || !pagination) return;

        const { page, total_pages, has_prev, has_next } = pagination;

        if (total_pages <= 1) {
            container.innerHTML = '';
            return;
        }

        let html = '<div class="pagination">';

        // Botão anterior
        if (has_prev) {
            html += `<button class="btn btn-sm" onclick="documentUpload.loadDocuments(${page - 1})">« Anterior</button>`;
        }

        // Números das páginas
        const startPage = Math.max(1, page - 2);
        const endPage = Math.min(total_pages, page + 2);

        for (let i = startPage; i <= endPage; i++) {
            const activeClass = i === page ? 'btn-primary' : 'btn-secondary';
            html += `<button class="btn btn-sm ${activeClass}" onclick="documentUpload.loadDocuments(${i})">${i}</button>`;
        }

        // Botão próximo
        if (has_next) {
            html += `<button class="btn btn-sm" onclick="documentUpload.loadDocuments(${page + 1})">Próximo »</button>`;
        }

        html += '</div>';
        container.innerHTML = html;
    }

    async deleteDocument(documentId, title) {
        if (!confirm(`Tem certeza que deseja deletar o documento "${title}"?`)) {
            return;
        }

        try {
            const response = await fetch(`/documents/${documentId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                const result = await response.json();
                this.showSuccess(result.message);
                this.loadDocuments(this.currentPage);
            } else {
                const error = await response.json();
                throw new Error(error.detail || 'Erro ao deletar documento');
            }

        } catch (error) {
            console.error('Erro ao deletar documento:', error);
            this.showError(error.message);
        }
    }

    // Métodos utilitários
    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    showModal() {
        const modal = document.getElementById('uploadModal');
        if (modal) {
            modal.style.display = 'flex';
        }
    }

    hideModal() {
        const modal = document.getElementById('uploadModal');
        if (modal) {
            modal.style.display = 'none';
        }
    }

    updateProgress(percent, text) {
        const progressFill = document.querySelector('.progress-fill');
        const progressText = document.getElementById('progressText');

        if (progressFill) {
            progressFill.style.width = percent + '%';
        }

        if (progressText) {
            progressText.textContent = text;
        }
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showWarning(message) {
        this.showNotification(message, 'warning');
    }

    showNotification(message, type) {
        // Criar elemento de notificação
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-icon">
                    ${type === 'success' ? '✅' : type === 'error' ? '❌' : '⚠️'}
                </span>
                <span class="notification-message">${message}</span>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;

        // Adicionar ao DOM
        document.body.appendChild(notification);

        // Auto-remover após 5 segundos
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }
}

// Adicionar estilos CSS para notificações
const notificationStyles = `
    .notification {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1001;
        min-width: 300px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        animation: slideIn 0.3s ease-out;
    }

    .notification-success {
        background: #d4edda;
        border-left: 4px solid #28a745;
        color: #155724;
    }

    .notification-error {
        background: #f8d7da;
        border-left: 4px solid #dc3545;
        color: #721c24;
    }

    .notification-warning {
        background: #fff3cd;
        border-left: 4px solid #ffc107;
        color: #856404;
    }

    .notification-content {
        display: flex;
        align-items: center;
        padding: 1rem;
    }

    .notification-icon {
        margin-right: 0.5rem;
        font-size: 1.2rem;
    }

    .notification-message {
        flex: 1;
        margin-right: 0.5rem;
    }

    .notification-close {
        background: none;
        border: none;
        font-size: 1.2rem;
        cursor: pointer;
        color: inherit;
        padding: 0;
        width: 20px;
        height: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    .no-documents {
        text-align: center;
        padding: 3rem;
        color: #666;
    }

    .pagination {
        display: flex;
        justify-content: center;
        gap: 0.5rem;
        margin-top: 1rem;
    }

    .pagination .btn {
        min-width: 40px;
    }
`;

// Adicionar estilos ao DOM
const styleSheet = document.createElement('style');
styleSheet.textContent = notificationStyles;
document.head.appendChild(styleSheet);

// Inicializar sistema de upload quando DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('uploadForm')) {
        window.documentUpload = new DocumentUpload();
    }
});

window.DocumentUpload = DocumentUpload;