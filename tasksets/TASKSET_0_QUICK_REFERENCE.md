/**
 * TASKSET 0: QUICK REFERENCE GUIDE
 * Routing & App Shell Architecture
 * 
 * Use this as a quick reference during development
 */

// ============================================================================
// QUICK START: HOW TO USE THE ROUTING SYSTEM
// ============================================================================

/**
 * 1. ACCESSING AUTHENTICATION IN ANY COMPONENT
 * 
 *    import { useAuth } from '@materi/client/contexts';
 * 
 *    function MyComponent() {
 *      const { user, isAuthenticated, login, logout } = useAuth();
 *      
 *      return (
 *        <div>
 *          {isAuthenticated ? (
 *            <button onClick={() => logout()}>Sign Out</button>
 *          ) : (
 *            <p>Please log in</p>
 *          )}
 *        </div>
 *      );
 *    }
 */

/**
 * 2. NAVIGATING PROGRAMMATICALLY
 * 
 *    import { useNavigation } from '@materi/client/hooks';
 * 
 *    function MyComponent() {
 *      const { toDashboard, toDocument, toSettings } = useNavigation();
 *      
 *      return (
 *        <div>
 *          <button onClick={() => toDashboard()}>Home</button>
 *          <button onClick={() => toDocument('doc-123')}>Open Doc</button>
 *          <button onClick={() => toSettings('profile')}>Profile</button>
 *        </div>
 *      );
 *    }
 */

/**
 * 3. CREATING A PROTECTED FEATURE PAGE
 * 
 *    // 1. Create the page component
 *    // src/pages/MyFeature.tsx
 *    export const MyFeaturePage: React.FC = () => {
 *      const { user } = useAuth();
 *      return <div>Welcome {user?.displayName}</div>;
 *    };
 * 
 *    // 2. Add route to App.tsx
 *    <Route path="/my-feature" element={<MyFeaturePage/>} />
 *    
 *    // 3. Add nav link to Sidebar.tsx
 *    <NavLink to="/my-feature">My Feature</NavLink>
 *    
 *    // 4. Navigate to it
 *    const { navigate } = useNavigation();
 *    navigate('/my-feature');
 */

/**
 * 4. ADDING A NEW SETTINGS TAB
 * 
 *    // 1. Create the page
 *    // src/pages/settings/CustomPage.tsx
 *    export const SettingsCustomPage: React.FC = () => {
 *      return <div>Custom Settings</div>;
 *    };
 * 
 *    // 2. Add route to App.tsx
 *    <Route path="/settings/custom" element={<SettingsCustomPage/>} />
 *    
 *    // 3. Add nav link to Sidebar.tsx in settings section
 *    <NavLink to="/settings/custom">Custom</NavLink>
 */

/**
 * 5. HANDLING AUTHENTICATION ERRORS
 * 
 *    import { useAuth } from '@materi/client/contexts';
 * 
 *    function LoginForm() {
 *      const { login, error, isLoading } = useAuth();
 *      const [email, setEmail] = useState('');
 *      const [password, setPassword] = useState('');
 *      
 *      const handleSubmit = async (e: React.FormEvent) => {
 *        e.preventDefault();
 *        try {
 *          await login(email, password);
 *          // Navigation happens automatically in most cases
 *        } catch (err) {
 *          console.error('Login failed:', err);
 *        }
 *      };
 *      
 *      return (
 *        <form onSubmit={handleSubmit}>
 *          {error && <p className="text-red-600">{error}</p>}
 *          {/* form fields */}
 *        </form>
 *      );
 *    }
 */

// ============================================================================
// ROUTE REFERENCE TABLE
// ============================================================================

/**
 * PUBLIC ROUTES (No authentication required)
 * ────────────────────────────────────────────────────────────────
 * 
 * Route                  Component              Layout      Purpose
 * ─────────────────────  ─────────────────────  ──────────  ─────────────────
 * /auth/login            LoginPage              AuthLayout  Email login form
 * /auth/signup           SignupPage             AuthLayout  New account form
 * /auth/callback         OAuthCallbackPage      AuthLayout  OAuth redirect
 * 
 * 
 * PROTECTED ROUTES (Authentication required)
 * ────────────────────────────────────────────────────────────────
 * 
 * Route                  Component              Layout      Purpose
 * ─────────────────────  ─────────────────────  ──────────  ─────────────────
 * /                      → /dashboard (redirect)
 * /dashboard             DashboardPage          AppShell    Home page
 * /documents             DocumentListPage       AppShell    Browse documents
 * /documents/:id         DocumentViewPage       AppShell    Edit document
 * /settings/profile      SettingsProfilePage    AppShell    User profile
 * /settings/workspace    SettingsWorkspacePage  AppShell    Workspace config
 * /settings/appearance   SettingsAppearancePage AppShell    Display settings
 * 
 * 
 * ERROR ROUTES
 * ────────────────────────────────────────────────────────────────
 * 
 * Route                  Component              Purpose
 * ─────────────────────  ─────────────────────  ─────────────────
 * /error                 ErrorPage              500 errors
 * * (catch-all)          NotFoundPage           404 errors
 */

// ============================================================================
// COMPONENT TREE
// ============================================================================

/**
 * <App>
 *   <BrowserRouter>
 *     <AuthProvider>
 *       <Routes>
 *         
 *         {/* Public Auth Routes */}
 *         <Route element={<AuthLayout>}>
 *           <Route path="/auth/login" element={<LoginPage/>}/>
 *           <Route path="/auth/signup" element={<SignupPage/>}/>
 *           <Route path="/auth/callback" element={<OAuthCallbackPage/>}/>
 *         </Route>
 *         
 *         {/* Protected App Routes */}
 *         <Route element={<ProtectedRoute><AppShell/></ProtectedRoute>}>
 *           <Route index element={<Navigate to="/dashboard"/>}/>
 *           <Route path="/dashboard" element={<DashboardPage/>}/>
 *           <Route path="/documents" element={<DocumentListPage/>}/>
 *           <Route path="/documents/:id" element={<DocumentViewPage/>}/>
 *           <Route path="/settings/profile" element={<SettingsProfilePage/>}/>
 *           <Route path="/settings/workspace" element={<SettingsWorkspacePage/>}/>
 *           <Route path="/settings/appearance" element={<SettingsAppearancePage/>}/>
 *         </Route>
 *         
 *         {/* Error Routes */}
 *         <Route path="/error" element={<ErrorPage/>}/>
 *         <Route path="*" element={<NotFoundPage/>}/>
 *         
 *       </Routes>
 *     </AuthProvider>
 *   </BrowserRouter>
 * </App>
 * 
 * 
 * APPSHELL STRUCTURE
 * 
 * <div className="flex h-screen w-full">
 *   <aside className="w-64">              {/* Sidebar */}
 *     <Sidebar/>
 *   </aside>
 *   <div className="flex flex-1 flex-col">
 *     <header>                             {/* Header */}
 *       <Header/>
 *     </header>
 *     <main className="flex-1 overflow-auto">  {/* Content */}
 *       <Outlet/>  {/* Page content goes here */}
 *     </main>
 *     <footer>                             {/* Footer */}
 *       <Footer/>
 *     </footer>
 *   </div>
 * </div>
 */

// ============================================================================
// HOOK REFERENCE
// ============================================================================

/**
 * useAuth()
 * ────────────────────────────────────────────────────────────────
 * Access global authentication state
 * 
 * Returns:
 *   - user: User | null - Current user object
 *   - token: AuthToken | null - Auth token
 *   - isAuthenticated: boolean - Is logged in
 *   - isLoading: boolean - Auth check in progress
 *   - error: string | null - Error message
 *   - login(email, password): Promise<void> - Log in user
 *   - logout(): Promise<void> - Log out user
 *   - refreshToken(): Promise<void> - Refresh token
 *   - updateUser(updates): void - Update user info
 *   - setError(msg): void - Set error message
 *   - clearError(): void - Clear error message
 * 
 * Usage:
 *   const { user, login, logout } = useAuth();
 */

/**
 * useNavigation()
 * ────────────────────────────────────────────────────────────────
 * Access routing utilities
 * 
 * Returns:
 *   - navigate(path): void - Navigate to path
 *   - toDashboard(): void - Go to dashboard
 *   - toDocuments(): void - Go to documents list
 *   - toDocument(id): void - Go to specific document
 *   - toSettings(section): void - Go to settings section
 *   - toLogin(): void - Go to login
 *   - toSignup(): void - Go to signup
 *   - goBack(): void - Go back one page
 * 
 * Usage:
 *   const { toDashboard, toDocument } = useNavigation();
 */

// ============================================================================
// COMMON PATTERNS
// ============================================================================

/**
 * PATTERN 1: Redirect authenticated users away from login
 * ────────────────────────────────────────────────────────────────
 * 
 * function LoginPage() {
 *   const { isAuthenticated } = useAuth();
 *   const navigate = useNavigate();
 *   
 *   useEffect(() => {
 *     if (isAuthenticated) {
 *       navigate('/dashboard');
 *     }
 *   }, [isAuthenticated, navigate]);
 *   
 *   return <LoginForm/>;
 * }
 */

/**
 * PATTERN 2: Redirect to login on logout
 * ────────────────────────────────────────────────────────────────
 * 
 * function LogoutButton() {
 *   const { logout } = useAuth();
 *   const navigate = useNavigate();
 *   
 *   const handleLogout = async () => {
 *     await logout();
 *     navigate('/auth/login');
 *   };
 *   
 *   return <button onClick={handleLogout}>Sign Out</button>;
 * }
 */

/**
 * PATTERN 3: Show user-specific content
 * ────────────────────────────────────────────────────────────────
 * 
 * function ProfilePanel() {
 *   const { user } = useAuth();
 *   
 *   if (!user) return null; // Won't happen in protected routes
 *   
 *   return (
 *     <div>
 *       <h1>{user.displayName}</h1>
 *       <p>{user.email}</p>
 *     </div>
 *   );
 * }
 */

/**
 * PATTERN 4: Navigate after action
 * ────────────────────────────────────────────────────────────────
 * 
 * function CreateDocumentButton() {
 *   const { toDocument } = useNavigation();
 *   const [isCreating, setIsCreating] = useState(false);
 *   
 *   const handleCreate = async () => {
 *     setIsCreating(true);
 *     const response = await fetch('/api/documents', {
 *       method: 'POST',
 *     });
 *     const { id } = await response.json();
 *     setIsCreating(false);
 *     toDocument(id);
 *   };
 *   
 *   return (
 *     <button onClick={handleCreate} disabled={isCreating}>
 *       Create
 *     </button>
 *   );
 * }
 */

// ============================================================================
// TROUBLESHOOTING
// ============================================================================

/**
 * ISSUE: useAuth() throws error "useAuth must be used within AuthProvider"
 * CAUSE: Component using useAuth is not wrapped by AuthProvider
 * SOLUTION: Check that the component is within the <App> component tree
 * 
 * ISSUE: Route doesn't redirect to login when not authenticated
 * CAUSE: ProtectedRoute component not wrapping the route
 * SOLUTION: Verify <ProtectedRoute> wraps the route in App.tsx
 * 
 * ISSUE: Sidebar links don't highlight active route
 * CAUSE: NavLink path doesn't match current location
 * SOLUTION: Use exact path without wildcards, e.g. to="/dashboard"
 * 
 * ISSUE: Logout doesn't clear auth state
 * CAUSE: logout() method not fully implemented (TODO: Shield API)
 * SOLUTION: Check AuthContext.tsx for mock implementation
 * 
 * ISSUE: Can't access URL params in DocumentViewPage
 * CAUSE: Not using useParams hook
 * SOLUTION: Add: const { id } = useParams<{ id: string }>();
 */

// ============================================================================
// PERFORMANCE NOTES
// ============================================================================

/**
 * CURRENT STATE (TASKSET 0):
 * - All pages loaded upfront
 * - No lazy loading yet
 * - Bundle: ~50-80KB (estimate)
 * 
 * TASKSET 1 GOALS:
 * - Lazy-load feature modules (Editor, Calc, Slides)
 * - Add Suspense boundaries with skeletons
 * - Target: <100KB initial, <50KB per feature
 * 
 * Route-Level Code Splitting Targets:
 * - /auth routes: ~10KB (minimal)
 * - /dashboard: ~15KB
 * - /documents: ~20KB
 * - /documents/:id → /Editor: ~40KB (lazy loaded)
 * - /documents/:id → /Calc: ~40KB (lazy loaded)
 * - /documents/:id → /Slides: ~40KB (lazy loaded)
 * - /settings: ~10KB
 */

// ============================================================================
// FILE LOCATIONS QUICK REFERENCE
// ============================================================================

/**
 * To modify routing:
 *   → /src/App.tsx
 * 
 * To add a page:
 *   → /src/pages/MyPage.tsx
 *   → Add route in App.tsx
 *   → Add link in Sidebar.tsx
 * 
 * To add authentication logic:
 *   → /src/contexts/AuthContext.tsx
 * 
 * To add layout:
 *   → /src/layouts/MyLayout.tsx
 * 
 * To add navigation helper:
 *   → /src/hooks/useNavigation.ts
 * 
 * To modify sidebar navigation:
 *   → /src/layouts/Sidebar.tsx
 * 
 * To modify header:
 *   → /src/layouts/Header.tsx
 */

// ============================================================================
// NEXT PHASE PREPARATION
// ============================================================================

/**
 * TASKSET 1 WILL:
 * 
 * 1. Add React.lazy() and Suspense to App.tsx
 * 2. Replace DocumentViewPage with dynamic routing
 * 3. Add loading skeletons
 * 4. Implement code splitting per feature
 * 5. Measure and validate bundle sizes
 * 
 * WHAT TO PREPARE:
 * 
 * - Ensure Editor, Calc, Slides modules export default components
 * - Create loading skeleton components
 * - Identify which pages should be lazy-loaded
 * - Plan fallback UI for slow networks
 */
