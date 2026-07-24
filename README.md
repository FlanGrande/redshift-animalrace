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

## Source layout

- `project.json`: solution metadata, cover palette, agent list, and output path.
- `agents/00-GM.exa`: game state, input, racers, odds, scoring, results, and
  local race messaging.
- `agents/01-UI.exa`: persistent `BANK` and `ODDS` labels.
- `agents/02-AU.exa`: persistent four-channel audio controller in host `801`.
- `sprites/00-GM.txt`: selection arrow inherited by game-manager clones.
- `sprites/01-UI.txt`: blank canvas for built-in font characters.
- `sprites/02-AU.txt`: blank audio-controller sprite.

Three EXAs are stored initially. `GM` moves to the input host and uses local
messaging with a single-reader protocol: racers only send odds and finish
messages, while `GM` alone receives them. `UI` creates the fixed headings. `AU`
moves to the sound host through `LINK 801` and receives isolated global audio
commands. Runtime host occupancy remains within Redshift capacity.
