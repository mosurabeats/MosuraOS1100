# MosuraOS 1100

Custom firmware for the Akai S1100 sampler, built by patching Akai's OS v4.x:
S950-mod-style performance features plus a built-in sequencer.

- `docs/ROADMAP.md` – plan and feature list
- `docs/HARDWARE.md` – what we know about the hardware, and what still needs checking
- `tools/romtool.py` – combine/split chip dumps, find free space, apply checked patches
- `tools/mkosdisk.py` – build bootable Akai floppy images (`.img`) holding an OS, and list disk contents
- `patches/` – our changes, as text files that check the original bytes first
- `rom/` – your local ROM dumps (git-ignored; Akai's code is never committed)

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
