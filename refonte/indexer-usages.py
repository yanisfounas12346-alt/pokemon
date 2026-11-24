#!/usr/bin/env python3
"""Index indicatif des usages de repères dans les sources du jeu, sans ROM."""
import argparse
import collections
import json
import re
import subprocess
from pathlib import Path

REF = "8baea56025e07db971b68f88aa85370f7432383e"
TOKEN = re.compile(r"\b[A-Za-z_][A-Za-z_0-9]*\b")
SUFFIXES = {".inc", ".s", ".c", ".h", ".S"}

def collect(source, labels):
    result = collections.defaultdict(list)
    for folder in ("data", "src", "include"):
        root = source / folder
        if not root.is_dir():
            raise ValueError("Source incomplète : " + folder)
        for path in sorted(root.rglob("*")):
            if not path.is_file() or path.suffix not in SUFFIXES:
                continue
            # Les fichiers de chaînes ne sont pas des sites d'utilisation.
            if path.name in ("text_fr.inc", "text.inc"):
                continue
            rel = path.relative_to(source).as_posix()
            for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                if path.suffix in (".inc", ".s", ".S"):
                    code = line.split("@", 1)[0].strip()
                else:
                    code = line.split("//", 1)[0].strip()
                if not code or code.startswith(("/*", "*", "#include", ".string")):
                    continue
                for label in sorted(set(TOKEN.findall(code)) & labels):
                    if re.match(r"^" + re.escape(label) + r"::?\s*$", code):
                        continue
                    kind = "code_c" if path.suffix in (".c", ".h") else "script_ou_assembleur"
                    result[label].append({"fichier": rel, "ligne": number,
                                          "categorie": kind, "extrait": code[:300]})
    return result

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--manifeste", required=True, type=Path)
    parser.add_argument("--sortie", required=True, type=Path)
    args = parser.parse_args()
    rev = subprocess.check_output(["git", "-C", str(args.source), "rev-parse", "HEAD"], text=True).strip()
    if rev != REF:
        parser.error("Révision de référence incorrecte")
    manifest = json.loads(args.manifeste.read_text(encoding="utf-8"))
    rows = manifest["repliques_secondaires"] + manifest["repliques_narratives"]
    labels = {r["repere"] for r in rows}
    uses = collect(args.source, labels)
    stats = collections.Counter()
    entries = []
    for row in rows:
        label = row["repere"]
        refs = uses[label]
        kind = ("non_retrouve" if not refs else
                "code_c_a_verifier" if any(r["categorie"] == "code_c" for r in refs) else
                "usages_multiples" if len(refs) > 1 else "usage_script_unique")
        stats[kind] += 1
        entries.append({"repere": label, "carte": row["carte"],
                        "classement": kind, "usages": refs})
    report = {"reference": REF, "statistiques": dict(stats), "reperes": entries,
              "limite": "Occurrences textuelles seulement : déclarations, références indirectes, macros et adresses ROM à vérifier. Aucun pointeur approuvé."}
    args.sortie.write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print("USAGES", json.dumps(dict(stats), ensure_ascii=False))

if __name__ == "__main__":
    main()
