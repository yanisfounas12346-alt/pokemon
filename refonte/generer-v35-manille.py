#!/usr/bin/env python3
"""V35: Binondo, auberge et comptoir de boissons. Base V34."""
import argparse, hashlib, json, struct
from collections import deque
from pathlib import Path
from rom_v27 import crc, patch_apply, patch_create
ALLOC=0x1138000
BANKS=0x48b464
OUT=0x4874a0

def build(source, previous):
    if len(source)!=0x2000000 or crc(source)!=0x75204B25: raise ValueError('V26 requise')
    base=patch_apply(source,previous)
    if crc(base)!=0x989D2CFC: raise ValueError('V34 requise')
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
            else:out.append({' ':0,'.':0xad,'\n':0xfe,'\f':0xfb,'é':0x1b,'è':0x1a,'à':0x16,'ç':0x19,'î':0x20,'’':0xb4}[c])
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
    assert struct.unpack_from('<II',base,layout)==(96,20) and base[e:e+4]==bytes([17,9,9,12])
    old=rows(OUT);r=[row+[0x3001]*24 for row in old]
    for y in range(20):
        for x in range(96,120):
            if y in (0,1,18,19) or x>=118:r[y][x]=((0x05d4,0x05d5),(0x05dc,0x05dd))[y%2][x%2]
            elif y in (9,10) or x in (106,107,115,116):r[y][x]=0x305e
    for y in (9,10):
        for x in range(92,118):r[y][x]=0x305e
    for y in range(5):
        for x in range(5):r[3+y][99+x]=old[4+y][2+x]
    assert r[7][102]==0x0648
    r[8][102]=0x305e
    oldale=ptr(ptr(BANKS)+40);o=rows(oldale)
    assert base[ptr(oldale)+16:ptr(oldale)+24]==base[layout+16:layout+24]
    for y in range(4):
        for x in range(4):r[12+y][110+x]=o[3+y][13+x]
    assert r[15][111]==0x0441
    for x in range(111,117):r[16][x]=0x305e
    for x,y in [(105,4),(108,4),(99,13),(102,13)]:r[y][x]=0x3004
    signs_new=[(98,8,'Binondo.\nRue des commerçants.'),(104,7,'Auberge de Binondo.\nSalle de repos.'),(114,15,'Comptoir de boissons.\nProvisions de voyage.')]
    for x,y,_ in signs_new:r[y][x]=0x3403
    changed_old={(x,y) for y in range(20) for x in range(96) if r[y][x]!=old[y][x]}
    assert changed_old=={(x,y) for y in (9,10) for x in (92,94,95)}
    grid=alloc(b''.join(struct.pack('<120H',*row) for row in r));put(layout,struct.pack('<I',120));put(layout+12,addr(grid))
    oo,ow,os=ptr(e+4),ptr(e+8),ptr(e+16)
    residents=[(18,100,11,oo+24,'Bienvenue à Binondo.\nLa rue mène au marché.'),(19,108,7,oo+48,'Je prépare les colis.\nLe port sera plus loin.'),(20,115,11,oo,'On trouve des boissons\nau comptoir du quartier.'),(21,104,14,oo+24,'Les voyageurs discutent\nautour des tables.')]
    objects=bytearray(base[oo:oo+17*24])
    for local,x,y,template,s in residents:
        assert not r[y][x]&0xc00
        objects.extend(npc(template,local,x,y,dialogue(s)))
    warps=base[ow:ow+9*8]+warp(102,7,0,1,12,1)+warp(111,15,0,0,13,1)
    signs=base[os:os+12*12]
    for x,y,s in signs_new:signs+=struct.pack('<hhBBH',x,y,0,0,0)+addr(dialogue(s,3))
    oe=bytearray(base[e:e+20]);oe[:4]=bytes([21,11,9,15]);oe[4:8]=addr(alloc(objects));oe[8:12]=addr(alloc(warps));oe[16:20]=addr(alloc(signs));put(OUT+4,addr(alloc(oe)))
    def interior(template,warp_id,objects):
        te=ptr(template+4);assert base[te+1]==2
        w=bytearray(base[ptr(te+8):ptr(te+8)+16]);w[5:8]=w[13:16]=bytes([warp_id,9,0])
        ev=alloc(bytes([len(objects)//24,2,0,0])+addr(alloc(objects))+addr(alloc(w))+b'\0'*8)
        h=bytearray(base[template:template+28]);h[4:8]=addr(ev);h[8:12]=addr(alloc(b'\0'));h[12:16]=b'\0'*4;h[20]=base[OUT+20]
        return alloc(h)
    house=0x487a88;ho=ptr(ptr(house+4)+4)
    inn=interior(house,9,npc(ho,1,3,4,dialogue('Bienvenue à l’auberge.\fLa salle est ouverte\naux voyageurs.'))+npc(ho+24,2,8,4,dialogue('Je prends des notes\nsur les villes du monde.')))
    mart=0x487adc;mo=ptr(ptr(mart+4)+4);clerk=ptr(mo+16)
    assert base[clerk:clerk+3]==bytes.fromhex('6a5a67') and base[clerk+7]==0x66 and base[clerk+17]==0x86 and base[clerk+22:clerk+24]==b'\x0f\x00' and base[clerk+28:clerk+32]==b'\x09\x04\x6c\x02'
    stock=(26,27,28,29,0);items=alloc(struct.pack('<5H',*stock))
    shop_script=alloc(b'\x6a\x5a\x67'+base[clerk+3:clerk+7]+b'\x66\x86'+addr(items)+b'\x0f\x00'+base[clerk+24:clerk+28]+b'\x09\x04\x6c\x02')
    shop=interior(mart,10,npc(mo,1,1,3,shop_script)+npc(mo+24,2,5,5,dialogue('Une boisson fraîche\nfait du bien.')))
    put(BANKS+4,addr(alloc(base[group:group+48]+addr(inn)+addr(shop))))
    end=ALLOC+len(blob)
    assert len(base.rstrip(b'\0'))<=ALLOC and not any(base[ALLOC:end])
    assert not any(0x8000000+ALLOC<=v<0x8000000+end for (v,) in struct.iter_unpack('<I',base))
    put(ALLOC,blob)
    blocked={struct.unpack_from('<hh',objects,i+4) for i in range(0,len(objects),24)}
    seen=flood(r,(19,11),blocked)
    assert {(98,9),(102,8),(104,8),(111,16),(114,16),(100,10),(108,8),(115,10),(104,15)}<=seen
    assert {(3,3),(8,3),(3,7)}<=flood(rows(house),(4,7),{(3,4),(8,4)})
    assert {(3,3),(5,6)}<=flood(rows(mart),(3,7),{(1,3),(5,5)})
    target=bytes(target)
    assert not any(a!=b and i not in allowed for i,(a,b) in enumerate(zip(base,target)))
    assert target[ptr(e+12):ptr(e+12)+9*16]==base[ptr(e+12):ptr(e+12)+9*16]
    patch=patch_create(source,target)
    assert patch_apply(source,patch)==target and patch_apply(target,patch,True)==source
    report={'version':'V35','crc32_source':f'{crc(source):08X}','crc32_cible':f'{crc(target):08X}','sha256_patch':hashlib.sha256(patch).hexdigest(),'dimensions':[120,20],'nouvelles_cartes':[[1,12],[1,13]],'nouveaux_pnj':8,'nouveaux_panneaux':3,'articles_ids':list(stock[:-1]),'cases_accessibles_extension':sum(x>=96 for x,y in seen),'ancienne_surface_modifiee':len(changed_old),'aller_retour':True,'test_emulateur':False}
    return patch,report
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('previous',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    patch,report=build(a.source.read_bytes(),a.previous.read_bytes())
    with a.output.open('xb') as f:f.write(patch)
    print(json.dumps(report,ensure_ascii=False,indent=2))
