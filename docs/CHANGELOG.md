# Changelog

## 2.10.0

**Five new heroes** — chosen to fill five axes the 54-hero roster genuinely did not cover.

- ⚡ **The Stormcaller** (`H0SC`) — Intelligence, ranged. *Forked Lightning*: 20% on-attack
  chance to call a real Chain Lightning that strikes up to 5 **distinct** enemies for
  80% + 0.9%/level of Intelligence each. Every other area passive in the map hits a uniform
  radius; nothing chained. See `docs/hero-the-stormcaller.md`.
- ☠️ **The Executioner** (`H0EX`) — Strength, melee. *Headsman's Toll*: attacks against an
  enemy at or below 20% of maximum health deal +150% damage (+0.5%/level, capped at +400%).
  *Grim Harvest*: kills restore 2% of max HP and mana. The roster's two HP-scaling heroes
  both scale off the **full** part of the health bar; this is the first low-health payoff.
- 🚩 **The Warchief** (`H0WC`) — Strength, melee. *Warlord's Presence*: +6% damage per allied
  Hero within 900 range, itself included, capped at 5. *Battle Standard*: heals itself and
  nearby allied Heroes every second for 30×level + Strength. **The first hero in the map
  that does anything for its allies** — across all 54 existing heroes the only ally-facing
  effect was an enemy debuff.
- 🗡️ **The Spellblade** (`H0SB`) — Intelligence, melee. *Arcane Edge*: every attack spends
  2% of maximum mana and deals magic damage worth 200% + 1%/level of the mana spent.
  *Mana Font*: kills restore 2% of maximum mana. Three heroes touch mana; none spent it.
- 🛡️ **The Grudgebearer** (`H0GR`) — Strength, melee. *Thick Hide*: 10% less damage taken
  (+0.01%/level, max 20%). *Grudge*: banks 40% of damage taken (+0.05%/level, max 60%) up to
  5× its attack damage, then dumps the whole store as magic damage in a 400 radius on its
  next attack. Two heroes react to being hit; none stored it.

**Hero picker capacity**

- The pick grid was 8 columns × **7 rows = 56 cells**, and all six consumer loops were
  hard-bounded at 56 — with 54 heroes there were only two free slots. The grid is now
  8 × **8 = 64 cells**: six `exitwhen …>56` bounds raised to `>64` and the
  `BlzFrameSetSize` height term changed from `.032*7+.008*6` to `.032*8+.008*7`. Slots
  60–64 stay empty and take the same blank-cell path 55/56 already took.
  *Without this change heroes 57–59 would simply never appear.*

**Notes**

- Built on top of **2.9.5**, so the damage meter (2.9.1–2.9.4) and the healing meter (2.9.5)
  are both included unchanged.
- The Warchief cannot use WC3 alliance to find team-mates: `war3map.w3i` puts all human
  players in one force with alliance flags `0x00000000`, so **players are never allied
  during a normal round**. Its ally test is `self OR IsUnitAlly (duel/team-mode team-mate)
  OR both players in the same co-op wave (t[] and not tL)`, which fails closed during PvP.
  This is also the structural reason no existing hero has an ally-facing effect.
- `KC[1..50]` is deliberately untouched — the save/load code walks those slots
  positionally, so the roster may only ever be appended to.
- The Spellblade's and Grudgebearer's damage each get their own row in the damage
  meter ("Arcane Edge", "Grudge") instead of displaying as the hero's name. That step is
  skipped automatically if the patch is applied to a base without the meter.

## 2.9.0

**New heroes**
- 🗡️ **Kerrigan, Queen of Blades** (`H0KB`) — Agility melee assassin. *Essence Harvest*
  (+2 permanent attack damage per kill, up to +6000) and *Psionic Storm* (20% on-attack,
  Luck-scaled AoE magic damage scaling with Agility). See `docs/hero-kerrigan.md`.

**Fixes**
- **PvP betting payout inversion** — bettors who backed the **loser** were being paid and those
  who backed the winner lost their gold. The winner-determination in `Tet` stored the *dying*
  (losing) side into the payout selector `UB`; the two stored values are swapped so `UB` names
  the winning side. Consumer `jot` unchanged.

## 2.8.7

**New heroes**
- 🎲 **The Gambler** (`H0GB`) — Agility. *Loaded Dice* (+25% Luck) and *Double or Nothing*
  (kill-gold gamble). See `docs/hero-the-gambler.md`.

**Fixes** (also the basis of the "2.8.6-fixed" build)
- **I07M zero-damage** — item I07M ("immunity to self-inflicted damage") zeroed *all* of its
  holder's outgoing damage due to operator precedence; the self-hit condition now applies to the
  item too.
- **Spell-reflect ×0** — the Retaliation Aura / "wizardbane" reflected-damage multiplier read a
  hashtable key that is never written (always 0.0), so mirrored spells dealt no damage. It now
  multiplies by the stored reflect fraction.
- **Betting init infinite loop** — the betting dialog initializer `B4q` was missing its loop
  counter increment, so it spun to the op-limit and never created the betting menus. Added the
  missing `set d4q=d4q+1`.
- Internal version strings bumped (map name, F9 info, resource-bar text).

> The betting **payout** inversion (2.9.0) only became observable *after* the 2.8.7 init fix made
> betting run at all — it was a latent bug in code that previously never executed.
