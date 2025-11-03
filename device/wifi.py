import network
import time

class AccessPoint:
    def __init__(self, essid="My-ESP-AP", password="12345678",
                 ip="192.168.4.1", subnet="255.255.255.0",
                 gateway="192.168.4.1", dns="8.8.8.8"):
        self.ap = network.WLAN(network.AP_IF)
        self.ap.active(True)
        self.ap.config(
            essid=essid,
            password=password,
            authmode=3  # WPA2-PSK
        )
        self.ap.ifconfig((ip, subnet, gateway, dns))

    def get_ip(self):
        return self.ap.ifconfig()[0]


class Station:
    def __init__(self, ssid=None, password=None,
                 ip=None, subnet="255.255.255.0",
                 gateway=None, dns="8.8.8.8"):
        self.sta = network.WLAN(network.STA_IF)
        self.sta.active(True)
        self.connected = False  # default belum connect

        # pastikan disconnect dulu
        if self.sta.isconnected():
            self.sta.disconnect()

        if ip and gateway:  # static IP
            self.sta.ifconfig((ip, subnet, gateway, dns))

        if ssid and password:
            print(f"Scanning for \"{ssid}\" ...")
            available = [ap[0].decode() for ap in self.sta.scan()]
            print(f"\n# SSID AVAILABLES:{available}\n")

            if ssid not in available:
                print(f"SSID \"{ssid}\" not found, skipping connection.")
                return  # langsung keluar, connected tetap False

            print(f"Connecting to \"{ssid}\" ...")
            if isinstance(ssid, str):
                ssid = ssid.encode()

            time.sleep(0.5)  # kasih jeda sebelum connect
            self.sta.connect(ssid, password)

            timeout = 15
            while not self.sta.isconnected() and timeout > 0:
                print("Waiting for connection...")
                time.sleep(1)
                timeout -= 1

            if self.sta.isconnected():
                self.connected = True
                print("Connected, IP:", self.get_ip())
            else:
                print("Failed to connect, timeout reached.")

    def __bool__(self):
        """Biar bisa if sta: ..."""
        return self.connected

    def connect(self, ssid, password, timeout=10):
        """
        Connect to WiFi station with proper handling
        Returns: (success: bool, message: str, ip: str)
        """
        import time
        
        try:
            # Disconnect from current network if connected
            if self.sta.isconnected():
                print(f"Disconnecting from current network...")
                self.sta.disconnect()
                # Wait for disconnect to complete
                time.sleep(1)
            
            # Activate station mode if not active
            if not self.sta.active():
                print("Activating station mode...")
                self.sta.active(True)
                time.sleep(1)
            
            print(f"Connecting to WiFi: {ssid}")
            self.sta.connect(ssid, password)
            
            # Wait for connection with timeout
            start_time = time.time()
            while not self.sta.isconnected():
                if time.time() - start_time > timeout:
                    return False, f"Connection timeout after {timeout} seconds", ""
                time.sleep(0.5)
                print(".", end="")
            
            # Connection successful
            ip_info = self.sta.ifconfig()
            ip_address = ip_info[0]
            print(f"\nConnected successfully! IP: {ip_address}")
            
            # Update connection status
            self.connected = True
            
            return True, f"Connected to {ssid}", ip_address
            
        except Exception as e:
            print(f"Connection error: {e}")
            return False, f"Connection failed: {str(e)}", ""

    def get_ip(self):
        return self.sta.ifconfig()[0]

    def scan(self):
        return self.sta.scan()
