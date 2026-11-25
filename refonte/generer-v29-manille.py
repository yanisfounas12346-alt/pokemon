#!/usr/bin/env python3
"""V29: extension orientale de Manille, événements et coordonnées conservés."""
import argparse
import importlib.util
import hashlib
import struct
from collections import deque
from pathlib import Path

spec=importlib.util.spec_from_file_location("v28",Path(__file__).with_name("generer-v28-manille.py"))
v28=importlib.util.module_from_spec(spec)
spec.loader.exec_module(v28)
inj=v28.inj
export=v28.v27.export
LAYOUT=0x3ef170
OLD_GRID=0x3eee50
NEW_GRID=0x1106000
W,H,NW=20,20,28

def build(source):
    base=inj.apply_ups(source,v28.build(source))
    if inj.crc(base)!=0xDF5A8ED8: raise ValueError("V28 inattendue")
    header=0x4874a0
    ptr=lambda p:struct.unpack_from("<I",base,p)[0]-0x8000000
    if ptr(header)!=LAYOUT or ptr(LAYOUT+12)!=OLD_GRID or struct.unpack_from("<II",base,LAYOUT)!=(W,H): raise ValueError("Plan inattendu")
    conn=ptr(header+12)
    if struct.unpack_from("<I",base,conn)[0]!=1 or struct.unpack_from("<IiBBH",base,ptr(conn+4))!=(2,0,0,16,0): raise ValueError("Connexions inattendues")
    old=[list(struct.unpack_from("<20H",base,OLD_GRID+40*y)) for y in range(H)]
    rows=[r+[0x3001]*8 for r in old]
    for y in range(H):
        for x in range(W,NW):
            if y in (0,1,18,19) or x>=26:
                rows[y][x]=((0x05d4,0x05d5),(0x05dc,0x05dd))[y%2][x%2]
            elif y in (5,6,13,14) and x in (21,24): rows[y][x]=0x3004
            elif x in (22,23) or y in (9,10): rows[y][x]=0x305e
    payload=b"".join(struct.pack("<28H",*r) for r in rows)
    end=NEW_GRID+len(payload)
    if any(base[NEW_GRID:end]) or len(base.rstrip(b"\0"))>NEW_GRID: raise ValueError("Zone non vide")
    for (v,) in struct.iter_unpack("<I",base):
        if 0x8000000+NEW_GRID<=v<0x8000000+end: raise ValueError("Référence à la zone choisie")
    def walk(x,y): return 0<=x<NW and 0<=y<H and rows[y][x] in (0x3001,0x3004,0x305e)
    start=(19,11); seen={start}; queue=deque([start])
    if not walk(*start): raise ValueError("Entrée inaccessible")
    while queue:
        x,y=queue.popleft()
        for p in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
            if p not in seen and walk(*p): seen.add(p); queue.append(p)
    added={(x,y) for y in range(H) for x in range(W,NW) if walk(x,y)}
    if not added<=seen or len(added)!=96 or any(r[:W]!=o for r,o in zip(rows,old)): raise ValueError("Accessibilité ou conservation invalide")
    target=bytearray(base)
    struct.pack_into("<I",target,LAYOUT,NW)
    struct.pack_into("<I",target,LAYOUT+12,0x8000000+NEW_GRID)
    target[NEW_GRID:end]=payload
    target=bytes(target)
    allowed=set(range(LAYOUT,LAYOUT+4))|set(range(LAYOUT+12,LAYOUT+16))|set(range(NEW_GRID,end))
    if any(a!=b and i not in allowed for i,(a,b) in enumerate(zip(base,target))): raise ValueError("Écriture hors périmètre")
    patch=export.create_ups(source,target)
    if inj.apply_ups(source,patch)!=target or inj.apply_ups(target,export.reverse_ups(patch))!=source: raise ValueError("Échec UPS")
    if inj.crc(target)!=0x562956D5: raise ValueError("CRC cible inattendu")
    return patch

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("source",type=Path)
    p.add_argument("output",type=Path)
    a=p.parse_args()
    if a.output.suffix.lower()!=".ups": p.error("Sortie UPS requise")
    patch=build(a.source.read_bytes())
    with a.output.open("xb") as f: f.write(patch)
    print("SHA256 UPS",hashlib.sha256(patch).hexdigest())
