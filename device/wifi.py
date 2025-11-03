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

    def get_ip(self):
        return self.sta.ifconfig()[0]

    def scan(self):
        return self.sta.scan()
