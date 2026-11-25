#!/usr/bin/env python3
"""V31: rue du marché, boutique native et maison des voyageurs, depuis V30."""
import argparse, hashlib, json, struct
from collections import deque
from pathlib import Path
from rom_v27 import crc, patch_apply, patch_create
ALLOC=0x110a000
OUT=0x4874a0
BANKS=0x48b464

def build(source, previous):
    if len(source)!=0x2000000 or crc(source)!=0x75204b25: raise ValueError('V26 requise')
    base=patch_apply(source,previous)
    if crc(base)!=0xA47494E5: raise ValueError('V30 requise')
    t=bytearray(base);blob=bytearray();allowed=set()
    def ptr(p):
        n=struct.unpack_from('<I',base,p)[0]-0x8000000
        if not 0<=n<len(base): raise ValueError('Pointeur invalide')
        return n
    def addr(n): return struct.pack('<I',n+0x8000000)
    def put(p,data):
        t[p:p+len(data)]=data;allowed.update(range(p,p+len(data)))
    def alloc(data):
        while len(blob)%4: blob.append(0)
        p=ALLOC+len(blob);blob.extend(data);return p
    def encode(s):
        out=bytearray()
        for c in s:
            if 'A'<=c<='Z': out.append(0xbb+ord(c)-65)
            elif 'a'<=c<='z': out.append(0xd5+ord(c)-97)
            else: out.append({' ':0,'.':0xad,'\n':0xfe,'\f':0xfb}[c])
        return bytes(out)+b'\xff'
    def dialogue(s,kind=2): return alloc(b'\x0f\x00'+addr(alloc(encode(s)))+bytes([9,kind,2]))
    def maprows(header):
        l=ptr(header);w,h=struct.unpack_from('<II',base,l);g=ptr(l+12)
        return [list(struct.unpack_from('<%dH'%w,base,g+2*w*y)) for y in range(h)]
    def reachable(rows,start,blocked=()):
        def walk(p):
            x,y=p;return 0<=y<len(rows) and 0<=x<len(rows[y]) and not rows[y][x]&0xc00 and p not in blocked
        assert walk(start);seen={start};q=deque([start])
        while q:
            x,y=q.popleft()
            for p in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
                if p not in seen and walk(p):seen.add(p);q.append(p)
        return seen
    layout=ptr(OUT);e=ptr(OUT+4);group=ptr(BANKS+4)
    assert struct.unpack_from('<II',base,layout)==(28,20) and base[e:e+4]==bytes([8,4,9,5])
    assert ptr(group+20)==0x1107148
    old=maprows(OUT);rows=[r+[0x3001]*12 for r in old]
    for y in range(20):
        for x in range(28,40):
            if y in (0,1,18,19) or x>=38: rows[y][x]=((0x05d4,0x05d5),(0x05dc,0x05dd))[y%2][x%2]
            elif y in (9,10) or x in (35,36): rows[y][x]=0x305e
    for y in (9,10):
        for x in range(26,38):rows[y][x]=0x305e
    oldale=ptr(ptr(BANKS)+10*4);ol=ptr(oldale)
    assert base[ol+16:ol+24]==base[layout+16:layout+24]
    o=maprows(oldale)
    for y in range(4):
        for x in range(4):rows[4+y][30+x]=o[3+y][13+x]
    assert rows[7][31]==o[6][14]==0x0441
    for y in (8,9):rows[y][31]=0x305e
    for y in range(5):
        for x in range(5):rows[12+y][30+x]=old[4+y][2+x]
    assert rows[16][33]==0x0648
    rows[17][33]=rows[17][34]=rows[17][35]=0x305e
    rows[7][34]=rows[16][35]=0x3403
    assert {(x,y) for y in range(20) for x in range(28) if rows[y][x]!=old[y][x]}=={(x,y) for y in (9,10) for x in (26,27)}
    grid=alloc(b''.join(struct.pack('<40H',*r) for r in rows))
    put(layout,struct.pack('<I',40));put(layout+12,addr(grid))
    ow,os=ptr(e+8),ptr(e+16)
    warps=base[ow:ow+32]+struct.pack('<hhBBBB',31,7,0,0,6,1)+struct.pack('<hhBBBB',33,16,0,1,7,1)
    signs=base[os:os+60]
    for x,y,s in [(34,7,'Boutique de Manille.\nSoins et provisions.'),(35,16,'Maison des voyageurs.\nEntree libre.')]:
        signs+=struct.pack('<hhBBH',x,y,0,0,0)+addr(dialogue(s,3))
    oe=bytearray(base[e:e+20]);oe[1]=6;oe[3]=7;oe[8:12]=addr(alloc(warps));oe[16:20]=addr(alloc(signs));put(OUT+4,addr(alloc(oe)))
    def interior(template,warp_id,npcscript):
        te=ptr(template+4);nw=bytearray(base[ptr(te+8):ptr(te+8)+16]);assert base[te+1]==2
        for j in (0,8):nw[j+5:j+8]=bytes([warp_id,9,0])
        npc=bytearray(base[ptr(te+4):ptr(te+4)+24]);npc[16:20]=addr(npcscript);npc[20:24]=b'\0'*4
        no=alloc(npc);wi=alloc(nw);ev=alloc(bytes([1,2,0,0])+addr(no)+addr(wi)+b'\0'*8)
        h=bytearray(base[template:template+28]);h[4:8]=addr(ev);h[8:12]=addr(alloc(b'\0'));h[12:16]=b'\0'*4;h[20]=base[OUT+20]
        return alloc(h)
    mart=0x487adc;me=ptr(mart+4);clerk=ptr(ptr(me+4)+16)
    assert base[clerk:clerk+3]==bytes.fromhex('6a5a67') and base[clerk+7]==0x66 and base[clerk+17]==0x86
    welcome=base[clerk+3:clerk+7];bye=base[clerk+24:clerk+28]
    assert base[clerk+22:clerk+24]==b'\x0f\x00' and base[clerk+28:clerk+32]==b'\x09\x04\x6c\x02'
    stock=(4,13,14,18,17,0);items=alloc(struct.pack('<6H',*stock))
    shop_script=alloc(b'\x6a\x5a\x67'+welcome+b'\x66\x86'+addr(items)+b'\x0f\x00'+bye+b'\x09\x04\x6c\x02')
    shop=interior(mart,4,shop_script)
    house=interior(0x487a6c,5,dialogue('Les voyageurs arrivent\npar les chemins du nord.\fPrends le temps de voir\nles jardins de Manille.'))
    put(BANKS+4,addr(alloc(base[group:group+24]+addr(shop)+addr(house))))
    end=ALLOC+len(blob)
    assert len(base.rstrip(b'\0'))<=ALLOC and not any(base[ALLOC:end])
    assert not any(0x8000000+ALLOC<=v<0x8000000+end for (v,) in struct.iter_unpack('<I',base))
    put(ALLOC,blob)
    seen=reachable(rows,(19,11))
    assert {(31,8),(33,17),(34,8),(35,17)}<=seen
    assert (3,3) in reachable(maprows(mart),(3,7),{(1,3)})
    assert (6,5) in reachable(maprows(0x487a6c),(4,8),{(6,4)})
    target=bytes(t)
    assert not any(a!=b and i not in allowed for i,(a,b) in enumerate(zip(base,target)))
    patch=patch_create(source,target)
    assert patch_apply(source,patch)==target and patch_apply(target,patch,True)==source
    report={'version':'V31','crc32_source':f'{crc(source):08X}','crc32_cible':f'{crc(target):08X}','sha256_patch':hashlib.sha256(patch).hexdigest(),'dimensions':[40,20],'nouvelles_cartes':[[1,6],[1,7]],'nouveaux_pnj':2,'nouveaux_panneaux':2,'articles_ids':list(stock[:-1]),'portes':[[31,7],[33,16]],'cases_accessibles_extension':sum(x>=28 for x,y in seen),'aller_retour':True,'test_emulateur':False}
    return patch,report
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('previous',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    patch,report=build(a.source.read_bytes(),a.previous.read_bytes())
    with a.output.open('xb') as f:f.write(patch)
    print(json.dumps(report,ensure_ascii=False,indent=2))
