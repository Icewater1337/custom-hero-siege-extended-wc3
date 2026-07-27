# Kerrigan, Queen of Blades

| | |
|---|---|
| Rawcode | `H0KB` |
| Base unit | `Ewar` (Warden) |
| Primary attribute | Agility (melee) |
| Start stats | STR 28 / AGI 38 / INT 22 |
| Growth | +3.5 / +5.5 / +3.0 |
| Move speed | 320 |
| Starting elements | Dark ×1, Arcane ×1 |
| Roster slot | `KC[54]` |

A StarCraft-inspired Agility melee assassin: an essence-consuming carry that snowballs off kills
and unleashes psionic AoE on her attacks.

## Passives

**Essence Harvest** *(The Swarm)* — The Queen of Blades consumes the essence of the fallen. Each
enemy slain permanently grants **+2 attack damage**, up to **+6000** (a "fully evolved" cap
≈ 3000 kills). Implemented in the reward function `eCt` with an incremental
`BlzSetUnitBaseDamage` — the same never-overwritten mechanism the base map's "+N base attack
damage" items use — with the running total stored in `pC[0]` and shown on the stat panel.

**Psionic Storm** *(proc)* — When the Hero **attacks** an enemy, a **20%** chance (improved by
Luck) to unleash a psionic storm dealing **magic damage** in a 250 radius around the target,
equal to **25 × Hero level** plus a percentage of the Hero's **Agility**
(**150% + 1% per level** — 350% at level 200). `[Luck]`

> **Rescaled in 2.10.0.** Psionic Storm originally scaled as `80% + 4% per level` of Agility
> with no flat term. 4%/level was 4–8× the roster's convention for attribute scaling and the
> steepest coefficient in the map — unbounded, it reached 2480% of Agility at the level-600
> cap. It now uses the same shape as the Stormcaller: a flat per-level term that gives the
> passive a real floor at low level, plus a 1%/level attribute share, which is the roster's
> target rate. Below roughly level 90 this is a straight buff; above it, a correction.

| level | old (% of AGI) | new |
|---|---|---|
| 1 | 84% | 25 + 151% |
| 50 | 280% | 1,250 + 200% |
| 200 | 880% | 5,000 + 350% |
| 600 | 2,480% | 15,000 + 750% |

## Implementation notes

- The proc lives in the damage handler `jQt` and is gated on `HZ[pZ]` (auto-attacks only), which
  also makes it **recursion-safe**: the AoE magic damage it deals is not an auto-attack, so it
  can never re-trigger the proc. A `boq(source, H0KB, 0.4s)` internal cooldown is a secondary
  backstop.
- AoE damage is dealt through the map's own deferred helper `mEq(source, x, y, amount, radius,
  spellFlag=true, attributionRawcode, magic=true, isAttack=false)`, which is safe to call from
  inside the damage engine.
- Agility is read as `I2R(GetHeroAgi(hX, true))` (total, with bonuses).
- Stat panel shows Psionic Storm chance, the Agility-scaling percentage, and (new in 2.10.0)
  the flat per-level component as a fourth row — `DC` allows exactly 0..3.

## Model / assets

Uses the base-game **Warden** model with the **Maiev** command icon (the closest bladed-female
assassin stand-in in classic WC3). If the card icon or the Arcane-Explosion cast effect renders
as a missing asset in your client, swap the `uico` path in `append_heroes.py` and the effect path
in `patch_03_hero_kerrigan.py`.
