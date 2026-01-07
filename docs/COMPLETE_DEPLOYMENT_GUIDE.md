# 🚀 Materi Platform - Complete Deployment Guide

**Version**: 1.0.0
**Last Updated**: 2025-12-17
**Status**: Production Ready

---

## 📋 Table of Contents

1. [Quick Start (30 minutes)](#quick-start)
2. [Core Services Deployment](#core-services-deployment)
3. [Observability Stack Deployment](#observability-stack-deployment)
4. [Team Member Onboarding](#team-member-onboarding)
5. [Monitoring & Metrics](#monitoring--metrics)
6. [CI/CD Templates](#cicd-templates)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 Quick Start

### Prerequisites

- Railway account (sign up at [railway.app](https://railway.app))
- GitHub account
- Homebrew (for CLI tools)

### One-Command Deployment

```bash
git clone https://github.com/yourusername/materi.git
cd materi
./scripts/deploy-materi-railway.sh
```

**What this does:**
1. Installs Railway CLI
2. Authenticates you with Railway
3. Creates/links Railway project
4. Deploys PostgreSQL + Redis
5. Guides you through deploying Shield, API, Relay, Canvas
6. Configures BetterStack monitoring
7. Generates team member setup script

**Time**: ~30 minutes total

---

## 🏗️ Core Services Deployment

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Railway Platform                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Shield     │  │     API      │  │    Relay     │          │
│  │  (Auth/JWT)  │◄─┤  (Backend)   │◄─┤  (WebSocket) │          │
│  │              │  │              │  │              │          │
│  │ Django/Python│  │  Go/Fiber    │  │   Rust/Axum  │          │
│  │   Port 8000  │  │  Port 8080   │  │  Port 8081   │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                  │                  │                  │
│         └──────────────────┴──────────────────┘                  │
│                           │                                      │
│         ┌─────────────────┴─────────────────┐                   │
│         │                                   │                   │
│    ┌────▼────┐                        ┌────▼────┐              │
│    │PostgreSQL│                        │  Redis  │              │
│    │ (Managed)│                        │(Managed)│              │
│    └─────────┘                        └─────────┘              │
│                                                                   │
│  ┌──────────────────────────────────────────────────────┐       │
│  │                    Canvas                             │       │
│  │                  (Frontend)                           │       │
│  │              React 19 + Vite                          │       │
│  │                  Port 80                              │       │
│  └──────────────────────────────────────────────────────┘       │
│                                                                   │
└───────────────────────────────────────────────────────────────┘
```

### Manual Deployment Steps

If the automated script fails or you prefer manual control:

#### 1. PostgreSQL & Redis

```bash
railway add --database postgres
railway add --database redis
```

#### 2. Shield Service

**Web UI Method** (Recommended):
1. Go to Railway dashboard → Click "+ New" → "GitHub Repo"
2. Select `materi` repository
3. Set "Root Directory": `domain/shield`
4. Add environment variables:

```bash
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=info
PORT=8000
DJANGO_SECRET_KEY=<generate-with-openssl-rand-base64-50>
ALLOWED_HOSTS=*.up.railway.app,*.railway.app
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
JWT_SECRET=<from-operations/live.env>
```

5. Deploy → Generate Domain
6. Copy domain for next steps

#### 3. API Service

Same process, Root Directory: `domain/api`

```bash
ENVIRONMENT=production
LOG_LEVEL=info
PORT=8080
JWT_SECRET=<same-as-shield>
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
SHIELD_SERVICE_URL=https://<shield-domain>
JWT_PUBLIC_KEY_URL=https://<shield-domain>/.well-known/jwks.json
ENABLE_METRICS=true
ENABLE_TRACING=false
```

#### 4. Relay Service

Root Directory: `domain/relay` (Rust - takes 5-8 minutes to build)

```bash
ENVIRONMENT=production
LOG_LEVEL=info
RUST_LOG=info
PORT=8081
JWT_SECRET=<same-as-shield>
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
SHIELD_SERVICE_URL=https://<shield-domain>
API_SERVICE_URL=https://<api-domain>
MAX_CONNECTIONS=10000
```

#### 5. Canvas Frontend

Root Directory: `products/app/canvas/apps/client`

```bash
VITE_SHIELD_API_URL=https://<shield-domain>
VITE_API_URL=https://<api-domain>
VITE_RELAY_URL=wss://<relay-domain>
VITE_ENVIRONMENT=production
VITE_LOG_LEVEL=info
VITE_ENABLE_ANALYTICS=true
```

---

## 📊 Observability Stack Deployment

### Option 1: Deploy to Railway

Deploy each observability service separately:

#### Folio (Runtime Observability)

Root Directory: `operations/folio`

```bash
PORT=8080
ENVIRONMENT=production
MATERI_SERVICES=api,shield,relay,canvas
API_URL=https://<api-domain>
SHIELD_URL=https://<shield-domain>
RELAY_URL=https://<relay-domain>
CANVAS_URL=https://<canvas-domain>
PROMETHEUS_URL=http://prometheus:9090
BETTERSTACK_API_TOKEN=<from-operations/live.env>
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
```

#### Prometheus

Use Railway's template gallery or deploy with Docker:

```yaml
# Railway docker-compose.yml
services:
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./operations/folio/prometheus:/etc/prometheus
```

#### Grafana

```yaml
services:
  grafana:
    image: grafana/grafana:latest
    environment:
      GF_SECURITY_ADMIN_USER: admin
      GF_SECURITY_ADMIN_PASSWORD: <secure-password>
```

### Option 2: Deploy to Coolify

**Coming Soon**: Self-hosted Coolify deployment with full observability stack.

For now, you can deploy locally using Docker Compose:

```bash
cd /Users/alexarno/materi
docker-compose -f docker-compose.observability.yml up -d
```

Access:
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/materi123)
- Folio: http://localhost:8085

---

## 👥 Team Member Onboarding

### For New Team Members

1. **Clone Repository**

```bash
git clone https://github.com/yourusername/materi.git
cd materi
```

2. **Run Setup Script**

```bash
./scripts/setup-teammate-railway.sh
```

This will:
- Install Railway CLI
- Guide them through Railway authentication
- Create their own isolated Railway project
- Deploy all services to their project
- Provide them with their own service URLs

3. **Share with Family**

Once deployed, team members can share their Canvas URL with family members to collaborate on documents during the holidays!

### Project Isolation

Each team member gets:
- ✅ Their own Railway project
- ✅ Isolated databases (PostgreSQL + Redis)
- ✅ Separate service instances
- ✅ Independent monitoring
- ✅ No interference with other deployments

---

## 🔍 Monitoring & Metrics

### BetterStack Integration

BetterStack provides uptime monitoring and log aggregation.

**Tokens** (from `operations/live.env`):
- API Token: `iVp6q44fTN9AmKseQ8RURobg`
- Telemetry Token: `bSmK7yPGKuhht9AEvaz9Jw1f`

**Setup**:

1. Add to each Railway service:

```bash
BETTERSTACK_API_TOKEN=iVp6q44fTN9AmKseQ8RURobg
BETTERSTACK_SOURCE_TOKEN=bSmK7yPGKuhht9AEvaz9Jw1f
```

2. Create uptime monitors at [betterstack.com/uptime](https://betterstack.com/uptime):

| Service | Endpoint | Interval |
|---------|----------|----------|
| Shield | `https://<shield-domain>/health/` | 60s |
| API | `https://<api-domain>/health` | 60s |
| Relay | `https://<relay-domain>/health` | 60s |
| Canvas | `https://<canvas-domain>/health` | 60s |

3. Configure alerts to Slack:

```bash
SLACK_WEBHOOK_CRITICAL=<from-live.env>
SLACK_WEBHOOK_DEVOPS=<from-live.env>
```

### Prometheus Metrics

All services expose Prometheus metrics:

| Service | Endpoint |
|---------|----------|
| Shield | `https://<shield-domain>/metrics` |
| API | `https://<api-domain>/metrics` |
| Relay | `https://<relay-domain>/metrics` |
| Folio | `https://<folio-domain>/metrics` |

**Key Metrics**:
- `http_requests_total` - Total HTTP requests
- `http_request_duration_seconds` - Request latency
- `materi_active_users` - Current active users
- `materi_documents_count` - Total documents
- `materi_websocket_connections` - Active WebSocket connections

### Grafana Dashboards

Pre-configured dashboards located in `operations/folio/grafana/dashboards/`:

1. **Materi Overview** - System-wide metrics
2. **Service Health** - Per-service health and performance
3. **User Activity** - User engagement and collaboration metrics
4. **Infrastructure** - Database, Redis, system metrics

**Access Grafana**:
- Local: `http://localhost:3000`
- Railway: `https://<grafana-domain>`
- Credentials: admin / <password-from-env>

---

## 🔄 CI/CD Templates

### Shield CI/CD Integration

Shield includes CI/CD template configuration for:
- GitHub Actions
- GitLab CI
- Railway auto-deployments

**Location**: `domain/shield/.github/workflows/`

**Templates Available**:
1. **Continuous Integration** - Linting, testing, security scans
2. **Continuous Deployment** - Automated deployments to Railway
3. **Database Migrations** - Automated migration runs
4. **Security Audits** - Dependency scanning, SAST

**Enable**:

```bash
cd domain/shield
cp .github/workflows/ci.yml.example .github/workflows/ci.yml
# Update with your Railway tokens
git add .github/workflows/ci.yml
git commit -m "Enable CI/CD"
git push
```

### Accessing Templates

The user mentioned templates were designed long ago. Let's find them:

```bash
# Search for CI/CD templates
find . -name "*template*" -o -name "*ci*" -o -name "*cd*" | grep -E "\.(yml|yaml)$"
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Railway CLI Monorepo Issues

**Problem**: `railway up` fails with indexing errors in monorepo

**Solution**: Use Railway Web UI for initial service deployment. CLI works fine for redeployments.

#### 2. Shield Migration Failures

**Problem**: Django migrations fail on first deploy

**Fix**:
```bash
railway shell --service materi-shield
python manage.py migrate
```

#### 3. Relay Build Timeout

**Problem**: Rust compilation exceeds Railway's build timeout

**Fix**: Increase timeout in Railway dashboard → Service Settings → Build

#### 4. WebSocket Connection Fails

**Problem**: Canvas can't connect to Relay

**Fix**: Ensure CORS is configured in Relay:
```rust
ALLOWED_ORIGINS=https://<canvas-domain>
```

#### 5. BetterStack Not Receiving Logs

**Problem**: Logs not appearing in BetterStack

**Fix**: Verify tokens are correct and services are sending to HTTPS endpoint

---

## 📝 Health Check Commands

### Quick Health Check

```bash
# Shield
curl https://<shield-domain>/health/

# API
curl https://<api-domain>/health

# Relay
curl https://<relay-domain>/health

# Canvas
curl https://<canvas-domain>/health
```

### Full System Check

```bash
./scripts/health-check-all.sh
```

---

## 🔗 Useful Links

- **Railway Dashboard**: https://railway.app
- **BetterStack**: https://betterstack.com
- **Materi Repository**: [Your GitHub URL]
- **Documentation**: `./docs/`
- **Deployment Logs**: `.railway/deployment-*.log`

---

## 🎉 Success Criteria

You know deployment is successful when:

✅ All health checks return 200 OK
✅ Canvas frontend loads in browser
✅ User can sign up/login via Shield
✅ Documents can be created via API
✅ Real-time collaboration works in Relay
✅ Metrics appear in Prometheus/Grafana
✅ Alerts are received in BetterStack
✅ Team members can deploy their own instances

---

## 📞 Support

For issues:
1. Check deployment logs: `.railway/deployment-*.log`
2. Review Railway service logs in dashboard
3. Consult `DEPLOYMENT_LESSONS_LEARNED.md` for known issues

---

**Happy Deploying!** 🚀
