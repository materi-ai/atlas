# Client Integration Quick Reference

## Status Summary

```
Test Coverage:        ✅ 538/538 passing (100%)
Type Safety:          ⚠️  167 TypeScript errors (BLOCKER)
Build Output:         ❌ Blocked by TypeScript errors
Service Integration:  🟡 Partially implemented
Overall Readiness:    🟡 CONDITIONAL (pending TypeScript fix)
```

## Critical Actions Required

### 1️⃣ FIX TYPESCRIPT ERRORS (4-6 hours) - BLOCKING EVERYTHING

```bash
# Identify all errors
npm run type-check > typescript-errors.log

# Fix priority order
operationalTransform.ts  (15+ errors)   → Add null checks
optimisticUpdates.ts     (20+ errors)   → Fix type mismatches
queryClient.ts           (3 errors)     → Fix staleTime type
component files          (50+ errors)   → Resolve imports

# Verify success
npm run build
# Should complete without errors
```

### 2️⃣ INTEGRATE SERVICES (12-16 hours) - After TypeScript Fixed

| Service | Status | Work Required | Time |
|---------|--------|---------------|------|
| Shield | 🟡 Partial | OAuth + tests | 3-4h |
| API | 🟡 Partial | CRUD + tests | 3-4h |
| Relay | 🟡 Partial | WebSocket + OT | 4-5h |
| Folio | ❌ Missing | Registration + discovery | 2-3h |

### 3️⃣ VALIDATE PRODUCTION (3-4 hours) - Last Phase

```bash
npm run build           # Production build
npm run preview        # Test in browser
npm test -- --run     # All integration tests
# Health checks       # All services responding
```

## File Locations

### Documents
```
INTEGRATION_READINESS_REPORT.md     ← Full assessment (READ THIS FIRST)
INTEGRATION_IMPLEMENTATION_GUIDE.md ← Step-by-step instructions
INTEGRATION_EXECUTIVE_SUMMARY.md    ← Approval & sign-off
INTEGRATION_QUICK_REFERENCE.md      ← This file
```

### Key Source Files to Fix
```
Utilities (80+ errors):
  src/utils/operationalTransform.ts     ← CRITICAL
  src/utils/optimisticUpdates.ts        ← CRITICAL
  src/utils/metricsCollector.ts
  src/utils/retry.ts

Config (15+ errors):
  src/config/queryClient.ts             ← FIX NEEDED
  src/contexts/AuthContext.tsx

Components (50+ errors):
  src/components/DocumentEditor.tsx
  src/components/SearchPage.tsx
  src/hooks/*.ts

Services (all ready):
  src/services/api.ts                   ← Ready for integration
  src/services/websocket.ts             ← Ready for integration
  src/services/analyticsService.ts      ← Ready
```

### New Files to Create
```
src/services/folio.ts                  ← Folio client (2-3h)
src/services/serviceDiscovery.ts       ← Service discovery (1-2h)
src/__tests__/shield.integration.test.ts
src/__tests__/api.integration.test.ts
src/__tests__/relay.integration.test.ts
src/__tests__/folio.integration.test.ts
```

## Environment Variables Template

```bash
# .env.local
VITE_SHIELD_API_URL=http://localhost:8080/api
VITE_SHIELD_OAUTH_CLIENT_ID=materi-client
VITE_API_BASE_URL=http://localhost:8081/api
VITE_API_TIMEOUT=30000
VITE_RELAY_WS_URL=ws://localhost:8082/ws
VITE_RELAY_HEARTBEAT_INTERVAL=30000
VITE_FOLIO_API_URL=http://localhost:8083/api
VITE_FOLIO_SERVICE_NAME=materi-client
VITE_FOLIO_SERVICE_VERSION=1.0.0
VITE_FOLIO_ENVIRONMENT=development
```

## Test Execution

```bash
# Run all tests
npm test -- --no-coverage --run

# Run specific test file
npm test -- src/__tests__/shield.integration.test.ts --run

# Run with watch mode
npm test -- --watch

# Run with coverage
npm test -- --coverage
```

## Build Commands

```bash
# Type check
npm run type-check

# Build for production
npm run build

# Preview production build
npm run preview

# Full build check
npm run build && npm run preview
```

## Integration Checklist

- [ ] **Phase 1**: TypeScript errors resolved → npm run build succeeds
- [ ] **Phase 2a**: Shield OAuth tests passing
- [ ] **Phase 2b**: API CRUD tests passing
- [ ] **Phase 2c**: Relay WebSocket tests passing
- [ ] **Phase 2d**: Folio service registration tests passing
- [ ] **Phase 3**: Production build successful
- [ ] **Phase 3**: All services health checks passing
- [ ] **Phase 3**: Performance benchmarks acceptable
- [ ] **Security**: Vulnerability audit complete

## Go/No-Go Decision Points

### Phase 1 (TypeScript) - CRITICAL
```
GO if:        ✅ npm run build succeeds
              ✅ 0 TypeScript errors
              ✅ All 538 tests still passing

NO-GO if:     ❌ Any build errors
              ❌ Tests regression
```

### Phase 2 (Integration) - HIGH PRIORITY
```
GO if:        ✅ All 4 services tested & working
              ✅ OAuth flow end-to-end working
              ✅ Real-time sync verified

NO-GO if:     ❌ Service connectivity issues
              ❌ Type mismatches with APIs
              ❌ Performance issues
```

### Phase 3 (Validation) - DEPLOYMENT
```
GO if:        ✅ Production build successful
              ✅ All health checks green
              ✅ Performance acceptable
              ✅ Security audit passed

NO-GO if:     ❌ Build failures
              ❌ Service unavailability
              ❌ Performance degradation
```

## Common Issues & Solutions

### TypeScript Build Fails
```bash
# Clear and rebuild
rm -rf dist node_modules
npm i
npm run build
```

### Services Unreachable
```bash
# Check services running
curl http://localhost:8080/health    # Shield
curl http://localhost:8081/health    # API
curl http://localhost:8083/health    # Folio
# ws://localhost:8082/ws              # Relay (check browser console)

# Check environment variables
env | grep VITE_
```

### Tests Failing
```bash
# Run single test for debugging
npm test -- src/__tests__/shield.integration.test.ts --reporter=verbose

# Clear test cache
npm test -- --clearCache

# Run with detailed output
npm test -- --reporter=verbose --bail
```

## Timeline Summary

| Phase | Duration | Dependency | Status |
|-------|----------|-----------|--------|
| Phase 1: TypeScript | 4-6h | None | 🔴 Blocked |
| Phase 2a: Shield | 3-4h | Phase 1 | 🟡 Waiting |
| Phase 2b: API | 3-4h | Phase 1 | 🟡 Waiting |
| Phase 2c: Relay | 4-5h | Phase 1 | 🟡 Waiting |
| Phase 2d: Folio | 2-3h | Phase 1 | 🟡 Waiting |
| Phase 3: Validation | 3-4h | Phase 2 | 🟡 Waiting |
| **Total** | **22-29h** | Sequential | 🔴 Blocked |

## Key Resources

- **Full Assessment**: INTEGRATION_READINESS_REPORT.md
- **Implementation Steps**: INTEGRATION_IMPLEMENTATION_GUIDE.md
- **Approval Document**: INTEGRATION_EXECUTIVE_SUMMARY.md
- **Test Suite**: npm test -- --no-coverage --run

## Support Escalation

| Issue | Contact | Urgency |
|-------|---------|---------|
| TypeScript errors | Senior Backend | 🔴 CRITICAL |
| Build failures | DevOps | 🔴 CRITICAL |
| Service integration | Architecture | 🟠 HIGH |
| Testing issues | QA Lead | 🟡 MEDIUM |
| Deployment | DevOps Manager | 🔴 CRITICAL |

## Success Indicators

✅ When ready for production:
- All tests passing (538/538)
- Zero TypeScript errors
- Build succeeds without warnings
- All services responding
- Integration tests passing
- Performance acceptable
- Security audit clean

## Document Update Schedule

- Last Updated: December 14, 2025
- Next Review: After Phase 1 completion
- Maintenance: Weekly during integration
- Final: Post-deployment validation

---

**Quick Start**: Read INTEGRATION_READINESS_REPORT.md → Approve Phase 1 → Execute INTEGRATION_IMPLEMENTATION_GUIDE.md → Deploy
