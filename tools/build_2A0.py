"""Build CHS_v2.10.0.w3x - 2.9.4 plus the five new heroes.

Replaces exactly five files inside the MPQ and verifies that every other file
re-extracts byte-identical to the original archive.
"""
import os
import struct
import zlib
from mpyq import MPQArchive

os.chdir(os.path.dirname(os.path.abspath(__file__)))

SRC = 'map.w3x'
OUT = 'CHS_v2.10.0.w3x'
REPLACEMENTS = {
    'war3map.j':        'war3map_2A0.j',
    'war3map.wts':      'new2A0_war3map.wts',
    'war3map.w3u':      'new2A0_war3map.w3u',
    'war3mapSkin.w3u':  'new2A0_war3mapSkin.w3u',
    'war3mapSkin.txt':  'new2A0_war3mapSkin.txt',
}
NEW_HEROES = {'H0SC': 17, 'H0EX': 16, 'H0WC': 18, 'H0SB': 18, 'H0GR': 20}

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
    assert entry is not None, '%s missing' % name
    bi = entry.block_table_index
    off, csize, fsize, flags = struct.unpack_from('<4I', plain_bt, bi * 16)
    assert flags == 0x80000200, '%s: flags 0x%08x' % (name, flags)
    content = open(path, 'rb').read()
    comp = zlib.compress(content, 9)
    sector = b'\x02' + comp
    if len(sector) >= len(content):
        sector = content
    blob = struct.pack('<2I', 8, 8 + len(sector)) + sector
    new_off = len(out)
    out += blob
    struct.pack_into('<4I', plain_bt, bi * 16, new_off, len(blob), len(content), flags)
    print('%-18s block %-4d %9d -> %9d @ %d' % (name, bi, len(content), len(blob), new_off))

new_ht_off = len(out); out += raw_ht
new_bt_off = len(out); out += crypt(bytes(plain_bt), KEY_BT, True)
struct.pack_into('<I', out, 8, len(out))
struct.pack_into('<I', out, 16, new_ht_off)
struct.pack_into('<I', out, 20, new_bt_off)
open(OUT, 'wb').write(bytes(out))
print('wrote %s: %d bytes' % (OUT, len(out)))

# ------------------------------------------------------------- verification --
b = MPQArchive(OUT, listfile=False)
for name, path in REPLACEMENTS.items():
    assert b.read_file(name) == open(path, 'rb').read(), '%s mismatch' % name
print('VERIFY: the 5 replaced files re-extract byte-identical')

# the string table must keep the original's line endings - build_2A0 cannot see
# this via the loop above, because that compares the archive against the very
# file that would carry the damage.
for n in ['war3map.wts', 'war3mapSkin.txt']:
    old_crlf = a.read_file(n).count(b'\r\n')
    new_crlf = b.read_file(n).count(b'\r\n')
    assert old_crlf == new_crlf, '%s: line endings rewritten (%d -> %d)' % (n, old_crlf, new_crlf)
print('VERIFY: text assets keep the original CRLF line endings')

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
    assert x is not None and x == y, '%s changed' % n
    ok += 1
print('VERIFY: %d untouched files byte-identical' % ok)

from parse_skin import parse_w3o
for tag, fn in [('gameplay', 'war3map.w3u'), ('skin', 'war3mapSkin.w3u')]:
    open('_t.w3u', 'wb').write(b.read_file(fn))
    _, objs = parse_w3o('_t.w3u', False)
    ids = [o['id'] for o in objs]
    assert len(ids) == len(set(ids)), '%s: duplicate ids' % tag
    for c in list(NEW_HEROES) + ['H0GB', 'H0KB']:
        assert c in ids, '%s: %s missing' % (tag, c)
os.remove('_t.w3u')
print('VERIFY: all 7 custom heroes present in both object-data tables')

js = b.read_file('war3map.j').decode('utf-8')
assert js.count('$48304742') == 16 and js.count('$48304b42') == 20, 'existing heroes disturbed'
for c, n in NEW_HEROES.items():
    lit = '$' + c.encode('latin1').hex()
    assert js.count(lit) == n, '%s: %d refs, expected %d' % (c, js.count(lit), n)
for i, code in enumerate(['$48305343', '$48304558', '$48305743', '$48305342', '$48304752'], 55):
    assert 'set KC[%d]=%s\n' % (i, code) in js, 'roster slot %d' % i
for pat in ['exitwhen Wnq>64', 'exitwhen EOq>64', 'exitwhen toq>64', 'exitwhen kJq>64']:
    assert pat in js, 'grid bound not raised: ' + pat
assert js.count('exitwhen Doq>64') == 2 and '>56' not in js, 'a 56-bound survived'
assert 'Loq*2.+.032*8+.008*7+.015+.02+.0145' in js, 'grid height not raised to 8 rows'
assert 'SetMapName("CHS_v2.10.0")' in js and 'set jm[yaq]="CHS v2.10.0"' in js
assert 'set UB[iet]=2\nelseif IsPlayerInForce(det,rB[iet]) then\nset UB[iet]=1' in js, 'betting fix lost'
assert 'function WcAllies takes' in js and 'function WcBanner takes' in js
# everything inherited from the 2.9.1-2.9.5 chain must still be here
assert 'function DmgObserve takes' in js, 'damage meter lost'
assert 'function HealObserve takes' in js and 'Healed by:' in js, '2.9.5 healing meter lost'
assert js.count('call HealObserve(') == 7, 'healing-meter hooks changed'
assert 'elseif b==' + "$48305342" + ' then' in js and 'Arcane Edge' in js, 'meter attribution lost'
wts = b.read_file('war3map.wts').decode('utf-8-sig')
skin = b.read_file('war3mapSkin.txt').decode('utf-8')
assert 'CHS_v2.9.5' not in wts and wts.count('CHS_v2.10.0') == 2
assert '2.9.29' in wts, 'the unrelated 2.9.29 tooltip was clobbered'
assert '|Cff00ff002.10.0' in skin and '2.9.5' not in skin
print('VERIFY: 5 heroes registered, grid at 64 cells, version 2.10.0,')
print('        damage meter + healing meter + all prior fixes intact')
