# The Spellblade

| | |
|---|---|
| Rawcode | `H0SB` |
| Base unit | `Hpal` (Paladin — melee hero chassis) |
| Primary attribute | Intelligence (melee) |
| Start stats | STR 26 / AGI 28 / INT 40 |
| Growth | +3.2 / +3.2 / +5.2 |
| Attack | 16 + 1d12, cooldown 1.40 |
| Move speed | 320 |
| Model / icon | `units\creeps\VoidWalker\VoidWalker.mdl` / `BTNVoidWalker` |
| Starting elements | Arcane ×1 |
| Roster slot | `KC[58]` |

Three existing heroes touch mana — one turns Intelligence into magic power, one turns
damage into mana and mana into a health bar, one drains it from enemies. **None of them
spend it.** The Spellblade turns the mana pool into ammunition: it is the only hero whose
damage has a running cost, and the only one for whom mana regeneration is an offensive
stat rather than a convenience.

## Passives

**Arcane Edge** — Every **attack** consumes **2%** of the Hero's maximum mana and unleashes
**magic damage** equal to a multiple of the mana consumed (**200% + 1% per level**).
Without mana there is no bonus.

**Mana Font** — Killing an enemy restores **2%** of maximum mana.

**Level Up Bonus** — Arcane Edge: +1% mana to damage conversion.

## Implementation notes

- No proc roll and no internal cooldown: the passive fires on every auto-attack that can
  pay for itself. The mana pool *is* the rate limit, which is what makes the hero a
  resource-management build rather than another chance-based proc.
- The bonus is a separate `DAMAGE_TYPE_MAGIC` instance through `sLq`, not an addition to
  the attack, so it bypasses physical armor — which matters enormously here, since
  round-50 creeps carry 1800 armor (98.2% physical reduction) against only 200 magic
  protection (80% magic reduction).
- `set j=3` / `set df=H0SB` immediately precede the `sLq` call, the map's standard idiom.
  `j=3` marks the generated hit as proc damage (`KX==1`), which excludes it from the entire
  on-hit proc block — so Arcane Edge cannot trigger itself, and the engine's 16-deep
  recursion cutout is never approached.
- `df` also makes the damage meter list it as its own row; the patch adds an
  **"Arcane Edge"** entry to `DmgName` so it does not display as the hero's name.
- Mana is read and written with `GetUnitState`/`SetUnitState` on
  `UNIT_STATE_MANA` / `UNIT_STATE_MAX_MANA`; the cost is checked *before* it is paid, so a
  hero below the threshold simply attacks normally.

## Balance note

This hero's output scales with **maximum mana**, which items and Intelligence can inflate a
long way. The intended check is that the cost scales identically — 2% per swing means
roughly 5% of the pool per second at typical attack speeds, so sustained damage is capped
by mana regeneration, not by the pool. Mana Font (2% per kill) is what keeps it firing
through a wave — deliberately set equal to the per-attack cost, so kills roughly pay for
the swings that earned them instead of making mana free. If the hero proves too strong in practice, the honest lever is the
conversion constant `2.+.01*level` in `patch_05_heroes5.py`, not the 2% cost.
