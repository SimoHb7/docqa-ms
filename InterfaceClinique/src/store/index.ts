import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import type { User, Notification, ChatMessage, Document } from '../types';

interface AppState {
  // Theme
  theme: 'light' | 'dark' | 'system';
  setTheme: (theme: 'light' | 'dark' | 'system') => void;

  // User
  user: User | null;
  setUser: (user: User | null) => void;

  // UI State
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;

  // Notifications
  notifications: Notification[];
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => void;
  markNotificationAsRead: (id: string) => void;
  clearNotifications: () => void;

  // Chat
  currentChatSession: string | null;
  setCurrentChatSession: (sessionId: string | null) => void;
  chatMessages: Record<string, ChatMessage[]>;
  addChatMessage: (sessionId: string, message: ChatMessage) => void;
  clearChatSession: (sessionId: string) => void;
  
  // Selected documents per session
  selectedDocuments: Record<string, Document[]>;
  setSelectedDocuments: (sessionId: string, documents: Document[]) => void;

  // Loading states
  isLoading: Record<string, boolean>;
  setLoading: (key: string, loading: boolean) => void;

  // Error states
  errors: Record<string, string>;
  setError: (key: string, error: string | null) => void;
  clearErrors: () => void;
}

export const useAppStore = create<AppState>()(
  devtools(
    persist(
      (set, get) => ({
        // Theme
        theme: 'system',
        setTheme: (theme) => set({ theme }),

        // User
        user: null,
        setUser: (user) => set({ user }),

        // UI State
        sidebarOpen: true,
        setSidebarOpen: (sidebarOpen) => set({ sidebarOpen }),

        // Notifications
        notifications: [],
        addNotification: (notification) => {
          const newNotification: Notification = {
            ...notification,
            id: crypto.randomUUID(),
            timestamp: new Date().toISOString(),
            read: false,
          };
          set((state) => ({
            notifications: [newNotification, ...state.notifications].slice(0, 50), // Keep last 50
          }));
        },
        markNotificationAsRead: (id) => {
          set((state) => ({
            notifications: state.notifications.map((n) =>
              n.id === id ? { ...n, read: true } : n
            ),
          }));
        },
        clearNotifications: () => set({ notifications: [] }),

        // Chat
        currentChatSession: null,
        setCurrentChatSession: (currentChatSession) => set({ currentChatSession }),
        chatMessages: {},
        addChatMessage: (sessionId, message) => {
          set((state) => ({
            chatMessages: {
              ...state.chatMessages,
              [sessionId]: [...(state.chatMessages[sessionId] || []), message],
            },
          }));
        },
        clearChatSession: (sessionId) => {
          set((state) => ({
            chatMessages: {
              ...state.chatMessages,
              [sessionId]: [],
            },
            selectedDocuments: {
              ...state.selectedDocuments,
              [sessionId]: [],
            },
          }));
        },

        // Selected documents per session
        selectedDocuments: {},
        setSelectedDocuments: (sessionId, documents) => {
          set((state) => ({
            selectedDocuments: {
              ...state.selectedDocuments,
              [sessionId]: documents,
            },
          }));
        },

        // Loading states
        isLoading: {},
        setLoading: (key, loading) => {
          set((state) => ({
            isLoading: {
              ...state.isLoading,
              [key]: loading,
            },
          }));
        },

        // Error states
        errors: {},
        setError: (key, error) => {
          set((state) => ({
            errors: {
              ...state.errors,
              [key]: error || '',
            },
          }));
        },
        clearErrors: () => set({ errors: {} }),
      }),
      {
        name: 'interface-clinique-storage',
        partialize: (state) => ({
          theme: state.theme,
          sidebarOpen: state.sidebarOpen,
          user: state.user,
          notifications: state.notifications,
          chatMessages: state.chatMessages,
          selectedDocuments: state.selectedDocuments,
        }),
      }
    ),
    {
      name: 'app-store',
    }
  )
);

// Selectors
export const useTheme = () => useAppStore((state) => state.theme);
export const useUser = () => useAppStore((state) => state.user);
export const useNotifications = () => useAppStore((state) => state.notifications);
export const useUnreadNotificationsCount = () =>
  useAppStore((state) => state.notifications.filter((n) => !n.read).length);
export const useCurrentChatMessages = () => {
  const sessionId = useAppStore((state) => state.currentChatSession);
  const messages = useAppStore((state) => state.chatMessages);
  return sessionId ? messages[sessionId] || [] : [];
};
export const useIsLoading = (key: string) =>
  useAppStore((state) => state.isLoading[key] || false);
export const useError = (key: string) =>
  useAppStore((state) => state.errors[key]);