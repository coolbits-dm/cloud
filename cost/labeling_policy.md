# CoolBits.ai Cost Labeling Policy
# ================================

## Overview
All CoolBits.ai services must have standardized cost tracking labels to enable proper cost allocation and monitoring.

## Required Labels

### Standard Labels (Mandatory)
- **env**: Environment (dev, staging, prod)
- **service**: Service name (frontend, bridge, dashboard, etc.)
- **owner**: Service owner (ogpt, andrei, team-name)
- **cost-center**: Cost center (ogpt, coolbits, specific-project)

### Optional Labels
- **version**: Service version
- **region**: Deployment region
- **tier**: Service tier (critical, standard, low-priority)

## Label Values

### Environment (env)
- `dev` - Development environment
- `staging` - Staging environment  
- `prod` - Production environment

### Service (service)
- `frontend` - Main dashboard/frontend
- `bridge` - FastAPI bridge service
- `dashboard` - Admin dashboard
- `api` - API services
- `worker` - Background workers
- `database` - Database services
- `cache` - Caching services
- `monitoring` - Monitoring services

### Owner (owner)
- `ogpt` - oPyGPT03 team
- `andr` - Andrei (CEO)
- `dev` - Development team
- `ops` - Operations team

### Cost Center (cost-center)
- `ogpt` - oPyGPT03 project
- `coolbits` - CoolBits.ai platform
- `infra` - Infrastructure costs
- `dev` - Development costs

## Implementation

### Cloud Run Services
```bash
gcloud run services update coolbits-frontend \
  --region=europe-west1 \
  --labels=env=prod,service=frontend,owner=ogpt,cost-center=ogpt,version=1.0.0
```

### Cloud SQL Instances
```bash
gcloud sql instances patch coolbits-db \
  --labels=env=prod,service=database,owner=ogpt,cost-center=ogpt
```

### Cloud Storage Buckets
```bash
gsutil label ch -l env:prod,service:storage,owner:ogpt,cost-center:ogpt gs://coolbits-storage
```

### Kubernetes Resources
```yaml
metadata:
  labels:
    env: prod
    service: frontend
    owner: ogpt
    cost-center: ogpt
    version: "1.0.0"
```

## Cost Tracking Queries

### Daily Cost by Service
```sql
SELECT 
  day,
  service,
  SUM(cost_eur) as daily_cost
FROM `coolbits.billing.v_cost_daily`
WHERE day >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
GROUP BY day, service
ORDER BY day DESC, daily_cost DESC;
```

### Monthly Budget Utilization
```sql
SELECT 
  month_start,
  budget_eur,
  actual_cost_eur,
  budget_utilization_pct
FROM `coolbits.billing.v_budget_vs_actual`
WHERE month_start = DATE_TRUNC(CURRENT_DATE(), MONTH);
```

## Budget Alerts

### Thresholds
- **Warning**: 80% of monthly budget
- **Critical**: 100% of monthly budget

### Alert Configuration
```bash
gcloud billing budgets create \
  --billing-account=$BILLING_ACCOUNT \
  --display-name="coolbits-monthly" \
  --budget-amount=1000EUR \
  --threshold-rule=percent=0.8 \
  --threshold-rule=percent=1.0 \
  --all-updates-rule-pubsub-topic="projects/$PROJECT/topics/billing-alerts"
```

## Compliance

### Pre-deployment Check
All services must have required labels before deployment. CI/CD pipeline will reject deployments without proper labeling.

### Cost Review Process
- Weekly cost review for all services
- Monthly budget vs actual analysis
- Quarterly cost optimization review

### Escalation
- High cost alerts (>100 EUR/day) → Immediate notification
- Budget threshold breaches → CEO notification
- Unlabeled resources → Automatic shutdown after 24h

## Examples

### Frontend Service
```bash
gcloud run services update coolbits-frontend \
  --region=europe-west1 \
  --labels=env=prod,service=frontend,owner=ogpt,cost-center=ogpt,version=1.0.0,tier=critical
```

### Database Service
```bash
gcloud sql instances patch coolbits-db \
  --labels=env=prod,service=database,owner=ogpt,cost-center=ogpt,version=1.0.0,tier=critical
```

### Storage Bucket
```bash
gsutil label ch -l env:prod,service:storage,owner=ogpt,cost-center=ogpt,tier=standard gs://coolbits-storage
```
