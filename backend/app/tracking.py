"""1x1 transparent PNG served by the open-tracking endpoint.

Built at import time instead of hardcoding a base64/hex blob, so there's no
risk of a hand-typed constant being subtly corrupt.
"""

import struct
import zlib


def _chunk(chunk_type: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + chunk_type
        + data
        + struct.pack(">I", zlib.crc32(chunk_type + data) & 0xFFFFFFFF)
    )


def _build_transparent_pixel() -> bytes:
    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, 0)  # 1x1, 8-bit RGBA
    raw_scanline = b"\x00" + b"\x00\x00\x00\x00"  # filter byte + transparent RGBA
    idat = zlib.compress(raw_scanline)
    return (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", idat)
        + _chunk(b"IEND", b"")
    )


TRACKING_PIXEL_PNG = _build_transparent_pixel()
