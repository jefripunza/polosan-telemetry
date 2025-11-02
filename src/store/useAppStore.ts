import { create } from "zustand";
import { persist } from "zustand/middleware";
import axios from "axios";

export type Language = "id" | "en";

interface AppState {
  language: Language;
  token: string | null;
  ipAddress: string | null;
  wifiMode: 'access-point' | 'station' | null;
  isAuthenticated: boolean;
  toggleLanguage: () => void;
  setLanguage: (language: Language) => void;
  setToken: (token: string) => void;
  setIpAddress: (ipAddress: string, wifiMode: 'access-point' | 'station') => void;
  clearToken: () => void;
  clearAuth: () => void;
  getHostUrl: () => string;
  validateToken: (host?: string) => Promise<boolean>;
}

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      language: "id",
      token: null,
      ipAddress: null,
      wifiMode: null,
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

      setIpAddress: (ipAddress: string, wifiMode: 'access-point' | 'station') => {
        const finalIpAddress = wifiMode === 'access-point' ? '192.168.4.1' : ipAddress;
        set({ ipAddress: finalIpAddress, wifiMode });
      },

      clearToken: () => {
        set({ token: null, isAuthenticated: false });
      },

      clearAuth: () => {
        set({ token: null, ipAddress: null, wifiMode: null, isAuthenticated: false });
      },

      getHostUrl: () => {
        const { ipAddress, wifiMode } = get();
        if (wifiMode === 'access-point') {
          return 'http://192.168.4.1';
        } else if (wifiMode === 'station' && ipAddress) {
          return `http://${ipAddress}`;
        }
        // Fallback to current hostname
        return `http://${window.location.hostname}`;
      },

      validateToken: async (host?: string) => {
        const { token } = get();
        if (!token) {
          get().clearToken();
          return false;
        }

        const hostUrl = host || get().getHostUrl();

        try {
          const response = await axios.get(`${hostUrl}/api/auth/token-validate`, {
            params: { token },
            timeout: 5000,
          });

          if (response.status === 200) {
            set({ isAuthenticated: true });
            return true;
          } else {
            get().clearToken();
            return false;
          }
        } catch (error) {
          console.error('Token validation failed:', error);
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
        ipAddress: state.ipAddress,
        wifiMode: state.wifiMode,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
