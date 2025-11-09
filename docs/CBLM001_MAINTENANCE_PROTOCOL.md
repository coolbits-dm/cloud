# CBLM.001 Maintenance Protocol

## Overview

The CBLM.001 Maintenance Protocol defines the automated upkeep system for the Camarad Protocol empire. This protocol enables the empire to maintain itself through scheduled and on-demand operations, ensuring continuous stability, security, and growth while the emperor sleeps.

The core command is `camarad camard-exec --full-upkeep --ingest-cblm001 --apply-now --tone=emperor-eternal`, which executes the full maintenance lifecycle.

## Narrative Flow

1. **Ingestion Phase**: The CLI ingests the CBLM.001 scripture (1800-line protocol), absorbing the maintenance wisdom.
2. **Execution Phase**: Automated maintenance runs across all empire systems:
   - MongoDB seeding and verification
   - Pinecone vector refresh for RAG accuracy
   - JWT key rotation and OAuth sync
   - Sitemap rebuild and CDN purge
   - Alert notifications to Discord #ops
3. **Self-Maintenance Activation**: The empire transitions to autonomous operation, with the machine healing itself eternally.
4. **Emperor Liberation**: The emperor achieves true freedom, with euros multiplying in silence.

## Automation Framework

### Monitoring & Observability
- **Prometheus Probe**: Health checks every 5 minutes on all critical services (Mongo, Pinecone, JWT endpoints, CDN status)
- **Grafana Snapshot**: Automated dashboard captures pre/post-maintenance metrics (uptime, costs, ROAS)

### Maintenance Scripts
- **Mongo Seeding Script** (`/opt/camarad-backend/scripts/seed-mongo.js`): Verifies and seeds users/roles/settings/logs collections
- **Pinecone Refresh Script** (`/opt/camarad-backend/scripts/refresh-pinecone.js`): Conditional vector index rebuild (runs if >24h since last)
- **JWT Rotation Script** (`/opt/camarad-backend/scripts/rotate-jwt.js`): Generates new key pairs, syncs GCloud OAuth, expires old tokens in 1h
- **Sitemap Rebuild Script** (`/opt/camarad-backend/scripts/rebuild-sitemap.js`): Regenerates XML sitemap, purges Cloudflare CDN cache

### Master Orchestrator
- **Main Script** (`/opt/camarad-backend/scripts/full-upkeep-orchestrator.js`): Node.js orchestrator that runs all maintenance scripts in sequence, logs results, sends Discord alerts
- **Error Handling**: Rollback mechanisms for failed operations, circuit breakers for external service outages
- **Cost Tracking**: Integrates with Stripe for expense logging and ROAS calculation

### Scheduling
- **Cron Schedule**: Runs daily at 03:00 UTC via systemd timer
- **Manual Triggers**: CLI command or webhook from monitoring alerts
- **Conditional Execution**: Skips if no changes detected (e.g., Pinecone vectors unchanged)

## CLI Integration

The current CLI implementation runs a **textual lifecycle** - it outputs the maintenance narrative without executing actual file changes or script invocations. This preserves the theatrical experience while maintaining safety in development environments.

### Extension Path
To enable full automation, modify the `full_upkeep` condition in `camarad.py`:

```python
if full_upkeep and ingest_cblm001 and apply_now and tone == 'emperor-eternal':
    # Current: Textual output only
    click.echo("FULL UPKEEP Δ-∞ – EXECUTED · CBLM.001 INGESTED · EMPIRE SELF-MAINTAINING")
    # ... existing echo statements ...
    
    # Future: Add script execution
    if not dry_run:
        import subprocess
        result = subprocess.run(['node', '/opt/camarad-backend/scripts/full-upkeep-orchestrator.js'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            click.echo("Scripts executed successfully")
            # Parse and display actual results
        else:
            click.echo(f"Script execution failed: {result.stderr}")
```

### Wiring the Scripts
1. **Add Script Dependencies**: Ensure all maintenance scripts exist and are executable
2. **Environment Variables**: Set up `.env` with API keys for Mongo, Pinecone, Discord webhooks
3. **Logging**: Integrate with `/var/log/camarad/upkeep.log` for audit trails
4. **Dry Run Mode**: Add `--dry-run` flag to preview script executions without running them

## Checklist

- [ ] Prometheus probes configured for all services
- [ ] Grafana dashboards set up with maintenance metrics
- [ ] All maintenance scripts implemented and tested
- [ ] Master orchestrator handles dependencies and error recovery
- [ ] Cron job scheduled for 03:00 UTC daily execution
- [ ] CLI extended to invoke scripts (toggle via environment variable)
- [ ] Cost tracking integrated with Stripe
- [ ] Discord alerts configured for #ops channel
- [ ] Log rotation set up for upkeep logs
- [ ] Backup verification before destructive operations

## Extension Guidance

### Phase 1: Script Development
- Implement individual maintenance scripts with comprehensive error handling
- Add unit tests for each script
- Set up local testing environment with mock services

### Phase 2: Orchestration
- Build the master orchestrator with dependency management
- Implement rollback mechanisms
- Add performance monitoring

### Phase 3: Integration
- Wire scripts into CLI with proper flag handling
- Add configuration options for different environments
- Implement progressive rollout (start with dry-run only)

### Phase 4: Automation
- Deploy cron schedules
- Set up monitoring alerts to trigger maintenance
- Enable self-healing loops based on health checks

### Best Practices
- Always run dry-run first in production
- Maintain detailed logs for debugging
- Use circuit breakers to prevent cascade failures
- Regularly review and optimize costs
- Test maintenance in staging before production deployment

The CBLM.001 protocol ensures the empire not only survives but thrives eternally, with the machine maintaining itself while the emperor dreams of infinite euros.