import time
import ntptime
from convert import first_zero

def sync_time_and_set_rtc(rtc, utc_offset_hours=7):
    # sinkronkan waktu dari NTP
    try:
        ntptime.settime()
        print("NTP time synced")
    except Exception as e:
        print("Failed to sync NTP time:", e)
        return False

    # ambil waktu lokal (dengan offset UTC)
    t = time.localtime(time.time() + utc_offset_hours * 3600)
    print("online dt:", t)
    # t = (year, month, mday, hour, minute, second, weekday, yearday)
    year, month, mday, hour, minute, second, weekday, yearday = t

    # set ke RTC – jika RTC internal di MicroPython:
    rtc.datetime((year, month, mday, hour, minute, second, weekday, 0))
    print("RTC set to:", rtc.datetime())
    return True
def set_datetime(rtc, year, month, mday, hour, minute, second, weekday):
    datetime = (year, month, mday, hour, minute, second, weekday)
    rtc.datetime(datetime)
def get_datetime(rtc):
    y, mo, d, wk, h, mi, s, _ = rtc.datetime()
    return {
        "year": y,
        "month": mo,
        "day": d,
        "hour": h,
        "minute": mi,
        "second": s,
        "week": wk,
        "date": first_zero(y) + "-" + first_zero(mo) + "-" + first_zero(d),
        "date_compact": first_zero(y) + first_zero(mo) + first_zero(d),
        "time": first_zero(h) + ":" + first_zero(mi) + ":" + first_zero(s),
    }