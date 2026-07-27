"""Fix the Ice Force (A053) extended tooltip.

The tooltip embedded the map's runtime placeholder token ',s01,', which the JASS
only swaps for the live value (pqq_2192) once the ability is active on a unit
(war3map.j: BlzSetAbilityExtendedTooltip at levelup / on proc). In the ability
preview the swap hasn't run, so players saw the raw '(,s01,%)' token. Replace it
with a self-contained description of the real mechanic - the incoming hit is
multiplied by 500/(500+INT), i.e. it blocks INT/(INT+500) of one hit.

The leftover pqq_2192(",s01,",...) calls then become harmless no-ops.

NOTE: ',s01,' is ALSO used by A089 (Martial Retribution)'s own live tooltip
("Current maximum: ,s01,"). That one is a working dynamic tooltip and is left
untouched - only the 30 Ice Force ubertip strings are rewritten.

Operates on war3map.wts (default new2A0_war3map.wts, i.e. after the version bump).
"""
import os
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))
FN = sys.argv[1] if len(sys.argv) > 1 else 'new2A0_war3map.wts'

OLD = b"Reduces damage taken by Hero based on its intelligence (,s01,%) once every few seconds."
NEW = (b"Reduces the damage of one incoming hit based on the Hero's Intelligence, "
       b"blocking |cffffcc00Int / (Int + 500)|r of it (50% at 500 Int), once every few seconds.")

w = open(FN, 'rb').read()
n = w.count(OLD)
assert n == 30, 'Ice Force tooltip anchor found %d times (expected 30 levels)' % n
before = w.count(b',s01,')
w = w.replace(OLD, NEW)
after = w.count(b',s01,')
assert after == before - 30, 'unexpected ,s01, delta (%d -> %d)' % (before, after)
assert after == 1, 'expected exactly the A089 (Martial Retribution) token to remain, got %d' % after
open(FN, 'wb').write(w)
print('Ice Force tooltip fixed x30 in %s; A089 live token preserved (%d remaining)' % (FN, after))
