import { createRoot } from "react-dom/client";

import { createBrowserRouter, Navigate } from "react-router";
import { RouterProvider } from "react-router/dom";

// Layouts
import AuthLayout from "@/layouts/AuthLayout";
import AppLayout from "@/layouts/AppLayout";

// Pages
import LandingPage from "@/pages/LandingPage";
import LoginPage from "@/pages/auth/LoginPage";
import LogoutPage from "@/pages/auth/LogoutPage";
import DashboardPage from "@/pages/app/DashboardPage";
import SettingPage from "@/pages/app/SettingPage";

import "@/index.css";

const router = createBrowserRouter([
  {
    path: "/",
    Component: LandingPage,
  },

  // Auth
  {
    path: "/login",
    element: <Navigate to="/auth/login" replace />,
  },
  {
    path: "logout",
    Component: LogoutPage,
  },
  {
    path: "/auth",
    Component: AuthLayout,
    children: [
      {
        path: "login",
        Component: LoginPage,
      },
    ],
  },

  // App
  {
    path: "/app",
    Component: AppLayout,
    children: [
      {
        path: "dashboard",
        Component: DashboardPage,
      },
      {
        path: "setting",
        Component: SettingPage,
      },
    ],
  },
]);

const root = document.getElementById("root");
createRoot(root!).render(<RouterProvider router={router} />);
