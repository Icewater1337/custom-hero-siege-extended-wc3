"""Fix the inverted PvP betting payout in war3map_290.j -> war3map_290_final.j.

Producer-side fix in Tet: `det` is the LOSER (owner of the dying unit), so UB
must name the WINNING side. Swap the two stored values so loser-in-A pays
B's backers and vice-versa.  UB's sole consumer jot is left unchanged.
"""
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
src = open('war3map_290.j', encoding='utf-8', newline='').read()

OLD = ('if IsPlayerInForce(det,oB[iet]) then\n'
       'set UB[iet]=1\n'
       'elseif IsPlayerInForce(det,rB[iet]) then\n'
       'set UB[iet]=2\n'
       'endif\n')
NEW = ('if IsPlayerInForce(det,oB[iet]) then\n'
       'set UB[iet]=2\n'
       'elseif IsPlayerInForce(det,rB[iet]) then\n'
       'set UB[iet]=1\n'
       'endif\n')

assert src.count(OLD) == 1, f'betting anchor count {src.count(OLD)}'
src = src.replace(OLD, NEW)
open('war3map_290_final.j', 'w', encoding='utf-8', newline='').write(src)
print('betting inversion fixed -> war3map_290_final.j')

# sanity: both hero rawcodes still present, version bumped
assert src.count('$48304b42') == 20 and src.count('$48304742') == 16
assert 'SetMapName("CHS_v2.9.0")' in src and 'CHS v2.9.0' in src
# the consumer jot must be unchanged
assert 'if UB[eP]==1 then\ncall ForForce(pL,Ek)\nelseif UB[eP]==2 then\ncall ForForce(DL,Ek)\nendif' in src
print('sanity: heroes present, version 2.9.0, jot consumer unchanged')
