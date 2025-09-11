# SmartBill - Soluția de Facturare COOL BITS SRL

## 📋 Overview

SmartBill este soluția completă de facturare pentru COOL BITS S.R.L., integrată cu SafeNet pentru semnarea digitală și delegarea operațiunilor către agenții interni.

## 🏢 Company Information

- **Company Name**: COOL BITS S.R.L.
- **CUI**: 42331573
- **Registration**: ROONRC.J22/676/2020
- **Address**: str. Columnei, nr.14, bl.K4, et.4, ap.19, Iași, România
- **Bank**: ING Office Iași Anastasie Panu
- **IBAN**: RO76INGB0000999910114315

## 🚀 System Components

### 1. SmartBill Core System (`smartbill_core_system.py`)

Sistemul principal de facturare cu următoarele funcționalități:

#### Key Features:
- ✅ Creare și gestionare facturi
- ✅ Calculare automată TVA
- ✅ Gestionare clienți
- ✅ Stocare persistentă JSON
- ✅ Statusuri factură (DRAFT, PENDING, APPROVED, SIGNED, SENT, PAID, OVERDUE, CANCELLED)
- ✅ Tipuri factură (STANDARD, PROFORMA, CREDIT_NOTE, DEBIT_NOTE, RECEIPT)

#### Usage Example:
```python
from smartbill_core_system import SmartBillCore, InvoiceType

# Initialize SmartBill
smartbill = SmartBillCore()

# Create invoice
client_data = {
    "name": "Client SRL",
    "cui": "12345678", 
    "address": "Strada Client, nr. 1, București"
}

items = [
    {
        "description": "Servicii software",
        "quantity": 10,
        "unit_price": 500.0,
        "vat_rate": 19.0
    }
]

invoice = smartbill.create_invoice(client_data, items)
```

### 2. SafeNet Integration (`smartbill_safenet_integration.py`)

Integrare completă cu SafeNet pentru semnarea digitală:

#### Key Features:
- ✅ Semnare digitală facturi cu SafeNet
- ✅ Verificare semnături
- ✅ Gestionare certificate
- ✅ Audit trail complet
- ✅ Niveluri securitate L1-L5
- ✅ Integrare API SafeNet

#### Usage Example:
```python
from smartbill_safenet_integration import SmartBillSafeNetIntegration

# Initialize SafeNet integration
safenet = SmartBillSafeNetIntegration()

# Sign invoice
result = safenet.sign_invoice_document(invoice_data, "L4")

# Verify signature
verification = safenet.verify_invoice_signature(invoice_id)
```

### 3. Agent Delegation (`smartbill_agent_delegation.py`)

Delegare operațiuni către agenții interni:

#### Delegated Agents:
- **ogpt01** - Frontend Agent (Frontend Development)
- **ogpt02** - Backend Agent (Backend Development)  
- **ogpt05** - Data Agent (Data Engineering)

#### Available Operations:
- `invoice_creation` - Creare factură
- `invoice_preview` - Preview factură
- `client_management` - Gestionare clienți
- `invoice_processing` - Procesare factură
- `api_management` - Gestionare API
- `data_validation` - Validare date
- `invoice_analytics` - Analiză facturi
- `reporting` - Generare rapoarte
- `data_export` - Export date

#### Usage Example:
```python
from smartbill_agent_delegation import SmartBillAgentDelegation

# Initialize agent delegation
agents = SmartBillAgentDelegation()

# Delegate operation
result = agents.delegate_operation(
    invoice_id="inv-123",
    operation="invoice_creation", 
    agent_id="ogpt01",
    priority="high"
)
```

### 4. oCursor & GeminiCLI Integration (`smartbill_cursor_gemini_integration.py`)

Integrare seamless cu oCursor și GeminiCLI:

#### Available Workflows:
- **invoice_creation_workflow** - Workflow complet creare factură
- **invoice_processing_workflow** - Workflow procesare factură
- **reporting_workflow** - Workflow generare rapoarte

#### Workflow Steps:
1. `cursor_code_generation` - Generare cod oCursor
2. `gemini_validation` - Validare GeminiCLI
3. `cursor_ui_optimization` - Optimizare UI oCursor
4. `gemini_deployment` - Deployment GeminiCLI

#### Usage Example:
```python
from smartbill_cursor_gemini_integration import SmartBillCursorGeminiIntegration

# Initialize integration
integration = SmartBillCursorGeminiIntegration()

# Execute workflow
result = integration.execute_integrated_workflow(
    "invoice_creation_workflow",
    invoice_data
)
```

### 5. API Server (`smartbill_api_server.py`)

API REST complet cu autentificare SafeNet:

#### API Endpoints:

##### System Status
- `GET /api/smartbill/status` - Status sistem SmartBill

##### Invoice Management
- `GET /api/smartbill/invoices` - Lista facturi
- `POST /api/smartbill/invoices` - Creare factură
- `GET /api/smartbill/invoices/<id>` - Detalii factură
- `POST /api/smartbill/invoices/<id>/sign` - Semnare factură

##### Agent Operations
- `POST /api/smartbill/invoices/<id>/delegate` - Delegare operațiune
- `GET /api/smartbill/agents` - Lista agenți
- `GET /api/smartbill/operations` - Lista operațiuni

##### Workflow Management
- `POST /api/smartbill/workflows` - Executare workflow
- `GET /api/smartbill/workflows` - Lista workflow-uri

##### Reports
- `GET /api/smartbill/reports/invoice` - Raport facturi
- `GET /api/smartbill/reports/delegation` - Raport delegări
- `GET /api/smartbill/reports/integration` - Raport integrare

##### SafeNet
- `GET /api/smartbill/safenet/status` - Status SafeNet
- `GET /api/smartbill/safenet/report` - Raport SafeNet

#### Usage Example:
```bash
# Start API server
python smartbill_api_server.py

# Create invoice via API
curl -X POST http://localhost:5002/api/smartbill/invoices \
  -H "Content-Type: application/json" \
  -d '{
    "client_data": {
      "name": "Client SRL",
      "cui": "12345678",
      "address": "Strada Client, nr. 1"
    },
    "items": [
      {
        "description": "Servicii software",
        "quantity": 5,
        "unit_price": 1000.0,
        "vat_rate": 19.0
      }
    ]
  }'

# Sign invoice
curl -X POST http://localhost:5002/api/smartbill/invoices/inv-123/sign \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "ogpt01"}'

# Delegate operation
curl -X POST http://localhost:5002/api/smartbill/invoices/inv-123/delegate \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "invoice_creation",
    "agent_id": "ogpt01",
    "priority": "high"
  }'
```

## 🔧 Installation & Setup

### Prerequisites

1. **Python 3.8+** installed
2. **Flask** for API server
3. **SafeNet Authentication Client** (for production)
4. **Write permissions** to workspace directory

### Required Python Modules

```bash
pip install flask>=2.0.0
pip install flask-cors>=3.0.0
pip install requests>=2.25.0
```

### Installation Steps

1. **Clone or download SmartBill files**
2. **Install dependencies**:
   ```bash
   pip install flask flask-cors requests
   ```

3. **Run complete system demo**:
   ```bash
   python smartbill_complete_system.py
   ```

4. **Start API server**:
   ```bash
   python smartbill_api_server.py
   ```

5. **Access API documentation**:
   ```
   http://localhost:5002/api/smartbill/status
   ```

## 📊 System Architecture

```
SmartBill System Architecture
=============================

┌─────────────────────────────────────────────────────────────┐
│                    SmartBill Core System                    │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   Invoice Mgmt  │  │  Client Mgmt    │  │  Data Store  │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    SafeNet Integration                      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │ Digital Signing │  │ Certificate Mgmt│  │ Audit Trail  │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                   Agent Delegation System                   │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │    ogpt01       │  │    ogpt02       │  │    ogpt05    │ │
│  │  Frontend Agent │  │  Backend Agent  │  │  Data Agent  │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│              oCursor & GeminiCLI Integration               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   oCursor       │  │   GeminiCLI     │  │  Workflows   │ │
│  │  Development    │  │  AI Processing  │  │  Automation  │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                      API Server                            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   REST API      │  │   Authentication│  │  Monitoring  │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 🔐 Security Features

### SafeNet Integration
- **Multi-Level Security**: L1 (Basic) to L5 (Maximum)
- **Digital Signing**: Timestamped signatures with document integrity
- **Certificate Management**: Secure storage and automatic renewal
- **Audit Trail**: Comprehensive logging for 7 years
- **Compliance**: GDPR compliant with tamper-proof logging

### Agent Security
- **Permission-Based Access**: Each agent has specific permissions
- **Operation Validation**: All operations validated before execution
- **Delegation Tracking**: Complete audit trail of all delegations
- **Access Levels**: L3-L5 security levels for different agents

## 📈 Monitoring & Reporting

### Available Reports
1. **Invoice Report**: Total invoices, amounts, status distribution
2. **Delegation Report**: Agent performance, operation statistics
3. **Integration Report**: oCursor/GeminiCLI operation statistics
4. **SafeNet Report**: Signing statistics, certificate status

### Monitoring Features
- Real-time system status
- Agent activity monitoring
- Workflow execution tracking
- API usage statistics
- Error logging and alerting

## 🚀 Production Deployment

### Environment Setup
```bash
# Production environment variables
export COMPANY_NAME="COOL BITS S.R.L."
export COMPANY_CUI="42331573"
export SAFENET_API_ENDPOINT="https://safenet-api.company.com"
export API_HOST="0.0.0.0"
export API_PORT="5002"
```

### Docker Deployment (Optional)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 5002
CMD ["python", "smartbill_api_server.py"]
```

## 📞 Support & Contact

### Technical Support
- **Company**: COOL BITS S.R.L.
- **Email**: coolbits.dm@gmail.com
- **CEO**: andrei@coolbits.ro
- **CTO**: bogdan.boureanu@gmail.com

### Documentation
- **SmartBill Integration Guide**: This document
- **API Documentation**: Available at `/api/smartbill/status`
- **SafeNet Documentation**: `SAFENET_INTEGRATION_DOCUMENTATION.md`

## 🔒 Legal & Compliance

### Data Protection
- All operations comply with GDPR requirements
- Audit trails maintained for 7 years
- Secure storage of certificates and keys
- Regular security reviews

### Company Compliance
- COOL BITS S.R.L. registration: ROONRC.J22/676/2020
- CUI: 42331573
- Banking: ING Office Iași Anastasie Panu
- IBAN: RO76INGB0000999910114315

---

**Document Version**: 1.0  
**Last Updated**: 2024-01-XX  
**Company**: COOL BITS S.R.L.  
**CUI**: 42331573  
**System**: SmartBill - Complete Billing Solution
