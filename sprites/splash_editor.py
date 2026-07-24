#!/usr/bin/env python3
"""Tiny ImGui editor for the adjacent 120x100 splash.txt canvas."""

from __future__ import annotations

import math
import os
import sys
from pathlib import Path


WIDTH = 120
HEIGHT = 100
PREVIEW_GAP = 20
SPLASH_PATH = Path(__file__).with_name("splash.txt")


def load_splash() -> list[list[bool]]:
    rows = SPLASH_PATH.read_text(encoding="ascii").splitlines()
    if len(rows) != HEIGHT or any(len(row) != WIDTH for row in rows):
        widths = sorted({len(row) for row in rows})
        raise ValueError(
            f"splash.txt must be exactly {WIDTH}x{HEIGHT}; "
            f"got {len(rows)} rows with widths {widths}"
        )
    invalid = sorted({character for row in rows for character in row} - {".", "#"})
    if invalid:
        raise ValueError(f"invalid splash.txt characters: {', '.join(invalid)}")
    return [[character == "#" for character in row] for row in rows]


def copy_splash(pixels: list[list[bool]]) -> list[list[bool]]:
    return [row.copy() for row in pixels]


def export_splash(pixels: list[list[bool]]) -> None:
    text = "\n".join(
        "".join("#" if pixel else "." for pixel in row) for row in pixels
    )
    SPLASH_PATH.write_text(text + "\n", encoding="ascii")


def main() -> None:
    try:
        from imgui_bundle import hello_imgui, imgui, immapp
    except ModuleNotFoundError as error:
        root = Path(__file__).resolve().parents[3]
        candidates = (root / ".venv/bin/python", root / ".venv/Scripts/python.exe")
        venv_python = next((path for path in candidates if path.is_file()), None)
        if venv_python and Path(sys.executable).resolve() != venv_python.resolve():
            os.execv(str(venv_python), [str(venv_python), *sys.argv])
        raise SystemExit(
            "Missing GUI dependency. Run: "
            "python3 -m pip install imgui-bundle, or use the project .venv"
        ) from error

    try:
        pixels = load_splash()
    except (OSError, UnicodeError, ValueError) as error:
        raise SystemExit(error) from error

    class SplashEditor:
        def __init__(self) -> None:
            self.pixels = pixels
            self.saved = copy_splash(pixels)
            self.status = f"Loaded {SPLASH_PATH.name}; startup state saved in memory"
            self.status_error = False

        def draw(self) -> None:
            if imgui.button("Save (memory)"):
                self.saved = copy_splash(self.pixels)
                self.status = "Saved current canvas in memory"
                self.status_error = False
            imgui.same_line()
            if imgui.button("Load (memory)"):
                self.pixels = copy_splash(self.saved)
                self.status = "Loaded memory save"
                self.status_error = False
            imgui.same_line()
            if imgui.button("Export splash.txt"):
                try:
                    export_splash(self.pixels)
                except OSError as error:
                    self.status = f"Export failed: {error}"
                    self.status_error = True
                else:
                    self.status = f"Exported {SPLASH_PATH}"
                    self.status_error = False

            if self.status_error:
                imgui.text_colored(
                    imgui.ImVec4(1.0, 0.35, 0.35, 1.0), self.status
                )
            else:
                imgui.text(self.status)

            available = imgui.get_content_region_avail()
            editor_width = max(1.0, available.x - WIDTH - PREVIEW_GAP)
            cell_size = max(
                1.0,
                math.floor(min(editor_width / WIDTH, available.y / HEIGHT)),
            )
            grid_width = WIDTH * cell_size
            grid_height = HEIGHT * cell_size
            combined_width = grid_width + PREVIEW_GAP + WIDTH
            cursor = imgui.get_cursor_screen_pos()
            cursor_x = cursor.x + max(0.0, (available.x - combined_width) / 2)
            cursor_y = cursor.y
            preview_x = cursor_x + grid_width + PREVIEW_GAP
            preview_y = cursor_y
            imgui.set_cursor_screen_pos(imgui.ImVec2(cursor_x, cursor_y))

            imgui.invisible_button(
                "splash-grid", imgui.ImVec2(grid_width, grid_height)
            )
            hovered = imgui.is_item_hovered()
            mouse = imgui.get_io().mouse_pos
            if hovered and imgui.is_mouse_clicked(imgui.MouseButton_.left):
                mouse_x, mouse_y = mouse.x, mouse.y
                column = int((mouse_x - cursor_x) / cell_size)
                row = int((mouse_y - cursor_y) / cell_size)
                if 0 <= column < WIDTH and 0 <= row < HEIGHT:
                    self.pixels[row][column] = not self.pixels[row][column]
                    self.status = f"Toggled ({column}, {row})"
                    self.status_error = False

            draw_list = imgui.get_window_draw_list()
            black = imgui.get_color_u32(imgui.ImVec4(0.04, 0.04, 0.04, 1.0))
            white = imgui.get_color_u32(imgui.ImVec4(1.0, 1.0, 1.0, 1.0))
            grid_color = imgui.get_color_u32(imgui.ImVec4(0.25, 0.25, 0.25, 1.0))
            for row in range(HEIGHT):
                y0 = cursor_y + row * cell_size
                y1 = y0 + cell_size
                for column in range(WIDTH):
                    x0 = cursor_x + column * cell_size
                    x1 = x0 + cell_size
                    color = white if self.pixels[row][column] else black
                    draw_list.add_rect_filled(
                        imgui.ImVec2(x0, y0), imgui.ImVec2(x1, y1), color
                    )

            if cell_size >= 4:
                for column in range(WIDTH + 1):
                    x = cursor_x + column * cell_size
                    draw_list.add_line(
                        imgui.ImVec2(x, cursor_y),
                        imgui.ImVec2(x, cursor_y + grid_height),
                        grid_color,
                    )
                for row in range(HEIGHT + 1):
                    y = cursor_y + row * cell_size
                    draw_list.add_line(
                        imgui.ImVec2(cursor_x, y),
                        imgui.ImVec2(cursor_x + grid_width, y),
                        grid_color,
                    )

            # Exact 1:1 display preview: one screen pixel per canvas pixel.
            draw_list.add_rect_filled(
                imgui.ImVec2(preview_x, preview_y),
                imgui.ImVec2(preview_x + WIDTH, preview_y + HEIGHT),
                black,
            )
            for row in range(HEIGHT):
                for column in range(WIDTH):
                    if self.pixels[row][column]:
                        x = preview_x + column
                        y = preview_y + row
                        draw_list.add_rect_filled(
                            imgui.ImVec2(x, y),
                            imgui.ImVec2(x + 1, y + 1),
                            white,
                        )
            draw_list.add_rect(
                imgui.ImVec2(preview_x - 1, preview_y - 1),
                imgui.ImVec2(preview_x + WIDTH + 1, preview_y + HEIGHT + 1),
                grid_color,
            )

    editor = SplashEditor()
    runner_params = hello_imgui.RunnerParams()
    runner_params.app_window_params.window_title = "Redshift Splash Editor"
    runner_params.app_window_params.window_geometry.size = (1120, 860)
    runner_params.imgui_window_params.default_imgui_window_type = (
        hello_imgui.DefaultImGuiWindowType.provide_full_screen_window
    )
    runner_params.callbacks.show_gui = editor.draw
    immapp.run(runner_params)


if __name__ == "__main__":
    main()
