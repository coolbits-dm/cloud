# 🚀 Complete RAG Creation Guide - Python SDK & REST API

## 📋 **Overview**

Acest ghid te ghidează prin procesul automatizat de creare a tuturor celor 88 RAG corpora pentru CoolBits.ai folosind două metode:

1. **Python SDK** - Script Python cu Vertex AI SDK
2. **REST API** - Script bash cu apeluri REST directe

## 🎯 **Ce facem:**

1. **Creează 88 RAG corpora** în Vertex AI Discovery Engine
2. **Creează 88 Search Apps** pentru fiecare corpus
3. **Configurează GCS connectors** pentru Cloud Storage buckets
4. **Testează funcționalitatea** cu query-uri de test

## 📁 **Scripturi disponibile:**

### **1. Python SDK Approach**
- `create_rag_corpora_python.py` - Script Python cu Vertex AI SDK
- `test_rag_corpora_rest_api.sh` - Testare cu REST API

### **2. REST API Approach**
- `create_rag_corpora_rest_api.sh` - Script bash cu REST API
- `test_rag_corpora_rest_api.sh` - Testare cu REST API

## 🐍 **Metoda 1: Python SDK**

### **Instalare dependențe:**
```bash
pip install google-cloud-discoveryengine google-cloud-storage
```

### **Execuție:**
```bash
python3 create_rag_corpora_python.py
```

### **Avantaje:**
- ✅ Folosește SDK oficial Google Cloud
- ✅ Gestionare automată a operațiunilor asincrone
- ✅ Error handling robust
- ✅ Logging detaliat

### **Dezavantaje:**
- ❌ Necesită instalare Python packages
- ❌ Poate fi mai lent pentru operațiuni mari

## 🌐 **Metoda 2: REST API**

### **Cerințe:**
- Google Cloud Shell sau Linux/macOS
- `jq` pentru procesarea JSON
- `curl` pentru apeluri HTTP

### **Execuție:**
```bash
chmod +x create_rag_corpora_rest_api.sh
./create_rag_corpora_rest_api.sh
```

### **Avantaje:**
- ✅ Nu necesită instalare packages Python
- ✅ Funcționează în Cloud Shell
- ✅ Control complet asupra apelurilor API
- ✅ Rapid și eficient

### **Dezavantaje:**
- ❌ Necesită gestionare manuală a operațiunilor
- ❌ Error handling mai complex

## 🚀 **Pași de execuție:**

### **Pasul 1: Pregătirea mediului**

#### **Pentru Python SDK:**
```bash
# Instalează dependențele
pip install google-cloud-discoveryengine google-cloud-storage

# Verifică autentificarea
gcloud auth application-default login
```

#### **Pentru REST API:**
```bash
# Verifică autentificarea
gcloud auth list
gcloud config get-value project

# Instalează jq dacă nu este instalat
sudo apt-get install jq
```

### **Pasul 2: Executarea scriptului**

#### **Python SDK:**
```bash
python3 create_rag_corpora_python.py
```

#### **REST API:**
```bash
./create_rag_corpora_rest_api.sh
```

### **Pasul 3: Testarea RAG-urilor**

```bash
chmod +x test_rag_corpora_rest_api.sh
./test_rag_corpora_rest_api.sh
```

## 📊 **Structura RAG-urilor create:**

### **Phase 1: High Priority (5 RAGs)**
- `ai_board` - AI Board management
- `business` - Business AI Council
- `agritech` - Agricultural Technology
- `banking` - Banking Services
- `saas_b2b` - SaaS B2B

### **Phase 2: Medium Priority (5 RAGs)**
- `healthcare` - Healthcare Technology
- `exchanges` - Cryptocurrency Exchanges
- `user` - Personal AI Assistant
- `agency` - Agency Management
- `dev` - Developer Tools

### **Phase 3: All Industries (75 RAGs)**
- Toate industriile din lista completă
- De la AgTech la Space Technology
- Incluzând toate sectoarele economice

### **Phase 4: Panel RAGs (6 RAGs)**
- `andrei-panel` - Andrei Panel
- `user-panel` - User Panel
- `business-panel` - Business Panel
- `agency-panel` - Agency Panel
- `dev-panel` - Dev Panel
- `admin-panel` - Admin Panel

## 🔧 **Configurația fiecărui RAG:**

### **Data Store Configuration:**
- **Name:** `{rag_id}-corpus`
- **Description:** `RAG corpus for {rag_name}`
- **Industry Vertical:** `GENERIC`
- **Solution Type:** `SOLUTION_TYPE_SEARCH`
- **Content Config:** `CONTENT_REQUIRED`

### **GCS Connector Configuration:**
- **Bucket:** `coolbits-rag-{rag_id}-coolbits-ai`
- **Input URIs:** `gs://{bucket_name}/*`
- **Data Schema:** `content`

### **Search App Configuration:**
- **Name:** `{rag_id}-search-app`
- **Description:** `Search app for {rag_name}`
- **Search Tier:** `SEARCH_TIER_STANDARD`
- **Search Add-ons:** `SEARCH_ADD_ON_LLM`

## 📝 **API Endpoints generate:**

Pentru fiecare RAG, se generează un endpoint de forma:
```
https://discoveryengine.googleapis.com/v1beta/projects/coolbits-ai/locations/global/searchApps/{search-app-id}/servingConfigs/default_search:search
```

## 🧪 **Testare:**

### **Query de test pentru ai_board:**
```json
{
  "query": "What are the best practices for AI Board management?",
  "pageSize": 3,
  "queryExpansionSpec": {
    "condition": "AUTO"
  },
  "spellCorrectionSpec": {
    "mode": "AUTO"
  }
}
```

### **Query de test pentru banking:**
```json
{
  "query": "What are the key regulations in commercial banking?",
  "pageSize": 3
}
```

## ⚠️ **Notă importantă:**

Scripturile creează structura RAG-urilor, dar pentru funcționalitate completă trebuie să:

1. **Uploadezi documente** în Cloud Storage buckets
2. **Aștepți indexarea** corpus-urilor
3. **Configurezi autentificarea** pentru API endpoints
4. **Testezi query-urile** cu documente reale

## 🔍 **Troubleshooting:**

### **Eroare: "Data store already exists"**
- Scripturile detectează automat corpus-urile existente
- Sare peste crearea duplicatelor
- Continuă cu următoarele RAG-uri

### **Eroare: "Bucket does not exist"**
- GCS connector creation poate eșua dacă bucket-ul nu există
- Nu afectează crearea data store-ului
- Bucket-urile pot fi create separat

### **Eroare: "Search app creation failed"**
- Verifică că data store-ul a fost creat cu succes
- Verifică permisiunile pentru Vertex AI
- Reîncearcă crearea manuală dacă este necesar

### **Eroare: "Access token expired"**
- Re-autentifică-te cu `gcloud auth login`
- Pentru Python SDK: `gcloud auth application-default login`

## 📞 **Support:**

Dacă întâmpini probleme:
1. Verifică logs-urile scriptului
2. Verifică permisiunile gcloud CLI
3. Verifică că proiectul `coolbits-ai` este activ
4. Contactează pentru suport tehnic

## 🎉 **Rezultat final:**

După execuția completă a scripturilor, vei avea:
- ✅ 88 RAG data stores create în Vertex AI Discovery Engine
- ✅ 88 Search Apps configurate
- ✅ 88 GCS Connectors conectate la Cloud Storage
- ✅ Structura completă pentru toate industriile CoolBits.ai
- ✅ API endpoints gata pentru integrare

**Next Steps:** Upload documente specifice pentru fiecare industrie și integrează cu Business Panel!

## 🔗 **Resurse utile:**

- [Vertex AI Discovery Engine Documentation](https://cloud.google.com/generative-ai-app-builder/docs)
- [Discovery Engine REST API Reference](https://cloud.google.com/generative-ai-app-builder/docs/reference/rest)
- [Python SDK Documentation](https://cloud.google.com/python/docs/reference/discoveryengine/latest)
