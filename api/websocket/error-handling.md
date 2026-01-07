# WebSocket Error Handling

<Info>
**SDD Classification:** L3-Technical
**Authority:** Engineering Team
**Review Cycle:** Quarterly
</Info>

This guide covers error handling for WebSocket connections, including error codes, recovery strategies, and best practices for building resilient real-time applications.

---

## Error Message Format

All WebSocket errors follow a consistent structure:

```json
{
  "type": "system",
  "event": "error",
  "data": {
    "error_code": "INSUFFICIENT_PERMISSIONS",
    "message": "You do not have write permissions for this document",
    "details": {
      "required_permission": "document:write",
      "user_permissions": ["document:read"]
    },
    "recoverable": false,
    "timestamp": "2025-01-07T10:30:00Z"
  }
}
```

### Error Fields

| Field | Type | Description |
|-------|------|-------------|
| `error_code` | string | Machine-readable error identifier |
| `message` | string | Human-readable description |
| `details` | object | Additional context (optional) |
| `recoverable` | boolean | Whether the error can be recovered from |
| `timestamp` | string | When the error occurred |

---

## Error Code Reference

### Connection Errors

| Code | Description | Recovery |
|------|-------------|----------|
| `CONNECTION_FAILED` | Failed to establish connection | Retry with backoff |
| `CONNECTION_TIMEOUT` | Connection timed out | Retry with backoff |
| `CONNECTION_LIMIT_EXCEEDED` | Max connections reached | Wait or close other connections |
| `PROTOCOL_ERROR` | Invalid WebSocket protocol | Check client implementation |

### Authentication Errors

| Code | Description | Recovery |
|------|-------------|----------|
| `AUTHENTICATION_FAILED` | Invalid or missing token | Re-authenticate |
| `TOKEN_EXPIRED` | JWT token has expired | Refresh token |
| `TOKEN_REVOKED` | Token was revoked | Re-authenticate |
| `INSUFFICIENT_PERMISSIONS` | User lacks required access | Contact admin |

### Document Errors

| Code | Description | Recovery |
|------|-------------|----------|
| `DOCUMENT_NOT_FOUND` | Document doesn't exist | Verify document ID |
| `DOCUMENT_LOCKED` | Document is locked | Wait and retry |
| `DOCUMENT_DELETED` | Document was deleted | Close connection |
| `VERSION_CONFLICT` | Operation version mismatch | Request sync |

### Operation Errors

| Code | Description | Recovery |
|------|-------------|----------|
| `INVALID_OPERATION` | Malformed operation | Fix operation data |
| `OPERATION_REJECTED` | Server rejected operation | Check permissions |
| `OPERATION_TIMEOUT` | Operation timed out | Retry operation |
| `RATE_LIMIT_EXCEEDED` | Too many operations | Wait and retry |

### System Errors

| Code | Description | Recovery |
|------|-------------|----------|
| `INTERNAL_ERROR` | Server error | Retry with backoff |
| `SERVICE_UNAVAILABLE` | Service temporarily down | Retry later |
| `MAINTENANCE_MODE` | Server in maintenance | Wait for service |

---

## Error Handler Implementation

```javascript
class WebSocketErrorHandler {
  constructor(websocket, options = {}) {
    this.ws = websocket;
    this.maxRetries = options.maxRetries || 5;
    this.errorCallbacks = new Map();
    this.errorCount = 0;
    this.errorWindow = 60000; // 1 minute
    this.errorTimestamps = [];
  }

  handleError(errorMessage) {
    const { error_code, message, recoverable, details } = errorMessage.data;

    // Track error rate
    this.trackError();

    // Check for error storm
    if (this.isErrorStorm()) {
      this.handleErrorStorm();
      return;
    }

    // Log error
    console.error(`WebSocket Error [${error_code}]: ${message}`, details);

    // Call registered handler
    const handler = this.errorCallbacks.get(error_code);
    if (handler) {
      handler(errorMessage.data);
      return;
    }

    // Default handling based on recoverability
    if (recoverable) {
      this.handleRecoverableError(errorMessage.data);
    } else {
      this.handleFatalError(errorMessage.data);
    }
  }

  trackError() {
    const now = Date.now();
    this.errorTimestamps.push(now);
    this.errorTimestamps = this.errorTimestamps.filter(
      ts => now - ts < this.errorWindow
    );
    this.errorCount = this.errorTimestamps.length;
  }

  isErrorStorm() {
    return this.errorCount > 10;
  }

  handleErrorStorm() {
    console.error('Error storm detected, backing off');
    this.ws.close(4999, 'Error storm');
    this.emit('error_storm');
  }

  on(errorCode, handler) {
    this.errorCallbacks.set(errorCode, handler);
  }

  handleRecoverableError(error) {
    switch (error.error_code) {
      case 'VERSION_CONFLICT':
        this.requestDocumentSync();
        break;

      case 'RATE_LIMIT_EXCEEDED':
        this.backoffAndRetry(error.details?.retry_after || 1000);
        break;

      case 'OPERATION_TIMEOUT':
        this.retryLastOperation();
        break;

      default:
        this.emit('recoverable_error', error);
    }
  }

  handleFatalError(error) {
    switch (error.error_code) {
      case 'AUTHENTICATION_FAILED':
      case 'TOKEN_EXPIRED':
        this.emit('auth_error', error);
        break;

      case 'INSUFFICIENT_PERMISSIONS':
        this.emit('permission_error', error);
        break;

      case 'DOCUMENT_DELETED':
        this.emit('document_deleted', error);
        this.ws.close(1000, 'Document deleted');
        break;

      default:
        this.emit('fatal_error', error);
    }
  }

  requestDocumentSync() {
    this.ws.send(JSON.stringify({
      type: 'system',
      event: 'sync_request',
      data: {}
    }));
  }

  backoffAndRetry(delay) {
    setTimeout(() => {
      this.emit('retry_ready');
    }, delay);
  }
}
```

---

## Specific Error Handling

### Authentication Errors

```javascript
class AuthErrorHandler {
  constructor(websocket, authService) {
    this.ws = websocket;
    this.authService = authService;
    this.refreshAttempts = 0;
    this.maxRefreshAttempts = 3;
  }

  async handleAuthError(error) {
    if (error.error_code === 'TOKEN_EXPIRED' && this.refreshAttempts < this.maxRefreshAttempts) {
      await this.attemptTokenRefresh();
    } else {
      this.redirectToLogin(error);
    }
  }

  async attemptTokenRefresh() {
    this.refreshAttempts++;

    try {
      const newToken = await this.authService.refreshToken();
      this.ws.reconnectWithToken(newToken);
      this.refreshAttempts = 0;
    } catch (refreshError) {
      if (this.refreshAttempts < this.maxRefreshAttempts) {
        // Wait and retry
        await this.delay(1000 * this.refreshAttempts);
        await this.attemptTokenRefresh();
      } else {
        this.redirectToLogin({ error_code: 'REFRESH_FAILED' });
      }
    }
  }

  redirectToLogin(error) {
    // Store current document for post-login redirect
    sessionStorage.setItem('returnTo', window.location.href);

    // Notify user
    this.showNotification('Session expired. Please log in again.');

    // Redirect
    window.location.href = '/login';
  }
}
```

### Version Conflict Recovery

```javascript
class ConflictRecoveryHandler {
  constructor(websocket, documentManager) {
    this.ws = websocket;
    this.documentManager = documentManager;
  }

  async handleVersionConflict(error) {
    const { client_version, server_version } = error.details;

    console.warn(`Version conflict: client=${client_version}, server=${server_version}`);

    // Request full document sync
    const syncData = await this.requestSync();

    // Apply server state
    this.documentManager.applyServerState(syncData.document);

    // Re-apply pending operations
    const pendingOps = this.documentManager.getPendingOperations();

    for (const op of pendingOps) {
      // Transform against new state
      const transformed = this.documentManager.transformOperation(op, syncData.operations);
      this.documentManager.sendOperation(transformed);
    }

    this.emit('conflict_resolved', {
      operationsReplayed: pendingOps.length
    });
  }

  async requestSync() {
    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        reject(new Error('Sync request timeout'));
      }, 5000);

      this.ws.once('document_sync', (data) => {
        clearTimeout(timeout);
        resolve(data);
      });

      this.ws.send(JSON.stringify({
        type: 'system',
        event: 'sync_request',
        data: {
          last_known_version: this.documentManager.getVersion()
        }
      }));
    });
  }
}
```

### Rate Limit Handling

```javascript
class RateLimitHandler {
  constructor() {
    this.operationQueue = [];
    this.isThrottled = false;
    this.throttleUntil = 0;
  }

  handleRateLimit(error) {
    const retryAfter = error.details?.retry_after || 1000;

    this.isThrottled = true;
    this.throttleUntil = Date.now() + retryAfter;

    console.warn(`Rate limited. Retry after ${retryAfter}ms`);

    // Queue subsequent operations
    setTimeout(() => {
      this.isThrottled = false;
      this.flushQueue();
    }, retryAfter);
  }

  queueOperation(operation) {
    if (this.isThrottled) {
      this.operationQueue.push(operation);
      return false;
    }
    return true;
  }

  flushQueue() {
    const ops = this.operationQueue.splice(0);
    ops.forEach(op => this.sendOperation(op));
  }
}
```

---

## Connection Close Codes

### Standard Codes

| Code | Name | Description |
|------|------|-------------|
| 1000 | Normal Closure | Clean close |
| 1001 | Going Away | Navigation or server shutdown |
| 1002 | Protocol Error | Protocol violation |
| 1003 | Unsupported Data | Unexpected data type |
| 1006 | Abnormal Closure | No close frame received |
| 1011 | Internal Error | Server error |

### Custom Codes

| Code | Name | Description |
|------|------|-------------|
| 4000 | Heartbeat Timeout | No pong received |
| 4001 | Auth Expired | Token expired |
| 4002 | Permission Denied | Lost access |
| 4003 | Document Locked | Document unavailable |
| 4004 | Kicked | Removed by admin |
| 4999 | Error Storm | Too many errors |

### Close Code Handler

```javascript
function handleCloseCode(code, reason) {
  switch (code) {
    case 1000:
      // Normal closure, no action needed
      break;

    case 1001:
      // Server going away, attempt reconnect
      scheduleReconnect();
      break;

    case 1006:
      // Abnormal closure, network issue
      scheduleReconnect();
      break;

    case 4000:
      // Heartbeat timeout, reconnect immediately
      reconnect();
      break;

    case 4001:
      // Auth expired, refresh token first
      refreshTokenAndReconnect();
      break;

    case 4002:
      // Permission denied, notify user
      showPermissionDeniedMessage();
      break;

    case 4003:
      // Document locked, show status
      showDocumentLockedMessage();
      scheduleReconnect(30000); // Try again in 30s
      break;

    case 4004:
      // Kicked by admin
      showKickedMessage();
      // Don't reconnect
      break;

    default:
      console.warn(`Unknown close code: ${code} - ${reason}`);
      scheduleReconnect();
  }
}
```

---

## Error Recovery Strategies

### Exponential Backoff

```javascript
class BackoffStrategy {
  constructor(options = {}) {
    this.baseDelay = options.baseDelay || 1000;
    this.maxDelay = options.maxDelay || 30000;
    this.maxAttempts = options.maxAttempts || 10;
    this.jitter = options.jitter || true;
    this.attempts = 0;
  }

  getNextDelay() {
    const exponentialDelay = Math.min(
      this.baseDelay * Math.pow(2, this.attempts),
      this.maxDelay
    );

    const delay = this.jitter
      ? exponentialDelay + Math.random() * 1000
      : exponentialDelay;

    this.attempts++;
    return delay;
  }

  shouldRetry() {
    return this.attempts < this.maxAttempts;
  }

  reset() {
    this.attempts = 0;
  }
}
```

### Circuit Breaker

```javascript
class CircuitBreaker {
  constructor(options = {}) {
    this.failureThreshold = options.failureThreshold || 5;
    this.resetTimeout = options.resetTimeout || 60000;
    this.failures = 0;
    this.state = 'CLOSED'; // CLOSED, OPEN, HALF_OPEN
    this.lastFailure = null;
  }

  recordFailure() {
    this.failures++;
    this.lastFailure = Date.now();

    if (this.failures >= this.failureThreshold) {
      this.state = 'OPEN';
      this.scheduleReset();
    }
  }

  recordSuccess() {
    this.failures = 0;
    this.state = 'CLOSED';
  }

  scheduleReset() {
    setTimeout(() => {
      this.state = 'HALF_OPEN';
    }, this.resetTimeout);
  }

  canExecute() {
    if (this.state === 'CLOSED') return true;
    if (this.state === 'OPEN') return false;
    if (this.state === 'HALF_OPEN') return true; // Allow test request
    return false;
  }
}
```

---

## User-Facing Error Messages

### Error Message Mapping

```javascript
const errorMessages = {
  AUTHENTICATION_FAILED: {
    title: 'Session Expired',
    message: 'Please log in again to continue editing.',
    action: 'Log In'
  },
  INSUFFICIENT_PERMISSIONS: {
    title: 'Access Denied',
    message: 'You no longer have permission to edit this document.',
    action: 'Request Access'
  },
  DOCUMENT_LOCKED: {
    title: 'Document Locked',
    message: 'This document is temporarily unavailable. Please try again shortly.',
    action: 'Retry'
  },
  RATE_LIMIT_EXCEEDED: {
    title: 'Slow Down',
    message: 'You\'re making changes too quickly. Please wait a moment.',
    action: null
  },
  CONNECTION_FAILED: {
    title: 'Connection Lost',
    message: 'Unable to connect to the server. Retrying...',
    action: 'Retry Now'
  },
  INTERNAL_ERROR: {
    title: 'Something Went Wrong',
    message: 'An unexpected error occurred. Our team has been notified.',
    action: 'Reload'
  }
};

function showUserError(errorCode) {
  const errorInfo = errorMessages[errorCode] || errorMessages.INTERNAL_ERROR;

  showNotification({
    type: 'error',
    title: errorInfo.title,
    message: errorInfo.message,
    action: errorInfo.action
  });
}
```

---

## Best Practices

### Do

1. **Log all errors** - For debugging and monitoring
2. **Show user-friendly messages** - Don't expose technical details
3. **Implement retry logic** - Most errors are transient
4. **Use circuit breakers** - Prevent cascade failures
5. **Track error metrics** - Monitor error rates

### Don't

1. **Don't ignore errors** - Always handle them appropriately
2. **Don't retry indefinitely** - Set maximum attempts
3. **Don't expose internal errors** - Hide technical details from users
4. **Don't block the UI** - Handle errors asynchronously
5. **Don't lose user data** - Queue operations during errors

---

## Related Documentation

- [WebSocket Overview](/api/websocket/overview) - API overview
- [Connection](/api/websocket/connection) - Connection management
- [Authentication](/api/websocket/authentication) - Auth errors
- [API Errors](/api/introduction/errors) - REST API errors

---

**Document Status:** Complete
**Version:** 2.0
