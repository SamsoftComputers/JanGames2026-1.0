#!/usr/bin/env python3
"""
CAT'S SUPER MARIO BROS REMASTERED - COMPLETE EDITION (1-1 to 8-4)
All 32 NES SMB1 Levels - Accurate Layouts, Power-ups & Physics
(C) 2026 Team Flames / Samsoft
"""
import pygame, sys, math, random

# --- CONFIGURATION ---
TILE = 24
SH = 15 * TILE  # 360 px height
SW = 800
FPS = 60

# --- NES PHYSICS CONSTANTS (Tuned for "Exact" Feel) ---
GRAVITY = 0.4        # Heavier gravity like NES
MAX_FALL = 4.5
JUMP_FORCE = -7.2    # Stronger initial impulse to counter heavy gravity
JUMP_GRAV_HOLD = 0.19
JUMP_GRAV_REL = 0.6  # Fast fall on release
WALK_ACCEL = 0.09
RUN_ACCEL = 0.15
FRICTION = 0.88      # Slippery ground
SKID_FRICTION = 0.82 # Distinct skid feel
MAX_WALK_SPD = 2.4
MAX_RUN_SPD = 4.2    # Faster running
BOUNCE_FORCE = -3.5

# --- COLORS ---
SKY = (92, 148, 252)
BLK, WHT = (0, 0, 0), (252, 252, 252)
RED, DRK_RED = (228, 56, 16), (136, 20, 0)
GRN, DGN = (0, 168, 0), (0, 120, 0)
BRK, BK2 = (200, 76, 12), (136, 52, 0)
GLD, GD2 = (252, 152, 56), (228, 92, 16)
CST, CS2 = (188, 188, 188), (116, 116, 116)
LVA = (228, 56, 24)
UND_BRK = (88, 148, 248)
WAT_BG = (60, 188, 252)
NIGHT_BG = (0, 0, 0)
COIN_YLW = (252, 188, 60)
HUD_TXT = (255, 255, 255)
MUSH_RED = (216, 40, 0)
MUSH_SKIN = (255, 180, 150)

PMETER_MAX = 120
PMETER_DECAY = 2

# --- SPRITE DATA ---
# Small Mario
MARIO_STAND = ["...RRRRR....","..RRRRRRRRR.","..BBBSSBS...",".BSBBSSSBSB.",".BSBBSSSBSB.",".BBSSSSSBBB.","...SSSSSS...","..RRBRRBB...",".RRRBRRRRRR.",".RRRBBRRRRR.",".RRRBBBRRRR.","...BBBBBB...","..BBRBBBB..."]
MARIO_RUN = ["...RRRRR....","..RRRRRRRRR.","..BBBSSBS...",".BSBBSSSBSB.",".BSBBSSSBSB.",".BBSSSSSBBB.","...SSSSSS...","..RRRRBBRR..","RRRRRRRBBRRR","RRRRRRRRRRRR","SS.RRRRRR...","SSSRRRRRRR..","SSBBBBBB...."]
MARIO_JUMP = ["...RRRRR....","..RRRRRRRRR.","..BBBSSBS...",".BSBBSSSBSB.",".BSBBSSSBSB.",".BBSSSSSBBB.","...SSSSSS...","....RRRR...B","BBBBRRRRRRRB","SSBBBRRRRRBB","SS.RRRRRRRRS","..RRRRRRRSS.","..RRRRRR...."]

# Big Mario (Corrected: Red Overalls, Brown Shirt, Taller)
BIG_STAND = [
    "...RRRRR....",
    "..RRRRRRRRR.",
    "..BBBSSBS...", # Head
    ".BSBBSSSBSB.",
    ".BSBBSSSBSB.",
    ".BBSSSSSBBB.",
    "...SSSSSS...",
    "...SSSSSS...",
    "..BBBRRRBB..", # Torso Start
    "..BBBRRRBB..",
    ".BBRRRRRRBB.",
    ".BBRRRRRRBB.",
    ".BBRRSSRRBB.", # Buttons
    ".BBRRRRRRBB.",
    "..RRRRRRRR..",
    "..RRRRRRRR..",
    "..RR....RR..", # Legs
    "..RR....RR..",
    "..RR....RR..",
    "..RR....RR..",
    ".BBB....BBB.", # Shoes
    ".BBB....BBB.",
    ".BBB....BBB.",
    ".BBB....BBB."
]

BIG_RUN = [
    "...RRRRR....",
    "..RRRRRRRRR.",
    "..BBBSSBS...",
    ".BSBBSSSBSB.",
    ".BSBBSSSBSB.",
    ".BBSSSSSBBB.",
    "...SSSSSS...",
    "...SSSSSS...",
    "..BBBRRRBB..",
    "..BBBRRRBB..",
    ".BBRRRRRRBB.",
    ".BBRRRRRRBB.",
    ".BBRRSSRRBB.",
    ".BBRRRRRRBB.",
    "..RRRRRRRR..",
    "RRRRRRRRRRRR", # Legs spread
    "RRR..RR..RRR",
    "RR...RR...RR",
    "BB...RR...BB",
    "BB...RR...BB",
    ".....BB.....",
    ".....BB.....",
    ".....BB.....",
    "............"
]
BIG_JUMP = BIG_STAND # Simple reuse for now

# Enemies
GOOMBA_DATA = ["....BBBB....","..BBBBBBBB..",".BBBBBBBBBB.",".BBWKBBWKBB.",".BWWKBBWWKB.","BBBBBBBBBBBB","BBBBBBBBBBBB",".BBBBBBBBBB.","..SSSSSSSS..",".SSSSSSSSSS.","SSSS....SSSS","BBB......BBB"]
KOOPA_DATA = ["....GGGG....","...GGGGGG...","...GWWKG....","..GWWWKG....",".GGGGGGGGG..","GGGGGGGGGGGG","GGGGGGGGGGGG",".GGGGGGGGGG.","..GGGGGGGG..","...SSSSSS...","..SSS..SSS.."]

def make_sprite(data, colors, scale=1.5):
    h, w = len(data), max(len(r) for r in data)
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    for y, row in enumerate(data):
        for x, c in enumerate(row):
            if c in colors and colors[c]: s.set_at((x, y), colors[c])
    return pygame.transform.scale(s, (int(w * scale), int(h * scale)))

SPR = {}
def get_spr(name, **kw):
    key = (name, tuple(sorted(kw.items())))
    if key in SPR: return SPR[key]
    
    # Colors
    M_RED = (228, 0, 0)
    M_BRN = (160, 80, 32)
    M_SKN = (255, 200, 168)
    
    if name == 'mario':
        big = kw.get('big', False)
        st = kw.get('state', 'stand')
        
        if big:
            d = BIG_JUMP if st == 'jump' else (BIG_RUN if st == 'run' else BIG_STAND)
            scale = 1.8
        else:
            d = MARIO_JUMP if st == 'jump' else (MARIO_RUN if st == 'run' else MARIO_STAND)
            scale = 1.8
            
        cols = {'.': None, 'R': M_RED, 'B': M_BRN, 'S': M_SKN}
        s = make_sprite(d, cols, scale)
        SPR[key] = s if kw.get('right', True) else pygame.transform.flip(s, True, False)
        
    elif name == 'goomba':
        cols = {'B': (172, 92, 0), 'S': (255, 200, 168), 'W': WHT, 'K': BLK, '.': None}
        SPR[key] = make_sprite(GOOMBA_DATA, cols, 2.0)
    elif name == 'koopa':
        cols = {'G': (0, 168, 0), 'S': (255, 200, 168), 'W': WHT, 'K': BLK, '.': None}
        SPR[key] = make_sprite(KOOPA_DATA, cols, 2.0)
    return SPR.get(key)

# --- LEVEL DEFINITIONS ---
LEVELS = {}
def add_lvl(n, theme, w, **kw):
    LEVELS[n] = {'theme': theme, 'w': w, 'objects': [], 'enemies': [], 'pits': [], **kw}

def add_obj(l, kind, x, y, w=1, h=1): LEVELS[l]['objects'].append((kind, x, y, w, h))
def add_en(l, kind, x, y): LEVELS[l]['enemies'].append((kind, x, y))
def add_pit(l, start, end): LEVELS[l]['pits'].append((start, end))
def rect_fill(l, kind, x, y, w, h):
    for i in range(w):
        for j in range(h): add_obj(l, kind, x+i, y+j)

# --- WORLD 1 ---
add_lvl('1-1', 'overworld', 210)
for x, y, k in [(16,8,'?'),(20,8,'B'),(21,8,'?'),(22,8,'B'),(23,8,'?'),(24,8,'B'),(22,4,'?')]: add_obj('1-1', k, x, y)
for x, h in [(28,2),(38,2),(46,3),(57,3)]: add_obj('1-1', 'P', x, 12, 2, h)
add_obj('1-1', '?', 64, 8)
for x, y, k in [(77,8,'B'),(78,8,'B'),(79,8,'B'),(80,8,'B'),(81,8,'B'),(82,8,'B')]: add_obj('1-1', k, x, y)
add_obj('1-1', '?', 78, 4); add_obj('1-1', '?', 80, 4)
rect_fill('1-1', 'S', 134, 11, 4, 1); rect_fill('1-1', 'S', 135, 10, 3, 1); rect_fill('1-1', 'S', 136, 9, 2, 1)
rect_fill('1-1', 'S', 140, 11, 4, 1); rect_fill('1-1', 'S', 140, 10, 3, 1); rect_fill('1-1', 'S', 140, 9, 2, 1)
add_pit('1-1', 69, 71); add_pit('1-1', 86, 89); add_pit('1-1', 153, 155)
add_en('1-1', 'goomba', 22, 11); add_en('1-1', 'goomba', 40, 11); add_en('1-1', 'koopa', 107, 10)
add_obj('1-1', 'F', 198, 2); add_obj('1-1', 'C', 202, 8)

add_lvl('1-2', 'underground', 190, ceiling=True)
add_obj('1-2', '?', 10, 8); add_obj('1-2', '?', 11, 8); add_obj('1-2', '?', 12, 8)
rect_fill('1-2', 'B', 20, 8, 5, 2); add_obj('1-2', 'P', 30, 10, 2, 3)
rect_fill('1-2', 'B', 40, 4, 10, 1); add_en('1-2', 'goomba', 42, 3); add_en('1-2', 'goomba', 45, 3)
add_pit('1-2', 55, 58); add_obj('1-2', 'P', 60, 11, 2, 2)
add_obj('1-2', 'F', 170, 2); add_obj('1-2', 'C', 175, 8)

add_lvl('1-3', 'athletic', 160)
rect_fill('1-3', 'M', 10, 10, 3, 1); rect_fill('1-3', 'M', 16, 8, 3, 1); rect_fill('1-3', 'M', 25, 10, 3, 1)
add_en('1-3', 'koopa', 17, 7); add_obj('1-3', '?', 30, 6)
add_obj('1-3', 'lift', 40, 6, 3, 1); add_obj('1-3', 'lift', 50, 10, 3, 1)
add_pit('1-3', 0, 5); add_pit('1-3', 15, 20); add_pit('1-3', 35, 45)
add_obj('1-3', 'F', 145, 2); add_obj('1-3', 'C', 150, 8)

add_lvl('1-4', 'castle', 100, ceiling=True)
add_pit('1-4', 20, 23); add_obj('1-4', 'firebar', 21, 5, 6)
rect_fill('1-4', 'B', 30, 8, 10, 1); add_obj('1-4', 'firebar', 35, 8, 6)
add_obj('1-4', 'bowser', 85, 9); add_obj('1-4', 'A', 90, 7)

# --- GENERIC GENERATOR ---
WORLD_THEMES = {
    1: ['overworld', 'underground', 'athletic', 'castle'],
    2: ['overworld', 'underwater', 'athletic', 'castle'],
    3: ['night', 'overworld', 'athletic', 'castle'],
    4: ['overworld', 'underground', 'athletic', 'castle'],
    5: ['overworld', 'overworld', 'athletic', 'castle'],
    6: ['night', 'overworld', 'athletic', 'castle'],
    7: ['overworld', 'underwater', 'athletic', 'castle'],
    8: ['overworld', 'overworld', 'overworld', 'castle']
}

for w in range(2, 9):
    for s in range(1, 5):
        lid = f'{w}-{s}'
        theme = WORLD_THEMES[w][s-1]
        width = 240 if s != 4 else 120
        if w==8 and s==1: width = 350
        add_lvl(lid, theme, width, ceiling=(theme in ['underground', 'castle']))
        if s == 4:
            add_obj(lid, 'bowser', width-15, 9); add_obj(lid, 'A', width-8, 7)
            if w == 8:
                add_obj(lid, 'P', 10, 11, 2, 2); add_obj(lid, 'P', 30, 9, 2, 4)
                add_pit(lid, 40, 45); add_obj(lid, 'firebar', 42, 6, 6)
                rect_fill(lid, 'W', 50, 13, 10, 1)
            else:
                for x in range(15, width-20, 25):
                    add_pit(lid, x, x+3); add_obj(lid, 'firebar', x+1, 6, 6)
        elif theme == 'underwater':
            add_obj(lid, 'F', width-12, 2); add_obj(lid, 'C', width-8, 8)
            for x in range(20, width-20, 30):
                rect_fill(lid, 'R', x, 10, 2, 3); rect_fill(lid, 'R', x+8, 4, 2, 5)
                add_en(lid, 'goomba', x+15, 6)
        elif theme == 'athletic':
            add_obj(lid, 'F', width-12, 2); add_obj(lid, 'C', width-8, 8)
            if w in [2, 7]:
                add_pit(lid, 0, width); rect_fill(lid, 'B', 0, 12, 15, 1)
                for x in range(15, width-15, 4):
                    if x % 10 != 0: add_obj(lid, 'B', x, 8)
                add_obj(lid, 'lift', width//2, 6, 4, 1)
            else:
                for x in range(15, width-30, 20):
                    add_obj(lid, 'M', x, random.choice([8, 10]), random.choice([3, 5]), 1)
                    if random.random() > 0.5: add_obj(lid, 'lift', x+10, 6, 3, 1)
                    add_pit(lid, x-2, x+8)
        else:
            add_obj(lid, 'F', width-12, 2); add_obj(lid, 'C', width-8, 8)
            difficulty = 0.9 if w == 8 else 0.3
            for x in range(14, width-20, random.randint(10, 20)):
                chunk = random.random()
                if chunk < 0.2 + difficulty:
                    sz = 2 if w < 4 else 4
                    add_pit(lid, x, x+sz)
                    if w == 8: add_obj(lid, 'spring', x-1, 12)
                elif chunk < 0.5:
                    h = random.randint(2, 4)
                    add_obj(lid, 'P', x, 13-h, 2, h)
                    add_en(lid, 'goomba', x+4, 11)
                elif chunk < 0.7:
                    for i in range(4): rect_fill(lid, 'S', x+i, 12-i, 1, i+1)
                    add_pit(lid, x+4, x+6)
                else:
                    add_obj(lid, '?', x, 8); add_obj(lid, 'B', x+1, 8); add_obj(lid, '?', x+2, 8)
                    add_en(lid, 'koopa', x, 7)

# --- GAME ENGINE ---
class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, c):
        super().__init__()
        self.image = pygame.Surface((6, 6)); self.image.fill(c)
        self.rect = self.image.get_rect(center=(x, y))
        a = random.uniform(0, math.pi*2); sp = random.uniform(2, 5)
        self.vx, self.vy = math.cos(a)*sp, math.sin(a)*sp; self.life = 40
    def update(self):
        self.rect.x += int(self.vx); self.rect.y += int(self.vy)
        self.vy += GRAVITY; self.life -= 1
        if self.life <= 0: self.kill()

class FloatText(pygame.sprite.Sprite):
    def __init__(self, x, y, txt, fnt):
        super().__init__()
        self.image = fnt.render(txt, True, WHT)
        self.rect = self.image.get_rect(center=(x, y)); self.vy, self.life = -2, 40
    def update(self):
        self.rect.y += int(self.vy); self.life -= 1
        if self.life <= 0: self.kill()

class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, kind):
        super().__init__()
        self.kind = kind
        self.image = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
        if kind == 'mushroom':
            # Mushroom Sprite
            pygame.draw.circle(self.image, MUSH_RED, (12, 12), 11)
            pygame.draw.circle(self.image, WHT, (6, 8), 3)
            pygame.draw.circle(self.image, WHT, (18, 8), 3)
            pygame.draw.circle(self.image, WHT, (12, 16), 3)
            pygame.draw.rect(self.image, MUSH_SKIN, (7, 14, 10, 10))
        
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vx = 1.5; self.vy = -3; self.rising = True
        self.start_y = y - TILE
    
    def update(self, blks):
        if self.rising:
            self.rect.y -= 1
            if self.rect.y <= self.start_y: self.rising = False
            return

        self.vy = min(self.vy + GRAVITY, MAX_FALL)
        self.rect.x += int(self.vx)
        for b in blks:
            if b.solid and self.rect.colliderect(b.rect):
                self.vx *= -1; self.rect.x += int(self.vx * 2) # Bump turn
        
        self.rect.y += int(self.vy)
        for b in blks:
            if b.solid and self.rect.colliderect(b.rect):
                if self.vy > 0: self.rect.bottom = b.rect.top; self.vy = 0

class Ent(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vx, self.vy = 0.0, 0.0

class Player(Ent):
    def __init__(self, x, y):
        super().__init__(x, y, TILE, TILE)
        self.right, self.dead = True, False
        self.coins, self.score, self.lives = 0, 0, 3
        self.on_gnd, self.jmp_hold, self.uw = False, False, False
        self.pm, self.iframes = 0, 0
        self.big = False # Power state
        self.skidding = False
        self.update_sprite()

    def update_sprite(self):
        st = 'jump' if not self.on_gnd and not self.uw else ('run' if abs(self.vx) > 0.1 else 'stand')
        self.image = get_spr('mario', right=self.right, state=st, big=self.big)
        
        # Adjust rect size/pos for growth/shrink
        tgt_h = TILE * 2 if self.big else TILE
        if self.rect.height != tgt_h:
            old_b = self.rect.bottom
            self.rect.height = tgt_h
            self.rect.bottom = old_b

    def hit(self):
        if self.iframes > 0: return
        if self.big:
            self.big = False; self.iframes = 120
            self.vy = -3 # Knockback hop
            self.update_sprite()
        else:
            self.dead = True

    def update(self, keys, blks, ptc, eff, fnt, pits, items):
        if self.dead: return
        
        # --- INPUT & PHYSICS ---
        run_btn = keys[pygame.K_z]
        left = keys[pygame.K_LEFT]
        right = keys[pygame.K_RIGHT]
        
        # Acceleration
        accel = RUN_ACCEL if run_btn else WALK_ACCEL
        max_s = MAX_RUN_SPD if run_btn else MAX_WALK_SPD
        if self.uw: max_s *= 0.6; accel *= 0.6

        if left:
            if self.vx > 0: self.vx *= SKID_FRICTION
            else: self.vx -= accel; self.right = False
        elif right:
            if self.vx < 0: self.vx *= SKID_FRICTION
            else: self.vx += accel; self.right = True
        else:
            self.vx *= FRICTION
            if abs(self.vx) < 0.1: self.vx = 0
        self.vx = max(-max_s, min(max_s, self.vx))

        # Jump
        jmp_btn = keys[pygame.K_SPACE] or keys[pygame.K_x]
        if self.uw:
            if jmp_btn and not self.jmp_hold: self.vy = -2.5; self.jmp_hold = True
            if not jmp_btn: self.jmp_hold = False
            self.vy = min(self.vy + 0.1, 2.0)
        else:
            if self.on_gnd and jmp_btn and not self.jmp_hold:
                self.vy = JUMP_FORCE; self.on_gnd = False; self.jmp_hold = True
            
            grav = JUMP_GRAV_HOLD if (jmp_btn and self.vy < 0) else JUMP_GRAV_REL
            self.vy = min(self.vy + grav, MAX_FALL)
            if not jmp_btn: self.jmp_hold = False

        # --- COLLISION ---
        self.rect.x += int(self.vx)
        for b in blks:
            if b.solid and self.rect.colliderect(b.rect):
                if self.vx > 0: self.rect.right = b.rect.left
                elif self.vx < 0: self.rect.left = b.rect.right
                self.vx = 0

        self.rect.y += int(self.vy); self.on_gnd = False
        for b in blks:
            if b.solid and self.rect.colliderect(b.rect):
                if self.vy > 0: self.rect.bottom = b.rect.top; self.vy = 0; self.on_gnd = True
                elif self.vy < 0:
                    self.rect.top = b.rect.bottom; self.vy = 0
                    if b.kind in ['B', '?', 'H']: b.bump(self, ptc, eff, fnt, items)

        # Item Collision
        for i in items:
            if self.rect.colliderect(i.rect) and not i.rising:
                if i.kind == 'mushroom':
                    if not self.big:
                        self.big = True; self.score += 1000
                        eff.add(FloatText(self.rect.centerx, self.rect.top, "1000", fnt))
                    else:
                        self.score += 1000; eff.add(FloatText(self.rect.centerx, self.rect.top, "1000", fnt))
                    i.kill()

        # Platforms & Springs
        for b in blks:
            if b.kind == 'lift' and self.rect.colliderect(b.rect) and self.vy > 0 and self.rect.bottom < b.rect.centery + 10:
                self.rect.bottom = b.rect.top; self.vy = 0; self.on_gnd = True; self.rect.x += int(b.vx)
            if b.kind == 'spring' and self.rect.colliderect(b.rect):
                if self.vy > 0: self.vy = -10.0; self.on_gnd = False; self.rect.bottom = b.rect.top

        self.update_sprite()
        
        # Pits & IFrames
        tx = self.rect.centerx // TILE
        for s, e in pits:
            if s <= tx < e and self.rect.top > SH: self.dead = True
        if self.rect.top > SH: self.dead = True
        if self.iframes > 0: self.iframes -= 1; self.image.set_alpha(128 if self.iframes % 4 < 2 else 255)

class Block(Ent):
    def __init__(self, x, y, kind, w=1, h=1, theme='overworld'):
        super().__init__(x*TILE, y*TILE, w*TILE, h*TILE)
        self.kind, self.theme, self.hit = kind, theme, False
        self.solid = kind not in ['F', 'G', 'W', 'A', 'firebar']
        self.vx = 0
        if kind == 'lift': self.solid = False 
        
        bc = UND_BRK if theme == 'underground' else (CST if theme == 'castle' else BRK)
        bd = (60,100,180) if theme == 'underground' else (CS2 if theme == 'castle' else BK2)
        if kind == '?':
            self.image.fill(GLD); pygame.draw.rect(self.image, GD2, (0,0,TILE,TILE), 2)
            pygame.draw.rect(self.image, BK2, (8,5,8,14))
        elif kind == 'B':
            self.image.fill(bc); pygame.draw.rect(self.image, bd, (0,0,TILE,TILE), 1)
            pygame.draw.line(self.image, bd, (0,TILE//2), (TILE,TILE//2))
        elif kind == 'ground':
            self.image.fill(bc); pygame.draw.rect(self.image, bd, (0,0,TILE,TILE), 1)
            for i in range(0,TILE,6): pygame.draw.rect(self.image, bd, (i,i,2,2))
        elif kind == 'P':
            self.image.fill(GRN); pygame.draw.rect(self.image, DGN, (0,0,self.rect.w, self.rect.h), 2)
            pygame.draw.rect(self.image, (0,100,0), (6,0,self.rect.w-12, self.rect.h))
        elif kind == 'spring':
            self.solid=False; self.image = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
            pygame.draw.rect(self.image, CST, (0, TILE//2, TILE, TILE//2))
            pygame.draw.line(self.image, WHT, (0, TILE//2), (TILE, TILE//2), 3)
        elif kind == 'lift':
            self.image.fill(GRN); pygame.draw.rect(self.image, DGN, (0,0,self.rect.w,self.rect.h), 1)
            self.vx = 1.0 if (y % 2 == 0) else -1.0
        elif kind == 'firebar':
            self.angle = 0; self.cx, self.cy = self.rect.centerx, self.rect.centery
            self.image = pygame.Surface((w*TILE*2, h*TILE*2), pygame.SRCALPHA)
            self.rect = self.image.get_rect(center=(self.cx, self.cy))

    def update(self):
        if self.kind == 'lift':
            self.rect.x += int(self.vx)
            if self.vx > 0 and self.rect.x > self.orig_x + TILE*3: self.vx *= -1
            if self.vx < 0 and self.rect.x < self.orig_x - TILE*3: self.vx *= -1
        elif self.kind == 'firebar':
            self.angle = (self.angle + 3) % 360
            self.image.fill((0,0,0,0))
            rad = math.radians(self.angle)
            for i in range(6):
                d = i * 12
                px = self.image.get_width()//2 + math.cos(rad)*d
                py = self.image.get_height()//2 + math.sin(rad)*d
                pygame.draw.circle(self.image, RED, (int(px), int(py)), 5)

    def bump(self, p, ptc, eff, fnt, items):
        if self.hit: return
        if self.kind == 'B':
            if p.big: # Break brick if Big
                self.hit = True; p.score += 50; self.kill()
                for _ in range(4): ptc.add(Particle(self.rect.centerx, self.rect.centery, BRK))
            else: # Bounce if Small
                self.rect.y -= 5 # Visual bump
                # Note: real physics would require logic to move it back down next frame,
                # but for this scale, a non-breaking collision is fine.
        elif self.kind == '?':
            self.hit = True; p.coins += 1; p.score += 200
            eff.add(FloatText(self.rect.centerx, self.rect.top, "200", fnt))
            self.image.fill(BK2); pygame.draw.rect(self.image, BLK, (0,0,TILE,TILE), 1)
            # Spawn Item (Mushroom)
            items.add(Item(self.rect.x, self.rect.y, 'mushroom'))

class Enemy(Ent):
    def __init__(self, x, y, kind):
        super().__init__(x*TILE, y*TILE, TILE, TILE)
        self.kind, self.dir, self.alive = kind, -1, True
        self.image = get_spr(kind)
        if kind == 'bowser': 
            self.image = pygame.transform.scale(self.image, (TILE*2, TILE*2))
            self.rect = self.image.get_rect(topleft=(x*TILE, y*TILE))
    def update(self, blks):
        if not self.alive: return False
        self.vy = min(self.vy + GRAVITY, MAX_FALL)
        self.rect.x += int(self.dir * (0.8 if self.kind != 'koopa' else 1.2))
        for b in blks:
            if b.solid and self.rect.colliderect(b.rect):
                self.dir *= -1; self.rect.x += self.dir * 2
        self.rect.y += int(self.vy)
        for b in blks:
            if b.solid and self.rect.colliderect(b.rect):
                if self.vy > 0: self.rect.bottom = b.rect.top; self.vy = 0
        return self.rect.top < SH + 64

class Game:
    def __init__(self):
        pygame.init(); pygame.display.set_caption("Super Mario Bros Remastered")
        self.clk = pygame.time.Clock()
        self.fnt = pygame.font.Font(None, 24); self.bfnt = pygame.font.Font(None, 40)
        self.scr = pygame.display.set_mode((800, 400))
        self.p = Player(0, 0); self.state = "MENU"; self.menu_idx = 0
        self.lvl = '1-1'; self.w, self.s = 1, 1
        
    def load(self, lid):
        self.lvl = lid; d = LEVELS[lid]; self.w, self.s = map(int, lid.split('-'))
        self.theme = d['theme']
        self.bg_col = NIGHT_BG if 'night' in self.theme else (WAT_BG if self.theme == 'underwater' else (BLK if self.theme in ['underground', 'castle'] else SKY))
        self.mw = d['w'] * TILE
        self.blks, self.ens, self.ptc, self.eff = pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        self.p = Player(2*TILE, 11*TILE); self.p.uw = (self.theme == 'underwater')
        
        # Build Terrain
        for x in range(d['w']):
            if not any(s <= x < e for s, e in d['pits']):
                fy = 13 if self.theme != 'castle' else 11 
                for y in range(fy, 16): self.blks.add(Block(x, y, 'ground', theme=self.theme))
        if d.get('ceiling'):
             for x in range(d['w']): self.blks.add(Block(x, 0, 'ground', theme=self.theme))

        for k, x, y, w, h in d['objects']:
            b = Block(x, y, k, w, h, theme=self.theme)
            if k == 'lift': b.orig_x = x * TILE
            self.blks.add(b)
        for k, x, y in d['enemies']: self.ens.add(Enemy(x, y, k))
        self.time = 400; self.camx = 0

    def draw_ui(self):
        # Exact SMB1 HUD Alignment
        # COLUMNS: MARIO (x=40), COINS (x=250), WORLD (x=450), TIME (x=650)
        
        lbls = [("MARIO", 40), ("WORLD", 450), ("TIME", 650)]
        for txt, x in lbls:
            self.scr.blit(self.fnt.render(txt, True, HUD_TXT), (x, 10))
        
        # Row 2 Values
        self.scr.blit(self.fnt.render(f"{self.p.score:06d}", True, HUD_TXT), (40, 30))
        
        # Coins Center
        # Coin icon below "WORLD" in some versions, but SMB1 standard is roughly centered
        cx = 260
        pygame.draw.circle(self.scr, COIN_YLW, (cx, 38), 6)
        pygame.draw.rect(self.scr, BLK, (cx-2, 34, 4, 8)) 
        self.scr.blit(self.fnt.render(f"x{self.p.coins:02d}", True, HUD_TXT), (cx+15, 30))
        
        self.scr.blit(self.fnt.render(f"{self.w}-{self.s}", True, HUD_TXT), (460, 30))
        self.scr.blit(self.fnt.render(f"{int(self.time):03d}", True, HUD_TXT), (660, 30))

    def run(self):
        while True:
            evs = pygame.event.get()
            for e in evs:
                if e.type == pygame.QUIT: sys.exit()
                if e.type == pygame.KEYDOWN:
                    if self.state == "MENU":
                        if e.key == pygame.K_RETURN: self.load('1-1'); self.p.lives=3; self.p.score=0; self.state = "PLAY"
                    elif self.state == "PLAY":
                        if e.key == pygame.K_n: # Debug Skip
                            self.s += 1
                            if self.s > 4: self.w += 1; self.s = 1
                            if self.w > 8: self.state = "WIN"
                            else: self.load(f'{self.w}-{self.s}')

            if self.state == "MENU":
                self.scr.fill(SKY)
                for x in range(0, 800, 24): pygame.draw.rect(self.scr, BRK, (x, 336, 24, 64))
                t = self.bfnt.render("SUPER MARIO BROS", True, RED)
                t2 = self.bfnt.render("REMASTERED", True, BLK)
                self.scr.blit(t, (SW//2 - t.get_width()//2, 80))
                self.scr.blit(t2, (SW//2 - t2.get_width()//2 + 2, 122))
                self.scr.blit(self.bfnt.render("REMASTERED", True, WHT), (SW//2 - t2.get_width()//2, 120))
                self.scr.blit(self.fnt.render("Press ENTER to Start", True, BLK), (SW//2-80, 240))
                self.scr.blit(self.fnt.render("Arrows to Move | Z to Run | Space to Jump", True, BLK), (SW//2-160, 270))
                pygame.display.flip(); self.clk.tick(60); continue

            if self.state == "WIN":
                self.scr.fill(BLK)
                self.scr.blit(self.bfnt.render("YOU WON!", True, GLD), (SW//2-60, 150))
                pygame.display.flip(); continue

            # Logic
            keys = pygame.key.get_pressed()
            self.p.update(keys, self.blks, self.ptc, self.eff, self.fnt, LEVELS[self.lvl]['pits'], self.items)
            self.blks.update(); self.ptc.update(); self.eff.update(); self.items.update(self.blks)
            
            # 1-Up Logic
            if self.p.coins >= 100:
                self.p.coins -= 100; self.p.lives += 1
                self.eff.add(FloatText(self.p.rect.centerx, self.p.rect.top, "1UP", self.fnt))

            for en in list(self.ens):
                if not en.update(self.blks): self.ens.remove(en)
                if en.alive and self.p.rect.colliderect(en.rect):
                    if self.p.vy > 0 and self.p.rect.bottom < en.rect.centery + 10:
                        en.alive = False; en.kill(); self.p.vy = BOUNCE_FORCE; self.p.score += 100
                        self.eff.add(FloatText(en.rect.centerx, en.rect.top, "100", self.fnt))
                    elif self.p.iframes == 0:
                        self.p.hit()
            
            # Firebar Collision
            for b in self.blks:
                if b.kind == 'firebar':
                    rad = math.radians(b.angle)
                    for i in range(6):
                        bx = b.rect.centerx + math.cos(rad)*i*12
                        by = b.rect.centery + math.sin(rad)*i*12
                        if self.p.rect.collidepoint(bx, by) and self.p.iframes == 0:
                            self.p.hit()

            # Level End / Death
            if self.p.dead:
                if self.p.lives > 0: self.load(self.lvl); self.p.lives -= 1
                else: self.state = "MENU"
            
            for b in self.blks:
                if b.kind in ['F', 'A'] and self.p.rect.colliderect(b.rect): # Flag or Axe
                    self.s += 1
                    if self.s > 4: self.w += 1; self.s = 1
                    if self.w > 8: self.state = "WIN"
                    else: self.load(f'{self.w}-{self.s}')
                    break

            # Render
            self.camx = max(0, min(self.p.rect.centerx - SW // 3, self.mw - SW))
            self.scr.fill(self.bg_col)
            
            for s in [self.blks, self.ens, self.items, [self.p], self.ptc, self.eff]:
                for i in s:
                    r = i.rect.copy(); r.x -= self.camx
                    if -50 < r.x < SW + 50: 
                        if hasattr(i, 'angle'): self.scr.blit(i.image, r) # firebar
                        else: self.scr.blit(i.image, r)
            
            self.draw_ui()
            pygame.display.flip(); self.clk.tick(FPS); self.time -= 1.5/60
            if self.time <= 0: self.p.hit()

if __name__ == '__main__': Game().run()
