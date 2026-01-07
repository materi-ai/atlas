# Backend System Architecture

<Info>
**SDD Classification:** L3-Technical | **Authority:** CTO + VP Engineering | **Review Cycle:** Quarterly
</Info>

This document provides the comprehensive backend architecture for the Materi document collaboration platform. It covers the polyglot microservices design using Go Fiber for HTTP APIs and Rust Axum for real-time collaboration, along with data layer design and scalability strategies.

**Performance Target**: <50ms API response P95, <25ms collaboration latency
**Architecture Style**: Polyglot microservices with event-driven integration
**Primary Languages**: Go (API), Rust (Real-time), Python (Auth)

---

## Architecture Overview

### Technology Decision Rationale

Our technology choices prioritize enterprise-grade performance while optimizing operational costs:

| Requirement | Traditional Approach | Materi's Approach | Business Impact |
|-------------|---------------------|-------------------|-----------------|
| **API Performance** | Python/FastAPI (~200ms) | Go Fiber (~50ms) | 4x faster user experience |
| **Real-time Collaboration** | Separate WebSocket service | Integrated Rust engine | Seamless collaborative editing |
| **Concurrent Users** | 1,000 per instance | 5,000+ per instance | 5x better cost efficiency |
| **Memory Usage** | 500MB-2GB (Python) | 50-200MB (Go/Rust) | 80% lower infrastructure cost |

### High-Level Service Topology

```mermaid
graph TB
    subgraph "Client Layer"
        WEB[Web Application]
        MOBILE[Mobile Apps]
        API_CLIENTS[API Integrations]
    end

    subgraph "Edge Layer"
        CDN[CloudFlare CDN]
        LB[Load Balancer]
    end

    subgraph "Core Services Layer"
        API[Fiber API Gateway<br/>Go Runtime]
        COLLAB[Collaboration Engine<br/>Rust/Axum]
        ADMIN[Admin Services<br/>Django]
    end

    subgraph "AI Integration Layer"
        AI_ROUTER[AI Request Router]
        OPENAI[OpenAI GPT-4]
        ANTHROPIC[Anthropic Claude]
        VECTOR[Vector Database]
    end

    subgraph "Data Persistence Layer"
        POSTGRES[(PostgreSQL<br/>Primary Database)]
        REDIS[(Redis Cluster<br/>Cache & Queues)]
        S3[(Object Storage<br/>Files & Assets)]
    end

    WEB --> CDN
    MOBILE --> CDN
    API_CLIENTS --> LB
    CDN --> LB

    LB --> API
    LB --> COLLAB

    API --> ADMIN
    API --> AI_ROUTER
    API --> POSTGRES
    API --> REDIS

    COLLAB --> POSTGRES
    COLLAB --> REDIS

    AI_ROUTER --> OPENAI
    AI_ROUTER --> ANTHROPIC
    AI_ROUTER --> VECTOR

    API --> S3
    ADMIN --> POSTGRES

    classDef fiberService fill:#00ADD8,color:#fff,stroke:#fff,stroke-width:2px
    classDef rustService fill:#CE422B,color:#fff,stroke:#fff,stroke-width:2px
    classDef dataStore fill:#336791,color:#fff,stroke:#fff,stroke-width:2px

    class API fiberService
    class COLLAB rustService
    class POSTGRES,REDIS,S3 dataStore
```

### Service Responsibilities Matrix

| Service | Primary Responsibility | Performance Target | Scaling Strategy |
|---------|----------------------|-------------------|------------------|
| **Fiber API Gateway** | HTTP APIs, Business Logic, Authentication | <50ms P95 response time | Horizontal scaling, stateless |
| **Rust Collaboration Engine** | WebSocket connections, CRDT operations | <100ms message latency | Connection pooling, memory efficiency |
| **Django Admin Services** | User management, billing, analytics | <200ms response time | Vertical scaling, background jobs |

---

## Fiber API Gateway (Go)

### Architecture Design

The Fiber API Gateway serves as the primary interface for all document operations, designed for enterprise-grade performance and reliability.

```mermaid
graph LR
    subgraph "Fiber API Gateway Architecture"
        direction TB

        subgraph "HTTP Layer"
            ROUTES[Route Handlers]
            MIDDLEWARE[Middleware Stack]
            VALIDATION[Input Validation]
        end

        subgraph "Business Layer"
            DOC_SVC[Document Service]
            AUTH_SVC[Auth Service]
            AI_SVC[AI Service]
            WORKSPACE_SVC[Workspace Service]
        end

        subgraph "Data Layer"
            REPOS[Repository Pattern]
            CACHE[Cache Manager]
            EVENTS[Event Publisher]
        end

        ROUTES --> DOC_SVC
        ROUTES --> AUTH_SVC
        ROUTES --> AI_SVC
        ROUTES --> WORKSPACE_SVC

        DOC_SVC --> REPOS
        AUTH_SVC --> CACHE
        AI_SVC --> EVENTS

        MIDDLEWARE --> VALIDATION
    end

    classDef serviceLayer fill:#00ADD8,color:#fff,stroke:#fff,stroke-width:2px
    classDef dataLayer fill:#059669,color:#fff,stroke:#fff,stroke-width:2px

    class DOC_SVC,AUTH_SVC,AI_SVC,WORKSPACE_SVC serviceLayer
    class REPOS,CACHE,EVENTS dataLayer
```

### Key Performance Characteristics

- **Concurrency Model:** Goroutines (lightweight threads) - 1M+ concurrent connections possible
- **Memory Efficiency:** ~2MB per 1000 connections vs ~200MB for equivalent Python service
- **Response Time:** 95th percentile under 50ms for document operations
- **Throughput:** 10,000+ requests/second per instance

### Enterprise Features

- **JWT Authentication** with refresh token rotation
- **Rate Limiting** per user/workspace with Redis backend
- **Audit Logging** for compliance (SOX, HIPAA, GDPR)
- **Circuit Breakers** for external service resilience

---

## Collaboration Engine (Rust/Axum)

### Architecture Design

The Rust Collaboration Engine provides real-time document collaboration that outperforms Google Docs in latency and concurrent user capacity.

```mermaid
graph TB
    subgraph "Rust Collaboration Architecture"
        direction TB

        subgraph "Connection Management"
            WS_HANDLER[WebSocket Handler]
            CONN_POOL[Connection Pool]
            PRESENCE[Presence Tracker]
        end

        subgraph "CRDT Engine"
            OP_TRANSFORM[Operational Transform]
            CONFLICT_RESOLVE[Conflict Resolution]
            STATE_SYNC[State Synchronization]
        end

        subgraph "Message Processing"
            MSG_ROUTER[Message Router]
            BROADCAST[Broadcast Engine]
            PERSISTENCE[Operation Persistence]
        end

        WS_HANDLER --> CONN_POOL
        CONN_POOL --> PRESENCE

        WS_HANDLER --> OP_TRANSFORM
        OP_TRANSFORM --> CONFLICT_RESOLVE
        CONFLICT_RESOLVE --> STATE_SYNC

        STATE_SYNC --> MSG_ROUTER
        MSG_ROUTER --> BROADCAST
        BROADCAST --> PERSISTENCE
    end

    classDef rustCore fill:#CE422B,color:#fff,stroke:#fff,stroke-width:2px
    classDef performance fill:#7C2D12,color:#fff,stroke:#fff,stroke-width:2px

    class WS_HANDLER,OP_TRANSFORM,MSG_ROUTER rustCore
    class CONN_POOL,BROADCAST performance
```

### Technical Advantages

- **Zero-Copy Operations:** Rust's memory safety without garbage collection pauses
- **Lock-Free Algorithms:** Concurrent data structures for maximum throughput
- **Predictable Latency:** No garbage collection = consistent sub-100ms performance
- **Memory Safety:** Prevents entire classes of security vulnerabilities

### Collaborative Features

- **Real-time Editing:** Character-by-character synchronization
- **Conflict-Free Resolution:** Mathematical guarantees against edit conflicts
- **Presence Awareness:** Live cursors and user indicators
- **Connection Recovery:** Automatic reconnection with state synchronization

---

## Data Layer Selection

### Primary Database (PostgreSQL)

| Feature | MongoDB | MySQL | DynamoDB | **PostgreSQL** |
|---------|---------|-------|----------|----------------|
| ACID Support | Limited | Yes | No | **Full** |
| JSON Handling | Native | Basic | Good | **Advanced** |
| Query Power | Medium | Good | Limited | **Excellent** |
| Enterprise Use | Medium | High | Medium | **Very High** |

**Why PostgreSQL:**
- Full ACID compliance for document integrity
- Superior JSON/JSONB support for flexible schemas
- Advanced query capabilities with indexing options
- Enterprise-grade security and reliability

### Cache & Message Layer (Redis)

| Feature | Memcached | RabbitMQ | Kafka | **Redis** |
|---------|-----------|----------|-------|-----------|
| Latency | Good | Medium | Medium | **Best** |
| Data Types | Basic | Queue | Streams | **Rich** |
| Memory Util | Medium | High | High | **Low** |
| Scalability | Limited | Good | Good | **Best** |

**Why Redis:**
- Sub-millisecond response times for caching
- Built-in pub/sub for real-time messaging
- Rich data structures for complex operations
- Simple deployment and maintenance model

---

## Performance & Scalability

### Scaling Characteristics by User Load

| Load Tier | Fiber Instances | Rust Instances | Database Config |
|-----------|----------------|----------------|-----------------|
| **1-1K Users** | 2 instances | 1 instance | Single DB |
| **1K-10K Users** | 5 instances | 3 instances | Read Replicas |
| **10K-100K Users** | 15+ instances | 8+ instances | Sharded Database |
| **100K+ Users** | Auto-scaling | Auto-scaling | Multi-region |

### Performance Benchmarks vs Competition

| Metric | Google Docs | Microsoft 365 | **Materi** | Advantage |
|--------|-------------|---------------|------------|-----------|
| **API Response Time** | 150-300ms | 200-400ms | **<50ms** | **3-8x faster** |
| **Concurrent Editors** | 100 users | 100 users | **1000+ users** | **10x capacity** |
| **WebSocket Latency** | 200-500ms | 300-600ms | **<100ms** | **2-5x faster** |
| **Memory per User** | ~10MB | ~15MB | **<2MB** | **5-7x efficient** |

### Cost Efficiency Analysis

| Cost Category | Traditional Python Stack | Materi Fiber/Axum | Savings |
|---------------|-------------------------|-------------------|---------|
| **Compute Cost per 1K Users** | $2,400/month | $960/month | 60% |
| **Memory Requirements** | 16GB per instance | 4GB per instance | 75% |
| **Instance Count (10K users)** | 20 instances | 8 instances | 60% |

---

## Data Flow & Integration

### Document Lifecycle Flow

```mermaid
sequenceDiagram
    participant Client
    participant Fiber as Fiber API
    participant Rust as Rust Collab
    participant DB as PostgreSQL
    participant AI as AI Services

    Note over Client,AI: Document Creation & Collaboration Flow

    Client->>Fiber: Create Document
    Fiber->>DB: Store Document
    Fiber->>Client: Document Created

    Client->>Rust: Join Collaboration
    Rust->>DB: Verify Permissions
    Rust->>Client: Connection Established

    Client->>Rust: Edit Operation
    Rust->>Rust: Apply CRDT Transform
    Rust->>DB: Persist Operation
    Rust->>Client: Broadcast to Peers

    Client->>Fiber: Request AI Generation
    Fiber->>AI: Generate Content
    AI-->>Fiber: Streaming Response
    Fiber-->>Client: Stream AI Content

    Fiber->>DB: Store AI Generation
    Fiber->>Rust: Notify Collaboration
    Rust->>Client: Update Collaborators
```

### Event-Driven Architecture

All services communicate via Redis Streams for cross-service synchronization:

| Stream Name | Purpose | Publishers | Consumers | Retention |
|-------------|---------|------------|-----------|-----------|
| `materi:events:users` | User lifecycle events | Shield | API, Relay | 7 days |
| `materi:events:documents` | Document CRUD operations | API | Relay, Shield | 7 days |
| `materi:events:collaboration` | Real-time operations | Relay | API | 24 hours |
| `materi:events:ai` | AI generation events | Aria | API | 24 hours |

---

## Security Architecture

### Security Layers

```mermaid
graph TB
    subgraph "Security Architecture"
        direction TB

        subgraph "Network Security"
            WAF[Web Application Firewall]
            DDoS[DDoS Protection]
            TLS[TLS 1.3 Encryption]
        end

        subgraph "Application Security"
            JWT[JWT Authentication]
            RBAC[Role-Based Access Control]
            RLS[Row-Level Security]
        end

        subgraph "Data Security"
            ENCRYPT[Encryption at Rest]
            BACKUP[Encrypted Backups]
            AUDIT[Audit Logging]
        end
    end

    classDef security fill:#DC2626,color:#fff,stroke:#fff,stroke-width:2px

    class JWT,RBAC,RLS,ENCRYPT security
```

### Compliance Framework

- **SOC 2 Type II** - Automated security controls and monitoring
- **GDPR Compliance** - Data portability and right to deletion
- **HIPAA Ready** - Encryption and audit logging for healthcare customers
- **Enterprise SSO** - SAML 2.0 and OAuth 2.0 integration

---

## Monitoring & Observability

### Three Pillars of Observability

| Pillar | Technology | Purpose |
|--------|------------|---------|
| **Metrics** | Prometheus + Grafana | Time-series performance data |
| **Logging** | Structured Logs + ELK | Searchable application logs |
| **Tracing** | Jaeger + OpenTelemetry | Distributed request tracing |

### Key Business Metrics

- **User Experience** - API latency, collaboration lag, error rates
- **System Health** - Resource utilization, connection counts, throughput
- **Business KPIs** - Document creation rate, AI usage, user engagement

---

## Cross-References

### Upstream Documents
- [L2-System Tactical Specifications](/internal/architecture/specs/l2-tactical-specs) - System architecture decisions
- [Platform Architecture](/internal/architecture/system-design/overview) - Platform overview

### Peer Documents
- [Frontend Architecture](/developer/products/canvas/architecture) - Canvas React application
- [Relay Architecture](/developer/domain/relay/architecture) - Real-time collaboration details
- [AI Integration](/developer/platform/aria/model-integration) - AI provider integration

### Downstream Documents
- [Testing Framework](/developer/testing/overview) - Testing strategy
- [Git Workflow](/developer/contributing/git-workflow) - Development workflow

---

**Document Status:** Complete
**Version:** 2.0
**Last Updated:** January 2026
**Authority:** CTO + VP Engineering
**Classification:** L3-Technical - Backend Development Guide

**Distribution:** Engineering Teams, Architecture Council
