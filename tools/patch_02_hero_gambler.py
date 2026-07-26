"""Add hero 'The Gambler' (H0GB=$48304742) to the bug-fixed script.

Input: war3map_fixed.j (three bug fixes applied)
Output: war3map_287.j (hero + version bump)
All insertions are exact-string anchored with uniqueness assertions.
"""
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
src = open('war3map_fixed.j', encoding='utf-8', newline='').read()

# extra collision safety for new identifiers
for ident in ['GamblerRollText', 'grtA', 'grtB', 'grtC', 'grtT']:
    assert ident not in src, f'identifier collision: {ident}'

HELPER = '''function GamblerRollText takes unit grtA,unit grtB,boolean grtC returns nothing
local texttag grtT
if GetLocalPlayer()==GetOwningPlayer(grtA) and IsUnitVisible(grtB,GetLocalPlayer()) then
set grtT=CreateTextTag()
if grtC then
call SetTextTagText(grtT,"|cffffdc00DOUBLE!|r",.024)
else
call SetTextTagText(grtT,"|cffff4040BUST!|r",.024)
endif
call SetTextTagPos(grtT,GetUnitX(grtB),GetUnitY(grtB),16.)
call SetTextTagColor(grtT,$ff,$ff,$ff,$ff)
call SetTextTagVelocity(grtT,.0,.05)
call SetTextTagFadepoint(grtT,1.5)
call SetTextTagLifespan(grtT,2.5)
call SetTextTagPermanent(grtT,false)
endif
set grtT=null
endfunction
'''

GAMBLE = '''if GetUnitTypeId(ACt)==$48304742 then
if GetRandomInt(1,$64)<=(15.+.05*I2R(GetHeroLevel(ACt))+Dwq(ACt))*LoadReal(tC,BCq(VO,GetHandleId(ACt)),5) then
call SaveReal(tC,BCq(pC,GetHandleId(ACt)),1,(LoadReal(tC,BCq(pC,GetHandleId(ACt)),1)+I2R(ICt))*1.)
set ICt=ICt*2
call GamblerRollText(ACt,lCt,true)
elseif GetRandomInt(1,$64)<=5 then
call SaveReal(tC,BCq(pC,GetHandleId(ACt)),2,(LoadReal(tC,BCq(pC,GetHandleId(ACt)),2)+I2R(ICt))*1.)
set ICt=0
call GamblerRollText(ACt,lCt,false)
endif
endif
'''

HWT = '''elseif emt==$48304742 then
call puq(Smt,5,.002*I2R(Ymt))
call SaveReal(tC,BCq(pC,GetHandleId(Smt)),0,(15.+.05*I2R(kmt))*1.)
'''

KDT = '''if GetUnitTypeId(ydt)==$48304742 and jdt then
call puq(ydt,5,.25)
call SaveReal(tC,BCq(pC,GetHandleId(ydt)),0,15.05*1.)
endif
'''

PO = '''call SaveStr(tC,BCq(Po,$48304742),1,"ReplaceableTextures\\\\CommandButtons\\\\BTNHeroFireLord.blp")
call SaveStr(tC,BCq(Po,$48304742),2,"|cff00ffffPassive|r: Loaded Dice: The Gambler's |cff5ce74aLuck|r is increased by 25%.|n|n|cff00ffffPassive|r: Double or Nothing: When the Hero kills an enemy it has a 15% chance to win |cffffcc00double|r the gold reward, but a 5% chance to lose it entirely. Win chance is improved by |cff5ce74aLuck|r. [|cff80ff80Luck|r]")
call SaveStr(tC,BCq(Po,$48304742),3,"|cffffff00Level Up Bonus|r: +0.2% |cff5ce74aLuck|r. Double or Nothing: +0.05% win chance.")
call SaveStr(tC,BCq(Po,$48304742),4,"24")
'''

DC = '''call SaveStr(tC,BCq(DC,$48304742),0,"|cffe7544aDouble or Nothing chance|r: ,0,%%")
call SaveStr(tC,BCq(DC,$48304742),1,"|cffd6e049Gold won|r: ,0,")
call SaveStr(tC,BCq(DC,$48304742),2,"|cff4daed4Gold lost|r: ,0,")
'''

CAT = '''set Zoq=LoadInteger(wH,$48304742,0)
set oH[Zoq]=BlzBitOr(uoq,oH[Zoq])
if uoq==4 then
set VH[SH]=$48304742
set SH=SH+1
elseif uoq==8 then
set kH[QH]=$48304742
set QH=QH+1
elseif uoq==16 then
set NH[YH]=$48304742
set YH=YH+1
endif
'''

def insert_before(src, anchor, text, label):
    n = src.count(anchor)
    assert n == 1, f'{label}: anchor count {n}'
    return src.replace(anchor, text + anchor)

def insert_after(src, anchor, text, label):
    n = src.count(anchor)
    assert n == 1, f'{label}: anchor count {n}'
    return src.replace(anchor, anchor + text)

# 1. helper before eCt
src = insert_before(src, 'function eCt takes unit lCt,unit ACt returns nothing\n',
                    HELPER, 'helper')
# 2. gamble block before the reward grant
src = insert_before(src, 'call mCt(ACt,lCt,ICt,bCt)\n', GAMBLE, 'gamble')
# 3. level-up branch before H016's branch
src = insert_before(src,
    'elseif emt==$48303136 then\ncall SaveReal(tC,BCq(pC,GetHandleId(Smt)),0,kmt*25*1.)',
    HWT, 'hwt')
# 4. creation branch before the baseline luck init at Kdt end
src = insert_before(src, 'call puq(ydt,5,1.)\nset ydt=null\nendfunction', KDT, 'kdt')
# 5. Po card before H016's entries
src = insert_before(src,
    'call SaveStr(tC,BCq(Po,$48303136),1,"ReplaceableTextures\\\\CommandButtons\\\\BTNDoomGuard.blp")',
    PO, 'po')
# 6. DC stat lines before H000's
src = insert_before(src,
    'call SaveStr(tC,BCq(DC,$48303030),0,"|cffe7544aDamage|r: ,0,")',
    DC, 'dc')
# 7. roster slot 53
src = insert_after(src, 'set KC[52]=$4f303042\n', 'set KC[53]=$48304742\n', 'kc')
# 8. attribute category block before H007's
src = insert_before(src, 'set Zoq=LoadInteger(wH,$48303037,0)\n', CAT, 'cat')
# 9. starting element Fire x1
src = insert_after(src, 'call NIq($48303030,7,1)\n',
                   'call NIq($48304742,1,1)\n', 'niq')
# 10. version bump
src = insert_before(src, 'x-version-marker-none', '', 'noop') if False else src
n = src.count('call SetMapName("CHS_v2.8.6")')
assert n == 1, f'SetMapName count {n}'
src = src.replace('call SetMapName("CHS_v2.8.6")', 'call SetMapName("CHS_v2.8.7")')

open('war3map_287.j', 'w', encoding='utf-8', newline='').write(src)
print('patched OK; lines:', src.count('\n') + 1)
print('H0GB refs in script:', src.count('$48304742'))
