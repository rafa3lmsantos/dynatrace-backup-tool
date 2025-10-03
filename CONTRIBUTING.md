# 🔧 Contribuindo para o Dynatrace Backup Tool

Obrigado por querer contribuir! Este documento contém informações para desenvolvedores.

## 🛠️ Setup de Desenvolvimento

### Pré-requisitos
- Python 3.6+
- Git

### Configuração
```bash
# Clone o repositório
git clone https://github.com/rafa3lmsantos/dynatrace-backup-tool.git
cd dynatrace-backup-tool

# Copie o arquivo de configuração
cp .env.example .env

# Edite suas credenciais
nano .env
```

## 📝 Padrões de Código

### Estilo
- Seguir PEP 8
- Usar docstrings em funções principais
- Comentários em português
- Emojis nos prints para melhor UX

### Estrutura de Commits
```
tipo: descrição curta

Descrição mais detalhada se necessário.

- Item 1
- Item 2
```

**Tipos de commit:**
- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Documentação
- `style`: Formatação
- `refactor`: Refatoração
- `test`: Testes
- `chore`: Manutenção

### Exemplo:
```
feat: adicionar monitoramento em tempo real

Implementa thread separada para acompanhar progresso do backup:
- Contador de arquivos em tempo real
- Taxa de processamento por segundo
- Estimativa de tempo restante
```

## 🧪 Testes

### Testes Locais
```bash
# Teste básico
python dynatrace-backup-auto.py

# Teste com dados fictícios
DT_CLUSTER_URL=https://test.dynatrace.com DT_API_TOKEN=test python dynatrace-backup-auto.py
```

### Checklist de Pull Request
- [ ] Código testado localmente
- [ ] Documentação atualizada
- [ ] CHANGELOG.md atualizado
- [ ] Sem credenciais hardcoded
- [ ] .gitignore respeitado

## 🔒 Segurança

### ⚠️ NUNCA faça commit de:
- Tokens de API reais
- URLs de produção
- Credenciais de qualquer tipo
- Dados sensíveis

### ✅ Sempre:
- Use `.env.example` para templates
- Mascare tokens nos logs
- Valide inputs do usuário
- Use HTTPS para downloads

## 📁 Estrutura do Código

```
dynatrace-backup-tool/
├── dynatrace-backup-auto.py    # 🎯 Script principal
├── .env.example               # 📋 Template de config
├── README.md                  # 📖 Documentação principal
├── CHANGELOG.md              # 📝 Histórico de versões
├── CONTRIBUTING.md           # 🤝 Este arquivo
├── LICENSE                   # ⚖️ Licença MIT
└── .gitignore               # 🚫 Arquivos ignorados
```

## 🎯 Roadmap

### Versão 1.1
- [ ] Suporte a múltiplos ambientes
- [ ] Validação aprimorada de tokens
- [ ] Modo verbose/quiet

### Versão 1.2
- [ ] Interface web básica
- [ ] API REST
- [ ] Webhooks

### Versão 2.0
- [ ] Backup diferencial
- [ ] Compressão
- [ ] Criptografia
- [ ] Agendamento

## 🐛 Reportando Bugs

Use este template:

```markdown
**Descrição do Bug**
Descrição clara do problema.

**Para Reproduzir**
1. Vá para '...'
2. Execute '....'
3. Veja o erro

**Comportamento Esperado**
O que deveria acontecer.

**Screenshots**
Se aplicável.

**Ambiente:**
- OS: [e.g. Windows 10]
- Python: [e.g. 3.9.0]
- Versão: [e.g. 1.0.0]

**Logs**
Inclua logs relevantes.
```

## 📞 Contato

- Issues: GitHub Issues
- Discussões: GitHub Discussions
- Email: Através das issues

---

**Obrigado por contribuir! 🎉**
