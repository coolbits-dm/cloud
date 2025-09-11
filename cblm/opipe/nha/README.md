# CoolBits.ai NHA Registry

**Non-Human Agents (NHA) Registry** - Single source of truth for all agents in the CoolBits ecosystem.

## 📋 Overview

This registry provides a canonical, validated, and synchronized system for managing all Non-Human Agents that participate in or have participated in the CoolBits project. It includes @oPyGPT03, @oRunner, providers, internal utilities, and all operational agents.

## 🏗️ Structure

```
cblm/opipe/nha/
├── registry.py           # Core loader + dataclasses + validation
├── schema.yaml           # JSONSchema for YAML validation
├── agents.yaml           # Canonical list of all NHAs (50+ agents)
├── generate.py           # Generates out/*.json, *.md artifacts
├── sync_gcp.py           # Syncs IAM (SA, roles) with Google Cloud
├── validate.py           # Validates schema + business rules
├── policies/
│   ├── iam_minimum.yaml  # Minimum roles per category
│   └── scopes_matrix.yaml # Capability scopes to IAM mapping
├── out/
│   ├── registry.json     # Generated JSON artifact
│   ├── registry.md       # Generated Markdown report
│   ├── by-category.md    # Category breakdown with tables
│   └── sync_report.json  # GCP sync report
└── README.md             # This file
```

## 🚀 Quick Commands

### Generate Artifacts
```bash
# Generate all artifacts (JSON, Markdown, category breakdown)
python cblm/opipe/nha/generate.py
```

### Validate Registry
```bash
# Validate YAML + IAM + scopes + business rules
python cblm/opipe/nha/validate.py
```

### Sync with Google Cloud
```bash
# Dry run (no changes)
python cblm/opipe/nha/sync_gcp.py --dry-run

# Apply changes to Google Cloud
python cblm/opipe/nha/sync_gcp.py --apply

# Validate IAM policies only
python cblm/opipe/nha/sync_gcp.py --validate-only
```

## 📊 Registry Statistics

- **Total Agents**: 50
- **Active Agents**: 47
- **Deprecated Agents**: 3
- **Categories**: 10

### Category Breakdown
- **Personal**: 3 agents (coordination, ownership)
- **Business Channels**: 3 agents (admin panels, status)
- **Business Tools**: 5 agents (export, RAG, registry API)
- **Development Tools**: 8 agents (CI/CD, testing, automation)
- **Infrastructure**: 8 agents (Cloud Run services, monitoring)
- **Security**: 6 agents (RBAC, scanning, breach response)
- **MLOps**: 8 agents (AI providers, workers)
- **Operations**: 6 agents (chaos engineering, DR, monitoring)
- **SEO Tools**: 2 agents (legacy, deprecated)
- **Agency**: 1 agent (legacy, deprecated)

## 🔐 Security & Permissions

### IAM Categories
Each NHA category has defined minimum permissions:

- **Personal**: `storage.objectViewer`, `logging.logWriter`, `run.invoker`, `roles/owner`
- **Business Channels**: `storage.objectViewer`, `logging.logWriter`, `run.invoker`, `run.admin`, `storage.objectAdmin`, `monitoring.viewer`
- **Business Tools**: `storage.objectViewer`, `logging.logWriter`, `run.invoker`, `monitoring.viewer`, `storage.objectCreator`
- **Development Tools**: `storage.objectViewer`, `logging.logWriter`, `run.invoker`, `cloudbuild.builds.create`, `source.repos.read`, `storage.objectCreator`
- **Infrastructure**: `run.invoker`, `logging.logWriter`, `storage.objectViewer`, `storage.objectCreator`, `monitoring.viewer`, `monitoring.writer`, `bigquery.dataViewer`, `bigquery.jobUser`, `kms.cryptoKeyDecrypter`, `aiplatform.user`
- **Security**: `run.invoker`, `logging.logWriter`, `secretmanager.secretAccessor`, `secretmanager.secretVersionManager`
- **MLOps**: `run.invoker`, `storage.objectViewer`, `aiplatform.user`, `aiplatform.deploymentManager`
- **Operations**: `run.invoker`, `logging.logWriter`, `storage.objectViewer`, `monitoring.viewer`, `monitoring.writer`, `billing.accounts.getSpendingInformation`

### Secret Management
All secrets follow the pattern: `nha/{agent-id}/{secret-type}`
- Example: `nha/opypgpt03/hmac`, `nha/ogpt/openai_key`

## 📝 NHA Model

Each NHA has the following structure:

```yaml
- id: "nha:agent-id"           # Unique identifier
  name: "@Agent-Name"           # Display name
  category: "category_name"     # One of: personal, biz_channels, biz_tools, seo_tools, agency, dev_tools, infra, security, mlops, ops
  owner: "owner_name"           # Owner (andrei, platform)
  status: "active"             # active, paused, deprecated
  channels:                    # Communication channels
    - kind: "http"             # http, ws, cli, sdk, ui
      endpoint: "https://..."  # URL, command, or package
      auth: "hmac"             # none, hmac, jwt, oauth, sa_key, kms
  capabilities:                # What the agent can do
    - name: "capability_name"
      description: "Description"
      scopes: ["read:data", "write:logs"]
  permissions: ["run.invoker"] # IAM roles
  secrets: ["nha/agent/hmac"]  # Secret references
  tags: ["env:prod", "service:api"] # Metadata tags
  slo:                         # Service Level Objectives
    latency_p95_ms: 200
    error_rate_max: 0.01
    availability_pct: 99.9
  notes: "Additional notes"
```

## 🔍 Validation Rules

### Schema Validation
- IDs must match pattern: `^nha:[a-z0-9\\-]+$`
- Names must be unique
- Categories must be from predefined list
- Channels must have valid kind and endpoint
- Permissions must have valid format
- Secrets must follow `nha/{id}/{type}` pattern
- Tags must follow `key:value` pattern

### Business Rules
- All NHAs must have at least one channel
- All NHAs must have an owner
- Required tags: `env`, `service`
- No duplicate IDs or names
- Permissions must be authorized for category

### IAM Policy Validation
- Permissions must be in allowed list for category
- No unauthorized roles (e.g., `roles/Editor` without explicit need)
- Secret references must be properly formatted

## 🔄 CI/CD Integration

### Pre-commit Hooks
```bash
# Validate registry before commit
python cblm/opipe/nha/validate.py
```

### GitHub Actions
```yaml
- name: Validate NHA Registry
  run: python cblm/opipe/nha/validate.py

- name: Sync GCP (Dry Run)
  run: python cblm/opipe/nha/sync_gcp.py --dry-run
```

### PR Gates
- Registry validation must pass
- IAM policy validation must pass
- No unauthorized permissions
- All required tags present

## 📡 API Integration

The generated `out/registry.json` is served by the existing API:

```bash
# Get all agents
GET /api/agents

# Response format
{
  "version": "1.0.0",
  "count": 50,
  "nhas": [...]
}
```

## 🎯 Definition of Done

✅ **Registry Complete**
- [x] `agents.yaml` includes all current/historical agents (50+)
- [x] No duplicate IDs or names
- [x] All agents have required tags (`env`, `service`)
- [x] All agents have at least one channel

✅ **Validation Complete**
- [x] `validate.py` passes all checks
- [x] `sync_gcp.py --dry-run` reports no conflicts
- [x] IAM policies consistent with minimum requirements
- [x] No unauthorized permissions

✅ **Artifacts Generated**
- [x] `out/registry.json` served by `/api/agents`
- [x] `out/registry.md` comprehensive report
- [x] `out/by-category.md` category breakdown
- [x] All artifacts signed and audited

✅ **GCP Integration**
- [x] Service accounts created for all active NHAs
- [x] IAM permissions applied according to policies
- [x] No service accounts with `roles/Editor`
- [x] Sync report generated

## 🚨 Anti-Regression

CI blocks PRs that:
- Add agent without owner, category, or channels
- Add secret without Secret Manager mapping
- Add permission outside `iam_minimum.yaml`
- Remove required tags or validation

## 📚 Examples

### Adding a New NHA
1. Add entry to `agents.yaml`
2. Run `python validate.py` to check
3. Run `python generate.py` to update artifacts
4. Run `python sync_gcp.py --dry-run` to verify IAM

### Updating Permissions
1. Update `agents.yaml` permissions
2. Update `policies/iam_minimum.yaml` if needed
3. Run validation to ensure compliance
4. Apply changes with `sync_gcp.py --apply`

### Deprecating an Agent
1. Change `status: "deprecated"` in `agents.yaml`
2. Add note explaining deprecation reason
3. Keep agent in registry for audit trail
4. Remove from active sync (deprecated agents skipped)

## 🔧 Troubleshooting

### Validation Failures
```bash
# Check specific validation
python cblm/opipe/nha/validate.py

# Common issues:
# - Missing required tags (env, service)
# - Invalid permission format
# - Duplicate IDs/names
# - Unauthorized permissions for category
```

### GCP Sync Issues
```bash
# Check IAM policies
python cblm/opipe/nha/sync_gcp.py --validate-only

# Dry run to see what would change
python cblm/opipe/nha/sync_gcp.py --dry-run

# Check sync report
cat cblm/opipe/nha/out/sync_report.json
```

### Artifact Generation
```bash
# Regenerate all artifacts
python cblm/opipe/nha/generate.py

# Check output files
ls -la cblm/opipe/nha/out/
```

## 📞 Support

For issues with the NHA Registry:
1. Check validation output first
2. Review IAM policies in `policies/`
3. Check sync report for GCP issues
4. Ensure all required tags are present

---

**Registry Version**: 1.0.0  
**Last Updated**: 2025-09-11  
**Total Agents**: 50  
**Status**: ✅ Production Ready
