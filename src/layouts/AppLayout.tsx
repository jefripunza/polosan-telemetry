import React, { useState } from "react";
import { useNavigate, Outlet, useLocation, Link } from "react-router";
import axios from "axios";

import { useAppStore } from "@/store/useAppStore";
import AppGuard from "@/components/guards/AppGuard";

import { routers } from "@/routers";

interface Menu {
  name: string;
  path: string;
  icon: React.JSX.Element;
}

export default function AppLayout() {
  const navigate = useNavigate();
  const location = useLocation();
  const { language, toggleLanguage, clearAuth, token, getHostUrl } =
    useAppStore();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  function menuName(path: string) {
    if (path === "dashboard") {
      return language === "id" ? "Dashboard" : "Dashboard";
    }
    if (path === "wifi") {
      return language === "id" ? "Connect WiFi" : "Connect WiFi";
    }
    if (path === "rs485") {
      return language === "id" ? "RS485 Mapping" : "RS485 Mapping";
    }
    if (path === "lora") {
      return language === "id" ? "LoRa Mapping" : "LoRa Mapping";
    }
    if (path === "pin") {
      return language === "id" ? "Pin Mapping" : "Pin Mapping";
    }
    if (path === "log") {
      return language === "id" ? "List Logs" : "List Logs";
    }
    if (path === "setting") {
      return language === "id" ? "Pengaturan" : "Settings";
    }
    return "-";
  }

  function menuIcon(path: string) {
    const iconClass = "w-5 h-5";
    
    if (path === "dashboard") {
      return (
        <svg className={iconClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      );
    }
    if (path === "wifi") {
      return (
        <svg className={iconClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.141 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0" />
        </svg>
      );
    }
    if (path === "rs485") {
      return (
        <svg className={iconClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      );
    }
    if (path === "lora") {
      return (
        <svg className={iconClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.348 14.651a3.75 3.75 0 010-5.303m5.304 0a3.75 3.75 0 010 5.303m-7.425 2.122a7.5 7.5 0 010-10.606m9.546 0a7.5 7.5 0 010 10.606M12 12h.01" />
        </svg>
      );
    }
    if (path === "pin") {
      return (
        <svg className={iconClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
      );
    }
    if (path === "log") {
      return (
        <svg className={iconClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      );
    }
    if (path === "setting") {
      return (
        <svg className={iconClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
      );
    }
    return (
      <svg className={iconClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
      </svg>
    );
  }

  // Menu items configuration
  const menuItems = routers
    .find((route) => route.path === "/app")
    ?.children?.map((route) => ({
      name: menuName(route.path),
      path: route.path,
      icon: menuIcon(route.path),
    })) as Menu[];

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
      console.error("Logout API call failed:", error);
      // Continue with local logout even if API call fails
    } finally {
      // Always clear local auth data and redirect
      clearAuth();
      navigate("/auth/login", { replace: true });
    }
  };

  return (
    <AppGuard>
      <div className="min-h-screen bg-gray-50 flex">
        {/* Sidebar */}
        <div
          className={`fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform ${
            sidebarOpen ? "translate-x-0" : "-translate-x-full"
          } transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0`}
        >
          <div className="flex items-center justify-center h-16 px-4 bg-linear-to-r from-emerald-600 to-teal-600">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">M</span>
              </div>
              <span className="text-white font-bold text-lg">Molinar IoT</span>
            </div>
          </div>

          {/* Navigation Menu */}
          <nav className="mt-8 px-4">
            <ul className="space-y-2">
              {menuItems.map((item) => (
                <li key={item.path}>
                  <Link
                    to={item.path}
                    className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors duration-200 ${
                      location.pathname === item.path
                        ? "bg-emerald-50 text-emerald-700 border-r-2 border-emerald-600"
                        : "text-gray-700 hover:bg-gray-50 hover:text-emerald-600"
                    }`}
                    onClick={() => setSidebarOpen(false)}
                  >
                    {item.icon}
                    <span className="font-medium">{item.name}</span>
                  </Link>
                </li>
              ))}
            </ul>
          </nav>
        </div>

        {/* Mobile sidebar overlay */}
        {sidebarOpen && (
          <div
            className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        {/* Main Content */}
        <div className="flex-1 flex flex-col lg:ml-0">
          {/* Top Header */}
          <header className="bg-white shadow-sm border-b border-gray-200">
            <div className="flex items-center justify-between px-4 py-4">
              {/* Mobile menu button */}
              <button
                onClick={() => setSidebarOpen(true)}
                className="lg:hidden p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100"
              >
                <svg
                  className="w-6 h-6"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 6h16M4 12h16M4 18h16"
                  />
                </svg>
              </button>

              {/* Page Title */}
              <h1 className="text-xl font-semibold text-gray-900 lg:ml-0">
                {menuItems.find((item) => item.path === location.pathname)
                  ?.name || "Dashboard"}
              </h1>

              {/* Header Controls */}
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

          {/* Main Content Area */}
          <main className="flex-1 p-6 bg-gray-50">
            <div className="max-w-7xl mx-auto">
              <Outlet />
            </div>
          </main>

          {/* Footer */}
          <footer className="bg-white border-t border-gray-200 px-6 py-4">
            <div className="text-center">
              <p className="text-gray-600 text-sm">
                {language === "id"
                  ? "© 2024 Molinar IoT Dashboard. Semua hak dilindungi."
                  : "© 2024 Molinar IoT Dashboard. All rights reserved."}
              </p>
            </div>
          </footer>
        </div>
      </div>
    </AppGuard>
  );
}
