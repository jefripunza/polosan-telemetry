from machine import Pin, UART
import time
import struct

# === Pin configuration ===
PIN_RST = Pin(14, Pin.OUT)
uart = UART(2, baudrate=9600, tx=15, rx=16, timeout=200)

# === Sensor Configuration ===
MODBUS_ADDR = 0x01  # default XY-MD02 address
FUNC_READ_INPUT_REGS = 0x04

# === CRC16 (Modbus RTU) ===
def modbus_crc(data: bytes) -> bytes:
    crc = 0xFFFF
    for pos in data:
        crc ^= pos
        for _ in range(8):
            if crc & 1:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return struct.pack('<H', crc)  # little-endian order

# === Send Modbus request ===
def modbus_read_input_registers(addr, start_reg, num_regs):
    # Build request (6 bytes)
    request = bytes([
        addr,
        FUNC_READ_INPUT_REGS,
        (start_reg >> 8) & 0xFF,
        start_reg & 0xFF,
        (num_regs >> 8) & 0xFF,
        num_regs & 0xFF
    ])
    request += modbus_crc(request)

    # Debug print
    print("--------------------------------------------------")
    print("Sending (hex):", request.hex())

    uart.write(request)
    time.sleep(0.15)  # give sensor time to respond

    response = uart.read()
    print("Received (raw):", response)

    if not response:
        print("❌ No response from sensor")
        return None
    if len(response) < 5:
        print("⚠️ Response too short:", response)
        return None

    # CRC check
    data = response[:-2]
    crc_received = response[-2:]
    crc_calculated = modbus_crc(data)
    if crc_received != crc_calculated:
        print("⚠️ CRC mismatch: got", crc_received.hex(), "expected", crc_calculated.hex())
        return None

    return response

# === Parse temperature & humidity ===
def parse_xy_md02_response(response: bytes):
    # Format: [Addr][Func][ByteCount][T_hi][T_lo][H_hi][H_lo][CRC_lo][CRC_hi]
    if len(response) < 9:
        return None, None
    raw_temp = (response[3] << 8) | response[4]
    raw_hum = (response[5] << 8) | response[6]
    temperature = raw_temp / 10.0
    humidity = raw_hum / 10.0
    return temperature, humidity

# === Main function ===
def read_sensor():
    print("\nReading XY-MD02 sensor...")
    response = modbus_read_input_registers(MODBUS_ADDR, 0x0001, 0x0002)
    if response:
        t, h = parse_xy_md02_response(response)
        if t is not None:
            print("✅ Temperature: {:.1f} °C | Humidity: {:.1f} %RH".format(t, h))
        else:
            print("⚠️ Failed to parse:", response)
    else:
        print("❌ No valid response.")

# === Initialization ===
def init_sensor():
    print("Resetting XY-MD02...")
    PIN_RST.value(0)
    time.sleep(0.2)
    PIN_RST.value(1)
    time.sleep(2)
    print("Sensor ready.\n")

# === Main Loop ===
init_sensor()

while True:
    read_sensor()
    time.sleep(3)
