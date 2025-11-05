"""
XY-MD02 UNLOCK TOOL
Untuk XY-MD02 yang dalam mode PROTECTED/LOCKED

Device merespon dengan error 0x83 0x02 = READ PROTECTED
Perlu unlock sequence dulu sebelum bisa read/write
"""

from machine import UART, Pin
import time

def crc16_modbus(data):
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
    # Add CRC
    crc = crc16_modbus(command)
    command.append(crc & 0xFF)
    command.append((crc >> 8) & 0xFF)
    
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
    if len(data) < 3:
        return False
    received_crc = data[-2] | (data[-1] << 8)
    calculated_crc = crc16_modbus(data[:-2])
    return received_crc == calculated_crc


def method_1_unlock_password():
    """
    Method 1: Unlock dengan password di register 0x07D2
    Beberapa XY-MD02 memerlukan unlock code dulu
    """
    print("\n" + "="*60)
    print("METHOD 1: UNLOCK dengan PASSWORD")
    print("="*60)
    
    uart = UART(2, baudrate=9600, tx=15, rx=16)
    de_re = Pin(14, Pin.OUT)
    de_re.value(0)
    time.sleep_ms(100)
    
    # Try unlock dengan berbagai password
    passwords = [
        (0x0000, "Default password"),
        (0x0001, "Password 1"),
        (0x0008, "Unlock code 8"),
        (0x5AA5, "Magic unlock"),
        (0xFFFF, "All bits set"),
    ]
    
    for password, desc in passwords:
        print(f"\nTrying: {desc} (0x{password:04X})")
        
        # Write password ke register 0x07D2
        command = bytearray([
            0x01, 0x06, 0x07, 0xD2,
            (password >> 8) & 0xFF,
            password & 0xFF
        ])
        
        response = send_command(uart, de_re, command, 300)
        
        if response and verify_crc(response):
            if response[1] == 0x06:
                print("✓ Unlock command accepted!")
                time.sleep_ms(500)
                
                # Test dengan read
                print("Testing read...")
                test_cmd = bytearray([0x01, 0x03, 0x00, 0x00, 0x00, 0x02])
                test_resp = send_command(uart, de_re, test_cmd, 300)
                
                if test_resp and verify_crc(test_resp):
                    if test_resp[1] == 0x03:
                        print("✓✓✓ SUCCESS! Device unlocked!")
                        return True
        
        time.sleep_ms(200)
    
    return False


def method_2_hardware_jumper():
    """
    Method 2: Instruksi hardware unlock
    XY-MD02 biasanya punya jumper atau pad untuk unlock
    """
    print("\n" + "="*60)
    print("METHOD 2: HARDWARE JUMPER/BUTTON")
    print("="*60)
    print("""
XY-MD02 biasanya memiliki salah satu dari ini:

1. JUMPER JP1 atau J1:
   - Short jumper saat power ON
   - Device akan masuk CONFIG MODE
   - LED akan berkedip berbeda
   
2. BUTTON atau PAD "CFG" atau "SET":
   - Tekan dan tahan saat power ON
   - Tahan 3-5 detik
   - Lepas setelah LED berkedip
   
3. SOLDERABLE PAD:
   - Ada 2 pad berlabel "CFG" atau "MODE"
   - Short dengan kawat/pinset saat power ON
   - Device masuk config mode

CARA:
1. Matikan power XY-MD02
2. Short jumper/tekan button/short pad
3. Nyalakan power (tetap short/tekan)
4. Tunggu 3 detik
5. Lepas jumper/button
6. Jalankan script lagi

Cek PCB XY-MD02 Anda untuk jumper/button ini!
    """)
    
    input("\nTekan Enter setelah melakukan hardware unlock...")
    
    # Test setelah unlock
    uart = UART(2, baudrate=9600, tx=15, rx=16)
    de_re = Pin(14, Pin.OUT)
    de_re.value(0)
    time.sleep_ms(100)
    
    print("\nTesting komunikasi...")
    command = bytearray([0x01, 0x03, 0x00, 0x00, 0x00, 0x02])
    response = send_command(uart, de_re, command, 300)
    
    if response and verify_crc(response):
        if response[1] == 0x03:
            print("✓ Device unlocked via hardware!")
            return True
    
    print("✗ Masih locked atau perlu coba lagi")
    return False


def method_3_broadcast_unlock():
    """
    Method 3: Broadcast unlock
    Beberapa device support broadcast untuk unlock
    """
    print("\n" + "="*60)
    print("METHOD 3: BROADCAST UNLOCK")
    print("="*60)
    print("PERINGATAN: Hanya gunakan jika HANYA 1 device!")
    
    uart = UART(2, baudrate=9600, tx=15, rx=16)
    de_re = Pin(14, Pin.OUT)
    de_re.value(0)
    time.sleep_ms(100)
    
    # Broadcast unlock sequences
    sequences = [
        bytearray([0x00, 0x06, 0x07, 0xD2, 0x00, 0x00]),  # Broadcast password
        bytearray([0x00, 0x06, 0x07, 0xD2, 0x00, 0x08]),  # Broadcast unlock
        bytearray([0x00, 0x10, 0x07, 0xD0, 0x00, 0x03, 0x06, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00]),  # Multi write
    ]
    
    for i, seq in enumerate(sequences, 1):
        print(f"\nBroadcast sequence {i}...")
        send_command(uart, de_re, seq, 100)
        time.sleep(1)
    
    # Test dengan address normal
    print("\nTesting dengan address 0x01...")
    command = bytearray([0x01, 0x03, 0x00, 0x00, 0x00, 0x02])
    response = send_command(uart, de_re, command, 300)
    
    if response and verify_crc(response):
        if response[1] == 0x03:
            print("✓ Device unlocked!")
            return True
    
    return False


def method_4_direct_address_change():
    """
    Method 4: Langsung ubah address tanpa read dulu
    Beberapa device allow write even when read is locked
    """
    print("\n" + "="*60)
    print("METHOD 4: DIRECT ADDRESS WRITE")
    print("="*60)
    print("Mencoba langsung ubah address tanpa read validasi...")
    
    uart = UART(2, baudrate=9600, tx=15, rx=16)
    de_re = Pin(14, Pin.OUT)
    de_re.value(0)
    time.sleep_ms(100)
    
    # Langsung write address ke 0x07D1
    print("\nWriting address 0x02 to register 0x07D1...")
    command = bytearray([0x01, 0x06, 0x07, 0xD1, 0x00, 0x02])
    response = send_command(uart, de_re, command, 300)
    
    if response and verify_crc(response):
        if response[1] == 0x06:
            print("✓ Write accepted!")
            time.sleep(2)
            
            # Test address baru
            print("\nTesting address 0x02...")
            test_cmd = bytearray([0x02, 0x03, 0x00, 0x00, 0x00, 0x02])
            test_resp = send_command(uart, de_re, test_cmd, 300)
            
            if test_resp and verify_crc(test_resp):
                if test_resp[1] == 0x03:
                    print("✓✓✓ SUCCESS! Address changed to 0x02!")
                    
                    # Parse data
                    temp_raw = (test_resp[3] << 8) | test_resp[4]
                    hum_raw = (test_resp[5] << 8) | test_resp[6]
                    temp = temp_raw / 10.0
                    hum = hum_raw / 10.0
                    print(f"Temperature: {temp}°C")
                    print(f"Humidity: {hum}%")
                    return True
        elif response[1] & 0x80:
            error_code = response[2] if len(response) > 2 else 0
            print(f"✗ Error: 0x{error_code:02X}")
    
    return False


def method_5_force_reset():
    """
    Method 5: Force reset to factory defaults
    """
    print("\n" + "="*60)
    print("METHOD 5: FORCE FACTORY RESET")
    print("="*60)
    
    uart = UART(2, baudrate=9600, tx=15, rx=16)
    de_re = Pin(14, Pin.OUT)
    de_re.value(0)
    time.sleep_ms(100)
    
    # Try writing multiple registers at once for reset
    print("\nSending factory reset command...")
    
    # Method A: Write to special reset register
    commands = [
        bytearray([0x01, 0x06, 0x07, 0xD0, 0x00, 0x02]),  # Reset baudrate to 9600
        bytearray([0x01, 0x06, 0x07, 0xD1, 0x00, 0x01]),  # Reset address to 0x01
        bytearray([0x01, 0x06, 0x07, 0xD2, 0x00, 0x00]),  # Reset parity to none
    ]
    
    for cmd in commands:
        send_command(uart, de_re, cmd, 200)
        time.sleep_ms(500)
    
    print("\nPower cycle device (matikan dan nyalakan lagi)!")
    input("Tekan Enter setelah power cycle...")
    
    # Test
    print("\nTesting...")
    test_cmd = bytearray([0x01, 0x03, 0x00, 0x00, 0x00, 0x02])
    response = send_command(uart, de_re, test_cmd, 300)
    
    if response and verify_crc(response):
        if response[1] == 0x03:
            print("✓ Device reset berhasil!")
            return True
    
    return False


def check_device_version():
    """
    Cek versi device - ada beberapa versi XY-MD02
    """
    print("\n" + "="*60)
    print("DEVICE VERSION CHECK")
    print("="*60)
    
    uart = UART(2, baudrate=9600, tx=15, rx=16)
    de_re = Pin(14, Pin.OUT)
    de_re.value(0)
    time.sleep_ms(100)
    
    print("""
Ada beberapa versi XY-MD02:

1. XY-MD02 V1.0 (OLD):
   - Locked by default
   - Perlu hardware jumper untuk unlock
   - Register 0x07D0-0x07D2
   
2. XY-MD02 V2.0 (NEW):
   - Tidak locked by default
   - Direct write support
   - Register sama
   
3. XY-MD02 dengan SHT20:
   - IC SHT20 terlihat di PCB
   - 4-pin connector
   
4. XY-MD02 dengan alternatif sensor:
   - Bisa pakai DHT22 atau lainnya
   - Protokol mungkin sedikit berbeda

CEK PCB ANDA:
- Ada label "V1.0" atau "V2.0"?
- Ada IC SHT20 (kotak kecil 4-pin)?
- Ada jumper atau button kecil?
    """)


def main():
    print("\n" + "="*60)
    print("XY-MD02 UNLOCK TOOL")
    print("="*60)
    print("""
Device Anda merespon dengan error 0x83 0x02
Ini berarti: READ PROTECTED / LOCKED

Error 0x83 = Function 0x03 + 0x80 (error flag)
Exception 0x02 = ILLEGAL DATA ADDRESS atau LOCKED

XY-MD02 memiliki mode proteksi. Mari kita coba unlock!
    """)
    
    input("\nTekan Enter untuk mulai...")
    
    # Check device version first
    check_device_version()
    input("\nTekan Enter untuk lanjut ke unlock methods...")
    
    methods = [
        ("DIRECT ADDRESS WRITE", method_4_direct_address_change),
        ("BROADCAST UNLOCK", method_3_broadcast_unlock),
        ("PASSWORD UNLOCK", method_1_unlock_password),
        ("HARDWARE JUMPER", method_2_hardware_jumper),
        ("FORCE RESET", method_5_force_reset),
    ]
    
    for name, method in methods:
        print("\n" + "="*60)
        print(f"TRYING: {name}")
        print("="*60)
        
        try:
            if method():
                print("\n" + "="*60)
                print(f"✓✓✓ SUCCESS with {name}!")
                print("="*60)
                print("\nDevice is now unlocked and configured!")
                return True
        except Exception as e:
            print(f"Error: {e}")
        
        time.sleep(1)
    
    # Final recommendation
    print("\n" + "="*60)
    print("SEMUA METHOD GAGAL")
    print("="*60)
    print("""
SARAN TERAKHIR:

1. CEK HARDWARE JUMPER di PCB:
   - Cari jumper JP1, J1, atau pad "CFG"
   - Short jumper saat power ON
   - Atau tekan button "SET" saat power ON

2. VERSI XY-MD02:
   - V1.0 = SELALU perlu hardware unlock
   - V2.0 = Biasanya tidak perlu unlock
   
3. FOTO PCB:
   - Ambil foto close-up PCB
   - Cari label versi
   - Cari jumper atau button
   
4. ALTERNATIVE:
   - Beli XY-MD02 versi baru (V2.0)
   - Atau gunakan sensor lain (XY-MD03, DHT22)
   - Atau hubungi seller untuk instruksi unlock

5. POWER CYCLE:
   - Coba matikan device
   - Tunggu 10 detik
   - Nyalakan lagi
   - Test lagi
    """)


if __name__ == "__main__":
    main()
