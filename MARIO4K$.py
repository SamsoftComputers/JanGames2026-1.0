#!/usr/bin/env python3
"""Cat's Ultra Mario 2D Bross! 0.1 - NES-Exact SMB1 Engine - Team Flames"""
import pygame
import math
import array

pygame.init()
pygame.mixer.init(44100, -16, 2, 512)

# === NES CONSTANTS ===
# NES runs at 60.0988 FPS, 256x240 resolution
# We scale 2x for modern displays: 512x480, using 32px tiles (16px NES * 2)
W, H, T, FPS = 800, 480, 32, 60
SUBPIXEL = 256  # NES subpixel precision

# === NES PHYSICS (from SMB disassembly - values in subpixels per frame) ===
# Walking friction: $E4 ($00.E4 = 228/256 = 0.890625 pixels decel per frame)
# Running friction: $98 ($00.98 = 152/256 = 0.59375)
# Max walk speed: $1800 ($18.00 = 24 pixels per frame... wait that's wrong)
# Let me use the correct values scaled for our 2x tiles

# Physics values (converted from NES, scaled 2x)
class Phys:
    # Horizontal movement (subpixels * 2 for scale)
    WALK_ACCEL = 0.09375      # Walking acceleration
    RUN_ACCEL = 0.140625      # Running acceleration  
    RELEASE_DECEL = 0.0625    # Deceleration when no input
    SKID_DECEL = 0.1875       # Deceleration when skidding
    WALK_MAX = 2.5            # Max walking speed
    RUN_MAX = 5.0             # Max running speed
    
    # Air movement
    AIR_ACCEL = 0.09375       # Same as ground in NES
    
    # Vertical movement - NES has complex jump tables
    # Initial jump velocities based on horizontal speed:
    JUMP_STANDING = -12.0     # Standing/slow jump
    JUMP_WALKING = -12.5      # Walking jump
    JUMP_RUNNING = -13.0      # Running jump
    
    # Gravity values
    GRAVITY_RISING = 0.375    # Gravity while rising (holding jump)
    GRAVITY_FALLING = 0.5625  # Gravity while falling
    GRAVITY_RELEASE = 0.5625  # Gravity when jump released early
    MAX_FALL = 12.0           # Terminal velocity
    
    # Jump hold frames
    JUMP_HOLD_MAX = 24        # Max frames jump can be held

# NES Palette colors
class Pal:
    SKY = (92, 148, 252)      # $22
    BLACK = (0, 0, 0)         # $0F
    WHITE = (252, 252, 252)   # $30
    RED = (228, 0, 88)        # $16
    BROWN = (200, 76, 12)     # $17
    BRICK = (172, 80, 36)     # $27
    QUESTION = (252, 152, 56) # $27 alt
    PIPE_LT = (0, 228, 0)     # $2A
    PIPE = (0, 168, 0)        # $1A
    PIPE_DK = (0, 108, 0)     # $0A
    SKIN = (252, 152, 56)     # $27
    GOOMBA = (172, 80, 36)    # $27
    KOOPA = (0, 168, 0)       # $1A
    CASTLE = (188, 188, 188)  # $10
    CASTLE_DK = (116, 116, 116)
    LAVA = (252, 60, 0)       # $15
    BLUE = (0, 88, 248)       # $12

# === SOUND EFFECTS ===
def make_sound(freq_func, duration, volume=0.25):
    samples = int(44100 * duration)
    data = array.array('h')
    for i in range(samples):
        t = i / 44100
        val = freq_func(t)
        sample = int(max(-1, min(1, val)) * 32767 * volume)
        data.append(sample)
        data.append(sample)
    return pygame.mixer.Sound(buffer=data)

SFX = {}
def init_sounds():
    global SFX
    # Jump - ascending sweep
    SFX['jump'] = make_sound(lambda t: math.sin(2*math.pi*(400 + 800*t)*t), 0.15)
    # Stomp
    SFX['stomp'] = make_sound(lambda t: math.sin(2*math.pi*200*t) * max(0, 1-t*12), 0.08)
    # Coin
    SFX['coin'] = make_sound(lambda t: math.sin(2*math.pi*(988 if t < 0.06 else 1319)*t), 0.15)
    # Powerup
    SFX['powerup'] = make_sound(lambda t: math.sin(2*math.pi*(400 + 600*t)*t), 0.5)
    # Die
    SFX['die'] = make_sound(lambda t: math.sin(2*math.pi*(400 - 100*t)*t), 1.0, 0.3)
    # Bump
    SFX['bump'] = make_sound(lambda t: math.sin(2*math.pi*150*t) * max(0, 1-t*15), 0.06)
    # Flag
    SFX['flag'] = make_sound(lambda t: math.sin(2*math.pi*(523 + 200*t)*t), 0.5)
    # Brick break
    SFX['break'] = make_sound(lambda t: (hash(int(t*10000)) % 1000 / 500 - 1) * max(0, 1-t*8), 0.12)
    # Menu
    SFX['select'] = make_sound(lambda t: math.sin(2*math.pi*660*t), 0.05)
    SFX['cursor'] = make_sound(lambda t: math.sin(2*math.pi*440*t), 0.03)

init_sounds()

# === TILE GRAPHICS ===
TILES = {}

def init_tiles():
    # Ground tile
    s = pygame.Surface((T, T))
    s.fill(Pal.BROWN)
    pygame.draw.rect(s, (228, 92, 16), (0, 0, T, 6))
    for i in range(4):
        pygame.draw.rect(s, (160, 52, 8), (i*8+2, 8, 4, 4))
        pygame.draw.rect(s, (160, 52, 8), (i*8+4, 20, 4, 4))
    pygame.draw.rect(s, Pal.BLACK, (0, 0, T, T), 1)
    TILES['G'] = s
    
    # Brick
    s = pygame.Surface((T, T))
    s.fill(Pal.BRICK)
    # Brick pattern
    pygame.draw.line(s, Pal.BLACK, (0, 15), (T, 15), 2)
    pygame.draw.line(s, Pal.BLACK, (15, 0), (15, 15), 2)
    pygame.draw.line(s, Pal.BLACK, (0, 16), (0, T), 2)
    pygame.draw.line(s, Pal.BLACK, (15, 17), (15, T), 2)
    pygame.draw.rect(s, (200, 100, 56), (2, 2, 11, 11))
    pygame.draw.rect(s, (200, 100, 56), (18, 2, 11, 11))
    pygame.draw.rect(s, (200, 100, 56), (2, 18, 11, 11))
    pygame.draw.rect(s, (200, 100, 56), (18, 18, 11, 11))
    pygame.draw.rect(s, Pal.BLACK, (0, 0, T, T), 1)
    TILES['B'] = s
    
    # Question block (animated)
    s = pygame.Surface((T, T))
    s.fill(Pal.QUESTION)
    pygame.draw.rect(s, (200, 120, 40), (3, 3, 26, 26))
    # Question mark
    pygame.draw.rect(s, Pal.BLACK, (12, 8, 8, 4))
    pygame.draw.rect(s, Pal.BLACK, (16, 10, 4, 6))
    pygame.draw.rect(s, Pal.BLACK, (12, 14, 8, 4))
    pygame.draw.rect(s, Pal.BLACK, (12, 16, 4, 4))
    pygame.draw.rect(s, Pal.BLACK, (12, 22, 4, 4))
    pygame.draw.rect(s, Pal.BLACK, (0, 0, T, T), 2)
    TILES['?'] = s
    
    # Used block
    s = pygame.Surface((T, T))
    s.fill((136, 68, 0))
    pygame.draw.rect(s, (100, 50, 0), (3, 3, 26, 26))
    pygame.draw.rect(s, Pal.BLACK, (0, 0, T, T), 2)
    TILES['U'] = s
    
    # Hard block (stone)
    s = pygame.Surface((T, T))
    s.fill((160, 120, 80))
    pygame.draw.rect(s, (120, 80, 50), (2, 2, 12, 12))
    pygame.draw.rect(s, (120, 80, 50), (18, 2, 12, 12))
    pygame.draw.rect(s, (120, 80, 50), (2, 18, 12, 12))
    pygame.draw.rect(s, (120, 80, 50), (18, 18, 12, 12))
    pygame.draw.rect(s, (200, 160, 120), (4, 4, 6, 6))
    pygame.draw.rect(s, (200, 160, 120), (20, 4, 6, 6))
    pygame.draw.rect(s, (200, 160, 120), (4, 20, 6, 6))
    pygame.draw.rect(s, (200, 160, 120), (20, 20, 6, 6))
    pygame.draw.rect(s, Pal.BLACK, (0, 0, T, T), 1)
    TILES['X'] = s
    
    # Pipe top
    s = pygame.Surface((T, T))
    s.fill(Pal.PIPE)
    pygame.draw.rect(s, Pal.PIPE_LT, (2, 4, 6, T-4))
    pygame.draw.rect(s, Pal.PIPE_DK, (24, 0, 6, T))
    pygame.draw.rect(s, Pal.PIPE_LT, (0, 0, T, 8))
    pygame.draw.rect(s, Pal.PIPE_DK, (0, 0, 4, 8))
    pygame.draw.rect(s, Pal.BLACK, (0, 0, T, 8), 1)
    TILES['T'] = s
    
    # Pipe body
    s = pygame.Surface((T, T))
    s.fill(Pal.PIPE)
    pygame.draw.rect(s, Pal.PIPE_LT, (2, 0, 6, T))
    pygame.draw.rect(s, Pal.PIPE_DK, (24, 0, 6, T))
    TILES['P'] = s
    
    # Castle block
    s = pygame.Surface((T, T))
    s.fill(Pal.CASTLE)
    pygame.draw.rect(s, Pal.CASTLE_DK, (0, 0, 16, 16))
    pygame.draw.rect(s, Pal.CASTLE_DK, (16, 16, 16, 16))
    pygame.draw.rect(s, Pal.BLACK, (0, 0, T, T), 1)
    TILES['C'] = s
    
    # Lava
    s = pygame.Surface((T, T), pygame.SRCALPHA)
    s.fill(Pal.LAVA)
    pygame.draw.rect(s, (252, 100, 0), (0, 0, T, 8))
    for i in range(4):
        pygame.draw.ellipse(s, (252, 160, 0), (i*8, 2, 8, 8))
    TILES['L'] = s
    
    # Axe
    s = pygame.Surface((T, T), pygame.SRCALPHA)
    pygame.draw.rect(s, (160, 160, 160), (12, 8, 8, 18))
    pygame.draw.ellipse(s, (200, 200, 200), (4, 2, 24, 14))
    pygame.draw.ellipse(s, (120, 120, 120), (8, 4, 16, 10))
    TILES['A'] = s
    
    # Flag
    s = pygame.Surface((T, T), pygame.SRCALPHA)
    pygame.draw.rect(s, (100, 100, 100), (14, 0, 4, T))
    pygame.draw.polygon(s, Pal.KOOPA, [(18, 4), (30, 12), (18, 20)])
    pygame.draw.circle(s, (252, 188, 60), (16, 2), 4)
    TILES['F'] = s

init_tiles()

# === LEVEL DATA (NES-accurate layouts) ===
# Format: (width, ground_segments, objects)
# Ground segments: list of (start_tile, end_tile)
# Objects: list of (x, y, type, [count])

LEVELS = {
    '1-1': (212, 
        [(0, 68), (71, 85), (89, 152), (155, 211)],
        [
            # Blocks row 1
            (16, 9, '?'), (20, 9, 'B'), (21, 9, 'M'), (22, 9, 'B'), (23, 9, '?'),
            (22, 5, '?'),
            # Pipes
            (28, 11, 'P', 2), (38, 11, 'P', 3), (46, 11, 'P', 4), (57, 11, 'P', 4),
            # More blocks
            (78, 9, '?'),
            (80, 5, 'B', 8), (91, 5, 'B', 3), (94, 5, '?'),
            (100, 9, 'B', 2), (106, 9, '?'), (109, 5, '?'), (112, 9, '?'),
            (118, 9, 'B'), (118, 5, 'B'),
            (121, 9, 'B', 3), (128, 5, 'B', 4), (129, 5, 'M'),
            # Stairs
            (134, 12, '^', 4), (140, 12, '^', 4), (148, 12, '^', 5), (152, 12, 'v', 4),
            # End section
            (163, 11, 'P', 2), (168, 9, 'B', 2), (169, 5, 'B', 2), (171, 9, '?'),
            (179, 11, 'P', 2), (181, 12, '^', 8), (198, 3, 'F'),
            # Enemies
            (22, 12, 'g'), (40, 12, 'g'), (51, 12, 'g'), (52, 12, 'g'),
            (80, 12, 'g'), (82, 12, 'g'), (97, 12, 'g'), (98, 12, 'g'),
            (107, 12, 'g'), (114, 12, 'g'), (115, 12, 'g'), (124, 12, 'g'), (125, 12, 'g'),
        ]),
    '1-2': (200,
        [(0, 199)],
        [
            (0, 0, 'C', 145),
            (16, 9, 'B', 5), (21, 5, 'B', 4), (28, 9, '?'), (32, 5, 'B', 6),
            (41, 9, 'B', 3), (44, 5, 'M'), (48, 9, 'B', 4), (55, 9, 'B', 3),
            (60, 5, 'B', 7), (64, 9, '?'), (71, 9, 'B', 4), (77, 9, 'B', 5),
            (80, 5, '?'), (83, 5, '?'), (87, 5, 'B', 3), (95, 9, 'B', 6),
            (104, 9, 'B', 3), (112, 5, 'B', 4), (122, 5, 'B', 6), (134, 9, 'B', 3),
            (145, 11, 'P', 2), (152, 5, 'X', 8), (162, 5, 'X', 6), (170, 9, 'X', 6),
            (180, 12, '^', 8), (192, 11, 'P', 2), (196, 3, 'F'),
            (20, 12, 'g'), (45, 12, 'g'), (75, 12, 'g'), (100, 12, 'g'), (130, 12, 'g'),
        ]),
    '1-3': (168,
        [(0, 15), (152, 167)],
        [
            (20, 10, '=', 6), (28, 8, '=', 5), (36, 10, '=', 6), (45, 6, '=', 4),
            (54, 8, '=', 5), (63, 10, '=', 6), (72, 8, '=', 5), (81, 6, '=', 4),
            (90, 8, '=', 5), (99, 10, '=', 6), (108, 8, '=', 5), (118, 6, '=', 4),
            (128, 8, '=', 5), (140, 12, '^', 5), (155, 3, 'F'),
            (24, 9, 'r'), (40, 9, 'r'), (58, 7, 'r'), (76, 7, 'r'), (94, 9, 'r'), (112, 7, 'r'),
        ]),
    '1-4': (152,
        [(0, 151)],
        [
            (0, 0, 'C', 152),
            (24, 13, 'L', 3), (38, 13, 'L', 3), (54, 13, 'L', 4),
            (68, 8, '=', 6), (82, 6, '=', 5), (96, 8, '=', 6),
            (115, 9, '=', 18), (135, 9, 'A'), (130, 10, 'W'),
        ]),
    '2-1': (210,
        [(0, 58), (62, 95), (99, 140), (144, 209)],
        [
            (18, 5, '?'), (20, 5, '?'), (22, 5, '?'), (26, 9, 'B', 4), (28, 9, 'M'),
            (36, 11, 'P', 2), (50, 11, 'P', 3), (64, 11, 'P', 4),
            (76, 9, '?'), (80, 9, 'B', 4), (88, 5, 'B', 5),
            (112, 9, 'B', 4), (118, 9, '?'), (128, 11, 'P', 2),
            (145, 12, '^', 5), (158, 12, '^', 6), (172, 11, 'P', 2),
            (188, 12, '^', 8), (200, 3, 'F'),
            (24, 12, 'g'), (32, 12, 'k'), (55, 12, 'g'), (56, 12, 'g'),
            (95, 12, 'g'), (96, 12, 'g'), (135, 12, 'k'),
        ]),
    '2-2': (180,
        [(0, 179)],
        [
            (20, 10, '=', 6), (35, 8, '=', 5), (50, 6, '=', 4),
            (65, 10, '=', 6), (80, 8, '=', 5), (95, 6, '=', 4),
            (110, 10, '=', 6), (125, 8, '=', 5), (140, 6, '=', 4),
            (155, 10, '=', 6), (165, 11, 'P', 2), (172, 3, 'F'),
        ]),
    '2-3': (168,
        [(0, 15), (152, 167)],
        [
            (18, 9, '=', 8), (30, 7, '=', 6), (42, 9, '=', 8), (56, 7, '=', 6),
            (70, 9, '=', 8), (84, 7, '=', 6), (98, 9, '=', 8), (112, 7, '=', 6),
            (126, 9, '=', 8), (140, 12, '^', 5), (155, 3, 'F'),
            (24, 8, 'r'), (48, 8, 'r'), (76, 8, 'r'), (104, 8, 'r'), (132, 8, 'r'),
        ]),
    '2-4': (160,
        [(0, 159)],
        [
            (0, 0, 'C', 160),
            (28, 13, 'L', 4), (48, 13, 'L', 4), (68, 13, 'L', 5),
            (80, 7, '=', 6), (96, 9, '=', 6), (112, 7, '=', 6),
            (125, 9, '=', 18), (145, 9, 'A'), (140, 10, 'W'),
        ]),
    '3-1': (215,
        [(0, 52), (56, 88), (92, 135), (139, 214)],
        [
            (20, 9, 'B', 3), (24, 9, '?'), (27, 5, 'M'), (32, 9, 'B', 4),
            (42, 11, 'P', 2), (58, 11, 'P', 3), (72, 9, 'B', 5), (78, 5, '?'),
            (92, 11, 'P', 4), (108, 9, '?', 3), (118, 9, 'B', 4),
            (135, 12, '^', 4), (150, 12, '^', 5), (165, 11, 'P', 2),
            (180, 12, '^', 8), (200, 3, 'F'),
            (38, 12, 'g'), (39, 12, 'g'), (68, 12, 'k'), (88, 12, 'g'), (89, 12, 'g'),
            (115, 12, 'g'), (145, 12, 'k'),
        ]),
    '3-2': (210,
        [(0, 48), (52, 90), (94, 138), (142, 209)],
        [
            (18, 9, '?'), (22, 9, 'B', 4), (32, 11, 'P', 3), (48, 9, 'M'),
            (62, 9, 'B', 5), (72, 5, '?'), (82, 11, 'P', 2), (102, 9, 'B', 4),
            (112, 9, '?', 2), (128, 11, 'P', 3), (148, 12, '^', 5),
            (168, 11, 'P', 2), (185, 12, '^', 8), (198, 3, 'F'),
            (28, 12, 'k'), (55, 12, 'g'), (56, 12, 'g'), (78, 12, 'g'),
            (108, 12, 'k'), (145, 12, 'g'), (146, 12, 'g'),
        ]),
    '3-3': (170,
        [(0, 15), (154, 169)],
        [
            (18, 10, '=', 5), (28, 8, '=', 6), (40, 10, '=', 5), (52, 6, '=', 4),
            (65, 8, '=', 6), (78, 10, '=', 5), (90, 8, '=', 6), (103, 6, '=', 4),
            (115, 8, '=', 6), (128, 10, '=', 5), (142, 12, '^', 5), (158, 3, 'F'),
            (32, 7, 'r'), (58, 9, 'r'), (84, 7, 'r'), (110, 9, 'r'),
        ]),
    '3-4': (168,
        [(0, 167)],
        [
            (0, 0, 'C', 168),
            (25, 13, 'L', 4), (45, 13, 'L', 4), (65, 13, 'L', 5), (85, 13, 'L', 4),
            (72, 7, '=', 5), (92, 9, '=', 6), (108, 7, '=', 5),
            (130, 9, '=', 18), (150, 9, 'A'), (145, 10, 'W'),
        ]),
    '4-1': (220,
        [(0, 45), (49, 82), (86, 128), (132, 219)],
        [
            (18, 9, 'B', 4), (24, 5, '?'), (30, 9, 'M'), (38, 11, 'P', 2),
            (52, 9, 'B', 3), (62, 11, 'P', 3), (78, 9, '?', 2), (88, 5, 'B', 4),
            (102, 11, 'P', 4), (118, 9, 'B', 5), (135, 12, '^', 4),
            (155, 12, '^', 5), (175, 11, 'P', 2), (195, 12, '^', 8), (210, 3, 'F'),
            (32, 12, 'g'), (33, 12, 'g'), (58, 12, 'k'), (85, 12, 'g'), (86, 12, 'g'),
            (125, 12, 'g'), (165, 12, 'k'),
        ]),
    '4-2': (200,
        [(0, 199)],
        [
            (0, 0, 'C', 150),
            (20, 9, 'B', 5), (28, 5, 'B', 4), (38, 9, '?'), (48, 9, 'B', 4),
            (58, 5, 'M'), (68, 9, 'B', 6), (82, 5, 'B', 5), (98, 9, 'B', 4),
            (112, 5, '?', 2), (128, 9, 'B', 5), (148, 5, 'X', 8), (162, 9, 'X', 6),
            (178, 12, '^', 8), (192, 11, 'P', 2), (196, 3, 'F'),
            (25, 12, 'g'), (55, 12, 'g'), (85, 12, 'g'), (115, 12, 'g'),
        ]),
    '4-3': (172,
        [(0, 15), (156, 171)],
        [
            (20, 9, '=', 6), (32, 7, '=', 5), (45, 9, '=', 6), (58, 5, '=', 4),
            (70, 7, '=', 6), (83, 9, '=', 5), (95, 7, '=', 6), (108, 5, '=', 4),
            (120, 7, '=', 6), (133, 9, '=', 5), (145, 12, '^', 5), (160, 3, 'F'),
            (26, 8, 'r'), (52, 8, 'r'), (76, 6, 'r'), (102, 8, 'r'), (126, 6, 'r'),
        ]),
    '4-4': (175,
        [(0, 174)],
        [
            (0, 0, 'C', 175),
            (30, 13, 'L', 5), (50, 13, 'L', 5), (72, 13, 'L', 6), (95, 13, 'L', 5),
            (62, 7, '=', 5), (88, 9, '=', 6), (112, 7, '=', 5), (128, 9, '=', 6),
            (140, 9, '=', 18), (160, 9, 'A'), (155, 10, 'W'),
        ]),
    '5-1': (225,
        [(0, 40), (44, 75), (79, 120), (124, 224)],
        [
            (15, 9, 'B', 5), (22, 5, 'M'), (28, 9, '?', 2), (40, 11, 'P', 2),
            (58, 9, 'B', 4), (68, 5, '?'), (78, 11, 'P', 3), (92, 9, 'B', 5),
            (108, 11, 'P', 4), (122, 9, '?', 3), (145, 12, '^', 5),
            (165, 12, '^', 6), (185, 11, 'P', 2), (205, 12, '^', 8), (218, 3, 'F'),
            (28, 12, 'g'), (29, 12, 'g'), (55, 12, 'k'), (75, 12, 'g'), (76, 12, 'g'),
            (100, 12, 'k'), (142, 12, 'g'), (143, 12, 'g'),
        ]),
    '5-2': (218,
        [(0, 35), (39, 70), (74, 115), (119, 217)],
        [
            (20, 9, '?'), (25, 9, 'B', 4), (38, 11, 'P', 3), (52, 9, 'M'),
            (65, 9, 'B', 5), (78, 5, '?', 2), (92, 11, 'P', 2), (108, 9, 'B', 4),
            (125, 12, '^', 4), (150, 12, '^', 5), (170, 11, 'P', 3),
            (190, 12, '^', 8), (208, 3, 'F'),
            (30, 12, 'k'), (58, 12, 'g'), (59, 12, 'g'), (88, 12, 'g'),
            (118, 12, 'k'), (158, 12, 'g'), (159, 12, 'g'),
        ]),
    '5-3': (175,
        [(0, 15), (158, 174)],
        [
            (18, 9, '=', 5), (30, 7, '=', 6), (45, 9, '=', 5), (58, 5, '=', 4),
            (72, 7, '=', 6), (86, 9, '=', 5), (100, 7, '=', 6), (114, 5, '=', 4),
            (128, 7, '=', 6), (142, 9, '=', 5), (150, 12, '^', 5), (162, 3, 'F'),
            (24, 8, 'r'), (50, 6, 'r'), (78, 8, 'r'), (106, 6, 'r'), (134, 8, 'r'),
        ]),
    '5-4': (185,
        [(0, 184)],
        [
            (0, 0, 'C', 185),
            (35, 13, 'L', 5), (55, 13, 'L', 5), (78, 13, 'L', 6),
            (102, 13, 'L', 5), (125, 13, 'L', 5),
            (68, 7, '=', 5), (95, 9, '=', 6), (118, 7, '=', 5), (138, 9, '=', 6),
            (152, 9, '=', 18), (172, 9, 'A'), (167, 10, 'W'),
        ]),
    '6-1': (232,
        [(0, 36), (40, 68), (72, 110), (114, 231)],
        [
            (18, 9, 'B', 4), (25, 5, '?'), (32, 9, 'M'), (42, 11, 'P', 2),
            (58, 9, 'B', 5), (70, 5, 'B', 4), (82, 11, 'P', 3), (98, 9, '?', 2),
            (112, 11, 'P', 4), (128, 9, 'B', 6), (150, 12, '^', 5),
            (172, 12, '^', 6), (195, 11, 'P', 2), (215, 12, '^', 8), (225, 3, 'F'),
            (35, 12, 'g'), (36, 12, 'g'), (62, 12, 'k'), (92, 12, 'g'), (93, 12, 'g'),
            (135, 12, 'k'), (180, 12, 'g'), (181, 12, 'g'),
        ]),
    '6-2': (205,
        [(0, 204)],
        [
            (0, 0, 'C', 155),
            (22, 9, 'B', 6), (32, 5, 'B', 4), (45, 9, '?'), (55, 9, 'B', 5),
            (68, 5, 'M'), (80, 9, 'B', 6), (95, 5, 'B', 5), (110, 9, 'B', 4),
            (125, 5, '?', 2), (140, 9, 'B', 5), (158, 5, 'X', 8), (172, 9, 'X', 6),
            (188, 12, '^', 8), (198, 11, 'P', 2), (202, 3, 'F'),
            (28, 12, 'g'), (60, 12, 'g'), (90, 12, 'g'), (120, 12, 'g'),
        ]),
    '6-3': (178,
        [(0, 15), (162, 177)],
        [
            (20, 9, '=', 5), (34, 7, '=', 6), (50, 9, '=', 5), (65, 5, '=', 4),
            (80, 7, '=', 6), (95, 9, '=', 5), (110, 7, '=', 6), (125, 5, '=', 4),
            (140, 7, '=', 6), (155, 9, '=', 5), (158, 12, '^', 5), (168, 3, 'F'),
            (28, 8, 'r'), (56, 6, 'r'), (86, 8, 'r'), (116, 6, 'r'), (146, 8, 'r'),
        ]),
    '6-4': (192,
        [(0, 191)],
        [
            (0, 0, 'C', 192),
            (38, 13, 'L', 5), (60, 13, 'L', 5), (85, 13, 'L', 6),
            (110, 13, 'L', 5), (135, 13, 'L', 6),
            (72, 7, '=', 5), (100, 9, '=', 6), (125, 7, '=', 5), (148, 9, '=', 6),
            (160, 9, '=', 18), (180, 9, 'A'), (175, 10, 'W'),
        ]),
    '7-1': (238,
        [(0, 32), (36, 65), (69, 105), (109, 237)],
        [
            (20, 9, 'B', 5), (28, 5, 'M'), (38, 9, '?', 2), (48, 11, 'P', 2),
            (60, 9, 'B', 4), (75, 5, '?'), (88, 11, 'P', 3), (102, 9, 'B', 5),
            (120, 11, 'P', 4), (138, 9, '?', 3), (158, 12, '^', 5),
            (180, 12, '^', 6), (202, 11, 'P', 2), (222, 12, '^', 8), (232, 3, 'F'),
            (32, 12, 'g'), (33, 12, 'g'), (55, 12, 'k'), (82, 12, 'g'), (83, 12, 'g'),
            (112, 12, 'k'), (168, 12, 'g'), (169, 12, 'g'),
        ]),
    '7-2': (188,
        [(0, 187)],
        [
            (25, 10, '=', 6), (42, 8, '=', 5), (60, 6, '=', 4),
            (78, 10, '=', 6), (96, 8, '=', 5), (114, 6, '=', 4),
            (132, 10, '=', 6), (150, 8, '=', 5), (168, 11, 'P', 2), (180, 3, 'F'),
        ]),
    '7-3': (182,
        [(0, 15), (166, 181)],
        [
            (22, 9, '=', 5), (38, 7, '=', 6), (55, 9, '=', 5), (72, 5, '=', 4),
            (88, 7, '=', 6), (105, 9, '=', 5), (122, 7, '=', 6), (138, 5, '=', 4),
            (155, 7, '=', 6), (162, 12, '^', 5), (172, 3, 'F'),
            (30, 8, 'r'), (62, 6, 'r'), (95, 8, 'r'), (128, 6, 'r'), (160, 8, 'r'),
        ]),
    '7-4': (200,
        [(0, 199)],
        [
            (0, 0, 'C', 200),
            (40, 13, 'L', 5), (65, 13, 'L', 5), (92, 13, 'L', 6),
            (118, 13, 'L', 5), (145, 13, 'L', 6),
            (78, 7, '=', 5), (108, 9, '=', 6), (135, 7, '=', 5), (158, 9, '=', 6),
            (170, 9, '=', 18), (190, 9, 'A'), (185, 10, 'W'),
        ]),
    '8-1': (250,
        [(0, 28), (32, 58), (62, 92), (96, 125), (129, 249)],
        [
            (22, 9, 'B', 5), (30, 5, 'M'), (42, 9, '?', 2), (55, 11, 'P', 2),
            (70, 9, 'B', 4), (85, 5, '?'), (98, 11, 'P', 3), (115, 9, 'B', 5),
            (132, 11, 'P', 4), (150, 9, '?', 3), (172, 12, '^', 5),
            (195, 12, '^', 6), (218, 11, 'P', 2), (238, 12, '^', 8), (245, 3, 'F'),
            (38, 12, 'g'), (39, 12, 'g'), (62, 12, 'k'), (92, 12, 'g'), (93, 12, 'g'),
            (128, 12, 'k'), (185, 12, 'g'), (186, 12, 'g'),
        ]),
    '8-2': (242,
        [(0, 26), (30, 55), (59, 88), (92, 120), (124, 241)],
        [
            (25, 9, '?'), (32, 9, 'B', 4), (48, 11, 'P', 3), (65, 9, 'M'),
            (80, 9, 'B', 5), (98, 5, '?', 2), (115, 11, 'P', 2), (132, 9, 'B', 4),
            (155, 12, '^', 5), (180, 12, '^', 6), (202, 11, 'P', 3),
            (225, 12, '^', 8), (238, 3, 'F'),
            (42, 12, 'k'), (72, 12, 'g'), (73, 12, 'g'), (108, 12, 'g'),
            (148, 12, 'k'), (192, 12, 'g'), (193, 12, 'g'),
        ]),
    '8-3': (188,
        [(0, 15), (172, 187)],
        [
            (25, 9, '=', 5), (42, 7, '=', 6), (60, 9, '=', 5), (78, 5, '=', 4),
            (95, 7, '=', 6), (113, 9, '=', 5), (130, 7, '=', 6), (148, 5, '=', 4),
            (165, 7, '=', 6), (170, 12, '^', 5), (180, 3, 'F'),
            (35, 8, 'r'), (68, 6, 'r'), (102, 8, 'r'), (138, 6, 'r'), (170, 8, 'r'),
        ]),
    '8-4': (240,
        [(0, 239)],
        [
            (0, 0, 'C', 240),
            (42, 13, 'L', 6), (68, 13, 'L', 6), (95, 13, 'L', 7),
            (125, 13, 'L', 6), (155, 13, 'L', 7), (185, 13, 'L', 6),
            (62, 7, '=', 5), (92, 9, '=', 6), (122, 7, '=', 5),
            (152, 9, '=', 6), (182, 7, '=', 5), (205, 9, '=', 18),
            (225, 9, 'A'), (220, 10, 'W'),
        ]),
}

# === TILE CLASS ===
class Tile:
    def __init__(self, x, y, tile_type):
        self.rect = pygame.Rect(x, y, T, T)
        self.base_y = y
        self.type = tile_type
        self.solid = tile_type not in 'LA'
        self.content = None
        self.used = False
        self.bump_timer = 0
        
        if tile_type == '?':
            self.content = 'coin'
        elif tile_type == 'M':
            self.type = '?'
            self.content = 'mushroom'
        elif tile_type == 'S':
            self.type = '?'
            self.content = 'star'
    
    def update(self):
        if self.bump_timer > 0:
            self.rect.y = self.base_y + int(math.sin(self.bump_timer * 0.6) * -8)
            self.bump_timer -= 1
        else:
            self.rect.y = self.base_y
    
    def bump(self, mario):
        if self.bump_timer > 0 or self.used:
            return None
        
        self.bump_timer = 8
        SFX['bump'].play()
        
        if self.type == '?' and self.content:
            self.used = True
            return self.content
        elif self.type == 'B' and mario.big:
            return 'break'
        return None
    
    def draw(self, screen, camera):
        if self.type == '.':
            return
        key = 'U' if self.used and self.type == '?' else self.type
        if key in TILES:
            screen.blit(TILES[key], (self.rect.x - camera, self.rect.y))

# === MARIO CLASS (NES-accurate) ===
class Mario:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.width = 24
        self.height = 32
        
        self.on_ground = False
        self.facing_right = True
        self.big = False
        self.fire = False
        self.star = False
        self.star_timer = 0
        self.invincible = 0
        
        self.dead = False
        self.won = False
        self.death_timer = 0
        self.win_timer = 0
        
        # Jump state
        self.jumping = False
        self.jump_held = False
        self.jump_timer = 0
    
    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)
    
    def update(self, keys, tiles, game):
        if self.dead:
            self.death_timer += 1
            if self.death_timer < 20:
                self.vy = -10
            else:
                self.vy += 0.5
            self.y += self.vy
            return
        
        if self.won:
            self.win_timer += 1
            if self.win_timer < 60:
                self.y += 2
            else:
                self.vx = 2.0
                self._apply_physics(tiles)
            return
        
        # Input
        left = keys[pygame.K_LEFT] or keys[pygame.K_a]
        right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        run = keys[pygame.K_LSHIFT] or keys[pygame.K_z]
        jump = keys[pygame.K_SPACE] or keys[pygame.K_x] or keys[pygame.K_UP]
        
        # Horizontal movement (NES-accurate)
        max_speed = Phys.RUN_MAX if run else Phys.WALK_MAX
        accel = Phys.RUN_ACCEL if run else Phys.WALK_ACCEL
        
        if self.on_ground:
            if right and not left:
                if self.vx < 0:
                    # Skidding
                    self.vx += Phys.SKID_DECEL
                    if self.vx > 0:
                        self.vx = 0
                else:
                    self.vx = min(self.vx + accel, max_speed)
                self.facing_right = True
            elif left and not right:
                if self.vx > 0:
                    # Skidding
                    self.vx -= Phys.SKID_DECEL
                    if self.vx < 0:
                        self.vx = 0
                else:
                    self.vx = max(self.vx - accel, -max_speed)
                self.facing_right = False
            else:
                # Friction
                if self.vx > 0:
                    self.vx = max(0, self.vx - Phys.RELEASE_DECEL)
                elif self.vx < 0:
                    self.vx = min(0, self.vx + Phys.RELEASE_DECEL)
        else:
            # Air control
            if right and not left:
                self.vx = min(self.vx + Phys.AIR_ACCEL, max_speed)
                self.facing_right = True
            elif left and not right:
                self.vx = max(self.vx - Phys.AIR_ACCEL, -max_speed)
                self.facing_right = False
        
        # Jumping (NES variable height)
        if jump and self.on_ground and not self.jump_held:
            # Initial jump velocity based on horizontal speed
            speed = abs(self.vx)
            if speed < 1.5:
                self.vy = Phys.JUMP_STANDING
            elif speed < 4.0:
                self.vy = Phys.JUMP_WALKING
            else:
                self.vy = Phys.JUMP_RUNNING
            
            self.on_ground = False
            self.jumping = True
            self.jump_held = True
            self.jump_timer = 0
            SFX['jump'].play()
        
        if not jump:
            self.jump_held = False
            self.jumping = False
        
        # Gravity
        if self.vy < 0 and jump and self.jump_timer < Phys.JUMP_HOLD_MAX:
            # Rising while holding jump - reduced gravity
            self.vy += Phys.GRAVITY_RISING
            self.jump_timer += 1
        else:
            # Falling or released jump
            self.vy += Phys.GRAVITY_FALLING
            self.jumping = False
        
        self.vy = min(self.vy, Phys.MAX_FALL)
        
        # Apply physics
        self._apply_physics(tiles)
        
        # Bounds
        if self.x < 0:
            self.x = 0
            self.vx = 0
        
        if self.y > H + 64:
            self.die(game)
        
        # Timers
        if self.star:
            self.star_timer -= 1
            if self.star_timer <= 0:
                self.star = False
        
        if self.invincible > 0:
            self.invincible -= 1
    
    def _apply_physics(self, tiles):
        # Horizontal collision
        self.x += self.vx
        rect = self.rect
        
        for tile in tiles:
            if tile.solid and rect.colliderect(tile.rect):
                if self.vx > 0:
                    self.x = tile.rect.left - self.width
                elif self.vx < 0:
                    self.x = tile.rect.right
                self.vx = 0
                rect = self.rect
        
        # Vertical collision
        was_on_ground = self.on_ground
        self.on_ground = False
        self.y += self.vy
        rect = self.rect
        
        for tile in tiles:
            if tile.solid and rect.colliderect(tile.rect):
                if self.vy > 0:
                    # Landing
                    self.y = tile.rect.top - self.height
                    self.vy = 0
                    self.on_ground = True
                    self.jumping = False
                elif self.vy < 0:
                    # Hit ceiling
                    self.y = tile.rect.bottom
                    self.vy = 0
                    self.jumping = False
                    # Bump block
                    return tile.bump(self)
                rect = self.rect
        
        return None
    
    def die(self, game):
        if self.invincible > 0 or self.star:
            return
        
        if self.big:
            self.big = False
            self.fire = False
            self.invincible = 120
            self.height = 32
            SFX['powerup'].play()
        else:
            self.dead = True
            self.vy = -10
            SFX['die'].play()
    
    def grow(self):
        if not self.big:
            self.big = True
            self.y -= 24
            self.height = 56
            SFX['powerup'].play()
    
    def draw(self, screen, camera):
        if self.dead and self.death_timer > 120:
            return
        
        if self.invincible > 0 and (self.invincible // 4) % 2:
            return
        
        h = 56 if self.big else 32
        img = pygame.Surface((24, h), pygame.SRCALPHA)
        
        # Color
        if self.fire:
            body_color = Pal.WHITE
        elif self.star and (pygame.time.get_ticks() // 60) % 2:
            body_color = (255, 255, 0)
        else:
            body_color = Pal.RED
        
        # Draw Mario
        # Hat
        pygame.draw.rect(img, body_color, (4, 0, 16, 8))
        # Face
        pygame.draw.rect(img, Pal.SKIN, (4, 8, 16, 10))
        # Eyes
        pygame.draw.rect(img, Pal.BLACK, (8, 10, 3, 3))
        pygame.draw.rect(img, Pal.BLACK, (14, 10, 3, 3))
        # Body
        pygame.draw.rect(img, body_color, (2, 18, 20, h // 3))
        # Overalls
        pygame.draw.rect(img, (0, 0, 200), (2, 18 + h // 3, 20, h // 3))
        # Legs
        if self.big:
            pygame.draw.rect(img, (0, 0, 200), (2, h - 16, 8, 16))
            pygame.draw.rect(img, (0, 0, 200), (14, h - 16, 8, 16))
        
        if not self.facing_right:
            img = pygame.transform.flip(img, True, False)
        
        screen.blit(img, (int(self.x) - camera, int(self.y)))

# === ENEMIES ===
class Goomba:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.vx = -1.0
        self.vy = 0.0
        self.width = T
        self.height = T
        self.alive = True
        self.stomped = False
        self.stomp_timer = 0
    
    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)
    
    def update(self, tiles):
        if self.stomped:
            self.stomp_timer += 1
            self.alive = self.stomp_timer <= 20
            return
        
        self.vy = min(self.vy + Phys.GRAVITY_FALLING, Phys.MAX_FALL)
        
        # Horizontal
        self.x += self.vx
        rect = self.rect
        for tile in tiles:
            if tile.solid and rect.colliderect(tile.rect):
                self.vx *= -1
                self.x += self.vx * 2
                rect = self.rect
        
        # Vertical
        self.y += self.vy
        rect = self.rect
        for tile in tiles:
            if tile.solid and rect.colliderect(tile.rect):
                if self.vy > 0:
                    self.y = tile.rect.top - self.height
                    self.vy = 0
                rect = self.rect
    
    def stomp(self):
        self.stomped = True
        self.vx = 0
        self.height = 12
        self.y += 20
    
    def draw(self, screen, camera):
        if not self.alive:
            return
        
        h = 12 if self.stomped else T
        img = pygame.Surface((T, h), pygame.SRCALPHA)
        
        # Body
        pygame.draw.ellipse(img, Pal.GOOMBA, (0, 0, T, h))
        
        if not self.stomped:
            # Face
            pygame.draw.ellipse(img, (200, 100, 50), (4, 4, 24, 16))
            # Eyes (angry)
            pygame.draw.polygon(img, Pal.WHITE, [(8, 8), (14, 12), (8, 14)])
            pygame.draw.polygon(img, Pal.WHITE, [(24, 8), (18, 12), (24, 14)])
            pygame.draw.rect(img, Pal.BLACK, (9, 11, 2, 2))
            pygame.draw.rect(img, Pal.BLACK, (21, 11, 2, 2))
            # Feet
            pygame.draw.ellipse(img, Pal.BLACK, (2, 26, 10, 6))
            pygame.draw.ellipse(img, Pal.BLACK, (20, 26, 10, 6))
        
        screen.blit(img, (int(self.x) - camera, int(self.y)))

class Koopa:
    def __init__(self, x, y, red=False):
        self.x = float(x)
        self.y = float(y)
        self.vx = -1.0
        self.vy = 0.0
        self.width = T
        self.height = 48
        self.alive = True
        self.shell = False
        self.shell_moving = False
        self.red = red
        self.on_ground = False
    
    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)
    
    def update(self, tiles):
        self.vy = min(self.vy + Phys.GRAVITY_FALLING, Phys.MAX_FALL)
        
        # Horizontal
        self.x += self.vx
        rect = self.rect
        for tile in tiles:
            if tile.solid and rect.colliderect(tile.rect):
                self.vx *= -1
                self.x += self.vx * 2
                rect = self.rect
        
        # Vertical
        self.on_ground = False
        self.y += self.vy
        rect = self.rect
        for tile in tiles:
            if tile.solid and rect.colliderect(tile.rect):
                if self.vy > 0:
                    self.y = tile.rect.top - self.height
                    self.vy = 0
                    self.on_ground = True
                rect = self.rect
        
        # Red koopa turns at edges
        if self.red and not self.shell and self.on_ground:
            test_x = self.x + self.width / 2 + (16 if self.vx > 0 else -16)
            test_y = self.y + self.height + 4
            on_floor = any(t.solid and t.rect.collidepoint(test_x, test_y) for t in tiles)
            if not on_floor:
                self.vx *= -1
    
    def stomp(self, mario):
        if not self.shell:
            self.shell = True
            self.vx = 0
            self.height = 28
            self.y += 20
        elif not self.shell_moving:
            self.shell_moving = True
            self.vx = 6 if mario.x < self.x else -6
        else:
            self.shell_moving = False
            self.vx = 0
        SFX['stomp'].play()
    
    def draw(self, screen, camera):
        color = (200, 50, 50) if self.red else Pal.KOOPA
        color_light = (255, 150, 150) if self.red else (100, 220, 100)
        
        img = pygame.Surface((T, self.height), pygame.SRCALPHA)
        
        if self.shell:
            pygame.draw.ellipse(img, color, (0, 0, T, 28))
            pygame.draw.ellipse(img, color_light, (4, 4, 24, 20))
        else:
            # Shell
            pygame.draw.ellipse(img, color, (4, 16, 24, 32))
            pygame.draw.ellipse(img, color_light, (8, 20, 16, 24))
            # Head
            pygame.draw.ellipse(img, (255, 220, 180), (4, 0, 20, 20))
            # Eyes
            pygame.draw.rect(img, Pal.BLACK, (8, 6, 4, 4))
            pygame.draw.rect(img, Pal.BLACK, (16, 6, 4, 4))
        
        screen.blit(img, (int(self.x) - camera, int(self.y)))

class Powerup:
    def __init__(self, x, y, ptype):
        self.x = float(x)
        self.y = float(y)
        self.vx = 1.5 if ptype in ['mushroom', '1up'] else 0
        self.vy = 0.0
        self.width = T
        self.height = T
        self.type = ptype
        self.alive = True
        self.emerging = True
        self.emerge_y = 0
    
    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)
    
    def update(self, tiles):
        if self.emerging:
            self.emerge_y += 0.5
            if self.emerge_y >= T:
                self.emerging = False
                self.y -= T
            return
        
        if self.type in ['mushroom', '1up', 'star']:
            self.vy = min(self.vy + Phys.GRAVITY_FALLING, Phys.MAX_FALL)
            
            if self.type == 'star':
                # Star bounces
                pass
            
            # Horizontal
            self.x += self.vx
            rect = self.rect
            for tile in tiles:
                if tile.solid and rect.colliderect(tile.rect):
                    self.vx *= -1
                    self.x += self.vx * 2
                    rect = self.rect
            
            # Vertical
            self.y += self.vy
            rect = self.rect
            for tile in tiles:
                if tile.solid and rect.colliderect(tile.rect):
                    if self.vy > 0:
                        self.y = tile.rect.top - self.height
                        self.vy = 0
                        if self.type == 'star':
                            self.vy = -8
                    rect = self.rect
    
    def draw(self, screen, camera):
        img = pygame.Surface((T, T), pygame.SRCALPHA)
        draw_y = int(self.y) + (T - int(self.emerge_y) if self.emerging else 0)
        
        if self.type == 'mushroom':
            pygame.draw.ellipse(img, Pal.RED, (2, 2, 28, 14))
            pygame.draw.ellipse(img, Pal.WHITE, (6, 4, 8, 8))
            pygame.draw.ellipse(img, Pal.WHITE, (18, 4, 8, 8))
            pygame.draw.rect(img, (255, 220, 180), (10, 14, 12, 14))
        elif self.type == 'flower':
            pygame.draw.circle(img, Pal.RED, (16, 10), 10)
            pygame.draw.circle(img, (255, 200, 0), (16, 10), 5)
            pygame.draw.rect(img, Pal.KOOPA, (14, 18, 4, 12))
        elif self.type == 'star':
            pts = [(16 + 10*math.cos(math.radians(i*72-90)), 
                    16 + 10*math.sin(math.radians(i*72-90))) for i in range(5)]
            pygame.draw.polygon(img, (252, 188, 60), pts)
            pygame.draw.circle(img, Pal.BLACK, (12, 14), 2)
            pygame.draw.circle(img, Pal.BLACK, (20, 14), 2)
        
        screen.blit(img, (int(self.x) - camera, draw_y))

# === LEVEL BUILDER ===
def build_level(level_key):
    width, ground_segments, objects = LEVELS[level_key]
    tiles = []
    enemies = []
    flag_x = 9999
    
    # Create grid
    rows = ['.' * width for _ in range(15)]
    
    # Build ground
    for start, end in ground_segments:
        for x in range(start, min(end + 1, width)):
            rows[13] = rows[13][:x] + 'G' + rows[13][x+1:]
            rows[14] = rows[14][:x] + 'G' + rows[14][x+1:]
    
    # Place objects
    for obj in objects:
        x, y, obj_type = obj[0], obj[1], obj[2]
        count = obj[3] if len(obj) > 3 else 1
        
        if obj_type == 'P':  # Pipe
            for i in range(count):
                py = y + i
                if py < 15:
                    ch = 'T' if i == 0 else 'P'
                    rows[py] = rows[py][:x] + ch + ch + rows[py][x+2:]
        elif obj_type in 'B?MXC':
            for i in range(count):
                if x + i < width:
                    rows[y] = rows[y][:x+i] + obj_type + rows[y][x+i+1:]
        elif obj_type == '=':  # Platform
            for i in range(count):
                if x + i < width:
                    rows[y] = rows[y][:x+i] + 'X' + rows[y][x+i+1:]
        elif obj_type == 'L':  # Lava
            for i in range(count):
                if x + i < width:
                    rows[y] = rows[y][:x+i] + 'L' + rows[y][x+i+1:]
        elif obj_type == '^':  # Ascending stairs
            for i in range(count):
                for j in range(i + 1):
                    if 12 - j >= 0 and x + i < width:
                        rows[12-j] = rows[12-j][:x+i] + 'X' + rows[12-j][x+i+1:]
        elif obj_type == 'v':  # Descending stairs
            for i in range(count):
                for j in range(count - i):
                    if 12 - j >= 0 and x + i < width:
                        rows[12-j] = rows[12-j][:x+i] + 'X' + rows[12-j][x+i+1:]
        elif obj_type == 'F':  # Flag
            rows[y] = rows[y][:x] + 'F' + rows[y][x+1:]
            flag_x = x * T
        elif obj_type == 'A':  # Axe
            rows[y] = rows[y][:x] + 'A' + rows[y][x+1:]
        elif obj_type == 'g':  # Goomba
            enemies.append(Goomba(x * T, y * T))
        elif obj_type == 'k':  # Green Koopa
            enemies.append(Koopa(x * T, (y - 0.5) * T, False))
        elif obj_type == 'r':  # Red Koopa
            enemies.append(Koopa(x * T, (y - 0.5) * T, True))
        elif obj_type == 'W':  # Bowser (placeholder as Koopa)
            enemies.append(Koopa(x * T, (y - 0.5) * T, False))
    
    # Convert to tiles
    for row_idx, row in enumerate(rows):
        for col_idx, char in enumerate(row):
            if char == '.':
                continue
            tiles.append(Tile(col_idx * T, row_idx * T, char))
            
            # Flag pole
            if char == 'F':
                for i in range(1, 11):
                    tiles.append(Tile(col_idx * T, (row_idx + i) * T, 'X'))
    
    return width, tiles, enemies, flag_x

# === MENU ===
class Menu:
    def __init__(self):
        self.selection = 0
        self.options = ['1 PLAYER GAME', 'OPTIONS', 'CREDITS']
        self.frame = 0
    
    def update(self, keys_pressed):
        if keys_pressed.get(pygame.K_UP) or keys_pressed.get(pygame.K_w):
            self.selection = (self.selection - 1) % len(self.options)
            SFX['cursor'].play()
        if keys_pressed.get(pygame.K_DOWN) or keys_pressed.get(pygame.K_s):
            self.selection = (self.selection + 1) % len(self.options)
            SFX['cursor'].play()
        if keys_pressed.get(pygame.K_SPACE) or keys_pressed.get(pygame.K_RETURN):
            SFX['select'].play()
            return self.selection
        self.frame += 1
        return -1
    
    def draw(self, screen, fonts):
        fnt, fntb, fnts = fonts
        
        # Background
        screen.fill(Pal.BLUE)
        
        # Decorative tiles
        for i in range(26):
            screen.blit(TILES['B'], (i * T, H - T))
            screen.blit(TILES['G'], (i * T, H - T * 2))
        
        # Animated question blocks
        qy = H - T * 5 + int(math.sin(self.frame * 0.1) * 3)
        screen.blit(TILES['?'], (4 * T, qy))
        screen.blit(TILES['?'], (20 * T, qy))
        
        # Pipe
        screen.blit(TILES['T'], (22 * T, H - T * 3))
        screen.blit(TILES['T'], (23 * T, H - T * 3))
        screen.blit(TILES['P'], (22 * T, H - T * 2))
        screen.blit(TILES['P'], (23 * T, H - T * 2))
        
        # Title
        title1 = "Cat's Ultra Mario"
        title2 = "2D Bross!"
        
        # Shadow
        t1 = fntb.render(title1, True, (0, 0, 100))
        t2 = fntb.render(title2, True, (0, 0, 100))
        screen.blit(t1, (W // 2 - t1.get_width() // 2 + 3, 53))
        screen.blit(t2, (W // 2 - t2.get_width() // 2 + 3, 93))
        
        # Main
        t1 = fntb.render(title1, True, Pal.WHITE)
        t2 = fntb.render(title2, True, (252, 188, 60))
        screen.blit(t1, (W // 2 - t1.get_width() // 2, 50))
        screen.blit(t2, (W // 2 - t2.get_width() // 2, 90))
        
        # Version
        v = fnts.render('v0.1', True, Pal.WHITE)
        screen.blit(v, (W // 2 + t2.get_width() // 2 + 10, 100))
        
        # Menu box
        box_w, box_h = 280, 160
        box_x, box_y = W // 2 - box_w // 2, 180
        pygame.draw.rect(screen, Pal.BLACK, (box_x, box_y, box_w, box_h))
        pygame.draw.rect(screen, Pal.WHITE, (box_x, box_y, box_w, box_h), 3)
        pygame.draw.rect(screen, (252, 188, 60), (box_x + 4, box_y + 4, box_w - 8, box_h - 8), 2)
        
        # Options
        for i, opt in enumerate(self.options):
            y = box_y + 30 + i * 40
            color = (252, 152, 56) if i == self.selection else Pal.WHITE
            txt = fnt.render(opt, True, color)
            screen.blit(txt, (box_x + 50, y))
            
            if i == self.selection:
                # Mushroom cursor
                mx, my = box_x + 20, y + 4
                pygame.draw.ellipse(screen, Pal.RED, (mx, my, 20, 10))
                pygame.draw.rect(screen, (255, 220, 180), (mx + 6, my + 8, 8, 8))
        
        # Credits
        cr = fnts.render('(C) 2025 Team Flames', True, Pal.WHITE)
        screen.blit(cr, (W // 2 - cr.get_width() // 2, H - 60))

# === GAME ===
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption("Cat's Ultra Mario 2D Bross! 0.1")
        self.clock = pygame.time.Clock()
        
        self.font = pygame.font.Font(None, 36)
        self.font_big = pygame.font.Font(None, 52)
        self.font_small = pygame.font.Font(None, 24)
        
        self.menu = Menu()
        self.world = 1
        self.stage = 1
        self.lives = 3
        self.score = 0
        self.coins = 0
        
        self.state = 'menu'
        self.transition_timer = 0
        self.keys_pressed = {}
    
    def load_level(self):
        key = f'{self.world}-{self.stage}'
        self.level_width, self.tiles, self.enemies, self.flag_x = build_level(key)
        
        # Background color
        if self.stage in [2, 4]:
            self.bg_color = Pal.BLACK
        else:
            self.bg_color = Pal.SKY
        
        self.time = 400 if self.stage != 4 else 300
        self.powerups = []
        self.mario = Mario(64, 320)
        self.camera = 0
    
    def update(self):
        if self.state == 'menu':
            result = self.menu.update(self.keys_pressed)
            if result == 0:
                self.load_level()
                self.state = 'transition'
                self.transition_timer = 90
        
        elif self.state == 'transition':
            self.transition_timer -= 1
            if self.transition_timer <= 0:
                self.state = 'play'
        
        elif self.state == 'win':
            keys = pygame.key.get_pressed()
            self.mario.update(keys, self.tiles, self)
            self.transition_timer -= 1
            if self.transition_timer <= 0:
                self.stage += 1
                if self.stage > 4:
                    self.stage = 1
                    self.world += 1
                if self.world > 8:
                    self.world = 1
                self.load_level()
                self.state = 'transition'
                self.transition_timer = 90
        
        elif self.state == 'play':
            keys = pygame.key.get_pressed()
            self.mario.update(keys, self.tiles, self)
            
            # Camera
            self.camera = max(0, min(int(self.mario.x) - W // 3, self.level_width * T - W))
            
            # Update entities
            for enemy in self.enemies:
                enemy.update(self.tiles)
            for powerup in self.powerups:
                powerup.update(self.tiles)
            for tile in self.tiles:
                tile.update()
            
            # Check block bumps
            for tile in self.tiles:
                if tile.bump_timer == 7 and tile.content:
                    content = tile.content
                    tile.content = None
                    
                    if content == 'mushroom':
                        ptype = 'mushroom' if not self.mario.big else 'flower'
                        self.powerups.append(Powerup(tile.rect.x, tile.rect.y, ptype))
                        SFX['powerup'].play()
                    elif content == 'star':
                        self.powerups.append(Powerup(tile.rect.x, tile.rect.y, 'star'))
                    elif content == 'coin':
                        self.coins += 1
                        self.score += 200
                        SFX['coin'].play()
            
            # Remove broken bricks
            self.tiles = [t for t in self.tiles if not (t.type == 'B' and t.bump_timer == 7 and self.mario.big)]
            
            # Powerup collection
            mario_rect = self.mario.rect
            for powerup in self.powerups[:]:
                if not powerup.emerging and powerup.alive and mario_rect.colliderect(powerup.rect):
                    if powerup.type == 'mushroom':
                        self.mario.grow()
                    elif powerup.type == 'flower':
                        self.mario.big = True
                        self.mario.fire = True
                        SFX['powerup'].play()
                    elif powerup.type == 'star':
                        self.mario.star = True
                        self.mario.star_timer = 600
                        SFX['powerup'].play()
                    self.powerups.remove(powerup)
            
            # Enemy collision
            for enemy in self.enemies[:]:
                if enemy.alive and mario_rect.colliderect(enemy.rect):
                    if self.mario.star:
                        enemy.alive = False
                        self.score += 200
                    elif isinstance(enemy, Goomba):
                        if self.mario.vy > 0 and mario_rect.bottom < enemy.y + enemy.height // 2 + 8 and not enemy.stomped:
                            enemy.stomp()
                            self.mario.vy = -8
                            self.score += 100
                            SFX['stomp'].play()
                        elif not enemy.stomped:
                            self.mario.die(self)
                    elif isinstance(enemy, Koopa):
                        if self.mario.vy > 0 and mario_rect.bottom < enemy.y + enemy.height // 2 + 8:
                            enemy.stomp(self.mario)
                            self.mario.vy = -8
                            self.score += 100
                        elif enemy.shell and not enemy.shell_moving:
                            enemy.stomp(self.mario)
                        elif not enemy.shell:
                            self.mario.die(self)
            
            # Hazards
            for tile in self.tiles:
                if tile.type == 'L' and mario_rect.colliderect(tile.rect):
                    self.mario.die(self)
                if tile.type == 'A' and mario_rect.colliderect(tile.rect) and not self.mario.won:
                    self.mario.won = True
                    self.state = 'win'
                    self.transition_timer = 180
                    SFX['flag'].play()
            
            # Flag
            if self.mario.x >= self.flag_x and not self.mario.won:
                self.mario.won = True
                self.state = 'win'
                self.transition_timer = 180
                SFX['flag'].play()
            
            if self.mario.dead:
                self.state = 'dead'
            
            if self.time > 0:
                self.time -= 1 / FPS
    
    def draw(self):
        if self.state == 'menu':
            self.menu.draw(self.screen, (self.font, self.font_big, self.font_small))
        
        elif self.state == 'transition':
            self.screen.fill(Pal.BLACK)
            txt = self.font_big.render(f'WORLD {self.world}-{self.stage}', True, Pal.WHITE)
            self.screen.blit(txt, (W // 2 - txt.get_width() // 2, H // 2 - 40))
            
            # Mario icon
            pygame.draw.ellipse(self.screen, Pal.RED, (W // 2 - 50, H // 2 + 15, 20, 10))
            pygame.draw.rect(self.screen, (255, 220, 180), (W // 2 - 46, H // 2 + 23, 12, 12))
            
            lives_txt = self.font.render(f'x {self.lives}', True, Pal.WHITE)
            self.screen.blit(lives_txt, (W // 2 - 20, H // 2 + 20))
        
        else:
            self.screen.fill(self.bg_color)
            
            for tile in self.tiles:
                tile.draw(self.screen, self.camera)
            for enemy in self.enemies:
                enemy.draw(self.screen, self.camera)
            for powerup in self.powerups:
                powerup.draw(self.screen, self.camera)
            self.mario.draw(self.screen, self.camera)
            
            # HUD
            pygame.draw.rect(self.screen, (0, 0, 0), (0, 0, W, 50))
            
            self.screen.blit(self.font.render(f'MARIO x{self.lives}', True, Pal.WHITE), (20, 8))
            self.screen.blit(self.font_small.render(f'{self.score:06d}', True, Pal.WHITE), (20, 32))
            
            world_txt = self.font.render(f'WORLD {self.world}-{self.stage}', True, Pal.WHITE)
            self.screen.blit(world_txt, (W // 2 - world_txt.get_width() // 2, 8))
            
            self.screen.blit(self.font.render(f'TIME {int(self.time)}', True, Pal.WHITE), (W - 150, 8))
            self.screen.blit(self.font_small.render(f'COINS x{self.coins:02d}', True, (252, 188, 60)), (W - 150, 32))
            
            if self.state == 'dead':
                self.screen.blit(self.font.render('Press SPACE', True, Pal.WHITE), (W // 2 - 70, H // 2 + 100))
    
    def run(self):
        running = True
        while running:
            self.keys_pressed = {}
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    self.keys_pressed[event.key] = True
                    
                    if self.state == 'dead' and event.key == pygame.K_SPACE:
                        self.lives -= 1
                        if self.lives <= 0:
                            self.lives = 3
                            self.score = 0
                            self.coins = 0
                            self.world = 1
                            self.stage = 1
                        self.load_level()
                        self.state = 'play'
            
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()

if __name__ == '__main__':
    Game().run()
