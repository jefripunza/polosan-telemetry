import { useNavigate, Outlet } from "react-router";
import { useAppStore } from "@/store/useAppStore";
import AppGuard from "@/components/guards/AppGuard";
import axios from "axios";

export default function AppLayout() {
  const navigate = useNavigate();
  const { language, toggleLanguage, clearAuth, token, getHostUrl } = useAppStore();

  const handleLogout = async () => {
    try {
      // Call logout API endpoint
      if (token) {
        const hostUrl = getHostUrl();
        await axios.delete(`${hostUrl}/api/auth/logout`, {
          params: { token },
          timeout: 5000,
        });
      }
    } catch (error) {
      console.error('Logout API call failed:', error);
      // Continue with local logout even if API call fails
    } finally {
      // Always clear local auth data and redirect
      clearAuth();
      navigate("/auth/login", { replace: true });
    }
  };

  return (
    <AppGuard>
      <div className="min-h-screen bg-linear-to-br from-emerald-50 via-white to-teal-50">
        {/* Header with Navigation */}
        <header className="relative z-10 px-4 py-6 sm:px-6 lg:px-8 bg-white/50 backdrop-blur-sm border-b border-gray-200">
          <div className="max-w-7xl mx-auto flex justify-between items-center">
            {/* Logo */}
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-linear-to-r from-emerald-600 to-teal-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">M</span>
              </div>
              <span className="text-xl font-bold text-gray-900">
                Molinar Dashboard
              </span>
            </div>

            {/* Navigation & Controls */}
            <div className="flex items-center space-x-4">
              {/* Language Toggle */}
              <button
                onClick={toggleLanguage}
                className="px-3 py-2 rounded-lg bg-white shadow-md hover:shadow-lg transition-all duration-200 text-sm font-medium text-gray-700 border border-gray-200"
              >
                {language === "id" ? "🇮🇩 ID" : "🇺🇸 EN"}
              </button>

              {/* Logout Button */}
              <button
                onClick={handleLogout}
                className="px-4 py-2 rounded-lg bg-red-600 hover:bg-red-700 text-white font-medium transition-colors duration-200 text-sm"
              >
                {language === "id" ? "Keluar" : "Logout"}
              </button>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8">
          <div className="max-w-7xl mx-auto">
            <Outlet />
          </div>
        </main>

        {/* Footer */}
        <footer className="px-4 py-8 sm:px-6 lg:px-8 bg-white/50 backdrop-blur-sm border-t border-gray-200">
          <div className="max-w-6xl mx-auto text-center">
            <p className="text-gray-600 text-sm">
              {language === "id"
                ? "© 2024 Molinar IoT Dashboard. Semua hak dilindungi."
                : "© 2024 Molinar IoT Dashboard. All rights reserved."}
            </p>
          </div>
        </footer>
      </div>
    </AppGuard>
  );
}
