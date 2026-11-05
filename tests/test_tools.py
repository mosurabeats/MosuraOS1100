"""Tests for the MosuraOS tools. Uses synthetic data only (no Akai ROM needed).

    python3 -m unittest discover -s tests -v
"""
import argparse
import struct
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import build  # noqa: E402
import mkosdisk  # noqa: E402
import romtool  # noqa: E402


def fake_rom():
    """128 KB image shaped like the S1100 OS: version 4.30 at 0x1C/0x1E,
    relocation pointers at 0xF3/0xF5, some text."""
    d = bytearray(range(256)) * 512
    d[0x1C], d[0x1D], d[0x1E] = 0x1E, 0x00, 0x09
    d[0xF3:0xF7] = struct.pack("<HH", 0x0548, 0x1546)
    d[0x1000:0x1012] = b"PROGRAMS IN MEMORY"
    return d


class RomTool(unittest.TestCase):
    def test_interleave_split_roundtrip(self):
        with tempfile.TemporaryDirectory() as t:
            t = Path(t)
            (t / "img").write_bytes(fake_rom())
            romtool.cmd_split(argparse.Namespace(inp=t / "img", even=t / "e", odd=t / "o"))
            romtool.cmd_interleave(argparse.Namespace(even=t / "e", odd=t / "o", out=t / "r"))
            self.assertEqual((t / "img").read_bytes(), (t / "r").read_bytes())

    def apply(self, text):
        d = fake_rom()
        with tempfile.TemporaryDirectory() as t:
            pf = Path(t) / "x.patch"
            pf.write_text(text)
            n = romtool.apply_patch_file(d, pf)
        return d, n

    def test_patch_text_and_hex(self):
        d, n = self.apply('0x1000 "PROGRAMS" -> "MOSURA#1"  # hash inside quotes is kept\n'
                          '0x0010 10 11 -> AA BB\n')
        self.assertEqual(n, 2)
        self.assertEqual(d[0x1000:0x1008], b"MOSURA#1")
        self.assertEqual(d[0x10:0x12], b"\xAA\xBB")

    def test_patch_refuses_wrong_bytes(self):
        with self.assertRaises(SystemExit):
            self.apply('0x1000 "PROGRAMX" -> "MOSURA 1"\n')

    def test_patch_refuses_length_change(self):
        with self.assertRaises(SystemExit):
            self.apply('0x1000 "PROGRAMS" -> "MOSURA"\n')

    def test_patch_free_space_only_on_blank(self):
        with self.assertRaises(SystemExit):
            self.apply("0x0020 * -> 90 90\n")

    def test_layout_matches_boot_code(self):
        lay = romtool.layout(fake_rom())
        self.assertEqual(lay, [(0, 0x5480, 0), (0x5480, 0x15460, 0x10000), (0x15460, 0x1FEE0, 0x30000)])


class MkOsDisk(unittest.TestCase):
    def test_disk_layout(self):
        disk = mkosdisk.make_disk(bytes(fake_rom()), 0x0A01, "MOSURAOS")
        self.assertEqual(len(disk), 1600 * 1024)
        e = disk[:24]
        self.assertEqual(e[16], 0x63)                                   # type 'c' = OS
        self.assertEqual(e[17] | e[18] << 8 | e[19] << 16, 0x1FEE0)     # size
        self.assertEqual(struct.unpack("<HH", e[20:24]), (5, 0x0A01))   # start block, version
        fat = [struct.unpack("<H", disk[1536 + 2 * i:1538 + 2 * i])[0] for i in range(1600)]
        self.assertEqual(fat[:5], [0x4000] * 5)
        last = 5 + -(-0x1FEE0 // 1024) - 1
        self.assertEqual(fat[last], 0xC000)
        self.assertTrue(all(fat[b] == b + 1 for b in range(5, last)))
        os_data = disk[5 * 1024:5 * 1024 + 0x1FEE0]
        self.assertEqual((os_data[0x1C], os_data[0x1E]), (0x01, 0x0A))  # version stamped

    def test_rejects_old_version(self):
        with self.assertRaises(SystemExit):
            mkosdisk.make_disk(bytes(fake_rom()), mkosdisk.parse_version("4.20"), "X")

    def test_names_and_versions(self):
        self.assertEqual(mkosdisk.ascii_name(mkosdisk.akai_name("mosura os")), "MOSURA OS")
        self.assertEqual(mkosdisk.parse_version("4.30"), 0x091E)
        self.assertEqual(mkosdisk.fmt_version(0x0A01), "5.01")

    def test_build_version_mapping(self):
        self.assertEqual(build.akai_version("0.1"), "5.01")
        self.assertEqual(build.akai_version("0.12"), "5.12")
        self.assertEqual(build.akai_version("1.0"), "6.00")


if __name__ == "__main__":
    unittest.main()
