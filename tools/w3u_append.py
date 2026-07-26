"""Append a new custom unit to a w3u file (version 3, non-extended), byte-level.

Learns field->vtype from existing entries so serialized types match WC3's
expectations exactly.
"""
import struct

def walk(data):
    """Yield (kind, ...) events; also return structure info."""
    pos = 4
    vtypes = {}
    counts = []
    for table in range(2):
        n = struct.unpack_from('<i', data, pos)[0]
        counts.append((pos, n))
        pos += 4
        for _ in range(n):
            pos += 8  # oldid newid
            ec = struct.unpack_from('<i', data, pos)[0]; pos += 4
            pos += 4 * ec
            mc = struct.unpack_from('<i', data, pos)[0]; pos += 4
            for _ in range(mc):
                fid = data[pos:pos+4]; pos += 4
                vt = struct.unpack_from('<i', data, pos)[0]; pos += 4
                vtypes[fid] = vt
                if vt in (0, 1, 2):
                    pos += 4
                else:
                    pos = data.index(b'\x00', pos) + 1
                pos += 4  # trailing id
    return vtypes, counts, pos

def serialize_mod(fid, value, vtypes):
    fidb = fid.encode('latin1')
    if isinstance(value, str):
        vt = 3
        payload = value.encode('utf-8') + b'\x00'
    elif isinstance(value, float):
        vt = vtypes.get(fidb, 1)
        if vt not in (1, 2):
            vt = 1
        payload = struct.pack('<f', value)
    else:
        vt = vtypes.get(fidb, 0)
        if vt == 0:
            payload = struct.pack('<i', int(value))
        else:  # field is typed real in WC3 even if we passed int
            payload = struct.pack('<f', float(value))
    return fidb + struct.pack('<i', vt) + payload + b'\x00\x00\x00\x00'

def append_unit(data, base, newid, mods):
    vtypes, counts, end = walk(data)
    assert end == len(data), f'walk mismatch: {end} vs {len(data)}'
    custom_count_off, custom_n = counts[1]
    obj = base.encode('latin1') + newid.encode('latin1')
    obj += struct.pack('<i', 1) + struct.pack('<i', 0)   # 1 set, flag 0
    obj += struct.pack('<i', len(mods))
    for fid, val in mods:
        obj += serialize_mod(fid, val, vtypes)
    out = bytearray(data)
    struct.pack_into('<i', out, custom_count_off, custom_n + 1)
    out += obj
    return bytes(out)
