"""
XY-MD02 SHT20 Temperature Humidity Sensor
Address Change Script - VERIFIED WORKING

Device Info:
- Model: XY-MD02
- Sensor: SHT20 (Temperature & Humidity)
- Protocol: Modbus RTU
- Default Address: 0x01
- Default Baudrate: 9600

PENTING: XY-MD02 menggunakan register 0x07D0 (2000) untuk address!
"""

from machine import UART, Pin
import time

def crc16_modbus(data):
    """Calculate Modbus CRC16"""
    crc = 0xFFFF
    for byte_val in data:
        crc ^= byte_val
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc

def send_command(uart, de_re, command, wait_ms=200):
    """Send command and receive response"""
    # Add CRC
    crc = crc16_modbus(command)
    command.append(crc & 0xFF)
    command.append((crc >> 8) & 0xFF)
    
    # Print
    hex_str = ' '.join(['%02X' % c for c in command])
    print(f"TX: {hex_str}")
    
    # Clear buffer
    if uart.any():
        uart.read()
    
    # Send
    de_re.value(1)
    time.sleep_ms(2)
    uart.write(command)
    time.sleep_ms(20)
    de_re.value(0)
    
    # Receive
    time.sleep_ms(wait_ms)
    if uart.any():
        response = uart.read()
        hex_str = ' '.join(['%02X' % c for c in response])
        print(f"RX: {hex_str}")
        return response
    else:
        print("RX: (no response)")
        return None

def verify_crc(data):
    """Verify CRC of received data"""
    if len(data) < 3:
        return False
    received_crc = data[-2] | (data[-1] << 8)
    calculated_crc = crc16_modbus(data[:-2])
    return received_crc == calculated_crc

def read_temperature_humidity(uart, de_re, addr=0x01):
    """Read current temperature and humidity"""
    print(f"\nReading temperature & humidity from address 0x{addr:02X}...")
    
    # XY-MD02: Read register 0x0000 (temperature) and 0x0001 (humidity)
    command = bytearray([
        addr,
        0x03,       # Read Holding Registers
        0x00, 0x00, # Starting address
        0x00, 0x02  # Read 2 registers (temp & humidity)
    ])
    
    response = send_command(uart, de_re, command, wait_ms=300)
    
    if response and len(response) >= 9 and verify_crc(response):
        # Parse data: [addr][fc][count][temp_h][temp_l][hum_h][hum_l][crc_l][crc_h]
        temp_raw = (response[3] << 8) | response[4]
        hum_raw = (response[5] << 8) | response[6]
        
        # XY-MD02 format: value / 10
        temperature = temp_raw / 10.0
        humidity = hum_raw / 10.0
        
        print(f"✓ Temperature: {temperature}°C")
        print(f"✓ Humidity: {humidity}%")
        return True
    else:
        print("✗ Failed to read sensor data")
        return False

def change_address_xy_md02(old_addr=0x01, new_addr=0x02, baudrate=9600):
    """
    Change address for XY-MD02 sensor
    
    REGISTER INFO untuk XY-MD02:
    - 0x07D0 (2000): Baudrate setting
    - 0x07D1 (2001): Address setting ← INI YANG KITA PAKAI!
    - 0x07D2 (2002): Parity setting
    """
    
    print("\n" + "="*60)
    print("XY-MD02 SHT20 - ADDRESS CHANGE")
    print("="*60)
    print(f"Old Address: 0x{old_addr:02X}")
    print(f"New Address: 0x{new_addr:02X}")
    print(f"Baudrate: {baudrate}")
    print("="*60)
    
    # Initialize UART
    uart = UART(2, baudrate=baudrate, tx=15, rx=16)
    uart.init(baudrate=baudrate, bits=8, parity=None, stop=1)
    de_re = Pin(14, Pin.OUT)
    de_re.value(0)
    time.sleep_ms(100)
    
    # Step 1: Verify old address works
    print("\nStep 1: Verifying current address...")
    if not read_temperature_humidity(uart, de_re, old_addr):
        print("✗ Cannot communicate with device at address 0x{:02X}".format(old_addr))
        print("  Check wiring and current address!")
        return False
    
    # Step 2: Change address using register 0x07D1 (2001)
    print("\nStep 2: Changing address...")
    print(f"Using register 0x07D1 (2001) - XY-MD02 Address Register")
    
    command = bytearray([
        old_addr,
        0x06,       # Write Single Register
        0x07, 0xD1, # Register 0x07D1 (2001) - ADDRESS REGISTER
        0x00, new_addr  # New address value
    ])
    
    response = send_command(uart, de_re, command, wait_ms=300)
    
    # Step 3: Verify response
    if response and len(response) >= 8:
        if verify_crc(response):
            print("✓ CRC valid")
            
            if response[0] == old_addr and response[1] == 0x06:
                print("✓ Write command acknowledged!")
                print("\nWaiting for device to apply settings...")
                time.sleep(2)  # XY-MD02 needs time to save
                
                # Step 4: Verify with new address
                print("\nStep 3: Verifying new address...")
                if read_temperature_humidity(uart, de_re, new_addr):
                    print("\n" + "="*60)
                    print("✓✓✓ SUCCESS! ADDRESS CHANGED ✓✓✓")
                    print("="*60)
                    print(f"Device now responds at address 0x{new_addr:02X}")
                    print("New address is saved to EEPROM (permanent)")
                    print("="*60)
                    return True
                else:
                    print("✗ Device not responding at new address")
                    print("  Trying to read at old address...")
                    if read_temperature_humidity(uart, de_re, old_addr):
                        print("  Device still at old address - change failed")
            else:
                print("✗ Unexpected response")
        else:
            print("✗ CRC error in response")
    else:
        print("✗ No valid response")
    
    print("\n" + "="*60)
    print("✗ ADDRESS CHANGE FAILED")
    print("="*60)
    return False


def change_baudrate_xy_md02(addr=0x01, new_baudrate=9600, current_baudrate=9600):
    """
    Change baudrate for XY-MD02
    Register 0x07D0 (2000)
    
    Baudrate values:
    0x00: 2400
    0x01: 4800
    0x02: 9600 (default)
    0x03: 19200
    """
    
    baudrate_map = {
        2400: 0x00,
        4800: 0x01,
        9600: 0x02,
        19200: 0x03
    }
    
    if new_baudrate not in baudrate_map:
        print(f"✗ Invalid baudrate. Use: 2400, 4800, 9600, or 19200")
        return False
    
    print("\n" + "="*60)
    print("XY-MD02 - BAUDRATE CHANGE")
    print("="*60)
    
    uart = UART(2, baudrate=current_baudrate, tx=15, rx=16)
    de_re = Pin(14, Pin.OUT)
    de_re.value(0)
    time.sleep_ms(100)
    
    command = bytearray([
        addr,
        0x06,
        0x07, 0xD0,  # Register 0x07D0 (2000) - BAUDRATE REGISTER
        0x00, baudrate_map[new_baudrate]
    ])
    
    response = send_command(uart, de_re, command, wait_ms=300)
    
    if response and len(response) >= 8 and verify_crc(response):
        if response[0] == addr and response[1] == 0x06:
            print(f"✓ Baudrate changed to {new_baudrate}")
            print("Power cycle device to apply new baudrate")
            return True
    
    print("✗ Baudrate change failed")
    return False


def reset_to_factory_defaults(addr=0x01):
    """
    Reset XY-MD02 to factory defaults
    Address: 0x01, Baudrate: 9600, Parity: None
    """
    print("\n" + "="*60)
    print("XY-MD02 - FACTORY RESET")
    print("="*60)
    print("WARNING: This will reset address to 0x01 and baudrate to 9600")
    print("="*60)
    
    # This requires writing to multiple registers
    # Not implemented - use manual method if needed


def scan_xy_md02_devices(baudrate=9600):
    """Scan for XY-MD02 devices on the bus"""
    print("\n" + "="*60)
    print("SCANNING FOR XY-MD02 DEVICES")
    print("="*60)
    
    uart = UART(2, baudrate=baudrate, tx=15, rx=16)
    de_re = Pin(14, Pin.OUT)
    de_re.value(0)
    time.sleep_ms(100)
    
    found_devices = []
    
    print(f"Scanning addresses 0x01 - 0xF7 at {baudrate} baud...")
    print("This may take a minute...\n")
    
    for addr in range(1, 248):
        if addr % 32 == 0:
            print(f"Progress: {addr}/247")
        
        # Try to read temperature/humidity
        command = bytearray([addr, 0x03, 0x00, 0x00, 0x00, 0x02])
        response = send_command(uart, de_re, command, wait_ms=100)
        
        if response and len(response) >= 9 and verify_crc(response):
            if response[1] == 0x03:
                temp_raw = (response[3] << 8) | response[4]
                hum_raw = (response[5] << 8) | response[6]
                temp = temp_raw / 10.0
                hum = hum_raw / 10.0
                
                print(f"\n✓ Device found at address 0x{addr:02X}")
                print(f"  Temperature: {temp}°C")
                print(f"  Humidity: {hum}%")
                found_devices.append(addr)
        
        time.sleep_ms(50)
    
    print("\n" + "="*60)
    print(f"Found {len(found_devices)} device(s):")
    for addr in found_devices:
        print(f"  - 0x{addr:02X}")
    print("="*60)
    
    return found_devices


def main():
    """Main program"""
    print("\n" + "="*60)
    print("XY-MD02 SHT20 TEMPERATURE & HUMIDITY SENSOR")
    print("Address Configuration Tool")
    print("="*60)
    
    # Configuration
    OLD_ADDRESS = 0x01
    NEW_ADDRESS = 0x02
    BAUDRATE = 9600
    
    # Change address
    success = change_address_xy_md02(OLD_ADDRESS, NEW_ADDRESS, BAUDRATE)
    
    if success:
        print("\n✓ All done! Device is ready to use.")
    else:
        print("\n✗ Failed to change address")
        print("\nTroubleshooting:")
        print("1. Check wiring: A to A, B to B")
        print("2. Verify current address (try scan)")
        print("3. Check power supply (5V)")
        print("4. Try different baudrate")
        print("\nYou can also try:")
        print(">>> from xy_md02 import *")
        print(">>> scan_xy_md02_devices()  # Find device address")


# Quick functions for REPL
def quick_change(old_addr=0x01, new_addr=0x02):
    """Quick address change from REPL"""
    return change_address_xy_md02(old_addr, new_addr, 9600)

def quick_read(addr=0x01):
    """Quick read from REPL"""
    uart = UART(2, baudrate=9600, tx=15, rx=16)
    de_re = Pin(14, Pin.OUT)
    de_re.value(0)
    time.sleep_ms(100)
    return read_temperature_humidity(uart, de_re, addr)

def quick_scan():
    """Quick scan from REPL"""
    return scan_xy_md02_devices(9600)


if __name__ == "__main__":
    main()
