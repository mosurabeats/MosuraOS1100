#!/usr/bin/env python3
"""build -- make a MosuraOS image from the stock Akai ROM image.

    python3 tools/build.py                       # -> build/mosura.bin + build/*.img
    python3 tools/build.py --gotek /media/STICK  # also add it to a Gotek stick

Steps: read rom/os430.bin, apply patches/os430/*.patch in name order (each patch
checks the original bytes first), stamp the version, write the OS image and a
bootable floppy image.

Version numbering: the ROM's loader shows "OPERATING SYSTEM x.xx" and only boots
disks with a version >= 4.30, so MosuraOS M.m is stored as Akai version (5+M).mm:
MosuraOS 0.1 -> 5.01, 0.12 -> 5.12, 1.0 -> 6.00.
"""
import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import mkosdisk  # noqa: E402
import romtool  # noqa: E402


def akai_version(mosura):
    major, _, minor = mosura.partition(".")
    major, minor = int(major), int(minor or 0)
    if not (0 <= minor < 100):
        sys.exit("minor version must be 0..99")
    return f"{major + 5}.{minor:02d}"


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--rom", default=str(ROOT / "rom/os430.bin"))
    p.add_argument("--patches", default=str(ROOT / "patches/os430"))
    p.add_argument("--out", default=str(ROOT / "build"))
    p.add_argument("--gotek", help="also add the build to this Gotek stick/folder")
    p.add_argument("--dd", action="store_true", help="800K disk images")
    a = p.parse_args()

    mosura = (ROOT / "VERSION").read_text().strip()
    akai = akai_version(mosura)
    rom = Path(a.rom)
    if not rom.exists():
        sys.exit(f"stock ROM image not found: {rom} (see rom/README.md)")
    d = bytearray(rom.read_bytes())
    orig = bytes(d)

    patches = sorted(Path(a.patches).glob("*.patch"))
    total = 0
    for pf in patches:
        n = romtool.apply_patch_file(d, pf)
        total += n
        print(f"  {pf.name}: {n} patch(es)")
    changed = sum(1 for x, y in zip(orig, d) if x != y)

    out = Path(a.out)
    out.mkdir(exist_ok=True)
    binp = out / "mosura.bin"
    binp.write_bytes(d)
    osver = mkosdisk.parse_version(akai)
    disk = mkosdisk.make_disk(bytes(d), osver, "MOSURAOS", a.dd)
    imgp = out / f"MOSURAOS_{mosura}_{'DD' if a.dd else 'HD'}.img"
    imgp.write_bytes(disk)
    print(f"MosuraOS {mosura} (loads as OPERATING SYSTEM {akai}): "
          f"{len(patches)} files, {total} patches, {changed} bytes changed")
    print(f"wrote {binp}\nwrote {imgp}")

    if a.gotek:
        mkosdisk.cmd_gotek(argparse.Namespace(
            dir=a.gotek, os=str(binp), version=akai, label=f"OS{mosura}",
            name="MOSURAOS", stock=a.rom, dd=a.dd, force_cfg=False))


if __name__ == "__main__":
    main()
