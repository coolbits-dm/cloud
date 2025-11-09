# Runbook: Stripe Webhook Failures

## Alert
- **Name:** StripeWebhookFailures
- **Condition:** rate(billing_webhook_errors_total[15m]) > 0
- **Severity:** TICKET
- **Runbook:** runbooks/stripe_webhook.md

## Immediate Actions (0-5 minutes)

### 1. Acknowledge Alert
- [ ] Acknowledge alert in Alertmanager
- [ ] Post to #incidents Slack channel
- [ ] Create incident ticket: SEV-2
- [ ] Check Stripe dashboard for webhook status

### 2. Verify Webhook Configuration
```bash
# Check webhook endpoint health
curl -s "$GW/v1/billing/webhook/stripe" -X POST -H "Content-Type: application/json" -d '{"test": true}'

# Check webhook signature validation
curl -s "$GW/v1/billing/webhook/status"
```

### 3. Check Recent Webhook Events
```bash
# Check webhook event logs
curl -s "$GW/v1/billing/webhook/events" | jq '.[] | select(.status == "failed")'

# Check Stripe event logs
stripe events list --limit=10
```

## Investigation (5-15 minutes)

### 4. Identify Failure Patterns
```bash
# Check error types
curl -s "$GW/metrics" | grep billing_webhook_errors_total

# Check timing patterns
curl -s "$GW/v1/billing/webhook/analytics"
```

### 5. Verify Server Time Sync
```bash
# Check server time
date -u
ntpq -p

# Check for time drift
curl -s "$GW/v1/time/check"
```

### 6. Check Idempotency
```bash
# Check duplicate event handling
curl -s "$GW/v1/billing/webhook/duplicates"

# Check idempotency table
curl -s "$GW/v1/billing/webhook/idempotency"
```

## Mitigation (15-30 minutes)

### 7. Immediate Fixes
- [ ] Resend failed webhooks: `stripe events resend <event_id>`
- [ ] Check webhook signature: Verify `x-stripe-signature` header
- [ ] Validate timestamp: Check for replay attacks

### 8. Configuration Updates
- [ ] Update webhook URL if needed
- [ ] Verify webhook secret in Secret Manager
- [ ] Check SSL certificate validity

### 9. Retry Mechanism
- [ ] Implement exponential backoff
- [ ] Set maximum retry attempts
- [ ] Configure dead letter queue

## Resolution (30-60 minutes)

### 10. Root Cause Analysis
- [ ] Check application logs for webhook processing
- [ ] Review recent code changes
- [ ] Check database transaction logs
- [ ] Verify external dependencies

### 11. Long-term Fixes
- [ ] Implement webhook signature validation
- [ ] Add comprehensive error handling
- [ ] Implement webhook event queuing
- [ ] Add webhook health monitoring

## Communication

### Internal Updates
- [ ] Update #incidents Slack every 15 minutes
- [ ] Post status to internal dashboard
- [ ] Notify billing team

### External Communication
- [ ] Update status page if billing affected
- [ ] Notify affected customers if payment issues
- [ ] Post-mortem within 48 hours

## Escalation

### If unresolved after 30 minutes:
- [ ] Escalate to SEV-1
- [ ] Page on-call engineer
- [ ] Consider manual payment processing

### If unresolved after 60 minutes:
- [ ] Page engineering manager
- [ ] Contact Stripe support
- [ ] Implement emergency billing procedures

## Post-Incident

### 12. Post-Mortem
- [ ] Schedule post-mortem within 48 hours
- [ ] Document timeline and root cause
- [ ] Create action items with owners
- [ ] Update this runbook with lessons learned

## Prevention

### Monitoring Improvements
- [ ] Add webhook signature validation monitoring
- [ ] Monitor webhook processing latency
- [ ] Track webhook success rates
- [ ] Alert on webhook queue depth

### Process Improvements
- [ ] Implement webhook testing
- [ ] Add webhook validation to deployment gates
- [ ] Create webhook capacity planning
- [ ] Regular webhook security reviews

## Stripe-Specific Actions

### 13. Stripe Dashboard
- [ ] Check webhook delivery status
- [ ] Review failed webhook attempts
- [ ] Check webhook endpoint configuration
- [ ] Verify webhook secret

### 14. Stripe CLI
```bash
# Test webhook locally
stripe listen --forward-to localhost:8080/v1/billing/webhook/stripe

# Resend failed events
stripe events resend <event_id>

# Check webhook logs
stripe events list --limit=50
```

### 15. Webhook Security
- [ ] Verify webhook signature validation
- [ ] Check for replay attacks
- [ ] Validate event timestamps
- [ ] Implement rate limiting
