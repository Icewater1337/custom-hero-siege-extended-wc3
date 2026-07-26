# Changelog

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
