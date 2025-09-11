# Plan de Migrare Andy & Kim la Vertex AI

## Faza 1: Pregătire Infrastructură (1-2 zile)

### 1.1 Configurare Vertex AI
```bash
# Activează API-urile necesare
gcloud services enable aiplatform.googleapis.com
gcloud services enable discoveryengine.googleapis.com
gcloud services enable secretmanager.googleapis.com

# Configurează regiunea
gcloud config set compute/region europe-west3
gcloud config set ai/region europe-west3
```

### 1.2 Creare RAG Corpora
```bash
# Creează corpus pentru coolbits.ai
gcloud ai search corpora create \
  --display-name="coolbits-ai-knowledge" \
  --location=europe-west3 \
  --project=coolbits-ai
```

### 1.3 Migrare API Keys
```bash
# Migrează toate cheile în Secret Manager
gcloud secrets create andy-gemini-key --data-file=andy_gemini_key.txt
gcloud secrets create kim-gemini-key --data-file=kim_gemini_key.txt
gcloud secrets create andy-codey-key --data-file=andy_codey_key.txt
```

## Faza 2: Containerizare Aplicații (2-3 zile)

### 2.1 Dockerfile pentru Andy
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
EXPOSE 8101
CMD ["node", "andy-server.js"]
```

### 2.2 Dockerfile pentru Kim
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
EXPOSE 8102
CMD ["node", "kim-server.js"]
```

### 2.3 Deploy la Cloud Run
```bash
# Build și deploy Andy
gcloud run deploy andy-agent \
  --source . \
  --platform managed \
  --region europe-west3 \
  --port 8101 \
  --set-env-vars="NODE_ENV=production,AGENT_TYPE=andy"

# Build și deploy Kim
gcloud run deploy kim-agent \
  --source . \
  --platform managed \
  --region europe-west3 \
  --port 8102 \
  --set-env-vars="NODE_ENV=production,AGENT_TYPE=kim"
```

## Faza 3: Integrare Vertex AI (3-4 zile)

### 3.1 Configurare Modele
```javascript
// andy-vertex-client.js
const { VertexAI } = require('@google-cloud/vertexai');

const vertexAI = new VertexAI({
  project: 'coolbits-ai',
  location: 'europe-west3'
});

const geminiModel = vertexAI.getGenerativeModel({
  model: 'gemini-1.5-pro',
  generationConfig: {
    maxOutputTokens: 8192,
    temperature: 0.7,
  }
});

const codeyModel = vertexAI.getGenerativeModel({
  model: 'code-bison',
  generationConfig: {
    maxOutputTokens: 4096,
    temperature: 0.3,
  }
});
```

### 3.2 Integrare RAG
```javascript
// rag-integration.js
const { DiscoveryEngineClient } = require('@google-cloud/discoveryengine');

const client = new DiscoveryEngineClient({
  projectId: 'coolbits-ai',
  location: 'europe-west3'
});

async function searchKnowledge(query, agentType) {
  const request = {
    servingConfig: `projects/coolbits-ai/locations/europe-west3/servingConfigs/${agentType}-config`,
    query: query,
    pageSize: 5
  };
  
  const [response] = await client.search(request);
  return response.results;
}
```

## Faza 4: Testing și Optimizare (2-3 zile)

### 4.1 Teste Funcționale
- Testare toate rutele Andy și Kim
- Verificare WebSocket connections
- Testare model routing
- Verificare RAG integration

### 4.2 Optimizare Performanță
- Configurare auto-scaling
- Optimizare cache
- Monitorizare costuri
- Fine-tuning modele

## Faza 5: Go-Live (1 zi)

### 5.1 DNS și Load Balancer
```bash
# Configurează custom domain
gcloud run domain-mappings create \
  --service andy-agent \
  --domain andy.coolbits.ai \
  --region europe-west3

gcloud run domain-mappings create \
  --service kim-agent \
  --domain kim.coolbits.ai \
  --region europe-west3
```

### 5.2 Monitorizare
- Setup Cloud Monitoring
- Configurează alerts
- Activează audit logs
- Testare finală

## Timeline Total: 9-13 zile
## Cost Estimativ: $50-100/lună (inclusiv free tier)
