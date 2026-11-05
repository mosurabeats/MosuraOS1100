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

## Phase 3 – Interface & workflow
Depends on the LCD (40×8 text-only, or a graphic screen?).
- [ ] Clearer page layouts, shortcut keys to jump between pages, "recent" lists
- [ ] If the screen can draw graphics: waveform view for trims, loops and chops
- [ ] Chop/slice: auto-slice a loop into keygroups, chop to grid, quick truncate
- [ ] Easier naming, batch rename, quicker file browsing
- [ ] MIDI CC → filter, pitch, loop points and other parameters, changed live; extra LFOs

## Phase 4 – Sequencer (MPC3000-style)
Our own code, modelled on how the MPC3000 works (it shares an engine with the S3000).
- [ ] 96 PPQN timing, 99 sequences × 32 tracks (or as many as memory allows), songs from chained sequences
- [ ] MPC-style swing (50–75%), timing correct, note repeat
- [ ] Real-time (loop) recording with overdub, step edit, erase while playing
- [ ] Drum mode: 16 "pads" across 4 banks, each pad triggering a keygroup;
      played from a MIDI pad controller, or from front-panel keys in a pad mode
- [ ] Mute/solo, tempo changes, bar copy/insert/delete
- [ ] Sync: internal clock, MIDI clock in/out, **SMPTE** (S1100 hardware)
- [ ] Plays the internal voices and sends to MIDI out; save/load with programs on floppy/SCSI

## Phase 5 – Vintage crunch
Three levels, from safest to most hardware-dependent:
1. **"Vintage" resample option, processed by the CPU (definitely doable).**
   Reduce the sample rate with no anti-aliasing filter and cut the bit
   depth, then stretch back to the original length so the pitch stays put.
   Presets: S900 (40 kHz/12-bit), S950 (48 kHz/12-bit), SP-1200 (26.04 kHz/12-bit),
   MPC60 (40 kHz/12-bit), plus custom values. Optional: imitate the
   drop-sample pitch shifting of old samplers when keygroups are transposed.
2. **Interpolation ROM swap (needs hardware).** The S1000's smooth pitch
   shifting comes from sinc tables stored in EPROMs. Burning tables that just
   repeat the nearest sample ("drop-sample") would give real-time aliasing
   whenever a sample is played away from its root pitch. A double-size EPROM
   plus a switch could select clean or crunchy. Check that the S1100 uses the same scheme.
3. **Real-time bit-crush on the effects DSP**, if the DSP turns out to be programmable (see Phase 6).

## Phase 6 – More effects
- [ ] **CPU processing of samples (definitely doable):** bit-crush, saturation, filters,
      reverse / tape-stop, simple time-stretch and pitch-shift improvements
- [ ] **Real-time effects:** find out whether the effects DSP runs programs that
      the OS loads. If so, write new ones: reverb, crusher, ring mod, filter, tape wobble.
      If its programs are fixed in a ROM, we can only change their parameters.

## Phase 7 – Distribution
- [ ] Patch set that applies to a user's own dump (we don't share Akai's code)
- [ ] Burning guide
