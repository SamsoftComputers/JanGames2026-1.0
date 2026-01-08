# program.py
import math
import random
import tkinter as tk
from dataclasses import dataclass
from typing import List, Tuple, Optional, Set, Dict

# ----------------------------
# Cat's Retro Platform Quest
# ----------------------------
# A single-file, original retro platformer inspired by classic 8-bit platform games.
# 8 worlds x 5 stages (1-1 through 8-5), deterministic level generation,
# main menu, level select, coins, hazards, simple enemies, and side-scrolling.
#
# Controls:
#   Left / Right : Move
#   Space / Up   : Jump
#   R            : Restart stage
#   Esc          : Back to menu
#
# Notes:
# - This is NOT a copy of any copyrighted game or its level layouts.
# - All stages are generated from a seed, so World 3-2 is always the same in THIS game,
#   but it's an original design.

TILE = 32
ROWS = 15
VISIBLE_COLS = 25
WIDTH = VISIBLE_COLS * TILE
HEIGHT = ROWS * TILE

FPS = 60
DT_MS = int(1000 / FPS)

# Physics tuning (pixels per frame, since we run a fixed timestep)
GRAVITY = 0.85
JUMP_VELOCITY = -14.0
MAX_FALL_SPEED = 18.0
ACCEL = 1.15
MAX_SPEED = 6.2

# AABB sizes
PLAYER_W = 24
PLAYER_H = 28

ENEMY_W = 24
ENEMY_H = 24
ENEMY_SPEED = 1.25

# Tiles
EMPTY = "."
SOLID = "#"
COIN = "C"
START = "S"
GOAL = "G"
HAZARD = "H"

SOLID_TILES = {SOLID, HAZARD}  # Hazard is solid *and* deadly when touched.

WORLDS = 8
STAGES_PER_WORLD = 5

# Visual themes by world (simple colors, no external assets)
THEMES: List[Dict[str, str]] = [
    {"bg": "#0b1020", "solid": "#3b2b1f", "coin": "#ffd34d", "hazard": "#d73a49", "goal": "#33d17a", "player": "#e6edf3", "enemy": "#ff8b3d"},
    {"bg": "#071a12", "solid": "#2d3b1f", "coin": "#ffd34d", "hazard": "#d73a49", "goal": "#33d17a", "player": "#e6edf3", "enemy": "#ff8b3d"},
    {"bg": "#0c1220", "solid": "#2b2b44", "coin": "#ffd34d", "hazard": "#d73a49", "goal": "#33d17a", "player": "#e6edf3", "enemy": "#ff8b3d"},
    {"bg": "#1a0b12", "solid": "#3b1f2a", "coin": "#ffd34d", "hazard": "#d73a49", "goal": "#33d17a", "player": "#e6edf3", "enemy": "#ff8b3d"},
    {"bg": "#081018", "solid": "#1f3b3b", "coin": "#ffd34d", "hazard": "#d73a49", "goal": "#33d17a", "player": "#e6edf3", "enemy": "#ff8b3d"},
    {"bg": "#101010", "solid": "#303030", "coin": "#ffd34d", "hazard": "#d73a49", "goal": "#33d17a", "player": "#e6edf3", "enemy": "#ff8b3d"},
    {"bg": "#0b0f1a", "solid": "#242a3b", "coin": "#ffd34d", "hazard": "#d73a49", "goal": "#33d17a", "player": "#e6edf3", "enemy": "#ff8b3d"},
    {"bg": "#0a0a0a", "solid": "#1f1f1f", "coin": "#ffd34d", "hazard": "#d73a49", "goal": "#33d17a", "player": "#e6edf3", "enemy": "#ff8b3d"},
]

def clamp(v: float, lo: float, hi: float) -> float:
    return lo if v < lo else hi if v > hi else v

def aabb_intersect(ax: float, ay: float, aw: float, ah: float, bx: float, by: float, bw: float, bh: float) -> bool:
    return (ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by)

@dataclass
class Enemy:
    x: float
    y: float
    vx: float
    alive: bool = True

@dataclass
class Player:
    x: float
    y: float
    vx: float = 0.0
    vy: float = 0.0
    on_ground: bool = False
    alive: bool = True

class Level:
    def __init__(self, world: int, stage: int):
        self.world = world
        self.stage = stage
        self.cols = self._compute_length(world, stage)
        self.grid = [[EMPTY for _ in range(self.cols)] for _ in range(ROWS)]
        self.enemies: List[Enemy] = []
        self.coins_total = 0
        self._spawn_x = 2 * TILE
        self._spawn_y = (ROWS - 3) * TILE
        self._goal_rect: Tuple[float, float, float, float] = (0, 0, 0, 0)
        self._generate()

    def _compute_length(self, world: int, stage: int) -> int:
        # Enough scroll room; slightly longer with later worlds/stages
        return 170 + (world - 1) * 12 + (stage - 1) * 10

    def _rng(self) -> random.Random:
        # Deterministic per world-stage.
        seed = (self.world * 10007) ^ (self.stage * 31337) ^ 0xC0FFEE
        return random.Random(seed)

    def _set_tile(self, cx: int, cy: int, t: str) -> None:
        if 0 <= cx < self.cols and 0 <= cy < ROWS:
            self.grid[cy][cx] = t

    def tile_at(self, cx: int, cy: int) -> str:
        if cx < 0 or cx >= self.cols or cy < 0 or cy >= ROWS:
            return EMPTY
        return self.grid[cy][cx]

    def is_solid(self, cx: int, cy: int) -> bool:
        return self.tile_at(cx, cy) in SOLID_TILES

    def is_hazard(self, cx: int, cy: int) -> bool:
        return self.tile_at(cx, cy) == HAZARD

    def is_goal(self, cx: int, cy: int) -> bool:
        return self.tile_at(cx, cy) == GOAL

    def is_coin(self, cx: int, cy: int) -> bool:
        return self.tile_at(cx, cy) == COIN

    def consume_coin(self, cx: int, cy: int) -> bool:
        if self.is_coin(cx, cy):
            self._set_tile(cx, cy, EMPTY)
            return True
        return False

    def spawn_point(self) -> Tuple[float, float]:
        return self._spawn_x, self._spawn_y

    def _generate(self) -> None:
        rng = self._rng()
        ground_y = ROWS - 2  # tiles at ground_y and ground_y+1 are ground, unless a pit
        # Base ground
        for x in range(self.cols):
            for y in range(ground_y, ROWS):
                self._set_tile(x, y, SOLID)

        # Carve pits (small enough to jump), more frequent in later worlds
        pit_prob = 0.06 + 0.01 * (self.world - 1) + 0.006 * (self.stage - 1)
        pit_prob = clamp(pit_prob, 0.06, 0.18)

        x = 8
        while x < self.cols - 15:
            if rng.random() < pit_prob:
                pit_len = rng.randint(2, 4 + (self.world // 3))
                pit_len = int(clamp(pit_len, 2, 6))
                # Avoid pits too close to start
                if x < 14:
                    x += 8
                    continue
                # Carve pit
                for px in range(x, min(self.cols, x + pit_len)):
                    for y in range(ground_y, ROWS):
                        self._set_tile(px, y, EMPTY)
                # Add a small "bridge" platform above some pits to keep things fair
                if rng.random() < 0.55:
                    plat_y = ground_y - rng.randint(3, 4)
                    plat_start = max(0, x - 1)
                    plat_end = min(self.cols - 1, x + pit_len + 1)
                    for px in range(plat_start, plat_end + 1):
                        self._set_tile(px, plat_y, SOLID)
                        # A few coins on the bridge
                        if rng.random() < 0.25:
                            self._set_tile(px, plat_y -  1, COIN)
                x += pit_len + rng.randint(6, 12)
            else:
                x += rng.randint(4, 9)

        # Add floating platforms
        platform_count = 8 + self.world * 2 + self.stage
        for _ in range(platform_count):
            w = rng.randint(3, 9)
            y = rng.randint(5, ROWS - 5)
            x = rng.randint(10, self.cols - 20)
            for px in range(x, min(self.cols, x + w)):
                self._set_tile(px, y, SOLID)
                if rng.random() < 0.22:
                    self._set_tile(px, y - 1, COIN)

        # Hazards on ground (rare; jump-over challenges)
        hazard_prob = 0.012 + 0.004 * (self.world - 1) + 0.002 * (self.stage - 1)
        for x in range(12, self.cols - 18):
            if rng.random() < hazard_prob:
                # Only place if there's solid ground and not in a pit
                if self.tile_at(x, ground_y) == SOLID:
                    self._set_tile(x, ground_y - 1, HAZARD)

        # Coins sprinkled on safe ground
        for x in range(6, self.cols - 10):
            if rng.random() < 0.06 and self.tile_at(x, ground_y) == SOLID:
                self._set_tile(x, ground_y - 3 if rng.random() < 0.35 else ground_y - 1, COIN)

        # Start
        self._set_tile(2, ground_y - 1, START)
        self._spawn_x = 2 * TILE
        self._spawn_y = (ground_y - 1) * TILE - (PLAYER_H - TILE)  # slightly above ground tile

        # Goal near end, ensure ground exists
        goal_x = self.cols - 6
        for gx in range(self.cols - 12, self.cols - 3):
            # Repair any pits near the end
            for y in range(ground_y, ROWS):
                self._set_tile(gx, y, SOLID)
        self._set_tile(goal_x, ground_y - 1, GOAL)
        self._goal_rect = (goal_x * TILE, (ground_y - 1) * TILE, TILE, TILE)

        # Enemies on ground segments (more in later worlds)
        enemy_prob = 0.03 + 0.006 * (self.world - 1) + 0.004 * (self.stage - 1)
        enemy_prob = clamp(enemy_prob, 0.03, 0.12)

        for x in range(10, self.cols - 10):
            if rng.random() < enemy_prob and self.tile_at(x, ground_y) == SOLID and self.tile_at(x, ground_y - 1) == EMPTY:
                # Avoid stacking enemies too close
                if self.enemies and abs(self.enemies[-1].x - x * TILE) < 5 * TILE:
                    continue
                ex = x * TILE + (TILE - ENEMY_W) / 2
                ey = (ground_y - 1) * TILE + (TILE - ENEMY_H)
                dir_choice = -1 if rng.random() < 0.5 else 1
                self.enemies.append(Enemy(ex, ey, dir_choice * ENEMY_SPEED))

        # Count coins
        self.coins_total = sum(1 for y in range(ROWS) for x in range(self.cols) if self.grid[y][x] == COIN)

class GameApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Cat's Retro Platform Quest")

        self.canvas = tk.Canvas(self.root, width=WIDTH, height=HEIGHT, highlightthickness=0)
        self.canvas.pack()

        self.keys: Set[str] = set()

        self.state = "menu"  # menu, level_select, howto, play, death, complete, win
        self.menu_index = 0
        self.menu_items = ["Start Adventure", "Level Select", "How to Play", "Quit"]

        self.level_select_cursor = (1, 1)  # (world, stage)
        self.unlocked_world = 1
        self.unlocked_stage = 1

        self.world = 1
        self.stage = 1
        self.level: Optional[Level] = None

        self.player = Player(0, 0)
        self.camera_x = 0.0

        self.score = 0
        self.coins_collected = 0

        self._bind_keys()
        self._load_level(self.world, self.stage)
        self._loop()

    def _bind_keys(self):
        self.root.bind("<KeyPress>", self._on_key_down)
        self.root.bind("<KeyRelease>", self._on_key_up)

    def _on_key_down(self, e):
        key = e.keysym
        self.keys.add(key)

        # One-shot actions by state
        if self.state == "menu":
            if key in ("Up", "w", "W"):
                self.menu_index = (self.menu_index - 1) % len(self.menu_items)
            elif key in ("Down", "s", "S"):
                self.menu_index = (self.menu_index + 1) % len(self.menu_items)
            elif key in ("Return", "space"):
                self._activate_menu()
        elif self.state == "howto":
            if key in ("Escape", "Return", "space"):
                self.state = "menu"
        elif self.state == "level_select":
            self._handle_level_select_key(key)
        elif self.state == "play":
            if key in ("r", "R"):
                self._restart_stage()
            elif key == "Escape":
                self.state = "menu"
        elif self.state in ("death", "complete"):
            if key in ("Return", "space"):
                if self.state == "death":
                    self._restart_stage()
                else:
                    self._advance_stage()
            elif key == "Escape":
                self.state = "menu"
        elif self.state == "win":
            if key in ("Return", "space", "Escape"):
                self.state = "menu"

    def _on_key_up(self, e):
        key = e.keysym
        if key in self.keys:
            self.keys.remove(key)

    def _activate_menu(self):
        choice = self.menu_items[self.menu_index]
        if choice == "Start Adventure":
            self.world, self.stage = 1, 1
            self.unlocked_world, self.unlocked_stage = 1, 1
            self.score = 0
            self.coins_collected = 0
            self._load_level(self.world, self.stage)
            self.state = "play"
        elif choice == "Level Select":
            self.level_select_cursor = (self.unlocked_world, self.unlocked_stage)
            self.state = "level_select"
        elif choice == "How to Play":
            self.state = "howto"
        elif choice == "Quit":
            self.root.destroy()

    def _handle_level_select_key(self, key: str):
        w, s = self.level_select_cursor
        if key in ("Left", "a", "A"):
            s = max(1, s - 1)
        elif key in ("Right", "d", "D"):
            s = min(STAGES_PER_WORLD, s + 1)
        elif key in ("Up", "w", "W"):
            w = max(1, w - 1)
        elif key in ("Down", "s", "S"):
            w = min(WORLDS, w + 1)
        elif key == "Escape":
            self.state = "menu"
            return
        elif key in ("Return", "space"):
            if self._is_unlocked(w, s):
                self.world, self.stage = w, s
                self._load_level(w, s)
                self.state = "play"
            return
        self.level_select_cursor = (w, s)

    def _is_unlocked(self, w: int, s: int) -> bool:
        if w < self.unlocked_world:
            return True
        if w == self.unlocked_world and s <= self.unlocked_stage:
            return True
        return False

    def _unlock_next(self):
        # Unlock the next stage in sequence (up to 8-5).
        w, s = self.unlocked_world, self.unlocked_stage
        if (w, s) == (WORLDS, STAGES_PER_WORLD):
            return
        if s < STAGES_PER_WORLD:
            s += 1
        else:
            w += 1
            s = 1
        self.unlocked_world, self.unlocked_stage = w, s

    def _load_level(self, world: int, stage: int):
        self.level = Level(world, stage)
        sx, sy = self.level.spawn_point()
        self.player = Player(sx, sy)
        self.camera_x = 0.0

    def _restart_stage(self):
        self._load_level(self.world, self.stage)
        self.state = "play"

    def _advance_stage(self):
        # If we just completed final stage, show win screen.
        if (self.world, self.stage) == (WORLDS, STAGES_PER_WORLD):
            self.state = "win"
            return

        # Advance by numbering: 1-1 ... 1-5, 2-1 ... 8-5
        if self.stage < STAGES_PER_WORLD:
            self.stage += 1
        else:
            self.world += 1
            self.stage = 1

        # Unlock progress up to the new stage
        if not self._is_unlocked(self.world, self.stage):
            self.unlocked_world, self.unlocked_stage = self.world, self.stage

        self._load_level(self.world, self.stage)
        self.state = "play"

    def _loop(self):
        self._update()
        self._render()
        self.root.after(DT_MS, self._loop)

    # ----------------------------
    # Gameplay update
    # ----------------------------
    def _update(self):
        if self.state != "play":
            return
        assert self.level is not None

        # World-based "feel" tweaks (subtle, original)
        friction = 0.78 if self.world in (1, 3, 4, 7) else 0.86
        if self.world in (2, 6):  # a little "slick"
            friction = 0.92

        p = self.player

        # Input -> acceleration
        left = ("Left" in self.keys) or ("a" in self.keys) or ("A" in self.keys)
        right = ("Right" in self.keys) or ("d" in self.keys) or ("D" in self.keys)
        jump = ("space" in self.keys) or ("Up" in self.keys) or ("w" in self.keys) or ("W" in self.keys)

        if left and not right:
            p.vx -= ACCEL
        elif right and not left:
            p.vx += ACCEL
        else:
            p.vx *= friction
            if abs(p.vx) < 0.08:
                p.vx = 0.0

        p.vx = clamp(p.vx, -MAX_SPEED, MAX_SPEED)

        # Jump (edge-triggered-ish)
        if not hasattr(self, "_jump_was_held"):
            self._jump_was_held = False  # type: ignore[attr-defined]

        if jump and p.on_ground and not self._jump_was_held:  # type: ignore[attr-defined]
            p.vy = JUMP_VELOCITY
            p.on_ground = False
        self._jump_was_held = jump  # type: ignore[attr-defined]

        # Gravity
        p.vy = clamp(p.vy + GRAVITY, -999, MAX_FALL_SPEED)

        # Move & collide
        self._move_player(p, p.vx, 0.0)
        self._move_player(p, 0.0, p.vy)

        # Update enemies
        for e in self.level.enemies:
            if not e.alive:
                continue
            self._update_enemy(e)

        # Interactions: coins, hazard, goal, enemies
        self._handle_pickups_and_tiles()
        self._handle_enemy_collisions()

        # Camera follows player
        target = p.x - WIDTH * 0.4
        self.camera_x = clamp(target, 0.0, max(0.0, self.level.cols * TILE - WIDTH))

        # Fall off world -> death
        if p.y > HEIGHT + 200:
            self.state = "death"

    def _move_player(self, p: Player, dx: float, dy: float):
        assert self.level is not None

        p.x += dx
        if dx != 0:
            if self._collides_with_solid(p.x, p.y, PLAYER_W, PLAYER_H):
                # Resolve horizontally
                if dx > 0:
                    cx = int((p.x + PLAYER_W - 1) // TILE)
                    p.x = cx * TILE - PLAYER_W
                else:
                    cx = int(p.x // TILE)
                    p.x = (cx + 1) * TILE
                p.vx = 0.0

        p.y += dy
        p.on_ground = False
        if dy != 0:
            if self._collides_with_solid(p.x, p.y, PLAYER_W, PLAYER_H):
                if dy > 0:
                    cy = int((p.y + PLAYER_H - 1) // TILE)
                    p.y = cy * TILE - PLAYER_H
                    p.vy = 0.0
                    p.on_ground = True
                else:
                    cy = int(p.y // TILE)
                    p.y = (cy + 1) * TILE
                    p.vy = 0.0

    def _collides_with_solid(self, x: float, y: float, w: float, h: float) -> bool:
        assert self.level is not None
        x1 = int(x // TILE)
        x2 = int((x + w - 1) // TILE)
        y1 = int(y // TILE)
        y2 = int((y + h - 1) // TILE)
        for cy in range(y1, y2 + 1):
            for cx in range(x1, x2 + 1):
                if self.level.is_solid(cx, cy):
                    return True
        return False

    def _handle_pickups_and_tiles(self):
        assert self.level is not None
        p = self.player

        # Use inclusive bounds (no -1) so "touching" hazards/goals counts, not only overlap.
        x1 = int(p.x // TILE)
        x2 = int((p.x + PLAYER_W) // TILE)
        y1 = int(p.y // TILE)
        y2 = int((p.y + PLAYER_H) // TILE)

        for cy in range(y1, y2 + 1):
            for cx in range(x1, x2 + 1):
                t = self.level.tile_at(cx, cy)
                if t == COIN:
                    if self.level.consume_coin(cx, cy):
                        self.coins_collected += 1
                        self.score += 10
                elif t == HAZARD:
                    self.state = "death"
                    return
                elif t == GOAL:
                    self.score += 100
                    self._unlock_next()
                    self.state = "complete"
                    return

    def _update_enemy(self, e: Enemy):
        assert self.level is not None

        # Horizontal movement with basic wall/edge detection
        e.x += e.vx

        # Collision with solid blocks
        if self._collides_with_solid(e.x, e.y, ENEMY_W, ENEMY_H):
            if e.vx > 0:
                cx = int((e.x + ENEMY_W - 1) // TILE)
                e.x = cx * TILE - ENEMY_W
            else:
                cx = int(e.x // TILE)
                e.x = (cx + 1) * TILE
            e.vx *= -1

        # Gravity-ish (enemies stay on ground)
        e.y += GRAVITY
        if self._collides_with_solid(e.x, e.y, ENEMY_W, ENEMY_H):
            cy = int((e.y + ENEMY_H - 1) // TILE)
            e.y = cy * TILE - ENEMY_H

        # Turn around at ledges (look ahead one tile down)
        dir_sign = 1 if e.vx > 0 else -1
        ahead_x = e.x + (ENEMY_W if dir_sign > 0 else -1)
        foot_y = e.y + ENEMY_H + 1
        cx = int(ahead_x // TILE)
        cy = int(foot_y // TILE)
        if not self.level.is_solid(cx, cy):
            e.vx *= -1

    def _handle_enemy_collisions(self):
        assert self.level is not None
        p = self.player
        for e in self.level.enemies:
            if not e.alive:
                continue
            if aabb_intersect(p.x, p.y, PLAYER_W, PLAYER_H, e.x, e.y, ENEMY_W, ENEMY_H):
                # If player is falling and hits enemy from above, stomp it
                player_bottom = p.y + PLAYER_H
                enemy_top = e.y
                if p.vy > 0 and player_bottom - enemy_top < 14:
                    e.alive = False
                    p.vy = JUMP_VELOCITY * 0.65  # small bounce
                    self.score += 50
                else:
                    self.state = "death"
                    return

    # ----------------------------
    # Rendering
    # ----------------------------
    def _render(self):
        self.canvas.delete("all")

        if self.state == "menu":
            self._render_menu()
        elif self.state == "howto":
            self._render_howto()
        elif self.state == "level_select":
            self._render_level_select()
        elif self.state in ("play", "death", "complete"):
            self._render_game()
            if self.state == "death":
                self._overlay_center("Ouch! Press Enter to retry\n( Esc: menu )")
            elif self.state == "complete":
                self._overlay_center("Stage clear! Press Enter to continue\n( Esc: menu )")
        elif self.state == "win":
            self._render_game()
            self._overlay_center("You cleared all 8 worlds!\nPress Enter (or Esc) for menu")

    def _render_menu(self):
        theme = THEMES[0]
        self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill=theme["bg"], outline="")
        self.canvas.create_text(WIDTH/2, 110, text="Cat's Retro Platform Quest", fill="#ffffff", font=("TkDefaultFont", 20, "bold"))
        self.canvas.create_text(WIDTH/2, 145, text="8 worlds • 5 stages each • original levels", fill="#c9d1d9", font=("TkDefaultFont", 11))

        y0 = 220
        for i, item in enumerate(self.menu_items):
            prefix = "▶ " if i == self.menu_index else "  "
            color = "#ffffff" if i == self.menu_index else "#c9d1d9"
            self.canvas.create_text(WIDTH/2, y0 + i*34, text=prefix + item, fill=color, font=("TkDefaultFont", 14))

        self.canvas.create_text(WIDTH/2, HEIGHT - 40, text="Arrow keys + Enter • Esc to back out", fill="#8b949e", font=("TkDefaultFont", 10))

    def _render_howto(self):
        theme = THEMES[0]
        self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill=theme["bg"], outline="")
        lines = [
            "How to Play",
            "",
            "Move: Left / Right (or A / D)",
            "Jump: Space (or Up / W)",
            "Restart: R",
            "Menu: Esc",
            "",
            "Collect coins, avoid hazards, stomp enemies from above,",
            "and reach the goal tile at the end of each stage.",
            "",
            "Press Enter (or Esc) to return."
        ]
        y = 90
        for idx, line in enumerate(lines):
            font = ("TkDefaultFont", 18, "bold") if idx == 0 else ("TkDefaultFont", 12)
            color = "#ffffff" if idx == 0 else "#c9d1d9"
            self.canvas.create_text(WIDTH/2, y, text=line, fill=color, font=font)
            y += 32 if idx == 0 else 24

    def _render_level_select(self):
        theme = THEMES[0]
        self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill=theme["bg"], outline="")
        self.canvas.create_text(WIDTH/2, 70, text="Level Select", fill="#ffffff", font=("TkDefaultFont", 20, "bold"))
        self.canvas.create_text(WIDTH/2, 100, text="Choose any unlocked stage (Enter) • Esc to menu", fill="#8b949e", font=("TkDefaultFont", 10))

        # Draw a simple grid of worlds x stages
        grid_top = 150
        cell_w = 82
        cell_h = 42
        left = (WIDTH - (STAGES_PER_WORLD * cell_w)) / 2

        for w in range(1, WORLDS + 1):
            y = grid_top + (w - 1) * (cell_h + 8)
            self.canvas.create_text(left - 46, y + cell_h/2, text=f"World {w}", fill="#c9d1d9", font=("TkDefaultFont", 10), anchor="e")
            for s in range(1, STAGES_PER_WORLD + 1):
                x = left + (s - 1) * cell_w
                unlocked = self._is_unlocked(w, s)
                cursor = (w, s) == self.level_select_cursor
                fill = "#2d333b" if unlocked else "#161b22"
                outline = "#ffffff" if cursor else "#30363d"
                self.canvas.create_rectangle(x, y, x + cell_w - 8, y + cell_h, fill=fill, outline=outline, width=2 if cursor else 1)
                label = f"{w}-{s}"
                col = "#ffffff" if unlocked else "#6e7681"
                self.canvas.create_text(x + (cell_w - 8)/2, y + cell_h/2, text=label, fill=col, font=("TkDefaultFont", 12, "bold" if cursor else "normal"))

        self.canvas.create_text(WIDTH/2, HEIGHT - 35, text=f"Unlocked up to: {self.unlocked_world}-{self.unlocked_stage}", fill="#8b949e", font=("TkDefaultFont", 10))

    def _render_game(self):
        if self.level is None:
            return
        theme = THEMES[(self.level.world - 1) % len(THEMES)]
        self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill=theme["bg"], outline="")

        # Draw visible tiles
        cam = self.camera_x
        col0 = int(cam // TILE)
        col1 = int((cam + WIDTH) // TILE) + 1
        col0 = max(0, col0 - 1)
        col1 = min(self.level.cols - 1, col1 + 1)

        for cy in range(ROWS):
            for cx in range(col0, col1 + 1):
                t = self.level.tile_at(cx, cy)
                if t == EMPTY or t == START:
                    continue
                sx = cx * TILE - cam
                sy = cy * TILE
                if t == SOLID:
                    self.canvas.create_rectangle(sx, sy, sx + TILE, sy + TILE, fill=theme["solid"], outline="")
                elif t == COIN:
                    pad = 9
                    self.canvas.create_oval(sx + pad, sy + pad, sx + TILE - pad, sy + TILE - pad, fill=theme["coin"], outline="")
                elif t == HAZARD:
                    # A simple triangle-ish shape
                    self.canvas.create_polygon(
                        sx + TILE/2, sy + 6,
                        sx + 6, sy + TILE - 6,
                        sx + TILE - 6, sy + TILE - 6,
                        fill=theme["hazard"],
                        outline=""
                    )
                elif t == GOAL:
                    # A gate block at the end
                    self.canvas.create_rectangle(sx + 6, sy + 4, sx + TILE - 6, sy + TILE - 4, fill=theme["goal"], outline="")

        # Enemies
        for e in self.level.enemies:
            if not e.alive:
                continue
            ex = e.x - cam
            ey = e.y
            self.canvas.create_rectangle(ex, ey, ex + ENEMY_W, ey + ENEMY_H, fill=theme["enemy"], outline="")
            # little "eyes"
            self.canvas.create_rectangle(ex + 6, ey + 8, ex + 10, ey + 12, fill="#000000", outline="")
            self.canvas.create_rectangle(ex + ENEMY_W - 10, ey + 8, ex + ENEMY_W - 6, ey + 12, fill="#000000", outline="")

        # Player
        px = self.player.x - cam
        py = self.player.y
        self.canvas.create_rectangle(px, py, px + PLAYER_W, py + PLAYER_H, fill=theme["player"], outline="")
        # cat ears
        self.canvas.create_polygon(px + 5, py + 6, px + 10, py, px + 15, py + 6, fill=theme["player"], outline="")
        self.canvas.create_polygon(px + PLAYER_W - 5, py + 6, px + PLAYER_W - 10, py, px + PLAYER_W - 15, py + 6, fill=theme["player"], outline="")

        # HUD
        self.canvas.create_text(12, 10, text=f"World {self.level.world}-{self.level.stage}", fill="#ffffff", anchor="nw", font=("TkDefaultFont", 11, "bold"))
        self.canvas.create_text(12, 30, text=f"Score: {self.score}", fill="#c9d1d9", anchor="nw", font=("TkDefaultFont", 10))
        self.canvas.create_text(12, 48, text=f"Coins: {self.coins_collected}", fill="#c9d1d9", anchor="nw", font=("TkDefaultFont", 10))
        self.canvas.create_text(WIDTH - 12, 10, text="R: restart  Esc: menu", fill="#8b949e", anchor="ne", font=("TkDefaultFont", 10))

    def _overlay_center(self, text: str):
        self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill="#000000", outline="", stipple="gray50")
        self.canvas.create_text(WIDTH/2, HEIGHT/2, text=text, fill="#ffffff", font=("TkDefaultFont", 16, "bold"), justify="center")

def main():
    # Tkinter ships with most Python installs. If you don't have it:
    # - On Windows/macOS: install official Python from python.org
    # - On Linux: install your distro's tkinter package (often python3-tk)
    app = GameApp()
    app.root.mainloop()

if __name__ == "__main__":
    main()
c
