#!/usr/bin/env python3
"""V38: centre des ascendants; preserves V37 and original prologue."""
import argparse, hashlib, json, struct
from collections import deque
from pathlib import Path
from rom_v27 import crc, patch_apply, patch_create

def build(source, previous):
    assert len(source)==0x2000000 and crc(source)==0x75204B25
    b=patch_apply(source,previous); assert crc(b)==0x853AE05D
    t=bytearray(b); blob=bytearray(); allowed=set(); A=0x1194000; OUT=0x4874a0; BANK=0x48b464
    def ptr(o):
        p=struct.unpack_from('<I',b,o)[0]-0x8000000; assert 0<=p<len(b); return p
    def addr(p): return struct.pack('<I',p+0x8000000)
    def put(p,d): t[p:p+len(d)]=d; allowed.update(range(p,p+len(d)))
    def alloc(d):
        while len(blob)%4: blob.append(0)
        p=A+len(blob);blob.extend(d);return p
    def talk(s,kind=2):
        assert all(len(l)<=26 for l in s.replace('\f','\n').split('\n'))
        chars={' ':0,'.':0xad,'\n':0xfe,'\f':0xfb,'é':0x1b,'è':0x1a,'à':0x16,'ç':0x19,'ê':0x1c,'ô':0x22,'î':0x20,'’':0xb4}
        enc=bytes(0xbb+ord(c)-65 if 'A'<=c<='Z' else 0xd5+ord(c)-97 if 'a'<=c<='z' else chars[c] for c in s)+b'\xff'
        return alloc(b'\x0f\x00'+addr(alloc(enc))+bytes([9,kind,2]))
    def rows(h):
        l=ptr(h);w,n=struct.unpack_from('<II',b,l);g=ptr(l+12)
        return [list(struct.unpack_from('<%dH'%w,b,g+2*w*y)) for y in range(n)]
    def npc(o,i,x,y,s):
        n=bytearray(b[o:o+24]);n[0]=i;struct.pack_into('<hh',n,4,x,y);n[8:16]=bytes([3,8,0,0,0,0,0,0]);n[16:20]=addr(talk(s));n[20:24]=b'\0'*4;return n
    def flood(r,start,blocked):
        def walk(p):
            x,y=p;return 0<=y<len(r) and 0<=x<len(r[y]) and not r[y][x]&0xc00 and p not in blocked and r[y][x] not in (0x10b0,0x10b1,0x10b2,0x10b8,0x10ba,0x10a1)
        assert walk(start);seen={start};q=deque([start])
        while q:
            x,y=q.popleft()
            for p in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
                if p not in seen and walk(p):seen.add(p);q.append(p)
        return seen
    l=ptr(OUT);e=ptr(OUT+4);g=ptr(BANK+4); old=rows(OUT)
    assert (len(old[0]),len(old))==(176,20) and b[e:e+4]==bytes([32,15,9,21])
    W=200;assert (W+15)*34<=10240
    r=[row+[0x3001]*24 for row in old]
    for y in range(20):
        for x in range(176,W):
            if y in (0,1,18,19) or x>=198:r[y][x]=((0x05d4,0x05d5),(0x05dc,0x05dd))[y%2][x%2]
            elif y in (9,10) or (182<=x<=195 and 11<=y<=15):r[y][x]=0x305e
    for y in (9,10):
        for x in range(174,198):r[y][x]=0x305e
    for y in range(5):
        for x in range(7):r[3+y][185+x]=old[12+y][3+x]
    assert r[7][189]==0x0649
    r[8][189]=0x305e
    for x,y in ((181,12),(181,13),(196,12),(196,13)):r[y][x]=0x3004
    signsnew=[(183,8,'Centre des ascendants.\nAccueil des voyageurs.'),(193,8,'Prépare ton départ.\nRenseigne-toi au centre.'.replace('-',' '))]
    for x,y,_ in signsnew:r[y][x]=0x3403
    changed={(x,y) for y in range(20) for x in range(176) if r[y][x]!=old[y][x]};assert changed=={(x,y) for y in (9,10) for x in (174,175)}
    grid=alloc(b''.join(struct.pack('<200H',*row) for row in r));put(l,struct.pack('<I',W));put(l+12,addr(grid))
    oo,ow,os=ptr(e+4),ptr(e+8),ptr(e+16)
    objs=bytearray(b[oo:oo+32*24]); residents=[(33,179,11,'Les ascendants passent\npar ce centre.'),(34,185,12,'Une ascension se prépare.\fVérifie ton équipe et\ntes provisions.'),(35,194,12,'Je viens du port.\nJe veux voir la tour.'),(36,196,7,'La tour nous attend.\nLe départ sera à l’est.')]
    for i,x,y,s in residents:
        assert not r[y][x]&0xc00; objs.extend(npc(oo+24*(i%3),i,x,y,s))
    warps=b[ow:ow+15*8]+struct.pack('<hhBBBB',189,7,0,0,18,1)
    signs=b[os:os+21*12]
    for x,y,s in signsnew:signs+=struct.pack('<hhBBH',x,y,0,0,0)+addr(talk(s,3))
    ev=bytearray(b[e:e+20]);ev[:4]=bytes([36,16,9,23]);ev[4:8]=addr(alloc(objs));ev[8:12]=addr(alloc(warps));ev[16:20]=addr(alloc(signs));put(OUT+4,addr(alloc(ev)))
    template=0x487a50;te=ptr(template+4);to=ptr(te+4);tw=ptr(te+8)
    assert b[te:te+4]==bytes([6,2,0,15]) and (len(rows(template)[0]),len(rows(template)))==(13,13)
    nw=bytearray(b[tw:tw+16]);nw[5:8]=nw[13:16]=bytes([15,9,0])
    inside=[(1,6,4,'Bienvenue au centre.\fLa tour rassemble des\nvoyageurs de tous lieux.'),(2,9,8,'Prépare une équipe variée.\fChaque palier présente\nde nouveaux défis.'),(3,4,8,'Je tiens les registres.\fLes sept épreuves\nont chacune leur maître.')]
    no=b''.join(npc(to,i,x,y,s) for i,x,y,s in inside)
    ie=alloc(bytes([3,2,0,0])+addr(alloc(no))+addr(alloc(nw))+b'\0'*8)
    h=bytearray(b[template:template+28]);h[4:8]=addr(ie);h[8:12]=addr(alloc(b'\0'));h[12:16]=b'\0'*4;h[20]=b[OUT+20]
    ih=alloc(h);put(BANK+4,addr(alloc(b[g:g+18*4]+addr(ih))))
    end=A+len(blob);assert len(b.rstrip(b'\0'))<=A and not any(b[A:end]);assert not any(0x8000000+A<=v<0x8000000+end for (v,) in struct.iter_unpack('<I',b));put(A,blob)
    blocked={struct.unpack_from('<hh',objs,i+4) for i in range(0,len(objs),24)};seen=flood(r,(19,11),blocked)
    assert {(189,8),(183,9),(193,9),(179,10),(185,11),(194,11),(196,8)}<=seen
    ins=flood(rows(template),(6,12),{(x,y) for _,x,y,_ in inside});assert {(7,12),(6,5),(9,9),(4,9)}<=ins
    target=bytes(t);assert not any(a!=b and i not in allowed for i,(a,b) in enumerate(zip(b,target)))
    patch=patch_create(source,target);assert patch_apply(source,patch)==target and patch_apply(target,patch,True)==source
    report={'version':'V38','crc32_source':f'{crc(source):08X}','crc32_cible':f'{crc(target):08X}','sha256_patch':hashlib.sha256(patch).hexdigest(),'dimensions':[W,20],'buffer_carte_cases':(W+15)*34,'buffer_limite_reference':10240,'nouvelles_cartes':[[1,18]],'nouveaux_pnj':7,'nouveaux_panneaux':2,'cases_accessibles_extension':sum(x>=176 for x,y in seen),'aller_retour':True,'test_emulateur':False}
    return patch,report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('previous',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    patch,report=build(a.source.read_bytes(),a.previous.read_bytes())
    with a.output.open('xb') as f:f.write(patch)
    print(json.dumps(report,ensure_ascii=False,indent=2))
