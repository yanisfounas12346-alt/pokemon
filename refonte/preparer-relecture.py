#!/usr/bin/env python3
"""Préparer une relecture manuelle des candidats, sans modifier de ROM."""
import argparse
import hashlib
import json
from pathlib import Path

CHECKS = ("texte_et_carte", "references_verifiees", "variables_et_affichage")

def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))

def save_json(path, content):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(content, stream, ensure_ascii=False, indent=2)
        stream.write("\n")

def load_report(manifest_path, report_path):
    raw = manifest_path.read_bytes()
    manifest, report = json.loads(raw), read_json(report_path)
    fingerprints = report["empreintes"]
    if hashlib.sha256(raw).hexdigest() != fingerprints["manifeste_sha256"]:
        raise ValueError("Le repérage ne correspond pas au manifeste")
    if manifest["erreurs_bloquantes"] or manifest.get("reperes_manquants_non_expliques"):
        raise ValueError("Manifeste incomplet")
    rows = {r["repere"]: r for r in manifest["repliques_secondaires"]}
    candidates = {}
    others = []
    seen = set()
    for item in report["reperes"]:
        label = item["repere"]
        if label not in rows:
            raise ValueError("Repère absent du manifeste : " + label)
        if label in seen:
            raise ValueError("Repère dupliqué : " + label)
        seen.add(label)
        if item["etat"] == "candidat_a_revoir":
            candidates[label] = item
        else:
            others.append(item)
    if seen != set(rows):
        raise ValueError("Repérage incomplet")
    return rows, candidates, others, fingerprints

def prepare(rows, candidates, others, fingerprints):
    review = []
    for label, item in sorted(candidates.items(), key=lambda x: (rows[x[0]]["carte"], x[1]["offset"], x[0])):
        row = rows[label]
        review.append({
            "repere": label,
            "carte": row["carte"],
            "fichier": row["fichier"],
            "origine_assembleur": row["origine_assembleur"],
            "nouveau_texte": row["texte"],
            "etat_v3": row["etat_v3"],
            "offset": item["offset"],
            "offset_hex": f"0x{item['offset']:08X}",
            "pointeurs": item["pointeurs"],
            "pointeurs_hex": [f"0x{p:08X}" for p in item["pointeurs"]],
            "decision": "a_revoir",
            "controles": {key: False for key in CHECKS},
            "verification": "",
        })
    return {"empreintes": fingerprints, "candidats": review,
            "autres_reperes": others,
            "instruction": "Ne marquer approuve qu'après contrôle réel dans HMA; aucun candidat n'est préapprouvé."}

def approve(review, rows, candidates, fingerprints):
    if review["empreintes"] != fingerprints:
        raise ValueError("Relecture périmée")
    approvals = []
    seen = set()
    for row in review["candidats"]:
        label = row["repere"]
        if label in seen or label not in candidates:
            raise ValueError("Repère de relecture inattendu : " + label)
        seen.add(label)
        item, original = candidates[label], rows[label]
        if row["offset"] != item["offset"] or row["pointeurs"] != item["pointeurs"] or row["nouveau_texte"] != original["texte"] or row["origine_assembleur"] != original["origine_assembleur"]:
            raise ValueError("Données de relecture modifiées : " + label)
        if row["decision"] not in ("a_revoir", "refuse", "approuve"):
            raise ValueError("Décision inconnue : " + label)
        if row["decision"] != "approuve":
            continue
        if not all(row["controles"].get(key) is True for key in CHECKS):
            raise ValueError("Contrôles incomplets : " + label)
        note = row["verification"]
        if not isinstance(note, str) or not note.strip():
            raise ValueError("Justification manquante : " + label)
        approvals.append({"repere": label, "offset": item["offset"],
                          "pointeurs": item["pointeurs"], "verification": note.strip()})
    if not approvals:
        raise ValueError("Aucun candidat approuvé")
    return {"empreintes": fingerprints, "approbations": approvals}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["preparer", "valider"])
    parser.add_argument("--manifeste", type=Path, required=True)
    parser.add_argument("--reperage", type=Path, required=True)
    parser.add_argument("--relecture", type=Path)
    parser.add_argument("--sortie", type=Path, required=True)
    args = parser.parse_args()
    rows, candidates, others, fingerprints = load_report(args.manifeste, args.reperage)
    if args.mode == "preparer":
        out = prepare(rows, candidates, others, fingerprints)
        print(len(out["candidats"]), "candidats à vérifier, aucun approuvé.")
    else:
        if not args.relecture:
            parser.error("--relecture est requis pour valider")
        out = approve(read_json(args.relecture), rows, candidates, fingerprints)
        print(len(out["approbations"]), "approbations explicites.")
    save_json(args.sortie, out)

if __name__ == "__main__":
    main()
