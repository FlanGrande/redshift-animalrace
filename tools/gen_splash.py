#!/usr/bin/env python3
"""Generate the isometric Flan splash across agents 03-BT.exa and 01-UI.exa."""

from __future__ import annotations

import math
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parents[1]
BT = PROJECT / "agents/03-BT.exa"
UI = PROJECT / "agents/01-UI.exa"
sys.path.insert(0, str(ROOT / "tools"))

from redshift_compile import OFFICIAL_OUTPUT_LINE_LIMIT, expanded_source_line_count

W, H = 120, 100
ROWS = [3, 13, 23, 33, 43, 53, 63]
COLS = [20, 30, 40, 50, 60, 70, 80, 90]
CORE_SLOTS = 14
INPUT_SLOTS = 19
SOUND_ART_MAX = 10

BOOT_SOUND = """MARK BOOT_SOUND
COPY 300 GP
LINK 801
COPY 48 #TRI0
@REP 4
WAIT
@END
COPY 60 #SQR0
COPY 64 #SQR1
@REP 4
WAIT
@END
COPY 67 #SQR0
COPY 72 #SQR1
COPY 55 #TRI0
@REP 6
WAIT
@END
COPY 72 #SQR0
COPY 76 #SQR1
COPY 60 #TRI0
@REP 8
WAIT
@END
COPY 76 #SQR0
COPY 79 #SQR1
COPY 64 #TRI0
@REP 8
WAIT
@END
COPY 84 #SQR0
COPY 72 #SQR1
COPY 67 #TRI0
COPY 35 #NSE0
@REP 6
WAIT
@END
COPY 0 #SQR0
COPY 0 #SQR1
COPY 0 #TRI0
COPY 0 #NSE0
HALT
"""

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
    img = [[0] * W for _ in range(H)]

    def ell(x: float, y: float, cx: float, cy: float, rx: float, ry: float) -> float:
        return ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2

    # Plate: isometric diamond, 2:1 slope, checkered rim band.
    for y in range(H):
        for x in range(W):
            d = 19.0 - (abs(x - 60) / 2 + abs(y - 51))
            if d >= 0:
                if d < 1.5:
                    img[y][x] = 1 if (x + y) % 2 == 0 else 0
                else:
                    img[y][x] = 1

    # Caramel puddle ring hugging the flan base.
    for y in range(H):
        for x in range(W):
            v = ell(x, y, 60, 50, 23, 6)
            if v <= 1.0:
                if v > 0.74:
                    img[y][x] = 1 if (x % 4 == 0 and y % 2 == 1) else 0
                else:
                    img[y][x] = 0

    # Custard body: gentle taper, rounded bottom bulge, right shading.
    for y in range(13, 56):
        t = (y - 13) / 39
        xl = 42 - 2 * t
        xr = 78 + 2 * t
        for x in range(int(math.ceil(xl)), int(math.floor(xr)) + 1):
            if y <= 47:
                inside = True
            else:
                u = (x - 60) / 20
                inside = abs(u) <= 1 and y <= 47 + 5 * math.sqrt(max(0.0, 1 - u * u))
            if not inside:
                continue
            if x >= xr - 5:
                img[y][x] = 1 if (x + y) % 2 == 0 else 0
            else:
                img[y][x] = 1

    # Caramel cap: dark 25% fill, bright rim, top-left glint.
    for y in range(H):
        for x in range(W):
            v = ell(x, y, 60, 15, 24, 11)
            if v <= 1.0:
                if v > 0.80:
                    img[y][x] = 1
                else:
                    img[y][x] = 1 if (x % 2 == 0 and y % 2 == 0) else 0
    for y in range(H):
        for x in range(W):
            if ell(x, y, 48, 9, 5, 2.2) <= 1.0:
                img[y][x] = 1

    # Face: round eyes plus open smiling mouth.
    for y in range(H):
        for x in range(W):
            if ell(x, y, 52, 33, 2.1, 3.0) <= 1.0 or ell(x, y, 67, 33, 2.1, 3.0) <= 1.0:
                img[y][x] = 0
            if ell(x, y, 59.5, 42, 5.6, 4.6) <= 1.0:
                img[y][x] = 0
    return img


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


def dispatch_and_routines(patterns, routine_fn, skip_zero) -> list[str]:
    out = ["MARK LOGO_TILE", "COPY 0 GZ"]
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
    boot_sound = BOOT_SOUND
    text_tail = TEXT_TAIL

    img = build_bitmap()
    tiles = []
    for gy in ROWS:
        for gx in COLS:
            pattern = tile_pattern(img, gx, gy)
            if any(pattern):
                tiles.append((gx, gy, pattern))

    # Cheap-from-blank tiles go to UI (blank sprite); the rest stay with BT (full sprite).
    ui_tiles = [t for t in tiles if len(sets(t[2])) <= 55]
    bt_tiles = [t for t in tiles if t not in ui_tiles]

    bt_core = bt_tiles[:CORE_SLOTS]
    bt_input: list = []
    bt_sound = bt_tiles[CORE_SLOTS:]
    ui_input = ui_tiles[:INPUT_SLOTS]
    ui_sound = ui_tiles[INPUT_SLOTS:]
    if len(bt_sound) + len(ui_sound) > SOUND_ART_MAX:
        raise SystemExit("sound host overflow")

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
    clear_sound = len(bt_sound) + len(ui_sound) + 6

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
    out.append("COPY 300 GP")
    for chunk in (
        "REPL TEXT_FL",
        "COPY 43 T",
        "REPL TEXT_AN",
        "REPL TEXT_GR",
        "COPY 63 T",
        "REPL TEXT_AN2",
        "REPL TEXT_DOT_D",
        "REPL TEXT_E",
    ):
        out.append(chunk)
        if chunk.startswith("REPL") and chunk != "REPL TEXT_E":
            out.append("@REP 3")
            out.append("WAIT")
            out.append("@END")
    out.append("")
    out.append("COPY 65 X")
    out.append("MARK BOOT_HOLD")
    out.append("WAIT")
    out.append("SUBI X 1 X")
    out.append("TEST X > 0")
    out.append("TJMP BOOT_HOLD")
    out.append("")
    out.append("; Clear local workers in each host before waking game EXAs.")
    out.append(f"COPY {clear_sound} X")
    out.append("MARK CLEAR_SOUND")
    out.append("COPY 1 M")
    out.append("SUBI X 1 X")
    out.append("TEST X > 0")
    out.append("TJMP CLEAR_SOUND")
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
    out.append(text_tail)
    out.append("JUMP LOGO_HOLD")
    out.append("")
    bt_text = "\n".join(out)

    # TEXT_AN is replicated twice with different T; keep single label.
    bt_text = bt_text.replace("REPL TEXT_AN2", "REPL TEXT_AN")

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
    ui.append("MODE")
    ui.append(UI_TAIL.rstrip())
    ui.append("")
    ui += dispatch_and_routines(ui_patterns, sets, skip_zero=False)
    ui.append("")
    ui_text = "\n".join(ui)

    for name, text in (("BT", bt_text), ("UI", ui_text)):
        expanded = expanded_source_line_count(text)
        print(f"{name}: raw={text.count(chr(10))} expanded={expanded}")
        if expanded > OFFICIAL_OUTPUT_LINE_LIMIT:
            raise SystemExit(f"{name} expanded {expanded} exceeds limit")
    print(
        f"tiles={len(tiles)} bt_core={len(bt_core)} bt_sound={len(bt_sound)} "
        f"ui_input={len(ui_input)} ui_sound={len(ui_sound)} "
        f"bt_patterns={len(bt_patterns)} ui_patterns={len(ui_patterns)} "
        f"clears=({clear_core},{clear_input},{clear_sound})"
    )
    BT.write_text(bt_text + "\n" if not bt_text.endswith("\n") else bt_text, encoding="utf-8")
    UI.write_text(ui_text + "\n" if not ui_text.endswith("\n") else ui_text, encoding="utf-8")


if __name__ == "__main__":
    main()
