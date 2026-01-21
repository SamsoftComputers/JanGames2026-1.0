#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           CAT'S DELTARUNE                                    ║
║                    A Deltarune-Inspired RPG Engine                           ║
║                         By Team Flames / Samsoft                             ║
║                                                                              ║
║  Features:                                                                   ║
║  - Full chapter-based story system (Chapters 1-7)                            ║
║  - Bullet-hell battle system with SOUL mechanics                             ║
║  - ACT / FIGHT / ITEM / MERCY combat options                                 ║
║  - Party system with multiple characters                                     ║
║  - Overworld exploration with collision detection                            ║
║  - Dialogue system with portraits and choices                                ║
║  - Save/Load system with multiple slots                                      ║
║  - Enemy AI with unique attack patterns                                      ║
║  - TP (Tension Points) system                                                ║
║  - Equipment and inventory management                                        ║
║                                                                              ║
║  Controls:                                                                   ║
║  Arrow Keys / WASD - Move                                                    ║
║  Z / Enter - Confirm / Interact                                              ║
║  X / Shift - Cancel / Menu                                                   ║
║  C - Quick Save (overworld)                                                  ║
║  F4 - Toggle Fullscreen                                                      ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import math
import pygame
import random
import json
import os
from typing import List, Dict, Tuple, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum, auto
from abc import ABC, abstractmethod

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

GAME_TITLE = "Cat's Deltarune"
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
FPS = 60
TILE_SIZE = 32

# Colors (Deltarune palette)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
RED = (255, 0, 0)
BLUE = (0, 120, 255)
GREEN = (0, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (148, 0, 211)
PINK = (255, 182, 193)
SOUL_RED = (255, 0, 0)
SOUL_CYAN = (0, 255, 255)
MENU_BG = (20, 20, 40)
BATTLE_BG = (0, 0, 0)
HP_GREEN = (0, 192, 0)
HP_YELLOW = (255, 255, 0)
TP_ORANGE = (255, 160, 0)

# Cat theme colors
CAT_PURPLE = (138, 43, 226)
CAT_PINK = (255, 105, 180)

# ═══════════════════════════════════════════════════════════════════════════════
# ENUMS AND DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════════

class GameState(Enum):
    TITLE = auto()
    OVERWORLD = auto()
    BATTLE = auto()
    DIALOGUE = auto()
    MENU = auto()
    CUTSCENE = auto()
    SAVE = auto()
    GAME_OVER = auto()
    CHAPTER_SELECT = auto()

class BattleState(Enum):
    MENU = auto()
    TARGET_SELECT = auto()
    ACTION_EXECUTE = auto()
    ENEMY_TURN = auto()
    BULLET_HELL = auto()
    DIALOGUE = auto()
    VICTORY = auto()
    DEFEAT = auto()

class SoulMode(Enum):
    RED = auto()      # Normal movement
    BLUE = auto()     # Gravity/platforming
    YELLOW = auto()   # Shooting
    PURPLE = auto()   # Rail movement
    GREEN = auto()    # Shield mode

@dataclass
class Stats:
    hp: int = 100
    max_hp: int = 100
    attack: int = 10
    defense: int = 10
    magic: int = 10
    speed: int = 10
    tp: int = 0
    max_tp: int = 100
    
@dataclass
class Item:
    name: str
    description: str
    item_type: str  # "healing", "weapon", "armor", "key"
    value: int = 0
    heal_amount: int = 0
    attack_boost: int = 0
    defense_boost: int = 0
    
@dataclass 
class Spell:
    name: str
    description: str
    tp_cost: int
    damage: int = 0
    heal_amount: int = 0
    effect: str = ""

# ═══════════════════════════════════════════════════════════════════════════════
# SPRITE GENERATOR (Procedural pixel art)
# ═══════════════════════════════════════════════════════════════════════════════

class SpriteGenerator:
    """Generates pixel art sprites procedurally"""
    
    @staticmethod
    def create_character(width: int, height: int, palette: List[Tuple[int,int,int]], 
                         char_type: str = "cat") -> pygame.Surface:
        """Generate a character sprite"""
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        
        if char_type == "cat":
            # Cat protagonist sprite
            primary = palette[0] if palette else CAT_PURPLE
            secondary = palette[1] if len(palette) > 1 else WHITE
            
            # Body
            pygame.draw.ellipse(surf, primary, (width//4, height//3, width//2, height//2))
            # Head
            pygame.draw.circle(surf, primary, (width//2, height//3), width//4)
            # Ears
            pygame.draw.polygon(surf, primary, [
                (width//3, height//6), (width//4, height//3), (width//3 + 4, height//3)
            ])
            pygame.draw.polygon(surf, primary, [
                (2*width//3, height//6), (2*width//3 - 4, height//3), (3*width//4, height//3)
            ])
            # Eyes
            pygame.draw.circle(surf, secondary, (width//2 - 4, height//3), 3)
            pygame.draw.circle(surf, secondary, (width//2 + 4, height//3), 3)
            pygame.draw.circle(surf, BLACK, (width//2 - 4, height//3), 2)
            pygame.draw.circle(surf, BLACK, (width//2 + 4, height//3), 2)
            
        elif char_type == "human":
            # Kris-like human sprite
            primary = palette[0] if palette else BLUE
            skin = palette[1] if len(palette) > 1 else (255, 220, 180)
            
            # Body
            pygame.draw.rect(surf, primary, (width//3, height//3, width//3, height//2))
            # Head
            pygame.draw.circle(surf, skin, (width//2, height//4), width//5)
            # Hair
            pygame.draw.arc(surf, (139, 69, 19), (width//3, height//8, width//3, height//4), 
                           0, math.pi, 3)
            
        elif char_type == "monster":
            # Fluffy monster sprite
            primary = palette[0] if palette else PURPLE
            
            # Fluffy body
            for i in range(5):
                offset = random.randint(-3, 3)
                pygame.draw.circle(surf, primary, 
                                  (width//2 + offset, height//2 + i*3), width//4)
            # Eyes
            pygame.draw.circle(surf, WHITE, (width//2 - 5, height//3), 4)
            pygame.draw.circle(surf, WHITE, (width//2 + 5, height//3), 4)
            pygame.draw.circle(surf, BLACK, (width//2 - 5, height//3), 2)
            pygame.draw.circle(surf, BLACK, (width//2 + 5, height//3), 2)
            
        return surf
    
    @staticmethod
    def create_soul(color: Tuple[int,int,int] = SOUL_RED) -> pygame.Surface:
        """Generate the SOUL sprite"""
        surf = pygame.Surface((16, 16), pygame.SRCALPHA)
        # Heart shape
        points = [
            (8, 14),   # Bottom point
            (1, 6),    # Left bottom
            (1, 4),    # Left middle
            (4, 1),    # Left top
            (8, 5),    # Center top
            (12, 1),   # Right top
            (15, 4),   # Right middle
            (15, 6),   # Right bottom
        ]
        pygame.draw.polygon(surf, color, points)
        # Highlight
        pygame.draw.circle(surf, WHITE, (5, 5), 2)
        return surf
    
    @staticmethod
    def create_bullet(bullet_type: str = "basic", 
                     color: Tuple[int,int,int] = WHITE) -> pygame.Surface:
        """Generate bullet sprites for attacks"""
        surf = pygame.Surface((16, 16), pygame.SRCALPHA)
        
        if bullet_type == "basic":
            pygame.draw.circle(surf, color, (8, 8), 6)
        elif bullet_type == "star":
            # 5-pointed star
            points = []
            for i in range(10):
                angle = math.pi/2 + i * math.pi/5
                r = 7 if i % 2 == 0 else 3
                points.append((8 + r * math.cos(angle), 8 - r * math.sin(angle)))
            pygame.draw.polygon(surf, color, points)
        elif bullet_type == "diamond":
            pygame.draw.polygon(surf, color, [(8, 0), (16, 8), (8, 16), (0, 8)])
        elif bullet_type == "bone":
            pygame.draw.rect(surf, color, (2, 6, 12, 4))
            pygame.draw.circle(surf, color, (2, 8), 3)
            pygame.draw.circle(surf, color, (14, 8), 3)
        elif bullet_type == "spade":
            # Spade shape
            pygame.draw.polygon(surf, color, [(8, 0), (14, 8), (8, 14), (2, 8)])
            pygame.draw.rect(surf, color, (6, 10, 4, 6))
            
        return surf
    
    @staticmethod
    def create_tile(tile_type: str = "floor") -> pygame.Surface:
        """Generate tileset sprites"""
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
        
        if tile_type == "floor":
            surf.fill((40, 40, 60))
            # Subtle pattern
            for i in range(0, TILE_SIZE, 8):
                for j in range(0, TILE_SIZE, 8):
                    if (i + j) % 16 == 0:
                        pygame.draw.rect(surf, (45, 45, 65), (i, j, 8, 8))
        elif tile_type == "wall":
            surf.fill((60, 40, 80))
            # Brick pattern
            for i in range(0, TILE_SIZE, 8):
                offset = 4 if (i // 8) % 2 else 0
                pygame.draw.line(surf, (70, 50, 90), (0, i), (TILE_SIZE, i))
                for j in range(offset, TILE_SIZE, 16):
                    pygame.draw.line(surf, (70, 50, 90), (j, i), (j, i+8))
        elif tile_type == "door":
            surf.fill((80, 60, 40))
            pygame.draw.rect(surf, (60, 40, 20), (4, 4, TILE_SIZE-8, TILE_SIZE-4))
            pygame.draw.circle(surf, YELLOW, (TILE_SIZE-8, TILE_SIZE//2), 3)
        elif tile_type == "save":
            surf.fill((40, 40, 60))
            # Glowing save point
            pygame.draw.polygon(surf, YELLOW, [
                (TILE_SIZE//2, 4), (TILE_SIZE-4, TILE_SIZE//2),
                (TILE_SIZE//2, TILE_SIZE-4), (4, TILE_SIZE//2)
            ])
            pygame.draw.polygon(surf, WHITE, [
                (TILE_SIZE//2, 8), (TILE_SIZE-8, TILE_SIZE//2),
                (TILE_SIZE//2, TILE_SIZE-8), (8, TILE_SIZE//2)
            ])
        elif tile_type == "dark_floor":
            surf.fill((20, 20, 30))
            for i in range(0, TILE_SIZE, 4):
                pygame.draw.line(surf, (25, 25, 35), (i, 0), (i, TILE_SIZE))
                
        return surf

# ═══════════════════════════════════════════════════════════════════════════════
# SOUND SYSTEM (Procedural audio)
# ═══════════════════════════════════════════════════════════════════════════════

class SoundSystem:
    """Generates and manages sound effects procedurally"""
    
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        if enabled:
            pygame.mixer.init(44100, -16, 2, 512)
            self._generate_sounds()
    
    def _generate_sounds(self):
        """Generate basic sound effects"""
        sample_rate = 44100
        
        # Menu select beep
        self.sounds['select'] = self._create_tone(440, 0.1, 'square')
        self.sounds['confirm'] = self._create_tone(880, 0.15, 'square')
        self.sounds['cancel'] = self._create_tone(220, 0.1, 'square')
        self.sounds['hit'] = self._create_noise(0.1)
        self.sounds['heal'] = self._create_tone(660, 0.3, 'sine')
        self.sounds['text'] = self._create_tone(330, 0.03, 'square')
        self.sounds['damage'] = self._create_tone(110, 0.2, 'sawtooth')
        self.sounds['victory'] = self._create_tone(880, 0.5, 'sine')
        
    def _create_tone(self, freq: float, duration: float, 
                     wave_type: str = 'sine') -> pygame.mixer.Sound:
        """Create a tone sound effect"""
        sample_rate = 44100
        n_samples = int(duration * sample_rate)
        
        import array
        buf = array.array('h')
        
        for i in range(n_samples):
            t = i / sample_rate
            if wave_type == 'sine':
                val = math.sin(2 * math.pi * freq * t)
            elif wave_type == 'square':
                val = 1.0 if math.sin(2 * math.pi * freq * t) > 0 else -1.0
            elif wave_type == 'sawtooth':
                val = 2.0 * (t * freq - math.floor(t * freq + 0.5))
            else:
                val = math.sin(2 * math.pi * freq * t)
            
            # Apply envelope
            envelope = 1.0
            if i < n_samples * 0.1:
                envelope = i / (n_samples * 0.1)
            elif i > n_samples * 0.7:
                envelope = (n_samples - i) / (n_samples * 0.3)
            
            sample = int(val * envelope * 16000)
            buf.append(sample)
            buf.append(sample)  # Stereo
            
        return pygame.mixer.Sound(buffer=buf)
    
    def _create_noise(self, duration: float) -> pygame.mixer.Sound:
        """Create white noise sound effect"""
        sample_rate = 44100
        n_samples = int(duration * sample_rate)
        
        import array
        buf = array.array('h')
        
        for i in range(n_samples):
            envelope = 1.0 - (i / n_samples)
            sample = int(random.uniform(-1, 1) * envelope * 8000)
            buf.append(sample)
            buf.append(sample)
            
        return pygame.mixer.Sound(buffer=buf)
    
    def play(self, sound_name: str):
        """Play a sound effect"""
        if self.enabled and sound_name in self.sounds:
            self.sounds[sound_name].play()

# ═══════════════════════════════════════════════════════════════════════════════
# PARTY MEMBER CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class PartyMember:
    """Represents a party member"""
    
    def __init__(self, name: str, char_type: str = "cat", 
                 palette: List[Tuple[int,int,int]] = None):
        self.name = name
        self.char_type = char_type
        self.palette = palette or [CAT_PURPLE, WHITE]
        
        self.stats = Stats()
        self.level = 1
        self.exp = 0
        self.exp_to_next = 100
        
        self.weapon: Optional[Item] = None
        self.armor: Optional[Item] = None
        self.spells: List[Spell] = []
        self.acts: List[Dict] = []  # ACT options specific to this character
        
        self.sprite = SpriteGenerator.create_character(32, 48, self.palette, char_type)
        self.portrait = self._create_portrait()
        
        self._init_default_spells()
        self._init_default_acts()
        
    def _create_portrait(self) -> pygame.Surface:
        """Create a larger portrait for dialogue"""
        return pygame.transform.scale(self.sprite, (64, 96))
    
    def _init_default_spells(self):
        """Initialize default spells based on character"""
        if "cat" in self.char_type.lower() or self.name.lower() == "kris":
            self.spells = [
                Spell("Heal Prayer", "Restore HP to one ally", 32, heal_amount=40),
                Spell("Pacify", "May end a tired enemy's fight", 16, effect="pacify"),
            ]
        else:
            self.spells = [
                Spell("Rude Buster", "Deals damage to one enemy", 50, damage=80),
                Spell("Red Buster", "Deals big damage, heals team", 100, damage=120, heal_amount=20),
            ]
    
    def _init_default_acts(self):
        """Initialize ACT options"""
        self.acts = [
            {"name": "Check", "description": "Check enemy stats", "tp_gain": 0},
            {"name": "Talk", "description": "Try to reason with enemy", "tp_gain": 10},
            {"name": "Compliment", "description": "Say something nice", "tp_gain": 15},
            {"name": "Flirt", "description": "Attempt flirtation", "tp_gain": 20},
        ]
    
    def take_damage(self, amount: int) -> int:
        """Take damage, return actual damage taken"""
        actual = max(1, amount - self.stats.defense // 5)
        self.stats.hp = max(0, self.stats.hp - actual)
        return actual
    
    def heal(self, amount: int) -> int:
        """Heal HP, return actual healing"""
        actual = min(amount, self.stats.max_hp - self.stats.hp)
        self.stats.hp += actual
        return actual
    
    def gain_tp(self, amount: int):
        """Gain TP"""
        self.stats.tp = min(self.stats.max_tp, self.stats.tp + amount)
    
    def use_tp(self, amount: int) -> bool:
        """Use TP, return True if successful"""
        if self.stats.tp >= amount:
            self.stats.tp -= amount
            return True
        return False
    
    def is_alive(self) -> bool:
        return self.stats.hp > 0
    
    def gain_exp(self, amount: int) -> bool:
        """Gain EXP, return True if leveled up"""
        self.exp += amount
        if self.exp >= self.exp_to_next:
            self.level_up()
            return True
        return False
    
    def level_up(self):
        """Level up the character"""
        self.level += 1
        self.exp -= self.exp_to_next
        self.exp_to_next = int(self.exp_to_next * 1.5)
        
        # Stat increases
        self.stats.max_hp += 5
        self.stats.hp = self.stats.max_hp
        self.stats.attack += 2
        self.stats.defense += 2
        self.stats.magic += 2
        

# ═══════════════════════════════════════════════════════════════════════════════
# ENEMY CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class Enemy:
    """Base enemy class"""
    
    def __init__(self, name: str, hp: int = 50, attack: int = 10, defense: int = 5):
        self.name = name
        self.stats = Stats(hp=hp, max_hp=hp, attack=attack, defense=defense)
        self.mercy = 0  # 0-100, can spare at 100
        self.tired = False
        self.dialogue: List[str] = []
        self.flavor_text: List[str] = []
        self.check_text = f"* {name} - ATK {attack} DEF {defense}\n* Just a regular enemy."
        
        self.sprite = SpriteGenerator.create_character(64, 64, [PURPLE, WHITE], "monster")
        self.attack_patterns: List[Callable] = []
        self.current_pattern = 0
        
        self.gold_drop = random.randint(10, 50)
        self.exp_drop = random.randint(5, 20)
        
        self._init_dialogue()
        self._init_attacks()
        
    def _init_dialogue(self):
        """Initialize enemy dialogue"""
        self.dialogue = [
            f"* {self.name} blocks the way!",
            f"* {self.name} is acting suspicious.",
            f"* {self.name} seems tired.",
        ]
        self.flavor_text = [
            "* Smells like darkness.",
            "* The air crackles with tension.",
        ]
        
    def _init_attacks(self):
        """Initialize attack patterns - to be overridden"""
        self.attack_patterns = [
            self._basic_bullet_circle,
            self._basic_bullet_wave,
        ]
    
    def _basic_bullet_circle(self, bullet_manager: 'BulletManager'):
        """Basic circular bullet pattern"""
        cx, cy = 320, 340
        for angle in range(0, 360, 30):
            rad = math.radians(angle)
            bx = cx + math.cos(rad) * 80
            by = cy + math.sin(rad) * 80
            vx = math.cos(rad) * -2
            vy = math.sin(rad) * -2
            bullet_manager.spawn_bullet(bx, by, vx, vy)
    
    def _basic_bullet_wave(self, bullet_manager: 'BulletManager'):
        """Basic wave pattern"""
        for i in range(5):
            bullet_manager.spawn_bullet(
                200 + i * 50, 280,
                0, 2,
                delay=i * 10
            )
    
    def get_attack(self) -> Callable:
        """Get next attack pattern"""
        pattern = self.attack_patterns[self.current_pattern % len(self.attack_patterns)]
        self.current_pattern += 1
        return pattern
    
    def take_damage(self, amount: int) -> int:
        """Take damage"""
        actual = max(1, amount - self.stats.defense // 5)
        self.stats.hp = max(0, self.stats.hp - actual)
        return actual
    
    def increase_mercy(self, amount: int):
        """Increase mercy percentage"""
        self.mercy = min(100, self.mercy + amount)
        if self.mercy >= 100:
            self.tired = True
    
    def can_spare(self) -> bool:
        return self.mercy >= 100 or self.tired
    
    def is_alive(self) -> bool:
        return self.stats.hp > 0
    
    def get_random_dialogue(self) -> str:
        return random.choice(self.dialogue) if self.dialogue else ""
    
    def get_flavor_text(self) -> str:
        return random.choice(self.flavor_text) if self.flavor_text else ""

# ═══════════════════════════════════════════════════════════════════════════════
# SPECIALIZED ENEMIES
# ═══════════════════════════════════════════════════════════════════════════════

class DarknerEnemy(Enemy):
    """A basic Darkner enemy"""
    def __init__(self):
        super().__init__("Rudinn", hp=60, attack=12, defense=4)
        self.check_text = "* Rudinn - ATK 12 DEF 4\n* A diamond-shaped Darkner.\n* Seems to worship cards."
        self.dialogue = [
            "* Long live the King!",
            "* You'll never defeat us!",
            "* For the glory of Card Kingdom!",
        ]
        self.sprite = SpriteGenerator.create_character(64, 64, [CYAN, WHITE], "monster")
        
    def _init_attacks(self):
        self.attack_patterns = [
            self._diamond_rain,
            self._card_spread,
        ]
    
    def _diamond_rain(self, bullet_manager: 'BulletManager'):
        """Rain of diamond bullets"""
        for i in range(8):
            x = random.randint(200, 440)
            bullet_manager.spawn_bullet(x, 280, 0, 3, bullet_type="diamond", 
                                        color=CYAN, delay=i*8)
    
    def _card_spread(self, bullet_manager: 'BulletManager'):
        """Spread of card-shaped bullets"""
        for angle in [-30, -15, 0, 15, 30]:
            rad = math.radians(angle + 90)
            bullet_manager.spawn_bullet(
                320, 300,
                math.cos(rad) * 3, math.sin(rad) * 3,
                bullet_type="spade", color=WHITE
            )

class CatEnemy(Enemy):
    """A cat-themed enemy (because cat theme)"""
    def __init__(self):
        super().__init__("Whiskerz", hp=45, attack=8, defense=6)
        self.check_text = "* Whiskerz - ATK 8 DEF 6\n* A mischievous dark cat.\n* Just wants scritches."
        self.dialogue = [
            "* Meow? (menacingly)",
            "* *hisses in darkness*",
            "* Purrhaps we can be friends?",
        ]
        self.sprite = SpriteGenerator.create_character(64, 64, [CAT_PURPLE, CAT_PINK], "cat")
        
    def _init_attacks(self):
        self.attack_patterns = [
            self._paw_swipe,
            self._yarn_ball,
        ]
    
    def _paw_swipe(self, bullet_manager: 'BulletManager'):
        """Paw swipe pattern"""
        for i in range(6):
            bullet_manager.spawn_bullet(
                200 + i * 40, 280,
                (i - 3) * 0.5, 3,
                bullet_type="star", color=CAT_PINK, delay=i*5
            )
    
    def _yarn_ball(self, bullet_manager: 'BulletManager'):
        """Bouncing yarn ball"""
        bullet_manager.spawn_bullet(220, 300, 2, 0, bullet_type="basic", 
                                   color=CAT_PURPLE, bouncy=True)
        bullet_manager.spawn_bullet(420, 300, -2, 0, bullet_type="basic", 
                                   color=CAT_PURPLE, bouncy=True)

class BossEnemy(Enemy):
    """Base class for boss enemies"""
    def __init__(self, name: str, hp: int = 500, attack: int = 25, defense: int = 10):
        super().__init__(name, hp, attack, defense)
        self.is_boss = True
        self.phase = 1
        self.max_phases = 3
        
    def check_phase_transition(self) -> bool:
        """Check if should transition to next phase"""
        hp_percent = self.stats.hp / self.stats.max_hp
        if self.phase == 1 and hp_percent <= 0.66:
            self.phase = 2
            return True
        elif self.phase == 2 and hp_percent <= 0.33:
            self.phase = 3
            return True
        return False

class KingEnemy(BossEnemy):
    """The King of Spades boss"""
    def __init__(self):
        super().__init__("King", hp=800, attack=30, defense=15)
        self.check_text = "* King - ATK 30 DEF 15\n* The tyrannical King of Spades.\n* His heart has been hardened."
        self.dialogue = [
            "* YOU DARE CHALLENGE ME?!",
            "* Lightners... you've caused enough trouble!",
            "* My people suffered because of you!",
        ]
        self.sprite = pygame.Surface((96, 96))
        pygame.draw.rect(self.sprite, BLUE, (0, 0, 96, 96))
        pygame.draw.polygon(self.sprite, YELLOW, [(48, 8), (88, 48), (48, 88), (8, 48)])

# ═══════════════════════════════════════════════════════════════════════════════
# BULLET SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Bullet:
    x: float
    y: float
    vx: float
    vy: float
    sprite: pygame.Surface
    alive: bool = True
    delay: int = 0
    bouncy: bool = False
    homing: float = 0.0
    lifetime: int = 300
    rotation: float = 0.0
    rotation_speed: float = 0.0

class BulletManager:
    """Manages all bullets in bullet hell sequences"""
    
    def __init__(self, arena_rect: pygame.Rect):
        self.bullets: List[Bullet] = []
        self.arena = arena_rect
        self.bullet_sprites: Dict[str, pygame.Surface] = {}
        self._init_bullet_sprites()
        
    def _init_bullet_sprites(self):
        """Pre-generate bullet sprites"""
        self.bullet_sprites = {
            'basic': SpriteGenerator.create_bullet('basic', WHITE),
            'star': SpriteGenerator.create_bullet('star', YELLOW),
            'diamond': SpriteGenerator.create_bullet('diamond', CYAN),
            'bone': SpriteGenerator.create_bullet('bone', WHITE),
            'spade': SpriteGenerator.create_bullet('spade', BLACK),
        }
        
    def spawn_bullet(self, x: float, y: float, vx: float, vy: float,
                     bullet_type: str = 'basic', color: Tuple[int,int,int] = WHITE,
                     delay: int = 0, bouncy: bool = False, homing: float = 0.0):
        """Spawn a new bullet"""
        if bullet_type in self.bullet_sprites:
            sprite = self.bullet_sprites[bullet_type].copy()
        else:
            sprite = SpriteGenerator.create_bullet(bullet_type, color)
            
        bullet = Bullet(x, y, vx, vy, sprite, delay=delay, bouncy=bouncy, homing=homing)
        self.bullets.append(bullet)
        
    def update(self, soul_pos: Tuple[float, float]):
        """Update all bullets"""
        for bullet in self.bullets:
            if bullet.delay > 0:
                bullet.delay -= 1
                continue
                
            # Homing behavior
            if bullet.homing > 0:
                dx = soul_pos[0] - bullet.x
                dy = soul_pos[1] - bullet.y
                dist = math.sqrt(dx*dx + dy*dy)
                if dist > 0:
                    bullet.vx += (dx / dist) * bullet.homing
                    bullet.vy += (dy / dist) * bullet.homing
                    
            bullet.x += bullet.vx
            bullet.y += bullet.vy
            bullet.lifetime -= 1
            bullet.rotation += bullet.rotation_speed
            
            # Bouncy bullets
            if bullet.bouncy:
                if bullet.x < self.arena.left or bullet.x > self.arena.right:
                    bullet.vx *= -1
                if bullet.y < self.arena.top or bullet.y > self.arena.bottom:
                    bullet.vy *= -1
            else:
                # Remove if outside arena
                if not self.arena.inflate(50, 50).collidepoint(bullet.x, bullet.y):
                    bullet.alive = False
                    
            if bullet.lifetime <= 0:
                bullet.alive = False
                
        # Remove dead bullets
        self.bullets = [b for b in self.bullets if b.alive]
        
    def check_collision(self, soul_rect: pygame.Rect) -> bool:
        """Check if soul collides with any bullet"""
        for bullet in self.bullets:
            if bullet.delay > 0:
                continue
            bullet_rect = bullet.sprite.get_rect(center=(bullet.x, bullet.y))
            # Smaller hitbox for fairness
            bullet_rect = bullet_rect.inflate(-4, -4)
            if soul_rect.colliderect(bullet_rect):
                return True
        return False
    
    def draw(self, surface: pygame.Surface):
        """Draw all bullets"""
        for bullet in self.bullets:
            if bullet.delay > 0:
                continue
            if bullet.rotation != 0:
                rotated = pygame.transform.rotate(bullet.sprite, bullet.rotation)
                rect = rotated.get_rect(center=(bullet.x, bullet.y))
                surface.blit(rotated, rect)
            else:
                rect = bullet.sprite.get_rect(center=(bullet.x, bullet.y))
                surface.blit(bullet.sprite, rect)
                
    def clear(self):
        """Clear all bullets"""
        self.bullets.clear()

# ═══════════════════════════════════════════════════════════════════════════════
# SOUL (PLAYER IN BATTLE)
# ═══════════════════════════════════════════════════════════════════════════════

class Soul:
    """Player soul in battle sequences"""
    
    def __init__(self, arena_rect: pygame.Rect):
        self.arena = arena_rect
        self.x = arena_rect.centerx
        self.y = arena_rect.centery
        self.speed = 4
        self.mode = SoulMode.RED
        self.sprite = SpriteGenerator.create_soul(SOUL_RED)
        self.invincible = 0
        self.gravity = 0.0
        self.vy = 0.0
        self.grounded = False
        
    def update(self, keys):
        """Update soul position"""
        if self.invincible > 0:
            self.invincible -= 1
            
        dx, dy = 0, 0
        
        if self.mode == SoulMode.RED:
            # Free movement
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx = -self.speed
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx = self.speed
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                dy = -self.speed
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dy = self.speed
                
            # Diagonal movement normalization
            if dx != 0 and dy != 0:
                dx *= 0.707
                dy *= 0.707
                
        elif self.mode == SoulMode.BLUE:
            # Platformer movement with gravity
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx = -self.speed
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx = self.speed
                
            self.vy += 0.5  # Gravity
            if (keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_z]) and self.grounded:
                self.vy = -10
                self.grounded = False
                
            dy = self.vy
            
        # Apply movement
        self.x += dx
        self.y += dy
        
        # Keep in arena
        self.x = max(self.arena.left + 8, min(self.arena.right - 8, self.x))
        
        if self.mode == SoulMode.BLUE:
            if self.y >= self.arena.bottom - 8:
                self.y = self.arena.bottom - 8
                self.vy = 0
                self.grounded = True
            self.y = max(self.arena.top + 8, self.y)
        else:
            self.y = max(self.arena.top + 8, min(self.arena.bottom - 8, self.y))
            
    def get_rect(self) -> pygame.Rect:
        """Get collision rect (smaller than sprite for fairness)"""
        return pygame.Rect(self.x - 4, self.y - 4, 8, 8)
    
    def set_mode(self, mode: SoulMode):
        """Change soul mode"""
        self.mode = mode
        if mode == SoulMode.RED:
            self.sprite = SpriteGenerator.create_soul(SOUL_RED)
            self.gravity = 0
        elif mode == SoulMode.BLUE:
            self.sprite = SpriteGenerator.create_soul(BLUE)
            self.gravity = 0.5
        elif mode == SoulMode.YELLOW:
            self.sprite = SpriteGenerator.create_soul(YELLOW)
        elif mode == SoulMode.GREEN:
            self.sprite = SpriteGenerator.create_soul(GREEN)
            
    def draw(self, surface: pygame.Surface):
        """Draw the soul"""
        if self.invincible > 0 and self.invincible % 4 < 2:
            return  # Flashing when invincible
        rect = self.sprite.get_rect(center=(self.x, self.y))
        surface.blit(self.sprite, rect)

# ═══════════════════════════════════════════════════════════════════════════════
# DIALOGUE SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class DialogueLine:
    text: str
    speaker: str = ""
    portrait: Optional[pygame.Surface] = None
    choices: List[str] = field(default_factory=list)
    
class DialogueSystem:
    """Handles dialogue display and progression"""
    
    def __init__(self, sound_system: SoundSystem):
        self.sound = sound_system
        self.current_dialogue: List[DialogueLine] = []
        self.current_index = 0
        self.displayed_text = ""
        self.text_speed = 2
        self.text_timer = 0
        self.char_index = 0
        self.active = False
        self.choice_index = 0
        self.waiting_for_choice = False
        self.choice_made: Optional[int] = None
        
        self.font = None  # Set after pygame init
        self.box_rect = pygame.Rect(50, 350, 540, 120)
        
    def set_font(self, font: pygame.font.Font):
        self.font = font
        
    def start(self, dialogue: List[DialogueLine]):
        """Start a dialogue sequence"""
        self.current_dialogue = dialogue
        self.current_index = 0
        self.displayed_text = ""
        self.char_index = 0
        self.active = True
        self.waiting_for_choice = False
        self.choice_made = None
        
    def update(self) -> bool:
        """Update dialogue, return True if still active"""
        if not self.active or self.current_index >= len(self.current_dialogue):
            self.active = False
            return False
            
        line = self.current_dialogue[self.current_index]
        
        if self.waiting_for_choice:
            return True
            
        # Text animation
        self.text_timer += 1
        if self.text_timer >= self.text_speed:
            self.text_timer = 0
            if self.char_index < len(line.text):
                self.displayed_text += line.text[self.char_index]
                self.char_index += 1
                if line.text[self.char_index - 1] not in ' \n':
                    self.sound.play('text')
                    
        return True
    
    def advance(self) -> Optional[int]:
        """Advance dialogue or make choice, return choice index if applicable"""
        if not self.active:
            return None
            
        line = self.current_dialogue[self.current_index]
        
        # If text not fully displayed, show all
        if self.char_index < len(line.text):
            self.displayed_text = line.text
            self.char_index = len(line.text)
            return None
            
        # If choices available
        if line.choices and not self.waiting_for_choice:
            self.waiting_for_choice = True
            return None
            
        if self.waiting_for_choice:
            self.choice_made = self.choice_index
            self.waiting_for_choice = False
            self.current_index += 1
            self._reset_line()
            return self.choice_made
            
        # Advance to next line
        self.current_index += 1
        self._reset_line()
        return None
    
    def _reset_line(self):
        """Reset for new line"""
        self.displayed_text = ""
        self.char_index = 0
        self.choice_index = 0
        
    def move_choice(self, direction: int):
        """Move choice selection"""
        if not self.waiting_for_choice:
            return
        line = self.current_dialogue[self.current_index]
        if line.choices:
            self.choice_index = (self.choice_index + direction) % len(line.choices)
            self.sound.play('select')
            
    def draw(self, surface: pygame.Surface):
        """Draw dialogue box"""
        if not self.active or self.current_index >= len(self.current_dialogue):
            return
            
        line = self.current_dialogue[self.current_index]
        
        # Draw box
        pygame.draw.rect(surface, BLACK, self.box_rect)
        pygame.draw.rect(surface, WHITE, self.box_rect, 3)
        
        # Draw portrait if exists
        text_x = self.box_rect.x + 20
        if line.portrait:
            surface.blit(line.portrait, (self.box_rect.x + 10, self.box_rect.y + 10))
            text_x = self.box_rect.x + 90
            
        # Draw speaker name
        if line.speaker and self.font:
            name_surf = self.font.render(line.speaker, True, YELLOW)
            surface.blit(name_surf, (text_x, self.box_rect.y + 10))
            
        # Draw text
        if self.font:
            y_offset = 35 if line.speaker else 15
            self._draw_wrapped_text(surface, self.displayed_text, 
                                   text_x, self.box_rect.y + y_offset,
                                   self.box_rect.width - (text_x - self.box_rect.x) - 20)
            
        # Draw choices
        if self.waiting_for_choice and line.choices:
            for i, choice in enumerate(line.choices):
                color = YELLOW if i == self.choice_index else WHITE
                prefix = "❤ " if i == self.choice_index else "  "
                choice_surf = self.font.render(prefix + choice, True, color)
                surface.blit(choice_surf, (text_x + i * 150, self.box_rect.bottom - 30))
                
    def _draw_wrapped_text(self, surface: pygame.Surface, text: str, 
                          x: int, y: int, max_width: int):
        """Draw text with word wrapping"""
        words = text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + word + " "
            if self.font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word + " "
        if current_line:
            lines.append(current_line)
            
        for i, line in enumerate(lines):
            text_surf = self.font.render(line, True, WHITE)
            surface.blit(text_surf, (x, y + i * 22))

# ═══════════════════════════════════════════════════════════════════════════════
# BATTLE SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

class BattleSystem:
    """Handles turn-based combat with bullet hell"""
    
    def __init__(self, party: List[PartyMember], enemies: List[Enemy],
                 sound_system: SoundSystem, dialogue_system: DialogueSystem):
        self.party = party
        self.enemies = enemies
        self.sound = sound_system
        self.dialogue = dialogue_system
        
        self.state = BattleState.MENU
        self.current_member_index = 0
        self.menu_index = 0
        self.target_index = 0
        self.action_queue: List[Dict] = []
        
        # Arena for bullet hell
        self.arena_rect = pygame.Rect(170, 280, 300, 140)
        self.soul = Soul(self.arena_rect)
        self.bullet_manager = BulletManager(self.arena_rect)
        
        # Timing
        self.turn_timer = 0
        self.attack_duration = 180  # 3 seconds at 60fps
        
        # Menu options
        self.menu_options = ["FIGHT", "ACT", "ITEM", "MERCY"]
        self.sub_menu: List[str] = []
        self.sub_menu_index = 0
        self.in_sub_menu = False
        
        self.battle_text = ""
        self.exp_gained = 0
        self.gold_gained = 0
        
        self.font = None
        
    def set_font(self, font: pygame.font.Font):
        self.font = font
        
    def update(self, keys_pressed: Dict, keys_just_pressed: Dict) -> Optional[str]:
        """Update battle, return result if battle ends"""
        
        if self.state == BattleState.MENU:
            self._handle_menu_input(keys_just_pressed)
            
        elif self.state == BattleState.TARGET_SELECT:
            self._handle_target_input(keys_just_pressed)
            
        elif self.state == BattleState.ACTION_EXECUTE:
            self._execute_actions()
            
        elif self.state == BattleState.ENEMY_TURN:
            self._start_enemy_attack()
            
        elif self.state == BattleState.BULLET_HELL:
            self._update_bullet_hell(keys_pressed, keys_just_pressed)
            
        elif self.state == BattleState.VICTORY:
            if keys_just_pressed.get(pygame.K_z) or keys_just_pressed.get(pygame.K_RETURN):
                return "victory"
                
        elif self.state == BattleState.DEFEAT:
            if keys_just_pressed.get(pygame.K_z) or keys_just_pressed.get(pygame.K_RETURN):
                return "defeat"
                
        # Check win/loss conditions
        if all(not e.is_alive() or e.can_spare() for e in self.enemies):
            if self.state not in [BattleState.VICTORY, BattleState.DEFEAT]:
                self._victory()
                
        if all(not m.is_alive() for m in self.party):
            if self.state not in [BattleState.VICTORY, BattleState.DEFEAT]:
                self._defeat()
                
        return None
    
    def _handle_menu_input(self, keys: Dict):
        """Handle main menu navigation"""
        if keys.get(pygame.K_LEFT) or keys.get(pygame.K_a):
            self.menu_index = (self.menu_index - 1) % len(self.menu_options)
            self.sound.play('select')
        elif keys.get(pygame.K_RIGHT) or keys.get(pygame.K_d):
            self.menu_index = (self.menu_index + 1) % len(self.menu_options)
            self.sound.play('select')
        elif keys.get(pygame.K_UP) or keys.get(pygame.K_w):
            if self.in_sub_menu:
                self.sub_menu_index = (self.sub_menu_index - 1) % max(1, len(self.sub_menu))
                self.sound.play('select')
        elif keys.get(pygame.K_DOWN) or keys.get(pygame.K_s):
            if self.in_sub_menu:
                self.sub_menu_index = (self.sub_menu_index + 1) % max(1, len(self.sub_menu))
                self.sound.play('select')
        elif keys.get(pygame.K_z) or keys.get(pygame.K_RETURN):
            self._select_menu_option()
        elif keys.get(pygame.K_x) or keys.get(pygame.K_LSHIFT):
            if self.in_sub_menu:
                self.in_sub_menu = False
                self.sub_menu = []
                self.sound.play('cancel')
                
    def _select_menu_option(self):
        """Handle menu selection"""
        option = self.menu_options[self.menu_index]
        member = self.party[self.current_member_index]
        
        if not self.in_sub_menu:
            if option == "FIGHT":
                self.state = BattleState.TARGET_SELECT
                self.sound.play('confirm')
            elif option == "ACT":
                self.sub_menu = [act['name'] for act in member.acts]
                self.in_sub_menu = True
                self.sub_menu_index = 0
                self.sound.play('confirm')
            elif option == "ITEM":
                # TODO: Implement inventory
                self.sub_menu = ["Healing Item", "Dark Candy", "Nothing"]
                self.in_sub_menu = True
                self.sub_menu_index = 0
                self.sound.play('confirm')
            elif option == "MERCY":
                self.sub_menu = ["Spare", "Flee"]
                self.in_sub_menu = True
                self.sub_menu_index = 0
                self.sound.play('confirm')
        else:
            self._execute_sub_menu_action(option)
            
    def _execute_sub_menu_action(self, main_option: str):
        """Execute submenu action"""
        member = self.party[self.current_member_index]
        
        if main_option == "ACT":
            act = member.acts[self.sub_menu_index]
            self.action_queue.append({
                'type': 'act',
                'member': member,
                'act': act,
                'target': self.enemies[0]  # TODO: target selection
            })
            self.sound.play('confirm')
            self._advance_turn()
            
        elif main_option == "ITEM":
            # Simple healing for now
            if self.sub_menu_index == 0:  # Healing item
                member.heal(30)
                self.battle_text = f"* {member.name} ate the Healing Item.\n* HP restored by 30!"
                self.sound.play('heal')
            self._advance_turn()
            
        elif main_option == "MERCY":
            if self.sub_menu_index == 0:  # Spare
                spareable = [e for e in self.enemies if e.can_spare()]
                if spareable:
                    for e in spareable:
                        e.stats.hp = 0  # Remove from battle
                        self.exp_gained += e.exp_drop // 2
                        self.gold_gained += e.gold_drop
                    self.battle_text = f"* YOU SPARED {spareable[0].name}!"
                    self.sound.play('confirm')
                else:
                    self.battle_text = "* But nobody could be spared..."
            else:  # Flee
                self.battle_text = "* You couldn't escape!"
            self._advance_turn()
            
        self.in_sub_menu = False
        self.sub_menu = []
        
    def _handle_target_input(self, keys: Dict):
        """Handle target selection"""
        alive_enemies = [e for e in self.enemies if e.is_alive()]
        
        if keys.get(pygame.K_UP) or keys.get(pygame.K_w):
            self.target_index = (self.target_index - 1) % max(1, len(alive_enemies))
            self.sound.play('select')
        elif keys.get(pygame.K_DOWN) or keys.get(pygame.K_s):
            self.target_index = (self.target_index + 1) % max(1, len(alive_enemies))
            self.sound.play('select')
        elif keys.get(pygame.K_z) or keys.get(pygame.K_RETURN):
            member = self.party[self.current_member_index]
            target = alive_enemies[self.target_index]
            self.action_queue.append({
                'type': 'fight',
                'member': member,
                'target': target
            })
            self.sound.play('confirm')
            self._advance_turn()
        elif keys.get(pygame.K_x) or keys.get(pygame.K_LSHIFT):
            self.state = BattleState.MENU
            self.sound.play('cancel')
            
    def _advance_turn(self):
        """Advance to next party member or enemy turn"""
        self.current_member_index += 1
        self.target_index = 0
        
        if self.current_member_index >= len(self.party):
            # All party members acted, execute actions then enemy turn
            self.state = BattleState.ACTION_EXECUTE
        else:
            # Skip dead members
            while (self.current_member_index < len(self.party) and 
                   not self.party[self.current_member_index].is_alive()):
                self.current_member_index += 1
            if self.current_member_index >= len(self.party):
                self.state = BattleState.ACTION_EXECUTE
            else:
                self.state = BattleState.MENU
                
    def _execute_actions(self):
        """Execute queued actions"""
        self.turn_timer += 1
        
        if self.turn_timer > 30 and self.action_queue:
            action = self.action_queue.pop(0)
            self._resolve_action(action)
            self.turn_timer = 0
        elif not self.action_queue and self.turn_timer > 30:
            self.state = BattleState.ENEMY_TURN
            self.turn_timer = 0
            
    def _resolve_action(self, action: Dict):
        """Resolve a single action"""
        if action['type'] == 'fight':
            member = action['member']
            target = action['target']
            damage = max(1, member.stats.attack - target.stats.defense // 4)
            damage += random.randint(-3, 5)
            actual = target.take_damage(damage)
            self.battle_text = f"* {member.name} attacked!\n* {actual} damage to {target.name}!"
            self.sound.play('hit')
            
            # TP gain on attack
            member.gain_tp(16)
            
            if not target.is_alive():
                self.exp_gained += target.exp_drop
                self.gold_gained += target.gold_drop
                
        elif action['type'] == 'act':
            member = action['member']
            act = action['act']
            target = action['target']
            
            if act['name'] == "Check":
                self.battle_text = target.check_text
            elif act['name'] == "Talk":
                target.increase_mercy(15)
                self.battle_text = f"* You talked to {target.name}.\n* Its mercy increased!"
            elif act['name'] == "Compliment":
                target.increase_mercy(20)
                self.battle_text = f"* You complimented {target.name}!\n* It seems pleased."
            elif act['name'] == "Flirt":
                target.increase_mercy(25)
                self.battle_text = f"* You flirted with {target.name}...\n* It's blushing?"
                
            member.gain_tp(act.get('tp_gain', 10))
            
    def _start_enemy_attack(self):
        """Start enemy attack phase"""
        alive_enemies = [e for e in self.enemies if e.is_alive()]
        
        if alive_enemies:
            # Pick random enemy to attack
            attacker = random.choice(alive_enemies)
            pattern = attacker.get_attack()
            pattern(self.bullet_manager)
            self.battle_text = attacker.get_flavor_text()
            
        self.state = BattleState.BULLET_HELL
        self.turn_timer = 0
        self.soul.x = self.arena_rect.centerx
        self.soul.y = self.arena_rect.centery
        
    def _update_bullet_hell(self, keys_pressed: Dict, keys_just_pressed: Dict):
        """Update bullet hell sequence"""
        self.turn_timer += 1
        
        self.soul.update(keys_pressed)
        self.bullet_manager.update((self.soul.x, self.soul.y))
        
        # Check collision
        if self.soul.invincible <= 0:
            if self.bullet_manager.check_collision(self.soul.get_rect()):
                # Damage party (distribute among alive members)
                alive = [m for m in self.party if m.is_alive()]
                if alive:
                    target = random.choice(alive)
                    damage = 10 + random.randint(0, 5)
                    target.take_damage(damage)
                    self.sound.play('damage')
                    self.soul.invincible = 60
                    
        # End attack phase
        if self.turn_timer >= self.attack_duration:
            self._end_enemy_turn()
            
    def _end_enemy_turn(self):
        """End enemy turn and return to menu"""
        self.bullet_manager.clear()
        self.state = BattleState.MENU
        self.current_member_index = 0
        self.turn_timer = 0
        
        # Skip dead members
        while (self.current_member_index < len(self.party) and 
               not self.party[self.current_member_index].is_alive()):
            self.current_member_index += 1
            
    def _victory(self):
        """Handle battle victory"""
        self.state = BattleState.VICTORY
        self.battle_text = f"* YOU WON!\n* Got {self.exp_gained} EXP and {self.gold_gained} Gold!"
        self.sound.play('victory')
        
        # Distribute EXP
        for member in self.party:
            if member.is_alive():
                if member.gain_exp(self.exp_gained):
                    self.battle_text += f"\n* {member.name} leveled up!"
                    
    def _defeat(self):
        """Handle battle defeat"""
        self.state = BattleState.DEFEAT
        self.battle_text = "* Your HP reached 0.\n* You cannot give up just yet..."
        
    def draw(self, surface: pygame.Surface):
        """Draw battle screen"""
        surface.fill(BATTLE_BG)
        
        # Draw enemies
        for i, enemy in enumerate(self.enemies):
            if enemy.is_alive():
                x = 320 - (len(self.enemies) - 1) * 50 + i * 100
                rect = enemy.sprite.get_rect(center=(x, 150))
                surface.blit(enemy.sprite, rect)
                
                # Target indicator
                if self.state == BattleState.TARGET_SELECT:
                    alive_enemies = [e for e in self.enemies if e.is_alive()]
                    if enemy in alive_enemies and alive_enemies.index(enemy) == self.target_index:
                        pygame.draw.polygon(surface, SOUL_RED, [
                            (x, rect.top - 20), (x - 10, rect.top - 35), (x + 10, rect.top - 35)
                        ])
                        
        # Draw arena
        pygame.draw.rect(surface, WHITE, self.arena_rect, 3)
        
        # Draw bullets and soul during bullet hell
        if self.state == BattleState.BULLET_HELL:
            self.bullet_manager.draw(surface)
            self.soul.draw(surface)
            
        # Draw battle text
        if self.font and self.battle_text:
            y = 290
            for line in self.battle_text.split('\n'):
                text_surf = self.font.render(line, True, WHITE)
                surface.blit(text_surf, (180, y))
                y += 22
                
        # Draw party status
        self._draw_party_status(surface)
        
        # Draw menu
        if self.state == BattleState.MENU:
            self._draw_menu(surface)
        elif self.state == BattleState.TARGET_SELECT:
            self._draw_target_select(surface)
            
    def _draw_party_status(self, surface: pygame.Surface):
        """Draw party HP/TP bars"""
        y = 430
        for i, member in enumerate(self.party):
            x = 50 + i * 200
            
            # Name
            if self.font:
                color = YELLOW if i == self.current_member_index and self.state == BattleState.MENU else WHITE
                name_surf = self.font.render(member.name, True, color)
                surface.blit(name_surf, (x, y))
                
            # HP bar
            hp_percent = member.stats.hp / member.stats.max_hp
            bar_width = 100
            pygame.draw.rect(surface, RED, (x, y + 20, bar_width, 10))
            hp_color = HP_GREEN if hp_percent > 0.3 else HP_YELLOW
            pygame.draw.rect(surface, hp_color, (x, y + 20, int(bar_width * hp_percent), 10))
            
            # HP text
            if self.font:
                hp_text = f"HP {member.stats.hp}/{member.stats.max_hp}"
                hp_surf = self.font.render(hp_text, True, WHITE)
                surface.blit(hp_surf, (x + bar_width + 10, y + 16))
                
    def _draw_menu(self, surface: pygame.Surface):
        """Draw battle menu"""
        if not self.font:
            return
            
        # Main menu
        for i, option in enumerate(self.menu_options):
            x = 80 + i * 140
            color = YELLOW if i == self.menu_index else WHITE
            
            # Button background
            pygame.draw.rect(surface, (40, 40, 60), (x - 10, 250, 100, 25))
            pygame.draw.rect(surface, color, (x - 10, 250, 100, 25), 2)
            
            text_surf = self.font.render(option, True, color)
            surface.blit(text_surf, (x, 253))
            
        # Sub menu
        if self.in_sub_menu and self.sub_menu:
            menu_rect = pygame.Rect(180, 290, 280, 120)
            pygame.draw.rect(surface, BLACK, menu_rect)
            pygame.draw.rect(surface, WHITE, menu_rect, 2)
            
            for i, option in enumerate(self.sub_menu[:5]):  # Show max 5 options
                color = YELLOW if i == self.sub_menu_index else WHITE
                prefix = "❤ " if i == self.sub_menu_index else "  "
                text_surf = self.font.render(prefix + option, True, color)
                surface.blit(text_surf, (190, 300 + i * 22))
                
    def _draw_target_select(self, surface: pygame.Surface):
        """Draw target selection prompt"""
        if self.font:
            text_surf = self.font.render("* Select target", True, WHITE)
            surface.blit(text_surf, (180, 290))

# ═══════════════════════════════════════════════════════════════════════════════
# OVERWORLD SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class MapObject:
    x: int
    y: int
    width: int
    height: int
    obj_type: str
    data: Dict = field(default_factory=dict)
    sprite: Optional[pygame.Surface] = None
    
class TileMap:
    """Tile-based map system"""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.tiles: List[List[int]] = [[0 for _ in range(width)] for _ in range(height)]
        self.collision: List[List[bool]] = [[False for _ in range(width)] for _ in range(height)]
        self.objects: List[MapObject] = []
        
        self.tile_sprites: Dict[int, pygame.Surface] = {}
        self._init_tile_sprites()
        
    def _init_tile_sprites(self):
        """Initialize tile sprites"""
        self.tile_sprites[0] = SpriteGenerator.create_tile("floor")
        self.tile_sprites[1] = SpriteGenerator.create_tile("wall")
        self.tile_sprites[2] = SpriteGenerator.create_tile("door")
        self.tile_sprites[3] = SpriteGenerator.create_tile("save")
        self.tile_sprites[4] = SpriteGenerator.create_tile("dark_floor")
        
    def set_tile(self, x: int, y: int, tile_id: int, collision: bool = False):
        """Set a tile"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.tiles[y][x] = tile_id
            self.collision[y][x] = collision
            
    def get_collision(self, x: int, y: int) -> bool:
        """Check collision at tile position"""
        tx, ty = int(x // TILE_SIZE), int(y // TILE_SIZE)
        if 0 <= tx < self.width and 0 <= ty < self.height:
            return self.collision[ty][tx]
        return True  # Outside map = collision
    
    def add_object(self, obj: MapObject):
        """Add an object to the map"""
        self.objects.append(obj)
        
    def get_objects_at(self, x: int, y: int, radius: int = 16) -> List[MapObject]:
        """Get objects near a position"""
        result = []
        for obj in self.objects:
            ox, oy = obj.x + obj.width // 2, obj.y + obj.height // 2
            if abs(ox - x) < radius + obj.width // 2 and abs(oy - y) < radius + obj.height // 2:
                result.append(obj)
        return result
    
    def draw(self, surface: pygame.Surface, camera_x: int, camera_y: int):
        """Draw visible tiles"""
        start_x = max(0, camera_x // TILE_SIZE)
        start_y = max(0, camera_y // TILE_SIZE)
        end_x = min(self.width, (camera_x + SCREEN_WIDTH) // TILE_SIZE + 1)
        end_y = min(self.height, (camera_y + SCREEN_HEIGHT) // TILE_SIZE + 1)
        
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile_id = self.tiles[y][x]
                if tile_id in self.tile_sprites:
                    screen_x = x * TILE_SIZE - camera_x
                    screen_y = y * TILE_SIZE - camera_y
                    surface.blit(self.tile_sprites[tile_id], (screen_x, screen_y))
                    
        # Draw objects
        for obj in self.objects:
            if obj.sprite:
                screen_x = obj.x - camera_x
                screen_y = obj.y - camera_y
                surface.blit(obj.sprite, (screen_x, screen_y))

class PlayerOverworld:
    """Player character in overworld"""
    
    def __init__(self, x: int, y: int, party_leader: PartyMember):
        self.x = x
        self.y = y
        self.speed = 3
        self.facing = "down"
        self.party_leader = party_leader
        self.sprite = party_leader.sprite
        self.hitbox = pygame.Rect(x - 8, y - 8, 16, 16)
        
    def update(self, keys, tilemap: TileMap):
        """Update player position"""
        dx, dy = 0, 0
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -self.speed
            self.facing = "left"
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = self.speed
            self.facing = "right"
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -self.speed
            self.facing = "up"
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = self.speed
            self.facing = "down"
            
        # Collision detection
        new_x = self.x + dx
        new_y = self.y + dy
        
        # Check X movement
        if not tilemap.get_collision(new_x - 8, self.y) and \
           not tilemap.get_collision(new_x + 7, self.y):
            self.x = new_x
            
        # Check Y movement
        if not tilemap.get_collision(self.x, new_y - 8) and \
           not tilemap.get_collision(self.x, new_y + 7):
            self.y = new_y
            
        self.hitbox.center = (self.x, self.y)
        
    def draw(self, surface: pygame.Surface, camera_x: int, camera_y: int):
        """Draw player"""
        screen_x = self.x - camera_x - self.sprite.get_width() // 2
        screen_y = self.y - camera_y - self.sprite.get_height() // 2
        surface.blit(self.sprite, (screen_x, screen_y))

# ═══════════════════════════════════════════════════════════════════════════════
# CHAPTER SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Chapter:
    number: int
    title: str
    subtitle: str
    maps: List[str]
    story_beats: List[Dict]
    bosses: List[str]
    unlocked: bool = False
    completed: bool = False

class ChapterManager:
    """Manages game chapters"""
    
    def __init__(self):
        self.chapters: List[Chapter] = []
        self.current_chapter = 0
        self._init_chapters()
        
    def _init_chapters(self):
        """Initialize all chapters"""
        self.chapters = [
            Chapter(
                number=1,
                title="THE BEGINNING",
                subtitle="A strange door opens...",
                maps=["dark_classroom", "cyber_city_entrance"],
                story_beats=[
                    {"type": "dialogue", "content": "You have entered the Dark World..."},
                    {"type": "battle", "enemy": "Rudinn"},
                ],
                bosses=["King"],
                unlocked=True
            ),
            Chapter(
                number=2,
                title="A CYBER'S WORLD",
                subtitle="Welcome to the digital realm",
                maps=["cyber_city", "cyber_field", "queen_mansion"],
                story_beats=[
                    {"type": "dialogue", "content": "The Cyber World awaits..."},
                ],
                bosses=["Queen"],
                unlocked=False
            ),
            Chapter(
                number=3,
                title="THE SHADOW REALM",
                subtitle="Darkness within darkness",
                maps=["shadow_entrance", "shadow_castle"],
                story_beats=[],
                bosses=["Shadow King"],
                unlocked=False
            ),
            Chapter(
                number=4,
                title="WHISKERS OF FATE",
                subtitle="The cats rise up",
                maps=["cat_kingdom", "yarn_dungeon"],
                story_beats=[],
                bosses=["Lord Whiskerz"],
                unlocked=False
            ),
            Chapter(
                number=5,
                title="BEYOND THE VOID",
                subtitle="What lies in emptiness?",
                maps=["void_entrance", "void_depths"],
                story_beats=[],
                bosses=["The Void"],
                unlocked=False
            ),
            Chapter(
                number=6,
                title="FINAL FOUNTAIN",
                subtitle="The last light fades",
                maps=["fountain_approach", "fountain_core"],
                story_beats=[],
                bosses=["The Angel"],
                unlocked=False
            ),
            Chapter(
                number=7,
                title="YOUR CHOICE",
                subtitle="...",
                maps=["ending_a", "ending_b"],
                story_beats=[],
                bosses=["???"],
                unlocked=False
            ),
        ]
        
    def get_current_chapter(self) -> Chapter:
        return self.chapters[self.current_chapter]
    
    def unlock_next_chapter(self):
        """Unlock next chapter after completing current"""
        self.chapters[self.current_chapter].completed = True
        if self.current_chapter + 1 < len(self.chapters):
            self.chapters[self.current_chapter + 1].unlocked = True
            
    def set_chapter(self, chapter_num: int):
        """Set current chapter"""
        if 0 <= chapter_num < len(self.chapters) and self.chapters[chapter_num].unlocked:
            self.current_chapter = chapter_num

# ═══════════════════════════════════════════════════════════════════════════════
# SAVE SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

class SaveSystem:
    """Handles game saving and loading"""
    
    def __init__(self, save_dir: str = "saves"):
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)
        
    def save(self, slot: int, game_data: Dict) -> bool:
        """Save game to slot"""
        try:
            filepath = os.path.join(self.save_dir, f"save_{slot}.json")
            with open(filepath, 'w') as f:
                json.dump(game_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Save error: {e}")
            return False
            
    def load(self, slot: int) -> Optional[Dict]:
        """Load game from slot"""
        try:
            filepath = os.path.join(self.save_dir, f"save_{slot}.json")
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Load error: {e}")
        return None
    
    def get_save_info(self, slot: int) -> Optional[Dict]:
        """Get basic save info for display"""
        data = self.load(slot)
        if data:
            return {
                'chapter': data.get('chapter', 1),
                'playtime': data.get('playtime', 0),
                'location': data.get('location', 'Unknown'),
            }
        return None
    
    def slot_exists(self, slot: int) -> bool:
        """Check if save slot has data"""
        filepath = os.path.join(self.save_dir, f"save_{slot}.json")
        return os.path.exists(filepath)

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN GAME CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class CatsDeltarune:
    """Main game class"""
    
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(GAME_TITLE)
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.fullscreen = False
        
        # Font setup
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 64)
        self.small_font = pygame.font.Font(None, 18)
        
        # Systems
        self.sound = SoundSystem(True)
        self.dialogue = DialogueSystem(self.sound)
        self.dialogue.set_font(self.font)
        self.chapter_manager = ChapterManager()
        self.save_system = SaveSystem()
        
        # Game state
        self.state = GameState.TITLE
        self.title_selection = 0
        self.chapter_selection = 0
        
        # Party
        self.party: List[PartyMember] = []
        self._init_party()
        
        # Overworld
        self.current_map: Optional[TileMap] = None
        self.player: Optional[PlayerOverworld] = None
        self.camera_x = 0
        self.camera_y = 0
        
        # Battle
        self.battle: Optional[BattleSystem] = None
        
        # Input handling
        self.keys_pressed: Dict = {}
        self.keys_just_pressed: Dict = {}
        
        # Playtime tracking
        self.playtime = 0
        
    def _init_party(self):
        """Initialize the player's party"""
        # Main character - a cat!
        kris = PartyMember("Kris", "cat", [CAT_PURPLE, WHITE])
        kris.stats = Stats(hp=90, max_hp=90, attack=12, defense=8, magic=5)
        
        # Second party member
        susie = PartyMember("Susie", "monster", [PURPLE, MAGENTA])
        susie.stats = Stats(hp=120, max_hp=120, attack=18, defense=5, magic=3)
        susie.spells = [
            Spell("Rude Buster", "Heavy damage to one enemy", 50, damage=80),
            Spell("Red Buster", "Massive damage + team heal", 100, damage=150, heal_amount=40),
        ]
        susie.acts = [
            {"name": "Check", "description": "Check enemy stats", "tp_gain": 0},
            {"name": "Threaten", "description": "Scare the enemy", "tp_gain": 10},
            {"name": "Rally", "description": "Boost party morale", "tp_gain": 20},
        ]
        
        # Third party member
        ralsei = PartyMember("Ralsei", "cat", [GREEN, WHITE])
        ralsei.stats = Stats(hp=70, max_hp=70, attack=8, defense=6, magic=15)
        ralsei.spells = [
            Spell("Heal Prayer", "Restore HP to one ally", 32, heal_amount=50),
            Spell("Pacify", "End a tired enemy's fight", 16, effect="pacify"),
            Spell("Fluffy Guard", "Reduce damage to party", 40, effect="guard"),
        ]
        ralsei.acts = [
            {"name": "Check", "description": "Check enemy stats", "tp_gain": 0},
            {"name": "Compliment", "description": "Say something nice", "tp_gain": 15},
            {"name": "Encourage", "description": "Encourage an ally", "tp_gain": 10},
        ]
        
        self.party = [kris, susie, ralsei]
        
    def _create_test_map(self) -> TileMap:
        """Create a test map for demonstration"""
        tilemap = TileMap(30, 20)
        
        # Fill with floor
        for y in range(20):
            for x in range(30):
                tilemap.set_tile(x, y, 4)  # Dark floor
                
        # Add walls around edges
        for x in range(30):
            tilemap.set_tile(x, 0, 1, True)
            tilemap.set_tile(x, 19, 1, True)
        for y in range(20):
            tilemap.set_tile(0, y, 1, True)
            tilemap.set_tile(29, y, 1, True)
            
        # Add some interior walls
        for x in range(5, 10):
            tilemap.set_tile(x, 10, 1, True)
        for y in range(5, 10):
            tilemap.set_tile(15, y, 1, True)
            
        # Add save point
        tilemap.set_tile(5, 5, 3)
        tilemap.add_object(MapObject(
            x=5 * TILE_SIZE, y=5 * TILE_SIZE,
            width=TILE_SIZE, height=TILE_SIZE,
            obj_type="save",
            data={"save_name": "Castle Entry"}
        ))
        
        # Add door
        tilemap.set_tile(25, 10, 2)
        tilemap.add_object(MapObject(
            x=25 * TILE_SIZE, y=10 * TILE_SIZE,
            width=TILE_SIZE, height=TILE_SIZE,
            obj_type="door",
            data={"destination": "next_room"}
        ))
        
        # Add enemy encounter zone
        tilemap.add_object(MapObject(
            x=15 * TILE_SIZE, y=15 * TILE_SIZE,
            width=TILE_SIZE * 3, height=TILE_SIZE * 3,
            obj_type="encounter",
            data={"enemies": ["Rudinn", "Whiskerz"]}
        ))
        
        return tilemap
    
    def start_new_game(self):
        """Start a new game"""
        self._init_party()
        self.chapter_manager = ChapterManager()
        self.current_map = self._create_test_map()
        self.player = PlayerOverworld(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
            self.party[0]
        )
        self.state = GameState.OVERWORLD
        self.playtime = 0
        
    def start_battle(self, enemies: List[Enemy]):
        """Start a battle"""
        self.battle = BattleSystem(self.party, enemies, self.sound, self.dialogue)
        self.battle.set_font(self.font)
        self.state = GameState.BATTLE
        
    def end_battle(self, result: str):
        """End battle and return to overworld"""
        self.battle = None
        if result == "victory":
            self.state = GameState.OVERWORLD
        elif result == "defeat":
            self.state = GameState.GAME_OVER
            
    def run(self):
        """Main game loop"""
        while self.running:
            self._handle_events()
            self._update()
            self._draw()
            self.clock.tick(FPS)
            
        pygame.quit()
        
    def _handle_events(self):
        """Handle pygame events"""
        self.keys_just_pressed = {}
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self.keys_just_pressed[event.key] = True
                
                # Global keys
                if event.key == pygame.K_F4:
                    self._toggle_fullscreen()
                    
        self.keys_pressed = pygame.key.get_pressed()
        
    def _toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            
    def _update(self):
        """Update game state"""
        self.playtime += 1
        
        if self.state == GameState.TITLE:
            self._update_title()
        elif self.state == GameState.CHAPTER_SELECT:
            self._update_chapter_select()
        elif self.state == GameState.OVERWORLD:
            self._update_overworld()
        elif self.state == GameState.BATTLE:
            self._update_battle()
        elif self.state == GameState.DIALOGUE:
            self._update_dialogue()
        elif self.state == GameState.GAME_OVER:
            self._update_game_over()
            
    def _update_title(self):
        """Update title screen"""
        if self.keys_just_pressed.get(pygame.K_UP) or self.keys_just_pressed.get(pygame.K_w):
            self.title_selection = (self.title_selection - 1) % 4
            self.sound.play('select')
        elif self.keys_just_pressed.get(pygame.K_DOWN) or self.keys_just_pressed.get(pygame.K_s):
            self.title_selection = (self.title_selection + 1) % 4
            self.sound.play('select')
        elif self.keys_just_pressed.get(pygame.K_z) or self.keys_just_pressed.get(pygame.K_RETURN):
            self.sound.play('confirm')
            if self.title_selection == 0:  # New Game
                self.start_new_game()
            elif self.title_selection == 1:  # Continue
                if self.save_system.slot_exists(1):
                    self._load_game(1)
                else:
                    self.start_new_game()
            elif self.title_selection == 2:  # Chapter Select
                self.state = GameState.CHAPTER_SELECT
            elif self.title_selection == 3:  # Quit
                self.running = False
                
    def _update_chapter_select(self):
        """Update chapter selection screen"""
        if self.keys_just_pressed.get(pygame.K_UP) or self.keys_just_pressed.get(pygame.K_w):
            self.chapter_selection = (self.chapter_selection - 1) % len(self.chapter_manager.chapters)
            self.sound.play('select')
        elif self.keys_just_pressed.get(pygame.K_DOWN) or self.keys_just_pressed.get(pygame.K_s):
            self.chapter_selection = (self.chapter_selection + 1) % len(self.chapter_manager.chapters)
            self.sound.play('select')
        elif self.keys_just_pressed.get(pygame.K_z) or self.keys_just_pressed.get(pygame.K_RETURN):
            chapter = self.chapter_manager.chapters[self.chapter_selection]
            if chapter.unlocked:
                self.sound.play('confirm')
                self.chapter_manager.set_chapter(self.chapter_selection)
                self.start_new_game()
        elif self.keys_just_pressed.get(pygame.K_x) or self.keys_just_pressed.get(pygame.K_LSHIFT):
            self.sound.play('cancel')
            self.state = GameState.TITLE
            
    def _update_overworld(self):
        """Update overworld state"""
        if self.player and self.current_map:
            self.player.update(self.keys_pressed, self.current_map)
            
            # Update camera
            self.camera_x = max(0, min(
                self.current_map.width * TILE_SIZE - SCREEN_WIDTH,
                self.player.x - SCREEN_WIDTH // 2
            ))
            self.camera_y = max(0, min(
                self.current_map.height * TILE_SIZE - SCREEN_HEIGHT,
                self.player.y - SCREEN_HEIGHT // 2
            ))
            
            # Check interactions
            if self.keys_just_pressed.get(pygame.K_z) or self.keys_just_pressed.get(pygame.K_RETURN):
                objects = self.current_map.get_objects_at(self.player.x, self.player.y)
                for obj in objects:
                    self._handle_object_interaction(obj)
                    
            # Quick save
            if self.keys_just_pressed.get(pygame.K_c):
                self._save_game(1)
                
            # Random encounters (simplified)
            if random.random() < 0.001:  # Very low chance per frame
                self.start_battle([DarknerEnemy(), CatEnemy()])
                
    def _handle_object_interaction(self, obj: MapObject):
        """Handle interaction with map object"""
        if obj.obj_type == "save":
            self._save_game(1)
            self.dialogue.start([
                DialogueLine(
                    "* The power of Cat Friendship shines within you.",
                    "",
                    None,
                    []
                ),
                DialogueLine(
                    f"* (HP and TP fully restored)\n* Progress saved!",
                    "",
                    None,
                    []
                )
            ])
            # Restore HP
            for member in self.party:
                member.stats.hp = member.stats.max_hp
                member.stats.tp = member.stats.max_tp
            self.state = GameState.DIALOGUE
            
        elif obj.obj_type == "door":
            # Transition to next room (simplified)
            pass
            
        elif obj.obj_type == "encounter":
            enemies = []
            for enemy_name in obj.data.get("enemies", []):
                if enemy_name == "Rudinn":
                    enemies.append(DarknerEnemy())
                elif enemy_name == "Whiskerz":
                    enemies.append(CatEnemy())
            if enemies:
                self.start_battle(enemies)
                
    def _update_battle(self):
        """Update battle state"""
        if self.battle:
            result = self.battle.update(self.keys_pressed, self.keys_just_pressed)
            if result:
                self.end_battle(result)
                
    def _update_dialogue(self):
        """Update dialogue state"""
        if self.dialogue.update():
            if self.keys_just_pressed.get(pygame.K_z) or self.keys_just_pressed.get(pygame.K_RETURN):
                self.dialogue.advance()
            elif self.keys_just_pressed.get(pygame.K_LEFT) or self.keys_just_pressed.get(pygame.K_a):
                self.dialogue.move_choice(-1)
            elif self.keys_just_pressed.get(pygame.K_RIGHT) or self.keys_just_pressed.get(pygame.K_d):
                self.dialogue.move_choice(1)
        else:
            self.state = GameState.OVERWORLD
            
    def _update_game_over(self):
        """Update game over state"""
        if self.keys_just_pressed.get(pygame.K_z) or self.keys_just_pressed.get(pygame.K_RETURN):
            # Revive party and return to title
            for member in self.party:
                member.stats.hp = member.stats.max_hp
            self.state = GameState.TITLE
            
    def _save_game(self, slot: int):
        """Save game to slot"""
        data = {
            'chapter': self.chapter_manager.current_chapter,
            'playtime': self.playtime,
            'location': "Dark World",
            'party': [
                {
                    'name': m.name,
                    'level': m.level,
                    'hp': m.stats.hp,
                    'max_hp': m.stats.max_hp,
                    'exp': m.exp
                }
                for m in self.party
            ],
            'chapters_unlocked': [c.unlocked for c in self.chapter_manager.chapters],
            'player_pos': (self.player.x, self.player.y) if self.player else (0, 0)
        }
        self.save_system.save(slot, data)
        self.sound.play('confirm')
        
    def _load_game(self, slot: int):
        """Load game from slot"""
        data = self.save_system.load(slot)
        if data:
            self.chapter_manager.current_chapter = data.get('chapter', 0)
            self.playtime = data.get('playtime', 0)
            
            # Restore party stats
            for i, member_data in enumerate(data.get('party', [])):
                if i < len(self.party):
                    self.party[i].level = member_data.get('level', 1)
                    self.party[i].stats.hp = member_data.get('hp', 100)
                    self.party[i].stats.max_hp = member_data.get('max_hp', 100)
                    self.party[i].exp = member_data.get('exp', 0)
                    
            # Restore chapter unlocks
            for i, unlocked in enumerate(data.get('chapters_unlocked', [])):
                if i < len(self.chapter_manager.chapters):
                    self.chapter_manager.chapters[i].unlocked = unlocked
                    
            # Setup game
            self.current_map = self._create_test_map()
            pos = data.get('player_pos', (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.player = PlayerOverworld(pos[0], pos[1], self.party[0])
            self.state = GameState.OVERWORLD
            
    def _draw(self):
        """Draw current game state"""
        self.screen.fill(BLACK)
        
        if self.state == GameState.TITLE:
            self._draw_title()
        elif self.state == GameState.CHAPTER_SELECT:
            self._draw_chapter_select()
        elif self.state == GameState.OVERWORLD:
            self._draw_overworld()
        elif self.state == GameState.BATTLE:
            self._draw_battle()
        elif self.state == GameState.DIALOGUE:
            self._draw_overworld()
            self.dialogue.draw(self.screen)
        elif self.state == GameState.GAME_OVER:
            self._draw_game_over()
            
        pygame.display.flip()
        
    def _draw_title(self):
        """Draw title screen"""
        # Title
        title_surf = self.title_font.render(GAME_TITLE, True, CAT_PURPLE)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 120))
        self.screen.blit(title_surf, title_rect)
        
        # Subtitle
        subtitle = self.font.render("A Deltarune-Style RPG by Team Flames", True, WHITE)
        sub_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 170))
        self.screen.blit(subtitle, sub_rect)
        
        # Menu options
        options = ["New Game", "Continue", "Chapter Select", "Quit"]
        for i, option in enumerate(options):
            color = YELLOW if i == self.title_selection else WHITE
            prefix = "❤ " if i == self.title_selection else "  "
            text = self.font.render(prefix + option, True, color)
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, 280 + i * 40))
            self.screen.blit(text, rect)
            
        # Controls hint
        hint = self.small_font.render("Arrow Keys: Navigate | Z/Enter: Select | X/Shift: Cancel", True, (150, 150, 150))
        hint_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, 450))
        self.screen.blit(hint, hint_rect)
        
        # Cat decoration
        cat_sprite = SpriteGenerator.create_character(48, 64, [CAT_PURPLE, CAT_PINK], "cat")
        self.screen.blit(cat_sprite, (80, 280))
        self.screen.blit(pygame.transform.flip(cat_sprite, True, False), (SCREEN_WIDTH - 128, 280))
        
    def _draw_chapter_select(self):
        """Draw chapter selection screen"""
        # Title
        title = self.title_font.render("Select Chapter", True, CAT_PURPLE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)
        
        # Chapters
        visible_start = max(0, self.chapter_selection - 2)
        visible_end = min(len(self.chapter_manager.chapters), visible_start + 5)
        
        for i, chapter in enumerate(self.chapter_manager.chapters[visible_start:visible_end]):
            actual_index = visible_start + i
            y = 120 + i * 70
            
            # Selection indicator
            if actual_index == self.chapter_selection:
                pygame.draw.rect(self.screen, (40, 40, 80), (50, y - 5, SCREEN_WIDTH - 100, 60))
                
            # Chapter info
            if chapter.unlocked:
                color = YELLOW if actual_index == self.chapter_selection else WHITE
                status = "✓" if chapter.completed else ""
            else:
                color = (80, 80, 80)
                status = "🔒"
                
            chapter_text = self.font.render(f"Chapter {chapter.number}: {chapter.title} {status}", True, color)
            self.screen.blit(chapter_text, (70, y))
            
            subtitle = self.small_font.render(chapter.subtitle if chapter.unlocked else "???", True, color)
            self.screen.blit(subtitle, (90, y + 25))
            
        # Instructions
        hint = self.small_font.render("Press Z to play | X to go back", True, (150, 150, 150))
        self.screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, 440))
        
    def _draw_overworld(self):
        """Draw overworld"""
        if self.current_map:
            self.current_map.draw(self.screen, self.camera_x, self.camera_y)
        if self.player:
            self.player.draw(self.screen, self.camera_x, self.camera_y)
            
        # HUD
        self._draw_hud()
        
    def _draw_hud(self):
        """Draw overworld HUD"""
        # Chapter info
        chapter = self.chapter_manager.get_current_chapter()
        chapter_text = self.small_font.render(f"Chapter {chapter.number}: {chapter.title}", True, WHITE)
        self.screen.blit(chapter_text, (10, 10))
        
        # Lead character HP
        if self.party:
            hp = self.party[0].stats.hp
            max_hp = self.party[0].stats.max_hp
            hp_text = self.small_font.render(f"HP: {hp}/{max_hp}", True, HP_GREEN)
            self.screen.blit(hp_text, (10, 30))
            
    def _draw_battle(self):
        """Draw battle screen"""
        if self.battle:
            self.battle.draw(self.screen)
            
    def _draw_game_over(self):
        """Draw game over screen"""
        # Dark overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(200)
        self.screen.blit(overlay, (0, 0))
        
        # Game over text
        go_text = self.title_font.render("GAME OVER", True, RED)
        go_rect = go_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(go_text, go_rect)
        
        # Continue prompt
        cont_text = self.font.render("Press Z to continue", True, WHITE)
        cont_rect = cont_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(cont_text, cont_rect)
        
        # Quote
        quote = self.small_font.render('"You cannot give up just yet..."', True, (150, 150, 150))
        quote_rect = quote.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        self.screen.blit(quote, quote_rect)

# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Main entry point"""
    print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           CAT'S DELTARUNE                                    ║
║                    A Deltarune-Inspired RPG Engine                           ║
║                         By Team Flames / Samsoft                             ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Controls:                                                                   ║
║  Arrow Keys / WASD - Move / Navigate menus                                   ║
║  Z / Enter - Confirm / Interact                                              ║
║  X / Shift - Cancel / Open menu                                              ║
║  C - Quick Save (overworld)                                                  ║
║  F4 - Toggle Fullscreen                                                      ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    game = CatsDeltarune()
    game.run()

if __name__ == "__main__":
    main()
