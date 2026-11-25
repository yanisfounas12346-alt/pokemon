#!/usr/bin/env python3
"""V36: baie, quais et capitainerie. Base V35."""
import argparse, hashlib, json, struct
from collections import deque
from pathlib import Path
from rom_v27 import crc, patch_apply, patch_create
ALLOC=0x1148000
BANKS=0x48b464
OUT=0x4874a0

def build(source, previous):
    if len(source)!=0x2000000 or crc(source)!=0x75204B25: raise ValueError('V26 requise')
    base=patch_apply(source,previous)
    if crc(base)!=0x45CC7D3B: raise ValueError('V35 requise')
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
            else:out.append({' ':0,'.':0xad,'\n':0xfe,'\f':0xfb,'é':0x1b,'è':0x1a,'à':0x16,'ç':0x19,'î':0x20,'’':0xb4,'ê':0x1c,'ô':0x22,'û':0x25}[c])
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
    assert struct.unpack_from('<II',base,layout)==(120,20) and base[e:e+4]==bytes([21,11,9,15])
    old=rows(OUT);r=[row+[0x3001]*28 for row in old]
    for y in range(20):
        for x in range(120,148):
            if y in (0,1,18,19) or x>=146:r[y][x]=((0x05d4,0x05d5),(0x05dc,0x05dd))[y%2][x%2]
            elif y in (8,9,10,11) or x in (125,126):r[y][x]=0x305e
    for y in (9,10):
        for x in range(118,146):r[y][x]=0x305e
    ref=ptr(ptr(BANKS));assert base[ptr(ref)+16:ptr(ref)+24]==base[layout+16:layout+24]
    rr=rows(ref);assert rr[4][21]==0x10a1 and rr[2][22]==0x10b0 and rr[9][22]==0x3002
    for left,right in ((127,132),(135,140),(143,145)):
        for y in range(12,18):
            for x in range(left,right+1):
                if y==12:tile=0x10b0 if x==left else 0x10b2 if x==right else 0x10b1
                else:tile=0x10b8 if x==left else 0x10ba if x==right else 0x10a1
                r[y][x]=tile
    for y in range(12,18):
        for x in (133,134,141,142):r[y][x]=0x305e
    for y in range(5):
        for x in range(5):r[3+y][129+x]=old[4+y][2+x]
    assert r[7][132]==0x0648
    r[8][132]=0x305e
    signs_new=[(122,8,'Baie de Manille.\nPromenade des quais.'),(135,7,'Capitainerie.\nAccueil des voyageurs.'),(144,10,'Quais de pêche.\nAttention à l’eau.')]
    for x,y,_ in signs_new:r[y][x]=0x3403
    changed_old={(x,y) for y in range(20) for x in range(120) if r[y][x]!=old[y][x]}
    assert changed_old=={(x,y) for y in (9,10) for x in (118,119)}
    grid=alloc(b''.join(struct.pack('<148H',*row) for row in r));put(layout,struct.pack('<I',148));put(layout+12,addr(grid))
    oo,ow,os=ptr(e+4),ptr(e+8),ptr(e+16)
    residents=[(22,124,11,oo+24,'Bienvenue sur les quais.\nRegarde la baie.'),(23,137,9,oo+48,'Je répare les filets.\nLa pêche prend du temps.'),(24,133,15,oo,'Je surveille les eaux.\nLe quai reste accessible.'),(25,142,15,oo+24,'Je ramène mes prises\nau marché de Binondo.'),(26,139,5,oo+48,'La capitainerie tient\nle registre des arrivées.')]
    objects=bytearray(base[oo:oo+21*24])
    for local,x,y,template,s in residents:
        assert not r[y][x]&0xc00
        objects.extend(npc(template,local,x,y,dialogue(s)))
    warps=base[ow:ow+11*8]+struct.pack('<hhBBBB',132,7,0,1,14,1)
    signs=base[os:os+15*12]
    for x,y,s in signs_new:signs+=struct.pack('<hhBBH',x,y,0,0,0)+addr(dialogue(s,3))
    oe=bytearray(base[e:e+20]);oe[:4]=bytes([26,12,9,18]);oe[4:8]=addr(alloc(objects));oe[8:12]=addr(alloc(warps));oe[16:20]=addr(alloc(signs));put(OUT+4,addr(alloc(oe)))
    template=0x487a88;te=ptr(template+4);il=ptr(template);ho=ptr(te+4)
    assert struct.unpack_from('<II',base,il)==(11,8) and base[te:te+4]==bytes([2,2,0,0])
    nw=bytearray(base[ptr(te+8):ptr(te+8)+16]);nw[5:8]=nw[13:16]=bytes([11,9,0])
    no=npc(ho,1,3,4,dialogue('Voici la capitainerie.\fNous notons les départs\net les arrivées.'))+npc(ho+24,2,8,4,dialogue('Les quais sont ouverts.\nPrudence près de l’eau.'))
    iev=alloc(bytes([2,2,0,0])+addr(alloc(no))+addr(alloc(nw))+b'\0'*8)
    h=bytearray(base[template:template+28]);h[4:8]=addr(iev);h[8:12]=addr(alloc(b'\0'));h[12:16]=b'\0'*4;h[20]=base[OUT+20]
    ih=alloc(h);put(BANKS+4,addr(alloc(base[group:group+56]+addr(ih))))
    end=ALLOC+len(blob)
    assert len(base.rstrip(b'\0'))<=ALLOC and not any(base[ALLOC:end])
    assert not any(0x8000000+ALLOC<=v<0x8000000+end for (v,) in struct.iter_unpack('<I',base))
    put(ALLOC,blob)
    blocked={struct.unpack_from('<hh',objects,i+4) for i in range(0,len(objects),24)}
    water={(x,y) for y in range(20) for x in range(120,148) if r[y][x] in (0x10b0,0x10b1,0x10b2,0x10b8,0x10ba,0x10a1)}
    seen=flood(r,(19,11),blocked|water)
    assert {(122,9),(132,8),(135,8),(144,9),(124,10),(137,10),(133,14),(142,14),(139,6),(134,17),(141,17)}<=seen
    assert not seen&water and len(water)==90
    assert {(3,3),(8,3),(3,7)}<=flood(rows(template),(4,7),{(3,4),(8,4)})
    target=bytes(target)
    assert not any(a!=b and i not in allowed for i,(a,b) in enumerate(zip(base,target)))
    assert target[ptr(e+12):ptr(e+12)+9*16]==base[ptr(e+12):ptr(e+12)+9*16]
    patch=patch_create(source,target)
    assert patch_apply(source,patch)==target and patch_apply(target,patch,True)==source
    report={'version':'V36','crc32_source':f'{crc(source):08X}','crc32_cible':f'{crc(target):08X}','sha256_patch':hashlib.sha256(patch).hexdigest(),'dimensions':[148,20],'nouvelles_cartes':[[1,14]],'nouveaux_pnj':7,'nouveaux_panneaux':3,'cases_eau':len(water),'cases_accessibles_extension':sum(x>=120 for x,y in seen),'ancienne_surface_modifiee':len(changed_old),'aller_retour':True,'test_emulateur':False}
    return patch,report
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('previous',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    patch,report=build(a.source.read_bytes(),a.previous.read_bytes())
    with a.output.open('xb') as f:f.write(patch)
    print(json.dumps(report,ensure_ascii=False,indent=2))
