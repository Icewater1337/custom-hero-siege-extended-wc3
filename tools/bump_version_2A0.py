"""Bump the version strings in war3map.wts and war3mapSkin.txt to 2.10.0.

usage: python bump_version_2A0.py [source-stage-prefix] [old-version]
       defaults: new295  2.9.5

Only the three precise full-version strings are touched. A blanket replace of the
old version is wrong: the string table legitimately contains other version-looking
text (e.g. tooltips reading "...since 2.9.29") that must not be rewritten.
"""
import os
import re
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))

PREFIX = sys.argv[1] if len(sys.argv) > 1 else 'new295'
OLD = sys.argv[2] if len(sys.argv) > 2 else '2.9.5'
NEW = '2.10.2'

# newline='' on the READ matters: without it Python's universal-newline mode
# silently rewrites all 165,295 CRLF line endings in war3map.wts to LF (the
# write side already uses newline=''). Nothing semantic changes, but no shipped
# build has ever deviated from the original's line endings and the string table
# is not worth gambling on.
wts = open('%s_war3map.wts' % PREFIX, encoding='utf-8-sig', newline='').read()
skin = open('%s_war3mapSkin.txt' % PREFIX, encoding='utf-8', newline='').read()
crlf_in = wts.count('\r\n')

# show every other version-looking string so an unintended match is visible
print('x.y.z strings in war3map.wts:', sorted(set(re.findall(r'\d+\.\d+\.\d+', wts))))

for old, new, n in [('CHS_v' + OLD, 'CHS_v' + NEW, 2),
                    ('|Cff00ff00' + OLD, '|Cff00ff00' + NEW, 1)]:
    assert wts.count(old) == n, 'wts: %r count %d != %d' % (old, wts.count(old), n)
    wts = wts.replace(old, new)

old, new = '|Cff00ff00' + OLD, '|Cff00ff00' + NEW
assert skin.count(old) == 1, 'skin.txt: %r count %d' % (old, skin.count(old))
skin = skin.replace(old, new)

open('new2A0_war3map.wts', 'w', encoding='utf-8-sig', newline='').write(wts)
open('new2A0_war3mapSkin.txt', 'w', encoding='utf-8', newline='').write(skin)

assert 'CHS_v' + OLD not in wts and wts.count('CHS_v' + NEW) == 2
assert '|Cff00ff00' + NEW in skin and OLD not in skin
assert '2.9.29' in wts, 'the unrelated 2.9.29 tooltip was clobbered'
assert wts.count('\r\n') == crlf_in, 'line endings rewritten (%d -> %d)' % (crlf_in, wts.count('\r\n'))
print('CRLF line endings preserved: %d' % crlf_in)
print('%s_war3map.wts     -> new2A0_war3map.wts     (%s -> %s)' % (PREFIX, OLD, NEW))
print('%s_war3mapSkin.txt -> new2A0_war3mapSkin.txt' % PREFIX)
print('remaining %r occurrences in wts: %d' % (OLD, wts.count(OLD)))
