import { useEffect } from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import { useUploadStore } from '../store/pageStores';
import { useMLAnalyticsStore } from '../store/pageStores';
import { useSynthesisStore } from '../store/pageStores';

/**
 * Hook that clears all persisted state when user logs out
 * This prevents data leakage between different user sessions
 */
export const useLogoutHandler = () => {
  const { user, isAuthenticated } = useAuth0();
  const clearMLState = useMLAnalyticsStore((state) => state.clearMLState);
  const clearSynthesisState = useSynthesisStore((state) => state.clearSynthesisState);
  const clearFiles = useUploadStore((state) => state.clearFiles);

  useEffect(() => {
    // When authentication state changes (user logs out)
    if (!isAuthenticated) {
      console.log('🔒 SECURITY: User logged out - Clearing session data');
      
      // Clear all Zustand stores
      clearMLState();
      clearSynthesisState();
      clearFiles();
      
      // Clean up all user-specific storage keys
      const userId = localStorage.getItem('current-user-id');
      if (userId) {
        localStorage.removeItem(`ml-analytics-${userId}`);
        localStorage.removeItem(`synthesis-${userId}`);
        console.log(`✅ Cleared storage for user: ${userId}`);
      }
      
      // Remove user ID marker
      localStorage.removeItem('current-user-id');
      
      console.log('✅ All session data cleared');
    }
  }, [isAuthenticated, clearMLState, clearSynthesisState, clearFiles]);

  // CRITICAL: Track and isolate user sessions
  useEffect(() => {
    const storedUserId = localStorage.getItem('current-user-id');
    const currentUserId = user?.sub;

    if (isAuthenticated && currentUserId) {
      // User switch detected - different user logged in
      if (storedUserId && storedUserId !== currentUserId) {
        console.log('🔒 SECURITY: User switch detected!');
        console.log('  Previous user:', storedUserId);
        console.log('  Current user:', currentUserId);
        
        // Clear in-memory stores (they still have old user data)
        clearMLState();
        clearSynthesisState();
        clearFiles();
        
        console.log('✅ Previous user data cleared from memory');
        console.log('✅ New user will load from their own storage');
      }

      // Store/update current user ID for isolation
      localStorage.setItem('current-user-id', currentUserId);
    } else if (!isAuthenticated) {
      // User logged out
      localStorage.removeItem('current-user-id');
    }
  }, [user?.sub, isAuthenticated, clearMLState, clearSynthesisState, clearFiles]);
};
