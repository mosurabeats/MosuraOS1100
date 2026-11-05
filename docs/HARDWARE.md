# S1100 hardware notes

Status key: ✅ confirmed on our unit · 🌐 reported online, not checked · ❓ unknown

| Item | Status | Notes |
|---|---|---|
| CPU | 🌐 | x86-compatible NEC V-series (V53 reported for Akai gear of this era). Read the chip marking. |
| CPU clock | ❓ | Read the crystal marking. |
| OS ROMs | 🌐 | Last official OS: v4.3 on EPROM. Need the chip count, type (27C010/020/040?) and IC numbers. |
| Even/odd ROM pairing | ❓ | Check which chip connects to D0–D7 and which to D8–D15. |
| Work RAM (CPU) | ❓ | Separate from sample RAM? How much? Important for storing sequencer data. |
| Sample RAM | 🌐 | 2 MB stock, expandable to 32 MB. |
| Voice hardware | ❓ | Custom Akai chips, 16 voices. We control them only through Akai's own routines. |
| Interpolation ROMs | 🌐 | Sinc tables in EPROMs (S1000 KVR analysis). Dump these too – they are the key to real-time aliasing. |
| Effects DSP | ❓ | Chip type? Does the OS load its program from RAM (= we can write new effects)? |
| LCD | 🌐 | 40×8 characters, or a graphic screen? Controller chip (e.g. a T6963C or HD61830 means graphics are possible). |
| MIDI UART | ❓ | Inside the V53, or a separate chip? |
| Timer for MIDI clock | ❓ | |
| SCSI controller | ❓ | Chip type? |
| Floppy controller | ❓ | Chip type? |
| SMPTE reader | 🌐 | S1100 has one built in. Good for syncing the sequencer. |

## Reading ROMs
Use an EPROM reader set to the exact chip type, and read each chip at least twice.
The reads must match byte for byte (`cmp a.bin b.bin`). Note the label on each chip.
