import esp
import gc
import micropython
import machine
import time
import os


#esp.osdebug(None)

# Cek PSRAM (jika tersedia)
try:
    import esp32
    psram_info = esp32.psram_info()
except (ImportError, AttributeError):
    psram_info = None

print("=== ESP32‑S3 SYSTEM INFO ===\n")

# Paksa CPU ke 240 MHz (default untuk ESP32‑S3)
try:
    machine.freq(240_000_000)
    print("force to 240 MHz !!!\n")
except Exception as e:
    print("Tidak bisa set CPU freq ke 240 MHz →", e)

# Flash internal
try:
    flash = esp.flash_size()
    print(f"Flash size: {flash / (1024*1024):.2f} MB")
except Exception as e:
    print("Flash size: Error →", e)

try:
    fs = os.statvfs('/')
    block_size = fs[0]
    total_blocks = fs[2]
    free_blocks = fs[3]
    total_fs = block_size * total_blocks
    free_fs = block_size * free_blocks
    used_fs = total_fs - free_fs

    print("\nFilesystem (Flash) Info:")
    print(f"Total space: {total_fs / (1024*1024):.2f} MB")
    print(f"Used space:  {used_fs / (1024*1024):.2f} MB")
    print(f"Free space:  {free_fs / (1024*1024):.2f} MB\n")
except Exception as e:
    print("Filesystem info unavailable →", e)

# Heap MicroPython (internal & eksternal)
gc.collect()
allocated = gc.mem_alloc()
free = gc.mem_free()
print(f"Heap allocated: {allocated / 1024:.2f} KB")
print(f"Heap free: {free / 1024:.2f} KB")

# PSRAM (jika tersedia)
if psram_info:
    total, free_psram = psram_info
    print(f"\nPSRAM total: {total / (1024*1024):.3f} MB")
    print(f"PSRAM free: {free_psram / (1024*1024):.3f} MB")
else:
    print("\nPSRAM not available or not supported in this firmware.")

# CPU frequency
freq = machine.freq()
print(f"\nCPU Frequency: {freq // 1_000_000} MHz")

# Estimasi performa CPU lewat loop sederhana
print("\nEstimasi performa CPU (loop sederhana):")
N = 100_000
start = time.ticks_ms()
for _ in range(N):
    pass
elapsed = time.ticks_diff(time.ticks_ms(), start)
print(f"Loop {N} iterasi butuh: {elapsed} ms (indikasi performa)")

print("\n=====================================================\n")