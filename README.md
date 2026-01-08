# 🚀 Dynatrace Configuration Backup Tool

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-green.svg)](#)

Uma ferramenta automatizada para fazer backup das configurações do Dynatrace usando Monaco CLI. Esta solução permite exportar e versionar todas as configurações do seu ambiente Dynatrace de forma simples e eficiente.

## 📋 **Características**

- ✅ **Backup Automático** - Exporta todas as configurações
- ✅ **Multi-Plataforma** - Windows, Linux e macOS
- ✅ **Configuração Simples** - Apenas edite o arquivo `.env`
- ✅ **Monaco Integrado** - Não requer instalação manual
- ✅ **Sem Dependências** - Funciona apenas com Python

## 🛠️ **Pré-requisitos**

- Python 3.6 ou superior
- Acesso ao ambiente Dynatrace com permissões de leitura
- Token de API do Dynatrace

## � **Documentação**

### 📖 Guias de Automação com OAuth Client

1. **[OAUTH_CLIENT_CAPABILITIES.md](OAUTH_CLIENT_CAPABILITIES.md)**  
   📘 Documentação completa de todas as capacidades do OAuth Client

2. **[QUICKSTART.md](QUICKSTART.md)**  
   ⚡ Guia rápido para começar em 5 minutos

3. **[RESUMO_EXECUTIVO.md](RESUMO_EXECUTIVO.md)**  
   📊 Visão executiva e casos de uso

4. **[MAPA_VISUAL.md](MAPA_VISUAL.md)**  
   🗺️ Diagramas e fluxos visuais das operações

5. **[GUIA_AUTENTICACAO.md](GUIA_AUTENTICACAO.md)** ⭐ **NOVO!**  
   🔐 OAuth Client vs Access Token - Entenda as diferenças e quando usar cada um

---

## �📦 **Instalação**

### 1. Clone o Repositório
```bash
git clone https://github.com/rafa3lmsantos/dynatrace-backup-tool.git
cd dynatrace-backup-tool
```

### 2. Configure suas Credenciais

**📝 Edite o arquivo `.env`:**

1. Copie o arquivo de exemplo: `cp .env.example .env`
2. Abra o arquivo `.env` no seu editor favorito
3. Substitua os valores pelas suas credenciais:

```env
# 🔧 Configuração Dynatrace - EDITE AQUI
DT_CLUSTER_URL=https://seu-ambiente.live.dynatrace.com
DT_API_TOKEN=seu-token-aqui
```

**🔑 Como obter o Token:**
1. Acesse: `https://seu-ambiente.live.dynatrace.com`
2. Vá em: **Settings → Integration → Dynatrace API**
3. Clique em: **Generate token**
4. Selecione as permissões: `Read configuration`, `Read metrics`, `Read entities`

### 3. Execute o Backup
```bash
python dynatrace-backup-auto.py
```

## 🚀 **Uso**

### Execução Simples
```bash
python dynatrace-backup-auto.py
```

**O script faz tudo automaticamente:**
1. ✅ Carrega as credenciais do arquivo `.env`
2. ✅ Verifica conectividade com o Dynatrace
3. ✅ Valida o token de API
4. ✅ Executa o backup completo
5. ✅ Organiza os arquivos por data/hora

### Estrutura de Backup

```
backups/
└── backup_YYYYMMDD_HHMMSS/
    └── project/
        ├── dashboards/
        ├── synthetic-monitors/
        ├── slo/
        └── ... (outras configurações)
```

## ⚙️ **Configuração Simples**

### Arquivo `.env`

O arquivo `.env` é a forma mais simples de configurar a ferramenta:

```env
# 🔧 Configuração Dynatrace - EDITE AQUI
DT_CLUSTER_URL=https://seu-ambiente.live.dynatrace.com
DT_API_TOKEN=seu-token-aqui
```

### Como Obter suas Credenciais

**1. URL do Ambiente:**
- Use a URL que você acessa o Dynatrace
- Exemplo: `https://abc12345.live.dynatrace.com`

**2. Token de API:**
1. Acesse seu ambiente Dynatrace
2. Vá para **Settings > Integration > Dynatrace API**
3. Clique em **Generate token**
4. Defina um nome para o token
5. Selecione as permissões:
   - ✅ `Read configuration`
   - ✅ `Read metrics` 
   - ✅ `Read entities`
   - ✅ `Read settings`
6. Copie o token gerado

## 🐛 **Solução de Problemas**

### Erro: "URL do cluster não configurada"
```
❌ Erro: URL do cluster não configurada!
```
**Solução:** Edite o arquivo `.env` e defina o `DT_CLUSTER_URL`

### Erro: "Token Authentication failed"  
```
❌ Token Authentication failed
```
**Solução:** 
1. Verifique se o token no arquivo `.env` está correto
2. Gere um novo token no Dynatrace com as permissões necessárias
3. Certifique-se de que o token não expirou

### Arquivo .env não encontrado
**Solução:** Certifique-se de que o arquivo `.env` existe no mesmo diretório do script

### Token sem permissões
**Solução:** O token precisa das permissões:
- `Read configuration`
- `Read metrics`
- `Read entities`
- `Read settings`

## 📁 **Estrutura do Projeto**

```
dynatrace-backup-tool/
├── dynatrace-backup-auto.py  # Script principal
├── .env                     # 🔧 Configuração (edite aqui!)
├── .env.example            # Template de configuração
├── monaco.exe              # Monaco CLI (Windows)
├── README.md              # Esta documentação
├── GUIA-RAPIDO.md        # ⚡ 3 passos rápidos
├── RESTORE.md            # 🔄 Guia completo de restore
├── LICENSE               # Licença MIT
└── backups/             # Pasta de backups (criada automaticamente)
```

## 🔄 **Restore (Restauração)**

Para restaurar as configurações em outro ambiente, consulte o **[Guia Completo de Restore](RESTORE.md)** que inclui:

- 🚀 **Métodos de restore** (Monaco CLI, Scripts Python)
- 🎯 **Restore seletivo** (apenas dashboards, SLOs, etc.)
- ⚠️ **Validações e cuidados** (backup antes, dry-run, etc.)
- 🔧 **Solução de problemas** (erros comuns e soluções)
- 📋 **Exemplos práticos** para diferentes cenários

**Comando rápido:**
```bash
# Navegue para o backup e execute:
cd backups/backup_YYYYMMDD_HHMMSS
../../monaco.exe deploy manifest.yaml --environment "https://destino.live.dynatrace.com"
```

## 🤝 **Contribuindo**

Contribuições são bem-vindas! Por favor:

1. Faça um Fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 **Changelog**

### v1.0.0 (2025-10-03)
- ✅ Configuração simplificada via arquivo `.env`
- ✅ Backup automático completo  
- ✅ Suporte multi-plataforma
- ✅ Monaco CLI integrado

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