"""Add hero 'Kerrigan, Queen of Blades' (H0KB=$48304b42) to war3map_287.j and
bump version 2.8.7 -> 2.9.0.  Output: war3map_290.j
All insertions are exact-string anchored with uniqueness assertions.
"""
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
src = open('war3map_287.j', encoding='utf-8', newline='').read()
assert '\r\n' not in src

DBS = chr(92) + chr(92)  # two backslash chars, as JASS escapes paths
ICON = 'ReplaceableTextures' + DBS + 'CommandButtons' + DBS + 'BTNMaiev.blp'
EFFECT = 'war3mapImported' + DBS + 'Arcane Explosion.mdx'

# collision guard for the rawcode
assert src.count('$48304b42') == 0, 'H0KB rawcode already present!'

# --- 1. Psionic Storm proc (jQt), inserted AFTER the Void Bash block ---
VOIDBASH = ('if HX==$48303030 and(not IsUnitIllusion(hX)) and GetRandomInt(0,$64)<=(20.+Dwq(hX))*uX and GetUnitAbilityLevel(CX,$4253544e)==0 then\n'
            'set pQt=GetHeroLevel(hX)*50\n'
            'set tQt=LoadReal(tC,oJ,nX)\n'
            'if boq(CQt,$48303030,tQt+.4) then\n'
            'call Psq(hX,CX,pQt,tQt)\n'
            'endif\n'
            'endif\n')
PSIONIC = ('if HX==$48304b42 and HZ[pZ] and(not IsUnitIllusion(hX)) and GetRandomInt(1,$64)<=(20.+Dwq(hX))*uX then\n'
           'if boq(GetHandleId(hX),$48304b42,.4) then\n'
           'call mEq(hX,GetUnitX(CX),GetUnitY(CX),I2R(GetHeroAgi(hX,true))*(.8+.04*I2R(GetHeroLevel(hX))),250.,true,$48304b42,true,false)\n'
           'if po then\n'
           'call DestroyEffect(AddSpecialEffect("' + EFFECT + '",GetUnitX(CX),GetUnitY(CX)))\n'
           'endif\n'
           'endif\n'
           'endif\n')

# --- 2. Essence Harvest kill hook (eCt) ---
ESSENCE = ('if GetUnitTypeId(ACt)==$48304b42 then\n'
           'if LoadReal(tC,BCq(pC,GetHandleId(ACt)),0)<6000. then\n'
           'call BlzSetUnitBaseDamage(ACt,BlzGetUnitBaseDamage(ACt,0)+2,0)\n'
           'call SaveReal(tC,BCq(pC,GetHandleId(ACt)),0,(LoadReal(tC,BCq(pC,GetHandleId(ACt)),0)+2.)*1.)\n'
           'endif\n'
           'endif\n')

# --- 3. Level-up display (Hwt) ---
HWT = ('elseif emt==$48304b42 then\n'
       'call SaveReal(tC,BCq(pC,GetHandleId(Smt)),1,20.*1.)\n'
       'call SaveReal(tC,BCq(pC,GetHandleId(Smt)),2,(80.+4.*I2R(kmt))*1.)\n')

# --- 4. Creation init (Kdt) ---
KDT = ('if GetUnitTypeId(ydt)==$48304b42 and jdt then\n'
       'call SaveReal(tC,BCq(pC,GetHandleId(ydt)),0,0.)\n'
       'call SaveReal(tC,BCq(pC,GetHandleId(ydt)),1,20.*1.)\n'
       'call SaveReal(tC,BCq(pC,GetHandleId(ydt)),2,84.*1.)\n'
       'endif\n')

# --- 5. roster slot ---
KC = 'set KC[54]=$48304b42\n'

# --- 6. picker attribute category block (AGI; uoq==8 pool) ---
CAT = ('set Zoq=LoadInteger(wH,$48304b42,0)\n'
       'set oH[Zoq]=BlzBitOr(uoq,oH[Zoq])\n'
       'if uoq==4 then\n'
       'set VH[SH]=$48304b42\n'
       'set SH=SH+1\n'
       'elseif uoq==8 then\n'
       'set kH[QH]=$48304b42\n'
       'set QH=QH+1\n'
       'elseif uoq==16 then\n'
       'set NH[YH]=$48304b42\n'
       'set YH=YH+1\n'
       'endif\n')

# --- 7. starting elements: Dark(7) + Arcane(13) ---
NIQ = ('call NIq($48304b42,7,1)\n'
       'call NIq($48304b42,13,1)\n')

# --- 8. Po hero card ---
PO = ('call SaveStr(tC,BCq(Po,$48304b42),1,"' + ICON + '")\n'
      'call SaveStr(tC,BCq(Po,$48304b42),2,"|cff00ffffPassive|r: Essence Harvest: The Queen of Blades consumes the essence of the fallen. Each enemy slain permanently grants |cffffcc00+2 attack damage|r (up to +6000).|n|n|cff00ffffPassive|r: Psionic Storm: When the Hero attacks an enemy it has a 20% chance to unleash a psionic storm, dealing |cffff00ffmagic damage|r to nearby enemies equal to a percentage of its |cffff8000Agility|r. [|cff80ff80Luck|r]")\n'
      'call SaveStr(tC,BCq(Po,$48304b42),3,"|cffffff00Level Up Bonus|r: Psionic Storm: +4% Agility damage.")\n'
      'call SaveStr(tC,BCq(Po,$48304b42),4,"24")\n')

# --- 9. DC stat lines (contiguous 0,1,2) ---
DC = ('call SaveStr(tC,BCq(DC,$48304b42),0,"|cffe7544aAssimilated damage|r: ,0,")\n'
      'call SaveStr(tC,BCq(DC,$48304b42),1,"|cffd6e049Psionic Storm chance|r: ,0,%%")\n'
      'call SaveStr(tC,BCq(DC,$48304b42),2,"|cff4daed4Psionic Storm damage (% of Agility)|r: ,0,%%")\n')


def before(s, anchor, text, label):
    assert s.count(anchor) == 1, f'{label}: anchor count {s.count(anchor)}'
    return s.replace(anchor, text + anchor)

def after(s, anchor, text, label):
    assert s.count(anchor) == 1, f'{label}: anchor count {s.count(anchor)}'
    return s.replace(anchor, anchor + text)

src = after(src, VOIDBASH, PSIONIC, 'psionic')
src = before(src, 'if GetUnitTypeId(ACt)==$48304742 then\n', ESSENCE, 'essence')
src = before(src, 'elseif emt==$48303136 then\ncall SaveReal(tC,BCq(pC,GetHandleId(Smt)),0,kmt*25*1.)', HWT, 'hwt')
src = before(src, 'call puq(ydt,5,1.)\nset ydt=null\nendfunction', KDT, 'kdt')
src = after(src, 'set KC[53]=$48304742\n', KC, 'kc')
src = before(src, 'set Zoq=LoadInteger(wH,$48304742,0)\n', CAT, 'cat')
src = after(src, 'call NIq($48304742,1,1)\n', NIQ, 'niq')
src = before(src, 'call SaveStr(tC,BCq(Po,$48304742),1,', PO, 'po')
src = before(src, 'call SaveStr(tC,BCq(DC,$48304742),0,', DC, 'dc')

# --- 10. version bump 2.8.7 -> 2.9.0 ---
for old, new, lab in [('call SetMapName("CHS_v2.8.7")', 'call SetMapName("CHS_v2.9.0")', 'mapname'),
                      ('set jm[yaq]="CHS v2.8.7"', 'set jm[yaq]="CHS v2.9.0"', 'vertable')]:
    assert src.count(old) == 1, f'{lab}: count {src.count(old)}'
    src = src.replace(old, new)

open('war3map_290.j', 'w', encoding='utf-8', newline='').write(src)
print('patched OK; lines:', src.count(chr(10)) + 1)
print('H0KB refs:', src.count('$48304b42'), '| H0GB refs:', src.count('$48304742'))
print('effect path sample:', EFFECT)
print('icon path sample:', ICON)
