# TASKSET 4: State Management Integration

## Overview
TASKSET 4 implements comprehensive client-side state management for offline-first document editing with:
- **Mutation Queue** - Persist mutations when offline
- **Editor State** - Track document content, cursor, history
- **Optimistic Updates** - Instant UI feedback before server confirmation  
- **Conflict Resolution** - Handle client/server version conflicts
- **Sync Service** - Sync queued mutations when reconnecting

## Files Created

### Core Stores (`src/stores/`)
1. **mutationQueue.ts** (95 lines)
   - Zustand store with localStorage persistence
   - Queue mutations while offline
   - Tracks retry attempts and errors
   - Methods: `addToQueue`, `removeFromQueue`, `updateMutationStatus`, `getQueue`, `getQueuedMutationsForDoc`

2. **editor.ts** (180 lines)
   - Zustand store for editor state
   - Tracks document content, version, cursor position
   - Undo/redo history management
   - Dirty state tracking
   - Methods: `setDocument`, `updateContent`, `undo`, `redo`, `addToHistory`, `canUndo`, `canRedo`

### Utilities (`src/utils/`)
1. **conflictResolution.ts** (140 lines)
   - Detect conflicts between client and server versions
   - Three strategies: `client` (keep local), `server` (accept server), `merge` (3-way merge)
   - Auto-resolution based on timestamps
   - User prompts for manual resolution
   - Functions: `detectConflict`, `getAutoResolution`, `askUserResolution`, `applyResolution`

2. **optimisticUpdates.ts** (145 lines)
   - Generic optimistic update function
   - Pre-update React Query cache
   - Rollback capability for errors
   - Document-specific helpers: `optimisticSaveDocument`, `optimisticRenameDocument`, `optimisticCreateDocument`, `optimisticDeleteDocument`

### Services (`src/services/`)
1. **mutationSync.ts** (210 lines)
   - Syncs all queued mutations to server when online
   - Per-type sync logic (save, rename, create, delete)
   - Conflict detection and resolution during sync
   - Retry logic with exponential backoff
   - Integrates conflict resolution and optimistic updates

### Hooks (`src/hooks/`)
1. **useDocumentOptimistic.ts** (190 lines)
   - Enhanced document hooks with optimistic updates
   - `useSaveDocumentWithOptimism` - Save with optimistic feedback
   - `useRenameDocumentWithOptimism` - Rename with optimistic feedback
   - `useCreateDocumentWithOptimism` - Create with optimistic feedback
   - `useDeleteDocumentWithOptimism` - Delete with optimistic feedback
   - All hooks queue mutations when offline

2. **useOptimisticMutation.ts** (180 lines)
   - Generic `useOptimisticMutation<TData, TVariables>` hook
   - Specific document mutation hooks
   - `useMutationQueueStatus` - Track queued mutations
   - States: `loading`, `error`, `success`, `queued`

### Components (`src/components/`)
1. **MutationQueueStatus.tsx** (50 lines)
   - Shows sync status indicator
   - Displays queued mutation count
   - Shows failed mutations badge
   - Color-coded by status (green=synced, yellow=queued, blue=syncing, red=failed)

2. **DocumentEditor.tsx** (280 lines)
   - Full editor component example
   - Integrates all state management features
   - Auto-save with debouncing
   - Undo/redo UI buttons
   - Keyboard shortcuts (Ctrl+S, Ctrl+Z, Ctrl+Y)
   - Network status display
   - Cursor tracking

### Network Integration
**Updated NetworkStatusContext** (`src/contexts/NetworkStatusContext.tsx`)
- Triggers `syncAllMutations` when coming back online
- Refetches document list and content after sync
- Handles slow connection detection

### Testing (`src/__tests__/`)
1. **stateManagement.integration.test.ts** (490 lines)
   - Tests for all stores, utilities, hooks
   - Coverage:
     - Mutation queue add/remove/update
     - Editor state load/update/undo/redo
     - Optimistic updates (save, rename, create, delete)
     - Conflict detection and resolution
     - Queue status tracking

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DOCUMENT EDITOR UI                        │
│         (DocumentEditor.tsx + useOptimisticMutation)          │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         v               v               v
   ┌─────────────┐ ┌──────────────┐ ┌─────────────┐
   │ Editor      │ │ Mutation     │ │ Network     │
   │ Store       │ │ Queue Store  │ │ Status      │
   │ (Zustand)   │ │ (Zustand)    │ │ Context     │
   └─────────────┘ └──────────────┘ └─────────────┘
         │               │                 │
         └───────────────┼─────────────────┘
                         │
    ┌────────────────────┼────────────────────┐
    │                    │                    │
    v                    v                    v
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Optimistic   │  │ Mutation     │  │ Conflict     │
│ Updates      │  │ Sync Service │  │ Resolution   │
│ (React Query)│  │              │  │              │
└──────────────┘  └──────────────┘  └──────────────┘
    │                    │                    │
    └────────────────────┼────────────────────┘
                         │
                    ┌────v────┐
                    │   API    │
                    │ (Server) │
                    └──────────┘
```

## Key Flows

### Online Document Save
1. User edits content → `updateContent()` updates editor store
2. Auto-save triggers → `useSaveDocumentWithOptimism()`
3. Optimistic update → React Query cache updated immediately
4. Save request → API call to server
5. Conflict check → `detectConflict()` on response
6. UI reflects server version on success

### Offline Document Save
1. User edits content → `updateContent()` updates editor store
2. Auto-save triggers → `useSaveDocumentWithOptimism()`
3. Optimistic update → React Query cache updated immediately
4. Offline detected → Mutation queued via `addToQueue()`
5. UI shows queued status in MutationQueueStatus
6. On reconnect → `syncAllMutations()` fires
7. Sync service → Sends queued mutation
8. Conflict resolution → Handles any version conflicts
9. Cache updated → React Query refetches

### Conflict Resolution
1. Sync service detects version mismatch
2. `getAutoResolution()` → Server-wins by default
3. If not auto-resolvable → `askUserResolution()` prompts user
4. User chooses: `client` (local), `server` (server), `merge` (merge)
5. `applyResolution()` → Applies strategy
6. Cache updated → UI reflects resolved content

## Usage Examples

### Basic Save with Optimistic Update
```typescript
import { useOptimisticSaveDocument } from '@/hooks/useOptimisticMutation';

function MyEditor({ documentId }) {
  const { mutate: save, loading, error } = useOptimisticSaveDocument(documentId);
  
  const handleSave = () => {
    save('new content').catch(err => console.error(err));
  };
  
  return (
    <button onClick={handleSave} disabled={loading}>
      {loading ? 'Saving...' : 'Save'}
    </button>
  );
}
```

### Full Editor Component
```typescript
import { DocumentEditor } from '@/components/DocumentEditor';
import { useParams } from 'react-router-dom';

function EditorPage() {
  const { docId } = useParams();
  return <DocumentEditor documentId={docId!} />;
}
```

### Check Queue Status
```typescript
import { useMutationQueueStatus } from '@/hooks/useOptimisticMutation';

function SyncStatus() {
  const { queuedCount, isSyncing, hasFailedMutations } = useMutationQueueStatus();
  
  if (queuedCount === 0) return null;
  
  return (
    <div>
      {isSyncing && <span>Syncing {queuedCount}...</span>}
      {hasFailedMutations && <span>⚠️ {queuedCount} failed</span>}
    </div>
  );
}
```

### Manual Sync Trigger
```typescript
import { useQueryClient } from '@tanstack/react-query';
import { syncAllMutations } from '@/services/mutationSync';

function ManualSync() {
  const queryClient = useQueryClient();
  
  const handleSync = async () => {
    await syncAllMutations(queryClient);
    console.log('Sync complete');
  };
  
  return <button onClick={handleSync}>Force Sync</button>;
}
```

## Data Structures

### QueuedMutation
```typescript
{
  id: string;                    // Unique ID
  type: 'save' | 'delete' | 'rename' | 'create';
  documentId: string;
  payload: Record<string, any>;  // Mutation data
  timestamp: number;             // When queued
  attempts: number;              // Retry count
  lastError?: string;            // Last error message
}
```

### EditorContent
```typescript
{
  content: string;               // Raw editor text
  version: number;               // Server version
  lastModifiedAt: string;        // ISO timestamp
  isDirty: boolean;              // Has unsaved changes
}
```

### ConflictResolution
```typescript
{
  strategy: 'client' | 'server' | 'merge';
  reason?: string;               // Why this strategy
}
```

## Integration Checklist

- [x] Zustand stores created (mutation queue, editor)
- [x] Optimistic update utilities implemented
- [x] Conflict resolution logic implemented
- [x] Mutation sync service created
- [x] Enhanced document hooks created
- [x] Optimistic mutation hook created
- [x] Network context integration
- [x] Example components created
- [x] Integration tests written
- [ ] Build verification (pending npm network)
- [ ] Component integration into main app layout
- [ ] Error handling improvements
- [ ] User notifications/toasts

## Performance Notes

1. **Mutation Queue Persistence** - localStorage keeps queue through refresh
2. **Debounced Auto-Save** - 2s delay prevents excessive API calls
3. **Lazy Conflict Resolution** - Only on version mismatch
4. **Optimistic Updates** - User sees changes instantly
5. **Retry Backoff** - 1s base delay with exponential backoff
6. **Cache Invalidation** - Minimal refetches after sync

## Security Considerations

1. All mutations validated server-side
2. Conflict resolution respects user intent
3. Queue cleared on logout
4. Version numbers prevent partial updates
5. Offline queue survives only in single browser session

## Future Enhancements

1. Operational Transform (OT) for better merge
2. Collaborative conflict resolution UI
3. Mutation queue analytics
4. Conflict resolution history
5. Per-document sync scheduling
6. Background sync API integration
