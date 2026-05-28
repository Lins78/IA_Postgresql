# SKILL.md

## Nome: Sistema de Backup Python — Checklist e Boas Práticas

### Objetivo
Padronizar a criação de sistemas de backup em Python, garantindo:
- Boas práticas de logging
- Compressão eficiente dos arquivos
- Agendamento automático de backups

---

## Passo a Passo (Workflow)

1. **Configuração Inicial**
   - Defina diretórios separados para backups de banco, arquivos e configurações.
   - Carregue configurações sensíveis (usuário, senha, host, etc) de variáveis de ambiente ou arquivos seguros.

2. **Backup do Banco de Dados**
   - Use `pg_dump` (ou equivalente) para exportar o banco.
   - Defina a senha via variável de ambiente para evitar exposição.
   - Comprima o backup (ex: gzip) e remova o arquivo não comprimido.
   - Gere e salve metadados do backup (nome, data, tamanho, status).
   - Faça logging detalhado de cada etapa e erros.

3. **Backup de Arquivos do Sistema**
   - Liste e compacte arquivos/diretórios críticos (ex: código, configs, scripts).
   - Use padrões glob para incluir múltiplos tipos de arquivo.
   - Gere metadados e faça logging.

4. **Backup de Configurações**
   - Exporte configurações relevantes (exceto senhas/chaves) para JSON.
   - Inclua variáveis de ambiente importantes, filtrando segredos.
   - Gere metadados e faça logging.

5. **Backup Completo**
   - Execute os três tipos de backup em sequência.
   - Consolide resultados e metadados.
   - Logging do status geral e tamanho total.

6. **Listagem e Limpeza**
   - Liste backups disponíveis, ordenando por data.
   - Implemente rotina de limpeza automática (ex: manter só últimos 7 dias).
   - Logging da limpeza e espaço liberado.

7. **Agendamento Automático**
   - Use biblioteca como `schedule` para agendar backups completos e parciais.
   - Logging do agendamento e execução.

---

## Critérios de Qualidade
- Logging detalhado e centralizado
- Compressão obrigatória dos arquivos
- Metadados salvos para cada backup
- Não expor senhas/chaves em logs ou arquivos
- Agendamento automático documentado
- Rotina de limpeza ativa

---

## Exemplo de Prompt
- "Crie um sistema de backup Python seguindo o SKILL.md do repositório."
- "Checklist para revisar meu backup: logging, compressão, agendamento, limpeza."
- "Como implementar backup seguro e automatizado em Python?"

---

## Sugestões de Customizações Futuras
- Skill para restauração automática de backups
- Skill para monitoramento e alerta de falhas de backup
- Skill para integração com armazenamento em nuvem
