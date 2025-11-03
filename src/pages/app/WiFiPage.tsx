import { useState, useEffect } from "react";
import { useAppStore } from "@/store/useAppStore";
import axios from "axios";

interface WiFiNetwork {
  ssid: string;
  signal: number;
  security: "open" | "wep" | "wpa" | "wpa2";
  connected?: boolean;
  bssid?: string;
  channel?: number;
  authmode?: number;
  hidden?: boolean;
}

interface SavedNetwork {
  ssid: string;
  lastConnected: string;
  autoConnect: boolean;
  connected: boolean;
}

export default function WiFiPage() {
  const { language } = useAppStore();
  const [availableNetworks, setAvailableNetworks] = useState<WiFiNetwork[]>([]);
  const [savedNetworks, setSavedNetworks] = useState<SavedNetwork[]>([]);
  const [isScanning, setIsScanning] = useState(false);
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [selectedNetwork, setSelectedNetwork] = useState<string>("");
  const [password, setPassword] = useState("");
  const [isConnecting, setIsConnecting] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<
    "idle" | "connecting" | "success" | "error"
  >("idle");

  // Convert RSSI to percentage (RSSI is typically negative, -30 to -90 dBm)
  const convertRSSIToPercentage = (rssi: number): number => {
    if (rssi >= -30) return 100;
    if (rssi <= -90) return 0;
    return Math.round(((rssi + 90) / 60) * 100);
  };

  // Map authmode numbers to security types
  const mapAuthModeToSecurity = (
    authmode: number
  ): "open" | "wep" | "wpa" | "wpa2" => {
    switch (authmode) {
      case 0:
        return "open";
      case 1:
        return "wep";
      case 2:
        return "wpa";
      case 3:
        return "wpa2";
      case 4:
        return "wpa2"; // WPA2_PSK
      case 5:
        return "wpa2"; // WPA_WPA2_PSK
      default:
        return "wpa2";
    }
  };

  const handleScanNetworks = async () => {
    setIsScanning(true);
    try {
      const token = useAppStore.getState().token;

      const response = await axios.get(
        `${window.location.origin}/api/wifi/list?token=${token}`
      );

      if (response.data && response.data.data) {
        const { availables, saveds, ssid_connnected } = response.data.data;

        // Map available networks to WiFiNetwork format
        const networks: WiFiNetwork[] = availables.map((network: any) => ({
          ssid: network.ssid,
          signal: convertRSSIToPercentage(network.rssi),
          security: mapAuthModeToSecurity(network.authmode),
          bssid: network.bssid,
          channel: network.channel,
          authmode: network.authmode,
          hidden: network.hidden,
          connected: network.ssid === ssid_connnected,
        }));

        // Filter out hidden networks and sort by signal strength
        const visibleNetworks = networks
          .filter((network) => !network.hidden && network.ssid.length > 0)
          .sort((a, b) => b.signal - a.signal);

        setAvailableNetworks(visibleNetworks);

        // Map saved networks to SavedNetwork format
        const savedNetworksList: SavedNetwork[] = saveds.map((saved: any) => ({
          ssid: saved.ssid || saved,
          lastConnected: saved.lastConnected || "Unknown",
          autoConnect: saved.autoConnect || false,
          connected: saved.ssid === ssid_connnected,
        }));

        setSavedNetworks(savedNetworksList);
      }
    } catch (error) {
      console.error("WiFi scan failed:", error);
      // Keep existing networks on error
    } finally {
      setIsScanning(false);
    }
  };

  // Perform initial WiFi scan on component mount
  useEffect(() => {
    handleScanNetworks();
  }, []);

  const handleConnectNew = (ssid: string, security: string) => {
    setSelectedNetwork(ssid);
    if (security === "open") {
      // Connect directly for open networks
      handleConnect("");
    } else {
      setShowPasswordModal(true);
    }
  };

  const handleConnectSaved = async (ssid: string) => {
    setSelectedNetwork(ssid);
    setIsConnecting(true);
    setConnectionStatus("connecting");

    // Simulate connection attempt
    await new Promise((resolve) => setTimeout(resolve, 3000));

    // Simulate success/failure
    const success = Math.random() > 0.3;
    setConnectionStatus(success ? "success" : "error");
    setIsConnecting(false);

    setTimeout(() => {
      setConnectionStatus("idle");
      setSelectedNetwork("");
    }, 2000);
  };

  const handleConnect = async (pwd: string) => {
    setPassword(pwd);
    setShowPasswordModal(false);
    setIsConnecting(true);
    setConnectionStatus("connecting");

    // Simulate connection attempt
    await new Promise((resolve) => setTimeout(resolve, 3000));

    // Simulate success/failure
    const success = Math.random() > 0.2;
    setConnectionStatus(success ? "success" : "error");
    setIsConnecting(false);

    setTimeout(() => {
      setConnectionStatus("idle");
      setSelectedNetwork("");
      setPassword("");
    }, 2000);
  };

  const getSignalIcon = (signal: number) => {
    if (signal >= 75) return "📶";
    if (signal >= 50) return "📶";
    if (signal >= 25) return "📶";
    return "📶";
  };

  const getSecurityIcon = (security: string) => {
    return security === "open" ? "🔓" : "🔒";
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          {language === "id" ? "Koneksi WiFi" : "WiFi Connection"}
        </h1>
        <p className="text-gray-600">
          {language === "id"
            ? "Kelola koneksi WiFi dan jaringan tersimpan"
            : "Manage WiFi connections and saved networks"}
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Available Networks */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900">
                {language === "id" ? "Jaringan Tersedia" : "Available Networks"}
              </h2>
              <button
                onClick={handleScanNetworks}
                disabled={isScanning}
                className="flex items-center space-x-2 px-4 py-2 bg-emerald-600 text-white rounded-md hover:bg-emerald-700 disabled:bg-gray-400 transition-colors duration-200"
              >
                {isScanning ? (
                  <>
                    <svg
                      className="animate-spin w-4 h-4"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                      />
                    </svg>
                    <span>
                      {language === "id" ? "Memindai..." : "Scanning..."}
                    </span>
                  </>
                ) : (
                  <>
                    <svg
                      className="w-4 h-4"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                      />
                    </svg>
                    <span>{language === "id" ? "Pindai" : "Scan"}</span>
                  </>
                )}
              </button>
            </div>
          </div>

          <div className="p-6">
            <div className="space-y-3">
              {availableNetworks.map((network, index) => (
                <div
                  key={index}
                  className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors duration-200"
                >
                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-3 sm:space-y-0">
                    <div className="flex items-center space-x-3">
                      <span className="text-2xl">
                        {getSignalIcon(network.signal)}
                      </span>
                      <div>
                        <div className="flex items-center space-x-2">
                          <span className="text-lg">
                            {getSecurityIcon(network.security)}
                          </span>
                          <span className="font-medium text-gray-900">
                            {network.ssid}
                          </span>
                        </div>
                        <div className="flex items-center space-x-2 text-sm text-gray-500">
                          <span>
                            {language === "id" ? "Sinyal" : "Signal"}:{" "}
                            {network.signal}%
                          </span>
                          <span>•</span>
                          <span className="capitalize">{network.security}</span>
                        </div>
                      </div>
                    </div>

                    {!network.connected && (
                      <button
                        onClick={() =>
                          handleConnectNew(network.ssid, network.security)
                        }
                        disabled={
                          isConnecting && selectedNetwork === network.ssid
                        }
                        className="w-full sm:w-auto px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 transition-colors duration-200 text-sm font-medium"
                      >
                        {isConnecting && selectedNetwork === network.ssid ? (
                          <div className="flex items-center justify-center space-x-2">
                            <svg
                              className="animate-spin w-4 h-4"
                              fill="none"
                              stroke="currentColor"
                              viewBox="0 0 24 24"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                              />
                            </svg>
                            <span>
                              {language === "id"
                                ? "Menghubungkan..."
                                : "Connecting..."}
                            </span>
                          </div>
                        ) : language === "id" ? (
                          "Hubungkan"
                        ) : (
                          "Connect"
                        )}
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Saved Networks */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">
              {language === "id" ? "Jaringan Tersimpan" : "Saved Networks"}
            </h2>
          </div>

          <div className="p-6">
            <div className="space-y-3">
              {savedNetworks.map((network, index) => (
                <div
                  key={index}
                  className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors duration-200"
                >
                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-3 sm:space-y-0">
                    <div className="flex items-center space-x-3">
                      <span className="text-2xl">💾</span>
                      <div>
                        <div className="flex items-center space-x-2">
                          <span className="font-medium text-gray-900">
                            {network.ssid}
                          </span>
                          {network.autoConnect && (
                            <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                              {language === "id" ? "Otomatis" : "Auto"}
                            </span>
                          )}
                        </div>
                        <div className="text-sm text-gray-500">
                          {language === "id"
                            ? "Terakhir terhubung"
                            : "Last connected"}
                          : {network.lastConnected}
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center space-x-2 w-full sm:w-auto">
                      {!network.connected ? (
                        <button
                          onClick={() => handleConnectSaved(network.ssid)}
                          disabled={
                            isConnecting && selectedNetwork === network.ssid
                          }
                          className="flex-1 sm:flex-none px-4 py-2 bg-emerald-600 text-white rounded-md hover:bg-emerald-700 disabled:bg-gray-400 transition-colors duration-200 text-sm font-medium"
                        >
                          {isConnecting && selectedNetwork === network.ssid ? (
                            <div className="flex items-center justify-center space-x-2">
                              <svg
                                className="animate-spin w-4 h-4"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                              >
                                <path
                                  strokeLinecap="round"
                                  strokeLinejoin="round"
                                  strokeWidth={2}
                                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                                />
                              </svg>
                              <span>
                                {language === "id"
                                  ? "Menghubungkan..."
                                  : "Connecting..."}
                              </span>
                            </div>
                          ) : language === "id" ? (
                            "Hubungkan"
                          ) : (
                            "Connect"
                          )}
                        </button>
                      ) : (
                        <div>Connected</div>
                      )}
                      <button className="p-2 text-gray-400 hover:text-red-600 transition-colors duration-200">
                        <svg
                          className="w-4 h-4"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                          />
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Password Modal */}
      {showPasswordModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">
                  {language === "id"
                    ? "Masukkan Password WiFi"
                    : "Enter WiFi Password"}
                </h3>
                <button
                  onClick={() => setShowPasswordModal(false)}
                  className="text-gray-400 hover:text-gray-600 transition-colors duration-200"
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
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
              </div>

              <div className="mb-4">
                <p className="text-sm text-gray-600 mb-2">
                  {language === "id" ? "Jaringan" : "Network"}:{" "}
                  <span className="font-medium">{selectedNetwork}</span>
                </p>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder={
                    language === "id" ? "Masukkan password" : "Enter password"
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                  autoFocus
                />
              </div>

              <div className="flex justify-end space-x-3">
                <button
                  onClick={() => setShowPasswordModal(false)}
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors duration-200"
                >
                  {language === "id" ? "Batal" : "Cancel"}
                </button>
                <button
                  onClick={() => handleConnect(password)}
                  disabled={!password.trim()}
                  className="px-4 py-2 bg-emerald-600 text-white rounded-md hover:bg-emerald-700 disabled:bg-gray-400 transition-colors duration-200"
                >
                  {language === "id" ? "Hubungkan" : "Connect"}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Connection Status Toast */}
      {connectionStatus !== "idle" && (
        <div className="fixed bottom-4 right-4 bg-white rounded-lg shadow-lg border border-gray-200 p-4 max-w-sm">
          <div className="flex items-center space-x-3">
            {connectionStatus === "connecting" && (
              <>
                <svg
                  className="animate-spin w-5 h-5 text-blue-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                  />
                </svg>
                <span className="text-gray-900">
                  {language === "id" ? "Menghubungkan ke" : "Connecting to"}{" "}
                  {selectedNetwork}...
                </span>
              </>
            )}
            {connectionStatus === "success" && (
              <>
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
                    d="M5 13l4 4L19 7"
                  />
                </svg>
                <span className="text-gray-900">
                  {language === "id"
                    ? "Berhasil terhubung ke"
                    : "Successfully connected to"}{" "}
                  {selectedNetwork}
                </span>
              </>
            )}
            {connectionStatus === "error" && (
              <>
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
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
                <span className="text-gray-900">
                  {language === "id"
                    ? "Gagal terhubung ke"
                    : "Failed to connect to"}{" "}
                  {selectedNetwork}
                </span>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
