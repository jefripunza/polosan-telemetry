## ============================================== ##
# Standard Library
import os
import json
from machine import Pin, I2C, SPI, UART
import uasyncio as asyncio

## ============================================== ##
# External Library

from device import device_id, get_storage, get_memory
from wifi import AccessPoint, Station
from microapi import Router
from data_json import DataJSON
from rtc import sync_time_and_set_rtc, set_datetime, get_datetime

from global_variable import  wifi_ap_is_ready, wifi_ap_ip_address, wifi_sta_is_online, \
                             wifi_sta_ssid_connected, wifi_sta_ip_address, \
                             rtc_is_sync_online_time, \
                             datetime, \
                             data_value

from i2c_lcd import I2cLcd
from ds3231 import DS3231
from sdcard import SDCard

## ============================================== ##
# Konfigurasi JSON Database

#wifi-rumah
# SSID = "HERDI"
# PASSWORD = "ojolalipw"
#tablet-jefri
# SSID = "Tab A9+ milik Jefri"
# PASSWORD = "wonkndeso"

db_json = DataJSON("db.json", {
    # tidak boleh berubah ketika import
    "device:id": "",
    "device:name": "",
    "integration:mode": "", # webhook, mqtt, lora
    "wifi:ssid": "Polosan-"+device_id,
    "wifi:pass": "12345678",
    "web:port": 80,
    "web:password": "12345678",

    # boleh berubah ketika import
    "wifi:station": [
#         {
#             "ssid": "HERDI",
#             "pass": "ojolalipw",
#             "is_selected": True,
#         },
    ],
    "webhook:url": "",
    "webhook:apikey": "",
    "log:interval": 1, # second
    "uart:baudrate": 115200, # default: 115200
    "uart:callback_url": "",
    "board:analog": {},  # 1, 2
    "board:digital": {}, # 21, 38, 47
    "module:rs485": [],
    "module:lora": [],
    "module:adc": {}, # Analog-to-Digital Converter (ADC): A1, A2, A3
})
db = db_json.read()

with open("session.json", "w") as f:
    f.write(json.dumps([]))


## ============================================== ##
# Setup Pin (khurslabs)
#
pin_sda = 8
pin_scl = 9
#
pin_spi_miso = 13
pin_spi_mosi = 11
pin_spi_sck  = 12

## I2C Address List
# ADS1115 (0x48)
# DS3231 (0x68)
# LCD-16x2 (0x27)

# Buzzer (OK)
pin_buzzer = 4

# RS485 (?)
pin_rs485_rst = 14
pin_rs485_tx2 = 15
pin_rs485_rx2 = 16

# LoRa (x)
pin_lora_miso = pin_spi_miso
pin_lora_mosi = pin_spi_mosi
pin_lora_sck  = pin_spi_sck
pin_lora_ss   = 10
pin_lora_rst  = 41
pin_lora_dio0 = 42

# SD Card (OK, only format FAT32)
pin_sdcard_miso = pin_spi_miso
pin_sdcard_mosi = pin_spi_mosi
pin_sdcard_sck  = pin_spi_sck
pin_sdcard_ss   = 40

# RTC (OK)
pin_rtc_sda = pin_sda
pin_rtc_scl = pin_scl

# LCD DWIN (x)
pin_lcd_dwin_a = 18
pin_lcd_dwin_b = 17

# LCD 16x2 (OK)
LCD_ADDR = 0x27
LCD_ROWS = 2
LCD_COLS = 16


## ============================================== ##
# Setup Variable

# Buzzer
buzzer = Pin(pin_buzzer, Pin.OUT)
buzzer.off()

# I2C
i2c = I2C(0, scl=Pin(pin_scl), sda=Pin(pin_sda), freq=400000)
i2c_lists = []

# LCD 16x2
lcd = I2cLcd(i2c, LCD_ADDR, LCD_ROWS, LCD_COLS)
lcd.clear()
lcd.backlight_on()

# RTC
rtc = DS3231(i2c)

# SD Card
sdcard_spi = SPI(1, # Anda bisa pilih SPI bus yang tersedia, misalnya SPI(1)
    baudrate=5_000_000,
    polarity=0,
    phase=0,
    sck=Pin(pin_sdcard_sck),
    mosi=Pin(pin_sdcard_mosi),
    miso=Pin(pin_sdcard_miso),
)
sdcard_cs = Pin(pin_sdcard_ss, Pin.OUT)

## ============================================== ##
# Setup Special Function

# LCD 16x2
def display_render(row, col_start, text):
    # reset
    lcd.move_to(0, row)
    lcd.putstr("                ")
    # render
    lcd.move_to(col_start, row)
    lcd.putstr(text)

# WiFi Station
station = None
def wifi_sta_connect(ssid, password):
    global wifi_sta_is_online, wifi_sta_ssid_connected, wifi_sta_ip_address
    global station
    station = Station(ssid=ssid, password=password)
    if station:
        print("Berhasil koneksi ke Wi-Fi:", ssid)
        wifi_sta_is_online = True
        wifi_sta_ssid_connected = ssid
        wifi_sta_ip_address = station.get_ip()
        print("Station IP:", wifi_sta_ip_address)
    return station

# Log
last_date = ""
def write_log(value):
    global last_date
    if not datetime:
        return
    filename = datetime["date"]
    if last_date != filename:
        print(f"Write to file {filename}.txt")
    with open(f"/sd/{filename}.txt", "a") as f:
        f.seek(0, 2)  # 2 = os.SEEK_END → ke akhir file
        f.write(f"{value}\n")
        last_date = filename
def read_log(filename):
    try:
        with open(f"/sd/{filename}.txt", "r") as f:
            return f.read()
    except Exception as e:
        print("Error during SD-card read:", e)

# Session
def set_session(session_string):
    # Read existing sessions
    try:
        with open("session.json", "r") as f:
            sessions = json.load(f)
    except:
        sessions = []
    # Append new session if not already exists
    if session_string not in sessions:
        sessions.append(session_string)
        with open("session.json", "w") as f:
            json.dump(sessions, f)
def get_session(session_string):
    try:
        with open("session.json", "r") as f:
            sessions = json.load(f)
            return session_string in sessions
    except Exception as e:
        print("Error during session read:", e)
        return False

def random_string(length):
    import urandom
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    return "".join(chars[urandom.getrandbits(6) % len(chars)] for _ in range(length))

def extract_zip_file(zip_filepath, extract_to_path):
    """
    Extract ZIP file to specified directory with MicroPython compatibility.
    
    Args:
        zip_filepath (str): Path to the ZIP file
        extract_to_path (str): Directory to extract files to
    
    Returns:
        dict: Result with success status and extracted files list
    """
    print(f'Extracting ZIP file {zip_filepath} to {extract_to_path}...')
    extracted_files = []
    
    try:
        with ZipFile(zip_filepath, "r") as myzip:
            for filename in myzip.namelist():
                # Skip directories (they end with /)
                if filename.endswith('/'):
                    continue
                    
                # Create target path manually
                target_path = extract_to_path + "/" + filename
                
                # Create directory structure if needed
                if '/' in filename:
                    dir_path = extract_to_path + "/" + filename.rsplit('/', 1)[0]
                    try:
                        # Create directories recursively
                        parts = dir_path.split('/')
                        current_path = ""
                        for part in parts:
                            if part:  # Skip empty parts
                                current_path += "/" + part
                                try:
                                    import os
                                    os.mkdir(current_path)
                                except OSError:
                                    pass  # Directory might already exist
                    except Exception as e:
                        print(f"Error creating directory: {e}")
                
                # Get file info to check compression type
                info = myzip.getinfo(filename)
                print(f"Processing {filename} - compression type: {info.compress_type}")
                
                # Extract the file based on compression type
                try:
                    if info.compress_type == 0:  # ZIP_STORED (no compression)
                        print(f"File {filename} is stored (no compression)")
                        # For uncompressed files, try direct read
                        with myzip.open(filename, 'r') as zf:
                            content = zf.read()
                            with open(target_path, 'wb') as target:
                                target.write(content)
                        print(f"Extracted (stored): {filename}")
                        extracted_files.append(filename)
                    else:
                        print(f"File {filename} is compressed (type: {info.compress_type})")
                        
                        if info.compress_type == 8:  # ZIP_DEFLATED
                            print("Attempting manual DEFLATE decompression...")
                            try:
                                # Try to read raw compressed data and decompress manually
                                import zlib
                                
                                # Get the raw file data from the ZIP
                                myzip.fp.seek(info.header_offset)
                                # Skip the local file header
                                local_header = myzip.fp.read(30)  # Basic header size
                                filename_len = int.from_bytes(local_header[26:28], 'little')
                                extra_len = int.from_bytes(local_header[28:30], 'little')
                                myzip.fp.seek(info.header_offset + 30 + filename_len + extra_len)
                                
                                # Read the compressed data
                                compressed_data = myzip.fp.read(info.compress_size)
                                print(f"Read {len(compressed_data)} bytes of compressed data")
                                
                                # Decompress using zlib with raw deflate
                                try:
                                    decompressed = zlib.decompress(compressed_data, -15)  # -15 for raw deflate
                                    print(f"Decompressed to {len(decompressed)} bytes")
                                    
                                    with open(target_path, 'wb') as target:
                                        target.write(decompressed)
                                    print(f"Extracted (manual deflate): {filename}")
                                    extracted_files.append(filename)
                                except Exception as e3:
                                    print(f"Manual decompression failed: {e3}")
                                    # Last resort: try to extract whatever we can
                                    with open(target_path, 'wb') as target:
                                        target.write(compressed_data)  # Write compressed data as-is
                                    print(f"Wrote compressed data as-is: {filename}")
                                    
                            except Exception as e2:
                                print(f"Manual extraction failed: {e2}")
                        else:
                            # For other compression types, try the normal methods
                            try:
                                content = myzip.read(filename)
                                with open(target_path, 'wb') as target:
                                    target.write(content)
                                print(f"Extracted (other compression): {filename}")
                                extracted_files.append(filename)
                            except Exception as e1:
                                print(f"Other compression extraction failed: {e1}")
                                        
                except Exception as e:
                    print(f"All extraction methods failed for {filename}: {e}")
        
        print('ZIP extraction completed!')
        return {"success": True, "extracted_files": extracted_files}
        
    except Exception as e:
        print(f"ZIP extraction error: {e}")
        return {"success": False, "error": str(e), "extracted_files": extracted_files}

def clear_directory(directory_path):
    """Clear all files and subdirectories from a directory."""
    import os
    try:
        for item in os.listdir(directory_path):
            item_path = directory_path + "/" + item
            try:
                # Try to remove as file first
                os.remove(item_path)
                print(f"Removed file: {item_path}")
            except OSError:
                # If it's a directory, remove recursively
                try:
                    clear_directory(item_path)
                    os.rmdir(item_path)
                    print(f"Removed directory: {item_path}")
                except OSError as e:
                    print(f"Could not remove {item_path}: {e}")
    except OSError as e:
        print(f"Error clearing directory {directory_path}: {e}")

## ============================================== ##
# Setup Router

app = Router()

app.static("/", "/web")  # serve folder web

# ------------------------------------------------ #
# basic

# @app.get("/")
# async def root(body, query, params):
#     return {"message": "OK"}

@app.post("/upload/:id")
async def upload_handler(body, query, params, files):
    print("Query:", query)
    print("Params:", params)
    print("Files:", files)
    file = files.get("file")
    filepath = file.get("path")
    
    # Clear the test directory first
    print("Clearing /web directory...")
    clear_directory("/web")
    
    # Extract ZIP file to temporary location first
    result = extract_zip_file(filepath, "/web")
    
    if result["success"]:
        return {
            "ok": True, 
            "message": "ZIP file extracted successfully",
            "extracted_files": result["extracted_files"]
        }
    else:
        return {
            "ok": False, 
            "error": result["error"],
            "extracted_files": result["extracted_files"]
        }

# ------------------------------------------------ #
# auth

@app.post("/api/auth/login")
async def auth_login(body, query, params):
    if not body or not body.get("password"):
        return {"message": "Password required", "status": 400}
    
    web_password = db.get("web:password")
    if body.get("password") == web_password:
        # Generate random token 13 characters
        token = random_string(13)
        
        # Save token to session
        set_session(token)
        
        return {
            "message": "Login successful",
            "token": token,
            "status": 200
        }
    
    return {"message": "Invalid password", "status": 401}

def middleware_use_token(query):
    token = query.get("token")
    if not token:
        return {"message": "Token required", "status": 400}
    if not get_session(token):
        return {"message": "Invalid token", "status": 401}
    return None

@app.get("/api/auth/token-validate")
async def auth_token_validate(body, query, params):
    result = middleware_use_token(query)
    if result: return result
    return {"message": "Token valid", "status": 200}

@app.delete("/api/auth/logout")
async def auth_logout(body, query, params):
    result = middleware_use_token(query)
    if result: return result

    # Get token from query parameters
    token = query.get("token")
    
    # Remove token from session
    try:
        with open("session.json", "r") as f:
            sessions = json.load(f)
        
        if token in sessions:
            sessions.remove(token)
            with open("session.json", "w") as f:
                json.dump(sessions, f)
            
            return {"message": "Logout successful", "status": 200}
    except Exception as e:
        print("Error during logout:", e)
    
    return {"message": "Logout failed", "status": 500}

# ------------------------------------------------ #
# wifi

@app.get("/api/wifi/list")
async def wifi_list(body, query, params):
    result = middleware_use_token(query)
    if result: return result

    global station, wifi_sta_ssid_connected
    nets = station.scan()
    availables = []
    for ssid, bssid, channel, RSSI, authmode, hidden in nets:
        availables.append({
            "ssid": ssid.decode(),
            "bssid": ":".join("%02x" % b for b in bssid),
            "channel": channel,
            "rssi": RSSI,
            "authmode": authmode,
            "hidden": hidden,
        })
    saveds = db.get("wifi:station", [])
    return {"data": {
        "availables": availables,
        "saveds": saveds,
        "ssid_connnected": wifi_sta_ssid_connected, # untuk hide list yang sudah terhubung
    }}

# ------------------------------------------------ #

@app.get("/*")
async def spa_fallback(body, query, params):
    # Serve index.html for SPA routing (React Router)
    with open("web/index.html", "rb") as f:
        content = f.read()
    return content, 200, "text/html"

# ------------------------------------------------ #

## ============================================== ##
# Setup Threading (Worker)



async def worker_show_memory():
    while True:
        storage = get_storage()
        memory = get_memory()
        print("storage:", storage)
        print("memory:", memory)
        await asyncio.sleep(1)



async def worker_display():
    global wifi_ap_is_ready, wifi_ap_ip_address
    global wifi_sta_ssid_connected, wifi_sta_ip_address

    is_booting = True
    section = 0
    next_section_count = 10
    while True:
        if is_booting:
            # buzzer.on()
            display_render(0, 0, "Welcome to ...")
            display_render(1, 0, "Polosan Scada")
            await asyncio.sleep(3)
            is_booting = False
        else:
            if section == 0: # date n time
                i = 0
                while True:
                    if i == next_section_count:
                        section = section+1
                        break
                    i = i+1
                    display_render(0, 0, "Date: "+datetime["date"])
                    display_render(1, 0, "Time: "+datetime["time"])
                    await asyncio.sleep(1)
            if section == 1: # wifi ap
                i = 0
                while True:
                    if i == next_section_count:
                        section = section+1
                        break
                    i = i+1
                    status = "Setup"
                    if wifi_ap_is_ready:
                        status = "Ready"
                    display_render(0, 0, "AP: "+status)
                    display_render(1, 0, wifi_ap_ip_address)
                    await asyncio.sleep(1)
            if section == 2: # wifi sta
                i = 0
                while True:
                    if i == next_section_count:
                        section = section+1
                        break
                    i = i+1
                    status = "Waiting"
                    if wifi_sta_ssid_connected:
                        status = "Connected"
                    display_render(0, 0, "STA: "+status)
                    display_render(1, 0, wifi_sta_ip_address)
                    await asyncio.sleep(1)
#             if section == 3: # show all values
#                 i = 0
#                 while True:
#                     if i == next_section_count:
#                         section = section+1
#                         break
#                     i = i+1
#                     ##
#                     ##
#                     await asyncio.sleep(1)
#             if section == 4: # log stats
#                 i = 0
#                 while True:
#                     if i == next_section_count:
#                         section = section+1
#                         break
#                     i = i+1
#                     ##
#                     ##
#                     await asyncio.sleep(1)
            else:
                display_render(0, 0, "Polosan Scada")
                display_render(1, 0, "it's the best!")
                await asyncio.sleep(5)
                section = 0
                
        await asyncio.sleep(0.1)



async def worker_wifi_ap():
    global wifi_ap_is_ready, wifi_ap_ip_address
    ap = AccessPoint(essid=db.get("wifi:ssid"), password=db.get("wifi:pass"))
    wifi_ap_ip_address = ap.get_ip()
    wifi_ap_is_ready = True
    print("SoftAP running at:", wifi_ap_ip_address)
    web_port = db.get("web:port", 80)
    app.listen(web_port, callback=lambda: print("Server running at http://%s/" % wifi_ap_ip_address))



async def worker_wifi_station():
    is_first_selected = True
    is_connected = False
    while True:
        stations = db.get("wifi:station", [])
        if is_first_selected:
            is_first_selected = False
            for station in stations:
                if station.get("is_selected") is True:
                    if wifi_sta_connect(station.get("ssid"), station.get("pass")):
                        is_connected = True
                        break
        else:
            for station in stations:
                if wifi_sta_connect(station.get("ssid"), station.get("pass")):
                    is_connected = True
                    break
        if is_connected:
            break
        await asyncio.sleep(0.1)



async def worker_rtc_sync_time():
    global wifi_sta_is_online, rtc_is_sync_online_time
    i = 0
    buzzer_is_off = False
    while True:
        print(f"NTP (i): {i}")
        i = i+1
        is_online = wifi_sta_is_online == True # sumber bisa dari mana saja online nya
        if is_online == True:
            if buzzer_is_off == False:
                buzzer.off()
                buzzer_is_off = True
        if is_online == True:
            if rtc_is_sync_online_time == False:
                if sync_time_and_set_rtc(rtc, utc_offset_hours=7):  # contoh UTC+7 untuk Indonesia
                    print("Waktu berhasil diset ke RTC.")
                    break
                else:
                    print("Gagal sinkronisasi waktu.")
        await asyncio.sleep(1)



async def worker_datetime():
    global datetime, rtc
    while True:
        datetime = get_datetime(rtc)
#         print(datetime["date"], datetime["time"], datetime["week"])
        await asyncio.sleep(1)  # jeda 1 detik



async def worker_i2c():
    global i2c_lists
    length = 0
    while True:
        devices = i2c.scan()
        if devices:
            i2c_lists = [hex(d) for d in devices]
            if length == 0:
                print("Found I2C device(s):", i2c_lists)
            length = len(i2c_lists)
        else:
            print("No I2C device found")
        await asyncio.sleep(1)



async def worker_sdcard():
    mounted = False
    sd = None
    vfs = None

    while True:
        if not mounted:
            # coba mount
            try:
                print("Attempting to mount SD card…")
                sd = SDCard(sdcard_spi, sdcard_cs)
                vfs = os.VfsFat(sd)
                os.mount(vfs, "/sd")
                print("Mounted /sd — isi direktori:", os.listdir("/sd"))
                mounted = True
            except Exception as e:
                print("Error mounting SD card:", e)
                mounted = False
                # tunggu dulu sebelum coba ulang
                await asyncio.sleep(1)
                continue  # ke loop selanjutnya
        # jika sudah mounted, jalankan penulisan
        try:
            log_interval = db.get("log:interval", 1)
            write_log("Hello SD card from ESP32-S3")
            await asyncio.sleep(log_interval)
        except Exception as e:
            print("Error during SD-card write:", e)
            # bisa ada indikasi bahwa SD card dilepas → lakukan unmount & reset status
            try:
                os.umount("/sd")
            except:
                pass
            mounted = False
            # minta spi bus di-deinit atau reset jika perlu (bergantung library)
            # lalu loop akan ulang mencoba mount
            await asyncio.sleep(0.1)



async def worker_webhook():
    global datetime
    while True:
        await asyncio.sleep(0.1)



async def worker_rs485():
    while True:
        await asyncio.sleep(0.1)



async def worker_uart():
    while True:
        await asyncio.sleep(0.1)

## ============================================== ##
# Main

async def main():
    await asyncio.gather(
        worker_show_memory(),
        # worker_display(),
        worker_wifi_ap(),
        worker_wifi_station(),
        worker_rtc_sync_time(),
        worker_datetime(),
        worker_i2c(),
        worker_sdcard(),
    )
asyncio.run(main())











