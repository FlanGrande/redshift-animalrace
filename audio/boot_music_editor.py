#!/usr/bin/env python3
"""Small ImGui composer for the adjacent boot_music.txt sequence."""

from __future__ import annotations

import math
import os
import random
import shutil
import subprocess
import sys
import tempfile
import wave
from array import array
from pathlib import Path


MUSIC_PATH = Path(__file__).with_name("boot_music.txt")
SAMPLE_RATE = 44_100
FRAME_RATE = 30
CHANNEL_NAMES = ("SQR0", "SQR1", "TRI0", "NSE0")
NOTE_NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")


def load_music() -> list[list[int]]:
    steps: list[list[int]] = []
    for line_number, line in enumerate(
        MUSIC_PATH.read_text(encoding="ascii").splitlines(), 1
    ):
        content = line.split("#", 1)[0].strip()
        if not content:
            continue
        fields = content.split()
        if len(fields) != 5:
            raise ValueError(
                f"line {line_number} must contain duration sqr0 sqr1 tri0 nse0"
            )
        try:
            step = [int(field) for field in fields]
        except ValueError as error:
            raise ValueError(f"line {line_number} is not numeric") from error
        if not 1 <= step[0] <= 64:
            raise ValueError(f"line {line_number} duration must be 1..64")
        if any(not 0 <= value <= 99 for value in step[1:]):
            raise ValueError(f"line {line_number} channels must be 0..99")
        steps.append(step)
    if not steps:
        raise ValueError("boot_music.txt must contain at least one step")
    return steps


def copy_music(steps: list[list[int]]) -> list[list[int]]:
    return [step.copy() for step in steps]


def export_music(steps: list[list[int]]) -> None:
    lines = ["# duration sqr0 sqr1 tri0 nse0"]
    lines.extend(" ".join(str(value) for value in step) for step in steps)
    MUSIC_PATH.write_text("\n".join(lines) + "\n", encoding="ascii")


def note_name(value: int) -> str:
    if value == 0:
        return "Off"
    octave = value // 12 - 1
    return f"{NOTE_NAMES[value % 12]}{octave}"


def write_preview_wav(steps: list[list[int]], path: Path) -> None:
    phases = [0.0, 0.0, 0.0]
    noise = random.Random(0)
    noise_value = 0.0
    noise_remaining = 0
    samples = array("h")

    for duration, sqr0, sqr1, tri0, nse0 in steps:
        values = (sqr0, sqr1, tri0)
        frequencies = [
            2.0 ** ((value - 60) / 12.0) * 261.63 if value else 0.0
            for value in values
        ]
        frame_samples = duration * SAMPLE_RATE // FRAME_RATE
        for _ in range(frame_samples):
            waves: list[float] = []
            for index in range(2):
                if values[index]:
                    phases[index] = (
                        phases[index] + frequencies[index] / SAMPLE_RATE
                    ) % 1.0
                    waves.append(1.0 if phases[index] < 0.5 else -1.0)
            if tri0:
                phases[2] = (phases[2] + frequencies[2] / SAMPLE_RATE) % 1.0
                waves.append(
                    (2.0 / math.pi) * math.asin(math.sin(2.0 * math.pi * phases[2]))
                )
            if nse0:
                if noise_remaining <= 0:
                    noise_value = noise.uniform(-1.0, 1.0)
                    noise_remaining = 100 - nse0
                noise_remaining -= 1
                waves.append(noise_value)
            sample = int((sum(waves) / len(waves) if waves else 0.0) * 12_000)
            samples.extend((sample, sample))

    with wave.open(str(path), "wb") as output:
        output.setnchannels(2)
        output.setsampwidth(2)
        output.setframerate(SAMPLE_RATE)
        output.writeframes(samples.tobytes())


def main() -> None:
    try:
        from imgui_bundle import hello_imgui, imgui, immapp
    except ModuleNotFoundError as error:
        root = Path(__file__).resolve().parents[3]
        candidates = (root / ".venv/bin/python", root / ".venv/Scripts/python.exe")
        venv_python = next((path for path in candidates if path.is_file()), None)
        if venv_python and Path(sys.executable).resolve() != venv_python.resolve():
            os.execv(str(venv_python), [str(venv_python), *sys.argv])
        raise SystemExit("Missing imgui-bundle; use the project .venv") from error

    try:
        initial_steps = load_music()
    except (OSError, UnicodeError, ValueError) as error:
        raise SystemExit(error) from error

    class MusicEditor:
        def __init__(self) -> None:
            self.steps = initial_steps
            self.saved = copy_music(initial_steps)
            self.selected = 0
            self.status = "Loaded boot music; startup state saved in memory"
            self.status_error = False
            self.player: subprocess.Popen[str] | None = None
            self.preview_path: Path | None = None

        def stop(self) -> None:
            if self.player and self.player.poll() is None:
                self.player.terminate()
                try:
                    self.player.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    self.player.kill()
            self.player = None
            if self.preview_path:
                self.preview_path.unlink(missing_ok=True)
                self.preview_path = None

        def play(self) -> None:
            self.stop()
            player = shutil.which("pw-play")
            if not player:
                self.status = "Preview needs pw-play"
                self.status_error = True
                return
            handle = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            handle.close()
            self.preview_path = Path(handle.name)
            write_preview_wav(self.steps, self.preview_path)
            self.player = subprocess.Popen(
                [player, str(self.preview_path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                text=True,
            )
            self.status = "Playing preview"
            self.status_error = False

        def poll_player(self) -> None:
            if self.player and self.player.poll() is not None:
                self.stop()

        def draw_timeline(self) -> None:
            available = imgui.get_content_region_avail()
            width = max(100.0, available.x)
            height = 96.0
            origin = imgui.get_cursor_screen_pos()
            imgui.invisible_button("timeline", imgui.ImVec2(width, height))
            hovered = imgui.is_item_hovered()
            draw_list = imgui.get_window_draw_list()
            background = imgui.get_color_u32(imgui.ImVec4(0.05, 0.05, 0.05, 1.0))
            active = imgui.get_color_u32(imgui.ImVec4(0.95, 0.95, 0.95, 1.0))
            inactive = imgui.get_color_u32(imgui.ImVec4(0.18, 0.18, 0.18, 1.0))
            selected = imgui.get_color_u32(imgui.ImVec4(1.0, 0.55, 0.15, 1.0))
            draw_list.add_rect_filled(
                origin, imgui.ImVec2(origin.x + width, origin.y + height), background
            )
            total = sum(step[0] for step in self.steps)
            x = origin.x
            boundaries: list[float] = [x]
            for index, step in enumerate(self.steps):
                step_width = width * step[0] / total
                for channel in range(4):
                    y0 = origin.y + channel * 24 + 2
                    y1 = y0 + 20
                    color = active if step[channel + 1] else inactive
                    draw_list.add_rect_filled(
                        imgui.ImVec2(x + 1, y0),
                        imgui.ImVec2(x + step_width - 1, y1),
                        color,
                    )
                if index == self.selected:
                    draw_list.add_rect(
                        imgui.ImVec2(x, origin.y),
                        imgui.ImVec2(x + step_width, origin.y + height),
                        selected,
                        0.0,
                        2.0,
                    )
                x += step_width
                boundaries.append(x)
            if hovered and imgui.is_mouse_clicked(imgui.MouseButton_.left):
                mouse_x = imgui.get_io().mouse_pos.x
                for index in range(len(self.steps)):
                    if boundaries[index] <= mouse_x < boundaries[index + 1]:
                        self.selected = index
                        break

        def draw(self) -> None:
            self.poll_player()
            if imgui.button("Save (memory)"):
                self.saved = copy_music(self.steps)
                self.status = "Saved sequence in memory"
                self.status_error = False
            imgui.same_line()
            if imgui.button("Load (memory)"):
                self.steps = copy_music(self.saved)
                self.selected = min(self.selected, len(self.steps) - 1)
                self.status = "Loaded memory save"
                self.status_error = False
            imgui.same_line()
            if imgui.button("Export boot_music.txt"):
                try:
                    export_music(self.steps)
                except OSError as error:
                    self.status = f"Export failed: {error}"
                    self.status_error = True
                else:
                    self.status = f"Exported {MUSIC_PATH}"
                    self.status_error = False
            imgui.same_line()
            if imgui.button("Play"):
                self.play()
            imgui.same_line()
            if imgui.button("Stop"):
                self.stop()
                self.status = "Stopped"

            if self.status_error:
                imgui.text_colored(
                    imgui.ImVec4(1.0, 0.35, 0.35, 1.0), self.status
                )
            else:
                imgui.text(self.status)

            self.draw_timeline()
            imgui.separator()
            imgui.text(
                f"Step {self.selected + 1}/{len(self.steps)} | "
                f"total {sum(step[0] for step in self.steps) / FRAME_RATE:.2f}s"
            )
            if imgui.button("Previous"):
                self.selected = max(0, self.selected - 1)
            imgui.same_line()
            if imgui.button("Next"):
                self.selected = min(len(self.steps) - 1, self.selected + 1)
            imgui.same_line()
            if imgui.button("Add after"):
                channels = self.steps[self.selected][1:].copy()
                self.steps.insert(self.selected + 1, [4, *channels])
                self.selected += 1
            imgui.same_line()
            if imgui.button("Duplicate"):
                self.steps.insert(self.selected + 1, self.steps[self.selected].copy())
                self.selected += 1
            imgui.same_line()
            if imgui.button("Delete") and len(self.steps) > 1:
                self.steps.pop(self.selected)
                self.selected = min(self.selected, len(self.steps) - 1)
            imgui.same_line()
            if imgui.button("Move left") and self.selected > 0:
                index = self.selected
                self.steps[index - 1], self.steps[index] = (
                    self.steps[index],
                    self.steps[index - 1],
                )
                self.selected -= 1
            imgui.same_line()
            if imgui.button("Move right") and self.selected + 1 < len(self.steps):
                index = self.selected
                self.steps[index], self.steps[index + 1] = (
                    self.steps[index + 1],
                    self.steps[index],
                )
                self.selected += 1

            step = self.steps[self.selected]
            changed, value = imgui.input_int("Duration (frames at 30Hz)", step[0])
            if changed:
                step[0] = max(1, min(64, value))
            for index, channel in enumerate(CHANNEL_NAMES, 1):
                changed, value = imgui.input_int(channel, step[index])
                if changed:
                    step[index] = max(0, min(99, value))
                if index < 4:
                    imgui.same_line()
                    imgui.text(note_name(step[index]))

    editor = MusicEditor()
    runner_params = hello_imgui.RunnerParams()
    runner_params.app_window_params.window_title = "Redshift Boot Music Composer"
    runner_params.app_window_params.window_geometry.size = (900, 560)
    runner_params.imgui_window_params.default_imgui_window_type = (
        hello_imgui.DefaultImGuiWindowType.provide_full_screen_window
    )
    runner_params.callbacks.show_gui = editor.draw
    runner_params.callbacks.before_exit = editor.stop
    immapp.run(runner_params)


if __name__ == "__main__":
    main()
