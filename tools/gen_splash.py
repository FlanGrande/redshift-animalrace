#!/usr/bin/env python3
"""Generate Redshift EXA splash workers and boot music."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parents[1]
BT = PROJECT / "agents/03-BT.exa"
UI = PROJECT / "agents/01-UI.exa"
AU = PROJECT / "agents/02-AU.exa"
GM = PROJECT / "agents/00-GM.exa"
GM_SPRITE = PROJECT / "sprites/00-GM.txt"
CANVAS = PROJECT / "sprites/splash.txt"
BOOT_MUSIC = PROJECT / "audio/boot_music.txt"
sys.path.insert(0, str(ROOT / "tools"))

from redshift_compile import OFFICIAL_OUTPUT_LINE_LIMIT, expanded_source_line_count

W, H = 120, 100
ROWS = range(0, H, 10)
COLS = range(0, W, 10)
CORE_SLOTS = 14
INPUT_SLOTS = 19
SOUND_ART_MAX = 18
AUX_SLOTS = 2

def build_boot_sound() -> str:
    try:
        lines = BOOT_MUSIC.read_text(encoding="ascii").splitlines()
    except (OSError, UnicodeError) as error:
        raise SystemExit(f"cannot read boot music {BOOT_MUSIC}: {error}") from error

    steps: list[tuple[int, int, int, int, int]] = []
    for line_number, line in enumerate(lines, 1):
        content = line.split("#", 1)[0].strip()
        if not content:
            continue
        fields = content.split()
        if len(fields) != 5:
            raise SystemExit(
                f"boot music line {line_number} must contain: "
                "duration sqr0 sqr1 tri0 nse0"
            )
        try:
            step = tuple(int(field) for field in fields)
        except ValueError as error:
            raise SystemExit(f"boot music line {line_number} is not numeric") from error
        duration, *channels = step
        if not 1 <= duration <= 64:
            raise SystemExit(
                f"boot music line {line_number} duration must be 1..64"
            )
        if any(not 0 <= value <= 99 for value in channels):
            raise SystemExit(
                f"boot music line {line_number} channels must be 0..99"
            )
        steps.append(step)
    if not steps:
        raise SystemExit("boot music must contain at least one step")

    registers = ("#SQR0", "#SQR1", "#TRI0", "#NSE0")
    previous = [0, 0, 0, 0]
    output = ["MARK BOOT_SOUND", "COPY 300 GP", "LINK 801"]
    for duration, *channels in steps:
        for index, value in enumerate(channels):
            if value != previous[index]:
                output.append(f"COPY {value} {registers[index]}")
                previous[index] = value
        output.extend((f"@REP {duration}", "WAIT", "@END"))
    for index, value in enumerate(previous):
        if value:
            output.append(f"COPY 0 {registers[index]}")
    output.append("HALT")
    return "\n".join(output)

TEXT_TAIL = """MARK TEXT_FL
COPY 33 GX
COPY 82 GY
COPY 101 GP
COPY 111 GP
COPY 121 GP
COPY 131 GP
COPY 102 GP
COPY 103 GP
COPY 113 GP
COPY 123 GP
COPY 104 GP
COPY 105 GP
COPY 106 GP
COPY 107 GP
COPY 151 GP
COPY 152 GP
COPY 153 GP
COPY 154 GP
COPY 155 GP
COPY 156 GP
COPY 157 GP
COPY 167 GP
COPY 177 GP
JUMP LOGO_HOLD

MARK TEXT_AN
COPY T GX
COPY 82 GY
COPY 112 GP
COPY 122 GP
COPY 133 GP
COPY 114 GP
COPY 124 GP
COPY 134 GP
COPY 105 GP
COPY 135 GP
COPY 106 GP
COPY 136 GP
COPY 117 GP
COPY 127 GP
COPY 137 GP
COPY 153 GP
COPY 163 GP
COPY 173 GP
COPY 154 GP
COPY 184 GP
COPY 155 GP
COPY 185 GP
COPY 156 GP
COPY 186 GP
COPY 157 GP
COPY 187 GP
JUMP LOGO_HOLD

MARK TEXT_GR
COPY 53 GX
COPY 82 GY
COPY 111 GP
COPY 121 GP
COPY 131 GP
COPY 102 GP
COPY 103 GP
COPY 104 GP
COPY 124 GP
COPY 134 GP
COPY 105 GP
COPY 135 GP
COPY 106 GP
COPY 136 GP
COPY 117 GP
COPY 127 GP
COPY 137 GP
COPY 153 GP
COPY 173 GP
COPY 183 GP
COPY 154 GP
COPY 164 GP
COPY 155 GP
COPY 156 GP
COPY 157 GP
JUMP LOGO_HOLD

MARK TEXT_DOT_D
COPY 73 GX
COPY 82 GY
COPY 117 GP
COPY 127 GP
COPY 181 GP
COPY 182 GP
COPY 163 GP
COPY 173 GP
COPY 183 GP
COPY 154 GP
COPY 184 GP
COPY 155 GP
COPY 185 GP
COPY 156 GP
COPY 186 GP
COPY 167 GP
COPY 177 GP
COPY 187 GP
JUMP LOGO_HOLD

MARK TEXT_E
COPY 83 GX
COPY 82 GY
COPY 113 GP
COPY 123 GP
COPY 104 GP
COPY 134 GP
COPY 105 GP
COPY 115 GP
COPY 125 GP
COPY 135 GP
COPY 106 GP
COPY 117 GP
COPY 127 GP
COPY 137 GP
"""

UI_HEAD = "; Persistent BANK and ODDS headings after the splash plate."
UI_TAIL = """COPY M T
COPY 300 GP
REPL BANK_B
REPL BANK_A
REPL BANK_N
REPL BANK_K
REPL ODDS_O
REPL ODDS_D1
REPL ODDS_D2
REPL ODDS_S
HALT

MARK BANK_B
COPY 302 GP
COPY 0 GX
COPY 0 GY
JUMP HOLD

MARK BANK_A
COPY 301 GP
COPY 10 GX
COPY 0 GY
JUMP HOLD

MARK BANK_N
COPY 314 GP
COPY 20 GX
COPY 0 GY
JUMP HOLD

MARK BANK_K
COPY 311 GP
COPY 30 GX
COPY 0 GY
JUMP HOLD

MARK ODDS_O
COPY 315 GP
COPY 75 GX
COPY 0 GY
JUMP HOLD

MARK ODDS_D1
COPY 304 GP
COPY 85 GX
COPY 0 GY
JUMP HOLD

MARK ODDS_D2
COPY 304 GP
COPY 95 GX
COPY 0 GY
JUMP HOLD

MARK ODDS_S
COPY 319 GP
COPY 105 GX
COPY 0 GY

MARK HOLD
WAIT
JUMP HOLD
"""


def build_bitmap() -> list[list[int]]:
    try:
        rows = CANVAS.read_text(encoding="ascii").splitlines()
    except (OSError, UnicodeError) as error:
        raise SystemExit(f"cannot read splash canvas {CANVAS}: {error}") from error
    if len(rows) != H or any(len(row) != W for row in rows):
        widths = sorted({len(row) for row in rows})
        raise SystemExit(
            f"splash canvas must be exactly {W}x{H}; "
            f"got {len(rows)} rows with widths {widths}"
        )
    invalid = sorted({character for row in rows for character in row} - {".", "#"})
    if invalid:
        raise SystemExit(
            "splash canvas contains invalid characters: " + ", ".join(invalid)
        )
    return [[int(character == "#") for character in row] for row in rows]


def tile_pattern(img: list[list[int]], gx: int, gy: int) -> tuple[int, ...]:
    return tuple(
        img[gy + dy][gx + dx] if 0 <= gy + dy < H and 0 <= gx + dx < W else 0
        for dy in range(10)
        for dx in range(10)
    )


def sets(pattern: tuple[int, ...]) -> list[str]:
    return [f"COPY {100 + 10 * (i % 10) + i // 10} GP" for i, v in enumerate(pattern) if v]


def clears(pattern: tuple[int, ...]) -> list[str]:
    return [f"COPY {10 * (i % 10) + i // 10:03d} GP" for i, v in enumerate(pattern) if not v]


def bt_routine(pattern: tuple[int, ...]) -> list[str]:
    lit, dark = sets(pattern), clears(pattern)
    return ["COPY 300 GP"] + lit if len(lit) + 1 < len(dark) else dark


def spawn_lines(section, patterns, state) -> list[str]:
    lines = []
    for gx, gy, pattern in section:
        co = patterns.index(pattern)
        if co != state["co"]:
            lines.append(f"COPY {co} CO")
            state["co"] = co
        lines.append(f"COPY {gx} GX")
        if gy != state["gy"]:
            lines.append(f"COPY {gy} GY")
            state["gy"] = gy
        lines.append("REPL LOGO_TILE")
    return lines


def dispatch_and_routines(patterns, routine_fn, skip_zero, clear_first=False) -> list[str]:
    out = ["MARK LOGO_TILE", "COPY 0 GZ"]
    if clear_first:
        out.append("COPY 300 GP")
    if skip_zero:
        out.append("TEST CO = 0")
        out.append("TJMP LOGO_HOLD")
    start = 1 if skip_zero else 0
    for index in range(start, len(patterns) - 1):
        out.append(f"TEST CO = {index}")
        out.append(f"TJMP TILE_{index}")
    out.append(f"JUMP TILE_{len(patterns) - 1}")
    out.append("")
    for index in range(start, len(patterns)):
        out.append(f"MARK TILE_{index}")
        out += routine_fn(patterns[index])
        out.append("JUMP LOGO_HOLD")
        out.append("")
    out.append("MARK LOGO_HOLD")
    out.append("COPY M T")
    out.append("HALT")
    return out


def main() -> None:
    boot_sound = build_boot_sound()

    img = build_bitmap()
    tiles = []
    for gy in ROWS:
        for gx in COLS:
            pattern = tile_pattern(img, gx, gy)
            if any(pattern):
                tiles.append((gx, gy, pattern))

    # Cheap-from-blank tiles go to UI (blank sprite); the rest stay with BT (full sprite).
    ui_tiles = [t for t in tiles if len(sets(t[2])) <= 45]
    bt_tiles = [t for t in tiles if t not in ui_tiles]

    # UI itself carries the cheapest tile while waiting for the global boot wake.
    ui_parent = min(ui_tiles, key=lambda tile: len(sets(tile[2])))
    ui_tiles.remove(ui_parent)
    au_parent = min(ui_tiles, key=lambda tile: len(sets(tile[2])))
    ui_tiles.remove(au_parent)
    gm_parent = min(ui_tiles, key=lambda tile: len(sets(tile[2])))
    ui_tiles.remove(gm_parent)

    bt_core = bt_tiles[:CORE_SLOTS]
    bt_input: list = []
    bt_sound = bt_tiles[CORE_SLOTS:]
    bt_parent = min(bt_sound, key=lambda tile: len(sets(tile[2])))
    bt_sound.remove(bt_parent)
    ui_input = ui_tiles[:INPUT_SLOTS]
    ui_remaining = ui_tiles[INPUT_SLOTS:]
    sound_free = SOUND_ART_MAX - len(bt_sound)
    if sound_free < 0:
        raise SystemExit("too many dense tiles for the sound host")
    ui_sound = ui_remaining[:sound_free]
    ui_aux1 = ui_remaining[sound_free : sound_free + AUX_SLOTS]
    ui_aux2 = ui_remaining[sound_free + AUX_SLOTS : sound_free + AUX_SLOTS * 2]
    if len(ui_remaining) > sound_free + AUX_SLOTS * 2:
        raise SystemExit("splash needs more EXAs than Redshift hosts can hold")

    full = tuple([1] * 100)
    bt_patterns = [full]
    for _, _, p in bt_core + bt_sound:
        if p not in bt_patterns:
            bt_patterns.append(p)
    ui_patterns = []
    for _, _, p in ui_tiles:
        if p not in ui_patterns:
            ui_patterns.append(p)

    clear_core = len(bt_core)
    clear_input = len(ui_input)
    clear_sound = len(bt_sound) + len(ui_sound)
    clear_aux1 = len(ui_aux1)
    clear_aux2 = len(ui_aux2)

    # ---- BT ----
    out = []
    out.append("; FlanGran.de boot logo and startup jingle.")
    out.append("COPY -10 GX")
    out.append("COPY -10 GY")
    out.append("MODE")
    out.append("REPL BOOT_SOUND")
    out.append("")
    out.append(f"; Isometric flan body and plate: {len(bt_core)} core workers.")
    state = {"co": None, "gy": None}
    out += spawn_lines(bt_core, bt_patterns, state)
    out.append("@REP 6")
    out.append("WAIT")
    out.append("@END")
    out.append("")
    out.append(f"; Remaining rows: {len(bt_sound)} sound workers.")
    out.append("LINK 801")
    out += spawn_lines(bt_sound, bt_patterns, state)
    out.append("@REP 8")
    out.append("WAIT")
    out.append("@END")
    out.append("; BT parent carries one tile without consuming another host slot.")
    out.append("COPY 300 GP")
    out += sets(bt_parent[2])
    out.append(f"COPY {bt_parent[0]} GX")
    out.append(f"COPY {bt_parent[1]} GY")
    out.append("")
    out.append("COPY 65 X")
    out.append("MARK BOOT_HOLD")
    out.append("WAIT")
    out.append("SUBI X 1 X")
    out.append("TEST X > 0")
    out.append("TJMP BOOT_HOLD")
    out.append("COPY 300 GP")
    out.append("")
    out.append("; Clear local workers in each host before waking game EXAs.")
    out.append(f"COPY {clear_sound} X")
    out.append("MARK CLEAR_SOUND")
    out.append("COPY 1 M")
    out.append("SUBI X 1 X")
    out.append("TEST X > 0")
    out.append("TJMP CLEAR_SOUND")
    out.append("LINK -1")
    if clear_aux1:
        out.append("LINK 802")
        out.append(f"COPY {clear_aux1} X")
        out.append("MARK CLEAR_AUX1")
        out.append("COPY 1 M")
        out.append("SUBI X 1 X")
        out.append("TEST X > 0")
        out.append("TJMP CLEAR_AUX1")
        out.append("LINK -1")
    if clear_aux2:
        out.append("LINK 803")
        out.append(f"COPY {clear_aux2} X")
        out.append("MARK CLEAR_AUX2")
        out.append("COPY 1 M")
        out.append("SUBI X 1 X")
        out.append("TEST X > 0")
        out.append("TJMP CLEAR_AUX2")
        out.append("LINK -1")
    out.append("LINK 800")
    out.append(f"COPY {clear_input} X")
    out.append("MARK CLEAR_INPUT")
    out.append("COPY 1 M")
    out.append("SUBI X 1 X")
    out.append("TEST X > 0")
    out.append("TJMP CLEAR_INPUT")
    out.append("LINK -1")
    out.append(f"COPY {clear_core} X")
    out.append("MARK CLEAR_CORE")
    out.append("COPY 1 M")
    out.append("SUBI X 1 X")
    out.append("TEST X > 0")
    out.append("TJMP CLEAR_CORE")
    out.append("")
    out.append("; Return to global mode and wake GM, UI, and AU exactly once each.")
    out.append("MODE")
    out.append("@REP 3")
    out.append("COPY 1 M")
    out.append("@END")
    out.append("HALT")
    out.append("")
    out.append(boot_sound.rstrip())
    out.append("")
    out += dispatch_and_routines(bt_patterns, bt_routine, skip_zero=True)
    out.append("")
    bt_text = "\n".join(
        line for line in out if line and not line.startswith(";")
    )

    # ---- UI ----
    ui = []
    ui.append(UI_HEAD)
    ui.append(f"; Boot: draw {len(ui_input)} input plus {len(ui_sound)} sound splash tiles.")
    ui.append("MODE")
    ui.append("LINK 800")
    state = {"co": None, "gy": None}
    ui += spawn_lines(ui_input, ui_patterns, state)
    ui.append("LINK -1")
    if ui_sound:
        ui.append("LINK 801")
        ui += spawn_lines(ui_sound, ui_patterns, state)
        ui.append("LINK -1")
    if ui_aux1:
        ui.append("LINK 802")
        ui += spawn_lines(ui_aux1, ui_patterns, state)
        ui.append("LINK -1")
    if ui_aux2:
        ui.append("LINK 803")
        ui += spawn_lines(ui_aux2, ui_patterns, state)
        ui.append("LINK -1")
    ui.append("MODE")
    ui.append("; Draw the parent's own splash tile LAST so spawning cannot drag it.")
    ui += sets(ui_parent[2])
    ui.append(f"COPY {ui_parent[0]} GX")
    ui.append(f"COPY {ui_parent[1]} GY")
    ui.append(UI_TAIL.rstrip())
    ui.append("")
    ui += dispatch_and_routines(ui_patterns, sets, skip_zero=False, clear_first=True)
    ui.append("")
    ui_text = "\n".join(
        line for line in ui if line and not line.startswith(";")
    )

    au_source = AU.read_text(encoding="utf-8")
    au_start = "; BEGIN GENERATED SPLASH TILE\n"
    au_end = "; END GENERATED SPLASH TILE"
    start_index = au_source.index(au_start) + len(au_start)
    end_index = au_source.index(au_end)
    au_tile = "\n".join(
        sets(au_parent[2])
        + [f"COPY {au_parent[0]} GX", f"COPY {au_parent[1]} GY"]
    )
    au_source = au_source[:start_index] + au_tile + "\n" + au_source[end_index:]

    gm_source = GM.read_text(encoding="utf-8")
    gm_start = "; BEGIN GENERATED SPLASH TILE\n"
    gm_end = "; END GENERATED SPLASH TILE"
    start_index = gm_source.index(gm_start) + len(gm_start)
    end_index = gm_source.index(gm_end)
    gm_tile = "\n".join(
        ["COPY 300 GP"]
        + sets(gm_parent[2])
        + [f"COPY {gm_parent[0]} GX", f"COPY {gm_parent[1]} GY"]
    )
    gm_source = gm_source[:start_index] + gm_tile + "\n" + gm_source[end_index:]

    sprite_rows = GM_SPRITE.read_text(encoding="ascii").splitlines()
    gm_runtime_pattern = tuple(
        character == "#" for row in sprite_rows for character in row
    )
    restore_start = "; BEGIN GENERATED RUNTIME SPRITE\n"
    restore_end = "; END GENERATED RUNTIME SPRITE"
    start_index = gm_source.index(restore_start) + len(restore_start)
    end_index = gm_source.index(restore_end)
    gm_restore = "\n".join(["COPY 300 GP"] + sets(gm_runtime_pattern))
    gm_source = gm_source[:start_index] + gm_restore + "\n" + gm_source[end_index:]

    for name, text in (("BT", bt_text), ("UI", ui_text)):
        expanded = expanded_source_line_count(text)
        print(f"{name}: raw={text.count(chr(10))} expanded={expanded}")
        if expanded > OFFICIAL_OUTPUT_LINE_LIMIT:
            raise SystemExit(f"{name} expanded {expanded} exceeds limit")
    print(
        f"tiles={len(tiles)} bt_parent=1 bt_core={len(bt_core)} bt_sound={len(bt_sound)} "
        f"ui_parent=1 au_parent=1 gm_parent=1 "
        f"ui_input={len(ui_input)} ui_sound={len(ui_sound)} "
        f"ui_aux=({len(ui_aux1)},{len(ui_aux2)}) "
        f"bt_patterns={len(bt_patterns)} ui_patterns={len(ui_patterns)} "
        f"clears=({clear_core},{clear_input},{clear_sound},{clear_aux1},{clear_aux2})"
    )
    BT.write_text(bt_text + "\n" if not bt_text.endswith("\n") else bt_text, encoding="utf-8")
    UI.write_text(ui_text + "\n" if not ui_text.endswith("\n") else ui_text, encoding="utf-8")
    AU.write_text(au_source, encoding="utf-8")
    GM.write_text(gm_source, encoding="utf-8")


if __name__ == "__main__":
    main()
