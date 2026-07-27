# The Executioner

| | |
|---|---|
| Rawcode | `H0EX` |
| Base unit | `Hpal` (Paladin — melee hero chassis) |
| Primary attribute | Strength (melee) |
| Start stats | STR 40 / AGI 24 / INT 18 |
| Growth | +4.8 / +3.0 / +2.4 |
| Attack | 22 + 1d10, cooldown 1.45 |
| Move speed | 310 |
| Model / icon | `Units\Undead\HeroDeathknight\HeroDeathknight.mdl` / `BTNHeroDeathKnight` |
| Starting elements | Dark ×1 |
| Roster slot | `KC[56]` |

The roster had **no low-health payoff at all**. Two heroes scale off the target's health
bar and both scale off the part that is still full — Horsepower takes 6% of *maximum* HP,
Cannibal Frenzy 2.5% of *current* HP. The Executioner is the mirror image: it does nothing
special to a healthy enemy and becomes lethal once the bar is nearly empty. That makes it
the roster's first genuine boss-finisher and a real threat in a duel.

## Passives

**Headsman's Toll** — The Hero's **attacks** against an enemy at or below **25%** of its
maximum hit points deal **+60% damage**. A target cannot be executed again for **1 second**.

Both halves grow with level and **both are hard-capped**:

| | at level 1 | per level | **cap** | cap reached at |
|---|---|---|---|---|
| execute threshold | 25% of max HP | +0.02% | **35% of max HP** | level 500 |
| damage bonus | +60% (×1.6) | +0.2% | **+150% (×2.5)** | level 450 |

At level 200 that is a 29% window for ×2.00 damage.

**Grim Harvest** — Killing an enemy restores **2%** of the Hero's maximum hit points and
**2%** of its maximum mana.

**Level Up Bonus** — Headsman's Toll: +0.2% execute damage, +0.02% execute threshold.

## Implementation notes

- Headsman's Toll is a pure **amplification of the hit that is already happening**
  (`set qZ[pZ]=qZ[pZ]*…`), not a second damage instance. It therefore creates no new
  damage event, cannot recurse, and needs no internal cooldown — the safest of the six
  proc archetypes this codebase offers.
- It runs in `jQt`, which fires on `EVENT_UNIT_DAMAGED`, so `qZ[pZ]` is the real
  post-armor, post-block, post-magic-protection damage. The multiplier applies to what the
  target would actually have taken.
- **The multiplier is deliberately below the map's own ceiling, and this hero was retuned
  once for exactly that reason.** The largest damage multiplier anywhere in the base script
  is ×3 (`$41304333`), and even that is gated behind a 2-second ability cooldown and a
  timing window; the ×2 at ~27127 needs a 20% roll. The first version of Headsman's Toll
  was ×2.5 rising to ×5.0 with **no roll and no cooldown** — above everything the map
  ships. It now runs ×1.6 → a hard **×2.5**, with a **1-second per-target internal
  cooldown** keyed on `boq(JX,…)`, matching Horsepower's convention.

- **Growth was moved off the multiplier and onto the threshold.** The crit engine `LAt()`
  resolves at line ~26660, well before `jQt`, so anything written here multiplies an
  already-critted hit: at level 200 the old ×3.5 on top of a ×3 crit was ×10 of the final
  post-armor damage. The threshold (25% → 35%) is a bounded axis — a wider execute window
  can never compound with anything.
- The health test uses `GetWidgetLife(CX) <= GetUnitState(CX,UNIT_STATE_MAX_LIFE)*.2`
  (both reals — `BlzGetUnitMaxHP` returns an integer and would need a conversion).
- Grim Harvest is 2% and not more because it has no cooldown and a wave is 25+ kills per
  player: at 2% it restores roughly half a health bar over a full wave, which is sustain
  rather than immortality.
- Grim Harvest lives in the reward function `eCt` and is credited through `ACt`, so summon
  and illusion kills count, consistent with how gold and XP are credited map-wide.
