#!/usr/bin/env python3
"""Tests de la procédure de relecture, sans ROM."""
import copy
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("relecture", Path(__file__).with_name("preparer-relecture.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class TestReview(unittest.TestCase):
    def setUp(self):
        self.rows = {"A": {"repere":"A", "carte":"Map", "fichier":"a.json",
                           "origine_assembleur":"Ancien$", "texte":"Nouveau",
                           "etat_v3":"a_integrer"}}
        self.candidates = {"A":{"repere":"A","etat":"candidat_a_revoir",
                                "offset":1000,"pointeurs":[200,300]}}
        self.fingerprints = {"base_sha256":"base","v3_sha256":"v3","manifeste_sha256":"m","charmap_sha256":"c"}
        self.review = mod.prepare(self.rows,self.candidates,[],self.fingerprints)

    def approved(self):
        row = self.review["candidats"][0]
        row["decision"] = "approuve"
        row["controles"] = {k:True for k in mod.CHECKS}
        row["verification"] = "Contrôle synthétique"
        return row

    def approve(self):
        return mod.approve(self.review,self.rows,self.candidates,self.fingerprints)

    def test_not_preapproved(self):
        self.assertEqual(self.review["candidats"][0]["decision"],"a_revoir")
        with self.assertRaisesRegex(ValueError,"Aucun candidat"):
            self.approve()

    def test_explicit_approval(self):
        self.approved()
        self.assertEqual(self.approve()["approbations"][0]["pointeurs"],[200,300])

    def test_missing_check(self):
        self.approved()["controles"][mod.CHECKS[0]] = False
        with self.assertRaisesRegex(ValueError,"incomplets"):
            self.approve()

    def test_missing_note(self):
        self.approved()["verification"] = " "
        with self.assertRaisesRegex(ValueError,"Justification"):
            self.approve()

    def test_tampered_text_or_address(self):
        for key,value in [("offset",999),("pointeurs",[200]),("nouveau_texte","Autre")]:
            with self.subTest(key=key):
                self.review = mod.prepare(self.rows,self.candidates,[],self.fingerprints)
                self.approved()[key] = value
                with self.assertRaisesRegex(ValueError,"modifiées"):
                    self.approve()

    def test_stale_and_duplicate(self):
        self.approved()
        self.review["empreintes"] = dict(self.fingerprints,charmap_sha256="autre")
        with self.assertRaisesRegex(ValueError,"périmée"):
            self.approve()
        self.review["empreintes"] = self.fingerprints
        self.review["candidats"].append(copy.deepcopy(self.review["candidats"][0]))
        with self.assertRaisesRegex(ValueError,"inattendu"):
            self.approve()

    def test_load_report_complete(self):
        with tempfile.TemporaryDirectory() as temp:
            m,r = Path(temp)/"manifest.json",Path(temp)/"report.json"
            m.write_text(json.dumps({"repliques_secondaires":list(self.rows.values()),
                                     "erreurs_bloquantes":[]}),encoding="utf-8")
            fp = dict(self.fingerprints,manifeste_sha256=hashlib.sha256(m.read_bytes()).hexdigest())
            for items in ([],[dict(self.candidates["A"],etat="identique")]*2):
                r.write_text(json.dumps({"empreintes":fp,"reperes":items}),encoding="utf-8")
                with self.assertRaises(ValueError):
                    mod.load_report(m,r)
            r.write_text(json.dumps({"empreintes":fp,"reperes":list(self.candidates.values())}),encoding="utf-8")
            self.assertEqual(set(mod.load_report(m,r)[1]),{"A"})

if __name__ == "__main__":
    unittest.main()
