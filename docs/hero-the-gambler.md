# The Gambler

| | |
|---|---|
| Rawcode | `H0GB` |
| Base unit | `Nfir` (Firelord) |
| Primary attribute | Agility (ranged) |
| Start stats | STR 30 / AGI 35 / INT 27 |
| Growth | +3.0 / +5.0 / +4.0 |
| Starting element | Fire ×1 |
| Roster slot | `KC[53]` |

## Passives

**Loaded Dice** — The Gambler's Luck is increased by **25%**. This adds `+0.25` to the hero's
luck multiplier (`VO` key 5) at creation, so *every* `[Luck]`-tagged proc in the map benefits.
Grows **+0.2% per level**.

**Double or Nothing** — When the Hero kills an enemy, it has a **15%** chance (+0.05%/level,
improved by Luck) to win **double** the gold reward, and a flat **5%** chance to lose the reward
entirely. Shows a `DOUBLE!` / `BUST!` floating text to the owner.

## Implementation notes

- Kill hook lives in the reward function `eCt`, after all wave multipliers, before the gold
  grant — so the doubled/zeroed amount is the final payout. Fires for summon kills too (the
  hero is credited as `Gh[pid]`), consistent with how gold/XP are credited map-wide.
- Stat panel (`pC` / `DC`) shows Double-or-Nothing chance, total gold won, and total gold lost.
- The displayed chance is the base value; the actual roll additionally multiplies in Luck
  (matches the map's convention for luck-scaled displays).
