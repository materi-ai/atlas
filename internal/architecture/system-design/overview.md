# System Design Overview

**Architecture Style**: Event-driven microservices with polyglot implementation  
**Performance Target**: Sub-50ms API, sub-25ms real-time collaboration  
**Scale**: 50,000+ concurrent users, global deployment  
**Availability**: 99.9% uptime SLA

---

## Architecture Philosophy

Materi's architecture follows three core principles:

1. **Performance-First Design**: Every architectural decision optimizes for user-perceived latency
2. **AI-Native Integration**: AI capabilities built into the core, not bolted on
3. **Enterprise Scalability**: Designed for Fortune 500 scale from day one

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Canvas    │  │   Mobile    │  │    API      │  │  Webhooks   │        │
│  │  (React)    │  │   Apps      │  │  Clients    │  │  Partners   │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
└─────────┼────────────────┼────────────────┼────────────────┼────────────────┘
          │                │                │                │
          ▼                ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            GATEWAY LAYER                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    API Gateway (Go Fiber)                            │   │
│  │           Load Balancing • Rate Limiting • Authentication            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SERVICE LAYER                                      │
│                                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │     API      │  │    Shield    │  │    Relay     │  │    Aria      │    │
│  │  (Go/Fiber)  │  │(Python/Django)│  │ (Rust/Axum) │  │  (Python)    │    │
│  │              │  │              │  │              │  │              │    │
│  │ Business     │  │ Auth & IAM   │  │ Real-time    │  │ AI/ML        │    │
│  │ Logic        │  │ User Mgmt    │  │ Collaboration│  │ Orchestration│    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │
│         │                 │                 │                 │             │
│  ┌──────┴─────────────────┴─────────────────┴─────────────────┴──────┐     │
│  │                    Redis Streams (Event Bus)                       │     │
│  └───────────────────────────────────────────────────────────────────┘     │
│                                                                              │
│  ┌──────────────┐  ┌──────────────┐                                        │
│  │  Manuscript  │  │   Printery   │                                        │
│  │  (Protobuf)  │  │   (Go)       │                                        │
│  │              │  │              │                                        │
│  │ Schema Defs  │  │ Document     │                                        │
│  │ Contracts    │  │ Rendering    │                                        │
│  └──────────────┘  └──────────────┘                                        │
└─────────────────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            DATA LAYER                                        │
│  ┌──────────────────────┐  ┌──────────────────────┐  ┌─────────────────┐   │
│  │     PostgreSQL       │  │        Redis         │  │     MinIO       │   │
│  │                      │  │                      │  │                 │   │
│  │  • User data         │  │  • Session cache     │  │  • File storage │   │
│  │  • Documents         │  │  • Rate limiting     │  │  • Attachments  │   │
│  │  • Workspaces        │  │  • Pub/Sub events    │  │  • Exports      │   │
│  │  • Audit logs        │  │  • Real-time state   │  │                 │   │
│  └──────────────────────┘  └──────────────────────┘  └─────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Service Responsibilities

| Service        | Language      | Primary Responsibility               | Performance Target |
| -------------- | ------------- | ------------------------------------ | ------------------ |
| **API**        | Go/Fiber      | REST API, business logic             | <50ms response     |
| **Shield**     | Python/Django | Authentication, user management      | <100ms auth        |
| **Relay**      | Rust/Axum     | Real-time collaboration, WebSockets  | <25ms latency      |
| **Aria**       | Python        | AI orchestration, content generation | <2s generation     |
| **Manuscript** | Protobuf      | Schema definitions, contracts        | N/A (build-time)   |
| **Printery**   | Go            | Document rendering, exports          | <5s render         |
| **Canvas**     | React/TS      | Web application, UI                  | <500ms load        |

---

## Communication Patterns

### Synchronous (HTTP/gRPC)

-   **Client → API**: REST API calls for CRUD operations
-   **API → Shield**: Token validation, permission checks
-   **API → Aria**: AI content generation requests

### Asynchronous (Redis Streams)

-   **Document Events**: Create, update, delete notifications
-   **Collaboration Events**: User presence, cursor positions
-   **AI Events**: Generation completion, context updates
-   **System Events**: Audit logs, analytics, notifications

### Real-time (WebSocket)

-   **Client ↔ Relay**: Bidirectional collaboration channel
-   **CRDT Operations**: Conflict-free document synchronization
-   **Presence Updates**: User cursors, selections, activity

---

## Deployment Architecture

### Production Environment

-   **Platform**: Railway (backend), Vercel (frontend)
-   **Database**: Railway Managed PostgreSQL
-   **Cache**: Railway Managed Redis
-   **CDN**: Cloudflare for global edge caching

### Scaling Strategy

-   **Horizontal**: Auto-scaling based on CPU/memory
-   **Vertical**: Database and cache tier upgrades
-   **Geographic**: Multi-region deployment for latency

---

## Security Architecture

### Authentication Flow

1. User authenticates via Shield (OAuth/SAML/Password)
2. JWT token issued with RS256 signing
3. Token validated on each API request
4. Token cached in Redis for performance

### Authorization Model

-   **RBAC**: Role-based access control
-   **Resource-level**: Document and workspace permissions
-   **Enterprise SSO**: SAML 2.0 integration

---

## Cross-References

-   **[Platform Services](platform-services.md)**: Detailed service specifications
-   **[Data Models](data-models.md)**: Database schemas and data flow
-   **[Event-Driven Architecture](event-driven-architecture.md)**: Messaging patterns
-   **[Domain Services](domain-services.md)**: Business domain breakdown

---

**Document Status**: ✅ Active  
**Last Updated**: December 2025  
**Authority**: CTO + Architecture Council  
**Classification**: Internal - Architecture
