---
title: 'Deployment overview'
description: 'How to think about deploying Materi services, what to verify, and where the sources of truth live'
---

This page describes deployment at a high level without assuming a specific hosting environment.
The repo contains multiple deployment targets (local/dev, cloud, and cluster-based), so the
**source of truth is the operational code and runbooks**, not a single fixed set of steps.

## What “deployment” means in Materi

-   Building and releasing service artifacts
-   Applying configuration and secrets for an environment
-   Migrating stateful dependencies (when required)
-   Verifying health checks and observability before traffic

## Where to find the real instructions

-   Ops runbooks: [/operations/RUNBOOK](/operations/RUNBOOK)
-   Platform runbook: [/platform/RUNBOOK](/platform/RUNBOOK)
-   Deployment scripts: `scripts/` (repo root)
-   Service-specific build/run targets: each service’s `Makefile` / `README.md`

## Suggested deployment order (baseline)

1. Provision dependencies (Postgres/Redis) and verify connectivity.
2. Apply environment configuration (non-secret config first, then secrets).
3. Deploy application services.
4. Deploy observability (metrics/logs/alerts) and confirm telemetry is flowing.
5. Run a smoke test (HTTP + collaboration if applicable).

## Verification checklist

-   Health endpoints return success for all critical services.
-   Database migrations (if any) have completed and the schema is compatible.
-   Logs show no crash loops or repeated fatal errors.
-   Key dashboards and alerts are enabled for the environment.

## Rollback and safety

Rollback strategy depends on whether a change is schema-breaking.

-   If a change is backwards compatible, rollback can often be a simple version revert.
-   If migrations are involved, ensure you have a documented downgrade/restore plan.
