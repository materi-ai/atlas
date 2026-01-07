---
title: 'Shield service'
description: 'Authentication, authorization, and user/workspace administration'
---

Shield is the authentication and administration surface for Materi.

In regulated environments, Shield is typically where identity, access control, and audit-related
behavior becomes explicit.

## Responsibilities

-   User lifecycle and identity management
-   Authentication flows (including enterprise SSO patterns)
-   Authorization and role/permission enforcement
-   Audit-related capabilities (where applicable)

## Integration notes

-   If you’re implementing a new API endpoint, ensure auth requirements are represented in OpenAPI.
-   If you change permission semantics, update both developer docs and any customer-facing permission guides.

## When making changes

-   Prefer explicit, testable permission checks over implicit behavior.
-   Keep authn/authz behavior consistent across services by updating shared contracts and docs.
