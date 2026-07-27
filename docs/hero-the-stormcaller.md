# The Stormcaller

| | |
|---|---|
| Rawcode | `H0SC` |
| Base unit | `Hjai` (Jaina — ranged hero chassis) |
| Primary attribute | Intelligence (ranged) |
| Start stats | STR 24 / AGI 26 / INT 42 |
| Growth | +4.5 / +4.5 / +5.5 |
| Attack | 14 + 1d12, cooldown 1.55 |
| Move speed | 300 |
| Model / icon | `units\orc\Shaman\Shaman.mdl` / `BTNShaman` |
| Starting elements | Wind ×1, Energy ×1 |
| Roster slot | `KC[55]` |

The roster's only *chaining* damage hero. Every other area passive in the map
(Psionic Storm, Moon Chakrum, Bladestorm, Disease Cloud) hits everything inside a
uniform radius; Forked Lightning instead hops between a bounded number of **distinct**
targets, so it reaches enemies that are spread out and cannot be dodged by spacing.

## Passives

**Forked Lightning** *(proc)* — When the Hero **attacks** an enemy, a **30%** chance
(improved by Luck) to call down a chain of lightning that strikes up to **5** enemies
(the target plus four arcs). Each enemy struck takes **magic damage** equal to
**25 × Hero level**, plus a percentage of the Hero's **Intelligence**
(**150% + 1% per level** — 350% at level 200). `[Luck]`

**Level Up Bonus** — Forked Lightning: +25 damage, +1% Intelligence damage.

## Implementation notes

- The chain is a **real** Chain Lightning cast, not a scripted approximation: the proc
  calls the map's own dummy-cast helper `Qsq(...)` with the existing ability `A02R`
  (`$41303252`) and the order string `"chainlightning"`, writing the per-target damage
  into `ABILITY_RLF_DAMAGE_PER_TARGET_OCL1` for the cast. The bouncing lightning visual
  and the distinct-target selection come from the WC3 ability itself. The same helper and
  ability are already used by the map's `A0DX` on-hit effect, so this is an established
  code path rather than a new system.
- Gated on `HZ[pZ]` (auto-attacks only), which also makes it recursion-safe: the chain's
  damage is not an auto-attack, so it can never re-trigger the proc. A
  `boq(GetHandleId(hX), H0SC, 0.4s)` internal cooldown is a second backstop, matching the
  convention for a high-frequency on-attack proc.
- Intelligence is read as `GetHeroInt(hX,true)` (total, including bonuses).
- Because the chain is dealt by the ability rather than by an attributed `mEq` call, the
  damage meter lists it under the ability's own name.
- **The damage is flat-per-level plus an attribute share**, which is the roster's dominant
  shape for area damage — H005 Disease Cloud is 40·L, O001 Thunder Bolt 30·L, H016 Hellfire
  25·L, N00K Bladestorm 35·L. At 25·L per target the flat half sits at the low end of that
  band, which is right for something that hits five targets per proc.
- Mixing the two matters most at the extremes. A pure `% of Intelligence` passive does almost
  nothing at low level, when Intelligence is still double digits, and then scales without a
  floor; the flat term gives the hero a usable early game, and the attribute term is what
  rewards actually building Intelligence later. The 1%/level attribute part is exactly the roster's
  target rate for attribute scaling (0.5–1.0%/level, never above 1.5), so the curve stays
  in convention even though it is paid on all five targets.
