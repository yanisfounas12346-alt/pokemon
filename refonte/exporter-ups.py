#!/usr/bin/env python3
"""Exporter un UPS expérimental, vérifié dans les deux sens."""
import argparse
import importlib.util
import json
import struct
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "injecteur", Path(__file__).with_name("injecter-dialogues.py"))
inj = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inj)

def encode_number(value):
    if value < 0:
        raise ValueError("Entier UPS négatif")
    result = bytearray()
    while True:
        digit = value & 127
        value >>= 7
        if not value:
            result.append(digit | 128)
            return bytes(result)
        result.append(digit)
        value -= 1

def create_ups(source, target):
    if not 0 < len(source) <= inj.MAX_SIZE or not 0 < len(target) <= inj.MAX_SIZE:
        raise ValueError("Taille hors limites")
    size = max(len(source), len(target))
    old, new = source.ljust(size, b"\0"), target.ljust(size, b"\0")
    result = bytearray(b"UPS1")
    result.extend(encode_number(len(source)))
    result.extend(encode_number(len(target)))
    cursor = pos = 0
    while pos < size:
        if old[pos] == new[pos]:
            pos += 1
            continue
        result.extend(encode_number(pos - cursor))
        while pos < size and old[pos] != new[pos]:
            result.append(old[pos] ^ new[pos])
            pos += 1
        result.append(0)
        cursor = pos + 1
        pos = cursor
    result.extend(struct.pack("<II", inj.crc(source), inj.crc(target)))
    result.extend(struct.pack("<I", inj.crc(result)))
    return bytes(result)

def reverse_ups(patch):
    """Échanger les tailles et CRC ; les blocs XOR restent identiques."""
    if patch[:4] != b"UPS1" or len(patch) < 18 or inj.crc(patch[:-4]) != struct.unpack("<I", patch[-4:])[0]:
        raise ValueError("UPS invalide")
    end = len(patch) - 12
    old, pos = inj.read_number(patch, 4, end)
    new, pos = inj.read_number(patch, pos, end)
    old_crc, new_crc = struct.unpack("<II", patch[-12:-4])
    result = (b"UPS1" + encode_number(new) + encode_number(old)
              + patch[pos:end] + struct.pack("<II", new_crc, old_crc))
    return result + struct.pack("<I", inj.crc(result))

def validate_injection(base, current, target, journal):
    """Vérifier la provenance et reconstruire exactement les changements journalisés."""
    fingerprints = journal["empreintes"]
    if fingerprints["base_sha256"] != inj.digest(base) or fingerprints["v3_sha256"] != inj.digest(current):
        raise ValueError("Journal relatif à une autre base ou v3")
    if journal["crc32_sortie"] != f"{inj.crc(target):08X}":
        raise ValueError("CRC de la ROM injectée différent du journal")
    if len(current) != inj.BASE_SIZE or len(target) != inj.MAX_SIZE:
        raise ValueError("Tailles inattendues pour une injection")
    changes = journal["modifications"]
    if not changes:
        raise ValueError("Aucune modification journalisée")
    expected = bytearray(current)
    expected.extend(b"\0" * (len(target) - len(current)))
    cursor = len(current)
    labels, occupied = set(), set()
    for entry in changes:
        label = entry["repere"]
        off, dest, size = entry["source"], entry["destination"], entry["taille"]
        refs = entry["pointeurs"]
        if label in labels or not 0 <= off < len(current) or dest != cursor or size <= 0 or dest + size > len(target):
            raise ValueError("Entrée du journal invalide : " + label)
        labels.add(label)
        payload = target[dest:dest+size]
        if not payload.endswith(b"\xff"):
            raise ValueError("Fin de texte manquante : " + label)
        if not refs or len(refs) != len(set(refs)) or set(refs) != set(inj.hits(current, inj.pointer(off))):
            raise ValueError("Références incomplètes : " + label)
        for pos in refs:
            if pos < 0xc0 or pos+4 > len(current) or current[pos:pos+4] != inj.pointer(off):
                raise ValueError("Pointeur journalisé invalide : " + label)
            span = set(range(pos, pos+4))
            if occupied & span:
                raise ValueError("Chevauchement de pointeurs : " + label)
            occupied.update(span)
            expected[pos:pos+4] = inj.pointer(dest)
        expected[dest:dest+size] = payload
        cursor += size
    if expected != target:
        raise ValueError("Modifications non journalisées détectées")
    return len(changes)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rom", required=True, type=Path)
    parser.add_argument("--rom-injectee", required=True, type=Path)
    parser.add_argument("--journal", required=True, type=Path)
    parser.add_argument("--sortie", required=True, type=Path)
    args = parser.parse_args()
    if args.sortie.suffix.lower() != ".ups" or args.sortie.exists():
        parser.error("La sortie doit être un nouveau fichier .ups")
    report = args.sortie.with_suffix(".verification.json")
    if report.exists():
        parser.error("Rapport de sortie déjà présent")
    base, target = args.rom.read_bytes(), args.rom_injectee.read_bytes()
    if len(base) != inj.BASE_SIZE or base[0xac:0xb0] != b"BPEF" or inj.crc(base) != inj.BASE_CRC:
        raise ValueError("ROM source BPEF incorrecte")
    current = inj.apply_ups(base, inj.V3.read_bytes())
    journal = json.loads(args.journal.read_text(encoding="utf-8"))
    count = validate_injection(base, current, target, journal)
    patch = create_ups(base, target)
    if inj.apply_ups(base, patch) != target:
        raise ValueError("Vérification aller échouée")
    if inj.apply_ups(target, reverse_ups(patch)) != base:
        raise ValueError("Vérification retour échouée")
    with args.sortie.open("xb") as stream:
        stream.write(patch)
    with report.open("x", encoding="utf-8") as stream:
        json.dump({"statut": "experimental_non_valide_en_jeu",
                   "dialogues_injectes": count,
                   "crc32_base": f"{inj.crc(base):08X}",
                   "crc32_cible": f"{inj.crc(target):08X}",
                   "sha256_ups": inj.digest(patch), "taille_ups": len(patch),
                   "aller_octet_pour_octet": True, "retour_octet_pour_octet": True},
                  stream, ensure_ascii=False, indent=2)
    print("UPS expérimental vérifié aller-retour. Tests en jeu indispensables.")

if __name__ == "__main__":
    main()
