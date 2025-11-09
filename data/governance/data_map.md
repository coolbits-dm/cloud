# CoolBits.ai Data Map
# ====================

| Dataset | Owner | Classification | Retention Days | Backup Scope | Restore Priority | Description |
|---------|-------|----------------|----------------|--------------|------------------|-------------|
| logs/application | ogpt | internal | 30 | config-only | P2 | Application logs |
| logs/security | ogpt | confidential | 90 | full | P0 | Security and audit logs |
| logs/debug | ogpt | internal | 7 | config-only | P3 | Debug and trace logs |
| data/rag_index | ogpt | confidential | 365 | full | P0 | RAG vector database |
| data/user_sessions | ogpt | confidential | 90 | full | P1 | User session data |
| data/transcripts | ogpt | confidential | 180 | full | P1 | Chat transcripts |
| config/secrets_refs | ogpt | confidential | 365 | full | P0 | Secret references |
| config/app_settings | ogpt | internal | 90 | config-only | P1 | Application configuration |
| artifacts/sbom | ogpt | internal | 90 | config-only | P2 | Software bill of materials |
| artifacts/releases | ogpt | internal | 365 | config-only | P2 | Release artifacts |
| data/roadmap | ogpt | internal | 365 | config-only | P2 | Project roadmap |
| data/backup_metadata | ogpt | internal | 365 | config-only | P1 | Backup metadata |
| logs/billing | ogpt | confidential | 90 | full | P0 | Billing and cost data |
| logs/monitoring | ogpt | internal | 30 | config-only | P2 | Monitoring metrics |
| data/feature_flags | ogpt | internal | 90 | config-only | P1 | Feature flag states |
| data/runtime_config | ogpt | internal | 30 | config-only | P1 | Runtime configuration |

## Classification Definitions

### Public
- Data that can be freely shared
- No restrictions on access
- Examples: public documentation, open source code

### Internal
- Data for internal use only
- Access restricted to CoolBits.ai team
- Examples: internal documentation, application logs

### Confidential
- Sensitive data requiring protection
- Access restricted to authorized personnel
- Examples: user data, secrets, PII

## Backup Scope Definitions

### Full
- Complete data backup including all content
- Required for: user data, secrets, critical configurations
- Frequency: Daily

### Config-only
- Configuration and metadata only
- Required for: logs, settings, non-sensitive data
- Frequency: Weekly

## Restore Priority Definitions

### P0 (Critical)
- Must be restored within 1 hour
- Business critical data
- Examples: secrets, user data, security logs

### P1 (High)
- Must be restored within 4 hours
- Important business data
- Examples: configurations, user sessions

### P2 (Medium)
- Must be restored within 24 hours
- Operational data
- Examples: application logs, monitoring data

### P3 (Low)
- Must be restored within 72 hours
- Non-critical data
- Examples: debug logs, temporary data
