#!/usr/bin/env python3
"""
CAT'S DELTARUNE - CHAPTERS 1 & 2
A faithful recreation of Toby Fox's Deltarune
By Team Flames / Samsoft / Flames Co.

Chapter 1: THE BEGINNING
Chapter 2: A CYBER'S WORLD

Features complete story progression, all major areas,
bosses, enemies, dialogue, and mechanics from both chapters.
"""

import pygame
import random
import math
import json
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Callable

# =============================================================================
# CONSTANTS
# =============================================================================

WIDTH, HEIGHT = 640, 480
TILE_SIZE = 32
FPS = 60

# Deltarune color palette
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 162, 232)
LIGHT_BLUE = (100, 200, 255)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 100, 0)
ORANGE = (255, 165, 0)
PURPLE = (148, 0, 211)
PINK = (255, 105, 180)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)

# Chapter 1 colors (Dark World)
DARK_PURPLE = (40, 20, 60)
CASTLE_BLUE = (20, 40, 80)
FIELD_GREEN = (20, 60, 40)

# Chapter 2 colors (Cyber World)  
CYBER_PINK = (255, 50, 150)
CYBER_BLUE = (50, 150, 255)
CYBER_BLACK = (10, 10, 30)
NEON_GREEN = (50, 255, 50)
NEON_PURPLE = (200, 50, 255)

# Battle box
BATTLE_BOX_X = 32
BATTLE_BOX_Y = 252
BATTLE_BOX_W = 576
BATTLE_BOX_H = 140

SOUL_SIZE = 16
SOUL_SPEED = 4

# =============================================================================
# ENUMS
# =============================================================================

class GameState(Enum):
    TITLE = auto()
    OVERWORLD = auto()
    BATTLE = auto()
    DIALOGUE = auto()
    CUTSCENE = auto()
    MENU = auto()
    SHOP = auto()
    CHAPTER_END = auto()

class BattleState(Enum):
    SELECTING_MEMBER = auto()
    SELECTING_ACTION = auto()
    SELECTING_TARGET = auto()
    SELECTING_ACT = auto()
    SELECTING_ITEM = auto()
    SELECTING_MAGIC = auto()
    ENEMY_TURN = auto()
    DIALOGUE = auto()
    VICTORY = auto()
    SPARE = auto()
    FLEE = auto()
    GAME_OVER = auto()

class Chapter(Enum):
    ONE = 1
    TWO = 2

# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class Stats:
    hp: int
    max_hp: int
    atk: int
    defense: int
    magic: int
    tp: int = 0
    max_tp: int = 100
    lv: int = 1
    exp: int = 0

@dataclass
class Spell:
    name: str
    tp_cost: int
    description: str
    target_type: str  # "enemy", "ally", "all_enemies", "all_allies"
    effect: str  # "damage", "heal", "pacify", "buff"
    power: int = 0

@dataclass
class PartyMember:
    name: str
    stats: Stats
    color: Tuple[int, int, int]
    weapon: str = ""
    armor: str = ""
    acts: List[str] = field(default_factory=list)
    spells: List[Spell] = field(default_factory=list)
    down: bool = False

@dataclass
class Item:
    name: str
    description: str
    heal_hp: int = 0
    heal_tp: int = 0
    is_key: bool = False
    sell_price: int = 0

@dataclass
class Enemy:
    name: str
    stats: Stats
    color: Tuple[int, int, int]
    acts: Dict[str, Tuple[str, int]]  # act_name: (response, mercy_gain)
    spare_threshold: int = 100
    mercy: int = 0
    check_text: str = ""
    attacks: List[str] = field(default_factory=list)
    flavor_texts: List[str] = field(default_factory=list)
    tired: bool = False
    defeated: bool = False
    is_boss: bool = False
    exp_reward: int = 0
    money_reward: int = 0

@dataclass
class DialogueLine:
    speaker: str
    text: str
    expression: str = "neutral"
    
@dataclass
class NPC:
    name: str
    x: int
    y: int
    dialogue: List[DialogueLine]
    color: Tuple[int, int, int] = WHITE
    
@dataclass
class AreaTransition:
    x: int
    y: int
    w: int
    h: int
    target_area: str
    target_x: int
    target_y: int
    
@dataclass
class SavePoint:
    x: int
    y: int
    text: str

# =============================================================================
# BULLET PATTERNS - CHAPTER 1 BOSSES
# =============================================================================

class Bullet:
    def __init__(self, x, y, dx, dy, color=WHITE, radius=6, damage=5):
        self.x, self.y = x, y
        self.dx, self.dy = dx, dy
        self.color = color
        self.radius = radius
        self.damage = damage
        self.alive = True
        self.grazed = False
        
    def update(self):
        self.x += self.dx
        self.y += self.dy
        if (self.x < BATTLE_BOX_X - 30 or self.x > BATTLE_BOX_X + BATTLE_BOX_W + 30 or
            self.y < BATTLE_BOX_Y - 30 or self.y > BATTLE_BOX_Y + BATTLE_BOX_H + 30):
            self.alive = False
            
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius, 1)

class BulletPattern:
    def __init__(self, duration=300):
        self.bullets: List[Bullet] = []
        self.timer = 0
        self.duration = duration
        self.finished = False
        self.special_objects = []
        
    def update(self, soul_x, soul_y):
        self.timer += 1
        if self.timer >= self.duration:
            self.finished = True
        for b in self.bullets[:]:
            b.update()
            if not b.alive:
                self.bullets.remove(b)
                
    def draw(self, screen):
        for b in self.bullets:
            b.draw(screen)
            
    def spawn(self, x, y, dx, dy, **kwargs):
        self.bullets.append(Bullet(x, y, dx, dy, **kwargs))

# --- KING PATTERNS (Chapter 1 Boss) ---

class KingSpadePattern(BulletPattern):
    """King's spade bullet barrage"""
    def __init__(self):
        super().__init__(duration=360)
        self.spawn_timer = 0
        
    def update(self, soul_x, soul_y):
        super().update(soul_x, soul_y)
        self.spawn_timer += 1
        if self.spawn_timer >= 15 and self.timer < 300:
            self.spawn_timer = 0
            # Rain spades from top
            for _ in range(3):
                x = random.randint(BATTLE_BOX_X + 20, BATTLE_BOX_X + BATTLE_BOX_W - 20)
                self.spawn(x, BATTLE_BOX_Y, 0, 3, color=BLUE, damage=8)

class KingChainPattern(BulletPattern):
    """King's chain attack - sweeping chains"""
    def __init__(self):
        super().__init__(duration=300)
        self.chain_x = BATTLE_BOX_X
        self.chain_dir = 1
        
    def update(self, soul_x, soul_y):
        super().update(soul_x, soul_y)
        self.chain_x += 4 * self.chain_dir
        if self.chain_x > BATTLE_BOX_X + BATTLE_BOX_W - 20:
            self.chain_dir = -1
        elif self.chain_x < BATTLE_BOX_X + 20:
            self.chain_dir = 1
            
        if self.timer % 3 == 0:
            self.spawn(self.chain_x, BATTLE_BOX_Y + BATTLE_BOX_H, 0, -4, color=PURPLE, damage=10)
            
    def draw(self, screen):
        super().draw(screen)
        # Draw chain line
        pygame.draw.line(screen, PURPLE, 
            (self.chain_x, BATTLE_BOX_Y + BATTLE_BOX_H),
            (self.chain_x, BATTLE_BOX_Y + BATTLE_BOX_H + 50), 3)

# --- JEVIL PATTERNS (Chapter 1 Secret Boss) ---

class JevilCarouselPattern(BulletPattern):
    """Jevil's carousel attack"""
    def __init__(self):
        super().__init__(duration=480)
        self.angle = 0
        self.horses = []
        for i in range(4):
            self.horses.append({
                'angle': i * math.pi / 2,
                'dist': 80,
                'y_offset': 0
            })
            
    def update(self, soul_x, soul_y):
        super().update(soul_x, soul_y)
        self.angle += 0.03
        cx = BATTLE_BOX_X + BATTLE_BOX_W // 2
        cy = BATTLE_BOX_Y + BATTLE_BOX_H // 2
        
        for horse in self.horses:
            horse['angle'] += 0.03
            horse['y_offset'] = math.sin(self.timer * 0.1 + horse['angle']) * 20
            
        # Spawn bullets from horses
        if self.timer % 20 == 0:
            for horse in self.horses:
                hx = cx + math.cos(horse['angle']) * horse['dist']
                hy = cy + math.sin(horse['angle']) * horse['dist'] + horse['y_offset']
                # Aim at soul
                dx = soul_x - hx
                dy = soul_y - hy
                dist = math.sqrt(dx*dx + dy*dy)
                if dist > 0:
                    self.spawn(hx, hy, dx/dist * 3, dy/dist * 3, color=MAGENTA, damage=8)
                    
    def draw(self, screen):
        super().draw(screen)
        cx = BATTLE_BOX_X + BATTLE_BOX_W // 2
        cy = BATTLE_BOX_Y + BATTLE_BOX_H // 2
        for horse in self.horses:
            hx = cx + math.cos(horse['angle']) * horse['dist']
            hy = cy + math.sin(horse['angle']) * horse['dist'] + horse['y_offset']
            pygame.draw.rect(screen, MAGENTA, (hx - 10, hy - 15, 20, 30))
            pygame.draw.rect(screen, WHITE, (hx - 10, hy - 15, 20, 30), 2)

class JevilDevilsKnifePattern(BulletPattern):
    """Jevil's signature attack"""
    def __init__(self):
        super().__init__(duration=420)
        self.knife_timer = 0
        
    def update(self, soul_x, soul_y):
        super().update(soul_x, soul_y)
        self.knife_timer += 1
        
        if self.knife_timer >= 30 and self.timer < 360:
            self.knife_timer = 0
            # Spawn knife from random side aimed at player
            side = random.randint(0, 3)
            if side == 0:
                x, y = random.randint(BATTLE_BOX_X, BATTLE_BOX_X + BATTLE_BOX_W), BATTLE_BOX_Y - 10
            elif side == 1:
                x, y = random.randint(BATTLE_BOX_X, BATTLE_BOX_X + BATTLE_BOX_W), BATTLE_BOX_Y + BATTLE_BOX_H + 10
            elif side == 2:
                x, y = BATTLE_BOX_X - 10, random.randint(BATTLE_BOX_Y, BATTLE_BOX_Y + BATTLE_BOX_H)
            else:
                x, y = BATTLE_BOX_X + BATTLE_BOX_W + 10, random.randint(BATTLE_BOX_Y, BATTLE_BOX_Y + BATTLE_BOX_H)
                
            dx = soul_x - x
            dy = soul_y - y
            dist = math.sqrt(dx*dx + dy*dy)
            if dist > 0:
                self.spawn(x, y, dx/dist * 5, dy/dist * 5, color=RED, radius=10, damage=12)

class JevilChaosPattern(BulletPattern):
    """CHAOS CHAOS! - Multiple spiral pattern"""
    def __init__(self):
        super().__init__(duration=480)
        self.spiral_angle = 0
        
    def update(self, soul_x, soul_y):
        super().update(soul_x, soul_y)
        
        if self.timer % 4 == 0 and self.timer < 400:
            cx = BATTLE_BOX_X + BATTLE_BOX_W // 2
            cy = BATTLE_BOX_Y + BATTLE_BOX_H // 2
            
            for offset in [0, math.pi * 2/3, math.pi * 4/3]:
                angle = self.spiral_angle + offset
                self.spawn(cx, cy, 
                    math.cos(angle) * 3, math.sin(angle) * 3,
                    color=random.choice([MAGENTA, CYAN, YELLOW]), damage=6)
            self.spiral_angle += 0.2

# --- SPAMTON NEO PATTERNS (Chapter 2 Secret Boss) ---

class SpamtonPipisPattern(BulletPattern):
    """Spamton's PIPIS attack"""
    def __init__(self):
        super().__init__(duration=360)
        self.pipis = []
        
    def update(self, soul_x, soul_y):
        super().update(soul_x, soul_y)
        
        # Spawn pipis (eggs that fall and explode)
        if self.timer % 60 == 0 and self.timer < 240:
            x = random.randint(BATTLE_BOX_X + 30, BATTLE_BOX_X + BATTLE_BOX_W - 30)
            self.pipis.append({'x': x, 'y': BATTLE_BOX_Y, 'vy': 2, 'exploded': False})
            
        # Update pipis
        for p in self.pipis[:]:
            if not p['exploded']:
                p['y'] += p['vy']
                if p['y'] > BATTLE_BOX_Y + BATTLE_BOX_H - 20:
                    p['exploded'] = True
                    # Explode into bullets
                    for angle in range(0, 360, 45):
                        rad = math.radians(angle)
                        self.spawn(p['x'], p['y'], math.cos(rad) * 3, math.sin(rad) * 3, 
                            color=LIGHT_BLUE, damage=7)
            else:
                self.pipis.remove(p)
                
    def draw(self, screen):
        super().draw(screen)
        for p in self.pipis:
            if not p['exploded']:
                pygame.draw.ellipse(screen, LIGHT_BLUE, (p['x'] - 8, p['y'] - 10, 16, 20))
                pygame.draw.ellipse(screen, WHITE, (p['x'] - 8, p['y'] - 10, 16, 20), 2)

class SpamtonPhonePattern(BulletPattern):
    """BIG SHOT phone attack"""
    def __init__(self):
        super().__init__(duration=300)
        self.phones = []
        
    def update(self, soul_x, soul_y):
        super().update(soul_x, soul_y)
        
        if self.timer % 40 == 0 and self.timer < 240:
            # Phones come from sides
            side = random.choice([-1, 1])
            x = BATTLE_BOX_X if side == -1 else BATTLE_BOX_X + BATTLE_BOX_W
            y = random.randint(BATTLE_BOX_Y + 20, BATTLE_BOX_Y + BATTLE_BOX_H - 20)
            self.phones.append({'x': x, 'y': y, 'vx': side * 4, 'timer': 0})
            
        for phone in self.phones[:]:
            phone['x'] += phone['vx']
            phone['timer'] += 1
            
            # Shoot at player periodically
            if phone['timer'] % 20 == 0:
                dx = soul_x - phone['x']
                dy = soul_y - phone['y']
                dist = math.sqrt(dx*dx + dy*dy)
                if dist > 0:
                    self.spawn(phone['x'], phone['y'], dx/dist * 4, dy/dist * 4,
                        color=YELLOW, damage=8)
                        
            if phone['x'] < BATTLE_BOX_X - 50 or phone['x'] > BATTLE_BOX_X + BATTLE_BOX_W + 50:
                self.phones.remove(phone)
                
    def draw(self, screen):
        super().draw(screen)
        for phone in self.phones:
            pygame.draw.rect(screen, YELLOW, (phone['x'] - 10, phone['y'] - 15, 20, 30))
            pygame.draw.rect(screen, WHITE, (phone['x'] - 10, phone['y'] - 15, 20, 30), 2)

class SpamtonBigShotPattern(BulletPattern):
    """NOW'S YOUR CHANCE TO BE A [[BIG SHOT]]"""
    def __init__(self):
        super().__init__(duration=480)
        
    def update(self, soul_x, soul_y):
        super().update(soul_x, soul_y)
        
        # Giant projectiles + small spam
        if self.timer % 60 == 0 and self.timer < 360:
            # BIG shot from center top
            self.spawn(BATTLE_BOX_X + BATTLE_BOX_W // 2, BATTLE_BOX_Y,
                0, 2, color=PINK, radius=20, damage=15)
                
        if self.timer % 8 == 0 and self.timer < 400:
            # Small spam from sides
            x = random.choice([BATTLE_BOX_X, BATTLE_BOX_X + BATTLE_BOX_W])
            y = random.randint(BATTLE_BOX_Y, BATTLE_BOX_Y + BATTLE_BOX_H)
            dx = 3 if x == BATTLE_BOX_X else -3
            self.spawn(x, y, dx, random.uniform(-1, 1), color=NEON_GREEN, radius=4, damage=5)

# --- QUEEN PATTERNS (Chapter 2 Boss) ---

class QueenWirePattern(BulletPattern):
    """Queen's electric wire attack"""
    def __init__(self):
        super().__init__(duration=360)
        self.wires = []
        
    def update(self, soul_x, soul_y):
        super().update(soul_x, soul_y)
        
        if self.timer % 90 == 0 and self.timer < 270:
            # Create horizontal wire
            y = random.randint(BATTLE_BOX_Y + 20, BATTLE_BOX_Y + BATTLE_BOX_H - 20)
            self.wires.append({'y': y, 'active_timer': 60, 'warned': False})
            
        for wire in self.wires[:]:
            wire['active_timer'] -= 1
            if wire['active_timer'] <= 0:
                # Wire activates - spawn damaging line
                for x in range(BATTLE_BOX_X, BATTLE_BOX_X + BATTLE_BOX_W, 20):
                    self.spawn(x, wire['y'], 0, 0, color=CYAN, radius=8, damage=10)
                self.wires.remove(wire)
                
    def draw(self, screen):
        super().draw(screen)
        for wire in self.wires:
            alpha = 255 if wire['active_timer'] < 20 else 100
            color = (0, 255, 255) if wire['active_timer'] < 20 else (100, 100, 255)
            pygame.draw.line(screen, color,
                (BATTLE_BOX_X, wire['y']), (BATTLE_BOX_X + BATTLE_BOX_W, wire['y']), 3)

class QueenAcidPattern(BulletPattern):
    """Queen's battery acid"""
    def __init__(self):
        super().__init__(duration=300)
        
    def update(self, soul_x, soul_y):
        super().update(soul_x, soul_y)
        
        if self.timer % 12 == 0 and self.timer < 260:
            # Acid drops from random positions
            x = random.randint(BATTLE_BOX_X + 10, BATTLE_BOX_X + BATTLE_BOX_W - 10)
            self.spawn(x, BATTLE_BOX_Y, 0, 2.5, color=NEON_GREEN, damage=7)
            
        # Acid pools at bottom
        if self.timer % 40 == 0:
            x = random.randint(BATTLE_BOX_X + 20, BATTLE_BOX_X + BATTLE_BOX_W - 20)
            for i in range(5):
                self.spawn(x + i * 8 - 16, BATTLE_BOX_Y + BATTLE_BOX_H - 10,
                    0, 0, color=NEON_GREEN, radius=4, damage=5)

# --- BASIC ENEMY PATTERNS ---

class BasicCirclePattern(BulletPattern):
    def __init__(self):
        super().__init__(duration=240)
        self.spawn_timer = 0
        
    def update(self, soul_x, soul_y):
        super().update(soul_x, soul_y)
        self.spawn_timer += 1
        if self.spawn_timer >= 40 and self.timer < 200:
            self.spawn_timer = 0
            cx = BATTLE_BOX_X + BATTLE_BOX_W // 2
            cy = BATTLE_BOX_Y + BATTLE_BOX_H // 2
            for i in range(8):
                angle = 2 * math.pi * i / 8 + self.timer * 0.02
                self.spawn(cx, cy, math.cos(angle) * 2.5, math.sin(angle) * 2.5, color=WHITE)

class BasicRainPattern(BulletPattern):
    def __init__(self):
        super().__init__(duration=240)
        
    def update(self, soul_x, soul_y):
        super().update(soul_x, soul_y)
        if self.timer % 10 == 0 and self.timer < 200:
            x = random.randint(BATTLE_BOX_X + 10, BATTLE_BOX_X + BATTLE_BOX_W - 10)
            self.spawn(x, BATTLE_BOX_Y, 0, 3, color=CYAN)

class DiamondPattern(BulletPattern):
    """For Rudinn enemies"""
    def __init__(self):
        super().__init__(duration=240)
        
    def update(self, soul_x, soul_y):
        super().update(soul_x, soul_y)
        if self.timer % 30 == 0 and self.timer < 200:
            # Diamond shape bullets
            cx = random.randint(BATTLE_BOX_X + 50, BATTLE_BOX_X + BATTLE_BOX_W - 50)
            for angle in [0, 90, 180, 270]:
                rad = math.radians(angle)
                self.spawn(cx, BATTLE_BOX_Y + 20, math.cos(rad) * 2, math.sin(rad) * 2 + 1.5, 
                    color=CYAN, radius=8)

class HeartPattern(BulletPattern):
    """For Hathy enemies"""
    def __init__(self):
        super().__init__(duration=240)
        
    def update(self, soul_x, soul_y):
        super().update(soul_x, soul_y)
        if self.timer % 25 == 0 and self.timer < 200:
            x = random.randint(BATTLE_BOX_X + 20, BATTLE_BOX_X + BATTLE_BOX_W - 20)
            self.spawn(x, BATTLE_BOX_Y, random.uniform(-0.5, 0.5), 2.5, color=PINK, radius=7)

# Pattern registry
PATTERNS = {
    'basic_circle': BasicCirclePattern,
    'basic_rain': BasicRainPattern,
    'diamond': DiamondPattern,
    'heart': HeartPattern,
    'king_spade': KingSpadePattern,
    'king_chain': KingChainPattern,
    'jevil_carousel': JevilCarouselPattern,
    'jevil_knife': JevilDevilsKnifePattern,
    'jevil_chaos': JevilChaosPattern,
    'spamton_pipis': SpamtonPipisPattern,
    'spamton_phone': SpamtonPhonePattern,
    'spamton_bigshot': SpamtonBigShotPattern,
    'queen_wire': QueenWirePattern,
    'queen_acid': QueenAcidPattern,
}

def get_pattern(name: str) -> BulletPattern:
    return PATTERNS.get(name, BasicCirclePattern)()

# =============================================================================
# DIALOGUE SYSTEM
# =============================================================================

class DialogueBox:
    def __init__(self):
        self.active = False
        self.lines: List[DialogueLine] = []
        self.current_line = 0
        self.char_index = 0
        self.char_timer = 0
        self.char_delay = 2
        self.finished_line = False
        self.callback: Optional[Callable] = None
        
    def start(self, lines: List[DialogueLine], callback=None):
        self.lines = lines
        self.current_line = 0
        self.char_index = 0
        self.char_timer = 0
        self.finished_line = False
        self.active = True
        self.callback = callback
        
    def update(self):
        if not self.active or not self.lines:
            return
        if not self.finished_line:
            self.char_timer += 1
            if self.char_timer >= self.char_delay:
                self.char_timer = 0
                self.char_index += 1
                if self.char_index >= len(self.lines[self.current_line].text):
                    self.finished_line = True
                    
    def advance(self) -> bool:
        if not self.finished_line:
            self.char_index = len(self.lines[self.current_line].text)
            self.finished_line = True
            return False
        else:
            self.current_line += 1
            if self.current_line >= len(self.lines):
                self.active = False
                if self.callback:
                    self.callback()
                return True
            self.char_index = 0
            self.finished_line = False
            return False
            
    def draw(self, screen, font):
        if not self.active or not self.lines:
            return
            
        box = pygame.Rect(32, HEIGHT - 150, WIDTH - 64, 130)
        pygame.draw.rect(screen, BLACK, box)
        pygame.draw.rect(screen, WHITE, box, 3)
        
        line = self.lines[self.current_line]
        
        # Speaker name
        if line.speaker:
            color = self._get_speaker_color(line.speaker)
            name_surf = font.render(f"* {line.speaker}", True, color)
            screen.blit(name_surf, (50, HEIGHT - 140))
            text_y = HEIGHT - 115
        else:
            text_y = HEIGHT - 135
            
        # Text with typewriter
        text = line.text[:self.char_index]
        words = text.split(' ')
        render_lines = []
        current = ""
        for word in words:
            test = current + " " + word if current else word
            if font.size(test)[0] < box.width - 50:
                current = test
            else:
                render_lines.append(current)
                current = word
        if current:
            render_lines.append(current)
            
        for i, txt in enumerate(render_lines[:3]):
            prefix = "* " if i == 0 and not line.speaker else "  "
            surf = font.render(prefix + txt, True, WHITE)
            screen.blit(surf, (50, text_y + i * 25))
            
        # Continue indicator
        if self.finished_line:
            ind = "▼" if self.current_line < len(self.lines) - 1 else "■"
            ind_surf = font.render(ind, True, YELLOW)
            screen.blit(ind_surf, (box.right - 30, box.bottom - 25))
            
    def _get_speaker_color(self, name):
        colors = {
            "Kris": BLUE, "Susie": PURPLE, "Ralsei": GREEN,
            "Lancer": BLUE, "King": DARK_GREEN, "Jevil": MAGENTA,
            "Noelle": YELLOW, "Berdly": CYAN, "Queen": CYAN,
            "Spamton": PINK, "Rouxls": BLUE
        }
        return colors.get(name, WHITE)

# =============================================================================
# BATTLE SYSTEM
# =============================================================================

class BattleSystem:
    def __init__(self, party: List[PartyMember], enemies: List[Enemy]):
        self.party = party
        self.enemies = enemies
        self.state = BattleState.SELECTING_MEMBER
        
        # Selection indices
        self.current_member = 0
        self.selected_action = 0
        self.selected_target = 0
        self.selected_act = 0
        self.selected_item = 0
        self.selected_spell = 0
        
        # Soul
        self.soul_x = BATTLE_BOX_X + BATTLE_BOX_W // 2
        self.soul_y = BATTLE_BOX_Y + BATTLE_BOX_H // 2
        self.invincibility = 0
        
        # Pattern
        self.pattern: Optional[BulletPattern] = None
        
        # TP
        self.tp = 0
        self.max_tp = 100
        
        # Dialogue
        self.dialogue = DialogueBox()
        
        # Items
        self.inventory: List[Item] = []
        
        # Messages
        self.message = ""
        self.message_timer = 0
        
        # Turns taken
        self.members_acted = []
        
        # Enemy shake effect
        self.enemy_shake = [0] * len(enemies)
        
    def update(self, keys_held, keys_pressed):
        if self.invincibility > 0:
            self.invincibility -= 1
            
        # Handle dialogue
        if self.dialogue.active:
            self.dialogue.update()
            if keys_pressed.get(pygame.K_z):
                self.dialogue.advance()
            return None
            
        # Message timer
        if self.message_timer > 0:
            self.message_timer -= 1
            if self.message_timer == 0:
                self.message = ""
                
        # State handling
        if self.state == BattleState.SELECTING_MEMBER:
            self._handle_member_select(keys_pressed)
        elif self.state == BattleState.SELECTING_ACTION:
            self._handle_action_select(keys_pressed)
        elif self.state == BattleState.SELECTING_TARGET:
            self._handle_target_select(keys_pressed)
        elif self.state == BattleState.SELECTING_ACT:
            self._handle_act_select(keys_pressed)
        elif self.state == BattleState.SELECTING_ITEM:
            self._handle_item_select(keys_pressed)
        elif self.state == BattleState.SELECTING_MAGIC:
            self._handle_magic_select(keys_pressed)
        elif self.state == BattleState.ENEMY_TURN:
            self._handle_enemy_turn(keys_held)
        elif self.state == BattleState.VICTORY:
            if keys_pressed.get(pygame.K_z):
                return "victory"
        elif self.state == BattleState.SPARE:
            if keys_pressed.get(pygame.K_z):
                return "spare"
        elif self.state == BattleState.GAME_OVER:
            if keys_pressed.get(pygame.K_z):
                return "game_over"
                
        # Update enemy shake
        for i in range(len(self.enemy_shake)):
            if self.enemy_shake[i] > 0:
                self.enemy_shake[i] -= 1
                
        return None
        
    def _handle_member_select(self, keys):
        # Find next party member who hasn't acted
        available = [i for i, m in enumerate(self.party) if i not in self.members_acted and not m.down]
        if not available:
            # All acted, start enemy turn
            self.members_acted = []
            self._start_enemy_turn()
            return
            
        if keys.get(pygame.K_LEFT) or keys.get(pygame.K_a):
            idx = available.index(self.current_member) if self.current_member in available else 0
            idx = (idx - 1) % len(available)
            self.current_member = available[idx]
        if keys.get(pygame.K_RIGHT) or keys.get(pygame.K_d):
            idx = available.index(self.current_member) if self.current_member in available else 0
            idx = (idx + 1) % len(available)
            self.current_member = available[idx]
        if keys.get(pygame.K_z) or keys.get(pygame.K_RETURN) or keys.get(pygame.K_SPACE):
            self.state = BattleState.SELECTING_ACTION
            self.selected_action = 0
            
    def _handle_action_select(self, keys):
        member = self.party[self.current_member]
        actions = ["FIGHT", "ACT", "ITEM", "SPARE"]
        if member.spells:
            actions.insert(2, "MAGIC")
            
        if keys.get(pygame.K_LEFT) or keys.get(pygame.K_a):
            self.selected_action = (self.selected_action - 1) % len(actions)
        if keys.get(pygame.K_RIGHT) or keys.get(pygame.K_d):
            self.selected_action = (self.selected_action + 1) % len(actions)
        if keys.get(pygame.K_z) or keys.get(pygame.K_RETURN) or keys.get(pygame.K_SPACE):
            action = actions[self.selected_action]
            if action == "FIGHT":
                self.state = BattleState.SELECTING_TARGET
                self.selected_target = 0
            elif action == "ACT":
                self.state = BattleState.SELECTING_TARGET
                self.selected_target = 0
            elif action == "MAGIC":
                self.state = BattleState.SELECTING_MAGIC
                self.selected_spell = 0
            elif action == "ITEM":
                if self.inventory:
                    self.state = BattleState.SELECTING_ITEM
                    self.selected_item = 0
            elif action == "SPARE":
                self._do_spare()
        if keys.get(pygame.K_x):
            self.state = BattleState.SELECTING_MEMBER
            
    def _handle_target_select(self, keys):
        alive = [e for e in self.enemies if not e.defeated]
        if keys.get(pygame.K_UP) or keys.get(pygame.K_w):
            self.selected_target = (self.selected_target - 1) % len(alive)
        if keys.get(pygame.K_DOWN) or keys.get(pygame.K_s):
            self.selected_target = (self.selected_target + 1) % len(alive)
        if keys.get(pygame.K_z) or keys.get(pygame.K_RETURN) or keys.get(pygame.K_SPACE):
            if self.selected_action == 0:  # FIGHT
                self._do_attack(self.selected_target)
            else:  # ACT
                self.state = BattleState.SELECTING_ACT
                self.selected_act = 0
        if keys.get(pygame.K_x):
            self.state = BattleState.SELECTING_ACTION
            
    def _handle_act_select(self, keys):
        alive = [e for e in self.enemies if not e.defeated]
        enemy = alive[self.selected_target]
        acts = ["Check"] + list(enemy.acts.keys())
        
        if keys.get(pygame.K_UP) or keys.get(pygame.K_w):
            self.selected_act = (self.selected_act - 1) % len(acts)
        if keys.get(pygame.K_DOWN) or keys.get(pygame.K_s):
            self.selected_act = (self.selected_act + 1) % len(acts)
        if keys.get(pygame.K_z) or keys.get(pygame.K_RETURN) or keys.get(pygame.K_SPACE):
            self._do_act(self.selected_target, acts[self.selected_act])
        if keys.get(pygame.K_x):
            self.state = BattleState.SELECTING_TARGET
            
    def _handle_item_select(self, keys):
        if not self.inventory:
            self.state = BattleState.SELECTING_ACTION
            return
            
        if keys.get(pygame.K_UP) or keys.get(pygame.K_w):
            self.selected_item = (self.selected_item - 1) % len(self.inventory)
        if keys.get(pygame.K_DOWN) or keys.get(pygame.K_s):
            self.selected_item = (self.selected_item + 1) % len(self.inventory)
        if keys.get(pygame.K_z) or keys.get(pygame.K_RETURN) or keys.get(pygame.K_SPACE):
            self._use_item(self.selected_item)
        if keys.get(pygame.K_x):
            self.state = BattleState.SELECTING_ACTION
            
    def _handle_magic_select(self, keys):
        member = self.party[self.current_member]
        if not member.spells:
            self.state = BattleState.SELECTING_ACTION
            return
            
        if keys.get(pygame.K_UP) or keys.get(pygame.K_w):
            self.selected_spell = (self.selected_spell - 1) % len(member.spells)
        if keys.get(pygame.K_DOWN) or keys.get(pygame.K_s):
            self.selected_spell = (self.selected_spell + 1) % len(member.spells)
        if keys.get(pygame.K_z) or keys.get(pygame.K_RETURN) or keys.get(pygame.K_SPACE):
            spell = member.spells[self.selected_spell]
            if self.tp >= spell.tp_cost:
                self._do_spell(spell)
            else:
                self.message = "Not enough TP!"
                self.message_timer = 60
        if keys.get(pygame.K_x):
            self.state = BattleState.SELECTING_ACTION
            
    def _handle_enemy_turn(self, keys):
        # Soul movement - support arrows and WASD
        speed = SOUL_SPEED
        if keys.get(pygame.K_LSHIFT) or keys.get(pygame.K_x):
            speed = SOUL_SPEED // 2
            
        dx = dy = 0
        if keys.get(pygame.K_LEFT) or keys.get(pygame.K_a): dx = -speed
        if keys.get(pygame.K_RIGHT) or keys.get(pygame.K_d): dx = speed
        if keys.get(pygame.K_UP) or keys.get(pygame.K_w): dy = -speed
        if keys.get(pygame.K_DOWN) or keys.get(pygame.K_s): dy = speed
        
        margin = SOUL_SIZE // 2
        new_x = self.soul_x + dx
        new_y = self.soul_y + dy
        if BATTLE_BOX_X + margin < new_x < BATTLE_BOX_X + BATTLE_BOX_W - margin:
            self.soul_x = new_x
        if BATTLE_BOX_Y + margin < new_y < BATTLE_BOX_Y + BATTLE_BOX_H - margin:
            self.soul_y = new_y
            
        # Update pattern
        if self.pattern:
            self.pattern.update(self.soul_x, self.soul_y)
            
            # Check collisions
            if self.invincibility == 0:
                for bullet in self.pattern.bullets:
                    dx = self.soul_x - bullet.x
                    dy = self.soul_y - bullet.y
                    dist = math.sqrt(dx*dx + dy*dy)
                    if dist < SOUL_SIZE // 2 + bullet.radius - 2:
                        self._take_damage(bullet.damage)
                        bullet.alive = False
                    elif not bullet.grazed and dist < SOUL_SIZE + bullet.radius:
                        bullet.grazed = True
                        self.tp = min(self.max_tp, self.tp + 2)
                        
            if self.pattern.finished:
                self.pattern = None
                self._next_player_turn()
                
    def _do_attack(self, target_idx):
        alive = [e for e in self.enemies if not e.defeated]
        enemy = alive[target_idx]
        member = self.party[self.current_member]
        
        damage = max(1, member.stats.atk - enemy.stats.defense + random.randint(-2, 2))
        enemy.stats.hp -= damage
        
        actual_idx = self.enemies.index(enemy)
        self.enemy_shake[actual_idx] = 15
        
        self.message = f"{member.name} attacked! {damage} damage!"
        self.message_timer = 60
        
        self.members_acted.append(self.current_member)
        
        if enemy.stats.hp <= 0:
            enemy.defeated = True
            self._check_battle_end()
        else:
            self._check_next_action()
            
    def _do_act(self, target_idx, act_name):
        alive = [e for e in self.enemies if not e.defeated]
        enemy = alive[target_idx]
        member = self.party[self.current_member]
        
        if act_name == "Check":
            lines = [
                DialogueLine("", f"* {enemy.name} - ATK {enemy.stats.atk} DEF {enemy.stats.defense}"),
                DialogueLine("", f"* {enemy.check_text}")
            ]
            self.dialogue.start(lines)
        else:
            response, mercy_gain = enemy.acts.get(act_name, ("...", 5))
            enemy.mercy = min(100, enemy.mercy + mercy_gain)
            
            lines = [
                DialogueLine("", f"* {member.name} used {act_name}!"),
                DialogueLine(enemy.name, response) if response else DialogueLine("", "* ...")
            ]
            self.dialogue.start(lines)
            
        self.tp = min(self.max_tp, self.tp + 10)
        self.members_acted.append(self.current_member)
        self._check_next_action()
        
    def _do_spell(self, spell):
        member = self.party[self.current_member]
        self.tp -= spell.tp_cost
        
        if spell.effect == "heal":
            # Heal all party members
            for m in self.party:
                heal = min(spell.power, m.stats.max_hp - m.stats.hp)
                m.stats.hp += heal
            self.message = f"{member.name} cast {spell.name}!"
        elif spell.effect == "damage":
            # Damage all enemies
            for e in self.enemies:
                if not e.defeated:
                    damage = max(1, spell.power + member.stats.magic - e.stats.defense)
                    e.stats.hp -= damage
                    if e.stats.hp <= 0:
                        e.defeated = True
            self.message = f"{member.name} cast {spell.name}!"
        elif spell.effect == "pacify":
            # Increase mercy on tired enemies
            for e in self.enemies:
                if e.tired and not e.defeated:
                    e.mercy = 100
            self.message = f"{member.name} cast {spell.name}!"
            
        self.message_timer = 60
        self.members_acted.append(self.current_member)
        self._check_battle_end()
        self._check_next_action()
        
    def _do_spare(self):
        spared = []
        for enemy in self.enemies:
            if not enemy.defeated and enemy.mercy >= enemy.spare_threshold:
                enemy.defeated = True
                spared.append(enemy.name)
                
        if spared:
            self.message = f"YOU SPARED {', '.join(spared)}!"
            self.message_timer = 90
            self._check_battle_end()
        else:
            self.message = "But nobody wanted to be spared..."
            self.message_timer = 60
            
        self.members_acted.append(self.current_member)
        self._check_next_action()
        
    def _use_item(self, item_idx):
        item = self.inventory[item_idx]
        member = self.party[self.current_member]
        
        if item.heal_hp > 0:
            heal = min(item.heal_hp, member.stats.max_hp - member.stats.hp)
            member.stats.hp += heal
            self.message = f"{member.name} used {item.name}! Recovered {heal} HP!"
        elif item.heal_tp > 0:
            self.tp = min(self.max_tp, self.tp + item.heal_tp)
            self.message = f"Used {item.name}! Recovered {item.heal_tp} TP!"
            
        if not item.is_key:
            self.inventory.pop(item_idx)
            
        self.message_timer = 60
        self.members_acted.append(self.current_member)
        self._check_next_action()
        
    def _take_damage(self, amount):
        target = self.party[self.current_member]
        damage = max(1, amount - target.stats.defense // 4)
        target.stats.hp -= damage
        self.invincibility = 60
        
        if target.stats.hp <= 0:
            target.stats.hp = 0
            target.down = True
            if all(m.down for m in self.party):
                self.state = BattleState.GAME_OVER
                
    def _start_enemy_turn(self):
        alive = [e for e in self.enemies if not e.defeated]
        if not alive:
            return
            
        attacker = random.choice(alive)
        
        if attacker.flavor_texts:
            self.message = f"* {random.choice(attacker.flavor_texts)}"
            self.message_timer = 60
            
        if attacker.attacks:
            pattern_name = random.choice(attacker.attacks)
            self.pattern = get_pattern(pattern_name)
        else:
            self.pattern = get_pattern('basic_circle')
            
        self.soul_x = BATTLE_BOX_X + BATTLE_BOX_W // 2
        self.soul_y = BATTLE_BOX_Y + BATTLE_BOX_H // 2
        self.state = BattleState.ENEMY_TURN
        
    def _next_player_turn(self):
        self.state = BattleState.SELECTING_MEMBER
        available = [i for i, m in enumerate(self.party) if i not in self.members_acted and not m.down]
        if available:
            self.current_member = available[0]
        else:
            self.members_acted = []
            self._start_enemy_turn()
            
    def _check_next_action(self):
        available = [i for i, m in enumerate(self.party) if i not in self.members_acted and not m.down]
        if available:
            self.current_member = available[0]
            self.state = BattleState.SELECTING_MEMBER
        else:
            self.members_acted = []
            self._start_enemy_turn()
            
    def _check_battle_end(self):
        alive = [e for e in self.enemies if not e.defeated]
        if not alive:
            # Check if any were spared
            any_spared = any(e.mercy >= e.spare_threshold for e in self.enemies)
            self.state = BattleState.SPARE if any_spared else BattleState.VICTORY
            
    def draw(self, screen, font):
        screen.fill(BLACK)
        
        # Draw enemies
        alive_enemies = [e for e in self.enemies if not e.defeated]
        spacing = WIDTH // (len(alive_enemies) + 1) if alive_enemies else WIDTH // 2
        for i, enemy in enumerate(alive_enemies):
            x = spacing * (i + 1) - 40
            y = 50
            actual_idx = self.enemies.index(enemy)
            shake = random.randint(-3, 3) if self.enemy_shake[actual_idx] > 0 else 0
            
            # Enemy sprite (box for now)
            size = 80 if enemy.is_boss else 64
            pygame.draw.rect(screen, enemy.color, (x + shake, y, size, size))
            pygame.draw.rect(screen, WHITE, (x + shake, y, size, size), 2)
            
            # Name
            name_surf = font.render(enemy.name, True, WHITE)
            screen.blit(name_surf, (x + size//2 - name_surf.get_width()//2, y + size + 5))
            
            # HP bar
            hp_w = 70
            hp_h = 8
            hp_x = x + size//2 - hp_w//2
            hp_y = y + size + 25
            pygame.draw.rect(screen, RED, (hp_x, hp_y, hp_w, hp_h))
            hp_fill = max(0, int((enemy.stats.hp / enemy.stats.max_hp) * hp_w))
            pygame.draw.rect(screen, GREEN, (hp_x, hp_y, hp_fill, hp_h))
            
            # Mercy
            if enemy.mercy > 0:
                mercy_text = f"[{enemy.mercy}%]" if enemy.mercy < 100 else "[SPARE]"
                color = YELLOW if enemy.mercy >= 100 else WHITE
                mercy_surf = font.render(mercy_text, True, color)
                screen.blit(mercy_surf, (x + size//2 - mercy_surf.get_width()//2, hp_y + 12))
                
        # Battle box
        pygame.draw.rect(screen, BLACK, (BATTLE_BOX_X, BATTLE_BOX_Y, BATTLE_BOX_W, BATTLE_BOX_H))
        pygame.draw.rect(screen, WHITE, (BATTLE_BOX_X, BATTLE_BOX_Y, BATTLE_BOX_W, BATTLE_BOX_H), 3)
        
        # Battle content
        if self.state == BattleState.ENEMY_TURN:
            # Draw soul
            if self.invincibility == 0 or self.invincibility % 4 < 2:
                pygame.draw.polygon(screen, RED, [
                    (self.soul_x, self.soul_y + SOUL_SIZE//2),
                    (self.soul_x - SOUL_SIZE//2, self.soul_y - SOUL_SIZE//4),
                    (self.soul_x, self.soul_y - SOUL_SIZE//2 + 2),
                    (self.soul_x + SOUL_SIZE//2, self.soul_y - SOUL_SIZE//4)
                ])
            # Draw bullets
            if self.pattern:
                self.pattern.draw(screen)
        else:
            # Message
            if self.message:
                msg_surf = font.render(self.message, True, WHITE)
                screen.blit(msg_surf, (BATTLE_BOX_X + 20, BATTLE_BOX_Y + 20))
                
        # Party HP display
        party_y = HEIGHT - 80
        for i, member in enumerate(self.party):
            x = 40 + i * 200
            
            # Highlight selection
            if self.state == BattleState.SELECTING_MEMBER and i == self.current_member:
                pygame.draw.rect(screen, member.color, (x - 5, party_y - 5, 180, 70), 2)
            elif self.state in [BattleState.SELECTING_ACTION, BattleState.SELECTING_TARGET,
                               BattleState.SELECTING_ACT, BattleState.SELECTING_ITEM,
                               BattleState.SELECTING_MAGIC] and i == self.current_member:
                pygame.draw.rect(screen, YELLOW, (x - 5, party_y - 5, 180, 70), 2)
                
            # Name
            color = (100, 100, 100) if member.down else member.color
            name_surf = font.render(member.name, True, color)
            screen.blit(name_surf, (x, party_y))
            
            # HP
            hp_text = f"HP {member.stats.hp}/{member.stats.max_hp}"
            hp_surf = font.render(hp_text, True, WHITE if not member.down else (100, 100, 100))
            screen.blit(hp_surf, (x, party_y + 22))
            
            # HP bar
            bar_w = 100
            pygame.draw.rect(screen, RED, (x, party_y + 45, bar_w, 10))
            fill = int((member.stats.hp / member.stats.max_hp) * bar_w)
            pygame.draw.rect(screen, YELLOW, (x, party_y + 45, fill, 10))
            
        # TP bar
        tp_x = WIDTH - 100
        pygame.draw.rect(screen, (50, 50, 50), (tp_x, party_y, 20, 60))
        tp_fill = int((self.tp / self.max_tp) * 60)
        pygame.draw.rect(screen, ORANGE, (tp_x, party_y + 60 - tp_fill, 20, tp_fill))
        tp_label = font.render("TP", True, ORANGE)
        screen.blit(tp_label, (tp_x, party_y - 20))
        tp_val = font.render(f"{self.tp}%", True, WHITE)
        screen.blit(tp_val, (tp_x - 10, party_y + 62))
        
        # Action menu
        if self.state == BattleState.SELECTING_ACTION:
            member = self.party[self.current_member]
            actions = ["FIGHT", "ACT", "ITEM", "SPARE"]
            if member.spells:
                actions.insert(2, "MAGIC")
            colors = [RED, YELLOW, ORANGE, GREEN, PURPLE]
            
            action_y = BATTLE_BOX_Y + BATTLE_BOX_H + 10
            spacing = BATTLE_BOX_W // len(actions)
            for i, (action, color) in enumerate(zip(actions, colors[:len(actions)])):
                x = BATTLE_BOX_X + spacing * i + spacing // 2
                text = f"[{action}]" if i == self.selected_action else action
                surf = font.render(text, True, color)
                screen.blit(surf, (x - surf.get_width()//2, action_y))
                
        # Target selection
        elif self.state in [BattleState.SELECTING_TARGET, BattleState.SELECTING_ACT]:
            alive = [e for e in self.enemies if not e.defeated]
            for i, enemy in enumerate(alive):
                y = BATTLE_BOX_Y + 20 + i * 28
                prefix = ">" if i == self.selected_target else " "
                color = YELLOW if i == self.selected_target else WHITE
                surf = font.render(f"{prefix} {enemy.name}", True, color)
                screen.blit(surf, (BATTLE_BOX_X + 20, y))
                
            # ACT list
            if self.state == BattleState.SELECTING_ACT:
                enemy = alive[self.selected_target]
                acts = ["Check"] + list(enemy.acts.keys())
                for i, act in enumerate(acts):
                    y = BATTLE_BOX_Y + 20 + i * 25
                    x = BATTLE_BOX_X + BATTLE_BOX_W // 2
                    prefix = ">" if i == self.selected_act else " "
                    color = YELLOW if i == self.selected_act else WHITE
                    surf = font.render(f"{prefix} {act}", True, color)
                    screen.blit(surf, (x, y))
                    
        # Item selection
        elif self.state == BattleState.SELECTING_ITEM:
            for i, item in enumerate(self.inventory[:5]):
                y = BATTLE_BOX_Y + 20 + i * 25
                prefix = ">" if i == self.selected_item else " "
                color = YELLOW if i == self.selected_item else WHITE
                surf = font.render(f"{prefix} {item.name}", True, color)
                screen.blit(surf, (BATTLE_BOX_X + 20, y))
                
        # Magic selection
        elif self.state == BattleState.SELECTING_MAGIC:
            member = self.party[self.current_member]
            for i, spell in enumerate(member.spells):
                y = BATTLE_BOX_Y + 20 + i * 25
                prefix = ">" if i == self.selected_spell else " "
                color = YELLOW if i == self.selected_spell else WHITE
                can_cast = self.tp >= spell.tp_cost
                if not can_cast:
                    color = (100, 100, 100)
                text = f"{prefix} {spell.name} ({spell.tp_cost} TP)"
                surf = font.render(text, True, color)
                screen.blit(surf, (BATTLE_BOX_X + 20, y))
                
        # Victory/Game Over
        if self.state == BattleState.VICTORY:
            surf = font.render("YOU WON!", True, YELLOW)
            screen.blit(surf, (WIDTH//2 - surf.get_width()//2, HEIGHT//2))
            sub = font.render("Press Z to continue", True, WHITE)
            screen.blit(sub, (WIDTH//2 - sub.get_width()//2, HEIGHT//2 + 30))
        elif self.state == BattleState.SPARE:
            surf = font.render("YOU WON!", True, YELLOW)
            screen.blit(surf, (WIDTH//2 - surf.get_width()//2, HEIGHT//2 - 20))
            sub = font.render("You showed mercy!", True, GREEN)
            screen.blit(sub, (WIDTH//2 - sub.get_width()//2, HEIGHT//2 + 10))
            cont = font.render("Press Z to continue", True, WHITE)
            screen.blit(cont, (WIDTH//2 - cont.get_width()//2, HEIGHT//2 + 40))
        elif self.state == BattleState.GAME_OVER:
            surf = font.render("GAME OVER", True, RED)
            screen.blit(surf, (WIDTH//2 - surf.get_width()//2, HEIGHT//2))
            
        # Dialogue on top
        self.dialogue.draw(screen, font)

# =============================================================================
# CHAPTER DATA - ENEMIES
# =============================================================================

def create_enemy(name: str) -> Enemy:
    """Factory for all enemies in Chapters 1 & 2"""
    
    enemies = {
        # === CHAPTER 1 ENEMIES ===
        "Rudinn": Enemy(
            name="Rudinn",
            stats=Stats(hp=70, max_hp=70, atk=8, defense=2, magic=4),
            color=CYAN,
            acts={
                "Bow": ("* Rudinn bows back respectfully.", 20),
                "Compliment": ("* Rudinn blushes slightly.", 15),
                "Flatter": ("Oh, you're too kind...", 25)
            },
            check_text="A diamond-headed warrior. Loyal to the bitter end.",
            attacks=['diamond', 'basic_rain'],
            flavor_texts=["Rudinn holds their ground!", "Rudinn adjusts their cape."]
        ),
        "Hathy": Enemy(
            name="Hathy",
            stats=Stats(hp=60, max_hp=60, atk=6, defense=1, magic=3),
            color=PINK,
            acts={
                "Flirt": ("* Hathy's hearts flutter!", 25),
                "Hug": ("* Hathy melts into the hug.", 30),
                "Dance": ("* Hathy dances along!", 20)
            },
            check_text="A heart-shaped creature. Full of love.",
            attacks=['heart', 'basic_circle'],
            flavor_texts=["Hathy floats peacefully.", "Hearts emit from Hathy."]
        ),
        "Lancer": Enemy(
            name="Lancer",
            stats=Stats(hp=150, max_hp=150, atk=10, defense=3, magic=2),
            color=BLUE,
            acts={
                "Laugh": ("Ho ho ho! You think YOU'RE funny!?", 15),
                "Insult": ("Those words... they cut deep.", 10),
                "Compliment": ("Hmph! I don't need YOUR approval!", 20)
            },
            check_text="The 'bad guy'. Son of the King.",
            attacks=['basic_circle', 'basic_rain'],
            flavor_texts=["Lancer is having fun!", "Lancer does a funny dance!"],
            is_boss=True
        ),
        "King": Enemy(
            name="King",
            stats=Stats(hp=800, max_hp=800, atk=14, defense=5, magic=5),
            color=DARK_GREEN,
            acts={
                "Plead": ("You think WORDS can stop me!?", 5),
                "Reason": ("Reason? From lightners?", 10),
                "Stand": ("...", 15)
            },
            spare_threshold=100,
            check_text="The ruthless King of Spades. Seeks to destroy the Lightners.",
            attacks=['king_spade', 'king_chain'],
            flavor_texts=[
                "King readies his attack!",
                "The King's hatred burns!",
                "King laughs maniacally!"
            ],
            is_boss=True
        ),
        "Jevil": Enemy(
            name="Jevil",
            stats=Stats(hp=2500, max_hp=2500, atk=16, defense=4, magic=10),
            color=MAGENTA,
            acts={
                "Pirouette": ("UEE HEE HEE! SPIN, SPIN!", 8),
                "Hypnosis": ("I'M... GETTING... TIRED...", 12),
                "Talk": ("CHAOS, CHAOS! I CAN DO ANYTHING!", 5)
            },
            spare_threshold=100,
            check_text="The secret boss. He can do anything!",
            attacks=['jevil_carousel', 'jevil_knife', 'jevil_chaos'],
            flavor_texts=[
                "CHAOS, CHAOS!",
                "Jevil is having the time of his life!",
                "A strange carousel plays in the distance.",
                "THE WORLD REVOLVING!"
            ],
            is_boss=True
        ),
        
        # === CHAPTER 2 ENEMIES ===
        "Tasque": Enemy(
            name="Tasque",
            stats=Stats(hp=80, max_hp=80, atk=9, defense=3, magic=5),
            color=WHITE,
            acts={
                "Pet": ("* Tasque purrs contentedly.", 25),
                "Command": ("* Tasque sits obediently.", 20),
                "Bell": ("* Tasque's ears perk up!", 30)
            },
            check_text="An orderly feline. Likes things tidy.",
            attacks=['basic_circle', 'basic_rain'],
            flavor_texts=["Tasque tidies the battlefield.", "Tasque meows orderly."]
        ),
        "Werewire": Enemy(
            name="Werewire",
            stats=Stats(hp=90, max_hp=90, atk=10, defense=2, magic=6),
            color=NEON_GREEN,
            acts={
                "Untangle": ("* Werewire feels more relaxed.", 25),
                "Pet": ("* Careful of the wires!", 15),
                "Howl": ("* Werewire howls along!", 20)
            },
            check_text="A tangled wolf-like creature.",
            attacks=['basic_rain', 'queen_wire'],
            flavor_texts=["Werewire sparks menacingly!", "Wires tangle around."]
        ),
        "Swatchling": Enemy(
            name="Swatchling",
            stats=Stats(hp=100, max_hp=100, atk=11, defense=4, magic=5),
            color=NEON_PURPLE,
            acts={
                "Request": ("* Swatchling bows and prepares.", 20),
                "Compliment": ("* Swatchling adjusts their outfit.", 15),
                "Order": ("Your order has been received.", 25)
            },
            check_text="A loyal servant. Very professional.",
            attacks=['basic_circle', 'diamond'],
            flavor_texts=["Swatchling awaits orders.", "Swatchling stands ready."]
        ),
        "Queen": Enemy(
            name="Queen",
            stats=Stats(hp=1200, max_hp=1200, atk=15, defense=6, magic=8),
            color=CYAN,
            acts={
                "Toast": ("Cheers To You Lightners lmao", 15),
                "Compliment": ("Yes I Am Amazing Thank You", 10),
                "Refuse": ("Oh Come On", 20)
            },
            spare_threshold=100,
            check_text="The ruler of the Cyber World. Loves battery acid.",
            attacks=['queen_wire', 'queen_acid'],
            flavor_texts=[
                "Queen takes a sip of battery acid.",
                "Queen laughs: Lmao",
                "Queen strikes a pose!"
            ],
            is_boss=True
        ),
        "Spamton NEO": Enemy(
            name="Spamton NEO",
            stats=Stats(hp=4000, max_hp=4000, atk=18, defense=5, magic=12),
            color=PINK,
            acts={
                "Snap Wire": ("HEY... THAT HURT, [Little Sponge]!", 10),
                "Struggle": ("I'M TRYING TO... BE A [Big Shot]!", 8),
                "Call": ("HELLO? IS ANYONE THERE?", 12)
            },
            spare_threshold=100,
            check_text="NOW'S YOUR CHANCE TO BE A [[BIG SHOT]]!",
            attacks=['spamton_pipis', 'spamton_phone', 'spamton_bigshot'],
            flavor_texts=[
                "NOW'S YOUR CHANCE TO BE A [[BIG SHOT]]!",
                "[Hyperlink Blocked]",
                "Spamton NEO's wires tangle!",
                "YOU WANT TO BE A [Big Shot]!?"
            ],
            is_boss=True
        ),
        
        # Generic training enemy
        "Dummy": Enemy(
            name="Dummy",
            stats=Stats(hp=50, max_hp=50, atk=5, defense=0, magic=0),
            color=ORANGE,
            acts={
                "Hit": ("* ...", 20),
                "Talk": ("* ...", 20),
                "Hug": ("* It doesn't hug back.", 30)
            },
            check_text="A training dummy. Doesn't do much.",
            attacks=['basic_circle'],
            flavor_texts=["Dummy stands there.", "Dummy does nothing."]
        ),
    }
    
    return enemies.get(name, enemies["Dummy"])

# =============================================================================
# CHAPTER DATA - AREAS
# =============================================================================

# Map tile types: 0=floor, 1=wall, 2=transition, 3=save, 4=npc_spawn, 5=enemy_spawn

CHAPTER1_AREAS = {
    "castle_entrance": {
        "name": "Castle Town",
        "map": [
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,3,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,1,1,1,0,0,0,0,0,0,0,1,1,1,0,0,0,1],
            [1,0,0,1,0,0,0,0,4,0,4,0,0,0,0,1,0,0,0,1],
            [1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1],
            [1,0,0,1,1,1,0,0,0,2,0,0,0,1,1,1,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        ],
        "bg_color": CASTLE_BLUE,
        "npcs": [
            {"name": "Ralsei", "x": 8, "y": 4, "color": GREEN,
             "dialogue": [
                DialogueLine("Ralsei", "Welcome to Castle Town!"),
                DialogueLine("Ralsei", "This is our base of operations."),
                DialogueLine("Ralsei", "Please, make yourself at home!")
            ]},
            {"name": "Lancer", "x": 10, "y": 4, "color": BLUE,
             "dialogue": [
                DialogueLine("Lancer", "Ho ho ho!"),
                DialogueLine("Lancer", "I'm the best bad guy around!"),
                DialogueLine("Lancer", "...Do you have any cookies?")
            ]},
        ],
        "transitions": [
            {"x": 9, "y": 10, "target": "field_start", "tx": 9, "ty": 1}
        ],
        "save": {"x": 9, "y": 1, "text": "The warmth of Castle Town fills you with power."}
    },
    "field_start": {
        "name": "Field of Hopes and Dreams",
        "map": [
            [1,1,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,5,0,0,0,5,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,1,1,1,1,0,0,0,1,1,1,1,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,3,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,5,0,0,0,5,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,1,1,1,1,0,0,0,1,1,1,1,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        ],
        "bg_color": FIELD_GREEN,
        "enemies": ["Rudinn", "Hathy"],
        "transitions": [
            {"x": 9, "y": 0, "target": "castle_entrance", "tx": 9, "ty": 9},
            {"x": 9, "y": 12, "target": "great_board", "tx": 9, "ty": 1}
        ],
        "save": {"x": 9, "y": 6, "text": "The field stretches endlessly before you."}
    },
    "great_board": {
        "name": "The Great Board",
        "map": [
            [1,1,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,5,0,0,5,0,0,0,0,0,5,0,0,5,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,1,1,1,1,0,1,1,1,1,0,0,0,0,0,1],
            [1,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,1],
            [1,0,0,0,0,1,0,0,0,3,0,0,0,1,0,0,0,0,0,1],
            [1,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,1],
            [1,0,0,0,0,1,1,1,0,0,0,1,1,1,0,0,0,0,0,1],
            [1,0,0,5,0,0,0,0,0,0,0,0,0,0,0,0,5,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        ],
        "bg_color": DARK_PURPLE,
        "enemies": ["Rudinn", "Hathy"],
        "npcs": [
            {"name": "Lancer", "x": 9, "y": 6, "color": BLUE,
             "dialogue": [
                DialogueLine("Lancer", "Welcome to the Great Board!"),
                DialogueLine("Lancer", "This is where we play... THE GAME!"),
                DialogueLine("Lancer", "Ho ho ho! Try to catch me!")
            ]},
        ],
        "transitions": [
            {"x": 9, "y": 0, "target": "field_start", "tx": 9, "ty": 11},
            {"x": 9, "y": 11, "target": "scarlet_forest", "tx": 9, "ty": 1}
        ],
        "save": {"x": 9, "y": 6, "text": "The Great Board stretches before you."}
    },
    "scarlet_forest": {
        "name": "Scarlet Forest",
        "map": [
            [1,1,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,1,0,1,0,1,0,0,0,0,0,1,0,1,0,1,0,0,1],
            [1,0,0,0,0,0,0,0,5,0,5,0,0,0,0,0,0,0,0,1],
            [1,0,1,0,1,0,1,0,0,0,0,0,1,0,1,0,1,0,0,1],
            [1,0,0,0,0,0,0,0,0,3,0,0,0,0,0,0,0,0,0,1],
            [1,0,1,0,1,0,1,0,0,0,0,0,1,0,1,0,1,0,0,1],
            [1,0,0,0,0,0,0,0,5,0,5,0,0,0,0,0,0,0,0,1],
            [1,0,1,0,1,0,1,0,0,0,0,0,1,0,1,0,1,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,2,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        ],
        "bg_color": (60, 20, 30),
        "enemies": ["Rudinn", "Hathy"],
        "transitions": [
            {"x": 9, "y": 0, "target": "great_board", "tx": 9, "ty": 10},
            {"x": 9, "y": 10, "target": "card_castle_entrance", "tx": 9, "ty": 1},
            {"x": 1, "y": 10, "target": "bake_sale", "tx": 17, "ty": 5}
        ],
        "save": {"x": 9, "y": 5, "text": "Red leaves fall around you. You feel determined."}
    },
    "bake_sale": {
        "name": "Bake Sale",
        "map": [
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,1],
            [1,0,0,0,0,0,1,0,0,4,0,0,0,1,0,0,0,0,0,1],
            [1,0,0,0,0,0,1,0,0,0,0,0,0,1,0,0,0,0,2,1],
            [1,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        ],
        "bg_color": (80, 40, 60),
        "npcs": [
            {"name": "Top Chef", "x": 9, "y": 4, "color": ORANGE,
             "dialogue": [
                DialogueLine("Top Chef", "Welcome to the Bake Sale!"),
                DialogueLine("Top Chef", "We have the finest Dark Candy!"),
                DialogueLine("Top Chef", "Take some for your journey!")
            ]},
        ],
        "transitions": [
            {"x": 18, "y": 5, "target": "scarlet_forest", "tx": 2, "ty": 10}
        ]
    },
    "card_castle_entrance": {
        "name": "Card Castle - Entrance",
        "map": [
            [1,1,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,1,1,1,0,0,0,0,0,0,0,1,1,1,0,0,0,1],
            [1,0,0,1,0,0,0,0,0,3,0,0,0,0,0,1,0,0,0,1],
            [1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        ],
        "bg_color": DARK_PURPLE,
        "enemies": ["Rudinn"],
        "transitions": [
            {"x": 9, "y": 0, "target": "scarlet_forest", "tx": 9, "ty": 9},
            {"x": 9, "y": 8, "target": "card_castle_floor1", "tx": 9, "ty": 1}
        ],
        "save": {"x": 9, "y": 4, "text": "Card Castle looms before you."}
    },
    "card_castle_floor1": {
        "name": "Card Castle - Floor 1",
        "map": [
            [1,1,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,5,0,0,0,0,0,0,0,0,0,0,0,5,0,0,0,1],
            [1,0,0,0,0,0,1,1,1,0,1,1,1,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,1],
            [1,0,0,5,0,0,1,1,1,0,1,1,1,0,0,5,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,2,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        ],
        "bg_color": DARK_PURPLE,
        "enemies": ["Rudinn", "Hathy"],
        "transitions": [
            {"x": 9, "y": 0, "target": "card_castle_entrance", "tx": 9, "ty": 7},
            {"x": 9, "y": 8, "target": "card_castle_floor2", "tx": 9, "ty": 1},
            {"x": 1, "y": 8, "target": "jevil_prison", "tx": 9, "ty": 7}
        ]
    },
    "jevil_prison": {
        "name": "??????",
        "map": [
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,1,1,1,1,1,1,1,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,1,0,0,4,0,0,1,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,1,1,1,1,1,1,1,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        ],
        "bg_color": (10, 10, 20),
        "boss": "Jevil",
        "transitions": [
            {"x": 9, "y": 7, "target": "card_castle_floor1", "tx": 2, "ty": 8}
        ],
        "npcs": [
            {"name": "Jevil", "x": 9, "y": 4, "color": MAGENTA, "is_boss": True,
             "dialogue": [
                DialogueLine("Jevil", "UEE HEE HEE!"),
                DialogueLine("Jevil", "WELCOME, WELCOME!"),
                DialogueLine("Jevil", "TO MY LITTLE FREEDOM!"),
                DialogueLine("Jevil", "I CAN DO ANYTHING!"),
                DialogueLine("Jevil", "CHAOS, CHAOS!")
            ]}
        ]
    },
    "card_castle_floor2": {
        "name": "Card Castle - Floor 2",
        "map": [
            [1,1,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,5,0,0,0,0,0,0,0,5,0,0,0,0,0,1],
            [1,0,0,1,1,1,1,0,0,0,0,0,1,1,1,1,0,0,0,1],
            [1,0,0,1,0,0,0,0,0,3,0,0,0,0,0,1,0,0,0,1],
            [1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1],
            [1,0,0,1,1,1,1,0,0,0,0,0,1,1,1,1,0,0,0,1],
            [1,0,0,0,0,5,0,0,0,0,0,0,0,5,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        ],
        "bg_color": DARK_PURPLE,
        "enemies": ["Rudinn", "Hathy"],
        "transitions": [
            {"x": 9, "y": 0, "target": "card_castle_floor1", "tx": 9, "ty": 7},
            {"x": 9, "y": 8, "target": "card_castle_floor3", "tx": 9, "ty": 1}
        ],
        "save": {"x": 9, "y": 4, "text": "You're getting closer to the top."}
    },
    "card_castle_floor3": {
        "name": "Card Castle - Floor 3",
        "map": [
            [1,1,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,1,1,1,1,1,0,1,1,1,1,1,0,0,0,0,1],
            [1,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1],
            [1,0,0,0,1,0,0,5,0,4,0,5,0,0,1,0,0,0,0,1],
            [1,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1],
            [1,0,0,0,1,1,1,1,1,0,1,1,1,1,1,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        ],
        "bg_color": DARK_PURPLE,
        "enemies": ["Rudinn"],
        "npcs": [
            {"name": "Rouxls Kaard", "x": 9, "y": 5, "color": LIGHT_BLUE,
             "dialogue": [
                DialogueLine("Rouxls Kaard", "Ho ho ho! Thoust hast arrived!"),
                DialogueLine("Rouxls Kaard", "I am the DUKE OF PUZZLES!"),
                DialogueLine("Rouxls Kaard", "Preparest to face mine greatest puzzle!"),
                DialogueLine("Rouxls Kaard", "...Actuallyeth, thou may pass.")
            ]},
        ],
        "transitions": [
            {"x": 9, "y": 0, "target": "card_castle_floor2", "tx": 9, "ty": 7},
            {"x": 9, "y": 8, "target": "card_castle_top", "tx": 9, "ty": 1}
        ]
    },
    "card_castle_top": {
        "name": "Card Castle - Top",
        "map": [
            [1,1,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,3,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        ],
        "bg_color": DARK_PURPLE,
        "transitions": [
            {"x": 9, "y": 0, "target": "card_castle_floor3", "tx": 9, "ty": 7},
            {"x": 9, "y": 7, "target": "throne_room", "tx": 9, "ty": 1}
        ],
        "save": {"x": 9, "y": 3, "text": "The throne room awaits. Stay determined."}
    },
    "throne_room": {
        "name": "Throne Room",
        "map": [
            [1,1,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,4,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        ],
        "bg_color": (30, 10, 40),
        "boss": "King",
        "transitions": [
            {"x": 9, "y": 0, "target": "card_castle_top", "tx": 9, "ty": 6}
        ],
        "npcs": [
            {"name": "King", "x": 9, "y": 3, "color": DARK_GREEN, "is_boss": True,
             "dialogue": [
                DialogueLine("King", "So... you've finally arrived."),
                DialogueLine("King", "Lightners... thinking you can waltz into MY kingdom!"),
                DialogueLine("King", "You think you can seal the fountain!?"),
                DialogueLine("King", "I'LL SHOW YOU THE POWER OF A KING!")
            ]}
        ]
    }
}

CHAPTER2_AREAS = {
    "cyber_entrance": {
        "name": "Cyber City - Entrance",
        "map": [
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,3,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,1,1,0,0,0,0,0,0,0,0,0,1,1,0,0,0,1],
            [1,0,0,1,0,0,0,0,4,0,4,0,0,0,0,1,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,5,0,0,0,0,0,5,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1],
            [1,0,0,1,1,0,0,0,0,2,0,0,0,0,1,1,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        ],
        "bg_color": CYBER_BLACK,
        "enemies": ["Tasque", "Werewire"],
        "npcs": [
            {"name": "Noelle", "x": 8, "y": 4, "color": YELLOW,
             "dialogue": [
                DialogueLine("Noelle", "K-Kris! Where are we?"),
                DialogueLine("Noelle", "This place is so... strange."),
                DialogueLine("Noelle", "We should stick together!")
            ]},
            {"name": "Berdly", "x": 10, "y": 4, "color": CYAN,
             "dialogue": [
                DialogueLine("Berdly", "Ah, this must be some kind of virtual world!"),
                DialogueLine("Berdly", "Fear not! I, Berdly, shall lead us to victory!"),
                DialogueLine("Berdly", "*strikes heroic pose*")
            ]},
        ],
        "transitions": [
            {"x": 9, "y": 10, "target": "trash_zone", "tx": 9, "ty": 1}
        ],
        "save": {"x": 9, "y": 1, "text": "The neon lights of Cyber City buzz around you."}
    },
    "trash_zone": {
        "name": "Trash Zone",
        "map": [
            [1,1,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,5,0,0,0,0,0,0,0,0,0,0,0,5,0,0,0,1],
            [1,0,0,0,0,0,1,1,0,0,0,1,1,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,3,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,5,0,0,0,0,0,0,0,0,0,0,0,5,0,0,0,1],
            [1,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,1,1,0,0,0,1,1,0,0,0,0,0,0,1],
            [1,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        ],
        "bg_color": (30, 30, 40),
        "enemies": ["Tasque", "Werewire"],
        "transitions": [
            {"x": 9, "y": 0, "target": "cyber_entrance", "tx": 9, "ty": 9},
            {"x": 9, "y": 10, "target": "cyber_city_main", "tx": 9, "ty": 1},
            {"x": 1, "y": 9, "target": "spamton_shop", "tx": 17, "ty": 5}
        ],
        "save": {"x": 9, "y": 5, "text": "Garbage surrounds you. You feel... determined?"}
    },
    "spamton_shop": {
        "name": "???",
        "map": [
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,1],
            [1,0,0,0,0,0,1,0,0,4,0,0,0,1,0,0,0,0,0,1],
            [1,0,0,0,0,0,1,0,0,0,0,0,0,1,0,0,0,0,2,1],
            [1,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        ],
        "bg_color": (20, 20, 30),
        "npcs": [
            {"name": "Spamton", "x": 9, "y": 4, "color": PINK,
             "dialogue": [
                DialogueLine("Spamton", "HEY EVERY !!"),
                DialogueLine("Spamton", "IT'S ME, EV3RY BUDDY'S FAVORITE [[Number 1 Rated Salesman1997]]"),
                DialogueLine("Spamton", "SPAMT  SPAMTON G. SPAMTON!!"),
                DialogueLine("Spamton", "WOAH!! IF IT ISN,T A... [[Lost Customer]]!"),
                DialogueLine("Spamton", "HEY-HE Y HEY!!!"),
                DialogueLine("Spamton", "LOOKS LIKE YOU'RE [[All Alone On A Late Night?]]"),
                DialogueLine("Spamton", "ALL YOUR FRIENDS, [[Abandoned you for the slime]] YOU ARE??"),
                DialogueLine("Spamton", "SALES, GONE DOWN THE [[Drain]] [[Drain]]??"),
                DialogueLine("Spamton", "LIVING IN A GODDAMN GARBAGE CAN???"),
                DialogueLine("Spamton", "..."),
                DialogueLine("Spamton", "WELL HAVE I GOT A [[Specil Deal]] FOR LONELY [[Hearts]] LIKE YOU!!")
            ]},
        ],
        "transitions": [
            {"x": 18, "y": 5, "target": "trash_zone", "tx": 2, "ty": 9}
        ]
    },
    "cyber_city_main": {
        "name": "Cyber City - Main Street",
        "map": [
            [1,1,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,5,0,0,0,0,0,0,0,0,0,5,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,1,1,1,0,0,0,0,0,0,0,1,1,1,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,3,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,5,0,0,0,0,0,0,0,0,0,5,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,1,1,1,0,0,0,0,0,0,0,1,1,1,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        ],
        "bg_color": CYBER_BLACK,
        "enemies": ["Tasque", "Werewire", "Swatchling"],
        "transitions": [
            {"x": 9, "y": 0, "target": "trash_zone", "tx": 9, "ty": 9},
            {"x": 9, "y": 11, "target": "acid_tunnel", "tx": 9, "ty": 1}
        ],
        "save": {"x": 9, "y": 5, "text": "Neon signs flash all around. You feel determined."}
    },
    "acid_tunnel": {
        "name": "Acid Tunnel",
        "map": [
            [1,1,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,1,1,1,1,0,1,1,1,1,0,0,0,0,0,1],
            [1,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,1],
            [1,0,0,0,0,1,0,0,0,3,0,0,0,1,0,0,0,0,0,1],
            [1,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,1],
            [1,0,0,0,0,1,1,1,1,0,1,1,1,1,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        ],
        "bg_color": (20, 50, 30),
        "enemies": ["Werewire", "Swatchling"],
        "transitions": [
            {"x": 9, "y": 0, "target": "cyber_city_main", "tx": 9, "ty": 10},
            {"x": 9, "y": 9, "target": "queens_mansion", "tx": 9, "ty": 1}
        ],
        "save": {"x": 9, "y": 5, "text": "Acid pools bubble below. Watch your step."}
    },
    "queens_mansion": {
        "name": "Queen's Mansion - Entrance",
        "map": [
            [1,1,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,1,1,1,1,0,0,0,0,0,1,1,1,1,0,0,0,1],
            [1,0,0,1,0,0,0,0,0,3,0,0,0,0,0,1,0,0,0,1],
            [1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        ],
        "bg_color": NEON_PURPLE,
        "enemies": ["Swatchling"],
        "transitions": [
            {"x": 9, "y": 0, "target": "acid_tunnel", "tx": 9, "ty": 8},
            {"x": 9, "y": 7, "target": "mansion_hall", "tx": 9, "ty": 1}
        ],
        "save": {"x": 9, "y": 4, "text": "Queen's mansion towers above. You feel determined."}
    },
    "mansion_hall": {
        "name": "Queen's Mansion - Hall",
        "map": [
            [1,1,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,5,0,0,0,0,0,0,0,0,0,5,0,0,0,0,1],
            [1,0,0,1,1,1,0,0,0,0,0,0,0,1,1,1,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,1,1,1,0,0,0,0,0,0,0,1,1,1,0,0,0,1],
            [1,0,0,0,5,0,0,0,0,0,0,0,0,0,5,0,0,0,0,1],
            [1,2,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        ],
        "bg_color": NEON_PURPLE,
        "enemies": ["Swatchling", "Tasque"],
        "transitions": [
            {"x": 9, "y": 0, "target": "queens_mansion", "tx": 9, "ty": 6},
            {"x": 9, "y": 8, "target": "mansion_top", "tx": 9, "ty": 1},
            {"x": 1, "y": 8, "target": "spamton_neo_room", "tx": 17, "ty": 5}
        ]
    },
    "spamton_neo_room": {
        "name": "??????",
        "map": [
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,1,1,1,1,1,1,1,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,1,0,0,4,0,0,1,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,2,1],
            [1,0,0,0,0,0,1,1,1,1,1,1,1,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        ],
        "bg_color": (10, 10, 20),
        "boss": "Spamton NEO",
        "transitions": [
            {"x": 18, "y": 5, "target": "mansion_hall", "tx": 2, "ty": 8}
        ],
        "npcs": [
            {"name": "Spamton NEO", "x": 9, "y": 4, "color": PINK, "is_boss": True,
             "dialogue": [
                DialogueLine("Spamton NEO", "KRIS!!!"),
                DialogueLine("Spamton NEO", "IT'S ME, YOUR BEST [[Salesman]]"),
                DialogueLine("Spamton NEO", "I'VE BECOME A [[BIG SHOT]]!!!"),
                DialogueLine("Spamton NEO", "NOW I'M FINALLY [[Free]]!"),
                DialogueLine("Spamton NEO", "[[FREE]]!!!!"),
                DialogueLine("Spamton NEO", "NOW... LET ME SHOW YOU..."),
                DialogueLine("Spamton NEO", "[[Hyperlink Blocked]]!!!")
            ]}
        ]
    },
    "mansion_top": {
        "name": "Queen's Mansion - Top",
        "map": [
            [1,1,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,3,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        ],
        "bg_color": NEON_PURPLE,
        "transitions": [
            {"x": 9, "y": 0, "target": "mansion_hall", "tx": 9, "ty": 7},
            {"x": 9, "y": 6, "target": "queen_arena", "tx": 9, "ty": 1}
        ],
        "save": {"x": 9, "y": 3, "text": "The Queen awaits. Stay determined."}
    },
    "queen_arena": {
        "name": "Queen's Arena",
        "map": [
            [1,1,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,4,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        ],
        "bg_color": CYBER_PINK,
        "boss": "Queen",
        "transitions": [
            {"x": 9, "y": 0, "target": "mansion_top", "tx": 9, "ty": 5}
        ],
        "npcs": [
            {"name": "Queen", "x": 9, "y": 3, "color": CYAN, "is_boss": True,
             "dialogue": [
                DialogueLine("Queen", "Ho Ho Ho. You Have Arrived"),
                DialogueLine("Queen", "I Must Say. You Have Impressed Me"),
                DialogueLine("Queen", "But Now It Is Time For You To"),
                DialogueLine("Queen", "Become My [[Willing]] Servants"),
                DialogueLine("Queen", "Prepare To Face My Wrath"),
                DialogueLine("Queen", "Lmao")
            ]}
        ]
    }
}

# =============================================================================
# OVERWORLD SYSTEM
# =============================================================================

class Overworld:
    def __init__(self, chapter: Chapter):
        self.chapter = chapter
        self.areas = CHAPTER1_AREAS if chapter == Chapter.ONE else CHAPTER2_AREAS
        self.current_area = "castle_entrance" if chapter == Chapter.ONE else "cyber_entrance"
        
        self.player_x = 9 * TILE_SIZE
        self.player_y = 6 * TILE_SIZE
        self.player_dir = "down"
        
        self.dialogue = DialogueBox()
        self.save_dialogue = DialogueBox()
        
        # Track defeated enemies per area
        self.defeated_enemies: Dict[str, List[Tuple[int, int]]] = {}
        
        # Pending battle
        self.pending_battle: Optional[str] = None
        self.pending_boss: Optional[str] = None
        
    def update(self, keys_held, keys_pressed):
        # Handle dialogue
        if self.dialogue.active:
            self.dialogue.update()
            if keys_pressed.get(pygame.K_z):
                if self.dialogue.advance():
                    # Check if this was a boss dialogue
                    if self.pending_boss:
                        boss = self.pending_boss
                        self.pending_boss = None
                        return ("boss", boss)
            return None
            
        if self.save_dialogue.active:
            self.save_dialogue.update()
            if keys_pressed.get(pygame.K_z):
                self.save_dialogue.advance()
            return None
            
        # Movement - support both arrow keys and WASD
        area = self.areas[self.current_area]
        area_map = area["map"]
        
        dx = dy = 0
        speed = 4
        if keys_held.get(pygame.K_LEFT) or keys_held.get(pygame.K_a):
            dx = -speed
            self.player_dir = "left"
        elif keys_held.get(pygame.K_RIGHT) or keys_held.get(pygame.K_d):
            dx = speed
            self.player_dir = "right"
        elif keys_held.get(pygame.K_UP) or keys_held.get(pygame.K_w):
            dy = -speed
            self.player_dir = "up"
        elif keys_held.get(pygame.K_DOWN) or keys_held.get(pygame.K_s):
            dy = speed
            self.player_dir = "down"
            
        new_x = self.player_x + dx
        new_y = self.player_y + dy
        
        tile_x = new_x // TILE_SIZE
        tile_y = new_y // TILE_SIZE
        
        if 0 <= tile_y < len(area_map) and 0 <= tile_x < len(area_map[0]):
            tile = area_map[tile_y][tile_x]
            
            if tile == 0 or tile == 3 or tile == 4 or tile == 5:  # Walkable
                self.player_x = new_x
                self.player_y = new_y
            elif tile == 2:  # Transition
                for trans in area.get("transitions", []):
                    if tile_x == trans["x"] and tile_y == trans["y"]:
                        self.current_area = trans["target"]
                        self.player_x = trans["tx"] * TILE_SIZE
                        self.player_y = trans["ty"] * TILE_SIZE
                        return None
                        
        # Interaction
        if keys_pressed.get(pygame.K_z):
            # Check NPCs
            for npc_data in area.get("npcs", []):
                npc_x = npc_data["x"] * TILE_SIZE
                npc_y = npc_data["y"] * TILE_SIZE
                if abs(self.player_x - npc_x) < TILE_SIZE * 1.5 and abs(self.player_y - npc_y) < TILE_SIZE * 1.5:
                    if npc_data.get("is_boss"):
                        self.pending_boss = npc_data["name"]
                    self.dialogue.start(npc_data["dialogue"])
                    return None
                    
            # Check save points
            save = area.get("save")
            if save:
                save_x = save["x"] * TILE_SIZE
                save_y = save["y"] * TILE_SIZE
                if abs(self.player_x - save_x) < TILE_SIZE * 1.5 and abs(self.player_y - save_y) < TILE_SIZE * 1.5:
                    lines = [
                        DialogueLine("", f"* {save['text']}"),
                        DialogueLine("", "* HP fully restored.")
                    ]
                    self.save_dialogue.start(lines)
                    return ("save", None)
                    
        # Enemy encounters (random from enemy spawn tiles)
        tile_x = self.player_x // TILE_SIZE
        tile_y = self.player_y // TILE_SIZE
        if 0 <= tile_y < len(area_map) and 0 <= tile_x < len(area_map[0]):
            if area_map[tile_y][tile_x] == 5:
                # Check if already defeated
                area_defeated = self.defeated_enemies.get(self.current_area, [])
                if (tile_x, tile_y) not in area_defeated:
                    if random.random() < 0.3:  # 30% chance per frame on enemy tile
                        area_defeated.append((tile_x, tile_y))
                        self.defeated_enemies[self.current_area] = area_defeated
                        enemies = area.get("enemies", ["Dummy"])
                        return ("battle", random.choice(enemies))
                        
        return None
        
    def draw(self, screen, font):
        area = self.areas[self.current_area]
        area_map = area["map"]
        bg_color = area.get("bg_color", BLACK)
        
        screen.fill(bg_color)
        
        # Draw tiles
        for y, row in enumerate(area_map):
            for x, tile in enumerate(row):
                rect = (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if tile == 1:  # Wall
                    wall_color = tuple(min(255, c + 40) for c in bg_color)
                    pygame.draw.rect(screen, wall_color, rect)
                    pygame.draw.rect(screen, tuple(min(255, c + 60) for c in bg_color), rect, 1)
                elif tile == 2:  # Transition
                    pygame.draw.rect(screen, tuple(min(255, c + 80) for c in bg_color), rect)
                elif tile == 3:  # Save point
                    pygame.draw.rect(screen, YELLOW, rect)
                    pygame.draw.rect(screen, WHITE, rect, 2)
                    # Star
                    pygame.draw.polygon(screen, WHITE, [
                        (x*TILE_SIZE + 16, y*TILE_SIZE + 4),
                        (x*TILE_SIZE + 20, y*TILE_SIZE + 12),
                        (x*TILE_SIZE + 28, y*TILE_SIZE + 12),
                        (x*TILE_SIZE + 22, y*TILE_SIZE + 18),
                        (x*TILE_SIZE + 24, y*TILE_SIZE + 28),
                        (x*TILE_SIZE + 16, y*TILE_SIZE + 22),
                        (x*TILE_SIZE + 8, y*TILE_SIZE + 28),
                        (x*TILE_SIZE + 10, y*TILE_SIZE + 18),
                        (x*TILE_SIZE + 4, y*TILE_SIZE + 12),
                        (x*TILE_SIZE + 12, y*TILE_SIZE + 12),
                    ])
                elif tile == 5:  # Enemy spawn
                    # Only draw if not defeated
                    area_defeated = self.defeated_enemies.get(self.current_area, [])
                    if (x, y) not in area_defeated:
                        pygame.draw.rect(screen, RED, rect)
                        pygame.draw.rect(screen, WHITE, rect, 2)
                        # Exclamation
                        exc = font.render("!", True, YELLOW)
                        screen.blit(exc, (x*TILE_SIZE + 12, y*TILE_SIZE + 6))
                        
        # Draw NPCs
        for npc_data in area.get("npcs", []):
            nx = npc_data["x"] * TILE_SIZE
            ny = npc_data["y"] * TILE_SIZE
            color = npc_data.get("color", WHITE)
            pygame.draw.rect(screen, color, (nx, ny, TILE_SIZE, TILE_SIZE))
            pygame.draw.rect(screen, WHITE, (nx, ny, TILE_SIZE, TILE_SIZE), 2)
            name_surf = font.render(npc_data["name"], True, WHITE)
            screen.blit(name_surf, (nx + TILE_SIZE//2 - name_surf.get_width()//2, ny - 20))
            
        # Draw player
        pygame.draw.rect(screen, BLUE, (self.player_x, self.player_y, TILE_SIZE, TILE_SIZE))
        pygame.draw.rect(screen, WHITE, (self.player_x, self.player_y, TILE_SIZE, TILE_SIZE), 2)
        
        # Direction indicator
        offsets = {"up": (12, 0), "down": (12, 28), "left": (0, 12), "right": (28, 12)}
        ox, oy = offsets[self.player_dir]
        pygame.draw.circle(screen, WHITE, (self.player_x + ox + 4, self.player_y + oy + 4), 3)
        
        # Area name
        name = area.get("name", self.current_area)
        name_surf = font.render(name, True, WHITE)
        pygame.draw.rect(screen, BLACK, (8, 8, name_surf.get_width() + 12, 26))
        screen.blit(name_surf, (14, 12))
        
        # Controls hint
        hint = "Z/Space:Interact  C:Menu  Arrows/WASD:Move"
        hint_surf = font.render(hint, True, WHITE)
        pygame.draw.rect(screen, BLACK, (0, HEIGHT - 24, hint_surf.get_width() + 16, 24))
        screen.blit(hint_surf, (8, HEIGHT - 20))
        
        # Draw dialogues
        self.dialogue.draw(screen, font)
        self.save_dialogue.draw(screen, font)

# =============================================================================
# MAIN GAME
# =============================================================================

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("CAT'S DELTARUNE - Chapters 1 & 2")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 48)
        
        self.state = GameState.TITLE
        self.chapter = Chapter.ONE
        
        # Party
        self.party = self._create_party()
        
        # Inventory
        self.inventory = [
            Item("Dark Candy", "Restores 40 HP.", heal_hp=40),
            Item("CD Bagel", "Restores 60 HP.", heal_hp=60),
            Item("Spin Cake", "Restores 80 HP to all.", heal_hp=80),
        ]
        
        # Systems
        self.overworld: Optional[Overworld] = None
        self.battle: Optional[BattleSystem] = None
        
        # Input
        self.keys_held = {}
        self.keys_pressed = {}
        self.prev_keys = {}
        
        # Title screen
        self.title_selection = 0
        
        # Cutscene
        self.cutscene_lines: List[DialogueLine] = []
        self.cutscene_dialogue = DialogueBox()
        
    def _create_party(self) -> List[PartyMember]:
        return [
            PartyMember(
                name="Kris",
                stats=Stats(hp=90, max_hp=90, atk=12, defense=2, magic=0),
                color=BLUE,
                weapon="Wood Blade",
                armor="Amber Card"
            ),
            PartyMember(
                name="Susie",
                stats=Stats(hp=110, max_hp=110, atk=14, defense=1, magic=3),
                color=PURPLE,
                weapon="Mane Ax",
                armor="Amber Card",
                spells=[
                    Spell("Rude Buster", 50, "Deals heavy damage to one enemy", "enemy", "damage", 80),
                    Spell("Red Buster", 60, "Deals massive damage to one enemy", "enemy", "damage", 120)
                ]
            ),
            PartyMember(
                name="Ralsei",
                stats=Stats(hp=70, max_hp=70, atk=8, defense=2, magic=8),
                color=GREEN,
                weapon="Red Scarf",
                armor="White Ribbon",
                spells=[
                    Spell("Heal Prayer", 32, "Heals all party members", "all_allies", "heal", 60),
                    Spell("Pacify", 16, "Spare tired enemies instantly", "all_enemies", "pacify", 0),
                    Spell("Dual Heal", 50, "Heals party significantly", "all_allies", "heal", 100)
                ]
            ),
        ]
        
    def _start_chapter(self, chapter: Chapter):
        self.chapter = chapter
        self.party = self._create_party()
        self.overworld = Overworld(chapter)
        self.state = GameState.CUTSCENE
        
        # Chapter intro
        if chapter == Chapter.ONE:
            self.cutscene_lines = [
                DialogueLine("", "* You find yourself in a dark room."),
                DialogueLine("", "* A strange world... made of darkness."),
                DialogueLine("Ralsei", "Welcome, heroes from the Light World!"),
                DialogueLine("Ralsei", "You have been chosen to restore balance."),
                DialogueLine("Ralsei", "Together, we must seal the Dark Fountain!"),
                DialogueLine("Susie", "Ugh... what is this place?"),
                DialogueLine("Susie", "Whatever. Let's just get this over with."),
            ]
        else:
            self.cutscene_lines = [
                DialogueLine("", "* The computer lab's lights flicker..."),
                DialogueLine("", "* You feel yourself falling into darkness."),
                DialogueLine("", "* A new Dark World opens before you."),
                DialogueLine("Queen", "Ho Ho Ho. Welcome To My City"),
                DialogueLine("Queen", "You Will Make Excellent Servants"),
                DialogueLine("Susie", "Not this again..."),
                DialogueLine("Ralsei", "Stay determined, everyone!"),
            ]
            
        self.cutscene_dialogue.start(self.cutscene_lines)
        
    def update(self):
        # Update input - use direct key checking
        current = pygame.key.get_pressed()
        
        # Build key state dictionaries with explicit key constants
        key_list = [
            pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT,
            pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d,  # WASD
            pygame.K_z, pygame.K_x, pygame.K_c, pygame.K_RETURN,
            pygame.K_LSHIFT, pygame.K_RSHIFT, pygame.K_ESCAPE, pygame.K_SPACE
        ]
        
        self.keys_held = {}
        self.keys_pressed = {}
        
        for k in key_list:
            self.keys_held[k] = current[k]
            self.keys_pressed[k] = current[k] and not self.prev_keys.get(k, False)
            
        self.prev_keys = dict(self.keys_held)
        
        if self.state == GameState.TITLE:
            self._update_title()
        elif self.state == GameState.CUTSCENE:
            self._update_cutscene()
        elif self.state == GameState.OVERWORLD:
            self._update_overworld()
        elif self.state == GameState.BATTLE:
            self._update_battle()
        elif self.state == GameState.MENU:
            self._update_menu()
        elif self.state == GameState.CHAPTER_END:
            self._update_chapter_end()
            
    def _update_title(self):
        if self.keys_pressed.get(pygame.K_UP) or self.keys_pressed.get(pygame.K_w):
            self.title_selection = (self.title_selection - 1) % 3
        if self.keys_pressed.get(pygame.K_DOWN) or self.keys_pressed.get(pygame.K_s):
            self.title_selection = (self.title_selection + 1) % 3
        if self.keys_pressed.get(pygame.K_z) or self.keys_pressed.get(pygame.K_RETURN) or self.keys_pressed.get(pygame.K_SPACE):
            if self.title_selection == 0:
                self._start_chapter(Chapter.ONE)
            elif self.title_selection == 1:
                self._start_chapter(Chapter.TWO)
            # Option 2 would be settings/quit
                
    def _update_cutscene(self):
        self.cutscene_dialogue.update()
        if self.keys_pressed.get(pygame.K_z):
            if self.cutscene_dialogue.advance():
                self.state = GameState.OVERWORLD
                
    def _update_overworld(self):
        # Menu
        if self.keys_pressed.get(pygame.K_c):
            self.state = GameState.MENU
            return
            
        result = self.overworld.update(self.keys_held, self.keys_pressed)
        if result:
            action, data = result
            if action == "battle":
                self._start_battle([data])
            elif action == "boss":
                self._start_battle([data], is_boss=True)
            elif action == "save":
                # Heal party
                for m in self.party:
                    m.stats.hp = m.stats.max_hp
                    m.down = False
                    
    def _start_battle(self, enemy_names: List[str], is_boss: bool = False):
        enemies = [create_enemy(name) for name in enemy_names]
        self.battle = BattleSystem(self.party, enemies)
        self.battle.inventory = self.inventory
        self.state = GameState.BATTLE
        
    def _update_battle(self):
        result = self.battle.update(self.keys_held, self.keys_pressed)
        if result in ["victory", "spare"]:
            # Check if it was a boss
            any_boss = any(e.is_boss for e in self.battle.enemies)
            if any_boss and result in ["victory", "spare"]:
                # Check chapter completion
                area = self.overworld.current_area
                if area == "throne_room" and self.chapter == Chapter.ONE:
                    self.state = GameState.CHAPTER_END
                elif area == "queen_arena" and self.chapter == Chapter.TWO:
                    self.state = GameState.CHAPTER_END
                else:
                    self.state = GameState.OVERWORLD
            else:
                self.state = GameState.OVERWORLD
            self.battle = None
        elif result == "game_over":
            # Restore and return to overworld for now
            for m in self.party:
                m.stats.hp = m.stats.max_hp
                m.down = False
            self.state = GameState.OVERWORLD
            self.battle = None
            
    def _update_menu(self):
        if self.keys_pressed.get(pygame.K_x) or self.keys_pressed.get(pygame.K_c):
            self.state = GameState.OVERWORLD
            
    def _update_chapter_end(self):
        if self.keys_pressed.get(pygame.K_z):
            if self.chapter == Chapter.ONE:
                self._start_chapter(Chapter.TWO)
            else:
                self.state = GameState.TITLE
                
    def draw(self):
        if self.state == GameState.TITLE:
            self._draw_title()
        elif self.state == GameState.CUTSCENE:
            self._draw_cutscene()
        elif self.state == GameState.OVERWORLD:
            self.overworld.draw(self.screen, self.font)
        elif self.state == GameState.BATTLE:
            self.battle.draw(self.screen, self.font)
        elif self.state == GameState.MENU:
            self._draw_menu()
        elif self.state == GameState.CHAPTER_END:
            self._draw_chapter_end()
            
        pygame.display.flip()
        
    def _draw_title(self):
        self.screen.fill(BLACK)
        
        # Title
        title = self.title_font.render("DELTARUNE", True, WHITE)
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        
        subtitle = self.font.render("Chapters 1 & 2", True, YELLOW)
        self.screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, 150))
        
        # Menu options
        options = ["Chapter 1", "Chapter 2", "Exit"]
        for i, opt in enumerate(options):
            color = YELLOW if i == self.title_selection else WHITE
            prefix = "> " if i == self.title_selection else "  "
            text = self.font.render(prefix + opt, True, color)
            self.screen.blit(text, (WIDTH//2 - 60, 250 + i * 40))
            
        # Credits
        credit = self.font.render("By Team Flames / Samsoft / Flames Co.", True, WHITE)
        self.screen.blit(credit, (WIDTH//2 - credit.get_width()//2, HEIGHT - 50))
        
        orig = self.font.render("Based on DELTARUNE by Toby Fox", True, (150, 150, 150))
        self.screen.blit(orig, (WIDTH//2 - orig.get_width()//2, HEIGHT - 30))
        
    def _draw_cutscene(self):
        # Dark background with some visual flair
        if self.chapter == Chapter.ONE:
            self.screen.fill(DARK_PURPLE)
        else:
            self.screen.fill(CYBER_BLACK)
            # Neon lines for cyber world
            for i in range(10):
                y = (pygame.time.get_ticks() // 50 + i * 50) % HEIGHT
                pygame.draw.line(self.screen, NEON_PURPLE, (0, y), (WIDTH, y), 1)
                
        self.cutscene_dialogue.draw(self.screen, self.font)
        
    def _draw_menu(self):
        # Draw overworld behind
        self.overworld.draw(self.screen, self.font)
        
        # Menu overlay
        menu_rect = pygame.Rect(50, 50, WIDTH - 100, HEIGHT - 100)
        pygame.draw.rect(self.screen, BLACK, menu_rect)
        pygame.draw.rect(self.screen, WHITE, menu_rect, 3)
        
        # Party stats
        title = self.font.render("PARTY", True, YELLOW)
        self.screen.blit(title, (70, 60))
        
        for i, member in enumerate(self.party):
            x = 70 + i * 180
            y = 100
            
            name = self.font.render(member.name, True, member.color)
            self.screen.blit(name, (x, y))
            
            hp = self.font.render(f"HP: {member.stats.hp}/{member.stats.max_hp}", True, WHITE)
            self.screen.blit(hp, (x, y + 25))
            
            atk = self.font.render(f"ATK: {member.stats.atk}", True, WHITE)
            self.screen.blit(atk, (x, y + 50))
            
            defense = self.font.render(f"DEF: {member.stats.defense}", True, WHITE)
            self.screen.blit(defense, (x, y + 75))
            
        # Items
        item_title = self.font.render("ITEMS", True, YELLOW)
        self.screen.blit(item_title, (70, 220))
        
        for i, item in enumerate(self.inventory[:6]):
            text = self.font.render(f"- {item.name}", True, WHITE)
            self.screen.blit(text, (70, 250 + i * 25))
            
        # Close hint
        hint = self.font.render("Press X or C to close", True, WHITE)
        self.screen.blit(hint, (70, HEIGHT - 80))
        
    def _draw_chapter_end(self):
        self.screen.fill(BLACK)
        
        if self.chapter == Chapter.ONE:
            text1 = self.title_font.render("CHAPTER 1 COMPLETE", True, YELLOW)
            text2 = self.font.render("The King has been defeated!", True, WHITE)
            text3 = self.font.render("But your journey is not over...", True, WHITE)
        else:
            text1 = self.title_font.render("CHAPTER 2 COMPLETE", True, CYAN)
            text2 = self.font.render("The Queen has been stopped!", True, WHITE)
            text3 = self.font.render("Thank you for playing!", True, WHITE)
            
        self.screen.blit(text1, (WIDTH//2 - text1.get_width()//2, 150))
        self.screen.blit(text2, (WIDTH//2 - text2.get_width()//2, 220))
        self.screen.blit(text3, (WIDTH//2 - text3.get_width()//2, 260))
        
        cont = self.font.render("Press Z to continue", True, WHITE)
        self.screen.blit(cont, (WIDTH//2 - cont.get_width()//2, 350))
        
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
            self.update()
            self.draw()
            self.clock.tick(FPS)
            
        pygame.quit()

# =============================================================================
# ENTRY POINT  
# =============================================================================

if __name__ == "__main__":
    game = Game()
    game.run()
