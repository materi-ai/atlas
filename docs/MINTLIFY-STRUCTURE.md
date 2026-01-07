# Materi Mintlify Documentation Structure

**Version:** 1.0.0
**Last Updated:** 2025-12-22
**Purpose:** Unified documentation architecture for all audiences

---

## Overview

This document explains the comprehensive Mintlify `mint.json` configuration that ties together all 4 architectural domains (Domain, Platform, Products, Operations) across customer, internal, and enterprise Materi applications.

---

## Documentation Architecture

### Audience Segmentation

```
┌─────────────────────────────────────────────────────────────┐
│                    MATERI DOCUMENTATION                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   CUSTOMER   │  │  DEVELOPER   │  │ API REFERENCE│     │
│  │     DOCS     │  │    GUIDE     │  │              │     │
│  │              │  │              │  │              │     │
│  │ End-user     │  │ Engineering  │  │ REST/WS/     │     │
│  │ features     │  │ architecture │  │ GraphQL      │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐                       │
│  │  ENTERPRISE  │  │   INTERNAL   │                       │
│  │     DOCS     │  │     DOCS     │                       │
│  │              │  │              │                       │
│  │ Self-hosted, │  │ Team docs,   │                       │
│  │ SSO, HA      │  │ processes    │                       │
│  └──────────────┘  └──────────────┘                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Tab Structure

### 1. Customer Docs Tab

**Audience:** End users, content creators, team leads
**Focus:** How to use Materi's features
**Path:** `/customer/*`

#### Navigation Groups:
- **Overview**: What is Materi, key features, pricing, use cases
- **Getting Started**: Sign-up, first document, workspace setup
- **Document Management**: Creating, editing, organizing, sharing documents
- **Real-Time Collaboration**: Presence, comments, conflict resolution
- **AI Features**: Content generation, analysis, enhancement
- **Workspaces & Teams**: Managing teams, roles, permissions
- **Integrations**: GitHub, Slack, Google Drive, webhooks
- **Security & Privacy**: Authentication, encryption, GDPR
- **Support & Resources**: FAQ, troubleshooting, tutorials

#### Key Pages:
```
customer/
├── overview/
│   ├── what-is-materi.mdx
│   ├── key-features.mdx
│   ├── pricing.mdx
│   └── use-cases.mdx
├── getting-started/
│   ├── sign-up.mdx
│   ├── first-document.mdx
│   ├── invite-team.mdx
│   └── workspace-setup.mdx
├── documents/
│   ├── creating-documents.mdx
│   ├── editing-documents.mdx
│   ├── organizing-documents.mdx
│   ├── sharing-documents.mdx
│   ├── version-history.mdx
│   └── templates.mdx
├── collaboration/
│   ├── overview.mdx
│   ├── presence.mdx
│   ├── comments.mdx
│   ├── mentions.mdx
│   ├── conflict-resolution.mdx
│   └── offline-mode.mdx
├── ai/
│   ├── overview.mdx
│   ├── content-generation.mdx
│   ├── summarization.mdx
│   ├── enhancement-suggestions.mdx
│   ├── code-analysis.mdx
│   ├── diagram-analysis.mdx
│   └── safety-gates.mdx
├── workspaces/
│   ├── creating-workspaces.mdx
│   ├── managing-members.mdx
│   ├── roles-permissions.mdx
│   ├── workspace-settings.mdx
│   └── billing.mdx
├── integrations/
│   ├── overview.mdx
│   ├── github.mdx
│   ├── slack.mdx
│   ├── google-drive.mdx
│   ├── notion.mdx
│   └── webhooks.mdx
├── security/
│   ├── overview.mdx
│   ├── authentication.mdx
│   ├── data-encryption.mdx
│   ├── access-controls.mdx
│   ├── audit-logs.mdx
│   └── gdpr-compliance.mdx
└── support/
    ├── contact-support.mdx
    ├── faq.mdx
    ├── troubleshooting.mdx
    ├── keyboard-shortcuts.mdx
    └── video-tutorials.mdx
```

---

### 2. Developer Guide Tab

**Audience:** Software engineers, architects, DevOps engineers
**Focus:** How to build, extend, and maintain Materi
**Path:** `/developer/*`

#### Architectural Domain Coverage:

##### Domain Services (Core Microservices)
```
developer/domain/
├── api/                    # Go/Fiber REST API
│   ├── overview.mdx
│   ├── architecture.mdx
│   ├── setup.mdx
│   ├── endpoints.mdx
│   ├── authentication.mdx
│   ├── rate-limiting.mdx
│   ├── testing.mdx
│   └── deployment.mdx
├── relay/                  # Rust/Axum Real-Time Service
│   ├── overview.mdx
│   ├── architecture.mdx
│   ├── operational-transform.mdx
│   ├── websocket-protocol.mdx
│   ├── presence-tracking.mdx
│   ├── testing.mdx
│   └── deployment.mdx
├── shield/                 # Python/Django Auth Service
│   ├── overview.mdx
│   ├── architecture.mdx
│   ├── authentication.mdx
│   ├── authorization.mdx
│   ├── user-management.mdx
│   ├── oauth-saml.mdx
│   ├── testing.mdx
│   └── deployment.mdx
├── manuscript/             # Protocol Buffers Event Schemas
│   ├── overview.mdx
│   ├── event-schemas.mdx
│   ├── custom-options.mdx
│   ├── code-generation.mdx
│   ├── versioning.mdx
│   └── msx-inspector.mdx
└── printery/              # Go Event Consumer Hub
    ├── overview.mdx
    ├── architecture.mdx
    ├── consumer-groups.mdx
    ├── handler-registry.mdx
    ├── resilience-patterns.mdx
    └── deployment.mdx
```

##### Platform Services (AI & Intelligence)
```
developer/platform/
├── aria/                   # AI Enhancement Engine
│   ├── overview.mdx
│   ├── architecture.mdx
│   ├── text-analysis.mdx
│   ├── code-safety.mdx
│   ├── diagram-analysis.mdx
│   ├── enhancement-suggestions.mdx
│   ├── model-integration.mdx
│   ├── graceful-degradation.mdx
│   ├── testing.mdx
│   └── deployment.mdx
└── intelligence/
    ├── scribe.mdx
    ├── github-integrations.mdx
    └── analytics.mdx
```

##### Products (Frontend & Specifications)
```
developer/products/
├── canvas/                 # React/TypeScript Monorepo
│   ├── overview.mdx
│   ├── architecture.mdx
│   ├── setup.mdx
│   ├── component-library.mdx
│   ├── state-management.mdx
│   ├── api-integration.mdx
│   ├── real-time-sync.mdx
│   ├── testing.mdx
│   ├── storybook.mdx
│   └── deployment.mdx
├── atlas/                  # Documentation Hub
│   ├── overview.mdx
│   ├── structure.mdx
│   ├── contributing.mdx
│   └── mdx-components.mdx
└── specifications/         # Requirements Traceability
    ├── overview.mdx
    ├── traceability.mdx
    ├── requirement-types.mdx
    └── verification.mdx
```

##### Operations (Infrastructure & Deployment)
```
developer/operations/
├── infrastructure/
│   ├── overview.mdx
│   ├── terraform.mdx
│   ├── kubernetes.mdx
│   ├── networking.mdx
│   └── security.mdx
├── deployment/
│   ├── overview.mdx
│   ├── gitops.mdx
│   ├── ci-cd.mdx
│   ├── blue-green.mdx
│   └── rollback.mdx
├── folio/                  # Observability Platform
│   ├── overview.mdx
│   ├── metrics.mdx
│   ├── logging.mdx
│   ├── tracing.mdx
│   ├── alerting.mdx
│   └── dashboards.mdx
└── runbooks/
    ├── incident-response.mdx
    ├── scaling.mdx
    ├── backup-restore.mdx
    └── disaster-recovery.mdx
```

##### Cross-Cutting Concerns
```
developer/
├── events/                 # Event-Driven Architecture
│   ├── overview.mdx
│   ├── event-envelope.mdx
│   ├── redis-streams.mdx
│   ├── publishing.mdx
│   ├── consuming.mdx
│   ├── idempotency.mdx
│   ├── retry-patterns.mdx
│   └── dead-letter-queue.mdx
├── testing/
│   ├── overview.mdx
│   ├── unit-tests.mdx
│   ├── integration-tests.mdx
│   ├── e2e-tests.mdx
│   ├── load-tests.mdx
│   ├── contract-tests.mdx
│   └── chaos-engineering.mdx
└── contributing/
    ├── overview.mdx
    ├── code-standards.mdx
    ├── git-workflow.mdx
    ├── pr-process.mdx
    ├── issue-templates.mdx
    └── documentation.mdx
```

---

### 3. API Reference Tab

**Audience:** Integration developers, API consumers
**Focus:** Comprehensive API documentation
**Path:** `/api/*`

#### API Types:

##### REST API
```
api/rest/
├── auth/
│   ├── login.mdx
│   ├── logout.mdx
│   ├── refresh-token.mdx
│   ├── oauth.mdx
│   └── saml.mdx
├── users/
│   ├── get-user.mdx
│   ├── update-user.mdx
│   ├── delete-user.mdx
│   ├── list-users.mdx
│   └── user-preferences.mdx
├── documents/
│   ├── create-document.mdx
│   ├── get-document.mdx
│   ├── update-document.mdx
│   ├── delete-document.mdx
│   ├── list-documents.mdx
│   ├── document-versions.mdx
│   └── document-permissions.mdx
├── workspaces/
│   ├── create-workspace.mdx
│   ├── get-workspace.mdx
│   ├── update-workspace.mdx
│   ├── delete-workspace.mdx
│   ├── list-workspaces.mdx
│   ├── workspace-members.mdx
│   └── workspace-roles.mdx
├── collaboration/
│   ├── get-session.mdx
│   ├── list-sessions.mdx
│   ├── get-presence.mdx
│   ├── comments.mdx
│   └── mentions.mdx
├── ai/
│   ├── analyze-text.mdx
│   ├── analyze-code.mdx
│   ├── analyze-diagram.mdx
│   ├── generate-content.mdx
│   ├── enhance-content.mdx
│   └── summarize.mdx
├── files/
│   ├── upload-file.mdx
│   ├── get-file.mdx
│   ├── delete-file.mdx
│   └── list-files.mdx
└── search/
    ├── search-documents.mdx
    ├── search-users.mdx
    └── search-workspaces.mdx
```

##### WebSocket API
```
api/websocket/
├── overview.mdx
├── connection.mdx
├── authentication.mdx
├── operations.mdx
├── presence.mdx
├── events.mdx
└── error-handling.mdx
```

##### GraphQL API (Beta)
```
api/graphql/
├── overview.mdx
├── schema.mdx
├── queries.mdx
├── mutations.mdx
└── subscriptions.mdx
```

##### SDKs
```
api/sdks/
├── overview.mdx
├── javascript-typescript.mdx
├── python.mdx
├── go.mdx
├── rust.mdx
└── java.mdx
```

##### Event Schemas (Protocol Buffers)
```
api/events/
├── overview.mdx
├── user-events.mdx
├── document-events.mdx
├── collaboration-events.mdx
├── workspace-events.mdx
├── aria-events.mdx
├── notification-events.mdx
└── audit-events.mdx
```

---

### 4. Enterprise Tab

**Audience:** Enterprise IT, security teams, compliance officers
**Focus:** Self-hosted deployment, security, compliance
**Path:** `/enterprise/*`

#### Enterprise Features:

```
enterprise/
├── overview/
│   ├── what-is-enterprise.mdx
│   ├── feature-comparison.mdx
│   ├── pricing.mdx
│   └── sla.mdx
├── deployment/
│   ├── self-hosted/
│   │   ├── overview.mdx
│   │   ├── requirements.mdx
│   │   ├── kubernetes.mdx
│   │   ├── docker-compose.mdx
│   │   ├── configuration.mdx
│   │   ├── upgrading.mdx
│   │   └── backup-restore.mdx
│   ├── cloud-dedicated/
│   │   ├── overview.mdx
│   │   ├── provisioning.mdx
│   │   ├── vpc-peering.mdx
│   │   ├── custom-domains.mdx
│   │   └── monitoring.mdx
│   └── hybrid/
│       ├── overview.mdx
│       ├── architecture.mdx
│       ├── data-residency.mdx
│       └── compliance.mdx
├── security/
│   ├── overview.mdx
│   ├── authentication.mdx
│   ├── sso-saml.mdx
│   ├── scim-provisioning.mdx
│   ├── encryption.mdx
│   ├── network-security.mdx
│   ├── audit-logs.mdx
│   ├── data-residency.mdx
│   ├── compliance-certifications.mdx
│   ├── penetration-testing.mdx
│   └── vulnerability-disclosure.mdx
├── admin/
│   ├── overview.mdx
│   ├── user-management.mdx
│   ├── workspace-management.mdx
│   ├── license-management.mdx
│   ├── usage-analytics.mdx
│   ├── billing.mdx
│   └── support.mdx
├── integration/
│   ├── overview.mdx
│   ├── ldap-ad.mdx
│   ├── okta.mdx
│   ├── azure-ad.mdx
│   ├── google-workspace.mdx
│   ├── custom-sso.mdx
│   ├── api-gateway.mdx
│   └── webhooks.mdx
├── monitoring/
│   ├── overview.mdx
│   ├── health-checks.mdx
│   ├── metrics.mdx
│   ├── logging.mdx
│   ├── alerting.mdx
│   ├── performance-tuning.mdx
│   └── capacity-planning.mdx
├── ha/                     # High Availability
│   ├── overview.mdx
│   ├── architecture.mdx
│   ├── failover.mdx
│   ├── load-balancing.mdx
│   ├── disaster-recovery.mdx
│   └── backup-strategy.mdx
├── scalability/
│   ├── overview.mdx
│   ├── horizontal-scaling.mdx
│   ├── database-scaling.mdx
│   ├── cache-strategy.mdx
│   ├── cdn-configuration.mdx
│   └── performance-benchmarks.mdx
├── migration/
│   ├── overview.mdx
│   ├── from-cloud.mdx
│   ├── from-competitors.mdx
│   ├── data-import.mdx
│   ├── user-migration.mdx
│   └── validation.mdx
└── support/
    ├── overview.mdx
    ├── support-tiers.mdx
    ├── contact.mdx
    ├── sla.mdx
    ├── escalation.mdx
    └── training.mdx
```

---

### 5. Internal Tab

**Audience:** Materi employees (engineering, product, operations)
**Focus:** Internal processes, architecture, team documentation
**Path:** `/internal/*`

#### Internal Documentation Structure:

```
internal/
├── overview/
│   ├── welcome.mdx
│   ├── team-structure.mdx
│   ├── communication.mdx
│   └── tools.mdx
├── architecture/
│   ├── system-design/
│   │   ├── overview.mdx
│   │   ├── domain-services.mdx
│   │   ├── platform-services.mdx
│   │   ├── product-architecture.mdx
│   │   ├── operations-architecture.mdx
│   │   ├── cross-segment-integration.mdx
│   │   ├── event-driven-architecture.mdx
│   │   └── data-models.mdx
│   ├── adrs/               # Architecture Decision Records
│   │   ├── overview.mdx
│   │   ├── adr-001-microservices-architecture.mdx
│   │   ├── adr-002-event-driven-communication.mdx
│   │   ├── adr-003-operational-transform.mdx
│   │   ├── adr-004-protocol-buffers.mdx
│   │   ├── adr-005-redis-streams.mdx
│   │   ├── adr-006-polyglot-services.mdx
│   │   └── adr-007-graceful-degradation.mdx
│   └── specs/
│       ├── l1-strategic-specs.mdx
│       ├── l2-tactical-specs.mdx
│       ├── requirement-traceability.mdx
│       └── verification-matrix.mdx
├── engineering/
│   ├── workflow/
│   │   ├── overview.mdx
│   │   ├── issue-templates.mdx
│   │   ├── pr-process.mdx
│   │   ├── code-review.mdx
│   │   ├── testing-strategy.mdx
│   │   └── deployment-process.mdx
│   ├── standards/
│   │   ├── overview.mdx
│   │   ├── go-standards.mdx
│   │   ├── rust-standards.mdx
│   │   ├── python-standards.mdx
│   │   ├── typescript-standards.mdx
│   │   └── proto-standards.mdx
│   ├── ownership/
│   │   ├── overview.mdx
│   │   ├── domain-team.mdx
│   │   ├── platform-team.mdx
│   │   ├── product-team.mdx
│   │   ├── operations-team.mdx
│   │   └── on-call-rotation.mdx
│   └── performance/
│       ├── overview.mdx
│       ├── benchmarking.mdx
│       ├── profiling.mdx
│       ├── optimization-guide.mdx
│       └── slo-sli-sla.mdx
├── operations/
│   ├── incidents/
│   │   ├── overview.mdx
│   │   ├── severity-levels.mdx
│   │   ├── response-process.mdx
│   │   ├── communication.mdx
│   │   ├── post-mortems.mdx
│   │   └── blameless-culture.mdx
│   ├── releases/
│   │   ├── overview.mdx
│   │   ├── versioning.mdx
│   │   ├── release-process.mdx
│   │   ├── rollback-procedures.mdx
│   │   └── change-management.mdx
│   ├── capacity/
│   │   ├── overview.mdx
│   │   ├── metrics.mdx
│   │   ├── forecasting.mdx
│   │   └── scaling-strategy.mdx
│   └── cost/
│       ├── overview.mdx
│       ├── tracking.mdx
│       ├── optimization.mdx
│       └── budgeting.mdx
├── product/
│   ├── strategy/
│   │   ├── vision.mdx
│   │   ├── roadmap.mdx
│   │   ├── okrs.mdx
│   │   └── competitive-analysis.mdx
│   ├── development/
│   │   ├── discovery.mdx
│   │   ├── planning.mdx
│   │   ├── execution.mdx
│   │   └── launch.mdx
│   └── research/
│       ├── overview.mdx
│       ├── user-personas.mdx
│       ├── interviews.mdx
│       ├── surveys.mdx
│       └── analytics.mdx
├── security/
│   ├── practices/
│   │   ├── overview.mdx
│   │   ├── threat-modeling.mdx
│   │   ├── secure-coding.mdx
│   │   ├── code-review-security.mdx
│   │   ├── dependency-management.mdx
│   │   └── secrets-management.mdx
│   ├── vulnerabilities/
│   │   ├── overview.mdx
│   │   ├── scanning.mdx
│   │   ├── reporting.mdx
│   │   ├── remediation.mdx
│   │   └── disclosure.mdx
│   └── compliance/
│       ├── overview.mdx
│       ├── soc2.mdx
│       ├── gdpr.mdx
│       ├── hipaa.mdx
│       └── iso27001.mdx
├── analytics/
│   ├── overview.mdx
│   ├── metrics-dashboard.mdx
│   ├── user-analytics.mdx
│   ├── system-analytics.mdx
│   └── business-intelligence.mdx
├── hr/
│   ├── onboarding.mdx
│   ├── engineering-levels.mdx
│   ├── performance-reviews.mdx
│   ├── compensation.mdx
│   ├── benefits.mdx
│   └── remote-work.mdx
└── legal/
    ├── contracts.mdx
    ├── intellectual-property.mdx
    ├── privacy-policy.mdx
    ├── terms-of-service.mdx
    ├── budget.mdx
    └── expense-policy.mdx
```

---

## Cross-Domain Integration

### How the 4 Architectural Domains Map to Documentation

```yaml
Domain Services (Core):
  Customer Docs: Real-time collaboration features
  Developer Guide: API, Relay, Shield, Manuscript, Printery architecture
  API Reference: REST endpoints, WebSocket protocol, Event schemas
  Enterprise: High availability, performance, scaling
  Internal: Service ownership, incident management, ADRs

Platform Services (AI/Intelligence):
  Customer Docs: AI features (content generation, analysis, safety)
  Developer Guide: Aria architecture, model integration, graceful degradation
  API Reference: AI endpoints (/analyze/*, /enhance/*)
  Enterprise: AI privacy, data residency, compliance
  Internal: Platform team ownership, AI strategy

Products (Frontend/Specs):
  Customer Docs: UI features, user workflows
  Developer Guide: Canvas architecture, component library, state management
  API Reference: Client-side SDK documentation
  Enterprise: Frontend deployment, CDN configuration
  Internal: Product strategy, design system, user research

Operations (Infrastructure):
  Customer Docs: System status, uptime, performance
  Developer Guide: Infrastructure setup, deployment processes, observability
  API Reference: Health checks, metrics endpoints
  Enterprise: Self-hosted deployment, monitoring, disaster recovery
  Internal: SRE practices, capacity planning, cost management
```

---

## Key Features

### 1. Navigation Hierarchy

- **5 Main Tabs**: Customer, Developer, API Reference, Enterprise, Internal
- **Nested Groups**: Up to 3 levels deep for complex topics
- **Logical Flow**: Progressive disclosure (overview → getting started → advanced)

### 2. Branding & Theming

```json
{
  "colors": {
    "primary": "#4A90E2",      // Materi Blue
    "light": "#7B68EE",        // Purple accent
    "dark": "#2E5C8A",         // Dark blue
    "anchors": {
      "from": "#4A90E2",
      "to": "#7B68EE"          // Gradient links
    }
  }
}
```

### 3. Search & Discovery

- **Global Search**: Searches across all documentation tabs
- **Prompt**: "Search Materi documentation..."
- **Indexed**: All MDX files automatically indexed

### 4. API Playground

```json
{
  "api": {
    "baseUrl": "https://api.materi.com/v1",
    "auth": {
      "method": "bearer"
    },
    "playground": {
      "mode": "show"              // Interactive API testing
    }
  }
}
```

### 5. OpenAPI Integration

```json
{
  "openapi": [
    "api/openapi/rest-api.yaml",        // Auto-generate REST docs
    "api/openapi/websocket-api.yaml",   // WebSocket protocol docs
    "api/openapi/graphql-schema.graphql" // GraphQL schema
  ]
}
```

### 6. Analytics Integration

```json
{
  "analytics": {
    "posthog": {
      "apiKey": "posthog_api_key"
    },
    "ga4": {
      "measurementId": "G-XXXXXXXXXX"
    },
    "mixpanel": {
      "projectToken": "mixpanel_project_token"
    }
  }
}
```

### 7. Feedback Mechanisms

```json
{
  "feedback": {
    "suggestEdit": true,     // "Suggest an edit" button
    "raiseIssue": true,      // "Report an issue" button
    "thumbsRating": true     // Thumbs up/down on each page
  }
}
```

### 8. Versioning

```json
{
  "versions": [
    "v1 (Current)",
    "v2 (Beta)"
  ]
}
```

---

## File Organization

### Recommended Directory Structure

```
docs/
├── mint.json                          # This configuration file
├── introduction.mdx                   # Landing page
├── quickstart.mdx                     # Quick start guide
├── architecture-overview.mdx          # High-level architecture
├── concepts.mdx                       # Core concepts
│
├── customer/                          # Customer documentation
│   ├── overview/
│   ├── getting-started/
│   ├── documents/
│   ├── collaboration/
│   ├── ai/
│   ├── workspaces/
│   ├── integrations/
│   ├── security/
│   └── support/
│
├── developer/                         # Developer guide
│   ├── introduction/
│   ├── domain/                        # Domain services
│   │   ├── api/
│   │   ├── relay/
│   │   ├── shield/
│   │   ├── manuscript/
│   │   └── printery/
│   ├── platform/                      # Platform services
│   │   ├── aria/
│   │   └── intelligence/
│   ├── products/                      # Products
│   │   ├── canvas/
│   │   ├── atlas/
│   │   └── specifications/
│   ├── operations/                    # Operations
│   │   ├── infrastructure/
│   │   ├── deployment/
│   │   ├── folio/
│   │   └── runbooks/
│   ├── events/
│   ├── testing/
│   └── contributing/
│
├── api/                               # API reference
│   ├── introduction/
│   ├── rest/
│   │   ├── auth/
│   │   ├── users/
│   │   ├── documents/
│   │   ├── workspaces/
│   │   ├── collaboration/
│   │   ├── ai/
│   │   ├── files/
│   │   └── search/
│   ├── websocket/
│   ├── graphql/
│   ├── sdks/
│   ├── events/
│   └── openapi/                       # OpenAPI specs
│       ├── rest-api.yaml
│       ├── websocket-api.yaml
│       └── graphql-schema.graphql
│
├── enterprise/                        # Enterprise documentation
│   ├── overview/
│   ├── deployment/
│   │   ├── self-hosted/
│   │   ├── cloud-dedicated/
│   │   └── hybrid/
│   ├── security/
│   ├── admin/
│   ├── integration/
│   ├── monitoring/
│   ├── ha/
│   ├── scalability/
│   ├── migration/
│   └── support/
│
├── internal/                          # Internal documentation
│   ├── overview/
│   ├── architecture/
│   │   ├── system-design/
│   │   ├── adrs/
│   │   └── specs/
│   ├── engineering/
│   │   ├── workflow/
│   │   ├── standards/
│   │   ├── ownership/
│   │   └── performance/
│   ├── operations/
│   │   ├── incidents/
│   │   ├── releases/
│   │   ├── capacity/
│   │   └── cost/
│   ├── product/
│   │   ├── strategy/
│   │   ├── development/
│   │   └── research/
│   ├── security/
│   │   ├── practices/
│   │   ├── vulnerabilities/
│   │   └── compliance/
│   ├── analytics/
│   ├── hr/
│   └── legal/
│
├── logo/                              # Branding assets
│   ├── dark.svg
│   ├── light.svg
│   └── favicon.svg
│
└── images/                            # Documentation images
    ├── background.png
    ├── og-image.png
    └── architecture/
        ├── domain-services.png
        ├── platform-services.png
        ├── product-architecture.png
        └── operations-architecture.png
```

---

## MDX Best Practices

### Frontmatter Structure

```mdx
---
title: "Real-Time Collaboration Overview"
description: "Learn how Materi's real-time collaboration engine enables concurrent editing"
icon: "users"
iconType: "solid"
---

# Real-Time Collaboration Overview

Your content here...
```

### Using Components

Mintlify provides built-in components:

```mdx
<Card title="Quick Start" icon="bolt" href="/quickstart">
  Get started with Materi in 5 minutes
</Card>

<Tabs>
  <Tab title="REST API">
    REST API documentation...
  </Tab>
  <Tab title="WebSocket">
    WebSocket documentation...
  </Tab>
</Tabs>

<CodeGroup>
```javascript
// JavaScript example
const client = new MateriClient({ apiKey: 'your-api-key' });
```

```python
# Python example
client = MateriClient(api_key='your-api-key')
```
</CodeGroup>

<Info>
  This is an informational callout
</Info>

<Warning>
  This is a warning callout
</Warning>

<Tip>
  This is a helpful tip
</Tip>
```

---

## Cross-References

### Linking Between Tabs

```mdx
<!-- From Customer Docs to Developer Guide -->
For technical details, see the [API Architecture](/developer/domain/api/architecture).

<!-- From Developer Guide to API Reference -->
Full endpoint documentation: [REST API Reference](/api/rest/documents/create-document).

<!-- From Enterprise to Internal -->
See internal [ADR-002](/internal/architecture/adrs/adr-002-event-driven-communication) for rationale.
```

---

## Deployment

### Mintlify CLI

```bash
# Install Mintlify CLI
npm i -g mintlify

# Preview documentation locally
mintlify dev

# Build documentation
mintlify build

# Deploy to Mintlify Cloud
mintlify deploy
```

### Environment Setup

```bash
# .env.example
MINTLIFY_API_KEY=your_mintlify_api_key
POSTHOG_API_KEY=your_posthog_key
GA4_MEASUREMENT_ID=your_ga4_id
MIXPANEL_PROJECT_TOKEN=your_mixpanel_token
```

---

## Maintenance

### Adding New Pages

1. Create MDX file in appropriate directory
2. Add entry to `mint.json` navigation array
3. Update cross-references if needed
4. Test locally with `mintlify dev`

### Updating OpenAPI Specs

1. Update `api/openapi/*.yaml` files
2. Mintlify auto-generates API reference pages
3. Test with `mintlify dev`

### Versioning Strategy

When creating v2 documentation:

```bash
docs/
├── v1/                   # Current version
│   └── ...
└── v2/                   # Beta version
    └── ...
```

Update `mint.json`:
```json
{
  "versions": ["v2 (Beta)", "v1 (Current)"]
}
```

---

## Access Control

### Tab Visibility

Configure per-tab access:

```json
{
  "tabs": [
    {
      "name": "Customer Docs",
      "url": "customer",
      "visibility": "public"
    },
    {
      "name": "Internal",
      "url": "internal",
      "visibility": "private",
      "auth": {
        "required": true,
        "provider": "okta"
      }
    }
  ]
}
```

---

## SEO & Metadata

### Page-Level SEO

```mdx
---
title: "Materi Real-Time Collaboration"
description: "Enterprise-grade collaborative editing with sub-50ms latency"
keywords:
  - real-time collaboration
  - operational transform
  - concurrent editing
  - WebSocket
og:image: "/images/collaboration-og.png"
twitter:card: "summary_large_image"
---
```

### Global SEO

Configured in `mint.json`:

```json
{
  "metadata": {
    "og:site_name": "Materi Documentation",
    "og:type": "website",
    "og:title": "Materi - Real-Time Collaborative Document Platform",
    "og:description": "Enterprise-grade collaborative document management with AI enhancement",
    "og:image": "/images/og-image.png",
    "twitter:card": "summary_large_image",
    "twitter:site": "@materi"
  }
}
```

---

## Performance Optimization

### Image Optimization

- Use WebP format for images
- Provide alt text for accessibility
- Use responsive images

```mdx
![Materi Architecture](/images/architecture.webp)
```

### Code Splitting

Mintlify automatically code-splits by tab and page.

### Caching Strategy

- Static assets: 1 year
- Documentation pages: 1 hour
- API specs: 5 minutes

---

## Accessibility

### WCAG 2.1 AA Compliance

- Semantic HTML
- Keyboard navigation
- Screen reader support
- Color contrast ratios
- Alt text for images

### Testing

```bash
# Install axe-core
npm install -D @axe-core/cli

# Run accessibility tests
axe https://docs.materi.com
```

---

## Support & Contributions

### Documentation Issues

Report issues: [GitHub Issues](https://github.com/materi-ai/docs/issues)

### Contributing

1. Fork repository
2. Create feature branch
3. Add/update MDX files
4. Update `mint.json` if needed
5. Submit pull request

---

## Appendix: Full mint.json Schema

See [docs/mint.json](mint.json) for the complete configuration.

---

**Document Version:** 1.0.0
**Last Updated:** 2025-12-22
**Maintainers:** Platform Engineering Team, Documentation Team

---

**End of Document**
