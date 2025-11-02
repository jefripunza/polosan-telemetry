## ============================================== ##
# Standard Library
import os
from machine import Pin, I2C, SPI
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
def wifi_sta_connect(ssid, password):
    global wifi_sta_is_online, wifi_sta_ssid_connected, wifi_sta_ip_address
    sta = Station(ssid=ssid, password=password)
    if sta:
        print("Berhasil koneksi ke Wi-Fi:", ssid)
        wifi_sta_is_online = True
        wifi_sta_ssid_connected = ssid
        wifi_sta_ip_address = sta.get_ip()
        print("Station IP:", wifi_sta_ip_address)
    return sta

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

## ============================================== ##
# Setup Router

app = Router()

# ------------------------------------------------ #
# basic

@app.get("/api/ssid-scan")
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

# ------------------------------------------------ #
# auth

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
            buzzer.on()
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
        # worker_show_memory(),
        worker_display(),
        worker_wifi_ap(),
        worker_wifi_station(),
        worker_rtc_sync_time(),
        worker_datetime(),
        worker_i2c(),
        worker_sdcard(),
    )
asyncio.run(main())








