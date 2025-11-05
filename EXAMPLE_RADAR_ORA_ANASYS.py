from machine import UART, Pin
import time

class WaterLevelRadarSensor:
    """
    Driver CEPAT untuk AnSens-0105 - Hanya Pembacaan Jarak
    """
    
    def __init__(self, uart_id=2, tx_pin=15, rx_pin=16, rst_pin=14, 
                 baudrate=9600, slave_addr=0x0A):
        """Inisialisasi sensor"""
        # Setup pin RST
        self.rst = Pin(rst_pin, Pin.OUT)
        self.rst.value(1)
        
        # Setup UART untuk RS485
        self.uart = UART(uart_id, baudrate=baudrate, tx=tx_pin, rx=rx_pin,
                        bits=8, parity=None, stop=1, timeout=200)
        
        self.slave_addr = slave_addr
        
        # Pre-calculate frame untuk pembacaan jarak (optimasi)
        self.distance_frame = self._create_modbus_frame(0x03, 0x0000, 0x0001)
        
        time.sleep_ms(50)
        print(f"Sensor siap! Address: 0x{slave_addr:02X}, Baudrate: {baudrate}")
    
    def _calculate_crc16(self, data):
        """Hitung CRC16 Modbus (optimized)"""
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x0001:
                    crc = (crc >> 1) ^ 0xA001
                else:
                    crc >>= 1
        return crc
    
    def _create_modbus_frame(self, function_code, start_addr, num_registers):
        """Buat frame Modbus RTU"""
        frame = bytearray([
            self.slave_addr,
            function_code,
            (start_addr >> 8) & 0xFF,
            start_addr & 0xFF,
            (num_registers >> 8) & 0xFF,
            num_registers & 0xFF
        ])
        
        crc = self._calculate_crc16(frame)
        frame.append(crc & 0xFF)
        frame.append((crc >> 8) & 0xFF)
        
        return frame
    
    def read_distance_fast(self):
        """
        Baca jarak dengan cepat
        
        Returns:
            int: Nilai raw dari sensor (satuan tergantung sensor: bisa mm atau cm*10)
        """
        # Bersihkan buffer
        while self.uart.any():
            self.uart.read()
        
        # Kirim command (menggunakan pre-calculated frame)
        self.uart.write(self.distance_frame)
        
        # Tunggu response (dipercepat)
        time.sleep_ms(30)
        
        if self.uart.any():
            response = self.uart.read()
            
            if response and len(response) >= 7:
                # Quick CRC check
                data = response[:-2]
                received_crc = response[-2] | (response[-1] << 8)
                calculated_crc = self._calculate_crc16(data)
                
                if received_crc == calculated_crc:
                    # Parse jarak
                    distance = (response[3] << 8) | response[4]
                    return distance
        
        return None
    
    def read_distance_cm(self):
        """
        Baca jarak dalam cm
        Sensor mengirim data dalam format: nilai * 10 = cm
        Contoh: 199 dari sensor = 199 cm = 19.9 dm = 1.99 m
        """
        distance = self.read_distance_fast()
        return distance if distance is not None else None
    
    def read_distance_m(self):
        """
        Baca jarak dalam meter
        Konversi: nilai sensor / 100 = meter
        Contoh: 199 dari sensor = 1.99 m
        """
        distance = self.read_distance_fast()
        return distance / 100.0 if distance is not None else None


# ===== PROGRAM UTAMA - VERSI CEPAT =====
def main():
    """Program utama - pembacaan cepat"""
    
    print("\n" + "="*50)
    print("FAST Water Level Radar Reader")
    print("="*50 + "\n")
    
    # Inisialisasi sensor
    sensor = WaterLevelRadarSensor(
        uart_id=2,
        tx_pin=15,
        rx_pin=16,
        rst_pin=14,
        baudrate=9600,  # Coba naikkan ke 19200 atau 38400 jika sensor support
        slave_addr=0x0A
    )
    
    print("Mulai pembacaan cepat...\n")
    
    # Variabel untuk tracking
    read_count = 0
    error_count = 0
    start_time = time.ticks_ms()
    
    try:
        while True:
            # Baca jarak
            distance_raw = sensor.read_distance_fast()
            
            if distance_raw is not None:
                read_count += 1
                
                # Konversi yang benar:
                # Raw value = cm
                # Contoh: 199 = 199 cm = 1.99 m
                distance_cm = distance_raw
                distance_m = distance_raw / 100.0
                
                print(f"[{read_count}] Jarak: {distance_raw} | {distance_cm} cm | {distance_m:.2f} m")
            else:
                error_count += 1
                print(f"[ERROR {error_count}] Gagal membaca")
            
            # Hitung reading rate setiap 10 pembacaan
            if read_count % 10 == 0 and read_count > 0:
                elapsed = time.ticks_diff(time.ticks_ms(), start_time)
                rate = read_count / (elapsed / 1000.0)
                print(f"\n>>> Rate: {rate:.1f} readings/second <<<\n")
            
            # Delay minimal untuk pembacaan cepat
            time.sleep_ms(1000*10)  # 50ms = ~20 readings/second max
            
    except KeyboardInterrupt:
        print("\n\nProgram dihentikan")
        print(f"Total pembacaan: {read_count}")
        print(f"Total error: {error_count}")
        if read_count > 0:
            print(f"Success rate: {(read_count/(read_count+error_count)*100):.1f}%")


# Jalankan program
if __name__ == "__main__":
    main()
