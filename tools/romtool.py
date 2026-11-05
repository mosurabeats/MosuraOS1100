#!/usr/bin/env python3
"""romtool -- helpers for working on Akai S1100 EPROM images.

16-bit CPUs usually run from a pair of 8-bit EPROMs: one holds the even
bytes, the other the odd bytes. We do all analysis and patching on the
combined ("interleaved") image, then split it back into chip images for
burning.

Commands:
  interleave EVEN ODD OUT     merge two chip dumps into one 16-bit image
  split IN EVEN ODD           split a 16-bit image back into chip images
  info IN                     size, simple checksums, vector area
  free IN [--min N]           find runs of 0xFF/0x00 (candidate patch space)
  strings IN [--min N]        printable strings with offsets (finds UI text)
  patch IN PATCHFILE OUT      apply a verified patch file (see patches/README.md)
"""
import argparse
import sys
from pathlib import Path


def read(p):
    return Path(p).read_bytes()


def cmd_interleave(a):
    even, odd = read(a.even), read(a.odd)
    if len(even) != len(odd):
        sys.exit(f"size mismatch: even={len(even)} odd={len(odd)}")
    out = bytearray(len(even) * 2)
    out[0::2], out[1::2] = even, odd
    Path(a.out).write_bytes(out)
    print(f"wrote {a.out} ({len(out)} bytes)")


def cmd_split(a):
    data = read(a.inp)
    if len(data) % 2:
        sys.exit("image length is odd; cannot split")
    Path(a.even).write_bytes(data[0::2])
    Path(a.odd).write_bytes(data[1::2])
    print(f"wrote {a.even} and {a.odd} ({len(data) // 2} bytes each)")


def cmd_info(a):
    d = read(a.inp)
    words = [d[i] | d[i + 1] << 8 for i in range(0, len(d) - 1, 2)]
    print(f"size      : {len(d)} bytes (0x{len(d):X})")
    print(f"sum8      : 0x{sum(d) & 0xFF:02X}")
    print(f"sum16 byte: 0x{sum(d) & 0xFFFF:04X}")
    print(f"sum16 word: 0x{sum(words) & 0xFFFF:04X}")
    # x86 reset vector is 16 bytes below the top of the address space; if
    # the ROM is mapped at the top, its last 16 bytes hold the first jump.
    tail = d[-16:]
    print(f"last 16   : {tail.hex(' ')}")
    if tail[0] == 0xEA:
        off = tail[1] | tail[2] << 8
        seg = tail[3] | tail[4] << 8
        print(f"            -> looks like JMP FAR {seg:04X}:{off:04X} (x86 reset entry)")


def runs(d, minlen):
    i = 0
    while i < len(d):
        b = d[i]
        if b in (0x00, 0xFF):
            j = i
            while j < len(d) and d[j] == b:
                j += 1
            if j - i >= minlen:
                yield i, j - i, b
            i = j
        else:
            i += 1


def cmd_free(a):
    total = 0
    for off, n, b in runs(read(a.inp), a.min):
        total += n
        print(f"0x{off:06X}  {n:7d} bytes of 0x{b:02X}")
    print(f"total candidate space: {total} bytes")


def cmd_strings(a):
    d = read(a.inp)
    cur, start = bytearray(), 0
    for i, b in enumerate(d + b"\0"):
        if 0x20 <= b < 0x7F:
            if not cur:
                start = i
            cur.append(b)
        else:
            if len(cur) >= a.min:
                print(f"0x{start:06X}  {cur.decode()}")
            cur = bytearray()


def parse_hex(s):
    s = s.replace(" ", "")
    return bytes.fromhex(s) if s else b""


def cmd_patch(a):
    """Patch file format, one patch per line:
        OFFSET  EXPECTED_HEX  ->  NEW_HEX   # comment
    EXPECTED must match the input exactly, so a patch can never be applied
    to the wrong OS version. Use '*' for EXPECTED only on free space you
    have confirmed is unused (it then must be all 0xFF or all 0x00).
    """
    d = bytearray(read(a.inp))
    applied = 0
    for ln, raw in enumerate(Path(a.patchfile).read_text().splitlines(), 1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        try:
            left, new_hex = line.split("->")
            off_s, exp_s = left.split(None, 1)
            off = int(off_s, 16)
            new = parse_hex(new_hex)
        except ValueError:
            sys.exit(f"{a.patchfile}:{ln}: cannot parse: {raw}")
        cur = bytes(d[off:off + len(new)])
        if exp_s.strip() == "*":
            if len(set(cur)) != 1 or cur[0] not in (0x00, 0xFF):
                sys.exit(f"{a.patchfile}:{ln}: 0x{off:X} is not free space")
        else:
            exp = parse_hex(exp_s)
            if len(exp) != len(new):
                sys.exit(f"{a.patchfile}:{ln}: expected/new length differ")
            if cur != exp:
                sys.exit(f"{a.patchfile}:{ln}: at 0x{off:X} found {cur.hex(' ')}, "
                         f"expected {exp.hex(' ')} -- wrong OS version?")
        d[off:off + len(new)] = new
        applied += 1
    Path(a.out).write_bytes(d)
    print(f"applied {applied} patches -> {a.out}")
    print("NOTE: if the OS checks a ROM checksum, fix it before burning.")


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    s = p.add_subparsers(dest="cmd", required=True)
    c = s.add_parser("interleave"); c.add_argument("even"); c.add_argument("odd"); c.add_argument("out")
    c.set_defaults(f=cmd_interleave)
    c = s.add_parser("split"); c.add_argument("inp"); c.add_argument("even"); c.add_argument("odd")
    c.set_defaults(f=cmd_split)
    c = s.add_parser("info"); c.add_argument("inp"); c.set_defaults(f=cmd_info)
    c = s.add_parser("free"); c.add_argument("inp"); c.add_argument("--min", type=int, default=256)
    c.set_defaults(f=cmd_free)
    c = s.add_parser("strings"); c.add_argument("inp"); c.add_argument("--min", type=int, default=6)
    c.set_defaults(f=cmd_strings)
    c = s.add_parser("patch"); c.add_argument("inp"); c.add_argument("patchfile"); c.add_argument("out")
    c.set_defaults(f=cmd_patch)
    a = p.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
