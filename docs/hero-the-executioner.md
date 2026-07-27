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

**Headsman's Toll** — The Hero's **attacks** against an enemy at or below **20%** of its
maximum hit points deal **+100% damage**. A target cannot be executed again for **1 second**.

Both halves grow with level and **neither is capped**:

| | at level 1 | per level | at level 200 | at level 400 |
|---|---|---|---|---|
| execute window | 20% of max HP | +0.2% | 60% of max HP | 100% — always on |
| damage bonus | +100% (×2.0) | +0.5% | +200% (×3.0) | +300% (×4.0) |

**Grim Harvest** — Killing an enemy restores **2%** of the Hero's maximum hit points and
**2%** of its maximum mana.

**Level Up Bonus** — Headsman's Toll: +0.5% execute damage, +0.2% execute threshold.

## Implementation notes

- Headsman's Toll is a pure **amplification of the hit that is already happening**
  (`set qZ[pZ]=qZ[pZ]*…`), not a second damage instance. It therefore creates no new
  damage event, cannot recurse, and needs no internal cooldown — the safest of the six
  proc archetypes this codebase offers.
- It runs in `jQt`, which fires on `EVENT_UNIT_DAMAGED`, so `qZ[pZ]` is the real
  post-armor, post-block, post-magic-protection damage. The multiplier applies to what the
  target would actually have taken.
- **Both terms are uncapped by explicit design decision.** The multiplier passes the map's own
  ×3 ceiling at level 200 and the execute window reaches 100% of maximum hit points at level
  400, from which point the bonus is unconditional. That is intended — but note the crit engine
  `LAt()` resolves at line ~26660, well before `jQt`, so this multiplies an already-critted hit.
  The **1-second per-target cooldown** (`boq(JX,…)`) is what keeps it bounded against a single
  target, and it was deliberately retained.
- The health test uses `GetWidgetLife(CX) <= GetUnitState(CX,UNIT_STATE_MAX_LIFE)*.2`
  (both reals — `BlzGetUnitMaxHP` returns an integer and would need a conversion).
- Grim Harvest is 2% and not more because it has no cooldown and a wave is 25+ kills per
  player: at 2% it restores roughly half a health bar over a full wave, which is sustain
  rather than immortality.
- Grim Harvest lives in the reward function `eCt` and is credited through `ACt`, so summon
  and illusion kills count, consistent with how gold and XP are credited map-wide.
