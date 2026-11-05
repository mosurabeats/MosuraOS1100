#!/usr/bin/env python3
"""mkosdisk -- build and inspect Akai S1000/S1100 floppy images holding an OS.

How the S1100 boots an OS from floppy (from disassembly of OS v4.30, CS=0548 module
around image offset 0xF4FA):
  * At power-on it looks for a file of type 'c' (0x63, "operating system").
  * It loads the file only if the file's directory-entry OS version >= the ROM's
    version (word at 0000:001C, 0x091E for v4.30), and the major byte is > 5
    (major 5 or less means an S1000 OS).
  * Displayed version = (major - 5).(minor), so 0x091E shows as "4.30".
  * The file is a raw RAM image: the first 64 KB goes to 0000:0000 and the rest (file size
    - 64 KB, which must be < 64 KB) goes to 1000:0000. It then jumps to 0000:0040.
  * So an OS file is the 128 KB ROM image minus the boot code at the top
    (0x1FEE0 bytes for v4.30).

Floppy layout (S1000 format, as documented by akaiutil):
  1 KB blocks; HD = 1600 blocks (5 header blocks), DD = 800 blocks (4 header blocks).
  Header = 64 directory entries x 24 bytes, FAT (2 bytes per block), volume label.
  FAT codes: 0x4000 system block, 0xC000 end of file, otherwise next block number.

Usage:
  mkosdisk.py build OS.bin OUT.img [--version 5.00] [--name MOSURAOS] [--dd]
  mkosdisk.py ls IMAGE.img
"""
import argparse
import struct
import sys
from pathlib import Path

BLK = 1024
GEOM = {"hd": (1600, 5), "dd": (800, 4)}  # (blocks, header blocks)
NENT = 64
FAT_SYS, FAT_END = 0x4000, 0xC000
FTYPE_OS = 0x63  # 'c'
OS_BOOTSTUB = 0x1FEE0  # ROM boot code at the top, not part of the RAM image
AKAI_CHARS = "0123456789 ABCDEFGHIJKLMNOPQRSTUVWXYZ#+-."  # same table as in ROM at 0x500


def akai_name(s):
    s = s.upper().ljust(12)[:12]
    try:
        return bytes(AKAI_CHARS.index(c) for c in s)
    except ValueError:
        sys.exit(f"name may only use: {AKAI_CHARS!r}")


def ascii_name(b):
    return "".join(AKAI_CHARS[x] if x < len(AKAI_CHARS) else "?" for x in b).rstrip()


def parse_version(s):
    """'5.00' -> stored word (major+5)<<8 | minor."""
    major, minor = s.split(".")
    major, minor = int(major) + 5, int(minor)
    if not (5 < major < 256 and 0 <= minor < 100):
        sys.exit("version must look like 4.30 .. 250.99")
    return major << 8 | minor


def fmt_version(w):
    return f"{(w >> 8) - 5}.{w & 0xFF:02d}"


def dir_entry(name, ftype, size, start, osver):
    return (akai_name(name) + bytes([0x20] * 4) + bytes([ftype])
            + struct.pack("<I", size)[:3] + struct.pack("<HH", start, osver))


def cmd_build(a):
    img = bytearray(Path(a.os).read_bytes())
    if len(img) == 0x20000:
        img = img[:OS_BOOTSTUB]  # full ROM image given: drop the boot stub
    if not (0x10000 < len(img) < 0x20000):
        sys.exit(f"OS image must be between 64 KB and 128 KB (got {len(img)} bytes)")
    osver = parse_version(a.version)
    if osver < 0x091E:
        sys.exit("version must be 4.30 or higher, or the S1100 ignores the disk "
                 "and boots its ROM OS (v4.30)")
    # stamp the version into the image too (minor at 0x1C, major at 0x1E; boot code
    # copies 0x1E to 0x1D so the running OS sees the word 0x001C)
    img[0x1C], img[0x1E] = osver & 0xFF, osver >> 8

    nblk, hblk = GEOM["dd" if a.dd else "hd"]
    need = -(-len(img) // BLK)
    if hblk + need > nblk:
        sys.exit("OS does not fit on this disk")
    disk = bytearray(nblk * BLK)

    entries = [dir_entry(a.name, FTYPE_OS, len(img), hblk, osver)]
    entries += [dir_entry("VVVVVVVVVVVV", 0, 0, 0, osver)] * (NENT - 1)  # free entries
    hdr = bytearray(b"".join(entries))

    fat = [0] * nblk
    for i in range(hblk):
        fat[i] = FAT_SYS
    for i in range(need):
        b = hblk + i
        fat[b] = FAT_END if i == need - 1 else b + 1
    hdr += b"".join(struct.pack("<H", x) for x in fat)

    label = akai_name(a.name) + bytes(2) + struct.pack("<H", osver)
    volparam = bytearray(48)
    volparam[1] = volparam[2] = 1  # program select: omni on, enabled (akaiutil defaults)
    hdr += label + volparam
    disk[:len(hdr)] = hdr
    disk[hblk * BLK:hblk * BLK + len(img)] = img
    Path(a.out).write_bytes(disk)
    print(f"wrote {a.out}: {'DD 800K' if a.dd else 'HD 1.6M'}, OS file '{a.name}' "
          f"{len(img)} bytes, version {fmt_version(osver)} (0x{osver:04X})")


def cmd_ls(a):
    d = Path(a.img).read_bytes()
    nblk = len(d) // BLK
    print(f"{a.img}: {len(d)} bytes, {nblk} blocks")
    fat_off = NENT * 24
    lab_off = fat_off + 2 * (1600 if nblk >= 1600 else 800)
    lab = d[lab_off:lab_off + 64]
    print(f"label '{ascii_name(lab[:12])}' osver 0x{struct.unpack('<H', lab[14:16])[0]:04X}")
    for i in range(NENT):
        e = d[i * 24:(i + 1) * 24]
        if e[16] == 0:
            continue
        size = e[17] | e[18] << 8 | e[19] << 16
        start, osver = struct.unpack("<HH", e[20:24])
        kind = "OS" if e[16] == FTYPE_OS else chr(e[16]) if 32 < e[16] < 127 else hex(e[16])
        print(f"  {i:2d} {ascii_name(e[:12]):12s} type {kind:3s} size {size:7d} "
              f"start {start:4d} osver 0x{osver:04X} ({fmt_version(osver)})")


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    s = p.add_subparsers(dest="cmd", required=True)
    b = s.add_parser("build")
    b.add_argument("os"); b.add_argument("out")
    b.add_argument("--version", default="5.00", help="displayed version, must be >= 4.30")
    b.add_argument("--name", default="MOSURAOS")
    b.add_argument("--dd", action="store_true", help="800K double-density disk")
    b.set_defaults(f=cmd_build)
    l = s.add_parser("ls"); l.add_argument("img"); l.set_defaults(f=cmd_ls)
    a = p.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
