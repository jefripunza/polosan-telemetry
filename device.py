import esp
import gc
import micropython
import machine
import time
import os

device_id = machine.unique_id().hex()

def get_psram():
    try:
        import esp32
        return esp32.psram_info()
    except (ImportError, AttributeError):
        return None

def get_machine_freq():
    return machine.freq() // 1_000_000

def get_storage():
    total_flash = esp.flash_size() / (1024*1024)
    fs = os.statvfs('/')
    block_size = fs[0]
    total_blocks = fs[2]
    free_blocks = fs[3]
    total_fs = (block_size * total_blocks) / (1024*1024)
    free_fs = (block_size * free_blocks) / (1024*1024)
    used_fs = (total_fs - free_fs) / (1024*1024)
    return {
        "total_flash": total_flash,
        "total": total_fs,
        "free": free_fs,
        "used": used_fs,
    }

def get_memory():
    gc.collect()
    allocated = gc.mem_alloc() / 1024
    free = gc.mem_free() / 1024
    return {
        "allocated": allocated,
        "free": free,
    }

def get_speed_ms():
    N = 100_000
    start = time.ticks_ms()
    for _ in range(N):
        pass
    return time.ticks_diff(time.ticks_ms(), start)
