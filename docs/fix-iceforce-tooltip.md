# Fix: Ice Force tooltip showing a raw `,s01,` token (2.10.2)

## Symptom

Ice Force's extended tooltip read literally:

> Reduces damage taken by Hero based on its intelligence **(,s01,%)** once every few seconds.

The `(,s01,%)` is not text the player should ever see.

## Root cause

`,s01,` is the map's **own runtime placeholder token**, not a standard WC3
`<AbilCode,Field>` reference. The JASS swaps it for the live value at run time:

- `war3map.j` (level-up refresh): `set BZt = pqq_2192(",s01,", I2S(R2I((1.-500./(500.+GetHeroInt(MZt,true)))*100.)), BZt)` → `BlzSetAbilityExtendedTooltip(...)`
- and again on proc.

So `(,s01,%)` is *meant* to become e.g. `(20%)`. But that swap only runs once the
ability is live on a unit — in the **ability preview / picker tooltip** it hasn't
run, so the raw token shows.

The real mechanic (from the JASS, `war3map.j` ~27141/27148): an incoming hit is
multiplied by `500 / (500 + INT)`, i.e. Ice Force **blocks `INT / (INT + 500)` of
one hit** (50% at 500 INT), on a short cooldown.

## Fix

Rewrite the tooltip to be self-contained and always correct — state the formula
instead of relying on the fragile runtime token:

> Reduces the damage of one incoming hit based on the Hero's Intelligence,
> blocking `Int / (Int + 500)` of it (50% at 500 Int), once every few seconds.

Applied to all 30 level strings (`tools/patch_06_iceforce_tooltip.py`). The
leftover `pqq_2192(",s01,",…)` calls become harmless no-ops.

**Careful:** `,s01,` is *also* used by **A089 (Martial Retribution)**'s own live
tooltip (`Current maximum: ,s01,`) — that is a working dynamic tooltip and is left
untouched. Only the Ice Force strings are rewritten; the patch asserts exactly one
`,s01,` (Martial Retribution's) survives.

## Trade-off

The tooltip now shows the *formula* rather than the current *live* percentage.
That's arguably clearer (it shows the scaling), and it's correct in every UI state
including the picker preview. If the live value is preferred instead, the fix would
be to make the runtime `pqq_2192` swap fire for Ice Force in all display states —
harder and needs in-game testing.
