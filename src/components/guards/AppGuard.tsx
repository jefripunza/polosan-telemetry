import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import { useAppStore } from "@/store/useAppStore";

interface AppGuardProps {
  children: React.ReactNode;
}

export default function AppGuard({ children }: AppGuardProps) {
  const { token, validateToken, clearToken } = useAppStore();
  const navigate = useNavigate();
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      if (!token) {
        // No token, redirect to login
        navigate("/auth/login", { replace: true });
        return;
      }

      // Token exists, validate it
      try {
        const isValid = await validateToken();

        if (isValid) {
          // Token is valid, allow access to app pages
          setIsChecking(false);
        } else {
          // Token is invalid, clear it and redirect to login
          clearToken();
          navigate("/auth/login", { replace: true });
        }
      } catch (error) {
        console.error("Auth check failed:", error);
        clearToken();
        navigate("/auth/login", { replace: true });
      }
    };

    checkAuth();
  }, [token, validateToken, clearToken, navigate]);

  if (isChecking) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-linear-to-br from-emerald-50 via-white to-teal-50">
        <div className="text-center">
          <div className="w-12 h-12 bg-linear-to-r from-emerald-600 to-teal-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <div className="w-6 h-6 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
          </div>
          <p className="text-gray-600">Memverifikasi akses...</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
