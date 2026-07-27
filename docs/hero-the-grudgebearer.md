# The Grudgebearer

| | |
|---|---|
| Rawcode | `H0GR` |
| Base unit | `Hpal` (Paladin — melee hero chassis) |
| Primary attribute | Strength (melee) |
| Start stats | STR 46 / AGI 20 / INT 16 |
| Growth | +5.4 / +2.6 / +2.2 |
| Attack | 24 + 1d10, cooldown 1.60 |
| Move speed | 290 |
| Model / icon | `Units\Creeps\MagnataurBlue\MagnataurBlue.mdl` / `BTNBlueMagnataur` |
| Starting elements | Cold ×1, Earth ×1 |
| Roster slot | `KC[59]` |

A tank whose offence *is* its defence. Two heroes already react to being hit — Stone Edge
reflects a share of Block instantly, Reinforced Bone grants an immunity window — but
nothing in the roster **banks** damage and spends it later. The Grudgebearer soaks a wave,
then hands the whole bill to the next thing it swings at.

## Passives

**Thick Hide** — The Grudgebearer takes **15%** less damage from all sources.

**Mountain's Weight** — Its attacks deal bonus **pure damage** equal to **1% of its maximum
hit points** (**+0.01% per level**, up to 4%), ignoring armor and block. A target can only be
hit by it once per **1 second**.

**Grudge** — Banks **every point** of damage it takes. Bank capacity is **15% of maximum hit
points, +0.2% per level, uncapped** — 55% at level 200, 135% at level 600. Its next attack
detonates the whole bank as **magic damage** to all enemies within **400** range of the target,
and clears it.

**Level Up Bonus** — Mountain's Weight: +0.01% of maximum hit points (maximum 4%). Grudge: +0.2% bank capacity.

## Why it was reworked

The first version scaled off **attack damage** — the bank was capped at 5× it, and the payload
was magic. Both were wrong for this chassis:

- This hero is built to be the worst attacker of the five (24 + 1d10, 1.60s cooldown, lowest
  Agility). Capping its payload against its weakest stat meant the cap was tiny, the bank
  overflowed within a couple of creep hits, and everything above it was silently discarded.
  Tanking *harder* bought you nothing.
- The dump was magic damage, which round-50 creeps cut by **80%** (200 magic protection). A cap
  of 5× a low attack damage, then quartered, is invisible.

Everything now measures in **maximum hit points** — the stat a tank actually stacks — and the
on-attack half is **pure**, so armor and Block do not touch it.

| max HP | Mountain's Weight per attack (L200) | Grudge bank capacity (L200, 55%) |
|---|---|---|
| 200,000 | 6,000 | 110,000 |
| 500,000 | 15,000 | 275,000 |
| 1,000,000 | 30,000 | 550,000 |

## Implementation notes

- **"Pure damage" is `set qZ[pZ]=(qZ[pZ]+x)*1.` inside `jQt`.** `jQt` runs on
  `EVENT_UNIT_DAMAGED`, i.e. *after* armor, Block and magic protection have all been applied,
  so anything added there is untaxed. This is exactly how H01H's Cannibal Frenzy — the card
  that advertises "ignores armor and block" — is implemented (line 39259). It is also why the
  old design underperformed: `mEq` can only deal `DAMAGE_TYPE_MAGIC` or `NORMAL`, both taxed.
- Mountain's Weight carries a **1-second per-target cooldown** (`boq(JX,…)`), the same guard
  the roster puts on every percentage-based on-attack effect (Horsepower 2s, Cannibal Frenzy
  0.35s). Without it, a percentage-of-HP effect deletes bosses.
- The AoE dump stays magic because `mEq` has no pure option — but its size now comes from a
  max-HP-scaled bank rather than an attack-damage-scaled one, so it survives the ×0.20 tax.
- Bank capacity is `I2R(BlzGetUnitMaxHP(CX))*(.15+.002*I2R(GetHeroLevel(CX)))` — still an
  `RMinBJ` ceiling on the stored total, but the percentage itself has no upper clamp, so the
  bank keeps pace with level instead of saturating. `BlzGetUnitMaxHP` returns an integer,
  hence the `I2R`.
- Thick Hide is a flat 15% with no level term. The previous +0.01%/level gained two percentage
  points across 200 levels — literally imperceptible, and not worth a stat-panel row pretending
  otherwise.
- The live bank is written to `pC[0]`, which the stat panel renders — the panel doubles as a
  charge meter you can watch fill.
