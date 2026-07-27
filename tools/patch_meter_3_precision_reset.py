"""2.9.3: (A) fix spell/passive damage not showing -- store bucket-id keys as
INTEGERS not reals (32-bit float corrupts rawcode keys >2^24); (B) move the
per-wave reset from wave-clear to wave-start. war3map_292.j -> war3map_293.j
"""
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
src = open('war3map_292.j', encoding='utf-8', newline='').read()

def repl(s, old, new, label, n=1):
    assert s.count(old) == n, f'{label}: count {s.count(old)} != {n}'
    return s.replace(old, new)

# ---- (A) precision fix: enum-list keys stored/read as integers ----
# DmgObserve DEALT list (DMGN)
src = repl(src, 'set n=R2I(LoadReal(tC,BCq(DMGN,oX),0))+1', 'set n=LoadInteger(tC,BCq(DMGN,oX),0)+1', 'a1')
src = repl(src, 'call SaveReal(tC,BCq(DMGN,oX),0,n*1.)', 'call SaveInteger(tC,BCq(DMGN,oX),0,n)', 'a2')
src = repl(src, 'call SaveReal(tC,BCq(DMGN,oX),n,bucket*1.)', 'call SaveInteger(tC,BCq(DMGN,oX),n,bucket)', 'a3')
# DmgObserve TAKEN list (DMGIN)
src = repl(src, 'set n=R2I(LoadReal(tC,BCq(DMGIN,rX),0))+1', 'set n=LoadInteger(tC,BCq(DMGIN,rX),0)+1', 'a4')
src = repl(src, 'call SaveReal(tC,BCq(DMGIN,rX),0,n*1.)', 'call SaveInteger(tC,BCq(DMGIN,rX),0,n)', 'a5')
src = repl(src, 'call SaveReal(tC,BCq(DMGIN,rX),n,ik*1.)', 'call SaveInteger(tC,BCq(DMGIN,rX),n,ik)', 'a6')
# DmgLoadSort reads (serves multiboard dealt + taken)
src = repl(src, 'local integer cnt=R2I(LoadReal(tC,BCq(enumP,pid),0))', 'local integer cnt=LoadInteger(tC,BCq(enumP,pid),0)', 'a7')
src = repl(src, 'set tk=R2I(LoadReal(tC,BCq(enumP,pid),i))', 'set tk=LoadInteger(tC,BCq(enumP,pid),i)', 'a8')

# ---- (B) reset at wave-start (NFt) instead of wave-clear (Oht) ----
src = repl(src, 'set DmgLabel="Wave "+I2S(GL+1)\nendfunction',
           'set DmgLabel="Wave "+I2S(GL)\nendfunction', 'b1')
src = repl(src, 'call DmgWaveReport()\n', '', 'b2-remove-oht')
src = repl(src,
'''function NFt takes nothing returns nothing
if pU[GL+1]then
if kt==3 then
call o1()
endif
set pU[GL+1]=false
call Waq(LP)
call DestroyTimerDialog(FP)
set LP=null
call TriggerExecute(vh)
endif
endfunction''',
'''function NFt takes nothing returns nothing
if pU[GL+1]then
if kt==3 then
call o1()
endif
set pU[GL+1]=false
call Waq(LP)
call DestroyTimerDialog(FP)
set LP=null
call DmgWaveReport()
call TriggerExecute(vh)
endif
endfunction''', 'b3-nft')
src = repl(src, 'call MultiboardSetTitleText(DmgMB,"Damage Meter")\n',
           'call MultiboardSetTitleText(DmgMB,"Damage Meter")\nset DmgLabel="Wave 1"\n', 'b4-initlabel')

# ---- (C) version bump 2.9.2 -> 2.9.3 ----
src = repl(src, 'call SetMapName("CHS_v2.9.2")', 'call SetMapName("CHS_v2.9.3")', 'c1')
src = repl(src, 'set jm[yaq]="CHS v2.9.2"', 'set jm[yaq]="CHS v2.9.3"', 'c2')

open('war3map_293.j', 'w', encoding='utf-8', newline='').write(src)
print('patched OK; lines:', src.count(chr(10)) + 1)
print('DmgWaveReport calls (want 1, in NFt):', src.count('call DmgWaveReport()'))
print('SaveInteger DMGN/DMGIN present:', src.count('SaveInteger(tC,BCq(DMGN') + src.count('SaveInteger(tC,BCq(DMGIN'))
