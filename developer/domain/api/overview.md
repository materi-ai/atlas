---
title: 'API service'
description: 'REST gateway for documents, workspaces, and AI features'
---

The API service is the primary HTTP entry point for Materi.

## Responsibilities

-   Document and workspace CRUD
-   Orchestration for system workflows
-   Publishing events for cross-service synchronization

## Canonical references

-   REST surface: `/openapi/openapi.json` (this docs site)
-   Architecture context: [/architecture-overview](/architecture-overview)

## How clients should integrate (baseline)

-   Start from the OpenAPI spec for parameter names, response types, and error shapes.
-   Expect transient failures in distributed systems; design clients to be resilient.
-   Treat server behavior as contract-driven: if it isn’t in OpenAPI (or explicitly documented),
    consider it unstable.

## Operational reality (baseline)

When integrating:

-   Prefer idempotent client behavior for retries.
-   Treat event-driven updates as at-least-once delivery unless a stronger guarantee is documented.

## When making changes

-   If you change an endpoint (inputs/outputs/status codes), update OpenAPI first.
-   If the change emits or consumes events, update protobuf schemas under `shared/proto`.
