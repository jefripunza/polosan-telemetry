import { createBrowserRouter, Navigate } from "react-router";

// Layouts
import AuthLayout from "@/layouts/AuthLayout";
import AppLayout from "@/layouts/AppLayout";

// Pages
import LandingPage from "@/pages/LandingPage";
import LoginPage from "@/pages/auth/LoginPage";
import LogoutPage from "@/pages/auth/LogoutPage";

import DashboardPage from "@/pages/app/DashboardPage";
import WiFiPage from "@/pages/app/WiFiPage";
import RS485Page from "@/pages/app/RS485Page";
import LoRaPage from "@/pages/app/LoRaPage";
import PinPage from "@/pages/app/PinPage";
import LogPage from "@/pages/app/LogPage";
import SettingPage from "@/pages/app/SettingPage";
import UpdateManager from "@/pages/app/UpdateManager";

export const routers = [
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
        path: "wifi",
        Component: WiFiPage,
      },
      {
        path: "rs485",
        Component: RS485Page,
      },
      {
        path: "lora",
        Component: LoRaPage,
      },
      {
        path: "pin",
        Component: PinPage,
      },
      {
        path: "log",
        Component: LogPage,
      },
      {
        path: "setting",
        Component: SettingPage,
      },
      {
        path: "update-manager",
        Component: UpdateManager,
      },
    ],
  },
];

const router = createBrowserRouter(routers);

export default router;
