"""Build CHS_v2.9.0.w3x from the original archive + all 2.9.0 changes.

Replaces 5 files: war3map.j (fixes + Gambler + Kerrigan + betting fix + ver),
war3map.wts, war3mapSkin.txt (version strings), war3map.w3u + war3mapSkin.w3u
(both new heroes). Every other file stays byte-identical to the original.
"""
import os, struct, zlib
from mpyq import MPQArchive

os.chdir(os.path.dirname(os.path.abspath(__file__)))

SRC = 'map.w3x'
OUT = 'CHS_v2.9.0.w3x'
REPLACEMENTS = {
    'war3map.j':        'war3map_290_final.j',
    'war3map.wts':      'new290_war3map.wts',
    'war3map.w3u':      'new290_war3map.w3u',
    'war3mapSkin.w3u':  'new290_war3mapSkin.w3u',
    'war3mapSkin.txt':  'new290_war3mapSkin.txt',
}

a = MPQArchive(SRC, listfile=False)
h = a.header
data = open(SRC, 'rb').read()
ENC = a.encryption_table

def crypt(buf, key, enc):
    seed1 = key & 0xFFFFFFFF
    seed2 = 0xEEEEEEEE
    out = bytearray()
    for i in range(len(buf) // 4):
        seed2 = (seed2 + ENC[0x400 + (seed1 & 0xFF)]) & 0xFFFFFFFF
        word = struct.unpack_from('<I', buf, i * 4)[0]
        if enc:
            plain = word
            out += struct.pack('<I', (plain ^ (seed1 + seed2)) & 0xFFFFFFFF)
        else:
            plain = (word ^ (seed1 + seed2)) & 0xFFFFFFFF
            out += struct.pack('<I', plain)
        seed1 = ((~seed1 << 0x15) + 0x11111111) | (seed1 >> 0x0B)
        seed1 &= 0xFFFFFFFF
        seed2 = (plain + seed2 + (seed2 << 5) + 3) & 0xFFFFFFFF
    return bytes(out)

KEY_BT = a._hash('(block table)', 'TABLE')
ht_off, bt_off = h['hash_table_offset'], h['block_table_offset']
ht_n, bt_n = h['hash_table_entries'], h['block_table_entries']
raw_ht = data[ht_off:ht_off + ht_n * 16]
raw_bt = data[bt_off:bt_off + bt_n * 16]
plain_bt = bytearray(crypt(raw_bt, KEY_BT, False))
assert crypt(bytes(plain_bt), KEY_BT, True) == raw_bt, 'crypto round-trip failed'

out = bytearray(data[:min(ht_off, bt_off)])
for name, path in REPLACEMENTS.items():
    entry = a.get_hash_table_entry(name)
    assert entry is not None, f'{name} missing'
    bi = entry.block_table_index
    off, csize, fsize, flags = struct.unpack_from('<4I', plain_bt, bi * 16)
    assert flags == 0x80000200, f'{name}: flags 0x{flags:08x}'
    content = open(path, 'rb').read()
    comp = zlib.compress(content, 9)
    sector = b'\x02' + comp
    if len(sector) >= len(content):
        sector = content
    blob = struct.pack('<2I', 8, 8 + len(sector)) + sector
    new_off = len(out)
    out += blob
    struct.pack_into('<4I', plain_bt, bi * 16, new_off, len(blob), len(content), flags)
    print(f'{name}: block {bi}, {len(content)} -> {len(blob)} @ {new_off}')

new_ht_off = len(out); out += raw_ht
new_bt_off = len(out); out += crypt(bytes(plain_bt), KEY_BT, True)
struct.pack_into('<I', out, 8, len(out))
struct.pack_into('<I', out, 16, new_ht_off)
struct.pack_into('<I', out, 20, new_bt_off)
open(OUT, 'wb').write(bytes(out))
print(f'wrote {OUT}: {len(out)} bytes')

# ---- verification ----
b = MPQArchive(OUT, listfile=False)
for name, path in REPLACEMENTS.items():
    assert b.read_file(name) == open(path, 'rb').read(), f'{name} mismatch'
print('VERIFY: 5 replaced files re-extract byte-identical')

unchanged = ['war3map.w3i', 'war3map.w3t', 'war3map.w3a', 'war3map.w3b',
             'war3map.w3d', 'war3map.w3h', 'war3map.wtg', 'war3map.wct',
             'war3map.w3r', 'war3map.w3c', 'war3map.doo', 'war3mapUnits.doo',
             'war3map.shd', 'war3map.wpm', 'war3map.w3e', 'war3map.imp',
             'war3mapMisc.txt', 'war3mapExtra.txt', 'war3mapMap.blp',
             'war3mapSkin.w3t', 'war3mapSkin.w3a', 'war3mapSkin.w3h',
             'war3mapSkin.w3b', 'war3mapSkin.w3d', 'Units\\CommandFunc.txt']
ok = 0
for n in unchanged:
    x, y = a.read_file(n), b.read_file(n)
    assert x is not None and x == y, f'{n} changed'
    ok += 1
print(f'VERIFY: {ok} unchanged files byte-identical')

from parse_skin import parse_w3o
for tag, fn in [('gameplay', 'war3map.w3u'), ('skin', 'war3mapSkin.w3u')]:
    open('_t.w3u', 'wb').write(b.read_file(fn))
    _, objs = parse_w3o('_t.w3u', False)
    ids = [o['id'] for o in objs]
    assert 'H0GB' in ids and 'H0KB' in ids, f'{fn} missing a hero'
os.remove('_t.w3u')
js = b.read_file('war3map.j').decode('utf-8')
assert js.count('$48304742') == 16 and js.count('$48304b42') == 20
assert 'SetMapName("CHS_v2.9.0")' in js
assert 'set UB[iet]=2\nelseif IsPlayerInForce(det,rB[iet]) then\nset UB[iet]=1' in js
wts = b.read_file('war3map.wts').decode('utf-8-sig')
skin = b.read_file('war3mapSkin.txt').decode('utf-8')
assert '2.8.7' not in wts and '2.8.6' not in wts and 'CHS_v2.9.0' in wts
assert '2.9.0' in skin and '2.8.7' not in skin
print('VERIFY: both heroes present, betting fix applied, version 2.9.0 everywhere')
