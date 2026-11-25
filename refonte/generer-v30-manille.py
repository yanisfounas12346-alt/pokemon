#!/usr/bin/env python3
"""V30: maison des jardins, intérieur autonome et gardien."""
import argparse, hashlib, json, struct, importlib.util
from collections import deque
from pathlib import Path
spec=importlib.util.spec_from_file_location("v27",Path(__file__).with_name("generer-v27.py"))
v27=importlib.util.module_from_spec(spec)
spec.loader.exec_module(v27)
inj=v27.inj
export=v27.export
crc=inj.crc
ALLOC=0x1107000
GRID=0x1106000
BANKS=0x48b464
OUT=0x4874a0
TEMPLATE=0x487a6c

def build(source, previous):
    if len(source)!=0x2000000 or crc(source)!=0x75204b25: raise ValueError('V26 requise')
    base=inj.apply_ups(source,previous)
    if crc(base)!=0x562956d5: raise ValueError('V29 requise')
    t=bytearray(base); blob=bytearray(); allowed=set()
    def ptr(at):
        v=struct.unpack_from('<I',base,at)[0]-0x8000000
        if not 0<=v<len(base): raise ValueError('Pointeur invalide')
        return v
    def addr(off): return struct.pack('<I',0x8000000+off)
    def put(at,data):
        t[at:at+len(data)]=data;allowed.update(range(at,at+len(data)))
    def alloc(data):
        while len(blob)%4: blob.append(0)
        at=ALLOC+len(blob);blob.extend(data);return at
    def text(s):
        out=bytearray()
        for c in s:
            if 'A'<=c<='Z': out.append(0xbb+ord(c)-65)
            elif 'a'<=c<='z': out.append(0xd5+ord(c)-97)
            else: out.append({' ':0,'.':0xad,'\n':0xfe,'\f':0xfb}[c])
        return bytes(out)+b'\xff'
    def dialogue(s,kind):
        q=alloc(text(s));return alloc(b'\x0f\x00'+addr(q)+bytes([9,kind,2]))
    layout=ptr(OUT); e=ptr(OUT+4); group=ptr(BANKS+4)
    if ptr(layout+12)!=GRID or struct.unpack_from('<II',base,layout)!=(28,20) or group!=0x48ad30 or ptr(BANKS+8)-group!=20 or base[e:e+4]!=bytes([8,3,9,4]): raise ValueError('Structure Manille inattendue')
    rows=[list(struct.unpack_from('<28H',base,GRID+56*y)) for y in range(20)]
    footprint={(x,y) for x in range(20,25) for y in range(3,8)}
    if not all(rows[y][x] in (0x3001,0x3004,0x305e) for x,y in footprint): raise ValueError('Terrain inattendu')
    for y in range(5):
        for x in range(5): rows[3+y][20+x]=rows[4+y][2+x]
    if rows[7][23]!=0x0648 or rows[8][23]!=0x305e or rows[7][25] not in (0x3001,0x305e): raise ValueError('Entrée inattendue')
    rows[7][25]=0x3403
    for x,y in footprint|{(25,7)}: put(GRID+2*(y*28+x),struct.pack('<H',rows[y][x]))
    ow=ptr(e+8); signs=ptr(e+16)
    new_warps=alloc(base[ow:ow+24]+struct.pack('<hhBBBB',23,7,0,1,5,1))
    sign_script=dialogue('Maison des jardins.\nEntree libre.',3)
    new_signs=alloc(base[signs:signs+48]+struct.pack('<hhBBH',25,7,0,0,0)+addr(sign_script))
    outdoor_events=bytearray(base[e:e+20]);outdoor_events[1]=4;outdoor_events[3]=5
    outdoor_events[8:12]=addr(new_warps);outdoor_events[16:20]=addr(new_signs)
    put(OUT+4,addr(alloc(outdoor_events)))
    il=ptr(TEMPLATE); ie=ptr(TEMPLATE+4); iw=ptr(ie+8); io=ptr(ie+4)
    if struct.unpack_from('<II',base,il)!=(10,9) or base[ie:ie+4]!=bytes([1,2,0,0]): raise ValueError('Interieur inattendu')
    warps=bytearray(base[iw:iw+16])
    for j in (0,8): warps[j+5:j+8]=bytes([3,9,0])
    wi=alloc(warps)
    npc=bytearray(base[io:io+24])
    if struct.unpack_from('<hh',npc,4)!=(6,4): raise ValueError('PNJ inattendu')
    npc[9]=0; npc[10]=0
    npc[16:20]=addr(dialogue('Bienvenue dans la maison\ndes jardins de Manille.\fLes jardins sont ouverts\naux voyageurs.',2))
    npc[20:24]=b'\0'*4
    ni=alloc(npc)
    events=alloc(bytes([1,2,0,0])+addr(ni)+addr(wi)+b'\0'*8)
    script_list=alloc(b'\0')
    header=bytearray(base[TEMPLATE:TEMPLATE+28]);header[4:8]=addr(events);header[8:12]=addr(script_list);header[12:16]=b'\0'*4;header[20]=base[OUT+20]
    hi=alloc(header)
    new_group=alloc(base[group:group+20]+addr(hi));put(BANKS+4,addr(new_group))
    end=ALLOC+len(blob)
    if len(base.rstrip(b'\0'))>ALLOC or any(base[ALLOC:end]): raise ValueError('Espace ROM non libre')
    if any(0x8000000+ALLOC<=v<0x8000000+end for (v,) in struct.iter_unpack('<I',base)): raise ValueError('Reference a la zone')
    put(ALLOC,blob)
    target=bytes(t)
    if any(a!=b and i not in allowed for i,(a,b) in enumerate(zip(base,target))): raise ValueError('Modification hors perimetre')
    def reachable(rows,start,blocked=frozenset()):
        def walk(p):
            x,y=p;return 0<=y<len(rows) and 0<=x<len(rows[y]) and (rows[y][x]&0xc00)==0 and p not in blocked
        if not walk(start): raise ValueError('Départ bloqué')
        seen={start};q=deque([start])
        while q:
            x,y=q.popleft()
            for p in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
                if p not in seen and walk(p):seen.add(p);q.append(p)
        return seen
    if (23,8) not in reachable(rows,(19,11)): raise ValueError('Maison inaccessible')
    ig=ptr(il+12);ir=[struct.unpack_from('<10H',base,ig+20*y) for y in range(9)]
    r=reachable(ir,(4,8),{(6,4)})
    if (6,5) not in r or (3,8) not in r: raise ValueError('Interieur inaccessible')
    if target[new_group:new_group+20]!=base[group:group+20] or target[new_warps:new_warps+24]!=base[ow:ow+24] or target[new_signs:new_signs+48]!=base[signs:signs+48]: raise ValueError('Evenements anciens modifies')
    if target[hi:hi+4]!=base[TEMPLATE:TEMPLATE+4] or crc(target)!=0xA47494E5: raise ValueError('Cible inattendue')
    patch=export.create_ups(source,target)
    if inj.apply_ups(source,patch)!=target or inj.apply_ups(target,export.reverse_ups(patch))!=source: raise ValueError('Echec UPS')
    return patch

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('source',type=Path);p.add_argument('previous',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args()
    if a.output.suffix.lower()!='.ups': p.error('Sortie UPS requise')
    patch=build(a.source.read_bytes(),a.previous.read_bytes())
    with a.output.open('xb') as f:f.write(patch)
    print(json.dumps({'crc32_cible':'A47494E5','sha256_patch':hashlib.sha256(patch).hexdigest(),'test_emulateur':False},indent=2))
