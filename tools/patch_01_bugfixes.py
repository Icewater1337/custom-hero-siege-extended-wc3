"""Apply the three bug fixes to war3map.j -> war3map_fixed.j"""
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
src = open('x_war3map.j', encoding='utf-8', newline='').read()

# Preserve original newline style: check
assert '\r\n' not in src, 'expected LF newlines'

patches = [
    # Bug 1: I07M zero-damage — enforce self-hit condition for both sources
    ('if utq(hX,$4930374d) or GetUnitAbilityLevel(hX,$4173736b)>0 and hX==CX then',
     'if (utq(hX,$4930374d) or GetUnitAbilityLevel(hX,$4173736b)>0) and hX==CX then'),
    # Bug 2: spell-reflect multiplier — use stored Yw fraction instead of never-written sr key
    ('set qZ[pZ]=qZ[pZ]*LoadReal(tC,sr,nX)',
     'set qZ[pZ]=qZ[pZ]*Yw[LoadInteger(tC,cO,GetHandleId(hX))]'),
    # Bug 3: betting dialog init — add missing loop counter increment
    ('''function B4q takes nothing returns nothing
local integer d4q=0
loop
exitwhen d4q>4
set bq[d4q]=DialogCreate()
endloop
endfunction''',
     '''function B4q takes nothing returns nothing
local integer d4q=0
loop
exitwhen d4q>4
set bq[d4q]=DialogCreate()
set d4q=d4q+1
endloop
endfunction'''),
]

for old, new in patches:
    n = src.count(old)
    assert n == 1, f'pattern not unique (count={n}): {old[:60]!r}'
    src = src.replace(old, new)

open('war3map_fixed.j', 'w', encoding='utf-8', newline='').write(src)

# sanity: line-level diff count
orig = open('x_war3map.j', encoding='utf-8').read().split('\n')
new = src.split('\n')
print('orig lines:', len(orig), '-> new lines:', len(new))
import difflib
diff = list(difflib.unified_diff(orig, new, lineterm='', n=1))
for line in diff:
    print(line[:120])
