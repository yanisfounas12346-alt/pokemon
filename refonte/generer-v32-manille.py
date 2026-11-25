#!/usr/bin/env python3
"""V32: centre de soins de Manille, étage calme et habitants. V31 requise."""
import argparse, hashlib, json, struct
from collections import deque
from pathlib import Path
from rom_v27 import crc, patch_apply, patch_create
ALLOC=0x110c000
BANKS=0x48b464
OUT=0x4874a0

def build(source, previous):
    if len(source)!=0x2000000 or crc(source)!=0x75204B25: raise ValueError('V26 requise')
    base=patch_apply(source,previous)
    if crc(base)!=0x38809DF3: raise ValueError('V31 requise')
    target=bytearray(base); blob=bytearray(); allowed=set()
    def ptr(p):
        n=struct.unpack_from('<I',base,p)[0]-0x8000000
        if not 0<=n<len(base): raise ValueError('Pointeur invalide')
        return n
    def addr(p): return struct.pack('<I',p+0x8000000)
    def put(p,data):
        target[p:p+len(data)]=data; allowed.update(range(p,p+len(data)))
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
    def dialogue(s,kind=2):return alloc(b'\x0f\x00'+addr(alloc(encode(s)))+bytes([9,kind,2]))
    def rows(h):
        l=ptr(h);w,n=struct.unpack_from('<II',base,l);g=ptr(l+12)
        return [list(struct.unpack_from('<%dH'%w,base,g+2*w*y)) for y in range(n)]
    def warp(x,y,e,d,m,b):return struct.pack('<hhBBBB',x,y,e,d,m,b)
    def npc(template,local,x,y,script):
        n=bytearray(base[template:template+24]);n[0]=local;struct.pack_into('<hh',n,4,x,y);n[9]=8;n[10:16]=b'\0'*6;n[16:20]=addr(script);n[20:24]=b'\0'*4;return n
    def flood(r,start,blocked=()):
        def walk(p):
            x,y=p;return 0<=y<len(r) and 0<=x<len(r[y]) and not r[y][x]&0xc00 and p not in blocked
        assert walk(start); seen={start};q=deque([start])
        while q:
            x,y=q.popleft()
            for p in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
                if p not in seen and walk(p):seen.add(p);q.append(p)
        return seen
    layout=ptr(OUT);e=ptr(OUT+4);group=ptr(BANKS+4)
    assert struct.unpack_from('<II',base,layout)==(40,20) and base[e:e+4]==bytes([8,6,9,7])
    old=rows(OUT);r=[row+[0x3001]*12 for row in old]
    for y in range(20):
        for x in range(40,52):
            if y in (0,1,18,19) or x>=50:r[y][x]=((0x05d4,0x05d5),(0x05dc,0x05dd))[y%2][x%2]
            elif y in (9,10) or x in (44,45):r[y][x]=0x305e
    for y in (9,10):
        for x in range(38,50):r[y][x]=0x305e
    oldale=ptr(ptr(BANKS)+40);o=rows(oldale)
    assert base[ptr(oldale)+16:ptr(oldale)+24]==base[layout+16:layout+24]
    for y in range(4):
        for x in range(4):r[4+y][43+x]=o[4+y][4+x]
    assert r[7][44]==0x0687
    r[8][44]=r[8][45]=0x305e;r[7][47]=0x3403
    assert {(x,y) for y in range(20) for x in range(40) if r[y][x]!=old[y][x]}=={(x,y) for y in (9,10) for x in (38,39)}
    grid=alloc(b''.join(struct.pack('<52H',*row) for row in r));put(layout,struct.pack('<I',52));put(layout+12,addr(grid))
    oo,ow,os=ptr(e+4),ptr(e+8),ptr(e+16)
    residents=[(9,41,11,oo+24,'Le marché est tout près.\nLe centre est au nord.'),(10,48,12,oo+48,'Les jardins de Manille\nsont ouverts à tous.'.replace('à','a')),(11,32,11,oo,'Je livre les provisions\naux voyageurs.')]
    objects=bytearray(base[oo:oo+8*24])
    for local,x,y,template,s in residents:
        assert r[y][x]&0xc00==0
        objects.extend(npc(template,local,x,y,dialogue(s)))
    warps=base[ow:ow+6*8]+warp(44,7,0,0,8,1)
    signs=base[os:os+7*12]+struct.pack('<hhBBH',47,7,0,0,0)+addr(dialogue('Centre Pokémon.\nSoins gratuits.',3))
    oe=bytearray(base[e:e+20]);oe[:4]=bytes([11,7,9,8]);oe[4:8]=addr(alloc(objects));oe[8:12]=addr(alloc(warps));oe[16:20]=addr(alloc(signs));put(OUT+4,addr(alloc(oe)))
    center=ptr(ptr(BANKS+8)+8); upstairs=ptr(ptr(BANKS+8)+12)
    ce=ptr(center+4);ue=ptr(upstairs+4);co=ptr(ce+4)
    assert center==0x487aa4 and upstairs==0x487ac0 and base[ce:ce+4]==bytes([4,3,0,0])
    nurse=base[co:co+24];ns=ptr(co+16)
    assert base[ns:ns+14]==bytes.fromhex('160b80010004df6b2708666d6c02')
    cobjects=nurse+npc(co+24,2,4,4,dialogue('Tu peux te reposer ici.\nLes soins sont gratuits.'))
    cw=bytearray(base[ptr(ce+8):ptr(ce+8)+24]);cw[5:8]=bytes([6,9,0]);cw[13:16]=bytes([6,9,0]);cw[21:24]=bytes([0,9,1])
    empty=alloc(b'\0')
    def new_header(template,objects,warps):
        ev=alloc(bytes([len(objects)//24,len(warps)//8,0,0])+addr(alloc(objects))+addr(alloc(warps))+b'\0'*8)
        h=bytearray(base[template:template+28]);h[4:8]=addr(ev);h[8:12]=addr(empty);h[12:16]=b'\0'*4;h[20]=base[OUT+20]
        return alloc(h)
    ch=new_header(center,cobjects,cw)
    uo=ptr(ue+4)
    uobjects=npc(co+24,1,7,7,dialogue('Cet étage est au calme.\nLes services de liaison\fne sont pas ouverts.'))
    uw=bytearray(base[ptr(ue+8):ptr(ue+8)+8]);uw[5:8]=bytes([2,8,1])
    uh=new_header(upstairs,uobjects,uw)
    put(BANKS+4,addr(alloc(base[group:group+8*4]+addr(ch)+addr(uh))))
    end=ALLOC+len(blob)
    assert len(base.rstrip(b'\0'))<=ALLOC and not any(base[ALLOC:end])
    assert not any(0x8000000+ALLOC<=v<0x8000000+end for (v,) in struct.iter_unpack('<I',base))
    put(ALLOC,blob)
    seen=flood(r,(19,11),{(x,y) for _,x,y,_,_ in residents})
    assert {(44,8),(47,8),(41,10),(48,11),(32,10)}<=seen
    cs=flood(rows(center),(7,8),{(7,2),(4,4)})
    assert (7,4) in cs and (2,6) in cs
    us=flood(rows(upstairs),(2,6),{(7,7)})
    assert (7,8) in us
    target=bytes(target)
    assert not any(a!=b and i not in allowed for i,(a,b) in enumerate(zip(base,target)))
    patch=patch_create(source,target)
    assert patch_apply(source,patch)==target and patch_apply(target,patch,True)==source
    report={'version':'V32','crc32_source':f'{crc(source):08X}','crc32_cible':f'{crc(target):08X}','sha256_patch':hashlib.sha256(patch).hexdigest(),'dimensions':[52,20],'nouvelles_cartes':[[1,8],[1,9]],'nouveaux_pnj':6,'pnj_exterieurs':3,'script_soins_natif':hex(ns),'respawn_nouveau_non_configure':True,'cases_accessibles_extension':sum(x>=40 for x,y in seen),'aller_retour':True,'test_emulateur':False}
    return patch,report
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('previous',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    patch,report=build(a.source.read_bytes(),a.previous.read_bytes())
    with a.output.open('xb') as f:f.write(patch)
    print(json.dumps(report,ensure_ascii=False,indent=2))
