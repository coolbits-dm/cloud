# CoolBits.ai API Documentation

## 📋 Overview
Complete API documentation for CoolBits.ai Offline AI Board system with 67 organizational roles, 6 panel system, bits framework, and cbT economy.

**CEO**: Andrei - andrei@coolbits.ro  
**Managed by**: oCursor (Local Development)  
**Base URL**: http://localhost:8082  
**Version**: 1.0.0  
**Mode**: OFFLINE (no internet required)

## 🚀 Quick Start

### Prerequisites
- Node.js v22.18.0+ installed
- CoolBits.ai AI Board running on port 8082
- Configuration files: `coolbits_ai_config.json` or `coolbits_ai_config.yaml`

### Start AI Board
```bash
# Start the AI Board server
node coolbits_ai_board_node.js

# Or use the batch file
start_ai_board_node.bat
```

### Test Connection
```bash
# Health check
curl http://localhost:8082/health

# Or using PowerShell
Invoke-WebRequest -Uri "http://localhost:8082/health" -UseBasicParsing
```

## 🔗 API Endpoints

### Health & Status

#### GET /health
**Description**: Health check and system status  
**Response**: System health information

**Example Request**:
```bash
curl http://localhost:8082/health
```

**Example Response**:
```json
{
  "status": "healthy",
  "service": "CoolBits.ai Offline AI Board (Node.js)",
  "ceo": "Andrei - andrei@coolbits.ro",
  "timestamp": "2025-01-07T16:32:43Z",
  "port": 8082,
  "roles_count": 67,
  "panels_count": 6,
  "bits_count": 5
}
```

#### GET /board
**Description**: AI Board status and metrics  
**Response**: Board status information

**Example Request**:
```bash
curl http://localhost:8082/board
```

**Example Response**:
```json
{
  "success": true,
  "board_status": {
    "roles": 67,
    "panels": 6,
    "bits": 5,
    "cbt_total": 1000000,
    "status": "ACTIVE",
    "mode": "OFFLINE"
  },
  "timestamp": "2025-01-07T16:32:43Z"
}
```

### Organizational Structure

#### GET /organization
**Description**: Complete organizational structure with all 67 roles  
**Response**: Full organizational hierarchy

**Example Request**:
```bash
curl http://localhost:8082/organization
```

**Example Response**:
```json
{
  "success": true,
  "organization": {
    "executive": {
      "ceo": {
        "name": "CEO",
        "email": "ceo@coolbits.ai",
        "status": "ACTIVE"
      },
      "strategy-office-cso": {
        "name": "CSO",
        "email": "cso@coolbits.ai",
        "status": "ACTIVE"
      },
      "board": {
        "name": "Board",
        "email": "board@coolbits.ai",
        "status": "ACTIVE"
      }
    },
    "technology": {
      "cto": {
        "name": "CTO",
        "email": "cto@coolbits.ai",
        "status": "ACTIVE"
      },
      "engineering": {
        "backend": {
          "name": "Backend Engineering",
          "email": "backend@coolbits.ai",
          "status": "ACTIVE"
        },
        "frontend": {
          "name": "Frontend Engineering",
          "email": "frontend@coolbits.ai",
          "status": "ACTIVE"
        }
      }
    }
  },
  "total_roles": 67,
  "timestamp": "2025-01-07T16:32:43Z"
}
```

#### GET /roles
**Description**: All roles in the organization  
**Response**: Complete roles list

**Example Request**:
```bash
curl http://localhost:8082/roles
```

#### GET /roles/{category}
**Description**: Roles filtered by category  
**Parameters**: 
- `category` (string): Category name (executive, technology, product, etc.)

**Example Request**:
```bash
curl http://localhost:8082/roles/executive
curl http://localhost:8082/roles/technology
curl http://localhost:8082/roles/product
```

**Example Response**:
```json
{
  "success": true,
  "category": "executive",
  "roles": {
    "ceo": {
      "name": "CEO",
      "email": "ceo@coolbits.ai",
      "status": "ACTIVE"
    },
    "strategy-office-cso": {
      "name": "CSO",
      "email": "cso@coolbits.ai",
      "status": "ACTIVE"
    },
    "board": {
      "name": "Board",
      "email": "board@coolbits.ai",
      "status": "ACTIVE"
    }
  },
  "timestamp": "2025-01-07T16:32:43Z"
}
```

### Panel System

#### GET /panels
**Description**: All panels in the system  
**Response**: Complete panel information

**Example Request**:
```bash
curl http://localhost:8082/panels
```

**Example Response**:
```json
{
  "success": true,
  "panels": {
    "user": {
      "name": "User Panel",
      "description": "General user dashboard",
      "access_level": "USER",
      "features": ["basic_ai_chat", "personal_dashboard", "user_settings"],
      "status": "ACTIVE"
    },
    "business": {
      "name": "Business Panel",
      "description": "Business management dashboard",
      "access_level": "BUSINESS",
      "features": ["business_ai_council", "multi_business_select", "business_analytics"],
      "status": "ACTIVE"
    },
    "agency": {
      "name": "Agency Panel",
      "description": "Digital marketing agency panel with MCC connects",
      "access_level": "AGENCY",
      "features": ["mcc_connects", "agency_tools", "client_management"],
      "status": "ACTIVE"
    },
    "dev": {
      "name": "Developer Panel",
      "description": "Developer panel with all developer tools",
      "access_level": "DEVELOPER",
      "features": ["cursor_integration", "google_cloud", "github", "api_tools"],
      "status": "ACTIVE"
    },
    "admin": {
      "name": "Admin Panel",
      "description": "User admin panel",
      "access_level": "ADMIN",
      "features": ["user_management", "system_settings", "admin_tools"],
      "status": "ACTIVE"
    },
    "andrei": {
      "name": "Andrei God Mode",
      "description": "CEO God mode panel with dedicated API keys",
      "access_level": "GOD_MODE",
      "features": ["full_access", "dedicated_openai", "dedicated_grok", "system_control"],
      "status": "ACTIVE"
    }
  },
  "total_panels": 6,
  "timestamp": "2025-01-07T16:32:43Z"
}
```

#### GET /panels/{panel_name}
**Description**: Specific panel details  
**Parameters**:
- `panel_name` (string): Panel name (user, business, agency, dev, admin, andrei)

**Example Request**:
```bash
curl http://localhost:8082/panels/andrei
curl http://localhost:8082/panels/user
curl http://localhost:8082/panels/business
```

**Example Response**:
```json
{
  "success": true,
  "panel": {
    "name": "Andrei God Mode",
    "description": "CEO God mode panel with dedicated API keys",
    "access_level": "GOD_MODE",
    "features": ["full_access", "dedicated_openai", "dedicated_grok", "system_control"],
    "status": "ACTIVE"
  },
  "timestamp": "2025-01-07T16:32:43Z"
}
```

### Bits Framework

#### GET /bits
**Description**: Bits framework information  
**Response**: Complete bits framework

**Example Request**:
```bash
curl http://localhost:8082/bits
```

**Example Response**:
```json
{
  "success": true,
  "bits_framework": {
    "c-bit": {
      "name": "Cool Bits (Admin Bits)",
      "description": "Secret internal CEO level bits",
      "access_level": "CEO_ONLY",
      "features": ["system_control", "god_mode_access", "all_permissions"],
      "status": "ACTIVE"
    },
    "u-bit": {
      "name": "User Bits",
      "description": "User level bits and permissions",
      "access_level": "USER",
      "features": ["personal_ai", "user_dashboard", "basic_features"],
      "status": "ACTIVE"
    },
    "b-bit": {
      "name": "Business Bits",
      "description": "Business level bits and permissions",
      "access_level": "BUSINESS",
      "features": ["business_ai_council", "multi_business", "business_analytics"],
      "status": "ACTIVE"
    },
    "a-bit": {
      "name": "Agency Bits",
      "description": "Agency level bits and permissions",
      "access_level": "AGENCY",
      "features": ["mcc_connects", "agency_tools", "client_management"],
      "status": "ACTIVE"
    },
    "d-bit": {
      "name": "Developer Bits",
      "description": "Developer level bits and permissions",
      "access_level": "DEVELOPER",
      "features": ["dev_tools", "api_access", "integration_tools"],
      "status": "ACTIVE"
    }
  },
  "total_bits": 5,
  "timestamp": "2025-01-07T16:32:43Z"
}
```

#### GET /bits/{bit_type}
**Description**: Specific bit type details  
**Parameters**:
- `bit_type` (string): Bit type (c-bit, u-bit, b-bit, a-bit, d-bit)

**Example Request**:
```bash
curl http://localhost:8082/bits/c-bit
curl http://localhost:8082/bits/u-bit
curl http://localhost:8082/bits/b-bit
```

**Example Response**:
```json
{
  "success": true,
  "bit": {
    "name": "Cool Bits (Admin Bits)",
    "description": "Secret internal CEO level bits",
    "access_level": "CEO_ONLY",
    "features": ["system_control", "god_mode_access", "all_permissions"],
    "status": "ACTIVE"
  },
  "timestamp": "2025-01-07T16:32:43Z"
}
```

### cbT Economy

#### GET /cbt
**Description**: cbT economy status  
**Response**: Economy information and allocations

**Example Request**:
```bash
curl http://localhost:8082/cbt
```

**Example Response**:
```json
{
  "success": true,
  "cbt_economy": {
    "total_supply": 1000000,
    "circulating": 750000,
    "reserved": 250000,
    "allocation": {
      "c-bit": 100000,
      "u-bit": 200000,
      "b-bit": 200000,
      "a-bit": 150000,
      "d-bit": 100000
    },
    "transactions": [],
    "status": "ACTIVE"
  },
  "timestamp": "2025-01-07T16:32:43Z"
}
```

#### POST /cbt/transfer
**Description**: Transfer cbT tokens between bit types  
**Request Body**:
```json
{
  "from": "c-bit",
  "to": "u-bit",
  "amount": 1000
}
```

**Example Request**:
```bash
curl -X POST http://localhost:8082/cbt/transfer \
  -H "Content-Type: application/json" \
  -d '{"from": "c-bit", "to": "u-bit", "amount": 1000}'
```

**Example Response**:
```json
{
  "success": true,
  "transaction": {
    "id": 1,
    "from": "c-bit",
    "to": "u-bit",
    "amount": 1000,
    "timestamp": "2025-01-07T16:32:43Z",
    "status": "COMPLETED"
  },
  "timestamp": "2025-01-07T16:32:43Z"
}
```

### AI Board Commands

#### POST /board/command
**Description**: Execute AI Board command  
**Request Body**:
```json
{
  "command": "status"
}
```

**Available Commands**:
- `status` - Get board status
- `roles` - Get all roles
- `panels` - Get all panels
- `bits` - Get bits framework
- `cbt` - Get cbT economy

**Example Request**:
```bash
curl -X POST http://localhost:8082/board/command \
  -H "Content-Type: application/json" \
  -d '{"command": "status"}'
```

**Example Response**:
```json
{
  "success": true,
  "command": "status",
  "response": {
    "roles": 67,
    "panels": 6,
    "bits": 5,
    "status": "ACTIVE"
  },
  "timestamp": "2025-01-07T16:32:43Z"
}
```

## 🎛️ Web Interface

### GET /ai-board
**Description**: AI Board web interface  
**Response**: HTML interface

**Example Request**:
```bash
# Open in browser
http://localhost:8082/ai-board
```

**Features**:
- Complete organizational structure visualization
- Panel system overview
- Bits framework display
- cbT economy status
- Real-time Socket.IO communication
- Interactive dashboard

## 🔌 Socket.IO Events

### Connection Events

#### connect
**Description**: Client connection  
**Emitted**: When client connects  
**Data**: Connection information

#### disconnect
**Description**: Client disconnection  
**Emitted**: When client disconnects  
**Data**: Disconnection information

### Board Events

#### board_command
**Description**: Send AI Board command  
**Data**:
```json
{
  "command": "status"
}
```

#### board_response
**Description**: Receive AI Board response  
**Data**:
```json
{
  "success": true,
  "response": {
    "roles": 67,
    "panels": 6,
    "bits": 5,
    "status": "ACTIVE"
  }
}
```

#### board_status
**Description**: Board status update  
**Data**:
```json
{
  "roles": 67,
  "panels": 6,
  "bits": 5,
  "status": "ACTIVE"
}
```

## 🛠️ Administration Script

### Usage
```bash
# Show help
python coolbits_admin.py --help

# Show system health
python coolbits_admin.py health

# List all roles
python coolbits_admin.py roles

# List roles by category
python coolbits_admin.py roles --category executive

# List all panels
python coolbits_admin.py panels

# List bits framework
python coolbits_admin.py bits

# Show cbT economy
python coolbits_admin.py cbt

# Transfer cbT tokens
python coolbits_admin.py cbt --transfer c-bit u-bit 1000

# Execute board command
python coolbits_admin.py board --command status

# Generate comprehensive report
python coolbits_admin.py report
```

### Configuration Files
- **JSON**: `coolbits_ai_config.json`
- **YAML**: `coolbits_ai_config.yaml`

## 🔒 Security & RBAC

### Access Levels
- **GOD_MODE**: CEO level access (Andrei)
- **CEO_ONLY**: CEO-only operations
- **EXECUTIVE**: Executive team access
- **BOARD_LEVEL**: Board of directors access
- **TECHNOLOGY_LEAD**: Technology leadership
- **PRODUCT_LEAD**: Product leadership
- **DATA_LEAD**: Data leadership
- **SECURITY_LEAD**: Security leadership
- **IT_LEAD**: IT leadership
- **OPERATIONS_LEAD**: Operations leadership
- **FINANCE_LEAD**: Finance leadership
- **HR_LEAD**: Human resources leadership
- **REVENUE_LEAD**: Revenue leadership
- **MARKETING_LEAD**: Marketing leadership
- **LEGAL_LEAD**: Legal leadership
- **CUSTOMER_LEAD**: Customer leadership
- **ENGINEERING**: Engineering team
- **ARCHITECTURE**: Architecture team
- **OPERATIONS**: Operations team
- **QUALITY**: Quality assurance team
- **RESEARCH**: Research team
- **PRODUCT_MANAGEMENT**: Product management
- **PRODUCT_OPERATIONS**: Product operations
- **DESIGN**: Design team
- **DOCUMENTATION**: Documentation team
- **DATA_ENGINEERING**: Data engineering
- **ANALYTICS**: Analytics team
- **ML_AI**: Machine learning/AI team
- **APPLICATION_SECURITY**: Application security
- **SECURITY_OPERATIONS**: Security operations
- **GOVERNANCE**: Governance team
- **COMPLIANCE**: Compliance team
- **IT_SUPPORT**: IT support
- **IDENTITY_MANAGEMENT**: Identity management
- **NETWORK_ADMIN**: Network administration
- **ENDPOINT_ADMIN**: Endpoint administration
- **PROGRAM_MANAGEMENT**: Program management
- **PROCUREMENT**: Procurement team
- **FACILITIES_MANAGEMENT**: Facilities management
- **LOGISTICS**: Logistics team
- **ACCOUNTING**: Accounting team
- **FINANCIAL_PLANNING**: Financial planning
- **TREASURY**: Treasury team
- **PAYROLL**: Payroll team
- **TALENT_ACQUISITION**: Talent acquisition
- **PEOPLE_OPERATIONS**: People operations
- **LEARNING_DEVELOPMENT**: Learning & development
- **COMPENSATION**: Compensation team
- **SALES**: Sales team
- **SALES_OPERATIONS**: Sales operations
- **PARTNERSHIP_MANAGEMENT**: Partnership management
- **CUSTOMER_SUCCESS**: Customer success
- **BRAND_MANAGEMENT**: Brand management
- **PERFORMANCE_MARKETING**: Performance marketing
- **CONTENT_MARKETING**: Content marketing
- **PUBLIC_RELATIONS**: Public relations
- **EVENTS_MANAGEMENT**: Events management
- **CONTRACT_MANAGEMENT**: Contract management
- **PRIVACY_MANAGEMENT**: Privacy management
- **INTELLECTUAL_PROPERTY**: Intellectual property
- **REGULATORY_AFFAIRS**: Regulatory affairs
- **CUSTOMER_SUPPORT**: Customer support
- **CUSTOMER_TRAINING**: Customer training
- **COMMUNITY_MANAGEMENT**: Community management
- **USER**: General user access
- **BUSINESS**: Business user access
- **AGENCY**: Agency user access
- **DEVELOPER**: Developer access
- **ADMIN**: Admin access

### Permissions
Each role has specific permissions based on their access level and responsibilities. See configuration files for detailed permission mappings.

## 📊 Error Handling

### HTTP Status Codes
- **200**: Success
- **400**: Bad Request
- **404**: Not Found
- **500**: Internal Server Error

### Error Response Format
```json
{
  "success": false,
  "error": "Error message description"
}
```

## 🚀 Examples

### Complete System Check
```bash
# Check health
curl http://localhost:8082/health

# Check board status
curl http://localhost:8082/board

# Get organization structure
curl http://localhost:8082/organization

# Get all panels
curl http://localhost:8082/panels

# Get bits framework
curl http://localhost:8082/bits

# Get cbT economy
curl http://localhost:8082/cbt
```

### PowerShell Examples
```powershell
# Health check
Invoke-WebRequest -Uri "http://localhost:8082/health" -UseBasicParsing

# Board status
Invoke-WebRequest -Uri "http://localhost:8082/board" -UseBasicParsing

# Execute command
$body = @{command="status"} | ConvertTo-Json
Invoke-WebRequest -Uri "http://localhost:8082/board/command" -Method POST -Body $body -ContentType "application/json"

# Transfer cbT
$body = @{from="c-bit"; to="u-bit"; amount=1000} | ConvertTo-Json
Invoke-WebRequest -Uri "http://localhost:8082/cbt/transfer" -Method POST -Body $body -ContentType "application/json"
```

### JavaScript Examples
```javascript
// Health check
fetch('http://localhost:8082/health')
  .then(response => response.json())
  .then(data => console.log(data));

// Board command
fetch('http://localhost:8082/board/command', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({command: 'status'})
})
.then(response => response.json())
.then(data => console.log(data));

// Socket.IO connection
const socket = io('http://localhost:8082');
socket.on('connect', () => {
  console.log('Connected to AI Board');
});
socket.emit('board_command', {command: 'status'});
socket.on('board_response', (data) => {
  console.log('Board response:', data);
});
```

## 📝 Notes

- All timestamps are in ISO 8601 format
- All monetary values (cbT) are integers
- The system runs in OFFLINE mode (no internet required)
- Socket.IO provides real-time communication
- Configuration can be in JSON or YAML format
- Administration script provides comprehensive management capabilities

## 🆘 Support

**CEO**: Andrei - andrei@coolbits.ro  
**Managed by**: oCursor (Local Development)  
**Documentation**: Generated automatically from system configuration  
**Version**: 1.0.0  
**Last Updated**: 2025-01-07T16:32:43Z
