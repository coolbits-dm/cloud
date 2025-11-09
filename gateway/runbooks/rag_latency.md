# Runbook: RAG Latency P95 High

## Alert
- **Name:** RAGLatencyP95High
- **Condition:** histogram_quantile(0.95, sum by (le) (rate(rag_latency_ms_bucket[5m]))) > 300
- **Severity:** PAGE
- **Runbook:** runbooks/rag_latency.md

## Immediate Actions (0-5 minutes)

### 1. Acknowledge Alert
- [ ] Acknowledge alert in Alertmanager
- [ ] Post to #incidents Slack channel
- [ ] Create incident ticket: SEV-2

### 2. Check RAG Variant Status
```bash
# Check if variant B is causing issues
curl -s "$GW/metrics" | grep rag_variant_queries_total
```

**If only variant B is affected:**
- [ ] Execute rollback: `m20-4-canary.cmd --rollback`
- [ ] Verify traffic returns to 100% variant A
- [ ] Monitor latency for 10 minutes

**If both variants affected:**
- [ ] Continue to database investigation

## Investigation (5-15 minutes)

### 3. Database Health Check
```bash
# Check PostgreSQL metrics
curl -s "$GW/v1/metrics" | grep postgresql

# Check connection pool
curl -s "$GW/v1/metrics" | grep db_connections
```

### 4. Check RAG Index Status
```bash
# Check embedding generation queue
curl -s "$GW/v1/metrics" | grep embedding_queue

# Check vector search performance
curl -s "$GW/v1/metrics" | grep vector_search
```

### 5. System Resources
```bash
# Check Cloud Run metrics
gcloud run services describe coolbits-gw --region europe-west1 --format="value(status.conditions)"

# Check memory usage
curl -s "$GW/v1/metrics" | grep memory_usage
```

## Mitigation (15-30 minutes)

### 6. Temporary Measures
- [ ] Reduce top_k parameter: Set `RAG_TOP_K=3` (from default 5)
- [ ] Enable query caching: Set `RAG_CACHE_TTL=300`
- [ ] Check for index bloat: `REINDEX CONCURRENTLY rag_chunks`

### 7. Scale Resources
- [ ] Increase Cloud Run instances: `--min-instances=3 --max-instances=20`
- [ ] Increase memory: `--memory=2Gi`
- [ ] Check CPU utilization

## Resolution (30-60 minutes)

### 8. Root Cause Analysis
- [ ] Check recent deployments: `gcloud run revisions list`
- [ ] Review RAG connector changes
- [ ] Check embedding model updates
- [ ] Verify pgvector extension status

### 9. Long-term Fixes
- [ ] Optimize vector indexes
- [ ] Implement query result caching
- [ ] Add RAG query timeout
- [ ] Implement circuit breaker for RAG

## Communication

### Internal Updates
- [ ] Update #incidents Slack every 15 minutes
- [ ] Post status to internal dashboard
- [ ] Notify stakeholders if >30 minutes

### External Communication
- [ ] Update status page if public impact
- [ ] Post-mortem within 48 hours

## Escalation

### If unresolved after 30 minutes:
- [ ] Escalate to SEV-1
- [ ] Page on-call engineer
- [ ] Consider emergency rollback

### If unresolved after 60 minutes:
- [ ] Page engineering manager
- [ ] Consider disabling RAG temporarily
- [ ] Implement fallback responses

## Post-Incident

### 10. Post-Mortem
- [ ] Schedule post-mortem within 48 hours
- [ ] Document timeline and root cause
- [ ] Create action items with owners
- [ ] Update this runbook with lessons learned

## Prevention

### Monitoring Improvements
- [ ] Add RAG query complexity metrics
- [ ] Monitor embedding generation latency
- [ ] Track vector index size growth
- [ ] Alert on database connection pool exhaustion

### Process Improvements
- [ ] Implement RAG performance testing
- [ ] Add RAG latency to deployment gates
- [ ] Create RAG capacity planning process
- [ ] Regular RAG performance reviews
