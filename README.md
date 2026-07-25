# Animal Race for TEC Redshift

This is an independent EXA-language adaptation of Brian Astle's 1978
`VIP Animal Race` for the RCA COSMAC VIP. It preserves the original betting,
odds, bankroll, and autonomous-race rules while using Redshift's 120x100 screen,
D-pad, Start button, sprites, frame synchronization, and audio hardware.

The original CHIP-8 ROM and hexadecimal reference listing remain at
[`animal_race.ch8`](../../animal_race.ch8) and
[`animal_race_source.txt`](../../animal_race_source.txt). The Redshift source
does not execute or embed that CHIP-8 program.

## Play

- Up/down moves the arrow between five racers.
- Start confirms the selected racer.
- Left/right changes the wager from `$1` through `$9`; it cannot exceed the
  current bank.
- Start confirms the wager and starts the countdown.
- Start begins a new randomized round after `WIN` or `LOSE`.

Selection and wager changes chirp through the square-wave channels. The
countdown, running animals, wins, and losses use distinct square, triangle, and
noise effects.

Startup assembles an isometric Flan pudding mascot in place, swings its upper
tiles wider than its lower tiles, reveals the `FlanGran.de` wordmark one piece
at a time, and gives the mascot a sparkling wink. A four-channel boot jingle
plays before game EXAs enter their input, UI, and audio hosts.
`sprites/splash.txt` is the complete splash source image. During every build,
`tools/gen_splash.py` slices it into EXA tiles and rewrites the generated
sections in all four agent files.

`BANK` appears at the top-left. Each lane's odds appear under `ODDS` on the
right. During wager selection, the wager digit appears just left of the chosen
lane's odds.

The player begins with `$10`. A losing bet subtracts the wager. A winning bet
adds `wager * odds`. Reaching `$256` displays `YOUWIN`; reaching `$0` displays
`NOCASH`.

## Race rules

Each animal receives a random start offset from `0` through `3`. Odds use the
original formula:

```text
odds = 6 - 2 * start + RAND(1, 2) + RAND(0, 1)
```

This produces odds from `7:1` through `9:1` at the back and `1:1` through
`3:1` at the front. Racers advance one pixel after independent random delays.
The first finish message received wins the round.

## Build

From repository root:

```sh
python3 tools/redshift_compile.py homebrew/animal-race
```

Output is [`Animal Race.tec.png`](Animal%20Race.tec.png). Drag it into the
official TEC Redshift Player or load it with a compatible Redshift emulator.

The compiler always decodes its output and rejects a cartridge that does not
round-trip to the exact project sources and sprites.

## Editing the splash

Edit `sprites/splash.txt` directly. It must contain exactly 100 rows of 120
characters. `#` is a lit pixel, `.` is an unlit pixel, and the top-left
character is display coordinate `(0, 0)`. The file represents the entire
Redshift display, including the `FlanGran.de` wordmark.

For a minimal graphical editor, install the repository requirements and run:

```sh
python3 homebrew/animal-race/sprites/splash_editor.py
```

Its Save and Load buttons use memory only. Export overwrites `splash.txt`.

The boot jingle uses `audio/boot_music.txt`. Each row is one 30Hz step:
`duration sqr0 sqr1 tri0 nse0`, with channel values from 0 (off) through 99.
Edit it graphically with:

```sh
python3 homebrew/animal-race/audio/boot_music_editor.py
```

The composer has RAM-only Save/Load, step editing/reordering, Export, and a
local preview matching Redshift's pitch and waveform rules.

The normal build command runs `tools/gen_splash.py` automatically through the
`prebuild` entry in `project.json`. The generator splits the canvas on the
screen's 10x10 grid, deduplicates tile patterns, and assigns nonempty tiles to
the available core, input, and sound-host EXAs. It rejects invalid dimensions,
characters, host overflow, or generated EXAs above the official 1,000-line
limit.

## Source layout

- `project.json`: solution metadata, cover palette, agent list, and output path.
- `agents/00-GM.exa`: generated splash tile, game state, racers, scoring, and
  local race messaging.
- `agents/01-UI.exa`: generated splash workers, then persistent `BANK` and
  `ODDS` labels.
- `agents/02-AU.exa`: generated splash tile and persistent audio controller.
- `agents/03-BT.exa`: generated splash workers, boot jingle, and startup sync.
- `sprites/00-GM.txt`: selection arrow inherited by game-manager clones.
- `sprites/01-UI.txt`: blank canvas for built-in font characters.
- `sprites/02-AU.txt`: full tile template used by the animated eye.
- `sprites/03-BT.txt`: blank canvas used to construct logo tiles.
- `sprites/splash.txt`: editable 120x100 source image for the complete splash.
- `sprites/splash_editor.py`: ImGui splash editor and exact-size preview.
- `audio/boot_music.txt`: editable four-channel startup score.
- `audio/boot_music_editor.py`: ImGui score editor and local audio preview.
- `tools/gen_splash.py`: compile-time canvas/music EXA source generator.

Four EXAs are stored initially. `BT` first reveals and clears the boot logo,
then wakes the three game EXAs. `GM` moves to the input host and uses local
messaging with a single-reader protocol: racers only send odds and finish
messages, while `GM` alone receives them. `UI` creates the fixed headings. `AU`
moves to the sound host through `LINK 801` and receives isolated global audio
commands. Runtime host occupancy remains within Redshift capacity.
