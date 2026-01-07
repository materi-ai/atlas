# Data Models & Architecture

**Primary Database**: PostgreSQL 15+  
**Cache Layer**: Redis 7+  
**Object Storage**: MinIO (S3-compatible)  
**Schema Strategy**: Multi-tenant with service isolation

---

## Database Architecture

### PostgreSQL Schema Organization

```
materi_db
├── public              # Shared utilities and extensions
├── auth                # Shield: Users, sessions, permissions
├── documents           # API: Documents, blocks, versions
├── workspaces          # API: Workspaces, teams, memberships
├── collaboration       # Relay: Presence, operations, cursors
├── ai                  # Aria: Context, usage, preferences
├── audit               # Cross-service: Audit logs
└── analytics           # Cross-service: Metrics, events
```

---

## Core Data Models

### User Domain (auth schema)

```sql
-- Users table
CREATE TABLE auth.users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) UNIQUE NOT NULL,
    password_hash   VARCHAR(255),
    first_name      VARCHAR(100),
    last_name       VARCHAR(100),
    avatar_url      VARCHAR(500),
    status          VARCHAR(20) DEFAULT 'active',
    email_verified  BOOLEAN DEFAULT false,
    mfa_enabled     BOOLEAN DEFAULT false,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    last_login_at   TIMESTAMPTZ
);

-- User sessions
CREATE TABLE auth.sessions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    token_hash      VARCHAR(255) NOT NULL,
    device_info     JSONB,
    ip_address      INET,
    expires_at      TIMESTAMPTZ NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- OAuth connections
CREATE TABLE auth.oauth_connections (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    provider        VARCHAR(50) NOT NULL,
    provider_id     VARCHAR(255) NOT NULL,
    access_token    TEXT,
    refresh_token   TEXT,
    expires_at      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(provider, provider_id)
);
```

### Document Domain (documents schema)

```sql
-- Documents table
CREATE TABLE documents.documents (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id    UUID NOT NULL,
    title           VARCHAR(500) NOT NULL,
    slug            VARCHAR(500),
    content         JSONB DEFAULT '{}',
    content_text    TEXT,  -- For full-text search
    status          VARCHAR(20) DEFAULT 'draft',
    visibility      VARCHAR(20) DEFAULT 'private',
    owner_id        UUID NOT NULL,
    parent_id       UUID REFERENCES documents.documents(id),
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ
);

-- Document versions
CREATE TABLE documents.versions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id     UUID REFERENCES documents.documents(id) ON DELETE CASCADE,
    version_number  INTEGER NOT NULL,
    content         JSONB NOT NULL,
    created_by      UUID NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    change_summary  TEXT,
    UNIQUE(document_id, version_number)
);

-- Document blocks (for structured content)
CREATE TABLE documents.blocks (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id     UUID REFERENCES documents.documents(id) ON DELETE CASCADE,
    type            VARCHAR(50) NOT NULL,
    content         JSONB DEFAULT '{}',
    position        INTEGER NOT NULL,
    parent_block_id UUID REFERENCES documents.blocks(id),
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);
```

### Workspace Domain (workspaces schema)

```sql
-- Workspaces table
CREATE TABLE workspaces.workspaces (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(255) NOT NULL,
    slug            VARCHAR(255) UNIQUE NOT NULL,
    description     TEXT,
    logo_url        VARCHAR(500),
    settings        JSONB DEFAULT '{}',
    plan            VARCHAR(50) DEFAULT 'free',
    owner_id        UUID NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Workspace members
CREATE TABLE workspaces.members (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id    UUID REFERENCES workspaces.workspaces(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL,
    role            VARCHAR(50) NOT NULL DEFAULT 'member',
    permissions     JSONB DEFAULT '{}',
    invited_by      UUID,
    joined_at       TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(workspace_id, user_id)
);

-- Teams within workspaces
CREATE TABLE workspaces.teams (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id    UUID REFERENCES workspaces.workspaces(id) ON DELETE CASCADE,
    name            VARCHAR(255) NOT NULL,
    description     TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

### Collaboration Domain (collaboration schema)

```sql
-- Active collaborators
CREATE TABLE collaboration.presence (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id     UUID NOT NULL,
    user_id         UUID NOT NULL,
    cursor_position JSONB,
    selection       JSONB,
    last_active     TIMESTAMPTZ DEFAULT NOW(),
    connection_id   VARCHAR(255),
    UNIQUE(document_id, user_id)
);

-- CRDT operations log
CREATE TABLE collaboration.operations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id     UUID NOT NULL,
    user_id         UUID NOT NULL,
    operation       JSONB NOT NULL,
    vector_clock    JSONB NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

### Audit Domain (audit schema)

```sql
-- Audit log
CREATE TABLE audit.logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    actor_id        UUID,
    actor_type      VARCHAR(50) DEFAULT 'user',
    action          VARCHAR(100) NOT NULL,
    resource_type   VARCHAR(100) NOT NULL,
    resource_id     UUID,
    workspace_id    UUID,
    metadata        JSONB DEFAULT '{}',
    ip_address      INET,
    user_agent      TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

---

## Redis Data Structures

### Session Cache (DB 1)

```
Key Pattern: session:{user_id}:{token_id}
Type: Hash
TTL: 24 hours
Fields:
  - user_id
  - email
  - roles
  - permissions
  - expires_at
```

### Rate Limiting (DB 0)

```
Key Pattern: ratelimit:{user_id}:{endpoint}
Type: String (counter)
TTL: 60 seconds
Value: Request count
```

### Real-time Presence (DB 2)

```
Key Pattern: presence:{document_id}
Type: Hash
Fields:
  - {user_id}: {cursor, selection, color, name}
TTL: None (cleaned on disconnect)
```

### Document Cache (DB 0)

```
Key Pattern: doc:{document_id}:content
Type: String (JSON)
TTL: 5 minutes
Value: Serialized document content
```

### AI Context Cache (DB 3)

```
Key Pattern: context:{document_id}:{user_id}
Type: String (JSON)
TTL: 30 minutes
Value: Assembled context for AI generation
```

---

## Redis Streams (Event Bus)

### Stream Definitions

```
Stream: documents
  Events: created, updated, deleted, published
  Consumer Groups: api, relay, printery, analytics

Stream: collaboration
  Events: user_joined, user_left, operation, cursor_moved
  Consumer Groups: relay, analytics

Stream: ai
  Events: generation_started, generation_completed, context_updated
  Consumer Groups: api, analytics

Stream: audit
  Events: all audit log events
  Consumer Groups: audit-writer, analytics
```

### Event Structure

```json
{
    "event_id": "uuid",
    "event_type": "document.created",
    "timestamp": "2025-12-29T10:30:00Z",
    "actor_id": "user-uuid",
    "resource_id": "document-uuid",
    "workspace_id": "workspace-uuid",
    "payload": {
        "title": "New Document",
        "visibility": "private"
    }
}
```

---

## Data Flow Patterns

### Document Creation Flow

```
1. API receives POST /documents
2. Validate user permissions (Shield)
3. Insert into documents.documents
4. Publish to Redis Stream 'documents'
5. Relay consumes event, notifies subscribers
6. Analytics consumes event, tracks metrics
7. Return document to client
```

### Real-time Collaboration Flow

```
1. User connects to Relay WebSocket
2. Presence updated in Redis Hash
3. CRDT operation received
4. Operation persisted to PostgreSQL
5. Operation broadcast via Redis Pub/Sub
6. All connected clients receive update
7. Document cache invalidated
```

---

## Indexing Strategy

### Primary Indexes

```sql
-- User lookups
CREATE INDEX idx_users_email ON auth.users(email);

-- Document queries
CREATE INDEX idx_documents_workspace ON documents.documents(workspace_id);
CREATE INDEX idx_documents_owner ON documents.documents(owner_id);
CREATE INDEX idx_documents_updated ON documents.documents(updated_at DESC);

-- Full-text search
CREATE INDEX idx_documents_content_fts ON documents.documents
    USING GIN(to_tsvector('english', content_text));

-- Workspace queries
CREATE INDEX idx_members_user ON workspaces.members(user_id);
CREATE INDEX idx_members_workspace ON workspaces.members(workspace_id);

-- Audit queries
CREATE INDEX idx_audit_actor ON audit.logs(actor_id);
CREATE INDEX idx_audit_resource ON audit.logs(resource_type, resource_id);
CREATE INDEX idx_audit_created ON audit.logs(created_at DESC);
```

---

## Data Retention & Archival

| Data Type         | Retention    | Archival Strategy               |
| ----------------- | ------------ | ------------------------------- |
| User data         | Indefinite   | N/A                             |
| Documents         | Indefinite   | Soft delete, 90-day hard delete |
| Versions          | 100 versions | Archive to object storage       |
| Audit logs        | 2 years      | Archive to cold storage         |
| Collaboration ops | 30 days      | Compact and archive             |
| Analytics         | 1 year       | Aggregate and archive           |

---

## Backup Strategy

### PostgreSQL

-   **Full backup**: Daily at 02:00 UTC
-   **WAL archiving**: Continuous
-   **Retention**: 30 days
-   **Point-in-time recovery**: Available

### Redis

-   **RDB snapshots**: Hourly
-   **AOF persistence**: Enabled
-   **Replication**: 1 replica minimum

---

**Document Status**: ✅ Active  
**Last Updated**: December 2025  
**Authority**: CTO + Database Lead  
**Classification**: Internal - Architecture
