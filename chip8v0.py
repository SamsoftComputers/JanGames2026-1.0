#!/usr/bin/env python3
"""
Cat's Chip 8 emulator ♡ — backend + frontend (v0.1, Tkinter)

Single-file, dependency-free Chip 8 emulator:
- Backend: Chip 8 CPU / VM (memory, registers, timers, display, keypad)
- Frontend: Tkinter GUI (ROM load, run/pause, display)

Note:
This is a starter / learning-friendly backend. Many ROMs need more opcodes + quirks.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import tkinter as tk
from tkinter import filedialog, messagebox


# ──────────────────────────────────────────────────────────────────────────────
# APP CONFIG (Cat's Chip 8 emulator — backend + frontend)
# ──────────────────────────────────────────────────────────────────────────────
APP_TITLE = "Cat's Chip 8 emulator ♡ — backend + frontend"
DISPLAY_W = 64
DISPLAY_H = 32
ROM_START = 0x200
FONT_START = 0x50

ROM_FILETYPES = [
    ("Chip 8 ROMs", "*.ch8 *.c8 *.rom *.bin"),
    ("All files", "*.*"),
]

# Chip 8 keypad mapping:
# 1 2 3 C    ->   1 2 3 4
# 4 5 6 D    ->   Q W E R
# 7 8 9 E    ->   A S D F
# A 0 B F    ->   Z X C V
KEYMAP = {
    "1": 0x1, "2": 0x2, "3": 0x3, "4": 0xC,
    "q": 0x4, "w": 0x5, "e": 0x6, "r": 0xD,
    "a": 0x7, "s": 0x8, "d": 0x9, "f": 0xE,
    "z": 0xA, "x": 0x0, "c": 0xB, "v": 0xF,
}

FONTSET = bytes([
    0xF0,0x90,0x90,0x90,0xF0, 0x20,0x60,0x20,0x20,0x70,
    0xF0,0x10,0xF0,0x80,0xF0, 0xF0,0x10,0xF0,0x10,0xF0,
    0x90,0x90,0xF0,0x10,0x10, 0xF0,0x80,0xF0,0x10,0xF0,
    0xF0,0x80,0xF0,0x90,0xF0, 0xF0,0x10,0x20,0x40,0x40,
    0xF0,0x90,0xF0,0x90,0xF0, 0xF0,0x90,0xF0,0x10,0xF0,
    0xF0,0x90,0xF0,0x90,0x90, 0xE0,0x90,0xE0,0x90,0xE0,
    0xF0,0x80,0x80,0x80,0xF0, 0xE0,0x90,0x90,0x90,0xE0,
    0xF0,0x80,0xF0,0x80,0xF0, 0xF0,0x80,0xF0,0x80,0x80,
])


@dataclass
class Quirks:
    """Quirks for Cat's Chip 8 emulator backend."""
    draw_wraps: bool = True


# ──────────────────────────────────────────────────────────────────────────────
# BACKEND — Cat's Chip 8 emulator backend (CPU / VM)
# ──────────────────────────────────────────────────────────────────────────────
class CatChip8Backend:
    def __init__(self, quirks: Optional[Quirks] = None) -> None:
        self.quirks = quirks or Quirks()
        self.reset()

    def reset(self) -> None:
        self.memory = bytearray(4096)
        self.V = [0] * 16
        self.I = 0
        self.pc = ROM_START

        self.stack = [0] * 16
        self.sp = 0

        self.delay_timer = 0
        self.sound_timer = 0

        self.keys = [0] * 16
        self.gfx = [0] * (DISPLAY_W * DISPLAY_H)

        self.draw_flag = False
        self.halted_wait_key: Optional[int] = None

        # Font for Cat's Chip 8 emulator backend
        self.memory[FONT_START:FONT_START + len(FONTSET)] = FONTSET

    def load_rom_bytes(self, data: bytes) -> None:
        if len(data) > (len(self.memory) - ROM_START):
            raise ValueError("ROM is too large for Chip 8 memory.")
        self.memory[ROM_START:ROM_START + len(data)] = data
        self.pc = ROM_START

    def set_key(self, key: int, pressed: bool) -> None:
        if 0 <= key <= 0xF:
            self.keys[key] = 1 if pressed else 0

    def _fetch(self) -> int:
        return (self.memory[self.pc] << 8) | self.memory[self.pc + 1]

    def cycle(self) -> None:
        # Fx0A wait-for-key (backend halts here until a key is pressed)
        if self.halted_wait_key is not None:
            for k, p in enumerate(self.keys):
                if p:
                    self.V[self.halted_wait_key] = k
                    self.halted_wait_key = None
                    self.pc = (self.pc + 2) & 0xFFFF
                    break
            return

        opcode = self._fetch()
        self.pc = (self.pc + 2) & 0xFFFF

        nnn = opcode & 0x0FFF
        n = opcode & 0x000F
        x = (opcode >> 8) & 0x000F
        y = (opcode >> 4) & 0x000F
        kk = opcode & 0x00FF
        top = opcode & 0xF000

        if opcode == 0x00E0:  # CLS
            self.gfx = [0] * (DISPLAY_W * DISPLAY_H)
            self.draw_flag = True
            return

        if opcode == 0x00EE:  # RET
            if self.sp <= 0:
                return
            self.sp -= 1
            self.pc = self.stack[self.sp] & 0xFFFF
            return

        if top == 0x1000:  # 1nnn JP
            self.pc = nnn
            return

        if top == 0x2000:  # 2nnn CALL
            if self.sp >= len(self.stack):
                return
            self.stack[self.sp] = self.pc
            self.sp += 1
            self.pc = nnn
            return

        if top == 0x6000:  # 6xkk LD Vx, byte
            self.V[x] = kk
            return

        if top == 0x7000:  # 7xkk ADD Vx, byte
            self.V[x] = (self.V[x] + kk) & 0xFF
            return

        if top == 0xA000:  # Annn LD I, addr
            self.I = nnn
            return

        if top == 0xD000:  # Dxyn DRW Vx, Vy, nibble
            self.V[0xF] = 0
            vx = self.V[x] % DISPLAY_W
            vy = self.V[y] % DISPLAY_H
            for row in range(n):
                sprite = self.memory[self.I + row]
                for col in range(8):
                    if sprite & (0x80 >> col):
                        px = vx + col
                        py = vy + row
                        if self.quirks.draw_wraps:
                            px %= DISPLAY_W
                            py %= DISPLAY_H
                        if px < 0 or px >= DISPLAY_W or py < 0 or py >= DISPLAY_H:
                            continue
                        idx = py * DISPLAY_W + px
                        if self.gfx[idx] == 1:
                            self.V[0xF] = 1
                        self.gfx[idx] ^= 1
            self.draw_flag = True
            return

        if top == 0xF000 and kk == 0x0A:  # Fx0A LD Vx, K
            self.halted_wait_key = x
            self.pc = (self.pc - 2) & 0xFFFF  # stay here until a key is pressed
            return

        # Unknown opcode: ignore safely (extend backend as you add instructions)
        return

    def tick_timers_60hz(self) -> None:
        if self.delay_timer > 0:
            self.delay_timer -= 1
        if self.sound_timer > 0:
            self.sound_timer -= 1


# ──────────────────────────────────────────────────────────────────────────────
# FRONTEND — Cat's Chip 8 emulator frontend (Tkinter GUI)
# ──────────────────────────────────────────────────────────────────────────────
class CatChip8Frontend(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.resizable(False, False)

        self.quirks = Quirks()
        self.backend = CatChip8Backend(self.quirks)

        self.running = False
        self.scale = tk.IntVar(value=12)
        self.cps = tk.IntVar(value=600)
        self.status = tk.StringVar(value="Ready ♡  Open a ROM to start")

        self._build_ui()
        self._rebuild_display()

        self.bind("<KeyPress>", self._on_key_press)
        self.bind("<KeyRelease>", self._on_key_release)
        self.after(0, self._loop)

    def _build_ui(self) -> None:
        tk.Button(self, text="Open ROM…", command=self.open_rom).pack(padx=10, pady=(10, 4))
        self.btn = tk.Button(self, text="Run", width=12, command=self.toggle)
        self.btn.pack(padx=10, pady=4)

        self.canvas = tk.Canvas(self, bg="black", highlightthickness=2)
        self.canvas.pack(padx=10, pady=10)

        tk.Label(self, textvariable=self.status, anchor="w").pack(fill="x", padx=10, pady=(0, 10))

    def _rebuild_display(self) -> None:
        s = int(self.scale.get())
        self.canvas.config(width=DISPLAY_W * s, height=DISPLAY_H * s)
        self.canvas.delete("all")

        self.pixels: list[int] = []
        for y in range(DISPLAY_H):
            for x in range(DISPLAY_W):
                rid = self.canvas.create_rectangle(
                    x * s, y * s, x * s + s, y * s + s,
                    fill="black", outline=""
                )
                self.pixels.append(rid)

    def open_rom(self) -> None:
        path = filedialog.askopenfilename(title="Open Chip 8 ROM", filetypes=ROM_FILETYPES)
        if not path:
            return
        try:
            data = Path(path).read_bytes()
            self.backend.reset()
            self.backend.load_rom_bytes(data)
            self.status.set(f"ROM loaded ♡  {Path(path).name}")
        except Exception as e:
            messagebox.showerror("Cat's Chip 8 emulator", str(e))

    def toggle(self) -> None:
        self.running = not self.running
        self.btn.config(text="Pause" if self.running else "Run")
        self.status.set("Running… nya~" if self.running else "Paused ♡")

    def _loop(self) -> None:
        if self.running:
            cycles = max(1, int(self.cps.get()) // 60)  # ~60fps pacing
            for _ in range(cycles):
                self.backend.cycle()

        self.backend.tick_timers_60hz()

        if self.backend.draw_flag:
            for i, v in enumerate(self.backend.gfx):
                self.canvas.itemconfig(self.pixels[i], fill=("white" if v else "black"))
            self.backend.draw_flag = False

        self.after(16, self._loop)

    def _on_key_press(self, e: tk.Event) -> None:
        ch = (e.char or "").lower()
        if ch in KEYMAP:
            self.backend.set_key(KEYMAP[ch], True)
        if e.keysym == "Escape":
            self.running = False
            self.btn.config(text="Run")
            self.status.set("Paused ♡ (Esc)")

    def _on_key_release(self, e: tk.Event) -> None:
        ch = (e.char or "").lower()
        if ch in KEYMAP:
            self.backend.set_key(KEYMAP[ch], False)


def main() -> None:
    os.environ.setdefault("TK_SILENCE_DEPRECATION", "1")
    CatChip8Frontend().mainloop()


if __name__ == "__main__":
    main()
