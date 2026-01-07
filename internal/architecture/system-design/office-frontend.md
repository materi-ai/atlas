# Office Frontend Architecture

## Purpose

The Office frontend (`products/canvas/apps/office`) is Materi's primary document editing application. It provides a rich collaborative editing experience for documents, spreadsheets, and presentations with real-time synchronization.

## Who it's for

- **Frontend Engineers** implementing new features
- **Platform Engineers** integrating with backend services
- **QA Engineers** testing the application

## How it fits

```
┌─────────────────────────────────────────────────────────────────┐
│                        Materi Platform                          │
├─────────────────────────────────────────────────────────────────┤
│  Products                                                       │
│  ├── Canvas (Monorepo)                                         │
│  │   ├── apps/office ◄─── This Document                        │
│  │   ├── apps/admin                                            │
│  │   └── packages/*                                            │
├─────────────────────────────────────────────────────────────────┤
│  Services                                                       │
│  ├── API (Go) ─────────── REST endpoints                       │
│  ├── Shield (Django) ──── Authentication                       │
│  └── Relay (Rust) ─────── Real-time collaboration              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Core Architecture

### Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Framework | React 18 | Component architecture |
| Language | TypeScript 5.x | Type safety |
| Build | Vite | Fast development/builds |
| Styling | Tailwind CSS | Utility-first styling |
| Animation | Framer Motion | Premium motion effects |
| State | Zustand + React Query | Global + server state |
| Testing | Vitest + Playwright | Unit + E2E testing |

### State Management Strategy

```
┌────────────────────────────────────────────────────────────┐
│                    State Management                         │
├───────────────────┬───────────────────┬───────────────────┤
│   Zustand Store   │   React Query     │   React Context   │
│   (Global UI)     │   (Server State)  │   (Scoped State)  │
├───────────────────┼───────────────────┼───────────────────┤
│ • User prefs      │ • API responses   │ • Chat sessions   │
│ • Project state   │ • Document data   │ • Editor state    │
│ • UI toggles      │ • Cached queries  │ • Form state      │
│ • Expanded nodes  │ • Mutations       │ • Modal state     │
└───────────────────┴───────────────────┴───────────────────┘
```

---

## Module Architecture

### Directory Structure

```
src/
├── lib/                    # Shared utilities
│   ├── motion/            # Animation system
│   │   ├── components/    # AnimatedButton, FadeIn, etc.
│   │   ├── tokens.ts      # Duration, easing, spring configs
│   │   └── hooks.ts       # useReducedMotion, useInView
│   └── utils/             # Helper functions
│
├── modules/               # Feature modules
│   ├── projects/          # Project management
│   │   ├── components/    # ProjectSidebar, ProjectCard, etc.
│   │   ├── hooks/         # useProjects, useCreateProject
│   │   ├── store.ts       # Zustand store
│   │   ├── api.ts         # API client
│   │   └── types.ts       # TypeScript types
│   │
│   ├── chat/              # AI chat integration
│   ├── calc/              # Spreadsheet module
│   └── slides/            # Presentation module
│
├── components/            # Shared components
│   ├── comments/          # Comment system
│   └── version-history/   # Version management
│
├── hooks/                 # Shared hooks
├── services/              # API services
└── __tests__/             # Test files
```

### Module Contract

Each feature module follows this structure:

```typescript
// modules/{feature}/index.ts
export * from './components';    // UI components
export * from './hooks';         // React hooks
export { useFeatureStore } from './store';  // Zustand store
export * from './types';         // TypeScript types
export * as featureApi from './api';  // API functions
```

---

## Motion System

### Animation Tokens

Located in `lib/motion/tokens.ts`:

```typescript
// Duration scale
export const duration = {
  instant: 0,      // No animation
  fast: 0.1,       // Micro-interactions
  normal: 0.2,     // Standard transitions
  slow: 0.3,       // Deliberate movements
  slower: 0.5,     // Page transitions
};

// Spring physics
export const spring = {
  snappy: { type: 'spring', stiffness: 400, damping: 30 },
  bouncy: { type: 'spring', stiffness: 300, damping: 20 },
  gentle: { type: 'spring', stiffness: 150, damping: 25 },
};
```

### Accessibility

All motion components respect `prefers-reduced-motion`:

```typescript
const prefersReducedMotion = useReducedMotion();
const shouldAnimate = !disableAnimation && !prefersReducedMotion;
```

### Available Components

| Component | Purpose | Props |
|-----------|---------|-------|
| `FadeIn` | Opacity entrance | direction, delay, duration |
| `SlideIn` | Directional slide | direction, distance, fade |
| `ScaleIn` | Scale entrance | origin, initialScale |
| `AnimatedList` | Staggered lists | staggerDelay, initialDelay |
| `AnimatedModal` | Dialog animations | animationStyle, closeOnEscape |
| `Collapse` | Accordion sections | isOpen, duration |

---

## Project Management

### Store Structure

```typescript
interface ProjectState {
  // Data
  projects: Project[];
  projectTree: Project[];
  currentProject: Project | null;

  // UI State
  ui: {
    selectedProjectId: string | null;
    expandedProjectIds: Set<string>;
    isCreating: boolean;
    isEditing: boolean;
    searchQuery: string;
  };

  // Expanded nodes for tree navigation
  expandedNodes: Set<string>;
}
```

### Hook Usage

```typescript
// List projects
const { data, isLoading } = useProjects(workspaceId);

// Create project
const createProject = useCreateProject(workspaceId);
await createProject.mutateAsync({ name: 'New Project' });

// Toggle pin (optimistic update)
const togglePin = useToggleProjectPin();
togglePin.mutate({ projectId, isPinned: true });
```

### API Endpoints

| Hook | Method | Endpoint |
|------|--------|----------|
| `useProjects` | GET | `/workspaces/{id}/projects` |
| `useProjectTree` | GET | `/workspaces/{id}/projects/tree` |
| `useCreateProject` | POST | `/workspaces/{id}/projects` |
| `useUpdateProject` | PUT | `/projects/{id}` |
| `useDeleteProject` | DELETE | `/projects/{id}` |

---

## Testing Strategy

### Test Pyramid

```
        ╱╲
       ╱E2E╲         Playwright (e2e/*.spec.ts)
      ╱──────╲       - Critical user flows
     ╱ Integ  ╲      Vitest (*.integration.test.ts)
    ╱──────────╲     - API integration
   ╱   Unit     ╲    Vitest (*.test.ts)
  ╱──────────────╲   - Components, hooks, stores
```

### Coverage Targets

| Category | Target | Current |
|----------|--------|---------|
| Hooks | 92% | ~92% |
| Stores | 80% | ~78% |
| Components | 75% | ~72% |
| Services | 60% | ~58% |

### Running Tests

```bash
# Unit tests
pnpm test              # Watch mode
pnpm test:ci           # CI mode
pnpm test:coverage     # With coverage

# E2E tests
pnpm test:e2e          # Headless
pnpm test:e2e:ui       # Interactive UI
pnpm test:e2e:headed   # See browser
```

---

## Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| LCP | < 2.5s | Lighthouse |
| FID | < 100ms | Web Vitals |
| CLS | < 0.1 | Lighthouse |
| Bundle Size | < 500KB | Vite build |
| TTI | < 3.5s | Lighthouse |

### Optimization Techniques

1. **Code Splitting**: Route-based lazy loading
2. **Tree Shaking**: ES modules for dead code elimination
3. **Image Optimization**: WebP format, lazy loading
4. **Caching**: React Query with stale-while-revalidate
5. **Memoization**: useMemo/useCallback for expensive operations

---

## Related References

- [Motion System Components](../../../products/canvas/apps/office/src/lib/motion/README.md)
- [Project Module Types](../../../products/canvas/apps/office/src/modules/projects/types.ts)
- [Vitest Configuration](../../../products/canvas/apps/office/vitest.config.ts)
- [Playwright Configuration](../../../products/canvas/apps/office/playwright.config.ts)
- [API Service (Go)](../../api/README.md)
- [Shield Service (Django)](../../shield/README.md)
- [Relay Service (Rust)](../../relay/README.md)
