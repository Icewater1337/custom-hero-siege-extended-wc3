"""Inventory every model/icon actually referenced by this map's object data,
and mark which ones are already taken by a roster hero."""
import os, json, re, collections
os.chdir(os.path.dirname(os.path.abspath(__file__)))

j = open('war3map_294.j', encoding='utf-8').read()
roster = [bytes.fromhex(h).decode('latin1') for _, h in
          re.findall(r'set KC\[(\d+)\]=\$([0-9a-fA-F]{8})\n', j)]
# hero card icons (Po key 1) -> icons already in use on the pick screen
card_icons = {}
for m in re.finditer(r'call SaveStr\(tC,BCq\(Po,\$([0-9a-fA-F]{8})\),1,"(.*?)"\)\n', j):
    card_icons[bytes.fromhex(m.group(1)).decode('latin1')] = m.group(2).replace('\\\\', '\\')

units = {}
for fn in ['obj_units.json', 'obj_skin_units.json']:
    d = json.load(open(fn, encoding='utf-8'))
    objs = d['objects'] if isinstance(d, dict) and 'objects' in d else d
    for o in objs:
        oid = o.get('id') or o.get('newid')
        rec = units.setdefault(oid, {'base': o.get('base') or o.get('oldid'), 'f': {}})
        for m in o.get('mods', []):
            rec['f'][m['field']] = m['value']

print('units in object data:', len(units))
print('roster heroes:', len(roster))

hero_models = {}
for h in roster:
    u = units.get(h, {})
    hero_models[h] = (u.get('f', {}).get('umdl'), u.get('f', {}).get('uico'),
                      u.get('f', {}).get('unam'), u.get('base'))

taken_mdl = set()
taken_ico = set()
print('\n=== ROSTER HERO MODELS ===')
for h in roster:
    mdl, ico, nam, base = hero_models[h]
    if mdl:
        taken_mdl.add(mdl.lower())
    if ico:
        taken_ico.add(ico.lower())
    print('%-5s base=%-5s %-38s | %-52s | %s' % (h, base, (nam or '')[:38], (mdl or '(inherits base)')[:52], (ico or '')[:40]))

for h, ic in card_icons.items():
    taken_ico.add(ic.lower())

# every distinct model/icon referenced anywhere in the object data
mdl_users = collections.defaultdict(list)
ico_users = collections.defaultdict(list)
for uid, rec in units.items():
    f = rec['f']
    if 'umdl' in f:
        mdl_users[f['umdl']].append(uid)
    if 'uico' in f:
        ico_users[f['uico']].append(uid)

print('\ndistinct models referenced:', len(mdl_users), '| distinct icons:', len(ico_users))

free = [(m, us) for m, us in sorted(mdl_users.items()) if m and m.lower() not in taken_mdl]
print('\n=== MODELS USED IN THIS MAP BUT NOT BY ANY ROSTER HERO (%d) ===' % len(free))
for m, us in free:
    names = [units[u]['f'].get('unam', u) for u in us[:3]]
    print('  %-60s  used by: %s' % (m[:60], ', '.join(str(n)[:24] for n in names)))

freei = [(i, us) for i, us in sorted(ico_users.items()) if i and i.lower() not in taken_ico]
print('\n=== ICONS USED IN THIS MAP BUT NOT BY ANY ROSTER HERO (%d) ===' % len(freei))
for i, us in freei:
    names = [units[u]['f'].get('unam', u) for u in us[:3]]
    print('  %-64s  used by: %s' % (i[:64], ', '.join(str(n)[:22] for n in names)))
