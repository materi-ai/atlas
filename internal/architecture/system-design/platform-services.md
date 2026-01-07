# Platform Services Architecture

**Services**: 7 core microservices  
**Languages**: Go, Rust, Python, TypeScript  
**Communication**: HTTP/REST, gRPC, WebSocket, Redis Streams

---

## Service Catalog

### API Service (Go/Fiber)

**Purpose**: Primary REST API gateway and business logic layer

**Technology Stack**:

-   Go 1.25.3 with Fiber v2 framework
-   PostgreSQL via SQLx
-   Redis for caching and rate limiting

**Responsibilities**:

-   RESTful API endpoints for all client operations
-   Business logic orchestration
-   Request validation and transformation
-   Response formatting and pagination
-   Rate limiting and throttling

**Key Endpoints**:

```
POST   /api/v1/documents          Create document
GET    /api/v1/documents/:id      Get document
PUT    /api/v1/documents/:id      Update document
DELETE /api/v1/documents/:id      Delete document
GET    /api/v1/workspaces         List workspaces
POST   /api/v1/workspaces         Create workspace
```

**Performance Targets**:

-   Response time: <50ms (P95)
-   Throughput: 10,000 req/s
-   Availability: 99.9%

**Dependencies**:

-   Shield: Authentication/authorization
-   PostgreSQL: Data persistence
-   Redis: Caching, rate limiting
-   Relay: Event broadcasting

---

### Shield Service (Python/Django)

**Purpose**: Authentication, authorization, and user management

**Technology Stack**:

-   Python 3.11+ with Django 4.2
-   Django REST Framework
-   PostgreSQL via Django ORM
-   Redis for session management

**Responsibilities**:

-   User registration and authentication
-   OAuth 2.0 / SAML SSO integration
-   JWT token issuance and validation
-   Role-based access control (RBAC)
-   User profile management
-   Password reset and MFA

**Key Endpoints**:

```
POST   /auth/login                User login
POST   /auth/register             User registration
POST   /auth/token/refresh        Refresh JWT token
GET    /auth/me                   Current user profile
POST   /auth/sso/saml             SAML SSO callback
```

**Security Features**:

-   RS256 JWT signing
-   Token rotation and revocation
-   Brute-force protection
-   Audit logging

**Dependencies**:

-   PostgreSQL: User data
-   Redis: Session cache, rate limiting
-   External: OAuth providers (Google, Microsoft)

---

### Relay Service (Rust/Axum)

**Purpose**: Real-time collaboration engine

**Technology Stack**:

-   Rust 1.78+ with Axum framework
-   Tokio async runtime
-   WebSocket connections
-   CRDT algorithms for conflict resolution

**Responsibilities**:

-   WebSocket connection management
-   Real-time document synchronization
-   CRDT-based conflict resolution
-   User presence and cursor tracking
-   Event broadcasting to connected clients

**Connection Flow**:

```
1. Client connects via WebSocket
2. JWT validated with Shield
3. Join document room
4. Receive/send CRDT operations
5. Presence updates broadcast
```

**Performance Targets**:

-   Latency: <25ms (P95)
-   Concurrent connections: 50,000+
-   Users per document: 1,000+

**CRDT Operations**:

-   Text insertions/deletions
-   Formatting changes
-   Block operations
-   Cursor/selection sync

**Dependencies**:

-   Shield: Token validation
-   Redis: Pub/sub, state management
-   PostgreSQL: Document persistence

---

### Aria Service (Python)

**Purpose**: AI orchestration and intelligent features

**Technology Stack**:

-   Python 3.11+
-   Multi-provider AI APIs (OpenAI, Anthropic, Cohere)
-   Custom model registry
-   Redis for context caching

**Responsibilities**:

-   AI content generation
-   Context assembly and management
-   Multi-provider routing and fallback
-   Cost optimization
-   Content safety and moderation

**Key Capabilities**:

```
Content Generation    - Draft text, summaries, expansions
Context Management    - Document context, user preferences
Provider Routing      - Cost/quality optimization
Streaming Responses   - Real-time generation output
```

**AI Providers**:
| Provider | Use Case | Fallback |
|----------|----------|----------|
| OpenAI GPT-4 | Complex generation | Anthropic Claude |
| Anthropic Claude | Long context | OpenAI GPT-4 |
| Cohere | Embeddings, search | OpenAI |

**Dependencies**:

-   Redis: Context caching
-   PostgreSQL: Usage tracking
-   External: AI provider APIs

---

### Manuscript Service (Protocol Buffers)

**Purpose**: Schema definitions and service contracts

**Technology Stack**:

-   Protocol Buffers v3
-   Go bindings (primary)
-   TypeScript bindings (frontend)

**Schema Domains**:

```
User Domain           - User, Profile, Preferences
Document Domain       - Document, Block, Version
Workspace Domain      - Workspace, Team, Permissions
Collaboration Domain  - Presence, Cursor, Operation
Notification Domain   - Notification, Event
Audit Domain          - AuditLog, Action
```

**Benefits**:

-   Type-safe cross-service communication
-   Automatic code generation
-   Schema versioning and evolution
-   Reduced serialization overhead

---

### Printery Service (Go)

**Purpose**: Document rendering and export

**Technology Stack**:

-   Go with custom rendering engine
-   Redis Streams consumer
-   S3-compatible storage (MinIO)

**Responsibilities**:

-   Document rendering to various formats
-   PDF/DOCX/HTML export
-   Print-ready output generation
-   Background job processing

**Supported Formats**:

```
PDF     - Print-ready documents
DOCX    - Microsoft Word compatible
HTML    - Web-ready output
Markdown - Plain text export
```

**Processing Model**:

-   Event-driven via Redis Streams
-   Worker pool for parallel processing
-   Progress tracking and callbacks

---

### Canvas Application (React/TypeScript)

**Purpose**: Primary web application

**Technology Stack**:

-   React 18+ with TypeScript
-   Next.js 14 for SSR/SSG
-   TipTap for rich text editing
-   Yjs for CRDT synchronization
-   TailwindCSS for styling

**Responsibilities**:

-   Document editing interface
-   Real-time collaboration UI
-   AI feature integration
-   Workspace management
-   User settings and preferences

**Key Features**:

```
Rich Text Editor      - Full formatting, blocks, embeds
Real-time Collab      - Cursors, presence, live updates
AI Integration        - Context panel, generation UI
Workspace UI          - Team management, permissions
```

**Performance Targets**:

-   Initial load: <500ms
-   Time to interactive: <1s
-   Collaboration latency: <25ms (via Relay)

---

## Service Dependencies Matrix

```
              API  Shield  Relay  Aria  Printery  Canvas
API            -     ✓       ✓      ✓       ✓        -
Shield         -     -       -      -       -        -
Relay          -     ✓       -      -       -        -
Aria           -     -       -      -       -        -
Printery       ✓     -       -      -       -        -
Canvas         ✓     ✓       ✓      -       -        -
```

---

## Service Communication

### Request Flow: Document Creation

```
1. Canvas → API: POST /documents (JWT in header)
2. API → Shield: Validate token
3. API → PostgreSQL: Create document
4. API → Redis Streams: Publish document.created
5. Relay: Consume event, notify connected users
6. API → Canvas: Return document response
```

### Request Flow: AI Generation

```
1. Canvas → API: POST /ai/generate
2. API → Shield: Validate token + permissions
3. API → Aria: Forward generation request
4. Aria → AI Provider: Generate content
5. Aria → API: Stream response
6. API → Canvas: Stream to client
```

---

## Health & Monitoring

### Health Endpoints

All services expose:

-   `GET /health` - Basic health check
-   `GET /ready` - Readiness probe (dependencies)
-   `GET /metrics` - Prometheus metrics

### Key Metrics per Service

| Service  | Critical Metrics                          |
| -------- | ----------------------------------------- |
| API      | Request latency, error rate, throughput   |
| Shield   | Auth latency, token validation rate       |
| Relay    | Connection count, message latency         |
| Aria     | Generation latency, provider availability |
| Printery | Job queue depth, render time              |

---

**Document Status**: ✅ Active  
**Last Updated**: December 2025  
**Authority**: CTO + Engineering Leads  
**Classification**: Internal - Architecture
