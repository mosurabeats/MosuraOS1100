# Roadmap

Personal build for one machine. No distribution, so we can freely reuse and
study Akai code (S1100 OS, and MPC3000/S3000 OS as a reference).

## Approach
Patch Akai's OS v4.30 rather than rewrite it. We reuse Akai's routines for voices,
disk and the LCD, and hook new code in at a few points: main loop/UI, MIDI input,
timer interrupt, voice start/stop.

**Development workflow – boot from floppy, no EPROM burning:**
the S1100 loads a newer OS from floppy at power-on, and the OS runs from RAM anyway.
1. Build a patched OS image (with a higher version number)
2. Write it to a floppy, or a Gotek/HxC floppy emulator image, in Akai OS-disk format
3. Power on → test → if it crashes, take the disk out and the stock ROM OS boots as normal

The disk-loaded OS isn't limited by ROM size: 512 KB of CPU RAM is available.
Burn EPROMs only at the end (or never). New code: C (OpenWatcom / gcc-ia16,
target 80186) plus NASM.

## Phase 0 – Hardware & references
- [x] Service manual parts list → `HARDWARE.md` (CPU = NEC V50, DSP56001, LC7981 graphic LCD)
- [x] OS v4.30 ROM image (`rom/`, git-ignored)
- [ ] Save the OS to floppy on the S1100 and image that disk → learn the OS-disk format
- [ ] Floppy emulator (Gotek with FlashFloppy, or HxC), or a USB floppy drive that can read and write 720K/1.44M disks
- [ ] Look at the board: are the SCOEF ROMs (IC12/13) socketed? Photos of the CPU board
- [ ] S1000 schematic, if you can find one: memory map and I/O decoding

## Phase 1 – Map the OS
- [x] Reset entry point: ROM copied to RAM 0x00000–0x1FFFF, OS starts at 0000:0000
- [ ] Ghidra project (x86 real mode, image loaded at 0x00000), interrupt vectors, V50 peripheral setup
- [ ] Find the routines that draw the LCD, read the keys/wheel, and handle MIDI input
- [ ] Find voice start/stop, program/keygroup data structures, disk load/save
- [ ] Find the disk OS version check and any checksum the OS verifies

## Phase 2 – First mod (tests the whole process)
- [ ] "MosuraOS" boot screen + version string
- [ ] Hook that jumps from Akai's code into our code and back, with a test page

## Phase 3 – Interface & workflow
The LCD is 240×64 graphic (LC7981 controller), so drawing graphics is possible.
- [ ] Clearer page layouts, shortcut keys to jump between pages, "recent" lists
- [ ] Waveform view for trim/loop/chop, envelope graphics, level meters
- [ ] Chop/slice: auto-slice a loop into keygroups, chop to grid, quick truncate
- [ ] Easier naming, batch rename, quicker file browsing
- [ ] MIDI CC → filter, pitch, loop points and other parameters, changed live; extra LFOs

## Phase 4 – Sequencer (MPC3000-style)
Our own sequencer engine, made to behave like the MPC3000. If we can get an MPC3000 ROM dump,
we disassemble its timing, swing and note-repeat code and copy that behaviour exactly.
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
2. **Interpolation ROM swap (needs hardware).** Smooth pitch shifting comes
   from sinc tables in the SCOEF ROMs (IC12/IC13, 512 Kbit each). Burning tables that just
   repeat the nearest sample ("drop-sample") would give real-time aliasing
   whenever a sample is played away from its root pitch. A double-size EPROM
   plus a switch could select clean or crunchy. Check that the S1100 uses the same scheme.
3. **Real-time bit-crush on the effects DSP**, if the DSP turns out to be programmable (see Phase 6).

## Phase 6 – More effects
- [ ] **CPU processing of samples (definitely doable):** bit-crush, saturation, filters,
      reverse / tape-stop, simple time-stretch and pitch-shift improvements
- [ ] **Real-time effects on the DSP56001** (20 MHz, 192 KB delay RAM, no program ROM →
      the OS uploads its program). Find the upload routine and the existing effect program,
      then write new ones in DSP56k assembly: reverb, crusher, ring mod, filters, tape wobble, lo-fi.

## Phase 7 – Burn & install
- [ ] Final images on EPROMs (sockets on the board), originals kept safe as a backup
