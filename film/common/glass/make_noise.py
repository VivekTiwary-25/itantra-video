"""Rebuild the deterministic, tileable 256x256 grain tile (stdlib only)."""
from pathlib import Path
import random
import struct
import zlib

SIZE = 256
rng = random.Random(777)
rows = []
for y in range(SIZE):
    row = bytearray([0])
    for x in range(SIZE):
        value = rng.randrange(0, 256)
        row.extend((value, value, value, 255))
    rows.append(bytes(row))

def chunk(kind, payload):
    return struct.pack('!I', len(payload)) + kind + payload + struct.pack('!I', zlib.crc32(kind + payload) & 0xffffffff)

png = bytearray(b'\x89PNG\r\n\x1a\n')
png.extend(chunk(b'IHDR', struct.pack('!2I5B', SIZE, SIZE, 8, 6, 0, 0, 0)))
png.extend(chunk(b'IDAT', zlib.compress(b''.join(rows), 9)))
png.extend(chunk(b'IEND', b''))
Path(__file__).with_name('noise.png').write_bytes(png)
