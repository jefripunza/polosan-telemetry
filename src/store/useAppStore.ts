import { create } from "zustand";
import { persist } from "zustand/middleware";

export type Language = "id" | "en";

interface AppState {
  language: Language;
  toggleLanguage: () => void;
  setLanguage: (language: Language) => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      language: "id",

      toggleLanguage: () => {
        const currentLanguage = get().language;
        const newLanguage: Language = currentLanguage === "id" ? "en" : "id";
        set({ language: newLanguage });
      },

      setLanguage: (language: Language) => {
        set({ language });
      },
    }),
    {
      name: "app-store",
      partialize: (state) => ({
        language: state.language,
      }),
    }
  )
);
