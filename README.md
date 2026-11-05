# MosuraOS 1100

Custom firmware for the Akai S1100 sampler, built by patching Akai's OS v4.x:
S950-mod-style performance features plus a built-in sequencer.

- `docs/ROADMAP.md` – plan and feature list
- `docs/DESIGN.md` – **the MosuraOS concept**: beatmaking workflow, modes, pads, screens, sequencer
- `docs/HARDWARE.md` – what we know about the hardware, and what still needs checking
- `docs/OSMAP.md` – map of Akai OS v4.30: memory layout, interrupts, I/O, routines found so far
- `tools/romtool.py` – combine/split chip dumps, find free space, apply checked patches
- `tools/mkosdisk.py` – build bootable Akai floppy images (`.img`) holding an OS, and list disk contents
- `patches/` – our changes, as text files that check the original bytes first
- `rom/` – your local ROM dumps (git-ignored; Akai's code is never committed)

## Build MosuraOS

    python3 tools/build.py                        # -> build/mosura.bin, build/MOSURAOS_<ver>_HD.img
    python3 tools/build.py --gotek /media/STICK   # also add it to a FlashFloppy Gotek stick
    python3 -m unittest discover -s tests         # tool tests (no ROM needed)

Needs `rom/os430.bin` (the stock v4.30 image, git-ignored). Patches live in
`patches/os430/`, applied in name order; the version is in `VERSION`.
MosuraOS M.m loads as "OPERATING SYSTEM (5+M).mm" (0.1 → 5.01), because the
ROM only boots disk OS versions of 4.30 or higher.

## Working with the ROM

Quick start once you have dumps:

    python3 tools/romtool.py interleave rom/even.bin rom/odd.bin rom/os430.bin
    python3 tools/romtool.py info rom/os430.bin
    python3 tools/romtool.py strings rom/os430.bin | less   # find menu text
    python3 tools/romtool.py free rom/os430.bin             # find room for new code
    python3 tools/mkosdisk.py build rom/os430.bin build/MOSURA_HD.img --version 4.31

Gotek (FlashFloppy) USB stick – writes FF.CFG, a stock 4.30 image in slot 00,
and each test build in the next numbered slot:

    python3 tools/mkosdisk.py gotek /media/USBSTICK
    python3 tools/mkosdisk.py gotek /media/USBSTICK \
        --os build/mosura.bin --version 4.31 --label banner
