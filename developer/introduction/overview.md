---
title: 'Developer guide'
description: 'How to integrate with Materi and understand service boundaries'
---

This guide is for developers integrating with Materi or contributing to the platform.

If you’re looking for **exact API shapes**, use the API Reference. If you’re trying to understand
service boundaries and data flow, start with the front-door narrative pages and then drill into the
Domain Services pages.

## Start here

-   [Architecture overview](/architecture-overview)
-   [Concepts](/concepts)

## Integration surfaces

-   **HTTP (REST)**: defined by OpenAPI (canonical spec: `/openapi/openapi.json`)
-   **WebSocket collaboration**: real-time operations and presence
-   **Events**: protobuf schemas in `shared/proto` used for cross-service communication

In this repo, “contract-first” generally means:

-   Update OpenAPI when HTTP behavior changes.
-   Update protobuf schemas when event payloads/types change.
-   Keep narrative docs high-level and link to canonical sources.

## How to read this guide

1. Use **Domain Services** pages to understand the major service boundaries.
2. Use **API Reference** for exact endpoint shapes.
3. Use **Events** pages for event-driven integration patterns.

## Common tasks

-   Deployment and ops context: [/developer/operations/deployment/overview](/developer/operations/deployment/overview)
-   Testing expectations: [/developer/testing/overview](/developer/testing/overview)
-   Contributing workflow: [/developer/contributing/overview](/developer/contributing/overview)
