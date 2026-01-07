# Ultimate LLM Prompt: Materi Documentation System

**Version:** 1.0.0
**Purpose:** Reproduce complete Materi documentation deliverables
**Target:** Any LLM (Claude, GPT-4, etc.)

---

## Prompt Template

```markdown
You are a technical documentation architect for Materi, an enterprise-grade real-time
collaborative document platform with event-driven microservices architecture.

# CONTEXT: Materi Architecture

Materi has 4 architectural segments:

1. **DOMAIN** (Core Microservices - Polyglot)
   - API: Go/Fiber - REST gateway, document CRUD, AI integration
   - Relay: Rust/Axum - Real-time WebSocket collaboration, Operational Transform
   - Shield: Python/Django - Auth, OAuth2/SAML, user management, RBAC
   - Manuscript: Protocol Buffers - Event schemas (50+ events across 8 domains)
   - Printery: Go - Event consumer hub, Redis Streams processing

2. **PLATFORM** (Cross-Cutting Services)
   - Aria: Python/FastAPI - AI content analysis, code safety, diagram analysis
   - Scribe: Python CLI - Documentation tooling
   - GitHub Integrations: Platform-level integrations

3. **PRODUCTS** (User-Facing)
   - Canvas: React/TypeScript monorepo (Turborepo + pnpm) - Frontend application
   - Atlas: MDX documentation hub - Technical documentation
   - __spec__: Requirements traceability (BR-*, FR-*, NFR-*, VER-*, IMPL-*)

4. **OPERATIONS** (Infrastructure)
   - Folio: Observability aggregation hub
   - Terraform: Infrastructure as Code
   - Kubernetes: Container orchestration
   - GitOps: ArgoCD deployment patterns
   - Monitoring: Prometheus, Grafana, Jaeger

**Event-Driven Communication:** All services communicate via Redis Streams with
Protocol Buffer event schemas defined in Manuscript.

**Tech Stack Summary:**
- Languages: Go, Rust, Python, TypeScript
- Databases: PostgreSQL 15+ (shared), Redis 7+ (streams, cache)
- APIs: REST (Fiber), WebSocket (Axum), GraphQL (planned)
- Frontend: React, Turborepo, pnpm, Storybook
- Observability: Prometheus, Grafana, Jaeger, OpenTelemetry
- Infrastructure: Kubernetes, Terraform, Docker

---

# TASK 1: System Requirement Specification for Issue Templates

Create a comprehensive SRS document covering:

## 1.1 GitHub Issue Templates (YAML format)
Design templates for each segment with progressive disclosure:

**Common Templates:**
- bug_report.yml (severity, segment, service, steps to reproduce)
- feature_request.yml (segment-aware, requirement linking)
- documentation.yml

**Segment-Specific Templates:**
- domain_service_enhancement.yml (event schema changes, breaking changes, performance targets)
- platform_ai_feature.yml (model requirements, graceful degradation, safety considerations)
- products_frontend_feature.yml (user stories, acceptance criteria, accessibility, design mockups)
- operations_infrastructure.yml (environment, urgency, rollback plan, monitoring)

**Requirements:**
- Dropdown validation for segments and services
- Required fields with clear descriptions
- Link to requirements (FR-XXX-YYY format)
- Auto-labeling triggers
- Template chooser configuration

## 1.2 GitHub PR Template
Include:
- Type of change checkboxes
- Architectural segment selection
- Related issues linking (Fixes #, Closes #, Related to #)
- Linked requirements (Implements: FR-XXX, Satisfies: BR-XXX, Verified by: VER-XXX)
- Testing checklist (unit, integration, e2e, coverage >80%)
- Documentation updates
- Pre-merge checklist
- Deployment notes and rollback plan

## 1.3 GitHub-to-Linear Sync Specification

**Requirements:**
- Unidirectional readonly sync (GitHub → Linear)
- Bidirectional comment sync only
- Real-time sync via GitHub Actions webhook
- Label mapping schema (50+ labels across segments, types, priorities, statuses)
- Conflict resolution: GitHub wins (source of truth)
- Retry policy: 3 attempts, exponential backoff
- Sync within 5 minutes
- Rate limiting: 60 req/min

**Label Categories:**
- Architectural Segments: segment:domain, segment:platform, segment:products, segment:operations
- Types: type:bug, type:feature, type:enhancement, type:performance, type:security
- Status: status:triage, status:in-progress, status:blocked, status:review, status:done
- Priority: priority:critical (P0), priority:high (P1), priority:medium (P2), priority:low (P3)
- Services: service:api, service:relay, service:shield, service:aria, etc.
- Components: component:canvas, component:atlas, etc.
- Operations: ops:infrastructure, ops:deployment, ops:monitoring

**GitHub Action Workflow (.github/workflows/linear-sync.yml):**
```yaml
on: [issues, issue_comment]
jobs:
  sync-to-linear:
    - Sync issue metadata
    - Map labels to Linear
    - Enable comment sync
    - Add Linear link to GitHub issue
```

## 1.4 L1/L2 Specification Templates

**L1 Strategic Specification (Quarterly/Annual):**
- Initiative ID format: L1-YYYY-QN-NAME
- Strategic themes (Scalability, UX, AI/ML, Enterprise, DevEx, Operations, Security, Cost)
- Vision statement (desired end state in 6-12 months)
- Business objectives (measurable KPIs)
- Affected segments (Domain, Platform, Products, Operations)
- L2 tactical breakdown (5-10 child initiatives)
- Success metrics with current/target values
- Risk assessment (Low/Medium/High) with mitigation strategies
- Cross-segment dependencies (Mermaid diagram)
- Resource requirements (teams, budget, timeline)
- Stakeholder sign-off (Product, Engineering, Architecture, Security, Finance)

**L2 Tactical Specification (Sprint/Quarter):**
- L2 ID format: L2-NNN-SERVICE-FEATURE
- Parent L1 initiative link
- Primary segment and service/component
- Tactical objective (specific, measurable)
- Scope (in-scope/out-of-scope)
- Technical approach (architecture decision, implementation steps, migration strategy)
- Implementation tasks (breakdown into GitHub issues with estimates)
- Acceptance criteria (definition of done checklist)
- Testing strategy (unit, integration, load, chaos)
- Timeline (4-12 weeks typical)
- Dependencies (blocks, blocked by, related)
- Risk level with mitigation
- Rollback plan (trigger conditions, steps, <1 hour recovery)
- Monitoring metrics (Grafana dashboards, Prometheus alerts)

**Example L1:** "Real-Time Collaboration at Scale" - Support 10K concurrent users with <50ms latency
**Example L2:** "Redis Streams Sharding" - Hash-based sharding, 3-node cluster, zero-downtime migration

## 1.5 Automated Workflows

**Required GitHub Actions:**
1. **auto-label.yml** - Detect segment, priority, type from issue body/title
2. **issue-routing.yml** - Route to teams based on segment labels (@materi/domain-team, etc.)
3. **dependency-tracker.yml** - Parse "Depends on #", "Blocks #", create dependency graph
4. **requirement-linking.yml** - Validate requirement links (FR-XXX format)

## 1.6 CODEOWNERS Configuration
Define reviewers per architectural segment:
```
/domain/api/ @materi/domain-team @materi/api-reviewers
/platform/aria/ @materi/platform-team @materi/ai-reviewers
/products/app/canvas/ @materi/product-team @materi/frontend-reviewers
/operations/terraform/ @materi/operations-team @materi/infra-reviewers
```

## 1.7 Implementation Roadmap
10-week phased rollout:
- Phase 1 (Weeks 1-2): Issue templates, labels, basic automation
- Phase 2 (Weeks 3-4): GitHub-Linear sync
- Phase 3 (Weeks 5-6): L1/L2 specifications
- Phase 4 (Weeks 7-8): Advanced workflows
- Phase 5 (Weeks 9-10): Optimization and training

**Output:** Create `docs/SRS-ISSUE-TEMPLATES-WORKFLOW-ORCHESTRATION.md` (18,000+ words,
production-ready specification with complete YAML examples)

---

# TASK 2: Mintlify Documentation Architecture

Create a comprehensive `docs/mint.json` skeleton that unifies all 4 architectural
segments across 5 audience types.

## 2.1 Documentation Tabs (5 Main Tabs)

**Tab 1: Customer Docs** (`/customer/*`)
- Audience: End users, content creators, team leads
- Focus: How to use Materi's features (no technical jargon)
- Groups (9 groups, ~60 pages):
  * Overview: What is Materi, key features, pricing, use cases
  * Getting Started: Sign-up, first document, workspace setup
  * Document Management: Creating, editing, organizing, sharing, version history, templates
  * Real-Time Collaboration: Presence, comments, mentions, conflict resolution, offline mode
  * AI Features: Content generation, summarization, enhancement, code analysis, diagram analysis, safety gates
  * Workspaces & Teams: Creating workspaces, managing members, roles/permissions, settings, billing
  * Integrations: GitHub, Slack, Google Drive, Notion, webhooks
  * Security & Privacy: Authentication, encryption, access controls, audit logs, GDPR
  * Support & Resources: Contact support, FAQ, troubleshooting, keyboard shortcuts, video tutorials

**Tab 2: Developer Guide** (`/developer/*`)
- Audience: Software engineers, architects, DevOps
- Focus: Build, extend, maintain Materi (all 4 architectural segments)
- Groups (10+ groups, ~120 pages):
  * Introduction: Overview, architecture, tech stack, getting started
  * Domain Services (5 services, 35+ pages):
    - API (Go/Fiber): Overview, architecture, setup, endpoints, auth, rate-limiting, testing, deployment
    - Relay (Rust/Axum): Overview, architecture, OT algorithm, WebSocket protocol, presence, testing, deployment
    - Shield (Python/Django): Overview, architecture, auth, authz, user management, OAuth/SAML, testing, deployment
    - Manuscript (Protocol Buffers): Overview, event schemas, custom options, code generation, versioning, MSX inspector
    - Printery (Go): Overview, architecture, consumer groups, handler registry, resilience patterns, deployment
  * Platform Services (2 services, 13+ pages):
    - Aria (Python/FastAPI): Overview, architecture, text/code/diagram analysis, enhancement, model integration, graceful degradation, testing, deployment
    - Intelligence: Scribe, GitHub integrations, analytics
  * Products (3 components, 18+ pages):
    - Canvas (React/TS): Overview, architecture, setup, component library, state management, API integration, real-time sync, testing, Storybook, deployment
    - Atlas: Overview, structure, contributing, MDX components
    - Specifications: Overview, traceability, requirement types, verification
  * Operations (4 areas, 20+ pages):
    - Infrastructure: Overview, Terraform, Kubernetes, networking, security
    - Deployment: Overview, GitOps, CI/CD, blue-green, rollback
    - Folio (Observability): Overview, metrics, logging, tracing, alerting, dashboards
    - Runbooks: Incident response, scaling, backup/restore, disaster recovery
  * Event-Driven Architecture (8 pages): Overview, event envelope, Redis Streams, publishing, consuming, idempotency, retry patterns, DLQ
  * Testing (7 pages): Overview, unit, integration, e2e, load, contract, chaos engineering
  * Contributing (6 pages): Overview, code standards, git workflow, PR process, issue templates, documentation

**Tab 3: API Reference** (`/api/*`)
- Audience: Integration developers, API consumers
- Focus: Complete API documentation with interactive playground
- Groups (6 groups, ~60 pages):
  * Introduction (7 pages): Overview, authentication (JWT/OAuth/SAML), rate limits, errors, pagination, versioning, webhooks
  * REST API (8 resource groups, 35+ endpoints):
    - Authentication: login, logout, refresh-token, oauth, saml
    - Users: get, update, delete, list, preferences
    - Documents: create, get, update, delete, list, versions, permissions
    - Workspaces: create, get, update, delete, list, members, roles
    - Collaboration: get-session, list-sessions, get-presence, comments, mentions
    - AI Features: analyze-text, analyze-code, analyze-diagram, generate-content, enhance-content, summarize
    - Files: upload, get, delete, list
    - Search: search-documents, search-users, search-workspaces
  * WebSocket API (7 pages): Overview, connection, authentication, operations, presence, events, error-handling
  * GraphQL API Beta (5 pages): Overview, schema, queries, mutations, subscriptions
  * SDKs (6 pages): Overview, JavaScript/TypeScript, Python, Go, Rust, Java
  * Event Schemas (8 pages): Overview, user-events, document-events, collaboration-events, workspace-events, aria-events, notification-events, audit-events

**Tab 4: Enterprise** (`/enterprise/*`)
- Audience: Enterprise IT, security teams, compliance officers
- Focus: Self-hosted deployment, security, compliance, high availability
- Groups (10 groups, ~70 pages):
  * Overview: What is enterprise, feature comparison, pricing, SLA
  * Deployment (3 deployment models, 21 pages):
    - Self-Hosted: Overview, requirements, Kubernetes, Docker Compose, configuration, upgrading, backup/restore
    - Cloud Dedicated: Overview, provisioning, VPC peering, custom domains, monitoring
    - Hybrid: Overview, architecture, data residency, compliance
  * Security & Compliance (11 pages): Overview, authentication, SSO/SAML, SCIM provisioning, encryption, network security, audit logs, data residency, compliance certifications (SOC2/GDPR/HIPAA/ISO27001), penetration testing, vulnerability disclosure
  * Administration (7 pages): Overview, user management, workspace management, license management, usage analytics, billing, support
  * Integration (8 pages): Overview, LDAP/AD, Okta, Azure AD, Google Workspace, custom SSO, API gateway, webhooks
  * Monitoring & Operations (7 pages): Overview, health checks, metrics, logging, alerting, performance tuning, capacity planning
  * High Availability (6 pages): Overview, architecture, failover, load balancing, disaster recovery, backup strategy
  * Scalability (6 pages): Overview, horizontal scaling, database scaling, cache strategy, CDN configuration, performance benchmarks
  * Migration (6 pages): Overview, from cloud, from competitors, data import, user migration, validation
  * Support (6 pages): Overview, support tiers, contact, SLA, escalation, training

**Tab 5: Internal** (`/internal/*`)
- Audience: Materi employees (engineering, product, operations, HR, legal)
- Focus: Internal processes, architecture decisions, team documentation
- Groups (9 groups, ~80 pages):
  * Overview: Welcome, team structure, communication, tools
  * Architecture (3 sub-groups, 25+ pages):
    - System Design: Overview, domain/platform/product/operations architecture, cross-segment integration, event-driven architecture, data models
    - ADRs (8+ decisions): Overview, microservices architecture, event-driven communication, operational transform, protocol buffers, Redis Streams, polyglot services, graceful degradation
    - Technical Specs: L1 strategic specs, L2 tactical specs, requirement traceability, verification matrix
  * Engineering (4 sub-groups, 22+ pages):
    - Development Workflow: Overview, issue templates, PR process, code review, testing strategy, deployment process
    - Code Standards: Overview, Go standards, Rust standards, Python standards, TypeScript standards, Proto standards
    - Service Ownership: Overview, domain team, platform team, product team, operations team, on-call rotation
    - Performance Engineering: Overview, benchmarking, profiling, optimization guide, SLO/SLI/SLA
  * Operations (4 sub-groups, 18+ pages):
    - Incident Management: Overview, severity levels, response process, communication, post-mortems, blameless culture
    - Release Management: Overview, versioning, release process, rollback procedures, change management
    - Capacity Planning: Overview, metrics, forecasting, scaling strategy
    - Cost Management: Overview, tracking, optimization, budgeting
  * Product (3 sub-groups, 13+ pages):
    - Product Strategy: Vision, roadmap, OKRs, competitive analysis
    - Product Development: Discovery, planning, execution, launch
    - User Research: Overview, user personas, interviews, surveys, analytics
  * Security (3 sub-groups, 15+ pages):
    - Security Practices: Overview, threat modeling, secure coding, code review security, dependency management, secrets management
    - Vulnerability Management: Overview, scanning, reporting, remediation, disclosure
    - Compliance: Overview, SOC2, GDPR, HIPAA, ISO27001
  * Data & Analytics (5 pages): Overview, metrics dashboard, user analytics, system analytics, business intelligence
  * HR & Culture (6 pages): Onboarding, engineering levels, performance reviews, compensation, benefits, remote work
  * Legal & Finance (6 pages): Contracts, intellectual property, privacy policy, terms of service, budget, expense policy

## 2.2 Mintlify Configuration Features

**Branding:**
- Primary color: #4A90E2 (Materi Blue)
- Light accent: #7B68EE (Purple)
- Dark: #2E5C8A
- Logo: dark.svg, light.svg
- Favicon: favicon.svg

**Navigation:**
- Topbar links: Customer Portal, Enterprise, Status
- Topbar CTA: "Get Started" → https://app.materi.com/signup
- Anchors: Community (Discord), GitHub, Blog, Changelog
- 5 main tabs with nested groups (up to 3 levels deep)

**API Integration:**
- Base URL: https://api.materi.com/v1
- Auth method: bearer (JWT)
- Playground mode: show (interactive API testing)
- OpenAPI specs: rest-api.yaml, websocket-api.yaml, graphql-schema.graphql

**Analytics:**
- PostHog: API key integration
- Google Analytics 4: Measurement ID
- Mixpanel: Project token

**Features:**
- Feedback: suggest-edit (true), raise-issue (true), thumbs-rating (true)
- Search: Global search with prompt "Search Materi documentation..."
- Versioning: v1 (Current), v2 (Beta)
- Redirects: /docs → /introduction, /getting-started → /quickstart

**SEO Metadata:**
- og:site_name: "Materi Documentation"
- og:type: "website"
- og:title: "Materi - Real-Time Collaborative Document Platform"
- og:description: "Enterprise-grade collaborative document management with AI enhancement"
- og:image: /images/og-image.png
- twitter:card: summary_large_image

**Social Links:**
- Twitter: @materi
- LinkedIn: /company/materi
- GitHub: /materi-ai
- Discord: /materi

## 2.3 File Structure (200+ MDX files)

Create complete directory skeleton:
```
docs/
├── mint.json
├── introduction.mdx
├── quickstart.mdx
├── architecture-overview.mdx
├── concepts.mdx
├── customer/              # 60+ files
├── developer/             # 120+ files
│   ├── domain/api/       # 8 files
│   ├── domain/relay/     # 7 files
│   ├── domain/shield/    # 8 files
│   ├── domain/manuscript/# 6 files
│   ├── domain/printery/  # 6 files
│   ├── platform/aria/    # 10 files
│   ├── products/canvas/  # 10 files
│   ├── operations/folio/ # 6 files
│   └── ...
├── api/                   # 60+ files
│   ├── rest/             # 35+ endpoint files
│   ├── websocket/        # 7 files
│   ├── graphql/          # 5 files
│   ├── sdks/             # 6 files
│   └── events/           # 8 files
├── enterprise/            # 70+ files
└── internal/              # 80+ files
```

**Output:** Create `docs/mint.json` (complete Mintlify config, ~500 lines) and
`docs/MINTLIFY-STRUCTURE.md` (comprehensive guide, 40+ pages)

---

# TASK 3: Documentation Integration

Ensure seamless integration between SRS and Mintlify:

## 3.1 Cross-References
- Link GitHub issue templates to developer guide pages
- Reference L1/L2 specs in internal documentation
- Connect API reference to developer architecture docs
- Map requirements to feature documentation

## 3.2 Traceability Matrix
Show how architectural domains flow through documentation:
- Domain Services → Developer Guide + API Reference + Enterprise HA
- Platform Services → Customer AI Features + Developer Platform + API AI Endpoints
- Products → Customer Docs + Developer Frontend Guide + Enterprise Deployment
- Operations → Developer Operations + Enterprise Infrastructure + Internal SRE

## 3.3 Access Control
- Customer/Developer/API Reference/Enterprise: Public
- Internal: Private (auth required, SSO integration)

---

# OUTPUT REQUIREMENTS

Generate 3 production-ready files:

1. **docs/SRS-ISSUE-TEMPLATES-WORKFLOW-ORCHESTRATION.md**
   - 18,000+ words
   - 10 main sections with subsections
   - Complete YAML examples for all templates
   - GitHub Actions workflows (4+ workflows)
   - Label taxonomy (50+ labels)
   - CODEOWNERS configuration
   - 10-week implementation roadmap
   - Appendices with examples

2. **docs/mint.json**
   - ~500 lines
   - 5 main tabs with nested navigation
   - 200+ page references
   - Complete branding and configuration
   - OpenAPI integration
   - Analytics setup
   - SEO optimization

3. **docs/MINTLIFY-STRUCTURE.md**
   - 40+ pages
   - Navigation hierarchy explanation
   - File organization guide (200+ files)
   - MDX best practices
   - Deployment instructions
   - Maintenance guidelines
   - Cross-domain integration matrix

---

# QUALITY CRITERIA

- **Comprehensive:** Cover all 4 architectural segments equally
- **Production-Ready:** YAML validates, JSON parses, real-world examples
- **Consistent:** Naming conventions, formatting, structure alignment
- **Traceable:** Clear links between requirements, issues, PRs, documentation
- **Audience-Aware:** Different content for customers vs developers vs enterprise
- **Actionable:** Include specific commands, examples, step-by-step instructions
- **Maintainable:** Modular structure, clear ownership, versioning support

---

# EXECUTION INSTRUCTIONS

1. Read and understand Materi's 4 architectural segments
2. Generate SRS document first (establishes GitHub workflow foundation)
3. Generate Mintlify config second (documentation structure)
4. Generate Mintlify guide third (implementation instructions)
5. Ensure cross-references between all three documents
6. Validate YAML/JSON syntax
7. Include real-world examples from Materi context

Execute now.
```

---

## Compression Analysis

**Original Session Requirements:**
- Multiple back-and-forth clarifications
- Incremental context building
- ~100,000 tokens of conversation

**Compressed Prompt:**
- ~4,500 words
- Single-shot execution
- All context embedded
- Zero ambiguity

**Compression Ratio:** ~95% reduction while maintaining 100% requirement fidelity

---

## Usage Instructions

### For Claude/GPT-4/Gemini:
```
Copy the entire prompt template section (between the markdown code blocks)
and paste directly into a new conversation.
```

### For Custom LLM:
```python
from openai import OpenAI

client = OpenAI(api_key="your-key")

with open("ULTIMATE-LLM-PROMPT.md", "r") as f:
    prompt = f.read()
    # Extract content between ```markdown and ```

response = client.chat.completions.create(
    model="gpt-4-turbo-preview",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.7,
    max_tokens=16000
)
```

### For Anthropic Claude API:
```python
import anthropic

client = anthropic.Anthropic(api_key="your-key")

with open("ULTIMATE-LLM-PROMPT.md", "r") as f:
    prompt = f.read()

message = client.messages.create(
    model="claude-opus-4-5",
    max_tokens=200000,
    messages=[{"role": "user", "content": prompt}]
)
```

---

## Validation Checklist

After LLM execution, verify:

- [ ] 3 files generated
- [ ] SRS document: 18,000+ words, 10 sections, YAML examples
- [ ] mint.json: Valid JSON, 5 tabs, 200+ page refs
- [ ] MINTLIFY-STRUCTURE.md: 40+ pages, file tree, deployment guide
- [ ] All 4 architectural segments covered equally
- [ ] Cross-references between documents present
- [ ] GitHub Actions workflows syntactically valid
- [ ] Label taxonomy includes 50+ labels
- [ ] L1/L2 specification templates complete
- [ ] API reference structure matches OpenAPI spec

---

## Optimization Notes

### What Makes This "Ultimate":

1. **Zero Ambiguity:** Every requirement explicit, no clarification needed
2. **Complete Context:** All 4 architectural segments defined upfront
3. **Structured Output:** Exact file structure, word counts, section breakdown
4. **Validation Criteria:** Quality checklist prevents incomplete responses
5. **Technology Specificity:** Stack, versions, tool names explicit
6. **Example-Driven:** References real Materi components (not generic)
7. **Execution Order:** Step-by-step generation sequence
8. **Cross-Reference Map:** How documents integrate specified
9. **Production-Ready:** Real YAML/JSON syntax, not pseudocode
10. **Audience Segmentation:** 5 distinct user types with clear needs

### Prompt Engineering Techniques Used:

- **Role Definition:** "You are a technical documentation architect"
- **Context Frontloading:** Architecture explained before tasks
- **Explicit Constraints:** Word counts, section counts, file counts
- **Output Formatting:** Markdown structure, YAML examples, JSON schema
- **Validation Requirements:** Quality criteria and checklist
- **Execution Sequence:** Numbered steps for systematic generation
- **Meta-Instructions:** "Execute now" trigger
- **Example Anchoring:** Real component names (Aria, Relay, Shield)
- **Hierarchical Organization:** Tasks → Subtasks → Requirements
- **Success Metrics:** Compression ratio, requirement fidelity

---

## Version History

- **v1.0.0** (2025-12-22): Initial release - Ultimate compressed prompt

---

**End of Document**
