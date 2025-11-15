import { create } from 'zustand'
import { QueryResponse } from '../services/api'

interface AppState {
  sessionId: string | null
  userType: string | null
  queryHistory: Array<{ query: string; response: QueryResponse; timestamp: Date }>
  currentQuery: QueryResponse | null
  isQuerying: boolean
  setSessionId: (sessionId: string) => void
  setUserType: (userType: string) => void
  addQuery: (query: string, response: QueryResponse) => void
  setCurrentQuery: (query: QueryResponse | null) => void
  setIsQuerying: (isQuerying: boolean) => void
  clearHistory: () => void
}

export const useStore = create<AppState>((set) => ({
  sessionId: null,
  userType: null,
  queryHistory: [],
  currentQuery: null,
  isQuerying: false,
  setSessionId: (sessionId: string) => set({ sessionId }),
  setUserType: (userType: string) => set({ userType }),
  addQuery: (query: string, response: QueryResponse) =>
    set((state) => ({
      queryHistory: [...state.queryHistory, { query, response, timestamp: new Date() }],
      currentQuery: response,
    })),
  setCurrentQuery: (query: QueryResponse | null) => set({ currentQuery: query }),
  setIsQuerying: (isQuerying: boolean) => set({ isQuerying }),
  clearHistory: () => set({ queryHistory: [], currentQuery: null }),
}))

