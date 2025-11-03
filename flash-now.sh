esptool erase-flash

esptool --baud 460800 --chip ESP32 erase-flash

esptool --baud 460800 write_flash 0 ESP32_GENERIC_S3-20250911-v1.26.1.bin

esptool --baud 460800 write_flash 0 ESP32_GENERIC_S3-SPIRAM_OCT-20250911-v1.26.1.bin
