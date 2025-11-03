import { useState } from "react";
import { useAppStore } from "@/store/useAppStore";
import { useNavigate } from "react-router";
import axios from "axios";
import { z } from "zod";

const loginSchema = z.object({
  password: z.string().min(1, "Password tidak boleh kosong"),
});

export default function LoginPage() {
  const { language, setToken } = useAppStore();
  const navigate = useNavigate();
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const content = {
    id: {
      title: "Login ke Sistem IoT",
      subtitle: "Masukkan password untuk mengakses sistem",
      passwordLabel: "Password",
      passwordPlaceholder: "Masukkan password",
      loginButton: "Masuk",
      loadingText: "Menghubungkan...",
      backToHome: "Kembali ke Beranda",
    },
    en: {
      title: "IoT System Login",
      subtitle: "Enter password to access the system",
      passwordLabel: "Password",
      passwordPlaceholder: "Enter password",
      loginButton: "Login",
      loadingText: "Connecting...",
      backToHome: "Back to Home",
    },
  };

  const currentContent = content[language];

  const validateForm = () => {
    try {
      const result = loginSchema.safeParse({ password });

      if (!result.success) {
        const firstError = result.error.issues[0];
        if (language === "id") {
          setError(firstError.message);
        } else {
          setError("Password cannot be empty");
        }
        return false;
      }

      return true;
    } catch (error) {
      setError(
        language === "id"
          ? "Terjadi kesalahan validasi"
          : "Validation error occurred"
      );
      return false;
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    if (!validateForm()) return;

    setIsLoading(true);

    try {
      // Use current hostname/origin for API calls
      const hostUrl = window.location.origin;
      const response = await axios.post(
        `${hostUrl}/api/auth/login`,
        {
          password: password,
        },
        {
          timeout: 10000, // 10 second timeout
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      if (response.status === 200 && response.data.token) {
        // Save token to Zustand store
        setToken(response.data.token);
        setSuccess(language === "id" ? "Login berhasil!" : "Login successful!");

        // Navigate to dashboard after short delay
        setTimeout(() => {
          navigate("/app/dashboard", { replace: true });
        }, 1000);

        console.log("Login successful:", response.data);
      }
    } catch (err: any) {
      console.error("Login error:", err);

      if (err.code === "ECONNABORTED") {
        setError(
          language === "id"
            ? "Koneksi timeout. Periksa koneksi jaringan."
            : "Connection timeout. Check network connection."
        );
      } else if (err.response?.status === 401) {
        setError(language === "id" ? "Password salah" : "Incorrect password");
      } else if (err.response?.status === 404) {
        setError(
          language === "id"
            ? "Endpoint tidak ditemukan."
            : "Endpoint not found."
        );
      } else if (err.code === "ERR_NETWORK") {
        setError(
          language === "id"
            ? "Tidak dapat terhubung ke perangkat. Periksa koneksi jaringan."
            : "Cannot connect to device. Check network connection."
        );
      } else {
        setError(
          language === "id"
            ? "Terjadi kesalahan saat login"
            : "An error occurred during login"
        );
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-[calc(100vh-200px)] p-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            {currentContent.title}
          </h1>
          <p className="text-gray-600">{currentContent.subtitle}</p>
        </div>

        {/* Login Form */}
        <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Password Field */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                {currentContent.passwordLabel}
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder={currentContent.passwordPlaceholder}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-colors"
                required
                autoFocus
              />
            </div>

            {/* Error Message */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-xl p-4 animate-in slide-in-from-top-2 duration-300">
                <div className="flex items-center space-x-2">
                  <svg
                    className="w-5 h-5 text-red-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                  <p className="text-sm text-red-700">{error}</p>
                </div>
              </div>
            )}

            {/* Success Message */}
            {success && (
              <div className="bg-green-50 border border-green-200 rounded-xl p-4 animate-in slide-in-from-top-2 duration-300">
                <div className="flex items-center space-x-2">
                  <svg
                    className="w-5 h-5 text-green-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                  <p className="text-sm text-green-700">{success}</p>
                </div>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-linear-to-r from-emerald-600 to-teal-600 text-white font-semibold py-3 px-6 rounded-xl hover:from-emerald-700 hover:to-teal-700 focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-[1.02] active:scale-[0.98]"
            >
              {isLoading ? (
                <div className="flex items-center justify-center space-x-2">
                  <svg
                    className="animate-spin w-5 h-5"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    ></circle>
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    ></path>
                  </svg>
                  <span>{currentContent.loadingText}</span>
                </div>
              ) : (
                currentContent.loginButton
              )}
            </button>
          </form>

          {/* Back to Home Link */}
          <div className="mt-6 text-center">
            <a
              href="/"
              className="text-emerald-600 hover:text-emerald-700 font-medium text-sm transition-colors"
            >
              ← {currentContent.backToHome}
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
