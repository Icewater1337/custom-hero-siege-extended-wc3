"""2.9.5: add a HEALING meter section. Track healing to the player's hero by
source: Lifesteal (Elt wrapper + AUcs + spell-vamp) and named heal spells.
Store in HEAL/HEALN (int-keyed), show a 'Healed by:' section in the multiboard.
war3map_294.j -> war3map_295.j
"""
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
src = open('war3map_294.j', encoding='utf-8', newline='').read()
for tok in ['HEAL=0', 'HealObserve']:
    assert tok not in src, f'collision: {tok}'

def repl(s, old, new, label, n=1):
    assert s.count(old) == n, f'{label}: count {s.count(old)} != {n}'
    return s.replace(old, new)

# --- globals + init ---
src = repl(src, 'integer DMGIN=0\n', 'integer DMGIN=0\ninteger HEAL=0\ninteger HEALN=0\n', 'globals')
src = repl(src, 'set DMGIN=kCq(1)\n', 'set DMGIN=kCq(1)\nset HEAL=kCq(1)\nset HEALN=kCq(1)\n', 'init')

# --- DmgName: key 3 = Lifesteal ---
src = repl(src,
'''function DmgName takes integer b returns string
if b==1 then
return "|cffffdc00Auto-attack|r"''',
'''function DmgName takes integer b returns string
if b==1 then
return "|cffffdc00Auto-attack|r"
elseif b==3 then
return "|cff80ff80Lifesteal|r"''', 'dmgname')

# --- DmgReset: flush HEAL/HEALN too ---
src = repl(src,
'''call FlushChildHashtable(tC,BCq(DMGI,pid))
call FlushChildHashtable(tC,BCq(DMGIN,pid))
endfunction''',
'''call FlushChildHashtable(tC,BCq(DMGI,pid))
call FlushChildHashtable(tC,BCq(DMGIN,pid))
call FlushChildHashtable(tC,BCq(HEAL,pid))
call FlushChildHashtable(tC,BCq(HEALN,pid))
endfunction''', 'dmgreset')

# --- DmgMbPrealloc: HEAL/HEALN ---
src = repl(src,
'''call SaveReal(tC,BCq(DMGIN,i),0,LoadReal(tC,BCq(DMGIN,i),0))
call SaveReal(tC,BCq(DMGI,i),0,LoadReal(tC,BCq(DMGI,i),0))
set i=i+1''',
'''call SaveReal(tC,BCq(DMGIN,i),0,LoadReal(tC,BCq(DMGIN,i),0))
call SaveReal(tC,BCq(DMGI,i),0,LoadReal(tC,BCq(DMGI,i),0))
call SaveReal(tC,BCq(HEALN,i),0,LoadReal(tC,BCq(HEALN,i),0))
call SaveReal(tC,BCq(HEAL,i),0,LoadReal(tC,BCq(HEAL,i),0))
set i=i+1''', 'prealloc')

# --- HealObserve helper (before AQt) ---
HEALOBS = '''function HealObserve takes unit u,integer srcKey,real amt returns nothing
local integer pid
local integer n
if amt<1. or u==null then
return
endif
set pid=GetPlayerId(GetOwningPlayer(u))
if pid<0 or pid>7 then
return
endif
if u!=Gh[pid] then
return
endif
if not HaveSavedReal(tC,BCq(HEAL,pid),srcKey) then
set n=LoadInteger(tC,BCq(HEALN,pid),0)+1
call SaveInteger(tC,BCq(HEALN,pid),0,n)
call SaveInteger(tC,BCq(HEALN,pid),n,srcKey)
endif
call SaveReal(tC,BCq(HEAL,pid),srcKey,LoadReal(tC,BCq(HEAL,pid),srcKey)+amt)
endfunction
'''
src = repl(src, 'function AQt takes nothing returns nothing\ncall DmgObserve()\n',
           HEALOBS + 'function AQt takes nothing returns nothing\ncall DmgObserve()\n', 'healobs')

# --- board rowcount 16 -> 20 ---
src = repl(src, 'call MultiboardSetRowCount(DmgMB,16)', 'call MultiboardSetRowCount(DmgMB,20)', 'rowcount')

# --- DmgMbRefresh: trim incoming to 3 rows, add Healed-by section ---
src = repl(src,
'''set row=11
set i=1
loop
exitwhen row>14
if i<=cnt and DmgTmpV[i]>=1. then
if taken>=1. then
call DmgMbSetRow(row,DmgName(DmgTmpK[i]),DmgFmt(R2I(DmgTmpV[i]))+" ("+I2S(R2I(DmgTmpV[i]*100./taken))+"%)")
else
call DmgMbSetRow(row,DmgName(DmgTmpK[i]),DmgFmt(R2I(DmgTmpV[i])))
endif
else
call DmgMbSetRow(row,"","")
endif
set i=i+1
set row=row+1
endloop
call DmgMbSetRow(15,"|cffff8080Total taken|r","|cffff8080"+DmgFmt(R2I(taken))+"|r")
endfunction''',
'''set row=11
set i=1
loop
exitwhen row>13
if i<=cnt and DmgTmpV[i]>=1. then
if taken>=1. then
call DmgMbSetRow(row,DmgName(DmgTmpK[i]),DmgFmt(R2I(DmgTmpV[i]))+" ("+I2S(R2I(DmgTmpV[i]*100./taken))+"%)")
else
call DmgMbSetRow(row,DmgName(DmgTmpK[i]),DmgFmt(R2I(DmgTmpV[i])))
endif
else
call DmgMbSetRow(row,"","")
endif
set i=i+1
set row=row+1
endloop
call DmgMbSetRow(14,"|cffff8080Total taken|r","|cffff8080"+DmgFmt(R2I(taken))+"|r")
set cnt=DmgLoadSort(HEAL,HEALN,pid)
set heald=DmgTotal
call DmgMbSetRow(15,"|cff80ff80Healed by:|r","")
set row=16
set i=1
loop
exitwhen row>18
if i<=cnt and DmgTmpV[i]>=1. then
if heald>=1. then
call DmgMbSetRow(row,DmgName(DmgTmpK[i]),DmgFmt(R2I(DmgTmpV[i]))+" ("+I2S(R2I(DmgTmpV[i]*100./heald))+"%)")
else
call DmgMbSetRow(row,DmgName(DmgTmpK[i]),DmgFmt(R2I(DmgTmpV[i])))
endif
else
call DmgMbSetRow(row,"","")
endif
set i=i+1
set row=row+1
endloop
call DmgMbSetRow(19,"|cff80ff80Total healed|r","|cff80ff80"+DmgFmt(R2I(heald))+"|r")
endfunction''', 'refresh')
# add the heald local
src = repl(src,
'''local real total
local real taken
if DmgMB==null or pid>7 then''',
'''local real total
local real taken
local real heald
if DmgMB==null or pid>7 then''', 'heald-local')

# --- HEAL HOOKS ---
# 1. AUcs on-damage lifesteal (AQt)
src = repl(src,
'''if UX==$41556373 then
call SetUnitState(hX,UNIT_STATE_LIFE,GetUnitState(hX,UNIT_STATE_LIFE)+qZ[pZ])
endif''',
'''if UX==$41556373 then
call SetUnitState(hX,UNIT_STATE_LIFE,GetUnitState(hX,UNIT_STATE_LIFE)+qZ[pZ])
call HealObserve(hX,3,qZ[pZ])
endif''', 'h-aucs')
# 2. Elt lifesteal wrapper (all leech)
src = repl(src, 'call SetWidgetLife(Alt,GetWidgetLife(Alt)+blt)\n',
           'call SetWidgetLife(Alt,GetWidgetLife(Alt)+blt)\ncall HealObserve(Alt,3,blt)\n', 'h-elt')
# 3. spell-vamp
src = repl(src,
'''if rQt>0 and fQt!=0. then
call SetUnitState(hX,UNIT_STATE_LIFE,GetUnitState(hX,UNIT_STATE_LIFE)+fQt*.1)
endif''',
'''if rQt>0 and fQt!=0. then
call SetUnitState(hX,UNIT_STATE_LIFE,GetUnitState(hX,UNIT_STATE_LIFE)+fQt*.1)
call HealObserve(hX,3,fQt*.1)
endif''', 'h-spellvamp')
# 4. A0EV +500
src = repl(src,
'''elseif JMt==$41304556 then
call SetUnitState(GetTriggerUnit(),UNIT_STATE_LIFE,GetUnitState(GetTriggerUnit(),UNIT_STATE_LIFE)+500.)''',
'''elseif JMt==$41304556 then
call SetUnitState(GetTriggerUnit(),UNIT_STATE_LIFE,GetUnitState(GetTriggerUnit(),UNIT_STATE_LIFE)+500.)
call HealObserve(GetTriggerUnit(),$41304556,500.)''', 'h-a0ev')
# 5. A0EX +1000
src = repl(src,
'''elseif JMt==$41304558 then
call SetUnitState(GetTriggerUnit(),UNIT_STATE_LIFE,GetUnitState(GetTriggerUnit(),UNIT_STATE_LIFE)+1000.)''',
'''elseif JMt==$41304558 then
call SetUnitState(GetTriggerUnit(),UNIT_STATE_LIFE,GetUnitState(GetTriggerUnit(),UNIT_STATE_LIFE)+1000.)
call HealObserve(GetTriggerUnit(),$41304558,1000.)''', 'h-a0ex')
# 6. A0EY full heal (measure delta before Oqq_996)
src = repl(src,
'''elseif JMt==$41304559 then
call Oqq_996(GetUnitState(CMt,UNIT_STATE_MAX_LIFE),GetUnitState(CMt,UNIT_STATE_MAX_MANA))''',
'''elseif JMt==$41304559 then
call HealObserve(CMt,$41304559,GetUnitState(CMt,UNIT_STATE_MAX_LIFE)-GetUnitState(CMt,UNIT_STATE_LIFE))
call Oqq_996(GetUnitState(CMt,UNIT_STATE_MAX_LIFE),GetUnitState(CMt,UNIT_STATE_MAX_MANA))''', 'h-a0ey')
# 7. QSq holy-bolt heal
src = repl(src,
'''call SetUnitState(TSq,UNIT_STATE_LIFE,GetUnitState(TSq,UNIT_STATE_LIFE)+VSq)
call vDq(TSq,1,1)''',
'''call SetUnitState(TSq,UNIT_STATE_LIFE,GetUnitState(TSq,UNIT_STATE_LIFE)+VSq)
call HealObserve(TSq,$41303157,VSq)
call vDq(TSq,1,1)''', 'h-qsq')

# --- BUG 1: reset meter at the post-PvP wave start (aet + qqf bypass NFt) ---
src = repl(src, 'call DestroyTimerDialog(tX)\ncall TriggerExecute(vh)\nendfunction',
           'call DestroyTimerDialog(tX)\ncall DmgWaveReport()\ncall TriggerExecute(vh)\nendfunction', 'bug1-aet')
src = repl(src, 'call DestroyTimerDialog(tX)\ncall TriggerExecute(vh)\nreturn true',
           'call DestroyTimerDialog(tX)\ncall DmgWaveReport()\ncall TriggerExecute(vh)\nreturn true', 'bug1-qqf')

# --- BUG 3: name creep-tagged incoming (e.g. Spiked Carapace reflect) via CZ[pZ] fallback ---
src = repl(src,
'''if UX!=0 then
set ik=UX
elseif HZ[pZ] then
set ik=HX
else
set ik=-HX
endif''',
'''if UX!=0 then
set ik=UX
elseif CZ[pZ]!=0 then
set ik=CZ[pZ]
elseif HZ[pZ] then
set ik=HX
else
set ik=-HX
endif''', 'bug3-cz')

# --- version bump 2.9.4 -> 2.9.5 (precise) ---
src = repl(src, 'call SetMapName("CHS_v2.9.4")', 'call SetMapName("CHS_v2.9.5")', 'mapname')
src = repl(src, 'set jm[yaq]="CHS v2.9.4"', 'set jm[yaq]="CHS v2.9.5"', 'vertable')

open('war3map_295.j', 'w', encoding='utf-8', newline='').write(src)
print('patched OK; lines:', src.count(chr(10)) + 1)
print('HealObserve calls:', src.count('call HealObserve('), '| HEAL refs:', src.count('HEAL'))
