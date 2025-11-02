from machine import Pin, I2C, SPI
import network
import uasyncio as asyncio

# custom library
from i2c_lcd import I2cLcd
#
from wiznet5k import WIZNET5K
import wiznet5k_socket as socket
import sma_esp32_w5500_requests as requests
from wifi import AccessPoint, Station
#
from microapi import Router
from multiplexer import Mux
from data_json import DataJSON
from unique import device_id
from zipfile import ZipFile, ZIP_DEFLATED, ZIP_STORED

# pin i2c lcd
lcd_sda = 5
lcd_scl = 6

# pin multiplexer
mux_s0 = 42
mux_s1 = 41
mux_s2 = 40
mux_s3 = 39
mux_sig = 38

# pin lan
lan_rst = 4
lan_cs = 15
lan_miso = 12
lan_mosi = 13
lan_sck = 14

# ======================================================================================== #

# Define the URL to fetch data from
TEXT_URL = 'http://103.56.206.121:8880/hostname'
while True:
    try:
        # Initialize SPI and W5500
        print("prepare lan ...")
        lan_spi = SPI(2, baudrate=20000000, polarity=0, phase=0,
                  sck=Pin(lan_sck), mosi=Pin(lan_mosi), miso=Pin(lan_miso))
        lan_cs = Pin(lan_cs, Pin.OUT)
        lan_rst = Pin(lan_rst)  # Sesuaikan dengan pin reset pada board Anda
        lan = WIZNET5K(lan_spi, lan_cs, lan_rst)
        print("setup done !")
        # Display chip info and network status
        print("Chip Version:", lan.chip)
        print("MAC Address:", [hex(i) for i in lan.mac_address])
        print("My IP address is:", lan.pretty_ip(lan.ip_address))
        while True:
            try:
                print("IP lookup google.com: %s" % lan.pretty_ip(lan.get_host_by_name("google.com")))
                break
            except Exception as e:
                print("lookup Error:", e)
        break
        # # Initialize requests object with socket and Ethernet interface
        # requests.set_socket(socket, nic)
        # # Loop forever
        # i_err = 0
        # while True:
        #     try:
        #         print("Fetching text from", TEXT_URL)
        #         r = requests.get(TEXT_URL)
        #         print('-' * 40)
        #         print(r.text)
        #         print('-' * 40)
        #         r.close()
        #         i_err = 0
        #     except Exception as e:
        #         i_err = i_err + 1
        #         print("fetch Error:", e)
        #         if i_err >= 5:
        #             break
        #     # delay biar tidak terlalu spam server
        #     time.sleep(0.3) # stable on 0.3 (minimal)
    except Exception as e:
        print("Error:", e)



# ====== Multiplexer instance ======
mux = Mux(s0=mux_s0, s1=mux_s1, s2=mux_s2, s3=mux_s3, sig=mux_sig)
# ======================================================================================== #



# ====== KONFIGURASI JSON DB ======
settings_db = DataJSON("settings.json", {
    "wifi:ssid": "Polosan-"+device_id,
    "wifi:pass": "12345678",
    "web:port": 80,
})
settings = settings_db.read()

pin_modes_db = DataJSON("pin_modes.json", {f"C{i}": "out" for i in range(16)})
pin_modes = pin_modes_db.read()

pin_states_db = DataJSON("pin_states.json", {f"C{i}": 0 for i in range(16)})
pin_states = pin_states_db.read()
# ======================================================================================== #



# ====== SETUP ====== #
print("Initializing system...")
if pin_modes and pin_states:
    print("Setting multiplexer according to saved states...")
    for i in range(16):
        pin_key = f"C{i}"
        if pin_modes.get(pin_key) == "out":
            mux.set(i, pin_states.get(pin_key, 0))
print("System initialization complete!")
# ======================================================================================== #


# ====== ZIP EXTRACTION FUNCTION ======
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

# ====== API ======
app = Router()

app.static("/", "/public")  # serve folder public

@app.post("/upload/:id")
async def upload_handler(body, query, params, files):
    print("Query:", query)
    print("Params:", params)
    print("Files:", files)
    file = files.get("file")
    filepath = file.get("path")
    
    # Clear the test directory first
    print("Clearing /public directory...")
    clear_directory("/public")
    
    # Extract ZIP file to temporary location first
    result = extract_zip_file(filepath, "/public")
    
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

@app.get("/ssid-scan")
async def ssid_scan(body, query_params, path_params=None):
    nets = station.scan()
    result = []
    for ssid, bssid, channel, RSSI, authmode, hidden in nets:
        result.append({
            "ssid": ssid.decode(),
            "bssid": ":".join("%02x" % b for b in bssid),
            "channel": channel,
            "rssi": RSSI,
            "authmode": authmode,
            "hidden": hidden,
        })
    return {"data": result}
# ======================================================================================== #


# ====== PIN API ENDPOINTS ======
@app.get("/api/pin/get-states")
async def get_pin_states(body, query_params, path_params=None):
    pin_modes = pin_modes_db.read()
    pin_states = pin_states_db.read()

    if not pin_modes or not pin_states:
        return {"error": "Configuration files not found", "status": 500}

    result = {"message": "OK", "data": {"in": {}, "out": {}}}

    for i in range(16):
        pin_key = f"C{i}"
        mode = pin_modes.get(pin_key, "out")

        if mode == "in":
            value = mux.get(i)   # baca dari hardware
            result["data"]["in"][pin_key] = value
        else:
            value = pin_states.get(pin_key, 0)
            result["data"]["out"][pin_key] = value

    return result


@app.get("/api/pin/set-mode/:pin/:mode")
async def set_pin_mode(body, query_params, path_params):
    try:
        pin_num = int(path_params.get("pin"))
        mode = path_params.get("mode")

        if not (0 <= pin_num <= 15):
            return {"error": "Pin must be 0-15", "status": 400}
        if mode not in ["in", "out"]:
            return {"error": "Mode must be 'in' or 'out'", "status": 400}

        pin_modes = pin_modes_db.read()
        pin_modes[f"C{pin_num}"] = mode
        pin_modes_db.write(pin_modes)

        return {"message": f"Pin C{pin_num} mode set to {mode}", "status": 200}
    except (ValueError, TypeError):
        return {"error": "Invalid pin number", "status": 400}


@app.get("/api/pin/set-state/:pin/:value")
async def set_pin_state(body, query_params, path_params):
    try:
        pin_num = int(path_params.get("pin"))
        pin_value = int(path_params.get("value"))

        if not (0 <= pin_num <= 15):
            return {"error": "Pin must be 0-15", "status": 400}
        if pin_value not in [0, 1]:
            return {"error": "Value must be 0 or 1", "status": 400}

        pin_states = pin_states_db.read()
        pin_states[f"C{pin_num}"] = pin_value
        pin_states_db.write(pin_states)

        mux.set(pin_num, pin_value)

        return {"message": f"Pin C{pin_num} state set to {pin_value}", "status": 200}
    except (ValueError, TypeError):
        return {"error": "Invalid pin number or value", "status": 400}
# ======================================================================================== #



# ====== WIFI STATION ======
async def wifi_station():
    sta = Station(ssid="HERDI", password="ojolalipw")
    if sta:
        print("Station IP:", sta.get_ip())

# ====== LOOP MULTIPLEXER ======
async def mux_loop():
    while True:
        for ch in range(16):
            print("Channel Next:", ch)
            mux.set(ch, 1)
            await asyncio.sleep_ms(300)
            mux.set(ch, 0)
            await asyncio.sleep_ms(200)

        for ch in reversed(range(16)):
            print("Channel Reverse:", ch)
            mux.set(ch, 1)
            await asyncio.sleep_ms(300)
            mux.set(ch, 0)
            await asyncio.sleep_ms(200)

# ====== WEB SERVER ======
async def web_server():
    ap = AccessPoint(essid=settings.get("wifi:ssid"), password=settings.get("wifi:pass"))
    print("SoftAP running at:", ap.get_ip())
    app.listen(80, callback=lambda: print("Server running at http://%s/" % ap.get_ip()))
# ======================================================================================== #

# ====== MAIN ======
async def main():
    await asyncio.gather(
        # wifi_station(),
        # mux_loop(),
        web_server()
    )
asyncio.run(main())
