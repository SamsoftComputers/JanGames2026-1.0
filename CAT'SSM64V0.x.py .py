#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  SUPER MARIO 64 - Complete Pygame-CE Recreation                              ║
║  Team Flames / Samsoft / Flames Co.                                          ║
║  Software 3D Renderer with Authentic SM64 Physics                            ║
╚══════════════════════════════════════════════════════════════════════════════╝

Controls:
  WASD/Arrows  - Move
  Space        - Jump (tap for single, double, triple jump)
  Z            - Ground Pound (in air)
  X            - Long Jump (while running + jump)
  C            - Backflip (while crouching + jump)
  Shift        - Run
  Ctrl         - Crouch
  Q/E          - Rotate Camera
  R/F          - Zoom Camera
  1-4          - Warp to Level
  ESC          - Quit
"""

import pygame
import math
import random
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict
from enum import Enum, auto

pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

# ══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
SKY_BLUE = (135, 206, 235)
CASTLE_TAN = (222, 184, 135)
GRASS_GREEN = (34, 139, 34)
WATER_BLUE = (65, 105, 225)
LAVA_ORANGE = (255, 69, 0)
SNOW_WHITE = (250, 250, 255)
SAND_YELLOW = (238, 214, 175)
COIN_GOLD = (255, 215, 0)
STAR_YELLOW = (255, 255, 100)
MARIO_RED = (255, 0, 0)
MARIO_BLUE = (0, 0, 200)
MARIO_SKIN = (255, 200, 150)
GOOMBA_BROWN = (139, 90, 43)
BOBOMB_BLACK = (30, 30, 30)
BRICK_RED = (178, 34, 34)

# Physics constants (SM64 authentic-ish)
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
WALL_KICK_FORCE = 0.9
GROUND_POUND_SPEED = 1.2

# ══════════════════════════════════════════════════════════════════════════════
# VECTOR & MATRIX MATH
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class Vec3:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def __add__(self, o):
        return Vec3(self.x + o.x, self.y + o.y, self.z + o.z)

    def __sub__(self, o):
        return Vec3(self.x - o.x, self.y - o.y, self.z - o.z)

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Vec3(self.x * other, self.y * other, self.z * other)
        if isinstance(other, Vec3):
            return Vec3(self.x * other.x, self.y * other.y, self.z * other.z)
        raise TypeError(f"Vec3 * {type(other)} not supported")

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, n):
        return Vec3(self.x / n, self.y / n, self.z / n)

    def __neg__(self):
        return Vec3(-self.x, -self.y, -self.z)

    def dot(self, o):
        return self.x * o.x + self.y * o.y + self.z * o.z

    def cross(self, o):
        return Vec3(
            self.y * o.z - self.z * o.y,
            self.z * o.x - self.x * o.z,
            self.x * o.y - self.y * o.x
        )

    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    def length_xz(self):
        return math.sqrt(self.x * self.x + self.z * self.z)

    def norm(self):
        l = self.length()
        if l < 1e-8:
            return Vec3(0, 0, 0)
        return self / l

    def norm_xz(self):
        l = self.length_xz()
        if l < 1e-8:
            return Vec3(0, 0, 0)
        return Vec3(self.x / l, 0, self.z / l)

    def lerp(self, other, t):
        return self + (other - self) * t

    def copy(self):
        return Vec3(self.x, self.y, self.z)

    def tuple(self):
        return (self.x, self.y, self.z)


class Mat4:
    def __init__(self):
        self.m = [[1 if i == j else 0 for j in range(4)] for i in range(4)]

    @staticmethod
    def identity():
        return Mat4()

    @staticmethod
    def translation(x, y, z):
        m = Mat4()
        m.m[3][0] = x
        m.m[3][1] = y
        m.m[3][2] = z
        return m

    @staticmethod
    def rotation_y(angle):
        m = Mat4()
        c, s = math.cos(angle), math.sin(angle)
        m.m[0][0] = c
        m.m[0][2] = s
        m.m[2][0] = -s
        m.m[2][2] = c
        return m

    @staticmethod
    def rotation_x(angle):
        m = Mat4()
        c, s = math.cos(angle), math.sin(angle)
        m.m[1][1] = c
        m.m[1][2] = -s
        m.m[2][1] = s
        m.m[2][2] = c
        return m

    @staticmethod
    def scale(sx, sy, sz):
        m = Mat4()
        m.m[0][0] = sx
        m.m[1][1] = sy
        m.m[2][2] = sz
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
        m.m[3][0] = -r.dot(eye)
        m.m[3][1] = -u.dot(eye)
        m.m[3][2] = f.dot(eye)
        return m

    @staticmethod
    def perspective(fov, aspect, near, far):
        f = 1.0 / math.tan(fov / 2.0)
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
            if abs(w) < 1e-6:
                w = 1e-6
            return Vec3(x / w, y / w, z / w)
        raise NotImplementedError(f"Mat4 * {type(other)} not supported")


# ══════════════════════════════════════════════════════════════════════════════
# SOUND GENERATOR (Simple synthesized sounds)
# ══════════════════════════════════════════════════════════════════════════════

class SoundGenerator:
    def __init__(self):
        self.sample_rate = 44100
        self.sounds = {}
        self._generate_sounds()

    def _generate_sounds(self):
        # Jump sound - quick rising tone
        self.sounds['jump'] = self._make_tone(0.15, [400, 600, 800], 'square')
        # Double jump
        self.sounds['double_jump'] = self._make_tone(0.15, [500, 750, 1000], 'square')
        # Triple jump
        self.sounds['triple_jump'] = self._make_tone(0.2, [600, 900, 1200, 1400], 'square')
        # Coin
        self.sounds['coin'] = self._make_tone(0.1, [988, 1319], 'sine')
        # Star
        self.sounds['star'] = self._make_tone(0.5, [523, 659, 784, 1047], 'sine')
        # Ground pound
        self.sounds['ground_pound'] = self._make_tone(0.2, [200, 100, 50], 'square')
        # Enemy hit
        self.sounds['enemy_hit'] = self._make_tone(0.15, [300, 200, 100], 'noise')
        # Hurt
        self.sounds['hurt'] = self._make_tone(0.3, [400, 300, 200, 150], 'square')
        # Mama mia (death)
        self.sounds['death'] = self._make_tone(0.5, [400, 350, 300, 250, 200], 'square')
        # Long jump
        self.sounds['long_jump'] = self._make_tone(0.2, [300, 450, 350], 'square')
        # Backflip
        self.sounds['backflip'] = self._make_tone(0.25, [350, 550, 750, 600], 'square')

    def _make_tone(self, duration, frequencies, wave_type='sine'):
        import array
        n_samples = int(self.sample_rate * duration)
        samples_per_freq = n_samples // len(frequencies)
        buf = array.array('h')

        for i, freq in enumerate(frequencies):
            for j in range(samples_per_freq):
                t = j / self.sample_rate
                # Envelope
                env = 1.0 - (i * samples_per_freq + j) / n_samples

                if wave_type == 'sine':
                    val = math.sin(2 * math.pi * freq * t)
                elif wave_type == 'square':
                    val = 1 if math.sin(2 * math.pi * freq * t) > 0 else -1
                elif wave_type == 'noise':
                    val = random.uniform(-1, 1)
                else:
                    val = math.sin(2 * math.pi * freq * t)

                sample = int(val * env * 16000)
                buf.append(sample)
                buf.append(sample)  # Stereo

        return pygame.mixer.Sound(buffer=buf)

    def play(self, name):
        if name in self.sounds:
            self.sounds[name].play()


# ══════════════════════════════════════════════════════════════════════════════
# SOFTWARE 3D RENDERER
# ══════════════════════════════════════════════════════════════════════════════

class Renderer:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.buffer = pygame.Surface((width, height))
        self.zbuffer = [[float('inf')] * width for _ in range(height)]
        self.view = Mat4.identity()
        self.proj = Mat4.perspective(math.radians(60), width / height, 0.1, 500)
        self.fog_start = 80
        self.fog_end = 200
        self.fog_color = SKY_BLUE

    def clear(self, color=SKY_BLUE):
        self.buffer.fill(color)
        self.fog_color = color
        for y in range(self.height):
            for x in range(self.width):
                self.zbuffer[y][x] = float('inf')

    def set_view(self, view_matrix):
        self.view = view_matrix

    def project_vertex(self, v: Vec3) -> Tuple[Optional[Tuple[int, int, float]], Vec3]:
        """Project a 3D vertex to screen space. Returns (screen_pos, view_space_pos)"""
        view_pos = self.view * v
        if view_pos.z > -0.1:  # Behind camera
            return None, view_pos

        proj_pos = self.proj * view_pos
        sx = int((proj_pos.x + 1) * 0.5 * self.width)
        sy = int((1 - proj_pos.y) * 0.5 * self.height)

        return (sx, sy, -view_pos.z), view_pos

    def apply_fog(self, color, depth):
        """Apply distance fog to a color"""
        if depth < self.fog_start:
            return color
        if depth > self.fog_end:
            return self.fog_color

        t = (depth - self.fog_start) / (self.fog_end - self.fog_start)
        return (
            int(color[0] + (self.fog_color[0] - color[0]) * t),
            int(color[1] + (self.fog_color[1] - color[1]) * t),
            int(color[2] + (self.fog_color[2] - color[2]) * t)
        )

    def draw_triangle_flat(self, p1, p2, p3, color):
        """Draw a filled triangle with flat shading"""
        # Sort by y
        pts = sorted([p1, p2, p3], key=lambda p: p[1])
        x0, y0, z0 = pts[0]
        x1, y1, z1 = pts[1]
        x2, y2, z2 = pts[2]

        if y0 == y2:
            return

        avg_z = (z0 + z1 + z2) / 3
        shaded_color = self.apply_fog(color, avg_z)

        def interp(y, ys, ye, vs, ve):
            if ye == ys:
                return vs
            return vs + (y - ys) / (ye - ys) * (ve - vs)

        y_start = max(0, int(y0))
        y_end = min(self.height - 1, int(y2))

        for y in range(y_start, y_end + 1):
            if y < y1:
                xa = interp(y, y0, y2, x0, x2)
                za = interp(y, y0, y2, z0, z2)
                xb = interp(y, y0, y1, x0, x1) if y1 != y0 else x0
                zb = interp(y, y0, y1, z0, z1) if y1 != y0 else z0
            else:
                xa = interp(y, y0, y2, x0, x2)
                za = interp(y, y0, y2, z0, z2)
                xb = interp(y, y1, y2, x1, x2) if y2 != y1 else x1
                zb = interp(y, y1, y2, z1, z2) if y2 != y1 else z1

            if xa > xb:
                xa, xb = xb, xa
                za, zb = zb, za

            x_start = max(0, int(xa))
            x_end = min(self.width - 1, int(xb))

            for x in range(x_start, x_end + 1):
                t = (x - xa) / (xb - xa) if xb != xa else 0
                z = za + t * (zb - za)

                if 0 <= y < self.height and 0 <= x < self.width:
                    if z < self.zbuffer[y][x]:
                        self.zbuffer[y][x] = z
                        self.buffer.set_at((x, y), shaded_color)

    def draw_quad(self, v1, v2, v3, v4, color):
        """Draw a quad as two triangles"""
        p1, _ = self.project_vertex(v1)
        p2, _ = self.project_vertex(v2)
        p3, _ = self.project_vertex(v3)
        p4, _ = self.project_vertex(v4)

        if p1 and p2 and p3:
            self.draw_triangle_flat(p1, p2, p3, color)
        if p1 and p3 and p4:
            self.draw_triangle_flat(p1, p3, p4, color)

    def draw_box(self, center: Vec3, size: Vec3, color, rotation_y=0):
        """Draw a 3D box with optional Y rotation"""
        hx, hy, hz = size.x / 2, size.y / 2, size.z / 2

        # Local vertices
        local_verts = [
            Vec3(-hx, -hy, -hz), Vec3(hx, -hy, -hz),
            Vec3(hx, hy, -hz), Vec3(-hx, hy, -hz),
            Vec3(-hx, -hy, hz), Vec3(hx, -hy, hz),
            Vec3(hx, hy, hz), Vec3(-hx, hy, hz),
        ]

        # Apply rotation and translation
        cos_r, sin_r = math.cos(rotation_y), math.sin(rotation_y)
        verts = []
        for v in local_verts:
            rx = v.x * cos_r - v.z * sin_r
            rz = v.x * sin_r + v.z * cos_r
            verts.append(Vec3(rx + center.x, v.y + center.y, rz + center.z))

        # Face definitions (indices)
        faces = [
            (0, 1, 2, 3, 0.8),   # Front
            (5, 4, 7, 6, 0.8),   # Back
            (4, 0, 3, 7, 0.6),   # Left
            (1, 5, 6, 2, 0.6),   # Right
            (3, 2, 6, 7, 1.0),   # Top
            (4, 5, 1, 0, 0.5),   # Bottom
        ]

        for i0, i1, i2, i3, shade in faces:
            shaded = tuple(int(c * shade) for c in color)
            self.draw_quad(verts[i0], verts[i1], verts[i2], verts[i3], shaded)

    def draw_cylinder(self, center: Vec3, radius: float, height: float, color, segments=8):
        """Draw a cylinder"""
        hy = height / 2
        top_verts = []
        bot_verts = []

        for i in range(segments):
            angle = 2 * math.pi * i / segments
            x = center.x + radius * math.cos(angle)
            z = center.z + radius * math.sin(angle)
            top_verts.append(Vec3(x, center.y + hy, z))
            bot_verts.append(Vec3(x, center.y - hy, z))

        # Draw sides
        for i in range(segments):
            ni = (i + 1) % segments
            shade = 0.6 + 0.4 * abs(math.cos(2 * math.pi * i / segments))
            shaded = tuple(int(c * shade) for c in color)
            self.draw_quad(bot_verts[i], bot_verts[ni], top_verts[ni], top_verts[i], shaded)

        # Draw top cap
        top_center = Vec3(center.x, center.y + hy, center.z)
        for i in range(segments):
            ni = (i + 1) % segments
            p1, _ = self.project_vertex(top_center)
            p2, _ = self.project_vertex(top_verts[i])
            p3, _ = self.project_vertex(top_verts[ni])
            if p1 and p2 and p3:
                self.draw_triangle_flat(p1, p2, p3, color)

    def draw_sphere_approx(self, center: Vec3, radius: float, color, lat_divs=6, lon_divs=8):
        """Draw an approximate sphere using quads"""
        verts = []
        for i in range(lat_divs + 1):
            lat = math.pi * i / lat_divs - math.pi / 2
            for j in range(lon_divs):
                lon = 2 * math.pi * j / lon_divs
                x = center.x + radius * math.cos(lat) * math.cos(lon)
                y = center.y + radius * math.sin(lat)
                z = center.z + radius * math.cos(lat) * math.sin(lon)
                verts.append(Vec3(x, y, z))

        for i in range(lat_divs):
            for j in range(lon_divs):
                i0 = i * lon_divs + j
                i1 = i * lon_divs + (j + 1) % lon_divs
                i2 = (i + 1) * lon_divs + (j + 1) % lon_divs
                i3 = (i + 1) * lon_divs + j

                # Simple shading based on latitude
                shade = 0.5 + 0.5 * (i / lat_divs)
                shaded = tuple(int(c * shade) for c in color)

                self.draw_quad(verts[i0], verts[i1], verts[i2], verts[i3], shaded)

    def draw_ground_plane(self, y, size, color, grid_color=None, grid_size=10):
        """Draw a ground plane with optional grid"""
        hs = size / 2
        corners = [
            Vec3(-hs, y, -hs),
            Vec3(hs, y, -hs),
            Vec3(hs, y, hs),
            Vec3(-hs, y, hs),
        ]
        self.draw_quad(corners[0], corners[1], corners[2], corners[3], color)

    def get_surface(self):
        return self.buffer


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
    WALL_SLIDING = auto()
    SWIMMING = auto()
    HURT = auto()
    DEAD = auto()


class Mario:
    def __init__(self, pos: Vec3):
        self.pos = pos.copy()
        self.vel = Vec3()
        self.facing = 0  # Radians
        self.state = MarioState.IDLE
        self.on_ground = False
        self.jump_count = 0
        self.jump_timer = 0
        self.invincible_timer = 0
        self.ground_pound_timer = 0

        # Stats
        self.health = 8
        self.max_health = 8
        self.coins = 0
        self.stars = 0
        self.lives = 4

        # Animation
        self.anim_timer = 0
        self.spin_angle = 0

    def update(self, dt, keys, level, sound):
        self.anim_timer += dt
        if self.invincible_timer > 0:
            self.invincible_timer -= dt

        # Handle death
        if self.state == MarioState.DEAD:
            self.vel.y -= GRAVITY * dt * 60
            self.pos.y += self.vel.y * dt * 60
            if self.pos.y < -50:
                return 'respawn'
            return None

        # Handle hurt
        if self.state == MarioState.HURT:
            self.vel.y -= GRAVITY * dt * 60
            self.pos += self.vel * dt * 60
            if self.on_ground and self.vel.y <= 0:
                self.state = MarioState.IDLE
            self._check_ground(level)
            return None

        # Ground pound landing
        if self.state == MarioState.GROUND_POUND_LAND:
            self.ground_pound_timer -= dt
            if self.ground_pound_timer <= 0:
                self.state = MarioState.IDLE
            return None

        # Input
        move_x = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
        move_z = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP])
        move_input = Vec3(move_x, 0, move_z)
        running = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        crouching = keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]

        # Jump timer for combo jumps
        if self.on_ground:
            self.jump_timer -= dt
            if self.jump_timer <= 0:
                self.jump_count = 0

        # State machine
        if self.on_ground:
            if self.state in (MarioState.JUMPING, MarioState.DOUBLE_JUMPING, 
                             MarioState.TRIPLE_JUMPING, MarioState.FALLING,
                             MarioState.LONG_JUMPING, MarioState.BACKFLIPPING):
                self.state = MarioState.IDLE

            # Ground pound landing
            if self.state == MarioState.GROUND_POUNDING:
                self.state = MarioState.GROUND_POUND_LAND
                self.ground_pound_timer = 0.3
                self.vel = Vec3()
                sound.play('ground_pound')
                return None

            if crouching:
                self.state = MarioState.CROUCHING
            elif move_input.length() > 0.1:
                self.state = MarioState.RUNNING if running else MarioState.WALKING
            else:
                self.state = MarioState.IDLE

        # Movement
        if self.state not in (MarioState.GROUND_POUNDING, MarioState.GROUND_POUND_LAND):
            if move_input.length() > 0.1:
                move_input = move_input.norm()
                target_angle = math.atan2(move_input.x, move_input.z)

                # Smooth rotation
                angle_diff = target_angle - self.facing
                while angle_diff > math.pi:
                    angle_diff -= 2 * math.pi
                while angle_diff < -math.pi:
                    angle_diff += 2 * math.pi
                self.facing += angle_diff * min(1.0, 10 * dt)

                # Speed based on state
                if self.state == MarioState.LONG_JUMPING:
                    speed = LONG_JUMP_HSPEED
                elif running or self.state == MarioState.RUNNING:
                    speed = RUN_SPEED
                else:
                    speed = WALK_SPEED

                # Air control is reduced
                if not self.on_ground:
                    speed *= 0.3

                self.vel.x = math.sin(self.facing) * speed * move_input.length()
                self.vel.z = math.cos(self.facing) * speed * move_input.length()
            else:
                # Friction
                friction = 0.85 if self.on_ground else 0.98
                self.vel.x *= friction
                self.vel.z *= friction

        # Gravity
        if not self.on_ground:
            self.vel.y -= GRAVITY * dt * 60
            if self.vel.y < -MAX_FALL_SPEED:
                self.vel.y = -MAX_FALL_SPEED

        # Apply velocity
        self.pos += self.vel * dt * 60

        # Ground check
        self._check_ground(level)

        # Wall collision
        self._check_walls(level)

        # Boundaries
        if self.pos.y < -20:
            self.take_damage(1, sound, fall_death=True)

        return None

    def handle_jump(self, keys, sound):
        """Handle jump input - called on key press"""
        if self.state == MarioState.DEAD or self.state == MarioState.HURT:
            return

        crouching = keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]
        running = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]

        if self.on_ground:
            # Long jump
            if running and self.vel.length_xz() > WALK_SPEED * 0.8:
                self.state = MarioState.LONG_JUMPING
                self.vel.y = LONG_JUMP_FORCE
                self.vel.x = math.sin(self.facing) * LONG_JUMP_HSPEED
                self.vel.z = math.cos(self.facing) * LONG_JUMP_HSPEED
                sound.play('long_jump')
                self.on_ground = False
                return

            # Backflip
            if crouching:
                self.state = MarioState.BACKFLIPPING
                self.vel.y = BACKFLIP_FORCE
                # Reverse direction
                self.vel.x = -math.sin(self.facing) * 0.2
                self.vel.z = -math.cos(self.facing) * 0.2
                sound.play('backflip')
                self.on_ground = False
                return

            # Normal/combo jumps
            self.jump_count += 1
            if self.jump_count >= 3 and self.jump_timer > 0:
                self.state = MarioState.TRIPLE_JUMPING
                self.vel.y = TRIPLE_JUMP_FORCE
                sound.play('triple_jump')
                self.jump_count = 0
            elif self.jump_count == 2 and self.jump_timer > 0:
                self.state = MarioState.DOUBLE_JUMPING
                self.vel.y = DOUBLE_JUMP_FORCE
                sound.play('double_jump')
            else:
                self.state = MarioState.JUMPING
                self.vel.y = JUMP_FORCE
                sound.play('jump')
                self.jump_count = 1

            self.jump_timer = 0.4
            self.on_ground = False

    def handle_ground_pound(self, sound):
        """Handle ground pound input"""
        if not self.on_ground and self.state not in (MarioState.GROUND_POUNDING, 
                                                       MarioState.DEAD, MarioState.HURT):
            self.state = MarioState.GROUND_POUNDING
            self.vel.x = 0
            self.vel.z = 0
            self.vel.y = -GROUND_POUND_SPEED
            self.spin_angle = 0

    def _check_ground(self, level):
        """Check collision with ground"""
        ground_y = level.get_ground_height(self.pos.x, self.pos.z)

        if self.pos.y <= ground_y:
            self.pos.y = ground_y
            self.vel.y = 0
            self.on_ground = True
        else:
            self.on_ground = False

    def _check_walls(self, level):
        """Check collision with walls"""
        for wall in level.walls:
            if wall.collides(self.pos, 0.5):
                # Push out of wall
                push = wall.get_push_vector(self.pos)
                self.pos += push
                
                # Wall slide
                if not self.on_ground and self.vel.y < 0:
                    self.vel.y *= 0.8  # Slow fall against wall

    def take_damage(self, amount, sound, fall_death=False):
        """Take damage"""
        if self.invincible_timer > 0 and not fall_death:
            return

        self.health -= amount

        if self.health <= 0 or fall_death:
            self.state = MarioState.DEAD
            self.vel = Vec3(0, 1.2, 0)
            sound.play('death')
            self.lives -= 1
        else:
            self.state = MarioState.HURT
            self.vel = Vec3(-math.sin(self.facing) * 0.3, 0.5, -math.cos(self.facing) * 0.3)
            self.invincible_timer = 2.0
            sound.play('hurt')

    def collect_coin(self, sound):
        """Collect a coin"""
        self.coins += 1
        if self.coins >= 100:
            self.coins -= 100
            self.lives += 1
        sound.play('coin')

    def collect_star(self, sound):
        """Collect a star"""
        self.stars += 1
        self.health = self.max_health
        sound.play('star')

    def draw(self, renderer: Renderer):
        """Draw Mario"""
        if self.state == MarioState.DEAD:
            return

        # Blink when invincible
        if self.invincible_timer > 0 and int(self.invincible_timer * 10) % 2 == 0:
            return

        # Body parts with rotation
        rot = self.facing

        # Animation offsets
        bob = 0
        if self.state in (MarioState.WALKING, MarioState.RUNNING):
            bob = math.sin(self.anim_timer * 15) * 0.1

        # Crouch
        crouch_offset = 0
        if self.state == MarioState.CROUCHING:
            crouch_offset = -0.3

        # Spin during backflip/triple jump
        spin = 0
        if self.state == MarioState.BACKFLIPPING:
            spin = self.anim_timer * 15
        elif self.state == MarioState.TRIPLE_JUMPING:
            spin = self.anim_timer * 10

        # Body (blue overalls)
        body_pos = Vec3(self.pos.x, self.pos.y + 0.7 + bob + crouch_offset, self.pos.z)
        renderer.draw_box(body_pos, Vec3(0.6, 0.7, 0.4), MARIO_BLUE, rot + spin)

        # Head
        head_pos = Vec3(self.pos.x, self.pos.y + 1.4 + bob + crouch_offset, self.pos.z)
        renderer.draw_sphere_approx(head_pos, 0.35, MARIO_SKIN, 4, 6)

        # Cap (red)
        cap_pos = Vec3(self.pos.x, self.pos.y + 1.6 + bob + crouch_offset, self.pos.z)
        renderer.draw_box(cap_pos, Vec3(0.5, 0.2, 0.5), MARIO_RED, rot + spin)

        # Legs
        leg_spread = 0.15
        leg_anim = math.sin(self.anim_timer * 15) * 0.2 if self.state in (MarioState.WALKING, MarioState.RUNNING) else 0

        left_leg = Vec3(
            self.pos.x - math.cos(rot) * leg_spread,
            self.pos.y + 0.2,
            self.pos.z + math.sin(rot) * leg_spread
        )
        right_leg = Vec3(
            self.pos.x + math.cos(rot) * leg_spread,
            self.pos.y + 0.2,
            self.pos.z - math.sin(rot) * leg_spread
        )

        renderer.draw_box(left_leg, Vec3(0.25, 0.4, 0.25), MARIO_BLUE, rot)
        renderer.draw_box(right_leg, Vec3(0.25, 0.4, 0.25), MARIO_BLUE, rot)


class Coin:
    def __init__(self, pos: Vec3):
        self.pos = pos.copy()
        self.collected = False
        self.spin = random.uniform(0, math.pi * 2)

    def update(self, dt):
        self.spin += dt * 5

    def check_collect(self, mario: Mario, sound):
        if self.collected:
            return False
        dist = (self.pos - mario.pos).length()
        if dist < 1.5:
            self.collected = True
            mario.collect_coin(sound)
            return True
        return False

    def draw(self, renderer: Renderer):
        if self.collected:
            return
        # Spinning coin
        renderer.draw_box(
            Vec3(self.pos.x, self.pos.y + math.sin(self.spin * 2) * 0.1, self.pos.z),
            Vec3(0.5, 0.5, 0.1),
            COIN_GOLD,
            self.spin
        )


class Star:
    def __init__(self, pos: Vec3):
        self.pos = pos.copy()
        self.collected = False
        self.spin = 0
        self.bob = 0

    def update(self, dt):
        self.spin += dt * 3
        self.bob += dt * 4

    def check_collect(self, mario: Mario, sound):
        if self.collected:
            return False
        dist = (self.pos - mario.pos).length()
        if dist < 2:
            self.collected = True
            mario.collect_star(sound)
            return True
        return False

    def draw(self, renderer: Renderer):
        if self.collected:
            return
        # Bobbing, spinning star
        draw_pos = Vec3(
            self.pos.x,
            self.pos.y + math.sin(self.bob) * 0.5,
            self.pos.z
        )
        # Draw as a simple shape for now (would be star-shaped ideally)
        renderer.draw_sphere_approx(draw_pos, 0.6, STAR_YELLOW, 4, 5)


class Enemy:
    def __init__(self, pos: Vec3, enemy_type='goomba'):
        self.pos = pos.copy()
        self.vel = Vec3()
        self.enemy_type = enemy_type
        self.alive = True
        self.squish_timer = 0
        self.facing = random.uniform(0, math.pi * 2)
        self.walk_timer = 0

        if enemy_type == 'goomba':
            self.speed = 0.05
            self.color = GOOMBA_BROWN
        elif enemy_type == 'bobomb':
            self.speed = 0.03
            self.color = BOBOMB_BLACK

    def update(self, dt, mario: Mario, level):
        if not self.alive:
            self.squish_timer -= dt
            return

        self.walk_timer += dt

        # Simple AI - walk toward mario sometimes, otherwise wander
        to_mario = mario.pos - self.pos
        dist = to_mario.length_xz()

        if dist < 15 and dist > 2:
            # Chase mario
            target_angle = math.atan2(to_mario.x, to_mario.z)
            angle_diff = target_angle - self.facing
            while angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            while angle_diff < -math.pi:
                angle_diff += 2 * math.pi
            self.facing += angle_diff * 2 * dt
        else:
            # Wander
            if random.random() < 0.01:
                self.facing += random.uniform(-0.5, 0.5)

        self.vel.x = math.sin(self.facing) * self.speed
        self.vel.z = math.cos(self.facing) * self.speed

        self.pos += self.vel * dt * 60

        # Stay on ground
        ground_y = level.get_ground_height(self.pos.x, self.pos.z)
        self.pos.y = ground_y

    def check_collision(self, mario: Mario, sound):
        if not self.alive:
            return

        to_mario = mario.pos - self.pos
        dist_xz = to_mario.length_xz()

        if dist_xz < 1.0:
            # Check if mario is above (stomping)
            if mario.vel.y < -0.1 and mario.pos.y > self.pos.y + 0.5:
                self.alive = False
                self.squish_timer = 0.5
                mario.vel.y = 0.6  # Bounce
                sound.play('enemy_hit')
            elif mario.invincible_timer <= 0:
                # Mario takes damage
                mario.take_damage(1, sound)

    def draw(self, renderer: Renderer):
        if self.squish_timer > 0:
            # Squished
            renderer.draw_box(
                self.pos + Vec3(0, 0.1, 0),
                Vec3(1.0, 0.2, 1.0),
                self.color
            )
            return

        if not self.alive:
            return

        if self.enemy_type == 'goomba':
            # Body
            bob = math.sin(self.walk_timer * 10) * 0.05
            renderer.draw_sphere_approx(
                self.pos + Vec3(0, 0.5 + bob, 0),
                0.5,
                self.color,
                4, 6
            )
            # Feet
            renderer.draw_box(
                self.pos + Vec3(-0.2, 0.15, 0),
                Vec3(0.2, 0.3, 0.25),
                (80, 50, 20)
            )
            renderer.draw_box(
                self.pos + Vec3(0.2, 0.15, 0),
                Vec3(0.2, 0.3, 0.25),
                (80, 50, 20)
            )

        elif self.enemy_type == 'bobomb':
            # Body
            renderer.draw_sphere_approx(
                self.pos + Vec3(0, 0.5, 0),
                0.5,
                self.color,
                5, 8
            )
            # Eyes (white)
            renderer.draw_sphere_approx(
                self.pos + Vec3(0.2, 0.6, 0.3),
                0.15,
                (255, 255, 255),
                3, 4
            )
            renderer.draw_sphere_approx(
                self.pos + Vec3(-0.2, 0.6, 0.3),
                0.15,
                (255, 255, 255),
                3, 4
            )
            # Fuse
            renderer.draw_cylinder(
                self.pos + Vec3(0, 1.0, 0),
                0.05, 0.3,
                (100, 100, 100),
                4
            )


class Wall:
    def __init__(self, pos: Vec3, size: Vec3, color):
        self.pos = pos
        self.size = size
        self.color = color
        self.min_x = pos.x - size.x / 2
        self.max_x = pos.x + size.x / 2
        self.min_z = pos.z - size.z / 2
        self.max_z = pos.z + size.z / 2

    def collides(self, point: Vec3, radius: float):
        closest_x = max(self.min_x, min(point.x, self.max_x))
        closest_z = max(self.min_z, min(point.z, self.max_z))
        
        dist = math.sqrt((point.x - closest_x) ** 2 + (point.z - closest_z) ** 2)
        return dist < radius and point.y < self.pos.y + self.size.y / 2

    def get_push_vector(self, point: Vec3):
        # Find closest point on wall surface
        closest_x = max(self.min_x, min(point.x, self.max_x))
        closest_z = max(self.min_z, min(point.z, self.max_z))

        dx = point.x - closest_x
        dz = point.z - closest_z
        dist = math.sqrt(dx * dx + dz * dz)

        if dist < 0.01:
            # Inside wall, push out based on center
            dx = point.x - self.pos.x
            dz = point.z - self.pos.z
            if abs(dx) > abs(dz):
                return Vec3(0.6 if dx > 0 else -0.6, 0, 0)
            else:
                return Vec3(0, 0, 0.6 if dz > 0 else -0.6)

        push = 0.55 - dist
        return Vec3(dx / dist * push, 0, dz / dist * push)

    def draw(self, renderer: Renderer):
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
        self.platforms: List[dict] = []  # {pos, size, color}
        self.decorations: List[dict] = []

    def get_ground_height(self, x, z):
        """Get ground height at position - checks platforms"""
        height = self.ground_y

        for plat in self.platforms:
            pos = plat['pos']
            size = plat['size']
            if (pos.x - size.x/2 < x < pos.x + size.x/2 and
                pos.z - size.z/2 < z < pos.z + size.z/2):
                plat_top = pos.y + size.y/2
                if plat_top > height:
                    height = plat_top

        return height

    def update(self, dt, mario: Mario, sound):
        for coin in self.coins:
            coin.update(dt)
            coin.check_collect(mario, sound)

        for star in self.stars:
            star.update(dt)
            star.check_collect(mario, sound)

        for enemy in self.enemies:
            enemy.update(dt, mario, self)
            enemy.check_collision(mario, sound)

    def draw(self, renderer: Renderer):
        # Ground
        renderer.draw_ground_plane(self.ground_y - 0.1, 500, self.ground_color)

        # Platforms
        for plat in self.platforms:
            renderer.draw_box(plat['pos'], plat['size'], plat['color'])

        # Walls
        for wall in self.walls:
            wall.draw(renderer)

        # Decorations
        for dec in self.decorations:
            if dec['type'] == 'tree':
                # Trunk
                renderer.draw_cylinder(dec['pos'], 0.5, 3, (100, 70, 40), 6)
                # Leaves
                renderer.draw_sphere_approx(
                    dec['pos'] + Vec3(0, 3, 0),
                    2,
                    (34, 139, 34),
                    4, 6
                )
            elif dec['type'] == 'rock':
                renderer.draw_sphere_approx(dec['pos'], dec.get('size', 1), (128, 128, 128), 3, 5)
            elif dec['type'] == 'pillar':
                renderer.draw_cylinder(dec['pos'], dec.get('radius', 1), dec.get('height', 5), dec.get('color', (200, 200, 200)), 8)
            elif dec['type'] == 'box':
                renderer.draw_box(dec['pos'], dec['size'], dec.get('color', (150, 150, 150)))

        # Coins
        for coin in self.coins:
            coin.draw(renderer)

        # Stars
        for star in self.stars:
            star.draw(renderer)

        # Enemies
        for enemy in self.enemies:
            enemy.draw(renderer)


def create_castle_grounds():
    """Peach's Castle exterior"""
    level = Level("Castle Grounds", SKY_BLUE, GRASS_GREEN)
    level.spawn_pos = Vec3(0, 1, 30)

    # Castle main building
    level.walls.append(Wall(Vec3(0, 10, -30), Vec3(40, 20, 30), CASTLE_TAN))
    # Castle towers
    level.decorations.append({'type': 'pillar', 'pos': Vec3(-18, 12, -15), 'radius': 4, 'height': 24, 'color': CASTLE_TAN})
    level.decorations.append({'type': 'pillar', 'pos': Vec3(18, 12, -15), 'radius': 4, 'height': 24, 'color': CASTLE_TAN})
    # Tower tops (cone would be better but using sphere)
    level.decorations.append({'type': 'box', 'pos': Vec3(-18, 26, -15), 'size': Vec3(6, 4, 6), 'color': (180, 0, 0)})
    level.decorations.append({'type': 'box', 'pos': Vec3(18, 26, -15), 'size': Vec3(6, 4, 6), 'color': (180, 0, 0)})

    # Bridge
    level.platforms.append({'pos': Vec3(0, 0.5, 10), 'size': Vec3(8, 1, 20), 'color': (139, 119, 101)})

    # Moat (visual only - would need water collision)
    level.decorations.append({'type': 'box', 'pos': Vec3(-25, -1, 0), 'size': Vec3(15, 2, 50), 'color': WATER_BLUE})
    level.decorations.append({'type': 'box', 'pos': Vec3(25, -1, 0), 'size': Vec3(15, 2, 50), 'color': WATER_BLUE})

    # Trees
    for i in range(8):
        x = random.uniform(-60, 60)
        z = random.uniform(20, 80)
        level.decorations.append({'type': 'tree', 'pos': Vec3(x, 0, z)})

    # Coins around the area
    for i in range(20):
        angle = i * math.pi * 2 / 20
        x = math.cos(angle) * 25
        z = math.sin(angle) * 25 + 20
        level.coins.append(Coin(Vec3(x, 1, z)))

    # Star on castle roof
    level.stars.append(Star(Vec3(0, 22, -30)))

    # A few goombas
    level.enemies.append(Enemy(Vec3(15, 0, 40), 'goomba'))
    level.enemies.append(Enemy(Vec3(-15, 0, 35), 'goomba'))
    level.enemies.append(Enemy(Vec3(0, 0, 60), 'goomba'))

    return level


def create_bob_omb_battlefield():
    """Bob-omb Battlefield"""
    level = Level("Bob-omb Battlefield", (135, 206, 250), GRASS_GREEN)
    level.spawn_pos = Vec3(0, 1, 0)

    # Central mountain
    level.platforms.append({'pos': Vec3(0, 5, -50), 'size': Vec3(30, 10, 30), 'color': (139, 119, 101)})
    level.platforms.append({'pos': Vec3(0, 12, -50), 'size': Vec3(20, 4, 20), 'color': (139, 119, 101)})
    level.platforms.append({'pos': Vec3(0, 17, -50), 'size': Vec3(10, 6, 10), 'color': (139, 119, 101)})

    # Paths and platforms
    level.platforms.append({'pos': Vec3(25, 1, -20), 'size': Vec3(10, 2, 30), 'color': (160, 140, 100)})
    level.platforms.append({'pos': Vec3(-25, 2, -30), 'size': Vec3(15, 4, 15), 'color': (160, 140, 100)})

    # Chain chomp area (just a platform)
    level.platforms.append({'pos': Vec3(35, 0.5, 20), 'size': Vec3(12, 1, 12), 'color': (100, 80, 60)})

    # Coins
    # Ring around mountain base
    for i in range(16):
        angle = i * math.pi * 2 / 16
        x = math.cos(angle) * 20
        z = math.sin(angle) * 20 - 50
        level.coins.append(Coin(Vec3(x, 1, z)))

    # Trail coins
    for i in range(10):
        level.coins.append(Coin(Vec3(i * 3 - 15, 1, i * 2)))

    # Star at mountain top
    level.stars.append(Star(Vec3(0, 22, -50)))

    # Bob-ombs!
    for i in range(5):
        x = random.uniform(-30, 30)
        z = random.uniform(-30, 30)
        level.enemies.append(Enemy(Vec3(x, 0, z), 'bobomb'))

    # Goombas
    for i in range(4):
        x = random.uniform(-40, 40)
        z = random.uniform(10, 50)
        level.enemies.append(Enemy(Vec3(x, 0, z), 'goomba'))

    # Trees
    for i in range(10):
        x = random.uniform(-60, 60)
        z = random.uniform(-80, 60)
        if abs(x) > 15 or z > -30:  # Not on mountain
            level.decorations.append({'type': 'tree', 'pos': Vec3(x, 0, z)})

    return level


def create_cool_cool_mountain():
    """Cool Cool Mountain"""
    level = Level("Cool Cool Mountain", (200, 220, 255), SNOW_WHITE)
    level.spawn_pos = Vec3(0, 25, 0)

    # Mountain peak (spawn area)
    level.platforms.append({'pos': Vec3(0, 24, 0), 'size': Vec3(20, 2, 20), 'color': SNOW_WHITE})

    # Descending platforms (spiral path)
    heights = [20, 16, 12, 8, 4, 0]
    angles = [0, 60, 120, 180, 240, 300]
    for h, a in zip(heights, angles):
        rad = math.radians(a)
        x = math.cos(rad) * (25 - h/2)
        z = math.sin(rad) * (25 - h/2)
        level.platforms.append({'pos': Vec3(x, h, z), 'size': Vec3(10, 2, 10), 'color': (220, 230, 255)})

    # Ice blocks
    for i in range(5):
        x = random.uniform(-30, 30)
        z = random.uniform(-30, 30)
        level.decorations.append({'type': 'box', 'pos': Vec3(x, 1, z), 'size': Vec3(3, 3, 3), 'color': (180, 220, 255)})

    # Coins on the path
    for i, (h, a) in enumerate(zip(heights, angles)):
        rad = math.radians(a)
        x = math.cos(rad) * (25 - h/2)
        z = math.sin(rad) * (25 - h/2)
        level.coins.append(Coin(Vec3(x, h + 2, z)))

    # More coins
    for i in range(15):
        angle = random.uniform(0, math.pi * 2)
        r = random.uniform(5, 35)
        h = random.uniform(0, 20)
        level.coins.append(Coin(Vec3(math.cos(angle) * r, h + 1, math.sin(angle) * r)))

    # Star at bottom
    level.stars.append(Star(Vec3(0, 2, -30)))

    # Goombas (they're cold!)
    for i in range(3):
        level.enemies.append(Enemy(Vec3(random.uniform(-20, 20), 0, random.uniform(-20, 20)), 'goomba'))

    return level


def create_lethal_lava_land():
    """Lethal Lava Land"""
    level = Level("Lethal Lava Land", (80, 40, 40), LAVA_ORANGE)
    level.spawn_pos = Vec3(0, 3, 0)
    level.ground_y = -2  # Lava is "ground" but deadly

    # Starting platform
    level.platforms.append({'pos': Vec3(0, 2, 0), 'size': Vec3(10, 4, 10), 'color': (80, 80, 80)})

    # Floating platforms
    platforms_data = [
        (Vec3(12, 2, 0), Vec3(6, 4, 6)),
        (Vec3(20, 3, 8), Vec3(5, 4, 5)),
        (Vec3(15, 4, 18), Vec3(6, 4, 6)),
        (Vec3(0, 5, 25), Vec3(8, 4, 8)),
        (Vec3(-15, 4, 18), Vec3(6, 4, 6)),
        (Vec3(-20, 3, 5), Vec3(5, 4, 5)),
        (Vec3(-12, 2, -5), Vec3(6, 4, 6)),
        (Vec3(0, 6, -20), Vec3(12, 6, 12)),  # Volcano base
    ]

    for pos, size in platforms_data:
        level.platforms.append({'pos': pos, 'size': size, 'color': (60, 60, 60)})

    # Volcano
    level.platforms.append({'pos': Vec3(0, 12, -20), 'size': Vec3(8, 6, 8), 'color': (50, 50, 50)})

    # Coins on platforms
    for pos, size in platforms_data:
        level.coins.append(Coin(Vec3(pos.x, pos.y + size.y/2 + 1, pos.z)))

    # Star on volcano top
    level.stars.append(Star(Vec3(0, 17, -20)))

    # Enemies on safe platforms
    level.enemies.append(Enemy(Vec3(0, 2.5, 25), 'goomba'))
    level.enemies.append(Enemy(Vec3(12, 2.5, 0), 'goomba'))

    return level


# ══════════════════════════════════════════════════════════════════════════════
# CAMERA
# ══════════════════════════════════════════════════════════════════════════════

class Camera:
    def __init__(self):
        self.distance = 15
        self.height = 6
        self.angle = 0  # Horizontal angle around Mario
        self.pitch = 0.3  # Vertical angle

        self.target_distance = 15
        self.target_height = 6

    def update(self, dt, keys, mario: Mario):
        # Rotate camera
        if keys[pygame.K_q]:
            self.angle -= 2.5 * dt
        if keys[pygame.K_e]:
            self.angle += 2.5 * dt

        # Zoom
        if keys[pygame.K_r]:
            self.target_distance = max(5, self.target_distance - 15 * dt)
        if keys[pygame.K_f]:
            self.target_distance = min(40, self.target_distance + 15 * dt)

        # Smooth zoom
        self.distance += (self.target_distance - self.distance) * 5 * dt

        # Auto-adjust based on Mario's state
        if mario.state in (MarioState.LONG_JUMPING, MarioState.TRIPLE_JUMPING):
            self.target_height = 8
        else:
            self.target_height = 6

        self.height += (self.target_height - self.height) * 3 * dt

    def get_position(self, mario: Mario) -> Vec3:
        return Vec3(
            mario.pos.x + math.sin(self.angle) * self.distance,
            mario.pos.y + self.height,
            mario.pos.z + math.cos(self.angle) * self.distance
        )

    def get_view_matrix(self, mario: Mario) -> Mat4:
        eye = self.get_position(mario)
        target = mario.pos + Vec3(0, 1.5, 0)
        return Mat4.look_at(eye, target, Vec3(0, 1, 0))


# ══════════════════════════════════════════════════════════════════════════════
# HUD
# ══════════════════════════════════════════════════════════════════════════════

class HUD:
    def __init__(self):
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)

    def draw(self, screen, mario: Mario, level: Level, fps: float):
        # Health meter (pie segments)
        health_x, health_y = 70, 50
        pygame.draw.circle(screen, (0, 0, 0), (health_x, health_y), 35, 3)

        for i in range(mario.max_health):
            angle_start = math.pi/2 - (i * math.pi * 2 / mario.max_health)
            angle_end = math.pi/2 - ((i + 1) * math.pi * 2 / mario.max_health)

            if i < mario.health:
                color = (50, 200, 50) if mario.health > 2 else (200, 200, 50) if mario.health > 1 else (200, 50, 50)
            else:
                color = (80, 80, 80)

            # Draw pie segment
            points = [(health_x, health_y)]
            for a in range(int(math.degrees(angle_end)), int(math.degrees(angle_start)) + 1, 5):
                rad = math.radians(a)
                points.append((
                    health_x + math.cos(rad) * 30,
                    health_y - math.sin(rad) * 30
                ))
            if len(points) > 2:
                pygame.draw.polygon(screen, color, points)

        # Lives
        lives_text = self.font_medium.render(f"x {mario.lives}", True, (255, 255, 255))
        screen.blit(lives_text, (120, 35))

        # Coins
        pygame.draw.circle(screen, COIN_GOLD, (SCREEN_WIDTH - 150, 40), 15)
        coin_text = self.font_medium.render(f"x {mario.coins}", True, (255, 255, 255))
        screen.blit(coin_text, (SCREEN_WIDTH - 125, 28))

        # Stars
        pygame.draw.circle(screen, STAR_YELLOW, (SCREEN_WIDTH - 150, 80), 15)
        star_text = self.font_medium.render(f"x {mario.stars}", True, (255, 255, 255))
        screen.blit(star_text, (SCREEN_WIDTH - 125, 68))

        # Level name
        level_text = self.font_small.render(level.name, True, (255, 255, 255))
        screen.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, 10))

        # FPS
        fps_text = self.font_small.render(f"FPS: {fps:.0f}", True, (200, 200, 200))
        screen.blit(fps_text, (10, SCREEN_HEIGHT - 25))

        # Controls hint
        controls = "WASD:Move  Space:Jump  Z:Pound  X:LongJump  C:Backflip  Q/E:Camera  1-4:Levels"
        ctrl_text = self.font_small.render(controls, True, (180, 180, 180))
        screen.blit(ctrl_text, (SCREEN_WIDTH // 2 - ctrl_text.get_width() // 2, SCREEN_HEIGHT - 25))


# ══════════════════════════════════════════════════════════════════════════════
# MAIN GAME
# ══════════════════════════════════════════════════════════════════════════════

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Super Mario 64 - Pygame-CE Recreation")
        self.clock = pygame.time.Clock()

        self.renderer = Renderer(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.sound = SoundGenerator()
        self.hud = HUD()

        # Create levels
        self.levels = [
            create_castle_grounds(),
            create_bob_omb_battlefield(),
            create_cool_cool_mountain(),
            create_lethal_lava_land(),
        ]
        self.current_level_idx = 0
        self.current_level = self.levels[0]

        # Create Mario
        self.mario = Mario(self.current_level.spawn_pos)
        self.camera = Camera()

        self.running = True
        self.paused = False

    def change_level(self, idx):
        if 0 <= idx < len(self.levels):
            self.current_level_idx = idx
            self.current_level = self.levels[idx]
            self.mario = Mario(self.current_level.spawn_pos)
            # Keep stars/coins
            self.camera = Camera()

    def respawn_mario(self):
        self.mario = Mario(self.current_level.spawn_pos)
        self.mario.lives = max(0, self.mario.lives)
        if self.mario.lives <= 0:
            # Game over - reset
            self.mario.lives = 4
            self.mario.coins = 0
            self.mario.stars = 0

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    self.mario.handle_jump(pygame.key.get_pressed(), self.sound)
                elif event.key == pygame.K_z:
                    self.mario.handle_ground_pound(self.sound)
                elif event.key == pygame.K_x:
                    # Long jump handled in handle_jump when running
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                        self.mario.handle_jump(pygame.key.get_pressed(), self.sound)
                elif event.key == pygame.K_c:
                    # Backflip - need to be crouching
                    pass  # Handled in handle_jump when crouching
                elif event.key == pygame.K_1:
                    self.change_level(0)
                elif event.key == pygame.K_2:
                    self.change_level(1)
                elif event.key == pygame.K_3:
                    self.change_level(2)
                elif event.key == pygame.K_4:
                    self.change_level(3)
                elif event.key == pygame.K_p:
                    self.paused = not self.paused

    def update(self, dt):
        if self.paused:
            return

        keys = pygame.key.get_pressed()

        result = self.mario.update(dt, keys, self.current_level, self.sound)
        if result == 'respawn':
            self.respawn_mario()

        self.camera.update(dt, keys, self.mario)
        self.current_level.update(dt, self.mario, self.sound)

    def draw(self):
        # Set up view
        view = self.camera.get_view_matrix(self.mario)
        self.renderer.set_view(view)
        self.renderer.clear(self.current_level.sky_color)

        # Draw level
        self.current_level.draw(self.renderer)

        # Draw Mario
        self.mario.draw(self.renderer)

        # Blit 3D buffer to screen
        self.screen.blit(self.renderer.get_surface(), (0, 0))

        # Draw HUD
        fps = self.clock.get_fps()
        self.hud.draw(self.screen, self.mario, self.current_level, fps)

        # Pause overlay
        if self.paused:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(128)
            self.screen.blit(overlay, (0, 0))

            font = pygame.font.Font(None, 72)
            text = font.render("PAUSED", True, (255, 255, 255))
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2,
                                    SCREEN_HEIGHT // 2 - text.get_height() // 2))

        pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            dt = min(dt, 0.05)  # Cap delta time

            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()


# ══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════════════════════╗
    ║  SUPER MARIO 64 - Pygame-CE Recreation                                   ║
    ║  Team Flames / Samsoft / Flames Co.                                      ║
    ╠══════════════════════════════════════════════════════════════════════════╣
    ║  Controls:                                                               ║
    ║    WASD/Arrows - Move           Space - Jump (combo for double/triple)   ║
    ║    Shift - Run                  Ctrl - Crouch                            ║
    ║    Z - Ground Pound             X - Long Jump (while running)            ║
    ║    C - Backflip (while crouch)  Q/E - Rotate Camera                      ║
    ║    R/F - Zoom Camera            1-4 - Change Level                       ║
    ║    P - Pause                    ESC - Quit                               ║
    ╚══════════════════════════════════════════════════════════════════════════╝
    """)
    game = Game()
    game.run()
