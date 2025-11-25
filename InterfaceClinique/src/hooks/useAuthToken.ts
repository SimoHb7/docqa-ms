import { useAuth0 } from '@auth0/auth0-react';
import { useEffect } from 'react';

/**
 * Secure token manager using memory storage (no localStorage)
 * Tokens are stored in memory only and never exposed to JavaScript
 */
class SecureTokenStore {
  private token: string | null = null;
  
  setToken(token: string) {
    this.token = token;
  }
  
  getToken(): string | null {
    return this.token;
  }
  
  clearToken() {
    this.token = null;
  }
}

export const tokenStore = new SecureTokenStore();

/**
 * Hook to manage Auth0 tokens securely in memory
 * Call this in App.tsx or Layout component
 */
export function useAuthToken() {
  const { isAuthenticated, getAccessTokenSilently } = useAuth0();

  useEffect(() => {
    const syncToken = async () => {
      if (isAuthenticated) {
        try {
          const token = await getAccessTokenSilently({
            authorizationParams: {
              audience: import.meta.env.VITE_AUTH0_AUDIENCE,
              scope: 'openid profile email',
            },
            cacheMode: 'on', // Use Auth0 internal cache
          });
          
          // Store token in memory only (NOT localStorage)
          tokenStore.setToken(token);
          console.log('✅ Auth0 token synced to secure memory');
        } catch (error) {
          console.error('❌ Failed to get Auth0 token:', error);
          tokenStore.clearToken();
        }
      } else {
        // Clear token if not authenticated
        tokenStore.clearToken();
      }
    };

    syncToken();

    // Listen for manual refresh requests from API interceptor
    const handleRefresh = () => {
      console.log('🔄 Manual token refresh requested');
      syncToken();
    };
    window.addEventListener('auth0-token-refresh', handleRefresh);

    // Refresh token every 10 minutes
    const interval = setInterval(syncToken, 10 * 60 * 1000);
    return () => {
      clearInterval(interval);
      window.removeEventListener('auth0-token-refresh', handleRefresh);
    };
  }, [isAuthenticated, getAccessTokenSilently]);
}
