"""2.9.4: incoming 'Taken from' breakdown distinguishes enemy auto-attacks from
untagged periodic/passive damage (e.g. Disease Cloud). Keys: tagged ability ->
UX (named); auto (HZ) -> HX (unit name); untagged non-attack -> -HX (unit name +
"(over time)").  war3map_293.j -> war3map_294.j
"""
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
src = open('war3map_293.j', encoding='utf-8', newline='').read()

def repl(s, old, new, label, n=1):
    assert s.count(old) == n, f'{label}: count {s.count(old)} != {n}'
    return s.replace(old, new)

# 1. incoming key: split auto vs untagged-periodic
src = repl(src,
'''if UX!=0 then
set ik=UX
else
set ik=HX
endif''',
'''if UX!=0 then
set ik=UX
elseif HZ[pZ] then
set ik=HX
else
set ik=-HX
endif''', 'incoming-ik')

# 2. DmgName: render negated unit key (-HX) as "<unit> (over time)"
src = repl(src,
'''elseif b==-3 then
return "|cffccccccOther|r"
endif
return "|cff8fd6ff"+GetObjectName(b)+"|r"''',
'''elseif b==-3 then
return "|cffccccccOther|r"
elseif b<0 then
return "|cffffb0b0"+GetObjectName(-b)+" (over time)|r"
endif
return "|cff8fd6ff"+GetObjectName(b)+"|r"''', 'dmgname-neg')

# 3. version bump 2.9.3 -> 2.9.4 (PRECISE full version strings only)
src = repl(src, 'call SetMapName("CHS_v2.9.3")', 'call SetMapName("CHS_v2.9.4")', 'mapname')
src = repl(src, 'set jm[yaq]="CHS v2.9.3"', 'set jm[yaq]="CHS v2.9.4"', 'vertable')

open('war3map_294.j', 'w', encoding='utf-8', newline='').write(src)
print('patched OK; lines:', src.count(chr(10)) + 1)
print('incoming -HX present:', 'set ik=-HX' in src, '| DmgName over-time present:', '(over time)' in src)
