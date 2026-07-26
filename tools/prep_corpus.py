"""Build analysis corpus: strings.json, object data JSON/CSV, script chunks."""
import os, re, json, struct

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# ---------- 1. Parse WTS ----------
raw = open('x_war3map.wts', 'rb').read().decode('utf-8-sig')
# Format: STRING <n> [\n // comment]* \n { \n content \n }
entries = {}
pos = 0
pat_head = re.compile(r'STRING (\d+)\s*\r?\n')
while True:
    m = pat_head.search(raw, pos)
    if not m:
        break
    num = int(m.group(1))
    brace = raw.find('{', m.end())
    if brace == -1:
        break
    end = raw.find('\r\n}', brace)
    if end == -1:
        end = raw.find('\n}', brace)
        content = raw[brace + 2:end] if end != -1 else ''
        pos = end + 2
    else:
        content = raw[brace + 3:end]
        pos = end + 3
    entries[num] = content
json.dump(entries, open('strings.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('WTS entries:', len(entries))

def resolve(s):
    if isinstance(s, str) and s.startswith('TRIGSTR_'):
        try:
            return entries.get(int(s[8:].lstrip('0') or '0'), s)
        except ValueError:
            return s
    return s

# ---------- 2. Parse W3O object files ----------
def read_str(data, pos):
    end = data.index(b'\0', pos)
    return data[pos:end].decode('utf-8', errors='replace'), end + 1

def fourcc(b):
    return b.decode('latin1')

def parse_w3o(path, extended):
    """Parse a war3map object-data file. extended=True for w3a/w3d/w3q (has level/pointer)."""
    data = open(path, 'rb').read()
    pos = 0
    version = struct.unpack_from('<i', data, pos)[0]; pos += 4
    objects = []
    for table in range(2):  # original table, custom table
        count = struct.unpack_from('<i', data, pos)[0]; pos += 4
        for _ in range(count):
            oldid = fourcc(data[pos:pos+4]); pos += 4
            newid = fourcc(data[pos:pos+4]); pos += 4
            if version >= 3:
                extra_count = struct.unpack_from('<i', data, pos)[0]; pos += 4
                pos += 4 * extra_count  # skip extra set flags/data
            mod_count = struct.unpack_from('<i', data, pos)[0]; pos += 4
            mods = []
            for _ in range(mod_count):
                mid = fourcc(data[pos:pos+4]); pos += 4
                vtype = struct.unpack_from('<i', data, pos)[0]; pos += 4
                level = dpointer = 0
                if extended:
                    level = struct.unpack_from('<i', data, pos)[0]; pos += 4
                    dpointer = struct.unpack_from('<i', data, pos)[0]; pos += 4
                if vtype == 0:
                    val = struct.unpack_from('<i', data, pos)[0]; pos += 4
                elif vtype in (1, 2):
                    val = struct.unpack_from('<f', data, pos)[0]; pos += 4
                elif vtype == 3:
                    val, pos = read_str(data, pos)
                else:
                    raise ValueError(f'bad vtype {vtype} at {pos}')
                pos += 4  # trailing old/new id (sanity field)
                mods.append({'field': mid, 'level': level, 'value': val})
            objects.append({'base': oldid, 'id': newid if newid != '\0\0\0\0' else oldid,
                            'table': 'original' if table == 0 else 'custom', 'mods': mods})
    return version, objects

results = {}
for path, ext, name in [('x_war3map.w3a', True, 'abilities'),
                        ('x_war3map.w3u', False, 'units'),
                        ('x_war3map.w3t', False, 'items'),
                        ('x_war3map.w3h', False, 'buffs'),
                        ('x_war3map.w3b', False, 'destructables'),
                        ('x_war3map.w3d', True, 'doodads')]:
    try:
        ver, objs = parse_w3o(path, ext)
        results[name] = objs
        print(f'{name}: version {ver}, {len(objs)} objects, '
              f'{sum(len(o["mods"]) for o in objs)} field mods')
    except Exception as e:
        print(f'{name}: FAILED {e!r}')

# Resolve TRIGSTR references in object data values
for name, objs in results.items():
    for o in objs:
        for mmod in o['mods']:
            if isinstance(mmod['value'], str) and 'TRIGSTR_' in mmod['value']:
                mmod['value'] = resolve(mmod['value'])
    json.dump(objs, open(f'obj_{name}.json', 'w', encoding='utf-8'),
              ensure_ascii=False, indent=0)

# ---------- 3. Split war3map.j ----------
script = open('x_war3map.j', 'r', encoding='utf-8', errors='replace').read()
lines = script.split('\n')
print('script lines:', len(lines))
os.makedirs('jchunks', exist_ok=True)
CHUNK = 2500
n = 0
for i in range(0, len(lines), CHUNK):
    chunk = lines[i:i + CHUNK]
    with open(f'jchunks/chunk_{i//CHUNK:02d}_L{i+1}.j', 'w', encoding='utf-8') as f:
        f.write('\n'.join(chunk))
    n += 1
print('chunks written:', n)
