# SDD Migration Manifest

> **Purpose**: Authoritative mapping between legacy v1 blueprints (`.atlas/.spec/__blueprints__/`) and Atlas docs targets.
>
> **Generated**: 2026-01-07 (TASKSET 2 Complete)
> **Total Legacy Documents**: 75 MDX files
> **Atlas Target Files**: 475 pages (114 internal)

## Migration Status Legend

| Status         | Meaning                                      |
| -------------- | -------------------------------------------- |
| 🔴 **STUB**    | Target is a stub file needing full content   |
| 🟡 **PARTIAL** | Target has some content but needs enrichment |
| 🟢 **EXISTS**  | Target already has substantive content       |
| ⬛ **NEW**     | No target exists; create new page            |

## Refresh Classification

| Refresh Type    | Description                                          |
| --------------- | ---------------------------------------------------- |
| **DIRECT PORT** | Content can be migrated with minimal changes         |
| **REFRESH**     | Content needs updating to match current architecture |
| **SUBSTANTIAL** | Content requires major rewrite with new information  |
| **SKIP**        | Legacy content superseded or no longer relevant      |

---

## L1-Strategic Documents (7 Sources)

Strategic documents define business direction, vision, and governance.

| Source File             | Title                            | Lines | Target Path                                               | Status    | Priority       | Refresh Type |
| ----------------------- | -------------------------------- | ----- | --------------------------------------------------------- | --------- | -------------- | ------------ |
| `intro.mdx`             | Platform Introduction            | 1534  | `introduction.mdx`                                        | 🟢 EXISTS | Low (done)     | SKIP         |
| `sdd:cls:hierarchy.mdx` | Documentation Taxonomy Hierarchy | 260   | `internal/architecture/specs/l1-strategic-specs.md`       | 🟢 EXISTS | ✅ DONE        | DIRECT PORT  |
| `sdd:cls:index.mdx`     | Documentation Index              | 301   | `internal/architecture/specs/taxonomy-index.md`           | 🟢 EXISTS | ✅ DONE        | DIRECT PORT  |
| `sdd:sys:brs.mdx`       | Business Requirements Spec       | 902   | `internal/architecture/specs/l1-strategic-specs.md`       | 🟢 EXISTS | ✅ DONE        | REFRESH      |
| `sdd:sys:cod.mdx`       | Concept of Operations            | 952   | `internal/architecture/specs/concept-of-operations.md`    | 🟢 EXISTS | Low (complete) | SKIP         |
| `sdd:sys:psd.mdx`       | Product Strategy Document        | 652   | `internal/product/strategy/vision.md`                     | 🟢 EXISTS | ✅ DONE        | REFRESH      |
| `sdd:sys:tsd.mdx`       | Technology Strategy              | 719   | `internal/architecture/specs/technology-strategy.md`      | 🟢 EXISTS | Low (complete) | SKIP         |

**Verification Notes (TASKSET 2 Complete):**
- ✅ `concept-of-operations.md` contains 952 lines of substantive content (pre-existing)
- ✅ `technology-strategy.md` contains 719 lines of substantive content (pre-existing)
- ✅ `l1-strategic-specs.md` now contains 388 lines (BRS + hierarchy content migrated)
- ✅ `vision.md` now contains 486 lines (Product Strategy migrated)
- ✅ `taxonomy-index.md` created with 307 lines (Documentation Index migrated)

---

## L2-System Documents (11 Sources)

System documents translate strategic vision into architecture and design.

| Source File           | Title                         | Lines | Target Path                                                        | Status     | Priority | Refresh Type |
| --------------------- | ----------------------------- | ----- | ------------------------------------------------------------------ | ---------- | -------- | ------------ |
| `sdd:sys:sad.mdx`     | System Architecture Document  | 1132  | `internal/architecture/system-design/overview.md`                  | 🟡 PARTIAL | HIGH     | REFRESH      |
| `sdd:sys:pad.mdx`     | Platform Architecture         | 1408  | `internal/architecture/system-design/platform-services.md`         | 🔴 STUB    | HIGH     | DIRECT PORT  |
| `sdd:sys:dad.mdx`     | Data Architecture Document    | 980   | `internal/architecture/system-design/data-models.md`               | 🟢 EXISTS  | Medium   | SKIP         |
| `sdd:sec:sad.mdx`     | Security Architecture         | 1517  | `internal/security/practices/overview.md`                          | 🔴 STUB    | HIGH     | DIRECT PORT  |
| `sdd:sys:nfr.mdx`     | Non-Functional Requirements   | 1046  | `internal/engineering/performance/slo-sli-sla.md`                  | 🔴 STUB    | HIGH     | REFRESH      |
| `sdd:sys:drp.mdx`     | Disaster Recovery Plan        | 548   | `developer/operations/runbooks/disaster-recovery.md`               | 🔴 STUB    | HIGH     | DIRECT PORT  |
| `sdd:sys:rcm.mdx`     | Requirements Continuity Model | 955   | `internal/architecture/specs/requirement-traceability.md`          | 🔴 STUB    | HIGH     | DIRECT PORT  |
| `sdd:sys:cid.mdx`     | Cloud Infrastructure Document | 579   | `developer/operations/infrastructure/overview.md`                  | 🔴 STUB    | HIGH     | REFRESH      |
| `sdd:sys:tax.mdx`     | System Taxonomy               | 723   | `internal/architecture/specs/l2-tactical-specs.md`                 | 🔴 STUB    | HIGH     | DIRECT PORT  |
| `sdd:sys:vif.mdx`     | Vendor Intelligence Framework | 861   | `internal/operations/cost/overview.md`                             | 🔴 STUB    | Medium   | REFRESH      |
| `sdd:integration.mdx` | Integration Architecture      | 855   | `internal/architecture/system-design/cross-segment-integration.md` | 🔴 STUB    | HIGH     | DIRECT PORT  |

**Verification Notes:**
- ✅ `data-models.md` contains 392 lines of substantive content (verified - includes SQL schemas)
- 🟡 `overview.md` (system-design) has 165 lines - PARTIAL, needs enrichment from SAD

---

## L3-Technical Documents (13 Sources + 7 Additional)

Technical documents specify implementation details and development standards.

### Core Technical Documents

| Source File                       | Title                            | Lines | Target Path                                          | Status     | Priority | Refresh Type |
| --------------------------------- | -------------------------------- | ----- | ---------------------------------------------------- | ---------- | -------- | ------------ |
| `dev:backend-architecture.mdx`    | Backend Architecture             | 1140  | `developer/introduction/architecture.md`             | 🔴 STUB    | HIGH     | DIRECT PORT  |
| `dev:frontend-architecture.mdx`   | Frontend Architecture            | 1478  | `developer/products/canvas/architecture.md`          | 🔴 STUB    | HIGH     | DIRECT PORT  |
| `dev:engine-architecture.mdx`     | Collaboration Engine (Relay)     | 1241  | `developer/domain/relay/architecture.md`             | 🔴 STUB    | HIGH     | DIRECT PORT  |
| `dev:ai-provider-integration.mdx` | AI Provider Integration          | 1049  | `developer/platform/aria/model-integration.md`       | 🔴 STUB    | HIGH     | DIRECT PORT  |
| `sdd:observability.mdx`           | Monitoring & Observability       | 817   | `developer/operations/folio/overview.md`             | 🔴 STUB    | HIGH     | DIRECT PORT  |
| `sdd:vvp.mdx`                     | Verification & Validation Plan   | 2545  | `internal/architecture/specs/verification-matrix.md` | 🔴 STUB    | HIGH     | SUBSTANTIAL  |
| `sdd:sys:vtm.mdx`                 | Verification Traceability Matrix | 706   | `internal/architecture/specs/verification-matrix.md` | 🔴 STUB    | HIGH     | SUBSTANTIAL  |
| `sdd:sys:qas.mdx`                 | Quality Assurance Strategy       | 161   | `developer/testing/overview.md`                      | 🟡 PARTIAL | Medium   | REFRESH      |
| `sdd:sys:sts.mdx`                 | Systems Thinking Standard        | 728   | `internal/engineering/workflow/overview.md`          | 🔴 STUB    | Medium   | REFRESH      |
| `sdd:sys:tas.mdx`                 | Taxonomy Automation Strategy     | 746   | `internal/architecture/specs/` (concepts)            | ⬛ NEW     | Low      | DIRECT PORT  |
| `sdd:sys:frm.mdx`                 | Fault Resilience Matrix          | 1193  | `internal/engineering/performance/overview.md`       | 🔴 STUB    | HIGH     | DIRECT PORT  |
| `sdd:sw:git.mdx`                  | Git Workflow Reference           | 593   | `developer/contributing/git-workflow.mdx`            | 🟡 PARTIAL | HIGH     | REFRESH      |
| `sdd:sw:env.mdx`                  | Development Environment          | —     | `developer/introduction/getting-started.md`          | 🔴 STUB    | HIGH     | DIRECT PORT  |
| `sdd:configuration.mdx`           | Configuration Management         | 185   | `developer/operations/infrastructure/overview.md`    | 🔴 STUB    | Medium   | REFRESH      |

### Additional Technical Documents (Discovered in Inventory)

| Source File                   | Title                           | Lines | Target Path                                | Status  | Priority | Refresh Type |
| ----------------------------- | ------------------------------- | ----- | ------------------------------------------ | ------- | -------- | ------------ |
| `sdd:debt.mdx`                | Technical Debt Framework        | 250   | `internal/engineering/workflow/overview.md`| 🔴 STUB | Medium   | DIRECT PORT  |
| `sdd:reliability.mdx`         | Reliability Architecture        | 970   | `internal/engineering/performance/overview.md` | 🔴 STUB | HIGH  | DIRECT PORT  |
| `sdd:knowledge.mdx`           | Knowledge Management            | 823   | `internal/overview/tools.md`               | 🔴 STUB | Low      | DIRECT PORT  |
| `sdd:guidelines.mdx`          | Development Guidelines          | —     | `developer/contributing/code-standards.mdx`| 🔴 STUB | Medium   | REFRESH      |
| `sdd:optimisation.mdx`        | Performance Optimization        | —     | `internal/engineering/performance/optimization-guide.md` | 🔴 STUB | Medium | DIRECT PORT |
| `dev:docs-as-code.mdx`        | Docs-as-Code Implementation     | 748   | `developer/products/atlas/contributing.md` | 🔴 STUB | Medium   | DIRECT PORT  |
| `sdd:sec:sis.mdx`             | Security Implementation Spec    | —     | `internal/security/practices/overview.md`  | 🔴 STUB | HIGH     | DIRECT PORT  |

**Verification Notes:**
- 🟡 `git-workflow.mdx` has 39 lines - PARTIAL, needs enrichment from legacy content
- `verification-matrix.md` should combine VVP + VTM content

---

## L4-Operational Documents (6 Sources)

Operational documents cover day-to-day operations and maintenance.

| Source File                 | Title                   | Lines | Target Path                                          | Status  | Priority | Refresh Type |
| --------------------------- | ----------------------- | ----- | ---------------------------------------------------- | ------- | -------- | ------------ |
| `sdd:sw:debug:api.mdx`      | API Debugging Guide     | —     | `developer/testing/integration-tests.md`             | 🔴 STUB | Medium   | DIRECT PORT  |
| `sdd:sw:debug:devops.mdx`   | DevOps Debugging        | —     | `developer/operations/runbooks/incident-response.md` | 🔴 STUB | Medium   | DIRECT PORT  |
| `sdd:sw:debug:front.mdx`    | Frontend Debugging      | —     | `developer/testing/e2e-tests.md`                     | 🔴 STUB | Medium   | DIRECT PORT  |
| `sdd:ops:vc-heat-suite.mdx` | Operations Heat Suite   | —     | `developer/operations/folio/alerting.md`             | 🔴 STUB | Medium   | DIRECT PORT  |
| `sdd:reliability.mdx`       | Reliability Engineering | 970   | `internal/engineering/performance/slo-sli-sla.md`    | 🔴 STUB | HIGH     | DIRECT PORT  |
| `sdd:knowledge.mdx`         | Knowledge Management    | 823   | `internal/overview/tools.md`                         | 🔴 STUB | Low      | DIRECT PORT  |

---

## Guide Documents (7 Sources)

User-facing guides for customers and developers.

| Source File                           | Title                 | Lines | Target Path                                  | Status    | Priority | Refresh Type |
| ------------------------------------- | --------------------- | ----- | -------------------------------------------- | --------- | -------- | ------------ |
| `guide:getting-started.mdx`           | Getting Started Guide | 867   | `quickstart.mdx`                             | 🟢 EXISTS | Low      | SKIP         |
| `guide:document-collaboration.mdx`    | Collaboration Guide   | 1234  | `customer/collaboration/overview.md`         | 🔴 STUB   | Medium   | DIRECT PORT  |
| `guide:ai-content-generation.mdx`     | AI Content Generation | 1269  | `customer/ai/overview.md`                    | 🔴 STUB   | Medium   | DIRECT PORT  |
| `guide:workspace-management.mdx`      | Workspace Management  | 1189  | `customer/workspaces/creating-workspaces.md` | 🔴 STUB   | Medium   | DIRECT PORT  |
| `guide:document-creation-editing.mdx` | Document Creation     | 1216  | `customer/documents/creating-documents.md`   | 🔴 STUB   | Medium   | DIRECT PORT  |
| `guide:markdown-syntax.mdx`           | Markdown Syntax       | 195   | `customer/documents/editing-documents.md`    | 🔴 STUB   | Low      | DIRECT PORT  |
| `guide:best-practices.mdx`            | Best Practices        | 276   | `developer/contributing/code-standards.mdx`  | 🔴 STUB   | Medium   | REFRESH      |

---

## API Documents (5 Sources)

API reference and integration documentation.

| Source File                   | Title               | Lines | Target Path                                 | Status  | Priority | Refresh Type |
| ----------------------------- | ------------------- | ----- | ------------------------------------------- | ------- | -------- | ------------ |
| `api:api-overview.mdx`        | API Overview        | —     | `api/introduction/overview.md`              | 🔴 STUB | HIGH     | DIRECT PORT  |
| `api:rest-api-reference.mdx`  | REST API Reference  | 1363  | (generated from OpenAPI)                    | N/A     | N/A      | SKIP         |
| `api:websocket-api-guide.mdx` | WebSocket API Guide | 1391  | `api/websocket/overview.md`                 | 🔴 STUB | HIGH     | DIRECT PORT  |
| `api:api-srs-diagrams.mdx`    | API SRS Diagrams    | 713   | `developer/domain/api/architecture.md`      | 🔴 STUB | Medium   | DIRECT PORT  |
| `api:scribe.mdx`              | Scribe CLI          | 718   | `developer/platform/intelligence/scribe.md` | 🔴 STUB | Medium   | DIRECT PORT  |

---

## SRS Documents (3 Sources - Discovered)

System Requirements Specifications for core services.

| Source File                  | Title                              | Lines | Target Path                            | Status  | Priority | Refresh Type |
| ---------------------------- | ---------------------------------- | ----- | -------------------------------------- | ------- | -------- | ------------ |
| `sdd:srs:auth.mdx`           | Shield Authentication SRS          | 1134  | `developer/domain/shield/overview.md`  | 🔴 STUB | HIGH     | DIRECT PORT  |
| `sdd:srs:collaboration.mdx`  | Real-Time Collaboration SRS        | ~600  | `developer/domain/relay/overview.md`   | 🔴 STUB | HIGH     | DIRECT PORT  |
| `sdd:srs:api.mdx`            | API Service SRS                    | ~600  | `developer/domain/api/overview.md`     | 🔴 STUB | HIGH     | DIRECT PORT  |

---

## Internal/Informational Documents (Skip)

These documents are internal tooling references and should not be migrated.

| Source File               | Title                     | Action |
| ------------------------- | ------------------------- | ------ |
| `ii:acronyms.mdx`         | Acronyms & Terminology    | SKIP   |
| `ii:cs:definitions.mdx`   | Component Definitions     | SKIP   |
| `ii:cs:docusaurus.mdx`    | Docusaurus Config         | SKIP   |
| `ii:cs:rex-masterclass.mdx` | REX Masterclass         | SKIP   |
| `ii:ppt:saas-2-docs.mdx`  | SaaS to Docs Conversion   | SKIP   |
| `ii:ppt:cut-the-fluff.mdx`| Cut The Fluff Principles  | SKIP   |
| `ii:cfg:ofs.mdx`          | Operational Framework     | SKIP   |

---

## TODO/In-Progress Documents (6 Sources)

Incomplete legacy documents that may contain useful fragments.

| Source File                        | Title                  | Action            |
| ---------------------------------- | ---------------------- | ----------------- |
| `TODO-ctx:system-architecture.mdx` | System Architecture    | Review for useful |
| `TODO-ctx:project-structure.mdx`   | Project Structure      | Review for useful |
| `TODO-dev:project-search-engine.mdx` | Search Engine        | Review for useful |
| `TODO-sdd:sw:environment-setup.mdx` | Environment Setup     | Review for useful |
| `TODO-sdd:sys:ops:runbooks.mdx`    | Operations Runbooks    | Review for useful |
| `TODO-ii:cs:component-showcase.mdx`| Component Showcase     | SKIP              |

---

## Migration Priority Summary

### HIGH Priority (34 targets)

These are critical stubs that need immediate content from legacy sources:

| Category     | Documents                                                                                         |
| ------------ | ------------------------------------------------------------------------------------------------- |
| L1-Strategic | `l1-strategic-specs.md`, `vision.md`, `taxonomy-index.md` (NEW)                                   |
| L2-System    | `platform-services.md`, `security/overview.md`, `slo-sli-sla.md`, `disaster-recovery.md`, etc.    |
| L3-Technical | `developer/architecture.md`, `canvas/architecture.md`, `relay/architecture.md`, `folio/overview.md` |
| API/SRS      | `api/overview.md`, `websocket/overview.md`, Shield/Relay/API SRS docs                             |

### Medium Priority (18 targets)

Enhance completeness but are less critical:
- Guide documents for customers
- Debugging guides
- Code standards, workflow docs

### Low Priority (7 targets)

Already complete or low impact:
- `concept-of-operations.md` ✅
- `technology-strategy.md` ✅
- `data-models.md` ✅
- Acronyms, internal tooling docs

---

## Classification System to Preserve

The legacy L1–L4 hierarchy should be integrated into the Atlas docs structure:

| Level              | Context               | Audience           | Atlas Location                                                               |
| ------------------ | --------------------- | ------------------ | ---------------------------------------------------------------------------- |
| **L1-Strategic**   | Enterprise/Market     | Board, CPO, CTO    | `internal/architecture/specs/l1-*` + `internal/product/strategy/*`           |
| **L2-System**      | Platform/Architecture | CTO + Domain Leads | `internal/architecture/system-design/*` + `internal/architecture/specs/l2-*` |
| **L3-Technical**   | Component/Module      | Engineering Teams  | `developer/*` (domain, platform, testing, operations)                        |
| **L4-Operational** | Execution/Maintenance | Ops/SRE            | `developer/operations/runbooks/*` + `internal/operations/*`                  |

---

## Content Refresh Guidelines

When migrating content:

1. **Strip Docusaurus-specific syntax** (imports, JSX components, custom admonitions)
2. **Convert to Mintlify MDX format** (use Mintlify-compatible callouts)
3. **Preserve Mermaid diagrams** (Mintlify supports Mermaid)
4. **Update references** to point to Atlas docs paths
5. **Verify service names** match current architecture (API, Shield, Relay, Aria, Manuscript, Printery)
6. **Add SDD classification note** at top of each refreshed page
7. **Cross-reference related docs** within the Atlas site

### Docusaurus → Mintlify Conversion

| Docusaurus Syntax                  | Mintlify Equivalent           |
| ---------------------------------- | ----------------------------- |
| `:::info`                          | `<Info>`                      |
| `:::note`                          | `<Note>`                      |
| `:::warning`                       | `<Warning>`                   |
| `:::tip`                           | `<Tip>`                       |
| `import Link from "@docusaurus/Link"` | Remove (use standard links)  |
| `<Link to="/path">Text</Link>`     | `[Text](/path)`               |

---

## TASKSET Summary

| TASKSET | Status      | Description                           |
| ------- | ----------- | ------------------------------------- |
| 1       | ✅ COMPLETE | Inventory & Mapping                   |
| 2       | ✅ COMPLETE | L1-Strategic Layer Refresh            |
| 3       | ⏳ PENDING  | L2-System Architecture Refresh        |
| 4       | ⏳ PENDING  | L3-Technical Implementation Refresh   |
| 5       | ⏳ PENDING  | L4-Operational Refresh                |
| 6       | ⏳ PENDING  | Validation & Cross-Reference          |

---

_Generated: 2026-01-07_
_Source: TASKSET 1 - Inventory & Mapping_
_Legacy Documents: 75 | Atlas Targets: 475 | HIGH Priority: 34_
