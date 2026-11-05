# S1100 hardware notes

Sources: S1100 service manual (Nov 1990, parts list), S1100 schematics (CPU 1/2 L6021002,
CPU 2/2 L6021003), S1100 owner's manual v1.0, and our own disassembly of OS v4.30.
Status: ✅ confirmed · 🔍 inferred from code or part numbers, needs checking · ❓ unknown

## Main parts (CPU board unless noted)

| Item | Part | Status | Notes |
|---|---|---|---|
| CPU | **NEC µPD70216 (V50)**, IC1 | ✅ | 8086/80186 instruction set. Built-in timer (8254-type), interrupt controller (8259-type), DMA and serial port. |
| CPU clock | X1 20 MHz crystal | 🔍 | V50 runs at half the crystal, so probably 10 MHz (the -10 suffix also means 10 MHz). |
| Other crystals | X2 32 MHz, X3 33.8688 MHz | 🔍 | 33.8688 MHz = 768 × 44.1 kHz, so this is the audio clock. |
| OS EPROMs | IC10 (L, D0–7) + IC11 (M, D8–15), MBM27C1001 (128K×8) | ✅ | Wired as a 256 KB window at **C0000–FFFFF**. Akai's code fills only the top half (E0000–FFFFF); **the bottom 128 KB (C0000–DFFFF) is free**, available just by burning full-size 27C1001s. |
| IC10A / IC11A | "BLANK ROM" in parts list | ✅ | Only blank spare EPROMs, not extra sockets (the schematic shows only IC10/IC11). |
| CPU RAM | IC18–21, 4 × MB81C4256 (256K×4) | 🔍 | = 512 KB. The OS runs from RAM (see boot below). |
| Battery/static RAM | IC14, LC3517 (2K×8) | 🔍 | Probably saved settings. |
| Interpolation coefficient ROMs | **IC12 (LSB) + IC13 (MSB), standard 27C512** (64K×8 each = 64K × 16-bit words) | ✅ | Addressed by the interpolator through latches IC39/IC40, read back through buffers IC42/IC43; CE/OE tied low. Ordinary EPROMs, so the drop-sample aliasing tables can simply be burned. Socketed? Check on the board. |
| Voice/pitch chips | ITP-L6009 (interpolator), FLR-L6009 (filter), ADR6021 | ✅ | Custom Akai chips, no documentation. We drive them through Akai's routines. |
| LCD controller | **Sanyo LC7981**, IC7 | ✅ | Text **and graphics** controller (HD61830-type). LCD is **240×64 graphic**, used as 40×8 text. |
| LCD module | EDM-MPJ2COW + EL backlight | ✅ | |
| Floppy controller | µPD72068 (IC3) | ✅ | Floppy is 3.5" HD/DD. |
| Parallel I/O | MB89255 (8255-type), IC9 | ✅ | Probably panel keys/LEDs. |
| Misc | TE7730, CXD1211P, PST520 (reset) | ❓ | TE7730 may be the second clock/timer chip. |
| MIDI | 6N137 opto → **V50 RXD**, TXD → OUT, THRU from RXD | ✅ | MIDI is the V50's built-in serial port (I/O 0x8020/0x8022). |

## Other boards

| Board | Main parts | Notes |
|---|---|---|
| **DSP** | **Motorola DSP56001 @ 20 MHz**, 6 × TC55257 (32K×8 SRAM = 192 KB) | **No program ROM on the board**, so the OS must upload the DSP's program. Writing new real-time effects is possible: reverb, crusher, filters and so on. |
| SMPTE | Hitachi HD63B03 (6303 microcontroller) with its own 27C256 ROM | Separate processor that decodes timecode and reports to the main CPU. |
| SCSI | Fujitsu MB89352 | |
| Voice 1/2 | 4 × PCM56P DAC each | 8 individual outputs. |
| A/D | AK5326 ADC, 3 × PCM56P (L, R, effect send) | |
| Memory | 16 × HM511000 (1M×1) = 2 MB sample RAM | EXM005 (+2 MB), EXM008 (+8 MB, HM514100). |

Front panel: 32 buttons (SW1–32, listed in the service manual), 8 LEDs, 2 rotary encoders (CURSOR, DATA).

## Boot (from disassembly of v4.30)

- Reset: JMP FFEE:0000. The ROM is mapped at E0000–FFFFF.
- The boot code **copies the whole ROM into RAM** (E000→0000:0000, F000→1000:0000) and jumps to 0000:0000.
  The OS runs from RAM, and the ROM is only read at power-on.
- A second entry point at FFEE:0033 is a **serial loader**. It reads a length and the
  data from I/O ports 0x8020/0x8022 into 0000:0000, then the second 64 KB block into 1000:0000, then runs it.
  Port 0x8020 is the V50 serial port = **MIDI**, so this is a load-the-OS-over-MIDI mode
  (probably factory use). If we find how to reach it, it would be the fastest way to test: send the OS from a computer over MIDI.
- The owner's manual says: if a disk holding a **later OS version** is in the drive at power-on,
  that OS is loaded instead of the ROM. The OS can also save itself to disk ("OPERATING SYSTEM").

## Memory map (CPU 1/2 schematic + boot code)
| Address | What |
|---|---|
| 00000–7FFFF | CPU work RAM, 512 KB (IC18–21). The OS runs from 00000–1FFFF after boot; stack at 3000:0000 |
| C0000–DFFFF | OS EPROMs, bottom half: **unused/free** |
| E0000–FFFFF | OS EPROMs, top half: OS v4.30 (copied to RAM at boot) |

ROM select: IC51 (AND A18·A19) → IC53 inverter → CE of IC10/IC11. CPU A1–A17 → ROM A0–A16.

## I/O map (IC30 74HC138: A=A12, B=A13, C=A14, enabled when A15=0)
| Ports | Select line | Device |
|---|---|---|
| 0x0000–0x0FFF | SCSICS | SCSI controller MB89352 |
| 0x1000–0x1FFF | FDCCS | Floppy controller µPD72068 |
| 0x2000–0x2FFF | CONICS | 8255 I/O expander IC9: panel keys, LEDs, encoders (CPU A1/A2 → 8255 A0/A1) |
| 0x3000–0x3FFF | (Y3) | Probably the IC29 74HC259 control latch (bits: 10/20, DM1, FDC/SCSI, MOTON, DM0, FDLODEN, EF MIX, FD RST) |
| 0x4000–0x4FFF | LSICS | Interpolator ITP-L6009 (voice engine) |
| 0x5000–0x5FFF | LSFCS | Digital filter FLR-L6009 |
| 0x6000–0x6FFF | LCDCS | LCD controller LC7981 |
| 0x7000–0x7FFF | GPCS | Expansion bus: DSP board, SMPTE board, option boards |
| 0x80xx | — | V50 internal peripherals (serial/MIDI at 0x8020/0x8022, timer around 0x8030) |

## Hardware test mode
Hold MARK + NAME at power-on, then press +. It offers CPU RAM and sample RAM tests and ADC offset checks. Press F8 to leave.
