# Vertex AI Architecture pentru Andy & Kim

## Arhitectura Completă în Google Cloud

```
┌─────────────────────────────────────────────────────────────────┐
│                    GOOGLE CLOUD PLATFORM                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐                   │
│  │   ANDY AGENT    │    │   KIM AGENT      │                   │
│  │   Cloud Run     │    │   Cloud Run      │                   │
│  │   Port: 8101    │    │   Port: 8102    │                   │
│  └─────────────────┘    └─────────────────┘                   │
│           │                       │                           │
│           └───────────┬───────────┘                           │
│                       │                                       │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              VERTEX AI MODEL GARDEN                    │  │
│  │                                                         │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │  │
│  │  │Gemini 1.5 Pro│  │   Codey     │  │Gemini 1.0 Pro│    │  │
│  │  │$3.50/1M inp  │  │$0.50/1M inp │  │$0.50/1M inp  │    │  │
│  │  │$10.50/1M out │  │$1.50/1M out │  │$1.50/1M out  │    │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘    │  │
│  └─────────────────────────────────────────────────────────┘  │
│                       │                                       │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              VERTEX AI SEARCH & RAG                     │  │
│  │                                                         │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │  │
│  │  │RAG Corpora  │  │Vector Store │  │Knowledge    │    │  │
│  │  │coolbits.ai │  │pgvector     │  │Base Search   │    │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘    │  │
│  └─────────────────────────────────────────────────────────┘  │
│                       │                                       │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              SECRET MANAGER                              │  │
│  │                                                         │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │  │
│  │  │API Keys     │  │Auth Tokens   │  │HMAC Keys    │    │  │
│  │  │Andy/Kim     │  │OAuth        │  │ogpt/ogrok   │    │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘    │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Beneficii Arhitectură Vertex AI

### 🚀 **Scalabilitate**
- **Auto-scaling**: De la 0 la milioane de request-uri
- **Global**: Disponibil în toate regiunile Google Cloud
- **Load Balancing**: Distribuție automată a traficului

### 💰 **Model de Cost Optimizat**
- **Pay-per-use**: Plătești doar ce folosești
- **Free Tier**: 1M tokeni gratis/lună pentru Gemini
- **Volume Discounts**: Reduceri pentru utilizare mare

### 🔒 **Securitate Enterprise**
- **Encryption**: Toate datele criptate în tranzit și la rest
- **IAM**: Control granular al accesului
- **Audit Logs**: Monitorizare completă a activității

### 🛠️ **Management Simplificat**
- **Single Console**: Totul într-un singur loc
- **Monitoring**: Cloud Monitoring integrat
- **Backup**: Backup automat și disaster recovery
