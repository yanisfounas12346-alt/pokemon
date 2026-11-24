#!/usr/bin/env python3
"""Tests d'export UPS et de contrôle du journal, sans ROM commerciale."""
import importlib.util
import random
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("exporteur", Path(__file__).with_name("exporter-ups.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
inj = mod.inj

class TestUPS(unittest.TestCase):
    def roundtrip(self, old, new):
        ups = mod.create_ups(old, new)
        self.assertEqual(inj.apply_ups(old, ups), new)
        reverse = mod.reverse_ups(ups)
        self.assertEqual(inj.apply_ups(new, reverse), old)
        self.assertEqual(mod.reverse_ups(reverse), ups)

    def test_cases(self):
        for old, new in [
            (b"ABC", b"ABC"),
            (b"ABC", b"XBC"),
            (b"ABC", b"ABX"),
            (b"ABC", b"XYZ"),
            (b"ABC", b"ABC\0\0"),
            (b"ABC", b"ABC\0Z"),
            (b"ABC\0Z", b"ABC"),
            (b"\0"*20000, b"\0"*19999+b"\xff"),
            (b"\xff"*300, b"\0"*300),
        ]:
            with self.subTest(old_size=len(old), new_size=len(new)):
                self.roundtrip(old, new)

    def test_random(self):
        rng = random.Random(312)
        for _ in range(100):
            old = bytes(rng.randrange(256) for _ in range(rng.randint(1, 256)))
            new = bytearray(old)
            for _ in range(5):
                new[rng.randrange(len(new))] ^= rng.randrange(1, 256)
            if rng.randrange(2):
                new.extend(bytes(rng.randrange(256) for _ in range(10)))
            else:
                del new[max(1, len(new)-10):]
            self.roundtrip(old, bytes(new))

    def test_invalid(self):
        with self.assertRaises(ValueError):
            mod.create_ups(b"", b"x")
        with self.assertRaises(ValueError):
            mod.reverse_ups(b"UPS1")
        data = mod.create_ups(b"abc", b"xyz")
        with self.assertRaises(ValueError):
            mod.reverse_ups(data[:-1]+bytes([data[-1]^1]))

class TestJournal(unittest.TestCase):
    def fixture(self):
        old = bytearray(1024)
        old[400:407] = b"ABCDEF\xff"
        old[200:204] = inj.pointer(400)
        old[220:224] = inj.pointer(400)
        old = bytes(old)
        out, changes = inj.relocate(old, [("label",400,b"ABCDEF\xff",b"NOUVEAU\xff",[200,220])])
        journal = {"empreintes":{"base_sha256":inj.digest(old),"v3_sha256":inj.digest(old)},
                   "crc32_sortie":f"{inj.crc(out):08X}","modifications":changes}
        return old, out, journal

    def test_valid(self):
        with patch.object(inj,"BASE_SIZE",1024), patch.object(inj,"MAX_SIZE",2048):
            old,out,journal = self.fixture()
            self.assertEqual(mod.validate_injection(old,old,out,journal),1)

    def test_reject_unlogged_change(self):
        with patch.object(inj,"BASE_SIZE",1024), patch.object(inj,"MAX_SIZE",2048):
            old,out,journal = self.fixture()
            corrupt = bytearray(out)
            corrupt[300] ^= 1
            journal["crc32_sortie"] = f"{inj.crc(corrupt):08X}"
            with self.assertRaisesRegex(ValueError,"non journalisées"):
                mod.validate_injection(old,old,bytes(corrupt),journal)

    def test_reject_missing_pointer(self):
        with patch.object(inj,"BASE_SIZE",1024), patch.object(inj,"MAX_SIZE",2048):
            old,out,journal = self.fixture()
            journal["modifications"][0]["pointeurs"] = [200]
            with self.assertRaisesRegex(ValueError,"incomplètes"):
                mod.validate_injection(old,old,out,journal)

    def test_reject_wrong_base(self):
        with patch.object(inj,"BASE_SIZE",1024), patch.object(inj,"MAX_SIZE",2048):
            old,out,journal = self.fixture()
            with self.assertRaisesRegex(ValueError,"autre base"):
                mod.validate_injection(b"wrong",old,out,journal)

if __name__ == "__main__":
    unittest.main()
