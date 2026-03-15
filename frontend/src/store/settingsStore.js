/**
 * store/settingsStore.js
 * Global application state using Zustand.
 * Persisted to localStorage automatically.
 */
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export const useSettingsStore = create(
  persist(
    (set, get) => ({
      // API
      apiBaseUrl: 'http://localhost:8888',

      // LLM configuration
      llmProvider: 'anthropic',   // 'anthropic' | 'deepseek' | 'openai' | 'moonshot'
      llmKey: '',                  // API key — stored in persisted store
      llmBaseUrl: '',              // override base URL (empty = use provider default)
      llmModel: 'claude-sonnet-4-6',  // model name

      // Theme
      theme: 'dark',
      accentColor: 'red',

      // Locale / defaults
      defaultGender: 'male',

      // Display
      compactMode: false,
      animationsEnabled: true,

      // Actions
      setApiBaseUrl:    (url) => set({ apiBaseUrl: url.replace(/\/$/, '') }),
      setLlmProvider:   (p)   => set({ llmProvider: p }),
      setLlmKey:        (k)   => set({ llmKey: k }),
      setLlmBaseUrl:    (u)   => set({ llmBaseUrl: u }),
      setLlmModel:      (m)   => set({ llmModel: m }),
      setTheme:         (t)   => set({ theme: t }),
      setAccentColor:   (c)   => set({ accentColor: c }),
      setDefaultGender: (g)   => set({ defaultGender: g }),
      setCompactMode:   (v)   => set({ compactMode: v }),
      setAnimationsEnabled: (v) => set({ animationsEnabled: v }),
      resetAll: () => set({
        apiBaseUrl: 'http://localhost:8888',
        llmProvider: 'anthropic', llmKey: '', llmBaseUrl: '', llmModel: 'claude-sonnet-4-6',
        theme: 'dark', accentColor: 'red',
        defaultGender: 'male', compactMode: false, animationsEnabled: true,
      }),
    }),
    { name: 'bagua-settings' }
  )
);

// ── Notification store (transient, not persisted) ─────────
export const useNotifyStore = create((set) => ({
  notifications: [],
  notify: (message, type = 'info') => {
    const id = Date.now();
    set((s) => ({ notifications: [...s.notifications, { id, message, type }] }));
    setTimeout(() => {
      set((s) => ({ notifications: s.notifications.filter((n) => n.id !== id) }));
    }, 4000);
  },
}));
