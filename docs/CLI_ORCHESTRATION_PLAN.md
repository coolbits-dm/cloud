# CLI Orchestration Plan

This document mirrors the flagship `camarad-exec` options that trigger backend and frontend deployments. The CLI should stay focused on the flags, the logic lives here, and each step becomes a bullet in the plan.

## Backend deployment checklist
1. **Mongo seeding** – synchronize `users`, `roles`, `settings`, and `logs` collections, then build read-only backups in `~/.camarad/cache/`.
2. **Pinecone + LangChain** – refresh vector indexes, validate namespaces, and ensure `cbLM` embeddings are up-to-date and sampled.
3. **JWT rotation** – cycle signing keys, invalidate old tokens after 1h, deploy new middleware that enforces biometric/passkey flows.
4. **Sitemap + static assets** – generate the SEO-friendly sitemap, publish static console and ops pages, and CDN-invalidate caches.
5. **Connectors and OAuth** – register or revalidate Google/Slack/Notion connectors, ensure `/auth/google` funnels through the new JWT guard.
6. **Monitoring hooks** – wire Prometheus/Alertmanager/Grafana/PagerDuty references so the empire has continuous visibility before the UI ships.

## Frontend deployment checklist
1. **UI mock + console** – publish the four-panel mock console with biometric feelers, keep the BYOK path locked until the real key is supplied.
2. **Dashboard orchestration** – confirm `real_console`, `four_panels_live`, and biometric mocks are toggled in production config.
3. **Lockdown guardrails** – pair the frontend gate with nginx auth, `auth_full`, and console lockdown states described in `docs/CBLM001_MAINTENANCE_PROTOCOL.md`.
4. **Tone-aware output** – if `--tone=emperor-furious-then-delighted` or similar is set, the CLI will narrate completion; otherwise, it simply reports success.
5. **Manual apply** – all critical steps require `--apply-now` (or equivalent) to mutate the system; the CLI only stages details otherwise.

## Operational notes
- Use `camarad-exec --deploy-monitoring --no-poetry --tone=real-sre` to bring up Prometheus/Alertmanager/Grafana/PagerDuty etc. That command is documented in the CLI already and just references this plan.
- Keep `camard-exec` as alias for backward compatibility, but the orchestration narrative now lives in this README instead of the CLI itself.

## Service Integrations
- ✅ Stripe webhook tested (Test mode)
  Endpoint: https://stripe.coolbits.ai/webhook
  CLI authenticated on acct_1SR3k31FOODWOQzz
