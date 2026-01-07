# API Service Deployment

<Info>
**SDD Classification:** L4-Operational
**Authority:** Engineering Team
**Review Cycle:** Quarterly
</Info>

This document covers deployment configuration and procedures for Materi's API Service, including Docker builds, Kubernetes manifests, and operational guidelines.

---

## Docker Configuration

### Multi-Stage Dockerfile

```dockerfile
# Build stage
FROM golang:1.25-alpine AS builder

# Install build dependencies
RUN apk add --no-cache git ca-certificates tzdata

WORKDIR /build

# Cache dependencies
COPY go.mod go.sum ./
RUN go mod download

# Build arguments
ARG VERSION=dev
ARG GIT_COMMIT=unknown
ARG BUILD_TIME

# Copy source and build
COPY . .
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build \
    -ldflags="-w -s \
        -X main.version=${VERSION} \
        -X main.commit=${GIT_COMMIT} \
        -X main.buildTime=${BUILD_TIME}" \
    -o /app/api ./cmd/api

# Migration tool
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build \
    -ldflags="-w -s" \
    -o /app/migrate ./cmd/migrate

# Runtime stage
FROM alpine:3.19

# Security: non-root user
RUN addgroup -g 1000 -S materi && \
    adduser -u 1000 -S materi -G materi

# Install runtime dependencies
RUN apk add --no-cache ca-certificates tzdata

WORKDIR /app

# Copy binaries
COPY --from=builder /app/api /app/api
COPY --from=builder /app/migrate /app/migrate

# Copy migrations
COPY migrations/ /app/migrations/

# Set ownership
RUN chown -R materi:materi /app

USER materi

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ["/app/api", "health"]

EXPOSE 8080 9090

ENTRYPOINT ["/app/api"]
```

### Build Commands

```bash
# Development build
docker build -t materi-api:dev .

# Production build with version
docker build \
    --build-arg VERSION=$(git describe --tags) \
    --build-arg GIT_COMMIT=$(git rev-parse HEAD) \
    --build-arg BUILD_TIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ") \
    -t materi-api:$(git describe --tags) .

# Multi-platform build
docker buildx build \
    --platform linux/amd64,linux/arm64 \
    --build-arg VERSION=$(git describe --tags) \
    -t ghcr.io/materi/api:$(git describe --tags) \
    --push .
```

---

## Kubernetes Deployment

### Namespace and ConfigMap

```yaml
# kubernetes/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: materi
  labels:
    name: materi
    istio-injection: enabled

---
# kubernetes/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: api-config
  namespace: materi
data:
  ENVIRONMENT: production
  LOG_LEVEL: info
  API_PORT: "8080"
  METRICS_PORT: "9090"
  DATABASE_POOL_SIZE: "20"
  DATABASE_TIMEOUT: "30s"
  REDIS_POOL_SIZE: "50"
  ENABLE_AI_FEATURES: "true"
  ENABLE_COLLABORATION: "true"
```

### Secrets

```yaml
# kubernetes/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: api-secrets
  namespace: materi
type: Opaque
stringData:
  DATABASE_URL: postgresql://user:pass@postgres:5432/materi
  REDIS_URL: redis://:password@redis:6379
  JWT_PUBLIC_KEY: |
    -----BEGIN PUBLIC KEY-----
    ...
    -----END PUBLIC KEY-----
  SHIELD_INTERNAL_SECRET: <shield-secret>
  OPENAI_API_KEY: <openai-key>
  ANTHROPIC_API_KEY: <anthropic-key>
```

### Deployment

```yaml
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  namespace: materi
  labels:
    app: api
    version: v1
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    metadata:
      labels:
        app: api
        version: v1
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "9090"
        prometheus.io/path: "/metrics"
    spec:
      serviceAccountName: api
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      containers:
        - name: api
          image: ghcr.io/materi/api:v1.0.0
          imagePullPolicy: IfNotPresent
          ports:
            - name: http
              containerPort: 8080
              protocol: TCP
            - name: metrics
              containerPort: 9090
              protocol: TCP
          envFrom:
            - configMapRef:
                name: api-config
            - secretRef:
                name: api-secrets
          resources:
            requests:
              cpu: 500m
              memory: 512Mi
            limits:
              cpu: 2000m
              memory: 2Gi
          livenessProbe:
            httpGet:
              path: /health
              port: http
            initialDelaySeconds: 10
            periodSeconds: 10
            timeoutSeconds: 5
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /ready
              port: http
            initialDelaySeconds: 5
            periodSeconds: 5
            timeoutSeconds: 3
            failureThreshold: 3
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop:
                - ALL
          volumeMounts:
            - name: tmp
              mountPath: /tmp
            - name: cache
              mountPath: /app/.cache
      volumes:
        - name: tmp
          emptyDir: {}
        - name: cache
          emptyDir: {}
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
            - weight: 100
              podAffinityTerm:
                labelSelector:
                  matchLabels:
                    app: api
                topologyKey: kubernetes.io/hostname
      topologySpreadConstraints:
        - maxSkew: 1
          topologyKey: topology.kubernetes.io/zone
          whenUnsatisfiable: ScheduleAnyway
          labelSelector:
            matchLabels:
              app: api
```

### Service

```yaml
# kubernetes/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: api
  namespace: materi
  labels:
    app: api
spec:
  type: ClusterIP
  ports:
    - name: http
      port: 80
      targetPort: http
      protocol: TCP
    - name: metrics
      port: 9090
      targetPort: metrics
      protocol: TCP
  selector:
    app: api
```

### HorizontalPodAutoscaler

```yaml
# kubernetes/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api
  namespace: materi
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api
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
          name: http_requests_per_second
        target:
          type: AverageValue
          averageValue: 1000
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 10
          periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
        - type: Percent
          value: 100
          periodSeconds: 15
        - type: Pods
          value: 4
          periodSeconds: 15
      selectPolicy: Max
```

### PodDisruptionBudget

```yaml
# kubernetes/pdb.yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: api
  namespace: materi
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: api
```

---

## Ingress Configuration

### Nginx Ingress

```yaml
# kubernetes/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api
  namespace: materi
  annotations:
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "50m"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "60"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "60"
    nginx.ingress.kubernetes.io/limit-rps: "100"
    nginx.ingress.kubernetes.io/limit-connections: "50"
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
    - hosts:
        - api.materi.dev
      secretName: api-tls
  rules:
    - host: api.materi.dev
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: api
                port:
                  number: 80
```

---

## Database Migrations

### Migration Job

```yaml
# kubernetes/migration-job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: api-migrate
  namespace: materi
spec:
  backoffLimit: 3
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: migrate
          image: ghcr.io/materi/api:v1.0.0
          command: ["/app/migrate", "up"]
          envFrom:
            - secretRef:
                name: api-secrets
```

### Pre-Deployment Hook

```yaml
# kubernetes/migration-hook.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: api-migrate-{{ .Release.Revision }}
  namespace: materi
  annotations:
    helm.sh/hook: pre-upgrade
    helm.sh/hook-weight: "-5"
    helm.sh/hook-delete-policy: before-hook-creation
spec:
  backoffLimit: 3
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: migrate
          image: ghcr.io/materi/api:{{ .Values.image.tag }}
          command: ["/app/migrate", "up"]
          envFrom:
            - secretRef:
                name: api-secrets
```

---

## Environment Variables Reference

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection | `postgresql://user:pass@host:5432/db` |
| `REDIS_URL` | Redis connection | `redis://:pass@host:6379` |
| `JWT_PUBLIC_KEY` | JWT verification key | PEM encoded public key |
| `SHIELD_URL` | Shield service URL | `http://shield:8000` |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | `development` | Environment name |
| `LOG_LEVEL` | `info` | Logging level |
| `API_PORT` | `8080` | HTTP listen port |
| `METRICS_PORT` | `9090` | Metrics port |
| `DATABASE_POOL_SIZE` | `20` | Connection pool size |
| `DATABASE_TIMEOUT` | `30s` | Query timeout |
| `REDIS_POOL_SIZE` | `50` | Redis pool size |
| `ENABLE_AI_FEATURES` | `true` | AI feature flag |
| `ENABLE_COLLABORATION` | `true` | Collab feature flag |

---

## Deployment Procedures

### Rolling Deployment

```bash
# Update image
kubectl set image deployment/api api=ghcr.io/materi/api:v1.1.0 -n materi

# Monitor rollout
kubectl rollout status deployment/api -n materi

# View rollout history
kubectl rollout history deployment/api -n materi

# Rollback if needed
kubectl rollout undo deployment/api -n materi
```

### Blue-Green Deployment

```bash
# Deploy green version
kubectl apply -f kubernetes/deployment-green.yaml

# Verify green is healthy
kubectl wait --for=condition=available deployment/api-green -n materi

# Switch traffic
kubectl patch service api -n materi -p '{"spec":{"selector":{"version":"green"}}}'

# Verify and cleanup blue
kubectl delete deployment api-blue -n materi
```

### Canary Deployment

```yaml
# kubernetes/canary.yaml
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: api
  namespace: materi
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api
  progressDeadlineSeconds: 600
  service:
    port: 80
    targetPort: http
  analysis:
    interval: 30s
    threshold: 5
    maxWeight: 50
    stepWeight: 10
    metrics:
      - name: request-success-rate
        threshold: 99
      - name: request-duration
        threshold: 500
        interval: 30s
```

---

## Health Checks

### Health Endpoint Implementation

```go
// internal/controller/health.go
func (c *HealthController) Health(ctx *fiber.Ctx) error {
    return ctx.JSON(fiber.Map{
        "status":  "healthy",
        "version": c.version,
        "uptime":  time.Since(c.startTime).String(),
    })
}

func (c *HealthController) Ready(ctx *fiber.Ctx) error {
    checks := make(map[string]string)
    healthy := true

    // Check database
    if err := c.db.PingContext(ctx.Context()); err != nil {
        checks["database"] = "error: " + err.Error()
        healthy = false
    } else {
        checks["database"] = "ok"
    }

    // Check Redis
    if _, err := c.redis.Ping(ctx.Context()).Result(); err != nil {
        checks["redis"] = "error: " + err.Error()
        healthy = false
    } else {
        checks["redis"] = "ok"
    }

    // Check Shield
    if err := c.checkShield(ctx.Context()); err != nil {
        checks["shield"] = "error: " + err.Error()
        healthy = false
    } else {
        checks["shield"] = "ok"
    }

    status := "ready"
    statusCode := 200
    if !healthy {
        status = "not_ready"
        statusCode = 503
    }

    return ctx.Status(statusCode).JSON(fiber.Map{
        "status": status,
        "checks": checks,
    })
}
```

---

## Monitoring

### Prometheus ServiceMonitor

```yaml
# kubernetes/servicemonitor.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: api
  namespace: materi
  labels:
    app: api
spec:
  selector:
    matchLabels:
      app: api
  endpoints:
    - port: metrics
      interval: 15s
      path: /metrics
  namespaceSelector:
    matchNames:
      - materi
```

### Grafana Dashboard

Key panels:
- Request rate by endpoint
- Response time percentiles
- Error rate by status code
- Active connections
- Database connection pool
- Redis operations
- CPU and memory usage

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Pod CrashLoopBackOff | Database connection failure | Check DATABASE_URL secret |
| 503 Service Unavailable | No ready pods | Check readiness probe logs |
| High latency | Database connection exhaustion | Increase pool size |
| OOMKilled | Memory limit too low | Increase memory limit |

### Debug Commands

```bash
# View pod logs
kubectl logs -f deployment/api -n materi

# Exec into pod
kubectl exec -it deployment/api -n materi -- /bin/sh

# Port forward for local debugging
kubectl port-forward svc/api 8080:80 -n materi

# Describe pod for events
kubectl describe pod -l app=api -n materi
```

---

## Related Documentation

- [Overview](overview) - Service overview
- [Architecture](architecture) - System design
- [Setup](setup) - Development environment
- [Testing](testing) - Test strategies

---

**Document Status:** Complete
**Version:** 2.0
