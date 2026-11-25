#!/usr/bin/env python3
"""Première modification cartographique V28; base V26 exclusivement."""
import argparse
import importlib.util
import hashlib
import struct
from pathlib import Path

spec=importlib.util.spec_from_file_location("v27",Path(__file__).with_name("generer-v27.py"))
v27=importlib.util.module_from_spec(spec)
spec.loader.exec_module(v27)
inj=v27.inj

def build(source):
    baseline=inj.apply_ups(source,v27.build(source))
    target=bytearray(baseline)
    def ptr(p):
        n=struct.unpack_from("<I",source,p)[0]-0x08000000
        if not 0<=n<len(source): raise ValueError("Pointeur invalide")
        return n
    header=ptr(ptr(0x48B464)+9*4)
    layout=ptr(header)
    w,h=struct.unpack_from("<II",source,layout)
    grid=ptr(layout+12)
    attrs=ptr(ptr(layout+16)+16)
    if (header,layout,w,h,grid)!=(0x4874A0,0x3EF170,20,20,0x3EEE50):
        raise ValueError("Carte inattendue")
    for tile in (1,0x5e):
        if struct.unpack_from("<H",source,attrs+2*tile)[0]!=0:
            raise ValueError("Comportement non neutre")
    coords={(x,y) for x in (10,11) for y in range(11,19)} | {(x,17) for x in (8,9)}
    events=ptr(header+4)
    for idx,stride,delta in [(0,24,4),(1,8,0),(2,16,0),(3,12,0)]:
        for i in range(source[events+idx]):
            if struct.unpack_from("<hh",source,ptr(events+4+idx*4)+stride*i+delta) in coords:
                raise ValueError("Événement sur le passage")
    for x,y in sorted(coords):
        off=grid+2*(y*w+x)
        if struct.unpack_from("<H",source,off)[0]!=0x3001:
            raise ValueError("Terrain inattendu")
        struct.pack_into("<H",target,off,0x305e)
    target=bytes(target)
    expected={grid+2*(y*w+x) for x,y in coords}
    if {i for i,(a,b) in enumerate(zip(baseline,target)) if a!=b}!=expected:
        raise ValueError("Modification hors périmètre")
    patch=v27.export.create_ups(source,target)
    if inj.apply_ups(source,patch)!=target or inj.apply_ups(target,v27.export.reverse_ups(patch))!=source:
        raise ValueError("Échec aller-retour")
    if inj.crc(target)!=0xDF5A8ED8:
        raise ValueError("CRC cible inattendu")
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
