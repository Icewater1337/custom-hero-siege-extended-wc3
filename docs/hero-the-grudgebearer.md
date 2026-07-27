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

**Thick Hide** — The Grudgebearer takes **10%** less damage from all sources
(**+0.01% per level**, up to 20%).

**Grudge** — Stores **40%** of all damage it takes (**+0.05% per level**, up to 60%), to a
maximum of **5×** its attack damage. Its next **attack** releases the entire stored Grudge
as **magic damage** to all enemies within **400** range of the target, and clears it.

**Level Up Bonus** — Grudge: +0.05% of damage stored. Thick Hide: +0.01% damage reduction.

## Implementation notes

- Both halves of the defensive side live in one block in `jQt`'s mitigation section, keyed
  on `OX` (the *target's* type id) rather than `HX`. Thick Hide applies first, so Grudge
  banks the damage that is actually taken, not the pre-mitigation figure — tanking harder
  does not secretly inflate the payload.
- Because `jQt` runs on `EVENT_UNIT_DAMAGED`, `qZ[pZ]` there is the true final damage after
  armor, Block and magic protection. That makes the stored number honest and keeps the
  effect meaningful against every damage type, not just auto-attacks.
- The store is capped at `UIq(CX,0)*5.` — five times the hero's own full attack damage. The
  cap is tied to the player's build rather than to a flat constant, so it scales with the
  hero instead of going stale, and a single enormous hit can never be converted into a
  wave-deleting nuke.
- Both per-level terms are clamped with `RMinBJ` (60% stored, 20% reduction). Nothing here
  keeps growing at the level-600 cap.
- The release is dealt through the map's deferred AoE helper
  `mEq(hX, x, y, stored, 400., true, H0GR, true, false)` — the `true` in position six sets
  `j=3`, so the burst is proc damage and cannot re-enter the proc block. The store is zeroed
  in the same block, so it cannot be double-spent.
- `mEq`'s attribution id makes the burst its own damage-meter row; the patch adds a
  **"Grudge"** entry to `DmgName`.
- The live stored value is written to `pC[0]`, which the stat panel renders — so the panel
  doubles as a charge meter you can watch fill up.
