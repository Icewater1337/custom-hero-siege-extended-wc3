"""Rework damage meter -> right-side multiboard widget; fix spell/passive
attribution (UX-first); add incoming-per-source breakdown. Bump 2.9.1 -> 2.9.2.
war3map_291.j -> war3map_292.j
"""
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
src = open('war3map_291.j', encoding='utf-8', newline='').read()
assert '\r\n' not in src
for tok in ['DmgMB', 'DMGI', 'DmgLoadSort', 'DmgMbRefresh']:
    assert tok not in src, f'collision: {tok}'

def repl(s, old, new, label, n=1):
    assert s.count(old) == n, f'{label}: count {s.count(old)} != {n}'
    return s.replace(old, new)

# 1. globals
src = repl(src, 'real array DmgTmpV\n',
           'real array DmgTmpV\nmultiboard DmgMB=null\nboolean array DmgMBOn\nreal DmgTotal=0.\ninteger DMGI=0\ninteger DMGIN=0\n',
           'globals')
# 2. init
src = repl(src, 'set DMGN=kCq(1)\n', 'set DMGN=kCq(1)\nset DMGI=kCq(1)\nset DMGIN=kCq(1)\n', 'init')

# 3. DmgName (add Other-by-type)
src = repl(src,
'''function DmgName takes integer b returns string
if b==1 then
return "|cffffdc00Auto-attack|r"
elseif b==0 then
return "|cffccccccOther|r"
endif
return "|cff8fd6ff"+GetObjectName(b)+"|r"
endfunction''',
'''function DmgName takes integer b returns string
if b==1 then
return "|cffffdc00Auto-attack|r"
elseif b==0 then
return "|cffccccccOther|r"
elseif b==-1 then
return "|cffccccccOther (physical)|r"
elseif b==-2 then
return "|cffccccccOther (magic)|r"
elseif b==-3 then
return "|cffccccccOther|r"
endif
return "|cff8fd6ff"+GetObjectName(b)+"|r"
endfunction''', 'dmgname')

# 4. DmgReset (flush incoming too)
src = repl(src,
'''function DmgReset takes integer pid returns nothing
call FlushChildHashtable(tC,BCq(DMG,pid))
call FlushChildHashtable(tC,BCq(DMGN,pid))
endfunction''',
'''function DmgReset takes integer pid returns nothing
call FlushChildHashtable(tC,BCq(DMG,pid))
call FlushChildHashtable(tC,BCq(DMGN,pid))
call FlushChildHashtable(tC,BCq(DMGI,pid))
call FlushChildHashtable(tC,BCq(DMGIN,pid))
endfunction''', 'dmgreset')

# 5. DmgObserve (UX-first bucket + Other-by-type + incoming per-source)
src = repl(src,
'''function DmgObserve takes nothing returns nothing
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
endfunction''',
'''function DmgObserve takes nothing returns nothing
local integer bucket
local integer ik
local integer n
if qZ[pZ]<1. then
return
endif
if oX<8 and PX!=null then
if rX==11 or(rX<8 and rX!=oX and CX==Gh[rX]) then
if UX!=0 then
set bucket=UX
elseif HZ[pZ] then
set bucket=1
elseif LZ[pZ]==DAMAGE_TYPE_NORMAL then
set bucket=-1
elseif LZ[pZ]==DAMAGE_TYPE_MAGIC then
set bucket=-2
else
set bucket=-3
endif
if not HaveSavedReal(tC,BCq(DMG,oX),bucket) then
set n=R2I(LoadReal(tC,BCq(DMGN,oX),0))+1
call SaveReal(tC,BCq(DMGN,oX),0,n*1.)
call SaveReal(tC,BCq(DMGN,oX),n,bucket*1.)
endif
call SaveReal(tC,BCq(DMG,oX),bucket,LoadReal(tC,BCq(DMG,oX),bucket)+qZ[pZ])
endif
endif
if rX<8 and CX==Gh[rX] and oX!=rX then
call SaveReal(tC,BCq(DMG,rX),2,LoadReal(tC,BCq(DMG,rX),2)+qZ[pZ])
if UX!=0 then
set ik=UX
else
set ik=HX
endif
if ik!=0 then
if not HaveSavedReal(tC,BCq(DMGI,rX),ik) then
set n=R2I(LoadReal(tC,BCq(DMGIN,rX),0))+1
call SaveReal(tC,BCq(DMGIN,rX),0,n*1.)
call SaveReal(tC,BCq(DMGIN,rX),n,ik*1.)
endif
call SaveReal(tC,BCq(DMGI,rX),ik,LoadReal(tC,BCq(DMGI,rX),ik)+qZ[pZ])
endif
endif
endfunction''', 'dmgobserve')

# 6. DmgWaveReport -> reset all + label next wave (no chat)
src = repl(src,
'''function DmgWaveReport takes nothing returns nothing
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
endfunction''',
'''function DmgWaveReport takes nothing returns nothing
local integer p=0
loop
exitwhen p>7
call DmgReset(p)
set p=p+1
endloop
set DmgLabel="Wave "+I2S(GL+1)
endfunction''', 'dmgwavereport')

# 7. multiboard functions block, inserted before AQt
MB = '''function DmgLoadSort takes integer sumP,integer enumP,integer pid returns integer
local integer cnt=R2I(LoadReal(tC,BCq(enumP,pid),0))
local integer i
local integer j
local integer tk
local real tv
set DmgTotal=0.
set i=1
loop
exitwhen i>cnt
set tk=R2I(LoadReal(tC,BCq(enumP,pid),i))
set DmgTmpK[i]=tk
set DmgTmpV[i]=LoadReal(tC,BCq(sumP,pid),tk)
set DmgTotal=DmgTotal+DmgTmpV[i]
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
return cnt
endfunction
function DmgMbSetRow takes integer row,string c0,string c1 returns nothing
local multiboarditem a=MultiboardGetItem(DmgMB,row,0)
local multiboarditem b=MultiboardGetItem(DmgMB,row,1)
call MultiboardSetItemValue(a,c0)
call MultiboardSetItemValue(b,c1)
call MultiboardReleaseItem(a)
call MultiboardReleaseItem(b)
set a=null
set b=null
endfunction
function DmgMbPrealloc takes nothing returns nothing
local integer i=0
loop
exitwhen i>7
call SaveReal(tC,BCq(DMGN,i),0,LoadReal(tC,BCq(DMGN,i),0))
call SaveReal(tC,BCq(DMG,i),2,LoadReal(tC,BCq(DMG,i),2))
call SaveReal(tC,BCq(DMGIN,i),0,LoadReal(tC,BCq(DMGIN,i),0))
call SaveReal(tC,BCq(DMGI,i),0,LoadReal(tC,BCq(DMGI,i),0))
set i=i+1
endloop
endfunction
function DmgMbRefresh takes nothing returns nothing
local integer pid=GetPlayerId(GetLocalPlayer())
local integer cnt
local integer i
local integer row
local real total
local real taken
if DmgMB==null or pid>7 then
return
endif
set taken=LoadReal(tC,BCq(DMG,pid),2)
set cnt=DmgLoadSort(DMG,DMGN,pid)
set total=DmgTotal
call DmgMbSetRow(0,"|cffffcc00"+DmgLabel+"|r","|cffffcc00Dealt|r")
set row=1
set i=1
loop
exitwhen row>8
if i<=cnt and DmgTmpV[i]>=1. then
if total>=1. then
call DmgMbSetRow(row,DmgName(DmgTmpK[i]),DmgFmt(R2I(DmgTmpV[i]))+" ("+I2S(R2I(DmgTmpV[i]*100./total))+"%)")
else
call DmgMbSetRow(row,DmgName(DmgTmpK[i]),DmgFmt(R2I(DmgTmpV[i])))
endif
else
call DmgMbSetRow(row,"","")
endif
set i=i+1
set row=row+1
endloop
call DmgMbSetRow(9,"|cffaaaaaaTotal dealt|r","|cffaaaaaa"+DmgFmt(R2I(total))+"|r")
set cnt=DmgLoadSort(DMGI,DMGIN,pid)
call DmgMbSetRow(10,"|cffff8080Taken from:|r","")
set row=11
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
endfunction
function DmgMbCreate takes nothing returns nothing
local integer r=0
local multiboarditem it=null
call DmgMbPrealloc()
set DmgMB=CreateMultiboard()
call MultiboardSetRowCount(DmgMB,16)
call MultiboardSetColumnCount(DmgMB,2)
call MultiboardSetTitleText(DmgMB,"Damage Meter")
loop
exitwhen r>=16
set it=MultiboardGetItem(DmgMB,r,0)
call MultiboardSetItemStyle(it,true,false)
call MultiboardSetItemWidth(it,0.10)
call MultiboardReleaseItem(it)
set it=MultiboardGetItem(DmgMB,r,1)
call MultiboardSetItemStyle(it,true,false)
call MultiboardSetItemWidth(it,0.06)
call MultiboardReleaseItem(it)
set r=r+1
endloop
set it=null
call MultiboardDisplay(DmgMB,true)
call TimerStart(CreateTimer(),1.,true,function DmgMbRefresh)
endfunction
function DmgMbToggle takes nothing returns nothing
local integer pid=GetPlayerId(GetTriggerPlayer())
set DmgMBOn[pid]=not DmgMBOn[pid]
if GetLocalPlayer()==GetTriggerPlayer() then
call MultiboardDisplay(DmgMB,not DmgMBOn[pid])
endif
endfunction
function DmgMbSetup takes nothing returns nothing
local trigger t=CreateTrigger()
local integer i=0
call DmgMbCreate()
loop
exitwhen i==8
call TriggerRegisterPlayerChatEvent(t,Player(i),"-dmg",true)
set i=i+1
endloop
call TriggerAddAction(t,function DmgMbToggle)
set t=null
endfunction
'''
src = repl(src, 'function AQt takes nothing returns nothing\ncall DmgObserve()\n',
           MB + 'function AQt takes nothing returns nothing\ncall DmgObserve()\n', 'mbblock')

# 8. Mqt: add PvP label
src = repl(src,
'call ForForce(Xqt,function DmgResetEnum)\ncall ForForce(Kqt,function DmgResetEnum)\n',
'set DmgLabel="PvP Battle"\ncall ForForce(Xqt,function DmgResetEnum)\ncall ForForce(Kqt,function DmgResetEnum)\n', 'mqt')
# 9. remove Tet chat block
src = repl(src,
'set DmgLabel="PvP Battle"\ncall ForForce(Eet,function DmgReportEnum)\ncall ForForce(xet,function DmgReportEnum)\n',
'', 'tet')
# 10. remove Met chat block
src = repl(src,
'set DmgLabel="PvP Battle"\ncall ForForce(oB[wet],function DmgReportEnum)\ncall ForForce(rB[wet],function DmgReportEnum)\n',
'', 'met')
# 11. init call
src = repl(src, 'call TimerStart(CreateTimer(),2.,true,MG)\n',
           'call TimerStart(CreateTimer(),2.,true,MG)\ncall DmgMbSetup()\n', 'initcall')
# 12. version bump
src = repl(src, 'call SetMapName("CHS_v2.9.1")', 'call SetMapName("CHS_v2.9.2")', 'mapname')
src = repl(src, 'set jm[yaq]="CHS v2.9.1"', 'set jm[yaq]="CHS v2.9.2"', 'vertable')

open('war3map_292.j', 'w', encoding='utf-8', newline='').write(src)
print('patched OK; lines:', src.count(chr(10)) + 1)
print('DmgMB refs:', src.count('DmgMB'), '| DMGI refs:', src.count('DMGI'), '| multiboard natives:', src.count('Multiboard'))
