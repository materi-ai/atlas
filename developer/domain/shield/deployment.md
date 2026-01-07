# Shield Deployment

<Info>
**SDD Classification:** L4-Operational
**Authority:** Platform Team
**Review Cycle:** Monthly
</Info>

This document covers Shield service deployment including Docker configuration, Kubernetes manifests, environment variables, health checks, and operational procedures.

---

## Deployment Architecture

```mermaid
flowchart TD
    subgraph "Load Balancer"
        A[Ingress / ALB]
    end

    subgraph "Shield Service"
        B[Pod 1<br/>Gunicorn]
        C[Pod 2<br/>Gunicorn]
        D[Pod 3<br/>Gunicorn]
    end

    subgraph "Data Layer"
        E[(PostgreSQL)]
        F[(Redis)]
    end

    subgraph "External"
        G[OAuth Providers]
        H[SAML IdPs]
        I[Email Service]
    end

    A --> B
    A --> C
    A --> D

    B --> E
    B --> F
    C --> E
    C --> F
    D --> E
    D --> F

    B --> G
    B --> H
    B --> I
```

---

## Docker Configuration

### Dockerfile

```dockerfile
# Multi-stage build for optimized production image
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# Production image
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r shield && useradd -r -g shield shield

# Copy wheels and install
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

# Copy application
COPY --chown=shield:shield . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Security: non-root user
USER shield

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

EXPOSE 8000

# Gunicorn entrypoint
CMD ["gunicorn", "config.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "4", \
     "--worker-class", "gthread", \
     "--threads", "2", \
     "--timeout", "30", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--capture-output", \
     "--enable-stdio-inheritance"]
```

### Docker Compose (Development)

```yaml
# docker-compose.yml
version: '3.8'

services:
  shield:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings.development
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/shield
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=dev-secret-key-change-in-production
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - .:/app
    command: python manage.py runserver 0.0.0.0:8000

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: shield
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
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

---

## Kubernetes Deployment

### Deployment Manifest

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: shield
  labels:
    app: shield
    component: auth
spec:
  replicas: 3
  selector:
    matchLabels:
      app: shield
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    metadata:
      labels:
        app: shield
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8000"
        prometheus.io/path: "/metrics/"
    spec:
      serviceAccountName: shield
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      containers:
        - name: shield
          image: gcr.io/materi/shield:latest
          ports:
            - containerPort: 8000
              name: http
          env:
            - name: DJANGO_SETTINGS_MODULE
              value: config.settings.production
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: shield-secrets
                  key: database-url
            - name: REDIS_URL
              valueFrom:
                secretKeyRef:
                  name: shield-secrets
                  key: redis-url
            - name: SECRET_KEY
              valueFrom:
                secretKeyRef:
                  name: shield-secrets
                  key: secret-key
            - name: JWT_PRIVATE_KEY
              valueFrom:
                secretKeyRef:
                  name: shield-secrets
                  key: jwt-private-key
          resources:
            requests:
              memory: "512Mi"
              cpu: "250m"
            limits:
              memory: "1Gi"
              cpu: "1000m"
          livenessProbe:
            httpGet:
              path: /health/
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 15
            timeoutSeconds: 5
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /ready/
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 10
            timeoutSeconds: 5
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
                        - shield
                topologyKey: kubernetes.io/hostname
```

### Service Manifest

```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: shield
  labels:
    app: shield
spec:
  type: ClusterIP
  ports:
    - port: 80
      targetPort: 8000
      protocol: TCP
      name: http
  selector:
    app: shield
```

### Ingress Configuration

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: shield
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
spec:
  tls:
    - hosts:
        - api.materi.dev
      secretName: shield-tls
  rules:
    - host: api.materi.dev
      http:
        paths:
          - path: /auth
            pathType: Prefix
            backend:
              service:
                name: shield
                port:
                  number: 80
          - path: /api/users
            pathType: Prefix
            backend:
              service:
                name: shield
                port:
                  number: 80
          - path: /api/workspaces
            pathType: Prefix
            backend:
              service:
                name: shield
                port:
                  number: 80
          - path: /.well-known/jwks.json
            pathType: Exact
            backend:
              service:
                name: shield
                port:
                  number: 80
```

### Horizontal Pod Autoscaler

```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: shield
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: shield
  minReplicas: 3
  maxReplicas: 10
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
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/shield` |
| `REDIS_URL` | Redis connection string | `redis://host:6379/0` |
| `SECRET_KEY` | Django secret key | Random 50+ char string |
| `JWT_PRIVATE_KEY` | RSA private key for JWT signing | PEM-encoded key |
| `JWT_PUBLIC_KEY` | RSA public key for JWT validation | PEM-encoded key |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DJANGO_SETTINGS_MODULE` | `config.settings.production` | Settings module |
| `DEBUG` | `False` | Debug mode |
| `ALLOWED_HOSTS` | `*` | Comma-separated allowed hosts |
| `DATABASE_POOL_SIZE` | `50` | Database connection pool |
| `LOG_LEVEL` | `INFO` | Logging level |
| `ENABLE_METRICS` | `true` | Prometheus metrics |
| `ENABLE_TRACING` | `true` | Distributed tracing |

### OAuth Provider Variables

| Variable | Description |
|----------|-------------|
| `GOOGLE_CLIENT_ID` | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret |
| `GITHUB_CLIENT_ID` | GitHub OAuth client ID |
| `GITHUB_CLIENT_SECRET` | GitHub OAuth client secret |
| `MICROSOFT_CLIENT_ID` | Microsoft OAuth client ID |
| `MICROSOFT_CLIENT_SECRET` | Microsoft OAuth client secret |

### SAML Variables

| Variable | Description |
|----------|-------------|
| `SAML_SP_ENTITY_ID` | Service Provider entity ID |
| `SAML_SP_X509_CERT` | SP certificate (PEM) |
| `SAML_SP_PRIVATE_KEY` | SP private key (PEM) |

---

## Health Endpoints

### Basic Health Check

```http
GET /health/
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "version": "2.1.0",
  "timestamp": "2025-01-07T10:00:00Z"
}
```

### Readiness Check

```http
GET /ready/
```

**Response (200 OK):**
```json
{
  "status": "ready",
  "checks": {
    "database": "ok",
    "redis": "ok",
    "migrations": "ok"
  }
}
```

**Response (503 Service Unavailable):**
```json
{
  "status": "not_ready",
  "checks": {
    "database": "ok",
    "redis": "error",
    "migrations": "ok"
  },
  "errors": ["Redis connection failed"]
}
```

### Health Check Implementation

```python
# apps/health/views.py
from django.http import JsonResponse
from django.db import connection
from django_redis import get_redis_connection

def health_check(request):
    """Basic health check - service is running."""
    return JsonResponse({
        'status': 'healthy',
        'version': settings.VERSION,
        'timestamp': datetime.utcnow().isoformat()
    })

def readiness_check(request):
    """Readiness check - all dependencies available."""
    checks = {}
    errors = []

    # Database check
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        checks['database'] = 'ok'
    except Exception as e:
        checks['database'] = 'error'
        errors.append(f'Database: {str(e)}')

    # Redis check
    try:
        redis = get_redis_connection()
        redis.ping()
        checks['redis'] = 'ok'
    except Exception as e:
        checks['redis'] = 'error'
        errors.append(f'Redis: {str(e)}')

    # Migrations check
    try:
        from django.core.management import call_command
        from io import StringIO
        out = StringIO()
        call_command('showmigrations', '--plan', stdout=out)
        if '[ ]' in out.getvalue():
            checks['migrations'] = 'pending'
            errors.append('Pending migrations')
        else:
            checks['migrations'] = 'ok'
    except Exception as e:
        checks['migrations'] = 'error'
        errors.append(f'Migrations: {str(e)}')

    status_code = 200 if not errors else 503

    return JsonResponse({
        'status': 'ready' if not errors else 'not_ready',
        'checks': checks,
        'errors': errors if errors else None
    }, status=status_code)
```

---

## Database Migrations

### Running Migrations

```bash
# Local development
python manage.py migrate

# Production (Kubernetes job)
kubectl apply -f k8s/migration-job.yaml
```

### Migration Job Manifest

```yaml
# k8s/migration-job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: shield-migrate
  annotations:
    argocd.argoproj.io/hook: PreSync
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: migrate
          image: gcr.io/materi/shield:latest
          command: ["python", "manage.py", "migrate", "--noinput"]
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: shield-secrets
                  key: database-url
          resources:
            requests:
              memory: "256Mi"
              cpu: "100m"
            limits:
              memory: "512Mi"
              cpu: "500m"
  backoffLimit: 3
```

### Migration Safety

```python
# Backward-compatible migration example
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('users', '0010_previous_migration'),
    ]

    operations = [
        # Safe: Add nullable column first
        migrations.AddField(
            model_name='user',
            name='new_field',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        # Then in next deployment, backfill and make NOT NULL
    ]
```

---

## Monitoring & Observability

### Prometheus Metrics

```python
# apps/metrics/middleware.py
from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter(
    'materi_shield_requests_total',
    'Total requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'materi_shield_request_duration_seconds',
    'Request latency',
    ['method', 'endpoint'],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)

AUTH_ATTEMPTS = Counter(
    'materi_auth_attempts_total',
    'Authentication attempts',
    ['method', 'status']  # method: email, oauth, saml
)

TOKEN_OPERATIONS = Counter(
    'materi_token_operations_total',
    'Token operations',
    ['operation', 'status']  # operation: issue, refresh, revoke
)
```

### Grafana Dashboard

Key panels for Shield monitoring:

| Panel | Query |
|-------|-------|
| Request Rate | `rate(materi_shield_requests_total[5m])` |
| Error Rate | `rate(materi_shield_requests_total{status=~"5.."}[5m])` |
| Auth Success Rate | `sum(rate(materi_auth_attempts_total{status="success"}[5m])) / sum(rate(materi_auth_attempts_total[5m]))` |
| P95 Latency | `histogram_quantile(0.95, rate(materi_shield_request_duration_seconds_bucket[5m]))` |
| Active Tokens | `sum(materi_active_refresh_tokens)` |

### Alerting Rules

```yaml
# prometheus/rules/shield.yaml
groups:
  - name: shield
    rules:
      - alert: ShieldHighErrorRate
        expr: |
          sum(rate(materi_shield_requests_total{status=~"5.."}[5m])) /
          sum(rate(materi_shield_requests_total[5m])) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Shield error rate above 5%"

      - alert: ShieldHighLatency
        expr: |
          histogram_quantile(0.95, rate(materi_shield_request_duration_seconds_bucket[5m])) > 0.5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Shield P95 latency above 500ms"

      - alert: ShieldAuthFailureSpike
        expr: |
          rate(materi_auth_attempts_total{status="failure"}[5m]) > 100
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "Possible brute force attack detected"
```

---

## Operational Procedures

### Deployment Checklist

1. **Pre-deployment:**
   - [ ] Run migrations in staging
   - [ ] Verify health checks pass
   - [ ] Review resource limits
   - [ ] Check secrets are configured

2. **Deployment:**
   - [ ] Apply migration job
   - [ ] Deploy new image
   - [ ] Monitor rollout progress
   - [ ] Verify pod health

3. **Post-deployment:**
   - [ ] Check error rates
   - [ ] Verify auth flows work
   - [ ] Monitor latency metrics
   - [ ] Test OAuth/SAML if changed

### Rollback Procedure

```bash
# Kubernetes rollback
kubectl rollout undo deployment/shield

# Check rollback status
kubectl rollout status deployment/shield

# View rollout history
kubectl rollout history deployment/shield
```

### Scaling

```bash
# Manual scale
kubectl scale deployment/shield --replicas=5

# View current scale
kubectl get hpa shield
```

---

## Secrets Management

### Kubernetes Secrets

```yaml
# k8s/secrets.yaml (use sealed-secrets or external-secrets in production)
apiVersion: v1
kind: Secret
metadata:
  name: shield-secrets
type: Opaque
stringData:
  database-url: postgresql://user:password@host:5432/shield
  redis-url: redis://host:6379/0
  secret-key: your-django-secret-key
  jwt-private-key: |
    -----BEGIN RSA PRIVATE KEY-----
    ...
    -----END RSA PRIVATE KEY-----
```

### Key Rotation

```python
# Key rotation procedure
# 1. Generate new key pair
# 2. Add new public key to JWKS endpoint (both keys active)
# 3. Update signing to use new private key
# 4. Wait for old tokens to expire (15 min for access, 30 days for refresh)
# 5. Remove old public key from JWKS

JWKS_KEYS = [
    {
        'kid': 'key_2025_01',  # Current key
        'kty': 'RSA',
        'use': 'sig',
        'alg': 'RS256',
        'n': '...',
        'e': 'AQAB'
    },
    {
        'kid': 'key_2024_10',  # Previous key (for validation only)
        'kty': 'RSA',
        'use': 'sig',
        'alg': 'RS256',
        'n': '...',
        'e': 'AQAB'
    }
]
```

---

## Backup & Recovery

### Database Backup

```bash
# Daily backup (via CronJob)
pg_dump -h $DB_HOST -U $DB_USER -d shield | gzip > backup_$(date +%Y%m%d).sql.gz
aws s3 cp backup_*.sql.gz s3://materi-backups/shield/

# Point-in-time recovery
pg_restore -h $DB_HOST -U $DB_USER -d shield_restore backup.sql.gz
```

### Recovery Time Objectives

| Scenario | RTO | RPO |
|----------|-----|-----|
| Pod failure | < 1 min | 0 |
| Node failure | < 5 min | 0 |
| Database failure | < 1 hour | < 5 min |
| Region failure | < 4 hours | < 15 min |

---

## Related Documentation

- [Overview](overview) - Service overview
- [Architecture](architecture) - System design
- [Testing](testing) - Test strategies
- [Operations Runbook](/operations/shield-runbook) - Incident response

---

**Document Status:** Complete
**Version:** 2.0
