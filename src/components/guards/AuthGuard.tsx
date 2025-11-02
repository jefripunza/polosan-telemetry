import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import { useAppStore } from "@/store/useAppStore";

interface AuthGuardProps {
  children: React.ReactNode;
}

export default function AuthGuard({ children }: AuthGuardProps) {
  const { token, validateToken, clearToken } = useAppStore();
  const navigate = useNavigate();
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      if (!token) {
        // No token, allow access to auth pages
        setIsChecking(false);
        return;
      }

      // Token exists, validate it
      try {
        const isValid = await validateToken();

        if (isValid) {
          // Token is valid, redirect to dashboard
          navigate("/app/dashboard", { replace: true });
        } else {
          // Token is invalid, clear it and allow access to auth pages
          clearToken();
          setIsChecking(false);
        }
      } catch (error) {
        console.error("Auth check failed:", error);
        clearToken();
        setIsChecking(false);
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
          <p className="text-gray-600">Memeriksa autentikasi...</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
