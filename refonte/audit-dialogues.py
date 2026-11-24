#!/usr/bin/env python3
"""Audit des répliques de La Part des absents, sans ROM ni modification de fichiers."""
import argparse
import collections
import csv
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REF = "8baea56025e07db971b68f88aa85370f7432383e"
LABEL = re.compile(r"^(\w+)::?\s*$", re.M)
VARIABLE = re.compile(r"\{[^{}]+\}")
LINK = re.compile(r"\[Repère FR · ([^\]]+)\]\(https://github\.com/pret/pokeemerald/blob/[^/]+/data/maps/([^/]+)/text_fr\.inc#L(\d+)[^)]*\)")

def read_source(path):
    content = path.read_text(encoding="utf-8")
    marks = list(LABEL.finditer(content))
    result = {}
    for i, mark in enumerate(marks):
        body = content[mark.end():marks[i+1].start() if i+1 < len(marks) else len(content)]
        strings = re.findall(r'^\s*\.string\s+"(.*)"\s*$', body, re.M)
        if strings:
            result[mark.group(1)] = ("".join(strings), content.count("\n", 0, mark.start()) + 1)
    return result

def variables(text):
    return collections.Counter(VARIABLE.findall(text))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True, help="Clone local de pret/pokeemerald au commit de référence")
    parser.add_argument("--rapport", type=Path, help="Écrire aussi le rapport JSON")
    args = parser.parse_args()
    rev = subprocess.check_output(["git", "-C", str(args.source), "rev-parse", "HEAD"], text=True).strip()
    if rev != REF:
        parser.error(f"Source attendue : {REF}, obtenue : {rev}")
    with (ROOT / "refonte/inventaire-cartes.csv").open(encoding="utf-8") as f:
        inventory = list(csv.DictReader(f, delimiter=";"))
    source_by_map = {}
    missing_source = []
    locations = collections.defaultdict(list)
    for row in inventory:
        name = row["carte"]
        path = args.source / "data/maps" / name / "text_fr.inc"
        if not path.is_file():
            missing_source.append(name)
            continue
        source_by_map[name] = read_source(path)
        for label, (text, line) in source_by_map[name].items():
            locations[label].append((name, text, line))
    written = collections.defaultdict(list)
    invalid_rows = []
    variable_warnings = []
    long_lines = []
    long_pages = []
    files = sorted((ROOT / "refonte").glob("*.json"))
    for path in files:
        try:
            rows = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(rows, list):
                raise ValueError("tableau JSON attendu")
        except (ValueError, OSError) as exc:
            invalid_rows.append({"fichier": path.name, "erreur": str(exc)})
            continue
        for index, row in enumerate(rows, 1):
            if not isinstance(row, dict) or not isinstance(row.get("repere"), str) or not isinstance(row.get("texte"), str) or not row["texte"].strip():
                invalid_rows.append({"fichier": path.name, "ligne_json": index})
                continue
            label, text = row["repere"], row["texte"]
            written[label].append(path.name)
            for number, line in enumerate(text.splitlines(), 1):
                if len(line) > 36:
                    long_lines.append({"repere": label, "fichier": path.name,
                        "ligne": number, "caracteres": len(line), "texte": line})
            for number, page in enumerate(text.split("\n\n"), 1):
                if len(page.splitlines()) > 2:
                    long_pages.append({"repere": label, "fichier": path.name,
                        "page": number, "lignes": len(page.splitlines())})
            if label in locations and variables(text) != variables(locations[label][0][1]):
                variable_warnings.append({"repere": label, "fichier": path.name,
                    "origine": dict(variables(locations[label][0][1])), "refonte": dict(variables(text))})
    narrative = collections.defaultdict(list)
    unresolved = []
    for path in sorted((ROOT / "dialogues").glob("*.md")):
        for match in LINK.finditer(path.read_text(encoding="utf-8")):
            short, name, line = match.groups()
            entries = source_by_map.get(name, {})
            candidates = [label for label in entries if label == short or label.endswith("_Text_" + short)]
            if len(candidates) != 1:
                candidates = [label for label, (_, pos) in entries.items() if pos == int(line)]
            if len(candidates) == 1:
                narrative[candidates[0]].append(path.name)
            else:
                unresolved.append({"fichier": path.name, "carte": name, "repere": short, "ligne": int(line)})
    covered = set(written) | set(narrative)
    per_map = []
    for name, entries in source_by_map.items():
        absent = sorted(set(entries) - covered)
        per_map.append({"carte": name, "textes_source": len(entries), "couverts": len(entries)-len(absent), "manquants": absent})
    report = {
        "source": REF, "cartes_inventaire": len(inventory),
        "fichiers_json": len(files), "repliques_json": sum(map(len, written.values())),
        "reperes_json_uniques": len(written), "reperes_narratifs": len(narrative),
        "cartes_entierement_couvertes": sum(not x["manquants"] for x in per_map),
        "cartes_partiellement_couvertes": sum(bool(x["manquants"]) and x["couverts"] > 0 for x in per_map),
        "cartes_sans_couverture": sum(x["couverts"] == 0 for x in per_map),
        "sources_absentes": missing_source, "lignes_invalides": invalid_rows,
        "reperes_inconnus": sorted(set(written) - set(locations)),
        "doublons_json": {k:v for k,v in written.items() if len(v)>1},
        "chevauchements_narratifs": sorted(set(written) & set(narrative)),
        "liens_narratifs_non_resolus": unresolved, "variables_a_verifier": variable_warnings,
        "lignes_de_plus_de_36_caracteres": long_lines,
        "pages_de_plus_de_deux_lignes": long_pages,
        "note_affichage": "Contrôle indicatif : la largeur réelle dépend de la police et des variables développées.",
        "cartes": per_map,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.rapport:
        args.rapport.write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")

if __name__ == "__main__":
    main()
