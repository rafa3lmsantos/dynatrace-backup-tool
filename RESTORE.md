# 🔄 Guia de Restore - Dynatrace Backup Tool

Este guia explica como restaurar as configurações do Dynatrace usando os backups criados pela ferramenta.

## 📋 **Índice**

- [Pré-requisitos](#-pré-requisitos)
- [Métodos de Restore](#-métodos-de-restore)
- [Exemplos Práticos](#-exemplos-práticos)
- [Restore Seletivo](#-restore-seletivo)
- [Cuidados e Validações](#-cuidados-e-validações)
- [Solução de Problemas](#-solução-de-problemas)

---

## 🔧 **Pré-requisitos**

### **Token com Permissões de Escrita**
Diferente do backup, o restore precisa de permissões de **ESCRITA**:

1. Acesse: **Settings → Integration → Dynatrace API**
2. **Generate token** com permissões:
   - ✅ **WriteConfig** - Para criar/atualizar configurações
   - ✅ **ReadConfig** - Para validar configurações existentes
   - ✅ **DataExport** - Para validação de dados
   - ✅ **DataImport** - Para importar configurações

### **Backup Disponível**
- Tenha um backup criado pela ferramenta
- Exemplo: `backups/backup_YYYYMMDD_HHMMSS/`

---

## 🚀 **Métodos de Restore**

### **Método 1: Monaco CLI Diretamente** ⚡

```powershell
# 1. Configure as variáveis de ambiente
$env:DT_TOKEN="dt0c01.SEU_TOKEN_DE_ESCRITA_AQUI"
$env:DT_CLUSTER_URL="https://ambiente-destino.live.dynatrace.com"

# 2. Navegue para o diretório do backup
cd "backups\backup_20251003_131434"

# 3. Execute o restore
..\..\monaco.exe deploy manifest.yaml --environment $env:DT_CLUSTER_URL
```

### **Método 2: Arquivo de Configuração** 📋

**Crie `environments.yaml`:**
```yaml
environments:
  production:
    name: "Production Environment"
    url:
      value: "https://ambiente-destino.live.dynatrace.com"
    auth:
      token:
        name: "DT_TOKEN"
  
  development:
    name: "Development Environment"
    url:
      value: "https://dev-ambiente.live.dynatrace.com"
    auth:
      token:
        name: "DT_TOKEN"
```

**Execute o restore:**
```powershell
$env:DT_TOKEN="seu-token-aqui"
monaco.exe deploy manifest.yaml --environment production
```

### **Método 3: Script Automatizado** 🐍

**Crie `restore.py`:**
```python
#!/usr/bin/env python3
import subprocess
import os
import sys
from pathlib import Path

def restore_dynatrace(backup_folder, target_environment):
    """
    Restaura configurações do Dynatrace a partir de backup
    """
    
    # Verificar se o backup existe
    backup_path = Path(f"backups/{backup_folder}")
    if not backup_path.exists():
        print(f"❌ Backup não encontrado: {backup_path}")
        return False
    
    # Verificar token
    token = os.getenv("DT_API_TOKEN")
    if not token:
        print("❌ Token não configurado! Configure DT_API_TOKEN")
        return False
    
    # Comando Monaco
    cmd = [
        str(Path("monaco.exe")),
        "deploy",
        str(backup_path / "manifest.yaml"),
        "--environment", target_environment
    ]
    
    print(f"🔄 Iniciando restore de {backup_folder}...")
    print(f"🎯 Destino: {target_environment}")
    
    try:
        # Executar restore
        env = os.environ.copy()
        env["DT_TOKEN"] = token
        
        result = subprocess.run(cmd, env=env, check=True)
        print("✅ Restore concluído com sucesso!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro no restore: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python restore.py <backup_folder> <target_url>")
        print("Exemplo: python restore.py backup_20251003_131434 https://prod.live.dynatrace.com")
        sys.exit(1)
    
    backup_folder = sys.argv[1]
    target_url = sys.argv[2]
    
    success = restore_dynatrace(backup_folder, target_url)
    sys.exit(0 if success else 1)
```

**Execute:**
```powershell
$env:DT_API_TOKEN="seu-token-de-escrita"
python restore.py backup_20251003_131434 https://destino.live.dynatrace.com
```

---

## 🎯 **Exemplos Práticos**

### **Restore Completo**
```powershell
# Restaurar todas as configurações
$env:DT_TOKEN="dt0c01.TOKEN_DE_ESCRITA"
cd "backups\backup_20251003_131434"
..\..\monaco.exe deploy manifest.yaml --environment "https://prod.live.dynatrace.com"
```

### **Validação Prévia (Dry-Run)**
```powershell
# Testar sem aplicar mudanças
..\..\monaco.exe deploy manifest.yaml --environment "https://prod.live.dynatrace.com" --dry-run
```

### **Restore Entre Ambientes**
```powershell
# DEV → PROD
$env:DT_TOKEN="token-producao"
..\..\monaco.exe deploy manifest.yaml --environment "https://prod.live.dynatrace.com"

# PROD → DEV  
$env:DT_TOKEN="token-desenvolvimento"
..\..\monaco.exe deploy manifest.yaml --environment "https://dev.live.dynatrace.com"
```

---

## 🔍 **Restore Seletivo**

### **Apenas Dashboards**
```powershell
# Criar configuração específica para dashboards
# Edite manifest.yaml para incluir apenas:
projects:
  - name: dashboard-restore
    path: project/dashboard
```

### **Configurações Específicas**
```powershell
# Restaurar apenas SLOs
monaco.exe deploy manifest.yaml --environment production --project slo

# Restaurar apenas monitores sintéticos  
monaco.exe deploy manifest.yaml --environment production --project synthetic-monitor
```

### **Exclusão de Configurações**
```yaml
# No manifest.yaml, comente ou remova projetos indesejados:
projects:
  - name: dashboard
    path: project/dashboard
  # - name: alerting  # ← Comentado = não será restaurado
  #   path: project/alerting
```

---

## ⚠️ **Cuidados e Validações**

### **1. Backup do Ambiente de Destino**
```powershell
# SEMPRE faça backup do ambiente atual antes do restore
python dynatrace-backup-auto.py
```

### **2. Validação de Compatibilidade**

**Verificar versões:**
- ✅ Versão do Dynatrace de origem vs destino
- ✅ Recursos disponíveis no ambiente de destino
- ✅ Licenças e limites do ambiente

**Teste em DEV primeiro:**
```powershell
# 1. Teste em desenvolvimento
$env:DT_CLUSTER_URL="https://dev.live.dynatrace.com"
monaco.exe deploy manifest.yaml --environment development --dry-run

# 2. Se OK, aplique em produção
$env:DT_CLUSTER_URL="https://prod.live.dynatrace.com"
monaco.exe deploy manifest.yaml --environment production
```

### **3. Verificação de Dependências**

Algumas configurações têm dependências:
- **SLOs** → Métricas e serviços devem existir
- **Dashboards** → Entidades referenciadas devem existir
- **Alertas** → Grupos de notificação devem estar configurados

---

## 🚨 **Cenários de Uso**

### **🔄 Migração de Ambientes**
```powershell
# Cenário: DEV → PROD
# 1. Backup do DEV
$env:DT_CLUSTER_URL="https://dev.live.dynatrace.com"
$env:DT_API_TOKEN="token-dev-readonly"
python dynatrace-backup-auto.py

# 2. Restore no PROD
$env:DT_CLUSTER_URL="https://prod.live.dynatrace.com"
$env:DT_API_TOKEN="token-prod-write"
cd "backups\backup_YYYYMMDD_HHMMSS"
..\..\monaco.exe deploy manifest.yaml --environment $env:DT_CLUSTER_URL
```

### **🆕 Novo Ambiente**
```powershell
# Configurar ambiente do zero com backup de referência
$env:DT_CLUSTER_URL="https://novo-ambiente.live.dynatrace.com"
$env:DT_API_TOKEN="token-novo-ambiente"
cd "backups\backup_referencia"
..\..\monaco.exe deploy manifest.yaml --environment $env:DT_CLUSTER_URL
```

### **🛠️ Disaster Recovery**
```powershell
# Restaurar após problemas
$env:DT_CLUSTER_URL="https://ambiente-recuperado.live.dynatrace.com"
$env:DT_API_TOKEN="token-recovery"
cd "backups\backup_antes_do_problema"
..\..\monaco.exe deploy manifest.yaml --environment $env:DT_CLUSTER_URL
```

---

## 🔧 **Solução de Problemas**

### **Erro: "401 Unauthorized"**
```
❌ Problema: Token sem permissões de escrita
✅ Solução: Gere novo token com WriteConfig, DataImport
```

### **Erro: "Config already exists"**
```
❌ Problema: Configuração já existe no destino
✅ Solução: Use --force ou delete configurações conflitantes
```

### **Erro: "Dependency not found"**
```
❌ Problema: Configuração depende de recurso inexistente
✅ Solução: Restaure dependências primeiro ou ajuste configuração
```

### **Restore Parcial**
```powershell
# Se restore falhou parcialmente, continue de onde parou:
monaco.exe deploy manifest.yaml --environment production --continue-on-error
```

### **Validação de Resultado**
```powershell
# Após restore, valide o ambiente:
# 1. Acesse o Dynatrace e verifique dashboards
# 2. Teste monitores sintéticos
# 3. Verifique alertas configurados
# 4. Confirme SLOs ativos
```

---

## 📊 **Logs e Monitoramento**

### **Habilitar Logs Detalhados**
```powershell
monaco.exe deploy manifest.yaml --environment production --verbose
```

### **Salvar Log de Restore**
```powershell
monaco.exe deploy manifest.yaml --environment production > restore.log 2>&1
```

### **Verificar Progresso**
Durante o restore, Monaco mostra:
- ✅ Configurações aplicadas com sucesso
- ⚠️ Avisos sobre conflitos ou dependências
- ❌ Erros que precisam de atenção

---

## 🎯 **Melhores Práticas**

1. **🔒 Sempre backup antes de restore**
2. **🧪 Teste em DEV antes de PROD**
3. **👀 Use --dry-run para validar**
4. **📝 Documente mudanças aplicadas**
5. **⏰ Execute fora do horário de pico**
6. **🔄 Valide resultado após restore**

---

## 📞 **Suporte**

- 📖 [Documentação Monaco](https://github.com/dynatrace/dynatrace-configuration-as-code)
- 🐛 [Issues do Projeto](https://github.com/rafa3lmsantos/dynatrace-backup-tool/issues)
- 💡 [Discussões](https://github.com/rafa3lmsantos/dynatrace-backup-tool/discussions)

---

**⚡ Restore concluído? Valide suas configurações no Dynatrace! 🚀**
