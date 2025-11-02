# MicroPython zlib module
# MIT license; Copyright (c) 2023 Jim Mussared

import io, deflate
try:
    import binascii
except ImportError:
    binascii = None

_MAX_WBITS = const(15)


def _decode_wbits(wbits, decompress):
    if -15 <= wbits <= -5:
        return (
            deflate.RAW,
            -wbits,
        )
    elif 5 <= wbits <= 15:
        return (deflate.ZLIB, wbits)
    elif decompress and wbits == 0:
        return (deflate.ZLIB,)
    elif 21 <= wbits <= 31:
        return (deflate.GZIP, wbits - 16)
    elif decompress and 35 <= wbits <= 47:
        return (deflate.AUTO, wbits - 32)
    else:
        raise ValueError("wbits")


if hasattr(deflate.DeflateIO, "write"):

    def compress(data, wbits=_MAX_WBITS):
        f = io.BytesIO()
        with deflate.DeflateIO(f, *_decode_wbits(wbits, False)) as g:
            g.write(data)
        return f.getvalue()


def decompress(data, wbits=_MAX_WBITS):
    f = io.BytesIO(data)
    with deflate.DeflateIO(f, *_decode_wbits(wbits, True)) as g:
        return g.read()


def crc32(data, crc=0):
    """Calculate CRC32 checksum of data.
    
    Args:
        data: bytes to calculate CRC32 for
        crc: initial CRC value (default 0)
    
    Returns:
        CRC32 checksum as signed 32-bit integer
    """
    if binascii:
        return binascii.crc32(data, crc)
    else:
        # Fallback implementation if binascii is not available
        crc = crc ^ 0xFFFFFFFF
        for byte in data:
            crc = crc ^ byte
            for _ in range(8):
                if crc & 1:
                    crc = (crc >> 1) ^ 0xEDB88320
                else:
                    crc = crc >> 1
        return crc ^ 0xFFFFFFFF