# Roadmap

## Approach
Patch Akai's OS rather than rewrite it. The voice chips are undocumented, so
we reuse Akai's own routines for triggering voices, reading the disk and
driving the LCD. New features hook in at a few points:

- **Main loop / UI** – new pages and menu entries
- **MIDI input** – new CC mappings, clock/transport handling
- **Timer interrupt** – sequencer clock and LFOs
- **Voice start/stop** – how both MIDI and the sequencer play notes

New code is written in C (gcc-ia16 or OpenWatcom, targeting 8086/186) plus
NASM, and placed in free ROM space. If there isn't enough room: use larger
EPROMs, or keep the ROM hook small and load most of the code from floppy into
RAM (also faster to test while developing).

## Phase 0 – Hardware + dumps (you)
- [ ] Chip markings for CPU, ROMs, RAM, LCD, SCSI, floppy, UART → `HARDWARE.md`
- [ ] Two matching dumps of every OS EPROM
- [ ] EPROM programmer + spare EPROMs (ideally an EPROM emulator for quick testing)

## Phase 1 – Map the OS
- [ ] Ghidra project: find where the ROM sits in memory, the reset entry point and interrupt vectors
- [ ] Find the routines that draw the LCD, read the keys/wheel, and handle MIDI input
- [ ] Find voice start/stop, program/keygroup data structures, disk load/save
- [ ] Find and reproduce the ROM checksum, if the OS checks one at boot

## Phase 2 – First mod (tests the whole process)
- [ ] "MosuraOS" boot screen + version string
- [ ] Hook that jumps from Akai's code into our code and back, with a test page

## Phase 3 – S950-style performance mods
- [ ] MIDI CC → filter, pitch, loop points and other parameters, changed live
- [ ] Extra LFO / modulation sources
- [ ] Lo-fi modes: lower sample rate / bit depth on resample, S950 / SP-1200-style character
- [ ] "FX mode" (like S950FX): record nonstop into a looping buffer and play it back with a voice,
      so incoming audio gets processed live. Research item – depends on how the hardware handles audio.
- [ ] Workflow: quicker chop/truncate, auto-slice to keygroups, better naming and file pages

## Phase 4 – Sequencer
- [ ] Pattern-based, 16+ tracks, plays internal voices and sends to MIDI out
- [ ] Step and real-time recording, quantize, swing, mute/solo
- [ ] Sync: internal clock, MIDI clock in/out, **SMPTE** (S1100 hardware)
- [ ] Patterns → song chaining
- [ ] Save/load with programs on floppy/SCSI

## Phase 5 – Distribution
- [ ] Patch set that applies to a user's own dump (we don't share Akai's code)
- [ ] Burning guide
