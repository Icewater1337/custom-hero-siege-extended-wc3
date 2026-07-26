"""Append the two custom hero unit definitions to the base map's object data.

Reads the base game-unit table (war3map.w3u) and the base display/skin table
(war3mapSkin.w3u) extracted from the base map, appends both heroes, and writes
*.patched.w3u files.

Heroes:
  H0GB  "The Gambler"            base Nfir (Firelord),  Agility, ranged
  H0KB  "Kerrigan, Queen of Blades" base Ewar (Warden),  Agility, melee

Run from a directory containing war3map.w3u and war3mapSkin.w3u (see tools/README.md).
"""
import os
from w3u_append import append_unit
from parse_skin import parse_w3o

BS = chr(92)  # single backslash, as used verbatim in object-data string fields

GAMBLER_GAMEPLAY = [
    ('uabi', 'A08H,AInv'), ('uhab', ''), ('upra', 'AGI'),
    ('ustr', 30), ('uagi', 35), ('uint', 27),
    ('ustp', 3.0), ('uagp', 5.0), ('uinp', 4.0),
    ('uhpm', 150), ('uhpr', 2.0),
    ('ua1b', 8), ('ua1d', 1), ('ua1s', 24), ('ua1c', 1.4),
    ('umvs', 300), ('ufoo', 0), ('uhhd', 1), ('ufle', 0), ('ucam', 0),
    ('upoi', 310), ('ucpt', 0.35),
]
GAMBLER_SKIN = [
    ('unam', 'The Gambler'),
    ('upro', 'Flint |cffffcc00Lucky|r Embermane'),
    ('upru', 1), ('ussi', ''),
]

KERRIGAN_GAMEPLAY = [
    ('uabi', 'A08H,AInv'), ('uhab', ''), ('upra', 'AGI'),
    ('ustr', 28), ('uagi', 38), ('uint', 22),
    ('ustp', 3.5), ('uagp', 5.5), ('uinp', 3.0),
    ('uhpm', 150), ('uhpr', 2.0),
    ('ua1b', 10), ('ua1d', 1), ('ua1s', 30), ('ua1c', 1.35),
    ('umvs', 320), ('ufoo', 0), ('uhhd', 1), ('ufle', 0), ('ucam', 0),
    ('upoi', 310), ('ucpt', 0.35),
]
KERRIGAN_SKIN = [
    ('unam', 'Kerrigan, Queen of Blades'),
    ('upro', 'Sarah Kerrigan'),
    ('uico', 'ReplaceableTextures' + BS + 'CommandButtons' + BS + 'BTNMaiev.blp'),
    ('umdl', 'units' + BS + 'NightElf' + BS + 'Warden' + BS + 'Warden.mdl'),
    ('usnd', 'Warden'), ('upru', 1), ('ussi', ''),
]


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    gp = open('war3map.w3u', 'rb').read()
    gp = append_unit(gp, 'Nfir', 'H0GB', GAMBLER_GAMEPLAY)
    gp = append_unit(gp, 'Ewar', 'H0KB', KERRIGAN_GAMEPLAY)
    open('war3map.w3u.patched', 'wb').write(gp)

    sk = open('war3mapSkin.w3u', 'rb').read()
    sk = append_unit(sk, 'Nfir', 'H0GB', GAMBLER_SKIN)
    sk = append_unit(sk, 'Ewar', 'H0KB', KERRIGAN_SKIN)
    open('war3mapSkin.w3u.patched', 'wb').write(sk)

    for fn in ('war3map.w3u.patched', 'war3mapSkin.w3u.patched'):
        _, objs = parse_w3o(fn, False)
        ids = [o['id'] for o in objs]
        assert 'H0GB' in ids and 'H0KB' in ids, fn
        print(f'{fn}: {len(objs)} units (H0GB + H0KB appended)')


if __name__ == '__main__':
    main()
