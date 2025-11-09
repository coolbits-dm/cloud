# 🚀 RAG Corpus Creation Guide for CoolBits.ai

## 📋 **Overview**

Acest ghid te ghidează prin procesul automatizat de creare a tuturor celor 88 RAG corpora pentru CoolBits.ai folosind gcloud CLI, conform recomandărilor Gemini boss.

## 🎯 **Ce facem:**

1. **Creează 88 RAG corpora** în Vertex AI Search
2. **Creează 88 Search Apps** pentru fiecare corpus
3. **Configurează data sources** pentru Cloud Storage buckets
4. **Testează funcționalitatea** cu query-uri de test

## 📁 **Scripturi disponibile:**

### **1. create_rag_corpora_automated.sh** (Linux/macOS)
- Script bash pentru crearea automată a tuturor RAG-urilor
- Folosește gcloud CLI pentru Vertex AI RAG Engine
- Creează corpora, search apps și data sources

### **2. create_rag_corpora_automated.ps1** (Windows PowerShell)
- Script PowerShell pentru Windows
- Aceeași funcționalitate ca scriptul bash
- Optimizat pentru mediul Windows

### **3. test_rag_corpora.sh** (Linux/macOS)
- Script pentru testarea RAG-urilor create
- Testează query-uri pe fiecare corpus
- Verifică funcționalitatea completă

## 🚀 **Pași de execuție:**

### **Pasul 1: Pregătirea mediului**

```bash
# Verifică că gcloud CLI este instalat și configurat
gcloud auth list
gcloud config get-value project

# Setează proiectul corect dacă nu este deja setat
gcloud config set project coolbits-ai
```

### **Pasul 2: Executarea scriptului de creare**

#### **Pentru Linux/macOS:**
```bash
# Execută scriptul bash
./create_rag_corpora_automated.sh
```

#### **Pentru Windows PowerShell:**
```powershell
# Execută scriptul PowerShell
.\create_rag_corpora_automated.ps1
```

### **Pasul 3: Testarea RAG-urilor**

```bash
# Testează RAG-urile create
./test_rag_corpora.sh
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

### **Corpus Configuration:**
- **Name:** `{rag_id}-corpus`
- **Description:** `RAG corpus for {rag_name}`
- **Embedding Model:** `text-embedding-004` (Google)
- **Region:** `europe-west1`

### **Data Source Configuration:**
- **Bucket:** `coolbits-rag-{rag_id}-coolbits-ai`
- **File Types:** PDF, TXT, DOC, DOCX
- **Chunk Size:** 1024
- **Chunk Overlap:** 200

### **Search App Configuration:**
- **Name:** `{rag_id}-search-app`
- **Description:** `Search app for {rag_name}`
- **Data Store:** Corpus-ul creat mai sus

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
  "pageSize": 5
}
```

### **Query de test pentru banking:**
```json
{
  "query": "What are the key regulations in commercial banking?",
  "pageSize": 5
}
```

## ⚠️ **Notă importantă:**

Scripturile creează structura RAG-urilor, dar pentru funcționalitate completă trebuie să:

1. **Uploadezi documente** în Cloud Storage buckets
2. **Aștepți indexarea** corpus-urilor
3. **Configurezi autentificarea** pentru API endpoints
4. **Testezi query-urile** cu documente reale

## 🔍 **Troubleshooting:**

### **Eroare: "Corpus already exists"**
- Scriptul detectează automat corpus-urile existente
- Sare peste crearea duplicatelor
- Continuă cu următoarele RAG-uri

### **Eroare: "Bucket does not exist"**
- Data source creation poate eșua dacă bucket-ul nu există
- Nu afectează crearea corpus-ului
- Bucket-urile pot fi create separat

### **Eroare: "Search app creation failed"**
- Verifică că corpus-ul a fost creat cu succes
- Verifică permisiunile pentru Vertex AI
- Reîncearcă crearea manuală dacă este necesar

## 📞 **Support:**

Dacă întâmpini probleme:
1. Verifică logs-urile scriptului
2. Verifică permisiunile gcloud CLI
3. Verifică că proiectul `coolbits-ai` este activ
4. Contactează pentru suport tehnic

## 🎉 **Rezultat final:**

După execuția completă a scripturilor, vei avea:
- ✅ 88 RAG corpora create în Vertex AI
- ✅ 88 Search Apps configurate
- ✅ 88 Data Sources conectate la Cloud Storage
- ✅ Structura completă pentru toate industriile CoolBits.ai
- ✅ API endpoints gata pentru integrare

**Next Steps:** Upload documente specifice pentru fiecare industrie și integrează cu Business Panel!
