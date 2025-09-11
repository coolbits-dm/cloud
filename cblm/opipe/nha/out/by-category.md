# CoolBits.ai NHA Registry - By Category

**Version**: 1.0.0  
**Total Agents**: 50

## Agency

| ID | Name | Owner | Status | Channels | Permissions | Tags |
|----|------|-------|--------|----------|-------------|------|
| `nha:agency-mcc-sync` | @Agency-MCC-Sync | platform | deprecated | 1 | storage.objectViewer | env:deprecated, service:agency... |

## Biz Channels

| ID | Name | Owner | Status | Channels | Permissions | Tags |
|----|------|-------|--------|----------|-------------|------|
| `nha:panel-admin` | @Panel-Admin | platform | active | 1 | run.admin, storage.objectAdmin | env:prod, service:admin... |
| `nha:panel-status` | @Panel-Status | platform | active | 1 | monitoring.viewer | env:prod, service:status... |
| `nha:panel-update` | @Panel-Update | platform | active | 1 | storage.objectViewer | env:prod, service:updater... |

## Biz Tools

| ID | Name | Owner | Status | Channels | Permissions | Tags |
|----|------|-------|--------|----------|-------------|------|
| `nha:agents-registry` | @Agents-Registry | platform | active | 1 | storage.objectViewer, logging.logWriter | env:prod, service:registry... |
| `nha:bridge-fastapi` | @Bridge-FastAPI | platform | active | 1 | run.invoker, logging.logWriter | env:prod, service:bridge... |
| `nha:export-pack` | @Export-Pack | platform | active | 1 | storage.objectViewer, storage.objectCreator | env:prod, service:export... |
| `nha:rag-mini` | @RAG-Mini | platform | active | 1 | storage.objectViewer | env:prod, service:rag... |
| `nha:ws-gateway` | @WS-Gateway | platform | active | 1 | run.invoker, logging.logWriter | env:prod, service:gateway... |

## Dev Tools

| ID | Name | Owner | Status | Channels | Permissions | Tags |
|----|------|-------|--------|----------|-------------|------|
| `nha:ci-runner` | @CI-Runner | platform | active | 1 | run.invoker, storage.objectViewer, logging.logWriter | env:prod, service:ci... |
| `nha:doctor` | @Doctor | platform | active | 1 | run.invoker, logging.logWriter | env:prod, service:diagnostics... |
| `nha:ocim-bridge` | @oCIM-Bridge | platform | active | 1 | run.invoker, logging.logWriter | env:prod, service:bridge... |
| `nha:ocursor` | @oCursor | platform | active | 1 | storage.objectViewer | env:prod, service:ide... |
| `nha:playwright-e2e` | @Playwright-E2E | platform | active | 1 | run.invoker, storage.objectViewer | env:prod, service:testing... |
| `nha:release-bot` | @Release-Bot | platform | active | 1 | run.invoker, storage.objectViewer | env:prod, service:release... |
| `nha:roadmap-bot` | @Roadmap-Bot | platform | active | 1 | storage.objectViewer, storage.objectCreator | env:prod, service:roadmap... |
| `nha:unit-tests` | @Unit-Tests | platform | active | 1 | run.invoker | env:prod, service:testing... |

## Infra

| ID | Name | Owner | Status | Channels | Permissions | Tags |
|----|------|-------|--------|----------|-------------|------|
| `nha:backup-worker` | @Backup-Worker | platform | active | 1 | storage.objectViewer, storage.objectCreator | env:prod, service:backup... |
| `nha:coolbits-bq` | @CoolBits-BQ | platform | active | 1 | bigquery.dataViewer, bigquery.jobUser | env:prod, service:bigquery... |
| `nha:coolbits-bridge` | @CoolBits-Bridge | platform | active | 1 | run.invoker, logging.logWriter | env:prod, service:bridge... |
| `nha:coolbits-frontend` | @CoolBits-Frontend | platform | active | 1 | run.invoker, logging.logWriter | env:prod, service:frontend... |
| `nha:coolbits-monitor` | @CoolBits-Monitor | platform | active | 1 | monitoring.viewer, monitoring.writer | env:prod, service:monitoring... |
| `nha:coolbits-rag` | @CoolBits-RAG | platform | active | 1 | run.invoker, storage.objectViewer, aiplatform.user | env:prod, service:rag... |
| `nha:cosign-enforcer` | @Cosign-Enforcer | platform | active | 1 | storage.objectViewer, kms.cryptoKeyDecrypter | env:prod, service:security... |
| `nha:restore-worker` | @Restore-Worker | platform | active | 1 | storage.objectViewer, storage.objectCreator | env:prod, service:restore... |

## Mlops

| ID | Name | Owner | Status | Channels | Permissions | Tags |
|----|------|-------|--------|----------|-------------|------|
| `nha:embedding-worker` | @Embedding-Worker | platform | active | 1 | run.invoker, aiplatform.user | env:prod, service:mlops... |
| `nha:ocopilot` | @OCopilot | platform | active | 1 | run.invoker | env:prod, service:mlops... |
| `nha:ogemini` | @OGemini | platform | active | 1 | run.invoker | env:prod, service:mlops... |
| `nha:ogpt` | @OGPT | platform | active | 1 | run.invoker | env:prod, service:mlops... |
| `nha:ogrok` | @OGrok | platform | active | 1 | run.invoker | env:prod, service:mlops... |
| `nha:rag-ingest-worker` | @RAG-Ingest-Worker | platform | active | 1 | run.invoker, storage.objectViewer, aiplatform.user | env:prod, service:mlops... |
| `nha:rag-search-worker` | @RAG-Search-Worker | platform | active | 1 | run.invoker, storage.objectViewer, aiplatform.user | env:prod, service:mlops... |
| `nha:vertex` | @Vertex | platform | active | 1 | aiplatform.user, aiplatform.deploymentManager | env:prod, service:mlops... |

## Ops

| ID | Name | Owner | Status | Channels | Permissions | Tags |
|----|------|-------|--------|----------|-------------|------|
| `nha:budget-guard` | @Budget-Guard | platform | active | 1 | billing.accounts.getSpendingInformation | env:prod, service:billing... |
| `nha:chaos-orchestrator` | @Chaos-Orchestrator | platform | active | 1 | run.invoker, logging.logWriter | env:prod, service:chaos... |
| `nha:chaos-runner` | @Chaos-Runner | platform | active | 1 | run.invoker, logging.logWriter | env:prod, service:chaos... |
| `nha:drill-runner` | @Drill-Runner | platform | active | 1 | run.invoker, storage.objectViewer, logging.logWriter | env:prod, service:dr... |
| `nha:slo-gate` | @SLO-Gate | platform | active | 1 | monitoring.viewer, run.invoker | env:prod, service:slo... |
| `nha:uptime-monitor` | @Uptime-Monitor | platform | active | 1 | monitoring.viewer, monitoring.writer | env:prod, service:monitoring... |

## Personal

| ID | Name | Owner | Status | Channels | Permissions | Tags |
|----|------|-------|--------|----------|-------------|------|
| `nha:andrei` | @Andrei | andrei | active | 1 | roles/owner | env:prod, service:owner... |
| `nha:opypgpt03` | @oPyGPT03 | platform | active | 1 | run.invoker, storage.objectViewer, logging.logWriter | env:prod, service:coordinator... |
| `nha:orunner` | @oRunner | platform | active | 1 | run.invoker, logging.logWriter | env:prod, service:runner... |

## Security

| ID | Name | Owner | Status | Channels | Permissions | Tags |
|----|------|-------|--------|----------|-------------|------|
| `nha:breach-runbook-bot` | @Breach-Runbook-Bot | platform | active | 1 | run.invoker, logging.logWriter | env:prod, service:security... |
| `nha:cve-scan` | @CVE-Scan | platform | active | 1 | run.invoker | env:prod, service:security... |
| `nha:gitleaks-scan` | @Gitleaks-Scan | platform | active | 1 | run.invoker | env:prod, service:security... |
| `nha:opa-conftest` | @OPA-Conftest | platform | active | 1 | run.invoker | env:prod, service:security... |
| `nha:rbac-hmac-gateway` | @RBAC-HMAC-Gateway | platform | active | 1 | run.invoker, logging.logWriter | env:prod, service:auth... |
| `nha:secret-manager-sync` | @Secret-Manager-Sync | platform | active | 1 | secretmanager.secretAccessor, secretmanager.secretVersionManager | env:prod, service:secrets... |

## Seo Tools

| ID | Name | Owner | Status | Channels | Permissions | Tags |
|----|------|-------|--------|----------|-------------|------|
| `nha:seo-audit` | @SEO-Audit | platform | deprecated | 1 | storage.objectViewer | env:deprecated, service:seo... |
| `nha:seo-keywords` | @SEO-Keywords | platform | deprecated | 1 | storage.objectViewer | env:deprecated, service:seo... |

