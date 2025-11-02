import { useState } from 'react';
import { useAppStore } from '@/store/useAppStore';
import { useNavigate } from 'react-router';
import axios from 'axios';
import { z } from 'zod';

type WiFiMode = 'access-point' | 'station' | '';

// Zod schema for IP address validation
const ipAddressSchema = z.string().regex(
  /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/,
  'Format IP address tidak valid (contoh: 192.168.1.100)'
);

const loginSchema = z.object({
  wifiMode: z.enum(['access-point', 'station']),
  ipAddress: z.string().optional(),
  password: z.string().min(1, 'Password tidak boleh kosong')
}).refine((data) => {
  if (data.wifiMode === 'station') {
    return data.ipAddress && ipAddressSchema.safeParse(data.ipAddress).success;
  }
  return true;
}, {
  message: 'IP address diperlukan untuk WiFi Station',
  path: ['ipAddress']
});

export default function LoginPage() {
  const { language, setToken, setIpAddress: setStoreIpAddress, getHostUrl: getStoreHostUrl } = useAppStore();
  const navigate = useNavigate();
  const [wifiMode, setWifiMode] = useState<WiFiMode>('');
  const [ipAddress, setIpAddress] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const content = {
    id: {
      title: 'Login ke Sistem IoT',
      subtitle: 'Pilih metode koneksi WiFi dan masukkan kredensial',
      wifiModeLabel: 'Metode WiFi',
      wifiModeOptions: {
        placeholder: 'Pilih metode WiFi...',
        accessPoint: 'Wi-Fi Access Point',
        station: 'Wi-Fi Station'
      },
      ipAddressLabel: 'Alamat IP',
      ipAddressPlaceholder: 'Masukkan alamat IP (contoh: 192.168.1.100)',
      passwordLabel: 'Password',
      passwordPlaceholder: 'Masukkan password WiFi',
      loginButton: 'Masuk',
      loadingText: 'Menghubungkan...',
      backToHome: 'Kembali ke Beranda'
    },
    en: {
      title: 'IoT System Login',
      subtitle: 'Select WiFi connection method and enter credentials',
      wifiModeLabel: 'WiFi Method',
      wifiModeOptions: {
        placeholder: 'Select WiFi method...',
        accessPoint: 'Wi-Fi Access Point',
        station: 'Wi-Fi Station'
      },
      ipAddressLabel: 'IP Address',
      ipAddressPlaceholder: 'Enter IP address (example: 192.168.1.100)',
      passwordLabel: 'Password',
      passwordPlaceholder: 'Enter WiFi password',
      loginButton: 'Login',
      loadingText: 'Connecting...',
      backToHome: 'Back to Home'
    }
  };

  const currentContent = content[language];


  // Format IP address input with xxx.xxx.xxx.xxx pattern
  const formatIpAddress = (value: string) => {
    // Remove all non-numeric characters except dots
    const cleaned = value.replace(/[^\d.]/g, '');
    
    // Split by dots and limit each segment to 3 digits
    const segments = cleaned.split('.');
    const formattedSegments = segments.map((segment) => {
      // Limit to 3 digits per segment
      let limitedSegment = segment.slice(0, 3);
      
      // Ensure each segment doesn't exceed 255
      const num = parseInt(limitedSegment);
      if (!isNaN(num) && num > 255) {
        limitedSegment = '255';
      }
      
      return limitedSegment;
    });
    
    // Limit to 4 segments
    const limitedSegments = formattedSegments.slice(0, 4);
    
    return limitedSegments.join('.');
  };

  const validateForm = () => {
    try {
      const formData = {
        wifiMode: wifiMode as 'access-point' | 'station',
        ipAddress: wifiMode === 'station' ? ipAddress : undefined,
        password: password
      };

      const result = loginSchema.safeParse(formData);
      
      if (!result.success) {
        const firstError = result.error.issues[0];
        if (language === 'id') {
          setError(firstError.message);
        } else {
          // English error messages
          if (firstError.path.includes('wifiMode')) {
            setError('Please select WiFi method first');
          } else if (firstError.path.includes('ipAddress')) {
            setError('Please enter a valid IP address for WiFi Station');
          } else if (firstError.path.includes('password')) {
            setError('Password cannot be empty');
          } else {
            setError('Invalid input format');
          }
        }
        return false;
      }

      return true;
    } catch (error) {
      setError(language === 'id' ? 'Terjadi kesalahan validasi' : 'Validation error occurred');
      return false;
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!validateForm()) return;

    setIsLoading(true);

    try {
      // Save IP address and WiFi mode to store first
      setStoreIpAddress(ipAddress, wifiMode as 'access-point' | 'station');
      
      // Get host URL from store
      const hostUrl = getStoreHostUrl();
      const response = await axios.post(`${hostUrl}/api/auth/login`, {
        password: password
      }, {
        timeout: 10000, // 10 second timeout
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (response.status === 200 && response.data.token) {
        // Save token to Zustand store
        setToken(response.data.token);
        setSuccess(language === 'id' ? 'Login berhasil!' : 'Login successful!');
        
        // Navigate to dashboard after short delay
        setTimeout(() => {
          navigate('/app/dashboard', { replace: true });
        }, 1000);
        
        console.log('Login successful:', response.data);
      }
    } catch (err: any) {
      console.error('Login error:', err);
      
      if (err.code === 'ECONNABORTED') {
        setError(language === 'id' ? 'Koneksi timeout. Periksa alamat IP dan koneksi jaringan.' : 'Connection timeout. Check IP address and network connection.');
      } else if (err.response?.status === 401) {
        setError(language === 'id' ? 'Password salah' : 'Incorrect password');
      } else if (err.response?.status === 404) {
        setError(language === 'id' ? 'Endpoint tidak ditemukan. Periksa alamat IP.' : 'Endpoint not found. Check IP address.');
      } else if (err.code === 'ERR_NETWORK') {
        setError(language === 'id' ? 'Tidak dapat terhubung ke perangkat. Periksa koneksi WiFi dan alamat IP.' : 'Cannot connect to device. Check WiFi connection and IP address.');
      } else {
        setError(language === 'id' ? 'Terjadi kesalahan saat login' : 'An error occurred during login');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleWifiModeChange = (mode: WiFiMode) => {
    setWifiMode(mode);
    setError('');
    setSuccess('');
    
    // Reset IP address when switching modes
    if (mode === 'access-point') {
      setIpAddress('');
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
            <p className="text-gray-600">
              {currentContent.subtitle}
            </p>
          </div>

        {/* Login Form */}
        <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* WiFi Mode Selection */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                {currentContent.wifiModeLabel}
              </label>
              <select
                value={wifiMode}
                onChange={(e) => handleWifiModeChange(e.target.value as WiFiMode)}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-colors bg-white text-gray-900"
                required
              >
                <option value="">{currentContent.wifiModeOptions.placeholder}</option>
                <option value="access-point">{currentContent.wifiModeOptions.accessPoint}</option>
                <option value="station">{currentContent.wifiModeOptions.station}</option>
              </select>
            </div>

            {/* IP Address Field (only for WiFi Station) */}
            {wifiMode === 'station' && (
              <div className="animate-in slide-in-from-top-2 duration-300">
                <label className="block text-sm font-semibold text-gray-700 mb-3">
                  {currentContent.ipAddressLabel}
                </label>
                <input
                  type="text"
                  value={ipAddress}
                  onChange={(e) => {
                    const formattedValue = formatIpAddress(e.target.value);
                    setIpAddress(formattedValue);
                  }}
                  placeholder="192.168.1.100"
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-colors font-mono"
                  required
                  maxLength={15}
                />
              </div>
            )}

            {/* Password Field (appears after WiFi mode selection) */}
            {wifiMode && (
              <div className="animate-in slide-in-from-top-2 duration-300">
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
                />
              </div>
            )}

            {/* Connection Info */}
            {wifiMode && (
              <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4 animate-in slide-in-from-top-2 duration-300">
                <div className="flex items-center space-x-2">
                  <svg className="w-5 h-5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <div className="text-sm">
                    <p className="font-medium text-emerald-800">
                      {language === 'id' ? 'Akan terhubung ke:' : 'Will connect to:'}
                    </p>
                    <p className="text-emerald-700 font-mono">
                      {wifiMode === 'access-point' ? '192.168.4.1' : ipAddress || 'IP belum diisi'}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Error Message */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-xl p-4 animate-in slide-in-from-top-2 duration-300">
                <div className="flex items-center space-x-2">
                  <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <p className="text-sm text-red-700">{error}</p>
                </div>
              </div>
            )}

            {/* Success Message */}
            {success && (
              <div className="bg-green-50 border border-green-200 rounded-xl p-4 animate-in slide-in-from-top-2 duration-300">
                <div className="flex items-center space-x-2">
                  <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <p className="text-sm text-green-700">{success}</p>
                </div>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading || !wifiMode}
              className="w-full bg-linear-to-r from-emerald-600 to-teal-600 text-white font-semibold py-3 px-6 rounded-xl hover:from-emerald-700 hover:to-teal-700 focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-[1.02] active:scale-[0.98]"
            >
              {isLoading ? (
                <div className="flex items-center justify-center space-x-2">
                  <svg className="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
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
