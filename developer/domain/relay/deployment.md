# Relay Deployment

<Info>
**SDD Classification:** L4-Operational
**Authority:** Platform Team
**Review Cycle:** Monthly
</Info>

This document covers Relay service deployment including Rust-optimized Docker configuration, Kubernetes manifests, environment variables, scaling strategies, and operational procedures.

---

## Deployment Architecture

```mermaid
flowchart TD
    subgraph "Load Balancer"
        A[Application Load Balancer<br/>WebSocket Sticky Sessions]
    end

    subgraph "Relay Service Cluster"
        B[Pod 1<br/>Tokio Runtime]
        C[Pod 2<br/>Tokio Runtime]
        D[Pod 3<br/>Tokio Runtime]
    end

    subgraph "Data Layer"
        E[(Redis Cluster<br/>Pub/Sub + State)]
        F[(PostgreSQL<br/>Persistence)]
    end

    subgraph "Platform Services"
        G[Shield Service<br/>Auth Validation]
        H[API Service<br/>Bidirectional Sync]
    end

    A -->|WSS| B
    A -->|WSS| C
    A -->|WSS| D

    B --> E
    B --> F
    C --> E
    C --> F
    D --> E
    D --> F

    B --> G
    B --> H
```

---

## Docker Configuration

### Multi-Stage Dockerfile

```dockerfile
# Stage 1: Build dependencies (cached)
FROM rust:1.78-slim-bookworm AS deps

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Create dummy project for dependency caching
COPY Cargo.toml Cargo.lock ./
RUN mkdir src && echo "fn main() {}" > src/main.rs
RUN cargo build --release
RUN rm -rf src

# Stage 2: Build application
FROM deps AS builder

COPY src ./src
COPY migrations ./migrations
RUN touch src/main.rs  # Update timestamp
RUN cargo build --release --bin relay

# Stage 3: Runtime image
FROM debian:bookworm-slim AS runtime

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    ca-certificates \
    libssl3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r relay && useradd -r -g relay relay

WORKDIR /app

# Copy binary
COPY --from=builder /app/target/release/relay /usr/local/bin/relay

# Copy migrations
COPY --from=builder /app/migrations ./migrations

# Security: non-root user
USER relay

# Environment defaults
ENV RUST_LOG=info
ENV RUST_BACKTRACE=1
ENV TOKIO_WORKER_THREADS=4

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8081/health || exit 1

EXPOSE 8081

ENTRYPOINT ["relay"]
```

### Docker Compose (Development)

```yaml
# docker-compose.yml
version: '3.8'

services:
  relay:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8081:8081"
    environment:
      - RUST_LOG=debug
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/relay
      - REDIS_URL=redis://redis:6379
      - BIND_ADDRESS=0.0.0.0:8081
      - JWT_PUBLIC_KEY_URL=http://shield:8000/.well-known/jwks.json
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./migrations:/app/migrations

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: relay
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
  redis_data:
```

---

## Kubernetes Deployment

### Deployment Manifest

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: relay
  labels:
    app: relay
    component: collaboration
spec:
  replicas: 3
  selector:
    matchLabels:
      app: relay
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    metadata:
      labels:
        app: relay
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "9090"
        prometheus.io/path: "/metrics"
    spec:
      serviceAccountName: relay
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      terminationGracePeriodSeconds: 60
      containers:
        - name: relay
          image: gcr.io/materi/relay:latest
          ports:
            - containerPort: 8081
              name: websocket
            - containerPort: 9090
              name: metrics
          env:
            - name: RUST_LOG
              value: "info,relay=debug"
            - name: RUST_BACKTRACE
              value: "1"
            - name: BIND_ADDRESS
              value: "0.0.0.0:8081"
            - name: METRICS_PORT
              value: "9090"
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: relay-secrets
                  key: database-url
            - name: REDIS_URL
              valueFrom:
                secretKeyRef:
                  name: relay-secrets
                  key: redis-url
            - name: JWT_PUBLIC_KEY_URL
              value: "http://shield.default.svc.cluster.local/.well-known/jwks.json"
            - name: TOKIO_WORKER_THREADS
              value: "4"
            - name: MAX_CONNECTIONS
              value: "10000"
          resources:
            requests:
              memory: "512Mi"
              cpu: "500m"
            limits:
              memory: "2Gi"
              cpu: "2000m"
          livenessProbe:
            httpGet:
              path: /health
              port: 8081
            initialDelaySeconds: 10
            periodSeconds: 15
            timeoutSeconds: 5
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /ready
              port: 8081
            initialDelaySeconds: 5
            periodSeconds: 10
            timeoutSeconds: 5
            failureThreshold: 3
          lifecycle:
            preStop:
              exec:
                command: ["/bin/sh", "-c", "sleep 15"]
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop:
                - ALL
          volumeMounts:
            - name: tmp
              mountPath: /tmp
      volumes:
        - name: tmp
          emptyDir: {}
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
            - weight: 100
              podAffinityTerm:
                labelSelector:
                  matchExpressions:
                    - key: app
                      operator: In
                      values:
                        - relay
                topologyKey: kubernetes.io/hostname
```

### Service Manifest

```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: relay
  labels:
    app: relay
spec:
  type: ClusterIP
  ports:
    - port: 80
      targetPort: 8081
      protocol: TCP
      name: websocket
    - port: 9090
      targetPort: 9090
      protocol: TCP
      name: metrics
  selector:
    app: relay
  sessionAffinity: ClientIP
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 3600
```

### Ingress Configuration

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: relay
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/proxy-read-timeout: "3600"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "3600"
    nginx.ingress.kubernetes.io/upstream-hash-by: "$remote_addr"
    nginx.ingress.kubernetes.io/websocket-services: "relay"
    nginx.ingress.kubernetes.io/configuration-snippet: |
      proxy_set_header Upgrade $http_upgrade;
      proxy_set_header Connection "upgrade";
spec:
  tls:
    - hosts:
        - relay.materi.dev
      secretName: relay-tls
  rules:
    - host: relay.materi.dev
      http:
        paths:
          - path: /collab
            pathType: Prefix
            backend:
              service:
                name: relay
                port:
                  number: 80
```

### Horizontal Pod Autoscaler

```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: relay
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: relay
  minReplicas: 3
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
    - type: Pods
      pods:
        metric:
          name: websocket_connections_active
        target:
          type: AverageValue
          averageValue: 3000
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
        - type: Pods
          value: 2
          periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Pods
          value: 1
          periodSeconds: 120
```

---

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/relay` |
| `REDIS_URL` | Redis connection string | `redis://host:6379` |
| `JWT_PUBLIC_KEY_URL` | Shield JWKS endpoint | `https://shield.materi.dev/.well-known/jwks.json` |
| `BIND_ADDRESS` | Server bind address | `0.0.0.0:8081` |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `RUST_LOG` | `info` | Log level filter |
| `RUST_BACKTRACE` | `0` | Enable backtraces |
| `TOKIO_WORKER_THREADS` | CPU cores | Async runtime workers |
| `MAX_CONNECTIONS` | `10000` | Max WebSocket connections |
| `METRICS_PORT` | `9090` | Prometheus metrics port |
| `REDIS_POOL_SIZE` | `50` | Redis connection pool |
| `PERMISSION_CACHE_TTL` | `300` | Permission cache seconds |
| `OPERATION_HISTORY_TTL` | `600` | OT history retention seconds |

### Performance Tuning Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CURSOR_THROTTLE_MS` | `50` | Cursor update throttle |
| `TYPING_DEBOUNCE_MS` | `500` | Typing indicator debounce |
| `OPERATION_BATCH_SIZE` | `100` | Max operations per batch |
| `HEARTBEAT_INTERVAL_SECS` | `30` | WebSocket heartbeat interval |
| `HEARTBEAT_TIMEOUT_SECS` | `60` | Connection timeout |

---

## Health Endpoints

### Health Check

```http
GET /health
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "version": "2.1.0",
  "uptime_seconds": 86400,
  "active_connections": 1500,
  "active_documents": 45
}
```

### Readiness Check

```http
GET /ready
```

**Response (200 OK):**
```json
{
  "status": "ready",
  "checks": {
    "database": "ok",
    "redis": "ok",
    "jwt_keys": "ok"
  }
}
```

### Health Implementation

```rust
pub async fn health_check(State(state): State<AppState>) -> impl IntoResponse {
    let active_connections = state.connection_manager.connection_count();
    let active_documents = state.document_manager.document_count();

    Json(json!({
        "status": "healthy",
        "version": env!("CARGO_PKG_VERSION"),
        "uptime_seconds": state.start_time.elapsed().as_secs(),
        "active_connections": active_connections,
        "active_documents": active_documents
    }))
}

pub async fn readiness_check(State(state): State<AppState>) -> impl IntoResponse {
    let mut checks = HashMap::new();
    let mut healthy = true;

    // Database check
    match state.db.execute("SELECT 1").await {
        Ok(_) => checks.insert("database", "ok"),
        Err(_) => {
            healthy = false;
            checks.insert("database", "error")
        }
    };

    // Redis check
    match state.redis.ping().await {
        Ok(_) => checks.insert("redis", "ok"),
        Err(_) => {
            healthy = false;
            checks.insert("redis", "error")
        }
    };

    // JWT keys check
    match state.jwt_validator.has_keys() {
        true => checks.insert("jwt_keys", "ok"),
        false => {
            healthy = false;
            checks.insert("jwt_keys", "error")
        }
    };

    let status_code = if healthy {
        StatusCode::OK
    } else {
        StatusCode::SERVICE_UNAVAILABLE
    };

    (status_code, Json(json!({
        "status": if healthy { "ready" } else { "not_ready" },
        "checks": checks
    })))
}
```

---

## Database Migrations

### SQLx Migrations

```bash
# Create migration
sqlx migrate add create_operations_table

# Run migrations
DATABASE_URL=postgresql://... sqlx migrate run

# Prepare offline queries
cargo sqlx prepare
```

### Migration Example

```sql
-- migrations/001_create_operations.sql
CREATE TABLE operations (
    id UUID PRIMARY KEY,
    document_id UUID NOT NULL,
    actor_id UUID NOT NULL,
    operation_type VARCHAR(20) NOT NULL,
    position INTEGER NOT NULL,
    content TEXT,
    attributes JSONB,
    vector_clock JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT fk_document FOREIGN KEY (document_id)
        REFERENCES documents(id) ON DELETE CASCADE
);

CREATE INDEX idx_operations_document_id ON operations(document_id);
CREATE INDEX idx_operations_created_at ON operations(created_at);

-- Partition by document for performance
CREATE TABLE operations_partitioned (
    LIKE operations INCLUDING ALL
) PARTITION BY HASH (document_id);
```

### Kubernetes Migration Job

```yaml
# k8s/migration-job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: relay-migrate
  annotations:
    argocd.argoproj.io/hook: PreSync
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: migrate
          image: gcr.io/materi/relay:latest
          command: ["sqlx", "migrate", "run"]
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: relay-secrets
                  key: database-url
          resources:
            requests:
              memory: "128Mi"
              cpu: "100m"
            limits:
              memory: "256Mi"
              cpu: "500m"
  backoffLimit: 3
```

---

## Monitoring & Observability

### Prometheus Metrics

```rust
lazy_static! {
    static ref WEBSOCKET_CONNECTIONS: GaugeVec = register_gauge_vec!(
        "materi_websocket_connections_active",
        "Active WebSocket connections",
        &["document_id"]
    ).unwrap();

    static ref OPERATIONS_PROCESSED: CounterVec = register_counter_vec!(
        "materi_operations_processed_total",
        "Total operations processed",
        &["operation_type", "status"]
    ).unwrap();

    static ref OPERATION_LATENCY: Histogram = register_histogram!(
        "materi_operation_latency_seconds",
        "Operation processing latency",
        vec![0.001, 0.005, 0.010, 0.025, 0.050, 0.100, 0.250, 0.500]
    ).unwrap();

    static ref PRESENCE_BROADCASTS: Counter = register_counter!(
        "materi_presence_broadcasts_total",
        "Total presence broadcast events"
    ).unwrap();
}
```

### Grafana Dashboard Panels

| Panel | Query |
|-------|-------|
| Active Connections | `sum(materi_websocket_connections_active)` |
| Operations/sec | `rate(materi_operations_processed_total[5m])` |
| P95 Latency | `histogram_quantile(0.95, rate(materi_operation_latency_seconds_bucket[5m]))` |
| Error Rate | `rate(materi_operations_processed_total{status="error"}[5m])` |
| Memory Usage | `container_memory_usage_bytes{pod=~"relay.*"}` |

### Alerting Rules

```yaml
# prometheus/rules/relay.yaml
groups:
  - name: relay
    rules:
      - alert: RelayHighLatency
        expr: |
          histogram_quantile(0.95, rate(materi_operation_latency_seconds_bucket[5m])) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Relay P95 latency above 50ms"

      - alert: RelayConnectionDrop
        expr: |
          rate(materi_websocket_connections_active[1m]) < -100
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Rapid WebSocket connection drop detected"

      - alert: RelayHighErrorRate
        expr: |
          rate(materi_operations_processed_total{status="error"}[5m]) /
          rate(materi_operations_processed_total[5m]) > 0.01
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Relay operation error rate above 1%"
```

---

## Operational Procedures

### Graceful Shutdown

```rust
pub async fn graceful_shutdown(
    shutdown_signal: impl Future<Output = ()>,
    connection_manager: Arc<ConnectionManager>,
) {
    shutdown_signal.await;

    info!("Initiating graceful shutdown...");

    // Stop accepting new connections
    connection_manager.stop_accepting();

    // Notify all clients
    connection_manager.broadcast_shutdown_notice().await;

    // Wait for clients to disconnect (max 30 seconds)
    let timeout = Duration::from_secs(30);
    let start = Instant::now();

    while start.elapsed() < timeout && connection_manager.has_connections() {
        tokio::time::sleep(Duration::from_millis(100)).await;
    }

    // Force close remaining connections
    connection_manager.close_all().await;

    info!("Graceful shutdown complete");
}
```

### Rolling Update Procedure

```bash
# Trigger rolling update
kubectl set image deployment/relay relay=gcr.io/materi/relay:v2.1.0

# Monitor rollout
kubectl rollout status deployment/relay

# Rollback if needed
kubectl rollout undo deployment/relay
```

### Scaling

```bash
# Manual scale
kubectl scale deployment/relay --replicas=10

# View HPA status
kubectl get hpa relay

# Describe HPA metrics
kubectl describe hpa relay
```

---

## Performance Tuning

### Tokio Runtime Configuration

```rust
fn main() {
    let runtime = tokio::runtime::Builder::new_multi_thread()
        .worker_threads(num_cpus::get())
        .enable_all()
        .thread_name("relay-worker")
        .build()
        .expect("Failed to create Tokio runtime");

    runtime.block_on(async {
        // Start server
    });
}
```

### Connection Pool Settings

```rust
pub struct PoolConfig {
    pub redis_pool_size: u32,      // 50
    pub db_pool_size: u32,         // 20
    pub db_max_lifetime: Duration, // 30 minutes
    pub db_idle_timeout: Duration, // 10 minutes
}
```

---

## Disaster Recovery

### Backup Strategy

```bash
# Backup operations log
pg_dump -h $DB_HOST -U $DB_USER -t operations relay | gzip > operations_backup.sql.gz

# Backup Redis state
redis-cli -h $REDIS_HOST BGSAVE
```

### Recovery Time Objectives

| Scenario | RTO | RPO |
|----------|-----|-----|
| Pod failure | < 30 sec | 0 (in-memory ops) |
| Node failure | < 2 min | 0 |
| Redis failure | < 5 min | < 10 sec |
| Database failure | < 1 hour | < 1 min |
| Region failure | < 4 hours | < 5 min |

---

## Security Hardening

### Network Policies

```yaml
# k8s/network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: relay-network-policy
spec:
  podSelector:
    matchLabels:
      app: relay
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              name: ingress-nginx
      ports:
        - protocol: TCP
          port: 8081
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: redis
      ports:
        - protocol: TCP
          port: 6379
    - to:
        - podSelector:
            matchLabels:
              app: postgres
      ports:
        - protocol: TCP
          port: 5432
    - to:
        - podSelector:
            matchLabels:
              app: shield
      ports:
        - protocol: TCP
          port: 8000
```

---

## Related Documentation

- [Overview](overview) - Service overview
- [Architecture](architecture) - System design
- [Testing](testing) - Test strategies
- [Operations Runbook](/operations/relay-runbook) - Incident response

---

**Document Status:** Complete
**Version:** 2.0
