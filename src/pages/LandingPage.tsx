import { Link } from "react-router";
import { useAppStore } from "@/store/useAppStore";

export default function LandingPage() {
  const { language, toggleLanguage } = useAppStore();

  const content = {
    id: {
      title: "Setup IoT Molinar",
      subtitle: "Konfigurasi perangkat IoT Anda dengan mudah dan aman",
      loginButton: "Masuk",
      stepsTitle: "Langkah-langkah Setup",
      steps: [
        {
          number: "01",
          title: "Akses Website",
          description:
            "Buka https://setup.molinar.id dan tunggu hingga halaman sepenuhnya dimuat",
        },
        {
          number: "02",
          title: "Login ke Sistem",
          description:
            'Klik tombol "Masuk" untuk mengakses panel konfigurasi perangkat',
        },
        {
          number: "03",
          title: "Pilih Metode WiFi",
          description:
            "Pilih antara WiFi Access Point atau WiFi Station (IP dapat diedit) dan masukkan password yang sesuai",
        },
      ],
      footer: "© 2024 Molinar IoT Setup. Semua hak dilindungi.",
    },
    en: {
      title: "Molinar IoT Setup",
      subtitle: "Configure your IoT devices easily and securely",
      loginButton: "Login",
      stepsTitle: "Setup Steps",
      steps: [
        {
          number: "01",
          title: "Access Website",
          description:
            "Open https://setup.molinar.id and wait until the page is fully loaded",
        },
        {
          number: "02",
          title: "Login to System",
          description:
            'Click the "Login" button to access the device configuration panel',
        },
        {
          number: "03",
          title: "Choose WiFi Method",
          description:
            "Select between WiFi Access Point or WiFi Station (editable IP) and enter the appropriate password",
        },
      ],
      footer: "© 2024 Molinar IoT Setup. All rights reserved.",
    },
  };

  const currentContent = content[language];

  return (
    <div className="min-h-screen">
      <div className="bg-linear-to-br from-emerald-50 via-white to-teal-50 min-h-screen">
        {/* Header */}
        <header className="relative z-10 px-4 py-6 sm:px-6 lg:px-8">
          <div className="max-w-7xl mx-auto flex justify-between items-center">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-linear-to-r from-emerald-600 to-teal-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">M</span>
              </div>
              <span className="text-xl font-bold text-gray-900">
                Molinar
              </span>
            </div>

            <div className="flex items-center space-x-4">
              {/* Language Toggle */}
              <button
                onClick={toggleLanguage}
                className="px-3 py-2 rounded-lg bg-white shadow-md hover:shadow-lg transition-all duration-200 text-sm font-medium text-gray-700 border border-gray-200"
              >
                {language === "id" ? "🇮🇩 ID" : "🇺🇸 EN"}
              </button>
            </div>
          </div>
        </header>

        {/* Hero Section */}
        <section className="relative px-4 py-20 sm:px-6 lg:px-8">
          <div className="max-w-4xl mx-auto text-center">
            {/* Floating Elements */}
            <div className="absolute top-10 left-10 w-20 h-20 bg-emerald-200 rounded-full opacity-20 animate-pulse"></div>
            <div className="absolute top-32 right-16 w-16 h-16 bg-teal-200 rounded-full opacity-20 animate-pulse delay-1000"></div>
            <div className="absolute bottom-20 left-20 w-12 h-12 bg-green-200 rounded-full opacity-20 animate-pulse delay-2000"></div>

            <div className="relative z-10">
              <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold text-gray-900 mb-6 leading-tight">
                <span className="bg-linear-to-r from-emerald-600 via-teal-600 to-green-600 bg-clip-text text-transparent">
                  {currentContent.title}
                </span>
              </h1>

              <p className="text-xl sm:text-2xl text-gray-600 mb-12 max-w-3xl mx-auto leading-relaxed">
                {currentContent.subtitle}
              </p>

              <Link
                to="/auth/login"
                className="group relative px-8 py-4 bg-linear-to-r from-emerald-600 to-teal-600 text-white font-semibold rounded-2xl shadow-xl hover:shadow-2xl transform hover:scale-105 transition-all duration-300 text-lg"
              >
                <span className="relative z-10">
                  {currentContent.loginButton}
                </span>
                <div className="absolute inset-0 bg-linear-to-r from-emerald-700 to-teal-700 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                <div className="absolute inset-0 bg-white rounded-2xl opacity-0 group-hover:opacity-20 transition-opacity duration-300"></div>
              </Link>
            </div>
          </div>
        </section>

        {/* Steps Section */}
        <section className="px-4 py-20 sm:px-6 lg:px-8 bg-white/50 backdrop-blur-sm">
          <div className="max-w-6xl mx-auto">
            <h2 className="text-4xl font-bold text-center text-gray-900 mb-16">
              {currentContent.stepsTitle}
            </h2>

            <div className="max-w-4xl mx-auto space-y-8">
              {currentContent.steps.map((step, index) => (
                <div key={index} className="group relative">
                  <div className="flex items-start space-x-6 bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 border border-gray-100">
                    <div className="shrink-0">
                      <div className="w-16 h-16 bg-linear-to-r from-emerald-600 to-teal-600 rounded-2xl flex items-center justify-center text-white font-bold text-xl shadow-lg">
                        {step.number}
                      </div>
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="text-2xl font-semibold text-gray-900 mb-4">
                        {step.title}
                      </h3>
                      <p className="text-lg text-gray-600 leading-relaxed">
                        {step.description}
                      </p>
                    </div>
                  </div>

                  {/* Connection Line */}
                  {index < currentContent.steps.length - 1 && (
                    <div className="flex justify-center my-4">
                      <div className="w-0.5 h-8 bg-linear-to-b from-emerald-300 to-teal-300"></div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="px-4 py-20 sm:px-6 lg:px-8">
          <div className="max-w-6xl mx-auto">
            <div className="grid md:grid-cols-3 gap-8">
              <div className="text-center group">
                <div className="w-16 h-16 bg-linear-to-r from-emerald-500 to-teal-500 rounded-2xl flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform duration-300">
                  <svg
                    className="w-8 h-8 text-white"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                    />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">
                  {language === "id"
                    ? "Aman & Terpercaya"
                    : "Secure & Reliable"}
                </h3>
                <p className="text-gray-600">
                  {language === "id"
                    ? "Konfigurasi perangkat dengan protokol keamanan terdepan"
                    : "Configure devices with cutting-edge security protocols"}
                </p>
              </div>

              <div className="text-center group">
                <div className="w-16 h-16 bg-linear-to-r from-teal-500 to-emerald-500 rounded-2xl flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform duration-300">
                  <svg
                    className="w-8 h-8 text-white"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.141 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0"
                    />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">
                  {language === "id"
                    ? "Koneksi Fleksibel"
                    : "Flexible Connection"}
                </h3>
                <p className="text-gray-600">
                  {language === "id"
                    ? "Mendukung WiFi Access Point dan Station mode"
                    : "Supports WiFi Access Point and Station modes"}
                </p>
              </div>

              <div className="text-center group">
                <div className="w-16 h-16 bg-linear-to-r from-green-500 to-emerald-600 rounded-2xl flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform duration-300">
                  <svg
                    className="w-8 h-8 text-white"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M13 10V3L4 14h7v7l9-11h-7z"
                    />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">
                  {language === "id" ? "Setup Cepat" : "Quick Setup"}
                </h3>
                <p className="text-gray-600">
                  {language === "id"
                    ? "Konfigurasi perangkat IoT dalam hitungan menit"
                    : "Configure IoT devices in minutes"}
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="px-4 py-8 sm:px-6 lg:px-8 bg-gray-50 border-t border-gray-200">
          <div className="max-w-6xl mx-auto text-center">
            <p className="text-gray-600">
              {currentContent.footer}
            </p>
          </div>
        </footer>
      </div>
    </div>
  );
}
