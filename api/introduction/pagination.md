# API Pagination

<Info>
**SDD Classification:** L3-Technical
**Authority:** Engineering Team
**Review Cycle:** Quarterly
</Info>

Materi uses cursor-based pagination for efficient traversal of large datasets. This guide covers pagination patterns, parameters, and best practices.

---

## Pagination Overview

```mermaid
flowchart LR
    A[First Request] --> B[Page 1 + Cursor]
    B --> C[Next Request with Cursor]
    C --> D[Page 2 + Cursor]
    D --> E[Continue...]
    E --> F[Last Page - No Cursor]
```

### Why Cursor-Based Pagination?

| Feature | Cursor-Based | Offset-Based |
|---------|--------------|--------------|
| **Performance** | O(1) | O(n) with offset |
| **Consistency** | Stable across changes | Duplicates/skips possible |
| **Real-time data** | Handles insertions well | Breaks on insertions |
| **Deep pagination** | Efficient at any depth | Slow for large offsets |

---

## Basic Usage

### Request Format

```bash
GET /api/v1/documents?limit=20&cursor=eyJpZCI6MTIzfQ
Authorization: Bearer <token>
```

### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 20 | Items per page (1-100) |
| `cursor` | string | null | Pagination cursor from previous response |
| `sort` | string | `created_at` | Sort field |
| `order` | string | `desc` | Sort order (`asc` or `desc`) |

### Response Format

```json
{
  "data": [
    {
      "id": "doc_abc123",
      "title": "Document 1",
      "created_at": "2025-01-07T10:00:00Z"
    },
    {
      "id": "doc_def456",
      "title": "Document 2",
      "created_at": "2025-01-07T09:30:00Z"
    }
  ],
  "pagination": {
    "cursor": "eyJpZCI6ImRvY19kZWY0NTYiLCJjcmVhdGVkX2F0IjoiMjAyNS0wMS0wN1QwOTozMDowMFoifQ",
    "has_more": true,
    "total_count": 156,
    "limit": 20
  }
}
```

### Pagination Object

| Field | Type | Description |
|-------|------|-------------|
| `cursor` | string | Cursor for next page (null if last page) |
| `has_more` | boolean | Whether more pages exist |
| `total_count` | integer | Total items matching query (optional) |
| `limit` | integer | Items per page |

---

## Cursor Structure

Cursors are base64-encoded JSON containing sort field values:

```json
// Decoded cursor example
{
  "id": "doc_def456",
  "created_at": "2025-01-07T09:30:00Z",
  "v": 1
}
```

<Warning>
Cursors are opaque tokens. Never construct or modify cursors manually. Always use the cursor value returned by the API.
</Warning>

---

## Pagination Examples

### JavaScript

```javascript
async function fetchAllDocuments(workspaceId) {
  const documents = [];
  let cursor = null;

  do {
    const params = new URLSearchParams({
      workspace_id: workspaceId,
      limit: '100',
      ...(cursor && { cursor }),
    });

    const response = await fetch(
      `https://api.materi.dev/v1/documents?${params}`,
      {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
        },
      }
    );

    const { data, pagination } = await response.json();
    documents.push(...data);
    cursor = pagination.cursor;

  } while (cursor);

  return documents;
}
```

### Python

```python
import requests

def fetch_all_documents(workspace_id: str, access_token: str) -> list:
    documents = []
    cursor = None

    while True:
        params = {
            'workspace_id': workspace_id,
            'limit': 100,
        }
        if cursor:
            params['cursor'] = cursor

        response = requests.get(
            'https://api.materi.dev/v1/documents',
            headers={'Authorization': f'Bearer {access_token}'},
            params=params
        )
        response.raise_for_status()

        data = response.json()
        documents.extend(data['data'])

        cursor = data['pagination'].get('cursor')
        if not cursor:
            break

    return documents
```

### Async Generator Pattern

```javascript
async function* paginatedDocuments(workspaceId) {
  let cursor = null;

  do {
    const params = new URLSearchParams({
      workspace_id: workspaceId,
      limit: '50',
      ...(cursor && { cursor }),
    });

    const response = await fetch(
      `https://api.materi.dev/v1/documents?${params}`,
      { headers: { 'Authorization': `Bearer ${accessToken}` } }
    );

    const { data, pagination } = await response.json();

    for (const document of data) {
      yield document;
    }

    cursor = pagination.cursor;
  } while (cursor);
}

// Usage
for await (const doc of paginatedDocuments('ws_123')) {
  console.log(doc.title);
}
```

---

## Sorting

### Available Sort Fields

| Endpoint | Sort Fields |
|----------|-------------|
| `/documents` | `created_at`, `updated_at`, `title` |
| `/workspaces` | `created_at`, `updated_at`, `name` |
| `/users` | `created_at`, `name`, `email` |
| `/versions` | `created_at`, `version_number` |

### Sort Order

```bash
# Newest first (default)
GET /api/v1/documents?sort=created_at&order=desc

# Oldest first
GET /api/v1/documents?sort=created_at&order=asc

# Alphabetical by title
GET /api/v1/documents?sort=title&order=asc
```

<Warning>
When changing sort parameters, you must start pagination from the beginning. Previous cursors become invalid when sort order changes.
</Warning>

---

## Filtering with Pagination

Filters can be combined with pagination:

```bash
GET /api/v1/documents?workspace_id=ws_123&status=published&limit=20&cursor=abc123
```

### Common Filters

| Endpoint | Available Filters |
|----------|-------------------|
| `/documents` | `workspace_id`, `status`, `owner_id`, `created_after`, `created_before` |
| `/workspaces` | `owner_id`, `member_id` |
| `/versions` | `document_id`, `created_after` |
| `/comments` | `document_id`, `resolved`, `author_id` |

### Filter Examples

```javascript
// Documents in a workspace, created this week
const params = new URLSearchParams({
  workspace_id: 'ws_123',
  created_after: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
  limit: '50',
});

// Published documents only
const params = new URLSearchParams({
  status: 'published',
  sort: 'updated_at',
  order: 'desc',
});
```

---

## Total Count Behavior

The `total_count` field behavior varies by endpoint:

| Scenario | `total_count` Included | Notes |
|----------|------------------------|-------|
| Small datasets (<1000) | Yes | Always included |
| Large datasets (>1000) | Optional | Use `include_total=true` |
| Search results | No | Too expensive to compute |
| Filtered queries | Yes | When dataset is bounded |

### Requesting Total Count

```bash
# Include total count for large datasets
GET /api/v1/documents?limit=20&include_total=true
```

<Warning>
Requesting `total_count` on very large datasets may impact performance. Use sparingly and consider caching the result.
</Warning>

---

## Bidirectional Pagination

Some endpoints support backward pagination:

```bash
# Forward (default)
GET /api/v1/documents?cursor=abc&direction=forward

# Backward
GET /api/v1/documents?cursor=abc&direction=backward
```

### Bidirectional Response

```json
{
  "data": [...],
  "pagination": {
    "next_cursor": "eyJkaXIiOiJmb3J3YXJkIi4uLn0",
    "prev_cursor": "eyJkaXIiOiJiYWNrd2FyZCIuLi59",
    "has_next": true,
    "has_prev": true
  }
}
```

---

## Pagination Best Practices

### Do

1. **Use reasonable page sizes** - Default to 20-50 items
2. **Store cursors temporarily** - For "load more" UIs
3. **Handle empty results** - `data: []` with `has_more: false`
4. **Implement retry logic** - For transient failures during pagination

### Don't

1. **Don't decode cursors** - Treat as opaque tokens
2. **Don't persist cursors long-term** - They may expire
3. **Don't mix sort parameters** - Invalidates cursors
4. **Don't request huge page sizes** - Max is 100 for performance

### UI Patterns

```javascript
// Infinite scroll implementation
class InfiniteScroll {
  constructor(containerEl, fetchFn) {
    this.container = containerEl;
    this.fetchFn = fetchFn;
    this.cursor = null;
    this.loading = false;
    this.hasMore = true;

    this.setupObserver();
  }

  setupObserver() {
    const sentinel = document.createElement('div');
    sentinel.className = 'scroll-sentinel';
    this.container.appendChild(sentinel);

    const observer = new IntersectionObserver(
      entries => {
        if (entries[0].isIntersecting && !this.loading && this.hasMore) {
          this.loadMore();
        }
      },
      { rootMargin: '100px' }
    );

    observer.observe(sentinel);
  }

  async loadMore() {
    this.loading = true;

    try {
      const { data, pagination } = await this.fetchFn(this.cursor);

      data.forEach(item => this.renderItem(item));

      this.cursor = pagination.cursor;
      this.hasMore = pagination.has_more;
    } finally {
      this.loading = false;
    }
  }

  renderItem(item) {
    // Implement item rendering
  }
}
```

---

## Error Handling

### Invalid Cursor

```json
{
  "error": {
    "code": "INVALID_CURSOR",
    "message": "The provided cursor is invalid or has expired",
    "details": {
      "cursor": "invalid_cursor_value"
    }
  }
}
```

**Resolution:** Start pagination from the beginning without a cursor.

### Cursor Expired

```json
{
  "error": {
    "code": "CURSOR_EXPIRED",
    "message": "The cursor has expired. Please start from the beginning.",
    "details": {
      "expired_at": "2025-01-07T08:00:00Z"
    }
  }
}
```

**Resolution:** Cursors expire after 24 hours. Restart pagination.

---

## Performance Tips

1. **Choose appropriate limits**: Larger limits = fewer requests but more data per request
2. **Use streaming for exports**: For very large datasets, use export endpoints
3. **Cache page results**: If data doesn't change frequently
4. **Parallelize carefully**: Respect rate limits when paginating multiple resources

```javascript
// Parallel pagination with rate limiting
async function paginateMultiple(workspaceIds) {
  const results = {};

  // Process in batches of 5 to respect rate limits
  for (let i = 0; i < workspaceIds.length; i += 5) {
    const batch = workspaceIds.slice(i, i + 5);

    const batchResults = await Promise.all(
      batch.map(id => fetchAllDocuments(id))
    );

    batch.forEach((id, idx) => {
      results[id] = batchResults[idx];
    });

    // Small delay between batches
    if (i + 5 < workspaceIds.length) {
      await new Promise(r => setTimeout(r, 200));
    }
  }

  return results;
}
```

---

## Related Documentation

- [API Overview](/api/introduction/overview) - API fundamentals
- [Rate Limits](/api/introduction/rate-limits) - Request limits
- [Errors](/api/introduction/errors) - Error handling

---

**Document Status:** Complete
**Version:** 2.0
