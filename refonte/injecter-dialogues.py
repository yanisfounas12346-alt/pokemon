#!/usr/bin/env python3
"""Repérage et injection prudente des textes BPEF sur une ROM locale."""
import argparse
import collections
import hashlib
import json
import re
import struct
import unicodedata
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE_CRC = 0xA3FDCCB1
BASE_SIZE = 16 * 1024 * 1024
MAX_SIZE = 32 * 1024 * 1024
ROM_START = 0x08000000
V3 = ROOT / "refonte/La-Part-des-absents-v3-partielle.ups"
ELIGIBLE = {"a_integrer", "a_integrer_controle_variables"}

def crc(data):
    return zlib.crc32(data) & 0xffffffff

def digest(data):
    return hashlib.sha256(data).hexdigest()

def read_number(data, pos, end):
    value, shift = 0, 1
    while pos < end:
        byte = data[pos]
        pos += 1
        value += (byte & 127) * shift
        if byte & 128:
            return value, pos
        shift <<= 7
        value += shift
        if shift > 1 << 35:
            break
    raise ValueError("Entier UPS invalide")

def apply_ups(source, patch):
    if len(patch) < 18 or patch[:4] != b"UPS1":
        raise ValueError("Patch UPS invalide")
    old_crc, new_crc, patch_crc = struct.unpack("<III", patch[-12:])
    if crc(patch[:-4]) != patch_crc or crc(source) != old_crc:
        raise ValueError("CRC UPS ou ROM source incorrect")
    end = len(patch) - 12
    old_size, pos = read_number(patch, 4, end)
    new_size, pos = read_number(patch, pos, end)
    if old_size != len(source) or not 0 < new_size <= MAX_SIZE:
        raise ValueError("Tailles UPS incompatibles")
    result = bytearray(source[:new_size].ljust(new_size, b"\0"))
    cursor = 0
    while pos < end:
        delta, pos = read_number(patch, pos, end)
        cursor += delta
        while True:
            if pos >= end:
                raise ValueError("Bloc UPS tronqué")
            byte = patch[pos]
            pos += 1
            if byte == 0:
                cursor += 1
                break
            if cursor >= max(old_size, new_size):
                raise ValueError("Bloc UPS hors limites")
            if cursor < new_size:
                result[cursor] ^= byte
            cursor += 1
    if crc(result) != new_crc:
        raise ValueError("CRC de sortie UPS incorrect")
    return bytes(result)

class Codec:
    def __init__(self, path):
        self.chars, self.tokens = {}, {}
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("@ Hiragana"):
                break
            match = re.match(r"^'(.*)'\s*=\s*([0-9A-Fa-f ]+)", line)
            if match:
                key, raw = match.groups()
                self.chars["'" if key == r"\'" else key] = bytes.fromhex(raw)
        for line in path.read_text(encoding="utf-8").splitlines():
            match = re.match(r"^([A-Z][A-Z_0-9]*)\s*=\s*([0-9A-Fa-f ]+)", line)
            if match:
                key, raw = match.groups()
                self.tokens[key] = bytes.fromhex(raw)
        self.allowed = {"PLAYER", "STR_VAR_1", "STR_VAR_2", "STR_VAR_3", "KUN", "RIVAL",
                        "POKEBLOCK", "SUPER_E", "SUPER_ER", "UP_ARROW", "DOWN_ARROW",
                        "LEFT_ARROW", "RIGHT_ARROW"}
        if self.tokens.get("PLAYER") != b"\xfd\x01" or self.chars.get("$") != b"\xff":
            raise ValueError("Charmap inattendue")

    def encode(self, text, source=False):
        text = unicodedata.normalize("NFC", text)
        terminators = 1
        if source:
            body = text.rstrip("$")
            terminators = len(text) - len(body)
            if terminators not in (1, 2) or "$" in body or not body:
                raise ValueError("Terminaison source non standard")
            text = body
        else:
            if "$" in text or "\\" in text:
                raise ValueError("Contrôle brut non autorisé")
            text = text.replace("°", "º")
        result = bytearray()
        i = 0
        while i < len(text):
            char = text[i]
            if char == "{":
                end = text.find("}", i)
                if end < 0:
                    raise ValueError("Variable non fermée")
                name = text[i+1:end]
                if name not in self.allowed or name not in self.tokens:
                    raise ValueError("Contrôle non pris en charge : " + name)
                result.extend(self.tokens[name])
                i = end + 1
                continue
            if source and char == "\\":
                code = {"n": 0xfe, "l": 0xfa, "p": 0xfb}.get(text[i+1:i+2])
                if code is None:
                    raise ValueError("Échappement source non pris en charge")
                result.append(code)
                i += 2
                continue
            if not source and char == "\n":
                paragraph = text[i:i+2] == "\n\n"
                result.append(0xfb if paragraph else 0xfe)
                i += 2 if paragraph else 1
                continue
            if char not in self.chars or char == "}":
                raise ValueError("Caractère non encodable : " + repr(char))
            result.extend(self.chars[char])
            i += 1
        return bytes(result) + b"\xff" * terminators

def hits(data, pattern, limit=65):
    found, start = [], 0
    while len(found) < limit:
        pos = data.find(pattern, start)
        if pos < 0:
            break
        found.append(pos)
        start = pos + 1
    return found

def pointer(offset):
    if not 0 <= offset < MAX_SIZE:
        raise ValueError("Adresse hors ROM")
    return struct.pack("<I", ROM_START + offset)

def load_inputs(args):
    base = args.rom.read_bytes()
    if len(base) != BASE_SIZE or base[0xac:0xb0] != b"BPEF" or crc(base) != BASE_CRC:
        raise ValueError("ROM attendue : Émeraude FR BPEF 16 Mio, CRC32 A3FDCCB1")
    patch = V3.read_bytes()
    current = apply_ups(base, patch)
    manifest_bytes = args.manifeste.read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest["erreurs_bloquantes"] or manifest.get("reperes_manquants_non_expliques"):
        raise ValueError("Manifeste avec anomalies bloquantes")
    codec = Codec(args.charmap)
    fingerprints = {"base_sha256": digest(base), "v3_sha256": digest(current),
                    "manifeste_sha256": digest(manifest_bytes)}
    return base, current, manifest, codec, fingerprints

def scan(base, current, manifest, codec):
    originals = collections.defaultdict(list)
    encoded = {}
    failures = {}
    all_rows = manifest["repliques_secondaires"] + manifest["repliques_narratives"]
    for row in all_rows:
        label = row["repere"]
        try:
            old = codec.encode(row["origine_assembleur"], source=True)
            originals[old].append(label)
            encoded[label] = old
        except ValueError as exc:
            failures[label] = str(exc)
    report = []
    for row in manifest["repliques_secondaires"]:
        label = row["repere"]
        item = {"repere": label, "etat": row["etat_v3"]}
        report.append(item)
        if row["etat_v3"] not in ELIGIBLE:
            continue
        if label in failures:
            item.update(etat="encodage_source_a_verifier", raison=failures[label])
            continue
        try:
            new = codec.encode(row["texte"])
        except ValueError as exc:
            item.update(etat="encodage_refonte_a_verifier", raison=str(exc))
            continue
        old = encoded[label]
        if old == new:
            item["etat"] = "identique"
            continue
        if len(old) < 6 or len(originals[old]) != 1:
            item.update(etat="texte_court_ou_partage", reperes_partages=originals[old])
            continue
        positions = hits(base, old)
        if len(positions) != 1:
            item.update(etat="source_absente_ou_ambigue", occurrences=positions)
            continue
        off = positions[0]
        if current[off:off+len(old)] != old:
            item.update(etat="source_modifiee_dans_v3", offset=off)
            continue
        refs = hits(current, pointer(off))
        if not refs or len(refs) >= 65:
            item.update(etat="pointeurs_absents_ou_trop_nombreux", offset=off)
            continue
        item.update(etat="candidat_a_revoir", offset=off, pointeurs=refs,
                    taille_source=len(old), taille_refonte=len(new))
    return report

def relocate(current, approved):
    if not approved:
        raise ValueError("Aucun dialogue approuvé")
    if len(current) > BASE_SIZE:
        raise ValueError("Extension déjà utilisée : contrôle manuel requis")
    output = bytearray(current)
    output.extend(b"\0" * (BASE_SIZE - len(output)))
    occupied = set()
    source_spans = [(off, off+len(old)) for _, off, old, _, _ in approved]
    changes = []
    for label, off, old, new, refs in approved:
        if current[off:off+len(old)] != old:
            raise ValueError("Source modifiée : " + label)
        if not refs or len(set(refs)) != len(refs):
            raise ValueError("Références invalides : " + label)
        if set(refs) != set(hits(current, pointer(off))):
            raise ValueError("Liste de pointeurs incomplète : " + label)
        for pos in refs:
            if pos < 0xc0 or pos + 4 > len(current) or current[pos:pos+4] != pointer(off):
                raise ValueError("Pointeur invalide : " + label)
            if any(pos < end and pos+4 > start for start, end in source_spans):
                raise ValueError("Pointeur chevauchant un texte source : " + label)
            span = set(range(pos, pos+4))
            if occupied & span:
                raise ValueError("Pointeurs en conflit : " + label)
            occupied.update(span)
        target = len(output)
        if target + len(new) > MAX_SIZE:
            raise ValueError("Limite de 32 Mio dépassée")
        output.extend(new)
        for pos in refs:
            output[pos:pos+4] = pointer(target)
        changes.append({"repere": label, "source": off, "destination": target,
                        "pointeurs": refs, "taille": len(new)})
    output.extend(b"\0" * (MAX_SIZE - len(output)))
    return bytes(output), changes

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["reperer", "injecter"])
    parser.add_argument("--rom", required=True, type=Path)
    parser.add_argument("--manifeste", required=True, type=Path)
    parser.add_argument("--charmap", required=True, type=Path)
    parser.add_argument("--sortie", required=True, type=Path)
    parser.add_argument("--approbations", type=Path)
    args = parser.parse_args()
    if args.sortie.exists() or args.sortie.resolve() == args.rom.resolve():
        parser.error("La sortie doit être un nouveau fichier")
    base, current, manifest, codec, fingerprints = load_inputs(args)
    report = scan(base, current, manifest, codec)
    if args.mode == "reperer":
        args.sortie.write_text(json.dumps({"empreintes": fingerprints,
            "statistiques": dict(collections.Counter(x["etat"] for x in report)),
            "reperes": report}, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
        print(dict(collections.Counter(x["etat"] for x in report)))
        return
    if not args.approbations:
        parser.error("Injection interdite sans liste de pointeurs approuvés")
    selection = json.loads(args.approbations.read_text(encoding="utf-8"))
    if selection["empreintes"] != fingerprints:
        raise ValueError("Approbations relatives à une autre ROM ou un autre manifeste")
    candidates = {x["repere"]: x for x in report if x["etat"] == "candidat_a_revoir"}
    rows = {x["repere"]: x for x in manifest["repliques_secondaires"]}
    approved, seen = [], set()
    for item in selection["approbations"]:
        label = item["repere"]
        if label in seen or label not in candidates or not item.get("verification"):
            raise ValueError("Approbation non valide : " + label)
        seen.add(label)
        candidate, row = candidates[label], rows[label]
        if item["offset"] != candidate["offset"] or sorted(item["pointeurs"]) != sorted(candidate["pointeurs"]):
            raise ValueError("Adresses différentes du repérage : " + label)
        approved.append((label, item["offset"], codec.encode(row["origine_assembleur"], True),
                         codec.encode(row["texte"]), item["pointeurs"]))
    output, changes = relocate(current, approved)
    journal = args.sortie.with_suffix(args.sortie.suffix + ".json")
    if journal.exists():
        raise ValueError("Journal de sortie déjà présent")
    with args.sortie.open("xb") as stream:
        stream.write(output)
    with journal.open("x", encoding="utf-8") as stream:
        json.dump({"empreintes": fingerprints, "crc32_sortie": f"{crc(output):08X}",
                   "modifications": changes}, stream, ensure_ascii=False, indent=2)
    print("ROM expérimentale locale créée ; test en émulateur obligatoire.")

if __name__ == "__main__":
    main()
