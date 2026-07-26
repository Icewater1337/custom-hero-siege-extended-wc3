"""Generate minimal-context unified diffs of each JASS change stage."""
import os, difflib
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# changes/ lives at the repo root, one level up from tools/
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CH = os.path.join(REPO, 'changes')
os.makedirs(CH, exist_ok=True)

stages = [
    ('01-bugfixes.diff', 'x_war3map.j', 'war3map_fixed.j',
     'Three gameplay bug fixes (I07M zero-damage, spell-reflect x0, betting init loop)'),
    ('02-hero-the-gambler.diff', 'war3map_fixed.j', 'war3map_287.j',
     'New hero "The Gambler" (H0GB) + version bump to 2.8.7'),
    ('03-hero-kerrigan.diff', 'war3map_287.j', 'war3map_290.j',
     'New hero "Kerrigan, Queen of Blades" (H0KB) + version bump to 2.9.0'),
    ('04-betting-payout-fix.diff', 'war3map_290.j', 'war3map_290_final.j',
     'Fix inverted PvP betting payout (winner/loser swap in Tet)'),
]

for name, a, b, desc in stages:
    la = open(a, encoding='utf-8').read().split('\n')
    lb = open(b, encoding='utf-8').read().split('\n')
    diff = difflib.unified_diff(la, lb, fromfile='a/war3map.j', tofile='b/war3map.j',
                                lineterm='', n=1)
    body = '\n'.join(diff)
    header = f'# {desc}\n# stage: {a} -> {b}\n#\n'
    with open(os.path.join(CH, name), 'w', encoding='utf-8', newline='\n') as f:
        f.write(header + body + '\n')
    added = sum(1 for l in body.split('\n') if l.startswith('+') and not l.startswith('+++'))
    removed = sum(1 for l in body.split('\n') if l.startswith('-') and not l.startswith('---'))
    print(f'{name}: +{added} -{removed}')
print('diffs written to', CH)
