# API Overview

<Info>
**SDD Classification:** L3-Technical
**Authority:** Engineering Team
**Review Cycle:** Quarterly
</Info>

Materi provides comprehensive REST and WebSocket APIs that enable you to integrate document collaboration, AI generation, and real-time editing into your applications. Build custom workflows, automate content creation, and embed Materi's capabilities directly into your products.

---

## API Architecture

```mermaid
flowchart TD
    A[Your Application] --> B[Materi API Gateway]
    B --> C[REST API Endpoints]
    B --> D[WebSocket Connections]
    B --> E[Authentication Service]

    subgraph "REST API Services"
        C1[Documents API]
        C2[Workspaces API]
        C3[Users API]
        C4[AI Generation API]
        C5[Templates API]
    end

    subgraph "Real-time Services"
        D1[Collaboration WebSocket]
        D2[Presence Updates]
        D3[Live Cursor Tracking]
        D4[Comment Threads]
    end

    C --> C1
    C --> C2
    C --> C3
    C --> C4
    C --> C5

    D --> D1
    D --> D2
    D --> D3
    D --> D4
```

### Key API Features

| Feature | Description |
|---------|-------------|
| **RESTful Design** | Standard HTTP methods and status codes |
| **JSON-First** | All requests and responses use JSON |
| **Real-time WebSockets** | Live collaboration and updates |
| **JWT Authentication** | Tokens with refresh capabilities |
| **Rate Limiting** | Fair usage policies with burst allowances |
| **Webhook Support** | Event-driven integrations |
| **Multi-language SDKs** | Official libraries for popular languages |

---

## Base URLs

### Production Environment

| Property | Value |
|----------|-------|
| **Base URL** | `https://api.materi.dev/v1` |
| **WebSocket URL** | `wss://api.materi.dev/v1/ws` |
| **Region** | Global with edge caching |
| **TLS** | Required (TLS 1.3) |

### Development Environment

| Property | Value |
|----------|-------|
| **Base URL** | `https://api-staging.materi.dev/v1` |
| **WebSocket URL** | `wss://api-staging.materi.dev/v1/ws` |
| **Purpose** | Testing and development |
| **Data** | Isolated from production |

---

## Authentication Overview

Materi uses JWT (JSON Web Tokens) for secure, stateless authentication across all API endpoints.

```mermaid
sequenceDiagram
    participant C as Client App
    participant A as Auth API
    participant R as Resource API
    participant DB as Database

    C->>A: POST /auth/login {email, password}
    A->>DB: Validate credentials
    DB-->>A: User data
    A-->>C: {access_token, refresh_token}

    Note over C: Store tokens securely

    C->>R: GET /documents<br/>Authorization: Bearer {access_token}
    R->>R: Validate JWT
    R-->>C: Documents data

    Note over C: Token expires (15 min)

    C->>A: POST /auth/refresh {refresh_token}
    A-->>C: {new_access_token, new_refresh_token}
```

### Token Types

| Token Type | Expiration | Purpose |
|------------|------------|---------|
| **Access Token** | 15 minutes | API request authorization |
| **Refresh Token** | 30 days | Obtain new access tokens |
| **Collaboration Token** | 60 minutes | WebSocket sessions |

### Authentication Methods

**Method A: User Authentication (OAuth 2.0)**

For applications acting on behalf of users with delegated authorization.

```javascript
// Redirect user to authorization URL
const authUrl = `https://api.materi.dev/oauth/authorize?
  client_id=${CLIENT_ID}&
  response_type=code&
  scope=documents:read documents:write&
  redirect_uri=${CALLBACK_URL}`;

// Exchange authorization code for tokens
const response = await fetch("https://api.materi.dev/oauth/token", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
        grant_type: "authorization_code",
        client_id: CLIENT_ID,
        client_secret: CLIENT_SECRET,
        code: authorizationCode,
        redirect_uri: CALLBACK_URL,
    }),
});

const { access_token, refresh_token } = await response.json();
```

**Method B: Service Authentication (Client Credentials)**

For server-to-server integrations without user context.

```javascript
// For server-to-server integrations
const response = await fetch("https://api.materi.dev/oauth/token", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
        grant_type: "client_credentials",
        client_id: CLIENT_ID,
        client_secret: CLIENT_SECRET,
        scope: "documents:read workspaces:read",
    }),
});

const { access_token } = await response.json();
```

### Using Access Tokens

Include the token in the Authorization header for all API requests:

```bash
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## Rate Limiting

```mermaid
flowchart LR
    A[API Request] --> B{Check Limits}
    B -->|Within Limits| C[Process Request]
    B -->|Exceeds Limits| D[Return 429 Error]

    C --> E[Update Counters]
    D --> F[Include Retry Headers]

    subgraph "Rate Limit Tiers"
        G[Free: 1000/hour]
        H[Pro: 10000/hour]
        I[Enterprise: Custom]
    end
```

### Rate Limits by Plan

| Plan | Requests/Hour | Burst Allowance | AI Requests/Day |
|------|---------------|-----------------|-----------------|
| **Free** | 1,000 | 100 | 100 |
| **Professional** | 10,000 | 500 | 1,000 |
| **Enterprise** | Custom | Custom | Unlimited |

### Rate Limit Headers

Every API response includes rate limit information:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 742
X-RateLimit-Reset: 1609459200
X-RateLimit-Retry-After: 3600
```

### Handling Rate Limits

```javascript
const rateLimitedApiCall = async (endpoint, options = {}) => {
    const response = await fetch(`https://api.materi.dev/v1${endpoint}`, {
        ...options,
        headers: {
            Authorization: `Bearer ${accessToken}`,
            "Content-Type": "application/json",
        },
    });

    if (response.status === 429) {
        const retryAfter = parseInt(response.headers.get("X-RateLimit-Retry-After"));
        console.warn(`Rate limit exceeded. Retry after ${retryAfter} seconds`);

        // Implement exponential backoff
        await new Promise((resolve) => setTimeout(resolve, retryAfter * 1000));
        return rateLimitedApiCall(endpoint, options);
    }

    return response.json();
};
```

---

## Error Handling

### Standard Error Response Format

All API errors follow a consistent format:

```json
{
    "error": {
        "code": "DOCUMENT_NOT_FOUND",
        "message": "The requested document could not be found",
        "details": {
            "document_id": "123e4567-e89b-12d3-a456-426614174000",
            "workspace_id": "workspace_abc123"
        },
        "request_id": "req_1234567890abcdef",
        "timestamp": "2025-01-15T10:30:00Z"
    }
}
```

### HTTP Status Codes

| Status | Meaning | Common Causes |
|--------|---------|---------------|
| **200** | Success | Request completed successfully |
| **201** | Created | Resource created successfully |
| **400** | Bad Request | Invalid request format or parameters |
| **401** | Unauthorized | Missing or invalid authentication |
| **403** | Forbidden | Insufficient permissions |
| **404** | Not Found | Resource doesn't exist |
| **409** | Conflict | Resource conflict (e.g., concurrent edit) |
| **422** | Unprocessable Entity | Valid format but invalid data |
| **429** | Rate Limited | Too many requests |
| **500** | Server Error | Internal server error |
| **503** | Service Unavailable | Temporary service outage |

### Error Codes Reference

**Authentication Errors:**
- `INVALID_TOKEN` - JWT token is malformed or expired
- `INSUFFICIENT_PERMISSIONS` - User lacks required permissions
- `ACCOUNT_SUSPENDED` - User account is temporarily disabled

**Resource Errors:**
- `DOCUMENT_NOT_FOUND` - Document ID doesn't exist or no access
- `WORKSPACE_NOT_FOUND` - Workspace doesn't exist or no access
- `USER_NOT_FOUND` - User ID doesn't exist in workspace

**Validation Errors:**
- `INVALID_DOCUMENT_CONTENT` - Document content format is invalid
- `TITLE_TOO_LONG` - Document title exceeds maximum length
- `INVALID_EMAIL_FORMAT` - Email address format is incorrect

**Conflict Errors:**
- `DOCUMENT_LOCKED` - Document is locked by another operation
- `VERSION_CONFLICT` - Document version has changed during edit
- `DUPLICATE_RESOURCE` - Resource with same identifier already exists

---

## Quick Start Example

```javascript
class MateriAPI {
    constructor(accessToken) {
        this.baseURL = "https://api.materi.dev/v1";
        this.accessToken = accessToken;
    }

    async request(endpoint, options = {}) {
        const response = await fetch(`${this.baseURL}${endpoint}`, {
            ...options,
            headers: {
                Authorization: `Bearer ${this.accessToken}`,
                "Content-Type": "application/json",
                ...options.headers,
            },
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(`API Error ${response.status}: ${error.error.message}`);
        }

        return response.json();
    }

    // Document operations
    async getDocuments(workspaceId = null) {
        const params = workspaceId ? `?workspace_id=${workspaceId}` : "";
        return this.request(`/documents${params}`);
    }

    async createDocument(data) {
        return this.request("/documents", {
            method: "POST",
            body: JSON.stringify(data),
        });
    }

    async getDocument(documentId) {
        return this.request(`/documents/${documentId}`);
    }

    async updateDocument(documentId, data) {
        return this.request(`/documents/${documentId}`, {
            method: "PATCH",
            body: JSON.stringify(data),
        });
    }

    // AI generation
    async generateContent(prompt, options = {}) {
        return this.request("/ai/generate", {
            method: "POST",
            body: JSON.stringify({ prompt, ...options }),
        });
    }
}

// Usage example
const api = new MateriAPI("your_access_token_here");

// Create a new document
const newDocument = await api.createDocument({
    title: "My API Document",
    content: "This document was created via the Materi API!",
    workspace_id: "workspace_123",
});

console.log("Created document:", newDocument.id);

// Generate AI content
const aiContent = await api.generateContent(
    "Write a summary of renewable energy benefits",
    { max_tokens: 500 }
);

console.log("Generated content:", aiContent.content);
```

---

## SDKs and Libraries

### Official SDKs

**JavaScript/TypeScript**

```bash
npm install @materi/api-client
```

```javascript
import { MateriAPI } from "@materi/api-client";

const client = new MateriAPI({
    accessToken: "your_token",
    environment: "production",
});

const documents = await client.documents.list();
```

**Python**

```bash
pip install materi-python
```

```python
from materi import MateriClient

client = MateriClient(access_token='your_token')
documents = client.documents.list()
```

**Go**

```bash
go get github.com/materi/materi-go
```

```go
import "github.com/materi/materi-go"

client := materi.NewClient("your_token")
documents, err := client.Documents.List(ctx)
```

---

## API Endpoints Summary

### Documents

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/documents` | Create document |
| `GET` | `/api/v1/documents/{id}` | Get document |
| `PATCH` | `/api/v1/documents/{id}` | Update document |
| `DELETE` | `/api/v1/documents/{id}` | Delete document |
| `GET` | `/api/v1/documents` | List documents |
| `GET` | `/api/v1/documents/search` | Search documents |

### AI Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/ai/generate` | Generate content (SSE) |
| `POST` | `/api/v1/ai/complete` | Autocomplete |
| `GET` | `/api/v1/ai/suggestions` | Get AI suggestions |

### Collaboration

| Method | Endpoint | Description |
|--------|----------|-------------|
| `WS` | `/api/v1/collab/document/{id}` | WebSocket connection |
| `GET` | `/api/v1/collab/presence/{id}` | Active users |

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/auth/refresh` | Refresh access token |
| `POST` | `/api/v1/auth/logout` | Revoke tokens |

### Health & Monitoring

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/ready` | Readiness check |
| `GET` | `/metrics` | Prometheus metrics |

---

## Related Documentation

- [Authentication](/api/introduction/authentication) - Detailed authentication guide
- [Rate Limits](/api/introduction/rate-limits) - Rate limiting policies
- [Errors](/api/introduction/errors) - Complete error reference
- [WebSocket API](/api/websocket/overview) - Real-time collaboration

---

**Document Status:** Complete
**Version:** 2.0
