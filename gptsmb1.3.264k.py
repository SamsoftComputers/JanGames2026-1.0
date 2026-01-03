#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                       ULTRA MARIO 2D BROS                                    ║
║              [C] SAMSOFT 2026  |  [C] 1985 NINTENDO                          ║
║   Authentic World 1-1 • Full Sprites • 60FPS • No External Assets            ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import sys
import pygame
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple

# ─────────────────────────────────────────────────────────────
# CONFIG & INIT - FAMICOM ACCURATE
# ─────────────────────────────────────────────────────────────
pygame.init()
pygame.display.set_caption("ULTRA MARIO 2D BROS [C] Samsoft 2026")

try:
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
except:
    pass

SCALE = 3
NES_PIXEL = SCALE
TILE_SIZE = 16 * NES_PIXEL
SCREEN_W = 256 * NES_PIXEL
SCREEN_H = 240 * NES_PIXEL
FPS = 60  # Famicom NTSC

# Physics tuned to match original SMB feel
GRAVITY = 0.4 * NES_PIXEL
MAX_FALL = 4.5 * NES_PIXEL
JUMP_FORCE = -6.5 * NES_PIXEL
WALK_ACCEL = 0.08 * NES_PIXEL
RUN_ACCEL = 0.12 * NES_PIXEL
MAX_WALK = 1.5 * NES_PIXEL
MAX_RUN = 2.5 * NES_PIXEL
FRICTION = 0.92
AIR_FRICTION = 0.98

# ─────────────────────────────────────────────────────────────
# NES PALETTE - Authentic SMB Colors
# ─────────────────────────────────────────────────────────────
class C:
    SKY = (104, 136, 252)
    BLACK = (0, 0, 0)
    WHITE = (252, 252, 252)
    
    # Mario
    M_RED = (238, 28, 37)
    M_SKIN = (254, 209, 176)
    M_BROWN = (137, 76, 47)
    
    # Enemies
    E_BODY = (228, 110, 60)
    E_DARK = (136, 20, 0)
    
    # Ground/Brick - SMB World 1 palette
    G_LIGHT = (252, 188, 116)
    G_MID = (228, 110, 60)
    G_DARK = (136, 20, 0)
    G_SHADOW = (68, 0, 0)
    
    # Question Block
    Q_LIGHT = (252, 188, 116)
    Q_DARK = (180, 92, 0)
    Q_SHADOW = (100, 48, 0)
    
    # Pipes
    PIPE_L = (0, 168, 68)
    PIPE_D = (0, 104, 40)
    PIPE_H = (128, 208, 76)
    
    # Items
    COIN_O = (252, 188, 60)
    COIN_I = (252, 252, 176)
    
    # Castle/Flag
    CASTLE = (160, 160, 160)
    CASTLE_D = (84, 84, 84)
    FLAG_GREEN = (0, 168, 68)

# ─────────────────────────────────────────────────────────────
# SPRITE DATA - Authentic SMB Style
# ─────────────────────────────────────────────────────────────
MARIO_PALETTE = {'R': C.M_RED, 'S': C.M_SKIN, 'B': C.M_BROWN}

# Authentic SMB1 Small Mario sprites (12x16 effective)
S_MARIO_STAND = [
    "................",
    "................",
    "................",
    ".....RRRR.......",
    "....RRRRRRRR....",
    "....BBBSSBS.....",
    "...BSSBSSSBS....",
    "...BSSBSSSSB....",
    "...BBSSSSBB.....",
    ".....SSSSSS.....",
    "....RRSRRSR.....",
    "...RRRSRRRSRR...",
    "...SSRSSSRSS....",
    "...SSSSSSSSSS...",
    "....BBB.BBB.....",
    "...BBB...BBB...."
]

S_MARIO_RUN1 = [
    "................",
    "................",
    "................",
    ".....RRRR.......",
    "....RRRRRRRR....",
    "....BBBSSBS.....",
    "...BSSBSSSBS....",
    "...BSSBSSSSB....",
    "...BBSSSSBB.....",
    ".....SSSSSS.....",
    "....RRRRRBB.....",
    "...SRRRRRBBB....",
    "...SSSSSBB......",
    "....RRRR........",
    "...BBBBB........",
    "..BBBB.........."
]

S_MARIO_RUN2 = [
    "................",
    "................",
    "................",
    ".....RRRR.......",
    "....RRRRRRRR....",
    "....BBBSSBS.....",
    "...BSSBSSSBS....",
    "...BSSBSSSSB....",
    "...BBSSSSBB.....",
    ".....SSSSSS.....",
    "....RRSRRSR.....",
    "...RRRSRRRSRR...",
    "...SSRSSSRSS....",
    "....BBBBBB......",
    "....BB..BB......",
    "................"
]

S_MARIO_RUN3 = [
    "................",
    "................",
    "................",
    ".....RRRR.......",
    "....RRRRRRRR....",
    "....BBBSSBS.....",
    "...BSSBSSSBS....",
    "...BSSBSSSSB....",
    "...BBSSSSBB.....",
    ".....SSSSSS.....",
    "....BBRRRRR.....",
    "...BBBRRRRRS....",
    "......BBSSSS....",
    "........RRRR....",
    "........BBBBB...",
    "..........BBBB.."
]

S_MARIO_JUMP = [
    "................",
    "....BBB.........",
    ".....RRRR.......",
    "....RRRRRRRR....",
    "....BBBSSBS.....",
    "...BSSBSSSBS....",
    "...BSSBSSSSB....",
    "...BBSSSSBB.....",
    ".....SSSSS......",
    "...RRRRSRRBB....",
    "..RRRRRRRRBBB...",
    "..SSRRRRRBB.....",
    "..SSSSSSS.......",
    "....SSSS........",
    "...BB..BB.......",
    "..BBB..BBB......"
]

GOOMBA_PALETTE = {'B': C.E_BODY, 'D': C.E_DARK, 'W': C.WHITE, 'K': C.BLACK}

# Authentic SMB1 Goomba - mushroom shape with angry eyes
S_GOOMBA1 = [
    "................",
    "......BBBB......",
    "....BBBBBBBB....",
    "...BBBBBBBBBB...",
    "..BBBBBBBBBBBB..",
    "..BBWWBBBBWWBB..",
    "..BWKKBBBBKKWB..",
    "..BBKKBBBBKKBB..",
    "..BBBBBBBBBBBB..",
    "...BBBBBBBBBB...",
    "....BBBBBBBB....",
    ".....DDDDDD.....",
    "....DDDDDDDD....",
    "...DDD....DDD...",
    "..DDDD....DDDD..",
    "................"
]

S_GOOMBA2 = [
    "................",
    "......BBBB......",
    "....BBBBBBBB....",
    "...BBBBBBBBBB...",
    "..BBBBBBBBBBBB..",
    "..BBWWBBBBWWBB..",
    "..BWKKBBBBKKWB..",
    "..BBKKBBBBKKBB..",
    "..BBBBBBBBBBBB..",
    "...BBBBBBBBBB...",
    "....BBBBBBBB....",
    ".....DDDDDD.....",
    "....DDDDDDDD....",
    "....DDD..DDD....",
    "................",
    "................"
]

S_GOOMBA_FLAT = [
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "..BBBBBBBBBBBB..",
    "..BWKBBBBBBKWB..",
    "..BBBBBBBBBBBB..",
    "..DDDDDDDDDDDD..",
    "................"
]

KOOPA_PALETTE = {'G': C.PIPE_L, 'D': C.PIPE_D, 'H': C.PIPE_H, 'S': C.M_SKIN, 'K': C.BLACK, 'W': C.WHITE}

S_KOOPA1 = [
    ".......GGG......",
    "......GGGGG.....",
    ".....GGGGGGG....",
    "....GGGGGGGG....",
    "....GGHGGHGG....",
    "...GGGGGGGGGG...",
    "...GGGGGGGGG....",
    "....SSSS........",
    "...SSSSSS.......",
    "..GGSSSSGG......",
    ".GGGGGGGGGGG....",
    ".GGGGGGGGGGG....",
    "..GGGGGGGGG.....",
    "...DD...DD......",
    "..DDD...DDD.....",
    "................"
]

# Tile sprites
TILE_PALETTE = {
    'L': C.G_LIGHT, 'M': C.G_MID, 'D': C.G_DARK, 'S': C.G_SHADOW, 'B': C.BLACK,
    'Q': C.Q_LIGHT, 'W': C.Q_DARK, 'X': C.Q_SHADOW,
    'G': C.PIPE_L, 'P': C.PIPE_D, 'H': C.PIPE_H,
    'Y': C.COIN_I, 'O': C.COIN_O,
    'C': C.CASTLE, 'R': C.CASTLE_D, 'F': C.FLAG_GREEN,
    'K': C.BLACK, 'T': C.WHITE
}

TILE_GROUND = [
    "LLLLDDDDLLLLDDDD",
    "LLLLDDDDLLLLDDDD",
    "LLLLDDDDLLLLDDDD",
    "LLLLDDDDLLLLDDDD",
    "SSSSSSSSSSSSSSSS",
    "DDDDLLLLDDDDLLLL",
    "DDDDLLLLDDDDLLLL",
    "DDDDLLLLDDDDLLLL",
    "DDDDLLLLDDDDLLLL",
    "SSSSSSSSSSSSSSSS",
    "LLLLDDDDLLLLDDDD",
    "LLLLDDDDLLLLDDDD",
    "LLLLDDDDLLLLDDDD",
    "LLLLDDDDLLLLDDDD",
    "SSSSSSSSSSSSSSSS",
    "DDDDLLLLDDDDLLLL"
]

TILE_BRICK = [
    "LLMMDDLLMMDDLLMM",
    "LLMMDDLLMMDDLLMM",
    "BBBBBBBBBBBBBBBB",
    "MMDDLLMMDDLLMMDD",
    "MMDDLLMMDDLLMMDD",
    "BBBBBBBBBBBBBBBB",
    "LLMMDDLLMMDDLLMM",
    "LLMMDDLLMMDDLLMM",
    "BBBBBBBBBBBBBBBB",
    "MMDDLLMMDDLLMMDD",
    "MMDDLLMMDDLLMMDD",
    "BBBBBBBBBBBBBBBB",
    "LLMMDDLLMMDDLLMM",
    "LLMMDDLLMMDDLLMM",
    "BBBBBBBBBBBBBBBB",
    "MMDDLLMMDDLLMMDD"
]

TILE_QBLOCK = [
    "BQQQQQQQQQQQQQQB",
    "QWWWWWWWWWWWWWWX",
    "QWQQQQQQQQQQQQWX",
    "QWQQQQQWWQQQQQWX",
    "QWQQQQWQQWQQQQWX",
    "QWQQQQWQQWQQQQWX",
    "QWQQQQQWWQQQQQWX",
    "QWQQQQQQWQQQQQWX",
    "QWQQQQQQWQQQQQWX",
    "QWQQQQQQQQQQQQWX",
    "QWQQQQQQWQQQQQWX",
    "QWQQQQQQWQQQQQWX",
    "QWQQQQQQQQQQQQWX",
    "QWWWWWWWWWWWWWWX",
    "BXXXXXXXXXXXXXXB",
    "BBBBBBBBBBBBBBBB"
]

TILE_QBLOCK_OFF = [
    "BDDDDDDDDDDDDDDDB",
    "DSSSSSSSSSSSSSSDD",
    "DSDDDDDDDDDDDDSDD",
    "DSDDDDDDDDDDDDSDD",
    "DSDDDDDDDDDDDDSDD",
    "DSDDDDDDDDDDDDSDD",
    "DSDDDDDDDDDDDDSDD",
    "DSDDDDDDDDDDDDSDD",
    "DSDDDDDDDDDDDDSDD",
    "DSDDDDDDDDDDDDSDD",
    "DSDDDDDDDDDDDDSDD",
    "DSDDDDDDDDDDDDSDD",
    "DSDDDDDDDDDDDDSDD",
    "DSSSSSSSSSSSSSSDD",
    "BDDDDDDDDDDDDDDDB",
    "BBBBBBBBBBBBBBBB"
]

TILE_PIPE_TL = [
    "................",
    "......GGGGGGGPP.",
    ".....GHHHHHHHHPP",
    ".....GHGGGGGGPP.",
    ".....GHGGGGGGPP.",
    "......GGGGGGPPP.",
    "......GGGGGGGPP.",
    "......GHGGGGGPP.",
    "......GHGGGGGPP.",
    "......GHGGGGGPP.",
    "......GHGGGGGPP.",
    "......GHGGGGGPP.",
    "......GHGGGGGPP.",
    "......GHGGGGGPP.",
    "......GHGGGGGPP.",
    "......GHGGGGGPP."
]

TILE_PIPE_TR = [
    "................",
    ".PPGGGGGGG......",
    "PPHHHHHHHHG.....",
    ".PPGGGGGGHG.....",
    ".PPGGGGGGHG.....",
    ".PPPGGGGGG......",
    ".PPGGGGGGG......",
    ".PPGGGGGHG......",
    ".PPGGGGGHG......",
    ".PPGGGGGHG......",
    ".PPGGGGGHG......",
    ".PPGGGGGHG......",
    ".PPGGGGGHG......",
    ".PPGGGGGHG......",
    ".PPGGGGGHG......",
    ".PPGGGGGHG......"
]

TILE_PIPE_L = [
    "......GHGGGGGPP.",
    "......GHGGGGGPP.",
    "......GHGGGGGPP.",
    "......GHGGGGGPP.",
    "......GHGGGGGPP.",
    "......GHGGGGGPP.",
    "......GHGGGGGPP.",
    "......GHGGGGGPP.",
    "......GHGGGGGPP.",
    "......GHGGGGGPP.",
    "......GHGGGGGPP.",
    "......GHGGGGGPP.",
    "......GHGGGGGPP.",
    "......GHGGGGGPP.",
    "......GHGGGGGPP.",
    "......GHGGGGGPP."
]

TILE_PIPE_R = [
    ".PPGGGGGHG......",
    ".PPGGGGGHG......",
    ".PPGGGGGHG......",
    ".PPGGGGGHG......",
    ".PPGGGGGHG......",
    ".PPGGGGGHG......",
    ".PPGGGGGHG......",
    ".PPGGGGGHG......",
    ".PPGGGGGHG......",
    ".PPGGGGGHG......",
    ".PPGGGGGHG......",
    ".PPGGGGGHG......",
    ".PPGGGGGHG......",
    ".PPGGGGGHG......",
    ".PPGGGGGHG......",
    ".PPGGGGGHG......"
]

TILE_FLAG_POLE = [
    ".......KK.......",
    ".......KK.......",
    ".......KK.......",
    ".......KK.......",
    ".......KK.......",
    ".......KK.......",
    ".......KK.......",
    ".......KK.......",
    ".......KK.......",
    ".......KK.......",
    ".......KK.......",
    ".......KK.......",
    ".......KK.......",
    ".......KK.......",
    ".......KK.......",
    ".......KK......."
]

TILE_FLAG_TOP = [
    ".......KK.......",
    "......TTTT......",
    ".....TTTTTT.....",
    "....TTTTTTTT....",
    ".......KK.......",
    ".......KK.......",
    ".......KK.......",
    ".......KK.......",
    ".......KK.......",
    ".......KK.......",
    ".......KK.......",
    ".......KK.......",
    ".......KK.......",
    ".......KK.......",
    ".......KK.......",
    ".......KK......."
]

TILE_FLAG = [
    "......FFFFF.....",
    ".....FFFFFF.....",
    "....FFFFFFF.....",
    "...FFFFFFFF.....",
    "..FFFFFFFFF.....",
    ".FFFFFFFFFF.....",
    "..FFFFFFFFF.....",
    "...FFFFFFFF.....",
    "....FFFFFFF.....",
    ".....FFFFFF.....",
    "......FFFFF.....",
    "................",
    "................",
    "................",
    "................",
    "................"
]

TILE_CASTLE = [
    "..CC..CCCC..CC..",
    "..CC..CCCC..CC..",
    "CCCCCCCCCCCCCCCC",
    "CCCCCCCCCCCCCCCC",
    "CC..CC..CC..CCCC",
    "CC..CC..CC..CCCC",
    "CCCCCCCCCCCCCCCC",
    "CCCCCCCCCCCCCCCC",
    "CCRRRRRRRRRRRCC",
    "CCRRRRRRRRRRRCC",
    "CCRRRRRRRRRRRCC",
    "CCRRRRKKKRRRRCC",
    "CCRRRRKKKKRRRCC",
    "CCRRRRKKKKRRRCC",
    "CCRRRRKKKKRRRCC",
    "CCCCCCCCCCCCCCCC"
]

TILE_STAIR = [
    "LLLLDDDDLLLLDDDD",
    "LLLLDDDDLLLLDDDD",
    "LLLLDDDDLLLLDDDD",
    "LLLLDDDDLLLLDDDD",
    "LLLLDDDDLLLLDDDD",
    "LLLLDDDDLLLLDDDD",
    "LLLLDDDDLLLLDDDD",
    "LLLLDDDDLLLLDDDD",
    "LLLLDDDDLLLLDDDD",
    "LLLLDDDDLLLLDDDD",
    "LLLLDDDDLLLLDDDD",
    "LLLLDDDDLLLLDDDD",
    "LLLLDDDDLLLLDDDD",
    "LLLLDDDDLLLLDDDD",
    "LLLLDDDDLLLLDDDD",
    "LLLLDDDDLLLLDDDD"
]

S_COIN = [
    ".......OO.......",
    "......OYYO......",
    ".....OYYYYO.....",
    "....OYYOOYYO....",
    "....OYYYYYYO....",
    "....OYYYYYYO....",
    "....OYYYYYYO....",
    "....OYYYYYYO....",
    "....OYYYYYYO....",
    "....OYYYYYYO....",
    "....OYYOOYYO....",
    ".....OYYYYO.....",
    "......OYYO......",
    ".......OO.......",
    "................",
    "................"
]

S_MUSHROOM = [
    "......RRRRRR....",
    "....RRRRRRRRRR..",
    "...RWWRRRRRWWR..",
    "..RWWWRRRRRWWWR.",
    "..RWWWRRRRRWWWR.",
    ".RWWWWRRRRRWWWWR",
    ".RRRRRRRRRRRRRR.",
    "..RRRRRRRRRRRR..",
    ".....SSSSSS.....",
    "....SSSSSSSS....",
    "...SSSSSSSSSS...",
    "...SSSSSSSSSS...",
    "...SSSSSSSSSS...",
    "....SSSSSSSS....",
    "................",
    "................"
]

S_MUSHROOM_1UP = [
    "......GGGGGG....",
    "....GGGGGGGGGG..",
    "...GWWGGGGGGWWG.",
    "..GWWWGGGGGGWWWG",
    "..GWWWGGGGGGWWWG",
    ".GWWWWGGGGGGWWWWG",
    ".GGGGGGGGGGGGGG.",
    "..GGGGGGGGGGGG..",
    ".....SSSSSS.....",
    "....SSSSSSSS....",
    "...SSSSSSSSSS...",
    "...SSSSSSSSSS...",
    "...SSSSSSSSSS...",
    "....SSSSSSSS....",
    "................",
    "................"
]

S_FIREFLOWER = [
    "................",
    ".......GG.......",
    "......GWWG......",
    ".....GWWWWG.....",
    "....GOOOOOOOG...",
    "...GOWWOWWOOOG..",
    "...GOWWOWWOOOG..",
    "...GOOOOOOOOOG..",
    "....GOOOOOOOG...",
    "......GGGG......",
    ".......BB.......",
    ".......BB.......",
    "......BBBB......",
    ".....BBBBBB.....",
    "......BBBB......",
    "................"
]

S_STARMAN = [
    ".......YY.......",
    "......YYYY......",
    "......YYYY......",
    ".....YYYYYY.....",
    "YYYYYKKYYYYYYY..",
    ".YYYYKKKKYYYYY..",
    "..YYYKKKKKYYYY..",
    "..YYYYKKKKYYY...",
    "...YYYYYYYYYYY..",
    "...YYYYYYYYYY...",
    "....YYYYYYYY....",
    "....YYY.YYYY....",
    "...YYY...YYY....",
    "...YY.....YY....",
    "..YY.......YY...",
    "................"
]

MUSH_PALETTE = {'R': C.M_RED, 'W': C.WHITE, 'S': C.M_SKIN, 'G': C.PIPE_L}
FLOWER_PALETTE = {'G': C.PIPE_L, 'W': C.WHITE, 'O': C.COIN_O, 'B': C.G_MID}
STAR_PALETTE = {'Y': C.COIN_I, 'K': C.BLACK}

# ─────────────────────────────────────────────────────────────
# GRAPHICS ENGINE
# ─────────────────────────────────────────────────────────────
def create_sprite_surface(grid, palette):
    s = pygame.Surface((16 * NES_PIXEL, 16 * NES_PIXEL)).convert_alpha()
    s.fill((0,0,0,0))
    for r, row in enumerate(grid):
        for c, char in enumerate(row):
            if char in palette:
                pygame.draw.rect(s, palette[char], (c*NES_PIXEL, r*NES_PIXEL, NES_PIXEL, NES_PIXEL))
    return s

class Assets:
    def __init__(self):
        self.mario_stand = create_sprite_surface(S_MARIO_STAND, MARIO_PALETTE)
        self.mario_run1 = create_sprite_surface(S_MARIO_RUN1, MARIO_PALETTE)
        self.mario_run2 = create_sprite_surface(S_MARIO_RUN2, MARIO_PALETTE)
        self.mario_run3 = create_sprite_surface(S_MARIO_RUN3, MARIO_PALETTE)
        self.mario_jump = create_sprite_surface(S_MARIO_JUMP, MARIO_PALETTE)
        
        self.goomba1 = create_sprite_surface(S_GOOMBA1, GOOMBA_PALETTE)
        self.goomba2 = create_sprite_surface(S_GOOMBA2, GOOMBA_PALETTE)
        self.goomba_flat = create_sprite_surface(S_GOOMBA_FLAT, GOOMBA_PALETTE)
        
        self.koopa1 = create_sprite_surface(S_KOOPA1, KOOPA_PALETTE)
        
        self.tile_ground = create_sprite_surface(TILE_GROUND, TILE_PALETTE)
        self.tile_brick = create_sprite_surface(TILE_BRICK, TILE_PALETTE)
        self.tile_q = create_sprite_surface(TILE_QBLOCK, TILE_PALETTE)
        self.tile_q_off = create_sprite_surface(TILE_QBLOCK_OFF, TILE_PALETTE)
        self.tile_stair = create_sprite_surface(TILE_STAIR, TILE_PALETTE)
        
        self.pipe_tl = create_sprite_surface(TILE_PIPE_TL, TILE_PALETTE)
        self.pipe_tr = create_sprite_surface(TILE_PIPE_TR, TILE_PALETTE)
        self.pipe_l = create_sprite_surface(TILE_PIPE_L, TILE_PALETTE)
        self.pipe_r = create_sprite_surface(TILE_PIPE_R, TILE_PALETTE)
        
        self.flag_pole = create_sprite_surface(TILE_FLAG_POLE, TILE_PALETTE)
        self.flag_top = create_sprite_surface(TILE_FLAG_TOP, TILE_PALETTE)
        self.flag = create_sprite_surface(TILE_FLAG, TILE_PALETTE)
        self.castle = create_sprite_surface(TILE_CASTLE, TILE_PALETTE)
        
        self.coin = create_sprite_surface(S_COIN, TILE_PALETTE)
        self.mushroom = create_sprite_surface(S_MUSHROOM, MUSH_PALETTE)
        self.mushroom_1up = create_sprite_surface(S_MUSHROOM_1UP, MUSH_PALETTE)
        self.fireflower = create_sprite_surface(S_FIREFLOWER, FLOWER_PALETTE)
        self.starman = create_sprite_surface(S_STARMAN, STAR_PALETTE)

GFX = None

# ─────────────────────────────────────────────────────────────
# TILE TYPES
# ─────────────────────────────────────────────────────────────
class Tile(Enum):
    AIR = 0
    GROUND = 1
    BRICK = 2
    QBLOCK = 3          # Contains coin
    QBLOCK_EMPTY = 4
    PIPE_TL = 5
    PIPE_TR = 6
    PIPE_L = 7
    PIPE_R = 8
    STAIR = 9
    FLAG_POLE = 10
    FLAG_TOP = 11
    CASTLE = 12
    COIN = 13
    QBLOCK_MUSH = 14    # Contains mushroom/fireflower
    QBLOCK_STAR = 15    # Contains starman
    QBLOCK_1UP = 16     # Contains 1-up

SOLID_TILES = {Tile.GROUND, Tile.BRICK, Tile.QBLOCK, Tile.QBLOCK_EMPTY, 
               Tile.PIPE_TL, Tile.PIPE_TR, Tile.PIPE_L, Tile.PIPE_R, Tile.STAIR,
               Tile.QBLOCK_MUSH, Tile.QBLOCK_STAR, Tile.QBLOCK_1UP}

# ─────────────────────────────────────────────────────────────
# AUTHENTIC SMB WORLD 1-1 LEVEL DATA
# Each row: (tile_type, x, y) or special structure markers
# Ground level = row 12-13 (0-indexed, 15 rows total)
# ─────────────────────────────────────────────────────────────

def create_world_1_1():
    """Creates authentic Super Mario Bros World 1-1 layout."""
    W = 224  # Level width in tiles
    H = 15
    FLOOR_Y = 13
    
    grid = [[Tile.AIR for _ in range(W)] for _ in range(H)]
    enemies = []
    
    # Helper functions
    def set_tile(x, y, t):
        if 0 <= x < W and 0 <= y < H:
            grid[y][x] = t
    
    def fill_floor(start, end):
        for x in range(start, end):
            set_tile(x, FLOOR_Y, Tile.GROUND)
            set_tile(x, FLOOR_Y+1, Tile.GROUND)
    
    def place_pipe(x, height):
        """Place a pipe at x with given height (1-4 tiles)"""
        base_y = FLOOR_Y - 1
        # Top
        set_tile(x, base_y - height + 1, Tile.PIPE_TL)
        set_tile(x+1, base_y - height + 1, Tile.PIPE_TR)
        # Body
        for h in range(height - 1):
            set_tile(x, base_y - h, Tile.PIPE_L)
            set_tile(x+1, base_y - h, Tile.PIPE_R)
    
    def place_block_row(x, y, length, tile_type):
        for i in range(length):
            set_tile(x + i, y, tile_type)
    
    def place_stair(x, height, direction=1):
        """Build stairs. direction: 1=ascending right, -1=ascending left"""
        for i in range(height):
            col = x + (i * direction) if direction > 0 else x - i
            for j in range(i + 1):
                set_tile(col, FLOOR_Y - 1 - j, Tile.STAIR)
    
    # === BUILD WORLD 1-1 ===
    
    # Initial floor section (tiles 0-68)
    fill_floor(0, 69)
    
    # First ? block with MUSHROOM (x=16) - the iconic first powerup
    set_tile(16, 9, Tile.QBLOCK_MUSH)
    
    # First brick-?-brick-?-brick-? row (x=20-24)
    set_tile(20, 9, Tile.BRICK)
    set_tile(21, 9, Tile.QBLOCK)      # Coin
    set_tile(22, 9, Tile.QBLOCK_MUSH) # Mushroom
    set_tile(23, 9, Tile.QBLOCK)      # Coin
    set_tile(24, 9, Tile.BRICK)
    
    # ? block above (x=22) - coin
    set_tile(22, 5, Tile.QBLOCK)
    
    # First pipe (x=28, height 2) - short pipe
    place_pipe(28, 2)
    
    # Second pipe (x=38, height 2)
    place_pipe(38, 2)
    
    # Third pipe (x=46, height 3)
    place_pipe(46, 3)
    
    # Fourth pipe (x=57, height 3)
    place_pipe(57, 3)
    
    # Gap 1 (tiles 69-70)
    # (floor already not filled here)
    
    # Floor continues (tiles 71-85)
    fill_floor(71, 86)
    
    # Brick row with hidden 1-up (x=77-79)
    set_tile(77, 9, Tile.BRICK)
    set_tile(78, 9, Tile.QBLOCK_1UP)  # Hidden 1-up in original
    set_tile(79, 9, Tile.BRICK)
    
    # High brick row (x=80-87)
    for i in range(8):
        set_tile(80 + i, 5, Tile.BRICK)
    
    # Gap 2 (tiles 86-88)
    
    # Floor continues (tiles 89-152)
    fill_floor(89, 153)
    
    # ? blocks (x=91) - coins
    set_tile(91, 9, Tile.QBLOCK)
    set_tile(94, 9, Tile.BRICK)
    
    # Ground ? blocks with powerup (x=100-101)
    set_tile(100, 9, Tile.QBLOCK_MUSH)  # Mushroom
    set_tile(101, 9, Tile.QBLOCK)       # Coin
    
    # Floating coins above (authentic SMB1 placement)
    set_tile(100, 5, Tile.COIN)
    set_tile(101, 5, Tile.COIN)
    set_tile(102, 5, Tile.COIN)
    
    # Brick row (x=106-108)
    set_tile(106, 9, Tile.BRICK)
    set_tile(107, 5, Tile.BRICK)
    set_tile(108, 5, Tile.BRICK)
    set_tile(109, 5, Tile.QBLOCK_STAR)  # STARMAN!
    set_tile(106, 5, Tile.BRICK)
    
    # Higher bricks (x=109-111)
    set_tile(109, 9, Tile.BRICK)
    set_tile(110, 9, Tile.QBLOCK)
    set_tile(111, 9, Tile.BRICK)
    
    # More bricks (x=118-121)
    set_tile(118, 5, Tile.BRICK)
    set_tile(119, 5, Tile.BRICK)
    set_tile(120, 5, Tile.BRICK)
    set_tile(121, 5, Tile.QBLOCK)
    set_tile(122, 5, Tile.BRICK)
    
    # Lower brick row
    set_tile(128, 9, Tile.BRICK)
    set_tile(129, 9, Tile.BRICK)
    set_tile(130, 5, Tile.QBLOCK)
    set_tile(131, 5, Tile.QBLOCK)
    set_tile(129, 5, Tile.BRICK)
    
    # Pipe (x=163)
    place_pipe(163, 2)
    
    # Gap 3 (tiles 153-154)
    
    # Floor (tiles 155-end)
    fill_floor(155, W)
    
    # Brick row (x=168-170)
    set_tile(168, 9, Tile.BRICK)
    set_tile(169, 9, Tile.BRICK)
    set_tile(170, 9, Tile.QBLOCK)
    set_tile(171, 9, Tile.BRICK)
    
    # Staircase 1 - ascending (x=134)
    for i in range(4):
        for j in range(i + 1):
            set_tile(134 + i, FLOOR_Y - 1 - j, Tile.STAIR)
    
    # Staircase 1 - descending
    for i in range(4):
        for j in range(4 - i):
            set_tile(140 + i, FLOOR_Y - j, Tile.STAIR)
    
    # Staircase 2 - ascending (x=148)
    for i in range(4):
        for j in range(i + 1):
            set_tile(148 + i, FLOOR_Y - 1 - j, Tile.STAIR)
    
    # Gap after staircase 2
    grid[FLOOR_Y][152] = Tile.AIR
    grid[FLOOR_Y+1][152] = Tile.AIR
    
    # Staircase 2 - descending (x=155-158)
    for i in range(4):
        for j in range(4 - i):
            set_tile(155 + i, FLOOR_Y - j, Tile.STAIR)
    
    # Pre-final staircase (x=181-188)
    for i in range(8):
        for j in range(i + 1):
            set_tile(181 + i, FLOOR_Y - 1 - j, Tile.STAIR)
    
    # Final staircase (x=189)
    for j in range(8):
        set_tile(189, FLOOR_Y - 1 - j, Tile.STAIR)
    
    # Flagpole (x=198)
    set_tile(198, 4, Tile.FLAG_TOP)
    for y in range(5, FLOOR_Y):
        set_tile(198, y, Tile.FLAG_POLE)
    
    # Castle (x=202-206) - just ground blocks for simplicity
    for i in range(5):
        for j in range(4):
            set_tile(202 + i, FLOOR_Y - 1 - j, Tile.GROUND)
    set_tile(204, FLOOR_Y - 5, Tile.GROUND)  # Castle top
    
    # === ENEMIES (Authentic 1-1 positions) ===
    
    # Goomba 1 (near start)
    enemies.append(Goomba(22 * TILE_SIZE, (FLOOR_Y - 1) * TILE_SIZE))
    
    # Goomba 2 (after first pipe)
    enemies.append(Goomba(40 * TILE_SIZE, (FLOOR_Y - 1) * TILE_SIZE))
    
    # Goomba pair (before gap)
    enemies.append(Goomba(51 * TILE_SIZE, (FLOOR_Y - 1) * TILE_SIZE))
    enemies.append(Goomba(53 * TILE_SIZE, (FLOOR_Y - 1) * TILE_SIZE))
    
    # Goombas in middle section
    enemies.append(Goomba(80 * TILE_SIZE, (FLOOR_Y - 1) * TILE_SIZE))
    enemies.append(Goomba(82 * TILE_SIZE, (FLOOR_Y - 1) * TILE_SIZE))
    
    # Goombas near stairs
    enemies.append(Goomba(97 * TILE_SIZE, (FLOOR_Y - 1) * TILE_SIZE))
    enemies.append(Goomba(99 * TILE_SIZE, (FLOOR_Y - 1) * TILE_SIZE))
    
    # Goomba pair before final section
    enemies.append(Goomba(114 * TILE_SIZE, (FLOOR_Y - 1) * TILE_SIZE))
    enemies.append(Goomba(116 * TILE_SIZE, (FLOOR_Y - 1) * TILE_SIZE))
    
    # Final goombas
    enemies.append(Goomba(124 * TILE_SIZE, (FLOOR_Y - 1) * TILE_SIZE))
    enemies.append(Goomba(126 * TILE_SIZE, (FLOOR_Y - 1) * TILE_SIZE))
    enemies.append(Goomba(128 * TILE_SIZE, (FLOOR_Y - 1) * TILE_SIZE))
    enemies.append(Goomba(130 * TILE_SIZE, (FLOOR_Y - 1) * TILE_SIZE))
    
    return grid, enemies

# ─────────────────────────────────────────────────────────────
# ENTITIES
# ─────────────────────────────────────────────────────────────

class Entity:
    def __init__(self, x, y, w, h):
        self.x, self.y = float(x), float(y)
        self.w, self.h = w, h
        self.vx, self.vy = 0.0, 0.0
        self.dead = False
        self.rect = pygame.Rect(x, y, w, h)

    def update_rect(self):
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

class Goomba(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, TILE_SIZE - 4*NES_PIXEL, TILE_SIZE)
        self.vx = -0.8 * NES_PIXEL
        self.frame = 0
        self.stomped = False
        self.stomp_timer = 0
        self.activated = False

    def update(self, grid, cam_x):
        if self.dead: 
            return
        
        # Only activate when on screen
        if not self.activated:
            if self.x < cam_x + SCREEN_W + TILE_SIZE * 2:
                self.activated = True
            else:
                return
        
        if self.stomped:
            self.stomp_timer += 1
            if self.stomp_timer > 30:
                self.dead = True
            return
            
        self.vy += GRAVITY
        if self.vy > MAX_FALL: 
            self.vy = MAX_FALL
        
        self.x += self.vx
        self.update_rect()
        self.collide_x(grid)
        
        self.y += self.vy
        self.update_rect()
        self.collide_y(grid)
        
        self.frame += 0.15
        
        if self.y > SCREEN_H + 64: 
            self.dead = True

    def collide_x(self, grid):
        tx1 = int(self.rect.left // TILE_SIZE)
        tx2 = int(self.rect.right // TILE_SIZE)
        ty1 = int(self.rect.top // TILE_SIZE)
        ty2 = int((self.rect.bottom - 1) // TILE_SIZE)
        
        if tx1 < 0 or tx2 >= len(grid[0]):
            self.vx *= -1
            return
        if ty1 < 0 or ty2 >= len(grid):
            return
            
        for ty in range(ty1, ty2 + 1):
            if self.vx < 0 and tx1 >= 0 and grid[ty][tx1] in SOLID_TILES:
                self.x = (tx1 + 1) * TILE_SIZE
                self.vx *= -1
                break
            if self.vx > 0 and tx2 < len(grid[0]) and grid[ty][tx2] in SOLID_TILES:
                self.x = tx2 * TILE_SIZE - self.w
                self.vx *= -1
                break

    def collide_y(self, grid):
        tx = int((self.x + self.w/2) // TILE_SIZE)
        ty2 = int(self.rect.bottom // TILE_SIZE)
        
        if tx < 0 or tx >= len(grid[0]) or ty2 >= len(grid):
            return
        if grid[ty2][tx] in SOLID_TILES:
            self.y = ty2 * TILE_SIZE - self.h
            self.vy = 0
            self.update_rect()

    def stomp(self):
        self.stomped = True
        self.vx = 0

    def draw(self, surf, cam_x):
        if self.dead:
            return
        
        draw_x = self.x - cam_x - 2*NES_PIXEL
        
        if self.stomped:
            surf.blit(GFX.goomba_flat, (draw_x, self.y + 8*NES_PIXEL))
        else:
            frame = GFX.goomba1 if int(self.frame) % 2 == 0 else GFX.goomba2
            surf.blit(frame, (draw_x, self.y))

class Mushroom(Entity):
    def __init__(self, x, y, is_1up=False):
        super().__init__(x, y, TILE_SIZE, TILE_SIZE)
        self.vx = 1.5 * NES_PIXEL
        self.emerging = True
        self.emerge_y = y
        self.target_y = y - TILE_SIZE
        self.is_1up = is_1up

    def update(self, grid):
        if self.dead:
            return
            
        if self.emerging:
            self.y -= 0.5 * NES_PIXEL
            if self.y <= self.target_y:
                self.y = self.target_y
                self.emerging = False
            self.update_rect()
            return
        
        self.vy += GRAVITY
        if self.vy > MAX_FALL:
            self.vy = MAX_FALL
        
        self.x += self.vx
        self.update_rect()
        self.collide_x(grid)
        
        self.y += self.vy
        self.update_rect()
        self.collide_y(grid)
        
        if self.y > SCREEN_H + 64:
            self.dead = True

    def collide_x(self, grid):
        tx1 = int(self.rect.left // TILE_SIZE)
        tx2 = int(self.rect.right // TILE_SIZE)
        ty1 = int(self.rect.top // TILE_SIZE)
        ty2 = int((self.rect.bottom - 1) // TILE_SIZE)
        
        if tx1 < 0 or tx2 >= len(grid[0]):
            self.vx *= -1
            return
            
        for ty in range(ty1, ty2 + 1):
            if ty < 0 or ty >= len(grid):
                continue
            if self.vx > 0 and grid[ty][tx2] in SOLID_TILES:
                self.vx *= -1
                break
            if self.vx < 0 and grid[ty][tx1] in SOLID_TILES:
                self.vx *= -1
                break

    def collide_y(self, grid):
        tx = int((self.x + self.w/2) // TILE_SIZE)
        ty2 = int(self.rect.bottom // TILE_SIZE)
        
        if tx < 0 or tx >= len(grid[0]) or ty2 >= len(grid):
            return
        if grid[ty2][tx] in SOLID_TILES:
            self.y = ty2 * TILE_SIZE - self.h
            self.vy = 0
            self.update_rect()

    def draw(self, surf, cam_x):
        if not self.dead:
            sprite = GFX.mushroom_1up if self.is_1up else GFX.mushroom
            surf.blit(sprite, (self.x - cam_x, self.y))


class FireFlower(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, TILE_SIZE, TILE_SIZE)
        self.emerging = True
        self.emerge_y = y
        self.target_y = y - TILE_SIZE
        self.anim_frame = 0

    def update(self, grid):
        if self.dead:
            return
            
        if self.emerging:
            self.y -= 0.5 * NES_PIXEL
            if self.y <= self.target_y:
                self.y = self.target_y
                self.emerging = False
            self.update_rect()
        
        self.anim_frame += 0.1

    def draw(self, surf, cam_x):
        if not self.dead:
            surf.blit(GFX.fireflower, (self.x - cam_x, self.y))


class Starman(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, TILE_SIZE, TILE_SIZE)
        self.vx = 2.0 * NES_PIXEL
        self.vy = -3.0 * NES_PIXEL
        self.emerging = True
        self.emerge_y = y
        self.target_y = y - TILE_SIZE
        self.anim_frame = 0

    def update(self, grid):
        if self.dead:
            return
            
        if self.emerging:
            self.y -= 0.5 * NES_PIXEL
            if self.y <= self.target_y:
                self.y = self.target_y
                self.emerging = False
                self.vy = -4.0 * NES_PIXEL
            self.update_rect()
            return
        
        # Starman bounces!
        self.vy += GRAVITY
        if self.vy > MAX_FALL:
            self.vy = MAX_FALL
        
        self.x += self.vx
        self.update_rect()
        self.collide_x(grid)
        
        self.y += self.vy
        self.update_rect()
        self.collide_y(grid)
        
        self.anim_frame += 0.2
        
        if self.y > SCREEN_H + 64:
            self.dead = True

    def collide_x(self, grid):
        tx1 = int(self.rect.left // TILE_SIZE)
        tx2 = int(self.rect.right // TILE_SIZE)
        ty1 = int(self.rect.top // TILE_SIZE)
        ty2 = int((self.rect.bottom - 1) // TILE_SIZE)
        
        if tx1 < 0 or tx2 >= len(grid[0]):
            self.vx *= -1
            return
            
        for ty in range(ty1, ty2 + 1):
            if ty < 0 or ty >= len(grid):
                continue
            if self.vx > 0 and grid[ty][tx2] in SOLID_TILES:
                self.vx *= -1
                break
            if self.vx < 0 and grid[ty][tx1] in SOLID_TILES:
                self.vx *= -1
                break

    def collide_y(self, grid):
        tx = int((self.x + self.w/2) // TILE_SIZE)
        ty2 = int(self.rect.bottom // TILE_SIZE)
        
        if tx < 0 or tx >= len(grid[0]) or ty2 >= len(grid):
            return
        if grid[ty2][tx] in SOLID_TILES:
            self.y = ty2 * TILE_SIZE - self.h
            self.vy = -4.0 * NES_PIXEL  # Bounce!
            self.update_rect()

    def draw(self, surf, cam_x):
        if not self.dead:
            # Flicker colors for star effect
            surf.blit(GFX.starman, (self.x - cam_x, self.y))


class FloatingCoin(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, TILE_SIZE, TILE_SIZE)
        self.anim_frame = 0
        self.collected = False

    def update(self):
        self.anim_frame += 0.15

    def draw(self, surf, cam_x):
        if not self.dead and not self.collected:
            surf.blit(GFX.coin, (self.x - cam_x, self.y))

class BrickParticle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = (2 - 4 * (x % 2)) * NES_PIXEL
        self.vy = -4 * NES_PIXEL * (1 + (y % 2) * 0.5)
        self.dead = False
        self.size = 4 * NES_PIXEL

    def update(self):
        self.vy += GRAVITY * 0.5
        self.x += self.vx
        self.y += self.vy
        if self.y > SCREEN_H:
            self.dead = True

    def draw(self, surf, cam_x):
        if not self.dead:
            pygame.draw.rect(surf, C.G_MID, (self.x - cam_x, self.y, self.size, self.size))

class CoinPopup:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.start_y = y
        self.vy = -4 * NES_PIXEL
        self.dead = False
        self.frame = 0

    def update(self):
        self.y += self.vy
        self.vy += GRAVITY * 0.3
        self.frame += 0.3
        if self.y > self.start_y:
            self.dead = True

    def draw(self, surf, cam_x):
        if not self.dead:
            surf.blit(GFX.coin, (self.x - cam_x, self.y))

class ScorePopup:
    def __init__(self, x, y, score):
        self.x = x
        self.y = y
        self.score = score
        self.timer = 0
        self.dead = False

    def update(self):
        self.y -= 1 * NES_PIXEL
        self.timer += 1
        if self.timer > 30:
            self.dead = True

    def draw(self, surf, cam_x, font):
        if not self.dead:
            text = font.render(str(self.score), True, C.WHITE)
            surf.blit(text, (self.x - cam_x, self.y))

class Mario(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 10 * NES_PIXEL, 14 * NES_PIXEL)
        self.grounded = False
        self.facing_right = True
        self.anim_timer = 0
        self.score = 0
        self.coins = 0
        self.lives = 3
        self.big = False
        self.fire_power = False
        self.invincible = 0
        self.star_power = 0
        self.jump_held = False
        self.finished = False
        self.finish_timer = 0

    def update(self, keys, grid, particles, popups, items):
        if self.finished:
            self.finish_timer += 1
            return
            
        if self.invincible > 0:
            self.invincible -= 1
        
        if self.star_power > 0:
            self.star_power -= 1
        
        # Running
        running = keys[pygame.K_LSHIFT] or keys[pygame.K_x]
        accel = RUN_ACCEL if running else WALK_ACCEL
        max_speed = MAX_RUN if running else MAX_WALK
        
        # Input
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx -= accel
            self.facing_right = False
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx += accel
            self.facing_right = True
        else:
            if self.grounded:
                self.vx *= FRICTION
            else:
                self.vx *= AIR_FRICTION
        
        # Clamp speed
        if abs(self.vx) < 0.05 * NES_PIXEL:
            self.vx = 0
        if self.vx > max_speed:
            self.vx = max_speed
        if self.vx < -max_speed:
            self.vx = -max_speed
        
        # Jump - variable height based on hold duration
        jump_pressed = keys[pygame.K_SPACE] or keys[pygame.K_z]
        if jump_pressed and self.grounded and not self.jump_held:
            self.vy = JUMP_FORCE
            self.grounded = False
            self.jump_held = True
        
        if not jump_pressed:
            self.jump_held = False
            # Cut jump short if released early
            if self.vy < -2 * NES_PIXEL:
                self.vy = -2 * NES_PIXEL
        
        # Gravity
        self.vy += GRAVITY
        if self.vy > MAX_FALL:
            self.vy = MAX_FALL
        
        # Movement and collision
        self.grounded = False
        
        self.x += self.vx
        if self.x < 0:
            self.x = 0
        self.update_rect()
        self.handle_collision(grid, True, particles, popups, items)
        
        self.y += self.vy
        self.update_rect()
        self.handle_collision(grid, False, particles, popups, items)
        
        # Fall death
        if self.y > SCREEN_H:
            self.dead = True

    def handle_collision(self, grid, x_axis, particles, popups, items):
        start_x = max(0, int(self.rect.left // TILE_SIZE))
        end_x = min(len(grid[0])-1, int(self.rect.right // TILE_SIZE))
        start_y = max(0, int(self.rect.top // TILE_SIZE))
        end_y = min(len(grid)-1, int(self.rect.bottom // TILE_SIZE))
        
        for y in range(start_y, end_y + 1):
            for x in range(start_x, end_x + 1):
                t = grid[y][x]
                if t in SOLID_TILES:
                    tile_rect = pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    if self.rect.colliderect(tile_rect):
                        if x_axis:
                            if self.vx > 0:
                                self.rect.right = tile_rect.left
                            elif self.vx < 0:
                                self.rect.left = tile_rect.right
                            self.x = float(self.rect.x)
                            self.vx = 0
                        else:
                            if self.vy > 0:
                                self.rect.bottom = tile_rect.top
                                self.grounded = True
                            elif self.vy < 0:
                                self.rect.top = tile_rect.bottom
                                # Block hit
                                self.hit_block(grid, x, y, t, particles, popups, items)
                            self.y = float(self.rect.y)
                            self.vy = 0

    def hit_block(self, grid, x, y, t, particles, popups, items):
        if t == Tile.QBLOCK:
            grid[y][x] = Tile.QBLOCK_EMPTY
            self.coins += 1
            self.score += 200
            popups.append(CoinPopup(x * TILE_SIZE, (y-1) * TILE_SIZE))
            popups.append(ScorePopup(x * TILE_SIZE, (y-1) * TILE_SIZE, 200))
        elif t == Tile.QBLOCK_MUSH:
            grid[y][x] = Tile.QBLOCK_EMPTY
            # Spawn mushroom if small, fire flower if big
            if self.big:
                items.append(FireFlower(x * TILE_SIZE, y * TILE_SIZE))
            else:
                items.append(Mushroom(x * TILE_SIZE, y * TILE_SIZE))
        elif t == Tile.QBLOCK_STAR:
            grid[y][x] = Tile.QBLOCK_EMPTY
            items.append(Starman(x * TILE_SIZE, y * TILE_SIZE))
        elif t == Tile.QBLOCK_1UP:
            grid[y][x] = Tile.QBLOCK_EMPTY
            items.append(Mushroom(x * TILE_SIZE, y * TILE_SIZE, is_1up=True))
        elif t == Tile.BRICK:
            if self.big:
                grid[y][x] = Tile.AIR
                self.score += 50
                # Spawn brick particles
                for i in range(4):
                    px = x * TILE_SIZE + (i % 2) * 8 * NES_PIXEL
                    py = y * TILE_SIZE + (i // 2) * 8 * NES_PIXEL
                    particles.append(BrickParticle(px, py))
            else:
                # Bump animation could go here
                self.score += 10

    def draw(self, surf, cam_x):
        if self.finished and self.finish_timer > 120:
            return
            
        # Invincibility flicker
        if self.invincible > 0 and (self.invincible // 3) % 2 == 0:
            return
        
        draw_x = self.x - cam_x - (3 * NES_PIXEL) 
        draw_y = self.y - (2 * NES_PIXEL)
        
        # Select sprite
        if not self.grounded:
            sprite = GFX.mario_jump
        elif abs(self.vx) > 0.2 * NES_PIXEL:
            self.anim_timer += abs(self.vx) * 0.15
            frame = int(self.anim_timer) % 3
            if frame == 0:
                sprite = GFX.mario_run1
            elif frame == 1:
                sprite = GFX.mario_run2
            else:
                sprite = GFX.mario_run3
        else:
            sprite = GFX.mario_stand
        
        if not self.facing_right:
            sprite = pygame.transform.flip(sprite, True, False)
        
        # Star power rainbow effect
        if self.star_power > 0:
            # Create color-shifted copy
            temp = sprite.copy()
            colors = [(255,0,0), (0,255,0), (0,0,255), (255,255,0), (255,0,255), (0,255,255)]
            color = colors[(self.star_power // 4) % len(colors)]
            temp.fill(color, special_flags=pygame.BLEND_ADD)
            surf.blit(temp, (draw_x, draw_y))
        else:
            surf.blit(sprite, (draw_x, draw_y))

# ─────────────────────────────────────────────────────────────
# GAME STATES
# ─────────────────────────────────────────────────────────────
class GameState(Enum):
    TITLE = 0
    MENU = 1
    PLAYING = 2
    GAME_OVER = 3
    LEVEL_CLEAR = 4
    OPTIONS = 5

# ─────────────────────────────────────────────────────────────
# MENU SPRITES
# ─────────────────────────────────────────────────────────────
S_MARIO_SMALL_ICON = [
    "....RRRR....",
    "...RRRRRR...",
    "...BBBSSB...",
    "..BSSBSSBS..",
    "..BSSBSSSB..",
    "..BBSSSSBB..",
    "....SSSSS...",
    "...RRSRRS...",
    "..RRRSSRRR..",
    "..SSRSSRSS..",
    "..SSSSSSSS..",
    "...BB.BB....",
    "..BBB.BBB...",
    "............"
]

S_MUSHROOM_ICON = [
    "....RRRR....",
    "...RRRRRR...",
    "..RWWRRWWR..",
    "..RWWRRWWR..",
    ".RWWWRRWWWR.",
    ".RRRRRRRRRR.",
    "..RRRRRRRR..",
    "....SSSS....",
    "...SSSSSS...",
    "...SSSSSS...",
    "....SSSS....",
    "............",
    "............",
    "............"
]

S_CURSOR = [
    "R...........",
    "RR..........",
    "RRR.........",
    "RRRR........",
    "RRRRR.......",
    "RRRRRR......",
    "RRRRRRR.....",
    "RRRRRR......",
    "RRRRR.......",
    "RRRR........",
    "RRR.........",
    "RR..........",
    "R...........",
    "............"
]

# Logo letters - "SUPER" and "MARIO BROS"
LOGO_PALETTE = {'R': C.M_RED, 'W': C.WHITE, 'Y': C.COIN_I, 'B': C.BLACK, 'O': C.COIN_O}

# ─────────────────────────────────────────────────────────────
# GAME
# ─────────────────────────────────────────────────────────────

class Game:
    def __init__(self):
        global GFX
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        self.clock = pygame.time.Clock()
        GFX = Assets()
        self.font = pygame.font.Font(None, int(16 * NES_PIXEL))
        self.small_font = pygame.font.Font(None, int(12 * NES_PIXEL))
        self.title_font = pygame.font.Font(None, int(24 * NES_PIXEL))
        
        # Menu sprites
        self.cursor_sprite = create_sprite_surface(S_CURSOR, MARIO_PALETTE)
        self.mario_icon = create_sprite_surface(S_MARIO_SMALL_ICON, MARIO_PALETTE)
        self.mush_icon = create_sprite_surface(S_MUSHROOM_ICON, MUSH_PALETTE)
        
        # Game state
        self.state = GameState.TITLE
        self.menu_selection = 0
        self.menu_options = ["GAME START", "OPTIONS", "SCORE RANKING"]
        self.options_selection = 0
        self.options_items = ["SOUND: ON", "MUSIC: ON", "LIVES: 3", "BACK"]
        self.sound_on = True
        self.music_on = True
        self.start_lives = 3
        
        # Title screen animation
        self.title_timer = 0
        self.title_blink = True
        self.demo_timer = 0
        
        # High scores
        self.high_scores = [
            ("SAMSOFT", 50000),
            ("MARIO", 30000),
            ("LUIGI", 20000),
            ("PEACH", 10000),
            ("TOAD", 5000),
        ]
        
        self.key_delay = 0
        self.reset_level()

    def reset_level(self):
        self.grid, self.enemies = create_world_1_1()
        self.mario = Mario(3 * TILE_SIZE, 11 * TILE_SIZE)
        self.mario.lives = self.start_lives
        self.cam_x = 0
        self.target_cam = 0
        self.game_over = False
        self.particles = []
        self.popups = []
        self.items = []
        self.time = 400
        self.time_tick = 0
        self.flag_y = 4 * TILE_SIZE
        self.world = 1
        self.stage = 1

    def draw_title_screen(self):
        """Draw SMB Deluxe style title screen"""
        self.screen.fill((0, 0, 0))  # Black background like GBC
        
        self.title_timer += 1
        if self.title_timer % 30 == 0:
            self.title_blink = not self.title_blink
        
        # Draw decorative top border
        pygame.draw.rect(self.screen, C.M_RED, (0, 0, SCREEN_W, 8 * NES_PIXEL))
        pygame.draw.rect(self.screen, C.COIN_I, (0, 8 * NES_PIXEL, SCREEN_W, 2 * NES_PIXEL))
        
        # "ULTRA" text - exciting and yellow
        ultra_text = self.title_font.render("ULTRA", True, C.COIN_I)
        self.screen.blit(ultra_text, (SCREEN_W//2 - ultra_text.get_width()//2, 28 * NES_PIXEL))
        
        # "MARIO 2D BROS" title - big and red
        title1 = self.title_font.render("MARIO 2D BROS", True, C.M_RED)
        shadow1 = self.title_font.render("MARIO 2D BROS", True, C.BLACK)
        self.screen.blit(shadow1, (SCREEN_W//2 - title1.get_width()//2 + 2, 48 * NES_PIXEL + 2))
        self.screen.blit(title1, (SCREEN_W//2 - title1.get_width()//2, 48 * NES_PIXEL))
        
        # Draw Mario icon
        mario_x = SCREEN_W//2 - 40 * NES_PIXEL
        mario_y = 85 * NES_PIXEL
        # Animate Mario bobbing
        bob = int(2 * NES_PIXEL * (1 if (self.title_timer // 15) % 2 == 0 else 0))
        self.screen.blit(self.mario_icon, (mario_x, mario_y + bob))
        
        # Draw mushroom icon
        mush_x = SCREEN_W//2 + 25 * NES_PIXEL
        self.screen.blit(self.mush_icon, (mush_x, mario_y))
        
        # "PRESS START" blinking text
        if self.title_blink:
            start_text = self.font.render("PRESS ENTER", True, C.WHITE)
            self.screen.blit(start_text, (SCREEN_W//2 - start_text.get_width()//2, 125 * NES_PIXEL))
        
        # Copyright - Samsoft and Nintendo
        copy_text1 = self.small_font.render("[C] SAMSOFT 2026", True, C.WHITE)
        self.screen.blit(copy_text1, (SCREEN_W//2 - copy_text1.get_width()//2, 150 * NES_PIXEL))
        
        copy_text2 = self.small_font.render("[C] 1985 NINTENDO", True, C.WHITE)
        self.screen.blit(copy_text2, (SCREEN_W//2 - copy_text2.get_width()//2, 162 * NES_PIXEL))
        
        # Draw bottom border
        pygame.draw.rect(self.screen, C.COIN_I, (0, SCREEN_H - 10 * NES_PIXEL, SCREEN_W, 2 * NES_PIXEL))
        pygame.draw.rect(self.screen, C.M_RED, (0, SCREEN_H - 8 * NES_PIXEL, SCREEN_W, 8 * NES_PIXEL))

    def draw_main_menu(self):
        """Draw SMB Deluxe style main menu"""
        self.screen.fill((0, 0, 48))  # Dark blue background
        
        # Top decorative area with ground tiles
        for x in range(0, SCREEN_W, TILE_SIZE):
            self.screen.blit(GFX.tile_ground, (x, SCREEN_H - TILE_SIZE * 2))
            self.screen.blit(GFX.tile_ground, (x, SCREEN_H - TILE_SIZE))
        
        # Draw pipe decoration
        self.screen.blit(GFX.pipe_tl, (20 * NES_PIXEL, SCREEN_H - TILE_SIZE * 4))
        self.screen.blit(GFX.pipe_tr, (20 * NES_PIXEL + TILE_SIZE, SCREEN_H - TILE_SIZE * 4))
        self.screen.blit(GFX.pipe_l, (20 * NES_PIXEL, SCREEN_H - TILE_SIZE * 3))
        self.screen.blit(GFX.pipe_r, (20 * NES_PIXEL + TILE_SIZE, SCREEN_H - TILE_SIZE * 3))
        
        # Right side pipe
        self.screen.blit(GFX.pipe_tl, (SCREEN_W - 70 * NES_PIXEL, SCREEN_H - TILE_SIZE * 4))
        self.screen.blit(GFX.pipe_tr, (SCREEN_W - 70 * NES_PIXEL + TILE_SIZE, SCREEN_H - TILE_SIZE * 4))
        self.screen.blit(GFX.pipe_l, (SCREEN_W - 70 * NES_PIXEL, SCREEN_H - TILE_SIZE * 3))
        self.screen.blit(GFX.pipe_r, (SCREEN_W - 70 * NES_PIXEL + TILE_SIZE, SCREEN_H - TILE_SIZE * 3))
        
        # Title at top
        ultra = self.font.render("ULTRA MARIO 2D BROS", True, C.COIN_I)
        self.screen.blit(ultra, (SCREEN_W//2 - ultra.get_width()//2, 15 * NES_PIXEL))
        
        copy1 = self.small_font.render("[C] SAMSOFT 2026  [C] 1985 NINTENDO", True, C.WHITE)
        self.screen.blit(copy1, (SCREEN_W//2 - copy1.get_width()//2, 32 * NES_PIXEL))
        
        # Menu box
        box_x = 50 * NES_PIXEL
        box_y = 48 * NES_PIXEL
        box_w = SCREEN_W - 100 * NES_PIXEL
        box_h = 80 * NES_PIXEL
        
        # Box border
        pygame.draw.rect(self.screen, C.WHITE, (box_x, box_y, box_w, box_h), 2)
        pygame.draw.rect(self.screen, (0, 0, 80), (box_x + 2, box_y + 2, box_w - 4, box_h - 4))
