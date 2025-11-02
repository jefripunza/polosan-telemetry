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


class _DecompressObj:
    """Streaming decompressor object for MicroPython ESP32 compatibility.
    
    This is a simplified implementation that accumulates data and 
    decompresses when enough data is available.
    """
    
    def __init__(self, wbits=_MAX_WBITS):
        self.wbits = wbits
        self._buffer = b""
        self._finished = False
        self._decode_args = _decode_wbits(wbits, True)
        self._output_buffer = b""
    
    def decompress(self, data):
        """Decompress a chunk of data.
        
        Args:
            data: bytes to decompress
            
        Returns:
            decompressed bytes (may be empty if more data needed)
        """
        if self._finished:
            return b""
        
        if not data:
            return b""
        
        # Add new data to buffer
        self._buffer += data
        
        # For streaming, we'll try to decompress in larger chunks
        # to avoid the overhead of creating many DeflateIO objects
        if len(self._buffer) < 4096:  # Wait for at least 4KB
            return b""
        
        # Try to decompress accumulated data
        try:
            input_stream = io.BytesIO(self._buffer)
            with deflate.DeflateIO(input_stream, *self._decode_args) as decompressor:
                # Read a reasonable chunk
                chunk = decompressor.read(16384)  # 16KB chunks
                if chunk:
                    # Clear the buffer since we processed it
                    self._buffer = b""
                    return chunk
                else:
                    return b""
        except Exception:
            # If decompression fails, it might be incomplete data
            # Keep accumulating until we have more
            return b""
    
    def flush(self):
        """Flush any remaining decompressed data.
        
        Returns:
            any remaining decompressed bytes
        """
        if self._finished:
            return b""
        
        if not self._buffer:
            self._finished = True
            return b""
        
        try:
            # Final decompression of remaining data
            input_stream = io.BytesIO(self._buffer)
            with deflate.DeflateIO(input_stream, *self._decode_args) as decompressor:
                result = decompressor.read()
                self._buffer = b""
                self._finished = True
                return result if result else b""
        except Exception as e:
            print(f"Flush error: {e}")
            self._finished = True
            return b""


def decompressobj(wbits=_MAX_WBITS):
    """Create a decompressor object for streaming decompression.
    
    Args:
        wbits: window size parameter (same as decompress())
        
    Returns:
        _DecompressObj instance for streaming decompression
    """
    return _DecompressObj(wbits)


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