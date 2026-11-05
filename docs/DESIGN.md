# MosuraOS design: the S1100 as a beat machine

> Dig, sample, chop, sequence.

## The idea

The S1000/S1100 OS was built for **instrument sampling**: multisampled pianos
across a keyboard, velocity crossfades, keyspans, positional crossfades, LFOs per
keygroup. Its sound is great, but the workflow is built for a sound-library
engineer, not someone digging through records.

MosuraOS turns it into a **sampling and sequencing machine for crate-diggers**,
in the spirit of how *Endtroducing.....*, *Since I Left You* or *Deadringer* were made:

- **Collect**: record lots of material fast, from records, tape, anything, and keep it organised.
- **Chop**: turn a break or a phrase into hits and pieces in seconds.
- **Flip**: re-pitch, reverse, crunch, layer and stretch the pieces.
- **Sequence**: play and arrange them with MPC feel (swing, note repeat, loop recording).

**Meet in the middle.** The MPC2000 is bare bones; the S1100 is deep. MosuraOS keeps
the S1100's power (16-bit, 32 MB, 8 outputs, DSP effects, SCSI, SMPTE, time-stretch, its
filter) but puts the beatmaking path up front and hides the instrument-sampling depth
behind one key combination (CLASSIC mode, see below).

### Design rules
1. **Every common action in 3 presses or fewer.** Record → chop → play is the core loop.
2. **Pads, not keyboards.** The unit you work with is a pad: 1 sample, 1 trigger, its own settings.
3. **Never lose the source.** Chopping makes new samples or regions; the original recording stays until you delete it.
4. **The grid is the tempo.** Chopping, stretching, quantising and metronome all follow the same BPM.
5. **Stock files stay stock.** Kits are saved as normal S1000/S1100 programs + samples, so disks load on any Akai S1000/S1100/S3000.
6. **Nothing is removed, only hidden.** All of Akai's pages stay reachable in CLASSIC mode.

---

## Words we use

| MosuraOS | Akai underneath | What it is |
|---|---|---|
| **Sample** | sample | A recording in memory (up to 200). |
| **Pad** | keygroup | One trigger: a sample plus tune, level, pan, filter, decay, mute group, output. |
| **Kit** | program | 64 pads (4 banks × 16), answering on MIDI notes 35–98 by default. |
| **Sequence** | (new) | A loop of 1–99 bars with up to 32 tracks. |
| **Track** | (new) | Notes for one kit, or for an external MIDI channel. |
| **Song** | (new) | A list of sequences with repeat counts. |
| **Crate** | (new) | A long "dig" recording you take chops from. |

---

## The front panel, remapped

```
   [F1] [F2] [F3] [F4] [F5] [F6] [F7] [F8]      soft keys (labels on LCD bottom line)

   [MAIN][SAMPL][CHOP][PADS][DISK][STEP][SONG][SETUP]   main buttons, each with an LED
    sel   edit   edit  midi  disk master drum utility    (original labels)
    prog  sampl  prog              tune

   CURSOR knob   DATA knob

   number keypad: numbers and naming as on the stock S1100, plus a few shortcuts
```

- **Playing is done on a MIDI pad controller** (see *The MIDI controller* below).
  The S1100 panel is for editing and navigation only.
- **Main buttons** select the mode (table below). The LED of the current mode lights;
  in MAIN the PLAY/REC state blinks on the MAIN LED to the beat.
- **Number keypad** keeps its Akai job: typing numbers and names. Shortcuts in MAIN:
  **ENT/PLAY** = play/stop, **MARK** = record, **JUMP** = go to bar (type the bar number).
  In CHOP, **MARK** drops a slice point while the sample plays.
- **CURSOR / DATA knobs** stay as Akai designed them: CURSOR moves between fields, DATA changes values.
- **Footswitches 1 and 2**: default PLAY/STOP and REC/OVERDUB (assignable: punch-in, tap tempo, next pad bank, note repeat).
- **CLASSIC mode**: hold **UTILITY + DISK** for 1 second to drop into the untouched Akai
  OS pages. Same again to come back. The sound engine and memory are shared, so you
  can use deep Akai editing (loop crossfade, velocity layers) on any sample, then return.

### Mode map

| Button (original) | Mode | Job |
|---|---|---|
| SELECT PROG | **MAIN** | Play/record sequences. Tempo, swing, track, bar position. Home base. |
| EDIT SAMPLE | **SAMPLE** | Record from the inputs or resample. Crate recording. Vintage modes. |
| EDIT PROG | **CHOP** | Trim, loop, chop a sample to pads, waveform view. |
| MIDI | **PADS** | Pad settings: sample, tune, level, pan, filter, envelope, mute group, output, FX send. |
| DISK | **DISK** | Load/save kits, sequences, songs, whole projects. Folder-style browser. |
| MASTER TUNE | **STEP** | Step editor / event list for the current track. |
| DRUM | **SONG** | Chain sequences into a song. Convert a song to one long sequence. |
| UTILITY | **SETUP** | MIDI controller setup, sync (MIDI clock / SMPTE), metronome, outputs, CLASSIC entry. |

---

## The MIDI controller

All playing comes in over MIDI IN, from any pad controller (MPD, MPK, an MPC used as a controller and so on).

| Feature | How it works |
|---|---|
| **Pad notes** | Presets: **MPC CLASSIC** (default, for the MPC Key 37) and **CHROMATIC** 36–51 (MPD/MPK). 4 banks = 64 pads. **LEARN**: in SETUP press LEARN, then hit your pads 1–16 in order. Saved with the setup. |
| **Banks** | Either the controller's own bank buttons (other notes → pads 17–64), or a **BANK** soft key / footswitch that shifts the same 16 notes to bank A/B/C/D. |
| **Velocity** | Per controller: curve soft / linear / hard, or **FULL LEVEL** (always 127, the MPC button). Per pad: velocity → level and velocity → filter amounts. |
| **Pad follow** | The last pad you hit becomes the selected pad on PADS, CHOP and STEP. Hit a pad, then edit it. |
| **Knobs/faders (CC)** | **CC LEARN**: move a controller knob, then select a field (pad tune, filter, decay, level, swing, tempo…). It controls the last hit pad live. Recorded into the sequence on request (filter sweeps). |
| **Transport** | Learn controller buttons (notes or CCs) for PLAY, STOP, REC, OVERDUB, TAP, NOTE REPEAT, ERASE. MIDI Start/Stop/Continue and MMC from the controller also work. |
| **Aftertouch** | Optional: note repeat rate or filter from channel/poly pressure. |
| **MIDI tracks** | Notes for tracks set to MIDI are sent to MIDI OUT (external synths); the controller's notes go thru to the selected MIDI track's channel. |

The S1100 has **one MIDI IN**. To use a controller and an external clock (DAW, drum machine)
at the same time, use a MIDI merge box, or let the S1100 be the clock master (MIDI clock OUT).

### Controller profile: Akai MPC Key 37 (default)

Connection: **MPC Key 37 MIDI OUT (DIN) → S1100 MIDI IN**. Optional: S1100 MIDI OUT → MPC Key MIDI IN
(for MIDI tracks played on the MPC's synths, or S1100 as clock master).

| MPC Key 37 | Channel (default) | What it does on the S1100 |
|---|---|---|
| **16 pads** | 10 | Play the current kit. Pad notes from the **MPC CLASSIC** preset (A01–A16 = 37 36 42 82 40 38 46 44 48 47 45 43 49 55 51 53), or LEARN. MPC pad banks A–D → S1100 banks A–D. |
| **37 keys** | 1 | **KEYS mode**: play the last hit pad *chromatically*, middle C = the sample's original pitch. For melodic chops, stabs, bass from a chopped note. |
| **Q-Link knobs** | 10 | CC LEARN to pad tune / filter / decay / level, swing, tempo. |
| **Pitch bend / mod** | 1 | Pitch bend and filter on KEYS mode notes. |
| **Play / Stop** | — | The MPC's transport sends **MIDI Start/Stop + clock**. With SYNC = MIDI, the S1100 sequencer follows the MPC's play/stop and tempo. Everything comes down one cable, so no merge box is needed. With SYNC = internal, the S1100 is the master and the MPC's play buttons are ignored. |

Set up on the MPC: a MIDI track (or two: pads and keys) with output **MIDI Out (DIN)** on the
channels above, and MIDI clock / transport sending switched on in the MPC's sync preferences.
(The exact menu names differ between MPC OS versions; check once it's set up. Akai notes that in
USB controller mode the transport buttons don't send MIDI, so use the MPC's MIDI clock/sync output for transport.)

The pad-note preset and channels are assumptions until tested with your unit; LEARN covers any difference.

---

## Screens (40 × 8 text on the 240 × 64 graphic LCD)

Mock-ups are 40 columns wide. `▮` marks the cursor field; the bottom line is soft keys.

### MAIN (home)
```
MAIN  SEQ 01 THE.WALK         PLAY   ▶
BPM 091.5  SWING 58%  BAR 003.2.48/004
TRK 01 DRUMS   KIT 01 BREAKS.A  BANK A
TRK 02 CHOPS   KIT 02 STRINGS
TRK 03 BASS    MIDI CH 02
QNT 1/16  NREP off  CNT-IN 1  CLICK on
LEN 004 bars   ▓▓▓▓▓▓▓▓░░░░░░░░ pads hit
[PLAY][STOP][REC][ODUB][NREP][TAP][TRK][SEQ]
```
- F1–F4 PLAY / STOP / REC / OVERDUB (as on an MPC; REC starts at bar 1 with count-in).
- **Hold pads while ERASE** (F-key held + pad) removes that pad's notes in real time.
- **NOTE REPEAT**: hold F5 and a pad. DATA knob sets the rate (1/4 … 1/32, triplets).
- **TAP** sets the tempo; double-tap F6 + DATA changes BPM in 0.1 steps.
- Track rows show mute state; pressing a track row's soft key mutes/unmutes it while playing.

### SAMPLE (recording)
```
SAMPLE  → SMP027  (next free name)  MONO
SOURCE analog   RATE 44.1k  MODE clean
TRIG   level -32dB  PRE-REC 50ms
LEN    auto (stop on ENT)  CRATE off
IN ▕████████████▌     ▏ -6dB peak  -2dB
MEM free 28.4MB = 05:37 mono / 02:48 st
AFTER: trim silence, normalise, to pad 01
[ARM ][MON ][MODE][CRAT][RSMP][ ][ ][KEEP]
```
- **Arm → record when the input passes the threshold → ENT stops.** Pre-roll keeps the attack.
- **AFTER** chain (each can be turned off): trim silence at both ends, normalise,
  give it the next free name, put it on the next free pad of the current kit.
- **MODE** (vintage character, applied when recording finishes, keeps 44.1 kHz playback so the pitch is unchanged):
  `clean` · `S950` 12-bit/40 kHz · `SP-1200` 12-bit/26.04 kHz, no filter ·
  `MPC60` 12-bit/40 kHz · `S900` 12-bit/40 kHz · `custom` bits/rate.
- **RSMP** resample: record the S1100's own output. First version records with an
  output-to-input cable (EFFECT SEND or a MIX OUT into REC IN); an internal digital path is a research item.
- **CRATE** mode: one long recording (minutes) into a crate buffer, then **MARK** good parts
  while listening back; each mark becomes its own named sample. The way you would dig through a
  stack of records in one sitting.

### CHOP
```
CHOP  SMP027 BREAK.FUNKY   2.000 s  91.5
 ▁▃█▆▃▂▁ ▂█▅▂▁ ▄█▆▃▁▁ ▂█▅▂ ▁▃█▆▃▂ ▂█▅▃▁
 |1      |2     |3     |4    |5     |6
START 000000  END 088200  LOOP off
BARS 1   BEATS 4  → BPM 120.0 (from len)
SLICE by grid 1/16   SLICES 16  → pads
[ZOOM][MARK][GRID][TRAN][AUDI][STR ][KIT][DO]
```
- **Waveform view** (graphic mode on the LC7981). Zoom in and out with the DATA knob on the ZOOM field.
- **Set BPM from length**: tell it how many bars the loop is and it works out the tempo (or the other way round).
- **Slice**: by **grid** (1/4, 1/8, 1/16 of the bars), by **transient** (threshold), or by
  **MARK** while playing back (tap MARK on each hit).
- **AUDI**: press a pad to hear that slice before committing.
- **STR** time-stretch the whole sample to the current sequence BPM (uses Akai's own time-stretch).
- **KIT → DO**: slices go to pads 1–16 of a new or current bank. Option: also write a
  sequence that plays the slices in order, so the original loop plays back and you can rearrange it.
- Slices are made as **regions of one sample** where possible (saves memory) and become
  real samples only when you edit one destructively.

### PADS
```
PADS  KIT 01 BREAKS.A  BANK A  PAD 05
SMP  SMP027.S05      NOTE 041
TUNE +00.00  LEVEL 85  PAN  M  OUT 3
FILT 99  RES 0  ENV attack 00 decay 20
MODE one-shot  MUTE GRP 1  POLY 4
FX send 00   VEL→LEVEL 50  VEL→FILT 0
16 LEVELS: off
[SMP ][TUNE][ENV ][FILT][OUT ][MUTE][16LV][CPY]
```
- **Press a pad to select it** (and hear it). All settings are per pad.
- **One-shot / note-on**: one-shot plays the whole slice; note-on stops when released.
- **Mute groups** (hi-hat choke, or a chopped phrase that cuts itself off).
- **OUT**: stereo mix or any of the **8 individual outputs** (mix on a desk, as on an SP-1200 or MPC60).
- **16 LEVELS** (MPC feature): spread one pad across all 16 pads by tune, level, filter or decay.
  Ideal for playing a chopped stab melodically.
- **CPY**: copy pad settings to another pad, or to the whole bank.

### STEP (event editor)
```
STEP  SEQ 01  TRK 01 DRUMS     BAR 003
003.1.00  PAD 01 KICK      v112  dur 24
003.1.48  PAD 03 HAT.CL    v 90  dur 12
003.2.00  PAD 02 SNARE     v120  dur 24
003.2.48  PAD 03 HAT.CL    v 74  dur 12
003.3.00▮ PAD 01 KICK      v110  dur 24
003.3.24  ─ empty ─
[<BAR][BAR>][INS ][DEL ][COPY][QNT ][VEL ][PLAY]
```
- Move with CURSOR; change with DATA; press a pad to insert it at the cursor position.
- Bar copy / insert / delete, per-track quantise, velocity scale.

### SONG
```
SONG 01 SINCE.I.LEFT      BPM from seq
STEP 01  SEQ 01 THE.WALK      × 4
STEP 02  SEQ 02 BREAKDOWN     × 2
STEP 03▮ SEQ 01 THE.WALK      × 4
STEP 04  SEQ 03 OUTRO         × 1
STEP 05  ── end ──  (loop to step 01)
[PLAY][STOP][INS ][DEL ][<   ][   >][CONV][  ]
```
- **CONV** turns the song into one long sequence for final edits (MPC-style "song to seq").

### DISK
```
DISK  floppy HD   vol MOSURA.BEATS
▮ THE.WALK    project   kit+seq+song
  BREAKS.A    kit       16 pads
  BREAK.FUNKY sample    2.0s
  DIGS.0412   crate     4:12
free 0.6MB
[LOAD][SAVE][PROJ][DEL ][NAME][FMT ][SCSI][  ]
```
- **Project** = everything needed for a beat (samples, kits, sequences, song) saved in one step.
- Shows only beatmaking file types by default; other Akai types appear in CLASSIC.
- Floppy, Gotek, SCSI hard disk / ZuluSCSI, CD-ROM (sample libraries) all through Akai's disk code.

### SETUP
MIDI in/out channels, pad note map, MIDI clock in/out, SMPTE sync and frame rate,
metronome (sound, level, output, count-in), footswitch roles, pad-grid behaviour,
CLASSIC mode entry.

---

## The sequencer (MPC-style feel)

| Feature | Value |
|---|---|
| Resolution | 96 PPQN (MPC60/3000 standard) |
| Sequences | 99, 1–99 bars each, time signature per sequence |
| Tracks | up to 32 per sequence; type DRUM (kit) or MIDI (channel 1–16 out) |
| Recording | real-time loop recording with overdub, count-in, erase while playing |
| Timing correct | off, 1/8, 1/8T, 1/16, 1/16T, 1/32, 1/32T, with **swing 50–75%** |
| Note repeat | same rates as timing correct, swing applies |
| Tempo | 30.0–300.0 BPM, tap tempo, tempo per sequence |
| Sync | internal, MIDI clock in (slave), MIDI clock out (master), SMPTE in via the S1100 SMPTE board |
| Memory | target ≥ 50,000 notes in CPU RAM (exact amount once we know how much of the 512 KB the OS leaves free) |

**Timing engine:** a V50 timer interrupt at the tick rate (96 PPQN at the current BPM)
plays events through Akai's own voice-start routine. That is the same path MIDI notes take, so
playback sounds exactly like playing the kit from MIDI. MIDI clock is sent and received in the same interrupt.

**Feel:** swing delays every second 1/16 (or 1/8) by the swing percentage,
the way the MPC60 does it. Once we know more, compare against real MPC60/3000 recordings and
match the timing to the tick.

---

## Vintage character, three layers

1. **On recording or resampling** (CPU processing, definitely possible): bit depth and sample rate
   reduction without anti-alias filtering, presets for S900 / S950 / SP-1200 / MPC60.
2. **Live crunch on pitch-shifting** (hardware option): burn new coefficient EPROMs
   (IC12/IC13, standard 27C512) with "drop-sample" tables. Every pad played away from its
   original pitch then aliases like an SP-1200 or S900. A toggle switch with a double-size EPROM could
   switch between clean and crunchy.
3. **Real-time effects on the DSP56001**: bit-crusher, sample-rate reducer, vinyl/tape
   saturation, plus the stock delays and choruses. Per-pad FX send.

---

## What gets hidden (still reachable in CLASSIC)

- Velocity crossfade layers, positional crossfade, keyspans and multi-keygroup editing
- Per-keygroup LFOs and modulation matrix detail (the pad filter and envelope cover most uses)
- Cue lists (Q-list), take lists, S900 file conversion screens
- Loop crossfading / loop finder (useful, but kept in CLASSIC for now)

---

## Build order (what makes beats soonest)

| Release | Contents | Can you make a beat? |
|---|---|---|
| **0.1 "boots"** | MosuraOS boot screen, version, CLASSIC = everything stock | No – proves the toolchain |
| **0.2 "pads"** | MIDI pad map + LEARN, velocity curves, pad follow, PADS page, kits = programs | Finger-drum live from the controller |
| **0.3 "loop"** | MAIN page, 1 sequence, real-time record, quantise, swing, metronome | **Yes**, first beats |
| **0.4 "chop"** | CHOP page: grid/MARK slicing to pads, BPM from length | Yes, chop breaks |
| **0.5 "dig"** | SAMPLE page: threshold record, auto trim/normalise, vintage modes | The full dig → chop → beat loop |
| **0.6 "arrange"** | 99 sequences, 32 tracks, MIDI tracks, STEP editor, note repeat, SONG | Full tracks |
| **0.7 "sync"** | MIDI clock in/out, SMPTE sync, footswitches | Studio integration |
| 0.8+ | Waveform view, crate mode, transient slicing, 16 levels, DSP effects, coefficient-ROM crunch | Polish and character |

## Technical approach (short)

- New pages are drawn with **our own UI layer**, drawing on the LCD directly (LC7981, port 0x6000)
  and reading the panel itself (8255, port 0x2000). Pads and controller knobs come
  through Akai's MIDI receive buffer (INT 09h, `0:0200`), which MosuraOS reads before Akai's
  MIDI handler does. Under it, **Akai's routines** do the hard parts:
  voice start/stop, sample memory, disk and SCSI, time-stretch, DSP setup.
- The OS runs from RAM and loads from floppy or Gotek, so we're not limited to the ROM size
  while developing (512 KB CPU RAM; the stock OS uses about 128 KB of code).
- What we need to find in the stock OS first (progress in `docs/OSMAP.md`): main loop and page
  dispatch, key/encoder input, LCD drawing, MIDI input handler, voice-start routine,
  program/keygroup/sample structures in memory, timer interrupt use.
