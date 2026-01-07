# WebSocket Protocol

<Info>
**SDD Classification:** L3-Technical
**Authority:** Engineering Team
**Review Cycle:** Quarterly
</Info>

This document defines the WebSocket protocol specification for Relay's real-time collaboration service, including message formats, handshake flow, connection lifecycle, and error handling.

---

## Protocol Overview

```mermaid
flowchart TD
    subgraph "Connection Phase"
        A[HTTP Upgrade Request] --> B{Token Valid?}
        B -->|Yes| C[WebSocket Established]
        B -->|No| D[401 Unauthorized]
        C --> E[Join Document Room]
        E --> F[Receive Initial State]
    end

    subgraph "Active Session"
        F --> G[Bidirectional Messages]
        G -->|Client→Server| H[Operations, Presence, Heartbeat]
        G -->|Server→Client| I[Broadcasts, Acks, Updates]
    end

    subgraph "Termination"
        H --> J{Connection Alive?}
        I --> J
        J -->|Heartbeat Timeout| K[Close Connection]
        J -->|Client Close| K
        K --> L[Cleanup Resources]
    end
```

---

## Connection Establishment

### WebSocket Endpoint

```
wss://relay.materi.dev/collab/document/{document_id}
```

### Handshake Request

```http
GET /collab/document/doc_abc123 HTTP/1.1
Host: relay.materi.dev
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13
Sec-WebSocket-Protocol: materi-collab-v1
Authorization: Bearer eyJhbGciOiJSUzI1NiIs...
```

### Handshake Response

```http
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
Sec-WebSocket-Protocol: materi-collab-v1
```

### Connection Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `document_id` | Target document UUID | `doc_abc123` |
| `token` | JWT access token (query or header) | `?token=eyJ...` |
| `client_id` | Unique client identifier | Auto-generated UUID |
| `reconnect_id` | Session ID for reconnection | Previous session ID |

---

## Message Format

### Binary Frame Structure

All messages use binary WebSocket frames with Protocol Buffer encoding:

```
┌────────────────┬────────────────┬─────────────────────┐
│ Message Type   │ Sequence ID    │ Payload (protobuf)  │
│ (1 byte)       │ (4 bytes)      │ (variable)          │
└────────────────┴────────────────┴─────────────────────┘
```

### Message Types

| Type | Code | Direction | Description |
|------|------|-----------|-------------|
| `OPERATION` | 0x01 | Bidirectional | Document operation |
| `OPERATION_ACK` | 0x02 | Server→Client | Operation acknowledgment |
| `PRESENCE` | 0x03 | Client→Server | Presence update |
| `PRESENCE_BROADCAST` | 0x04 | Server→Client | Presence broadcast |
| `CURSOR` | 0x05 | Client→Server | Cursor position |
| `CURSOR_BROADCAST` | 0x06 | Server→Client | Cursor broadcast |
| `HEARTBEAT` | 0x07 | Bidirectional | Connection keepalive |
| `SYNC_REQUEST` | 0x08 | Client→Server | State sync request |
| `SYNC_RESPONSE` | 0x09 | Server→Client | Full state sync |
| `ERROR` | 0x0F | Server→Client | Error message |

### Protocol Buffer Definitions

```protobuf
syntax = "proto3";

message Operation {
  string id = 1;
  string document_id = 2;
  string actor_id = 3;
  uint64 timestamp = 4;
  VectorClock vector_clock = 5;
  oneof op_type {
    InsertOp insert = 6;
    DeleteOp delete = 7;
    FormatOp format = 8;
    RetainOp retain = 9;
  }
}

message InsertOp {
  uint32 position = 1;
  string content = 2;
  map<string, string> attributes = 3;
}

message DeleteOp {
  uint32 position = 1;
  uint32 length = 2;
}

message FormatOp {
  uint32 position = 1;
  uint32 length = 2;
  map<string, string> attributes = 3;
}

message RetainOp {
  uint32 length = 1;
}

message VectorClock {
  map<string, uint64> clocks = 1;
}

message PresenceUpdate {
  string user_id = 1;
  string document_id = 2;
  PresenceState state = 3;
  CursorPosition cursor = 4;
  Selection selection = 5;
  uint64 timestamp = 6;
}

message PresenceState {
  bool online = 1;
  bool typing = 2;
  bool focused = 3;
  string activity = 4;  // "editing", "viewing", "idle"
}

message CursorPosition {
  uint32 line = 1;
  uint32 column = 2;
  uint32 offset = 3;
}

message Selection {
  CursorPosition anchor = 1;
  CursorPosition head = 2;
}

message OperationAck {
  string operation_id = 1;
  VectorClock server_clock = 2;
  bool success = 3;
  string error = 4;
}

message ErrorMessage {
  uint32 code = 1;
  string message = 2;
  string details = 3;
  bool recoverable = 4;
}
```

---

## Client-to-Server Messages

### Operation Message

Sent when user performs an edit:

```json
{
  "type": "operation",
  "id": "op_123456",
  "document_id": "doc_abc123",
  "actor_id": "user_789",
  "vector_clock": {"user_789": 42, "user_456": 38},
  "operation": {
    "insert": {
      "position": 150,
      "content": "Hello, World!",
      "attributes": {"bold": "true"}
    }
  }
}
```

### Presence Update

Sent when user presence changes:

```json
{
  "type": "presence",
  "user_id": "user_789",
  "document_id": "doc_abc123",
  "state": {
    "online": true,
    "typing": true,
    "focused": true,
    "activity": "editing"
  },
  "timestamp": 1704067200000
}
```

### Cursor Update

Sent on cursor movement:

```json
{
  "type": "cursor",
  "user_id": "user_789",
  "document_id": "doc_abc123",
  "cursor": {
    "line": 10,
    "column": 25,
    "offset": 450
  },
  "selection": {
    "anchor": {"line": 10, "column": 20, "offset": 445},
    "head": {"line": 10, "column": 30, "offset": 455}
  }
}
```

### Heartbeat

Sent every 30 seconds:

```json
{
  "type": "heartbeat",
  "timestamp": 1704067200000,
  "client_id": "client_xyz"
}
```

### Sync Request

Request full document state:

```json
{
  "type": "sync_request",
  "document_id": "doc_abc123",
  "last_known_clock": {"user_789": 40, "user_456": 35}
}
```

---

## Server-to-Client Messages

### Operation Broadcast

Broadcast operation from another user:

```json
{
  "type": "operation_broadcast",
  "operation": {
    "id": "op_987654",
    "actor_id": "user_456",
    "vector_clock": {"user_789": 42, "user_456": 39},
    "insert": {
      "position": 200,
      "content": "New text"
    }
  },
  "transformed": true
}
```

### Operation Acknowledgment

Confirm operation receipt:

```json
{
  "type": "operation_ack",
  "operation_id": "op_123456",
  "server_clock": {"user_789": 43, "user_456": 39},
  "success": true
}
```

### Presence Broadcast

Broadcast presence changes:

```json
{
  "type": "presence_broadcast",
  "users": [
    {
      "user_id": "user_456",
      "name": "Alice",
      "avatar_url": "https://...",
      "state": {"online": true, "typing": false, "activity": "viewing"},
      "cursor": {"line": 5, "column": 10, "offset": 200}
    }
  ]
}
```

### Sync Response

Full document state:

```json
{
  "type": "sync_response",
  "document_id": "doc_abc123",
  "content": "Full document content...",
  "vector_clock": {"user_789": 43, "user_456": 39},
  "operations_since": [/* missed operations */],
  "active_users": [/* current collaborators */]
}
```

### Error Message

```json
{
  "type": "error",
  "code": 4003,
  "message": "Permission denied",
  "details": "User does not have write access to this document",
  "recoverable": false
}
```

---

## Connection Lifecycle

### State Machine

```mermaid
stateDiagram-v2
    [*] --> Connecting: WebSocket Open
    Connecting --> Authenticating: Connection Established
    Authenticating --> Syncing: Auth Success
    Authenticating --> Closed: Auth Failed
    Syncing --> Active: Sync Complete
    Active --> Active: Operations/Presence
    Active --> Reconnecting: Connection Lost
    Reconnecting --> Syncing: Reconnected
    Reconnecting --> Closed: Max Retries
    Active --> Closed: Clean Disconnect
    Closed --> [*]
```

### Connection States

| State | Description | Client Action |
|-------|-------------|---------------|
| `CONNECTING` | Opening WebSocket | Wait for open event |
| `AUTHENTICATING` | Validating JWT | Wait for auth response |
| `SYNCING` | Loading document state | Wait for sync_response |
| `ACTIVE` | Ready for operations | Send/receive messages |
| `RECONNECTING` | Attempting reconnect | Exponential backoff |
| `CLOSED` | Connection terminated | Cleanup resources |

### Reconnection Strategy

```javascript
const RECONNECT_CONFIG = {
  initialDelay: 1000,      // 1 second
  maxDelay: 30000,         // 30 seconds
  multiplier: 1.5,
  maxRetries: 10,
  jitter: 0.1              // 10% random jitter
};

function calculateBackoff(attempt) {
  const delay = Math.min(
    RECONNECT_CONFIG.initialDelay * Math.pow(RECONNECT_CONFIG.multiplier, attempt),
    RECONNECT_CONFIG.maxDelay
  );
  const jitter = delay * RECONNECT_CONFIG.jitter * (Math.random() * 2 - 1);
  return delay + jitter;
}
```

---

## Heartbeat Protocol

### Configuration

| Parameter | Value | Description |
|-----------|-------|-------------|
| Interval | 30 seconds | Client sends heartbeat |
| Timeout | 60 seconds | Server closes if no response |
| Grace Period | 5 seconds | Buffer before timeout |

### Heartbeat Flow

```mermaid
sequenceDiagram
    participant C as Client
    participant S as Server

    loop Every 30s
        C->>S: HEARTBEAT
        S-->>C: HEARTBEAT (pong)
    end

    Note over C,S: If no heartbeat for 60s
    S->>C: Close (4008 Heartbeat Timeout)
```

### Implementation

```rust
// Server-side heartbeat monitoring
pub struct HeartbeatMonitor {
    last_heartbeat: Instant,
    timeout: Duration,
}

impl HeartbeatMonitor {
    pub fn new() -> Self {
        Self {
            last_heartbeat: Instant::now(),
            timeout: Duration::from_secs(60),
        }
    }

    pub fn record_heartbeat(&mut self) {
        self.last_heartbeat = Instant::now();
    }

    pub fn is_expired(&self) -> bool {
        self.last_heartbeat.elapsed() > self.timeout
    }
}
```

---

## Error Codes

### WebSocket Close Codes

| Code | Name | Description |
|------|------|-------------|
| 4000 | `BAD_REQUEST` | Malformed message |
| 4001 | `UNAUTHORIZED` | Invalid or expired token |
| 4002 | `TOKEN_EXPIRED` | Token needs refresh |
| 4003 | `FORBIDDEN` | Insufficient permissions |
| 4004 | `NOT_FOUND` | Document not found |
| 4005 | `CONFLICT` | Unresolvable conflict |
| 4006 | `RATE_LIMITED` | Too many messages |
| 4007 | `INTERNAL_ERROR` | Server error |
| 4008 | `HEARTBEAT_TIMEOUT` | No heartbeat received |
| 4009 | `CONNECTION_REPLACED` | New connection from same user |
| 4010 | `SERVER_SHUTDOWN` | Graceful server shutdown |

### Error Response Format

```json
{
  "type": "error",
  "code": 4001,
  "message": "Authentication failed",
  "details": "JWT token signature verification failed",
  "recoverable": true,
  "retry_after": 5000
}
```

---

## Rate Limiting

### Limits per Connection

| Message Type | Limit | Window |
|--------------|-------|--------|
| Operations | 100/sec | Sliding window |
| Cursor updates | 50/sec | Throttled |
| Presence updates | 10/sec | Debounced |
| Sync requests | 1/min | Hard limit |

### Rate Limit Response

```json
{
  "type": "error",
  "code": 4006,
  "message": "Rate limit exceeded",
  "details": "Operation rate: 150/sec exceeds limit of 100/sec",
  "recoverable": true,
  "retry_after": 1000
}
```

---

## Compression

### Message Compression

Large messages (>1KB) are compressed using LZ4:

```
┌────────────────┬────────────────┬─────────────────────┐
│ Compression    │ Original Size  │ Compressed Payload  │
│ Flag (1 bit)   │ (4 bytes)      │ (LZ4 compressed)    │
└────────────────┴────────────────┴─────────────────────┘
```

### Compression Thresholds

| Payload Size | Compression |
|--------------|-------------|
| < 1KB | None |
| 1KB - 100KB | LZ4 |
| > 100KB | Chunked + LZ4 |

---

## Security Considerations

### Token Validation

- JWT validated on every connection
- Token refresh during long sessions
- Connection closed on permission revocation

### Message Validation

- All operations validated against document schema
- Input sanitized for XSS prevention
- Position bounds checked against document length

### Rate Limiting

- Per-user and per-connection limits
- Graduated throttling before disconnection
- Abuse detection and blocking

---

## Client Implementation Example

```typescript
class CollaborationClient {
  private ws: WebSocket;
  private messageQueue: Message[] = [];
  private vectorClock: VectorClock;
  private reconnectAttempts = 0;

  async connect(documentId: string, token: string): Promise<void> {
    const url = `wss://relay.materi.dev/collab/document/${documentId}`;

    this.ws = new WebSocket(url, ['materi-collab-v1']);
    this.ws.binaryType = 'arraybuffer';

    this.ws.onopen = () => {
      // Send authentication
      this.send({
        type: 'auth',
        token: token
      });
    };

    this.ws.onmessage = (event) => {
      const message = this.decode(event.data);
      this.handleMessage(message);
    };

    this.ws.onclose = (event) => {
      if (event.code === 4002) {
        // Token expired, refresh and reconnect
        this.refreshTokenAndReconnect();
      } else if (this.shouldReconnect(event.code)) {
        this.scheduleReconnect();
      }
    };

    this.startHeartbeat();
  }

  sendOperation(operation: Operation): void {
    operation.vectorClock = this.vectorClock.increment(this.userId);
    this.messageQueue.push(operation);
    this.send({
      type: 'operation',
      ...operation
    });
  }

  private startHeartbeat(): void {
    setInterval(() => {
      this.send({
        type: 'heartbeat',
        timestamp: Date.now(),
        client_id: this.clientId
      });
    }, 30000);
  }
}
```

---

## Related Documentation

- [Overview](overview) - Service overview
- [Architecture](architecture) - System design
- [Operational Transform](operational-transform) - OT algorithms
- [WebSocket API](/api/websocket/overview) - Client integration

---

**Document Status:** Complete
**Version:** 2.0
