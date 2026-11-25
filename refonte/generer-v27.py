#!/usr/bin/env python3
"""V27: modification reversible du titre interne, sans changement de gameplay."""
import argparse
import hashlib
import importlib.util
from pathlib import Path

def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(filename))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

export = load("export_v27", "exporter-ups.py")
inj = export.inj

def build(source):
    if len(source) != inj.MAX_SIZE or inj.crc(source) != 0x75204B25 or source[0xac:0xb0] != b"BPEF":
        raise ValueError("V26 BPEF CRC32 75204B25 requise")
    if source[0xbd] != (-sum(source[0xa0:0xbd])-0x19) & 255:
        raise ValueError("Somme de controle incorrecte")
    target = bytearray(source)
    target[0xa0:0xac] = b"PART ABSENTS"
    target[0xbd] = (-sum(target[0xa0:0xbd])-0x19) & 255
    target = bytes(target)
    patch = export.create_ups(source, target)
    if inj.apply_ups(source, patch) != target or inj.apply_ups(target, export.reverse_ups(patch)) != source:
        raise ValueError("Echec verification aller-retour")
    if inj.crc(target) != 0x95CC1A55:
        raise ValueError("CRC cible inattendu")
    return patch

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("source", type=Path)
    p.add_argument("output", type=Path)
    a = p.parse_args()
    if a.output.suffix.lower() != ".ups":
        p.error("La sortie doit etre un UPS")
    patch = build(a.source.read_bytes())
    with a.output.open("xb") as f:
        f.write(patch)
    print("UPS V27 SHA256", hashlib.sha256(patch).hexdigest())

if __name__ == "__main__":
    main()
