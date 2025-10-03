# 🚀 Dynatrace Configuration Backup Tool

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-green.svg)](#)

Uma ferramenta automatizada para fazer backup das configurações do Dynatrace usando Monaco CLI. Esta solução permite exportar e versionar todas as configurações do seu ambiente Dynatrace de forma simples e eficiente.

## 📋 **Características**

- ✅ **Backup Automático Completo** - Exporta todas as configurações do Dynatrace
- ✅ **Multi-Plataforma** - Funciona em Windows, Linux e macOS
- ✅ **Fácil de Usar** - Um único comando para executar
- ✅ **Organização Automática** - Backups organizados por data/hora
- ✅ **Monaco CLI Integrado** - Não requer instalação manual do Monaco
- ✅ **Sem Dependências Externas** - Funciona apenas com Python

## 🛠️ **Pré-requisitos**

- Python 3.6 ou superior
- Acesso ao ambiente Dynatrace com permissões de leitura
- Token de API do Dynatrace

## 📦 **Instalação**

### 1. Clone o Repositório
```bash
git clone https://github.com/rafa3lmsantos/dynatrace-backup-tool.git
cd dynatrace-backup-tool
```

### 2. Configure as Variáveis de Ambiente

**Opção 1: Variáveis de Sistema**

**Windows:**
```cmd
set DT_CLUSTER_URL=https://your-environment.live.dynatrace.com
set DT_API_TOKEN=your-api-token
```

**Linux/macOS:**
```bash
export DT_CLUSTER_URL=https://your-environment.live.dynatrace.com
export DT_API_TOKEN=your-api-token
```

**Opção 2: Arquivo .env (Recomendado)**

Copie o arquivo de exemplo e configure:
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

Conteúdo do arquivo `.env`:
```env
DT_CLUSTER_URL=https://your-environment.live.dynatrace.com
DT_API_TOKEN=your-api-token
```

### 3. Execute o Backup
```bash
python dynatrace-backup-auto.py
```

## 🚀 **Uso**

### Execução Simples
```bash
python dynatrace-backup-auto.py
```

### Verificação de Conectividade
O script automaticamente:
1. Verifica a conectividade com o ambiente Dynatrace
2. Valida o token de API
3. Testa o Monaco CLI
4. Executa o backup completo

### Estrutura de Backup

Os backups são organizados automaticamente:
```
backups/
└── backup_YYYYMMDD_HHMMSS/
    └── project/
        ├── dashboard-share-settings/
        ├── key-user-actions-mobile/
        ├── key-user-actions-web/
        ├── network-zone/
        ├── reports/
        ├── request-attributes/
        ├── service-resource-naming/
        ├── slo/
        └── synthetic-monitor/
```

## ⚙️ **Configuração de Tokens**

### Como Obter o Token de API

1. Acesse seu ambiente Dynatrace
2. Vá para **Settings > Integration > Dynatrace API**
3. Clique em **Generate token**
4. Selecione as seguintes permissões:
   - `ReadConfig` - Para ler configurações
   - `WriteConfig` - Para validação (opcional)
   - `DataExport` - Para exportar dados

### Escopo das Permissões

O token deve ter permissões para:
- Dashboard settings
- Key user actions
- Network zones
- SLO definitions
- Synthetic monitors
- Request attributes
- Reports

## 🐛 **Solução de Problemas**

### Erro de Conectividade
```
❌ Erro de conectividade com a API do Dynatrace
```
**Solução:** Verifique se o `DT_CLUSTER_URL` está correto e acessível.

### Erro de Token
```
❌ Token de API inválido ou sem permissões
```
**Solução:** Verifique se o `DT_API_TOKEN` está correto e tem as permissões necessárias.

### Erro do Monaco
```
❌ Monaco CLI não está funcionando corretamente
```
**Solução:** O script tentará corrigir automaticamente. Se persistir, entre em contato.

## 📁 **Estrutura do Projeto**

```
dynatrace-backup-tool/
├── dynatrace-backup-auto.py  # Script principal
├── monaco.exe               # Monaco CLI (Windows)
├── README.md               # Documentação
├── .gitignore             # Exclusões do Git
├── LICENSE                # Licença MIT
├── requirements.txt       # Dependências
└── backups/              # Pasta de backups (criada automaticamente)
```

## 🤝 **Contribuindo**

Contribuições são bem-vindas! Por favor:

1. Faça um Fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 **Changelog**

### v1.0.0 (2025-01-03)
- ✅ Primeira versão estável
- ✅ Backup automático completo
- ✅ Suporte multi-plataforma
- ✅ Monaco CLI integrado
- ✅ Documentação completa

## 📜 **Licença**

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🙋‍♂️ **Suporte**

Se você encontrar algum problema ou tiver sugestões:

1. 🐛 [Reporte bugs](https://github.com/rafa3lmsantos/dynatrace-backup-tool/issues)
2. 💡 [Sugira melhorias](https://github.com/rafa3lmsantos/dynatrace-backup-tool/discussions)
3. 📧 Entre em contato através das issues

## 🌟 **Reconhecimentos**

- [Dynatrace Monaco](https://github.com/dynatrace/dynatrace-configuration-as-code) - Ferramenta oficial para Configuration as Code
- [Dynatrace](https://www.dynatrace.com/) - Plataforma de monitoramento

---

**Feito com ❤️ para a comunidade Dynatrace**