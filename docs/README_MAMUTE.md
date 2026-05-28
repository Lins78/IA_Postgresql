# 🐘 Mamute - IA Conectada ao PostgreSQL

## Sobre o Mamute

**Mamute** é uma inteligência artificial especializada em análise de dados e operações com PostgreSQL. Com uma personalidade amigável e conhecimento avançado em bancos de dados, Mamute pode ajudar você em diversas tarefas relacionadas a dados.

## Características do Mamute

### 🧠 Capacidades Principais
- **Análise de Dados**: Análise profunda de dados armazenados no PostgreSQL
- **Consultas SQL**: Criação e otimização de consultas complexas
- **Insights**: Geração de relatórios e descoberta de padrões
- **Conversação**: Interface natural para interação com o banco de dados
- **Busca Semântica**: Busca inteligente em documentos usando embeddings

### 🛠️ Funcionalidades
- **Gestão de Conversas**: Mantém contexto das conversas
- **Análise de Tabelas**: Análise automática da estrutura e dados
- **Documentos**: Adição e busca de documentos relevantes
- **Embeddings**: Processamento de texto para busca semântica
- **Sessões**: Gerenciamento de sessões de usuário

### 💾 Estrutura do Banco
Mamute trabalha com as seguintes tabelas:
- `conversations` - Histórico de conversas
- `documents` - Documentos para busca semântica  
- `user_sessions` - Sessões ativas de usuários
- `ai_models` - Informações dos modelos de IA
- `queries` - Log de consultas executadas

## Como Usar o Mamute

### Inicialização
```python
from main import IAPostgreSQL

# Inicializar o sistema
ia_system = IAPostgreSQL()
ia_system.setup_database()

# Iniciar conversa com Mamute
session_id = ia_system.start_conversation("seu_usuario")

# Conversar com Mamute
response = ia_system.chat("Olá Mamute! Como você pode me ajudar?", session_id)
print(response['response'])
```

### Exemplos de Conversas
- "Mamute, quais tabelas estão disponíveis?"
- "Pode analisar os dados da tabela user_sessions?"
- "Como otimizar uma consulta que está lenta?"
- "Mostre-me insights sobre os padrões de uso"

## Configuração

O nome da IA pode ser configurado no arquivo `.env`:
```env
AI_NAME=Mamute
```

## Tecnologias Utilizadas
- **PostgreSQL**: Banco de dados principal
- **OpenAI**: Modelo de linguagem
- **SQLAlchemy**: ORM para Python
- **psycopg2**: Driver PostgreSQL
- **Streamlit**: Interface web opcional

## Personalidade do Mamute
Mamute é:
- 🤝 **Amigável**: Sempre disposto a ajudar
- 🎯 **Focado**: Especialista em dados e PostgreSQL
- 💡 **Inteligente**: Análises precisas e insights valiosos
- 🔍 **Detalhista**: Atenção aos detalhes em consultas e análises

---

*Mamute - Sua IA especialista em PostgreSQL e análise de dados! 🐘*