# Atlas Docs Ownership

This file defines **who owns what** in the documentation.
Ownership means accountability for accuracy, freshness, and review.

## How ownership works

| Role                  | Responsibility                                               |
| --------------------- | ------------------------------------------------------------ |
| **Primary owner**     | Reviews all changes, ensures accuracy, schedules updates     |
| **Secondary owner**   | Backup reviewer, escalation path when primary is unavailable |
| **Contributing team** | Can propose changes; changes require owner approval          |

## Ownership matrix

### Front-door pages (Getting Started tab)

| Page                   | Primary        | Secondary      | Team     |
| ---------------------- | -------------- | -------------- | -------- |
| introduction           | @docs-lead     | @product       | docs     |
| quickstart             | @docs-lead     | @product       | docs     |
| development            | @platform-lead | @docs-lead     | platform |
| documentation-contract | @docs-lead     | @platform-lead | docs     |
| architecture-overview  | @platform-lead | @domain-lead   | platform |
| concepts               | @platform-lead | @docs-lead     | platform |

### Customer Docs tab

| Section                     | Primary        | Secondary    | Team     |
| --------------------------- | -------------- | ------------ | -------- |
| customer/overview/\*        | @product       | @docs-lead   | product  |
| customer/getting-started/\* | @product       | @docs-lead   | product  |
| customer/documents/\*       | @product       | @canvas-lead | product  |
| customer/collaboration/\*   | @relay-lead    | @product     | domain   |
| customer/ai/\*              | @aria-lead     | @product     | platform |
| customer/workspaces/\*      | @shield-lead   | @product     | domain   |
| customer/integrations/\*    | @platform-lead | @product     | platform |
| customer/security/\*        | @shield-lead   | @security    | domain   |
| customer/support/\*         | @product       | @docs-lead   | product  |

### Developer Guide tab

| Section                              | Primary          | Secondary      | Team     |
| ------------------------------------ | ---------------- | -------------- | -------- |
| developer/contributing/\*            | @docs-lead       | @platform-lead | docs     |
| developer/introduction/\*            | @platform-lead   | @docs-lead     | platform |
| developer/recipes/\*                 | @docs-lead       | @platform-lead | docs     |
| developer/domain/api/\*              | @api-lead        | @domain-lead   | domain   |
| developer/domain/relay/\*            | @relay-lead      | @domain-lead   | domain   |
| developer/domain/shield/\*           | @shield-lead     | @domain-lead   | domain   |
| developer/domain/manuscript/\*       | @manuscript-lead | @domain-lead   | domain   |
| developer/domain/printery/\*         | @printery-lead   | @domain-lead   | domain   |
| developer/platform/aria/\*           | @aria-lead       | @platform-lead | platform |
| developer/platform/intelligence/\*   | @platform-lead   | @aria-lead     | platform |
| developer/products/canvas/\*         | @canvas-lead     | @product       | products |
| developer/products/atlas/\*          | @docs-lead       | @platform-lead | docs     |
| developer/products/specifications/\* | @product         | @platform-lead | products |
| developer/events/\*                  | @manuscript-lead | @printery-lead | domain   |
| developer/testing/\*                 | @platform-lead   | @domain-lead   | platform |
| developer/operations/\*              | @ops-lead        | @platform-lead | ops      |

### Enterprise tab

| Section                    | Primary        | Secondary      | Team     |
| -------------------------- | -------------- | -------------- | -------- |
| enterprise/overview/\*     | @product       | @security      | product  |
| enterprise/deployment/\*   | @ops-lead      | @platform-lead | ops      |
| enterprise/security/\*     | @security      | @shield-lead   | security |
| enterprise/compliance/\*   | @security      | @legal         | security |
| enterprise/integrations/\* | @platform-lead | @security      | platform |
| enterprise/support/\*      | @product       | @ops-lead      | product  |
| enterprise/admin/\*        | @product       | @ops-lead      | product  |
| enterprise/ha/\*           | @ops-lead      | @platform-lead | ops      |
| enterprise/integration/\*  | @platform-lead | @security      | platform |
| enterprise/migration/\*    | @ops-lead      | @platform-lead | ops      |
| enterprise/monitoring/\*   | @ops-lead      | @platform-lead | ops      |
| enterprise/scalability/\*  | @ops-lead      | @platform-lead | ops      |

### Internal tab

| Section                    | Primary        | Secondary      | Team     |
| -------------------------- | -------------- | -------------- | -------- |
| internal/runbooks/\*       | @ops-lead      | @platform-lead | ops      |
| internal/adr/\*            | @platform-lead | @domain-lead   | platform |
| internal/service-health/\* | @ops-lead      | @platform-lead | ops      |
| internal/postmortems/\*    | @ops-lead      | @platform-lead | ops      |
| internal/analytics/\*      | @platform-lead | @product       | platform |
| internal/architecture/\*   | @platform-lead | @domain-lead   | platform |
| internal/engineering/\*    | @platform-lead | @domain-lead   | platform |
| internal/finance/\*        | @legal         | @product       | legal    |
| internal/hr/\*             | @legal         | @product       | legal    |
| internal/legal/\*          | @legal         | @security      | legal    |
| internal/operations/\*     | @ops-lead      | @platform-lead | ops      |
| internal/overview/\*       | @docs-lead     | @platform-lead | docs     |
| internal/product/\*        | @product       | @docs-lead     | product  |
| internal/security/\*       | @security      | @platform-lead | security |

### API Reference tab

| Section    | Primary   | Secondary      | Team   |
| ---------- | --------- | -------------- | ------ |
| api/\*     | @api-lead | @platform-lead | domain |
| openapi/\* | @api-lead | @platform-lead | domain |

## Team aliases

| Alias              | Description               | Members |
| ------------------ | ------------------------- | ------- |
| `@docs-lead`       | Documentation team lead   | —       |
| `@product`         | Product management        | —       |
| `@platform-lead`   | Platform engineering lead | —       |
| `@domain-lead`     | Domain services lead      | —       |
| `@api-lead`        | API service owner         | —       |
| `@relay-lead`      | Relay/collaboration owner | —       |
| `@shield-lead`     | Shield/auth owner         | —       |
| `@manuscript-lead` | Manuscript/events owner   | —       |
| `@printery-lead`   | Printery/consumers owner  | —       |
| `@aria-lead`       | Aria/AI owner             | —       |
| `@canvas-lead`     | Canvas frontend owner     | —       |
| `@ops-lead`        | Operations/SRE lead       | —       |
| `@security`        | Security team             | —       |
| `@legal`           | Legal/compliance          | —       |

> **Note**: Replace `—` with actual GitHub usernames or team handles when onboarding.

## Escalation path

1. Ping the **primary owner** on the PR or issue.
2. If no response in 2 business days, ping the **secondary owner**.
3. If still blocked, escalate to `@platform-lead` or `@docs-lead`.

## Review requirements

| Change type                | Required reviewers                       |
| -------------------------- | ---------------------------------------- |
| New page                   | Primary owner + 1 from contributing team |
| Content update             | Primary owner                            |
| Structure change (nav, IA) | `@docs-lead` + affected primary owners   |
| Reference regeneration     | Automated (CI gate)                      |
| Ownership change           | Current owner + new owner + `@docs-lead` |

## Stale content process

Pages are considered **stale** if:

-   Not updated in 6 months AND
-   The underlying system has changed

Stale pages should be:

1. Flagged with a `DRAFT:` notice at the top
2. Assigned to the primary owner for refresh
3. Tracked in the docs backlog

## Adding new pages

When adding a new page:

1. Determine which section it belongs to (see matrix above)
2. The primary owner for that section is the default owner
3. Add the page to `docs.json` navigation
4. Ensure the page meets the documentation contract requirements
5. Get approval from the section's primary owner
