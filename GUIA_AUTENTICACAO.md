# 🔐 Guia Completo de Autenticação Dynatrace

## 📋 Índice
- [Visão Geral](#visão-geral)
- [OAuth Client vs Access Token](#oauth-client-vs-access-token)
- [Como Criar Access Token](#como-criar-access-token)
- [Comparação de Permissões](#comparação-de-permissões)
- [Quando Usar Cada Tipo](#quando-usar-cada-tipo)

---

## 🎯 Visão Geral

O Dynatrace possui **DOIS TIPOS** de autenticação completamente diferentes:

```
┌─────────────────────────────────────────────────────────────┐
│                    DYNATRACE AUTHENTICATION                  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌───────────────────────┐      ┌──────────────────────┐   │
│  │   OAuth Client        │      │  Environment Access  │   │
│  │   (Account Level)     │      │  Token (Env Level)   │   │
│  └───────────────────────┘      └──────────────────────┘   │
│           │                               │                  │
│           ├─ Gerenciamento de Conta      ├─ Métricas       │
│           ├─ Usuários                     ├─ Logs           │
│           ├─ Grupos                       ├─ Traces         │
│           ├─ Permissões                   ├─ Entidades      │
│           ├─ Ambientes                    ├─ Configurações  │
│           └─ Políticas                    └─ APIs de dados  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔑 OAuth Client vs Access Token

### **OAuth Client** (Você já tem configurado!)

#### ✅ **O que ele FAZ:**
```python
# Account Management API
https://api.dynatrace.com/iam/v1/...
https://api.dynatrace.com/env/v1/...

Exemplos:
- Listar usuários da conta
- Criar/remover usuários
- Gerenciar grupos
- Atribuir permissões
- Listar ambientes
- Gerenciar políticas de acesso
```

#### ❌ **O que ele NÃO FAZ:**
```python
# Environment API (REQUER ACCESS TOKEN)
https://{environment-id}.live.dynatrace.com/api/v2/...

Exemplos:
- Consultar métricas Apdex ❌
- Buscar logs ❌
- Analisar traces ❌
- Listar entidades (hosts, serviços) ❌
- Configurar alertas ❌
```

#### 📝 **Configuração OAuth Client:**
```python
# Credenciais que você já tem
client_id = "dt0s02.MEVY2YGD..."
client_secret = "dt0s02.***"
account_urn = "urn:dtaccount:f48dd9d6-72d8-47ca-9fc8-c956ad38120e"

# Token gerado automaticamente (expira em 5 minutos)
token_url = "https://sso.dynatrace.com/sso/oauth2/token"
```

---

### **Environment Access Token**

#### ✅ **O que ele FAZ:**
```python
# Environment API
https://{environment-id}.live.dynatrace.com/api/v2/...

Exemplos:
- Consultar métricas Apdex ✅
- Buscar logs ✅
- Analisar traces ✅
- Listar entidades ✅
- Configurar alertas ✅
- Gerenciar dashboards ✅
```

#### ❌ **O que ele NÃO FAZ:**
```python
# Account Management API (REQUER OAUTH CLIENT)
https://api.dynatrace.com/iam/v1/...

Exemplos:
- Gerenciar usuários da conta ❌
- Criar grupos ❌
- Atribuir permissões de conta ❌
- Listar ambientes da conta ❌
```

#### 📝 **Configuração Access Token:**
```python
# Token gerado manualmente no Dynatrace UI
environment_id = "abc12345"
access_token = "dt0c01.ABC123XYZ..."

# URL base do ambiente
base_url = f"https://{environment_id}.live.dynatrace.com/api/v2"
```

---

## 🛠️ Como Criar Access Token

### **Passo a Passo:**

1. **Acesse seu ambiente Dynatrace:**
   ```
   https://{seu-environment-id}.live.dynatrace.com
   ```

2. **Navegue até Access Tokens:**
   ```
   Menu > Access Tokens
   ou
   Settings > Access Tokens
   ```

3. **Clique em "Generate new token"**

4. **Configure o token:**
   ```
   Token name: "Apdex Metrics Reader"
   Token type: API Token
   ```

5. **Selecione as permissões necessárias:**

   #### **Para Métricas Apdex:**
   ```
   ☑ Read metrics (metrics.read)
   ☑ Write metrics (metrics.write) [opcional]
   ☑ Ingest metrics (metrics.ingest) [opcional]
   ```

   #### **Para Configurações:**
   ```
   ☑ Read settings (settings.read)
   ☑ Write settings (settings.write)
   ```

   #### **Para Entidades:**
   ```
   ☑ Read entities (entities.read)
   ```

   #### **Para Logs:**
   ```
   ☑ Read logs (logs.read)
   ☑ Ingest logs (logs.ingest)
   ```

6. **Gere e copie o token:**
   ```
   ⚠️ IMPORTANTE: Copie o token IMEDIATAMENTE!
   Ele será exibido apenas UMA VEZ.
   ```

7. **Armazene com segurança:**
   ```powershell
   # PowerShell
   $env:DT_ENVIRONMENT_ID = "seu_environment_id"
   $env:DT_ACCESS_TOKEN = "dt0c01.ABC123..."
   ```

---

## 📊 Comparação de Permissões

| Funcionalidade | OAuth Client | Access Token |
|----------------|--------------|--------------|
| **Gerenciamento de Usuários** | ✅ | ❌ |
| **Gerenciamento de Grupos** | ✅ | ❌ |
| **Permissões de Conta** | ✅ | ❌ |
| **Listar Ambientes** | ✅ | ❌ |
| **Métricas Apdex** | ❌ | ✅ |
| **Métricas de Performance** | ❌ | ✅ |
| **Logs** | ❌ | ✅ |
| **Traces** | ❌ | ✅ |
| **Entidades (Hosts/Serviços)** | ❌ | ✅ |
| **Dashboards** | ❌ | ✅ |
| **Alertas** | ❌ | ✅ |
| **Configurações do Ambiente** | ❌ | ✅ |

---

## 🎯 Quando Usar Cada Tipo

### **Use OAuth Client quando precisar de:**

```python
✅ Automação de onboarding de usuários
✅ Sincronização de grupos com AD/LDAP
✅ Auditoria de permissões
✅ Gerenciamento centralizado de acessos
✅ Criação automática de ambientes
✅ Provisionamento em larga escala
```

**Exemplo de uso:**
```python
from oauth_client import DynatraceOAuthClient

client = DynatraceOAuthClient(
    client_id="dt0s02.MEVY2YGD...",
    client_secret="dt0s02.***",
    account_urn="urn:dtaccount:..."
)

# Criar usuário
client.create_user("novo.usuario@empresa.com")

# Adicionar a grupo
client.add_user_to_group("uuid-do-usuario", "uuid-do-grupo")
```

---

### **Use Access Token quando precisar de:**

```python
✅ Consultar métricas de performance (Apdex, Response Time, etc.)
✅ Buscar logs da aplicação
✅ Analisar distributed traces
✅ Listar hosts, serviços, processos
✅ Criar/editar dashboards
✅ Configurar alertas
✅ Integrar com ferramentas de monitoramento
```

**Exemplo de uso:**
```python
from exemplo_apdex_metrics import DynatraceMetricsClient

client = DynatraceMetricsClient(
    environment_id="abc12345",
    access_token="dt0c01.ABC123..."
)

# Consultar Apdex
apdex_data = client.query_apdex_data(
    metric_key="builtin:apps.web.apdex.userType",
    hours_ago=24
)
```

---

## 🔄 Usando Ambos em Conjunto

**Cenário Real:** Sistema completo de automação

```python
# 1. OAuth Client: Provisionar novo usuário
oauth_client = DynatraceOAuthClient(...)
new_user = oauth_client.create_user("analista@empresa.com")
oauth_client.add_user_to_group(new_user['uuid'], "monitoring-team-group")

# 2. Access Token: Criar dashboard personalizado para o usuário
metrics_client = DynatraceMetricsClient(...)
dashboard_data = metrics_client.create_dashboard(
    name=f"Dashboard - {new_user['email']}",
    metrics=["builtin:apps.web.apdex.userType", ...]
)

# 3. Access Token: Configurar alertas
alerts_client = DynatraceMetricsClient(...)
alerts_client.create_alert(
    name="Apdex baixo",
    condition="apdex < 0.85",
    notification_email=new_user['email']
)
```

---

## 🔒 Segurança e Boas Práticas

### **OAuth Client:**
```python
✅ Armazene client_secret em Azure Key Vault ou similar
✅ Use variáveis de ambiente, nunca hardcode
✅ Implemente rotação automática de secrets
✅ Monitore uso através de audit logs
✅ Use princípio do menor privilégio
```

### **Access Token:**
```python
✅ Crie tokens com permissões mínimas necessárias
✅ Use tokens diferentes para diferentes propósitos
✅ Implemente expiração automática
✅ Armazene em secrets managers (Azure Key Vault, AWS Secrets)
✅ Nunca comite tokens no Git
✅ Use .gitignore para arquivos de configuração
```

### **Exemplo de .env (NÃO COMITAR!):**
```bash
# OAuth Client (Account Management)
DT_CLIENT_ID=dt0s02.MEVY2YGD...
DT_CLIENT_SECRET=dt0s02.***
DT_ACCOUNT_URN=urn:dtaccount:f48dd9d6-72d8-47ca-9fc8-c956ad38120e

# Access Token (Environment Metrics)
DT_ENVIRONMENT_ID=abc12345
DT_ACCESS_TOKEN=dt0c01.ABC123...
```

---

## 📚 Recursos Adicionais

### **Documentação Oficial:**
- [OAuth Client](https://docs.dynatrace.com/docs/dynatrace-api/iam)
- [Access Tokens](https://docs.dynatrace.com/docs/dynatrace-api/basics/dynatrace-api-authentication)
- [Metrics API v2](https://docs.dynatrace.com/docs/dynatrace-api/environment-api/metric-v2)
- [Built-in Metrics](https://docs.dynatrace.com/docs/analyze-explore-automate/metrics-classic/built-in-metrics)

### **Exemplos de Código:**
- `oauth_client.py` - Cliente OAuth para Account Management
- `exemplo_apdex_metrics.py` - Cliente de métricas com Access Token
- `exemplo_auditoria.py` - Relatório de usuários (OAuth)
- `testar_conexao.py` - Teste de conexão OAuth

---

## ❓ FAQ

**P: Posso usar OAuth Client para métricas?**
R: ❌ Não. OAuth Client é apenas para Account Management API.

**P: Posso usar Access Token para criar usuários?**
R: ❌ Não. Access Token é apenas para Environment API.

**P: Preciso dos dois?**
R: Depende! Se você precisa de:
- Apenas gerenciar usuários → OAuth Client
- Apenas consultar métricas → Access Token
- Sistema completo → **Ambos**

**P: O Access Token expira?**
R: Sim, mas você define a expiração ao criar (pode ser "nunca expira").

**P: O OAuth token expira?**
R: Sim, expira em 5 minutos. Mas é renovado automaticamente pela biblioteca.

**P: Como saber qual usar?**
R: Veja a URL da API:
- `api.dynatrace.com/iam/*` → OAuth Client
- `{env-id}.live.dynatrace.com/api/v2/*` → Access Token

---

## 🚀 Próximos Passos

1. ✅ **OAuth Client já configurado** (você tem!)
2. ⏳ **Criar Access Token** (siga o guia acima)
3. 📊 **Testar consulta de Apdex** (use `exemplo_apdex_metrics.py`)
4. 🔄 **Integrar ambos** (sistema completo)

---

**📝 Última atualização:** 2025-01-05  
**✍️ Criado para:** Automação Dynatrace com Python
