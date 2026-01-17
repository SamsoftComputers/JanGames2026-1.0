#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════╗
║          ULTRA MARIO 2D BROS (Math OST - 1-1 to 8-4)          ║
║               "NES Lore Accurate Edition"                     ║
║          (C) 2025 Samsoft / Team Flames                       ║
╚═══════════════════════════════════════════════════════════════╝
"""

import pygame
import math
import random
import array

# --- CONSTANTS ---
SCALE = 3
NES_W, NES_H = 256, 240
SW, SH = NES_W * SCALE, NES_H * SCALE
FPS = 60
AUDIO_RATE = 44100

# --- COLORS & PALETTES ---
class C:
    BLACK = (0, 0, 0)
    WHITE = (252, 252, 252)
    SKY = (92, 148, 252)
    GROUND = (200, 76, 12)
    BRICK = (180, 60, 0)
    UG_BG = (0, 0, 0)
    UG_GROUND = (0, 80, 160)
    UG_BRICK = (0, 56, 128)
    CAS_BG = (0, 0, 0)
    CAS_WALL = (116, 116, 116)
    CAS_BRICK = (168, 16, 0)
    UW_BG = (32, 56, 236)
    UW_GROUND = (0, 128, 136)
    QBLOCK = (252, 152, 56)
    PIPE = (0, 168, 0)
    PIPE_HI = (128, 208, 16)
    MARIO_RED = (216, 40, 0)
    SKIN = (252, 152, 56)
    GOOMBA = (112, 24, 0)
    KOOPA_G = (0, 168, 0)
    COIN = (252, 216, 168)
    FIREBAR = (216, 40, 0)

# --- INIT ---
pygame.init()
pygame.mixer.pre_init(AUDIO_RATE, -16, 1, 1024)
pygame.mixer.init()

screen = pygame.display.set_mode((SW, SH))
pygame.display.set_caption("ULTRA MARIO 2D BROS (1-1 > 8-4)")
clock = pygame.time.Clock()
nes = pygame.Surface((NES_W, NES_H))

font = pygame.font.Font(None, 8 * SCALE)
font_lg = pygame.font.Font(None, 12 * SCALE)

# --- NES-STYLE AUDIO ENGINE (Math-Based) ---
class ChiptuneSynth:
    def __init__(self):
        self.sounds = {}
        self.current_channel = None
        self.init_buffers()

    def make_tone(self, freq, duration, wave='square', duty=0.5, vol=0.1):
        n_samples = int(duration * AUDIO_RATE)
        buf = array.array('h', [0] * n_samples)
        if freq <= 0:
            return buf
        period = AUDIO_RATE / freq
        amp = int(32767 * vol)
        for i in range(n_samples):
            t = (i % period) / period
            val = 0
            if wave == 'square':
                val = amp if t < duty else -amp
            elif wave == 'triangle':
                val = int(amp * (4 * abs(t - 0.5) - 1))
            elif wave == 'noise':
                val = random.randint(-amp, amp)
            if duration < 0.1:
                val = int(val * (1 - i / n_samples))
            buf[i] = val
        return buf

    def seq_to_sound(self, sequence, tempo=0.12):
        full_buf = array.array('h')
        for note in sequence:
            f, d = note[0], note[1] * tempo
            w = note[2] if len(note) > 2 else 'square'
            v = note[3] if len(note) > 3 else 0.1
            full_buf.extend(self.make_tone(f, d, w, 0.5, v))
            full_buf.extend(array.array('h', [0] * int(0.01 * AUDIO_RATE)))
        return pygame.mixer.Sound(buffer=full_buf)

    def init_buffers(self):
        print("Synthesizing NES Audio (Math-based)...")
        N = {
            'C3': 130.8, 'D3': 146.8, 'E3': 164.8, 'F3': 174.6, 'G3': 196.0, 'A3': 220.0, 'A#3': 233.1, 'B3': 246.9,
            'C4': 261.6, 'C#4': 277.2, 'D4': 293.6, 'E4': 329.6, 'F4': 349.2, 'F#4': 370.0, 'G4': 392.0, 'G#4': 415.3,
            'A4': 440.0, 'A#4': 466.2, 'B4': 493.9, 'C5': 523.3, 'D5': 587.3, 'E5': 659.3, 'F5': 698.5, 'G5': 784.0,
            'A5': 880.0, 'B5': 987.8, 'C6': 1046.5, 'E6': 1318.5
        }

        # OVERWORLD THEME
        ow_melody = [
            ('E5', 1), ('E5', 1), (0, 1), ('E5', 1), (0, 1), ('C5', 1), ('E5', 2), ('G5', 4), (0, 4), ('G4', 4), (0, 4),
            ('C5', 3), (0, 1), ('G4', 3), (0, 1), ('E4', 3), (0, 1), ('A4', 2), ('B4', 2), ('A#4', 1), ('A4', 2),
            ('G4', 1.3), ('E5', 1.3), ('G5', 1.3), ('A5', 2), ('F5', 1), ('G5', 1), (0, 1), ('E5', 2), ('C5', 1), ('D5', 1), ('B4', 2), (0, 2)
        ] * 2
        ow_seq = [(N.get(n, 0), d, 'square', 0.12) if n != 0 else (0, d) for n, d in ow_melody]
        self.sounds['overworld'] = self.seq_to_sound(ow_seq, 0.11)

        # UNDERGROUND THEME
        ug_melody = [('C4', 1), ('C5', 1), ('A3', 1), ('A4', 1), ('A#3', 1), ('A#4', 1), (0, 6)] * 4
        ug_seq = [(N.get(n, 0), d, 'triangle', 0.2) if n != 0 else (0, d) for n, d in ug_melody]
        self.sounds['underground'] = self.seq_to_sound(ug_seq, 0.13)

        # CASTLE THEME
        ca_seq = []
        for root in [N['G3'], N['A#3'], N['G3']]:
            for _ in range(8):
                ca_seq.append((root, 0.5, 'square', 0.1))
                ca_seq.append((root * 1.5, 0.5, 'square', 0.1))
                ca_seq.append((root * 3, 0.5, 'square', 0.05))
        self.sounds['castle'] = self.seq_to_sound(ca_seq, 0.07)

        # STAR THEME
        star_seq = []
        for _ in range(4):
            for n in ['C5', 'C5', 'D5', 'D5', 'E5', 'E5', 'C5', 'C5']:
                star_seq.append((N[n], 1, 'square', 0.15))
        self.sounds['star'] = self.seq_to_sound(star_seq, 0.08)

        # DIE SFX
        die_seq = [(N['B4'], 1), (N['F5'], 1), (0, 1), (N['F4'], 3)]
        self.sounds['die'] = self.seq_to_sound([(f, d, 'square', 0.2) if f else (0, d) for f, d in die_seq], 0.1)

        # CLEAR SFX
        clear_seq = [(N['G4'], 1), (N['C5'], 1), (N['E5'], 1), (N['G5'], 1), (N['C6'], 1), (N['E6'], 3)]
        self.sounds['clear'] = self.seq_to_sound([(f, d, 'square', 0.15) for f, d in clear_seq], 0.12)

        # JUMP SFX
        jump_buf = array.array('h')
        for i in range(8):
            freq = 300 + i * 80
            jump_buf.extend(self.make_tone(freq, 0.015, 'square', 0.5, 0.15))
        self.sounds['jump'] = pygame.mixer.Sound(buffer=jump_buf)

        # COIN SFX
        coin_buf = array.array('h')
        coin_buf.extend(self.make_tone(N['B5'], 0.05, 'square', 0.5, 0.2))
        coin_buf.extend(self.make_tone(N['E6'], 0.25, 'square', 0.5, 0.2))
        self.sounds['coin'] = pygame.mixer.Sound(buffer=coin_buf)

        # STOMP SFX
        stomp_buf = array.array('h')
        for i in range(5):
            freq = 400 - i * 50
            stomp_buf.extend(self.make_tone(freq, 0.02, 'square', 0.5, 0.15))
        self.sounds['stomp'] = pygame.mixer.Sound(buffer=stomp_buf)

    def play(self, name, loops=-1):
        if self.current_channel:
            self.current_channel.stop()
        if name in self.sounds:
            self.current_channel = self.sounds[name].play(loops)

    def play_sfx(self, name):
        if name in self.sounds:
            self.sounds[name].play()

    def stop(self):
        if self.current_channel:
            self.current_channel.stop()

audio = ChiptuneSynth()

# --- PLAYER ---
class Player:
    def __init__(self, x, y):
        self.x, self.y = float(x), float(y)
        self.vx, self.vy = 0.0, 0.0
        self.w, self.h = 12, 16
        self.big = False
        self.grounded = False
        self.facing = 1
        self.dead = False
        self.iframes = 0
        self.star_timer = 0
        self.coins, self.score, self.lives = 0, 0, 3

    def update(self, keys, blocks):
        if self.dead:
            self.vy += 0.3
            self.y += self.vy
            return

        acc = 0.15 if self.grounded else 0.1
        max_v = 2.5 if keys[pygame.K_x] else 1.5

        if keys[pygame.K_LEFT]:
            self.vx = max(-max_v, self.vx - acc)
            self.facing = -1
        elif keys[pygame.K_RIGHT]:
            self.vx = min(max_v, self.vx + acc)
            self.facing = 1
        else:
            if abs(self.vx) < 0.1:
                self.vx = 0
            elif self.vx > 0:
                self.vx -= 0.1
            else:
                self.vx += 0.1

        if keys[pygame.K_z] and self.grounded:
            self.vy = -5.2
            self.grounded = False
            audio.play_sfx('jump')

        grav = 0.25 if keys[pygame.K_z] and self.vy < 0 else 0.35
        self.vy = min(self.vy + grav, 6.0)
        self.x += self.vx
        self.y += self.vy

        self.h = 24 if self.big else 16
        self.grounded = False

        for bx, by in blocks:
            br = pygame.Rect(bx, by, 16, 16)
            pr = pygame.Rect(int(self.x), int(self.y), self.w, self.h)
            if not pr.colliderect(br):
                continue
            if self.vy > 0 and pr.bottom > br.top and pr.bottom - self.vy <= br.top + 6:
                self.y = br.top - self.h
                self.vy = 0
                self.grounded = True
            elif self.vy < 0 and pr.top < br.bottom and pr.top - self.vy >= br.bottom - 6:
                self.y = br.bottom
                self.vy = 0
            pr = pygame.Rect(int(self.x), int(self.y), self.w, self.h)
            if pr.colliderect(br):
                if self.vx > 0:
                    self.x = br.left - self.w
                elif self.vx < 0:
                    self.x = br.right
                self.vx = 0

        if self.x < 0:
            self.x = 0
        if self.y > NES_H + 16:
            self.die()
        if self.star_timer > 0:
            self.star_timer -= 1
        if self.iframes > 0:
            self.iframes -= 1

    def die(self):
        if not self.dead:
            self.dead = True
            self.vy = -5
            self.lives -= 1
            audio.play('die', 0)

    def draw(self, s, cx):
        if self.dead:
            pygame.draw.rect(s, C.MARIO_RED, (int(self.x - cx), int(self.y), 12, 14))
            return
        if self.iframes > 0 and self.iframes % 4 < 2:
            return

        c_over, c_skin = C.MARIO_RED, C.SKIN
        if self.star_timer > 0:
            colors = [C.MARIO_RED, C.WHITE, C.SKY]
            c_over = colors[(self.star_timer // 4) % 3]
            c_skin = colors[(self.star_timer // 2) % 3]

        x, y = int(self.x - cx), int(self.y)
        if self.big:
            pygame.draw.rect(s, c_over, (x + 2, y, 8, 8))
            pygame.draw.rect(s, c_skin, (x + 2, y + 4, 8, 6))
            pygame.draw.rect(s, c_over, (x, y + 10, 12, 8))
            pygame.draw.rect(s, (0, 0, 180), (x + 1, y + 18, 4, 6))
            pygame.draw.rect(s, (0, 0, 180), (x + 7, y + 18, 4, 6))
        else:
            pygame.draw.rect(s, c_over, (x + 2, y, 8, 6))
            pygame.draw.rect(s, c_skin, (x + 2, y + 3, 7, 4))
            pygame.draw.rect(s, c_over, (x + 1, y + 7, 10, 5))
            pygame.draw.rect(s, (0, 0, 180), (x + 1, y + 12, 4, 4))
            pygame.draw.rect(s, (0, 0, 180), (x + 7, y + 12, 4, 4))

# --- GOOMBA ---
class Goomba:
    def __init__(self, x, y):
        self.x, self.y = float(x), float(y)
        self.vx, self.vy = -0.5, 0.0
        self.alive = True
        self.squished = 0
        self.anim = 0

    def update(self, blocks):
        if self.squished > 0:
            self.squished -= 1
            if self.squished == 0:
                self.alive = False
            return
        if not self.alive:
            return

        self.vy = min(self.vy + 0.3, 4)
        self.x += self.vx
        self.y += self.vy
        self.anim = (self.anim + 1) % 20

        gr = pygame.Rect(int(self.x), int(self.y), 16, 16)
        for bx, by in blocks:
            br = pygame.Rect(bx, by, 16, 16)
            if not gr.colliderect(br):
                continue
            if self.vy > 0 and gr.bottom > br.top:
                self.y = br.top - 16
                self.vy = 0
            if self.vx > 0 and gr.right > br.left and gr.left < br.left:
                self.vx = -0.5
            elif self.vx < 0 and gr.left < br.right and gr.right > br.right:
                self.vx = 0.5
            gr = pygame.Rect(int(self.x), int(self.y), 16, 16)

        if self.y > NES_H + 32:
            self.alive = False

    def draw(self, s, cx):
        if not self.alive:
            return
        x = int(self.x - cx)
        if x < -20 or x > NES_W + 20:
            return
        if self.squished > 0:
            pygame.draw.rect(s, C.GOOMBA, (x, int(self.y) + 8, 16, 8))
        else:
            pygame.draw.ellipse(s, C.GOOMBA, (x, int(self.y), 16, 14))
            pygame.draw.rect(s, C.BLACK, (x + 2, int(self.y) + 14, 4, 2))
            pygame.draw.rect(s, C.BLACK, (x + 10, int(self.y) + 14, 4, 2))
            pygame.draw.rect(s, C.WHITE, (x + 3, int(self.y) + 4, 4, 4))
            pygame.draw.rect(s, C.WHITE, (x + 9, int(self.y) + 4, 4, 4))

# --- FIREBAR ---
class FireBar:
    def __init__(self, x, y, length=5):
        self.x, self.y = x + 8, y + 8
        self.angle = 0
        self.length = length
        self.balls = []

    def update(self):
        self.angle = (self.angle + 3) % 360
        self.balls = []
        rad = math.radians(self.angle)
        for i in range(1, self.length + 1):
            dist = i * 10
            bx = self.x + math.cos(rad) * dist
            by = self.y + math.sin(rad) * dist
            self.balls.append(pygame.Rect(int(bx) - 4, int(by) - 4, 8, 8))

    def draw(self, s, cx):
        for b in self.balls:
            if 0 < b.x - cx < NES_W:
                pygame.draw.circle(s, C.FIREBAR, (int(b.x - cx), int(b.y)), 4)
                pygame.draw.circle(s, C.QBLOCK, (int(b.x - cx), int(b.y)), 2)

# --- LEVEL GEN ---
def get_palettes(ltype):
    if ltype == 'underground':
        return C.UG_GROUND, C.UG_BRICK, C.UG_BG
    if ltype == 'castle':
        return C.CAS_WALL, C.CAS_BRICK, C.CAS_BG
    if ltype == 'underwater':
        return C.UW_GROUND, C.UW_GROUND, C.UW_BG
    return C.GROUND, C.BRICK, C.SKY

def gen_level(w, l):
    l_type = 'overworld'
    if l == 2:
        l_type = 'underground'
    if l == 4:
        l_type = 'castle'

    pal = get_palettes(l_type)
    blocks, enemies, pipes, firebars = [], [], [], []

    length = 2400 + w * 200
    if l_type == 'castle':
        length = 2000

    x = 0
    ground_y = NES_H - 32

    while x < length:
        if l_type != 'castle' and 300 < x < length - 300 and random.random() < 0.08:
            x += random.choice([32, 48])
            continue

        if l_type == 'castle':
            for r in range(2):
                blocks.append((x, ground_y + r * 16, 'ground'))
            for r in range(2):
                blocks.append((x, r * 16, 'brick'))
        else:
            for r in range(2):
                blocks.append((x, ground_y + r * 16, 'ground'))

        if 200 < x < length - 200:
            if l_type != 'castle' and random.random() < 0.06:
                h = random.randint(2, 4)
                pipes.append((x, ground_y - h * 16, h))
                x += 16
            elif random.random() < 0.15:
                by = ground_y - random.choice([32, 48, 64])
                width = random.randint(3, 6)
                for i in range(width):
                    b_type = 'qblock' if random.random() < 0.2 else 'brick'
                    blocks.append((x + i * 16, by, b_type))
                    if random.random() < 0.2:
                        enemies.append(Goomba(x + i * 16, by - 16))
            elif l_type == 'castle' and random.random() < 0.04:
                firebars.append(FireBar(x, ground_y - 48, 5))
                blocks.append((x, ground_y - 48, 'block'))
            elif random.random() < 0.04 + (w * 0.01):
                enemies.append(Goomba(x, ground_y - 16))
        x += 16

    goal_x = length - 100
    if l_type != 'castle':
        sx = goal_x - 120
        sy = ground_y - 16
        for i in range(8):
            for j in range(i + 1):
                blocks.append((sx + i * 16, sy - j * 16, 'block'))

    return {'blocks': blocks, 'enemies': enemies, 'pipes': pipes, 'firebars': firebars,
            'type': l_type, 'width': length, 'goal': goal_x, 'pal': pal}

# --- DRAWING ---
def draw_level(s, data, cx):
    s.fill(data['pal'][2])
    pg, pb, _ = data['pal']

    for b in data['blocks']:
        if not (-16 < b[0] - cx < NES_W):
            continue
        x, y, t = int(b[0] - cx), b[1], b[2]
        if t == 'ground':
            pygame.draw.rect(s, pg, (x, y, 16, 16))
            pygame.draw.rect(s, C.BLACK, (x, y, 16, 16), 1)
        elif t == 'brick':
            pygame.draw.rect(s, pb, (x, y, 16, 16))
            pygame.draw.rect(s, C.BLACK, (x, y, 16, 16), 1)
            pygame.draw.line(s, C.BLACK, (x, y + 8), (x + 16, y + 8))
            pygame.draw.line(s, C.BLACK, (x + 8, y), (x + 8, y + 8))
            pygame.draw.line(s, C.BLACK, (x + 4, y + 8), (x + 4, y + 16))
            pygame.draw.line(s, C.BLACK, (x + 12, y + 8), (x + 12, y + 16))
        elif t == 'block':
            pygame.draw.rect(s, pb, (x, y, 16, 16))
            pygame.draw.rect(s, C.BLACK, (x, y, 16, 16), 1)
        elif t == 'qblock':
            pygame.draw.rect(s, C.QBLOCK, (x, y, 16, 16))
            pygame.draw.rect(s, C.BRICK, (x, y, 16, 16), 1)
            pygame.draw.rect(s, C.BRICK, (x + 6, y + 4, 4, 6))
            pygame.draw.rect(s, C.BRICK, (x + 7, y + 12, 2, 2))

    for p in data['pipes']:
        if not (-40 < p[0] - cx < NES_W):
            continue
        x, y, h = int(p[0] - cx), p[1], p[2]
        c = C.CAS_WALL if data['type'] == 'castle' else C.PIPE
        c2 = C.CAS_BRICK if data['type'] == 'castle' else C.PIPE_HI
        pygame.draw.rect(s, c, (x, y, 32, h * 16))
        pygame.draw.rect(s, C.BLACK, (x, y, 32, h * 16), 1)
        pygame.draw.rect(s, c, (x - 2, y, 36, 16))
        pygame.draw.rect(s, C.BLACK, (x - 2, y, 36, 16), 1)
        pygame.draw.rect(s, c2, (x + 4, y + 2, 4, 12))
        pygame.draw.rect(s, c2, (x + 6, y + 16, 4, (h - 1) * 16))

    for f in data['firebars']:
        f.draw(s, cx)

    if data['type'] != 'castle':
        gx = int(data['goal'] - cx)
        if -20 < gx < NES_W:
            pygame.draw.rect(s, C.PIPE_HI, (gx, NES_H - 168, 4, 136))
            pygame.draw.circle(s, C.PIPE_HI, (gx + 2, NES_H - 168), 4)
            pygame.draw.polygon(s, C.MARIO_RED, [(gx + 4, NES_H - 160), (gx + 24, NES_H - 152), (gx + 4, NES_H - 144)])

def draw_hud(s, player, world, level, time_rem):
    pygame.draw.rect(s, C.BLACK, (0, 0, NES_W, 16))
    txt = f"MARIO {player.score:06d}  x{player.coins:02d}  {world}-{level}  TIME {int(time_rem)}"
    t = font.render(txt, True, C.WHITE)
    s.blit(t, (8, 4))

def draw_menu(s, coin_anim):
    s.fill(C.SKY)
    for x in range(0, NES_W, 16):
        pygame.draw.rect(s, C.GROUND, (x, NES_H - 32, 16, 16))
        pygame.draw.rect(s, C.BRICK, (x, NES_H - 16, 16, 16))

    ty = 40
    for i, c in enumerate("ULTRA"):
        x = 65 + i * 18
        pygame.draw.rect(s, C.MARIO_RED, (x, ty, 16, 16))
        pygame.draw.rect(s, C.BLACK, (x, ty, 16, 16), 1)
        t = font.render(c, True, C.WHITE)
        s.blit(t, (x + 4, ty + 3))

    for i, c in enumerate("MARIO"):
        x = 55 + i * 20
        pygame.draw.rect(s, C.QBLOCK, (x, ty + 22, 18, 18))
        pygame.draw.rect(s, C.BRICK, (x, ty + 22, 18, 18), 1)
        t = font.render(c, True, C.MARIO_RED)
        s.blit(t, (x + 4, ty + 26))

    t = font.render("2D BROS.", True, C.WHITE)
    s.blit(t, (85, ty + 48))
    t = font.render("@2025 SAMSOFT", True, C.WHITE)
    s.blit(t, (70, ty + 65))

    my = 140
    ws = [8, 6, 2, 6]
    w = ws[int(coin_anim) % 4]
    pygame.draw.ellipse(s, C.COIN, (92 - w // 2, my - 2, w, 12))
    pygame.draw.ellipse(s, C.MARIO_RED, (73, my + 2, 10, 8))
    pygame.draw.rect(s, C.SKIN, (75, my + 8, 6, 6))

    t = font.render("1 PLAYER GAME", True, C.WHITE)
    s.blit(t, (105, my))
    t = font.render("2 PLAYER GAME", True, C.WHITE)
    s.blit(t, (105, my + 16))
    t = font.render("TOP- 000000", True, C.WHITE)
    s.blit(t, (80, my + 38))

    pygame.draw.rect(s, C.PIPE, (200, NES_H - 80, 32, 48))
    pygame.draw.rect(s, C.PIPE, (198, NES_H - 80, 36, 16))
    pygame.draw.rect(s, C.PIPE_HI, (204, NES_H - 78, 4, 12))

# --- MAIN ---
def main():
    state = "MENU"
    world, level = 1, 1
    player = None
    level_data = None
    cam_x = 0.0
    coin_anim = 0.0
    time_rem = 0.0
    trans_timer = 0

    running = True
    while running:
        keys = pygame.key.get_pressed()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            if e.type == pygame.KEYDOWN:
                if state == "MENU" and e.key == pygame.K_RETURN:
                    state = "LOAD"
                    world, level = 1, 1
                    player = Player(50, 100)
                    trans_timer = 120
                elif state == "GAMEOVER" and e.key == pygame.K_RETURN:
                    state = "MENU"
                    audio.stop()
                elif state == "WIN" and e.key == pygame.K_RETURN:
                    state = "MENU"
                    audio.stop()

        coin_anim = (coin_anim + 0.15) % 4
        nes.fill(C.BLACK)

        if state == "MENU":
            draw_menu(nes, coin_anim)

        elif state == "LOAD":
            nes.fill(C.BLACK)
            t = font_lg.render(f"WORLD {world}-{level}", True, C.WHITE)
            nes.blit(t, (NES_W // 2 - t.get_width() // 2, NES_H // 2 - 20))
            pygame.draw.rect(nes, C.MARIO_RED, (100, NES_H // 2 + 5, 8, 12))
            pygame.draw.rect(nes, C.SKIN, (101, NES_H // 2 + 8, 6, 4))
            m = font.render(f"x {player.lives}", True, C.WHITE)
            nes.blit(m, (115, NES_H // 2 + 8))

            trans_timer -= 1
            if trans_timer <= 0:
                level_data = gen_level(world, level)
                player.x, player.y = 50, NES_H - 80
                player.vx, player.vy = 0, 0
                player.dead = False
                cam_x = 0
                time_rem = 400
                state = "PLAY"
                if level_data['type'] == 'castle':
                    audio.play('castle')
                elif level_data['type'] == 'underground':
                    audio.play('underground')
                else:
                    audio.play('overworld')

        elif state == "PLAY":
            time_rem -= 1 / 60
            if time_rem <= 0 and not player.dead:
                player.die()

            solid = [(b[0], b[1]) for b in level_data['blocks']]
            for p in level_data['pipes']:
                for i in range(p[2]):
                    solid.append((p[0], p[1] + i * 16))
                    solid.append((p[0] + 16, p[1] + i * 16))

            player.update(keys, solid)

            for en in level_data['enemies']:
                en.update(solid)
                if en.alive and not player.dead and en.squished == 0:
                    pr = pygame.Rect(int(player.x), int(player.y), player.w, player.h)
                    er = pygame.Rect(int(en.x), int(en.y), 16, 16)
                    if pr.colliderect(er):
                        if player.vy > 0 and player.y + player.h < en.y + 10:
                            en.squished = 20
                            player.vy = -3
                            player.score += 100
                            audio.play_sfx('stomp')
                        elif player.iframes == 0 and player.star_timer == 0:
                            if player.big:
                                player.big = False
                                player.iframes = 120
                            else:
                                player.die()

            for f in level_data['firebars']:
                f.update()
                if not player.dead and player.iframes == 0:
                    pr = pygame.Rect(int(player.x), int(player.y), player.w, player.h)
                    for ball in f.balls:
                        if pr.colliderect(ball):
                            player.die()

            target_cam = player.x - NES_W // 3
            cam_x += (target_cam - cam_x) * 0.1
            cam_x = max(0, min(cam_x, level_data['width'] - NES_W))

            draw_level(nes, level_data, cam_x)
            for en in level_data['enemies']:
                en.draw(nes, cam_x)
            player.draw(nes, cam_x)
            draw_hud(nes, player, world, level, time_rem)

            if player.dead and player.y > NES_H + 50:
                if player.lives > 0:
                    state = "LOAD"
                    trans_timer = 60
                else:
                    state = "GAMEOVER"
                    audio.stop()

            if not player.dead and player.x > level_data['goal']:
                audio.play('clear', 0)
                player.score += int(time_rem) * 50
                level += 1
                if level > 4:
                    level = 1
                    world += 1
                if world > 8:
                    state = "WIN"
                else:
                    state = "LOAD"
                    trans_timer = 180

        elif state == "GAMEOVER":
            nes.fill(C.BLACK)
            t = font_lg.render("GAME OVER", True, C.WHITE)
            nes.blit(t, (NES_W // 2 - t.get_width() // 2, NES_H // 2 - 10))
            t2 = font.render("PRESS ENTER", True, C.WHITE)
            nes.blit(t2, (NES_W // 2 - t2.get_width() // 2, NES_H // 2 + 20))

        elif state == "WIN":
            nes.fill(C.BLACK)
            t = font_lg.render("CONGRATULATIONS!", True, C.WHITE)
            nes.blit(t, (NES_W // 2 - t.get_width() // 2, NES_H // 2 - 30))
            t2 = font.render("YOU SAVED THE PRINCESS!", True, C.WHITE)
            nes.blit(t2, (NES_W // 2 - t2.get_width() // 2, NES_H // 2))
            t3 = font.render(f"SCORE: {player.score}", True, C.QBLOCK)
            nes.blit(t3, (NES_W // 2 - t3.get_width() // 2, NES_H // 2 + 25))
            t4 = font.render("PRESS ENTER", True, C.WHITE)
            nes.blit(t4, (NES_W // 2 - t4.get_width() // 2, NES_H // 2 + 50))

        scaled = pygame.transform.scale(nes, (SW, SH))
        screen.blit(scaled, (0, 0))
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    print("╔═══════════════════════════════════════════════════════╗")
    print("║          ULTRA MARIO 2D BROS                          ║")
    print("║        Math-Based NES OST Edition                     ║")
    print("║           Worlds 1-1 to 8-4                           ║")
    print("║      (C) 2025 Samsoft / Team Flames                   ║")
    print("╠═══════════════════════════════════════════════════════╣")
    print("║  Controls:                                            ║")
    print("║    Arrow Keys - Move                                  ║")
    print("║    Z - Jump    X - Run    Enter - Start               ║")
    print("╚═══════════════════════════════════════════════════════╝")
    main()
