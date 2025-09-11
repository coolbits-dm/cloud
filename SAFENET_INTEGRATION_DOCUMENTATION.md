# SafeNet Authentication Client Integration - COOL BITS S.R.L.

## Overview

This document provides comprehensive documentation for the SafeNet Authentication Client integration implemented for COOL BITS S.R.L. (CUI: 42331573, Registration: ROONRC.J22/676/2020).

## Company Information

- **Company Name**: COOL BITS S.R.L.
- **CUI**: 42331573
- **Registration**: ROONRC.J22/676/2020
- **Address**: str. Columnei, nr.14, bl.K4, et.4, ap.19, Iași, România
- **Bank**: ING Office Iași Anastasie Panu
- **IBAN**: RO76INGB0000999910114315

## Architecture Components

### 1. SafeNet Integration Architecture (`safenet_integration_architecture.py`)

The core integration module that provides:

- **SafeNetIntegrationManager**: Main class for managing SafeNet operations
- **SafeNetCertificate**: Certificate management and configuration
- **SafeNetSigningRequest/Result**: Digital signing request and result handling
- **Certificate Types**: Company signing, API authentication, document signing, code signing, SSL/TLS, email signing
- **Security Levels**: L1 (Basic) to L5 (Maximum) security classifications

#### Key Features:
- Certificate generation and management
- Document digital signing
- Signature verification
- Compliance reporting
- Audit trail management

### 2. SafeNet API Integration Layer (`safenet_api_integration.py`)

REST API endpoints for SafeNet operations:

#### API Endpoints:
- `GET /api/safenet/status` - Get SafeNet integration status
- `GET /api/safenet/certificates` - List all certificates
- `POST /api/safenet/certificates` - Create new certificate
- `GET /api/safenet/certificates/<id>/status` - Get certificate status
- `POST /api/safenet/sign` - Sign document
- `POST /api/safenet/verify` - Verify signature
- `GET /api/safenet/signing-history` - Get signing history
- `GET /api/safenet/compliance-report` - Generate compliance report
- `GET /api/safenet/audit-trail` - Get audit trail
- `POST /api/safenet/install` - Install SafeNet client

#### API Server Configuration:
- **Host**: 0.0.0.0
- **Port**: 5001
- **Protocol**: HTTP/HTTPS
- **CORS**: Enabled for cross-origin requests

### 3. SafeNet Security Policies (`safenet_security_policies.py`)

Comprehensive security policy management:

#### Security Policies:
- **CB-CERT-001**: Certificate Management Policy
- **CB-SIGN-001**: Digital Signing Policy
- **CB-AUDIT-001**: Audit Trail Policy
- **CB-ACCESS-001**: Access Control Policy

#### Policy Levels:
- **Basic**: Internal documents
- **Standard**: Business documents
- **High**: Legal documents
- **Critical**: Financial documents
- **Maximum**: Executive documents

#### Compliance Features:
- Policy validation
- Audit event logging
- Compliance reporting
- Violation tracking

### 4. SafeNet Testing Suite (`safenet_testing_suite.py`)

Comprehensive testing framework:

#### Test Categories:
- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end workflow testing
- **Performance Tests**: Load and performance testing
- **API Tests**: REST API endpoint testing

#### Test Coverage:
- Certificate lifecycle management
- Document signing workflows
- Signature verification
- Policy validation
- Compliance reporting

### 5. SafeNet Deployment Manager (`safenet_deployment_manager.py`)

Automated deployment and configuration:

#### Deployment Features:
- Prerequisites checking
- Directory structure creation
- Dependency installation
- Configuration file generation
- Service script creation
- Testing execution
- Deployment reporting

## Installation and Setup

### Prerequisites

1. **Python 3.8+** installed
2. **THALES SafeNet Authentication Client** (to be installed separately)
3. **Write permissions** to workspace directory
4. **Company configuration file** (`coolbits_srl_complete_details.json`)

### Required Python Modules

```bash
pip install flask>=2.0.0
pip install flask-cors>=3.0.0
pip install requests>=2.25.0
```

### Installation Steps

1. **Run Deployment Manager**:
   ```bash
   python safenet_deployment_manager.py
   ```

2. **Install THALES SafeNet Client**:
   - Download from THALES official website
   - Install according to THALES documentation
   - Configure for COOL BITS S.R.L.

3. **Start API Server**:
   ```bash
   # Windows
   start_safenet_api.bat
   
   # Linux/Mac
   ./start_safenet_api.sh
   ```

4. **Verify Installation**:
   ```bash
   python safenet_testing_suite.py
   ```

## Usage Examples

### 1. Generate Company Certificate

```python
from safenet_integration_architecture import SafeNetIntegrationManager, SafeNetCertificateType, SafeNetSecurityLevel

# Initialize manager
manager = SafeNetIntegrationManager(company_config)

# Generate certificate
certificate = manager.generate_company_certificate(
    SafeNetCertificateType.COMPANY_SIGNING,
    SafeNetSecurityLevel.LEVEL_3
)
```

### 2. Sign Document

```python
# Sign document
result = manager.sign_document(
    document_path="contract.pdf",
    certificate_id=certificate.certificate_id,
    signing_purpose="Contract Signing",
    security_level=SafeNetSecurityLevel.LEVEL_4
)
```

### 3. Verify Signature

```python
# Verify signature
is_valid = manager.verify_signature(
    document_path="contract.pdf",
    signature=result.signature,
    certificate_id=certificate.certificate_id
)
```

### 4. API Usage

```bash
# Get status
curl http://localhost:5001/api/safenet/status

# Create certificate
curl -X POST http://localhost:5001/api/safenet/certificates \
  -H "Content-Type: application/json" \
  -d '{"certificate_type": "company_signing", "security_level": "L3"}'

# Sign document
curl -X POST http://localhost:5001/api/safenet/sign \
  -F "document=@contract.pdf" \
  -F "certificate_id=cb-company_signing-1234567890" \
  -F "signing_purpose=Contract Signing" \
  -F "security_level=L4"
```

## Security Features

### 1. Multi-Level Security

- **L1 (Basic)**: Internal documents
- **L2 (Standard)**: Business documents
- **L3 (High)**: Legal documents
- **L4 (Critical)**: Financial documents
- **L5 (Maximum)**: Executive documents

### 2. Certificate Management

- Secure certificate storage
- Password strength requirements (minimum 12 characters)
- Automatic renewal alerts (30 days before expiry)
- Certificate revocation capabilities

### 3. Digital Signing

- Dual authentication required
- Timestamped signatures
- Document integrity verification
- Signature validation

### 4. Audit and Compliance

- Comprehensive audit trails
- 7-year log retention
- Tamper-proof logging
- Compliance reporting
- Policy violation tracking

## Configuration

### Environment Variables

```bash
# Company Information
COMPANY_NAME=COOL BITS S.R.L.
COMPANY_CUI=42331573
COMPANY_REGISTRATION=ROONRC.J22/676/2020

# SafeNet Paths
SAFENET_INSTALLATION_PATH=/path/to/safenet
SAFENET_CERTIFICATES_PATH=/path/to/certificates
SAFENET_LOGS_PATH=/path/to/logs
SAFENET_BACKUP_PATH=/path/to/backup

# API Configuration
SAFENET_API_HOST=0.0.0.0
SAFENET_API_PORT=5001

# Security Settings
SAFENET_DEFAULT_SECURITY_LEVEL=L3
SAFENET_CERTIFICATE_EXPIRY_DAYS=365
SAFENET_AUDIT_RETENTION_DAYS=2555
SAFENET_PASSWORD_MIN_LENGTH=12
```

### Configuration File

The system uses `safenet_config.json` for configuration:

```json
{
  "company_info": {
    "name": "COOL BITS S.R.L.",
    "cui": "42331573",
    "registration": "ROONRC.J22/676/2020"
  },
  "safenet_settings": {
    "version": "12.0.0",
    "installation_path": "/path/to/safenet"
  },
  "api_settings": {
    "host": "0.0.0.0",
    "port": 5001,
    "ssl_enabled": true
  },
  "security_settings": {
    "default_security_level": "L3",
    "certificate_expiry_days": 365,
    "audit_retention_days": 2555
  }
}
```

## Monitoring and Maintenance

### 1. Log Files

- **Audit Log**: `safenet_audit_log.json`
- **Application Log**: `safenet.log`
- **Error Log**: `safenet_error.log`

### 2. Compliance Reporting

Generate compliance reports:

```python
# Generate compliance report
report = manager.generate_compliance_report()

# Export compliance data
manager.export_compliance_data("compliance_export.json")
```

### 3. Health Checks

Monitor system health:

```bash
# Check API status
curl http://localhost:5001/api/safenet/status

# Check certificate status
curl http://localhost:5001/api/safenet/certificates/cert-id/status

# Get compliance report
curl http://localhost:5001/api/safenet/compliance-report
```

## Troubleshooting

### Common Issues

1. **Certificate Not Found**
   - Verify certificate ID
   - Check certificate registry
   - Ensure certificate is active

2. **Signing Failed**
   - Check certificate validity
   - Verify document permissions
   - Check security policy compliance

3. **API Server Not Starting**
   - Check port availability
   - Verify Python dependencies
   - Check configuration files

4. **Policy Violations**
   - Review security policies
   - Check operation parameters
   - Verify user permissions

### Debug Mode

Enable debug mode:

```python
# Set debug level
logging.basicConfig(level=logging.DEBUG)

# Enable API debug
app.run(debug=True)
```

## Support and Contact

### Technical Support

- **Company**: COOL BITS S.R.L.
- **Email**: coolbits.dm@gmail.com
- **CEO**: andrei@coolbits.ro
- **CTO**: bogdan.boureanu@gmail.com

### Documentation

- **SafeNet Integration Guide**: This document
- **API Documentation**: Available at `/api/safenet/status`
- **Deployment Report**: `safenet_deployment_report.json`
- **Compliance Report**: Generated via API

## Legal and Compliance

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
