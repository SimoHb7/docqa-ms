import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

// Helper to get current user ID for storage isolation
const getCurrentUserId = (): string | null => {
  return localStorage.getItem('current-user-id');
};

// Custom storage that includes user ID in key for complete isolation
const createUserScopedStorage = (baseKey: string) => {
  return createJSONStorage(() => ({
    getItem: (name) => {
      const userId = getCurrentUserId();
      if (!userId) return null; // No data if not logged in
      
      const userKey = `${baseKey}-${userId}`;
      const value = localStorage.getItem(userKey);
      return value;
    },
    setItem: (name, value) => {
      const userId = getCurrentUserId();
      if (!userId) return; // Don't persist if not logged in
      
      const userKey = `${baseKey}-${userId}`;
      localStorage.setItem(userKey, value);
    },
    removeItem: (name) => {
      const userId = getCurrentUserId();
      if (!userId) return;
      
      const userKey = `${baseKey}-${userId}`;
      localStorage.removeItem(userKey);
    },
  }));
};

// Upload page state
interface UploadedFile {
  file: File;
  progress: number;
  status: 'uploading' | 'success' | 'error';
  id: string;
}

interface UploadState {
  files: UploadedFile[];
  setFiles: (files: UploadedFile[]) => void;
  addFile: (file: UploadedFile) => void;
  updateFile: (id: string, updates: Partial<UploadedFile>) => void;
  removeFile: (id: string) => void;
  clearFiles: () => void;
}

// ML Analytics page state
interface MLAnalyticsState {
  patientId: string;
  setPatientId: (id: string) => void;
  showDocuments: boolean;
  setShowDocuments: (show: boolean) => void;
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  selectedDocumentId: string | null;
  setSelectedDocumentId: (id: string | null) => void;
  classificationResult: any | null;
  setClassificationResult: (result: any | null) => void;
  entitiesResult: any | null;
  setEntitiesResult: (result: any | null) => void;
  processingTime: number;
  setProcessingTime: (time: number) => void;
  clearMLState: () => void;
}

// Synthesis page state
interface SynthesisState {
  synthesisType: 'patient_timeline' | 'comparison' | 'summary';
  setSynthesisType: (type: 'patient_timeline' | 'comparison' | 'summary') => void;
  patientId: string;
  setPatientId: (id: string) => void;
  selectedDocuments: any[];
  setSelectedDocuments: (docs: any[]) => void;
  result: any | null;
  setResult: (result: any | null) => void;
  clearSynthesisState: () => void;
}

// Upload Store - Note: Files will be lost on page refresh since File objects can't be serialized
export const useUploadStore = create<UploadState>()((set) => ({
  files: [],
  setFiles: (files) => set({ files }),
  addFile: (file) => set((state) => ({ files: [...state.files, file] })),
  updateFile: (id, updates) =>
    set((state) => ({
      files: state.files.map((f) =>
        f.id === id ? { ...f, ...updates } : f
      ),
    })),
  removeFile: (id) =>
    set((state) => ({
      files: state.files.filter((f) => f.id !== id),
    })),
  clearFiles: () => set({ files: [] }),
}));

// ML Analytics Store - SECURITY: User-isolated storage
export const useMLAnalyticsStore = create<MLAnalyticsState>()(
  persist(
    (set) => ({
      patientId: '',
      setPatientId: (patientId) => set({ patientId }),
      showDocuments: false,
      setShowDocuments: (showDocuments) => set({ showDocuments }),
      searchQuery: '',
      setSearchQuery: (searchQuery) => set({ searchQuery }),
      selectedDocumentId: null,
      setSelectedDocumentId: (selectedDocumentId) => set({ selectedDocumentId }),
      classificationResult: null,
      setClassificationResult: (classificationResult) =>
        set({ classificationResult }),
      entitiesResult: null,
      setEntitiesResult: (entitiesResult) => set({ entitiesResult }),
      processingTime: 0,
      setProcessingTime: (processingTime) => set({ processingTime }),
      clearMLState: () =>
        set({
          patientId: '',
          showDocuments: false,
          searchQuery: '',
          selectedDocumentId: null,
          classificationResult: null,
          entitiesResult: null,
          processingTime: 0,
        }),
    }),
    {
      name: 'ml-analytics-storage',
      storage: createUserScopedStorage('ml-analytics'),
    }
  )
);

// Synthesis Store - SECURITY: User-isolated storage
export const useSynthesisStore = create<SynthesisState>()(
  persist(
    (set) => ({
      synthesisType: 'patient_timeline',
      setSynthesisType: (synthesisType) => set({ synthesisType }),
      patientId: '',
      setPatientId: (patientId) => set({ patientId }),
      selectedDocuments: [],
      setSelectedDocuments: (selectedDocuments) => set({ selectedDocuments }),
      result: null,
      setResult: (result) => set({ result }),
      clearSynthesisState: () =>
        set({
          synthesisType: 'patient_timeline',
          patientId: '',
          selectedDocuments: [],
          result: null,
        }),
    }),
    {
      name: 'synthesis-storage',
      storage: createUserScopedStorage('synthesis'),
    }
  )
);
