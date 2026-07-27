# Damage & healing meter (map versions 2.9.1 → 2.9.5)

A per-player combat meter rendered as a right-side **multiboard** widget, built on top of
the 2.9.0 script. It hooks the map's central damage engine (read-only) and shows, live:

- **Dealt** — your outgoing damage, broken down by ability (named) and Auto-attack, with %.
- **Taken from** — incoming damage, broken down by source (enemy ability, or unit name).
- **Healed by** — healing received, by source (Lifesteal, named heal spells). *(2.9.5)*
- Totals for each section.

Toggle with `-dmg`. The widget updates ~1×/second and resets at the start of each wave and at
duel start. Each player sees only their own numbers (per-local-player multiboard).

## How attribution works

All accumulation happens in `DmgObserve`, called first in `AQt` — the map's *After-damage*
phase, where the damage value is final and the source/ability globals are still live. Keys:

- Source ability = `UX` (the map's `df`/`CZ` attribution rawcode). Auto-attacks have `UX==0`.
- Bucket = `UX` if set, else `1` (Auto-attack), else split by damage type into "Other".
- Incoming falls back to `CZ[pZ]` when `UX==0`, so creep abilities (e.g. Spiked Carapace's
  reflect) show by **name** instead of the creep's unit type. Untagged periodic damage is
  labelled "*(over time)*"; auto-attacks by the attacker's unit name.
- Lifesteal is captured at the map's single lifesteal wrapper (`Elt`) plus two direct sites,
  all under one "Lifesteal" row. Named heal spells are hooked at their cast sites.

Healing is decentralised in this map (≈20 scattered `SetUnitState(... LIFE + x)` sites, no
heal engine), so the meter names the high-value sources (lifesteal + the main active heals)
and does not yet itemise every minor passive regen.

## Non-obvious pitfalls fixed along the way

- **32-bit float key corruption (2.9.3).** Ability rawcodes (~1.09e9) were stored as JASS
  `real` in the source list; a float can't hold integers above 2²⁴ exactly, so the key was
  corrupted on read-back and the row vanished — only small keys (Auto-attack = `1`) survived.
  Fixed by storing enum keys with `SaveInteger`/`LoadInteger`.
- **Post-PvP freeze (2.9.5).** The first wave after a PvP round spawns via `aet`/`qqf`, which
  bypass the normal wave-start hook (`NFt`) where the reset lives; a reset was added to both.
- **Multiboard desync trap.** The map's hashtable helper `BCq` allocates on first read
  (advancing a shared counter). The per-local-player refresh pre-allocates all player tables
  and early-returns for observer slots (`pid>7`), so `BCq` is a pure read there.
- **On-hit bonuses folded into the attack** (e.g. Incinerate's living-flames +N) are added
  directly to the auto-attack's damage by the map, so they are counted inside the
  **Auto-attack** row and cannot be split out without double-counting.

## Reproducing

The five stages are `tools/patch_meter_1_perwave.py` … `patch_meter_5_healing_pvpreset.py`,
applied in order over the 2.9.0 script (`war3map_290_final.j` → … → `war3map_295.j`). The
consolidated result is `changes/05-damage-healing-meter.diff`. Version strings are bumped by
each stage; see `tools/README.md` for the full extract→patch→rebuild pipeline.

> Verifying a patched script before building: run the external-call / block-balance /
> locals-order checks (a misspelled native — the classic "map is unavailable or corrupted"
> cause — surfaces as a new external call). See `tools/README.md`.
