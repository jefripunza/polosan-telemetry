"""
MicroPython Driver untuk RK300-02B Dust Sensor via RS485
Pin Configuration:
- RST (DE/RE): GPIO 14 (Direction Control)
- TX2: GPIO 15 (UART TX)
- RX2: GPIO 16 (UART RX)
"""

from machine import UART, Pin
import time

class RK300_RS485:
    def __init__(self, rst_pin=14, tx_pin=15, rx_pin=16, uart_id=2, baudrate=9600):
        """
        Inisialisasi RK300-02B dengan RS485
        
        Args:
            rst_pin: Pin untuk DE/RE control (default: 14)
            tx_pin: Pin untuk TX (default: 15)
            rx_pin: Pin untuk RX (default: 16)
            uart_id: UART ID (default: 2)
            baudrate: Baud rate (default: 9600)
        """
        # Setup pin DE/RE untuk kontrol arah komunikasi RS485
        self.de_re = Pin(rst_pin, Pin.OUT)
        self.de_re.value(0)  # Set ke mode receive (LOW)
        
        # Setup UART
        self.uart = UART(uart_id, baudrate=baudrate, tx=tx_pin, rx=rx_pin,
                        bits=8, parity=None, stop=1, timeout=1000)
        
        # Default device address (sesuaikan dengan setting sensor Anda)
        self.device_addr = 0x01
        
        print("RK300-02B RS485 Initialized")
        print(f"RST/DE/RE Pin: {rst_pin}")
        print(f"TX Pin: {tx_pin}")
        print(f"RX Pin: {rx_pin}")
        
    def _calculate_checksum(self, data):
        """Hitung checksum untuk protokol Modbus RTU"""
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x0001:
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        return crc
    
    def _send_command(self, command):
        """Kirim perintah via RS485"""
        # Set ke mode transmit
        self.de_re.value(1)
        time.sleep_ms(10)  # Delay kecil untuk stabilitas
        
        # Kirim command
        self.uart.write(command)
        
        # Tunggu transmisi selesai
        time.sleep_ms(50)
        
        # Set ke mode receive
        self.de_re.value(0)
        time.sleep_ms(10)
    
    def _read_response(self, expected_length, timeout_ms=1000):
        """Baca response dari sensor"""
        start_time = time.ticks_ms()
        response = bytearray()
        
        while len(response) < expected_length:
            if time.ticks_diff(time.ticks_ms(), start_time) > timeout_ms:
                print("Timeout waiting for response")
                return None
            
            if self.uart.any():
                response.extend(self.uart.read(1))
        
        return bytes(response)
    
    def read_dust_data(self):
        """
        Baca data debu dari sensor RK300-02B
        Returns: Dictionary dengan PM1.0, PM2.5, PM10 atau None jika gagal
        """
        # Command untuk membaca data (Modbus RTU Read Holding Registers)
        # Format: [Address][Function][Start Reg High][Start Reg Low][Num Reg High][Num Reg Low]
        command = bytearray([
            self.device_addr,  # Device address
            0x03,              # Function code: Read Holding Registers
            0x00,              # Start register high byte
            0x00,              # Start register low byte
            0x00,              # Number of registers high byte
            0x06               # Number of registers low byte (6 registers)
        ])
        
        # Tambahkan checksum
        crc = self._calculate_checksum(command)
        command.append(crc & 0xFF)
        command.append((crc >> 8) & 0xFF)
        
        # Clear buffer
        while self.uart.any():
            self.uart.read()
        
        # Kirim command
        self._send_command(command)
        
        # Baca response (Address + Function + Byte Count + Data + CRC = 3 + 12 + 2 = 17 bytes)
        response = self._read_response(17, timeout_ms=1000)
        
        if response is None or len(response) < 17:
            print("Failed to read data from sensor")
            return None
        
        # Verifikasi checksum
        received_crc = response[-2] | (response[-1] << 8)
        calculated_crc = self._calculate_checksum(response[:-2])
        
        if received_crc != calculated_crc:
            print("Checksum error")
            return None
        
        # Parse data
        # Data format: [Addr][Func][Byte Count][PM1.0 H][PM1.0 L][PM2.5 H][PM2.5 L][PM10 H][PM10 L][Reserved...][CRC]
        pm1_0 = (response[3] << 8) | response[4]
        pm2_5 = (response[5] << 8) | response[6]
        pm10 = (response[7] << 8) | response[8]
        
        return {
            'PM1.0': pm1_0,
            'PM2.5': pm2_5,
            'PM10': pm10,
            'unit': 'μg/m³'
        }
    
    def read_continuous(self, interval_sec=2):
        """
        Baca data secara kontinyu
        
        Args:
            interval_sec: Interval pembacaan dalam detik
        """
        print("\nMembaca data sensor (Ctrl+C untuk stop)...")
        print("-" * 50)
        
        try:
            while True:
                data = self.read_dust_data()
                
                if data:
                    print(f"PM1.0: {data['PM1.0']:4d} {data['unit']} | "
                          f"PM2.5: {data['PM2.5']:4d} {data['unit']} | "
                          f"PM10: {data['PM10']:4d} {data['unit']}")
                else:
                    print("Gagal membaca data")
                
                time.sleep(interval_sec)
                
        except KeyboardInterrupt:
            print("\n\nPembacaan dihentikan")


# ============ CONTOH PENGGUNAAN ============

def main():
    """Fungsi utama untuk testing"""
    
    # Inisialisasi sensor
    sensor = RK300_RS485(rst_pin=14, tx_pin=15, rx_pin=16)
    
    # Tunggu sensor ready
    time.sleep(2)
    
    print("\n=== Test Pembacaan Tunggal ===")
    data = sensor.read_dust_data()
    if data:
        print(f"PM1.0: {data['PM1.0']} {data['unit']}")
        print(f"PM2.5: {data['PM2.5']} {data['unit']}")
        print(f"PM10:  {data['PM10']} {data['unit']}")
    else:
        print("Gagal membaca data sensor")
    
    print("\n=== Test Pembacaan Kontinyu ===")
    # Baca data setiap 2 detik
    sensor.read_continuous(interval_sec=2)


if __name__ == "__main__":
    main()
