# Custom Hero Survival v2.8.6 — Gameplay Bug Report

Analysis of `CHS_v2.8.6.w3x` (map: **Custom Hero Survival**, dated 7 May 2026). The map is protected, so the 50,428-line JASS script was extracted from the MPQ archive and analyzed in obfuscated form (variable names are meaningless, but all logic, arithmetic, string literals, and native calls are intact). Object-editor data (811 abilities, 549 items, 270 units) and all 27,508 tooltip strings were extracted and cross-checked as well.

Every finding below was independently re-verified against the full script/data by an adversarial review pass; 12 additional candidate findings were **rejected** during verification (listed at the end). Line numbers refer to the extracted `war3map.j`.

A recurring root cause: **JASS `and` binds tighter than `or` and there are no parentheses in many mixed conditions.** At least nine separate bugs below are operator-precedence mistakes of the form `itemCheck and A or B`, which parses as `(itemCheck and A) or B` instead of the intended `itemCheck and (A or B)`.

---

## 1. Critical — broken systems and game-warping bugs

### 1.1 The 50,000g item I07M zeroes ALL of its holder's damage
**L26891 (damage engine `Ykt`)** — `if utq(hX,'I07M') or GetUnitAbilityLevel(hX,'Assk')>0 and hX==CX then set qZ[pZ]=0.`
Both the item I07M (+1750 strength, "Immunity to self-inflicted damage") and the Earth-element ability `Assk` are only supposed to negate **self-inflicted** damage. Due to precedence this parses as `holdsItem OR (hasAbility AND self-hit)` — the `source==target` condition doesn't apply to the item. Result: **any hero carrying I07M deals 0 damage with every attack and every spell** for as long as the item is in inventory. Intended: `(utq(hX,'I07M') or GetUnitAbilityLevel(hX,'Assk')>0) and hX==CX`.

### 1.2 Spell-reflect (Retaliation Aura / "Wizardbane") always deals 0 damage
**L37948-49 (damage engine) + L40169 (`qtt`)** — The aura A0A9 (item I0B1; also creep "wizardbane" rounds) copies spells back at the attacker for 25% + 2.5%/level damage (100% at 30). The intended fraction is stored in `Yw[]`, but the damage engine multiplies the reflected damage by `LoadReal(tC,sr,nX)` — and the hashtable key `sr` is **written nowhere in the entire script** (it appears exactly 3 times: declaration, key allocation, and this read). The load always returns 0.0, so **every mirrored spell deals exactly 0 damage at every level**. The visuals and non-damage effects (stuns/slows) still apply, masking the bug. Intended: multiply by `Yw[cO[nX]]`.

### 1.3 Same system: use-after-null corrupts the dummy-caster pool
**L36976-78 (`jjq`) and L43737-39 (`t0t`)** — Both destructors of the spell-mirror record system run `set Nw[i]=null` **before** `SaveInteger(tC,cO,GetHandleId(Nw[i]),0)`. `GetHandleId(null)` is 0, so the real dummy's handle→record mapping is never cleared (the twin destructor `t7t` at L43897-99 does it in the correct order). Because dummy casters are pooled and recycled, stale mappings accumulate: unrelated dummy-cast spells can silently deal 0 damage when a recycled dummy still matches a mirror record, and record indexes get double-freed. Intermittent and worsens over long games.

### 1.4 PvP betting is completely non-functional (infinite loop at init)
**L3142-48 (`B4q`, called via `ExecuteFunc` at L50012)** — The dialog-creation loop has no counter increment:
```
local integer d4q=0
loop
exitwhen d4q>4
set bq[d4q]=DialogCreate()
endloop
```
The thread spins until the op-limit kills it; `bq[1..4]` stay null forever. The betting menu (built on `bq[1]`, L14075-88), the Gold/Cancel menu (`bq[2]`) and the 25%/50%/100% bet-size menu (`bq[3]`) are all created on null dialogs, and their click triggers (L3686, L5314, L47407, L47648, L48871) are registered on null dialogs. **When the "PVP Betting" mode is enabled, no betting UI ever appears and bets can never be placed.** Fix: add `set d4q=d4q+1`.

### 1.5 Hidden global ×0.7 damage multiplier; Bamboo Stick's defense is dead code
**L38616 (damage handler `jQt`)** — `if GetUnitAbilityLevel(CX,'A0CM')>0 and HX=='BBHH' or oX!=8 then set qZ[pZ]=qZ[pZ]*.7`
`oX` is the damage source's owner player id — and **no unit in the map is ever owned by Player(8)** (heroes are players 0-7; creeps/pets belong to Player 11; dummies to their caster or neutral). So `oX!=8` is always true and **every damage event in the game is silently multiplied by 0.7**, while the intended condition (defender has Conqueror's Bamboo Stick's ability vs. the BBHH summon-boss) is unreachable dead code. The map's balance presumably grew around this global 30% reduction, but the item's advertised protection does nothing.

### 1.6 Sylvan Construct hero gets a free permanent 30% damage reduction
**L38681 (damage handler `jQt`)** — `utq(aX,'I0B6') and (not IsUnitType(CX,UNIT_TYPE_HERO)) or GetUnitTypeId(CX)=='BBHH'`
Item I0B6 (15,000g): "Your Hero and non-Hero [Summon] units take 30% less damage." The `or BBHH` clause was meant to extend the item's protection to the summon-type hero BBHH, but as parsed, **any BBHH (Sylvan Construct) takes 30% less damage from everything without owning the item**. Its own hero description lists no such passive. Intended: `utq(aX,'I0B6') and ((not IsUnitType(CX,UNIT_TYPE_HERO)) or GetUnitTypeId(CX)=='BBHH')`.

### 1.7 The glory cost of 14 endgame items is almost never charged
**L24045-24136 (`YMt`, 14 parallel branches)** — Each hybrid gold+glory token (I06W, I070, I06Z, I0D8, I0A4-I0AB, I0AG, I0D6; 10,000-25,000 glory each) is granted via:
`if slot0Free or slot1Free or slot2Free or slot3Free or slot4Free or slot5Free and OFq(glory) then`
Precedence + short-circuit: the glory check `OFq` only runs when slots 0-4 are ALL occupied and only slot 5 is free. **With any of the first five inventory slots open (the normal case), the item is granted and glory is never deducted.** The advertised glory price of the strongest item tier is effectively decorative.

### 1.8 Three wave types never cast their signature spells (wrong order strings in creep AI)
**L30866, L30815, L30971 (`d6q` creep AI)** — The periodic creep AI issues cast orders by name, but three don't match any ability the creeps hold, so the orders silently fail:
- **"Cyclone" waves**: creeps have A05X (Channel-based, real order `creepanimatedead` per its own data and the map's own registration at L49487), but the AI orders `cyclone`.
- **"Acid Spray" waves**: creeps have ANhs (negative-heal spray, real order `healingspray`, cf. L49276), but the AI orders `channel`.
- **"Icy Breath" waves**: creeps have A046 (base Breath of Frost, real order `breathoffrost`, cf. L49445), but the AI orders `breathoffire`.
These waves are announced with their spell name but **never cast it** — all three wave types are far easier than designed. (A fourth claim of this type, Lightning Shield/"slow", was checked and refuted — that order string is actually correct.)

### 1.9 Big Bad Voodoo becomes free at level 30 → chainable mass invulnerability
**Object data `AOvd`, `amcs` levels 21-30** — Mana cost climbs +45/level to 1000 at level 20, then **descends** -100/level to **0 at level 30** (clearly an editor auto-fill entered in the wrong direction; every comparable ultimate ascends steeply post-20, e.g. AUin→4000, AHpx→4500). With its flat 3s cooldown and 20s duration, a level-30 Voodoo hero can chain-channel **permanent invulnerability for all allied heroes, units and summons in the area** at zero cost. Verdict: PLAUSIBLE-to-confirmed (data is unambiguous; only author intent is technically unprovable).

---

## 2. Significant balance bugs

### 2.1 Everyone gets item I03B's ignite DoT for free
**L26902 (also L26912, L26932, L26786 pattern family)** — The burn-proc condition parses so that the "has ability A06Q (item I03B's hidden ignite) and its cooldown is ready" gate binds only to the last of four or-disjuncts. In general combat, **any hero's normal attacks apply the ignite: a magic DoT of 10×(spell power + physical power) per second for ~3s on every hit, without owning the 900g item**. Actual owners gain little over non-owners, and creeps stamp cosmetic burn debuffs with every attack.

### 2.2 Light/Dark element counting is wrong in four places (precedence family)
The element aggregator `CRq`/`Wvq` decides how many "Light"/"Dark" spells a unit has — these counts scale several damage/armor effects and pick the Avatar Spirit hero's (O003) form. The 25,000g item I0AM is supposed to merge Light↔Dark **only while held**. Four sites drop that requirement on one side:
- **L9697**: every unit gets **+1 Dark count unconditionally** (the +1 was supposed to require I0AM; only the Light direction checks the item).
- **L9733**: item-granted Light bonuses always merge into Dark queries without I0AM.
- **L9636 (`Wvq`)**: an ability's Dark element value counts toward **Light** queries unconditionally (and for gem holders it *replaces* rather than adds the ability's own Light value).
- **L9717**: the Paladin H002's "Lightbringer" perk (+1 Light per 10 levels) is granted **to the Dark count of any I0AM holder** of any hero.
Net effect: Dark/Light-scaling effects (A07Q aura, the +25%-damage-per-Dark-count scaler at L20489, A07X at L20489, tooltip readouts, O003's form comparison) run permanently skewed. The correctly-parenthesized sibling `xvq` (L9662) shows the intended logic for all four.

### 2.3 Xesil's Legacy resets [Stable] cooldowns despite its own rule
**L9827 (`RUt` cooldown calculation)** — The [Stable] tag exists to keep safety-valve spells (Reset Time, Wind Walk, reincarnation passives…) on fixed cooldowns, and hero H01D's description explicitly says its 20%+0.1%/level reset "does not reset the cooldown of spells with the [Stable] tag." Precedence puts the `not Mt[ability]` exclusion on the item branch only, so **the H01D hero resets Stable spells anyway** — e.g. Reset Time's own cooldown zeroed roughly one cast in five.

### 2.4 Waves 28/38 can roll the "Last Breaths" elite wave in full lobbies
**L34690 (`dst`)** — `if GL==28 or GL==38 or GL==48 and hst()<5` — the under-5-players gate only binds to wave 48. In 5-8 player games, waves 28 and 38 each have a 1/3 chance to become a "Last Breaths" wave (2-5 creeps that cannot die while buffed), a wave type that is restricted to small lobbies everywhere else in the code.

### 2.5 Wave after a Thorns/Reflection/Wizardbane wave can lose its melee procs
**L32483 + ~20 parallel guards in `ast`/`rst`** — The guards compare `HX` — a damage-engine global holding the unit-type of the **most recent damage source** (stale combat data) — instead of the wave-type variable `eL` (which the fourth check in the same condition correctly uses). When the previous wave was one of the special types n01H/n03C/n03B, the stale value suppresses granting Critical Strike, Cruelty, Cutting, Pulverize, Bash, etc. to the next wave: **random, invisible difficulty drops**.

### 2.6 Chaos Rune and Eruption randomly fizzle (inclusive-bound off-by-one)
**L8897-99 (`DCt`, Chaos Rune) and L28043 (`n7q`, Eruption A0DA)** — Both pick random targets with `BlzGroupUnitAt(g, GetRandomInt(0, BlzGroupGetSize(g)))`. `GetRandomInt` is inclusive, valid indexes are `0..size-1`, so with probability 1/(N+1) the pick is null and the strike/cast is silently consumed. Chaos Rune loses one of its three casts 50% of the time with one unit nearby; each Eruption pulse vs. a lone boss has a 12.5% chance to do nothing. The same file uses the correct `GetRandomInt(0,size-1)` idiom elsewhere (L8739/L8742).

### 2.7 Hero O006 can never get both Blood and Arcane absolute abilities
**L10676 (`Nlq`)** — The element-index scan loop is bounded `exitwhen klq>10 or CC[klq]==Vlq`, but the table stores Blood at index 11 and Arcane at index 13. Both resolve to klq=11, sharing one "already acquired" flag: **whichever is rolled first permanently locks the other out of the every-25-levels rotation**, and Arcane's acquisition message prints "[Blood] absolute ability acquired." A parallel scan at L12487 with an `if <=10` guard means Blood/Arcane starting picks set no flag and show no message at all.

### 2.8 Ensnare / Wind Rune grant item I0BW's unique buff without the item
**L40469 (`kEt`)** — `utq(EEt,'I0BW') and cast=='AEer' or cast=='ANen' or cast=='A075'` — the item check only guards Entangling Roots. Any hero casting the purchasable Ensnare (I03A) or triggering the area-root effect receives I0BW's [Unique] +35 physical power for 15s free; with Ensnare's ~19.5s cooldown this is a near-permanent stat boost.

### 2.9 Cold Rune's damage-amp is permanent for ~half the affected creeps
**L21590-21604 (`mVq`)** — The rune stacks +10%/second damage-taken on units inside; the cleanup iterates the group by index while removing units, so removal-compaction skips every other unit. **About half the creeps keep up to +100% damage-taken for the rest of their lives** (player-favoring).

### 2.10 Evade-nova item I08Z fires on ~35% of its mana cost
**L24920/L24929 (`NDt`)** — The proc gates on `mana > 7*level` but deducts `20*level` (the tooltip's stated cost). The nova fires at full strength even when the hero can't actually pay; the deduction clamps at 0.

### 2.11 "Learnability" writes a hidden, purchase-order-dependent XP multiplier
**L8300-08 (`yZt`, ability A02W)** — Besides its correctly-implemented advertised bonus (+1% XP per level, applied at L37459), the purchase handler overwrites a second, undocumented XP multiplier with `.05+.005*(levelDelta)`. Level one-at-a-time → always +5.5%; bulk-buy N levels in one transaction (or the hero-copy path) → up to +19.5% at the same ability level. Two identical heroes can have different XP rates depending on how they clicked the shop.

### 2.12 Battle Royale: "random team" players can be excluded from the fight
**L39501 (`Yht`)** — Leftover random-team players are assigned `GetRandomInt(0,BP)` where valid premade team indexes are `0..BP-1`. With probability 1/(teams+1) the player lands in a phantom slot: if solo-FFA players exist they get silently fused onto one of their teams; otherwise **the player is left at base, allied to everyone, and never enters the round**.

### 2.13 Spirit Link can never be rolled by "cast a random spell" effects
**L49250 (`YIq` registration)** — Registered with the misspelled order string `"spirtlink"`; `OrderId` returns 0, and the pool-builder guard `OrderId(s)!=0` silently drops it from the random-spell pools used by every random-cast mechanic. (Its direct cast path works; only the random pools lose it.)

### 2.14 Cleave can roll on ranged/caster waves that were meant to be excluded
**L34531 (`dst`)** — `(not f9q(eL)) or (not F9q(eL))` is a tautology (the two sets are disjoint); the intended operator was `and`. ~1 in 20 excluded waves carries Cleaving Attack anyway. Tempered by the fact that ranged attackers don't trigger Cleave often; still contrary to design and to the wave announcements.

### 2.15 Truestrike item I06B sabotages the Truestrike aura
**L24986 (`OZt`)** — Tooltips state "Different sources of Truestrike do not stack," but the exclusion parses as `I06B or (I0BN and no-aura)`. A hero owning both the AEar aura (15% miss-through at level 30) and item I06B (10%) gets the **item's 10% instead of the aura's 15%** — buying the item makes the hero worse.

---

## 3. Minor / cosmetic bugs

- **3.1 Blink Strike lands in the wrong spot** — L19706-07 (`yNq`, A08J/A06I): the Y offset uses `Cos` instead of `Sin` (`target + (80cosθ, 80cosθ)`). Damage still applies, but the hero can land stacked on the target or displaced diagonally, sometimes facing away from it.
- **3.2 Tether/leash snaps units to the east edge** — L11435-44 (`jvq`, buff `Bclf`): `Atan2` returns radians but the code multiplies by `bj_DEGTORAD` before `Cos`/`Sin` (treating radians as degrees). Every unit leaving the 400-radius is teleported to ~the due-east point of the circle instead of back where it exited (up to ~800 units sideways).
- **3.3 Backstab's percent bonus never applies** — L26269 (`Ykt`, A0D0): `qZ*(1.+.05*I2R(vkt))+20*xkt`, but local `vkt` is provably 0 here (first assignment is later; JASS is case-sensitive, `Vkt` is a different variable). The advertised 5%/level multiplier (up to +150%) is a no-op; only the flat +20/level applies. Intended variable: `xkt` (the ability level, matching the tooltip's 5%/level).
- **3.4 Observer row of the Battle Creator UI collapses** — L10271 (`rxt`): precedence makes the `(Pu==0, Uu==1)` layout branch unreachable; all 8 observer-slot indicator frames stack at y=0.51 on top of the Observers/Solo buttons instead of a 2×4 grid.
- **3.5 Illusion item I03R procs at 74%, tooltip says 75%** — L40046 (`Tbq`): `GetRandomInt(1,100)<75` (sole `<` outlier; every sibling uses `<=`).
- **3.6 ~9.5% of hints are blank** — L47189-210: `jq[7]` and `jq[15]` are never assigned but the hint roll is `GetRandomInt(1,21)`; players regularly see an empty "Hint:" line.
- **3.7 H000's thunderbolt proc rolls GetRandomInt(0,100)** — L38959: 101 outcomes instead of 100 (~20.8% instead of 20%); the only 0-lower-bound roll in the file. (PLAUSIBLE — imperceptible in practice.)
- **3.8 Item I086's luck formula is transposed** — L24771: `30*luckMult + luckFlat` where all eleven sibling procs use `30 + luckFlat*luckMult`. A few percentage points of skew. (PLAUSIBLE — intent not pinned down.)
- **3.9 Chain Lightning's bounce cadence hiccups at 21-29** — object data `AOcl` field `Ocl2`: the "+1 target per 2 levels" pattern repeats 11 a third time at level 21; odd levels 21-29 get one fewer bounce than the cadence implies. Converges to the same value (16) at 30; tooltips display the actual values. (PLAUSIBLE — minor.)

---

## 4. Tooltip vs. actual-value mismatches (verified against live data)

| Item | Tooltip claim | Actual | Notes |
|---|---|---|---|
| **Savage Totem (BBCW)** | +25,000 HP | **+60,000 HP** (35,000 from engine ability A0QQ + 25,000 added again by script L15933-42) | The one *gameplay-significant* tooltip bug: the item is 2.4× stronger than advertised. Its stale Description also claims 1500 mana cost vs. actual 250. |
| Moonstone (I03O) | Description: "+1500 mana" | +20,000 mana, +25 magic power, +300 mana/s | Stale Description (ground-item info panel); shop/inventory Ubertip is correct. |
| Heart of Darkness (I04V) | Description: 60s cooldown, 0.01s stun | 15s cooldown, 0.5s stun | Stale Description; Ubertip correct. |
| Book of Necromancy (I06J) | Description: 50s cooldown | 24s | Stale Description; Ubertip correct. |
| Anti-Magic Flag (I04Q) | Description: 10s immunity, 60s cooldown | 6s immunity, 36s cooldown, + undocumented buff-strip | Stale Description; Ubertip correct. |
| Blessed Striders (I0DB) | Description: 6s cooldown (+old stats) | 11s cooldown | Only case where the stale text *flatters* the item. |
| Conqueror's Bamboo Stick (I0C2) | Description: 30s cooldown (+old effects) | 25s cooldown | Stale Description; Ubertip correct. (See also bug 1.5 — its summon-defense clause is dead code.) |

---

## 5. Candidate bugs checked and rejected (for completeness)

During verification these initially-suspicious findings were **refuted** with concrete evidence — listed so they aren't re-reported:

- All `x - x/N*N` sites — the standard JASS modulo idiom, not truncation bugs.
- Bash (A06S) stun tooltip "0.20s" — correct: the stun dummy-casts A06T which has `alev=1` and is hardcoded to level 1; only its damage field is overridden, so the 0.2s level-1 stun applies exactly as advertised.
- "Speed Freak" round-timestamp `Bt+R2I(1.6)` — the constant is in ticks (aligning with a 0.05s timer), and the 8-second window matches the hero's tooltip exactly.
- Mana-cost-increase debuff re-application (L39946) — per-application stacking is the advertised behavior ("This effect… stacks"); the identical if/else branches are dead but harmless.
- Boss round "+300% gold/xp" announcement vs ×3 payout — loose colloquial phrasing; preview and payout agree everywhere.
- Lightning Shield creep AI order "slow" (L31506) — the custom ability's order really is `slow`; correct.
- Lucky Trigger `JD==1` duplicate (L34698) — redundant but harmless duplicate in an or-chain.
- Tome purchase `GetUnitAbilityLevel()>=0` (L27771) — always-true but the enclosing logic still behaves as designed.
- %-HP damage buff-immunity checks (L25447), votekick loop bound (L44174), mana-gem I01Q price inversion, creep-roster duplicate indexes 45-47 (L17836), summon attack-speed `Leq/2` truncation (L15105), consume-at-full-HP check (L19602) — each examined; behavior matches design or has no player-visible effect.

---

## Methodology

Extracted `war3map.j`, object data (`.w3a/.w3u/.w3t/...`), and `war3map.wts` from the MPQ (protected header patched, files recovered by known-name hash). Ten parallel reviewers audited the script in 5,000-line slices alongside three data analysts (ability level progressions, tooltip cross-check, item/unit data); every candidate finding was then re-verified by independent adversarial reviewers with full-corpus access, and contested verdicts were resolved manually against the primary data. 56 raw findings → 43 verified (40 confirmed, 3 plausible) → ~40 distinct bugs after merging duplicates.
