# Custom Hero Survival — Extended (patch set)

A set of **modifications** to the Warcraft III custom map *Custom Hero Survival* (CHS):
bug fixes, two new heroes, and a repeatable build pipeline. This repository contains
**only the changes and the tooling** — not the base map, its decompiled source, or the
built map file.

> **About the base map / disclaimer.** *Custom Hero Survival* is the work of its original
> author (BLOKKADE) and is a protected map. This repository does **not** redistribute the
> base map, its full decompiled `war3map.j`, or any built `.w3x`. To use these patches you
> must supply your own copy of the base map. The material here is limited to our own
> modifications plus small code excerpts used as patch anchors, and to tooling for applying
> them. If you are the author and want any of this taken down, open an issue.

## What's in this release (v2.9.0)

- **3 bug fixes** to existing map logic:
  - Item **I07M** no longer zeroes *all* of its holder's damage (operator-precedence fix).
  - **Spell-reflect** (Retaliation Aura / "wizardbane") now deals its damage instead of ×0
    (it multiplied by a hashtable key that was never written).
  - The **PvP betting** dialog initializer no longer infinite-loops (missing `+1`), so the
    betting menus actually get created.
- **Betting payout fix** — the payout was **inverted** (backers of the *loser* were paid).
  The winner-determination stored the dying (losing) side into the "pay this side" selector.
- **Two new heroes** (see `docs/`):
  - 🎲 **The Gambler** (`H0GB`) — Agility; *Loaded Dice* (+25% Luck) and *Double or Nothing*
    (chance to double the gold on a kill, small chance to lose it).
  - 🗡️ **Kerrigan, Queen of Blades** (`H0KB`) — Agility melee; *Essence Harvest* (+2 permanent
    attack damage per kill, capped) and *Psionic Storm* (Luck-scaled on-attack AoE magic damage
    scaling with Agility).
- Internal version bumped to **2.9.0**.

## Repository layout

```
changes/     Human-readable unified diffs of every war3map.j change (the canonical changes)
docs/        Bug report and per-hero design docs
tools/       The Python pipeline: extract -> patch -> rebuild (see tools/README.md)
```

## How the changes are structured

Each change is captured two ways so it can be **re-applied to a future base version**:

1. **`changes/*.diff`** — a minimal-context unified diff of the decompiled `war3map.j`.
   Readable, and applies with `git apply` / `patch` as long as the surrounding lines match.
2. **`tools/patch_0X_*.py`** — the script that produced the change. Each edit is anchored on a
   **verbatim code snippet** rather than a line number, so it re-applies even if the base code
   shifted around, and it *fails loudly* (assertion) if an anchor no longer matches — which is
   exactly what you want when re-patching a new base version.

The two new heroes also touch the map's binary object data (`war3map.w3u`,
`war3mapSkin.w3u`); that part is produced by `tools/append_heroes.py`, which appends both hero
unit definitions to the extracted base tables.

See **`tools/README.md`** for the exact end-to-end pipeline (extract → patch → rebuild) and the
intermediate-filename chain.

## Re-patching a new base version, in short

1. Put your base `CHS_vX.Y.Z.w3x` next to the tools and extract it (`tools/extract.py` +
   the object/skin files).
2. Run the `patch_0X_*.py` scripts in order over the decompiled `war3map.j`, and
   `append_heroes.py` over the object data. If the base changed a region an anchor targets, the
   script asserts — update that one anchor and re-run.
3. Rebuild the `.w3x` with `tools/build_map.py`.

Nothing here runs against the base map automatically; you always supply your own copy.
