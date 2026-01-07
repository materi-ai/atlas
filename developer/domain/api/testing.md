# API Service Testing

<Info>
**SDD Classification:** L3-Technical
**Authority:** Engineering Team
**Review Cycle:** Quarterly
</Info>

This document describes the testing strategy and practices for Materi's API Service, including unit tests, integration tests, and end-to-end testing.

---

## Testing Strategy

```mermaid
flowchart TB
    subgraph "Test Pyramid"
        E2E[E2E Tests]
        INT[Integration Tests]
        UNIT[Unit Tests]
    end

    subgraph "Coverage Targets"
        E2E_COV[~10% - Critical Paths]
        INT_COV[~20% - Service Boundaries]
        UNIT_COV[~70% - Business Logic]
    end

    E2E --> E2E_COV
    INT --> INT_COV
    UNIT --> UNIT_COV

    style UNIT fill:#90EE90
    style INT fill:#87CEEB
    style E2E fill:#FFB6C1
```

### Coverage Targets

| Layer | Target | Focus |
|-------|--------|-------|
| Unit Tests | 80%+ | Business logic, models, utilities |
| Integration Tests | 70%+ | Database, Redis, external services |
| E2E Tests | Critical paths | Full request lifecycle |

---

## Unit Testing

### Test Structure

```go
// internal/service/document_test.go
func TestDocumentService_Create(t *testing.T) {
    t.Run("creates document with valid input", func(t *testing.T) {
        // Arrange
        ctrl := gomock.NewController(t)
        defer ctrl.Finish()

        mockRepo := mocks.NewMockDocumentRepository(ctrl)
        mockPerm := mocks.NewMockPermissionService(ctrl)
        mockEvent := mocks.NewMockEventService(ctrl)

        svc := service.NewDocumentService(mockRepo, mockPerm, mockEvent)

        req := service.CreateDocumentRequest{
            Title:       "Test Document",
            Content:     "Test content",
            WorkspaceID: "ws_123",
        }

        mockPerm.EXPECT().
            CheckWorkspacePermission(gomock.Any(), "user_123", "ws_123", service.PermissionWrite).
            Return(nil)

        mockRepo.EXPECT().
            Create(gomock.Any(), gomock.Any()).
            DoAndReturn(func(ctx context.Context, doc *model.Document) error {
                assert.NotEmpty(t, doc.ID)
                assert.Equal(t, "Test Document", doc.Title)
                assert.Equal(t, 1, doc.Version)
                return nil
            })

        mockEvent.EXPECT().
            Publish(gomock.Any(), "materi:events:documents", gomock.Any()).
            Return(nil)

        // Act
        doc, err := svc.Create(context.Background(), "user_123", req)

        // Assert
        assert.NoError(t, err)
        assert.NotNil(t, doc)
        assert.Equal(t, "Test Document", doc.Title)
        assert.Equal(t, "user_123", doc.OwnerID)
    })

    t.Run("fails when permission denied", func(t *testing.T) {
        ctrl := gomock.NewController(t)
        defer ctrl.Finish()

        mockRepo := mocks.NewMockDocumentRepository(ctrl)
        mockPerm := mocks.NewMockPermissionService(ctrl)
        mockEvent := mocks.NewMockEventService(ctrl)

        svc := service.NewDocumentService(mockRepo, mockPerm, mockEvent)

        req := service.CreateDocumentRequest{
            Title:       "Test Document",
            WorkspaceID: "ws_123",
        }

        mockPerm.EXPECT().
            CheckWorkspacePermission(gomock.Any(), "user_123", "ws_123", service.PermissionWrite).
            Return(errors.ErrForbidden)

        doc, err := svc.Create(context.Background(), "user_123", req)

        assert.Nil(t, doc)
        assert.ErrorIs(t, err, errors.ErrForbidden)
    })
}
```

### Table-Driven Tests

```go
func TestDocumentService_Validate(t *testing.T) {
    tests := []struct {
        name    string
        input   service.CreateDocumentRequest
        wantErr bool
        errCode string
    }{
        {
            name: "valid document",
            input: service.CreateDocumentRequest{
                Title:       "Valid Title",
                WorkspaceID: "ws_123",
            },
            wantErr: false,
        },
        {
            name: "empty title",
            input: service.CreateDocumentRequest{
                Title:       "",
                WorkspaceID: "ws_123",
            },
            wantErr: true,
            errCode: "VALIDATION_ERROR",
        },
        {
            name: "title too long",
            input: service.CreateDocumentRequest{
                Title:       strings.Repeat("a", 256),
                WorkspaceID: "ws_123",
            },
            wantErr: true,
            errCode: "VALIDATION_ERROR",
        },
        {
            name: "missing workspace",
            input: service.CreateDocumentRequest{
                Title: "Valid Title",
            },
            wantErr: true,
            errCode: "VALIDATION_ERROR",
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            err := tt.input.Validate()
            if tt.wantErr {
                assert.Error(t, err)
                var appErr *errors.AppError
                if errors.As(err, &appErr) {
                    assert.Equal(t, tt.errCode, appErr.Code)
                }
            } else {
                assert.NoError(t, err)
            }
        })
    }
}
```

### Mock Generation

```bash
# Generate mocks with mockgen
mockgen -source=internal/repository/document.go -destination=internal/mocks/document_repo.go
mockgen -source=internal/service/permission.go -destination=internal/mocks/permission_svc.go

# Or use go generate directive
//go:generate mockgen -source=document.go -destination=../mocks/document_repo.go
```

---

## Integration Testing

### Database Integration Tests

```go
// internal/repository/document_integration_test.go
// +build integration

func TestDocumentRepository_Integration(t *testing.T) {
    if testing.Short() {
        t.Skip("skipping integration test")
    }

    // Setup test database
    db := setupTestDB(t)
    defer cleanupTestDB(t, db)

    repo := repository.NewDocumentRepository(db)

    t.Run("Create and Get", func(t *testing.T) {
        doc := &model.Document{
            ID:          uuid.New().String(),
            Title:       "Integration Test Doc",
            Content:     "Test content",
            WorkspaceID: "ws_test",
            OwnerID:     "user_test",
            Version:     1,
        }

        err := repo.Create(context.Background(), doc)
        require.NoError(t, err)

        retrieved, err := repo.GetByID(context.Background(), doc.ID)
        require.NoError(t, err)
        assert.Equal(t, doc.Title, retrieved.Title)
        assert.Equal(t, doc.Content, retrieved.Content)
    })

    t.Run("Search with full-text", func(t *testing.T) {
        // Create documents with searchable content
        docs := []model.Document{
            {ID: uuid.New().String(), Title: "Go Programming", Content: "Learn Go programming language", WorkspaceID: "ws_test", OwnerID: "user_test", Version: 1},
            {ID: uuid.New().String(), Title: "Python Tutorial", Content: "Python is versatile", WorkspaceID: "ws_test", OwnerID: "user_test", Version: 1},
            {ID: uuid.New().String(), Title: "Go Best Practices", Content: "Best practices for Go development", WorkspaceID: "ws_test", OwnerID: "user_test", Version: 1},
        }

        for _, doc := range docs {
            err := repo.Create(context.Background(), &doc)
            require.NoError(t, err)
        }

        // Search for "Go"
        results, err := repo.Search(context.Background(), "ws_test", "Go")
        require.NoError(t, err)
        assert.Len(t, results, 2)
    })
}

func setupTestDB(t *testing.T) *sqlx.DB {
    t.Helper()

    dbURL := os.Getenv("TEST_DATABASE_URL")
    if dbURL == "" {
        dbURL = "postgresql://postgres:postgres@localhost:5432/materi_test"
    }

    db, err := sqlx.Connect("postgres", dbURL)
    require.NoError(t, err)

    // Run migrations
    err = runMigrations(db)
    require.NoError(t, err)

    return db
}

func cleanupTestDB(t *testing.T, db *sqlx.DB) {
    t.Helper()
    _, _ = db.Exec("TRUNCATE documents, workspaces, users CASCADE")
    _ = db.Close()
}
```

### Redis Integration Tests

```go
// internal/infra/redis_integration_test.go
// +build integration

func TestRedisCache_Integration(t *testing.T) {
    if testing.Short() {
        t.Skip("skipping integration test")
    }

    client := setupRedis(t)
    defer client.Close()

    cache := infra.NewRedisCache(client)

    t.Run("Set and Get", func(t *testing.T) {
        ctx := context.Background()
        key := "test:key:" + uuid.New().String()
        value := map[string]interface{}{
            "id":   "doc_123",
            "name": "Test",
        }

        err := cache.Set(ctx, key, value, 5*time.Minute)
        require.NoError(t, err)

        var retrieved map[string]interface{}
        err = cache.Get(ctx, key, &retrieved)
        require.NoError(t, err)
        assert.Equal(t, "doc_123", retrieved["id"])
    })

    t.Run("Expiration", func(t *testing.T) {
        ctx := context.Background()
        key := "test:expire:" + uuid.New().String()

        err := cache.Set(ctx, key, "value", 100*time.Millisecond)
        require.NoError(t, err)

        // Wait for expiration
        time.Sleep(150 * time.Millisecond)

        var value string
        err = cache.Get(ctx, key, &value)
        assert.ErrorIs(t, err, redis.Nil)
    })
}

func setupRedis(t *testing.T) *redis.Client {
    t.Helper()

    url := os.Getenv("TEST_REDIS_URL")
    if url == "" {
        url = "redis://localhost:6379/15" // Use DB 15 for tests
    }

    opt, err := redis.ParseURL(url)
    require.NoError(t, err)

    client := redis.NewClient(opt)
    _, err = client.Ping(context.Background()).Result()
    require.NoError(t, err)

    // Clean test database
    client.FlushDB(context.Background())

    return client
}
```

---

## HTTP Controller Testing

### Handler Tests

```go
// internal/controller/document_test.go
func TestDocumentController_Create(t *testing.T) {
    ctrl := gomock.NewController(t)
    defer ctrl.Finish()

    mockSvc := mocks.NewMockDocumentService(ctrl)
    controller := controller.NewDocumentController(mockSvc, zap.NewNop())

    app := fiber.New()
    app.Post("/api/v1/documents", func(c *fiber.Ctx) error {
        c.Locals("user_id", "user_123")
        return controller.Create(c)
    })

    t.Run("successful creation", func(t *testing.T) {
        mockSvc.EXPECT().
            Create(gomock.Any(), "user_123", gomock.Any()).
            Return(&model.Document{
                ID:      "doc_new",
                Title:   "New Document",
                Version: 1,
            }, nil)

        body := `{"title": "New Document", "workspace_id": "ws_123"}`
        req := httptest.NewRequest("POST", "/api/v1/documents", strings.NewReader(body))
        req.Header.Set("Content-Type", "application/json")

        resp, err := app.Test(req)
        require.NoError(t, err)
        assert.Equal(t, 201, resp.StatusCode)

        var result map[string]interface{}
        json.NewDecoder(resp.Body).Decode(&result)
        assert.True(t, result["success"].(bool))
    })

    t.Run("validation error", func(t *testing.T) {
        body := `{"workspace_id": "ws_123"}` // Missing title
        req := httptest.NewRequest("POST", "/api/v1/documents", strings.NewReader(body))
        req.Header.Set("Content-Type", "application/json")

        resp, err := app.Test(req)
        require.NoError(t, err)
        assert.Equal(t, 422, resp.StatusCode)
    })
}
```

### Middleware Tests

```go
// internal/middleware/auth_test.go
func TestAuthMiddleware(t *testing.T) {
    ctrl := gomock.NewController(t)
    defer ctrl.Finish()

    mockRedis := mocks.NewMockRedisClient(ctrl)
    mockShield := mocks.NewMockShieldClient(ctrl)

    middleware := middleware.NewAuthMiddleware(mockRedis, mockShield, zap.NewNop())

    app := fiber.New()
    app.Use(middleware.Authenticate())
    app.Get("/test", func(c *fiber.Ctx) error {
        userID := c.Locals("user_id")
        return c.JSON(fiber.Map{"user_id": userID})
    })

    t.Run("valid token from cache", func(t *testing.T) {
        token := "valid-jwt-token"
        userCtx := &middleware.UserContext{
            UserID: "user_123",
            Email:  "user@example.com",
        }

        mockRedis.EXPECT().
            Get(gomock.Any(), gomock.Any()).
            Return(redis.NewStringResult(mustJSON(userCtx), nil))

        req := httptest.NewRequest("GET", "/test", nil)
        req.Header.Set("Authorization", "Bearer "+token)

        resp, err := app.Test(req)
        require.NoError(t, err)
        assert.Equal(t, 200, resp.StatusCode)
    })

    t.Run("missing authorization header", func(t *testing.T) {
        req := httptest.NewRequest("GET", "/test", nil)

        resp, err := app.Test(req)
        require.NoError(t, err)
        assert.Equal(t, 401, resp.StatusCode)
    })
}
```

---

## End-to-End Testing

### E2E Test Setup

```go
// test/e2e/setup.go
type E2ETestSuite struct {
    suite.Suite
    app      *fiber.App
    db       *sqlx.DB
    redis    *redis.Client
    baseURL  string
    adminToken string
    userToken  string
}

func (s *E2ETestSuite) SetupSuite() {
    // Initialize test environment
    cfg := config.LoadTest()
    s.db = setupDB(cfg.DatabaseURL)
    s.redis = setupRedis(cfg.RedisURL)

    // Build application
    app, cleanup := wire.InitializeTestApp(cfg)
    s.app = app
    s.T().Cleanup(cleanup)

    // Create test users and get tokens
    s.adminToken = s.createTestUser("admin@test.com", "admin")
    s.userToken = s.createTestUser("user@test.com", "member")
}

func (s *E2ETestSuite) TearDownSuite() {
    s.db.Close()
    s.redis.Close()
}

func (s *E2ETestSuite) SetupTest() {
    // Clean data between tests
    s.cleanDatabase()
}
```

### E2E Test Cases

```go
// test/e2e/documents_test.go
func (s *E2ETestSuite) TestDocumentLifecycle() {
    // Create workspace
    workspace := s.createWorkspace(s.userToken, "Test Workspace")

    // Create document
    createReq := map[string]interface{}{
        "title":        "E2E Test Document",
        "content":      "Initial content",
        "workspace_id": workspace.ID,
    }

    resp := s.request("POST", "/api/v1/documents", createReq, s.userToken)
    s.Equal(201, resp.StatusCode)

    var createResult struct {
        Success bool `json:"success"`
        Data    struct {
            ID      string `json:"id"`
            Title   string `json:"title"`
            Version int    `json:"version"`
        } `json:"data"`
    }
    json.NewDecoder(resp.Body).Decode(&createResult)
    s.True(createResult.Success)
    s.Equal("E2E Test Document", createResult.Data.Title)
    s.Equal(1, createResult.Data.Version)

    docID := createResult.Data.ID

    // Read document
    resp = s.request("GET", "/api/v1/documents/"+docID, nil, s.userToken)
    s.Equal(200, resp.StatusCode)

    // Update document
    updateReq := map[string]interface{}{
        "title":   "Updated Title",
        "version": 1,
    }
    resp = s.request("PATCH", "/api/v1/documents/"+docID, updateReq, s.userToken)
    s.Equal(200, resp.StatusCode)

    var updateResult struct {
        Data struct {
            Title   string `json:"title"`
            Version int    `json:"version"`
        } `json:"data"`
    }
    json.NewDecoder(resp.Body).Decode(&updateResult)
    s.Equal("Updated Title", updateResult.Data.Title)
    s.Equal(2, updateResult.Data.Version)

    // Delete document
    resp = s.request("DELETE", "/api/v1/documents/"+docID, nil, s.userToken)
    s.Equal(204, resp.StatusCode)

    // Verify deleted
    resp = s.request("GET", "/api/v1/documents/"+docID, nil, s.userToken)
    s.Equal(404, resp.StatusCode)
}

func (s *E2ETestSuite) TestConcurrentEdits() {
    workspace := s.createWorkspace(s.userToken, "Concurrent Test")
    doc := s.createDocument(s.userToken, workspace.ID, "Concurrent Doc", "Initial")

    // Simulate concurrent updates
    var wg sync.WaitGroup
    results := make(chan int, 10)

    for i := 0; i < 10; i++ {
        wg.Add(1)
        go func(version int) {
            defer wg.Done()
            updateReq := map[string]interface{}{
                "content": fmt.Sprintf("Update %d", version),
                "version": 1, // All using same version
            }
            resp := s.request("PATCH", "/api/v1/documents/"+doc.ID, updateReq, s.userToken)
            results <- resp.StatusCode
        }(i)
    }

    wg.Wait()
    close(results)

    // Only one should succeed with 200, rest should get 409
    successCount := 0
    conflictCount := 0
    for status := range results {
        if status == 200 {
            successCount++
        } else if status == 409 {
            conflictCount++
        }
    }

    s.Equal(1, successCount)
    s.Equal(9, conflictCount)
}
```

---

## Test Configuration

### Test Environment

```go
// test/config.go
type TestConfig struct {
    DatabaseURL string
    RedisURL    string
    ShieldURL   string
    LogLevel    string
}

func LoadTest() *TestConfig {
    return &TestConfig{
        DatabaseURL: envOrDefault("TEST_DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/materi_test"),
        RedisURL:    envOrDefault("TEST_REDIS_URL", "redis://localhost:6379/15"),
        ShieldURL:   envOrDefault("TEST_SHIELD_URL", "http://localhost:8000"),
        LogLevel:    envOrDefault("TEST_LOG_LEVEL", "error"),
    }
}
```

### Test Fixtures

```go
// test/fixtures/documents.go
var TestDocuments = []model.Document{
    {
        ID:          "doc_fixture_1",
        Title:       "Fixture Document 1",
        Content:     "Content for testing",
        WorkspaceID: "ws_fixture",
        OwnerID:     "user_fixture",
        Version:     1,
    },
    {
        ID:          "doc_fixture_2",
        Title:       "Fixture Document 2",
        Content:     "More test content with searchable words",
        WorkspaceID: "ws_fixture",
        OwnerID:     "user_fixture",
        Version:     3,
    },
}

func LoadFixtures(db *sqlx.DB) error {
    for _, doc := range TestDocuments {
        _, err := db.NamedExec(`
            INSERT INTO documents (id, title, content, workspace_id, owner_id, version, created_at, updated_at)
            VALUES (:id, :title, :content, :workspace_id, :owner_id, :version, NOW(), NOW())
            ON CONFLICT (id) DO NOTHING
        `, doc)
        if err != nil {
            return err
        }
    }
    return nil
}
```

---

## Running Tests

### Commands

```bash
# Run all unit tests
make test

# Run with coverage report
make test-coverage

# Run integration tests
make test-integration

# Run E2E tests
make test-e2e

# Run specific test
go test -v -run TestDocumentService_Create ./internal/service/

# Run with race detector
go test -race ./...

# Generate HTML coverage report
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out -o coverage.html
```

### CI Configuration

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version: '1.25'
      - name: Run unit tests
        run: make test-coverage
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  integration-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: materi_test
        ports:
          - 5432:5432
      redis:
        image: redis:7
        ports:
          - 6379:6379
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version: '1.25'
      - name: Run migrations
        run: make migrate-up ENV=test
      - name: Run integration tests
        run: make test-integration
```

---

## Related Documentation

- [Overview](overview) - Service overview
- [Architecture](architecture) - System design
- [Setup](setup) - Development environment
- [Deployment](deployment) - Production deployment

---

**Document Status:** Complete
**Version:** 2.0
