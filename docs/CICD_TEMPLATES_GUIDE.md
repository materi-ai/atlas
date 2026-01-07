# 🔄 Materi Platform - CI/CD Templates Guide

**Version**: 1.0.0
**Last Updated**: 2025-12-17
**Location**: `/operations/.workflows/`

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Available Workflows](#available-workflows)
3. [Quick Setup](#quick-setup)
4. [Service-Specific Pipelines](#service-specific-pipelines)
5. [Deployment Workflows](#deployment-workflows)
6. [Security & Quality](#security--quality)
7. [Railway Integration](#railway-integration)
8. [Team Access](#team-access)

---

## 🎯 Overview

The Materi platform includes comprehensive CI/CD templates for:
- ✅ Automated testing and linting
- ✅ Security scanning (SAST, dependency checks)
- ✅ Multi-service builds (API, Shield, Relay)
- ✅ Environment-specific deployments (staging, production)
- ✅ Multi-repo orchestration
- ✅ Quality gates and approval flows

**All templates are located in**: `/Users/alexarno/materi/operations/.workflows/`

---

## 📦 Available Workflows

### Core CI/CD Pipelines

| Workflow | File | Purpose |
|----------|------|---------|
| **Main CI/CD** | `main-cicd.yml` | Complete pipeline for all services |
| **Main Pipeline** | `main-pipeline.yml` | Comprehensive build & deploy (41KB - full featured) |
| **Multi-Repo Assembly** | `multi-repo-assembly.yml` | Orchestrates builds across multiple repos |
| **Multi-Repo Sync** | `multi-repo-sync.yml` | Keeps related repos in sync |

### Service-Specific Builds

| Service | File | Description |
|---------|------|-------------|
| **Shield** | `ci-build-shield.yml` | Django/Python CI pipeline |
| **API** | `ci-build-api.yml` | Go/Fiber CI pipeline |
| **Relay** | `ci-build-relay.yml` | Rust/Axum CI pipeline |
| **Aria** | `ci-test-aria.yml` | AI gateway tests |

### Deployment Workflows

| Environment | File | Features |
|-------------|------|----------|
| **Production** | `deploy-production.yml` | Approval gates, rollback support |
| **Staging** | `deploy-staging.yml` | Auto-deploy from develop branch |

### Security & Quality

| Type | File | Tools |
|------|------|-------|
| **Security Scan** | `security-scan.yml` | Trivy, Semgrep, dependency checks |
| **Secrets Management** | `security/secrets-management.yml` | Secret scanning, rotation |
| **Security Scanning** | `security/security-scanning.yml` | SAST, DAST, container scanning |
| **PR Quality** | `pr-quality-checks.yml` | Code quality gates for PRs |

### Specialized Workflows

| Workflow | File | Purpose |
|----------|------|---------|
| **Relay Tests** | `relay-tests.yml` | Comprehensive Rust test suite (30KB) |
| **Relay Security** | `relay-security.yml` | Rust-specific security checks |
| **Relay Release** | `relay-release.yml` | Release automation for Relay |
| **Aria Load Tests** | `aria-load-tests.yml` | Performance testing for AI gateway |
| **Aria Quality** | `aria-quality-checks.yml` | AI-specific quality metrics |

---

## 🚀 Quick Setup

### 1. Copy Workflows to Project

The workflows are already in `/operations/.workflows/`. To activate them for GitHub Actions:

```bash
# Copy to GitHub Actions directory
cp -r operations/.workflows/* .github/workflows/

# Or create symbolic links
mkdir -p .github/workflows
ln -s ../../operations/.workflows/* .github/workflows/
```

### 2. Set GitHub Secrets

Add these secrets to your GitHub repository (Settings → Secrets → Actions):

```bash
# Railway
RAILWAY_TOKEN=<your-railway-api-token>
RAILWAY_PROJECT_ID=<your-project-id>

# Container Registry
GHCR_TOKEN=${{ secrets.GITHUB_TOKEN }}  # Automatic

# Database
DATABASE_URL=<from-railway>
REDIS_URL=<from-railway>

# Security
JWT_SECRET=<from-operations/live.env>
DJANGO_SECRET_KEY=<generated>

# Monitoring
BETTERSTACK_API_TOKEN=iVp6q44fTN9AmKseQ8RURobg
BETTERSTACK_TELEMETRY_TOKEN=bSmK7yPGKuhht9AEvaz9Jw1f

# Notifications
SLACK_WEBHOOK_CRITICAL=<from-operations/live.env>
SLACK_WEBHOOK_DEVOPS=<from-operations/live.env>
```

### 3. Enable Workflows

Commit and push to activate:

```bash
git add .github/workflows/
git commit -m "Enable CI/CD workflows"
git push origin main
```

---

## 🛠️ Service-Specific Pipelines

### Shield Service (Django/Python)

**File**: `operations/.workflows/ci-build-shield.yml`

**Features**:
- Flake8 linting with max-line-length=100
- Black code formatting checks
- isort import sorting
- MyPy type checking
- Semgrep SAST scanning
- Django test suite
- Database migration validation
- Docker image build & push

**Triggers**:
- Push to main/develop/staging
- Pull requests affecting `shield/**`
- Tagged releases (`v*`)

**Usage**:
```bash
# Manually trigger
gh workflow run ci-build-shield.yml

# View status
gh run list --workflow=ci-build-shield.yml
```

### API Service (Go)

**File**: `operations/.workflows/ci-build-api.yml`

**Features**:
- golangci-lint with comprehensive rules
- Go test suite with race detector
- Go vet static analysis
- gosec security scanning
- Docker multi-stage builds
- Binary artifact uploads

**Environment Variables**:
```yaml
GO_VERSION: "1.25"
CGO_ENABLED: 0
GOOS: linux
GOARCH: amd64
```

### Relay Service (Rust)

**File**: `operations/.workflows/ci-build-relay.yml`

**Features**:
- Cargo clippy linting
- Cargo fmt formatting checks
- Cargo audit for vulnerabilities
- Cargo test with coverage
- Cross-compilation support
- Optimized release builds

**Special Notes**:
- Uses Rust 1.78+ for performance
- Aggressive optimization flags
- Static linking for portability

---

## 🚢 Deployment Workflows

### Production Deployment

**File**: `operations/.workflows/deploy-production.yml`

**Safety Features**:
1. ✅ **Pre-deployment checks**
   - Verifies main branch only
   - Requires approval ticket number
   - Checks git tags
   - Monitors deployment frequency

2. ✅ **n8n Approval Workflow**
   - Triggers external approval system
   - Blocks deployment until approved
   - Logs approval decisions

3. ✅ **Folio Health Check**
   - Queries Folio observability service
   - Verifies all critical services healthy
   - Blocks deployment if unhealthy

4. ✅ **Smoke Tests**
   - Post-deployment verification
   - Health endpoint checks
   - Rollback on failure

**Manual Trigger**:
```bash
# Via GitHub CLI
gh workflow run deploy-production.yml \
  -f service=shield \
  -f approval_ticket=TICKET-123

# Via GitHub UI
Actions → Deploy to Production → Run workflow
```

**Required Inputs**:
- `service`: api, shield, relay, or all
- `approval_ticket`: JIRA/Linear/GitHub issue number

### Staging Deployment

**File**: `operations/.workflows/deploy-staging.yml`

**Auto-deployment**:
- Triggers on push to `develop` branch
- No approval required
- Faster iteration
- Separate database instance

---

## 🔒 Security & Quality

### Security Scanning

**File**: `operations/.workflows/security-scan.yml`

**Scans**:
1. **Trivy** - Container vulnerability scanning
2. **Semgrep** - SAST for Python, Go, Rust
3. **gosec** - Go security analyzer
4. **Bandit** - Python security linter
5. **cargo-audit** - Rust dependency vulnerabilities
6. **npm audit** - JavaScript dependencies

**Results**: Published to GitHub Security tab

### Secrets Management

**File**: `operations/.workflows/security/secrets-management.yml`

**Features**:
- Scans for hardcoded secrets
- Validates secret rotation policies
- Checks for leaked credentials
- Integrates with GitGuardian

### PR Quality Checks

**File**: `operations/.workflows/pr-quality-checks.yml`

**Gates**:
- ✅ All tests pass
- ✅ Linting passes
- ✅ Code coverage meets threshold (80%)
- ✅ No security vulnerabilities
- ✅ Conventional commit messages
- ✅ PR description completed

---

## 🚂 Railway Integration

### Automated Railway Deployment

Add Railway deployment step to any workflow:

```yaml
- name: Deploy to Railway
  env:
    RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
  run: |
    npm install -g @railway/cli
    railway link ${{ secrets.RAILWAY_PROJECT_ID }}
    railway up --service materi-shield --detach
```

### Service-Specific Railway Configs

**Shield**:
```yaml
railway up --service materi-shield \
  --environment production \
  --variable DJANGO_SECRET_KEY=${{ secrets.DJANGO_SECRET_KEY }}
```

**API**:
```yaml
railway up --service materi-api \
  --environment production \
  --variable JWT_SECRET=${{ secrets.JWT_SECRET }}
```

**Relay**:
```yaml
railway up --service materi-relay \
  --environment production \
  --variable RUST_LOG=info
```

### Environment Variable Sync

Use this workflow to sync GitHub secrets to Railway:

```yaml
- name: Sync secrets to Railway
  run: |
    railway variables set \
      --service ${{ inputs.service }} \
      DATABASE_URL="${{ secrets.DATABASE_URL }}" \
      REDIS_URL="${{ secrets.REDIS_URL }}" \
      JWT_SECRET="${{ secrets.JWT_SECRET }}"
```

---

## 👥 Team Access

### Granting Team Access to Workflows

1. **Repository Settings** → **Environments**
2. Create environments:
   - `staging` (no restrictions)
   - `production` (required reviewers)

3. **Add required reviewers for production**:
   - Go to Settings → Environments → production
   - Add team members who can approve deployments

4. **Configure branch protection**:
   - Require PR reviews
   - Require status checks to pass
   - Include administrators in restrictions

### Running Workflows as Team Member

```bash
# Install GitHub CLI
brew install gh

# Authenticate
gh auth login

# List available workflows
gh workflow list

# Run a workflow
gh workflow run ci-build-shield.yml

# View recent runs
gh run list --workflow=ci-build-shield.yml

# View specific run
gh run view <run-id>

# Download logs
gh run download <run-id>
```

---

## 📊 Monitoring CI/CD Performance

### Storm Integration

The Storm observability system monitors CI/CD pipelines:

**Metrics Collected**:
- Build duration by service
- Test pass/fail rates
- Deployment frequency
- Lead time for changes
- Mean time to recovery (MTTR)

**Access Storm Dashboard**:
- Location: `/Users/alexarno/materi/lab/sparki.tools/storm/`
- Dashboards: `/Users/alexarno/materi/lab/sparki.tools/storm/dashboards/`

### BetterStack CI/CD Monitoring

Send build status to BetterStack:

```yaml
- name: Report to BetterStack
  if: always()
  run: |
    curl -X POST https://in.logs.betterstack.com/events \
      -H "Authorization: Bearer ${{ secrets.BETTERSTACK_API_TOKEN }}" \
      -H "Content-Type: application/json" \
      -d '{
        "event": "build_${{ job.status }}",
        "service": "${{ github.workflow }}",
        "commit": "${{ github.sha }}",
        "branch": "${{ github.ref_name }}"
      }'
```

---

## 🔧 Customization

### Adding a New Service

1. **Copy existing template**:
```bash
cp operations/.workflows/ci-build-shield.yml \
   operations/.workflows/ci-build-myservice.yml
```

2. **Update service paths**:
```yaml
paths:
  - "myservice/**"
  - ".github/workflows/ci-build-myservice.yml"
```

3. **Customize build steps**:
```yaml
- name: Build myservice
  run: |
    cd myservice
    make build
```

### Custom Deployment Stages

Add custom stages to `main-pipeline.yml`:

```yaml
custom-verification:
  name: 🧪 Custom Verification
  needs: deploy
  runs-on: ubuntu-latest
  steps:
    - name: Run smoke tests
      run: ./scripts/smoke-tests.sh

    - name: Verify metrics
      run: ./scripts/check-metrics.sh
```

---

## 📚 Additional Resources

- **Main CI/CD**: `operations/.workflows/main-cicd.yml` (22KB)
- **Full Pipeline**: `operations/.workflows/main-pipeline.yml` (41KB)
- **Security**: `operations/.workflows/security/`
- **Storm Docs**: `lab/sparki.tools/storm/README.md`
- **Deployment Guide**: `COMPLETE_DEPLOYMENT_GUIDE.md`

---

## ✅ Checklist for Team Members

Before using CI/CD templates:

- [ ] GitHub repository access granted
- [ ] GitHub secrets configured
- [ ] Railway account linked
- [ ] Workflows copied to `.github/workflows/`
- [ ] Branch protection rules enabled
- [ ] Required reviewers added for production
- [ ] Slack webhook configured for notifications
- [ ] BetterStack integration tested

---

**Ready to automate!** 🚀
