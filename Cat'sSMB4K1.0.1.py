#!/usr/bin/env python3
"""
CAT'S SUPER MARIO BROS v6 - PIPES FIXED FOR REAL
Pipes now proper NES proportion to Mario

(C) 2026 Team Flames / Samsoft
"""

import pygame
import sys

# =========================
# CONFIG
# =========================
SW, SH = 800, 480
FPS = 60

# Smaller scale for proper proportions
TILE = 24  # Each tile is 24px

# Physics
GRAV = 0.3
MAXF = 3.0
WALK_A = 0.08
RUN_A = 0.12
WALK_M = 1.2
RUN_M = 2.0
FRIC = 0.88
JMPV = -4.5
JMPG = 0.15

# Colors
SKY = (92, 148, 252)
BLK = (0, 0, 0)
WHT = (252, 252, 252)
RED = (228, 56, 24)
GRN = (0, 168, 0)
DGN = (0, 120, 0)
LGN = (80, 208, 80)
BRN = (172, 124, 0)
SKN = (252, 188, 176)
BRK = (200, 76, 12)
BK2 = (136, 52, 0)
GLD = (252, 152, 56)
GD2 = (200, 100, 0)
CST = (188, 188, 188)
CS2 = (116, 116, 116)
LVA = (228, 56, 24)
GMB = (172, 92, 0)

# =========================
# SPRITES
# =========================
def mario_spr(right=True):
    """Mario - same size as 1 tile (24x24)"""
    s = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
    
    # Simple but clear Mario
    # Hat
    pygame.draw.rect(s, RED, (6, 2, 12, 4))
    pygame.draw.rect(s, RED, (4, 4, 16, 3))
    
    # Face
    pygame.draw.rect(s, SKN, (6, 7, 12, 6))
    pygame.draw.rect(s, BRN, (4, 7, 4, 3))  # Hair
    
    # Eyes
    pygame.draw.rect(s, WHT, (7, 8, 2, 2))
    pygame.draw.rect(s, BLK, (8, 9, 1, 1))
    pygame.draw.rect(s, WHT, (13, 8, 2, 2))
    pygame.draw.rect(s, BLK, (14, 9, 1, 1))
    
    # Body
    pygame.draw.rect(s, RED, (5, 13, 14, 4))
    
    # Overalls
    pygame.draw.rect(s, BRN, (6, 17, 5, 5))
    pygame.draw.rect(s, BRN, (13, 17, 5, 5))
    
    # Feet
    pygame.draw.rect(s, BRN, (4, 21, 6, 3))
    pygame.draw.rect(s, BRN, (14, 21, 6, 3))
    
    if not right:
        s = pygame.transform.flip(s, True, False)
    return s

def pipe_spr(h_tiles):
    """
    Pipe - 1.5 tiles wide (36px), not 2 tiles
    This makes it look right compared to Mario
    """
    pw = int(TILE * 1.5)  # 36px wide - narrower!
    ph = TILE * h_tiles
    s = pygame.Surface((pw, ph), pygame.SRCALPHA)
    
    # Lip (top rim)
    lip_h = 8
    pygame.draw.rect(s, DGN, (0, 0, pw, lip_h))
    pygame.draw.rect(s, GRN, (2, 2, pw - 4, lip_h - 4))
    pygame.draw.rect(s, LGN, (4, 2, 8, lip_h - 4))  # Highlight
    
    # Body (narrower than lip)
    bx = 4
    bw = pw - 8
    pygame.draw.rect(s, DGN, (bx, lip_h, bw, ph - lip_h))
    pygame.draw.rect(s, GRN, (bx + 2, lip_h, bw - 4, ph - lip_h))
    pygame.draw.rect(s, LGN, (bx + 4, lip_h, 6, ph - lip_h))  # Highlight
    
    return s

def goomba_spr():
    s = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
    # Head
    pygame.draw.ellipse(s, GMB, (2, 0, 20, 14))
    # Eyes
    pygame.draw.rect(s, WHT, (5, 4, 4, 4))
    pygame.draw.rect(s, BLK, (7, 5, 2, 2))
    pygame.draw.rect(s, WHT, (15, 4, 4, 4))
    pygame.draw.rect(s, BLK, (17, 5, 2, 2))
    # Body
    pygame.draw.rect(s, SKN, (6, 12, 12, 6))
    # Feet
    pygame.draw.rect(s, GMB, (2, 18, 8, 6))
    pygame.draw.rect(s, GMB, (14, 18, 8, 6))
    return s

def koopa_spr(right=True):
    s = pygame.Surface((TILE, int(TILE * 1.5)), pygame.SRCALPHA)
    # Shell
    pygame.draw.ellipse(s, GRN, (2, 8, 20, 20))
    # Head
    pygame.draw.ellipse(s, GRN, (12, 0, 10, 12))
    # Eye
    pygame.draw.rect(s, WHT, (15, 3, 3, 3))
    pygame.draw.rect(s, BLK, (16, 4, 2, 2))
    # Feet
    pygame.draw.rect(s, SKN, (4, 26, 6, 4))
    pygame.draw.rect(s, SKN, (14, 26, 6, 4))
    if not right:
        s = pygame.transform.flip(s, True, False)
    return s

def ground_spr():
    s = pygame.Surface((TILE, TILE))
    s.fill(BRK)
    for y in range(0, TILE, 6):
        for x in range(0, TILE, 6):
            if (x + y) % 12 == 0:
                pygame.draw.rect(s, BK2, (x, y, 3, 3))
    return s

def brick_spr():
    s = pygame.Surface((TILE, TILE))
    s.fill(BRK)
    pygame.draw.line(s, BK2, (0, 0), (TILE, 0), 1)
    pygame.draw.line(s, BK2, (0, TILE//2), (TILE, TILE//2), 1)
    pygame.draw.line(s, BK2, (0, 0), (0, TILE//2), 1)
    pygame.draw.line(s, BK2, (TILE//2, 0), (TILE//2, TILE//2), 1)
    pygame.draw.line(s, BK2, (TILE//4, TILE//2), (TILE//4, TILE), 1)
    pygame.draw.line(s, BK2, (TILE*3//4, TILE//2), (TILE*3//4, TILE), 1)
    return s

def question_spr():
    s = pygame.Surface((TILE, TILE))
    s.fill(GLD)
    pygame.draw.rect(s, GD2, (0, 0, TILE, TILE), 2)
    # ?
    pygame.draw.rect(s, WHT, (8, 4, 8, 3))
    pygame.draw.rect(s, WHT, (13, 6, 3, 4))
    pygame.draw.rect(s, WHT, (9, 9, 6, 3))
    pygame.draw.rect(s, WHT, (10, 16, 4, 3))
    return s

def castle_spr():
    s = pygame.Surface((TILE, TILE))
    s.fill(CST)
    pygame.draw.line(s, CS2, (0, 0), (TILE, 0), 1)
    pygame.draw.line(s, CS2, (0, TILE//2), (TILE, TILE//2), 1)
    pygame.draw.line(s, CS2, (TILE//4, 0), (TILE//4, TILE), 1)
    pygame.draw.line(s, CS2, (TILE*3//4, 0), (TILE*3//4, TILE), 1)
    return s

def flag_spr():
    s = pygame.Surface((TILE, TILE * 10), pygame.SRCALPHA)
    pygame.draw.rect(s, DGN, (TILE//2 - 1, 0, 2, TILE * 10))
    pygame.draw.circle(s, GRN, (TILE//2, 6), 4)
    pts = [(TILE//2, 8), (TILE//2 - 12, 16), (TILE//2, 24)]
    pygame.draw.polygon(s, GRN, pts)
    return s

# Cache
SPR = {}
def get(n, **k):
    key = (n, tuple(k.items()))
    if key not in SPR:
        if n == 'mario': SPR[key] = mario_spr(k.get('r', True))
        elif n == 'goomba': SPR[key] = goomba_spr()
        elif n == 'koopa': SPR[key] = koopa_spr(k.get('r', True))
        elif n == 'ground': SPR[key] = ground_spr()
        elif n == 'brick': SPR[key] = brick_spr()
        elif n == 'question': SPR[key] = question_spr()
        elif n == 'castle': SPR[key] = castle_spr()
        elif n == 'flag': SPR[key] = flag_spr()
    return SPR.get(key)

# =========================
# LEVELS - Pipes positioned for height from ground
# Ground is at row 13-14 (y=13,14), so:
# 2-tile pipe: y = 12 (starts 2 tiles above ground base)
# 3-tile pipe: y = 11
# 4-tile pipe: y = 10
# =========================
L1_1 = {
    'theme': 'sky', 'time': 400, 'w': 224, 'gnd': 2, 'spawn': (3, 12),
    'obj': [
        ('?', 16, 9), ('B', 20, 9), ('?', 21, 9), ('B', 22, 9), ('?', 23, 9), ('B', 24, 9),
        ('?', 22, 5),
        # Pipes with correct heights (h = tiles tall)
        ('P', 28, 12, 2),   # 2 tiles tall - JUMPABLE
        ('P', 38, 11, 3),   # 3 tiles 
        ('P', 46, 10, 4),   # 4 tiles
        ('P', 57, 10, 4),   # 4 tiles
        ('B', 77, 9), ('?', 78, 9), ('B', 79, 9),
        ('B', 80, 5), ('B', 81, 5), ('B', 82, 5), ('B', 83, 5), ('B', 84, 5), ('B', 85, 5), ('B', 86, 5), ('B', 87, 5),
        ('B', 91, 5), ('B', 92, 5), ('B', 93, 5), ('?', 94, 5), ('B', 94, 9),
        ('B', 100, 9), ('B', 101, 9), ('?', 106, 9), ('?', 109, 9), ('?', 109, 5),
        ('B', 118, 9), ('?', 121, 9), ('B', 124, 9),
        ('S', 134, 13, 1), ('S', 135, 12, 2), ('S', 136, 11, 3), ('S', 137, 10, 4),
        ('S', 138, 9, 5), ('S', 139, 8, 6), ('S', 140, 7, 7), ('S', 141, 6, 8),
        ('F', 144, 3), ('C', 149, 8, 5, 6),
    ],
    'enemies': [('goomba', 22, 12), ('goomba', 40, 12), ('goomba', 51, 12), ('goomba', 53, 12),
                ('goomba', 97, 12), ('goomba', 99, 12), ('koopa', 107, 11), ('goomba', 114, 12)],
    'gaps': [(69, 2), (86, 2)],
}

L1_2 = {
    'theme': 'blk', 'time': 400, 'w': 240, 'gnd': 2, 'spawn': (3, 12), 'ceil': True,
    'obj': [
        ('B', 8, 3), ('B', 9, 3), ('B', 10, 3), ('?', 10, 7),
        ('B', 19, 7), ('B', 20, 7), ('?', 21, 7), ('B', 22, 7),
        ('P', 42, 12, 2), ('P', 60, 11, 3), ('P', 88, 12, 2), ('P', 100, 12, 2),
        ('B', 108, 7), ('?', 109, 7), ('?', 110, 7), ('B', 111, 7),
        ('S', 128, 13, 1), ('S', 129, 12, 2), ('S', 130, 11, 3), ('S', 131, 10, 4),
        ('S', 132, 9, 5), ('S', 133, 8, 6), ('S', 134, 7, 7),
        ('P', 160, 6, 8),
    ],
    'enemies': [('goomba', 14, 12), ('goomba', 28, 12), ('goomba', 46, 12), ('koopa', 55, 11)],
    'gaps': [],
}

L1_3 = {
    'theme': 'sky', 'time': 300, 'w': 176, 'gnd': 0, 'spawn': (2, 10),
    'obj': [
        ('-', 0, 12, 10), ('-', 13, 10, 4), ('-', 20, 12, 3), ('-', 26, 8, 5),
        ('-', 34, 12, 4), ('-', 41, 6, 4), ('-', 48, 10, 5), ('-', 56, 12, 4),
        ('-', 63, 5, 3), ('-', 69, 9, 5), ('-', 77, 12, 4), ('-', 84, 7, 4),
        ('-', 91, 11, 5), ('-', 99, 5, 3), ('-', 105, 9, 5), ('-', 113, 12, 4),
        ('-', 120, 7, 4), ('-', 127, 12, 10),
        ('S', 141, 13, 1), ('S', 142, 12, 2), ('S', 143, 11, 3), ('S', 144, 10, 4),
        ('F', 147, 3), ('C', 152, 8, 5, 6),
    ],
    'enemies': [('koopa', 15, 9), ('koopa', 28, 7), ('koopa', 50, 9)],
    'gaps': [(0, 1000)],
}

L1_4 = {
    'theme': 'blk', 'time': 300, 'w': 176, 'gnd': 2, 'spawn': (2, 12), 'ceil': True,
    'obj': [
        ('C', 12, 7, 2, 6), ('C', 22, 3, 2, 4),
        ('L', 30, 13, 4), ('-', 30, 10, 4), ('C', 42, 7, 2, 6),
        ('L', 52, 13, 5), ('-', 52, 9, 5), ('C', 66, 3, 2, 10),
        ('L', 78, 13, 4), ('-', 78, 10, 4),
        ('-', 110, 10, 24), ('L', 110, 13, 24),
        ('G', 134, 9),
    ],
    'enemies': [],
    'gaps': [(30, 4), (52, 5), (78, 4)],
}

LEVELS = {'1-1': L1_1, '1-2': L1_2, '1-3': L1_3, '1-4': L1_4}
for w in range(2, 9):
    for s in range(1, 5):
        k = f'{w}-{s}'
        if k not in LEVELS:
            LEVELS[k] = dict([L1_1, L1_2, L1_3, L1_4][(s-1) % 4])

LEVELS['8-4'] = {
    'theme': 'blk', 'time': 400, 'w': 360, 'gnd': 2, 'spawn': (2, 12), 'ceil': True,
    'obj': [
        ('C', 8, 7, 2, 6), ('L', 26, 13, 4), ('-', 26, 10, 4),
        ('L', 58, 13, 5), ('-', 58, 9, 5),
        ('P', 165, 10, 4), ('P', 180, 10, 4), ('P', 195, 10, 4),
        ('-', 270, 10, 40), ('L', 270, 13, 40), ('G', 310, 9),
    ],
    'enemies': [],
    'gaps': [(26, 4), (58, 5)],
}

# =========================
# ENTITIES
# =========================
class Entity(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vx = self.vy = 0.0
        self.on_ground = False

class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, TILE, TILE)
        self.right = True
        self.image = get('mario', r=True)
        self.dead = False
        self.coins = self.score = 0
        self.lives = 3
        self.jh = False

    def update(self, keys, blocks):
        run = keys[pygame.K_LSHIFT] or keys[pygame.K_x]
        a = RUN_A if run else WALK_A
        m = RUN_M if run else WALK_M
        
        mv = False
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: self.vx -= a; self.right = False; mv = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.vx += a; self.right = True; mv = True
        if not mv: self.vx *= FRIC
        if abs(self.vx) < 0.05: self.vx = 0
        self.vx = max(-m, min(m, self.vx))
        
        jk = keys[pygame.K_SPACE] or keys[pygame.K_z] or keys[pygame.K_w] or keys[pygame.K_UP]
        if self.on_ground and jk and not self.jh:
            self.vy = JMPV; self.on_ground = False; self.jh = True
        if not jk: self.jh = False
        
        self.vy += JMPG if (self.vy < 0 and jk) else GRAV
        self.vy = min(self.vy, MAXF)
        
        self.rect.x += int(self.vx)
        for b in blocks:
            if b.solid and self.rect.colliderect(b.rect):
                if self.vx > 0: self.rect.right = b.rect.left
                elif self.vx < 0: self.rect.left = b.rect.right
                self.vx = 0
        
        self.rect.y += int(self.vy)
        self.on_ground = False
        for b in blocks:
            if b.solid and self.rect.colliderect(b.rect):
                if self.vy > 0: self.rect.bottom = b.rect.top; self.vy = 0; self.on_ground = True
                elif self.vy < 0: self.rect.top = b.rect.bottom; self.vy = 0
        
        self.image = get('mario', r=self.right)
        if self.rect.top > SH: self.dead = True

class Block(Entity):
    def __init__(self, x, y, kind, w=None, h=None):
        super().__init__(x, y, w or TILE, h or TILE)
        self.kind = kind
        self.solid = kind not in ['F', 'G', 'L']
        self.hit = False
        
        sp = {'X': 'ground', 'B': 'brick', '?': 'question', 'S': 'ground', 'C': 'castle'}.get(kind)
        if sp:
            base = get(sp)
            if base: self.image = pygame.transform.scale(base, (self.rect.w, self.rect.h))
        elif kind == 'F': self.image = get('flag')
        elif kind == '-': self.image.fill(BRK)
        elif kind == 'L': self.image.fill(LVA)
        elif kind == 'G': self.image.fill(WHT); self.solid = False

    def bump(self, p):
        if self.kind == '?' and not self.hit:
            self.hit = True; p.coins += 1; p.score += 200
            self.image.fill(BK2)

class Pipe(Entity):
    """Pipe - 1.5 tiles wide for proper proportions"""
    def __init__(self, x, y, h):
        pw = int(TILE * 1.5)  # 1.5 tiles wide = 36px
        ph = TILE * h
        super().__init__(x, y, pw, ph)
        self.image = pipe_spr(h)
        self.solid = True
        self.kind = 'P'

class Enemy(Entity):
    def __init__(self, x, y, kind):
        h = int(TILE * 1.5) if kind == 'koopa' else TILE
        super().__init__(x, y, TILE, h)
        self.kind = kind
        self.dir = -1
        self.speed = 0.5
        self.alive = True
        self.dt = 0
        self.image = get('koopa' if kind == 'koopa' else 'goomba')

    def update(self, blocks):
        if not self.alive: self.dt -= 1; return self.dt > 0
        self.vx = self.dir * self.speed
        self.vy = min(self.vy + GRAV * 0.5, MAXF)
        
        self.rect.x += int(self.vx)
        for b in blocks:
            if b.solid and self.rect.colliderect(b.rect):
                if self.vx > 0: self.rect.right = b.rect.left
                else: self.rect.left = b.rect.right
                self.dir *= -1
        
        self.rect.y += int(self.vy)
        for b in blocks:
            if b.solid and self.rect.colliderect(b.rect):
                if self.vy > 0: self.rect.bottom = b.rect.top; self.vy = 0
        return self.rect.top < SH + 100

    def stomp(self): self.alive = False; self.dt = 10

# =========================
# CAMERA
# =========================
class Camera:
    def __init__(self, lw): self.x = 0; self.lw = lw
    def apply(self, r): return r.move(-self.x, 0)
    def update(self, t):
        self.x = max(self.x, t.rect.centerx - SW // 3)
        self.x = max(0, min(self.x, self.lw - SW))

# =========================
# LOADER
# =========================
def load(lid):
    d = LEVELS.get(lid, LEVELS['1-1'])
    blocks, enemies = pygame.sprite.Group(), pygame.sprite.Group()
    w, gh = d['w'], d.get('gnd', 2)
    
    for x in range(w):
        skip = any(gx <= x < gx + gw for gx, gw in d.get('gaps', []))
        if not skip:
            for gy in range(14 - gh, 14):
                blocks.add(Block(x * TILE, gy * TILE, 'X'))
    
    if d.get('ceil'):
        for x in range(w): blocks.add(Block(x * TILE, 0, 'X'))
    
    for o in d.get('obj', []):
        k, ox, oy = o[0], o[1], o[2]
        if k == 'P':
            h = o[3] if len(o) > 3 else 2
            blocks.add(Pipe(ox * TILE, oy * TILE, h))
        elif k == 'F':
            blocks.add(Block(ox * TILE, oy * TILE, 'F', TILE, TILE * 10))
        elif k == 'G':
            blocks.add(Block(ox * TILE, oy * TILE, 'G'))
        elif k == 'L':
            lw = o[3] if len(o) > 3 else 1
            for dx in range(lw): blocks.add(Block((ox+dx)*TILE, oy*TILE, 'L'))
        elif k in ['X', 'B', '?', 'S', 'C', '-']:
            bw = o[3] if len(o) > 3 else 1
            bh = o[4] if len(o) > 4 else 1
            for dx in range(bw):
                for dy in range(bh):
                    blocks.add(Block((ox+dx)*TILE, (oy+dy)*TILE, k))
    
    for e in d.get('enemies', []):
        enemies.add(Enemy(e[1]*TILE, e[2]*TILE, e[0]))
    
    sp = d.get('spawn', (3, 12))
    return blocks, enemies, d.get('theme', 'sky'), d.get('time', 400), (sp[0]*TILE, sp[1]*TILE), w*TILE

# =========================
# GAME
# =========================
class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Cat's SMB v6 - Proper Pipe Size!")
        self.scr = pygame.display.set_mode((SW, SH))
        self.clk = pygame.time.Clock()
        self.fnt = pygame.font.Font(None, 24)
        self.w = self.s = 1
        self.paused = False
        self.load()
        print("=" * 40)
        print("Cat's SMB v6")
        print("Pipes are now 1.5 tiles wide")
        print("Mario is 1 tile wide")
        print("=" * 40)

    def load(self):
        self.blocks, self.enemies, self.theme, self.time, sp, lw = load(f'{self.w}-{self.s}')
        self.player = Player(sp[0], sp[1])
        self.tleft = float(self.time)
        self.cam = Camera(lw)

    def nxt(self):
        self.s += 1
        if self.s > 4: self.s = 1; self.w += 1
        if self.w > 8: self.w = self.s = 1
        self.load()

    def die(self):
        self.player.lives -= 1
        if self.player.lives <= 0:
            self.w = self.s = 1
            self.player.lives = 3; self.player.score = self.player.coins = 0
        self.load()

    def run(self):
        running = True
        while running:
            dt = self.clk.tick(FPS) / 1000.0
            
            for e in pygame.event.get():
                if e.type == pygame.QUIT: running = False
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE: self.paused = not self.paused
                    elif e.key == pygame.K_n: self.nxt()
                    elif e.key == pygame.K_r: self.load()
            
            if self.paused:
                self.scr.blit(self.fnt.render("PAUSED", True, WHT), (SW//2-30, SH//2))
                pygame.display.flip(); continue
            
            keys = pygame.key.get_pressed()
            self.player.update(keys, self.blocks)
            
            for en in list(self.enemies):
                if not en.update(self.blocks): self.enemies.remove(en)
            
            for en in self.enemies:
                if not en.alive: continue
                if self.player.rect.colliderect(en.rect):
                    if self.player.vy > 0 and self.player.rect.bottom < en.rect.centery + 4:
                        en.stomp(); self.player.vy = -JMPV * 0.5; self.player.score += 100
                    else: self.player.dead = True
            
            for b in self.blocks:
                if not self.player.rect.colliderect(b.rect): continue
                if b.kind == 'F': self.player.score += 1000; self.nxt(); break
                elif b.kind == 'G': self.player.score += 5000; self.nxt(); break
                elif b.kind == 'L' and self.player.rect.bottom > b.rect.top + 2: self.player.dead = True
            
            self.cam.update(self.player)
            self.tleft -= dt
            if self.tleft <= 0: self.player.dead = True
            if self.player.dead: self.die(); continue
            
            self.scr.fill(SKY if self.theme == 'sky' else BLK)
            for b in self.blocks:
                sr = self.cam.apply(b.rect)
                if -TILE*2 < sr.x < SW + TILE*2:
                    self.scr.blit(b.image, sr)
            for en in self.enemies:
                if en.alive or en.dt > 0: self.scr.blit(en.image, self.cam.apply(en.rect))
            self.scr.blit(self.player.image, self.cam.apply(self.player.rect))
            
            # HUD
            pygame.draw.rect(self.scr, BLK, (0, 0, SW, 30))
            txt = f"MARIO {self.player.score:06d}  x{self.player.coins:02d}  WORLD {self.w}-{self.s}  TIME {int(max(0,self.tleft)):03d}  x{self.player.lives}"
            self.scr.blit(self.fnt.render(txt, True, WHT), (10, 8))
            
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    Game().run()
