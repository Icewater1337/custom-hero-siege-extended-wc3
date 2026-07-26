# Build pipeline

These are the scripts used to produce this release. They are **reference-quality**: each was
run in a single flat working directory containing the files extracted from the base map. They
are not a turnkey `make` — reproducing a build means setting up that working directory and
running the steps in order. Every JASS edit is anchored on a verbatim code snippet and asserts
if the anchor is missing, so re-patching a changed base fails loudly at the exact edit that
needs attention.

## Requirements

- Python 3.10+
- `pip install mpyq` (MPQ archive reading)

## Files

| script | purpose |
|---|---|
| `extract.py` | Pull `war3map.j`, object data, strings, etc. out of the base `.w3x` (MPQ). |
| `prep_corpus.py` | Parse `war3map.wts` and the object-data files into JSON; split the script into chunks. |
| `parse_skin.py` | W3U/W3O object-data parser (library, also runnable). |
| `w3u_append.py` | Append a new unit definition to a `.w3u` table at the byte level (library). |
| `append_heroes.py` | Append **The Gambler** (`H0GB`) and **Kerrigan** (`H0KB`) to `war3map.w3u` and `war3mapSkin.w3u`. |
| `patch_01_bugfixes.py` | The 3 gameplay bug fixes. `x_war3map.j` → `war3map_fixed.j`. |
| `patch_02_hero_gambler.py` | The Gambler hero + version 2.8.7. `war3map_fixed.j` → `war3map_287.j`. |
| `patch_03_hero_kerrigan.py` | Kerrigan hero + version 2.9.0. `war3map_287.j` → `war3map_290.j`. |
| `patch_04_betting_fix.py` | Betting payout inversion fix. `war3map_290.j` → `war3map_290_final.j`. |
| `build_map.py` | Rebuild the `.w3x`, replacing the 5 modified files; verifies all others stay byte-identical. |
| `assemble_diffs.py` | Regenerate `changes/*.diff` from the intermediate `war3map_*.j` stages. |

## Order of operations

```
# 0. place your base map here as map.w3x  (header-normalized copy of CHS_v2.8.6.w3x)
python extract.py            # -> x_war3map.j, x_war3map.w3u, ... (and the war3mapSkin.* files)
python prep_corpus.py        # -> obj_*.json, strings.json, jchunks/

# JASS script chain (each stage asserts its anchors):
python patch_01_bugfixes.py  # x_war3map.j        -> war3map_fixed.j
python patch_02_hero_gambler.py  # war3map_fixed.j -> war3map_287.j
python patch_03_hero_kerrigan.py # war3map_287.j   -> war3map_290.j
python patch_04_betting_fix.py   # war3map_290.j   -> war3map_290_final.j

# object data (both heroes):
python append_heroes.py      # war3map.w3u/war3mapSkin.w3u -> *.patched

# version strings (war3map.wts, war3mapSkin.txt): 2.8.6 -> 2.9.0  (see the diffs / build script)

# rebuild:
python build_map.py          # -> CHS_v2.9.0.w3x  (+ integrity verification)
```

`build_map.py` replaces exactly five files inside the archive — `war3map.j`, `war3map.wts`,
`war3map.w3u`, `war3mapSkin.w3u`, `war3mapSkin.txt` — and verifies that every other file in the
map re-extracts byte-identical to the original.

> Note on filenames: the scripts as shipped use the intermediate names above
> (`war3map_fixed.j`, `war3map_287.j`, …) exactly as they were run. `append_heroes.py` reads the
> standard extracted names `war3map.w3u` / `war3mapSkin.w3u`; adjust paths to match your extract
> step if needed.
