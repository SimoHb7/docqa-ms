import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useMemo, lazy, Suspense } from 'react';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { useAuth0 } from '@auth0/auth0-react';
import { Toaster } from 'react-hot-toast';
import { useAppStore } from './store';
import getTheme from './theme';
import { useAuthToken } from './hooks/useAuthToken';

// Modern Layout
import ModernLayout from './components/layout/ModernLayout';

// Critical pages - load immediately
import Login from './pages/Login';
import LoadingSpinner from './components/ui/LoadingSpinner';
import ErrorBoundary from './components/ui/ErrorBoundary';

// Lazy load non-critical pages for better LCP
const ProfessionalDashboard = lazy(() => import('./pages/ProfessionalDashboard'));
const Documents = lazy(() => import('./pages/Documents'));
const Upload = lazy(() => import('./pages/Upload'));
const Search = lazy(() => import('./pages/Search'));
const QAChat = lazy(() => import('./pages/QAChat'));
const Settings = lazy(() => import('./pages/Settings'));
const AuditLogs = lazy(() => import('./pages/AuditLogs'));
const ModernSynthesis = lazy(() => import('./pages/ModernSynthesis'));

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: (failureCount, error: any) => {
        // Don't retry on 4xx errors
        if (error?.response?.status >= 400 && error?.response?.status < 500) {
          return false;
        }
        return failureCount < 3;
      },
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

// Protected Route Component
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated, isLoading } = useAuth0();

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

// App Router Component
const AppRouter = () => {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={<Login />} />

        {/* Protected routes with modern layout */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <ModernLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={
            <Suspense fallback={<LoadingSpinner />}>
              <ProfessionalDashboard />
            </Suspense>
          } />
          <Route path="documents" element={
            <Suspense fallback={<LoadingSpinner />}>
              <Documents />
            </Suspense>
          } />
          <Route path="upload" element={
            <Suspense fallback={<LoadingSpinner />}>
              <Upload />
            </Suspense>
          } />
          <Route path="search" element={
            <Suspense fallback={<LoadingSpinner />}>
              <Search />
            </Suspense>
          } />
          <Route path="qa" element={
            <Suspense fallback={<LoadingSpinner />}>
              <QAChat />
            </Suspense>
          } />
          <Route path="synthesis" element={
            <Suspense fallback={<LoadingSpinner />}>
              <ModernSynthesis />
            </Suspense>
          } />
          <Route path="audit" element={
            <Suspense fallback={<LoadingSpinner />}>
              <AuditLogs />
            </Suspense>
          } />
          <Route path="settings" element={<Settings />} />
        </Route>

        {/* Catch all */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
};

// Main App Component
function App() {
  const { theme: appTheme } = useAppStore();
  
  // Sync Auth0 tokens with API client
  useAuthToken();

  // Create MUI theme based on app theme
  const theme = useMemo(() => getTheme(appTheme), [appTheme]);

  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <AppRouter />
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: theme.palette.background.paper,
                color: theme.palette.text.primary,
                border: `1px solid ${theme.palette.divider}`,
              },
            }}
          />
        </ThemeProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;