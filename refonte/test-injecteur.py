#!/usr/bin/env python3
"""Tests synthétiques de l'injecteur, sans ROM commerciale."""
import importlib.util
import json
import os
import struct
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("injecteur", Path(__file__).with_name("injecter-dialogues.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def number(value):
    result = bytearray()
    while True:
        digit = value & 127
        value >>= 7
        if not value:
            result.append(digit | 128)
            return bytes(result)
        result.append(digit)
        value -= 1

class TestUPS(unittest.TestCase):
    def test_apply(self):
        old, new = b"abcdef", b"abXdef!"
        body = b"UPS1" + number(len(old)) + number(len(new))
        body += number(2) + bytes([ord("c") ^ ord("X"), 0])
        body += number(2) + b"!\0"
        body += struct.pack("<II", mod.crc(old), mod.crc(new))
        ups = body + struct.pack("<I", mod.crc(body))
        self.assertEqual(mod.apply_ups(old, ups), new)
        with self.assertRaises(ValueError):
            mod.apply_ups(b"wrong!", ups)
        with self.assertRaises(ValueError):
            mod.apply_ups(old, ups[:-1] + bytes([ups[-1] ^ 1]))

    def test_number(self):
        for n in (0, 1, 127, 128, 255, 16384, 16777216, 33554432):
            raw = number(n)
            self.assertEqual(mod.read_number(raw, 0, len(raw)), (n, len(raw)))
        with self.assertRaises(ValueError):
            mod.read_number(b"\0", 0, 1)

class TestCodec(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        p = Path(self.temp.name) / "charmap.txt"
        p.write_text("' ' = 00\n'A' = BB\n'B' = BC\n'º' = 2A\n'$' = FF\n'\\'' = B4\n@ Hiragana\n'A' = 01\nPLAYER = FD 01\n", encoding="utf-8")
        self.codec = mod.Codec(p)

    def test_controls(self):
        self.assertEqual(self.codec.encode("A{PLAYER}\nB\n\nA°"), bytes.fromhex("BB FD 01 FE BC FB BB 2A FF"))
        self.assertEqual(self.codec.encode(r"A\nB\lA\pB$", True), bytes.fromhex("BB FE BC FA BB FB BC FF"))
        self.assertEqual(self.codec.encode("A'B"), bytes.fromhex("BB B4 BC FF"))
        for bad in ("{UNKNOWN}", "A$", "A\\nB", "{PLAYER", "Z"):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                self.codec.encode(bad)

    def test_double_source_terminator(self):
        self.assertEqual(self.codec.encode("AB$", True), bytes.fromhex("BB BC FF FF"))
        self.assertEqual(self.codec.encode("AB"), bytes.fromhex("BB BC FF"))
        for bad in ("A$B$", "AB$$", "AB", "$"):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                self.codec.encode(bad, True)

    def test_real_charmap(self):
        path = os.environ.get("CHARMAP_REFERENCE")
        if not path:
            self.skipTest("Charmap de référence non fournie")
        codec = mod.Codec(Path(path))
        self.assertEqual(codec.encode("Été {PLAYER}"), bytes.fromhex("06 E8 1B 00 FD 01 FF"))

class TestRelocation(unittest.TestCase):
    def fixture(self):
        current = bytearray(1024)
        old, new = b"ABCDEF\xff", b"NEW TEXT\xff"
        current[400:407] = old
        current[200:204] = mod.pointer(400)
        current[220:224] = mod.pointer(400)
        return bytes(current), old, new

    def test_relocate(self):
        current, old, new = self.fixture()
        with patch.object(mod, "BASE_SIZE", 1024), patch.object(mod, "MAX_SIZE", 2048):
            output, changes = mod.relocate(current, [("label", 400, old, new, [200, 220])])
            self.assertEqual(output[200:204], mod.pointer(1024))
            self.assertEqual(output[220:224], mod.pointer(1024))
            self.assertEqual(output[400:407], old)
            self.assertEqual(output[1024:1024+len(new)], new)
            self.assertEqual(len(output), 2048)
            self.assertEqual(changes[0]["destination"], 1024)
            self.assertEqual(current[200:204], mod.pointer(400))

    def test_refuse_partial_refs(self):
        current, old, new = self.fixture()
        with patch.object(mod, "BASE_SIZE", 1024), patch.object(mod, "MAX_SIZE", 2048):
            with self.assertRaises(ValueError):
                mod.relocate(current, [("label", 400, old, new, [200])])
            with self.assertRaises(ValueError):
                mod.relocate(current, [])
            with self.assertRaises(ValueError):
                mod.relocate(current, [("label", 400, b"wrong", new, [200, 220])])

    def test_scan_refuses_shared_source(self):
        current, old, new = self.fixture()
        class FakeCodec:
            def encode(self, text, source=False):
                return old if source else new
        row = {"repere":"label", "etat_v3":"a_integrer", "origine_assembleur":"x", "texte":"y"}
        manifest = {"repliques_secondaires":[row], "repliques_narratives":[]}
        self.assertEqual(mod.scan(current, current, manifest, FakeCodec())[0]["etat"], "candidat_a_revoir")
        manifest["repliques_narratives"].append(dict(row, repere="protege"))
        self.assertEqual(mod.scan(current, current, manifest, FakeCodec())[0]["etat"], "texte_court_ou_partage")

if __name__ == "__main__":
    unittest.main()
