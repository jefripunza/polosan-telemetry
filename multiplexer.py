from machine import Pin


class Mux:
    def __init__(self, s0=12, s1=13, s2=14, s3=15, sig=16):
        # Pin selector multiplexer (S0 - S3)
        self.s0 = Pin(s0, Pin.OUT)
        self.s1 = Pin(s1, Pin.OUT)
        self.s2 = Pin(s2, Pin.OUT)
        self.s3 = Pin(s3, Pin.OUT)

        # Signal pin (bisa input/output)
        self.sig_pin_num = sig
        self.sig = Pin(sig, Pin.OUT)

    def _set_channel(self, ch: int):
        """Pilih channel multiplexer (0-15)."""
        self.s0.value((ch >> 0) & 1)
        self.s1.value((ch >> 1) & 1)
        self.s2.value((ch >> 2) & 1)
        self.s3.value((ch >> 3) & 1)

    def set(self, channel: int, value: int):
        """Set nilai output multiplexer di channel tertentu."""
        self.sig = Pin(self.sig_pin_num, Pin.OUT)
        self._set_channel(channel)
        self.sig.value(value)

    def get(self, channel: int) -> int:
        """Baca nilai input multiplexer di channel tertentu."""
        self.sig = Pin(self.sig_pin_num, Pin.IN)
        self._set_channel(channel)
        return self.sig.value()
