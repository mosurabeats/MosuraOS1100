# MosuraOS 1100

Custom firmware for the Akai S1100 sampler, built by patching Akai's OS v4.x:
S950-mod-style performance features plus a built-in sequencer.

- `docs/ROADMAP.md` – plan and feature list
- `docs/HARDWARE.md` – what we know about the hardware, and what still needs checking
- `tools/romtool.py` – combine/split chip dumps, find free space, apply checked patches
- `patches/` – our changes, as text files that check the original bytes first
- `rom/` – your local ROM dumps (git-ignored; Akai's code is never committed)

Quick start once you have dumps:

    python3 tools/romtool.py interleave rom/even.bin rom/odd.bin rom/os43.bin
    python3 tools/romtool.py info rom/os43.bin
    python3 tools/romtool.py strings rom/os43.bin | less   # find menu text
    python3 tools/romtool.py free rom/os43.bin             # find room for new code
