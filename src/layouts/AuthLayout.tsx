import { Outlet } from "react-router";
import { useAppStore } from "@/store/useAppStore";
import AuthGuard from "@/components/guards/AuthGuard";

export default function AuthLayout() {
  const { language, toggleLanguage } = useAppStore();

  return (
    <AuthGuard>
      <div className="min-h-screen bg-linear-to-br from-emerald-50 via-white to-teal-50">
        {/* Header with Language Toggle */}
        <header className="relative z-10 px-4 py-6 sm:px-6 lg:px-8">
          <div className="max-w-7xl mx-auto flex justify-between items-center">
            {/* Logo */}
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-linear-to-r from-emerald-600 to-teal-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">M</span>
              </div>
              <span className="text-xl font-bold text-gray-900">Molinar</span>
            </div>

            {/* Language Toggle */}
            <div className="flex items-center space-x-4">
              <button
                onClick={toggleLanguage}
                className="px-3 py-2 rounded-lg bg-white shadow-md hover:shadow-lg transition-all duration-200 text-sm font-medium text-gray-700 border border-gray-200"
              >
                {language === "id" ? "🇮🇩 ID" : "🇺🇸 EN"}
              </button>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-1">
          <Outlet />
        </main>

        {/* Footer */}
        <footer className="px-4 py-8 sm:px-6 lg:px-8">
          <div className="max-w-6xl mx-auto text-center">
            <p className="text-gray-600 text-sm">
              {language === "id"
                ? "© 2024 Molinar IoT Setup. Semua hak dilindungi."
                : "© 2024 Molinar IoT Setup. All rights reserved."}
            </p>
          </div>
        </footer>
      </div>
    </AuthGuard>
  );
}
