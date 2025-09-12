# Runbook: SLO Burn Rate Fast

## Alert
- **Name:** SLOBurnFast
- **Condition:** (sum(rate(http_requests_total{error="true"}[5m])) / sum(rate(http_requests_total[5m]))) / 0.001 > 14
- **Severity:** PAGE
- **Runbook:** runbooks/slo_burn.md

## Immediate Actions (0-5 minutes)

### 1. Acknowledge Alert
- [ ] Acknowledge alert in Alertmanager
- [ ] Post to #incidents Slack channel
- [ ] Create incident ticket: SEV-1
- [ ] Page on-call engineer immediately

### 2. Confirm with Synthetic Monitoring
```bash
# Check synthetic monitoring results
curl -s "$GW/v1/metrics/synthetics" | grep success

# Verify external monitoring
curl -s "https://status.coolbits.ai/api/health"
```

**If synthetic confirms issue:**
- [ ] Continue to mitigation
- [ ] Update status page

**If synthetic shows no issues:**
- [ ] Check alert configuration
- [ ] Verify metric collection
- [ ] Consider false positive

## Investigation (5-15 minutes)

### 3. Identify Affected Endpoints
```bash
# Check error rates by endpoint
curl -s "$GW/metrics" | grep http_requests_total | grep error="true"

# Check specific endpoint health
curl -s "$GW/v1/metrics" | grep endpoint_error_rate
```

### 4. Check Recent Deployments
```bash
# List recent revisions
gcloud run revisions list --region europe-west1 --service coolbits-gw --limit=5

# Check deployment status
gcloud run services describe coolbits-gw --region europe-west1
```

### 5. System Health Check
```bash
# Check overall system metrics
curl -s "$GW/v1/metrics" | grep -E "(cpu|memory|connections)"

# Check dependency health
curl -s "$GW/v1/health/dependencies"
```

## Mitigation (15-30 minutes)

### 6. Immediate Rate Limiting
- [ ] Implement emergency rate limiting: `RATE_LIMIT_PER_IP=10/min`
- [ ] Enable circuit breakers: `CIRCUIT_BREAKER_ENABLED=true`
- [ ] Check for DDoS patterns

### 7. Traffic Management
- [ ] If single endpoint affected: Route traffic away
- [ ] If multiple endpoints: Consider full rollback
- [ ] Check Cloud Armor WAF rules

### 8. Rollback Decision
**If recent deployment (<2 hours):**
- [ ] Execute rollback: `m20-5-rollback.cmd`
- [ ] Route 100% traffic to previous revision
- [ ] Monitor error rate for 10 minutes

**If no recent deployment:**
- [ ] Check for external factors (DDoS, dependency issues)
- [ ] Implement temporary fixes
- [ ] Consider scaling resources

## Resolution (30-60 minutes)

### 9. Root Cause Analysis
- [ ] Check application logs: `gcloud run logs read coolbits-gw --region europe-west1 --limit=1000`
- [ ] Review recent changes
- [ ] Check dependency status
- [ ] Verify configuration changes

### 10. Long-term Fixes
- [ ] Implement proper error handling
- [ ] Add retry mechanisms
- [ ] Improve monitoring coverage
- [ ] Update alerting thresholds

## Communication

### Internal Updates
- [ ] Update #incidents Slack every 10 minutes
- [ ] Post status to internal dashboard
- [ ] Notify stakeholders immediately

### External Communication
- [ ] Update status page within 5 minutes
- [ ] Post to social media if public impact
- [ ] Send email to affected users if >15 minutes

## Escalation

### If unresolved after 15 minutes:
- [ ] Page engineering manager
- [ ] Consider emergency procedures
- [ ] Activate incident command center

### If unresolved after 30 minutes:
- [ ] Page CTO
- [ ] Consider external support
- [ ] Implement emergency maintenance mode

## Post-Incident

### 11. Post-Mortem
- [ ] Schedule post-mortem within 24 hours
- [ ] Document timeline and root cause
- [ ] Create action items with owners
- [ ] Update this runbook with lessons learned

## Prevention

### Monitoring Improvements
- [ ] Add more granular error rate monitoring
- [ ] Implement predictive alerting
- [ ] Add business impact metrics
- [ ] Monitor error budget burn rate

### Process Improvements
- [ ] Implement deployment gates
- [ ] Add error rate testing
- [ ] Create capacity planning process
- [ ] Regular SLO reviews

## Error Budget Recovery

### 12. Budget Management
- [ ] Calculate remaining error budget
- [ ] Plan for budget recovery
- [ ] Consider temporary SLO adjustments
- [ ] Document budget impact

### 13. Stakeholder Communication
- [ ] Notify business stakeholders
- [ ] Update SLO dashboard
- [ ] Plan for budget recovery period
- [ ] Review SLO targets if needed
