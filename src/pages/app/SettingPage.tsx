import { useState } from 'react';
import { useAppStore } from '@/store/useAppStore';

type SettingTab = 'identity' | 'network' | 'webserver' | 'server-integration' | 'log' | 'uart';

export default function SettingPage() {
  const { language } = useAppStore();
  const [activeTab, setActiveTab] = useState<SettingTab>('identity');

  const tabs = [
    {
      id: 'identity' as SettingTab,
      name: language === 'id' ? 'Identitas' : 'Identity',
      icon: '🆔'
    },
    {
      id: 'network' as SettingTab,
      name: language === 'id' ? 'Jaringan' : 'Network',
      icon: '🌐'
    },
    {
      id: 'webserver' as SettingTab,
      name: language === 'id' ? 'Web Server' : 'Web Server',
      icon: '🖥️'
    },
    {
      id: 'server-integration' as SettingTab,
      name: language === 'id' ? 'Integrasi Server' : 'Server Integration',
      icon: '🔗'
    },
    {
      id: 'log' as SettingTab,
      name: language === 'id' ? 'Log' : 'Log',
      icon: '📝'
    },
    {
      id: 'uart' as SettingTab,
      name: language === 'id' ? 'UART' : 'UART',
      icon: '📡'
    }
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case 'identity':
        return <IdentityTab />;
      case 'network':
        return <NetworkTab />;
      case 'webserver':
        return <WebServerTab />;
      case 'server-integration':
        return <ServerIntegrationTab />;
      case 'log':
        return <LogTab />;
      case 'uart':
        return <UARTTab />;
      default:
        return <IdentityTab />;
    }
  };

  return (
    <div className="max-w-6xl mx-auto">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        {/* Tab Navigation */}
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6" aria-label="Tabs">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors duration-200 ${
                  activeTab === tab.id
                    ? 'border-emerald-500 text-emerald-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <span className="text-lg">{tab.icon}</span>
                <span>{tab.name}</span>
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="p-6">
          {renderTabContent()}
        </div>
      </div>
    </div>
  );
}

// Identity Tab Component
function IdentityTab() {
  const { language } = useAppStore();
  
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          {language === 'id' ? 'Informasi Perangkat' : 'Device Information'}
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {language === 'id' ? 'Nama Perangkat' : 'Device Name'}
            </label>
            <input
              type="text"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
              placeholder="Molinar IoT Device"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {language === 'id' ? 'ID Perangkat' : 'Device ID'}
            </label>
            <input
              type="text"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
              placeholder="MOL-001"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {language === 'id' ? 'Lokasi' : 'Location'}
            </label>
            <input
              type="text"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
              placeholder={language === 'id' ? 'Masukkan lokasi' : 'Enter location'}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {language === 'id' ? 'Deskripsi' : 'Description'}
            </label>
            <input
              type="text"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
              placeholder={language === 'id' ? 'Deskripsi perangkat' : 'Device description'}
            />
          </div>
        </div>
      </div>
      
      <div className="flex justify-end">
        <button className="px-4 py-2 bg-emerald-600 text-white rounded-md hover:bg-emerald-700 transition-colors duration-200">
          {language === 'id' ? 'Simpan' : 'Save'}
        </button>
      </div>
    </div>
  );
}

// Network Tab Component
function NetworkTab() {
  const { language } = useAppStore();
  
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          {language === 'id' ? 'Konfigurasi Jaringan' : 'Network Configuration'}
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {language === 'id' ? 'Mode WiFi' : 'WiFi Mode'}
            </label>
            <select className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500">
              <option value="ap">Access Point</option>
              <option value="station">Station</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {language === 'id' ? 'SSID' : 'SSID'}
            </label>
            <input
              type="text"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
              placeholder="Molinar-IoT"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {language === 'id' ? 'Password WiFi' : 'WiFi Password'}
            </label>
            <input
              type="password"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
              placeholder="********"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {language === 'id' ? 'IP Address' : 'IP Address'}
            </label>
            <input
              type="text"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
              placeholder="192.168.4.1"
            />
          </div>
        </div>
      </div>
      
      <div className="flex justify-end">
        <button className="px-4 py-2 bg-emerald-600 text-white rounded-md hover:bg-emerald-700 transition-colors duration-200">
          {language === 'id' ? 'Simpan' : 'Save'}
        </button>
      </div>
    </div>
  );
}

// WebServer Tab Component
function WebServerTab() {
  const { language } = useAppStore();
  
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          {language === 'id' ? 'Konfigurasi Web Server' : 'Web Server Configuration'}
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {language === 'id' ? 'Port' : 'Port'}
            </label>
            <input
              type="number"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
              placeholder="80"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {language === 'id' ? 'Timeout (detik)' : 'Timeout (seconds)'}
            </label>
            <input
              type="number"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
              placeholder="30"
            />
          </div>
          <div className="md:col-span-2">
            <label className="flex items-center">
              <input type="checkbox" className="rounded border-gray-300 text-emerald-600 focus:ring-emerald-500" />
              <span className="ml-2 text-sm text-gray-700">
                {language === 'id' ? 'Aktifkan HTTPS' : 'Enable HTTPS'}
              </span>
            </label>
          </div>
        </div>
      </div>
      
      <div className="flex justify-end">
        <button className="px-4 py-2 bg-emerald-600 text-white rounded-md hover:bg-emerald-700 transition-colors duration-200">
          {language === 'id' ? 'Simpan' : 'Save'}
        </button>
      </div>
    </div>
  );
}

// Server Integration Tab Component
function ServerIntegrationTab() {
  const { language } = useAppStore();
  
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          {language === 'id' ? 'Integrasi Server' : 'Server Integration'}
        </h3>
        <div className="grid grid-cols-1 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {language === 'id' ? 'URL Server' : 'Server URL'}
            </label>
            <input
              type="url"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
              placeholder="https://api.molinar.id"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {language === 'id' ? 'API Key' : 'API Key'}
            </label>
            <input
              type="password"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
              placeholder="Enter API key"
            />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {language === 'id' ? 'Interval Kirim (detik)' : 'Send Interval (seconds)'}
              </label>
              <input
                type="number"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                placeholder="60"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {language === 'id' ? 'Retry Count' : 'Retry Count'}
              </label>
              <input
                type="number"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                placeholder="3"
              />
            </div>
          </div>
        </div>
      </div>
      
      <div className="flex justify-end">
        <button className="px-4 py-2 bg-emerald-600 text-white rounded-md hover:bg-emerald-700 transition-colors duration-200">
          {language === 'id' ? 'Simpan' : 'Save'}
        </button>
      </div>
    </div>
  );
}

// Log Tab Component
function LogTab() {
  const { language } = useAppStore();
  
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          {language === 'id' ? 'Konfigurasi Log' : 'Log Configuration'}
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {language === 'id' ? 'Level Log' : 'Log Level'}
            </label>
            <select className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500">
              <option value="debug">Debug</option>
              <option value="info">Info</option>
              <option value="warning">Warning</option>
              <option value="error">Error</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {language === 'id' ? 'Maksimal File Log' : 'Max Log Files'}
            </label>
            <input
              type="number"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
              placeholder="10"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {language === 'id' ? 'Ukuran File (KB)' : 'File Size (KB)'}
            </label>
            <input
              type="number"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
              placeholder="1024"
            />
          </div>
          <div>
            <label className="flex items-center">
              <input type="checkbox" className="rounded border-gray-300 text-emerald-600 focus:ring-emerald-500" />
              <span className="ml-2 text-sm text-gray-700">
                {language === 'id' ? 'Aktifkan Log ke Server' : 'Enable Server Logging'}
              </span>
            </label>
          </div>
        </div>
      </div>
      
      <div className="flex justify-end">
        <button className="px-4 py-2 bg-emerald-600 text-white rounded-md hover:bg-emerald-700 transition-colors duration-200">
          {language === 'id' ? 'Simpan' : 'Save'}
        </button>
      </div>
    </div>
  );
}

// UART Tab Component
function UARTTab() {
  const { language } = useAppStore();
  
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          {language === 'id' ? 'Konfigurasi UART' : 'UART Configuration'}
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {language === 'id' ? 'Baud Rate' : 'Baud Rate'}
            </label>
            <select className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500">
              <option value="9600">9600</option>
              <option value="19200">19200</option>
              <option value="38400">38400</option>
              <option value="57600">57600</option>
              <option value="115200">115200</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {language === 'id' ? 'Data Bits' : 'Data Bits'}
            </label>
            <select className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500">
              <option value="7">7</option>
              <option value="8">8</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {language === 'id' ? 'Parity' : 'Parity'}
            </label>
            <select className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500">
              <option value="none">None</option>
              <option value="even">Even</option>
              <option value="odd">Odd</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {language === 'id' ? 'Stop Bits' : 'Stop Bits'}
            </label>
            <select className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500">
              <option value="1">1</option>
              <option value="2">2</option>
            </select>
          </div>
        </div>
      </div>
      
      <div className="flex justify-end">
        <button className="px-4 py-2 bg-emerald-600 text-white rounded-md hover:bg-emerald-700 transition-colors duration-200">
          {language === 'id' ? 'Simpan' : 'Save'}
        </button>
      </div>
    </div>
  );
}
