"""
RS485 Address Scanner for MicroPython
Konfigurasi Pin:
- RST (DE/RE): GPIO 14
- TX2: GPIO 15
- RX2: GPIO 16
"""

from machine import UART, Pin
import time

# Konfigurasi Pin
RST_PIN = 14  # Pin untuk DE/RE (Direction Enable/Receiver Enable)
TX_PIN = 15   # Pin TX untuk RS485
RX_PIN = 16   # Pin RX untuk RS485

# Inisialisasi Pin RST (DE/RE)
rst = Pin(RST_PIN, Pin.OUT)

# Inisialisasi UART2
uart = UART(2, baudrate=9600, tx=TX_PIN, rx=RX_PIN, bits=8, parity=None, stop=1)

def set_transmit_mode():
    """Set RS485 ke mode transmit"""
    rst.value(1)
    time.sleep_ms(1)

def set_receive_mode():
    """Set RS485 ke mode receive"""
    rst.value(0)
    time.sleep_ms(1)

def send_command(address, command):
    """
    Kirim command ke address tertentu
    Sesuaikan format command dengan protokol sensor Anda
    """
    set_transmit_mode()
    
    # Contoh format: [address, command, checksum]
    # Sesuaikan dengan protokol sensor Anda
    data = bytearray([address, command])
    
    # Hitung checksum (contoh sederhana)
    checksum = sum(data) & 0xFF
    data.append(checksum)
    
    uart.write(data)
    time.sleep_ms(10)
    
    set_receive_mode()

def read_response(timeout_ms=1000):
    """Baca response dari RS485"""
    start_time = time.ticks_ms()
    response = bytearray()
    
    while time.ticks_diff(time.ticks_ms(), start_time) < timeout_ms:
        if uart.any():
            response.extend(uart.read())
            time.sleep_ms(10)
    
    return response

def scan_addresses(start_addr=1, end_addr=247, command=0x03):
    """
    Scan address RS485 dari start_addr sampai end_addr
    
    Args:
        start_addr: Address awal (default: 1)
        end_addr: Address akhir (default: 247)
        command: Command untuk query (default: 0x03 - Read Holding Register Modbus)
    
    Returns:
        List of active addresses
    """
    print("=" * 50)
    print("Memulai scan address RS485...")
    print(f"Range: {start_addr} - {end_addr}")
    print("=" * 50)
    
    active_addresses = []
    
    for addr in range(start_addr, end_addr + 1):
        print(f"Scanning address {addr}...", end=" ")
        
        # Clear buffer
        while uart.any():
            uart.read()
        
        # Kirim command
        send_command(addr, command)
        
        # Tunggu response
        response = read_response(timeout_ms=500)
        
        if len(response) > 0:
            hex_response = ' '.join(['{:02X}'.format(b) for b in response])
            print(f"✓ FOUND! Response: {hex_response}")
            active_addresses.append(addr)
        else:
            print("✗ No response")
        
        time.sleep_ms(50)  # Delay antar scan
    
    print("=" * 50)
    print(f"Scan selesai! Ditemukan {len(active_addresses)} device aktif")
    if active_addresses:
        print(f"Address aktif: {active_addresses}")
    print("=" * 50)
    
    return active_addresses

def scan_modbus_addresses(start_addr=1, end_addr=247):
    """
    Scan khusus untuk Modbus RTU
    Menggunakan Function Code 0x03 (Read Holding Registers)
    """
    print("Scanning Modbus RTU addresses...")
    print("Scanning: ", end="")
    
    active_addresses = []
    
    for addr in range(start_addr, end_addr + 1):
        # Show progress
        if addr % 10 == 1:
            print(f"\n[{addr:3d}-{min(addr+9, end_addr):3d}] ", end="")
        
        # Clear buffer
        while uart.any():
            uart.read()
        
        set_transmit_mode()
        
        # Modbus RTU Frame: [Address][Function][Start Hi][Start Lo][Count Hi][Count Lo][CRC Lo][CRC Hi]
        frame = bytearray([addr, 0x03, 0x00, 0x00, 0x00, 0x01])
        
        # Hitung CRC16 Modbus
        crc = calculate_modbus_crc(frame)
        frame.append(crc & 0xFF)
        frame.append((crc >> 8) & 0xFF)
        
        uart.write(frame)
        time.sleep_ms(10)
        
        set_receive_mode()
        
        # Baca response
        response = read_response(timeout_ms=500)
        
        if len(response) >= 5 and response[0] == addr:
            print(f"0x{addr:02X} ", end="")
            active_addresses.append(addr)
        else:
            print(".", end="")
        
        time.sleep_ms(50)
    
    print("\n" + "="*50)
    if active_addresses:
        print(f"Ditemukan {len(active_addresses)} device:")
        hex_addrs = [f"0x{addr:02X}" for addr in active_addresses]
        print(f"  {', '.join(hex_addrs)}")
    else:
        print("Tidak ada device ditemukan")
    print("="*50)
    
    return active_addresses

def calculate_modbus_crc(data):
    """Hitung CRC16 untuk Modbus RTU"""
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

def test_communication(address):
    """Test komunikasi dengan address tertentu"""
    print(f"\nTest komunikasi dengan address {address}...")
    
    for i in range(3):
        print(f"Percobaan {i+1}...")
        send_command(address, 0x03)
        response = read_response()
        
        if response:
            hex_response = ' '.join(['{:02X}'.format(b) for b in response])
            print(f"Response: {hex_response}")
        else:
            print("Tidak ada response")
        
        time.sleep(1)

# Main program
if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("RS485 Address Scanner")
    print("Konfigurasi:")
    print(f"  RST (DE/RE): GPIO {RST_PIN}")
    print(f"  TX: GPIO {TX_PIN}")
    print(f"  RX: GPIO {RX_PIN}")
    print(f"  Baudrate: 9600")
    print("=" * 50 + "\n")
    
    # Set ke receive mode sebagai default
    set_receive_mode()
    
    # Pilih metode scan:
    
    # 1. Scan umum (sesuaikan dengan protokol sensor Anda)
    # active_devices = scan_addresses(start_addr=1, end_addr=20)
    
    # 2. Scan khusus Modbus RTU
    active_devices = scan_modbus_addresses(start_addr=1, end_addr=247)
    
    # Test komunikasi dengan device yang ditemukan
    if active_devices:
        print("\nIngin test komunikasi dengan device pertama? (y/n)")
        # test_communication(active_devices[0])