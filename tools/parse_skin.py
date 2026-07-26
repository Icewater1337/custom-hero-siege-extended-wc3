import struct, json, os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

def read_str(data, pos):
    end = data.index(b'\x00', pos)
    return data[pos:end].decode('utf-8', errors='replace'), end + 1

def parse_w3o(path, extended):
    data = open(path, 'rb').read()
    pos = 0
    version = struct.unpack_from('<i', data, pos)[0]; pos += 4
    objects = []
    for table in range(2):
        count = struct.unpack_from('<i', data, pos)[0]; pos += 4
        for _ in range(count):
            oldid = data[pos:pos+4].decode('latin1'); pos += 4
            newid = data[pos:pos+4].decode('latin1'); pos += 4
            if version >= 3:
                ec = struct.unpack_from('<i', data, pos)[0]; pos += 4
                pos += 4 * ec
            mc = struct.unpack_from('<i', data, pos)[0]; pos += 4
            mods = []
            for _ in range(mc):
                mid = data[pos:pos+4].decode('latin1'); pos += 4
                vt = struct.unpack_from('<i', data, pos)[0]; pos += 4
                lvl = 0
                if extended:
                    lvl = struct.unpack_from('<i', data, pos)[0]; pos += 4
                    pos += 4
                if vt == 0:
                    val = struct.unpack_from('<i', data, pos)[0]; pos += 4
                elif vt in (1, 2):
                    val = struct.unpack_from('<f', data, pos)[0]; pos += 4
                else:
                    val, pos = read_str(data, pos)
                pos += 4
                mods.append({'field': mid, 'level': lvl, 'value': val})
            objects.append({'base': oldid,
                            'id': newid if newid != '\x00\x00\x00\x00' else oldid,
                            'table': 'original' if table == 0 else 'custom',
                            'mods': mods})
    return version, objects

if __name__ == '__main__':
    ver, objs = parse_w3o('x_wm_Skin.w3u', False)
    json.dump(objs, open('obj_skin_units.json', 'w', encoding='utf-8'),
              ensure_ascii=False, indent=0)
    print('skin w3u:', ver, len(objs), 'objects')
    for o in objs:
        if o['id'] in ('H000', 'H01D'):
            print('---', o['id'], 'base', o['base'])
            for m in o['mods']:
                print('   ', m['field'], '=', str(m['value'])[:90])
