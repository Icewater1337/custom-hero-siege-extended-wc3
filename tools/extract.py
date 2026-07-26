import os
from mpyq import MPQArchive

os.chdir(os.path.dirname(os.path.abspath(__file__)))
a = MPQArchive('map.w3x', listfile=False)

BS = '\\'
candidates = [
    'war3map.j', BS.join(['Scripts', 'war3map.j']), BS.join(['scripts', 'war3map.j']),
    'war3map.lua', BS.join(['Scripts', 'war3map.lua']),
    'war3map.w3i', 'war3map.wts', 'war3map.w3u', 'war3map.w3t',
    'war3map.w3a', 'war3map.w3b', 'war3map.w3d', 'war3map.w3q',
    'war3map.w3h', 'war3map.wtg', 'war3map.wct', 'war3map.w3s',
    'war3map.w3r', 'war3map.w3c', 'war3map.doo', 'war3mapUnits.doo',
    'war3map.shd', 'war3map.wpm', 'war3map.mmp', 'war3map.w3e',
    'war3map.imp', 'war3mapMisc.txt', 'war3mapSkin.txt', 'war3mapExtra.txt',
    'war3mapMap.blp', 'war3mapPreview.tga',
]
slks = ['UpgradeData.slk', 'UnitAbilities.slk', 'UnitBalance.slk',
        'UnitData.slk', 'UnitUI.slk', 'UnitWeapons.slk', 'ItemData.slk',
        'AbilityData.slk', 'AbilityBuffData.slk', 'DestructableData.slk',
        'CommandFunc.txt', 'ItemFunc.txt', 'ItemStrings.txt',
        'HumanUnitFunc.txt', 'OrcUnitFunc.txt', 'NightElfUnitFunc.txt',
        'UndeadUnitFunc.txt', 'NeutralUnitFunc.txt', 'CampaignUnitFunc.txt',
        'HumanUnitStrings.txt', 'OrcUnitStrings.txt', 'NightElfUnitStrings.txt',
        'UndeadUnitStrings.txt', 'NeutralUnitStrings.txt', 'CampaignUnitStrings.txt',
        'HumanAbilityFunc.txt', 'OrcAbilityFunc.txt', 'NightElfAbilityFunc.txt',
        'UndeadAbilityFunc.txt', 'NeutralAbilityFunc.txt', 'CommonAbilityFunc.txt',
        'CampaignAbilityFunc.txt', 'ItemAbilityFunc.txt',
        'HumanAbilityStrings.txt', 'OrcAbilityStrings.txt',
        'NightElfAbilityStrings.txt', 'UndeadAbilityStrings.txt',
        'NeutralAbilityStrings.txt', 'CommonAbilityStrings.txt',
        'CampaignAbilityStrings.txt', 'ItemAbilityStrings.txt',
        'CampaignUpgradeFunc.txt', 'HumanUpgradeFunc.txt',
        'OrcUpgradeFunc.txt', 'NightElfUpgradeFunc.txt',
        'UndeadUpgradeFunc.txt', 'NeutralUpgradeFunc.txt']
for s in slks:
    candidates.append(s)
    candidates.append(BS.join(['Units', s]))
candidates += ['(attributes)', '(signature)', '(listfile)']

found = []
for name in candidates:
    try:
        data = a.read_file(name)
    except Exception:
        data = None
    if data:
        found.append((name, len(data)))
        safe = name.replace(BS, '_').replace('(', '').replace(')', '')
        with open('x_' + safe, 'wb') as f:
            f.write(data)

for n, l in found:
    print(f'{l:>10}  {n}')
print(f'--- {len(found)} of {len(candidates)} candidates found; archive has 702 blocks')
