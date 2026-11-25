#!/usr/bin/env python3
"""V33: enceinte historique d'Intramuros, place et archives. Base V32."""
import argparse, hashlib, json, struct
from collections import deque
from pathlib import Path
from rom_v27 import crc, patch_apply, patch_create
ALLOC=0x112a000
BANKS=0x48b464
OUT=0x4874a0

def build(source, previous):
    if len(source)!=0x2000000 or crc(source)!=0x75204B25: raise ValueError('V26 requise')
    base=patch_apply(source,previous)
    if crc(base)!=0x1F9AFEDE: raise ValueError('V32 requise')
    target=bytearray(base);blob=bytearray();allowed=set()
    def ptr(p):
        n=struct.unpack_from('<I',base,p)[0]-0x8000000
        if not 0<=n<len(base): raise ValueError('Pointeur invalide')
        return n
    def addr(p): return struct.pack('<I',p+0x8000000)
    def put(p,data):
        target[p:p+len(data)]=data;allowed.update(range(p,p+len(data)))
    def alloc(data):
        while len(blob)%4:blob.append(0)
        p=ALLOC+len(blob);blob.extend(data);return p
    def encode(s):
        out=bytearray()
        for c in s:
            if 'A'<=c<='Z':out.append(0xbb+ord(c)-65)
            elif 'a'<=c<='z':out.append(0xd5+ord(c)-97)
            else:out.append({' ':0,'.':0xad,'\n':0xfe,'\f':0xfb,'é':0x1b,'è':0x1a}[c])
        return bytes(out)+b'\xff'
    def dialogue(s,kind=2):
        assert all(len(line)<=26 for line in s.replace('\f','\n').split('\n'))
        return alloc(b'\x0f\x00'+addr(alloc(encode(s)))+bytes([9,kind,2]))
    def rows(h):
        l=ptr(h);w,n=struct.unpack_from('<II',base,l);g=ptr(l+12)
        return [list(struct.unpack_from('<%dH'%w,base,g+2*w*y)) for y in range(n)]
    def warp(x,y,e,d,m,b):return struct.pack('<hhBBBB',x,y,e,d,m,b)
    def npc(template,local,x,y,script):
        n=bytearray(base[template:template+24]);n[0]=local;struct.pack_into('<hh',n,4,x,y);n[8]=3;n[9]=8;n[10:16]=b'\0'*6;n[16:20]=addr(script);n[20:24]=b'\0'*4;return n
    def flood(r,start,blocked=()):
        def walk(p):
            x,y=p;return 0<=y<len(r) and 0<=x<len(r[y]) and not r[y][x]&0xc00 and p not in blocked
        assert walk(start);seen={start};q=deque([start])
        while q:
            x,y=q.popleft()
            for p in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
                if p not in seen and walk(p):seen.add(p);q.append(p)
        return seen
    layout=ptr(OUT);e=ptr(OUT+4);group=ptr(BANKS+4)
    assert struct.unpack_from('<II',base,layout)==(52,20) and base[e:e+4]==bytes([11,7,9,8])
    old=rows(OUT);r=[row+[0x3001]*20 for row in old]
    # Use the existing stone enclosure tiles, with their native collision bits.
    for y in range(20):
        for x in range(52,72):
            if y in (0,1,18,19) or x>=70:r[y][x]=((0x05d4,0x05d5),(0x05dc,0x05dd))[y%2][x%2]
            elif y in (9,10) or 56<=x<=68 and 11<=y<=15:r[y][x]=0x305e
    for y in (9,10):
        for x in range(50,56):r[y][x]=0x305e
    # Stone perimeter, with an open two-cell gate to the west.
    for x in range(55,70):
        r[3][x]=0x0549;r[16][x]=0x0549
    r[3][55]=r[16][55]=0x0541;r[3][69]=r[16][69]=0x054a
    for y in range(4,16):
        if y not in (9,10):r[y][55]=0x0542
        r[y][69]=0x0540
    # Two small flower beds frame the south plaza, with clear circulation.
    for x,y in [(57,13),(57,14),(67,13),(67,14)]:r[y][x]=0x3004
    # Historic archive facade: adapt a native 5x5 roof/wall/door assembly.
    for y in range(5):
        for x in range(5):r[4+y][61+x]=old[4+y][2+x]
    assert r[8][64]==0x0648
    for y in (9,10):r[y][64]=0x305e
    signs_new=[(54,8,'Intramuros.\nQuartier historique.'),(66,8,'Archives de Manille.\nEntree libre.')]
    for x,y,_ in signs_new:r[y][x]=0x3403
    changed_old={(x,y) for y in range(20) for x in range(52) if r[y][x]!=old[y][x]}
    assert changed_old=={(x,y) for y in (9,10) for x in (50,51)}
    grid=alloc(b''.join(struct.pack('<72H',*row) for row in r));put(layout,struct.pack('<I',72));put(layout+12,addr(grid))
    oo,ow,os=ptr(e+4),ptr(e+8),ptr(e+16)
    residents=[(12,57,8,oo+24,'Les murs gardent la trace\ndes anciens passages.'),(13,60,13,oo+48,'Je repare les pierres.\fLe quartier appartient\na tous les habitants.'),(14,66,12,oo,'Les archives conservent\nles noms des voyageurs.')]
    objects=bytearray(base[oo:oo+11*24])
    for local,x,y,template,s in residents:
        assert not r[y][x]&0xc00
        objects.extend(npc(template,local,x,y,dialogue(s)))
    warps=base[ow:ow+7*8]+warp(64,8,0,1,10,1)
    signs=base[os:os+8*12]
    for x,y,s in signs_new:signs+=struct.pack('<hhBBH',x,y,0,0,0)+addr(dialogue(s,3))
    oe=bytearray(base[e:e+20]);oe[:4]=bytes([14,8,9,10]);oe[4:8]=addr(alloc(objects));oe[8:12]=addr(alloc(warps));oe[16:20]=addr(alloc(signs));put(OUT+4,addr(alloc(oe)))
    # Clone a house interior but use an independent script, object and exit list.
    template=0x487a6c;te=ptr(template+4);il=ptr(template)
    assert struct.unpack_from('<II',base,il)==(10,9) and base[te:te+4]==bytes([1,2,0,0])
    nw=bytearray(base[ptr(te+8):ptr(te+8)+16]);nw[5:8]=nw[13:16]=bytes([7,9,0])
    no=npc(ptr(te+4),1,6,4,dialogue('Bienvenue aux archives.\fOn y conserve les lettres\net les anciens registres.\fTu peux revenir quand\ntu le souhaites.'))
    iev=alloc(bytes([1,2,0,0])+addr(alloc(no))+addr(alloc(nw))+b'\0'*8)
    h=bytearray(base[template:template+28]);h[4:8]=addr(iev);h[8:12]=addr(alloc(b'\0'));h[12:16]=b'\0'*4;h[20]=base[OUT+20]
    ih=alloc(h);put(BANKS+4,addr(alloc(base[group:group+40]+addr(ih))))
    end=ALLOC+len(blob)
    assert len(base.rstrip(b'\0'))<=ALLOC and not any(base[ALLOC:end])
    assert not any(0x8000000+ALLOC<=v<0x8000000+end for (v,) in struct.iter_unpack('<I',base))
    put(ALLOC,blob)
    seen=flood(r,(19,11),{(x,y) for _,x,y,_,_ in residents})
    assert {(54,9),(56,9),(64,9),(66,9),(57,9),(60,12),(66,11),(61,14)}<=seen
    assert all(r[y][x]&0xc00 for y in range(4,16) if y not in (9,10) for x in (55,69))
    ins=flood(rows(template),(4,8),{(6,4)})
    assert {(6,5),(3,8)}<=ins
    target=bytes(target)
    assert not any(a!=b and i not in allowed for i,(a,b) in enumerate(zip(base,target)))
    assert target[ptr(e+12):ptr(e+12)+9*16]==base[ptr(e+12):ptr(e+12)+9*16]
    patch=patch_create(source,target)
    assert patch_apply(source,patch)==target and patch_apply(target,patch,True)==source
    report={'version':'V33','crc32_source':f'{crc(source):08X}','crc32_cible':f'{crc(target):08X}','sha256_patch':hashlib.sha256(patch).hexdigest(),'dimensions':[72,20],'nouvelles_cartes':[[1,10]],'nouveaux_pnj':4,'nouveaux_panneaux':2,'cases_accessibles_extension':sum(x>=52 for x,y in seen),'ancienne_surface_modifiee':len(changed_old),'aller_retour':True,'test_emulateur':False}
    return patch,report
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('previous',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    patch,report=build(a.source.read_bytes(),a.previous.read_bytes())
    with a.output.open('xb') as f:f.write(patch)
    print(json.dumps(report,ensure_ascii=False,indent=2))
