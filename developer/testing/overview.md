---
title: 'Testing overview'
description: 'How to validate changes in Materi services and what “verified” should mean'
---

Testing in Materi is multi-layered because the system spans multiple services and integration
surfaces (HTTP, WebSocket collaboration, and events).

This page provides a baseline approach. The authoritative commands live in each service’s
`Makefile` / `README.md`.

## Test layers

-   **Unit tests**: fast, isolated behavior (preferred for most logic)
-   **Integration tests**: validate persistence, auth boundaries, and service contracts
-   **End-to-end checks**: validate cross-service flows (including collaboration where relevant)

## What to run before opening a PR

At minimum:

1. Run the service’s standard test target (see its `Makefile`).
2. If you changed an integration surface, update contracts and docs:
    - HTTP behavior: update OpenAPI and ensure reference drift check passes
    - Events: update protobuf schemas and ensure consumers remain compatible

## Verification philosophy

-   Prefer tests that are deterministic and run in CI.
-   When adding new endpoints or workflows, include at least one concrete example request.
-   If a change is user-visible, ensure Customer Docs or Developer Guide is updated accordingly.

## Related docs

-   Contributing workflow: [/developer/contributing/overview](/developer/contributing/overview)
-   API contract: `/openapi/openapi.json`
-   Event schemas: `shared/proto/*.proto`
