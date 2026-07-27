# The Warchief

| | |
|---|---|
| Rawcode | `H0WC` |
| Base unit | `Hpal` (Paladin — melee hero chassis) |
| Primary attribute | Strength (melee) |
| Start stats | STR 42 / AGI 22 / INT 24 |
| Growth | +4.8 / +2.8 / +3.2 |
| Attack | 18 + 1d10, cooldown 1.50 |
| Move speed | 300 |
| Model / icon | `units\demon\ChaosWarlord\ChaosWarlord.mdl` / `BTNChaosWarlord` |
| Starting elements | Light ×1, Earth ×1 |
| Roster slot | `KC[57]` |

**The first hero in the map that does anything for its allies.** Custom Hero Survival is
an eight-player co-op survival game, and across all 54 existing heroes there is exactly one
ally-facing effect — Fear Aura, which only debuffs enemies. Every other passive is
self-contained. The Warchief is built entirely around standing with the team: it pays out
for grouping up, and it keeps the group alive.

## Passives

**Warlord's Presence** — All damage the Warchief deals is increased by **6%** for every
allied Hero within **900** range, itself included (maximum 5, so +6% solo and +30% in a
full group).

**Battle Standard** — Every second, the Warchief restores hit points to itself and to every
allied Hero within **900** range, equal to **30 × its level + 100% of its Strength**.

**Level Up Bonus** — Battle Standard: +30 hit points restored per second.

## Implementation notes

- Both passives share a small helper pair inserted ahead of `PGt`:
  `WcAllies(u)` counts and `WcBanner(u)` heals, by walking `Gh[0..7]` (the per-player hero
  array). Eight iterations, no group handles created, nothing to leak.

- **The ally test is not WC3 alliance**, and that is the one genuinely subtle thing about
  this hero. `war3map.w3i` puts every human player in a single force whose alliance flags
  are `0x00000000` — so in Custom Hero Survival **two players are never allied during a
  normal round**, and a plain `IsUnitAlly` check would have made both passives silently
  inert (the Warchief would have counted only itself, forever). That is also why no
  existing hero has an ally-facing effect: the map's own "allied unit" filters only ever
  match a player's own units.

  Alliance *is* meaningful in PvP, where the duel and team code explicitly allies each side
  (`SetForceAllianceStateBJ(Xqt,Xqt,bj_ALLIANCE_ALLIED)`) and un-allies the other. So the
  predicate is three-part:

  | clause | covers |
  |---|---|
  | `Gh[i]==u` | the Warchief itself, in every phase |
  | `IsUnitAlly(Gh[i],p)` | a duel / team-mode team-mate |
  | `t[i] and t[pid] and not tL` | both players in the same co-op wave |

  `t[]` is the map's "player is in the round" flag and `tL` marks team/battle-royale mode,
  so the third clause is off during PvP. The test therefore **fails closed**: in an
  ambiguous phase the Warchief supports nobody rather than healing a duel opponent.
- Warlord's Presence counts the Warchief itself, so the hero is never dead weight in a solo
  game — it simply gets the smallest tier of its own bonus. The count is clamped with
  `IMinBJ(...,5)`, so the multiplier is bounded at ×1.30 no matter how many players join.
  A bounded flat multiplier is deliberately much smaller than the map's existing
  everything-multipliers (Valiant Strike is 10% + 0.5%/level of Strength on *all* damage).
- Battle Standard runs from `PGt`, the map's one-second per-hero loop, inserted as an
  `elseif CGt==…` branch in the existing type-dispatch chain — never as a new leading `if`,
  because that chain reassigns its "unit type" local partway through.
- Healing is a plain `SetUnitState(…, UNIT_STATE_LIFE, current + amount)`, which WC3 clamps
  at maximum hit points.
- The live per-second figure is written into the stat panel each tick, so the panel shows
  the real current value including Strength from items, not a stale level-up snapshot.

## Balance note

Battle Standard heals **each** ally for the full amount rather than splitting a budget, so
total party throughput grows linearly with headcount. Per target the number is deliberately
modest — about 10,500 HP/s at level 300, roughly 1.4× what N00I's Troll Anatomy already
gives itself, and around 14% of a single round-50 creep hit. Per-hero sustain is what
decides whether a hero lives, not the sum across eight separate health bars, which is why
it is not split. If it plays too strong in a full lobby, the lever is the `30.*` level
coefficient in `WcBanner`.
