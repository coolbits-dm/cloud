# 🔐 CoolBits.ai - API Keys Integration Guide

## 📋 **OVERVIEW**

Integrarea cheilor API pentru **12 roluri oGrok (xAI)** și **12 roluri oGPT (OpenAI)** în Google Cloud Secret Manager cu best practices de securitate.

---

## 🚀 **QUICK START**

### **1. Rularea scriptului de integrare**
```bash
# În Cloud Shell
chmod +x integrate_api_keys.sh
./integrate_api_keys.sh
```

### **2. Verificarea integrarei**
```bash
# Listează toate secretele create
gcloud secrets list --filter="name:xai_api_key_ogrok*"
gcloud secrets list --filter="name:openai_api_key_ogpt*"
gcloud secrets list --filter="name:bridge_webhook_hmac_ogpt*"
```

---

## 🔐 **STRUCTURA SECRETELOR**

### **oGrok Keys (xAI)**
```
xai_api_key_ogrok01  → CEO
xai_api_key_ogrok02  → CTO
xai_api_key_ogrok03  → Marketing Manager/CMO
xai_api_key_ogrok04  → Development Manager
xai_api_key_ogrok05  → Operations Manager/COO
xai_api_key_ogrok06  → Finance Manager/CFO
xai_api_key_ogrok07  → HR Manager/CHRO
xai_api_key_ogrok08  → Product Manager/CPO
xai_api_key_ogrok09  → Security Manager/CISO
xai_api_key_ogrok10  → Customer Manager/CCO
xai_api_key_ogrok11  → Board
xai_api_key_ogrok12  → Strategy Office Manager/CSO
```

### **oGPT Keys (OpenAI)**
```
openai_api_key_ogpt01  → CEO
openai_api_key_ogpt02  → CTO
openai_api_key_ogpt03  → Marketing Manager/CMO
openai_api_key_ogpt04  → Development Manager
openai_api_key_ogpt05  → Operations Manager/COO
openai_api_key_ogpt06  → Finance Manager/CFO
openai_api_key_ogpt07  → HR Manager/CHRO
openai_api_key_ogpt08  → Product Manager/CPO
openai_api_key_ogpt09  → Security Manager/CISO
openai_api_key_ogpt10  → Customer Manager/CCO
openai_api_key_ogpt11  → Board
openai_api_key_ogpt12  → Strategy Office Manager/CSO
```

### **Bridge Webhook HMAC Keys**
```
bridge_webhook_hmac_ogpt01  → HMAC pentru ogpt01
bridge_webhook_hmac_ogpt02  → HMAC pentru ogpt02
...
bridge_webhook_hmac_ogpt12  → HMAC pentru ogpt12
```

---

## 🏗️ **INTEGRAREA ÎN APLICAȚIE**

### **1. Variabile de mediu**
```bash
# În Cloud Run sau .env
SECRET_MANAGER_PROJECT_ID=coolbits-ai
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

### **2. Service Account**
```
coolbits-ai-app@coolbits-ai.iam.gserviceaccount.com
Permisiuni: roles/secretmanager.secretAccessor
```

### **3. Cod pentru accesarea cheilor**
```typescript
import { SecretManagerServiceClient } from '@google-cloud/secret-manager';

const client = new SecretManagerServiceClient();

async function getApiKey(role: string, provider: 'xai' | 'openai') {
  const secretName = provider === 'xai' 
    ? `xai_api_key_ogrok${role}` 
    : `openai_api_key_ogpt${role}`;
    
  const name = `projects/coolbits-ai/secrets/${secretName}/versions/latest`;
  
  const [version] = await client.accessSecretVersion({ name });
  return version.payload?.data?.toString();
}

// Exemplu de utilizare
const ceoXaiKey = await getApiKey('01', 'xai');
const ceoOpenAiKey = await getApiKey('01', 'openai');
```

---

## 🔒 **SECURITATE**

### **Best Practices Implementate:**
- ✅ **Replication automatic** - Backup în multiple regiuni
- ✅ **IAM Permissions** - Acces controlat prin Service Account
- ✅ **Audit Logging** - Toate accesurile sunt logate
- ✅ **Versioning** - Istoric complet al modificărilor
- ✅ **Encryption** - Criptare automată în repaus și tranzit

### **Monitoring:**
```bash
# Verifică accesurile la secrete
gcloud logging read "resource.type=secretmanager.googleapis.com/Secret" --limit=50

# Verifică audit logs
gcloud logging read "resource.type=secretmanager.googleapis.com/SecretVersion" --limit=50
```

---

## 🎯 **ROLURI ȘI SUBDOMAINE**

### **Mapping Roluri → Subdomene**
```
CEO (ogrok01/ogpt01)           → ceo.roles.coolbits.ai
CTO (ogrok02/ogpt02)           → cto.roles.coolbits.ai
Marketing Manager (ogrok03/ogpt03) → marketing.roles.coolbits.ai
Development Manager (ogrok04/ogpt04) → development.roles.coolbits.ai
Operations Manager (ogrok05/ogpt05) → operations.roles.coolbits.ai
Finance Manager (ogrok06/ogpt06) → finance.roles.coolbits.ai
HR Manager (ogrok07/ogpt07)    → hr.roles.coolbits.ai
Product Manager (ogrok08/ogpt08) → product.roles.coolbits.ai
Security Manager (ogrok09/ogpt09) → security.roles.coolbits.ai
Customer Manager (ogrok10/ogpt10) → customer.roles.coolbits.ai
Board (ogrok11/ogpt11)          → board.roles.coolbits.ai
Strategy Office Manager (ogrok12/ogpt12) → strategy.roles.coolbits.ai
```

---

## 🚨 **TROUBLESHOOTING**

### **Erori comune:**
1. **Permission denied** → Verifică IAM permissions
2. **Secret not found** → Verifică numele secretului
3. **Authentication failed** → Verifică Service Account

### **Debugging:**
```bash
# Testează accesul la un secret
gcloud secrets versions access latest --secret="xai_api_key_ogrok01"

# Verifică Service Account
gcloud auth list
gcloud config get-value account
```

---

## 📊 **STATUS MONITORING**

### **Comandă pentru verificarea statusului:**
```bash
# Script de monitoring
#!/bin/bash
echo "🔐 CoolBits.ai - API Keys Status"
echo "================================"

echo "📊 Secretele oGrok (xAI):"
gcloud secrets list --filter="name:xai_api_key_ogrok*" --format="table(name,createTime,state)"

echo ""
echo "📊 Secretele oGPT (OpenAI):"
gcloud secrets list --filter="name:openai_api_key_ogpt*" --format="table(name,createTime,state)"

echo ""
echo "📊 Bridge Webhook HMAC:"
gcloud secrets list --filter="name:bridge_webhook_hmac_ogpt*" --format="table(name,createTime,state)"
```

---

## 🎉 **SUCCES!**

**Integrarea completă include:**
- ✅ 24 chei API (12 oGrok + 12 oGPT)
- ✅ 12 chei Bridge Webhook HMAC
- ✅ Service Account cu permisiuni
- ✅ Best practices de securitate
- ✅ Documentație completă

**Gata pentru utilizare în aplicație!** 🚀
