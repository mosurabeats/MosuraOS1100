# OS v4.30 map

Addresses are **runtime** `seg:off` unless marked "image" (offset in the 128 KB ROM image).
Convert with `python3 tools/romtool.py addr rom/os430.bin <image-hex | seg:off>`.
Build a runtime RAM image for Ghidra/ndisasm with `python3 tools/romtool.py ramimage rom/os430.bin build/ram.bin`
(load as x86 real mode, base 0x00000).

## Boot and memory layout
1. Reset → `FFEE:0000` (ROM): copy ROM E000/F000 → RAM 0000/1000, set `0:4F4F = 1`, jump `0000:0000`.
2. `0000:0000` `jmp 0040` → init (image 0x40–0xA3):
   - sets INT 0 (divide error) → `0000:00A8` (writes 0xAA to the LEDs, a crash indicator)
   - copies the major version byte 0x1E → 0x1D (version word at `0:001C`)
   - **moves code into place**, using the segment pointers at image 0xF3/0xF5 (0x0548 / 0x1546):

| Runtime | Image | Size | Contents |
|---|---|---|---|
| `0000:0000–547F` | 0x00000–0x0547F | 21 KB | vectors, init, tables, strings, variables (0x4000–0x54xx are RAM variables) |
| `1000:0000–FFDF` | 0x05480–0x1545F | 64 KB | main code (CS = 1000) |
| `3000:0000–AA7F` | 0x15460–0x1FEDF | 43 KB | more code and data (CS = 3000) |

   - jumps to `1000:0000`.
3. A disk-loaded OS replaces RAM 0x00000–0x1FFFF and re-enters at `0000:0040`, so it goes through the same init and move.
   **Our patched OS is laid out the same way, and the free space after 3000:AA80 is usable.**

## Interrupts (V50 ICU, ICW2 = 0x08 → IR0 = INT 08h)
| INT | IR | Vector → handler | Job |
|---|---|---|---|
| 08h | 0 | `1000:134C` | **System tick** (timer 0). Calls `1000:8AC9`, `1000:B486`, `1000:E7B0`, `1000:55F4` (4 periodic tasks, still to identify) |
| 09h | 1 | `1000:13B1` | **MIDI receive** (SCU). Byte → ring buffer at `0:0200–02FF`, write ptr `0:4A90`, read ptr `0:4A92`. Errors (status & 0x70) reset the UART via `1000:1385` |
| 0Ch | 4 | `0000:00B4` | sets bit 0x20 in `0:4E70` (flag from external INTP4 – source TBD) |
| 0Dh | 5 | `0000:00BB` | **Rotary encoder** A: direction from 8255 port A bit 5 → counters `0:00F7`, `0:00F9` |
| 0Eh | 6 | `0000:00D6` | **Rotary encoder** B: direction from 8255 port A bit 7 → counters `0:00F8`, `0:00FA` |
| 0Ah/0Bh/0Fh | 2/3/7 | `0000:00B3` | unused (`iret`) |

ICU init at `1000:1422` (ICW1 0x13, ICW2 0x08, ICW4 0x03; mask 0x1C). Masks are changed at `1000:143B–1447`.

## V50 internal peripherals (base 0x8000, set via 0xFFFx at `1000:12xx`)
| Ports | Block | Setup |
|---|---|---|
| 0x8000–0x800F | DMA (µPD71071-type) | heavy use: sample transfers, floppy, SCSI |
| 0x8010/0x8012 | ICU (8259-type) | see above |
| 0x8020/0x8022 | SCU (8251-type) = **MIDI** | init `1000:1373`: mode 0x4E (async, 8N1, ×16), command 0x35 |
| 0x8030–0x8036 | TCU (8254-type) | init `1000:132D` |

TCU channels:
- **ch0** mode 2, count 0xC300 (49,920) → INT 08h system tick. About 100 Hz if the TCU clock is 5 MHz (to confirm).
- **ch1** mode 3, count 16 → SCU baud clock (MIDI 31,250 baud × 16)
- **ch2** mode 2, count 65,536, free running: read at `1000:1366` (latch, read MSB, invert) as a coarse timestamp

**Sequencer plan:** reprogram ch0 to a faster rate (e.g. ~2 kHz), run a tempo phase-accumulator
for 96 PPQN on every tick, and call Akai's four periodic tasks only every Nth tick, so their timing stays as before.

## 8255 panel I/O (IC9, ports 0x2000–0x2006)
| Port | Use |
|---|---|
| 0x2000 (A, in) | encoder direction bits (5, 7), other inputs TBD |
| 0x2002 (B, out) | TBD (key matrix scan?) |
| 0x2004 (C, out) | **LEDs**, active low. `1000:1455` lights LED `cl` only, `1000:1466` adds one; current mask in `0:4A94` |
| 0x2006 | control: 0x90 (A in, B/C out) set at `1000:144E` |

Key matrix scan (32 buttons): still to find.

## LCD (LC7981 / HD61830-type, ports 0x6000–0x6006)
Write-register routine at **`1000:D711`** (image 0x12B91): `al` = register, `ah` = value.
- wait: read 0x6006, loop while bit 7 (busy) is set (skipped if `0:4A21` ≠ 0)
- write register number to **0x6004** (instruction), value to **0x6000** (data)
- registers as on the HD61830: 0x0A/0x0B cursor address low/high, 0x0C write display data, 0x08/0x09 display start
- cursor address shadow in `0:5218/5219`, flags `0:527B`
- `1000:D6F1`: sets cursor 0x021C and writes 60 bytes from `0:64B2` (a screen buffer, to confirm)

## Floppy OS boot (see HARDWARE.md for details)
Runs at `1000:A07A` (image 0xF4FA). The directory entry is copied to `0:4EEE`. Version check against `0:001C`.
After loading: copy stub `1000:A13E` (image 0xF5BE) → `7000:FFC0`.

## Other I/O blocks
| Ports | Device | Notes |
|---|---|---|
| 0x0000–0x0FFF | SCSI MB89352 | register n at port 2n (e.g. `in al,0x0C`, `out 0x14`) |
| 0x1000/0x1002 | FDC µPD72068 | status / data |
| 0x3000–0x301E | 74HC259 latch | bit n at 0x3000 + 2n, value in A4 (0x30x0 = 0, 0x30x0+0x10 = 1); bits: 10/20, DM1, FDC/SCSI, MOTON, DM0, FDLODEN, EF MIX, FD RST |
| 0x40E0/0x40E8/0x40F0 … | interpolator ITP-L6009 | voice registers; `rep outsw` to 0x40F0 for block writes |
| 0x5000–0x50D4 | filter FLR-L6009 | |
| 0x7000–0x706A | DSP board / SMPTE / options | DSP56001 host interface: still to find |

## Data structures (first hints)
- Keygroup/voice parameter code around `1000:134C–1420` (image ~0x67CC) reads a structure through `es:si`
  with fields at +0x15, +0x16, +0x18, +0x1D, +0x1E, +0x1F, +0x20, +0x38, +0x39, +0x46.
- Page/field descriptor tables in segment 0 around image 0x28C0–0x2990 (records ending in `73 0B`): the menu system is data-driven.

## Next to find
1. Key matrix scan and the main-button dispatch (what happens on SELECT PROG / EDIT SAMPLE …)
2. Page system: how a page is described, drawn and how soft keys are bound
3. Note-on path: MIDI note → keygroup → voice start (the call our sequencer and pads will use)
4. Program / keygroup / sample header structures in memory
5. Boot/startup screen text → first visible patch ("MosuraOS")
