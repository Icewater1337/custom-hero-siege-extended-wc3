"""Add a per-wave + PvP damage meter to war3map_290_final.j -> war3map_291.j
and bump version 2.9.0 -> 2.9.1.

Hooks:
- DmgObserve() at top of AQt (After phase): accumulate final damage per
  (player, ability|auto) and per-hero taken. Read-only wrt game state.
- DmgWaveReport() at the wave-clear gate in Oht: display+reset per player.
- reset at duel start (Mqt); display+reset at duel end (Tet win / Met draw).
Storage: hashtable parents DMG (per-player,bucket sums) + DMGN (per-player
enum list), keyed by PLAYER ID, reset via FlushChildHashtable.
"""
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
src = open('war3map_290_final.j', encoding='utf-8', newline='').read()
assert '\r\n' not in src
for tok in ['DmgObserve', 'DmgReport', 'DmgWaveReport', 'DMGN', 'DmgTmpK']:
    assert tok not in src, f'identifier collision: {tok}'

GLOBALS_DECL = ('integer DMG=0\n'
                'integer DMGN=0\n'
                'string DmgLabel=""\n'
                'integer array DmgTmpK\n'
                'real array DmgTmpV\n')

# meter functions (raw string: in-message \n must stay literal backslash-n)
METER = r'''function DmgFmt takes integer n returns string
local string s=""
local integer x=n
local integer g
if x<=0 then
return "0"
endif
loop
exitwhen x<=0
set g=x-(x/1000)*1000
set x=x/1000
if x>0 then
if g<10 then
set s=",00"+I2S(g)+s
elseif g<100 then
set s=",0"+I2S(g)+s
else
set s=","+I2S(g)+s
endif
else
set s=I2S(g)+s
endif
endloop
return s
endfunction
function DmgName takes integer b returns string
if b==1 then
return "|cffffdc00Auto-attack|r"
elseif b==0 then
return "|cffccccccOther|r"
endif
return "|cff8fd6ff"+GetObjectName(b)+"|r"
endfunction
function DmgReset takes integer pid returns nothing
call FlushChildHashtable(tC,BCq(DMG,pid))
call FlushChildHashtable(tC,BCq(DMGN,pid))
endfunction
function DmgReport takes integer pid returns nothing
local integer cnt=R2I(LoadReal(tC,BCq(DMGN,pid),0))
local integer i
local integer j
local integer tk
local real tv
local real total=0.
local real taken=LoadReal(tC,BCq(DMG,pid),2)
local string s
local integer shown
if cnt<=0 then
return
endif
set i=1
loop
exitwhen i>cnt
set tk=R2I(LoadReal(tC,BCq(DMGN,pid),i))
set DmgTmpK[i]=tk
set DmgTmpV[i]=LoadReal(tC,BCq(DMG,pid),tk)
set total=total+DmgTmpV[i]
set i=i+1
endloop
set i=2
loop
exitwhen i>cnt
set tk=DmgTmpK[i]
set tv=DmgTmpV[i]
set j=i-1
loop
exitwhen j<1 or DmgTmpV[j]>=tv
set DmgTmpK[j+1]=DmgTmpK[j]
set DmgTmpV[j+1]=DmgTmpV[j]
set j=j-1
endloop
set DmgTmpK[j+1]=tk
set DmgTmpV[j+1]=tv
set i=i+1
endloop
set s="|cffffcc00== "+DmgLabel+" - Your Damage ==|r"
set i=1
set shown=0
loop
exitwhen i>cnt or shown>=10
if DmgTmpV[i]>=1. then
set s=s+"\n"+DmgName(DmgTmpK[i])+": |cffff5555"+DmgFmt(R2I(DmgTmpV[i]))+"|r"
if total>=1. then
set s=s+" ("+I2S(R2I(DmgTmpV[i]*100./total))+"%)"
endif
set shown=shown+1
endif
set i=i+1
endloop
set s=s+"\n|cffaaaaaaTotal dealt: "+DmgFmt(R2I(total))+"   Taken: "+DmgFmt(R2I(taken))+"|r"
call DisplayTimedTextToPlayer(Player(pid),0.,0.,15.,s)
endfunction
function DmgWaveReport takes nothing returns nothing
local integer p=0
set DmgLabel="Wave "+I2S(GL)
loop
exitwhen p>7
if Gh[p]!=null then
call DmgReport(p)
endif
set p=p+1
endloop
set p=0
loop
exitwhen p>7
call DmgReset(p)
set p=p+1
endloop
endfunction
function DmgObserve takes nothing returns nothing
local integer bucket
local integer n
if qZ[pZ]<1. then
return
endif
if oX<8 and PX!=null then
if rX==11 or(rX<8 and rX!=oX and CX==Gh[rX]) then
if HZ[pZ] then
set bucket=1
else
set bucket=UX
endif
if not HaveSavedReal(tC,BCq(DMG,oX),bucket) then
set n=R2I(LoadReal(tC,BCq(DMGN,oX),0))+1
call SaveReal(tC,BCq(DMGN,oX),0,n*1.)
call SaveReal(tC,BCq(DMGN,oX),n,bucket*1.)
endif
call SaveReal(tC,BCq(DMG,oX),bucket,LoadReal(tC,BCq(DMG,oX),bucket)+qZ[pZ])
endif
endif
if rX<8 and CX==Gh[rX] then
call SaveReal(tC,BCq(DMG,rX),2,LoadReal(tC,BCq(DMG,rX),2)+qZ[pZ])
endif
endfunction
function DmgReportEnum takes nothing returns nothing
call DmgReport(GetPlayerId(GetEnumPlayer()))
call DmgReset(GetPlayerId(GetEnumPlayer()))
endfunction
function DmgResetEnum takes nothing returns nothing
call DmgReset(GetPlayerId(GetEnumPlayer()))
endfunction
'''

def before(s, anchor, text, label):
    assert s.count(anchor) == 1, f'{label}: anchor count {s.count(anchor)}'
    return s.replace(anchor, text + anchor)

def after(s, anchor, text, label):
    assert s.count(anchor) == 1, f'{label}: anchor count {s.count(anchor)}'
    return s.replace(anchor, anchor + text)

# 1. globals
src = before(src, '\nendglobals\n', '\n' + GLOBALS_DECL.rstrip('\n'), 'globals')
# 2. init
src = after(src, 'set VO=kCq(1)\n', 'set DMG=kCq(1)\nset DMGN=kCq(1)\n', 'init')
# 3. meter functions block (before AQt)
src = before(src, 'function AQt takes nothing returns nothing\n', METER, 'meter')
# 4. accumulate at top of AQt
src = after(src, 'function AQt takes nothing returns nothing\n', 'call DmgObserve()\n', 'accum')
# 5. wave-end display+reset
src = after(src, 'if kL>=vL and LP==null then\n', 'call DmgWaveReport()\n', 'oht')
# 6. duel-start reset (after Mqt locals)
src = after(src, 'local boolean Iqt\n',
            'call ForForce(Xqt,function DmgResetEnum)\ncall ForForce(Kqt,function DmgResetEnum)\n', 'mqt')
# 7. duel-win display (Tet)
src = before(src, 'call met(iet)\n',
             'set DmgLabel="PvP Battle"\ncall ForForce(Eet,function DmgReportEnum)\ncall ForForce(xet,function DmgReportEnum)\n', 'tet')
# 8. duel-draw display (Met)
src = before(src, 'call met(wet)\n',
             'set DmgLabel="PvP Battle"\ncall ForForce(oB[wet],function DmgReportEnum)\ncall ForForce(rB[wet],function DmgReportEnum)\n', 'met')
# 9. version bump 2.9.0 -> 2.9.1
for old, new, lab in [('call SetMapName("CHS_v2.9.0")', 'call SetMapName("CHS_v2.9.1")', 'mapname'),
                      ('set jm[yaq]="CHS v2.9.0"', 'set jm[yaq]="CHS v2.9.1"', 'vertable')]:
    assert src.count(old) == 1, f'{lab}: count {src.count(old)}'
    src = src.replace(old, new)

open('war3map_291.j', 'w', encoding='utf-8', newline='').write(src)
print('patched OK; lines:', src.count(chr(10)) + 1)
print('DmgObserve refs:', src.count('DmgObserve'), '| DmgReport refs:', src.count('DmgReport'))
