"""Add five new heroes to CHS and raise the hero-picker grid from 56 to 64 cells.

    H0SC  The Stormcaller   INT ranged  - Forked Lightning (chain lightning proc)
    H0EX  The Executioner   STR melee   - Headsman's Toll (execute) + Grim Harvest
    H0WC  The Warchief      STR melee   - Warlord's Presence + Battle Standard (ally support)
    H0SB  The Spellblade    INT melee   - Arcane Edge (mana as ammo) + Mana Font
    H0GR  The Grudgebearer  STR melee   - Thick Hide + Grudge (store damage, release it)

Input : the newest war3map_*.j stage (default war3map_294.j, override with argv[1])
Output: war3map_2A0.j, version bumped to 2.10.0

Every insertion is anchored on a verbatim code snippet with a uniqueness
assertion, so this re-applies to a future base (and on top of the in-flight
2.9.5 healing-meter patch) or fails loudly at the one anchor that moved.
"""
import os
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))

SRC = sys.argv[1] if len(sys.argv) > 1 else 'war3map_294.j'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'war3map_2A0.j'
NEW_VERSION = '2.10.2'

src = open(SRC, encoding='utf-8', newline='').read()
assert '\r\n' not in src, 'input has CRLF line endings'

DBS = chr(92) + chr(92)          # the two-backslash escape JASS uses in paths


def rc(code):
    """'H0SC' -> '$48305343' (the JASS rawcode literal)."""
    return '$' + code.encode('latin1').hex()


SC, EX, WC, SB, GR = (rc(c) for c in ('H0SC', 'H0EX', 'H0WC', 'H0SB', 'H0GR'))
CODES = ['H0SC', 'H0EX', 'H0WC', 'H0SB', 'H0GR']

# ---------------------------------------------------------------- guards ----
for c in CODES:
    assert src.count(rc(c)) == 0, 'rawcode %s already present' % c
    assert src.count(c) == 0, 'rawcode %s present as plain text' % c
for ident in ['WcAllies', 'WcBanner']:
    assert ident not in src, 'identifier collision: %s' % ident


def before(s, anchor, text, label, n=1):
    assert s.count(anchor) == n, '%s: anchor count %d != %d' % (label, s.count(anchor), n)
    return s.replace(anchor, text + anchor)


def after(s, anchor, text, label, n=1):
    assert s.count(anchor) == n, '%s: anchor count %d != %d' % (label, s.count(anchor), n)
    return s.replace(anchor, anchor + text)


def swap(s, old, new, label, n=1):
    assert s.count(old) == n, '%s: count %d != %d' % (label, s.count(old), n)
    return s.replace(old, new)


# ============================================================================
# 1. PICKER CAPACITY - the grid is 8 columns x 7 rows = 56 cells and every
#    consumer loop is hard-bounded at 56. Slots 55-59 need 8 rows = 64 cells.
#    (Two of the six bounds are byte-identical, hence the n=2.)
# ============================================================================
src = swap(src, 'exitwhen Wnq>56', 'exitwhen Wnq>64', 'bound-Wnq')
src = swap(src, 'exitwhen EOq>56', 'exitwhen EOq>64', 'bound-EOq')
src = swap(src, 'exitwhen Doq>56', 'exitwhen Doq>64', 'bound-Doq', n=2)
src = swap(src, 'exitwhen toq>56', 'exitwhen toq>64', 'bound-toq')
src = swap(src, 'exitwhen kJq>56', 'exitwhen kJq>64', 'bound-kJq')
src = swap(src,
           'call BlzFrameSetSize(hoq,Loq*2.+.032*8+.008*7,Loq*2.+.032*7+.008*6+.015+.02+.0145)',
           'call BlzFrameSetSize(hoq,Loq*2.+.032*8+.008*7,Loq*2.+.032*8+.008*7+.015+.02+.0145)',
           'grid-height')

# ============================================================================
# 2. HELPERS for the Warchief (defined before PGt, the first user).
#    G4q (distance, 6419), Gh[], t[] and tL are all in scope there.
#
#    THE ALLY TEST. WC3 alliance alone does not work in this map: war3map.w3i
#    puts players 0-10 and 12-14 in one force with alliance flags 0x00000000,
#    so two human players are NEVER allied during a normal round, and
#    IsUnitAlly(Gh[i],p) would be true only for i == the hero's own player.
#    Alliance IS meaningful in PvP, where the duel/team code explicitly allies
#    each side (SetForceAllianceStateBJ(Xqt,Xqt,bj_ALLIANCE_ALLIED)) and
#    un-allies the other. So the test is three-part:
#
#      Gh[i]==u                     the hero itself, always
#      IsUnitAlly(Gh[i],p)          a duel / team-mode team-mate
#      t[i] and t[pid] and not tL   both players in the same co-op wave
#
#    t[] is the map's "player is in the round" flag and tL marks team/battle
#    -royale mode, so the third clause is off during PvP. That makes the
#    predicate fail CLOSED - if the phase is ambiguous the Warchief supports
#    nobody, rather than healing a duel opponent.
# ============================================================================
HELPERS = '''function WcAllies takes unit u returns integer
local integer i=0
local integer n=0
local player p=GetOwningPlayer(u)
local integer pid=GetPlayerId(GetOwningPlayer(u))
loop
exitwhen i>7
if Gh[i]!=null and UnitAlive(Gh[i]) and(Gh[i]==u or IsUnitAlly(Gh[i],p) or(t[i] and t[pid] and(not tL))) and G4q(u,Gh[i])<=900. then
set n=n+1
endif
set i=i+1
endloop
set p=null
return n
endfunction
function WcBanner takes unit u returns nothing
local integer i=0
local player p=GetOwningPlayer(u)
local integer pid=GetPlayerId(GetOwningPlayer(u))
local real amt=30.*I2R(GetHeroLevel(u))+I2R(GetHeroStr(u,true))
local real tot=0.
local real bef=0.
loop
exitwhen i>7
if Gh[i]!=null and UnitAlive(Gh[i]) and(Gh[i]==u or IsUnitAlly(Gh[i],p) or(t[i] and t[pid] and(not tL))) and G4q(u,Gh[i])<=900. then
set bef=GetUnitState(Gh[i],UNIT_STATE_LIFE)
call SetUnitState(Gh[i],UNIT_STATE_LIFE,bef+amt)
set tot=tot+GetUnitState(Gh[i],UNIT_STATE_LIFE)-bef
if po then
call DestroyEffect(AddSpecialEffectTarget("Abilities''' + DBS + '''Spells''' + DBS + '''Human''' + DBS + '''HolyBolt''' + DBS + '''HolyBoltSpecialArt.mdl",Gh[i],"origin"))
endif
endif
set i=i+1
endloop
call SaveReal(tC,BCq(pC,GetHandleId(u)),1,amt)
call SaveReal(tC,BCq(pC,GetHandleId(u)),2,LoadReal(tC,BCq(pC,GetHandleId(u)),2)+tot)
set p=null
endfunction
'''
src = before(src, 'function PGt takes', HELPERS, 'helpers')

# ============================================================================
# 3. THE GRUDGEBEARER's damage-taken side, in jQt's mitigation section.
#    jQt runs on EVENT_UNIT_DAMAGED, so qZ[pZ] here is the real post-armor,
#    post-block, post-magic-protection damage about to land.
# ============================================================================
#    Everything the Grudgebearer does is measured in MAXIMUM HIT POINTS, not in
#    attack damage. The first version capped the bank at 5x attack damage, which
#    is the one stat this chassis is deliberately worst at (24+1d10, 1.60s
#    cooldown, lowest of the five) - so the cap was tiny, the bank overflowed
#    instantly, and everything above it was thrown away. Max HP is what a tank
#    actually builds, so tying both halves to it makes the hero scale with its
#    own stat instead of fighting it.
GR_TAKEN = ('if OX==' + GR + ' and qZ[pZ]>0. and(not IsUnitIllusion(CX)) then\n'
            'set qZ[pZ]=qZ[pZ]*.85*1.\n'
            'call SaveReal(tC,BCq(pC,GetHandleId(CX)),0,RMinBJ(LoadReal(tC,BCq(pC,GetHandleId(CX)),0)+qZ[pZ],I2R(BlzGetUnitMaxHP(CX))*.15))\n'
            'endif\n')
src = before(src,
             'if GetUnitAbilityLevel(CX,$42303245)>0 then\nset qZ[pZ]=qZ[pZ]*.5\nendif\n',
             GR_TAKEN, 'grudge-taken')

# ============================================================================
# 4. THE ON-ATTACK PROCS - appended after Kerrigan's block, i.e. as the last
#    statements inside jQt's "if KX==0 or KX==2 and qZ[pZ]>0." proc block.
#    KX==0/2 means "this hit was not itself generated by a proc", which is what
#    makes all of these recursion-safe.
# ============================================================================
KERRIGAN_PROC = (
    'if HX==$48304b42 and HZ[pZ] and(not IsUnitIllusion(hX)) and GetRandomInt(1,$64)<=(20.+Dwq(hX))*uX then\n'
    'if boq(GetHandleId(hX),$48304b42,.4) then\n'
    'call mEq(hX,GetUnitX(CX),GetUnitY(CX),I2R(GetHeroAgi(hX,true))*(.8+.04*I2R(GetHeroLevel(hX))),250.,true,$48304b42,true,false)\n'
    'if po then\n'
    'call DestroyEffect(AddSpecialEffect("war3mapImported' + DBS + 'Arcane Explosion.mdx",GetUnitX(CX),GetUnitY(CX)))\n'
    'endif\n'
    'endif\n'
    'endif\n')

# Stormcaller - real Chain Lightning (A02R, 5 targets) fired through the map's
# own dummy-cast helper, damage per target scaled off Intelligence.
PROC_SC = ('if HX==' + SC + ' and HZ[pZ] and(not IsUnitIllusion(hX)) and GetRandomInt(1,$64)<=(30.+Dwq(hX))*uX then\n'
           'if boq(GetHandleId(hX),' + SC + ',.4) then\n'
           'call Qsq(hX,CX,GetUnitX(hX),GetUnitY(hX),$41303252,"chainlightning",25.*I2R(GetHeroLevel(hX))+I2R(GetHeroInt(hX,true))*(1.5+.01*I2R(GetHeroLevel(hX))),ABILITY_RLF_DAMAGE_PER_TARGET_OCL1)\n'
           'endif\n'
           'endif\n')

# Executioner - pure amplification of this same hit, no new damage instance.
#   The multiplier is deliberately below the map's own ceiling. The largest damage
#   multiplier anywhere in the base script is x3 ($41304333, line ~26899) and even
#   that one is gated behind a 2s ability cooldown and a timing window; the x2 at
#   ~27127 needs a 20% roll. This one is unconditional inside its window, so it sits
#   at x1.6 rising to a hard x2.5 - and it gets a 1s per-target internal cooldown,
#   matching Horsepower's boq(JX,...) convention for a big on-attack payoff.
#   Growth is on the THRESHOLD (a bounded axis, 25%->35%) rather than on the
#   multiplier, because the crit engine LAt() resolves at line ~26660, well before
#   jQt, so anything here multiplies on top of an already-critted hit.
PROC_EX = ('if HX==' + EX + ' and HZ[pZ] and(not IsUnitIllusion(hX)) and qZ[pZ]>0. and GetWidgetLife(CX)<=GetUnitState(CX,UNIT_STATE_MAX_LIFE)*RMinBJ(.25+.0002*I2R(GetHeroLevel(hX)),.35) then\n'
           'if boq(JX,' + EX + ',1.) then\n'
           'set qZ[pZ]=qZ[pZ]*RMinBJ(1.6+.002*I2R(GetHeroLevel(hX)),2.5)*1.\n'
           'if po then\n'
           'call DestroyEffect(AddSpecialEffect("Abilities' + DBS + 'Spells' + DBS + 'NightElf' + DBS + 'FanOfKnives' + DBS + 'FanOfKnivesTarget.mdl",GetUnitX(CX),GetUnitY(CX)))\n'
           'endif\n'
           'endif\n'
           'endif\n')

# Warchief - +6% damage per allied Hero within 900 (counts itself), capped at 5.
PROC_WC = ('if HX==' + WC + ' and(not IsUnitIllusion(hX)) and qZ[pZ]>0. then\n'
           'set qZ[pZ]=qZ[pZ]*(1.+.06*I2R(IMinBJ(WcAllies(hX),5)))*1.\n'
           'endif\n')

# Spellblade - spends 2% of max mana per swing for a separate magic hit.
# set j=3 marks the generated damage as proc damage so it cannot re-enter here.
PROC_SB = ('if HX==' + SB + ' and HZ[pZ] and(not IsUnitIllusion(hX)) and GetUnitState(hX,UNIT_STATE_MANA)>=GetUnitState(hX,UNIT_STATE_MAX_MANA)*.02 then\n'
           'set j=3\n'
           'set df=' + SB + '\n'
           'call SetUnitState(hX,UNIT_STATE_MANA,GetUnitState(hX,UNIT_STATE_MANA)-GetUnitState(hX,UNIT_STATE_MAX_MANA)*.02)\n'
           'call sLq(hX,CX,RMinBJ(GetUnitState(hX,UNIT_STATE_MAX_MANA)*.02*(2.+.01*I2R(GetHeroLevel(hX))),UIq(hX,0)*6.),false,false,null,DAMAGE_TYPE_MAGIC,null)\n'
           'if po then\n'
           'call DestroyEffect(AddSpecialEffect("Abilities' + DBS + 'Weapons' + DBS + 'Bolt' + DBS + 'BoltImpact.mdl",GetUnitX(CX),GetUnitY(CX)))\n'
           'endif\n'
           'endif\n')

# Grudgebearer - dumps everything stored in pC[0] as an AoE, then clears it.
# Grudgebearer - Mountain's Weight (pure damage from max HP) then the Grudge dump.
#   Adding to qZ[pZ] here IS the map's "pure damage": jQt runs on
#   EVENT_UNIT_DAMAGED, i.e. after armor, after Block and after magic protection,
#   so the added amount is untaxed. H01H's Cannibal Frenzy - the card that says
#   "ignores armor and block" - is the identical idiom (39259).
PROC_GR = ('if HX==' + GR + ' and HZ[pZ] and(not IsUnitIllusion(hX)) then\n'
           'if boq(JX,' + GR + ',1.) then\n'
           'set qZ[pZ]=(qZ[pZ]+I2R(BlzGetUnitMaxHP(hX))*RMinBJ(.01+.0001*I2R(GetHeroLevel(hX)),.04))*1.\n'
           'endif\n'
           'if LoadReal(tC,BCq(pC,GetHandleId(hX)),0)>=1. then\n'
           'call mEq(hX,GetUnitX(CX),GetUnitY(CX),LoadReal(tC,BCq(pC,GetHandleId(hX)),0),400.,true,' + GR + ',true,false)\n'
           'call SaveReal(tC,BCq(pC,GetHandleId(hX)),0,0.)\n'
           'if po then\n'
           'call DestroyEffect(AddSpecialEffect("Abilities' + DBS + 'Spells' + DBS + 'Orc' + DBS + 'WarStomp' + DBS + 'WarStompCaster.mdl",GetUnitX(CX),GetUnitY(CX)))\n'
           'endif\n'
           'endif\n'
           'endif\n')

src = after(src, KERRIGAN_PROC, PROC_SC + PROC_EX + PROC_WC + PROC_SB + PROC_GR, 'procs')

# ============================================================================
# 4b. RESCALE KERRIGAN (H0KB) onto the same curve as the Stormcaller:
#     flat (25 x hero level) + a percentage of the attribute, 150% + 1%/level.
#
#     Psionic Storm shipped as AGI*(0.8+0.04*level). 4%/level is 4-8x the
#     roster's convention for attribute scaling and the single steepest
#     coefficient in the map - unbounded, it reaches 24.8x Agility at the
#     level-600 cap. Moving it to 1%/level (the roster's target rate) plus a
#     flat per-level term gives her a real floor at low level and a sane tail,
#     and puts her on the same footing as the new heroes.
#
#     MUST run after the proc insertion above, which anchors on the original
#     mEq line.
# ============================================================================
KB = '$48304b42'
src = swap(src,
           'I2R(GetHeroAgi(hX,true))*(.8+.04*I2R(GetHeroLevel(hX)))',
           '25.*I2R(GetHeroLevel(hX))+I2R(GetHeroAgi(hX,true))*(1.5+.01*I2R(GetHeroLevel(hX)))',
           'kb-damage')
# 4th stat row for the flat half (DC allows 0..3, contiguous)
src = after(src,
            'call SaveStr(tC,BCq(DC,' + KB + '),2,"|cff4daed4Psionic Storm damage (% of Agility)|r: ,0,%%")\n',
            'call SaveStr(tC,BCq(DC,' + KB + '),3,"|cff51d44dPsionic Storm damage|r: ,0,")\n',
            'kb-dc')
src = swap(src,
           'call SaveReal(tC,BCq(pC,GetHandleId(ydt)),2,84.*1.)\n',
           'call SaveReal(tC,BCq(pC,GetHandleId(ydt)),2,151.*1.)\n'
           'call SaveReal(tC,BCq(pC,GetHandleId(ydt)),3,25.*1.)\n',
           'kb-kdt')
src = swap(src,
           'call SaveReal(tC,BCq(pC,GetHandleId(Smt)),2,(80.+4.*I2R(kmt))*1.)\n',
           'call SaveReal(tC,BCq(pC,GetHandleId(Smt)),2,(150.+1.*I2R(kmt))*1.)\n'
           'call SaveReal(tC,BCq(pC,GetHandleId(Smt)),3,25.*I2R(kmt)*1.)\n',
           'kb-hwt')
src = swap(src,
           'dealing |cffff00ffmagic damage|r to nearby enemies equal to a percentage of its |cffff8000Agility|r.',
           'dealing |cffff00ffmagic damage|r to nearby enemies equal to |cffffcc0025 per Hero level|r plus a percentage of its |cffff8000Agility|r.',
           'kb-po2')
src = swap(src,
           '|cffffff00Level Up Bonus|r: Psionic Storm: +4% Agility damage.',
           '|cffffff00Level Up Bonus|r: Psionic Storm: +25 damage, +1% Agility damage.',
           'kb-po3')

# ============================================================================
# 5. ON-KILL (eCt). ACt = the credited hero, lCt = the victim.
# ============================================================================
ONKILL = ('if GetUnitTypeId(ACt)==' + EX + ' then\n'
          'call SetUnitState(ACt,UNIT_STATE_LIFE,GetUnitState(ACt,UNIT_STATE_LIFE)+GetUnitState(ACt,UNIT_STATE_MAX_LIFE)*.02)\n'
          'call SetUnitState(ACt,UNIT_STATE_MANA,GetUnitState(ACt,UNIT_STATE_MANA)+GetUnitState(ACt,UNIT_STATE_MAX_MANA)*.02)\n'
          'endif\n'
          'if GetUnitTypeId(ACt)==' + SB + ' then\n'
          'call SetUnitState(ACt,UNIT_STATE_MANA,GetUnitState(ACt,UNIT_STATE_MANA)+GetUnitState(ACt,UNIT_STATE_MAX_MANA)*.02)\n'
          'endif\n')
src = before(src, 'if GetUnitTypeId(ACt)==$48304b42 then\n', ONKILL, 'onkill')

# ============================================================================
# 6. PER-SECOND (PGt) - the Warchief's Battle Standard. Inserted as an elseif
#    in the existing type-dispatch chain, never as a new leading if.
# ============================================================================
src = before(src,
             'elseif CGt==$4f303033 then\ncall ZSq(fGt,GetHeroLevel(fGt))',
             'elseif CGt==' + WC + ' then\ncall WcBanner(fGt)\n', 'pgt')

# ============================================================================
# 7. SPAWN INIT (Kdt). Kdt is an EnterRegion trigger with no idempotency guard,
#    so every seed here is an absolute SaveReal, never an additive puq.
# ============================================================================
KDT = (
    'if GetUnitTypeId(ydt)==' + SC + ' and jdt then\n'
    'call SaveReal(tC,BCq(pC,GetHandleId(ydt)),0,30.*1.)\n'
    'call SaveReal(tC,BCq(pC,GetHandleId(ydt)),1,25.*1.)\n'
    'call SaveReal(tC,BCq(pC,GetHandleId(ydt)),2,151.*1.)\n'
    'endif\n'
    'if GetUnitTypeId(ydt)==' + EX + ' and jdt then\n'
    'call SaveReal(tC,BCq(pC,GetHandleId(ydt)),0,60.2*1.)\n'
    'call SaveReal(tC,BCq(pC,GetHandleId(ydt)),1,25.02*1.)\n'
    'endif\n'
    'if GetUnitTypeId(ydt)==' + WC + ' and jdt then\n'
    'call SaveReal(tC,BCq(pC,GetHandleId(ydt)),0,6.*1.)\n'
    'call SaveReal(tC,BCq(pC,GetHandleId(ydt)),1,0.)\n'
    'call SaveReal(tC,BCq(pC,GetHandleId(ydt)),2,0.)\n'
    'endif\n'
    'if GetUnitTypeId(ydt)==' + SB + ' and jdt then\n'
    'call SaveReal(tC,BCq(pC,GetHandleId(ydt)),0,2.*1.)\n'
    'call SaveReal(tC,BCq(pC,GetHandleId(ydt)),1,201.*1.)\n'
    'endif\n'
    'if GetUnitTypeId(ydt)==' + GR + ' and jdt then\n'
    'call SaveReal(tC,BCq(pC,GetHandleId(ydt)),0,0.)\n'
    'call SaveReal(tC,BCq(pC,GetHandleId(ydt)),1,1.01*1.)\n'
    'call SaveReal(tC,BCq(pC,GetHandleId(ydt)),2,15.*1.)\n'
    'call SaveReal(tC,BCq(pC,GetHandleId(ydt)),3,15.*1.)\n'
    'endif\n')
src = before(src, 'call puq(ydt,5,1.)\nset ydt=null\nendfunction', KDT, 'kdt')

# ============================================================================
# 8. LEVEL-UP (Hwt). kmt = the new level (absolute).
# ============================================================================
HWT = (
    'elseif emt==' + SC + ' then\n'
    'call SaveReal(tC,BCq(pC,GetHandleId(Smt)),0,30.*1.)\n'
    'call SaveReal(tC,BCq(pC,GetHandleId(Smt)),1,25.*I2R(kmt)*1.)\n'
    'call SaveReal(tC,BCq(pC,GetHandleId(Smt)),2,(150.+1.*I2R(kmt))*1.)\n'
    'elseif emt==' + EX + ' then\n'
    'call SaveReal(tC,BCq(pC,GetHandleId(Smt)),0,RMinBJ(60.+.2*I2R(kmt),150.)*1.)\n'
    'call SaveReal(tC,BCq(pC,GetHandleId(Smt)),1,RMinBJ(25.+.02*I2R(kmt),35.)*1.)\n'
    'elseif emt==' + WC + ' then\n'
    'call SaveReal(tC,BCq(pC,GetHandleId(Smt)),0,6.*1.)\n'
    'elseif emt==' + SB + ' then\n'
    'call SaveReal(tC,BCq(pC,GetHandleId(Smt)),0,2.*1.)\n'
    'call SaveReal(tC,BCq(pC,GetHandleId(Smt)),1,(200.+I2R(kmt))*1.)\n'
    'elseif emt==' + GR + ' then\n'
    'call SaveReal(tC,BCq(pC,GetHandleId(Smt)),1,RMinBJ(1.+.01*I2R(kmt),4.)*1.)\n')
src = before(src,
             'elseif emt==$48303136 then\ncall SaveReal(tC,BCq(pC,GetHandleId(Smt)),0,kmt*25*1.)',
             HWT, 'hwt')

# ============================================================================
# 9. ROSTER SLOTS 55-59
# ============================================================================
src = after(src, 'set KC[54]=$48304b42\n',
            'set KC[55]=' + SC + '\n'
            'set KC[56]=' + EX + '\n'
            'set KC[57]=' + WC + '\n'
            'set KC[58]=' + SB + '\n'
            'set KC[59]=' + GR + '\n', 'kc')

# ============================================================================
# 10. ATTRIBUTE POOLS - joq=4 STR, uoq=8 AGI, goq=16 INT. Must land before
#     line ~42852 where goq stops holding its constant, hence anchoring on
#     Kerrigan's block. Must agree with 'upra' in the object data.
# ============================================================================
def cat(code_hex, attrvar):
    return ('set Zoq=LoadInteger(wH,' + code_hex + ',0)\n'
            'set oH[Zoq]=BlzBitOr(' + attrvar + ',oH[Zoq])\n'
            'if ' + attrvar + '==4 then\n'
            'set VH[SH]=' + code_hex + '\n'
            'set SH=SH+1\n'
            'elseif ' + attrvar + '==8 then\n'
            'set kH[QH]=' + code_hex + '\n'
            'set QH=QH+1\n'
            'elseif ' + attrvar + '==16 then\n'
            'set NH[YH]=' + code_hex + '\n'
            'set YH=YH+1\n'
            'endif\n')


CAT = (cat(SC, 'goq') + cat(EX, 'joq') + cat(WC, 'joq') + cat(SB, 'goq') + cat(GR, 'joq'))
src = before(src, 'set Zoq=LoadInteger(wH,$48304b42,0)\n', CAT, 'cat')

# ============================================================================
# 11. STARTING ELEMENTS
#     1 Fire 2 Water 3 Wind 4 Earth 5 Wild 6 Energy 7 Dark
#     8 Light 9 Cold 10 Poison 11 Blood 12 Summon 13 Arcane
# ============================================================================
NIQ = ('call NIq(' + SC + ',3,1)\n'      # Wind
       'call NIq(' + SC + ',6,1)\n'      # Energy
       'call NIq(' + EX + ',7,1)\n'      # Dark
       'call NIq(' + WC + ',8,1)\n'      # Light
       'call NIq(' + WC + ',4,1)\n'      # Earth
       'call NIq(' + SB + ',13,1)\n'     # Arcane
       'call NIq(' + GR + ',9,1)\n'      # Cold
       'call NIq(' + GR + ',4,1)\n')     # Earth
src = after(src, 'call NIq($48304b42,13,1)\n', NIQ, 'niq')

# ============================================================================
# 12. HERO CARDS (Po 1..4) and STAT PANEL LABELS (DC 0..n, contiguous from 0)
# ============================================================================
def ico(name):
    return 'ReplaceableTextures' + DBS + 'CommandButtons' + DBS + name + '.blp'


PO = ''
for code_hex, icon, desc, lvl in [
    (SC, 'BTNShaman',
     "|cff00ffffPassive|r: Forked Lightning: When the Hero attacks an enemy it has a 30% chance to call down a chain of lightning that strikes up to 5 enemies in a chain, each struck for |cffff00ffmagic damage|r equal to |cffffcc0025 per Hero level|r plus a percentage of its |cff8fd6ffIntelligence|r. [|cff80ff80Luck|r]",
     "|cffffff00Level Up Bonus|r: Forked Lightning: +25 damage, +1% Intelligence damage."),
    (EX, 'BTNHeroDeathKnight',
     "|cff00ffffPassive|r: Headsman's Toll: The Hero's attacks against an enemy below |cffffcc0025%|r of its maximum hit points deal |cffffcc00+60%|r damage. Both the threshold and the bonus grow with level, to a maximum of |cffffcc0035%|r of maximum hit points and |cffffcc00+150%|r damage. A target cannot be executed again for 1 second.|n|n|cff00ffffPassive|r: Grim Harvest: Killing an enemy restores |cffffcc002%|r of the Hero's maximum hit points and mana.",
     "|cffffff00Level Up Bonus|r: Headsman's Toll: +0.2% execute damage (max +150%), +0.02% execute threshold (max 35%)."),
    (WC, 'BTNChaosWarlord',
     "|cff00ffffPassive|r: Warlord's Presence: All damage the Warchief deals is increased by |cffffcc006%|r for every allied Hero within 900 range, itself included (maximum 5).|n|n|cff00ffffPassive|r: Battle Standard: Every second the Warchief restores hit points to itself and every allied Hero within 900 range, based on its level and |cffff8000Strength|r.",
     "|cffffff00Level Up Bonus|r: Battle Standard: +30 hit points restored per second."),
    (SB, 'BTNVoidWalker',
     "|cff00ffffPassive|r: Arcane Edge: Every attack consumes |cffffcc002%|r of the Hero's maximum mana and unleashes |cffff00ffmagic damage|r equal to a multiple of the mana consumed. Without mana there is no bonus.|n|n|cff00ffffPassive|r: Mana Font: Killing an enemy restores |cffffcc002%|r of maximum mana.",
     "|cffffff00Level Up Bonus|r: Arcane Edge: +1% mana to damage conversion."),
    (GR, 'BTNBlueMagnataur',
     "|cff00ffffPassive|r: Thick Hide: The Grudgebearer takes |cffffcc0015%|r less damage from all sources.|n|n|cff00ffffPassive|r: Mountain's Weight: Its attacks deal bonus |cff00ffffpure damage|r equal to a percentage of its |cffffcc00maximum hit points|r, ignoring armor and block. 1 second cooldown per target.|n|n|cff00ffffPassive|r: Grudge: Banks every point of damage it takes, up to |cffffcc0015%|r of its maximum hit points. Its next attack detonates the whole bank as |cffff00ffmagic damage|r to all enemies within 400 range of the target.",
     "|cffffff00Level Up Bonus|r: Mountain's Weight: +0.01% of maximum hit points (maximum 4%)."),
]:
    PO += ('call SaveStr(tC,BCq(Po,' + code_hex + '),1,"' + ico(icon) + '")\n'
           'call SaveStr(tC,BCq(Po,' + code_hex + '),2,"' + desc + '")\n'
           'call SaveStr(tC,BCq(Po,' + code_hex + '),3,"' + lvl + '")\n'
           'call SaveStr(tC,BCq(Po,' + code_hex + '),4,"24")\n')
src = before(src, 'call SaveStr(tC,BCq(Po,$48304b42),1,', PO, 'po')

DC_COLORS = ['|cffe7544a', '|cffd6e049', '|cff4daed4', '|cff51d44d']
DC = ''
for code_hex, rows in [
    (SC, [('Forked Lightning chance', '%%'), ('Lightning damage per target', ''), ('Lightning damage (% of Intelligence)', '%%')]),
    (EX, [('Execute damage bonus', '%%'), ('Execute threshold (% of max hit points)', '%%')]),
    (WC, [('Damage bonus per nearby ally', '%%'), ('Battle Standard healing per second', ''), ('Total hit points restored', '')]),
    (SB, [('Mana spent per attack', '%%'), ('Mana to damage conversion', '%%')]),
    (GR, [('Stored Grudge', ''), ("Mountain's Weight (% of max hit points)", '%%'), ('Grudge cap (% of max hit points)', '%%'), ('Damage reduction', '%%')]),
]:
    for i, (label, suffix) in enumerate(rows):
        DC += ('call SaveStr(tC,BCq(DC,' + code_hex + '),' + str(i) + ',"'
               + DC_COLORS[i] + label + '|r: ,0,' + suffix + '")\n')
src = before(src, 'call SaveStr(tC,BCq(DC,$48304b42),0,', DC, 'dc')

# ============================================================================
# 13. DAMAGE-METER ATTRIBUTION (only if the 2.9.1+ meter is present).
#     The two passives that create their own damage instance pass their hero
#     rawcode as the attribution id, which would otherwise print the hero name.
# ============================================================================
DMGNAME_ANCHOR = 'elseif b==-3 then\nreturn "|cffccccccOther|r"\n'
meter = 'function DmgName takes integer b returns string' in src
if meter:
    src = after(src, DMGNAME_ANCHOR,
                'elseif b==' + SB + ' then\n'
                'return "|cff8fd6ffArcane Edge|r"\n'
                'elseif b==' + GR + ' then\n'
                'return "|cff8fd6ffGrudge|r"\n', 'dmgname')

# ============================================================================
# 13b. HEALING-METER ROW FIX, ported from the parallel 2.10.1 build.
#      2.9.5 raised the multiboard to 20 rows for the "Healed by:" section, but
#      DmgMbCreate's item-styling loop still stopped at 16, so rows 16-19 never
#      got their style or column widths applied. Not hero work - carried here
#      only so this build is a superset of 2.10.1 rather than a fork of it.
#      Skipped automatically on a base without the healing meter.
# ============================================================================
if 'function DmgMbCreate takes' in src and 'call MultiboardSetRowCount(DmgMB,20)' in src:
    src = swap(src, 'exitwhen r>=16', 'exitwhen r>=20', 'meter-rows')

# ============================================================================
# 14. VERSION BUMP (reads whatever version the input carries)
# ============================================================================
i = src.index('call SetMapName("CHS_v')
cur = src[i + len('call SetMapName("CHS_v'):src.index('"', i + 22)]
src = swap(src, 'call SetMapName("CHS_v%s")' % cur,
           'call SetMapName("CHS_v%s")' % NEW_VERSION, 'ver-mapname')
src = swap(src, 'set jm[yaq]="CHS v%s"' % cur,
           'set jm[yaq]="CHS v%s"' % NEW_VERSION, 'ver-table')

# ---------------------------------------------------------------- output ----
open(OUT, 'w', encoding='utf-8', newline='').write(src)

print('%s -> %s   (version %s -> %s)' % (SRC, OUT, cur, NEW_VERSION))
print('lines: %d  (+%d)' % (src.count('\n') + 1,
                            src.count('\n') - open(SRC, encoding='utf-8').read().count('\n')))
print('damage meter present: %s' % meter)
for c in CODES:
    print('  %s (%s): %d references' % (c, rc(c), src.count(rc(c))))
