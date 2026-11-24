#!/usr/bin/env python3
"""Construit un manifeste de repères; ne modifie aucune ROM."""
import argparse
import collections
import csv
import json
import re
import runpy
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AUDIT = runpy.run_path(str(ROOT / "refonte/audit-dialogues.py"))
REF = AUDIT["REF"]
read_source = AUDIT["read_source"]
variables = AUDIT["variables"]
# Les répliques de raccord, sans instruction explicite, sont des remplacements.
NARRATIVE = re.compile(
    r"^([^\n]*?)\[Repère FR · ([^\]]+)\]"
    r"\(https://github\.com/pret/pokeemerald/blob/([^/]+)/"
    r"data/maps/([^/]+)/text_fr\.inc#L(\d+)[^)]*\)\s*\n"
    r"\s*```text\n([\s\S]*?)\n```", re.M
)
APPLIED_V3 = {"bourg.json", "ligue.json"}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--sortie", required=True, type=Path)
    args = parser.parse_args()
    rev = subprocess.check_output(
        ["git", "-C", str(args.source), "rev-parse", "HEAD"], text=True
    ).strip()
    if rev != REF:
        parser.error(f"Source attendue : {REF}; obtenue : {rev}")
    with (ROOT / "refonte/inventaire-cartes.csv").open(encoding="utf-8") as stream:
        inventory = list(csv.DictReader(stream, delimiter=";"))
    source = {}
    locations = collections.defaultdict(list)
    errors = []
    warnings = []
    for row in inventory:
        name = row["carte"]
        path = args.source / "data/maps" / name / "text_fr.inc"
        if not path.is_file():
            errors.append({"carte": name, "erreur": "source absente"})
            continue
        source[name] = read_source(path)
        for label, (text, line) in source[name].items():
            locations[label].append((name, text, line))

    narrative = {}
    for path in sorted((ROOT / "dialogues").glob("*.md")):
        content = path.read_text(encoding="utf-8")
        matches = list(NARRATIVE.finditer(content))
        if len(matches) != content.count("[Repère FR · "):
            errors.append({"fichier": path.name, "erreur": "répliques non analysées"})
        for match in matches:
            instruction, short, rev, name, line, text = match.groups()
            entries = source.get(name, {})
            candidates = [k for k in entries if k == short or k.endswith("_Text_" + short)]
            if rev != REF or len(candidates) != 1:
                errors.append({"fichier": path.name, "repere": short, "erreur": "repère narratif non résolu"})
                continue
            label = candidates[0]
            if label in narrative:
                errors.append({"repere": label, "erreur": "doublon narratif"})
                continue
            original, source_line = entries[label]
            narrative[label] = {
                "repere": label, "carte": name, "ligne_source": source_line,
                "origine_assembleur": original, "texte": text,
                "operation": "ajouter" if instruction.startswith("Ajouter") else "remplacer",
                "fichier": "dialogues/" + path.name,
                "etat_v3": "narratif_deja_integre_a_preserver",
            }
    if len(narrative) != 95:
        errors.append({"erreur": "95 répliques narratives attendues", "nombre": len(narrative)})

    ordinary = {}
    for path in sorted((ROOT / "refonte").glob("*.json")):
        try:
            rows = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(rows, list):
                raise ValueError("tableau attendu")
        except (ValueError, OSError) as exc:
            errors.append({"fichier": path.name, "erreur": str(exc)})
            continue
        for row in rows:
            if not isinstance(row, dict) or not isinstance(row.get("repere"), str) or not isinstance(row.get("texte"), str) or not row["texte"].strip():
                errors.append({"fichier": path.name, "erreur": "entrée invalide"})
                continue
            label, text = row["repere"], row["texte"]
            if label in ordinary or label in narrative:
                errors.append({"repere": label, "fichier": path.name, "erreur": "conflit ou doublon"})
                continue
            if len(locations[label]) != 1:
                errors.append({"repere": label, "fichier": path.name,
                               "erreur": "source absente ou ambiguë",
                               "cartes": [item[0] for item in locations[label]]})
                continue
            name, original, line = locations[label][0]
            status = "deja_integre_v3_a_verifier" if path.name in APPLIED_V3 else "a_integrer"
            if variables(original) != variables(text):
                warnings.append({"repere": label, "origine": dict(variables(original)),
                                 "refonte": dict(variables(text))})
                status = "verification_variables_requise"
            ordinary[label] = {
                "repere": label, "carte": name, "ligne_source": line,
                "origine_assembleur": original, "texte": text,
                "operation": "remplacer", "fichier": "refonte/" + path.name,
                "etat_v3": status,
            }

    covered = set(narrative) | set(ordinary)
    missing = {name: sorted(set(rows) - covered) for name, rows in source.items()
               if set(rows) - covered}
    report = {
        "reference": REF, "base": "BPEF / patch v3 partiel",
        "avertissement": "Manifeste logique, sans adresses ROM ni encodage GBA. Ne pas appliquer directement.",
        "repliques_narratives": list(narrative.values()),
        "repliques_secondaires": list(ordinary.values()),
        "erreurs_bloquantes": errors,
        "variables_a_verifier": warnings,
        "reperes_sans_refonte": missing,
        "statistiques": {
            "cartes_lues": len(source), "cartes_inventaire": len(inventory),
            "narratives": len(narrative), "secondaires": len(ordinary),
            "a_integrer": sum(r["etat_v3"] == "a_integrer" for r in ordinary.values()),
            "erreurs": len(errors), "avertissements_variables": len(warnings),
            "cartes_avec_reperes_manquants": len(missing),
        },
    }
    args.sortie.parent.mkdir(parents=True, exist_ok=True)
    args.sortie.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["statistiques"], ensure_ascii=False, indent=2))
    if errors:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
