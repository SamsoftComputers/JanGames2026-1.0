#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  SUPER MARIO 64 - N64-Style Software Renderer                                ║
║  Team Flames / Samsoft / Flames Co.                                          ║
║  Pure Python - No Pygame - 600x400 @60FPS - N64 Physics                      ║
╚══════════════════════════════════════════════════════════════════════════════╝

Controls:
  WASD/Arrows  - Move
  Space        - Jump (tap for single, double, triple jump)
  z            - Ground Pound (in air)
  x            - Long Jump (while running + jump)
  c            - Backflip (while crouching + jump)
  Shift        - Run
  Control      - Crouch
  q/e          - Rotate Camera
  r/f          - Zoom Camera
  1-4          - Warp to Level
  Escape       - Quit
"""

import math as mth
import random
import time
import tkinter as tk
from dataclasses import dataclass
from typing import List, Tuple, Optional
from enum import Enum, auto

# ══════════════════════════════════════════════════════════════════════════════
# N64 CONSTANTS - Auto HDR 600x400 @60FPS
# ══════════════════════════════════════════════════════════════════════════════

WIDTH = 600
HEIGHT = 400
TARGET_FPS = 60

# Colors (N64 16-bit palette feel)
SKY_BLUE = (135, 206, 235)
CASTLE_TAN = (222, 184, 135)
GRASS_GREEN = (34, 139, 34)
WATER_BLUE = (65, 105, 225)
LAVA_ORANGE = (255, 69, 0)
SNOW_WHITE = (250, 250, 255)
COIN_GOLD = (255, 215, 0)
STAR_YELLOW = (255, 255, 100)
MARIO_RED = (255, 0, 0)
MARIO_BLUE = (0, 0, 200)
MARIO_SKIN = (255, 200, 150)
GOOMBA_BROWN = (139, 90, 43)
BOBOMB_BLACK = (30, 30, 30)

# N64 SM64 Physics (authentic values)
GRAVITY = 0.08
MAX_FALL_SPEED = 2.5
WALK_SPEED = 0.15
RUN_SPEED = 0.35
JUMP_FORCE = 0.85
DOUBLE_JUMP_FORCE = 1.0
TRIPLE_JUMP_FORCE = 1.3
LONG_JUMP_FORCE = 0.7
LONG_JUMP_HSPEED = 0.6
BACKFLIP_FORCE = 1.4
GROUND_POUND_SPEED = 1.2

# ══════════════════════════════════════════════════════════════════════════════
# VECTOR & MATRIX MATH (N64 RSP style)
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class Vec3:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def __add__(self, o): return Vec3(self.x + o.x, self.y + o.y, self.z + o.z)
    def __sub__(self, o): return Vec3(self.x - o.x, self.y - o.y, self.z - o.z)
    def __mul__(self, n): return Vec3(self.x * n, self.y * n, self.z * n) if isinstance(n, (int, float)) else Vec3(self.x * n.x, self.y * n.y, self.z * n.z)
    def __rmul__(self, n): return self.__mul__(n)
    def __truediv__(self, n): return Vec3(self.x / n, self.y / n, self.z / n)
    def __neg__(self): return Vec3(-self.x, -self.y, -self.z)
    def dot(self, o): return self.x * o.x + self.y * o.y + self.z * o.z
    def cross(self, o): return Vec3(self.y * o.z - self.z * o.y, self.z * o.x - self.x * o.z, self.x * o.y - self.y * o.x)
    def length(self): return mth.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)
    def length_xz(self): return mth.sqrt(self.x * self.x + self.z * self.z)
    def norm(self):
        l = self.length()
        return Vec3(0, 0, 0) if l < 1e-8 else self / l
    def copy(self): return Vec3(self.x, self.y, self.z)


class Mat4:
    def __init__(self):
        self.m = [[1 if i == j else 0 for j in range(4)] for i in range(4)]

    @staticmethod
    def identity(): return Mat4()

    @staticmethod
    def translation(x, y, z):
        m = Mat4()
        m.m[3][0], m.m[3][1], m.m[3][2] = x, y, z
        return m

    @staticmethod
    def rotation_y(angle):
        m = Mat4()
        c, s = mth.cos(angle), mth.sin(angle)
        m.m[0][0], m.m[0][2], m.m[2][0], m.m[2][2] = c, s, -s, c
        return m

    @staticmethod
    def look_at(eye: Vec3, target: Vec3, up: Vec3):
        f = (target - eye).norm()
        r = f.cross(up).norm()
        u = r.cross(f)
        m = Mat4()
        m.m[0][0], m.m[1][0], m.m[2][0] = r.x, r.y, r.z
        m.m[0][1], m.m[1][1], m.m[2][1] = u.x, u.y, u.z
        m.m[0][2], m.m[1][2], m.m[2][2] = -f.x, -f.y, -f.z
        m.m[3][0], m.m[3][1], m.m[3][2] = -r.dot(eye), -u.dot(eye), f.dot(eye)
        return m

    @staticmethod
    def perspective(fov, aspect, near, far):
        f = 1.0 / mth.tan(fov / 2.0)
        m = Mat4()
        m.m[0][0] = f / aspect
        m.m[1][1] = f
        m.m[2][2] = (far + near) / (near - far)
        m.m[2][3] = -1
        m.m[3][2] = (2 * far * near) / (near - far)
        m.m[3][3] = 0
        return m

    def __mul__(self, other):
        if isinstance(other, Mat4):
            result = Mat4()
            for i in range(4):
                for j in range(4):
                    result.m[i][j] = sum(self.m[i][k] * other.m[k][j] for k in range(4))
            return result
        if isinstance(other, Vec3):
            x = self.m[0][0] * other.x + self.m[1][0] * other.y + self.m[2][0] * other.z + self.m[3][0]
            y = self.m[0][1] * other.x + self.m[1][1] * other.y + self.m[2][1] * other.z + self.m[3][1]
            z = self.m[0][2] * other.x + self.m[1][2] * other.y + self.m[2][2] * other.z + self.m[3][2]
            w = self.m[0][3] * other.x + self.m[1][3] * other.y + self.m[2][3] * other.z + self.m[3][3]
            w = w if abs(w) > 1e-6 else 1e-6
            return Vec3(x / w, y / w, z / w)
        raise NotImplementedError


# ══════════════════════════════════════════════════════════════════════════════
# N64-STYLE SOFTWARE RASTERIZER
# ══════════════════════════════════════════════════════════════════════════════

class N64Renderer:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.framebuffer = bytearray(width * height * 3)
        self.zbuffer = [float('inf')] * (width * height)
        self.view = Mat4.identity()
        self.proj = Mat4.perspective(mth.radians(60), width / height, 0.1, 500)
        self.fog_start = 60
        self.fog_end = 150
        self.fog_color = SKY_BLUE

    def clear(self, color=SKY_BLUE):
        self.fog_color = color
        r, g, b = color
        for i in range(self.width * self.height):
            idx = i * 3
            self.framebuffer[idx] = r
            self.framebuffer[idx + 1] = g
            self.framebuffer[idx + 2] = b
            self.zbuffer[i] = float('inf')

    def set_view(self, view_matrix):
        self.view = view_matrix

    def set_pixel(self, x, y, z, color):
        if 0 <= x < self.width and 0 <= y < self.height:
            idx = y * self.width + x
            if z < self.zbuffer[idx]:
                self.zbuffer[idx] = z
                pidx = idx * 3
                self.framebuffer[pidx] = min(255, max(0, int(color[0])))
                self.framebuffer[pidx + 1] = min(255, max(0, int(color[1])))
                self.framebuffer[pidx + 2] = min(255, max(0, int(color[2])))

    def project_vertex(self, v: Vec3):
        view_pos = self.view * v
        if view_pos.z > -0.1:
            return None, view_pos
        proj_pos = self.proj * view_pos
        sx = int((proj_pos.x + 1) * 0.5 * self.width)
        sy = int((1 - proj_pos.y) * 0.5 * self.height)
        return (sx, sy, -view_pos.z), view_pos

    def apply_fog(self, color, depth):
        if depth < self.fog_start: return color
        if depth > self.fog_end: return self.fog_color
        t = (depth - self.fog_start) / (self.fog_end - self.fog_start)
        return (int(color[0] + (self.fog_color[0] - color[0]) * t),
                int(color[1] + (self.fog_color[1] - color[1]) * t),
                int(color[2] + (self.fog_color[2] - color[2]) * t))

    def draw_triangle_flat(self, p1, p2, p3, color):
        pts = sorted([p1, p2, p3], key=lambda p: p[1])
        x0, y0, z0 = pts[0]
        x1, y1, z1 = pts[1]
        x2, y2, z2 = pts[2]
        if y0 == y2: return
        avg_z = (z0 + z1 + z2) / 3
        shaded_color = self.apply_fog(color, avg_z)

        def interp(y, ys, ye, vs, ve):
            return vs if ye == ys else vs + (y - ys) / (ye - ys) * (ve - vs)

        for y in range(max(0, int(y0)), min(self.height - 1, int(y2)) + 1):
            if y < y1:
                xa, za = interp(y, y0, y2, x0, x2), interp(y, y0, y2, z0, z2)
                xb = interp(y, y0, y1, x0, x1) if y1 != y0 else x0
                zb = interp(y, y0, y1, z0, z1) if y1 != y0 else z0
            else:
                xa, za = interp(y, y0, y2, x0, x2), interp(y, y0, y2, z0, z2)
                xb = interp(y, y1, y2, x1, x2) if y2 != y1 else x1
                zb = interp(y, y1, y2, z1, z2) if y2 != y1 else z1
            if xa > xb: xa, xb, za, zb = xb, xa, zb, za
            for x in range(max(0, int(xa)), min(self.width - 1, int(xb)) + 1):
                t = (x - xa) / (xb - xa) if xb != xa else 0
                self.set_pixel(x, y, za + t * (zb - za), shaded_color)

    def draw_quad(self, v1, v2, v3, v4, color):
        p1, _ = self.project_vertex(v1)
        p2, _ = self.project_vertex(v2)
        p3, _ = self.project_vertex(v3)
        p4, _ = self.project_vertex(v4)
        if p1 and p2 and p3: self.draw_triangle_flat(p1, p2, p3, color)
        if p1 and p3 and p4: self.draw_triangle_flat(p1, p3, p4, color)

    def draw_box(self, center: Vec3, size: Vec3, color, rotation_y=0):
        hx, hy, hz = size.x / 2, size.y / 2, size.z / 2
        local_verts = [Vec3(-hx, -hy, -hz), Vec3(hx, -hy, -hz), Vec3(hx, hy, -hz), Vec3(-hx, hy, -hz),
                       Vec3(-hx, -hy, hz), Vec3(hx, -hy, hz), Vec3(hx, hy, hz), Vec3(-hx, hy, hz)]
        cos_r, sin_r = mth.cos(rotation_y), mth.sin(rotation_y)
        verts = [Vec3(v.x * cos_r - v.z * sin_r + center.x, v.y + center.y, v.x * sin_r + v.z * cos_r + center.z) for v in local_verts]
        faces = [(0, 1, 2, 3, 0.8), (5, 4, 7, 6, 0.8), (4, 0, 3, 7, 0.6), (1, 5, 6, 2, 0.6), (3, 2, 6, 7, 1.0), (4, 5, 1, 0, 0.5)]
        for i0, i1, i2, i3, shade in faces:
            self.draw_quad(verts[i0], verts[i1], verts[i2], verts[i3], tuple(int(c * shade) for c in color))

    def draw_cylinder(self, center: Vec3, radius: float, height: float, color, segments=8):
        hy = height / 2
        top_verts = [Vec3(center.x + radius * mth.cos(2 * mth.pi * i / segments), center.y + hy,
                         center.z + radius * mth.sin(2 * mth.pi * i / segments)) for i in range(segments)]
        bot_verts = [Vec3(center.x + radius * mth.cos(2 * mth.pi * i / segments), center.y - hy,
                         center.z + radius * mth.sin(2 * mth.pi * i / segments)) for i in range(segments)]
        for i in range(segments):
            ni = (i + 1) % segments
            shade = 0.6 + 0.4 * abs(mth.cos(2 * mth.pi * i / segments))
            self.draw_quad(bot_verts[i], bot_verts[ni], top_verts[ni], top_verts[i], tuple(int(c * shade) for c in color))

    def draw_sphere_approx(self, center: Vec3, radius: float, color, lat_divs=5, lon_divs=6):
        verts = []
        for i in range(lat_divs + 1):
            lat = mth.pi * i / lat_divs - mth.pi / 2
            for j in range(lon_divs):
                lon = 2 * mth.pi * j / lon_divs
                verts.append(Vec3(center.x + radius * mth.cos(lat) * mth.cos(lon),
                                  center.y + radius * mth.sin(lat),
                                  center.z + radius * mth.cos(lat) * mth.sin(lon)))
        for i in range(lat_divs):
            for j in range(lon_divs):
                i0, i1 = i * lon_divs + j, i * lon_divs + (j + 1) % lon_divs
                i2, i3 = (i + 1) * lon_divs + (j + 1) % lon_divs, (i + 1) * lon_divs + j
                shade = 0.5 + 0.5 * (i / lat_divs)
                self.draw_quad(verts[i0], verts[i1], verts[i2], verts[i3], tuple(int(c * shade) for c in color))

    def draw_ground_plane(self, y, size, color):
        hs = size / 2
        self.draw_quad(Vec3(-hs, y, -hs), Vec3(hs, y, -hs), Vec3(hs, y, hs), Vec3(-hs, y, hs), color)

    def get_ppm_data(self) -> bytes:
        return f"P6\n{self.width} {self.height}\n255\n".encode() + bytes(self.framebuffer)


# ══════════════════════════════════════════════════════════════════════════════
# GAME ENTITIES
# ══════════════════════════════════════════════════════════════════════════════

class MarioState(Enum):
    IDLE = auto()
    WALKING = auto()
    RUNNING = auto()
    JUMPING = auto()
    DOUBLE_JUMPING = auto()
    TRIPLE_JUMPING = auto()
    FALLING = auto()
    CROUCHING = auto()
    GROUND_POUNDING = auto()
    GROUND_POUND_LAND = auto()
    LONG_JUMPING = auto()
    BACKFLIPPING = auto()
    HURT = auto()
    DEAD = auto()


class Mario:
    def __init__(self, pos: Vec3):
        self.pos = pos.copy()
        self.vel = Vec3()
        self.facing = 0
        self.state = MarioState.IDLE
        self.on_ground = False
        self.jump_count = 0
        self.jump_timer = 0
        self.invincible_timer = 0
        self.ground_pound_timer = 0
        self.health = 8
        self.max_health = 8
        self.coins = 0
        self.stars = 0
        self.lives = 4
        self.anim_timer = 0

    def update(self, dt, keys: dict, level):
        self.anim_timer += dt
        if self.invincible_timer > 0: self.invincible_timer -= dt

        if self.state == MarioState.DEAD:
            self.vel.y -= GRAVITY * dt * 60
            self.pos.y += self.vel.y * dt * 60
            return 'respawn' if self.pos.y < -50 else None

        if self.state == MarioState.HURT:
            self.vel.y -= GRAVITY * dt * 60
            self.pos += self.vel * dt * 60
            if self.on_ground and self.vel.y <= 0: self.state = MarioState.IDLE
            self._check_ground(level)
            return None

        if self.state == MarioState.GROUND_POUND_LAND:
            self.ground_pound_timer -= dt
            if self.ground_pound_timer <= 0: self.state = MarioState.IDLE
            return None

        # Input
        move_x = (1 if keys.get('d') or keys.get('Right') else 0) - (1 if keys.get('a') or keys.get('Left') else 0)
        move_z = (1 if keys.get('s') or keys.get('Down') else 0) - (1 if keys.get('w') or keys.get('Up') else 0)
        move_input = Vec3(move_x, 0, move_z)
        running = keys.get('Shift_L') or keys.get('Shift_R')
        crouching = keys.get('Control_L') or keys.get('Control_R')

        if self.on_ground:
            self.jump_timer -= dt
            if self.jump_timer <= 0: self.jump_count = 0

        if self.on_ground:
            if self.state in (MarioState.JUMPING, MarioState.DOUBLE_JUMPING, MarioState.TRIPLE_JUMPING,
                             MarioState.FALLING, MarioState.LONG_JUMPING, MarioState.BACKFLIPPING):
                self.state = MarioState.IDLE
            if self.state == MarioState.GROUND_POUNDING:
                self.state = MarioState.GROUND_POUND_LAND
                self.ground_pound_timer = 0.3
                self.vel = Vec3()
                return None
            if crouching: self.state = MarioState.CROUCHING
            elif move_input.length() > 0.1: self.state = MarioState.RUNNING if running else MarioState.WALKING
            else: self.state = MarioState.IDLE

        if self.state not in (MarioState.GROUND_POUNDING, MarioState.GROUND_POUND_LAND):
            if move_input.length() > 0.1:
                move_input = move_input.norm()
                target_angle = mth.atan2(move_input.x, move_input.z)
                angle_diff = target_angle - self.facing
                while angle_diff > mth.pi: angle_diff -= 2 * mth.pi
                while angle_diff < -mth.pi: angle_diff += 2 * mth.pi
                self.facing += angle_diff * min(1.0, 10 * dt)
                speed = LONG_JUMP_HSPEED if self.state == MarioState.LONG_JUMPING else (RUN_SPEED if running else WALK_SPEED)
                if not self.on_ground: speed *= 0.3
                self.vel.x = mth.sin(self.facing) * speed
                self.vel.z = mth.cos(self.facing) * speed
            else:
                friction = 0.85 if self.on_ground else 0.98
                self.vel.x *= friction
                self.vel.z *= friction

        if not self.on_ground:
            self.vel.y -= GRAVITY * dt * 60
            if self.vel.y < -MAX_FALL_SPEED: self.vel.y = -MAX_FALL_SPEED

        self.pos += self.vel * dt * 60
        self._check_ground(level)
        self._check_walls(level)
        if self.pos.y < -20: self.take_damage(1, fall_death=True)
        return None

    def handle_jump(self, keys):
        if self.state in (MarioState.DEAD, MarioState.HURT): return
        running = keys.get('Shift_L') or keys.get('Shift_R')
        crouching = keys.get('Control_L') or keys.get('Control_R')

        if self.on_ground:
            if running and self.vel.length_xz() > WALK_SPEED * 0.8:
                self.state = MarioState.LONG_JUMPING
                self.vel.y = LONG_JUMP_FORCE
                self.vel.x = mth.sin(self.facing) * LONG_JUMP_HSPEED
                self.vel.z = mth.cos(self.facing) * LONG_JUMP_HSPEED
                self.on_ground = False
                return
            if crouching:
                self.state = MarioState.BACKFLIPPING
                self.vel.y = BACKFLIP_FORCE
                self.vel.x = -mth.sin(self.facing) * 0.2
                self.vel.z = -mth.cos(self.facing) * 0.2
                self.on_ground = False
                return
            self.jump_count += 1
            if self.jump_count >= 3 and self.jump_timer > 0:
                self.state = MarioState.TRIPLE_JUMPING
                self.vel.y = TRIPLE_JUMP_FORCE
                self.jump_count = 0
            elif self.jump_count == 2 and self.jump_timer > 0:
                self.state = MarioState.DOUBLE_JUMPING
                self.vel.y = DOUBLE_JUMP_FORCE
            else:
                self.state = MarioState.JUMPING
                self.vel.y = JUMP_FORCE
                self.jump_count = 1
            self.jump_timer = 0.4
            self.on_ground = False

    def handle_ground_pound(self):
        if not self.on_ground and self.state not in (MarioState.GROUND_POUNDING, MarioState.DEAD, MarioState.HURT):
            self.state = MarioState.GROUND_POUNDING
            self.vel.x = self.vel.z = 0
            self.vel.y = -GROUND_POUND_SPEED

    def _check_ground(self, level):
        ground_y = level.get_ground_height(self.pos.x, self.pos.z)
        if self.pos.y <= ground_y:
            self.pos.y = ground_y
            self.vel.y = 0
            self.on_ground = True
        else:
            self.on_ground = False

    def _check_walls(self, level):
        for wall in level.walls:
            if wall.collides(self.pos, 0.5):
                self.pos += wall.get_push_vector(self.pos)
                if not self.on_ground and self.vel.y < 0: self.vel.y *= 0.8

    def take_damage(self, amount, fall_death=False):
        if self.invincible_timer > 0 and not fall_death: return
        self.health -= amount
        if self.health <= 0 or fall_death:
            self.state = MarioState.DEAD
            self.vel = Vec3(0, 1.2, 0)
            self.lives -= 1
        else:
            self.state = MarioState.HURT
            self.vel = Vec3(-mth.sin(self.facing) * 0.3, 0.5, -mth.cos(self.facing) * 0.3)
            self.invincible_timer = 2.0

    def collect_coin(self):
        self.coins += 1
        if self.coins >= 100:
            self.coins -= 100
            self.lives += 1

    def collect_star(self):
        self.stars += 1
        self.health = self.max_health

    def draw(self, renderer: N64Renderer):
        if self.state == MarioState.DEAD: return
        if self.invincible_timer > 0 and int(self.invincible_timer * 10) % 2 == 0: return

        rot = self.facing
        bob = mth.sin(self.anim_timer * 15) * 0.1 if self.state in (MarioState.WALKING, MarioState.RUNNING) else 0
        crouch_offset = -0.3 if self.state == MarioState.CROUCHING else 0
        spin = self.anim_timer * 15 if self.state == MarioState.BACKFLIPPING else (self.anim_timer * 10 if self.state == MarioState.TRIPLE_JUMPING else 0)

        # Body
        renderer.draw_box(Vec3(self.pos.x, self.pos.y + 0.7 + bob + crouch_offset, self.pos.z), Vec3(0.6, 0.7, 0.4), MARIO_BLUE, rot + spin)
        # Head
        renderer.draw_sphere_approx(Vec3(self.pos.x, self.pos.y + 1.4 + bob + crouch_offset, self.pos.z), 0.35, MARIO_SKIN, 4, 5)
        # Cap
        renderer.draw_box(Vec3(self.pos.x, self.pos.y + 1.6 + bob + crouch_offset, self.pos.z), Vec3(0.5, 0.2, 0.5), MARIO_RED, rot + spin)
        # Legs
        ls = 0.15
        renderer.draw_box(Vec3(self.pos.x - mth.cos(rot) * ls, self.pos.y + 0.2, self.pos.z + mth.sin(rot) * ls), Vec3(0.25, 0.4, 0.25), MARIO_BLUE, rot)
        renderer.draw_box(Vec3(self.pos.x + mth.cos(rot) * ls, self.pos.y + 0.2, self.pos.z - mth.sin(rot) * ls), Vec3(0.25, 0.4, 0.25), MARIO_BLUE, rot)


class Coin:
    def __init__(self, pos: Vec3):
        self.pos = pos.copy()
        self.collected = False
        self.spin = random.uniform(0, mth.pi * 2)

    def update(self, dt): self.spin += dt * 5
    def check_collect(self, mario: Mario):
        if self.collected: return False
        if (self.pos - mario.pos).length() < 1.5:
            self.collected = True
            mario.collect_coin()
            return True
        return False

    def draw(self, renderer: N64Renderer):
        if not self.collected:
            renderer.draw_box(Vec3(self.pos.x, self.pos.y + mth.sin(self.spin * 2) * 0.1, self.pos.z), Vec3(0.5, 0.5, 0.1), COIN_GOLD, self.spin)


class Star:
    def __init__(self, pos: Vec3):
        self.pos = pos.copy()
        self.collected = False
        self.spin = self.bob = 0

    def update(self, dt):
        self.spin += dt * 3
        self.bob += dt * 4

    def check_collect(self, mario: Mario):
        if self.collected: return False
        if (self.pos - mario.pos).length() < 2:
            self.collected = True
            mario.collect_star()
            return True
        return False

    def draw(self, renderer: N64Renderer):
        if not self.collected:
            renderer.draw_sphere_approx(Vec3(self.pos.x, self.pos.y + mth.sin(self.bob) * 0.5, self.pos.z), 0.6, STAR_YELLOW, 4, 5)


class Enemy:
    def __init__(self, pos: Vec3, enemy_type='goomba'):
        self.pos = pos.copy()
        self.vel = Vec3()
        self.enemy_type = enemy_type
        self.alive = True
        self.squish_timer = 0
        self.facing = random.uniform(0, mth.pi * 2)
        self.walk_timer = 0
        self.speed = 0.05 if enemy_type == 'goomba' else 0.03
        self.color = GOOMBA_BROWN if enemy_type == 'goomba' else BOBOMB_BLACK

    def update(self, dt, mario: Mario, level):
        if not self.alive:
            self.squish_timer -= dt
            return
        self.walk_timer += dt
        to_mario = mario.pos - self.pos
        dist = to_mario.length_xz()
        if 2 < dist < 15:
            target_angle = mth.atan2(to_mario.x, to_mario.z)
            angle_diff = target_angle - self.facing
            while angle_diff > mth.pi: angle_diff -= 2 * mth.pi
            while angle_diff < -mth.pi: angle_diff += 2 * mth.pi
            self.facing += angle_diff * 2 * dt
        elif random.random() < 0.01:
            self.facing += random.uniform(-0.5, 0.5)
        self.vel.x = mth.sin(self.facing) * self.speed
        self.vel.z = mth.cos(self.facing) * self.speed
        self.pos += self.vel * dt * 60
        self.pos.y = level.get_ground_height(self.pos.x, self.pos.z)

    def check_collision(self, mario: Mario):
        if not self.alive: return
        to_mario = mario.pos - self.pos
        if to_mario.length_xz() < 1.0:
            if mario.vel.y < -0.1 and mario.pos.y > self.pos.y + 0.5:
                self.alive = False
                self.squish_timer = 0.5
                mario.vel.y = 0.6
            elif mario.invincible_timer <= 0:
                mario.take_damage(1)

    def draw(self, renderer: N64Renderer):
        if self.squish_timer > 0:
            renderer.draw_box(self.pos + Vec3(0, 0.1, 0), Vec3(1.0, 0.2, 1.0), self.color)
            return
        if not self.alive: return
        bob = mth.sin(self.walk_timer * 10) * 0.05
        renderer.draw_sphere_approx(self.pos + Vec3(0, 0.5 + bob, 0), 0.5, self.color, 4, 5)
        renderer.draw_box(self.pos + Vec3(-0.2, 0.15, 0), Vec3(0.2, 0.3, 0.25), (80, 50, 20))
        renderer.draw_box(self.pos + Vec3(0.2, 0.15, 0), Vec3(0.2, 0.3, 0.25), (80, 50, 20))


class Wall:
    def __init__(self, pos: Vec3, size: Vec3, color):
        self.pos, self.size, self.color = pos, size, color
        self.min_x, self.max_x = pos.x - size.x / 2, pos.x + size.x / 2
        self.min_z, self.max_z = pos.z - size.z / 2, pos.z + size.z / 2

    def collides(self, point: Vec3, radius: float):
        closest_x = max(self.min_x, min(point.x, self.max_x))
        closest_z = max(self.min_z, min(point.z, self.max_z))
        dist = mth.sqrt((point.x - closest_x) ** 2 + (point.z - closest_z) ** 2)
        return dist < radius and point.y < self.pos.y + self.size.y / 2

    def get_push_vector(self, point: Vec3):
        closest_x = max(self.min_x, min(point.x, self.max_x))
        closest_z = max(self.min_z, min(point.z, self.max_z))
        dx, dz = point.x - closest_x, point.z - closest_z
        dist = mth.sqrt(dx * dx + dz * dz)
        if dist < 0.01:
            dx, dz = point.x - self.pos.x, point.z - self.pos.z
            return Vec3(0.6 if dx > 0 else -0.6, 0, 0) if abs(dx) > abs(dz) else Vec3(0, 0, 0.6 if dz > 0 else -0.6)
        push = 0.55 - dist
        return Vec3(dx / dist * push, 0, dz / dist * push)

    def draw(self, renderer: N64Renderer):
        renderer.draw_box(self.pos, self.size, self.color)


# ══════════════════════════════════════════════════════════════════════════════
# LEVELS
# ══════════════════════════════════════════════════════════════════════════════

class Level:
    def __init__(self, name, sky_color, ground_color):
        self.name = name
        self.sky_color = sky_color
        self.ground_color = ground_color
        self.ground_y = 0
        self.spawn_pos = Vec3(0, 1, 0)
        self.coins: List[Coin] = []
        self.stars: List[Star] = []
        self.enemies: List[Enemy] = []
        self.walls: List[Wall] = []
        self.platforms: List[dict] = []
        self.decorations: List[dict] = []

    def get_ground_height(self, x, z):
        height = self.ground_y
        for plat in self.platforms:
            pos, size = plat['pos'], plat['size']
            if pos.x - size.x/2 < x < pos.x + size.x/2 and pos.z - size.z/2 < z < pos.z + size.z/2:
                plat_top = pos.y + size.y/2
                if plat_top > height: height = plat_top
        return height

    def update(self, dt, mario: Mario):
        for coin in self.coins:
            coin.update(dt)
            coin.check_collect(mario)
        for star in self.stars:
            star.update(dt)
            star.check_collect(mario)
        for enemy in self.enemies:
            enemy.update(dt, mario, self)
            enemy.check_collision(mario)

    def draw(self, renderer: N64Renderer):
        renderer.draw_ground_plane(self.ground_y - 0.1, 500, self.ground_color)
        for plat in self.platforms:
            renderer.draw_box(plat['pos'], plat['size'], plat['color'])
        for wall in self.walls: wall.draw(renderer)
        for dec in self.decorations:
            if dec['type'] == 'tree':
                renderer.draw_cylinder(dec['pos'], 0.5, 3, (100, 70, 40), 6)
                renderer.draw_sphere_approx(dec['pos'] + Vec3(0, 3, 0), 2, (34, 139, 34), 4, 5)
            elif dec['type'] == 'box':
                renderer.draw_box(dec['pos'], dec['size'], dec.get('color', (150, 150, 150)))
            elif dec['type'] == 'pillar':
                renderer.draw_cylinder(dec['pos'], dec.get('radius', 1), dec.get('height', 5), dec.get('color', (200, 200, 200)), 8)
        for coin in self.coins: coin.draw(renderer)
        for star in self.stars: star.draw(renderer)
        for enemy in self.enemies: enemy.draw(renderer)


def create_castle_grounds():
    level = Level("Castle Grounds", SKY_BLUE, GRASS_GREEN)
    level.spawn_pos = Vec3(0, 1, 30)
    level.walls.append(Wall(Vec3(0, 10, -30), Vec3(40, 20, 30), CASTLE_TAN))
    level.decorations.append({'type': 'pillar', 'pos': Vec3(-18, 12, -15), 'radius': 4, 'height': 24, 'color': CASTLE_TAN})
    level.decorations.append({'type': 'pillar', 'pos': Vec3(18, 12, -15), 'radius': 4, 'height': 24, 'color': CASTLE_TAN})
    level.platforms.append({'pos': Vec3(0, 0.5, 10), 'size': Vec3(8, 1, 20), 'color': (139, 119, 101)})
    for i in range(8):
        level.decorations.append({'type': 'tree', 'pos': Vec3(random.uniform(-60, 60), 0, random.uniform(20, 80))})
    for i in range(20):
        angle = i * mth.pi * 2 / 20
        level.coins.append(Coin(Vec3(mth.cos(angle) * 25, 1, mth.sin(angle) * 25 + 20)))
    level.stars.append(Star(Vec3(0, 22, -30)))
    level.enemies.append(Enemy(Vec3(15, 0, 40), 'goomba'))
    level.enemies.append(Enemy(Vec3(-15, 0, 35), 'goomba'))
    level.enemies.append(Enemy(Vec3(0, 0, 60), 'goomba'))
    return level


def create_bob_omb_battlefield():
    level = Level("Bob-omb Battlefield", (135, 206, 250), GRASS_GREEN)
    level.spawn_pos = Vec3(0, 1, 0)
    level.platforms.append({'pos': Vec3(0, 5, -50), 'size': Vec3(30, 10, 30), 'color': (139, 119, 101)})
    level.platforms.append({'pos': Vec3(0, 12, -50), 'size': Vec3(20, 4, 20), 'color': (139, 119, 101)})
    level.platforms.append({'pos': Vec3(0, 17, -50), 'size': Vec3(10, 6, 10), 'color': (139, 119, 101)})
    for i in range(16):
        angle = i * mth.pi * 2 / 16
        level.coins.append(Coin(Vec3(mth.cos(angle) * 20, 1, mth.sin(angle) * 20 - 50)))
    level.stars.append(Star(Vec3(0, 22, -50)))
    for i in range(5):
        level.enemies.append(Enemy(Vec3(random.uniform(-30, 30), 0, random.uniform(-30, 30)), 'bobomb'))
    for i in range(6):
        level.decorations.append({'type': 'tree', 'pos': Vec3(random.uniform(-60, 60), 0, random.uniform(-80, 60))})
    return level


def create_cool_cool_mountain():
    level = Level("Cool Cool Mountain", (200, 220, 255), SNOW_WHITE)
    level.spawn_pos = Vec3(0, 25, 0)
    level.platforms.append({'pos': Vec3(0, 24, 0), 'size': Vec3(20, 2, 20), 'color': SNOW_WHITE})
    heights = [20, 16, 12, 8, 4, 0]
    angles = [0, 60, 120, 180, 240, 300]
    for h, a in zip(heights, angles):
        rad = mth.radians(a)
        x, z = mth.cos(rad) * (25 - h/2), mth.sin(rad) * (25 - h/2)
        level.platforms.append({'pos': Vec3(x, h, z), 'size': Vec3(10, 2, 10), 'color': (220, 230, 255)})
        level.coins.append(Coin(Vec3(x, h + 2, z)))
    level.stars.append(Star(Vec3(0, 2, -30)))
    for i in range(3):
        level.enemies.append(Enemy(Vec3(random.uniform(-20, 20), 0, random.uniform(-20, 20)), 'goomba'))
    return level


def create_lethal_lava_land():
    level = Level("Lethal Lava Land", (80, 40, 40), LAVA_ORANGE)
    level.spawn_pos = Vec3(0, 3, 0)
    level.ground_y = -2
    level.platforms.append({'pos': Vec3(0, 2, 0), 'size': Vec3(10, 4, 10), 'color': (80, 80, 80)})
    plat_data = [(Vec3(12, 2, 0), Vec3(6, 4, 6)), (Vec3(20, 3, 8), Vec3(5, 4, 5)), (Vec3(15, 4, 18), Vec3(6, 4, 6)),
                 (Vec3(0, 5, 25), Vec3(8, 4, 8)), (Vec3(-15, 4, 18), Vec3(6, 4, 6)), (Vec3(-20, 3, 5), Vec3(5, 4, 5)),
                 (Vec3(-12, 2, -5), Vec3(6, 4, 6)), (Vec3(0, 6, -20), Vec3(12, 6, 12))]
    for pos, size in plat_data:
        level.platforms.append({'pos': pos, 'size': size, 'color': (60, 60, 60)})
        level.coins.append(Coin(Vec3(pos.x, pos.y + size.y/2 + 1, pos.z)))
    level.platforms.append({'pos': Vec3(0, 12, -20), 'size': Vec3(8, 6, 8), 'color': (50, 50, 50)})
    level.stars.append(Star(Vec3(0, 17, -20)))
    level.enemies.append(Enemy(Vec3(0, 2.5, 25), 'goomba'))
    return level


# ══════════════════════════════════════════════════════════════════════════════
# CAMERA
# ══════════════════════════════════════════════════════════════════════════════

class Camera:
    def __init__(self):
        self.distance = 15
        self.height = 6
        self.angle = 0
        self.target_distance = 15

    def update(self, dt, keys, mario: Mario):
        if keys.get('q'): self.angle -= 2.5 * dt
        if keys.get('e'): self.angle += 2.5 * dt
        if keys.get('r'): self.target_distance = max(5, self.target_distance - 15 * dt)
        if keys.get('f'): self.target_distance = min(40, self.target_distance + 15 * dt)
        self.distance += (self.target_distance - self.distance) * 5 * dt

    def get_position(self, mario: Mario) -> Vec3:
        return Vec3(mario.pos.x + mth.sin(self.angle) * self.distance, mario.pos.y + self.height,
                    mario.pos.z + mth.cos(self.angle) * self.distance)

    def get_view_matrix(self, mario: Mario) -> Mat4:
        return Mat4.look_at(self.get_position(mario), mario.pos + Vec3(0, 1.5, 0), Vec3(0, 1, 0))


# ══════════════════════════════════════════════════════════════════════════════
# HUD (Pure Tkinter Canvas)
# ══════════════════════════════════════════════════════════════════════════════

class HUD:
    def draw(self, canvas, mario: Mario, level: Level, fps: float):
        # Health
        canvas.create_oval(35, 20, 105, 90, outline='black', width=2)
        for i in range(mario.max_health):
            angle_start = 90 - (i * 360 / mario.max_health)
            color = '#32C832' if i < mario.health else '#505050'
            if mario.health <= 2 and i < mario.health: color = '#C8C832' if mario.health > 1 else '#C83232'
            canvas.create_arc(40, 25, 100, 85, start=angle_start, extent=-360/mario.max_health, fill=color, outline='')

        # Lives
        canvas.create_text(130, 55, text=f"x {mario.lives}", fill='white', font=('Arial', 14, 'bold'), anchor='w')

        # Coins
        canvas.create_oval(WIDTH - 165, 30, WIDTH - 135, 60, fill='#FFD700', outline='#DAA520')
        canvas.create_text(WIDTH - 120, 45, text=f"x {mario.coins}", fill='white', font=('Arial', 14, 'bold'), anchor='w')

        # Stars
        canvas.create_oval(WIDTH - 165, 70, WIDTH - 135, 100, fill='#FFFF64', outline='#DAA520')
        canvas.create_text(WIDTH - 120, 85, text=f"x {mario.stars}", fill='white', font=('Arial', 14, 'bold'), anchor='w')

        # Level name
        canvas.create_text(WIDTH // 2, 20, text=level.name, fill='white', font=('Arial', 12, 'bold'))

        # FPS
        canvas.create_text(15, HEIGHT - 15, text=f"FPS: {fps:.0f}", fill='#C8C8C8', font=('Arial', 10), anchor='w')

        # Controls
        canvas.create_text(WIDTH // 2, HEIGHT - 15, text="WASD:Move Space:Jump Z:Pound X:LongJump C:Backflip Q/E:Camera 1-4:Levels", fill='#B4B4B4', font=('Arial', 9))


# ══════════════════════════════════════════════════════════════════════════════
# MAIN GAME (Pure Tkinter)
# ══════════════════════════════════════════════════════════════════════════════

class Game:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Super Mario 64 - N64 Style (Team Flames)")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(self.root, width=WIDTH, height=HEIGHT, bg='black', highlightthickness=0)
        self.canvas.pack()

        self.renderer = N64Renderer(WIDTH, HEIGHT)
        self.hud = HUD()

        self.levels = [create_castle_grounds(), create_bob_omb_battlefield(), create_cool_cool_mountain(), create_lethal_lava_land()]
        self.current_level_idx = 0
        self.current_level = self.levels[0]

        self.mario = Mario(self.current_level.spawn_pos)
        self.camera = Camera()

        self.keys = {}
        self.running = True
        self.last_time = time.time()
        self.fps = TARGET_FPS

        self.root.bind('<KeyPress>', self.on_key_press)
        self.root.bind('<KeyRelease>', self.on_key_release)
        self.root.protocol("WM_DELETE_WINDOW", self.quit)

        self.photo = None

    def on_key_press(self, event):
        self.keys[event.keysym] = True
        if event.keysym == 'space': self.mario.handle_jump(self.keys)
        elif event.keysym == 'z': self.mario.handle_ground_pound()
        elif event.keysym == 'x' and (self.keys.get('Shift_L') or self.keys.get('Shift_R')): self.mario.handle_jump(self.keys)
        elif event.keysym in '1234': self.change_level(int(event.keysym) - 1)
        elif event.keysym == 'Escape': self.quit()

    def on_key_release(self, event):
        self.keys[event.keysym] = False

    def change_level(self, idx):
        if 0 <= idx < len(self.levels):
            self.current_level_idx = idx
            self.current_level = self.levels[idx]
            self.mario = Mario(self.current_level.spawn_pos)
            self.camera = Camera()

    def respawn_mario(self):
        self.mario = Mario(self.current_level.spawn_pos)
        self.mario.lives = max(0, self.mario.lives)
        if self.mario.lives <= 0:
            self.mario.lives = 4
            self.mario.coins = 0
            self.mario.stars = 0

    def quit(self):
        self.running = False
        self.root.destroy()

    def update(self, dt):
        result = self.mario.update(dt, self.keys, self.current_level)
        if result == 'respawn': self.respawn_mario()
        self.camera.update(dt, self.keys, self.mario)
        self.current_level.update(dt, self.mario)

    def draw(self):
        view = self.camera.get_view_matrix(self.mario)
        self.renderer.set_view(view)
        self.renderer.clear(self.current_level.sky_color)

        self.current_level.draw(self.renderer)
        self.mario.draw(self.renderer)

        # Convert framebuffer to PhotoImage
        ppm_data = self.renderer.get_ppm_data()
        self.photo = tk.PhotoImage(data=ppm_data)

        self.canvas.delete('all')
        self.canvas.create_image(0, 0, anchor='nw', image=self.photo)
        self.hud.draw(self.canvas, self.mario, self.current_level, self.fps)

    def game_loop(self):
        if not self.running: return

        current_time = time.time()
        dt = current_time - self.last_time
        self.last_time = current_time

        # Cap delta time
        dt = min(dt, 0.05)
        self.fps = 1.0 / dt if dt > 0 else TARGET_FPS

        self.update(dt)
        self.draw()

        # Schedule next frame (60fps target)
        delay = max(1, int((1.0 / TARGET_FPS - dt) * 1000))
        self.root.after(delay, self.game_loop)

    def run(self):
        print("""
╔══════════════════════════════════════════════════════════════════════════╗
║  SUPER MARIO 64 - N64 Style Recreation                                   ║
║  Team Flames / Samsoft / Flames Co.                                      ║
╠══════════════════════════════════════════════════════════════════════════╣
║  Controls:                                                               ║
║    WASD/Arrows - Move           Space - Jump (combo for double/triple)   ║
║    Shift - Run                  Ctrl - Crouch                            ║
║    Z - Ground Pound             X - Long Jump (while running)            ║
║    C - Backflip (while crouch)  Q/E - Rotate Camera                      ║
║    R/F - Zoom Camera            1-4 - Change Level                       ║
║    Escape - Quit                                                         ║
╚══════════════════════════════════════════════════════════════════════════╝
        """)
        self.game_loop()
        self.root.mainloop()


# ══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    game = Game()
    game.run()
