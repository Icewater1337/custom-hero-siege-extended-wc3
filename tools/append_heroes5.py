"""Append the five new heroes to both object-data tables.

war3map.w3u    holds the GAMEPLAY record (stats, primary attribute, abilities)
war3mapSkin.w3u holds the DISPLAY record (name, model, icon)

The two files have zero field overlap and both are mandatory: LJq silently drops
any hero whose GetObjectName() (i.e. 'unam', which lives only in the skin file)
hashes to 0.

in : new290_war3map.w3u / new290_war3mapSkin.w3u   (already contain H0GB, H0KB)
out: new2A0_war3map.w3u / new2A0_war3mapSkin.w3u
"""
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
from w3u_append import append_unit
from parse_skin import parse_w3o

BS = chr(92)


def ico(name):
    return 'ReplaceableTextures' + BS + 'CommandButtons' + BS + name + '.blp'


# Every (model, icon) pair below is already referenced by a unit in this map's
# own object data - so it is guaranteed to load - and is used by no other hero.
HEROES = [
    dict(
        code='H0SC', base='Hjai', name='The Stormcaller', proper='Zar Thundertongue',
        model='units' + BS + 'orc' + BS + 'Shaman' + BS + 'Shaman.mdl', icon='BTNShaman',
        pra='INT',
        stats=dict(ustr=24, uagi=26, uint=42, ustp=4.5, uagp=4.5, uinp=5.5,
                   uhpm=150, uhpr=2.0, ua1b=14, ua1d=1, ua1s=12, ua1c=1.55,
                   umvs=300, upoi=320, ucpt=0.35),
    ),
    dict(
        code='H0EX', base='Hpal', name='The Executioner', proper='Mordred the Headsman',
        model='Units' + BS + 'Undead' + BS + 'HeroDeathknight' + BS + 'HeroDeathknight.mdl',
        icon='BTNHeroDeathKnight', pra='STR',
        stats=dict(ustr=40, uagi=24, uint=18, ustp=4.8, uagp=3.0, uinp=2.4,
                   uhpm=250, uhpr=3.5, ua1b=22, ua1d=1, ua1s=10, ua1c=1.45,
                   umvs=310, upoi=300, ucpt=0.30),
    ),
    dict(
        code='H0WC', base='Hpal', name='The Warchief', proper='Gharuk Ironbanner',
        model='units' + BS + 'demon' + BS + 'ChaosWarlord' + BS + 'ChaosWarlord.mdl',
        icon='BTNChaosWarlord', pra='STR',
        stats=dict(ustr=42, uagi=22, uint=24, ustp=4.8, uagp=2.8, uinp=3.2,
                   uhpm=300, uhpr=4.0, ua1b=18, ua1d=1, ua1s=10, ua1c=1.50,
                   umvs=300, upoi=300, ucpt=0.30),
    ),
    dict(
        code='H0SB', base='Hpal', name='The Spellblade', proper='Vaelin Nullborn',
        model='units' + BS + 'creeps' + BS + 'VoidWalker' + BS + 'VoidWalker.mdl',
        icon='BTNVoidWalker', pra='INT',
        stats=dict(ustr=26, uagi=28, uint=40, ustp=3.2, uagp=3.2, uinp=5.2,
                   uhpm=175, uhpr=2.5, ua1b=16, ua1d=1, ua1s=12, ua1c=1.40,
                   umvs=320, upoi=300, ucpt=0.30),
    ),
    dict(
        code='H0GR', base='Hpal', name='The Grudgebearer', proper='Rimefang',
        model='Units' + BS + 'Creeps' + BS + 'MagnataurBlue' + BS + 'MagnataurBlue.mdl',
        icon='BTNBlueMagnataur', pra='STR',
        stats=dict(ustr=46, uagi=20, uint=16, ustp=5.4, uagp=2.6, uinp=2.2,
                   uhpm=350, uhpr=5.0, ua1b=24, ua1d=1, ua1s=10, ua1c=1.60,
                   umvs=290, upoi=320, ucpt=0.35),
    ),
]

# field -> serialised type. Passing a Python float to an int-typed field writes
# float bytes under an int vtype and corrupts the record, so keep this explicit.
INT_FIELDS = {'ustr', 'uagi', 'uint', 'uhpm', 'umvs', 'ua1b', 'ua1d', 'ua1s',
              'ufoo', 'uhhd', 'ufle', 'ucam', 'upoi', 'upru'}
REAL_FIELDS = {'ustp', 'uagp', 'uinp', 'uhpr', 'ua1c', 'ucpt'}

# ------------------------------------------------------------- gameplay ----
data = open('new290_war3map.w3u', 'rb').read()
for h in HEROES:
    mods = [('uabi', 'A08H,AInv'), ('uhab', ''), ('upra', h['pra'])]
    for k, v in h['stats'].items():
        assert k in INT_FIELDS or k in REAL_FIELDS, 'unclassified field ' + k
        mods.append((k, int(v) if k in INT_FIELDS else float(v)))
    mods += [('ufoo', 0), ('uhhd', 1), ('ufle', 0), ('ucam', 0)]
    data = append_unit(data, h['base'], h['code'], mods)
open('new2A0_war3map.w3u', 'wb').write(data)

# ----------------------------------------------------------------- skin ----
sdata = open('new290_war3mapSkin.w3u', 'rb').read()
for h in HEROES:
    smods = [
        ('unam', h['name']),
        ('upro', h['proper']),
        ('upru', 1),
        ('ussi', ''),
        ('uico', ico(h['icon'])),
        ('umdl', h['model']),
    ]
    sdata = append_unit(sdata, h['base'], h['code'], smods)
open('new2A0_war3mapSkin.w3u', 'wb').write(sdata)

# --------------------------------------------------------------- verify ----
for tag, fn in [('gameplay', 'new2A0_war3map.w3u'), ('skin', 'new2A0_war3mapSkin.w3u')]:
    _, objs = parse_w3o(fn, False)
    ids = [o['id'] for o in objs]
    assert len(ids) == len(set(ids)), '%s: duplicate object ids' % tag
    for h in HEROES:
        assert h['code'] in ids, '%s: %s missing' % (tag, h['code'])
    assert 'H0GB' in ids and 'H0KB' in ids, '%s: lost an existing hero' % tag
    print('%s w3u: %d objects, all 5 new heroes present, no duplicate ids' % (tag, len(objs)))

_, sobjs = parse_w3o('new2A0_war3mapSkin.w3u', False)
for h in HEROES:
    o = [x for x in sobjs if x['id'] == h['code']][0]
    got = {m['field']: m['value'] for m in o['mods']}
    print('  %s  base=%-5s %-18s %s' % (h['code'], o['base'], got['unam'], got['umdl']))
