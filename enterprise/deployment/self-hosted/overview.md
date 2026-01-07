---
title: 'Self-hosted overview'
description: 'How Materi self-hosting is structured, what you need, and where to go next'
---

Self-hosting Materi means you operate the services and data plane in your own environment.
This page stays intentionally high-level and links to the repo’s operational sources of truth.

## What you run

-   Application services (API + supporting components)
-   Postgres and Redis
-   Observability (metrics/logs/alerts)

## What you decide

-   Deployment target (Kubernetes vs. VM-based)
-   Network and ingress boundaries
-   Identity (SSO) and key management
-   Backups, retention, and disaster recovery

## Sources of truth in this repo

-   Incident response: [Incident response runbook](/developer/operations/runbooks/incident-response)
-   Disaster recovery: [DR runbook](/developer/operations/runbooks/disaster-recovery)
-   Environment configuration examples live under `operations/` and `domain/`

## Next steps

-   Follow the environment setup guide for your target platform
-   Deploy dependencies (Postgres/Redis) first, then application services, then observability
-   Validate health checks and alerts before onboarding production traffic
