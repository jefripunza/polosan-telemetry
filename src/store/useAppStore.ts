import { create } from "zustand";
import { persist } from "zustand/middleware";
import axios from "axios";

export type Language = "id" | "en";

interface AppState {
  language: Language;
  token: string | null;
  isAuthenticated: boolean;
  toggleLanguage: () => void;
  setLanguage: (language: Language) => void;
  setToken: (token: string) => void;
  clearToken: () => void;
  clearAuth: () => void;
  validateToken: () => Promise<boolean>;
}

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      language: "id",
      token: null,
      isAuthenticated: false,

      toggleLanguage: () => {
        const currentLanguage = get().language;
        const newLanguage: Language = currentLanguage === "id" ? "en" : "id";
        set({ language: newLanguage });
      },

      setLanguage: (language: Language) => {
        set({ language });
      },

      setToken: (token: string) => {
        set({ token, isAuthenticated: true });
      },

      clearToken: () => {
        set({ token: null, isAuthenticated: false });
      },

      clearAuth: () => {
        set({ token: null, isAuthenticated: false });
      },

      validateToken: async () => {
        const { token } = get();
        if (!token) {
          get().clearToken();
          return false;
        }

        try {
          const response = await axios.get(
            `${window.location.origin}/api/auth/token-validate`,
            {
              params: { token },
              timeout: 5000,
            }
          );

          if (response.status === 200) {
            set({ isAuthenticated: true });
            return true;
          } else {
            get().clearToken();
            return false;
          }
        } catch (error) {
          console.error("Token validation failed:", error);
          get().clearToken();
          return false;
        }
      },
    }),
    {
      name: "app-store",
      partialize: (state) => ({
        language: state.language,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
