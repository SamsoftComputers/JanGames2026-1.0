#!/usr/bin/env python3
"""
Mariofan Builder 0.1
(C) Samsoft

A complete SMBX 1.3.0.1 style level editor and game engine
Inspired by Super Mario Bros. X 2.0
"""

import pygame
import json
import sys
import os
import math
import copy
import random
import time
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any

pygame.init()
pygame.mixer.init()

# --- Constants ---
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
TOOLBAR_HEIGHT = 140
GRID_SIZE = 32
FPS = 60
VERSION = "0.1"
TITLE = "Mariofan Builder"
COPYRIGHT = "(C) Samsoft"

# Physics Constants (SMBX 1.3 accurate)
GRAVITY = 0.4
MAX_FALL_SPEED = 12
JUMP_FORCE = -10.5
JUMP_HOLD_GRAVITY = 0.2
ACCEL_GROUND = 0.15
ACCEL_AIR = 0.1
FRICTION = 0.1
MAX_WALK_SPEED = 3.5
MAX_RUN_SPEED = 6.0
PMETER_MAX = 100
PMETER_CHARGE = 2
PMETER_DECAY = 1

# Colors - SMBX Classic Palette
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (192, 192, 192)
DARK_GRAY = (64, 64, 64)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 128, 0)
BROWN = (139, 69, 19)
PINK = (255, 192, 203)

# SMBX Menu Colors
MENU_BG_TOP = (0, 0, 48)
MENU_BG_BOTTOM = (0, 0, 96)
MENU_PANEL = (32, 32, 96)
MENU_PANEL_LIGHT = (48, 48, 128)
MENU_BORDER = (128, 128, 192)
MENU_HIGHLIGHT = (255, 255, 128)
MENU_TEXT = (255, 255, 255)
MENU_TEXT_SHADOW = (0, 0, 64)
MENU_SELECTED = (255, 220, 64)
MENU_DISABLED = (128, 128, 128)

# Editor Colors
EDITOR_BG = (64, 64, 80)
EDITOR_TOOLBAR = (32, 32, 48)
EDITOR_GRID = (80, 80, 100)
EDITOR_SELECTION = (255, 255, 0)

# Game Background Colors
SKY_BLUE = (92, 148, 252)
SKY_NIGHT = (0, 0, 48)
UNDERGROUND_BG = (0, 0, 0)
CASTLE_BG = (32, 32, 32)
WATER_BG = (0, 64, 128)

# --- Enums ---
class GameState(Enum):
    MAIN_MENU = 0
    EPISODE_SELECT = 1
    BATTLE_MODE = 2
    EDITOR_MENU = 3
    EDITOR = 4
    PLAY = 5
    OPTIONS = 6
    CREDITS = 7
    WORLD_MAP = 8
    PAUSE = 9

class Layer(Enum):
    BACKGROUND_2 = 0
    BACKGROUND = 1
    MAIN = 2
    FOREGROUND = 3
    FOREGROUND_2 = 4

class EditorMode(Enum):
    BLOCKS = 0
    BGOS = 1
    NPCS = 2
    WARPS = 3
    WATER = 4
    LAYERS = 5
    EVENTS = 6
    SECTION = 7
    LEVEL = 8

class PowerState(Enum):
    SMALL = 0
    BIG = 1
    FIRE = 2
    LEAF = 3
    TANOOKI = 4
    HAMMER = 5
    ICE = 6

class Direction(Enum):
    LEFT = 0
    RIGHT = 1
    UP = 2
    DOWN = 3

# --- Setup ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(f"{TITLE} {VERSION}")
clock = pygame.time.Clock()

# Fonts - SMBX Style
try:
    font_tiny = pygame.font.SysFont("consolas", 10)
    font_small = pygame.font.SysFont("consolas", 12)
    font_medium = pygame.font.SysFont("consolas", 16)
    font_large = pygame.font.SysFont("consolas", 24)
    font_title = pygame.font.SysFont("consolas", 32, bold=True)
    font_huge = pygame.font.SysFont("consolas", 48, bold=True)
except:
    font_tiny = pygame.font.Font(None, 12)
    font_small = pygame.font.Font(None, 14)
    font_medium = pygame.font.Font(None, 18)
    font_large = pygame.font.Font(None, 28)
    font_title = pygame.font.Font(None, 36)
    font_huge = pygame.font.Font(None, 52)

# --- Utility Functions ---
def draw_gradient(surface, rect, color1, color2, vertical=True):
    """Draw a gradient rectangle"""
    x, y, w, h = rect
    for i in range(h if vertical else w):
        ratio = i / (h if vertical else w)
        r = int(color1[0] + (color2[0] - color1[0]) * ratio)
        g = int(color1[1] + (color2[1] - color1[1]) * ratio)
        b = int(color1[2] + (color2[2] - color1[2]) * ratio)
        if vertical:
            pygame.draw.line(surface, (r, g, b), (x, y + i), (x + w, y + i))
        else:
            pygame.draw.line(surface, (r, g, b), (x + i, y), (x + i, y + h))

def draw_text_shadow(surface, text, pos, font, color=WHITE, shadow_color=BLACK, offset=2):
    """Draw text with shadow"""
    shadow = font.render(text, True, shadow_color)
    surface.blit(shadow, (pos[0] + offset, pos[1] + offset))
    txt = font.render(text, True, color)
    surface.blit(txt, pos)

def draw_panel(surface, rect, selected=False, style="default"):
    """Draw an SMBX-style panel"""
    x, y, w, h = rect
    # Shadow
    pygame.draw.rect(surface, (0, 0, 32), (x + 4, y + 4, w, h))
    # Main panel
    if style == "default":
        draw_gradient(surface, rect, MENU_PANEL_LIGHT, MENU_PANEL)
    elif style == "dark":
        draw_gradient(surface, rect, DARK_GRAY, (32, 32, 32))
    elif style == "light":
        draw_gradient(surface, rect, LIGHT_GRAY, GRAY)
    # Border
    border_color = MENU_SELECTED if selected else MENU_BORDER
    pygame.draw.rect(surface, border_color, rect, 2)
    # Highlight
    pygame.draw.line(surface, (min(255, MENU_PANEL_LIGHT[0] + 40), 
                               min(255, MENU_PANEL_LIGHT[1] + 40),
                               min(255, MENU_PANEL_LIGHT[2] + 40)), 
                     (x + 2, y + 2), (x + w - 3, y + 2))
    pygame.draw.line(surface, (min(255, MENU_PANEL_LIGHT[0] + 40),
                               min(255, MENU_PANEL_LIGHT[1] + 40),
                               min(255, MENU_PANEL_LIGHT[2] + 40)), 
                     (x + 2, y + 2), (x + 2, y + h - 3))

def draw_stars(surface, scroll_offset, star_count=80):
    """Draw twinkling stars for menu background"""
    random.seed(12345)
    for i in range(star_count):
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(0, SCREEN_HEIGHT - 100)
        base_bright = random.randint(100, 200)
        twinkle = int(math.sin(time.time() * 2 + i * 0.5) * 50)
        brightness = max(50, min(255, base_bright + twinkle))
        size = random.randint(1, 2)
        pygame.draw.circle(surface, (brightness, brightness, brightness), 
                          ((x + int(scroll_offset * 0.05)) % SCREEN_WIDTH, y), size)

def draw_menu_background(surface, scroll_offset=0):
    """Draw the SMBX-style menu background"""
    draw_gradient(surface, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), MENU_BG_TOP, MENU_BG_BOTTOM)
    draw_stars(surface, scroll_offset)
    # Ground decoration
    ground_y = SCREEN_HEIGHT - 64
    pygame.draw.rect(surface, (64, 128, 64), (0, ground_y, SCREEN_WIDTH, 64))
    pygame.draw.rect(surface, (96, 160, 96), (0, ground_y, SCREEN_WIDTH, 8))
    # Simple grass tufts
    for i in range(0, SCREEN_WIDTH, 32):
        x = (i + int(scroll_offset * 0.1)) % SCREEN_WIDTH
        pygame.draw.polygon(surface, (64, 160, 64), 
                           [(x, ground_y), (x + 8, ground_y - 12), (x + 16, ground_y)])

# --- Data Classes ---
@dataclass
class Episode:
    name: str
    folder: str
    description: str = ""
    author: str = "Unknown"
    version: str = "1.0"
    credits: str = ""
    world_map: str = ""
    intro_level: str = ""
    no_pause: bool = False
    stars_total: int = 0
    
    def to_dict(self):
        return {
            "name": self.name,
            "folder": self.folder,
            "description": self.description,
            "author": self.author,
            "version": self.version,
            "credits": self.credits,
            "world_map": self.world_map,
            "intro_level": self.intro_level,
            "no_pause": self.no_pause,
            "stars_total": self.stars_total
        }
    
    @staticmethod
    def from_dict(data):
        return Episode(**data)

@dataclass 
class LevelSettings:
    name: str = "Untitled Level"
    width: int = 6400
    height: int = 1200
    music: int = 0
    background: int = 1
    wrap_h: bool = False
    wrap_v: bool = False
    no_turn_back: bool = False
    underwater: bool = False
    star_count: int = 0
    sections: List[Dict] = field(default_factory=lambda: [{
        "x": 0, "y": 0, "width": 6400, "height": 600,
        "music": 0, "background": 1, "wrap_h": False, "wrap_v": False
    }])
    player_start: Tuple[int, int] = (200, 400)
    
    def to_dict(self):
        return {
            "name": self.name,
            "width": self.width,
            "height": self.height,
            "music": self.music,
            "background": self.background,
            "wrap_h": self.wrap_h,
            "wrap_v": self.wrap_v,
            "no_turn_back": self.no_turn_back,
            "underwater": self.underwater,
            "star_count": self.star_count,
            "sections": self.sections,
            "player_start": list(self.player_start)
        }

# --- Block Definitions (SMBX 1.3 IDs) ---
BLOCK_DATA = {
    # SMB1 Blocks
    1: {"name": "Brick (SMB1)", "color": (165, 82, 41), "sizable": False, "semisolid": False},
    2: {"name": "Stone (SMB1)", "color": (128, 128, 128), "sizable": False, "semisolid": False},
    3: {"name": "Wood", "color": (139, 90, 43), "sizable": False, "semisolid": False},
    4: {"name": "Question Block", "color": (255, 200, 64), "sizable": False, "semisolid": False, "content": True},
    5: {"name": "Question Block (Used)", "color": (128, 96, 32), "sizable": False, "semisolid": False},
    # SMB3 Blocks
    6: {"name": "Brick (SMB3)", "color": (198, 99, 49), "sizable": False, "semisolid": False},
    7: {"name": "Wood Block (SMB3)", "color": (156, 107, 49), "sizable": False, "semisolid": False},
    8: {"name": "Ice Block", "color": (192, 224, 255), "sizable": False, "semisolid": False},
    9: {"name": "Bouncy Note", "color": (255, 128, 160), "sizable": False, "semisolid": False},
    10: {"name": "Coin Block", "color": (255, 192, 64), "sizable": False, "semisolid": False},
    # SMW Blocks
    11: {"name": "Turn Block", "color": (192, 192, 64), "sizable": False, "semisolid": False},
    12: {"name": "Switch Block (Yellow)", "color": (255, 255, 0), "sizable": False, "semisolid": False},
    13: {"name": "Switch Block (Green)", "color": (0, 255, 0), "sizable": False, "semisolid": False},
    14: {"name": "Switch Block (Blue)", "color": (0, 128, 255), "sizable": False, "semisolid": False},
    15: {"name": "Switch Block (Red)", "color": (255, 0, 0), "sizable": False, "semisolid": False},
    # Terrain
    16: {"name": "Grass Top", "color": (64, 192, 64), "sizable": False, "semisolid": True},
    17: {"name": "Grass Fill", "color": (139, 90, 43), "sizable": True, "semisolid": False},
    18: {"name": "Stone Fill", "color": (96, 96, 96), "sizable": True, "semisolid": False},
    19: {"name": "Underground Fill", "color": (64, 64, 128), "sizable": True, "semisolid": False},
    20: {"name": "Castle Fill", "color": (80, 80, 80), "sizable": True, "semisolid": False},
    # Slopes
    21: {"name": "Slope Up Left", "color": (100, 180, 100), "sizable": False, "semisolid": False, "slope": True},
    22: {"name": "Slope Up Right", "color": (100, 180, 100), "sizable": False, "semisolid": False, "slope": True},
    # Pipes
    23: {"name": "Pipe Top L", "color": (0, 200, 0), "sizable": False, "semisolid": False},
    24: {"name": "Pipe Top R", "color": (0, 200, 0), "sizable": False, "semisolid": False},
    25: {"name": "Pipe Body L", "color": (0, 160, 0), "sizable": False, "semisolid": False},
    26: {"name": "Pipe Body R", "color": (0, 160, 0), "sizable": False, "semisolid": False},
    # Special
    27: {"name": "Invisible Block", "color": (255, 255, 255, 128), "sizable": False, "semisolid": False, "invisible": True},
    28: {"name": "Spike", "color": (192, 192, 192), "sizable": False, "semisolid": False, "hurt": True},
    29: {"name": "Lava", "color": (255, 64, 0), "sizable": True, "semisolid": False, "hurt": True},
    30: {"name": "Donut Block", "color": (200, 160, 120), "sizable": False, "semisolid": True, "donut": True},
}

# --- NPC Definitions (SMBX 1.3 IDs) ---
NPC_DATA = {
    # Enemies - Goombas
    1: {"name": "Goomba", "color": (139, 69, 19), "width": 32, "height": 32, "score": 100},
    2: {"name": "Red Goomba", "color": (178, 34, 34), "width": 32, "height": 32, "score": 100},
    3: {"name": "Flying Goomba", "color": (139, 69, 19), "width": 40, "height": 40, "score": 200},
    # Enemies - Koopas
    4: {"name": "Green Koopa", "color": (0, 128, 0), "width": 32, "height": 48, "score": 100},
    5: {"name": "Red Koopa", "color": (200, 0, 0), "width": 32, "height": 48, "score": 100},
    6: {"name": "Green Shell", "color": (0, 160, 0), "width": 32, "height": 32, "score": 0},
    7: {"name": "Red Shell", "color": (200, 0, 0), "width": 32, "height": 32, "score": 0},
    8: {"name": "Green Para-Koopa", "color": (0, 128, 0), "width": 32, "height": 48, "score": 200},
    9: {"name": "Red Para-Koopa", "color": (200, 0, 0), "width": 32, "height": 48, "score": 200},
    # Enemies - Piranha Plants
    10: {"name": "Piranha Plant", "color": (0, 100, 0), "width": 32, "height": 48, "score": 100},
    11: {"name": "Fire Piranha", "color": (200, 50, 0), "width": 32, "height": 48, "score": 200},
    # Enemies - Buzzy Beetle
    12: {"name": "Buzzy Beetle", "color": (32, 32, 96), "width": 32, "height": 32, "score": 100},
    13: {"name": "Buzzy Shell", "color": (32, 32, 96), "width": 32, "height": 28, "score": 0},
    # Enemies - Spinies
    14: {"name": "Spiny", "color": (200, 0, 0), "width": 32, "height": 32, "score": 100},
    15: {"name": "Spiny Egg", "color": (0, 128, 0), "width": 16, "height": 16, "score": 0},
    # Enemies - Lakitu
    16: {"name": "Lakitu", "color": (0, 128, 0), "width": 32, "height": 48, "score": 200},
    # Enemies - Cheep Cheeps
    17: {"name": "Red Cheep", "color": (255, 64, 64), "width": 32, "height": 32, "score": 200},
    18: {"name": "Green Cheep", "color": (64, 200, 64), "width": 32, "height": 32, "score": 200},
    # Enemies - Bloopers
    19: {"name": "Blooper", "color": (255, 255, 255), "width": 32, "height": 48, "score": 200},
    # Enemies - Hammer Bros
    20: {"name": "Hammer Bro", "color": (0, 128, 0), "width": 32, "height": 48, "score": 1000},
    # Enemies - Bullet Bills
    21: {"name": "Bullet Bill", "color": (32, 32, 32), "width": 32, "height": 28, "score": 200},
    22: {"name": "Bill Blaster", "color": (32, 32, 32), "width": 32, "height": 64, "score": 0},
    # Enemies - Bob-ombs
    23: {"name": "Bob-omb", "color": (32, 32, 32), "width": 28, "height": 32, "score": 100},
    # Enemies - Thwomps
    24: {"name": "Thwomp", "color": (128, 128, 160), "width": 48, "height": 64, "score": 0},
    # Enemies - Boos
    25: {"name": "Boo", "color": (255, 255, 255), "width": 32, "height": 32, "score": 100},
    # Enemies - Dry Bones
    26: {"name": "Dry Bones", "color": (224, 224, 224), "width": 32, "height": 48, "score": 100},
    # Powerups
    27: {"name": "Mushroom", "color": (255, 64, 64), "width": 32, "height": 32, "score": 1000, "powerup": True},
    28: {"name": "Fire Flower", "color": (255, 128, 0), "width": 32, "height": 32, "score": 1000, "powerup": True},
    29: {"name": "Super Leaf", "color": (200, 100, 50), "width": 32, "height": 32, "score": 1000, "powerup": True},
    30: {"name": "Tanooki Suit", "color": (160, 82, 45), "width": 32, "height": 32, "score": 1000, "powerup": True},
    31: {"name": "Hammer Suit", "color": (32, 32, 32), "width": 32, "height": 32, "score": 1000, "powerup": True},
    32: {"name": "Ice Flower", "color": (128, 192, 255), "width": 32, "height": 32, "score": 1000, "powerup": True},
    33: {"name": "1-Up Mushroom", "color": (64, 200, 64), "width": 32, "height": 32, "score": 0, "powerup": True},
    34: {"name": "Poison Mushroom", "color": (128, 0, 128), "width": 32, "height": 32, "score": 0, "powerup": True},
    35: {"name": "Star", "color": (255, 255, 0), "width": 32, "height": 32, "score": 1000, "powerup": True},
    # Coins
    36: {"name": "Coin", "color": (255, 200, 0), "width": 32, "height": 32, "score": 0, "coin": True},
    # Goal
    37: {"name": "SMB3 Card", "color": (255, 200, 128), "width": 32, "height": 32, "score": 0, "goal": True},
    38: {"name": "SMW Goal Tape", "color": (255, 255, 255), "width": 16, "height": 256, "score": 0, "goal": True},
    39: {"name": "SMB1 Axe", "color": (192, 128, 64), "width": 32, "height": 48, "score": 0, "goal": True},
    # Platforms
    40: {"name": "Moving Platform", "color": (128, 64, 0), "width": 96, "height": 16, "score": 0, "platform": True},
    # Yoshi
    41: {"name": "Green Yoshi", "color": (0, 200, 0), "width": 32, "height": 32, "score": 0, "yoshi": True},
    42: {"name": "Blue Yoshi", "color": (0, 0, 200), "width": 32, "height": 32, "score": 0, "yoshi": True},
    43: {"name": "Yellow Yoshi", "color": (200, 200, 0), "width": 32, "height": 32, "score": 0, "yoshi": True},
    44: {"name": "Red Yoshi", "color": (200, 0, 0), "width": 32, "height": 32, "score": 0, "yoshi": True},
}

# --- BGO Definitions ---
BGO_DATA = {
    1: {"name": "Bush", "color": (64, 160, 64), "width": 64, "height": 32},
    2: {"name": "Small Bush", "color": (64, 160, 64), "width": 32, "height": 32},
    3: {"name": "Cloud", "color": (255, 255, 255), "width": 64, "height": 32},
    4: {"name": "Large Cloud", "color": (255, 255, 255), "width": 96, "height": 48},
    5: {"name": "Hill", "color": (64, 128, 64), "width": 128, "height": 64},
    6: {"name": "Fence", "color": (139, 69, 19), "width": 32, "height": 32},
    7: {"name": "Tree", "color": (34, 139, 34), "width": 64, "height": 96},
    8: {"name": "Castle", "color": (128, 128, 128), "width": 160, "height": 160},
    9: {"name": "Flag Pole", "color": (0, 128, 0), "width": 16, "height": 160},
    10: {"name": "Water Surface", "color": (64, 128, 255), "width": 32, "height": 32},
}

# --- Game Objects ---
class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.zoom = 1.0
        self.target = None
        self.section_bounds = None
        
    def update(self, keys, mouse_buttons, mouse_pos, editor_mode=False):
        if editor_mode:
            speed = 12 / self.zoom
            if keys[pygame.K_a] or keys[pygame.K_LEFT]: self.x -= speed
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]: self.x += speed
            if keys[pygame.K_w] or keys[pygame.K_UP]: self.y -= speed
            if keys[pygame.K_s] or keys[pygame.K_DOWN]: self.y += speed
            if mouse_buttons[2]:
                rel = pygame.mouse.get_rel()
                self.x -= rel[0] / self.zoom
                self.y -= rel[1] / self.zoom
            else:
                pygame.mouse.get_rel()
        elif self.target:
            target_x = self.target.rect.centerx - SCREEN_WIDTH / (2 * self.zoom)
            target_y = self.target.rect.centery - SCREEN_HEIGHT / (2 * self.zoom)
            self.x += (target_x - self.x) * 0.15
            self.y += (target_y - self.y) * 0.15
            if self.section_bounds:
                bx, by, bw, bh = self.section_bounds
                self.x = max(bx, min(self.x, bx + bw - SCREEN_WIDTH / self.zoom))
                self.y = max(by, min(self.y, by + bh - SCREEN_HEIGHT / self.zoom))
    
    def world_to_screen(self, pos):
        return (int((pos[0] - self.x) * self.zoom), int((pos[1] - self.y) * self.zoom))
    
    def screen_to_world(self, pos):
        return (pos[0] / self.zoom + self.x, pos[1] / self.zoom + self.y)
    
    def set_zoom(self, zoom):
        self.zoom = max(0.25, min(4.0, zoom))

class Block:
    def __init__(self, x, y, id, layer=Layer.MAIN):
        self.x = x
        self.y = y
        self.id = id
        self.layer = layer
        data = BLOCK_DATA.get(id, {"name": "Unknown", "color": MAGENTA, "sizable": False, "semisolid": False})
        self.width = GRID_SIZE
        self.height = GRID_SIZE
        self.color = data["color"]
        self.name = data["name"]
        self.semisolid = data.get("semisolid", False)
        self.hurt = data.get("hurt", False)
        self.slope = data.get("slope", False)
        self.invisible = data.get("invisible", False)
        self.content = data.get("content", False)
        self.content_id = 0
        self.rect = pygame.Rect(x, y, self.width, self.height)
    
    def update_rect(self):
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw(self, surface, camera, selected=False, show_invisible=True):
        screen_pos = camera.world_to_screen((self.x, self.y))
        w = int(self.width * camera.zoom)
        h = int(self.height * camera.zoom)
        if screen_pos[0] > SCREEN_WIDTH or screen_pos[0] + w < 0 or screen_pos[1] > SCREEN_HEIGHT or screen_pos[1] + h < 0:
            return
        rect = pygame.Rect(screen_pos[0], screen_pos[1], w, h)
        if self.invisible and not show_invisible:
            return
        alpha = 128 if self.invisible else 255
        color = self.color[:3] if len(self.color) == 4 else self.color
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(surf, (*color, alpha), (0, 0, w, h))
        # Add detail based on block type
        if self.id == 4:  # Question block
            txt = font_medium.render("?", True, BLACK)
            txt_rect = txt.get_rect(center=(w//2, h//2))
            surf.blit(txt, txt_rect)
        elif self.id in [23, 24, 25, 26]:  # Pipes
            pygame.draw.rect(surf, (0, 255, 0), (0, 0, w, h), 2)
        elif self.slope:
            pygame.draw.polygon(surf, color, [(0, h), (w, h), (w if self.id == 21 else 0, 0)])
        pygame.draw.rect(surf, (color[0]//2, color[1]//2, color[2]//2), (0, 0, w, h), 1)
        surface.blit(surf, screen_pos)
        if selected:
            pygame.draw.rect(surface, EDITOR_SELECTION, rect, 2)
    
    def to_dict(self):
        return {"x": self.x, "y": self.y, "id": self.id, "layer": self.layer.value, 
                "width": self.width, "height": self.height, "content_id": self.content_id}
    
    @staticmethod
    def from_dict(data):
        b = Block(data["x"], data["y"], data["id"], Layer(data.get("layer", 2)))
        b.width = data.get("width", GRID_SIZE)
        b.height = data.get("height", GRID_SIZE)
        b.content_id = data.get("content_id", 0)
        b.update_rect()
        return b

class BGO:
    def __init__(self, x, y, id, layer=Layer.BACKGROUND):
        self.x = x
        self.y = y
        self.id = id
        self.layer = layer
        data = BGO_DATA.get(id, {"name": "Unknown", "color": GRAY, "width": 32, "height": 32})
        self.width = data["width"]
        self.height = data["height"]
        self.color = data["color"]
        self.name = data["name"]
        self.rect = pygame.Rect(x, y, self.width, self.height)
    
    def draw(self, surface, camera, selected=False):
        screen_pos = camera.world_to_screen((self.x, self.y))
        w = int(self.width * camera.zoom)
        h = int(self.height * camera.zoom)
        if screen_pos[0] > SCREEN_WIDTH or screen_pos[0] + w < 0 or screen_pos[1] > SCREEN_HEIGHT or screen_pos[1] + h < 0:
            return
        rect = pygame.Rect(screen_pos[0], screen_pos[1], w, h)
        pygame.draw.rect(surface, self.color, rect)
        pygame.draw.rect(surface, (self.color[0]//2, self.color[1]//2, self.color[2]//2), rect, 1)
        if selected:
            pygame.draw.rect(surface, EDITOR_SELECTION, rect, 2)
    
    def to_dict(self):
        return {"x": self.x, "y": self.y, "id": self.id, "layer": self.layer.value}
    
    @staticmethod
    def from_dict(data):
        return BGO(data["x"], data["y"], data["id"], Layer(data.get("layer", 1)))

class NPC:
    def __init__(self, x, y, id):
        self.x = x
        self.y = y
        self.id = id
        data = NPC_DATA.get(id, {"name": "Unknown", "color": MAGENTA, "width": 32, "height": 32, "score": 0})
        self.width = data["width"]
        self.height = data["height"]
        self.color = data["color"]
        self.name = data["name"]
        self.score = data.get("score", 0)
        self.is_powerup = data.get("powerup", False)
        self.is_coin = data.get("coin", False)
        self.is_goal = data.get("goal", False)
        self.is_yoshi = data.get("yoshi", False)
        self.is_platform = data.get("platform", False)
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.vel_x = -1.5 if not (self.is_powerup or self.is_coin or self.is_goal) else 0
        self.vel_y = 0
        self.on_ground = False
        self.direction = Direction.LEFT
        self.active = True
        self.generator = False
        self.generator_delay = 60
        self.message = ""
        self.talk_npc = False
        self.friendly = False
    
    def update_rect(self):
        self.rect = pygame.Rect(int(self.x), int(self.y), self.width, self.height)
    
    def update(self, tiles, npcs):
        if not self.active or self.talk_npc or self.friendly:
            return
        # Gravity
        self.vel_y = min(self.vel_y + GRAVITY, MAX_FALL_SPEED)
        # Move
        self.x += self.vel_x
        self.y += self.vel_y
        self.update_rect()
        # Collision
        self.on_ground = False
        for tile in tiles:
            if tile.layer != Layer.MAIN:
                continue
            if self.rect.colliderect(tile.rect):
                # Horizontal
                if self.vel_x > 0 and self.rect.right > tile.rect.left and self.rect.left < tile.rect.left:
                    self.rect.right = tile.rect.left
                    self.x = self.rect.x
                    self.vel_x = -abs(self.vel_x)
                    self.direction = Direction.LEFT
                elif self.vel_x < 0 and self.rect.left < tile.rect.right and self.rect.right > tile.rect.right:
                    self.rect.left = tile.rect.right
                    self.x = self.rect.x
                    self.vel_x = abs(self.vel_x)
                    self.direction = Direction.RIGHT
                # Vertical
                if self.vel_y > 0:
                    overlap = self.rect.bottom - tile.rect.top
                    if 0 < overlap < 16:
                        self.rect.bottom = tile.rect.top
                        self.y = self.rect.y
                        self.vel_y = 0
                        self.on_ground = True
    
    def draw(self, surface, camera, selected=False):
        screen_pos = camera.world_to_screen((self.x, self.y))
        w = int(self.width * camera.zoom)
        h = int(self.height * camera.zoom)
        if screen_pos[0] > SCREEN_WIDTH or screen_pos[0] + w < 0 or screen_pos[1] > SCREEN_HEIGHT or screen_pos[1] + h < 0:
            return
        rect = pygame.Rect(screen_pos[0], screen_pos[1], w, h)
        # Draw based on NPC type
        if self.id in [1, 2, 3]:  # Goombas
            pygame.draw.ellipse(surface, self.color, rect)
            # Feet
            pygame.draw.ellipse(surface, (80, 40, 0), (rect.x + 2, rect.bottom - 8, w//3, 8))
            pygame.draw.ellipse(surface, (80, 40, 0), (rect.right - w//3 - 2, rect.bottom - 8, w//3, 8))
        elif self.id in [4, 5, 8, 9]:  # Koopas
            pygame.draw.ellipse(surface, self.color, (rect.x, rect.y, w, h * 2 // 3))
            pygame.draw.ellipse(surface, (200, 180, 100), (rect.x + 4, rect.bottom - h//2, w - 8, h//2))
        elif self.id in [36]:  # Coin
            pygame.draw.ellipse(surface, YELLOW, rect)
            pygame.draw.ellipse(surface, (200, 150, 0), rect, 2)
        elif self.id in [27, 33, 34]:  # Mushrooms
            pygame.draw.ellipse(surface, self.color, (rect.x, rect.y, w, h * 2 // 3))
            pygame.draw.rect(surface, (255, 220, 180), (rect.x + w//4, rect.y + h//2, w//2, h//2))
        elif self.id in [28, 32]:  # Flowers
            pygame.draw.circle(surface, self.color, rect.center, w//2)
            pygame.draw.circle(surface, YELLOW, rect.center, w//4)
        elif self.id == 35:  # Star
            self.draw_star(surface, rect.center, w//2)
        else:
            pygame.draw.rect(surface, self.color, rect)
        pygame.draw.rect(surface, (self.color[0]//2, self.color[1]//2, self.color[2]//2), rect, 1)
        if selected:
            pygame.draw.rect(surface, EDITOR_SELECTION, rect, 2)
    
    def draw_star(self, surface, center, size):
        points = []
        for i in range(5):
            angle = math.radians(i * 144 - 90)
            points.append((center[0] + size * math.cos(angle), center[1] + size * math.sin(angle)))
        pygame.draw.polygon(surface, YELLOW, points)
    
    def to_dict(self):
        return {"x": self.x, "y": self.y, "id": self.id, "direction": self.direction.value,
                "generator": self.generator, "generator_delay": self.generator_delay,
                "message": self.message, "friendly": self.friendly}
    
    @staticmethod
    def from_dict(data):
        n = NPC(data["x"], data["y"], data["id"])
        n.direction = Direction(data.get("direction", 0))
        n.generator = data.get("generator", False)
        n.generator_delay = data.get("generator_delay", 60)
        n.message = data.get("message", "")
        n.friendly = data.get("friendly", False)
        if n.direction == Direction.RIGHT:
            n.vel_x = abs(n.vel_x)
        return n

class Warp:
    def __init__(self, x, y, direction=Direction.DOWN):
        self.x = x
        self.y = y
        self.width = GRID_SIZE * 2
        self.height = GRID_SIZE * 2
        self.direction = direction
        self.warp_to_x = 0
        self.warp_to_y = 0
        self.warp_to_level = ""
        self.warp_to_section = 0
        self.exit_direction = Direction.UP
        self.locked = False
        self.stars_required = 0
        self.rect = pygame.Rect(x, y, self.width, self.height)
    
    def draw(self, surface, camera, selected=False):
        screen_pos = camera.world_to_screen((self.x, self.y))
        w = int(self.width * camera.zoom)
        h = int(self.height * camera.zoom)
        rect = pygame.Rect(screen_pos[0], screen_pos[1], w, h)
        pygame.draw.rect(surface, (0, 255, 255, 128), rect)
        pygame.draw.rect(surface, CYAN, rect, 2)
        # Arrow showing direction
        cx, cy = rect.center
        arrow_size = 10 * camera.zoom
        if self.direction == Direction.DOWN:
            pygame.draw.polygon(surface, WHITE, [(cx, cy + arrow_size), (cx - arrow_size, cy - arrow_size), (cx + arrow_size, cy - arrow_size)])
        elif self.direction == Direction.UP:
            pygame.draw.polygon(surface, WHITE, [(cx, cy - arrow_size), (cx - arrow_size, cy + arrow_size), (cx + arrow_size, cy + arrow_size)])
        elif self.direction == Direction.LEFT:
            pygame.draw.polygon(surface, WHITE, [(cx - arrow_size, cy), (cx + arrow_size, cy - arrow_size), (cx + arrow_size, cy + arrow_size)])
        elif self.direction == Direction.RIGHT:
            pygame.draw.polygon(surface, WHITE, [(cx + arrow_size, cy), (cx - arrow_size, cy - arrow_size), (cx - arrow_size, cy + arrow_size)])
        if selected:
            pygame.draw.rect(surface, EDITOR_SELECTION, rect, 3)
    
    def to_dict(self):
        return {"x": self.x, "y": self.y, "direction": self.direction.value,
                "warp_to_x": self.warp_to_x, "warp_to_y": self.warp_to_y,
                "warp_to_level": self.warp_to_level, "warp_to_section": self.warp_to_section,
                "exit_direction": self.exit_direction.value, "locked": self.locked,
                "stars_required": self.stars_required}

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 24
        self.height = 32
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.direction = Direction.RIGHT
        self.power = PowerState.SMALL
        self.p_meter = 0
        self.flying = False
        self.sliding = False
        self.ducking = False
        self.invincible = 0
        self.star_power = 0
        self.jump_held = False
        self.spin_jump = False
        self.coins = 0
        self.lives = 3
        self.score = 0
    
    def update_rect(self):
        if self.power == PowerState.SMALL or self.ducking:
            self.height = 32
        else:
            self.height = 54
        self.rect = pygame.Rect(int(self.x), int(self.y), self.width, self.height)
    
    def update(self, keys, tiles, npcs):
        # Horizontal input
        target_speed = 0
        running = keys[pygame.K_x] or keys[pygame.K_LSHIFT]
        max_speed = MAX_RUN_SPEED if running else MAX_WALK_SPEED
        accel = ACCEL_GROUND if self.on_ground else ACCEL_AIR
        
        if keys[pygame.K_LEFT]:
            target_speed = -max_speed
            self.direction = Direction.LEFT
        elif keys[pygame.K_RIGHT]:
            target_speed = max_speed
            self.direction = Direction.RIGHT
        
        # Approach target speed
        if abs(target_speed) > 0:
            if self.vel_x < target_speed:
                self.vel_x = min(self.vel_x + accel, target_speed)
            else:
                self.vel_x = max(self.vel_x - accel, target_speed)
            # P-meter
            if running and self.on_ground and abs(self.vel_x) >= MAX_RUN_SPEED - 0.5:
                self.p_meter = min(PMETER_MAX, self.p_meter + PMETER_CHARGE)
        else:
            # Friction
            if abs(self.vel_x) < FRICTION:
                self.vel_x = 0
            elif self.vel_x > 0:
                self.vel_x -= FRICTION
            else:
                self.vel_x += FRICTION
            self.p_meter = max(0, self.p_meter - PMETER_DECAY)
        
        # Jump
        jump_pressed = keys[pygame.K_z] or keys[pygame.K_SPACE]
        if jump_pressed and self.on_ground and not self.jump_held:
            self.vel_y = JUMP_FORCE
            if self.p_meter >= PMETER_MAX and self.power in [PowerState.LEAF, PowerState.TANOOKI]:
                self.flying = True
            self.on_ground = False
            self.jump_held = True
        if not jump_pressed:
            self.jump_held = False
            self.flying = False
        
        # Gravity
        grav = GRAVITY
        if jump_pressed and self.vel_y < 0:
            grav = JUMP_HOLD_GRAVITY
        if self.flying and self.vel_y > 0:
            grav = GRAVITY * 0.3
        self.vel_y = min(self.vel_y + grav, MAX_FALL_SPEED)
        
        # Ducking
        self.ducking = keys[pygame.K_DOWN] and self.on_ground and self.power != PowerState.SMALL
        
        # Move X
        self.x += self.vel_x
        self.update_rect()
        for tile in tiles:
            if tile.layer != Layer.MAIN:
                continue
            if self.rect.colliderect(tile.rect):
                if self.vel_x > 0:
                    self.rect.right = tile.rect.left
                    self.vel_x = 0
                elif self.vel_x < 0:
                    self.rect.left = tile.rect.right
                    self.vel_x = 0
                self.x = self.rect.x
        
        # Move Y
        self.y += self.vel_y
        self.update_rect()
        self.on_ground = False
        for tile in tiles:
            if tile.layer != Layer.MAIN:
                continue
            if self.rect.colliderect(tile.rect):
                if self.vel_y > 0:
                    if not tile.semisolid or self.rect.bottom - self.vel_y <= tile.rect.top + 4:
                        self.rect.bottom = tile.rect.top
                        self.vel_y = 0
                        self.on_ground = True
                        self.y = self.rect.y
                elif self.vel_y < 0 and not tile.semisolid:
                    self.rect.top = tile.rect.bottom
                    self.vel_y = 0
                    self.y = self.rect.y
        
        # NPC Collision
        for npc in npcs:
            if not npc.active:
                continue
            if self.rect.colliderect(npc.rect):
                if npc.is_coin:
                    self.coins += 1
                    self.score += 200
                    npc.active = False
                elif npc.is_powerup:
                    self.collect_powerup(npc)
                    npc.active = False
                elif npc.is_goal:
                    return "goal"
                elif not npc.friendly:
                    # Stomp check
                    if self.vel_y > 0 and self.rect.bottom - self.vel_y <= npc.rect.top + 8:
                        self.score += npc.score
                        self.vel_y = JUMP_FORCE * 0.6
                        npc.active = False
                    else:
                        self.take_damage()
        
        # Invincibility timer
        if self.invincible > 0:
            self.invincible -= 1
        if self.star_power > 0:
            self.star_power -= 1
        
        # Fall death
        if self.y > 2000:
            self.lives -= 1
            self.x = 200
            self.y = 200
            self.vel_y = 0
            if self.lives <= 0:
                return "gameover"
        
        return None
    
    def collect_powerup(self, npc):
        if npc.id == 27:  # Mushroom
            if self.power == PowerState.SMALL:
                self.power = PowerState.BIG
                self.y -= 22
        elif npc.id == 28:  # Fire flower
            self.power = PowerState.FIRE
            if self.height < 54:
                self.y -= 22
        elif npc.id == 29:  # Leaf
            self.power = PowerState.LEAF
            if self.height < 54:
                self.y -= 22
        elif npc.id == 33:  # 1-Up
            self.lives += 1
        elif npc.id == 35:  # Star
            self.star_power = 600
        self.score += 1000
    
    def take_damage(self):
        if self.invincible > 0 or self.star_power > 0:
            return
        if self.power == PowerState.SMALL:
            self.lives -= 1
            self.x = 200
            self.y = 200
            self.vel_y = 0
        else:
            self.power = PowerState.SMALL
            self.invincible = 120
    
    def draw(self, surface, camera):
        if self.invincible > 0 and self.invincible % 6 < 3:
            return
        screen_pos = camera.world_to_screen((self.x, self.y))
        w = int(self.width * camera.zoom)
        h = int(self.height * camera.zoom)
        rect = pygame.Rect(screen_pos[0], screen_pos[1], w, h)
        # Colors based on power
        colors = {
            PowerState.SMALL: (RED, (200, 100, 100)),
            PowerState.BIG: (RED, (200, 100, 100)),
            PowerState.FIRE: (WHITE, (255, 100, 0)),
            PowerState.LEAF: (RED, (200, 150, 100)),
            PowerState.TANOOKI: ((160, 82, 45), (100, 60, 30)),
            PowerState.HAMMER: ((32, 32, 32), (255, 200, 100)),
            PowerState.ICE: ((128, 192, 255), (64, 128, 200)),
        }
        if self.star_power > 0:
            t = time.time() * 10
            color1 = (int(127 + 127 * math.sin(t)), int(127 + 127 * math.sin(t + 2)), int(127 + 127 * math.sin(t + 4)))
            color2 = (int(127 + 127 * math.cos(t)), int(127 + 127 * math.cos(t + 2)), int(127 + 127 * math.cos(t + 4)))
        else:
            color1, color2 = colors.get(self.power, (RED, BROWN))
        
        # Draw body
        body_rect = pygame.Rect(rect.x, rect.y + h//3, w, h * 2 // 3)
        pygame.draw.rect(surface, color2, body_rect)
        # Draw head
        head_rect = pygame.Rect(rect.x, rect.y, w, h//2)
        pygame.draw.ellipse(surface, color1, head_rect)
        # Hat
        pygame.draw.rect(surface, color1, (rect.x - 4, rect.y + 4, w + 8, h//6))
        # Eye
        eye_x = rect.x + (w * 2 // 3 if self.direction == Direction.RIGHT else w // 3 - 4)
        pygame.draw.circle(surface, WHITE, (eye_x, rect.y + h//4), 4)
        pygame.draw.circle(surface, BLACK, (eye_x + (2 if self.direction == Direction.RIGHT else -2), rect.y + h//4), 2)

# --- Level ---
class Level:
    def __init__(self):
        self.settings = LevelSettings()
        self.blocks = []
        self.bgos = []
        self.npcs = []
        self.warps = []
        self.events = []
        self.layers = {"Default": True}
    
    def clear(self):
        self.blocks = []
        self.bgos = []
        self.npcs = []
        self.warps = []
    
    def save(self, filename):
        data = {
            "settings": self.settings.to_dict(),
            "blocks": [b.to_dict() for b in self.blocks],
            "bgos": [b.to_dict() for b in self.bgos],
            "npcs": [n.to_dict() for n in self.npcs],
            "warps": [w.to_dict() for w in self.warps],
            "layers": self.layers
        }
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        return True
    
    def load(self, filename):
        if not os.path.exists(filename):
            return False
        with open(filename, "r") as f:
            data = json.load(f)
        self.settings = LevelSettings(**{k: v for k, v in data.get("settings", {}).items() 
                                        if k in LevelSettings.__dataclass_fields__})
        self.blocks = [Block.from_dict(d) for d in data.get("blocks", [])]
        self.bgos = [BGO.from_dict(d) for d in data.get("bgos", [])]
        self.npcs = [NPC.from_dict(d) for d in data.get("npcs", [])]
        self.layers = data.get("layers", {"Default": True})
        return True

# --- Main Application ---
class MariofanBuilder:
    def __init__(self):
        self.state = GameState.MAIN_MENU
        self.prev_state = None
        self.level = Level()
        self.camera = Camera()
        self.player = None
        self.play_level = None
        self.episodes = []
        self.selected_episode = 0
        self.menu_selection = 0
        self.scroll_offset = 0
        self.editor_mode = EditorMode.BLOCKS
        self.selected_id = 1
        self.selected_layer = Layer.MAIN
        self.selection_box = None
        self.selected_objects = []
        self.clipboard = []
        self.undo_stack = []
        self.redo_stack = []
        self.grid_snap = True
        self.show_grid = True
        self.show_invisible = True
        self.current_filename = ""
        self.message = ""
        self.message_timer = 0
        self.load_episodes()
        self.populate_demo_level()
    
    def load_episodes(self):
        """Load episodes from worlds folder"""
        self.episodes = [
            Episode("The Invasion 2", "invasion2", "An epic adventure!", "Redigit", "1.0"),
            Episode("A Super Mario Thing", "asmt", "Classic SMBX adventure", "raocow", "1.0"),
            Episode("Talkhaus Project", "talkhaus", "Community episode", "Talkhaus", "2.0"),
            Episode("The Princess Cliche", "princess", "Save the princess!", "Demo Author", "1.0"),
            Episode("Demo Episode", "demo", "A sample episode", "Samsoft", "0.1"),
        ]
        # Try to load from disk
        if os.path.exists("worlds"):
            for folder in os.listdir("worlds"):
                ep_file = os.path.join("worlds", folder, "episode.json")
                if os.path.exists(ep_file):
                    with open(ep_file) as f:
                        data = json.load(f)
                        self.episodes.append(Episode.from_dict(data))
    
    def populate_demo_level(self):
        """Create a demo level"""
        # Ground
        for i in range(50):
            self.level.blocks.append(Block(i * GRID_SIZE, 480, 16))  # Grass top
            self.level.blocks.append(Block(i * GRID_SIZE, 512, 17))  # Dirt
            self.level.blocks.append(Block(i * GRID_SIZE, 544, 17))
        # Platforms
        self.level.blocks.append(Block(256, 384, 1))
        self.level.blocks.append(Block(288, 384, 4))  # Question block
        self.level.blocks.append(Block(320, 384, 1))
        # Question blocks with content
        q = Block(416, 288, 4)
        q.content_id = 27  # Mushroom
        self.level.blocks.append(q)
        # Pipes
        for i in range(4):
            self.level.blocks.append(Block(640, 384 + i * 32, 25 if i > 0 else 23))
            self.level.blocks.append(Block(672, 384 + i * 32, 26 if i > 0 else 24))
        # NPCs
        self.level.npcs.append(NPC(512, 448, 1))  # Goomba
        self.level.npcs.append(NPC(800, 448, 4))  # Koopa
        self.level.npcs.append(NPC(300, 352, 36))  # Coin
        self.level.npcs.append(NPC(332, 352, 36))
        self.level.npcs.append(NPC(364, 352, 36))
        # BGOs
        self.level.bgos.append(BGO(100, 400, 1))  # Bush
        self.level.bgos.append(BGO(300, 200, 3))  # Cloud
        self.level.bgos.append(BGO(600, 180, 4))  # Large cloud
    
    def show_message(self, msg, duration=120):
        self.message = msg
        self.message_timer = duration
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                self.handle_keydown(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mousedown(event)
            if event.type == pygame.MOUSEWHEEL:
                if self.state == GameState.EDITOR:
                    if event.y > 0:
                        self.camera.set_zoom(self.camera.zoom * 1.1)
                    else:
                        self.camera.set_zoom(self.camera.zoom / 1.1)
        return True
    
    def handle_keydown(self, event):
        if self.state == GameState.MAIN_MENU:
            if event.key in [pygame.K_UP, pygame.K_w]:
                self.menu_selection = (self.menu_selection - 1) % 5
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                self.menu_selection = (self.menu_selection + 1) % 5
            elif event.key in [pygame.K_RETURN, pygame.K_z, pygame.K_SPACE]:
                self.select_menu_item()
            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
        
        elif self.state == GameState.EPISODE_SELECT:
            if event.key in [pygame.K_UP, pygame.K_w]:
                self.selected_episode = (self.selected_episode - 1) % max(1, len(self.episodes))
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                self.selected_episode = (self.selected_episode + 1) % max(1, len(self.episodes))
            elif event.key in [pygame.K_RETURN, pygame.K_z, pygame.K_SPACE]:
                self.start_episode()
            elif event.key == pygame.K_ESCAPE:
                self.state = GameState.MAIN_MENU
        
        elif self.state == GameState.EDITOR_MENU:
            if event.key in [pygame.K_UP, pygame.K_w]:
                self.menu_selection = (self.menu_selection - 1) % 4
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                self.menu_selection = (self.menu_selection + 1) % 4
            elif event.key in [pygame.K_RETURN, pygame.K_z, pygame.K_SPACE]:
                self.select_editor_menu_item()
            elif event.key == pygame.K_ESCAPE:
                self.state = GameState.MAIN_MENU
        
        elif self.state == GameState.EDITOR:
            keys = pygame.key.get_pressed()
            ctrl = keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]
            
            if event.key == pygame.K_ESCAPE:
                self.state = GameState.EDITOR_MENU
            elif event.key == pygame.K_p or event.key == pygame.K_F5:
                self.start_play_test()
            elif event.key == pygame.K_g:
                self.show_grid = not self.show_grid
            elif event.key == pygame.K_h:
                self.grid_snap = not self.grid_snap
            elif event.key == pygame.K_i:
                self.show_invisible = not self.show_invisible
            # Mode switching
            elif event.key == pygame.K_1:
                self.editor_mode = EditorMode.BLOCKS
            elif event.key == pygame.K_2:
                self.editor_mode = EditorMode.BGOS
            elif event.key == pygame.K_3:
                self.editor_mode = EditorMode.NPCS
            elif event.key == pygame.K_4:
                self.editor_mode = EditorMode.WARPS
            # ID selection
            elif event.key == pygame.K_q:
                self.selected_id = max(1, self.selected_id - 1)
            elif event.key == pygame.K_e:
                self.selected_id = self.selected_id + 1
            elif event.key == pygame.K_PAGEUP:
                self.selected_id = max(1, self.selected_id - 10)
            elif event.key == pygame.K_PAGEDOWN:
                self.selected_id += 10
            # Save/Load
            elif event.key == pygame.K_s and ctrl:
                self.save_level()
            elif event.key == pygame.K_o and ctrl:
                self.load_level_dialog()
            elif event.key == pygame.K_n and ctrl:
                self.new_level()
            # Undo/Redo
            elif event.key == pygame.K_z and ctrl:
                self.undo()
            elif event.key == pygame.K_y and ctrl:
                self.redo()
            # Delete
            elif event.key == pygame.K_DELETE:
                self.delete_selected()
        
        elif self.state == GameState.PLAY:
            if event.key == pygame.K_ESCAPE:
                self.stop_play_test()
            elif event.key == pygame.K_p:
                self.state = GameState.PAUSE
        
        elif self.state == GameState.PAUSE:
            if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                self.state = GameState.PLAY
            elif event.key == pygame.K_q:
                self.stop_play_test()
    
    def handle_mousedown(self, event):
        if self.state == GameState.EDITOR:
            mouse_pos = pygame.mouse.get_pos()
            if mouse_pos[1] < SCREEN_HEIGHT - TOOLBAR_HEIGHT:
                world_pos = self.camera.screen_to_world(mouse_pos)
                if event.button == 1:  # Left click - place
                    self.place_object(world_pos)
                elif event.button == 2:  # Middle click - pick
                    self.pick_object(world_pos)
                elif event.button == 3:  # Right click handled by camera
                    pass
    
    def place_object(self, pos):
        if self.grid_snap:
            x = int(pos[0] // GRID_SIZE) * GRID_SIZE
            y = int(pos[1] // GRID_SIZE) * GRID_SIZE
        else:
            x, y = int(pos[0]), int(pos[1])
        
        # Check for existing object
        for b in self.level.blocks:
            if b.x == x and b.y == y and b.layer == self.selected_layer:
                return
        
        # Save undo state
        self.save_undo_state()
        
        if self.editor_mode == EditorMode.BLOCKS:
            if self.selected_id in BLOCK_DATA:
                self.level.blocks.append(Block(x, y, self.selected_id, self.selected_layer))
        elif self.editor_mode == EditorMode.BGOS:
            if self.selected_id in BGO_DATA:
                self.level.bgos.append(BGO(x, y, self.selected_id, Layer.BACKGROUND))
        elif self.editor_mode == EditorMode.NPCS:
            if self.selected_id in NPC_DATA:
                self.level.npcs.append(NPC(x, y, self.selected_id))
        elif self.editor_mode == EditorMode.WARPS:
            self.level.warps.append(Warp(x, y))
    
    def pick_object(self, pos):
        """Pick object ID under cursor"""
        for npc in reversed(self.level.npcs):
            if npc.rect.collidepoint(pos):
                self.editor_mode = EditorMode.NPCS
                self.selected_id = npc.id
                return
        for block in reversed(self.level.blocks):
            if block.rect.collidepoint(pos):
                self.editor_mode = EditorMode.BLOCKS
                self.selected_id = block.id
                return
        for bgo in reversed(self.level.bgos):
            if bgo.rect.collidepoint(pos):
                self.editor_mode = EditorMode.BGOS
                self.selected_id = bgo.id
                return
    
    def delete_at(self, pos):
        """Delete object at position"""
        for lst in [self.level.npcs, self.level.blocks, self.level.bgos, self.level.warps]:
            for obj in reversed(lst):
                if obj.rect.collidepoint(pos):
                    self.save_undo_state()
                    lst.remove(obj)
                    return
    
    def delete_selected(self):
        pass  # TODO: multi-select
    
    def save_undo_state(self):
        state = {
            "blocks": [b.to_dict() for b in self.level.blocks],
            "bgos": [b.to_dict() for b in self.level.bgos],
            "npcs": [n.to_dict() for n in self.level.npcs],
        }
        self.undo_stack.append(state)
        if len(self.undo_stack) > 50:
            self.undo_stack.pop(0)
        self.redo_stack.clear()
    
    def undo(self):
        if not self.undo_stack:
            return
        # Save current for redo
        current = {
            "blocks": [b.to_dict() for b in self.level.blocks],
            "bgos": [b.to_dict() for b in self.level.bgos],
            "npcs": [n.to_dict() for n in self.level.npcs],
        }
        self.redo_stack.append(current)
        # Restore previous
        state = self.undo_stack.pop()
        self.level.blocks = [Block.from_dict(d) for d in state["blocks"]]
        self.level.bgos = [BGO.from_dict(d) for d in state["bgos"]]
        self.level.npcs = [NPC.from_dict(d) for d in state["npcs"]]
        self.show_message("Undo")
    
    def redo(self):
        if not self.redo_stack:
            return
        current = {
            "blocks": [b.to_dict() for b in self.level.blocks],
            "bgos": [b.to_dict() for b in self.level.bgos],
            "npcs": [n.to_dict() for n in self.level.npcs],
        }
        self.undo_stack.append(current)
        state = self.redo_stack.pop()
        self.level.blocks = [Block.from_dict(d) for d in state["blocks"]]
        self.level.bgos = [BGO.from_dict(d) for d in state["bgos"]]
        self.level.npcs = [NPC.from_dict(d) for d in state["npcs"]]
        self.show_message("Redo")
    
    def select_menu_item(self):
        if self.menu_selection == 0:  # Start Game
            self.state = GameState.EPISODE_SELECT
        elif self.menu_selection == 1:  # Editor
            self.state = GameState.EDITOR_MENU
        elif self.menu_selection == 2:  # Options
            self.state = GameState.OPTIONS
        elif self.menu_selection == 3:  # Credits
            self.state = GameState.CREDITS
        elif self.menu_selection == 4:  # Exit
            pygame.quit()
            sys.exit()
    
    def select_editor_menu_item(self):
        if self.menu_selection == 0:  # New Level
            self.new_level()
            self.state = GameState.EDITOR
        elif self.menu_selection == 1:  # Open Level
            self.load_level_dialog()
        elif self.menu_selection == 2:  # Edit Episode
            self.show_message("Episode editor coming soon!")
        elif self.menu_selection == 3:  # Back
            self.state = GameState.MAIN_MENU
    
    def start_episode(self):
        """Start playing selected episode"""
        self.state = GameState.PLAY
        self.camera.target = None
        # Load first level of episode
        self.start_play_test()
    
    def new_level(self):
        self.level = Level()
        self.current_filename = ""
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.show_message("New level created")
    
    def save_level(self):
        filename = self.current_filename or "level.lvl"
        if self.level.save(filename):
            self.current_filename = filename
            self.show_message(f"Saved: {filename}")
    
    def load_level_dialog(self):
        """Simple file loading"""
        if os.path.exists("level.lvl"):
            if self.level.load("level.lvl"):
                self.current_filename = "level.lvl"
                self.show_message("Level loaded!")
                self.state = GameState.EDITOR
    
    def start_play_test(self):
        """Start playing the current level"""
        self.prev_state = self.state
        self.state = GameState.PLAY
        # Deep copy level for play
        self.play_level = Level()
        self.play_level.blocks = copy.deepcopy(self.level.blocks)
        self.play_level.bgos = copy.deepcopy(self.level.bgos)
        self.play_level.npcs = copy.deepcopy(self.level.npcs)
        self.play_level.settings = copy.deepcopy(self.level.settings)
        # Create player
        start_x, start_y = self.level.settings.player_start
        self.player = Player(start_x, start_y)
        self.camera.target = self.player
        self.camera.section_bounds = (0, 0, self.level.settings.width, self.level.settings.height)
    
    def stop_play_test(self):
        self.state = self.prev_state or GameState.EDITOR
        self.player = None
        self.play_level = None
        self.camera.target = None
        self.camera.section_bounds = None
    
    def update(self):
        self.scroll_offset += 1
        if self.message_timer > 0:
            self.message_timer -= 1
        
        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        
        if self.state == GameState.EDITOR:
            self.camera.update(keys, mouse, mouse_pos, editor_mode=True)
            # Continuous placement
            if mouse[0] and mouse_pos[1] < SCREEN_HEIGHT - TOOLBAR_HEIGHT:
                world_pos = self.camera.screen_to_world(mouse_pos)
                self.place_object(world_pos)
            # Delete with middle click
            if mouse[1] and mouse_pos[1] < SCREEN_HEIGHT - TOOLBAR_HEIGHT:
                world_pos = self.camera.screen_to_world(mouse_pos)
                self.delete_at(world_pos)
        
        elif self.state == GameState.PLAY:
            if self.player and self.play_level:
                result = self.player.update(keys, self.play_level.blocks, self.play_level.npcs)
                for npc in self.play_level.npcs:
                    if npc.active:
                        npc.update(self.play_level.blocks, self.play_level.npcs)
                self.camera.update(keys, mouse, mouse_pos, editor_mode=False)
                if result == "goal":
                    self.show_message("Level Complete!")
                    self.stop_play_test()
                elif result == "gameover":
                    self.show_message("Game Over!")
                    self.stop_play_test()
    
    def draw(self):
        if self.state == GameState.MAIN_MENU:
            self.draw_main_menu()
        elif self.state == GameState.EPISODE_SELECT:
            self.draw_episode_select()
        elif self.state == GameState.EDITOR_MENU:
            self.draw_editor_menu()
        elif self.state == GameState.EDITOR:
            self.draw_editor()
        elif self.state == GameState.PLAY:
            self.draw_play()
        elif self.state == GameState.PAUSE:
            self.draw_play()
            self.draw_pause_overlay()
        elif self.state == GameState.OPTIONS:
            self.draw_options()
        elif self.state == GameState.CREDITS:
            self.draw_credits()
        
        # Message overlay
        if self.message_timer > 0:
            draw_panel(screen, (SCREEN_WIDTH//2 - 150, 20, 300, 40))
            draw_text_shadow(screen, self.message, (SCREEN_WIDTH//2 - 140, 28), font_medium, MENU_SELECTED)
        
        pygame.display.flip()
    
    def draw_main_menu(self):
        draw_menu_background(screen, self.scroll_offset)
        
        # Title
        title_y = 60
        draw_text_shadow(screen, TITLE, (SCREEN_WIDTH//2 - 160, title_y), font_huge, MENU_SELECTED)
        draw_text_shadow(screen, f"Version {VERSION}", (SCREEN_WIDTH//2 - 50, title_y + 50), font_small, LIGHT_GRAY)
        
        # Menu panel
        panel_x = SCREEN_WIDTH//2 - 150
        panel_y = 150
        draw_panel(screen, (panel_x, panel_y, 300, 280))
        
        # Menu items
        menu_items = ["Start Game", "Level Editor", "Options", "Credits", "Exit"]
        for i, item in enumerate(menu_items):
            y = panel_y + 30 + i * 48
            selected = i == self.menu_selection
            color = MENU_SELECTED if selected else MENU_TEXT
            if selected:
                # Selection indicator
                pygame.draw.polygon(screen, MENU_SELECTED, 
                                   [(panel_x + 20, y + 10), (panel_x + 35, y + 18), (panel_x + 20, y + 26)])
            draw_text_shadow(screen, item, (panel_x + 50, y), font_large, color)
        
        # Copyright
        draw_text_shadow(screen, COPYRIGHT, (10, SCREEN_HEIGHT - 30), font_small, GRAY)
        draw_text_shadow(screen, "Press Enter to Select", (SCREEN_WIDTH - 180, SCREEN_HEIGHT - 30), font_small, GRAY)
    
    def draw_episode_select(self):
        draw_menu_background(screen, self.scroll_offset)
        
        draw_text_shadow(screen, "Select Episode", (SCREEN_WIDTH//2 - 100, 30), font_title, MENU_SELECTED)
        
        # Episode list panel
        panel_x = 50
        panel_y = 80
        panel_w = SCREEN_WIDTH - 100
        panel_h = SCREEN_HEIGHT - 150
        draw_panel(screen, (panel_x, panel_y, panel_w, panel_h))
        
        # Episode list
        visible_episodes = 8
        start_idx = max(0, self.selected_episode - visible_episodes // 2)
        for i, ep in enumerate(self.episodes[start_idx:start_idx + visible_episodes]):
            actual_idx = start_idx + i
            y = panel_y + 20 + i * 50
            selected = actual_idx == self.selected_episode
            
            # Episode entry
            entry_rect = (panel_x + 10, y, panel_w - 20, 45)
            if selected:
                pygame.draw.rect(screen, (64, 64, 128), entry_rect)
                pygame.draw.rect(screen, MENU_SELECTED, entry_rect, 2)
            
            color = MENU_SELECTED if selected else MENU_TEXT
            draw_text_shadow(screen, ep.name, (panel_x + 20, y + 5), font_medium, color)
            draw_text_shadow(screen, f"by {ep.author} - v{ep.version}", (panel_x + 20, y + 25), font_small, GRAY)
        
        # Info panel for selected episode
        if self.episodes:
            ep = self.episodes[self.selected_episode]
            info_y = SCREEN_HEIGHT - 60
            draw_text_shadow(screen, ep.description or "No description", (panel_x + 20, info_y), font_small, LIGHT_GRAY)
        
        draw_text_shadow(screen, "Enter: Play | Esc: Back", (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 25), font_small, GRAY)
    
    def draw_editor_menu(self):
        draw_menu_background(screen, self.scroll_offset)
        
        draw_text_shadow(screen, "Level Editor", (SCREEN_WIDTH//2 - 90, 50), font_title, MENU_SELECTED)
        
        # Menu panel
        panel_x = SCREEN_WIDTH//2 - 150
        panel_y = 130
        draw_panel(screen, (panel_x, panel_y, 300, 240))
        
        menu_items = ["New Level", "Open Level", "Edit Episode", "Back"]
        for i, item in enumerate(menu_items):
            y = panel_y + 30 + i * 50
            selected = i == self.menu_selection
            color = MENU_SELECTED if selected else MENU_TEXT
            if selected:
                pygame.draw.polygon(screen, MENU_SELECTED,
                                   [(panel_x + 20, y + 10), (panel_x + 35, y + 18), (panel_x + 20, y + 26)])
            draw_text_shadow(screen, item, (panel_x + 50, y), font_large, color)
    
    def draw_editor(self):
        # Background
        screen.fill(SKY_BLUE)
        
        # Grid
        if self.show_grid:
            self.draw_grid()
        
        # BGOs (background)
        for bgo in self.level.bgos:
            bgo.draw(screen, self.camera)
        
        # Blocks
        for block in self.level.blocks:
            block.draw(screen, self.camera, show_invisible=self.show_invisible)
        
        # NPCs
        for npc in self.level.npcs:
            npc.draw(screen, self.camera)
        
        # Warps
        for warp in self.level.warps:
            warp.draw(screen, self.camera)
        
        # Player start marker
        start_pos = self.camera.world_to_screen(self.level.settings.player_start)
        pygame.draw.rect(screen, (0, 255, 0, 128), 
                        (start_pos[0], start_pos[1] - 32, 24 * self.camera.zoom, 64 * self.camera.zoom), 2)
        draw_text_shadow(screen, "P1", (start_pos[0], start_pos[1] - 50), font_small, GREEN)
        
        # Toolbar
        self.draw_editor_toolbar()
    
    def draw_grid(self):
        """Draw editor grid"""
        grid_color = EDITOR_GRID
        # Calculate visible grid range
        start_x = int(self.camera.x // GRID_SIZE) * GRID_SIZE
        start_y = int(self.camera.y // GRID_SIZE) * GRID_SIZE
        end_x = int((self.camera.x + SCREEN_WIDTH / self.camera.zoom) // GRID_SIZE + 2) * GRID_SIZE
        end_y = int((self.camera.y + (SCREEN_HEIGHT - TOOLBAR_HEIGHT) / self.camera.zoom) // GRID_SIZE + 2) * GRID_SIZE
        
        for x in range(start_x, end_x, GRID_SIZE):
            screen_x = int((x - self.camera.x) * self.camera.zoom)
            pygame.draw.line(screen, grid_color, (screen_x, 0), (screen_x, SCREEN_HEIGHT - TOOLBAR_HEIGHT))
        for y in range(start_y, end_y, GRID_SIZE):
            screen_y = int((y - self.camera.y) * self.camera.zoom)
            pygame.draw.line(screen, grid_color, (0, screen_y), (SCREEN_WIDTH, screen_y))
    
    def draw_editor_toolbar(self):
        """Draw the SMBX-style editor toolbar"""
        toolbar_y = SCREEN_HEIGHT - TOOLBAR_HEIGHT
        
        # Background
        pygame.draw.rect(screen, EDITOR_TOOLBAR, (0, toolbar_y, SCREEN_WIDTH, TOOLBAR_HEIGHT))
        pygame.draw.line(screen, MENU_BORDER, (0, toolbar_y), (SCREEN_WIDTH, toolbar_y), 2)
        
        # Mode tabs
        modes = ["Blocks", "BGOs", "NPCs", "Warps", "Water", "Layers", "Events"]
        tab_width = 80
        for i, mode in enumerate(modes):
            tab_x = 10 + i * (tab_width + 5)
            selected = i == self.editor_mode.value
            color = MENU_SELECTED if selected else MENU_BORDER
            pygame.draw.rect(screen, MENU_PANEL if selected else EDITOR_TOOLBAR, 
                           (tab_x, toolbar_y + 5, tab_width, 25))
            pygame.draw.rect(screen, color, (tab_x, toolbar_y + 5, tab_width, 25), 2)
            draw_text_shadow(screen, mode, (tab_x + 5, toolbar_y + 8), font_small, 
                           MENU_SELECTED if selected else MENU_TEXT)
        
        # Object palette
        palette_y = toolbar_y + 40
        palette_x = 10
        
        # Get current data dict
        if self.editor_mode == EditorMode.BLOCKS:
            data_dict = BLOCK_DATA
        elif self.editor_mode == EditorMode.BGOS:
            data_dict = BGO_DATA
        elif self.editor_mode == EditorMode.NPCS:
            data_dict = NPC_DATA
        else:
            data_dict = {}
        
        # Draw palette items
        items_per_row = 16
        item_size = 36
        for i, (id, data) in enumerate(list(data_dict.items())[:32]):
            row = i // items_per_row
            col = i % items_per_row
            x = palette_x + col * (item_size + 4)
            y = palette_y + row * (item_size + 4)
            
            selected = id == self.selected_id
            rect = pygame.Rect(x, y, item_size, item_size)
            
            # Draw item preview
            color = data.get("color", GRAY)
            pygame.draw.rect(screen, color, rect)
            if selected:
                pygame.draw.rect(screen, MENU_SELECTED, rect, 3)
            else:
                pygame.draw.rect(screen, MENU_BORDER, rect, 1)
            
            # ID number
            id_txt = font_tiny.render(str(id), True, WHITE)
            screen.blit(id_txt, (x + 2, y + 2))
        
        # Info panel
        info_x = SCREEN_WIDTH - 250
        draw_panel(screen, (info_x, toolbar_y + 5, 240, TOOLBAR_HEIGHT - 15), style="dark")
        
        # Current selection info
        if self.editor_mode == EditorMode.BLOCKS and self.selected_id in BLOCK_DATA:
            name = BLOCK_DATA[self.selected_id]["name"]
        elif self.editor_mode == EditorMode.BGOS and self.selected_id in BGO_DATA:
            name = BGO_DATA[self.selected_id]["name"]
        elif self.editor_mode == EditorMode.NPCS and self.selected_id in NPC_DATA:
            name = NPC_DATA[self.selected_id]["name"]
        else:
            name = "Unknown"
        
        draw_text_shadow(screen, f"ID: {self.selected_id}", (info_x + 10, toolbar_y + 15), font_small, MENU_TEXT)
        draw_text_shadow(screen, name[:25], (info_x + 10, toolbar_y + 35), font_small, MENU_SELECTED)
        draw_text_shadow(screen, f"Layer: {self.selected_layer.name}", (info_x + 10, toolbar_y + 55), font_small, MENU_TEXT)
        draw_text_shadow(screen, f"Zoom: {self.camera.zoom:.1f}x", (info_x + 10, toolbar_y + 75), font_small, MENU_TEXT)
        
        # Controls hint
        controls = "Q/E:ID | 1-4:Mode | G:Grid | P:Play | Ctrl+S:Save"
        draw_text_shadow(screen, controls, (info_x + 10, toolbar_y + 100), font_tiny, GRAY)
    
    def draw_play(self):
        """Draw the game play view"""
        # Background
        screen.fill(SKY_BLUE)
        
        if self.play_level:
            # BGOs
            for bgo in self.play_level.bgos:
                bgo.draw(screen, self.camera)
            
            # Blocks
            for block in self.play_level.blocks:
                block.draw(screen, self.camera, show_invisible=False)
            
            # NPCs
            for npc in self.play_level.npcs:
                if npc.active:
                    npc.draw(screen, self.camera)
            
            # Player
            if self.player:
                self.player.draw(screen, self.camera)
        
        # HUD
        self.draw_hud()
    
    def draw_hud(self):
        """Draw game HUD"""
        # Top bar
        pygame.draw.rect(screen, (0, 0, 0, 180), (0, 0, SCREEN_WIDTH, 40))
        
        if self.player:
            # Lives
            draw_text_shadow(screen, f"LIVES: {self.player.lives}", (20, 10), font_medium, WHITE)
            # Coins
            draw_text_shadow(screen, f"COINS: {self.player.coins}", (150, 10), font_medium, YELLOW)
            # Score
            draw_text_shadow(screen, f"SCORE: {self.player.score}", (280, 10), font_medium, WHITE)
            # P-Meter
            meter_x = SCREEN_WIDTH - 200
            pygame.draw.rect(screen, DARK_GRAY, (meter_x, 15, 100, 12))
            pygame.draw.rect(screen, YELLOW, (meter_x, 15, self.player.p_meter, 12))
            pygame.draw.rect(screen, WHITE, (meter_x, 15, 100, 12), 1)
            if self.player.p_meter >= PMETER_MAX:
                draw_text_shadow(screen, "P", (meter_x + 105, 10), font_medium, YELLOW)
        
        # Play test indicator
        if self.prev_state == GameState.EDITOR:
            draw_text_shadow(screen, "[TESTING] ESC to stop", (SCREEN_WIDTH//2 - 80, 10), font_small, (255, 128, 128))
    
    def draw_pause_overlay(self):
        """Draw pause menu overlay"""
        # Darken screen
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        
        # Pause panel
        panel_x = SCREEN_WIDTH//2 - 100
        panel_y = SCREEN_HEIGHT//2 - 60
        draw_panel(screen, (panel_x, panel_y, 200, 120))
        draw_text_shadow(screen, "PAUSED", (panel_x + 55, panel_y + 20), font_large, MENU_SELECTED)
        draw_text_shadow(screen, "P - Resume", (panel_x + 50, panel_y + 60), font_medium, MENU_TEXT)
        draw_text_shadow(screen, "Q - Quit", (panel_x + 60, panel_y + 85), font_medium, MENU_TEXT)
    
    def draw_options(self):
        draw_menu_background(screen, self.scroll_offset)
        draw_text_shadow(screen, "Options", (SCREEN_WIDTH//2 - 60, 50), font_title, MENU_SELECTED)
        draw_panel(screen, (100, 120, SCREEN_WIDTH - 200, 300))
        draw_text_shadow(screen, "Options menu coming soon!", (SCREEN_WIDTH//2 - 120, 200), font_medium, MENU_TEXT)
        draw_text_shadow(screen, "Press Escape to return", (SCREEN_WIDTH//2 - 100, 350), font_small, GRAY)
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            self.state = GameState.MAIN_MENU
    
    def draw_credits(self):
        draw_menu_background(screen, self.scroll_offset)
        draw_text_shadow(screen, "Credits", (SCREEN_WIDTH//2 - 50, 50), font_title, MENU_SELECTED)
        draw_panel(screen, (100, 120, SCREEN_WIDTH - 200, 350))
        
        credits = [
            f"{TITLE} {VERSION}",
            "",
            "Created by Samsoft",
            "",
            "Inspired by:",
            "- Super Mario Bros. X by Redigit",
            "- SMBX2 by the SMBX2 Team",
            "- Super Mario Bros. by Nintendo",
            "",
            "Built with Python & Pygame",
            "",
            "Thank you for playing!"
        ]
        
        for i, line in enumerate(credits):
            color = MENU_SELECTED if i == 0 else MENU_TEXT
            draw_text_shadow(screen, line, (120, 140 + i * 25), font_medium if i == 0 else font_small, color)
        
        draw_text_shadow(screen, "Press Escape to return", (SCREEN_WIDTH//2 - 100, 450), font_small, GRAY)
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            self.state = GameState.MAIN_MENU
    
    def run(self):
        """Main game loop"""
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            clock.tick(FPS)
        pygame.quit()

# --- Entry Point ---
if __name__ == "__main__":
    print(f"{TITLE} {VERSION}")
    print(COPYRIGHT)
    print("Starting...")
    
    app = MariofanBuilder()
    app.run()
