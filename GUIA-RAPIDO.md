# 🚀 Guia Rápido - Dynatrace Backup

## ⚡ **3 Passos para Executar**

### 1. **📝 Edite o arquivo `.env`**
```env
DT_CLUSTER_URL=https://lkx73873.live.dynatrace.com
DT_API_TOKEN=seu-token-aqui
```

### 2. **🔑 Obtenha seu Token**
1. Acesse seu Dynatrace
2. **Settings → Integration → Dynatrace API**
3. **Generate token** com permissões:
   - ✅ Read configuration
   - ✅ Read metrics  
   - ✅ Read entities
   - ✅ Read settings

### 3. **🚀 Execute**
```bash
python dynatrace-backup-auto.py
```

## ✅ **Pronto!**
Backup será salvo em `backups/backup_YYYYMMDD_HHMMSS/`

---

### 🐛 **Problemas Comuns**

**❌ "URL do cluster não configurada"**
→ Edite o arquivo `.env`

**❌ "Token Authentication failed"**  
→ Gere um novo token com as permissões corretas

**❌ Arquivo não encontrado**
→ Execute no diretório correto com o arquivo `.env`
