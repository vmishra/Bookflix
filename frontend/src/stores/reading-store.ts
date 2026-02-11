import { create } from 'zustand';

interface ReadingState {
  currentSessionId: number | null;
  startSession: (sessionId: number) => void;
  endSession: () => void;
}

export const useReadingStore = create<ReadingState>((set) => ({
  currentSessionId: null,
  startSession: (sessionId) => set({ currentSessionId: sessionId }),
  endSession: () => set({ currentSessionId: null }),
}));
