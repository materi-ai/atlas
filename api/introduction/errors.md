# API Errors

<Info>
**SDD Classification:** L3-Technical
**Authority:** Engineering Team
**Review Cycle:** Quarterly
</Info>

This guide covers the error response format, HTTP status codes, error codes, and best practices for handling API errors in your applications.

---

## Error Response Format

All API errors return a consistent JSON structure:

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
    "timestamp": "2025-01-07T10:30:00Z"
  }
}
```

### Error Object Properties

| Property | Type | Description |
|----------|------|-------------|
| `code` | string | Machine-readable error code |
| `message` | string | Human-readable error description |
| `details` | object | Additional context (optional) |
| `request_id` | string | Unique request identifier for support |
| `timestamp` | string | ISO 8601 timestamp |

---

## HTTP Status Codes

### Success Codes (2xx)

| Code | Status | Description |
|------|--------|-------------|
| **200** | OK | Request succeeded |
| **201** | Created | Resource created successfully |
| **204** | No Content | Request succeeded, no response body |

### Client Error Codes (4xx)

| Code | Status | Description | Action |
|------|--------|-------------|--------|
| **400** | Bad Request | Invalid request format | Check request body/parameters |
| **401** | Unauthorized | Missing/invalid authentication | Refresh token or re-authenticate |
| **403** | Forbidden | Insufficient permissions | Check user permissions |
| **404** | Not Found | Resource doesn't exist | Verify resource ID |
| **409** | Conflict | Resource conflict | Retry with fresh data |
| **422** | Unprocessable Entity | Validation failed | Check field values |
| **429** | Too Many Requests | Rate limit exceeded | Wait and retry |

### Server Error Codes (5xx)

| Code | Status | Description | Action |
|------|--------|-------------|--------|
| **500** | Internal Server Error | Unexpected server error | Retry with exponential backoff |
| **502** | Bad Gateway | Upstream service error | Retry after delay |
| **503** | Service Unavailable | Service temporarily unavailable | Retry after Retry-After header |
| **504** | Gateway Timeout | Request timed out | Retry with shorter timeout |

---

## Error Code Reference

### Authentication Errors

| Code | HTTP | Description | Resolution |
|------|------|-------------|------------|
| `INVALID_CREDENTIALS` | 401 | Email or password incorrect | Verify credentials |
| `INVALID_TOKEN` | 401 | JWT token malformed or expired | Refresh token |
| `TOKEN_EXPIRED` | 401 | Access token has expired | Use refresh token |
| `TOKEN_REVOKED` | 401 | Token has been invalidated | Re-authenticate |
| `REFRESH_TOKEN_EXPIRED` | 401 | Refresh token has expired | Re-authenticate |
| `INSUFFICIENT_PERMISSIONS` | 403 | User lacks required permission | Contact admin |
| `ACCOUNT_LOCKED` | 403 | Too many failed login attempts | Wait or reset password |
| `ACCOUNT_SUSPENDED` | 403 | Account disabled by admin | Contact support |
| `INSUFFICIENT_SCOPE` | 403 | Token lacks required OAuth scope | Request additional scopes |

### Resource Errors

| Code | HTTP | Description | Resolution |
|------|------|-------------|------------|
| `DOCUMENT_NOT_FOUND` | 404 | Document doesn't exist | Verify document ID |
| `WORKSPACE_NOT_FOUND` | 404 | Workspace doesn't exist | Verify workspace ID |
| `USER_NOT_FOUND` | 404 | User doesn't exist | Verify user ID |
| `VERSION_NOT_FOUND` | 404 | Document version doesn't exist | List available versions |
| `TEMPLATE_NOT_FOUND` | 404 | Template doesn't exist | Verify template ID |

### Validation Errors

| Code | HTTP | Description | Resolution |
|------|------|-------------|------------|
| `INVALID_REQUEST_BODY` | 400 | Request body is malformed | Check JSON syntax |
| `MISSING_REQUIRED_FIELD` | 400 | Required field not provided | Include all required fields |
| `INVALID_FIELD_VALUE` | 422 | Field value is invalid | Check field constraints |
| `TITLE_TOO_LONG` | 422 | Title exceeds 500 characters | Shorten title |
| `CONTENT_TOO_LARGE` | 422 | Content exceeds 10MB limit | Reduce content size |
| `INVALID_EMAIL_FORMAT` | 422 | Email format incorrect | Provide valid email |
| `INVALID_UUID_FORMAT` | 422 | UUID format incorrect | Provide valid UUID |

### Conflict Errors

| Code | HTTP | Description | Resolution |
|------|------|-------------|------------|
| `VERSION_CONFLICT` | 409 | Document was modified | Fetch latest, retry |
| `DOCUMENT_LOCKED` | 409 | Document being edited | Wait and retry |
| `DUPLICATE_RESOURCE` | 409 | Resource already exists | Use unique identifier |
| `CONCURRENT_MODIFICATION` | 409 | Concurrent edit detected | Merge changes manually |

### Rate Limit Errors

| Code | HTTP | Description | Resolution |
|------|------|-------------|------------|
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests | Wait for Retry-After |
| `AI_QUOTA_EXCEEDED` | 429 | Daily AI limit reached | Upgrade plan or wait |
| `CONCURRENT_LIMIT` | 429 | Too many concurrent connections | Close unused connections |

### Server Errors

| Code | HTTP | Description | Resolution |
|------|------|-------------|------------|
| `INTERNAL_ERROR` | 500 | Unexpected server error | Retry, report if persistent |
| `SERVICE_UNAVAILABLE` | 503 | Service temporarily down | Retry after delay |
| `AI_SERVICE_ERROR` | 503 | AI provider unavailable | Retry or use fallback |
| `DATABASE_ERROR` | 503 | Database connection issue | Retry after delay |

---

## Error Handling Best Practices

### JavaScript/TypeScript Example

```typescript
class MateriAPIError extends Error {
  constructor(
    public status: number,
    public code: string,
    public message: string,
    public details?: Record<string, unknown>,
    public requestId?: string
  ) {
    super(message);
    this.name = 'MateriAPIError';
  }
}

async function handleResponse(response: Response) {
  if (response.ok) {
    return response.json();
  }

  const error = await response.json();
  throw new MateriAPIError(
    response.status,
    error.error.code,
    error.error.message,
    error.error.details,
    error.error.request_id
  );
}

async function apiCall(endpoint: string, options?: RequestInit) {
  try {
    const response = await fetch(`https://api.materi.dev/v1${endpoint}`, {
      ...options,
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });
    return handleResponse(response);
  } catch (error) {
    if (error instanceof MateriAPIError) {
      switch (error.code) {
        case 'TOKEN_EXPIRED':
          await refreshToken();
          return apiCall(endpoint, options);

        case 'RATE_LIMIT_EXCEEDED':
          const retryAfter = 60; // seconds
          await delay(retryAfter * 1000);
          return apiCall(endpoint, options);

        case 'VERSION_CONFLICT':
          // Handle conflict resolution
          throw error;

        default:
          throw error;
      }
    }
    throw error;
  }
}
```

### Retry Strategy with Exponential Backoff

```javascript
async function retryWithBackoff(fn, maxRetries = 3) {
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      const isRetryable = [500, 502, 503, 504, 429].includes(error.status);

      if (!isRetryable || attempt === maxRetries) {
        throw error;
      }

      const delay = Math.pow(2, attempt) * 1000 + Math.random() * 1000;
      console.log(`Retry ${attempt + 1}/${maxRetries} after ${delay}ms`);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
}
```

---

## Validation Error Details

Validation errors include detailed field-level information:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": {
      "fields": [
        {
          "field": "title",
          "code": "TITLE_TOO_LONG",
          "message": "Title must be 500 characters or less",
          "value_provided": "Very long title...",
          "max_length": 500
        },
        {
          "field": "email",
          "code": "INVALID_EMAIL_FORMAT",
          "message": "Email format is invalid",
          "value_provided": "not-an-email"
        }
      ]
    },
    "request_id": "req_abc123"
  }
}
```

---

## Debugging with Request IDs

Every API response includes a unique `request_id`. When contacting support:

1. Note the `request_id` from the error response
2. Include the timestamp of the request
3. Describe the action being performed
4. Provide any relevant context

Example support request:
```
Request ID: req_1234567890abcdef
Timestamp: 2025-01-07T10:30:00Z
Action: Creating document in workspace ws_abc123
Error: INSUFFICIENT_PERMISSIONS
```

---

## Related Documentation

- [API Overview](/api/introduction/overview) - API fundamentals
- [Authentication](/api/introduction/authentication) - Auth error details
- [Rate Limits](/api/introduction/rate-limits) - Rate limit errors

---

**Document Status:** Complete
**Version:** 2.0
