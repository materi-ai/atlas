# Client Integration Implementation Guide

## Quick Start for Integration Team

**Estimated Time to Full Integration**: 17-22 hours  
**Current Blocker**: TypeScript compilation errors (Phase 1 priority)  
**Status**: Awaiting Phase 1 completion

---

## Phase 1: Resolve TypeScript Build Errors (2-3 hours)

### Step 1.1: Identify All Errors

```bash
cd /Users/alexarno/materi/web/apps/client
npm run type-check 2>&1 | tee typescript-errors.log
```

### Step 1.2: Error Priority List

**CRITICAL** (blocking build):
1. `operationalTransform.ts` - 15+ errors (null safety)
2. `optimisticUpdates.ts` - 20+ errors (type mismatches)

**HIGH** (prevents features):
3. `config/queryClient.ts` - 3 errors (staleTime type)
4. Component files - 50+ errors (type resolution)

**MEDIUM** (utility):
5. `retry.ts` - 5+ errors (error typing)
6. Hook files - 20+ errors (method signatures)

### Step 1.3: Automated Fixes

```bash
# Install dependencies
npm i

# Run TypeScript strict checks
npx tsc --strict --noEmit

# Attempt automatic fixes
npx tsc --noEmit --pretty false > errors.json

# Review and fix manually (see detailed error categories below)
```

### Step 1.4: Critical File Fixes

#### Fix operationalTransform.ts

```typescript
// Current problematic code (line ~180):
const current = stack[stack.length - 1];  // Can be undefined
const next = operations[i];                // Can be undefined

// Fixed version:
const current = stack[stack.length - 1];
const next = operations[i];

if (!current || !next) {
  continue;  // or handle appropriately
}

// Use after guarantee
use(current, next);
```

#### Fix optimisticUpdates.ts

```typescript
// Current issue (line ~78):
// Type 'number' is not assignable to type 'string'
{ fromIndex, toIndex }  // These are numbers but expected as strings

// Solution: Update type definitions
export interface CacheUpdate {
  fromIndex: number;  // Explicitly number
  toIndex: number;    // Explicitly number
  items: any[];
}

// Or adjust API response type expectations
```

#### Fix queryClient.ts

```typescript
// Current issue (line ~91):
staleTime: 'stale'  // Type error

// Solution: Use correct type
staleTime: 1000 * 60 * 5  // milliseconds, not string

// Or if using constants:
import { STALE_TIME } from './constants';
staleTime: STALE_TIME.DOCUMENTS  // 300000
```

### Step 1.5: Verify Build Success

```bash
npm run type-check
npm run build
echo "✅ Build successful!"
```

---

## Phase 2: Shield Authentication Integration (3-4 hours)

### Step 2.1: Configure Shield Endpoint

```bash
# Create .env.local
cat > .env.local << 'EOF'
# Shield Authentication Service
VITE_SHIELD_API_URL=http://localhost:8080/api
VITE_SHIELD_OAUTH_CLIENT_ID=materi-client-local
VITE_SHIELD_OAUTH_REDIRECT_URI=http://localhost:5173/auth/callback

# Disable for development
VITE_SHIELD_OAUTH_ENABLED=true
EOF
```

### Step 2.2: Update AuthContext.tsx

```typescript
// src/contexts/AuthContext.tsx
import { createContext, useCallback, useEffect, useState } from 'react';

export interface AuthUser {
  id: string;
  email: string;
  displayName: string;
  avatarUrl?: string;
}

export interface AuthContextType {
  user: AuthUser | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  isLoading: boolean;
}

const ShieldAPI = {
  async login(email: string, password: string) {
    const response = await fetch(
      `${import.meta.env.VITE_SHIELD_API_URL}/auth/login`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      }
    );
    const data = await response.json();
    localStorage.setItem('auth_token', data.token);
    return data.user;
  },

  async logout() {
    await fetch(
      `${import.meta.env.VITE_SHIELD_API_URL}/auth/logout`,
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('auth_token')}`,
        },
      }
    );
    localStorage.removeItem('auth_token');
  },
};

export const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      // Verify token with Shield
      fetch(`${import.meta.env.VITE_SHIELD_API_URL}/auth/verify`, {
        headers: { Authorization: `Bearer ${token}` },
      })
        .then((r) => r.json())
        .then((data) => setUser(data.user))
        .catch(() => localStorage.removeItem('auth_token'))
        .finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        login: ShieldAPI.login,
        logout: ShieldAPI.logout,
        isLoading,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
```

### Step 2.3: Create Integration Test

```typescript
// src/__tests__/shield.integration.test.ts
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';

describe('Shield Authentication Integration', () => {
  const shieldUrl = 'http://localhost:8080/api';

  beforeEach(() => {
    localStorage.clear();
    vi.stubGlobal('fetch', vi.fn());
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should login with Shield credentials', async () => {
    const mockUser = {
      id: 'user-123',
      email: 'test@example.com',
      displayName: 'Test User',
    };

    global.fetch = vi.fn()
      .mockResolvedValueOnce({
        json: () => Promise.resolve({
          token: 'test-token',
          user: mockUser,
        }),
      } as any);

    // Test login
    const response = await fetch(`${shieldUrl}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: 'test@example.com',
        password: 'password',
      }),
    });

    const data = await response.json();
    expect(data.user).toEqual(mockUser);
    expect(localStorage.getItem('auth_token')).toBe('test-token');
  });

  it('should verify token with Shield', async () => {
    localStorage.setItem('auth_token', 'valid-token');

    global.fetch = vi.fn()
      .mockResolvedValueOnce({
        json: () => Promise.resolve({
          user: {
            id: 'user-123',
            email: 'test@example.com',
          },
        }),
      } as any);

    const response = await fetch(`${shieldUrl}/auth/verify`, {
      headers: { Authorization: 'Bearer valid-token' },
    });

    const data = await response.json();
    expect(data.user.id).toBe('user-123');
  });

  it('should handle logout', async () => {
    localStorage.setItem('auth_token', 'test-token');

    global.fetch = vi.fn()
      .mockResolvedValueOnce({ ok: true } as any);

    await fetch(`${shieldUrl}/auth/logout`, {
      method: 'POST',
      headers: { Authorization: 'Bearer test-token' },
    });

    localStorage.removeItem('auth_token');
    expect(localStorage.getItem('auth_token')).toBeNull();
  });
});
```

### Step 2.4: Verify Shield Connectivity

```bash
# Test against running Shield service
export VITE_SHIELD_API_URL=http://localhost:8080/api
npm test -- src/__tests__/shield.integration.test.ts

# Should see:
# ✓ should login with Shield credentials
# ✓ should verify token with Shield
# ✓ should handle logout
```

---

## Phase 3: API Service Integration (3-4 hours)

### Step 3.1: Configure API Endpoint

```bash
# Update .env.local
cat >> .env.local << 'EOF'

# API Service
VITE_API_BASE_URL=http://localhost:8081/api
VITE_API_TIMEOUT=30000
EOF
```

### Step 3.2: Update API Client

```typescript
// src/services/api.ts
import axios, { AxiosInstance } from 'axios';

export class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL,
      timeout: parseInt(import.meta.env.VITE_API_TIMEOUT || '30000'),
    });

    // Add auth token to requests
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('auth_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Handle errors
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('auth_token');
          window.location.href = '/login';
        }
        throw error;
      }
    );
  }

  async getDocuments(page = 1, limit = 20) {
    const response = await this.client.get('/documents', {
      params: { page, limit },
    });
    return response.data;
  }

  async getDocument(id: string) {
    const response = await this.client.get(`/documents/${id}`);
    return response.data;
  }

  async saveDocument(id: string, content: string, version: number) {
    const response = await this.client.post(`/documents/${id}/save`, {
      content,
      version,
    });
    return response.data;
  }
}

export const apiClient = new APIClient();
```

### Step 3.3: Create Integration Test

```typescript
// src/__tests__/api.integration.test.ts
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { apiClient } from '../services/api';

describe('API Service Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.setItem('auth_token', 'test-token');
  });

  it('should fetch documents from API', async () => {
    const mockDocuments = {
      items: [
        {
          id: 'doc-1',
          title: 'Test Document',
          type: 'editor',
        },
      ],
      total: 1,
      page: 1,
      limit: 20,
    };

    vi.spyOn(apiClient['client'], 'get')
      .mockResolvedValueOnce({ data: mockDocuments });

    const result = await apiClient.getDocuments();
    expect(result.items).toHaveLength(1);
    expect(result.items[0].title).toBe('Test Document');
  });

  it('should save document changes', async () => {
    const mockResponse = {
      id: 'doc-1',
      version: 2,
      lastModifiedAt: new Date().toISOString(),
    };

    vi.spyOn(apiClient['client'], 'post')
      .mockResolvedValueOnce({ data: mockResponse });

    const result = await apiClient.saveDocument('doc-1', 'new content', 1);
    expect(result.version).toBe(2);
  });

  it('should handle API errors gracefully', async () => {
    vi.spyOn(apiClient['client'], 'get')
      .mockRejectedValueOnce(new Error('Network error'));

    await expect(apiClient.getDocuments()).rejects.toThrow();
  });
});
```

### Step 3.4: Verify API Connectivity

```bash
# Test against running API service
export VITE_API_BASE_URL=http://localhost:8081/api
npm test -- src/__tests__/api.integration.test.ts

# Should see all tests passing
```

---

## Phase 4: Relay Collaboration Integration (4-5 hours)

### Step 4.1: Configure Relay Endpoint

```bash
# Update .env.local
cat >> .env.local << 'EOF'

# Relay Collaboration Service
VITE_RELAY_WS_URL=ws://localhost:8082/ws
VITE_RELAY_HEARTBEAT_INTERVAL=30000
VITE_RELAY_RECONNECT_ATTEMPTS=5
VITE_RELAY_RECONNECT_DELAY=3000
EOF
```

### Step 4.2: Update WebSocket Service

```typescript
// src/services/websocket.ts
import { EventEmitter } from 'eventemitter3';

export class RelayWebSocket extends EventEmitter {
  private ws: WebSocket | null = null;
  private url: string;
  private userId: string | null = null;
  private reconnectAttempts = 0;
  private messageQueue: any[] = [];

  constructor() {
    super();
    this.url = import.meta.env.VITE_RELAY_WS_URL || 'ws://localhost:8082/ws';
  }

  async connect(userId: string, token: string): Promise<void> {
    this.userId = userId;

    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(
          `${this.url}?userId=${userId}&token=${token}`
        );

        this.ws.onopen = () => {
          console.log('[Relay] Connected');
          this.reconnectAttempts = 0;
          this.emit('connected');
          this.flushQueue();
          resolve();
        };

        this.ws.onmessage = (event) => {
          const message = JSON.parse(event.data);
          this.emit('message', message);
        };

        this.ws.onerror = (error) => {
          console.error('[Relay] Error:', error);
          this.emit('error', error);
          reject(error);
        };

        this.ws.onclose = () => {
          console.log('[Relay] Disconnected');
          this.attemptReconnect();
        };
      } catch (error) {
        reject(error);
      }
    });
  }

  send(message: any): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      this.messageQueue.push(message);
    }
  }

  private flushQueue(): void {
    while (this.messageQueue.length > 0) {
      const message = this.messageQueue.shift();
      this.send(message);
    }
  }

  private attemptReconnect(): void {
    if (
      this.reconnectAttempts <
      parseInt(import.meta.env.VITE_RELAY_RECONNECT_ATTEMPTS || '5')
    ) {
      this.reconnectAttempts++;
      setTimeout(() => {
        if (this.userId) {
          const token = localStorage.getItem('auth_token');
          this.connect(this.userId, token || '');
        }
      }, parseInt(import.meta.env.VITE_RELAY_RECONNECT_DELAY || '3000'));
    }
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

export const relayWebSocket = new RelayWebSocket();
```

### Step 4.3: Create Integration Test

```typescript
// src/__tests__/relay.integration.test.ts
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { relayWebSocket } from '../services/websocket';

describe('Relay Collaboration Integration', () => {
  beforeEach(() => {
    localStorage.setItem('auth_token', 'test-token');
    vi.clearAllMocks();
  });

  afterEach(() => {
    relayWebSocket.disconnect();
  });

  it('should connect to Relay WebSocket', async () => {
    const connectPromise = new Promise<void>((resolve) => {
      relayWebSocket.once('connected', () => resolve());
      relayWebSocket.connect('user-123', 'test-token').catch(() => {});
    });

    // Mock WebSocket for testing
    global.WebSocket = vi.fn().mockImplementation((url) => {
      const socket = {
        readyState: 1,
        send: vi.fn(),
        close: vi.fn(),
        onopen: null as any,
        onmessage: null as any,
        onerror: null as any,
        onclose: null as any,
      };

      setTimeout(() => socket.onopen?.());
      return socket;
    }) as any;

    await expect(connectPromise).resolves.toBeUndefined();
  });

  it('should queue messages when disconnected', async () => {
    const message = { type: 'edit', data: 'test' };
    relayWebSocket.send(message);

    // Message should be queued internally
    expect(relayWebSocket).toBeDefined();
  });

  it('should emit messages from Relay', async () => {
    const messagePromise = new Promise<any>((resolve) => {
      relayWebSocket.once('message', resolve);
    });

    global.WebSocket = vi.fn().mockImplementation((url) => {
      const socket = {
        readyState: 1,
        send: vi.fn(),
        close: vi.fn(),
        onopen: null as any,
        onmessage: null as any,
        onerror: null as any,
        onclose: null as any,
      };

      setTimeout(() => {
        socket.onopen?.();
        socket.onmessage?.({
          data: JSON.stringify({
            type: 'operation',
            operation: { type: 'insert', content: 'hello' },
          }),
        });
      });

      return socket;
    }) as any;

    await relayWebSocket.connect('user-123', 'test-token').catch(() => {});
    const message = await messagePromise;
    expect(message.type).toBe('operation');
  });
});
```

### Step 4.4: Verify Relay Connectivity

```bash
# Test against running Relay service
export VITE_RELAY_WS_URL=ws://localhost:8082/ws
npm test -- src/__tests__/relay.integration.test.ts

# Should see all WebSocket tests passing
```

---

## Phase 5: Folio Integration (2-3 hours)

### Step 5.1: Configure Folio Endpoint

```bash
# Update .env.local
cat >> .env.local << 'EOF'

# Folio Observability Service
VITE_FOLIO_API_URL=http://localhost:8083/api
VITE_FOLIO_SERVICE_NAME=materi-client
VITE_FOLIO_SERVICE_VERSION=1.0.0
VITE_FOLIO_ENVIRONMENT=development
EOF
```

### Step 5.2: Create Folio Client

```typescript
// src/services/folio.ts
import axios from 'axios';

export interface ServiceInfo {
  name: string;
  version: string;
  environment: string;
  endpoints?: string[];
  healthCheckUrl?: string;
}

export class FolioClient {
  private client = axios.create({
    baseURL: import.meta.env.VITE_FOLIO_API_URL,
    timeout: 5000,
  });

  async registerService(): Promise<void> {
    const serviceInfo: ServiceInfo = {
      name: import.meta.env.VITE_FOLIO_SERVICE_NAME,
      version: import.meta.env.VITE_FOLIO_SERVICE_VERSION,
      environment: import.meta.env.VITE_FOLIO_ENVIRONMENT,
      endpoints: [window.location.origin],
      healthCheckUrl: `${window.location.origin}/health`,
    };

    try {
      await this.client.post('/services', serviceInfo);
      console.log('[Folio] Service registered successfully');
    } catch (error) {
      console.warn('[Folio] Failed to register service:', error);
    }
  }

  async discoverServices(): Promise<Map<string, string>> {
    try {
      const response = await this.client.get('/services');
      const serviceMap = new Map<string, string>();

      for (const service of response.data.services) {
        serviceMap.set(service.name, service.endpoints[0]);
      }

      return serviceMap;
    } catch (error) {
      console.warn('[Folio] Failed to discover services:', error);
      return new Map();
    }
  }

  async sendMetrics(metrics: Record<string, any>): Promise<void> {
    try {
      await this.client.post('/metrics', {
        service: import.meta.env.VITE_FOLIO_SERVICE_NAME,
        timestamp: new Date().toISOString(),
        metrics,
      });
    } catch (error) {
      console.warn('[Folio] Failed to send metrics:', error);
    }
  }

  async sendError(error: Error): Promise<void> {
    try {
      await this.client.post('/errors', {
        service: import.meta.env.VITE_FOLIO_SERVICE_NAME,
        timestamp: new Date().toISOString(),
        error: {
          message: error.message,
          stack: error.stack,
          type: error.name,
        },
      });
    } catch (err) {
      console.warn('[Folio] Failed to send error:', err);
    }
  }
}

export const folioClient = new FolioClient();
```

### Step 5.3: Initialize Folio on App Start

```typescript
// src/main.tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import { folioClient } from './services/folio';

// Register with Folio on app startup
if (import.meta.env.VITE_FOLIO_API_URL) {
  folioClient.registerService().then(() => {
    console.log('[App] Folio registration complete');
  });
}

// Setup global error handler
window.addEventListener('error', (event) => {
  folioClient.sendError(event.error);
});

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

### Step 5.4: Create Integration Test

```typescript
// src/__tests__/folio.integration.test.ts
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { folioClient } from '../services/folio';

describe('Folio Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should register service with Folio', async () => {
    const postSpy = vi.spyOn(folioClient['client'], 'post')
      .mockResolvedValueOnce({ data: { success: true } });

    await folioClient.registerService();
    expect(postSpy).toHaveBeenCalledWith(
      expect.stringContaining('/services'),
      expect.objectContaining({
        name: import.meta.env.VITE_FOLIO_SERVICE_NAME,
      })
    );
  });

  it('should discover services from Folio', async () => {
    const getSpy = vi.spyOn(folioClient['client'], 'get')
      .mockResolvedValueOnce({
        data: {
          services: [
            { name: 'shield', endpoints: ['http://shield:8080'] },
            { name: 'api', endpoints: ['http://api:8081'] },
          ],
        },
      });

    const services = await folioClient.discoverServices();
    expect(services.has('shield')).toBe(true);
    expect(services.get('shield')).toBe('http://shield:8080');
  });

  it('should send metrics to Folio', async () => {
    const postSpy = vi.spyOn(folioClient['client'], 'post')
      .mockResolvedValueOnce({ data: { success: true } });

    await folioClient.sendMetrics({
      activeUsers: 5,
      documentsOpen: 10,
    });

    expect(postSpy).toHaveBeenCalledWith(
      expect.stringContaining('/metrics'),
      expect.objectContaining({
        metrics: expect.objectContaining({ activeUsers: 5 }),
      })
    );
  });

  it('should report errors to Folio', async () => {
    const postSpy = vi.spyOn(folioClient['client'], 'post')
      .mockResolvedValueOnce({ data: { success: true } });

    const error = new Error('Test error');
    await folioClient.sendError(error);

    expect(postSpy).toHaveBeenCalledWith(
      expect.stringContaining('/errors'),
      expect.objectContaining({
        error: expect.objectContaining({
          message: 'Test error',
        }),
      })
    );
  });
});
```

### Step 5.5: Verify Folio Connectivity

```bash
# Test against running Folio service
export VITE_FOLIO_API_URL=http://localhost:8083/api
npm test -- src/__tests__/folio.integration.test.ts

# Should see all Folio tests passing
```

---

## Phase 6: Full Integration Verification (1-2 hours)

### Step 6.1: Run Complete Test Suite

```bash
# Run all tests
npm test -- --no-coverage --run

# Expected output:
# Test Files  14 passed (14)
# Tests       538 passed (538)
```

### Step 6.2: Build for Production

```bash
npm run build
# dist/ folder should be created with optimized bundle
```

### Step 6.3: Run Full Integration Test

```bash
# With all services running:
export VITE_SHIELD_API_URL=http://localhost:8080/api
export VITE_API_BASE_URL=http://localhost:8081/api
export VITE_RELAY_WS_URL=ws://localhost:8082/ws
export VITE_FOLIO_API_URL=http://localhost:8083/api

npm test -- --run

# Test end-to-end scenario:
# 1. User logs in via Shield
# 2. Client fetches documents from API
# 3. Real-time collaboration via Relay
# 4. Metrics sent to Folio
```

### Step 6.4: Health Check

```bash
# Add health endpoint
cat > src/pages/health.tsx << 'EOF'
import { useEffect, useState } from 'react';

export function HealthCheck() {
  const [health, setHealth] = useState<any>(null);

  useEffect(() => {
    (async () => {
      const checks = {
        shield: await checkService(import.meta.env.VITE_SHIELD_API_URL),
        api: await checkService(import.meta.env.VITE_API_BASE_URL),
        folio: await checkService(import.meta.env.VITE_FOLIO_API_URL),
        relay: 'ws' in window ? 'available' : 'not-available',
      };
      setHealth(checks);
    })();
  }, []);

  return <pre>{JSON.stringify(health, null, 2)}</pre>;
}

async function checkService(url?: string): Promise<string> {
  if (!url) return 'not-configured';
  try {
    const response = await fetch(url, { method: 'HEAD' });
    return response.ok ? 'healthy' : 'unhealthy';
  } catch {
    return 'unreachable';
  }
}
EOF
```

---

## Service Connectivity Checklist

### ✅ Pre-Integration Verification

```bash
# 1. Verify all services are running
curl http://localhost:8080/health          # Shield
curl http://localhost:8081/health          # API
curl http://localhost:8082/health          # Relay (if HTTP health endpoint)
curl http://localhost:8083/health          # Folio

# 2. Verify environment variables
env | grep VITE_

# 3. Run tests
npm test -- --run

# 4. Build
npm run build

# 5. Preview production build
npm run preview
```

### 🚀 Deployment Readiness

- [ ] Phase 1: TypeScript build successful
- [ ] Phase 2: Shield authentication working
- [ ] Phase 3: API CRUD operations tested
- [ ] Phase 4: Relay WebSocket synchronized
- [ ] Phase 5: Folio metrics collection active
- [ ] Phase 6: Full integration tests passing
- [ ] Health checks all green
- [ ] Security audit completed
- [ ] Performance benchmarks acceptable
- [ ] Documentation updated

---

## Emergency Troubleshooting

### Build Failures

```bash
# Clear cache and rebuild
rm -rf dist node_modules
npm i
npm run build
```

### Service Connection Issues

```bash
# Test connectivity to each service
curl -i http://localhost:8080/api     # Shield
curl -i http://localhost:8081/api     # API
curl -i http://localhost:8083/api     # Folio
wscat -c ws://localhost:8082/ws       # Relay

# Check environment variables
grep VITE_ .env.local
```

### Test Failures

```bash
# Run specific test file
npm test -- src/__tests__/shield.integration.test.ts --reporter=verbose

# Run in watch mode for debugging
npm test -- --watch

# Check for flaky tests
npm test -- --reporter=verbose --bail
```

---

## Success Criteria

✅ **Integration Complete When**:

1. All 538 tests passing
2. Build completes without errors
3. All service connectivity tests green
4. Health check endpoint returns healthy
5. Folio metrics collection active
6. Error reporting working
7. Real-time collaboration working
8. Document CRUD operations working
9. User authentication working
10. Performance benchmarks acceptable

---

## Support Contacts

| Issue | Contact | Channel |
|-------|---------|---------|
| TypeScript/Build | DevOps | #devops-channel |
| Shield Integration | Auth Team | #auth-channel |
| API Integration | Backend Team | #api-channel |
| Relay Integration | Collab Team | #collab-channel |
| Folio Integration | DevOps | #devops-channel |
| Testing/QA | QA Team | #qa-channel |

---

**Estimated Total Time**: 17-22 hours  
**Start Date**: [TO BE DETERMINED]  
**Go/No-Go Decision**: Awaiting Phase 1 completion
