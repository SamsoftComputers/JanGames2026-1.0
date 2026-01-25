#!/usr/bin/env python3
"""
CAT'S SUPER MARIO BROS v8 (GBA Edition)
FIXED: Pits work properly + GBA Style Mario sprite
(C) 2026 Team Flames / Samsoft
"""

import pygame
import sys

# =========================
# CONFIG
# =========================
SW, SH = 800, 480
FPS = 60
TILE = 24

# Physics
GRAV = 0.25
MAXF = 3.0
WALK_A = 0.06
RUN_A = 0.10
WALK_M = 1.1
RUN_M = 1.9
FRIC = 0.88
JMPV = -4.2
JMPG = 0.12

# NES Palette (Keep for world)
SKY = (92, 148, 252)
BLK = (0, 0, 0)
WHT = (252, 252, 252)
RED = (228, 56, 16)
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

# GBA Mario Specific Palette (Richer colors)
GBA_RED = (248, 56, 0)      # Bright Red
GBA_DRK = (168, 16, 0)      # Dark Red (Shadow)
GBA_SKN = (248, 216, 168)   # Skin
GBA_SKD = (216, 160, 104)   # Dark Skin (Shadow)
GBA_BLU = (40, 96, 248)     # Overalls Blue
GBA_BLD = (0, 0, 168)       # Dark Blue (Shadow)
GBA_BRN = (136, 88, 24)     # Brown (Shoes/Hair)
GBA_YLW = (248, 216, 0)     # Buttons
GBA_GRY = (192, 192, 192)   # Glove Shadow

# =========================
# GBA STYLE MARIO SPRITE
# =========================
def mario_spr(right=True):
    """
    GBA-Style Small Mario Sprite
    Recreated with 16-bit aesthetic shading
    """
    # 16x16 pixel art data 
    # . = Transparent
    # R = Red (Bright)
    # D = Dark Red
    # B = Blue
    # L = Dark Blue
    # S = Skin
    # T = Tan/Dark Skin
    # H = Brown (Hair/Shoes)
    # Y = Yellow Button
    # W = White Glove
    # G = Gray Glove Shadow
    
    pixels = [
        ".....DDDDD......",  # Hat Top (Shadow)
        "....DDRRRRD.....",  # Hat
        "....RRRRRRR.....",  # Hat
        "....HHHSSSH.....",  # Hair line
        "...HSHSSSHSH....",  # Face / Sideburn
        "...HSHSSSHSH....",  # Face
        "...HHSSSSHHH....",  # Face / Mustache
        ".....TTTT.......",  # Chin shadow
        "....RRRBRRR.....",  # Shirt/Chest
        "...RRRBLBRRR....",  # Shirt/Overalls strap
        "..WWRBBBBBRWW...",  # Arms/Overalls
        ".WWWRBBBBBRWWW..",  # Gloves
        ".WGWRBBBBBRWGW..",  # Gloves/Shadow
        "....LL...LL.....",  # Legs (Dark Blue)
        "...HHH...HHH....",  # Shoes
        "..HHHH...HHHH...",  # Shoes Bottom
    ]
    
    colors = {
        '.': None,
        'R': GBA_RED,
        'D': GBA_DRK,
        'B': GBA_BLU,
        'L': GBA_BLD,
        'S': GBA_SKN,
        'T': GBA_SKD,
        'H': GBA_BRN,
        'Y': GBA_YLW,
        'W': WHT,
        'G': GBA_GRY
    }
    
    # Create at 16x16
    nes_surf = pygame.Surface((16, 16), pygame.SRCALPHA)
    
    for y, row in enumerate(pixels):
        for x, c in enumerate(row):
            if c in colors and colors[c]:
                pygame.draw.rect(nes_surf, colors[c], (x, y, 1, 1))
    
    # Scale up to TILE size (24x24)
    s = pygame.transform.scale(nes_surf, (TILE, TILE))
    
    if not right:
        s = pygame.transform.flip(s, True, False)
    return s

def pipe_spr(h):
    """NES-accurate pipe sprite (unchanged)"""
    pw = TILE * 2
    ph = TILE * h
    s = pygame.Surface((pw, ph), pygame.SRCALPHA)
    lip_h = 8
    pygame.draw.rect(s, DGN, (0, 0, pw, lip_h))
    pygame.draw.rect(s, GRN, (2, 2, pw - 4, lip_h - 4))
    pygame.draw.rect(s, LGN, (4, 2, 4, lip_h - 4))
    body_x = 4
    body_w = pw - 8
    body_start = lip_h
    pygame.draw.rect(s, DGN, (body_x, body_start, body_w, ph - body_start))
    pygame.draw.rect(s, GRN, (body_x + 2, body_start, body_w - 4, ph - body_start))
    pygame.draw.rect(s, LGN, (body_x + 4, body_start, 4, ph - body_start))
    return s

def goomba_spr():
    """NES accurate Goomba"""
    pixels = [
        "......BBBB......",
        "....BBBBBBBB....",
        "...BBBBBBBBBB...",
        "..BBBWKBBWKBBB..",
        "..BBWWKBBWWKBB..",
        ".BBBBBBBBBBBBBB.",
        ".BBBBBBBBBBBBBB.",
        "..BBBBBBBBBBBB..",
        "....SSSSSSSS....",
        "...SSSSSSSSSS...",
        "..SSSSSSSSSSSS..",
        "..SSSS....SSSS..",
        ".BBBB......BBBB.",
        "BBBBB......BBBBB",
        "................",
        "................",
    ]
    colors = {'.': None, 'B': GMB, 'S': SKN, 'W': WHT, 'K': BLK}
    s = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
    scale = TILE / 16
    for y, row in enumerate(pixels):
        for x, c in enumerate(row):
            if c in colors and colors[c]:
                pygame.draw.rect(s, colors[c], (int(x*scale), int(y*scale), max(1,int(scale)), max(1,int(scale))))
    return s

def koopa_spr(right=True):
    """NES accurate Koopa"""
    pixels = [
        "......GGGG......",
        ".....GGGGGG.....",
        ".....GWWKG......",
        "....GWWWKG......",
        "....GGGGGG......",
        "...GGGGGGG......",
        "..GGGGGGGG......",
        "..GGGGGGGG......",
        ".GGGGGGGGGG.....",
        ".GGGGGGGGGG.....",
        "GGGGGGGGGGGG....",
        "GGGGGGGGGGGG....",
        ".GGGGGGGGGG.....",
        "..GGGGGGGG......",
        "...SSSSSS.......",
        "..SSSS.SSSS.....",
    ]
    colors = {'.': None, 'G': GRN, 'S': SKN, 'W': WHT, 'K': BLK}
    s = pygame.Surface((TILE, int(TILE * 1.2)), pygame.SRCALPHA)
    scale = TILE / 16
    for y, row in enumerate(pixels):
        for x, c in enumerate(row):
            if c in colors and colors[c]:
                pygame.draw.rect(s, colors[c], (int(x*scale), int(y*scale), max(1,int(scale)), max(1,int(scale))))
    if not right:
        s = pygame.transform.flip(s, True, False)
    return s

def ground_spr():
    s = pygame.Surface((TILE, TILE)); s.fill(BRK)
    for y in range(0, TILE, 6):
        for x in range(0, TILE, 6):
            if (x+y) % 12 == 0: pygame.draw.rect(s, BK2, (x, y, 3, 3))
    return s

def brick_spr():
    s = pygame.Surface((TILE, TILE)); s.fill(BRK)
    pygame.draw.line(s, BK2, (0, 0), (TILE, 0), 1)
    pygame.draw.line(s, BK2, (0, TILE//2), (TILE, TILE//2), 1)
    pygame.draw.line(s, BK2, (0, 0), (0, TILE//2), 1)
    pygame.draw.line(s, BK2, (TILE//2, 0), (TILE//2, TILE//2), 1)
    pygame.draw.line(s, BK2, (TILE//4, TILE//2), (TILE//4, TILE), 1)
    pygame.draw.line(s, BK2, (TILE*3//4, TILE//2), (TILE*3//4, TILE), 1)
    return s

def question_spr():
    s = pygame.Surface((TILE, TILE)); s.fill(GLD)
    pygame.draw.rect(s, GD2, (0, 0, TILE, TILE), 2)
    pygame.draw.rect(s, WHT, (7, 4, 10, 2))
    pygame.draw.rect(s, WHT, (13, 5, 3, 4))
    pygame.draw.rect(s, WHT, (8, 8, 6, 2))
    pygame.draw.rect(s, WHT, (9, 14, 4, 3))
    return s

def castle_spr():
    s = pygame.Surface((TILE, TILE)); s.fill(CST)
    pygame.draw.rect(s, CS2, (0, 0, TILE, TILE), 1)
    pygame.draw.line(s, CS2, (TILE//2, 0), (TILE//2, TILE), 1)
    pygame.draw.line(s, CS2, (0, TILE//2), (TILE, TILE//2), 1)
    return s

def flag_spr():
    s = pygame.Surface((TILE, TILE*10), pygame.SRCALPHA)
    pygame.draw.rect(s, DGN, (TILE//2-1, 0, 2, TILE*10))
    pygame.draw.circle(s, GRN, (TILE//2, 5), 4)
    pygame.draw.polygon(s, GRN, [(TILE//2, 7), (TILE//2-10, 13), (TILE//2, 19)])
    return s

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
# BIT-ACCURATE LEVELS WITH FIXED PITS
# =========================
LEVEL_1_1 = {
    'theme': 'sky', 'time': 400, 'w': 210, 'gnd': 2, 'spawn': (2, 11),
    'obj': [
        ('?', 16, 8),
        ('B', 20, 8), ('?', 21, 8), ('B', 22, 8), ('?', 23, 8), ('B', 24, 8),
        ('?', 22, 4),
        ('P', 28, 11, 2), ('P', 38, 10, 3), ('P', 46, 9, 4), ('P', 57, 9, 4),
        ('B', 64, 8), ('B', 65, 8), ('?', 66, 8), ('B', 67, 8),
        ('B', 77, 4), ('B', 78, 4), ('B', 79, 4),
        ('B', 80, 8), ('?', 81, 8), ('B', 82, 8),
        ('B', 91, 4), ('B', 92, 4), ('B', 93, 4), ('B', 94, 4), ('B', 94, 8),
        ('B', 100, 4), ('?', 101, 4), ('?', 102, 4), ('B', 103, 4),
        ('B', 106, 8), ('B', 109, 8), ('B', 110, 8), ('?', 111, 8), ('B', 112, 8),
        ('B', 118, 4), ('B', 119, 4), ('B', 120, 4),
        ('?', 129, 8), ('H', 129, 4),
        ('S', 134, 12, 1), ('S', 135, 11, 2), ('S', 136, 10, 3), ('S', 137, 9, 4),
        ('S', 140, 12, 1), ('S', 141, 11, 2), ('S', 142, 10, 3), ('S', 143, 9, 4),
        ('S', 144, 8, 5), ('S', 145, 7, 6), ('S', 146, 6, 7), ('S', 147, 5, 8),
        ('F', 153, 2), ('C', 160, 8, 5, 5),
    ],
    'enemies': [
        ('goomba', 22, 11), ('goomba', 40, 11), ('goomba', 51, 11), ('goomba', 52, 11),
        ('goomba', 80, 3), ('goomba', 82, 3), ('goomba', 97, 11), ('goomba', 98, 11),
        ('koopa', 107, 10), ('goomba', 113, 11), ('goomba', 114, 11),
        ('goomba', 123, 11), ('goomba', 124, 11),
    ],
    'pits': [(69, 71), (86, 89)],
}

LEVEL_1_2 = {
    'theme': 'blk', 'time': 400, 'w': 256, 'gnd': 2, 'spawn': (2, 11), 'ceil': True,
    'obj': [
        ('B', 10, 9), ('B', 11, 9), ('B', 12, 9), ('B', 13, 9),
        ('?', 15, 5),
        ('B', 21, 5), ('B', 22, 5), ('B', 23, 5), ('B', 24, 5),
        ('?', 22, 9), ('?', 23, 9),
        ('P', 29, 11, 2),
        ('B', 34, 5), ('B', 35, 5), ('B', 36, 5), ('B', 37, 5),
        ('B', 50, 9), ('?', 51, 9), ('B', 52, 9),
        ('P', 59, 10, 3),
        ('B', 66, 5), ('B', 67, 5), ('?', 68, 5), ('?', 69, 5), ('B', 70, 5),
        ('P', 77, 11, 2), ('P', 87, 11, 2),
        ('B', 93, 5), ('B', 94, 5), ('B', 95, 5), ('B', 96, 5),
        ('?', 94, 9), ('B', 95, 9), ('B', 96, 9), ('?', 97, 9),
        ('P', 103, 11, 2), ('P', 110, 10, 3), ('P', 117, 9, 4),
        ('S', 134, 12, 1), ('S', 135, 11, 2), ('S', 136, 10, 3), ('S', 137, 9, 4),
        ('S', 138, 8, 5), ('S', 139, 7, 6), ('S', 140, 6, 7), ('S', 141, 5, 8),
        ('P', 163, 5, 8), ('P', 175, 5, 8), ('P', 187, 5, 8),
        ('P', 230, 5, 8),
    ],
    'enemies': [
        ('goomba', 18, 11), ('goomba', 20, 11), ('goomba', 44, 11), ('goomba', 46, 11),
        ('koopa', 56, 10), ('goomba', 63, 11), ('goomba', 65, 11),
        ('goomba', 82, 11), ('goomba', 84, 11), ('goomba', 107, 11), ('goomba', 109, 11),
    ],
    'pits': [],
}

LEVEL_1_3 = {
    'theme': 'sky', 'time': 300, 'w': 176, 'gnd': 0, 'spawn': (1, 10),
    'obj': [
        ('-', 0, 11, 8), ('-', 12, 9, 4), ('?', 15, 5), ('-', 18, 11, 3),
        ('-', 23, 7, 4), ('-', 29, 11, 3), ('-', 34, 5, 4), ('-', 40, 9, 4),
        ('-', 46, 11, 3), ('-', 51, 7, 3), ('-', 56, 11, 4), ('-', 62, 5, 3),
        ('?', 64, 5), ('-', 67, 9, 4), ('-', 73, 11, 3), ('-', 78, 6, 4),
        ('-', 84, 10, 4), ('-', 90, 5, 3), ('-', 95, 9, 4), ('-', 101, 11, 3),
        ('-', 106, 7, 4), ('-', 112, 11, 6),
        ('S', 122, 12, 1), ('S', 123, 11, 2), ('S', 124, 10, 3), ('S', 125, 9, 4),
        ('S', 126, 8, 5), ('S', 127, 7, 6),
        ('F', 131, 2), ('C', 138, 8, 5, 5),
    ],
    'enemies': [
        ('koopa', 14, 8), ('koopa', 25, 6), ('koopa', 41, 8), ('koopa', 53, 6),
        ('koopa', 69, 8), ('koopa', 80, 5), ('koopa', 97, 8), ('koopa', 108, 6),
    ],
    'pits': [],
    'noground': True,
}

LEVEL_1_4 = {
    'theme': 'blk', 'time': 300, 'w': 192, 'gnd': 2, 'spawn': (1, 11), 'ceil': True,
    'obj': [
        ('C', 16, 7, 2, 6), ('C', 24, 4, 2, 3),
        ('L', 32, 12, 4, 1), ('-', 32, 9, 4),
        ('C', 40, 7, 2, 6),
        ('L', 48, 12, 4, 1), ('-', 48, 9, 4),
        ('C', 56, 4, 2, 9),
        ('L', 64, 12, 3, 1), ('-', 64, 8, 3),
        ('C', 72, 6, 2, 7),
        ('L', 80, 12, 4, 1), ('-', 80, 9, 4),
        ('C', 88, 4, 2, 9),
        ('-', 112, 9, 24), ('L', 112, 12, 24, 1),
        ('G', 136, 8), ('C', 144, 6, 6, 7),
    ],
    'enemies': [('bowser', 130, 8)],
    'pits': [(32, 36), (48, 52), (64, 67), (80, 84)],
}

LEVEL_2_1 = {
    'theme': 'sky', 'time': 400, 'w': 224, 'gnd': 2, 'spawn': (2, 11),
    'obj': [
        ('?', 12, 8), ('?', 13, 8),
        ('B', 18, 4), ('B', 19, 4), ('B', 20, 4), ('B', 21, 4),
        ('?', 23, 8),
        ('P', 29, 11, 2), ('P', 39, 10, 3),
        ('S', 48, 12, 1), ('S', 49, 11, 2), ('S', 50, 10, 3), ('S', 51, 9, 4),
        ('S', 55, 9, 4), ('S', 56, 10, 3), ('S', 57, 11, 2), ('S', 58, 12, 1),
        ('?', 60, 8),
        ('B', 64, 8), ('?', 65, 8), ('?', 66, 8), ('B', 67, 8),
        ('?', 65, 4), ('?', 66, 4),
        ('P', 73, 9, 4),
        ('B', 84, 8), ('B', 85, 8),
        ('B', 94, 4), ('B', 95, 4), ('B', 96, 4),
        ('?', 98, 8), ('B', 99, 8), ('B', 100, 8), ('?', 101, 8),
        ('B', 107, 8), ('B', 108, 8),
        ('P', 115, 11, 2),
        ('S', 130, 12, 1), ('S', 131, 11, 2), ('S', 132, 10, 3), ('S', 133, 9, 4),
        ('S', 134, 8, 5), ('S', 135, 7, 6), ('S', 136, 6, 7), ('S', 137, 5, 8),
        ('F', 142, 2), ('C', 150, 8, 5, 5),
    ],
    'enemies': [
        ('koopa', 15, 10), ('goomba', 25, 11), ('goomba', 26, 11),
        ('goomba', 43, 11), ('koopa', 52, 8),
        ('goomba', 70, 11), ('goomba', 71, 11),
        ('koopa', 80, 10), ('goomba', 88, 11), ('goomba', 89, 11),
        ('goomba', 104, 11), ('goomba', 110, 11), ('goomba', 122, 11),
    ],
    'pits': [(52, 55), (78, 81)],
}

LEVEL_2_2 = {
    'theme': 'water', 'time': 400, 'w': 192, 'gnd': 2, 'spawn': (2, 6), 'water': True,
    'obj': [
        ('X', 10, 11, 2, 2), ('X', 16, 10, 1, 3), ('X', 22, 11, 3, 2),
        ('X', 32, 9, 2, 4), ('X', 40, 11, 2, 2), ('X', 48, 10, 1, 3),
        ('X', 58, 11, 3, 2), ('X', 68, 9, 2, 4), ('X', 78, 11, 2, 2),
        ('X', 88, 10, 1, 3), ('X', 98, 11, 3, 2), ('X', 108, 9, 2, 4),
        ('X', 120, 11, 2, 2), ('X', 130, 10, 1, 3), ('X', 142, 11, 3, 2),
        ('P', 168, 4, 9),
    ],
    'enemies': [
        ('blooper', 25, 5), ('blooper', 55, 6), ('blooper', 85, 5),
        ('blooper', 115, 6), ('blooper', 145, 5),
    ],
    'pits': [],
}

LEVEL_2_3 = {
    'theme': 'sky', 'time': 300, 'w': 176, 'gnd': 0, 'spawn': (1, 10),
    'obj': [
        ('-', 0, 11, 7), ('-', 10, 8, 4), ('-', 17, 11, 3), ('-', 23, 6, 4),
        ('-', 30, 10, 3), ('-', 36, 5, 3), ('-', 42, 9, 4), ('-', 49, 11, 3),
        ('-', 55, 7, 4), ('-', 62, 11, 3), ('-', 68, 5, 3), ('-', 74, 9, 4),
        ('-', 81, 11, 3), ('-', 87, 6, 4), ('-', 94, 10, 4), ('-', 101, 5, 3),
        ('-', 107, 8, 4), ('-', 114, 11, 8),
        ('S', 126, 12, 1), ('S', 127, 11, 2), ('S', 128, 10, 3),
        ('F', 132, 2), ('C', 140, 8, 5, 5),
    ],
    'enemies': [
        ('koopa', 12, 7), ('koopa', 25, 5), ('koopa', 44, 8),
        ('koopa', 57, 6), ('koopa', 76, 8), ('koopa', 95, 9),
    ],
    'pits': [],
    'noground': True,
}

LEVEL_2_4 = {
    'theme': 'blk', 'time': 300, 'w': 208, 'gnd': 2, 'spawn': (1, 11), 'ceil': True,
    'obj': [
        ('C', 14, 7, 2, 6), ('C', 24, 4, 2, 3),
        ('L', 32, 12, 5, 1), ('-', 32, 8, 5),
        ('C', 42, 6, 2, 7),
        ('L', 52, 12, 4, 1), ('-', 52, 9, 4),
        ('C', 62, 4, 2, 9),
        ('L', 72, 12, 5, 1), ('-', 72, 8, 5),
        ('C', 84, 6, 2, 7),
        ('L', 96, 12, 4, 1), ('-', 96, 9, 4),
        ('-', 120, 9, 28), ('L', 120, 12, 28, 1),
        ('G', 148, 8), ('C', 156, 6, 6, 7),
    ],
    'enemies': [('bowser', 142, 8)],
    'pits': [(32, 37), (52, 56), (72, 77), (96, 100)],
}

# Generate remaining levels
def gen(base, w):
    lvl = dict(base)
    lvl['time'] = max(200, base['time'] - (w-1) * 20)
    return lvl

LEVELS = {
    '1-1': LEVEL_1_1, '1-2': LEVEL_1_2, '1-3': LEVEL_1_3, '1-4': LEVEL_1_4,
    '2-1': LEVEL_2_1, '2-2': LEVEL_2_2, '2-3': LEVEL_2_3, '2-4': LEVEL_2_4,
}

bases = [LEVEL_1_1, LEVEL_1_2, LEVEL_1_3, LEVEL_1_4, LEVEL_2_1, LEVEL_2_2, LEVEL_2_3, LEVEL_2_4]
for w in range(3, 9):
    for s in range(1, 5):
        k = f'{w}-{s}'
        LEVELS[k] = gen(bases[(w + s - 2) % len(bases)], w)

LEVELS['8-4'] = {
    'theme': 'blk', 'time': 400, 'w': 400, 'gnd': 2, 'spawn': (1, 11), 'ceil': True,
    'obj': [
        ('C', 12, 7, 2, 6), ('C', 24, 4, 2, 3),
        ('L', 32, 12, 4, 1), ('-', 32, 8, 4),
        ('C', 42, 6, 2, 7), ('C', 56, 4, 2, 9),
        ('L', 66, 12, 5, 1), ('-', 66, 8, 5),
        ('W', 85, 9, 20, 4),
        ('C', 90, 6, 2, 3), ('C', 100, 6, 2, 3),
        ('P', 130, 9, 4), ('P', 145, 9, 4), ('P', 160, 9, 4),
        ('C', 180, 6, 2, 7), ('C', 195, 4, 2, 9), ('C', 210, 6, 2, 7),
        ('L', 220, 12, 5, 1), ('-', 220, 8, 5),
        ('C', 240, 6, 2, 7), ('C', 255, 4, 2, 9), ('C', 270, 6, 2, 7),
        ('-', 300, 9, 40), ('L', 300, 12, 40, 1),
        ('G', 340, 8), ('C', 350, 5, 8, 8),
    ],
    'enemies': [('bowser', 335, 8)],
    'pits': [(32, 36), (66, 71), (220, 225)],
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
        self.solid = kind not in ['F', 'G', 'L', 'H', 'W']
        self.hit = False
        
        sp = {'X': 'ground', 'B': 'brick', '?': 'question', 'S': 'ground', 'C': 'castle'}.get(kind)
        if sp:
            base = get(sp)
            if base: self.image = pygame.transform.scale(base, (self.rect.w, self.rect.h))
        elif kind == 'F': self.image = get('flag')
        elif kind == '-': self.image.fill(BRK)
        elif kind == 'L': self.image.fill(LVA)
        elif kind == 'G': self.image.fill(WHT); self.solid = False
        elif kind == 'H': self.image.fill((0,0,0,0))
        elif kind == 'W': self.image.fill((60, 120, 248, 128))

    def bump(self, p):
        if self.kind == '?' and not self.hit:
            self.hit = True; p.coins += 1; p.score += 200
            self.image.fill(BK2)
        elif self.kind == 'H' and not self.hit:
            self.hit = True; self.kind = '?'; p.score += 1000
            base = get('question')
            self.image = pygame.transform.scale(base, (self.rect.w, self.rect.h))

class Pipe(Entity):
    def __init__(self, x, y, h):
        # Consistent width: 2 tiles (48px) - NES accurate
        pw = TILE * 2
        super().__init__(x, y, pw, TILE * h)
        self.image = pipe_spr(h)
        self.solid = True
        self.kind = 'P'

class Enemy(Entity):
    def __init__(self, x, y, kind):
        h = int(TILE * 1.2) if kind == 'koopa' else TILE
        super().__init__(x, y, TILE, h)
        self.kind = kind
        self.dir = -1
        self.speed = 0.4
        self.alive = True
        self.dt = 0
        if kind in ['goomba', 'koopa']:
            self.image = get('koopa' if kind == 'koopa' else 'goomba')
        else:
            self.image.fill(RED)

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

class Camera:
    def __init__(self, lw): self.x = 0; self.lw = lw
    def apply(self, r): return r.move(-self.x, 0)
    def update(self, t):
        self.x = max(self.x, t.rect.centerx - SW // 3)
        self.x = max(0, min(self.x, self.lw - SW))

# =========================
# LEVEL LOADER
# =========================
def load(lid):
    d = LEVELS.get(lid, LEVELS['1-1'])
    blocks, enemies = pygame.sprite.Group(), pygame.sprite.Group()
    w = d['w']
    gh = d.get('gnd', 2)
    pits = d.get('pits', [])
    noground = d.get('noground', False)
    
    # Generate ground - skip pit areas
    if not noground and gh > 0:
        for x in range(w):
            # Check if this X is in a pit
            in_pit = False
            for pit_start, pit_end in pits:
                if pit_start <= x < pit_end:
                    in_pit = True
                    break
            
            # Only add ground if NOT in a pit
            if not in_pit:
                for gy in range(13 - gh, 13):
                    blocks.add(Block(x * TILE, gy * TILE, 'X'))
    
    # Ceiling
    if d.get('ceil'):
        for x in range(w):
            blocks.add(Block(x * TILE, 0, 'X'))
    
    # Objects
    for o in d.get('obj', []):
        k, ox, oy = o[0], o[1], o[2]
        if k == 'P':
            h = o[3] if len(o) > 3 else 2
            blocks.add(Pipe(ox * TILE, oy * TILE, h))
        elif k == 'F':
            blocks.add(Block(ox * TILE, oy * TILE, 'F', TILE, TILE * 10))
        elif k == 'G':
            blocks.add(Block(ox * TILE, oy * TILE, 'G'))
        elif k in ['L', 'W']:
            lw = o[3] if len(o) > 3 else 1
            lh = o[4] if len(o) > 4 else 1
            for dx in range(lw):
                for dy in range(lh):
                    blocks.add(Block((ox+dx)*TILE, (oy+dy)*TILE, k))
        elif k in ['X', 'B', '?', 'S', 'C', '-', 'H']:
            bw = o[3] if len(o) > 3 and isinstance(o[3], int) else 1
            bh = o[4] if len(o) > 4 else 1
            for dx in range(bw):
                for dy in range(bh):
                    blocks.add(Block((ox+dx)*TILE, (oy+dy)*TILE, k))
    
    # Enemies
    for e in d.get('enemies', []):
        if e[0] in ['goomba', 'koopa', 'bowser', 'blooper']:
            enemies.add(Enemy(e[1]*TILE, e[2]*TILE, e[0]))
    
    sp = d.get('spawn', (2, 11))
    return blocks, enemies, d.get('theme', 'sky'), d.get('time', 400), (sp[0]*TILE, sp[1]*TILE), w*TILE

# =========================
# GAME
# =========================
class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Cat's SMB v8 - GBA Edition")
        self.scr = pygame.display.set_mode((SW, SH))
        self.clk = pygame.time.Clock()
        self.fnt = pygame.font.Font(None, 24)
        self.w = self.s = 1
        self.paused = False
        self.load()
        print("=" * 45)
        print(" CAT'S SUPER MARIO BROS v8 - GBA EDITION")
        print(" FIXED: Pits + GBA-style Mario sprite")
        print("=" * 45)

    def load(self):
        self.blocks, self.enemies, self.theme, self.time, sp, lw = load(f'{self.w}-{self.s}')
        self.player = Player(sp[0], sp[1])
        self.tleft = float(self.time)
        self.cam = Camera(lw)

    def nxt(self):
        self.s += 1
        if self.s > 4: self.s = 1; self.w += 1
        if self.w > 8: self.w = self.s = 1; print("CONGRATULATIONS!")
        self.load()

    def die(self):
        self.player.lives -= 1
        if self.player.lives <= 0:
            self.w = self.s = 1; self.player.lives = 3
            self.player.score = self.player.coins = 0
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
                self.scr.blit(self.fnt.render("PAUSED", True, WHT), (SW//2-25, SH//2))
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
            
            bg = {'sky': SKY, 'blk': BLK, 'water': (0, 88, 180)}.get(self.theme, SKY)
            self.scr.fill(bg)
            
            for b in self.blocks:
                sr = self.cam.apply(b.rect)
                if -TILE*2 < sr.x < SW + TILE*2: self.scr.blit(b.image, sr)
            for en in self.enemies:
                if en.alive or en.dt > 0: self.scr.blit(en.image, self.cam.apply(en.rect))
            self.scr.blit(self.player.image, self.cam.apply(self.player.rect))
            
            pygame.draw.rect(self.scr, BLK, (0, 0, SW, 28))
            self.scr.blit(self.fnt.render(f"MARIO {self.player.score:06d}  x{self.player.coins:02d}  WORLD {self.w}-{self.s}  TIME {int(max(0,self.tleft)):03d}  x{self.player.lives}", True, WHT), (10, 6))
            
            pygame.display.flip()
        
        pygame.quit(); sys.exit()

if __name__ == '__main__':
    Game().run()
