# System Design Document: GitHub Organization Structure for Materi

**Document Version:** 1.0
**Date:** 2025-12-22
**Status:** Final
**Authors:** Technical Architecture Team
**Reviewers:** Engineering Leadership, DevOps Team

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Context](#2-system-context)
3. [Design Principles](#3-design-principles)
4. [Repository Architecture](#4-repository-architecture)
5. [GitHub Teams Structure](#5-github-teams-structure)
6. [GitHub Projects](#6-github-projects)
7. [GitHub Packages](#7-github-packages)
8. [Security & Access Control](#8-security--access-control)
9. [Branch Protection & Workflows](#9-branch-protection--workflows)
10. [Settings & Policies](#10-settings--policies)
11. [Insights & Analytics](#11-insights--analytics)
12. [Operational Procedures](#12-operational-procedures)
13. [Implementation Roadmap](#13-implementation-roadmap)
14. [Appendices](#14-appendices)

---

## 1. Executive Summary

### 1.1 Purpose

This System Design Document (SDD) defines the comprehensive GitHub organization structure for the Materi platform, a polyglot microservices ecosystem comprising 13+ repositories across 4 architectural segments. The design optimizes for:

- **Operational Efficiency**: Streamlined workflows, automated governance, minimal friction
- **Security**: Defense-in-depth access controls, automated security scanning, compliance
- **Developer Experience**: Clear ownership, fast onboarding, self-service capabilities
- **Scalability**: Support for 50+ engineers, 20+ repositories, multi-region deployments
- **Observability**: Comprehensive insights into code quality, velocity, and security posture

### 1.2 Scope

This document covers the **technical and operational design** of the following GitHub organization components:

| Component | Coverage |
|-----------|----------|
| **Repositories** | 13 core services + shared libraries + infrastructure repos |
| **Teams** | 12 teams across 4 architectural segments + cross-functional teams |
| **Projects** | 6 organization-level projects for portfolio management |
| **Packages** | Container Registry, npm/pnpm packages, Go modules, Rust crates, Python packages |
| **Security** | Code scanning, secret scanning, Dependabot, SBOM generation, vulnerability management |
| **Settings** | Branch protection, webhooks, integrations, compliance policies |
| **Insights** | Traffic analytics, dependency graphs, security advisories, code frequency |

### 1.3 Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Monorepo per Segment** | Domain, Platform, Products each use monorepo pattern for tightly coupled services |
| **Team-Based Access** | RBAC via GitHub Teams instead of individual permissions |
| **Multi-Environment Projects** | Separate projects for Dev, Staging, Production lifecycle tracking |
| **Automated Security** | CodeQL, Dependabot, Trivy scanning on all repositories |
| **Package Registry Strategy** | GitHub Packages for all artifacts (containers, libraries, binaries) |
| **GitOps Deployment** | ArgoCD + Kustomize for declarative infrastructure management |

---

## 2. System Context

### 2.1 Materi Architecture Overview

Materi follows a **polyglot microservices architecture** organized into **4 architectural segments**:

```
┌─────────────────────────────────────────────────────────────────┐
│                    MATERI ORGANIZATION                          │
├─────────────────────────────────────────────────────────────────┤
│  DOMAIN (Core Business Logic)                                   │
│  ├─ API (Go/Fiber) - HTTP Gateway                              │
│  ├─ Relay (Rust/Axum) - Real-time Collaboration                │
│  ├─ Shield (Python/Django) - Auth & User Management            │
│  ├─ Manuscript (Protocol Buffers) - Event Schemas              │
│  └─ Printery (Go) - Event Consumer Hub                         │
├─────────────────────────────────────────────────────────────────┤
│  PLATFORM (Enhancement Layer)                                    │
│  ├─ Aria (Python/FastAPI) - AI Content Analysis                │
│  ├─ Scribe (Python) - Documentation Tooling                    │
│  └─ GitHub Integrations - Platform connectors                   │
├─────────────────────────────────────────────────────────────────┤
│  PRODUCTS (User-Facing)                                          │
│  ├─ Canvas (TypeScript/React) - Frontend Monorepo              │
│  ├─ Atlas (Markdown/MDX) - Technical Documentation              │
│  └─ __spec__ (YAML/Markdown) - Requirements Management          │
├─────────────────────────────────────────────────────────────────┤
│  OPERATIONS (Infrastructure)                                     │
│  ├─ Folio (Go) - Observability Hub                             │
│  ├─ Shredder (Multi-lang) - E2E Testing                        │
│  ├─ GitOps (ArgoCD/Kustomize) - Deployment                     │
│  ├─ Nestr (Go) - Multi-repo Orchestration                      │
│  └─ Traceo (Python/MCP) - Requirements Traceability            │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Technology Stack Distribution

| Language | Repositories | Primary Use Cases |
|----------|--------------|-------------------|
| **Go** | 4 (API, Printery, Folio, Nestr) | High-throughput HTTP services, CLI tools, observability |
| **Rust** | 1 (Relay) | Real-time WebSocket, operational transform, performance-critical |
| **Python** | 3 (Shield, Aria, Scribe, Traceo) | Django admin, AI/ML, data processing, tooling |
| **TypeScript** | 1 (Canvas) | React frontend, design system, customer-facing UI |
| **Protocol Buffers** | 1 (Manuscript) | Event schema definitions, cross-service contracts |
| **IaC** | 3 (Terraform, K8s, GitOps) | Infrastructure, deployment, orchestration |

### 2.3 Current State Assessment

**Existing Structure** (as of 2025-12-22):

```bash
/Users/alexarno/materi/
├── domain/           # Domain services (5 repos worth of code)
├── platform/         # Platform services (3 repos worth)
├── products/         # Product applications (3 repos worth)
├── operations/       # Operations & tooling (5+ repos worth)
├── lab/              # Experimental services (2 repos)
├── shared/           # Shared libraries
└── docs/             # Documentation
```

**Current Status:**
- **Repository Model**: Single monorepo with nested directories
- **Team Structure**: Undefined (implicit via CODEOWNERS)
- **Projects**: Not configured
- **Packages**: Not published to GitHub Packages
- **Security**: Basic branch protection, no automated scanning

**Target State** (This SDD):
- **Repository Model**: Multi-repo with segment-based monorepos
- **Team Structure**: 12 GitHub Teams with defined ownership
- **Projects**: 6 organization-level projects for lifecycle tracking
- **Packages**: All artifacts published to GitHub Packages
- **Security**: Comprehensive automated scanning, SBOM, compliance

---

## 3. Design Principles

### 3.1 Core Principles

#### P1: **Segment Alignment**
- GitHub structure must mirror the 4-segment architecture (Domain, Platform, Products, Operations)
- Teams, repositories, and projects organized by architectural segment
- Cross-segment collaboration enabled via shared teams and projects

#### P2: **Team Autonomy with Guardrails**
- Teams have full autonomy within their segment repositories
- Organization-wide guardrails via branch protection and required reviews
- Self-service capabilities for common operations (deployments, rollbacks, scaling)

#### P3: **Security by Default**
- All repositories have security scanning enabled from day 1
- Secrets never committed (enforced via pre-commit hooks + secret scanning)
- Dependency vulnerabilities auto-detected and prioritized
- SBOM generation for all production artifacts

#### P4: **Observable & Auditable**
- All actions logged and traceable (GitHub audit log + custom integrations)
- Metrics-driven insights (cycle time, deployment frequency, MTTR)
- Compliance-ready (SOC2, GDPR, ISO 27001 alignment)

#### P5: **Developer Experience First**
- Onboarding time: <2 hours for new engineers
- Clear ownership and escalation paths (CODEOWNERS, GitHub Teams)
- Fast feedback loops (CI <10min, PR reviews <4 hours)
- Self-documenting structure (README-driven, ADRs, runbooks)

### 3.2 Non-Functional Requirements

| NFR ID | Requirement | Target | Measurement |
|--------|-------------|--------|-------------|
| **NFR-GH-001** | Repository creation time | <5 minutes | Time from request to first commit |
| **NFR-GH-002** | Team permission propagation | <1 minute | Time for access change to take effect |
| **NFR-GH-003** | Security scan coverage | 100% repos | % of repos with CodeQL + Dependabot |
| **NFR-GH-004** | Secret scanning false positive rate | <5% | False positives / total alerts |
| **NFR-GH-005** | Package registry availability | 99.9% | Uptime for GitHub Packages |
| **NFR-GH-006** | CI pipeline success rate | >95% | Successful builds / total builds |
| **NFR-GH-007** | Dependency update latency | <7 days | Time from CVE to patch deployment |
| **NFR-GH-008** | Insights dashboard load time | <3 seconds | Time to render org-level insights |

---

## 4. Repository Architecture

### 4.1 Repository Taxonomy

Materi uses a **hybrid repository model**:
- **Segment Monorepos**: Domain, Platform, Products each have a monorepo for tightly coupled services
- **Standalone Repos**: Operations services, infrastructure, and tooling use dedicated repos
- **Shared Libraries**: Cross-cutting libraries in dedicated repos

#### 4.1.1 Repository Naming Convention

```
<segment>-<service-name>
```

**Examples:**
- `domain-api` (API service in Domain segment)
- `platform-aria` (Aria AI service in Platform segment)
- `products-canvas` (Canvas frontend in Products segment)
- `operations-folio` (Folio observability in Operations segment)
- `shared-manuscript` (Manuscript event schemas, shared)
- `infra-terraform` (Infrastructure as code)

#### 4.1.2 Repository Ownership Matrix

| Repository | Segment | Owner Team | Technology | Status |
|------------|---------|------------|------------|--------|
| **domain-monorepo** | Domain | @materi/domain-leads | Multi | ✅ Core |
| **domain-api** | Domain | @materi/domain-api | Go 1.25.3 | ✅ Core |
| **domain-relay** | Domain | @materi/domain-relay | Rust 1.75+ | ✅ Core |
| **domain-shield** | Domain | @materi/domain-shield | Python 3.11+ | ✅ Core |
| **shared-manuscript** | Domain | @materi/domain-events | Protocol Buffers | ✅ Core |
| **domain-printery** | Domain | @materi/domain-events | Go | 📋 Planned |
| **platform-aria** | Platform | @materi/platform-ai | Python 3.12+ | ✅ Core |
| **platform-scribe** | Platform | @materi/platform-tooling | Python | 🚧 Beta |
| **platform-integrations** | Platform | @materi/platform-integrations | Multi | 📋 Planned |
| **products-canvas** | Products | @materi/frontend | TypeScript/React | ✅ Core |
| **products-atlas** | Products | @materi/documentation | Markdown/MDX | ✅ Core |
| **products-specifications** | Products | @materi/product-management | YAML/Markdown | ✅ Core |
| **operations-folio** | Operations | @materi/sre | Go | ✅ Core |
| **operations-shredder** | Operations | @materi/qa | Multi-lang | ✅ Core |
| **operations-gitops** | Operations | @materi/sre | ArgoCD/Kustomize | ✅ Core |
| **operations-nestr** | Operations | @materi/devtools | Go 1.24+ | ✅ Core |
| **operations-traceo** | Operations | @materi/product-management | Python/MCP | 🚧 Beta |
| **infra-terraform** | Operations | @materi/sre | Terraform | ✅ Core |
| **infra-kubernetes** | Operations | @materi/sre | K8s YAML | ✅ Core |
| **shared-proto** | Shared | @materi/domain-events | Protocol Buffers | ✅ Core |
| **shared-sdk-typescript** | Shared | @materi/frontend | TypeScript | 📋 Planned |
| **shared-sdk-python** | Shared | @materi/platform-ai | Python | 📋 Planned |
| **shared-sdk-go** | Shared | @materi/domain-api | Go | 📋 Planned |
| **shared-sdk-rust** | Shared | @materi/domain-relay | Rust | 📋 Planned |

**Legend:**
- ✅ Core: Production-ready, actively maintained
- 🚧 Beta: In development, not yet production
- 📋 Planned: Roadmap item, not started

### 4.2 Repository Configuration Standards

#### 4.2.1 Required Files (All Repositories)

Every repository MUST contain:

```
repo-root/
├── README.md                    # Overview, quickstart, links to docs
├── LICENSE                      # MIT or Apache 2.0
├── .gitignore                   # Language-specific ignores
├── .github/
│   ├── CODEOWNERS               # Team ownership mapping
│   ├── PULL_REQUEST_TEMPLATE.md # PR checklist and guidelines
│   ├── ISSUE_TEMPLATE/          # Issue templates per SRS document
│   │   ├── bug_report.yml
│   │   ├── feature_request.yml
│   │   ├── l1_strategic_spec.yml
│   │   └── l2_tactical_spec.yml
│   └── workflows/               # CI/CD pipelines
│       ├── ci.yml               # Build, test, lint
│       ├── security.yml         # CodeQL, Trivy, secret scanning
│       ├── deploy-dev.yml       # Deploy to development
│       ├── deploy-staging.yml   # Deploy to staging
│       └── deploy-prod.yml      # Deploy to production (manual approval)
├── CONTRIBUTING.md              # Contribution guidelines
├── CHANGELOG.md                 # Version history (Keep a Changelog format)
├── SECURITY.md                  # Security policy and reporting
├── docs/
│   ├── architecture/            # ADRs, system design docs
│   ├── api/                     # API documentation
│   ├── deployment/              # Deployment guides
│   └── troubleshooting/         # Runbooks, debugging guides
└── scripts/
    ├── setup.sh                 # Local development setup
    ├── test.sh                  # Run all tests
    └── build.sh                 # Build artifacts
```

#### 4.2.2 Repository Metadata (About Section)

All repositories MUST have:
- **Description**: One-line summary (<100 chars)
- **Website**: Link to documentation (products-atlas or docs/)
- **Topics**: Architectural segment + technology tags
- **Social Preview Image**: Materi logo + service name

**Example (domain-api):**
```yaml
description: "Materi API Gateway - Go/Fiber HTTP service for document management and AI integration"
website: "https://docs.materi.com/developer/domain/api/overview"
topics:
  - materi
  - domain
  - api-gateway
  - golang
  - fiber
  - microservices
  - event-driven
  - rest-api
social_preview: ".github/assets/domain-api-social-preview.png"
```

#### 4.2.3 Repository Settings Template

**General Settings:**
```yaml
features:
  wikis: false                    # Use products-atlas instead
  issues: true
  projects: true                  # Enable repository projects
  discussions: false              # Use organization discussions

merge_button:
  allow_merge_commit: false       # Enforce squash or rebase
  allow_squash_merge: true        # Preferred merge strategy
  allow_rebase_merge: true        # For linear history
  allow_auto_merge: true          # Enable auto-merge when checks pass
  delete_branch_on_merge: true    # Auto-cleanup merged branches

pull_requests:
  allow_update_branch: true       # Keep PRs up-to-date with base
  default_branch: main
```

**Branch Protection (main/production branches):**
```yaml
required_status_checks:
  strict: true                    # Require branches to be up-to-date
  contexts:
    - "CI / Build"
    - "CI / Test"
    - "CI / Lint"
    - "Security / CodeQL"
    - "Security / Trivy"

required_pull_request_reviews:
  required_approving_review_count: 2    # Minimum 2 approvals
  dismiss_stale_reviews: true           # Re-review after new commits
  require_code_owner_reviews: true      # CODEOWNERS must approve
  require_last_push_approval: true      # Fresh approval after last commit

required_signatures: false              # Optional: GPG signing
enforce_admins: true                    # No bypass, even for admins
require_linear_history: true            # No merge commits
allow_force_pushes: false
allow_deletions: false

required_conversation_resolution: true  # All comments resolved before merge
```

### 4.3 Repository Migration Strategy

**Phase 1: Segment Monorepos (Weeks 1-2)**

Consolidate existing code into segment monorepos:

```bash
# Domain Monorepo
domain-monorepo/
├── api/           # domain/api → here
├── relay/         # domain/relay → here
├── shield/        # domain/shield → here
├── printery/      # domain/printery → here
└── manuscript/    # domain/manuscript → here (or shared-proto)

# Platform Monorepo
platform-monorepo/
├── aria/          # platform/intelligence/aria → here
├── scribe/        # platform/scribe → here
└── integrations/  # platform/github → here

# Products Monorepo (already exists as products/app/canvas)
products-monorepo/
├── canvas/        # products/app/canvas → here
├── atlas/         # docs/ → here
└── specifications/ # products/__spec__ → here
```

**Phase 2: Standalone Repos (Weeks 3-4)**

Extract operations and infrastructure:

```bash
operations-folio/      # operations/folio → standalone
operations-shredder/   # operations/shredder → standalone
operations-nestr/      # lab/nestr → standalone
operations-traceo/     # lab/traceo → standalone
operations-gitops/     # operations/gitops → standalone
infra-terraform/       # operations/terraform → standalone
infra-kubernetes/      # operations/kubernetes → standalone
```

**Phase 3: Shared Libraries (Weeks 5-6)**

Create shared library repositories:

```bash
shared-manuscript/     # Protocol Buffer schemas (domain/manuscript)
shared-sdk-typescript/ # TypeScript SDK for API/WebSocket clients
shared-sdk-python/     # Python SDK for internal services
shared-sdk-go/         # Go SDK for internal services
shared-sdk-rust/       # Rust SDK for Relay clients
```

**Migration Tooling:**

Use **Nestr CLI** for automated repository extraction with history preservation:

```bash
# Extract domain/api to domain-api repo with git history
nestr extract \
  --source /Users/alexarno/materi \
  --path domain/api \
  --target git@github.com:materi-ai/domain-api.git \
  --preserve-history \
  --update-links

# Bulk migration script
nestr migrate \
  --manifest migration-manifest.yml \
  --dry-run
```

---

## 5. GitHub Teams Structure

### 5.1 Team Hierarchy

GitHub Teams organized by **architectural segment + cross-functional roles**:

```
materi (Organization)
├── @materi/engineering-leadership
│   ├── CTO
│   ├── VP Engineering
│   ├── Engineering Managers (4)
│   └── Principal Engineers (3)
│
├── @materi/domain-leads
│   ├── Domain Tech Lead
│   └── Domain Engineering Manager
│
├── @materi/domain-api
│   ├── API Team Lead
│   └── Backend Engineers (Go) (4-6)
│
├── @materi/domain-relay
│   ├── Relay Team Lead
│   └── Systems Engineers (Rust) (2-3)
│
├── @materi/domain-shield
│   ├── Shield Team Lead
│   └── Backend Engineers (Python) (2-3)
│
├── @materi/domain-events
│   ├── Event Systems Lead
│   └── Backend Engineers (Go/Proto) (2)
│
├── @materi/platform-leads
│   ├── Platform Tech Lead
│   └── Platform Engineering Manager
│
├── @materi/platform-ai
│   ├── AI Team Lead
│   ├── ML Engineers (3-4)
│   └── Backend Engineers (Python) (2)
│
├── @materi/platform-tooling
│   ├── Tooling Lead
│   └── Developer Experience Engineers (2)
│
├── @materi/platform-integrations
│   ├── Integrations Lead
│   └── Integration Engineers (2)
│
├── @materi/product-leads
│   ├── Product Tech Lead
│   └── Product Engineering Manager
│
├── @materi/frontend
│   ├── Frontend Tech Lead
│   ├── Senior Frontend Engineers (4-6)
│   └── Frontend Engineers (6-8)
│
├── @materi/product-management
│   ├── Head of Product
│   ├── Senior Product Managers (2)
│   └── Product Managers (3)
│
├── @materi/documentation
│   ├── Technical Writer
│   └── Documentation Contributors (rotational)
│
├── @materi/operations-leads
│   ├── Operations Tech Lead
│   └── Operations Manager
│
├── @materi/sre
│   ├── SRE Team Lead
│   └── Site Reliability Engineers (4-6)
│
├── @materi/qa
│   ├── QA Lead
│   ├── QA Engineers (3-4)
│   └── SDET Engineers (2)
│
├── @materi/devtools
│   ├── DevTools Lead
│   └── Developer Tooling Engineers (2)
│
├── @materi/security
│   ├── Security Lead
│   ├── Security Engineers (2-3)
│   └── Security Champions (rotational, 1 per team)
│
├── @materi/compliance
│   ├── Compliance Officer
│   └── Compliance Engineers (2)
│
└── @materi/contractors
    └── External contractors (temporary access)
```

**Total Teams**: 20 teams
**Estimated Headcount**: 60-80 engineers at full scale

### 5.2 Team Access Levels

| Team | Role | Repositories | Permissions |
|------|------|-------------|-------------|
| **@materi/engineering-leadership** | Admin | All repos | Admin access, can force merge (emergency only) |
| **@materi/domain-leads** | Maintain | domain-* | Write access, manage issues/PRs, merge with approval |
| **@materi/domain-api** | Write | domain-api | Push to branches, cannot merge to main without approval |
| **@materi/domain-relay** | Write | domain-relay | Push to branches, cannot merge to main without approval |
| **@materi/domain-shield** | Write | domain-shield | Push to branches, cannot merge to main without approval |
| **@materi/domain-events** | Maintain | shared-manuscript, domain-printery | Write + merge access (event schemas are critical) |
| **@materi/platform-leads** | Maintain | platform-* | Write access, manage issues/PRs, merge with approval |
| **@materi/platform-ai** | Write | platform-aria | Push to branches, cannot merge to main without approval |
| **@materi/platform-tooling** | Write | platform-scribe | Push to branches, cannot merge to main without approval |
| **@materi/platform-integrations** | Write | platform-integrations | Push to branches, cannot merge to main without approval |
| **@materi/product-leads** | Maintain | products-* | Write access, manage issues/PRs, merge with approval |
| **@materi/frontend** | Write | products-canvas | Push to branches, cannot merge to main without approval |
| **@materi/product-management** | Triage | products-specifications | Create issues, manage labels, read access |
| **@materi/documentation** | Write | products-atlas, all repos (docs/) | Write access to documentation files |
| **@materi/operations-leads** | Maintain | operations-*, infra-* | Write access, manage issues/PRs, merge with approval |
| **@materi/sre** | Write | operations-*, infra-* | Push to branches, cannot merge to main without approval |
| **@materi/qa** | Write | operations-shredder | Push to branches, manage test suites |
| **@materi/devtools** | Write | operations-nestr | Push to branches, manage tooling |
| **@materi/security** | Read | All repos | Read access, receive security alerts, triage vulnerabilities |
| **@materi/compliance** | Read | All repos | Read access, audit compliance posture |
| **@materi/contractors** | Read | Assigned repos only | Time-limited read or write access per project |

### 5.3 Team Membership Rules

**Automatic Team Assignment:**
- New engineers added to base team on day 1 (e.g., @materi/domain-api)
- Promoted to lead teams after 6 months + demonstrated leadership
- Security Champions program: 1 champion per team, rotates quarterly

**Team Sync Mechanisms:**
- **GitHub Teams ↔ Slack Channels**: Bidirectional sync (e.g., @materi/domain-api ↔ #team-domain-api)
- **GitHub Teams ↔ PagerDuty**: On-call rotations linked to team membership
- **GitHub Teams ↔ Okta/SAML**: SSO group mapping for automated provisioning

**Offboarding:**
- Automated removal from all teams within 1 hour of HR system update
- Contractor access expires automatically after defined end date

---

## 6. GitHub Projects

### 6.1 Organization-Level Projects

**6 GitHub Projects** for portfolio management:

#### 6.1.1 **Development Workflow Project**

**Name:** `Materi - Development Pipeline`
**Type:** Board
**Views:**
- **Kanban**: Backlog → In Progress → In Review → Ready for Staging → Done
- **Table**: All issues with custom fields (Segment, Priority, Estimate, Assignee)
- **Roadmap**: Timeline view by quarter

**Automation:**
- Auto-add issues from all repos with label `status:triage`
- Move to "In Progress" when PR is opened
- Move to "In Review" when PR enters review
- Move to "Done" when PR is merged

**Custom Fields:**
```yaml
- Segment: [Domain, Platform, Products, Operations]
- Priority: [P0-Critical, P1-High, P2-Medium, P3-Low]
- Estimate: [XS (1-2d), S (3-5d), M (1-2w), L (2-4w), XL (1-2m)]
- Type: [Feature, Bug, Tech Debt, Docs, Security]
- Requirement ID: Text (e.g., FR-AUTH-001)
- Target Release: [2025.Q1, 2025.Q2, 2025.Q3, 2025.Q4]
```

#### 6.1.2 **Staging Environment Project**

**Name:** `Materi - Staging Deployments`
**Type:** Board
**Views:**
- **Deployment Queue**: Ready → Deploying → Smoke Testing → Validated → Promoted to Prod
- **Service Matrix**: Grid view by service + deployment status
- **Release Calendar**: Timeline of staging deployments

**Automation:**
- Auto-add PRs merged to `develop` branch
- Trigger deployment workflows when moved to "Deploying"
- Auto-promote to production project after 24h soak time + approval

#### 6.1.3 **Production Releases Project**

**Name:** `Materi - Production Releases`
**Type:** Roadmap
**Views:**
- **Release Timeline**: Quarterly release schedule
- **Release Checklist**: Pre-release, deployment, post-release tasks
- **Rollback Dashboard**: Quick access to rollback procedures

**Automation:**
- Create release issues from template (pre-flight checklist)
- Require security review, QA signoff, SRE approval
- Auto-create post-mortems for failed deployments

#### 6.1.4 **Security & Compliance Project**

**Name:** `Materi - Security Posture`
**Type:** Table
**Views:**
- **Vulnerabilities**: Critical → High → Medium → Low
- **Dependency Updates**: Dependabot PRs across all repos
- **Security Incidents**: Active incidents + post-mortems

**Automation:**
- Auto-add security advisories from Dependabot
- Auto-add CodeQL findings above "High" severity
- Escalate P0/P1 vulnerabilities to @materi/security
- Track SLA: P0 <24h, P1 <7d, P2 <30d

**Custom Fields:**
```yaml
- CVE ID: Text
- CVSS Score: Number (0-10)
- Affected Services: Multi-select
- Remediation Status: [Identified, Triaged, In Progress, Patched, Verified]
- Remediation ETA: Date
```

#### 6.1.5 **Technical Debt Project**

**Name:** `Materi - Tech Debt Register`
**Type:** Table
**Views:**
- **Debt Backlog**: Ordered by impact × effort
- **Debt by Segment**: Grouped by Domain/Platform/Products/Operations
- **Quarterly Paydown**: Track tech debt reduction over time

**Automation:**
- Auto-add issues with label `type:tech-debt`
- Calculate debt score: `(Impact: 1-5) × (Effort: 1-5)`
- Reserve 20% sprint capacity for debt paydown (enforced via metrics)

**Custom Fields:**
```yaml
- Debt Type: [Architecture, Code Quality, Testing, Documentation, Performance]
- Impact: [1-Minimal, 2-Low, 3-Medium, 4-High, 5-Critical]
- Effort: [1-Trivial, 2-Small, 3-Medium, 4-Large, 5-Epic]
- Debt Score: Calculated (Impact × Effort)
- Introduced Date: Date
- Paydown Target: Quarter
```

#### 6.1.6 **Cross-Team Initiatives Project**

**Name:** `Materi - Strategic Initiatives`
**Type:** Roadmap
**Views:**
- **Initiative Timeline**: Multi-quarter roadmap
- **Dependency Graph**: Cross-team dependencies
- **Initiative Health**: On Track / At Risk / Blocked

**Automation:**
- Link L1 strategic specs to initiatives
- Track completion % across linked L2 tactical specs
- Alert leads when initiatives are blocked >5 days

**Custom Fields:**
```yaml
- Initiative ID: Text (L1-YYYY-QN-NAME)
- Owner: Person (@materi/engineering-leadership)
- Status: [Planning, In Progress, Blocked, Complete]
- Health: [Green, Yellow, Red]
- Cross-Team Dependencies: Multi-select teams
- OKRs: Text (link to company OKRs)
```

### 6.2 Repository-Level Projects

Each repository can create **service-specific projects** for:
- Sprint planning (2-week sprints)
- Feature development tracking
- Bug triage and prioritization

**Recommended Structure:**
```
domain-api/projects/
├── Sprint Planning (Board view)
├── API v2 Migration (Roadmap view)
└── Bug Triage (Table view)
```

---

## 7. GitHub Packages

### 7.1 Package Registry Strategy

**All build artifacts published to GitHub Packages:**

#### 7.1.1 Container Registry (GHCR)

**Registry**: `ghcr.io/materi-ai`

**Image Naming Convention:**
```
ghcr.io/materi-ai/<service-name>:<tag>
```

**Tags:**
- `latest` - Latest main branch build
- `develop` - Latest develop branch build
- `v1.2.3` - Semantic versioned releases
- `sha-abc1234` - Commit SHA for exact reproducibility
- `pr-123` - PR preview images

**Examples:**
```bash
# Production images
ghcr.io/materi-ai/domain-api:v1.5.2
ghcr.io/materi-ai/domain-relay:v2.0.0
ghcr.io/materi-ai/platform-aria:v1.3.0

# Development images
ghcr.io/materi-ai/domain-api:develop
ghcr.io/materi-ai/domain-api:sha-a3f2b19

# PR preview images
ghcr.io/materi-ai/domain-api:pr-456
```

**Image Metadata (Labels):**
```dockerfile
LABEL org.opencontainers.image.source="https://github.com/materi-ai/domain-api"
LABEL org.opencontainers.image.description="Materi API Gateway"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.version="1.5.2"
LABEL com.materi.segment="domain"
LABEL com.materi.service="api"
```

**Access Control:**
- **Public Images**: Base images, SDK images (for external developers)
- **Private Images**: Production service images (internal only)

#### 7.1.2 npm/pnpm Packages

**Registry**: `npm.pkg.github.com/@materi-ai`

**Packages:**
- `@materi-ai/sdk` - TypeScript SDK for API/WebSocket clients
- `@materi-ai/ui` - React component library (Canvas design system)
- `@materi-ai/proto` - TypeScript bindings for Protocol Buffers
- `@materi-ai/utils` - Shared utilities

**Publishing Workflow:**
```yaml
# .github/workflows/publish-npm.yml
name: Publish to npm
on:
  push:
    tags:
      - 'v*'
jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          registry-url: 'https://npm.pkg.github.com'
          scope: '@materi-ai'
      - run: pnpm install
      - run: pnpm build
      - run: pnpm publish --access public
        env:
          NODE_AUTH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

#### 7.1.3 Go Modules

**Registry**: GitHub Releases + Go Module Proxy

**Module Naming:**
```go
github.com/materi-ai/domain-api v1.5.2
github.com/materi-ai/shared-manuscript v2.1.0
```

**go.mod Example:**
```go
module github.com/materi-ai/domain-api

go 1.25.3

require (
    github.com/materi-ai/shared-manuscript v2.1.0
    github.com/gofiber/fiber/v2 v2.52.5
)
```

**Publishing:**
- Tag releases with semantic versioning: `git tag v1.5.2 && git push origin v1.5.2`
- GitHub automatically exposes as Go module via `https://github.com/materi-ai/domain-api`

#### 7.1.4 Rust Crates (crates.io + GitHub Packages)

**Registry**: crates.io (public) + GitHub Packages (private)

**Crates:**
- `materi-relay` - Relay service crate
- `materi-proto` - Rust bindings for Protocol Buffers

**Cargo.toml:**
```toml
[package]
name = "materi-relay"
version = "2.0.0"
edition = "2021"
repository = "https://github.com/materi-ai/domain-relay"
license = "MIT"

[dependencies]
materi-proto = { version = "2.1.0", registry = "github" }
```

**Publishing:**
```bash
cargo publish --registry crates-io
```

#### 7.1.5 Python Packages (PyPI + GitHub Packages)

**Registry**: PyPI (public SDKs) + GitHub Packages (internal libs)

**Packages:**
- `materi-sdk` - Python SDK for API clients
- `materi-proto` - Python bindings for Protocol Buffers

**pyproject.toml:**
```toml
[project]
name = "materi-sdk"
version = "1.3.0"
description = "Official Python SDK for Materi API"
repository = "https://github.com/materi-ai/shared-sdk-python"
```

**Publishing Workflow:**
```yaml
# .github/workflows/publish-pypi.yml
name: Publish to PyPI
on:
  push:
    tags:
      - 'v*'
jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install build twine
      - run: python -m build
      - run: twine upload dist/*
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
```

### 7.2 Package Lifecycle Management

**Retention Policy:**
- **Tagged Releases**: Keep forever (immutable)
- **PR Previews**: Delete after PR closed + 7 days
- **Nightly Builds**: Keep last 30 days
- **Untagged Images**: Delete after 90 days (except `latest`, `develop`)

**Automated Cleanup Workflow:**
```yaml
# .github/workflows/cleanup-packages.yml
name: Cleanup Old Packages
on:
  schedule:
    - cron: '0 2 * * 0'  # Weekly on Sunday 2am UTC
jobs:
  cleanup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/delete-package-versions@v4
        with:
          package-name: 'domain-api'
          package-type: 'container'
          min-versions-to-keep: 30
          delete-only-untagged-versions: true
```

---

## 8. Security & Access Control

### 8.1 Security Scanning Configuration

#### 8.1.1 CodeQL (SAST - Static Application Security Testing)

**Enabled for:** All repositories with Go, Rust, Python, TypeScript code

**Configuration (`.github/workflows/codeql.yml`):**
```yaml
name: CodeQL Security Analysis
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]
  schedule:
    - cron: '0 6 * * 1'  # Weekly scan on Monday 6am UTC

jobs:
  analyze:
    name: Analyze
    runs-on: ubuntu-latest
    permissions:
      actions: read
      contents: read
      security-events: write
    strategy:
      matrix:
        language: [go, python, typescript, rust]
    steps:
      - uses: actions/checkout@v4
      - uses: github/codeql-action/init@v3
        with:
          language: ${{ matrix.language }}
          queries: security-extended  # Use extended query suite
      - uses: github/codeql-action/autobuild@v3
      - uses: github/codeql-action/analyze@v3
        with:
          category: "/language:${{ matrix.language }}"
```

**Custom Queries:**
- SQL injection detection (Go, Python)
- Command injection (all languages)
- XSS vulnerabilities (TypeScript/React)
- Insecure deserialization (Python)
- Race conditions (Rust, Go)

**Severity Thresholds:**
- **Critical/High**: Block PR merge, require immediate fix
- **Medium**: Create issue, fix within 30 days
- **Low**: Create issue, fix during tech debt sprints

#### 8.1.2 Dependabot (Dependency Scanning)

**Enabled for:** All repositories

**Configuration (`.github/dependabot.yml`):**
```yaml
version: 2
updates:
  # Go modules
  - package-ecosystem: "gomod"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
    open-pull-requests-limit: 10
    reviewers:
      - "materi/domain-api"
    assignees:
      - "materi/security"
    labels:
      - "dependencies"
      - "security"
    commit-message:
      prefix: "chore(deps)"
      include: "scope"
    groups:
      production-dependencies:
        patterns:
          - "*"
        exclude-patterns:
          - "*-dev"
          - "*-test"

  # Rust crates
  - package-ecosystem: "cargo"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
    open-pull-requests-limit: 10
    reviewers:
      - "materi/domain-relay"

  # Python packages
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
    open-pull-requests-limit: 10
    reviewers:
      - "materi/platform-ai"

  # npm packages
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
    open-pull-requests-limit: 10
    reviewers:
      - "materi/frontend"
    versioning-strategy: increase

  # Docker base images
  - package-ecosystem: "docker"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
    reviewers:
      - "materi/sre"

  # GitHub Actions
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
    reviewers:
      - "materi/devtools"
```

**Auto-Merge Rules:**
- Patch version updates (1.2.3 → 1.2.4) auto-merge after CI passes
- Minor version updates (1.2.0 → 1.3.0) require manual review
- Major version updates (1.x → 2.x) require tech lead approval + migration plan

#### 8.1.3 Secret Scanning

**Enabled for:** All repositories (push protection ON)

**Scanned Secrets:**
- AWS credentials (access keys, secret keys)
- Database credentials (PostgreSQL, Redis connection strings)
- API keys (OpenAI, Anthropic, third-party services)
- JWT secrets, encryption keys
- OAuth client secrets
- Private keys (RSA, ECDSA)

**Custom Patterns:**
```yaml
# .github/secret_scanning.yml
patterns:
  - name: "Materi Internal API Key"
    regex: "materi_[a-zA-Z0-9]{32}"
    severity: high

  - name: "PostgreSQL Connection String"
    regex: "postgres://[^:]+:[^@]+@[^/]+"
    severity: critical

  - name: "Redis Connection String"
    regex: "redis://[^:]+:[^@]+@[^/]+"
    severity: high
```

**Alert Routing:**
- **Push Protection**: Block commits with secrets immediately
- **Detected Secrets**: Alert @materi/security + repository admins
- **Revocation**: Auto-rotate secrets via Vault API (if supported)

#### 8.1.4 Trivy (Container & IaC Scanning)

**Enabled for:** All repositories with Dockerfiles or Terraform

**Configuration (`.github/workflows/trivy.yml`):**
```yaml
name: Trivy Security Scan
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]
  schedule:
    - cron: '0 8 * * 1'  # Weekly on Monday 8am UTC

jobs:
  scan-docker:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build Docker Image
        run: docker build -t test-image .
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'test-image'
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'
      - name: Upload Trivy results to GitHub Security
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: 'trivy-results.sarif'

  scan-iac:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Trivy IaC scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'config'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-iac-results.sarif'
      - name: Upload Trivy IaC results
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: 'trivy-iac-results.sarif'
```

#### 8.1.5 SBOM Generation (Software Bill of Materials)

**Enabled for:** All production services

**Configuration (`.github/workflows/sbom.yml`):**
```yaml
name: Generate SBOM
on:
  push:
    tags:
      - 'v*'

jobs:
  sbom:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Generate SBOM (Syft)
        uses: anchore/sbom-action@v0
        with:
          image: ghcr.io/materi-ai/domain-api:${{ github.ref_name }}
          format: spdx-json
          output-file: sbom.spdx.json
      - name: Upload SBOM to GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          files: sbom.spdx.json
      - name: Sign SBOM (Cosign)
        run: |
          cosign sign-blob --key cosign.key sbom.spdx.json > sbom.spdx.json.sig
      - name: Upload Signature
        uses: softprops/action-gh-release@v1
        with:
          files: sbom.spdx.json.sig
```

**SBOM Use Cases:**
- Compliance audits (SOC2, ISO 27001)
- Supply chain security (know all dependencies)
- Vulnerability tracking (cross-reference CVEs with SBOM)
- License compliance (identify GPL/copyleft dependencies)

### 8.2 Access Control Matrix

#### 8.2.1 Repository Permissions

| Role | Base Permissions | Can... | Cannot... |
|------|------------------|--------|-----------|
| **Admin** | All access | Force push, change settings, delete repo, bypass protections | (None) |
| **Maintain** | Write + issues/PRs | Manage issues/PRs, push to protected branches (with approval), create releases | Modify security settings, delete repo |
| **Write** | Read + push | Push to non-protected branches, create PRs, assign reviewers | Merge to main, modify settings, delete branches |
| **Triage** | Read + issues | Label issues, assign issues, close stale issues | Push code, merge PRs, modify settings |
| **Read** | View only | Clone, view code, download releases | Push, create issues (unless public repo), comment |

#### 8.2.2 CODEOWNERS Configuration

**Per-Repository CODEOWNERS (`.github/CODEOWNERS`):**

**Example: domain-api repository**
```
# Global owners (fallback)
* @materi/engineering-leadership

# Service-wide ownership
* @materi/domain-api @materi/domain-leads

# Specific directory ownership
/internal/service/ @materi/domain-api
/internal/controller/ @materi/domain-api
/internal/middleware/ @materi/domain-api

# Database migrations (require extra scrutiny)
/migrations/ @materi/domain-api @materi/sre

# Security-sensitive code
/internal/auth/ @materi/domain-api @materi/security
/internal/crypto/ @materi/domain-api @materi/security

# Infrastructure
/Dockerfile @materi/domain-api @materi/sre
/docker-compose*.yml @materi/domain-api @materi/sre
/.github/workflows/ @materi/domain-api @materi/devtools

# Documentation (broad access)
/docs/ @materi/documentation
README.md @materi/documentation
CONTRIBUTING.md @materi/documentation

# Configuration
/config/ @materi/domain-api @materi/sre
/.env.example @materi/domain-api @materi/sre
```

**Example: shared-manuscript repository (event schemas)**
```
# Event schemas require multi-team review
* @materi/domain-events @materi/domain-leads @materi/platform-leads

# Proto definitions
/.msx/*.proto @materi/domain-events

# Generated code (auto-approved via CI)
/msx/ @materi/domain-events

# Schema versioning (critical)
/versions/ @materi/domain-events @materi/engineering-leadership
```

#### 8.2.3 Rulesets (Organization-Wide)

**Organization Ruleset: All Repositories**
```yaml
name: "Organization Security Baseline"
target: all_repos
enforcement: active

rules:
  # Require signed commits (optional, recommended)
  - type: required_signatures
    enabled: false

  # Require status checks
  - type: required_status_checks
    parameters:
      required_checks:
        - context: "CI / Build"
        - context: "CI / Test"
        - context: "Security / CodeQL"

  # Restrict deletions
  - type: deletion
    enforcement: deny

  # Restrict force pushes
  - type: non_fast_forward
    enforcement: deny

  # Require linear history
  - type: required_linear_history
    enabled: true

  # Restrict creation of specific branches
  - type: creation
    parameters:
      restricted_ref_names:
        - "refs/heads/master"  # Use 'main' instead
        - "refs/heads/hotfix-*"  # Hotfixes via dedicated process
```

**Production Branch Ruleset: main/production**
```yaml
name: "Production Branch Protection"
target:
  branches:
    - main
    - production
enforcement: active

rules:
  # Require pull request
  - type: pull_request
    parameters:
      required_approving_review_count: 2
      dismiss_stale_reviews: true
      require_code_owner_reviews: true
      require_last_push_approval: true

  # Require status checks
  - type: required_status_checks
    parameters:
      strict: true
      required_checks:
        - context: "CI / Build"
        - context: "CI / Test"
        - context: "CI / Lint"
        - context: "Security / CodeQL"
        - context: "Security / Trivy"
        - context: "E2E / Smoke Tests"

  # Require deployments to succeed
  - type: required_deployments
    parameters:
      required_deployment_environments:
        - staging

  # Block merge if conversations unresolved
  - type: required_conversation_resolution
    enabled: true
```

### 8.3 Compliance & Audit

#### 8.3.1 GitHub Audit Log

**Retention:** 180 days (GitHub Enterprise)

**Monitored Events:**
- Repository access changes (permissions granted/revoked)
- Team membership changes (added/removed)
- Branch protection rule changes
- Secret scanning alerts
- Security advisory publications
- Failed authentication attempts
- Admin actions (force pushes, protection bypasses)

**Audit Log Streaming:**
```yaml
# Export audit logs to SIEM (Splunk/Datadog)
# .github/audit-log-streaming.yml
destination:
  type: splunk
  endpoint: https://splunk.materi.com/services/collector
  token: ${{ secrets.SPLUNK_HEC_TOKEN }}

filters:
  - action: repo.access
  - action: team.add_member
  - action: team.remove_member
  - action: protected_branch.*
  - action: secret_scanning.*
  - action: security_advisory.*
```

#### 8.3.2 Compliance Reporting

**Automated Reports (Monthly):**
- Security posture: # vulnerabilities, remediation time, open advisories
- Access review: Team memberships, permission changes, dormant accounts
- Code quality: Test coverage, linting violations, tech debt score
- Deployment frequency: # deploys per service, success rate, rollback rate
- Incident summary: # incidents, MTTR, post-mortem completion rate

**Compliance Frameworks:**
- **SOC 2 Type II**: Evidence collection for security controls
- **ISO 27001**: Information security management
- **GDPR**: Data handling, right to erasure, audit trails
- **HIPAA** (if applicable): Protected health information handling

---

## 9. Branch Protection & Workflows

### 9.1 Branch Strategy

**Trunk-Based Development with Release Branches:**

```
main (production)
  ├─ release/v1.5.x (long-lived release branch)
  ├─ release/v1.4.x (long-lived release branch)
  └─ develop (integration branch)
       ├─ feature/FR-AUTH-001-oauth-sso (short-lived)
       ├─ feature/FR-DOC-023-templates (short-lived)
       ├─ bugfix/BUG-456-relay-crash (short-lived)
       └─ hotfix/CVE-2024-12345 (short-lived, merged to main directly)
```

**Branch Naming Convention:**
- `main` - Production-ready code
- `develop` - Integration branch for next release
- `release/v1.x.x` - Long-lived release branches for patch releases
- `feature/REQ-ID-short-description` - Feature branches
- `bugfix/BUG-ID-short-description` - Bug fix branches
- `hotfix/ISSUE-ID-short-description` - Emergency hotfix branches
- `chore/task-description` - Maintenance tasks (deps, refactoring)

### 9.2 Merge Strategies

| Branch | Target | Merge Strategy | Approval Required |
|--------|--------|----------------|-------------------|
| `feature/*` | `develop` | Squash merge | 1 approval (any team member) |
| `bugfix/*` | `develop` | Squash merge | 1 approval (any team member) |
| `develop` | `main` | Merge commit (preserve history) | 2 approvals (1 from leads + 1 from SRE) |
| `hotfix/*` | `main` | Squash merge | 2 approvals (1 from leads + 1 from SRE) |
| `release/*` | `main` | Merge commit | 2 approvals (1 from leads + 1 from SRE) |

**Rationale:**
- **Squash merge**: Keeps main history clean, one commit per feature/bug
- **Merge commit**: Preserves full history for releases and major integrations
- **No merge commits on feature branches**: Linear history enforced

### 9.3 CI/CD Workflow Templates

#### 9.3.1 Standard CI Workflow

**`.github/workflows/ci.yml`** (all repositories):

```yaml
name: CI
on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main, develop]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  build:
    name: Build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up language runtime
        # Language-specific setup (Go, Rust, Python, Node)
      - name: Cache dependencies
        uses: actions/cache@v4
        with:
          path: # Language-specific cache paths
          key: ${{ runner.os }}-deps-${{ hashFiles('**/go.sum') }}
      - name: Install dependencies
        run: make deps
      - name: Build
        run: make build
      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: build-artifacts
          path: ./dist

  test:
    name: Test
    runs-on: ubuntu-latest
    needs: build
    steps:
      - uses: actions/checkout@v4
      - name: Set up language runtime
      - name: Download build artifacts
        uses: actions/download-artifact@v4
      - name: Run unit tests
        run: make test
      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          token: ${{ secrets.CODECOV_TOKEN }}
          files: ./coverage.out
          flags: unittests

  lint:
    name: Lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up language runtime
      - name: Run linter
        run: make lint

  integration-test:
    name: Integration Test
    runs-on: ubuntu-latest
    needs: build
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: materi_test
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v4
      - name: Set up language runtime
      - name: Download build artifacts
        uses: actions/download-artifact@v4
      - name: Run integration tests
        run: make test-integration
        env:
          DATABASE_URL: postgres://postgres:postgres@localhost:5432/materi_test
          REDIS_URL: redis://localhost:6379
```

#### 9.3.2 Security Scanning Workflow

Already covered in Section 8.1.

#### 9.3.3 Deployment Workflow (GitOps)

**`.github/workflows/deploy-staging.yml`:**

```yaml
name: Deploy to Staging
on:
  push:
    branches: [develop]

jobs:
  deploy:
    name: Deploy to Staging Environment
    runs-on: ubuntu-latest
    environment:
      name: staging
      url: https://staging.materi.com
    steps:
      - uses: actions/checkout@v4

      - name: Build Docker Image
        run: |
          docker build -t ghcr.io/materi-ai/${{ github.event.repository.name }}:${{ github.sha }} .
          docker tag ghcr.io/materi-ai/${{ github.event.repository.name }}:${{ github.sha }} \
                     ghcr.io/materi-ai/${{ github.event.repository.name }}:develop

      - name: Push to GHCR
        run: |
          echo ${{ secrets.GITHUB_TOKEN }} | docker login ghcr.io -u ${{ github.actor }} --password-stdin
          docker push ghcr.io/materi-ai/${{ github.event.repository.name }}:${{ github.sha }}
          docker push ghcr.io/materi-ai/${{ github.event.repository.name }}:develop

      - name: Update GitOps Repository
        run: |
          git clone https://github.com/materi-ai/operations-gitops.git
          cd operations-gitops
          kustomize edit set image \
            ghcr.io/materi-ai/${{ github.event.repository.name }}=ghcr.io/materi-ai/${{ github.event.repository.name }}:${{ github.sha }}
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git commit -am "chore(staging): update ${{ github.event.repository.name }} to ${{ github.sha }}"
          git push

      - name: Wait for ArgoCD Sync
        run: |
          argocd app wait ${{ github.event.repository.name }}-staging --timeout 300

      - name: Run Smoke Tests
        run: |
          curl -f https://staging.materi.com/health || exit 1

      - name: Notify Slack
        if: always()
        uses: slackapi/slack-github-action@v1
        with:
          webhook-url: ${{ secrets.SLACK_WEBHOOK_STAGING }}
          payload: |
            {
              "text": "Staging Deployment: ${{ job.status }}",
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "*${{ github.event.repository.name }}* deployed to staging\nCommit: ${{ github.sha }}\nStatus: ${{ job.status }}"
                  }
                }
              ]
            }
```

**`.github/workflows/deploy-production.yml`:**

Similar to staging, but with:
- **Manual approval** required (GitHub Environments)
- **Blue-green deployment** strategy
- **Automated rollback** on health check failure
- **Extended smoke tests** (30 min soak time)

---

## 10. Settings & Policies

### 10.1 Organization-Wide Settings

#### 10.1.1 General Settings

```yaml
# Organization settings
name: materi-ai
display_name: Materi
description: "Enterprise-grade content management with real-time collaboration and AI enhancement"
website: https://materi.com
email: engineering@materi.com
location: Remote-first (Global)

billing_email: billing@materi.com
twitter_username: materi
blog: https://materi.com/blog

# Visibility
default_repository_permission: none  # No default access, use Teams
members_can_create_repositories: false  # Require admin approval
members_can_create_pages: false
members_can_fork_private_repositories: false
```

#### 10.1.2 Member Privileges

```yaml
member_privileges:
  base_permissions: read  # Default read access to public repos

  repository_creation:
    members_can_create_public: false
    members_can_create_private: false
    members_can_create_internal: true  # For experiments/prototypes

  repository_forking:
    members_can_fork_private: false  # Prevent data leaks

  pages:
    members_can_create_public: false
    members_can_create_private: false

  team_discussions:
    members_can_create_discussions: true

  project_visibility:
    members_can_change_project_visibility: false  # Admins only
```

#### 10.1.3 GitHub Actions Settings

```yaml
actions:
  enabled_repositories: all
  allowed_actions: selected

  allowed_actions_config:
    github_owned_allowed: true
    verified_allowed: true
    patterns_allowed:
      - "docker/*"
      - "aquasecurity/*"
      - "codecov/*"
      - "slackapi/*"
      - "aws-actions/*"

  default_workflow_permissions: read

  workflow_permissions:
    can_approve_pull_request_reviews: false

  runner_groups:
    - name: default
      visibility: all
      runners:
        - ubuntu-latest
        - ubuntu-22.04
        - macos-latest
        - windows-latest

    - name: high-memory
      visibility: selected
      selected_repositories:
        - domain-relay  # Rust compilation
        - platform-aria  # ML model loading
      runners:
        - self-hosted-16gb
        - self-hosted-32gb
```

#### 10.1.4 GitHub Packages Settings

```yaml
packages:
  package_deletion:
    admins_can_delete: true
    members_can_delete: false

  package_creation:
    members_can_create_public: false
    members_can_create_private: true

  visibility:
    default_visibility: private
    can_change_visibility: true  # Teams can make packages public

  access:
    inherit_from_repository: true  # Package access follows repo access
```

### 10.2 Repository Default Settings

**Applied to all new repositories:**

```yaml
repository_defaults:
  # Features
  has_issues: true
  has_projects: true
  has_wiki: false  # Use products-atlas instead
  has_discussions: false  # Use organization discussions

  # Merge options
  allow_squash_merge: true
  allow_merge_commit: false
  allow_rebase_merge: true
  allow_auto_merge: true
  delete_branch_on_merge: true

  # Updates
  allow_update_branch: true

  # Security
  vulnerability_alerts: true
  automated_security_fixes: true

  # Default branch
  default_branch: main

  # Topics (auto-applied based on repository name)
  topics:
    - materi
    - microservices
    # + segment-specific topics
```

### 10.3 Webhooks & Integrations

#### 10.3.1 Organization-Level Webhooks

**1. Slack Integration**
```yaml
webhook:
  url: https://hooks.slack.com/services/XXX/YYY/ZZZ
  content_type: application/json
  events:
    - push
    - pull_request
    - pull_request_review
    - issues
    - issue_comment
    - deployment
    - deployment_status
    - release
  active: true
```

**2. Linear Integration (GitHub → Linear Sync)**
```yaml
webhook:
  url: https://api.linear.app/webhooks/github/materi-ai
  content_type: application/json
  secret: ${{ secrets.LINEAR_WEBHOOK_SECRET }}
  events:
    - issues
    - issue_comment
    - pull_request
    - pull_request_review_comment
  active: true
```

**3. DataDog Monitoring**
```yaml
webhook:
  url: https://webhooks.datadoghq.com/github/materi-ai
  content_type: application/json
  secret: ${{ secrets.DATADOG_WEBHOOK_SECRET }}
  events:
    - deployment
    - deployment_status
    - workflow_run
    - workflow_job
  active: true
```

**4. PagerDuty Incidents**
```yaml
webhook:
  url: https://events.pagerduty.com/integration/XXX/enqueue
  content_type: application/json
  events:
    - deployment_status  # Failed deployments
    - workflow_run  # Failed CI runs on main
  active: true
  filters:
    - event: deployment_status
      conditions:
        - state: failure
          environment: production
    - event: workflow_run
      conditions:
        - conclusion: failure
          branch: main
```

#### 10.3.2 Third-Party Integrations

| Integration | Purpose | Access Level |
|-------------|---------|--------------|
| **Slack** | Notifications, PR reviews | Read repos, write comments |
| **Linear** | Issue sync (GitHub → Linear) | Read issues, write comments |
| **DataDog** | Monitoring, APM | Read repos, read deployments |
| **PagerDuty** | On-call, incident management | Read repos, read deployments |
| **Codecov** | Test coverage tracking | Read repos, write checks |
| **Snyk** | Vulnerability scanning | Read repos, write checks |
| **Renovate** | Dependency updates (alternative to Dependabot) | Read repos, create PRs |
| **SonarCloud** | Code quality analysis | Read repos, write checks |
| **Sentry** | Error tracking, release tracking | Read repos, read deployments |

---

## 11. Insights & Analytics

### 11.1 Organization-Level Insights

**GitHub Insights Dashboard Metrics:**

#### 11.1.1 Repository Metrics
- **Active Repositories**: # repos with commits in last 30 days
- **Code Churn**: Lines added/deleted per week
- **Repository Growth**: New repos created over time
- **Archive Rate**: # repos archived per quarter

#### 11.1.2 Code Quality Metrics
- **Test Coverage**: Average coverage across all repos (target: >80%)
- **Code Review Velocity**: Time from PR open → first review (target: <4h)
- **PR Merge Time**: Time from PR open → merge (target: <24h)
- **CI Success Rate**: % of CI runs passing (target: >95%)

#### 11.1.3 Security Metrics
- **Open Vulnerabilities**: By severity (Critical, High, Medium, Low)
- **Remediation Time**: Average time to fix vulnerabilities
  - P0: <24h
  - P1: <7d
  - P2: <30d
- **Secret Scanning Alerts**: Active alerts, false positive rate
- **Security Advisory Compliance**: % of advisories patched within SLA

#### 11.1.4 Deployment Metrics (DORA Metrics)
- **Deployment Frequency**: # deployments per week (per service)
- **Lead Time for Changes**: Commit → production (target: <24h)
- **Change Failure Rate**: % deployments causing incidents (target: <5%)
- **Mean Time to Recovery (MTTR)**: Time to restore service after failure (target: <1h)

#### 11.1.5 Team Metrics
- **Contributor Activity**: # active contributors per repo
- **Review Participation**: % of PRs reviewed by each team member
- **On-Call Load**: # incidents per on-call engineer
- **Burnout Indicators**: PRs created after hours, weekend commits

### 11.2 Custom Analytics Dashboards

**DataDog Dashboard: "GitHub Engineering Metrics"**

```yaml
dashboard:
  title: "Materi - GitHub Engineering Metrics"
  widgets:
    - type: timeseries
      title: "PR Cycle Time by Repository"
      query: avg:github.pr.cycle_time{repo:*} by {repo}

    - type: query_value
      title: "Open Critical Vulnerabilities"
      query: sum:github.security.vulnerabilities{severity:critical}

    - type: toplist
      title: "Top Contributors (Last 30 Days)"
      query: sum:github.commits.count{*} by {author}

    - type: heatmap
      title: "Deployment Activity (by Hour of Day)"
      query: count:github.deployments{*} by {hour}

    - type: servicemap
      title: "Dependency Graph"
      query: github.dependencies{*}
```

**Grafana Dashboard: "GitHub Operations"**

```yaml
dashboard:
  title: "Materi - GitHub Operations"
  panels:
    - title: "CI/CD Pipeline Health"
      type: stat
      targets:
        - expr: sum(rate(github_workflow_runs_total{conclusion="success"}[1h])) / sum(rate(github_workflow_runs_total[1h]))
      thresholds:
        - value: 0.95
          color: green
        - value: 0.90
          color: yellow
        - value: 0
          color: red

    - title: "Deployment Frequency (DORA)"
      type: graph
      targets:
        - expr: sum(rate(github_deployments_total{environment="production"}[1d])) by (service)

    - title: "Mean Time to Recovery"
      type: stat
      targets:
        - expr: avg(github_incident_duration_seconds) / 3600
      unit: hours
```

### 11.3 Automated Reporting

**Weekly Engineering Report (Automated via GitHub Actions):**

```yaml
# .github/workflows/weekly-report.yml
name: Weekly Engineering Report
on:
  schedule:
    - cron: '0 9 * * 1'  # Monday 9am UTC

jobs:
  generate-report:
    runs-on: ubuntu-latest
    steps:
      - name: Fetch GitHub Metrics
        uses: actions/github-script@v7
        with:
          script: |
            const repos = await github.rest.repos.listForOrg({ org: 'materi-ai' });
            const metrics = await Promise.all(repos.data.map(async (repo) => {
              const [commits, prs, issues] = await Promise.all([
                github.rest.repos.getCommitActivityStats({ owner: 'materi-ai', repo: repo.name }),
                github.rest.pulls.list({ owner: 'materi-ai', repo: repo.name, state: 'closed', per_page: 100 }),
                github.rest.issues.listForRepo({ owner: 'materi-ai', repo: repo.name, state: 'closed', per_page: 100 })
              ]);
              return { repo: repo.name, commits, prs, issues };
            }));
            // Generate report...

      - name: Send to Slack
        uses: slackapi/slack-github-action@v1
        with:
          webhook-url: ${{ secrets.SLACK_WEBHOOK_ENGINEERING }}
          payload: |
            {
              "text": "Weekly Engineering Report",
              "blocks": [
                {
                  "type": "header",
                  "text": { "type": "plain_text", "text": "📊 Materi Weekly Engineering Report" }
                },
                {
                  "type": "section",
                  "fields": [
                    { "type": "mrkdwn", "text": "*PRs Merged:* 127" },
                    { "type": "mrkdwn", "text": "*Commits:* 342" },
                    { "type": "mrkdwn", "text": "*Issues Closed:* 89" },
                    { "type": "mrkdwn", "text": "*Deployments:* 43" }
                  ]
                }
              ]
            }
```

---

## 12. Operational Procedures

### 12.1 Repository Lifecycle Management

#### 12.1.1 Creating a New Repository

**Process:**

1. **Request Approval** (via GitHub Issue in `operations-gitops` repo):
   ```yaml
   title: "[NEW REPO] <segment>-<service-name>"
   labels: [request:new-repo, segment:<segment>]
   assignees: @materi/engineering-leadership

   body: |
     ## Repository Information
     - **Name**: `<segment>-<service-name>`
     - **Segment**: [Domain/Platform/Products/Operations]
     - **Owner Team**: @materi/<team-name>
     - **Technology**: [Go/Rust/Python/TypeScript]
     - **Purpose**: <one-line description>

     ## Justification
     <Why this needs to be a separate repository>

     ## Dependencies
     - Depends on: <list of repos>
     - Consumed by: <list of repos>
   ```

2. **Automated Repository Provisioning** (via GitHub Actions):
   ```bash
   # Triggered when issue is labeled 'approved'
   gh repo create materi-ai/<segment>-<service-name> \
     --description "<description>" \
     --private \
     --template materi-ai/repository-template

   # Apply configuration
   gh api repos/materi-ai/<segment>-<service-name> \
     --method PATCH \
     --field has_issues=true \
     --field has_projects=true \
     --field has_wiki=false

   # Add to team
   gh api orgs/materi-ai/teams/<team-name>/repos/materi-ai/<segment>-<service-name> \
     --method PUT \
     --field permission=push

   # Apply branch protection
   gh api repos/materi-ai/<segment>-<service-name>/branches/main/protection \
     --method PUT \
     --input branch-protection.json

   # Enable security features
   gh api repos/materi-ai/<segment>-<service-name>/vulnerability-alerts \
     --method PUT
   gh api repos/materi-ai/<segment>-<service-name>/automated-security-fixes \
     --method PUT
   ```

3. **Initial Commit** (via repository template):
   - README.md with service overview
   - LICENSE (MIT)
   - .gitignore (language-specific)
   - .github/ directory (CODEOWNERS, issue templates, workflows)
   - Language-specific boilerplate (go.mod, Cargo.toml, pyproject.toml, package.json)

#### 12.1.2 Archiving a Repository

**Criteria for Archiving:**
- Service deprecated/decommissioned
- Merged into another repository
- No commits in 12+ months + no plans for future work

**Process:**
1. Create deprecation notice in README
2. Add `archived` topic to repository
3. Disable issues, PRs, and GitHub Actions
4. Archive repository (read-only mode)
5. Update cross-references in other repos (replace links, update docs)

**Unarchiving (if needed):**
- Requires VP Engineering approval
- Document justification in GitHub issue

### 12.2 Incident Response Procedures

#### 12.2.1 Security Incident Response

**Trigger:** Critical security vulnerability detected (CodeQL, Dependabot, Secret Scanning)

**Response Process:**

1. **Alert Routing** (automated):
   - Create incident in PagerDuty
   - Notify @materi/security in Slack
   - Create GitHub Security Advisory (draft)

2. **Triage** (within 1 hour):
   - Security team assesses severity (P0/P1/P2/P3)
   - Identify affected services
   - Determine exploitability

3. **Remediation** (SLA: P0 <24h, P1 <7d):
   - Create hotfix branch
   - Implement fix
   - Create PR with `security` label
   - Fast-track review (2 approvals required)

4. **Deployment**:
   - Merge to main
   - Deploy to production (bypass staging if P0)
   - Monitor for 30 minutes

5. **Post-Incident**:
   - Publish Security Advisory (GitHub)
   - Update SBOM for affected releases
   - Post-mortem (template in `operations-gitops/docs/post-mortem-template.md`)

#### 12.2.2 Production Outage Response

**Trigger:** Production service unavailable or degraded

**Response Process:**

1. **Detection** (automated monitoring):
   - Health check failures → PagerDuty alert
   - On-call SRE paged

2. **Incident Declaration**:
   - Create incident in PagerDuty
   - Notify #incidents Slack channel
   - Start incident timeline (Google Doc)

3. **Rollback Decision** (within 15 minutes):
   - Check recent deployments (via ArgoCD history)
   - If deployment caused issue: rollback immediately
   - If infrastructure issue: escalate to SRE

4. **Rollback Execution** (via GitOps):
   ```bash
   # Revert to previous image tag
   cd operations-gitops
   git revert HEAD
   git push

   # Wait for ArgoCD sync
   argocd app wait <service>-production --timeout 300
   ```

5. **Verification**:
   - Run smoke tests
   - Monitor error rates for 30 minutes
   - Confirm customer impact resolved

6. **Post-Incident**:
   - Update status page
   - Post-mortem within 48 hours
   - Identify action items (create GitHub issues)

### 12.3 Onboarding Procedures

#### 12.3.1 New Engineer Onboarding

**Day 1:**
- [ ] HR adds to Okta/SAML group → auto-provisioned to GitHub org
- [ ] Assigned to base team (e.g., @materi/domain-api)
- [ ] Added to Slack channels (auto-synced from GitHub Teams)
- [ ] Receives onboarding issue (from template):
  ```markdown
  ## Welcome to Materi! 🎉

  Complete these tasks to get up to speed:

  ### Access & Tools
  - [ ] Verify GitHub access (https://github.com/materi-ai)
  - [ ] Install local development tools (see repo READMEs)
  - [ ] Clone your team's primary repository
  - [ ] Run local development environment

  ### Documentation
  - [ ] Read architecture overview (products-atlas)
  - [ ] Read team-specific docs
  - [ ] Familiarize with CODEOWNERS

  ### First Contribution
  - [ ] Find a "good first issue" (label: good-first-issue)
  - [ ] Create feature branch
  - [ ] Open PR (pair with buddy)
  - [ ] Merge your first PR!

  ### Week 1 Goals
  - [ ] Attend team standup
  - [ ] Shadow on-call (if applicable)
  - [ ] Complete security training
  ```

**Week 1:**
- Pair programming with team lead
- Shadow on-call rotation
- First PR merged (good-first-issue)

**Month 1:**
- Independently ship feature
- On-call rotation (shadowed)
- Complete security training

#### 12.3.2 Contractor Onboarding

**Process:**
- Added to @materi/contractors team
- Time-limited access (auto-expires after contract end date)
- Restricted to specific repositories only
- No admin or maintain permissions
- All PRs require 2 approvals (1 must be full-time employee)

**Offboarding:**
- Access auto-revoked on contract end date
- Manual removal if early termination

---

## 13. Implementation Roadmap

### 13.1 Phase 1: Foundation (Weeks 1-4)

**Objectives:**
- Establish GitHub Teams structure
- Configure organization-wide settings
- Enable security scanning on all repositories

**Tasks:**

| Week | Task | Owner | Status |
|------|------|-------|--------|
| 1 | Create 20 GitHub Teams per Section 5.1 | @materi/engineering-leadership | 📋 Planned |
| 1 | Assign team members based on current roles | Engineering Managers | 📋 Planned |
| 1 | Configure organization settings (Section 10.1) | @materi/sre | 📋 Planned |
| 2 | Enable CodeQL on all repos | @materi/security | 📋 Planned |
| 2 | Configure Dependabot (Section 8.1.2) | @materi/security | 📋 Planned |
| 2 | Enable secret scanning + push protection | @materi/security | 📋 Planned |
| 3 | Apply branch protection rules (Section 9.1) | @materi/devtools | 📋 Planned |
| 3 | Create CODEOWNERS files for all repos | Team Leads | 📋 Planned |
| 4 | Set up organization rulesets (Section 8.2.3) | @materi/sre | 📋 Planned |
| 4 | Configure webhooks (Slack, Linear, DataDog) | @materi/sre | 📋 Planned |

**Success Criteria:**
- ✅ All 20 teams created with correct membership
- ✅ Security scanning enabled on 100% of repos
- ✅ Branch protection active on main/develop branches
- ✅ CODEOWNERS files in all repos

### 13.2 Phase 2: Repository Migration (Weeks 5-8)

**Objectives:**
- Migrate from monorepo to multi-repo structure
- Establish GitHub Packages for all artifacts
- Set up GitHub Projects

**Tasks:**

| Week | Task | Owner | Status |
|------|------|-------|--------|
| 5 | Create segment monorepos (domain, platform, products) | @materi/sre | 📋 Planned |
| 5 | Migrate Domain services (API, Relay, Shield) | @materi/domain-leads | 📋 Planned |
| 6 | Migrate Platform services (Aria, Scribe) | @materi/platform-leads | 📋 Planned |
| 6 | Migrate Product repos (Canvas, Atlas) | @materi/product-leads | 📋 Planned |
| 7 | Extract standalone repos (Folio, Shredder, Nestr) | @materi/operations-leads | 📋 Planned |
| 7 | Create shared library repos (manuscript, SDKs) | @materi/domain-events | 📋 Planned |
| 8 | Update all cross-references and links | @materi/documentation | 📋 Planned |
| 8 | Archive original monorepo (read-only) | @materi/sre | 📋 Planned |

**Success Criteria:**
- ✅ All services migrated with git history preserved
- ✅ CI/CD pipelines working in new repos
- ✅ No broken cross-references
- ✅ Original monorepo archived

### 13.3 Phase 3: GitHub Packages & Projects (Weeks 9-10)

**Objectives:**
- Publish all artifacts to GitHub Packages
- Configure 6 organization-level GitHub Projects
- Set up automated workflows

**Tasks:**

| Week | Task | Owner | Status |
|------|------|-------|--------|
| 9 | Configure GHCR for all services | @materi/sre | 📋 Planned |
| 9 | Publish container images to GHCR | Team Leads | 📋 Planned |
| 9 | Configure npm packages (@materi-ai scope) | @materi/frontend | 📋 Planned |
| 10 | Create 6 GitHub Projects (Section 6.1) | @materi/devtools | 📋 Planned |
| 10 | Configure project automation rules | @materi/devtools | 📋 Planned |
| 10 | Integrate Linear sync (GitHub → Linear) | @materi/product-management | 📋 Planned |

**Success Criteria:**
- ✅ All production images published to GHCR
- ✅ npm packages available for TypeScript SDK
- ✅ 6 GitHub Projects configured with automation
- ✅ Linear sync operational

### 13.4 Phase 4: Advanced Security & Compliance (Weeks 11-12)

**Objectives:**
- Implement SBOM generation
- Configure compliance reporting
- Set up audit log streaming

**Tasks:**

| Week | Task | Owner | Status |
|------|------|-------|--------|
| 11 | Generate SBOMs for all production releases | @materi/security | 📋 Planned |
| 11 | Configure Trivy scanning (Section 8.1.4) | @materi/security | 📋 Planned |
| 11 | Set up audit log streaming to Splunk | @materi/compliance | 📋 Planned |
| 12 | Configure monthly compliance reports | @materi/compliance | 📋 Planned |
| 12 | Document security incident response playbooks | @materi/security | 📋 Planned |
| 12 | Conduct tabletop security exercise | @materi/security | 📋 Planned |

**Success Criteria:**
- ✅ SBOM generated for all v1.x releases
- ✅ Trivy scanning integrated into CI
- ✅ Audit logs streaming to SIEM
- ✅ Monthly compliance report automation live

### 13.5 Phase 5: Analytics & Optimization (Weeks 13-14)

**Objectives:**
- Deploy custom analytics dashboards
- Optimize workflows based on metrics
- Train teams on new structure

**Tasks:**

| Week | Task | Owner | Status |
|------|------|-------|--------|
| 13 | Deploy DataDog dashboard (Section 11.2) | @materi/sre | 📋 Planned |
| 13 | Deploy Grafana dashboard (Section 11.2) | @materi/sre | 📋 Planned |
| 13 | Configure weekly engineering reports | @materi/devtools | 📋 Planned |
| 14 | Conduct team training sessions (all teams) | Engineering Leadership | 📋 Planned |
| 14 | Document runbooks and procedures | @materi/documentation | 📋 Planned |
| 14 | Retrospective and feedback collection | Engineering Leadership | 📋 Planned |

**Success Criteria:**
- ✅ Dashboards deployed and accessible
- ✅ Weekly reports generating automatically
- ✅ All teams trained on new workflows
- ✅ Runbooks documented in products-atlas

---

## 14. Appendices

### 14.1 Glossary

| Term | Definition |
|------|------------|
| **ADR** | Architecture Decision Record - document capturing architectural decisions |
| **ArgoCD** | GitOps continuous delivery tool for Kubernetes |
| **CODEOWNERS** | GitHub file defining code ownership and required reviewers |
| **DORA Metrics** | DevOps Research and Assessment metrics (deployment frequency, lead time, MTTR, change failure rate) |
| **GHCR** | GitHub Container Registry - Docker image registry |
| **GitOps** | Declarative infrastructure management using Git as source of truth |
| **L1 Spec** | Strategic specification (quarterly/annual initiatives) |
| **L2 Spec** | Tactical specification (sprint/quarter implementations) |
| **MTTR** | Mean Time To Recovery - average time to restore service after failure |
| **RBAC** | Role-Based Access Control |
| **SBOM** | Software Bill of Materials - inventory of software components |
| **SIEM** | Security Information and Event Management |
| **SLA** | Service Level Agreement |
| **SRE** | Site Reliability Engineering |

### 14.2 References

- [SRS: GitHub Issue Templates & Workflow Orchestration](./SRS-ISSUE-TEMPLATES-WORKFLOW-ORCHESTRATION.md)
- [Mintlify Documentation Structure](./MINTLIFY-STRUCTURE.md)
- [Ultimate LLM Prompt for Materi Deliverables](./ULTIMATE-LLM-PROMPT.md)
- [GitHub Branch Protection Best Practices](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [GitHub Security Best Practices](https://docs.github.com/en/code-security/getting-started/github-security-features)
- [DORA Metrics Guide](https://cloud.google.com/blog/products/devops-sre/using-the-four-keys-to-measure-your-devops-performance)

### 14.3 Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-22 | Technical Architecture Team | Initial release |

---

## Document Approval

**Prepared By:** Technical Architecture Team
**Reviewed By:**
- [ ] VP Engineering
- [ ] CTO
- [ ] Security Lead
- [ ] SRE Lead

**Approved By:**
- [ ] CTO (Final Sign-off)

**Approval Date:** _____________

---

**END OF DOCUMENT**
