# Reference: Production Readiness

"Done" for a shippable app is not a merged PR — it is **running safely in production and
operable**. This is the checklist that takes an app from building to production. It applies whenever
the requirement includes **deploying / shipping / releasing / going live** (not just building a
feature in isolation).

## Plan requirement (non-negotiable when production is in scope)

When going to production is in scope, the **plan MUST contain a "Production Readiness" section** that
lists every applicable item below as a **trackable checkbox** — each either **addressed** or marked
**N/A with a one-line reason**. A plan that omits production concerns is an incomplete plan; do not
enter Phase 3 for the release without it. Verify it against the checklist in
`project-profile.md` (§Plan verification).

**Right-size, don't pad.** A static site has no DB migrations; a CLI has no CORS; an internal tool
may skip DR. Skip what genuinely doesn't apply — but **say so explicitly** (N/A + reason) rather than
silently dropping it, so the gap is a decision, not an oversight.

## The checklist (group by concern; cover every applicable line)

### 1. Build & release
- Reproducible production build (optimized, minified/tree-shaken; source maps handled).
- Artifact/versioning strategy (semver/tags); immutable, promotable artifacts (Docker image, bundle).
- Containerization / packaging where the target needs it (Dockerfile, buildpack); pinned base images.

### 2. Configuration, environments & secrets
- Config externalized from code; **no secrets committed** — sourced from env / secret manager / vault.
- Distinct **dev / staging / prod** environments with separate config and credentials.
- Documented required env vars (name, purpose, example) and safe defaults; startup fails fast on
  missing required config.

### 3. Data: migrations, seeding, backups & recovery
- Schema migrations that run **forward cleanly** and have a **rollback / down** path; tested on a
  prod-like copy.
- Seed/reference-data strategy; idempotent, repeatable.
- **Backups** scheduled and **restore actually tested**; retention + point-in-time recovery as needed.
- Data migration/backfill plan for existing records; zero-downtime (expand/contract) if required.

### 4. CI/CD pipeline
- CI runs **lint + type + unit + integration + E2E + build** on every PR; red blocks merge.
- Automated deploy/release path (or its config) to staging then prod; **reuse the repo's existing
  pipeline** — don't invent a parallel one.
- Gated promotion (manual approval or checks) to prod; deployments are auditable/repeatable.

### 5. Observability
- **Structured logging** (levels, correlation/request IDs; no secrets/PII in logs).
- **Metrics** for the golden signals (latency, traffic, errors, saturation) + key business metrics.
- **Health/readiness/liveness** endpoints or checks.
- **Error/crash reporting** (e.g. Sentry) wired for backend and client.
- **Tracing** for distributed calls where the architecture warrants it.
- **Alerting** on the symptoms a human must react to (error spikes, latency, saturation, down),
  routed to a real destination; dashboards for the key signals.

### 6. Security & compliance hardening
- **AuthN/AuthZ** enforced on every protected route/action; least privilege.
- Input validation & output encoding at boundaries; injection/XSS/SSRF/CSRF handled.
- Secure transport (TLS everywhere); security headers (HSTS, CSP, etc.); safe CORS.
- Rate limiting / abuse protection on public endpoints; secrets rotation plan.
- **Dependency & image vulnerability scan** clean (audit/SCA); SBOM if required.
- Sensitive-data handling: encryption at rest/in transit; PII minimization.

### 7. Performance, scaling & capacity
- Meets the target latency/throughput under **realistic load** (load/stress-tested if it matters).
- No obvious N+1 / hot-path blocking; caching where it earns its keep; sensible payloads.
- Scaling model defined (horizontal/vertical, autoscaling, connection pools, rate/quota limits).
- Resource limits/requests set (CPU/mem); graceful behavior under pressure (timeouts, backpressure).

### 8. Reliability & release safety
- **Rollback plan** that is fast and tested (previous artifact re-deployable).
- Progressive delivery where risky: **feature flags**, canary/blue-green, staged rollout.
- Graceful degradation & retries/circuit-breakers on external deps; sensible timeouts.
- **DR**: RPO/RTO understood; failover story for the datastore/region if the SLA demands it.
- **Post-deploy smoke test** runs against the live environment and gates the release.

### 9. Networking & delivery (web)
- Domain, DNS, and **TLS certificates** (auto-renew); CDN/static-asset caching & cache-busting.
- Reverse proxy / load balancer config; timeouts and body limits.

### 10. Privacy, legal & compliance
- Data-retention & deletion policy; consent/cookie handling; GDPR/CCPA obligations if in scope.
- Licenses of dependencies compatible; required notices included.
- Audit logging for sensitive actions where regulated.

### 11. Cost & quotas
- Estimated running cost and third-party quota/rate limits understood; alarms on cost/quota where it
  can runaway.

### 12. Documentation & operability
- README/`docs` section: **how to build, configure, run, deploy, and operate** the app.
- **Runbook**: common failures + fixes, restart/rollback steps, on-call/escalation, dashboards & alert
  links.
- ADRs/notes for significant production decisions.

### 13. Mobile release (React Native / Expo / Flutter / native — when mobile)
- **Code signing & provisioning** (iOS certificates/profiles; Android keystore) handled and secured.
- App **versioning & build numbers** bumped; release/debug configs separated.
- **Store submission** path: App Store Connect / TestFlight, Google Play Console / internal testing;
  store metadata, screenshots, and **privacy nutrition labels / data-safety** form.
- **Crash reporting & analytics** in the release build (Crashlytics/Sentry).
- **OTA update** strategy where used (EAS Update / CodePush) with rollout & rollback.
- Permissions declared and justified; deep-link/universal-link config verified.

## Verify before calling it production-ready
- Every applicable item above is **addressed or explicitly N/A** in the plan and **done** in the work.
- The app has been **deployed to a prod-like environment** and the **post-deploy smoke test passes**
  — or, if no deploy target is available this run, the **production-readiness artifacts** (Dockerfile,
  CI/CD config, env templates, migrations, health checks, runbook) exist and you state precisely what
  remains to actually go live.
- Rollback has been rehearsed (or its exact steps documented).
