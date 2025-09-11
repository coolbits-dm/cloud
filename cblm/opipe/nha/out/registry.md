# CoolBits.ai NHA Registry

**Version**: 1.0.0  
**Total Agents**: 50  
**Generated**: 1757568579.0529418

## Summary by Category

### Personal
**Count**: 3

- **@Andrei** (`nha:andrei`)
  - Owner: andrei
  - Status: active
  - Channels: 1
  - Capabilities: 1
  - Permissions: roles/owner
  - Tags: env:prod, service:owner, role:admin
  - Notes: Project owner and primary coordinator

- **@oPyGPT03** (`nha:opypgpt03`)
  - Owner: platform
  - Status: active
  - Channels: 1
  - Capabilities: 1
  - Permissions: run.invoker, storage.objectViewer, logging.logWriter
  - Tags: env:prod, service:coordinator, provider:openai
  - Notes: Technical coordination and architecture decisions

- **@oRunner** (`nha:orunner`)
  - Owner: platform
  - Status: active
  - Channels: 1
  - Capabilities: 1
  - Permissions: run.invoker, logging.logWriter
  - Tags: env:prod, service:runner, role:executor
  - Notes: Local execution and automation runner

### Dev Tools
**Count**: 8

- **@oCursor** (`nha:ocursor`)
  - Owner: platform
  - Status: active
  - Channels: 1
  - Capabilities: 1
  - Permissions: storage.objectViewer
  - Tags: env:prod, service:ide, provider:cursor
  - Notes: Cursor IDE automation agent

- **@oCIM-Bridge** (`nha:ocim-bridge`)
  - Owner: platform
  - Status: active
  - Channels: 1
  - Capabilities: 1
  - Permissions: run.invoker, logging.logWriter
  - Tags: env:prod, service:bridge, protocol:ocim
  - Notes: OCIM protocol bridge for agent communication

- **@CI-Runner** (`nha:ci-runner`)
  - Owner: platform
  - Status: active
  - Channels: 1
  - Capabilities: 1
  - Permissions: run.invoker, storage.objectViewer, logging.logWriter
  - Tags: env:prod, service:ci, provider:github
  - Notes: GitHub Actions CI/CD runner

- **@Playwright-E2E** (`nha:playwright-e2e`)
  - Owner: platform
  - Status: active
  - Channels: 1
  - Capabilities: 1
  - Permissions: run.invoker, storage.objectViewer
  - Tags: env:prod, service:testing, framework:playwright
  - Notes: Playwright E2E testing

- **@Unit-Tests** (`nha:unit-tests`)
  - Owner: platform
  - Status: active
  - Channels: 1
  - Capabilities: 1
  - Permissions: run.invoker
  - Tags: env:prod, service:testing, framework:pytest
  - Notes: Unit test runner

- **@Release-Bot** (`nha:release-bot`)
  - Owner: platform
  - Status: active
  - Channels: 1
  - Capabilities: 1
  - Permissions: run.invoker, storage.objectViewer
  - Tags: env:prod, service:release, provider:github
  - Notes: Automated release bot

- **@Doctor** (`nha:doctor`)
  - Owner: platform
  - Status: active
  - Channels: 1
  - Capabilities: 1
  - Permissions: run.invoker, logging.logWriter
  - Tags: env:prod, service:diagnostics, platform:windows
  - Notes: System health diagnostics

- **@Roadmap-Bot** (`nha:roadmap-bot`)
  - Owner: platform
  - Status: active
  - Channels: 1
  - Capabilities: 1
  - Permissions: storage.objectViewer, storage.objectCreator
  - Tags: env:prod, service:roadmap, tool:planning
  - Notes: Project roadmap management

### Biz Channels
**Count**: 3

- **@Panel-Admin** (`nha:panel-admin`)
  - Owner: platform
  - Status: active
  - Channels: 1
  - Capabilities: 1
  - Permissions: run.admin, storage.objectAdmin
  - Tags: env:prod, service:admin, ui:web
  - Notes: Web administration console

- **@Panel-Status** (`nha:panel-status`)
  - Owner: platform
  - Status: active
  - Channels: 1
  - Capabilities: 1
  - Permissions: monitoring.viewer
  - Tags: env:prod, service:status, ui:public
  - Notes: Public status dashboard

- **@Panel-Update** (`nha:panel-update`)
  - Owner: platform
  - Status: active
  - Channels: 1
  - Capabilities: 1
  - Permissions: storage.objectViewer
  - Tags: env:prod, service:updater, ui:tauri
  - Notes: Application updater for Tauri apps

### Biz Tools
**Count**: 5

- **@Export-Pack** (`nha:export-pack`)
  - Owner: platform
  - Status: active
  - Channels: 1
  - Capabilities: 1
  - Permissions: storage.objectViewer, storage.objectCreator
  - Tags: env:prod, service:export, format:multi
  - Notes: Data export service

- **@RAG-Mini** (`nha:rag-mini`)
  - Owner: platform
  - Status: active
  - Channels: 1
  - Capabilities: 1
  - Permissions: storage.objectViewer
  - Tags: env:prod, service:rag, db:faiss
  - Notes: Lightweight RAG service

- **@Agents-Registry** (`nha:agents-registry`)
  - Owner: platform
  - Status: active
  - Channels: 1
  - Capabilities: 1
  - Permissions: storage.objectViewer, logging.logWriter
  - Tags: env:prod, service:registry, api:agents
  - Notes: Agent registry API

- **@Bridge-FastAPI** (`nha:bridge-fastapi`)
  - Owner: platform
  - Status: active
  - Channels: 1
  - Capabilities: 1
  - Permissions: run.invoker, logging.logWriter
  - Tags: env:prod, service:bridge, framework:fastapi
  - Notes: FastAPI bridge service

- **@WS-Gateway** (`nha:ws-gateway`)
  - Owner: platform
  - Status: active
  - Channels: 1
  - Capabilities: 1
  - Permissions: run.invoker, logging.logWriter
  - Tags: env:prod, service:gateway, protocol:websocket
  - Notes: WebSocket chat gateway

### Infra
**Count**: 8

- **@CoolBits-Frontend** (`nha:coolbits-frontend`)
  - Owner: platform
  - Status: active
  - Channels: 1
  - Capabilities: 1
  - Permissions: run.invoker, logging.logWriter
  - Tags: env:prod, service:frontend, platform:cloudrun
  - Notes: Main web frontend on Cloud Run

- **@CoolBits-Bridge** (`nha:coolbits-bridge`)
  - Owner: platform
  - Status: active
  - Channels: 1
  - Capabilities: 1
  - Permissions: run.invoker, logging.logWriter
  - Tags: env:prod, service:bridge, platform:cloudrun
  - Notes: API bridge service on Cloud Run

- **@CoolBits-RAG** (`nha:coolbits-rag`)
  - Owner: platform
  - Status: active
  - Channels: 1
  - Capabilities: 1
  - Permissions: run.invoker, storage.objectViewer, aiplatform.user
  - Tags: env:prod, service:rag, platform:cloudrun
  - Notes: RAG service on Cloud Run

- **@CoolBits-Monitor** (`nha:coolbits-monitor`)
  - Owner: platform
  - Status: active
  - Channels: 1
  - Capabilities: 1
  - Permissions: monitoring.viewer, monitoring.writer
  - Tags: env:prod, service:monitoring, platform:cloudrun
  - Notes: Monitoring service on Cloud Run

- **@CoolBits-BQ** (`nha:coolbits-bq`)
  - Owner: platform
  - Status: active
  - Channels: 1
  - Capabilities: 1
  - Permissions: bigquery.dataViewer, bigquery.jobUser
  - Tags: env:prod, service:bigquery, platform:gcp
  - Notes: BigQuery export service

- **@Cosign-Enforcer** (`nha:cosign-enforcer`)
  - Owner: platform
  - Status: active
  - Channels: 1
  - Capabilities: 1
  - Permissions: storage.objectViewer, kms.cryptoKeyDecrypter
  - Tags: env:prod, service:security, tool:cosign
  - Notes: Container image signing enforcement

- **@Backup-Worker** (`nha:backup-worker`)
  - Owner: platform
  - Status: active
  - Channels: 1
  - Capabilities: 1
  - Permissions: storage.objectViewer, storage.objectCreator
  - Tags: env:prod, service:backup, platform:gcp
  - Notes: Automated backup worker

- **@Restore-Worker** (`nha:restore-worker`)
  - Owner: platform
  - Status: active
  - Channels: 1
  - Capabilities: 1
  - Permissions: storage.objectViewer, storage.objectCreator
  - Tags: env:prod, service:restore, platform:gcp
  - Notes: Automated restore worker

### Security
**Count**: 6

- **@RBAC-HMAC-Gateway** (`nha:rbac-hmac-gateway`)
  - Owner: platform
  - Status: active
  - Channels: 1
  - Capabilities: 1
  - Permissions: run.invoker, logging.logWriter
  - Tags: env:prod, service:auth, security:rbac
  - Notes: RBAC enforcement gateway

- **@Secret-Manager-Sync** (`nha:secret-manager-sync`)
  - Owner: platform
  - Status: active
  - Channels: 1
  - Capabilities: 1
  - Permissions: secretmanager.secretAccessor, secretmanager.secretVersionManager
  - Tags: env:prod, service:secrets, platform:gcp
  - Notes: Secret Manager synchronization

- **@Gitleaks-Scan** (`nha:gitleaks-scan`)
  - Owner: platform
  - Status: active
  - Channels: 1
  - Capabilities: 1
  - Permissions: run.invoker
  - Tags: env:prod, service:security, tool:gitleaks
  - Notes: Git secret scanning

- **@CVE-Scan** (`nha:cve-scan`)
  - Owner: platform
  - Status: active
  - Channels: 1
  - Capabilities: 1
  - Permissions: run.invoker
  - Tags: env:prod, service:security, tool:trivy
  - Notes: CVE vulnerability scanning

- **@OPA-Conftest** (`nha:opa-conftest`)
  - Owner: platform
  - Status: active
  - Channels: 1
  - Capabilities: 1
  - Permissions: run.invoker
  - Tags: env:prod, service:security, tool:opa
  - Notes: OPA policy enforcement

- **@Breach-Runbook-Bot** (`nha:breach-runbook-bot`)
  - Owner: platform
  - Status: active
  - Channels: 1
  - Capabilities: 1
  - Permissions: run.invoker, logging.logWriter
  - Tags: env:prod, service:security, tool:runbook
  - Notes: Automated breach response bot

### Mlops
**Count**: 8

- **@OGPT** (`nha:ogpt`)
  - Owner: platform
  - Status: active
  - Channels: 1
  - Capabilities: 1
  - Permissions: run.invoker
  - Tags: env:prod, service:mlops, provider:openai
  - Notes: OpenAI provider integration

- **@OGrok** (`nha:ogrok`)
  - Owner: platform
  - Status: active
  - Channels: 1
  - Capabilities: 1
  - Permissions: run.invoker
  - Tags: env:prod, service:mlops, provider:xai
  - Notes: xAI Grok provider integration

- **@OGemini** (`nha:ogemini`)
  - Owner: platform
  - Status: active
  - Channels: 1
  - Capabilities: 1
  - Permissions: run.invoker
  - Tags: env:prod, service:mlops, provider:google
  - Notes: Google Gemini provider integration

- **@OCopilot** (`nha:ocopilot`)
  - Owner: platform
  - Status: active
  - Channels: 1
  - Capabilities: 1
  - Permissions: run.invoker
  - Tags: env:prod, service:mlops, provider:microsoft
  - Notes: Microsoft Copilot provider integration

- **@Vertex** (`nha:vertex`)
  - Owner: platform
  - Status: active
  - Channels: 1
  - Capabilities: 1
  - Permissions: aiplatform.user, aiplatform.deploymentManager
  - Tags: env:prod, service:mlops, platform:gcp
  - Notes: Vertex AI gateway service

- **@Embedding-Worker** (`nha:embedding-worker`)
  - Owner: platform
  - Status: active
  - Channels: 1
  - Capabilities: 1
  - Permissions: run.invoker, aiplatform.user
  - Tags: env:prod, service:mlops, worker:embedding
  - Notes: Embedding generation worker

- **@RAG-Ingest-Worker** (`nha:rag-ingest-worker`)
  - Owner: platform
  - Status: active
  - Channels: 1
  - Capabilities: 1
  - Permissions: run.invoker, storage.objectViewer, aiplatform.user
  - Tags: env:prod, service:mlops, worker:ingest
  - Notes: RAG document ingestion worker

- **@RAG-Search-Worker** (`nha:rag-search-worker`)
  - Owner: platform
  - Status: active
  - Channels: 1
  - Capabilities: 1
  - Permissions: run.invoker, storage.objectViewer, aiplatform.user
  - Tags: env:prod, service:mlops, worker:search
  - Notes: RAG vector search worker

### Ops
**Count**: 6

- **@Chaos-Runner** (`nha:chaos-runner`)
  - Owner: platform
  - Status: active
  - Channels: 1
  - Capabilities: 1
  - Permissions: run.invoker, logging.logWriter
  - Tags: env:prod, service:chaos, tool:engineering
  - Notes: Chaos engineering runner

- **@Chaos-Orchestrator** (`nha:chaos-orchestrator`)
  - Owner: platform
  - Status: active
  - Channels: 1
  - Capabilities: 1
  - Permissions: run.invoker, logging.logWriter
  - Tags: env:prod, service:chaos, tool:orchestration
  - Notes: Chaos experiment orchestrator

- **@Drill-Runner** (`nha:drill-runner`)
  - Owner: platform
  - Status: active
  - Channels: 1
  - Capabilities: 1
  - Permissions: run.invoker, storage.objectViewer, logging.logWriter
  - Tags: env:prod, service:dr, tool:drills
  - Notes: Disaster recovery drill runner

- **@Uptime-Monitor** (`nha:uptime-monitor`)
  - Owner: platform
  - Status: active
  - Channels: 1
  - Capabilities: 1
  - Permissions: monitoring.viewer, monitoring.writer
  - Tags: env:prod, service:monitoring, tool:uptime
  - Notes: Service uptime monitoring

- **@SLO-Gate** (`nha:slo-gate`)
  - Owner: platform
  - Status: active
  - Channels: 1
  - Capabilities: 1
  - Permissions: monitoring.viewer, run.invoker
  - Tags: env:prod, service:slo, tool:gating
  - Notes: SLO enforcement gateway

- **@Budget-Guard** (`nha:budget-guard`)
  - Owner: platform
  - Status: active
  - Channels: 1
  - Capabilities: 1
  - Permissions: billing.accounts.getSpendingInformation
  - Tags: env:prod, service:billing, tool:cost
  - Notes: Cost monitoring and budget guard

### Seo Tools
**Count**: 2

- **@SEO-Audit** (`nha:seo-audit`)
  - Owner: platform
  - Status: deprecated
  - Channels: 1
  - Capabilities: 1
  - Permissions: storage.objectViewer
  - Tags: env:deprecated, service:seo, status:legacy
  - Notes: Legacy SEO audit service - deprecated

- **@SEO-Keywords** (`nha:seo-keywords`)
  - Owner: platform
  - Status: deprecated
  - Channels: 1
  - Capabilities: 1
  - Permissions: storage.objectViewer
  - Tags: env:deprecated, service:seo, status:legacy
  - Notes: Legacy keyword research service - deprecated

### Agency
**Count**: 1

- **@Agency-MCC-Sync** (`nha:agency-mcc-sync`)
  - Owner: platform
  - Status: deprecated
  - Channels: 1
  - Capabilities: 1
  - Permissions: storage.objectViewer
  - Tags: env:deprecated, service:agency, status:legacy
  - Notes: Legacy agency MCC sync service - deprecated

