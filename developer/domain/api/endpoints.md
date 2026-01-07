# API Endpoints

<Info>
**SDD Classification:** L3-Technical
**Authority:** Engineering Team
**Review Cycle:** Quarterly
</Info>

This document provides a comprehensive reference for all API endpoints in Materi's API Service, including request/response formats, authentication requirements, and usage examples.

---

## Base URL

| Environment | Base URL |
|-------------|----------|
| Production | `https://api.materi.dev/api/v1` |
| Staging | `https://api.staging.materi.dev/api/v1` |
| Development | `http://localhost:8080/api/v1` |

---

## Document Endpoints

### Create Document

Creates a new document in a workspace.

```
POST /api/v1/documents
```

**Authentication:** Required (JWT or API Key)

**Request Body:**

```json
{
  "title": "My Document",
  "content": "Initial content...",
  "workspace_id": "ws_abc123"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | Yes | Document title (1-255 chars) |
| `content` | string | No | Initial content (max 10MB) |
| `workspace_id` | string | Yes | Target workspace UUID |

**Response:** `201 Created`

```json
{
  "success": true,
  "data": {
    "id": "doc_xyz789",
    "title": "My Document",
    "content": "Initial content...",
    "workspace_id": "ws_abc123",
    "owner_id": "user_abc123",
    "version": 1,
    "created_at": "2025-01-07T10:00:00Z",
    "updated_at": "2025-01-07T10:00:00Z"
  }
}
```

**Errors:**

| Code | Status | Description |
|------|--------|-------------|
| `VALIDATION_ERROR` | 422 | Missing or invalid fields |
| `FORBIDDEN` | 403 | No write access to workspace |
| `WORKSPACE_NOT_FOUND` | 404 | Workspace doesn't exist |

---

### Get Document

Retrieves a document by ID.

```
GET /api/v1/documents/{id}
```

**Authentication:** Required

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | string | Document UUID |

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `include_content` | boolean | true | Include full content |

**Response:** `200 OK`

```json
{
  "success": true,
  "data": {
    "id": "doc_xyz789",
    "title": "My Document",
    "content": "Document content...",
    "workspace_id": "ws_abc123",
    "owner_id": "user_abc123",
    "version": 5,
    "created_at": "2025-01-07T10:00:00Z",
    "updated_at": "2025-01-07T14:30:00Z"
  }
}
```

**Errors:**

| Code | Status | Description |
|------|--------|-------------|
| `NOT_FOUND` | 404 | Document doesn't exist |
| `FORBIDDEN` | 403 | No read access |

---

### Update Document

Partially updates a document.

```
PATCH /api/v1/documents/{id}
```

**Authentication:** Required

**Request Body:**

```json
{
  "title": "Updated Title",
  "content": "Updated content...",
  "version": 5
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | No | New title |
| `content` | string | No | New content |
| `version` | integer | No | Expected version (optimistic lock) |

**Response:** `200 OK`

```json
{
  "success": true,
  "data": {
    "id": "doc_xyz789",
    "title": "Updated Title",
    "content": "Updated content...",
    "version": 6,
    "updated_at": "2025-01-07T15:00:00Z"
  }
}
```

**Errors:**

| Code | Status | Description |
|------|--------|-------------|
| `CONFLICT` | 409 | Version mismatch (concurrent edit) |
| `FORBIDDEN` | 403 | No write access |
| `NOT_FOUND` | 404 | Document doesn't exist |

---

### Delete Document

Soft-deletes a document (recoverable for 30 days).

```
DELETE /api/v1/documents/{id}
```

**Authentication:** Required

**Response:** `204 No Content`

**Errors:**

| Code | Status | Description |
|------|--------|-------------|
| `FORBIDDEN` | 403 | Only owner can delete |
| `NOT_FOUND` | 404 | Document doesn't exist |

---

### List Documents

Lists documents with pagination and filtering.

```
GET /api/v1/documents
```

**Authentication:** Required

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `workspace_id` | string | - | Filter by workspace |
| `page` | integer | 1 | Page number |
| `limit` | integer | 20 | Items per page (max 100) |
| `sort` | string | `updated_at` | Sort field |
| `order` | string | `desc` | Sort order (asc/desc) |
| `owner_id` | string | - | Filter by owner |
| `created_after` | datetime | - | Filter by creation date |
| `created_before` | datetime | - | Filter by creation date |

**Response:** `200 OK`

```json
{
  "success": true,
  "data": [
    {
      "id": "doc_xyz789",
      "title": "My Document",
      "workspace_id": "ws_abc123",
      "owner_id": "user_abc123",
      "version": 5,
      "created_at": "2025-01-07T10:00:00Z",
      "updated_at": "2025-01-07T14:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 42,
    "total_pages": 3,
    "has_more": true
  }
}
```

---

### Search Documents

Full-text search across documents.

```
GET /api/v1/documents/search
```

**Authentication:** Required

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `q` | string | Yes | Search query |
| `workspace_id` | string | No | Filter by workspace |
| `limit` | integer | No | Max results (default 20, max 50) |

**Response:** `200 OK`

```json
{
  "success": true,
  "data": [
    {
      "id": "doc_xyz789",
      "title": "My Document",
      "snippet": "...matching <mark>content</mark> here...",
      "relevance": 0.95,
      "created_at": "2025-01-07T10:00:00Z"
    }
  ],
  "meta": {
    "query": "content",
    "total_results": 5,
    "search_time_ms": 45
  }
}
```

---

## Workspace Endpoints

### Create Workspace

```
POST /api/v1/workspaces
```

**Authentication:** Required

**Request Body:**

```json
{
  "name": "My Team",
  "slug": "my-team"
}
```

**Response:** `201 Created`

```json
{
  "success": true,
  "data": {
    "id": "ws_abc123",
    "name": "My Team",
    "slug": "my-team",
    "owner_id": "user_abc123",
    "settings": {
      "default_permission": "read",
      "allow_public_links": false,
      "ai_enabled": true
    },
    "created_at": "2025-01-07T10:00:00Z"
  }
}
```

---

### Get Workspace

```
GET /api/v1/workspaces/{id}
```

**Response:** `200 OK`

```json
{
  "success": true,
  "data": {
    "id": "ws_abc123",
    "name": "My Team",
    "slug": "my-team",
    "owner_id": "user_abc123",
    "member_count": 5,
    "document_count": 42,
    "settings": {
      "default_permission": "read",
      "allow_public_links": false,
      "ai_enabled": true
    },
    "created_at": "2025-01-07T10:00:00Z"
  }
}
```

---

### List Workspace Members

```
GET /api/v1/workspaces/{id}/members
```

**Response:** `200 OK`

```json
{
  "success": true,
  "data": [
    {
      "user_id": "user_abc123",
      "email": "owner@example.com",
      "name": "John Doe",
      "role": "owner",
      "joined_at": "2025-01-07T10:00:00Z"
    },
    {
      "user_id": "user_def456",
      "email": "member@example.com",
      "name": "Jane Smith",
      "role": "member",
      "joined_at": "2025-01-08T10:00:00Z"
    }
  ]
}
```

---

### Invite Member

```
POST /api/v1/workspaces/{id}/members
```

**Authentication:** Required (Admin or Owner)

**Request Body:**

```json
{
  "email": "newmember@example.com",
  "role": "member"
}
```

**Response:** `201 Created`

```json
{
  "success": true,
  "data": {
    "invitation_id": "inv_abc123",
    "email": "newmember@example.com",
    "role": "member",
    "expires_at": "2025-01-14T10:00:00Z"
  }
}
```

---

## AI Endpoints

### Generate Content

Generates content using AI with streaming response.

```
POST /api/v1/ai/generate
```

**Authentication:** Required

**Headers:**

| Header | Required | Description |
|--------|----------|-------------|
| `Idempotency-Key` | Recommended | Prevent duplicate requests |
| `Accept` | No | `text/event-stream` for streaming |

**Request Body:**

```json
{
  "prompt": "Write an introduction about...",
  "max_tokens": 500,
  "document_id": "doc_xyz789",
  "model": "claude-3-sonnet"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `prompt` | string | Yes | Generation prompt |
| `max_tokens` | integer | No | Max tokens (default 500) |
| `document_id` | string | No | Context document |
| `model` | string | No | AI model to use |
| `temperature` | float | No | Creativity (0-1) |

**Streaming Response:** `200 OK` (text/event-stream)

```
event: content
data: {"text": "Here is ", "done": false}

event: content
data: {"text": "the generated ", "done": false}

event: content
data: {"text": "content.", "done": false}

event: done
data: {"tokens_used": 45, "model": "claude-3-sonnet", "finish_reason": "stop"}
```

**Batch Response:** `200 OK` (application/json)

```json
{
  "success": true,
  "data": {
    "content": "Here is the generated content.",
    "tokens_used": 45,
    "model": "claude-3-sonnet",
    "finish_reason": "stop"
  }
}
```

**Errors:**

| Code | Status | Description |
|------|--------|-------------|
| `RATE_LIMITED` | 429 | AI quota exceeded |
| `AI_SERVICE_UNAVAILABLE` | 503 | AI provider down |
| `CONTENT_POLICY_VIOLATION` | 400 | Content flagged |

---

### Get AI Usage

```
GET /api/v1/ai/usage
```

**Authentication:** Required

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `period` | string | `day`, `week`, `month` |
| `workspace_id` | string | Filter by workspace |

**Response:** `200 OK`

```json
{
  "success": true,
  "data": {
    "period": "month",
    "requests": 150,
    "tokens_used": 75000,
    "cost_usd": 1.50,
    "limit": {
      "requests": 1000,
      "tokens": 500000
    },
    "reset_at": "2025-02-01T00:00:00Z"
  }
}
```

---

## File Endpoints

### Upload File

Get a pre-signed URL for file upload.

```
POST /api/v1/files/upload
```

**Authentication:** Required

**Request Body:**

```json
{
  "filename": "image.png",
  "content_type": "image/png",
  "size": 1048576,
  "document_id": "doc_xyz789"
}
```

**Response:** `200 OK`

```json
{
  "success": true,
  "data": {
    "upload_url": "https://storage.materi.dev/upload?...",
    "file_id": "file_abc123",
    "expires_at": "2025-01-07T11:00:00Z"
  }
}
```

---

### Get File

```
GET /api/v1/files/{id}
```

**Response:** `200 OK`

```json
{
  "success": true,
  "data": {
    "id": "file_abc123",
    "filename": "image.png",
    "content_type": "image/png",
    "size": 1048576,
    "url": "https://cdn.materi.dev/files/...",
    "thumbnail_url": "https://cdn.materi.dev/thumbs/...",
    "created_at": "2025-01-07T10:00:00Z"
  }
}
```

---

## Authentication Endpoints

### Refresh Token

```
POST /api/v1/auth/refresh
```

**Authentication:** Refresh token in HTTP-only cookie

**Response:** `200 OK`

```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJSUzI1NiIs...",
    "expires_in": 900
  }
}
```

---

### Logout

```
POST /api/v1/auth/logout
```

**Authentication:** Required

**Response:** `204 No Content`

---

## Health Endpoints

### Health Check

```
GET /health
```

**Authentication:** None

**Response:** `200 OK`

```json
{
  "status": "healthy",
  "version": "1.2.3",
  "uptime": 86400
}
```

---

### Readiness Check

```
GET /ready
```

**Authentication:** None

**Response:** `200 OK`

```json
{
  "status": "ready",
  "checks": {
    "database": "ok",
    "redis": "ok",
    "shield": "ok"
  }
}
```

**Response:** `503 Service Unavailable` (if dependencies unhealthy)

```json
{
  "status": "not_ready",
  "checks": {
    "database": "ok",
    "redis": "error: connection refused",
    "shield": "ok"
  }
}
```

---

### Metrics

```
GET /metrics
```

**Authentication:** None (internal network only)

**Response:** `200 OK` (text/plain, Prometheus format)

```
# HELP materi_http_requests_total Total HTTP requests
# TYPE materi_http_requests_total counter
materi_http_requests_total{method="GET",endpoint="/api/v1/documents",status="200"} 12345
materi_http_requests_total{method="POST",endpoint="/api/v1/documents",status="201"} 678

# HELP materi_http_duration_seconds HTTP request duration
# TYPE materi_http_duration_seconds histogram
materi_http_duration_seconds_bucket{method="GET",endpoint="/api/v1/documents",le="0.1"} 11000
materi_http_duration_seconds_bucket{method="GET",endpoint="/api/v1/documents",le="0.25"} 12000
```

---

## Error Response Format

All errors follow a consistent format:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable description",
    "details": {
      "field": "Additional context"
    }
  },
  "meta": {
    "request_id": "req_xyz789"
  }
}
```

### Common Error Codes

| Code | Status | Description |
|------|--------|-------------|
| `UNAUTHORIZED` | 401 | Missing or invalid auth |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `VALIDATION_ERROR` | 422 | Invalid request body |
| `CONFLICT` | 409 | Resource conflict |
| `RATE_LIMITED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |
| `SERVICE_UNAVAILABLE` | 503 | Dependency unavailable |

---

## Related Documentation

- [Overview](overview) - Service overview
- [Authentication](authentication) - Auth flows
- [Rate Limiting](rate-limiting) - Request limits
- [Architecture](architecture) - System design

---

**Document Status:** Complete
**Version:** 2.0
