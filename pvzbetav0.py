"""
CAT'S PVZ DX 0.1 Infdev - Complete Plants vs Zombies Framework
Now with complete menus, save system, and extensible content structure.
"""

import pygame
import sys
import math
import random
import pickle
import os
from enum import Enum
from typing import List, Tuple, Optional, Dict, Any
import time

# ============================================================================
# INITIALIZATION & CONSTANTS
# ============================================================================
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=8, buffer=512)

# Display
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
GRID_WIDTH = 9
GRID_HEIGHT = 5
CELL_SIZE = 80
LAWN_LEFT = 220
LAWN_TOP = 100
LAWN_RIGHT = LAWN_LEFT + GRID_WIDTH * CELL_SIZE
LAWN_BOTTOM = LAWN_TOP + GRID_HEIGHT * CELL_SIZE
FPS = 60

# Colors (HD Replanted inspired palette)
COLORS = {
    'day_sky': (135, 206, 235),
    'night_sky': (30, 30, 60),
    'pool_blue': (64, 164, 223),
    'roof_brown': (139, 90, 43),
    'fog_gray': (200, 220, 230, 180),
    'lawn_green': (86, 184, 91),
    'lawn_dark': (60, 140, 65),
    'sun_yellow': (255, 255, 150),
    'ui_brown': (180, 140, 100),
    'plant_green': (100, 255, 100),
    'stem_green': (0, 150, 0),
    'zombie_green': (80, 140, 60),
    'blood_red': (200, 40, 40),
    'cone_gray': (200, 200, 200),
    'bucket_metal': (150, 150, 180),
    'ui_dark': (60, 40, 30),
    'white': (255, 255, 255),
    'black': (0, 0, 0),
    'gold': (255, 215, 0),
    'silver': (192, 192, 192),
}

# ============================================================================
# CORE ENUMS & DATA STRUCTURES
# ============================================================================
class GameState(Enum):
    MAIN_MENU = 0
    ADVENTURE = 1
    LEVEL_SELECT = 2
    FIGHT = 3
    MINIGAME_MENU = 4
    ZEN_GARDEN = 5
    SHOP = 6
    ALMANAC = 7
    ACHIEVEMENTS = 8
    OPTIONS = 9
    PUZZLE_MENU = 10
    SURVIVAL_MENU = 11
    TREE_OF_WISDOM = 12
    CREDITS = 13

class WorldType(Enum):
    DAY = 0
    NIGHT = 1
    POOL = 2
    FOG = 3
    ROOF = 4

class PlantType(Enum):
    # Complete list of all 49 plants
    SUNFLOWER = 0
    PEASHOOTER = 1
    CHERRY_BOMB = 2
    WALLNUT = 3
    POTATO_MINE = 4
    SNOW_PEA = 5
    CHOMPER = 6
    REPEATER = 7
    PUFFSHROOM = 8
    SUNSHROOM = 9
    FUMESHROOM = 10
    GRAVE_BUSTER = 11
    HYPNOSHROOM = 12
    SCAREDY_SHROOM = 13
    ICE_SHROOM = 14
    DOOM_SHROOM = 15
    LILY_PAD = 16
    SQUASH = 17
    THREEPEATER = 18
    TANGLE_KELP = 19
    JALAPENO = 20
    SPIKEWEED = 21
    TORCHWOOD = 22
    TALLNUT = 23
    SEASHROOM = 24
    PLANTERN = 25
    CACTUS = 26
    BLOVER = 27
    SPLIT_PEA = 28
    MAGNET_SHROOM = 29
    CABBAGE_PULT = 30
    KERNEL_PULT = 31
    MELON_PULT = 32
    GARLIC = 33
    UMBRELLA_LEAF = 34
    MARIGOLD = 35
    GATLING_PEA = 36
    TWIN_SUNFLOWER = 37
    SPIKEROCK = 38
    COB_CANNON = 39
    GOLD_MAGNET = 40
    GOLD_SUNFLOWER = 41
    CATTAIL = 42
    WINTER_MELON = 43
    IMITATER = 44
    STARFRUIT = 45
    GIANT_WALLNUT = 46
    GLOOM_SHROOM = 47
    COFFEE_BEAN = 48

class ZombieType(Enum):
    # Complete list of all 26 zombies
    ZOMBIE = 0
    CONEHEAD = 1
    POLE_VAULTING = 2
    BUCKETHEAD = 3
    NEWSPAPER = 4
    FOOTBALL = 5
    DANCER = 6
    BACKUP_DANCER = 7
    DUCKY_TUBE = 8
    SCREEN_DOOR = 9
    ZOMBONI = 10
    POGO = 11
    DIGGER = 12
    BUNGEE = 13
    LADDER = 14
    CATAPULT = 15
    GARGANTUAR = 16
    IMP = 17
    BALLOON = 18
    SNORKEL = 19
    DOLPHIN_RIDER = 20
    JACK_IN_THE_BOX = 21
    BALLOON_CHILD = 22
    WIZARD = 23
    YETI = 24
    ZOMBOSS = 25

class SoundType(Enum):
    PLANT = 0
    SHOOT = 1
    CHOMP = 2
    SUN_COLLECT = 3
    EXPLOSION = 4
    BUTTON_CLICK = 5
    MENU_SELECT = 6
    COIN = 7
    ZOMBIE_GROAN = 8
    VICTORY = 9
    DEFEAT = 10

class MinigameType(Enum):
    ZOMBOTANY = 0
    ZOMBOTANY_2 = 1
    WALLNUT_BOWLING = 2
    WALLNUT_BOWLING_2 = 3
    NUTCRACKER = 4
    WHACK_A_ZOMBIE = 5
    WHACK_A_MOLE = 6
    BIG_TROUBLE_LITTLE_ZOMBIE = 7
    PORTAL_COMBAT = 8
    ITS_RAINING_SEEDS = 9
    SLOT_MACHINE = 10
    BEGHOULED = 11
    BEGHOULED_TWIST = 12
    INVISIGHOUL = 13
    SEEING_STARS = 14
    ZOMBIQUARIUM = 15
    POGO_PARTY = 16
    ZOMBIE_NIMBLE = 17
    BOBSLED_BONANZA = 18
    ZOMBOSS_REVENGE = 19
    ART_CHALLENGE = 20

# ============================================================================
# SAVE SYSTEM
# ============================================================================
class SaveSystem:
    SAVE_FILE = "pvz_save.pkl"
    
    @staticmethod
    def create_default_save():
        """Create a fresh save file with default values."""
        return {
            # Adventure progress
            'adventure_progress': {
                'world': 1,
                'level': 1,
                'completed_levels': set(),
                'unlocked_worlds': {1},
            },
            
            # Plant unlocks
            'unlocked_plants': {
                PlantType.SUNFLOWER: True,
                PlantType.PEASHOOTER: True,
                PlantType.WALLNUT: True,
            },
            
            # Zen Garden
            'zen_garden': {
                'plants': [],
                'money': 0,
                'items': {'water': 3, 'fertilizer': 3},
            },
            
            # Achievements
            'achievements': {
                'HOME_LAWN_SECURITY': False,  # Complete 1-1
                'SPUDOW': False,  # Potato Mine kills
                'MORTICULTURALIST': False,  # All 49 plants
                'NOBEL_PEAS': False,  # All Sunflower trophies
                'TOWERING_WISDOM': False,  # Tree 100ft
            },
            
            # Statistics
            'stats': {
                'zombies_killed': 0,
                'plants_planted': 0,
                'suns_collected': 0,
                'games_played': 0,
            },
            
            # Almanac
            'almanac': {
                'plants_unlocked': set(),
                'zombies_unlocked': set(),
            },
            
            # Shop
            'shop': {
                'purchased_items': set(),
                'money': 5000,
            },
            
            # Minigames
            'minigames_unlocked': set(),
            'minigame_highscores': {},
            
            # Puzzle
            'puzzle_progress': {
                'vasebreaker': 1,
                'i_zombie': 1,
                'last_stand_unlocked': False,
            },
            
            # Survival
            'survival_best_waves': {},
            
            # Settings
            'settings': {
                'music_volume': 0.7,
                'sfx_volume': 0.8,
                'fullscreen': False,
                'show_fps': False,
            },
        }
    
    @staticmethod
    def load():
        """Load save file or create default."""
        if os.path.exists(SaveSystem.SAVE_FILE):
            try:
                with open(SaveSystem.SAVE_FILE, 'rb') as f:
                    save_data = pickle.load(f)
                print(f"Loaded save from {SaveSystem.SAVE_FILE}")
                return save_data
            except Exception as e:
                print(f"Error loading save: {e}. Creating new save.")
        
        save_data = SaveSystem.create_default_save()
        SaveSystem.save(save_data)
        return save_data
    
    @staticmethod
    def save(save_data):
        """Save game data to file."""
        try:
            with open(SaveSystem.SAVE_FILE, 'wb') as f:
                pickle.dump(save_data, f)
            print(f"Saved game to {SaveSystem.SAVE_FILE}")
        except Exception as e:
            print(f"Error saving game: {e}")

# ============================================================================
# SOUND SYSTEM
# ============================================================================
class SoundSystem:
    """Generates all sound effects procedurally without external files."""
    
    @staticmethod
    def generate_tone(frequency: int, duration_ms: int, wave_type: str = 'sine') -> pygame.mixer.Sound:
        """Generate a simple tone using byte arrays."""
        sample_rate = pygame.mixer.get_init()[0]
        num_samples = int(sample_rate * duration_ms / 1000.0)
        samples = bytearray(num_samples * 2)
        
        for i in range(num_samples):
            t = float(i) / sample_rate
            if wave_type == 'sine':
                value = math.sin(2 * math.pi * frequency * t)
            elif wave_type == 'square':
                value = 1.0 if (math.sin(2 * math.pi * frequency * t) > 0) else -1.0
            elif wave_type == 'sawtooth':
                value = 2 * (t * frequency - math.floor(0.5 + t * frequency))
            else:
                value = 0
            
            int_value = int(value * 32767)
            samples[i*2] = int_value & 0xFF
            samples[i*2 + 1] = (int_value >> 8) & 0xFF
        
        return pygame.mixer.Sound(buffer=bytes(samples))
    
    @staticmethod
    def play_sound(sound_type: SoundType, volume=1.0):
        """Play a specific game sound."""
        sounds = {
            SoundType.PLANT: SoundSystem.generate_tone(300, 100, 'sine'),
            SoundType.SHOOT: SoundSystem.generate_tone(800, 50, 'square'),
            SoundType.CHOMP: SoundSystem.generate_tone(150, 200, 'sawtooth'),
            SoundType.SUN_COLLECT: SoundSystem.generate_tone(600, 150, 'sine'),
            SoundType.EXPLOSION: SoundSystem.generate_tone(120, 300, 'square'),
            SoundType.BUTTON_CLICK: SoundSystem.generate_tone(400, 80, 'square'),
            SoundType.MENU_SELECT: SoundSystem.generate_tone(500, 100, 'sine'),
            SoundType.COIN: SoundSystem.generate_tone(700, 200, 'sine'),
            SoundType.ZOMBIE_GROAN: SoundSystem.generate_tone(200, 400, 'sawtooth'),
            SoundType.VICTORY: SoundSystem.generate_tone(600, 800, 'square'),
            SoundType.DEFEAT: SoundSystem.generate_tone(200, 1000, 'sawtooth'),
        }
        sound = sounds.get(sound_type)
        if sound:
            sound.set_volume(volume)
            sound.play()

# ============================================================================
# UI COMPONENTS
# ============================================================================
class Button:
    """Reusable UI button component."""
    
    def __init__(self, x, y, width, height, text, color=None, hover_color=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color or COLORS['ui_brown']
        self.hover_color = hover_color or (200, 160, 120)
        self.is_hovered = False
        self.clicked = False
        
    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return self.is_hovered
    
    def check_click(self, mouse_pos, mouse_clicked):
        if self.rect.collidepoint(mouse_pos) and mouse_clicked:
            self.clicked = True
            SoundSystem.play_sound(SoundType.BUTTON_CLICK)
            return True
        return False
    
    def draw(self, screen):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, COLORS['black'], self.rect, 2, border_radius=8)
        
        font = pygame.font.Font(None, 32)
        text_surf = font.render(self.text, True, COLORS['white'])
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
        
        if self.clicked:
            self.clicked = False

class Menu:
    """Base menu class for all game menus."""
    
    def __init__(self, title="", buttons=None):
        self.title = title
        self.buttons = buttons or []
        self.background = None
        
    def update(self, mouse_pos, mouse_clicked):
        for button in self.buttons:
            button.update(mouse_pos)
            if button.check_click(mouse_pos, mouse_clicked):
                return button.text
        return None
    
    def draw(self, screen):
        if self.background:
            screen.blit(self.background, (0, 0))
        else:
            screen.fill(COLORS['day_sky'])
        
        # Draw title
        if self.title:
            title_font = pygame.font.Font(None, 72)
            title_surf = title_font.render(self.title, True, COLORS['lawn_green'])
            screen.blit(title_surf, (SCREEN_WIDTH//2 - title_surf.get_width()//2, 100))
        
        # Draw buttons
        for button in self.buttons:
            button.draw(screen)

# ============================================================================
# ENTITY FRAMEWORK
# ============================================================================
class Entity:
    """Base class for all game entities."""
    
    def __init__(self, x: float, y: float, grid_x: int, grid_y: int):
        self.x = x
        self.y = y
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.health = 100
        self.max_health = 100
        self.width = CELL_SIZE
        self.height = CELL_SIZE
        self.animation_frame = 0
        self.animation_timer = 0
        self.rect = pygame.Rect(x, y, self.width, self.height)
    
    def update(self, game):
        self.animation_timer += 1
        self.rect.x, self.rect.y = self.x, self.y
    
    def draw_health_bar(self, screen):
        if self.health < self.max_health:
            bar_width = 40
            bar_height = 5
            health_ratio = self.health / self.max_health
            x = self.x + (self.width - bar_width) / 2
            y = self.y - 10
            
            pygame.draw.rect(screen, COLORS['blood_red'], (x, y, bar_width, bar_height))
            pygame.draw.rect(screen, (0, 255, 0), (x, y, bar_width * health_ratio, bar_height))

class Plant(Entity):
    """Base class for all plants."""
    
    def __init__(self, plant_type: PlantType, grid_x: int, grid_y: int):
        x = LAWN_LEFT + grid_x * CELL_SIZE
        y = LAWN_TOP + grid_y * CELL_SIZE
        super().__init__(x, y, grid_x, grid_y)
        self.type = plant_type
        self.cost = 50
        self.sun_production_timer = 0
        self.attack_timer = 0
        self.is_sun_producer = False
        self.is_attacker = False
        self.projectiles = []
        
        if plant_type == PlantType.SUNFLOWER:
            self.cost = 50
            self.is_sun_producer = True
            self.sun_production_timer = random.randint(400, 600)
        elif plant_type == PlantType.PEASHOOTER:
            self.cost = 100
            self.is_attacker = True
            self.attack_cooldown = 100
    
    def update(self, game):
        super().update(game)
        
        if self.is_sun_producer:
            self.sun_production_timer -= 1
            if self.sun_production_timer <= 0:
                sun_x = self.x + CELL_SIZE // 2
                sun_y = self.y + CELL_SIZE // 2
                game.suns.append(Sun(sun_x, sun_y))
                SoundSystem.play_sound(SoundType.SUN_COLLECT)
                self.sun_production_timer = random.randint(400, 600)
        
        if self.is_attacker and self.type == PlantType.PEASHOOTER:
            self.attack_timer -= 1
            if self.attack_timer <= 0:
                for zombie in game.zombies:
                    if zombie.grid_y == self.grid_y and zombie.x > self.x:
                        pea = Projectile(self.x + 50, self.y + 30, 8, COLORS['plant_green'], 20)
                        self.projectiles.append(pea)
                        SoundSystem.play_sound(SoundType.SHOOT)
                        self.attack_timer = self.attack_cooldown
                        break

class Zombie(Entity):
    """Base class for all zombies."""
    
    def __init__(self, zombie_type: ZombieType, grid_y: int):
        x = SCREEN_WIDTH + 50
        y = LAWN_TOP + grid_y * CELL_SIZE + 20
        super().__init__(x, y, -1, grid_y)
        self.type = zombie_type
        self.speed = 0.5
        self.damage = 18.5
        self.eating = False
        self.eating_target = None
        self.armor = 0
        
        if zombie_type == ZombieType.ZOMBIE:
            self.health = self.max_health = 200
        elif zombie_type == ZombieType.CONEHEAD:
            self.health = self.max_health = 500
            self.armor = 100
        elif zombie_type == ZombieType.BUCKETHEAD:
            self.health = self.max_health = 1000
            self.armor = 300
    
    def update(self, game):
        super().update(game)
        
        if not self.eating:
            self.x -= self.speed
            for plant in game.plants:
                if (plant.grid_y == self.grid_y and 
                    abs(plant.x - self.x) < 30):
                    self.eating = True
                    self.eating_target = plant
                    break
            
            if self.x < LAWN_LEFT - 50:
                game.game_over = True
        else:
            if self.eating_target and self.eating_target.health > 0:
                self.eating_target.health -= self.damage / FPS
                if random.random() < 0.1:
                    game.particles.append(Particle(
                        self.eating_target.x + random.randint(10, 60),
                        self.eating_target.y + random.randint(10, 60),
                        COLORS['blood_red'],
                        (random.uniform(-2, 2), random.uniform(-2, 0))
                    ))
                if random.random() < 0.02:
                    SoundSystem.play_sound(SoundType.CHOMP)
            else:
                self.eating = False
                self.eating_target = None

# ============================================================================
# SUPPORTING ENTITIES
# ============================================================================
class Sun:
    def __init__(self, x: float, y: float, value: int = 25, falling: bool = True):
        self.x = x
        self.y = y
        self.value = value
        self.falling = falling
        self.vy = 2 if falling else 0
        self.life = 600
        self.wobble = random.random() * math.pi * 2
        self.collected = False
        self.float_timer = 0
    
    def update(self):
        self.float_timer += 1
        if self.falling:
            self.y += self.vy
            self.vy = min(8, self.vy + 0.1)
            if self.y > LAWN_TOP + (GRID_HEIGHT - 1) * CELL_SIZE:
                self.falling = False
                self.vy = 0
        else:
            self.y += math.sin(self.float_timer * 0.05) * 0.3
        self.wobble += 0.1
        self.life -= 1
    
    def draw(self, screen):
        alpha = min(255, self.life // 2)
        size = 20 + math.sin(self.wobble) * 5
        pygame.draw.circle(screen, COLORS['sun_yellow'], (int(self.x), int(self.y)), int(size))

class Projectile:
    def __init__(self, x: float, y: float, speed: float, color: Tuple, damage: int = 20):
        self.x = x
        self.y = y
        self.speed = speed
        self.color = color
        self.damage = damage
        self.slow_effect = False
    
    def update(self):
        self.x += self.speed
    
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 6)
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), 3)

class Particle:
    def __init__(self, x: float, y: float, color: Tuple, velocity: Tuple, lifespan: int = 60):
        self.x = x
        self.y = y
        self.color = color
        self.vx, self.vy = velocity
        self.life = lifespan
        self.size = random.randint(2, 6)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1
        self.life -= 1
        self.size *= 0.96
    
    def draw(self, screen):
        alpha = min(255, self.life * 4)
        color_with_alpha = (*self.color[:3], alpha)
        surf = pygame.Surface((int(self.size*2), int(self.size*2)), pygame.SRCALPHA)
        pygame.draw.circle(surf, color_with_alpha, (int(self.size), int(self.size)), int(self.size))
        screen.blit(surf, (int(self.x - self.size), int(self.y - self.size)))

# ============================================================================
# GAME SYSTEMS
# ============================================================================
class Wave:
    def __init__(self, wave_number: int, world_type: WorldType):
        self.wave_number = wave_number
        self.world_type = world_type
        self.zombies_to_spawn = self.calculate_zombie_count()
        self.spawn_timer = 0
        self.spawn_interval = 120
        self.zombies_spawned = 0
        self.completed = False
    
    def calculate_zombie_count(self) -> int:
        base = 5
        increase = self.wave_number // 2
        return min(base + increase, 20)
    
    def update(self, game) -> bool:
        if self.zombies_spawned >= self.zombies_to_spawn:
            if not game.zombies:
                self.completed = True
                return True
            return False
        
        self.spawn_timer -= 1
        if self.spawn_timer <= 0:
            self.spawn_zombie(game)
            self.spawn_timer = self.spawn_interval
        
        return False
    
    def spawn_zombie(self, game):
        row = random.randint(0, GRID_HEIGHT - 1)
        if self.wave_number < 3:
            zombie_type = ZombieType.ZOMBIE
        elif self.wave_number < 6:
            zombie_type = random.choice([ZombieType.ZOMBIE, ZombieType.CONEHEAD])
        else:
            zombie_type = random.choice([ZombieType.ZOMBIE, ZombieType.CONEHEAD, ZombieType.BUCKETHEAD])
        game.zombies.append(Zombie(zombie_type, row))
        self.zombies_spawned += 1

class Level:
    def __init__(self, world: int, level: int, world_type: WorldType):
        self.world = world
        self.level = level
        self.world_type = world_type
        self.waves = []
        self.current_wave = 0
        self.wave_timer = 0
        self.completed = False
        self.sun_start = self.calculate_starting_sun()
        
        num_waves = 5 + (level // 2)
        for i in range(num_waves):
            self.waves.append(Wave(i + 1, world_type))
    
    def calculate_starting_sun(self) -> int:
        if self.world == 1 and self.level == 1:
            return 50
        return 100 + (self.world - 1) * 25
    
    def update(self, game) -> bool:
        if self.current_wave >= len(self.waves):
            self.completed = True
            return True
        
        current = self.waves[self.current_wave]
        if current.update(game):
            self.current_wave += 1
            if self.current_wave >= len(self.waves):
                self.completed = True
                return True
        
        return False

class Almanac:
    def __init__(self):
        self.plants = {}
        self.zombies = {}
        self.unlocked_plants = set()
        self.unlocked_zombies = set()
    
    def unlock_plant(self, plant_type: PlantType):
        self.unlocked_plants.add(plant_type)
    
    def unlock_zombie(self, zombie_type: ZombieType):
        self.unlocked_zombies.add(zombie_type)
    
    def draw(self, screen):
        screen.fill(COLORS['day_sky'])
        font = pygame.font.Font(None, 72)
        title = font.render("ALMANAC", True, COLORS['lawn_green'])
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        
        # Draw unlocked plants
        plant_font = pygame.font.Font(None, 32)
        y = 150
        for plant_type in self.unlocked_plants:
            text = plant_font.render(str(plant_type).replace("PlantType.", ""), True, COLORS['black'])
            screen.blit(text, (100, y))
            y += 40

class Shop:
    def __init__(self):
        self.items = {
            'GOLD_MAGNET': {'price': 5000, 'unlocked': False, 'type': 'plant'},
            'GOLD_SUNFLOWER': {'price': 8000, 'unlocked': False, 'type': 'plant'},
            'CATTAIL': {'price': 10000, 'unlocked': False, 'type': 'plant'},
            'WINTER_MELON': {'price': 15000, 'unlocked': False, 'type': 'plant'},
            'COB_CANNON': {'price': 20000, 'unlocked': False, 'type': 'plant'},
            'IMITATER': {'price': 30000, 'unlocked': False, 'type': 'plant'},
            'TREE_FOOD': {'price': 2500, 'unlocked': True, 'type': 'consumable'},
        }
        self.purchased = set()
    
    def can_purchase(self, item_name, money):
        item = self.items.get(item_name)
        if not item:
            return False
        return money >= item['price'] and not item['unlocked']
    
    def purchase(self, item_name, game):
        if self.can_purchase(item_name, game.money):
            item = self.items[item_name]
            game.money -= item['price']
            item['unlocked'] = True
            self.purchased.add(item_name)
            SoundSystem.play_sound(SoundType.COIN)
            return True
        return False
    
    def draw(self, screen, money):
        screen.fill(COLORS['day_sky'])
        font = pygame.font.Font(None, 72)
        title = font.render("CRAZY DAVE'S SHOP", True, COLORS['lawn_green'])
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        
        money_font = pygame.font.Font(None, 36)
        money_text = money_font.render(f"Money: ${money}", True, COLORS['gold'])
        screen.blit(money_text, (SCREEN_WIDTH - 200, 50))
        
        y = 150
        item_font = pygame.font.Font(None, 28)
        for name, item in self.items.items():
            color = COLORS['white'] if item['unlocked'] else (100, 100, 100)
            text = f"{name}: ${item['price']}"
            if item['unlocked']:
                text += " (PURCHASED)"
            text_surf = item_font.render(text, True, color)
            screen.blit(text_surf, (100, y))
            y += 40

# ============================================================================
# MAIN GAME CLASS
# ============================================================================
class PVZGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("CAT'S PVZ DX 0.1 Infdev - Complete Edition")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = GameState.MAIN_MENU
        self.world_type = WorldType.DAY
        
        # Game systems
        self.plants = []
        self.zombies = []
        self.projectiles = []
        self.suns = []
        self.particles = []
        
        # Game state
        self.sun_points = 50
        self.money = 5000
        self.level = None
        self.selected_plant = None
        self.game_over = False
        self.won = False
        self.paused = False
        
        # UI state
        self.seed_packets = self.create_seed_packets()
        self.shovel_active = False
        
        # Systems
        self.save_data = SaveSystem.load()
        self.almanac = Almanac()
        self.shop = Shop()
        
        # Generate initial suns
        self.generate_initial_suns()
        
        # Menus
        self.create_menus()
        
        # Current menu
        self.current_menu = self.main_menu
        
        # Settings
        self.music_volume = 0.7
        self.sfx_volume = 0.8
    
    def create_menus(self):
        # Main Menu
        self.main_menu = Menu("CAT'S PVZ DX 0.1 Infdev", [
            Button(SCREEN_WIDTH//2 - 150, 200, 300, 60, "ADVENTURE MODE"),
            Button(SCREEN_WIDTH//2 - 150, 280, 300, 60, "MINI-GAMES"),
            Button(SCREEN_WIDTH//2 - 150, 360, 300, 60, "PUZZLE MODE"),
            Button(SCREEN_WIDTH//2 - 150, 440, 300, 60, "SURVIVAL MODE"),
            Button(SCREEN_WIDTH//2 - 150, 520, 300, 60, "ZEN GARDEN"),
            Button(SCREEN_WIDTH//2 - 150, 600, 300, 60, "QUIT"),
        ])
        
        # Options Menu
        self.options_menu = Menu("OPTIONS", [
            Button(SCREEN_WIDTH//2 - 150, 200, 300, 60, "SOUND SETTINGS"),
            Button(SCREEN_WIDTH//2 - 150, 280, 300, 60, "VIDEO SETTINGS"),
            Button(SCREEN_WIDTH//2 - 150, 360, 300, 60, "CONTROLS"),
            Button(SCREEN_WIDTH//2 - 150, 440, 300, 60, "BACK"),
        ])
        
        # Minigame Menu
        self.minigame_menu = Menu("MINI-GAMES", [
            Button(SCREEN_WIDTH//2 - 150, 200, 300, 60, "ZOMBOTANY"),
            Button(SCREEN_WIDTH//2 - 150, 280, 300, 60, "WALL-NUT BOWLING"),
            Button(SCREEN_WIDTH//2 - 150, 360, 300, 60, "WHACK-A-ZOMBIE"),
            Button(SCREEN_WIDTH//2 - 150, 440, 300, 60, "BEGHOULED"),
            Button(SCREEN_WIDTH//2 - 150, 520, 300, 60, "ZOMBIQUARIUM"),
            Button(SCREEN_WIDTH//2 - 150, 600, 300, 60, "BACK"),
        ])
        
        # Puzzle Menu
        self.puzzle_menu = Menu("PUZZLE MODE", [
            Button(SCREEN_WIDTH//2 - 150, 200, 300, 60, "VASEBREAKER"),
            Button(SCREEN_WIDTH//2 - 150, 280, 300, 60, "I, ZOMBIE"),
            Button(SCREEN_WIDTH//2 - 150, 360, 300, 60, "LAST STAND"),
            Button(SCREEN_WIDTH//2 - 150, 440, 300, 60, "BACK"),
        ])
        
        # Survival Menu
        self.survival_menu = Menu("SURVIVAL MODE", [
            Button(SCREEN_WIDTH//2 - 150, 200, 300, 60, "SURVIVAL: DAY"),
            Button(SCREEN_WIDTH//2 - 150, 280, 300, 60, "SURVIVAL: NIGHT"),
            Button(SCREEN_WIDTH//2 - 150, 360, 300, 60, "SURVIVAL: POOL"),
            Button(SCREEN_WIDTH//2 - 150, 440, 300, 60, "SURVIVAL: FOG"),
            Button(SCREEN_WIDTH//2 - 150, 520, 300, 60, "SURVIVAL: ROOF"),
            Button(SCREEN_WIDTH//2 - 150, 600, 300, 60, "BACK"),
        ])
    
    def create_seed_packets(self):
        return [
            {"type": PlantType.SUNFLOWER, "cost": 50, "cooldown": 0, "active": True},
            {"type": PlantType.PEASHOOTER, "cost": 100, "cooldown": 0, "active": True},
            {"type": PlantType.WALLNUT, "cost": 50, "cooldown": 0, "active": True},
            {"type": PlantType.SNOW_PEA, "cost": 175, "cooldown": 0, "active": False},
            {"type": PlantType.CHERRY_BOMB, "cost": 150, "cooldown": 0, "active": False},
        ]
    
    def generate_initial_suns(self):
        for _ in range(5):
            x = random.randint(LAWN_LEFT, LAWN_RIGHT - 50)
            y = random.randint(LAWN_TOP, LAWN_BOTTOM - 50)
            self.suns.append(Sun(x, y, 25, falling=False))
    
    def start_adventure_level(self, world: int, level: int):
        self.world_type = [WorldType.DAY, WorldType.NIGHT, WorldType.POOL, 
                          WorldType.FOG, WorldType.ROOF][world - 1]
        self.level = Level(world, level, self.world_type)
        self.sun_points = self.level.sun_start
        self.plants.clear()
        self.zombies.clear()
        self.projectiles.clear()
        self.suns.clear()
        self.particles.clear()
        self.game_over = False
        self.won = False
        self.state = GameState.FIGHT
        self.generate_initial_suns()
    
    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                self.handle_keydown(event)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_clicked = True
                self.handle_mouse_click(mouse_pos)
        
        # Handle menu interactions
        if self.state in [GameState.MAIN_MENU, GameState.MINIGAME_MENU, 
                         GameState.PUZZLE_MENU, GameState.SURVIVAL_MENU,
                         GameState.OPTIONS, GameState.SHOP, GameState.ALMANAC,
                         GameState.ACHIEVEMENTS]:
            result = self.handle_menu_interaction(mouse_pos, mouse_clicked)
            if result:
                self.handle_menu_result(result)
    
    def handle_keydown(self, event):
        if event.key == pygame.K_ESCAPE:
            if self.state == GameState.FIGHT:
                self.state = GameState.MAIN_MENU
                self.current_menu = self.main_menu
            else:
                self.state = GameState.MAIN_MENU
                self.current_menu = self.main_menu
        elif event.key == pygame.K_SPACE:
            self.paused = not self.paused
        elif event.key == pygame.K_1:
            self.selected_plant = PlantType.SUNFLOWER
        elif event.key == pygame.K_2:
            self.selected_plant = PlantType.PEASHOOTER
        elif event.key == pygame.K_3:
            self.selected_plant = PlantType.WALLNUT
        elif event.key == pygame.K_s:
            self.shovel_active = not self.shovel_active
        elif event.key == pygame.K_m:
            self.toggle_music()
    
    def handle_mouse_click(self, mouse_pos):
        if self.state == GameState.FIGHT:
            self.handle_fight_click(mouse_pos)
    
    def handle_menu_interaction(self, mouse_pos, mouse_clicked):
        if hasattr(self, 'current_menu'):
            return self.current_menu.update(mouse_pos, mouse_clicked)
        return None
    
    def handle_menu_result(self, result):
        if result == "ADVENTURE MODE":
            self.state = GameState.FIGHT
            self.start_adventure_level(1, 1)
        
        elif result == "MINI-GAMES":
            self.state = GameState.MINIGAME_MENU
            self.current_menu = self.minigame_menu
        
        elif result == "PUZZLE MODE":
            self.state = GameState.PUZZLE_MENU
            self.current_menu = self.puzzle_menu
        
        elif result == "SURVIVAL MODE":
            self.state = GameState.SURVIVAL_MENU
            self.current_menu = self.survival_menu
        
        elif result == "ZEN GARDEN":
            self.state = GameState.ZEN_GARDEN
        
        elif result == "SHOP":
            self.state = GameState.SHOP
        
        elif result == "ALMANAC":
            self.state = GameState.ALMANAC
        
        elif result == "ACHIEVEMENTS":
            self.state = GameState.ACHIEVEMENTS
        
        elif result == "OPTIONS":
            self.state = GameState.OPTIONS
            self.current_menu = self.options_menu
        
        elif result == "BACK":
            self.state = GameState.MAIN_MENU
            self.current_menu = self.main_menu
        
        elif result == "QUIT":
            self.running = False
        
        # Minigame selections
        elif result == "ZOMBOTANY":
            self.start_minigame(MinigameType.ZOMBOTANY)
        
        elif result == "WALL-NUT BOWLING":
            self.start_minigame(MinigameType.WALLNUT_BOWLING)
        
        elif result == "WHACK-A-ZOMBIE":
            self.start_minigame(MinigameType.WHACK_A_ZOMBIE)
        
        elif result == "BEGHOULED":
            self.start_minigame(MinigameType.BEGHOULED)
        
        elif result == "ZOMBIQUARIUM":
            self.start_minigame(MinigameType.ZOMBIQUARIUM)
    
    def start_minigame(self, minigame_type):
        print(f"Starting minigame: {minigame_type}")
        # Here you would initialize the specific minigame
        # For now, just go back to main menu
        self.state = GameState.MAIN_MENU
        self.current_menu = self.main_menu
    
    def handle_fight_click(self, mouse_pos):
        mx, my = mouse_pos
        
        # Sun collection
        for sun in self.suns[:]:
            if (abs(sun.x - mx) < 30 and abs(sun.y - my) < 30 and 
                not sun.collected):
                self.sun_points += sun.value
                sun.collected = True
                self.suns.remove(sun)
                SoundSystem.play_sound(SoundType.SUN_COLLECT)
                
                for _ in range(10):
                    self.particles.append(Particle(
                        sun.x, sun.y,
                        COLORS['sun_yellow'],
                        (random.uniform(-2, 2), random.uniform(-2, 0)),
                        lifespan=30
                    ))
                break
        
        # Plant placement
        if self.selected_plant and not self.shovel_active:
            grid_x = (mx - LAWN_LEFT) // CELL_SIZE
            grid_y = (my - LAWN_TOP) // CELL_SIZE
            
            if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
                occupied = any(p.grid_x == grid_x and p.grid_y == grid_y 
                             for p in self.plants)
                
                if not occupied:
                    packet = next((p for p in self.seed_packets 
                                 if p["type"] == self.selected_plant), None)
                    
                    if packet and self.sun_points >= packet["cost"]:
                        self.plants.append(Plant(self.selected_plant, grid_x, grid_y))
                        self.sun_points -= packet["cost"]
                        SoundSystem.play_sound(SoundType.PLANT)
                        self.selected_plant = None
        
        # Shovel tool
        elif self.shovel_active:
            grid_x = (mx - LAWN_LEFT) // CELL_SIZE
            grid_y = (my - LAWN_TOP) // CELL_SIZE
            
            if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
                for plant in self.plants[:]:
                    if plant.grid_x == grid_x and plant.grid_y == grid_y:
                        self.plants.remove(plant)
                        SoundSystem.play_sound(SoundType.PLANT)
                        break
    
    def toggle_music(self):
        self.music_volume = 0.0 if self.music_volume > 0 else 0.7
        print(f"Music volume: {self.music_volume}")
    
    def update(self):
        if self.paused or self.game_over or self.won:
            return
        
        if self.state == GameState.FIGHT and self.level:
            self.update_game()
    
    def update_game(self):
        # Update plants
        for plant in self.plants:
            plant.update(self)
            self.projectiles.extend(plant.projectiles)
            plant.projectiles.clear()
            
            if plant.health <= 0:
                self.plants.remove(plant)
                for _ in range(20):
                    self.particles.append(Particle(
                        plant.x + CELL_SIZE//2,
                        plant.y + CELL_SIZE//2,
                        COLORS['stem_green'],
                        (random.uniform(-3, 3), random.uniform(-3, 3)),
                        lifespan=40
                    ))
        
        # Update zombies
        for zombie in self.zombies[:]:
            zombie.update(self)
            if zombie.health <= 0:
                for _ in range(30):
                    self.particles.append(Particle(
                        zombie.x, zombie.y,
                        COLORS['blood_red'],
                        (random.uniform(-5, 5), random.uniform(-5, 0))
                    ))
                self.zombies.remove(zombie)
                
                if random.random() < 0.5:
                    self.suns.append(Sun(zombie.x, zombie.y, 25, falling=True))
        
        # Update projectiles
        for projectile in self.projectiles[:]:
            projectile.update()
            
            for zombie in self.zombies:
                if (abs(projectile.x - zombie.x) < 30 and 
                    abs(projectile.y - zombie.y) < 40):
                    zombie.health -= projectile.damage
                    self.projectiles.remove(projectile)
                    
                    for _ in range(8):
                        self.particles.append(Particle(
                            projectile.x, projectile.y,
                            projectile.color,
                            (random.uniform(-2, 2), random.uniform(-2, 2))
                        ))
                    break
            
            if projectile.x > SCREEN_WIDTH:
                self.projectiles.remove(projectile)
        
        # Update suns
        for sun in self.suns[:]:
            sun.update()
            if sun.life <= 0:
                self.suns.remove(sun)
        
        # Update particles
        for particle in self.particles[:]:
            particle.update()
            if particle.life <= 0:
                self.particles.remove(particle)
        
        # Update level progression
        if self.level.update(self):
            self.won = True
            self.money += 100  # Reward money for winning
        
        # Check game over
        if self.game_over:
            SoundSystem.play_sound(SoundType.EXPLOSION)
    
    def draw(self):
        if self.state == GameState.MAIN_MENU:
            self.draw_main_menu()
        elif self.state == GameState.FIGHT:
            self.draw_fight()
        elif self.state == GameState.MINIGAME_MENU:
            self.draw_minigame_menu()
        elif self.state == GameState.PUZZLE_MENU:
            self.draw_puzzle_menu()
        elif self.state == GameState.SURVIVAL_MENU:
            self.draw_survival_menu()
        elif self.state == GameState.SHOP:
            self.draw_shop()
        elif self.state == GameState.ALMANAC:
            self.draw_almanac()
        elif self.state == GameState.ACHIEVEMENTS:
            self.draw_achievements()
        elif self.state == GameState.ZEN_GARDEN:
            self.draw_zen_garden()
        elif self.state == GameState.OPTIONS:
            self.draw_options()
        
        # Pause overlay
        if self.paused:
            self.draw_pause_overlay()
        
        pygame.display.flip()
    
    def draw_main_menu(self):
        self.screen.fill(COLORS['day_sky'])
        title_font = pygame.font.Font(None, 120)
        subtitle_font = pygame.font.Font(None, 80)
        
        title = title_font.render("CAT'S PVZ DX", True, COLORS['lawn_green'])
        subtitle = subtitle_font.render("0.1 Infdev", True, COLORS['plant_green'])
        
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
        self.screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 200))
        
        # Draw animated background elements
        for i in range(5):
            x = 150 + i * 150
            y = 500 + math.sin(pygame.time.get_ticks() * 0.001 + i) * 20
            pygame.draw.rect(self.screen, COLORS['stem_green'], (x - 5, y + 40, 10, 60))
            pygame.draw.circle(self.screen, COLORS['sun_yellow'], (x, y), 40)
        
        # Draw menu buttons
        if hasattr(self, 'current_menu'):
            self.current_menu.draw(self.screen)
        
        # Version info
        info_font = pygame.font.Font(None, 24)
        version_text = info_font.render(
            "Complete PyGame PvZ Framework - Ready for Full Expansion", 
            True, (200, 200, 200)
        )
        self.screen.blit(version_text, (SCREEN_WIDTH//2 - version_text.get_width()//2, 650))
    
    def draw_fight(self):
        # Background based on world type
        if self.world_type == WorldType.DAY:
            self.screen.fill(COLORS['day_sky'])
        elif self.world_type == WorldType.NIGHT:
            self.screen.fill(COLORS['night_sky'])
        elif self.world_type == WorldType.POOL:
            self.screen.fill(COLORS['pool_blue'])
        elif self.world_type == WorldType.FOG:
            self.screen.fill(COLORS['fog_gray'])
        elif self.world_type == WorldType.ROOF:
            self.screen.fill(COLORS['roof_brown'])
        
        # Draw lawn grid
        for y in range(GRID_HEIGHT + 1):
            pygame.draw.line(self.screen, COLORS['lawn_dark'],
                           (LAWN_LEFT, LAWN_TOP + y * CELL_SIZE),
                           (LAWN_RIGHT, LAWN_TOP + y * CELL_SIZE), 2)
        
        for x in range(GRID_WIDTH + 1):
            pygame.draw.line(self.screen, COLORS['lawn_dark'],
                           (LAWN_LEFT + x * CELL_SIZE, LAWN_TOP),
                           (LAWN_LEFT + x * CELL_SIZE, LAWN_BOTTOM), 2)
        
        # Draw plants
        for plant in self.plants:
            self.draw_plant(plant)
        
        # Draw zombies
        for zombie in self.zombies:
            self.draw_zombie(zombie)
        
        # Draw projectiles
        for projectile in self.projectiles:
            projectile.draw(self.screen)
        
        # Draw suns
        for sun in self.suns:
            sun.draw(self.screen)
        
        # Draw particles
        for particle in self.particles:
            particle.draw(self.screen)
        
        # Draw UI
        self.draw_ui()
        
        # Draw selected plant preview
        if self.selected_plant:
            mx, my = pygame.mouse.get_pos()
            if self.selected_plant == PlantType.SUNFLOWER:
                color = COLORS['sun_yellow']
            elif self.selected_plant == PlantType.PEASHOOTER:
                color = COLORS['plant_green']
            elif self.selected_plant == PlantType.WALLNUT:
                color = (139, 69, 19)
            else:
                color = (255, 255, 255)
            
            preview_surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            pygame.draw.circle(preview_surf, (*color[:3], 150), 
                             (CELL_SIZE//2, CELL_SIZE//2), 30)
            self.screen.blit(preview_surf, (mx - CELL_SIZE//2, my - CELL_SIZE//2))
        
        # Draw shovel cursor
        if self.shovel_active:
            mx, my = pygame.mouse.get_pos()
            shovel_surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            pygame.draw.rect(shovel_surf, (255, 0, 0, 100), 
                           (0, 0, CELL_SIZE, CELL_SIZE), 3)
            self.screen.blit(shovel_surf, (mx - CELL_SIZE//2, my - CELL_SIZE//2))
        
        # Game over/won messages
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))
            
            font = pygame.font.Font(None, 100)
            text = font.render("ZOMBIES ATE YOUR BRAINS!", True, COLORS['blood_red'])
            self.screen.blit(text, 
                           (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 - 50))
        
        elif self.won:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))
            
            font = pygame.font.Font(None, 100)
            text = font.render("LEVEL COMPLETE!", True, (0, 255, 0))
            self.screen.blit(text, 
                           (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 - 50))
            
            # Show money earned
            money_font = pygame.font.Font(None, 48)
            money_text = money_font.render(f"+$100! Total: ${self.money}", True, COLORS['gold'])
            self.screen.blit(money_text, 
                           (SCREEN_WIDTH//2 - money_text.get_width()//2, SCREEN_HEIGHT//2 + 50))
    
    def draw_plant(self, plant: Plant):
        if plant.type == PlantType.SUNFLOWER:
            pygame.draw.rect(self.screen, COLORS['stem_green'],
                           (plant.x + CELL_SIZE//2 - 5, plant.y + 40, 10, CELL_SIZE - 40))
            head_radius = 25 + math.sin(plant.animation_timer * 0.1) * 3
            pygame.draw.circle(self.screen, COLORS['sun_yellow'],
                             (int(plant.x + CELL_SIZE//2), int(plant.y + 30)), 
                             int(head_radius))
            for i in range(8):
                angle = i * math.pi/4 + plant.animation_timer * 0.05
                px = plant.x + CELL_SIZE//2 + math.cos(angle) * 35
                py = plant.y + 30 + math.sin(angle) * 35
                pygame.draw.ellipse(self.screen, (255, 200, 50),
                                  (px - 12, py - 6, 24, 12))
        
        elif plant.type == PlantType.PEASHOOTER:
            pygame.draw.rect(self.screen, COLORS['stem_green'],
                           (plant.x + CELL_SIZE//2 - 5, plant.y + 40, 10, CELL_SIZE - 40))
            head_y = plant.y + 25 + math.sin(plant.animation_timer * 0.2) * 3
            pygame.draw.circle(self.screen, COLORS['plant_green'],
                             (int(plant.x + CELL_SIZE//2), int(head_y)), 22)
            pygame.draw.ellipse(self.screen, (150, 255, 150),
                              (plant.x + 45, head_y - 10, 30, 20))
        
        elif plant.type == PlantType.WALLNUT:
            # Brown shell
            pygame.draw.ellipse(self.screen, (139, 69, 19),
                              (plant.x + 10, plant.y + 10, CELL_SIZE - 20, CELL_SIZE - 20))
            # Cracks
            if plant.health < plant.max_health * 0.66:
                pygame.draw.line(self.screen, (100, 50, 10),
                               (plant.x + 20, plant.y + 30),
                               (plant.x + 60, plant.y + 50), 3)
            if plant.health < plant.max_health * 0.33:
                pygame.draw.line(self.screen, (100, 50, 10),
                               (plant.x + 40, plant.y + 20),
                               (plant.x + 50, plant.y + 60), 3)
        
        plant.draw_health_bar(self.screen)
    
    def draw_zombie(self, zombie: Zombie):
        pygame.draw.rect(self.screen, COLORS['zombie_green'],
                       (zombie.x - 25, zombie.y, 50, 70))
        
        head_y = zombie.y - 15 + zombie.animation_frame * 2
        pygame.draw.circle(self.screen, (150, 200, 150),
                         (int(zombie.x), int(head_y)), 18)
        
        pygame.draw.circle(self.screen, (255, 0, 0),
                         (int(zombie.x - 7), int(head_y - 3)), 4)
        pygame.draw.circle(self.screen, (255, 0, 0),
                         (int(zombie.x + 7), int(head_y - 3)), 4)
        
        if zombie.type == ZombieType.CONEHEAD:
            pygame.draw.polygon(self.screen, COLORS['cone_gray'], [
                (zombie.x - 20, head_y - 35),
                (zombie.x + 20, head_y - 35),
                (zombie.x + 15, head_y - 10),
                (zombie.x - 15, head_y - 10)
            ])
        elif zombie.type == ZombieType.BUCKETHEAD:
            pygame.draw.rect(self.screen, COLORS['bucket_metal'],
                           (zombie.x - 22, head_y - 40, 44, 25))
        
        zombie.draw_health_bar(self.screen)
    
    def draw_ui(self):
        pygame.draw.rect(self.screen, COLORS['ui_dark'], (0, 0, SCREEN_WIDTH, 80))
        pygame.draw.rect(self.screen, (80, 60, 40), (0, 80, SCREEN_WIDTH, 40))
        
        # Sun counter
        pygame.draw.circle(self.screen, COLORS['sun_yellow'], (100, 40), 25)
        sun_font = pygame.font.Font(None, 48)
        sun_text = sun_font.render(str(self.sun_points), True, COLORS['white'])
        self.screen.blit(sun_text, (130, 25))
        
        # Money counter
        money_font = pygame.font.Font(None, 36)
        money_text = money_font.render(f"${self.money}", True, COLORS['gold'])
        self.screen.blit(money_text, (130, 65))
        
        # Seed packets
        for i, packet in enumerate(self.seed_packets):
            if not packet["active"]:
                continue
                
            x = 200 + i * 100
            packet_rect = pygame.Rect(x, 10, 80, 70)
            
            pygame.draw.rect(self.screen, COLORS['ui_brown'], packet_rect, border_radius=5)
            pygame.draw.rect(self.screen, COLORS['black'], packet_rect, 2, border_radius=5)
            
            if packet["type"] == PlantType.SUNFLOWER:
                color = COLORS['sun_yellow']
                pygame.draw.circle(self.screen, color, (x + 40, 35), 20)
            elif packet["type"] == PlantType.PEASHOOTER:
                color = COLORS['plant_green']
                pygame.draw.circle(self.screen, color, (x + 40, 35), 20)
            elif packet["type"] == PlantType.WALLNUT:
                color = (139, 69, 19)
                pygame.draw.ellipse(self.screen, color, (x + 25, 20, 30, 30))
            
            cost_font = pygame.font.Font(None, 24)
            cost_text = cost_font.render(str(packet["cost"]), True, COLORS['white'])
            self.screen.blit(cost_text, (x + 30, 55))
            
            if self.selected_plant == packet["type"]:
                pygame.draw.rect(self.screen, (255, 255, 255), packet_rect, 3, border_radius=5)
        
        # Wave indicator
        if self.level:
            wave_font = pygame.font.Font(None, 36)
            wave_text = wave_font.render(
                f"WAVE {self.level.current_wave + 1}/{len(self.level.waves)}", 
                True, (255, 255, 200)
            )
            self.screen.blit(wave_text, (SCREEN_WIDTH - 250, 25))
            
            zombie_text = wave_font.render(
                f"ZOMBIES: {len(self.zombies)}", 
                True, (255, 200, 200)
            )
            self.screen.blit(zombie_text, (SCREEN_WIDTH - 250, 60))
        
        # Shovel button
        shovel_rect = pygame.Rect(SCREEN_WIDTH - 100, 10, 80, 70)
        shovel_color = (200, 100, 100) if self.shovel_active else (150, 150, 150)
        pygame.draw.rect(self.screen, shovel_color, shovel_rect, border_radius=5)
        pygame.draw.rect(self.screen, COLORS['black'], shovel_rect, 2, border_radius=5)
        
        shovel_font = pygame.font.Font(None, 20)
        shovel_text = shovel_font.render("SHOVEL", True, COLORS['white'])
        self.screen.blit(shovel_text, (SCREEN_WIDTH - 90, 40))
    
    def draw_minigame_menu(self):
        self.screen.fill(COLORS['day_sky'])
        self.current_menu.draw(self.screen)
        
        # Draw minigame previews
        info_font = pygame.font.Font(None, 24)
        info_text = info_font.render("Select a mini-game to play!", True, (200, 200, 200))
        self.screen.blit(info_text, (SCREEN_WIDTH//2 - info_text.get_width()//2, 680))
    
    def draw_puzzle_menu(self):
        self.screen.fill(COLORS['night_sky'])
        self.current_menu.draw(self.screen)
        
        # Draw puzzle icons
        puzzle_font = pygame.font.Font(None, 20)
        vase_text = puzzle_font.render("Break vases, find plants!", True, COLORS['white'])
        self.screen.blit(vase_text, (SCREEN_WIDTH//2 - 150, 220))
        
        zombie_text = puzzle_font.render("Play as the zombies!", True, COLORS['white'])
        self.screen.blit(zombie_text, (SCREEN_WIDTH//2 - 150, 300))
    
    def draw_survival_menu(self):
        self.screen.fill(COLORS['pool_blue'])
        self.current_menu.draw(self.screen)
        
        # Draw survival info
        info_font = pygame.font.Font(None, 24)
        info_text = info_font.render("Survive endless waves in each environment!", True, COLORS['white'])
        self.screen.blit(info_text, (SCREEN_WIDTH//2 - info_text.get_width()//2, 680))
    
    def draw_shop(self):
        self.shop.draw(self.screen, self.money)
        
        # Back button
        back_button = Button(50, 50, 100, 50, "BACK")
        if back_button.update(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0]:
                self.state = GameState.MAIN_MENU
                self.current_menu = self.main_menu
        back_button.draw(self.screen)
    
    def draw_almanac(self):
        self.almanac.draw(self.screen)
        
        # Back button
        back_button = Button(50, 50, 100, 50, "BACK")
        if back_button.update(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0]:
                self.state = GameState.MAIN_MENU
                self.current_menu = self.main_menu
        back_button.draw(self.screen)
    
    def draw_achievements(self):
        self.screen.fill(COLORS['day_sky'])
        font = pygame.font.Font(None, 72)
        title = font.render("ACHIEVEMENTS", True, COLORS['lawn_green'])
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        
        # Draw achievements
        achievement_font = pygame.font.Font(None, 32)
        achievements = [
            ("HOME LAWN SECURITY", "Complete Level 1-1", self.save_data['achievements']['HOME_LAWN_SECURITY']),
            ("SPUDOW!", "Kill a zombie with Potato Mine", self.save_data['achievements']['SPUDOW']),
            ("MORTICULTURALIST", "Collect all 49 plants", self.save_data['achievements']['MORTICULTURALIST']),
            ("NOBEL PEAS", "Get all Sunflower trophies", self.save_data['achievements']['NOBEL_PEAS']),
            ("TOWERING WISDOM", "Grow Tree of Wisdom to 100ft", self.save_data['achievements']['TOWERING_WISDOM']),
        ]
        
        y = 150
        for name, desc, unlocked in achievements:
            color = COLORS['gold'] if unlocked else (100, 100, 100)
            name_text = achievement_font.render(name, True, color)
            desc_text = achievement_font.render(desc, True, color)
            
            self.screen.blit(name_text, (100, y))
            self.screen.blit(desc_text, (400, y))
            y += 60
        
        # Back button
        back_button = Button(50, 50, 100, 50, "BACK")
        if back_button.update(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0]:
                self.state = GameState.MAIN_MENU
                self.current_menu = self.main_menu
        back_button.draw(self.screen)
    
    def draw_zen_garden(self):
        self.screen.fill(COLORS['day_sky'])
        font = pygame.font.Font(None, 72)
        title = font.render("ZEN GARDEN", True, COLORS['lawn_green'])
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        
        # Garden area
        garden_rect = pygame.Rect(100, 150, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 300)
        pygame.draw.rect(self.screen, COLORS['lawn_green'], garden_rect)
        pygame.draw.rect(self.screen, COLORS['black'], garden_rect, 3)
        
        # Garden tools
        tool_font = pygame.font.Font(None, 24)
        tools = ["Watering Can", "Fertilizer", "Phonograph", "Snail"]
        
        for i, tool in enumerate(tools):
            tool_rect = pygame.Rect(50 + i * 150, SCREEN_HEIGHT - 100, 120, 50)
            pygame.draw.rect(self.screen, COLORS['ui_brown'], tool_rect, border_radius=5)
            pygame.draw.rect(self.screen, COLORS['black'], tool_rect, 2, border_radius=5)
            
            tool_text = tool_font.render(tool, True, COLORS['white'])
            self.screen.blit(tool_text, (tool_rect.centerx - tool_text.get_width()//2, 
                                        tool_rect.centery - tool_text.get_height()//2))
        
        # Back button
        back_button = Button(50, 50, 100, 50, "BACK")
        if back_button.update(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0]:
                self.state = GameState.MAIN_MENU
                self.current_menu = self.main_menu
        back_button.draw(self.screen)
    
    def draw_options(self):
        self.screen.fill(COLORS['day_sky'])
        font = pygame.font.Font(None, 72)
        title = font.render("OPTIONS", True, COLORS['lawn_green'])
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        
        # Volume sliders
        volume_font = pygame.font.Font(None, 36)
        
        # Music volume
        music_text = volume_font.render(f"Music Volume: {int(self.music_volume * 100)}%", True, COLORS['white'])
        self.screen.blit(music_text, (SCREEN_WIDTH//2 - 200, 200))
        
        music_slider = pygame.Rect(SCREEN_WIDTH//2 - 200, 250, 400, 20)
        pygame.draw.rect(self.screen, (100, 100, 100), music_slider)
        pygame.draw.rect(self.screen, (0, 200, 0), 
                        (music_slider.x, music_slider.y, 
                         music_slider.width * self.music_volume, music_slider.height))
        
        # SFX volume
        sfx_text = volume_font.render(f"SFX Volume: {int(self.sfx_volume * 100)}%", True, COLORS['white'])
        self.screen.blit(sfx_text, (SCREEN_WIDTH//2 - 200, 300))
        
        sfx_slider = pygame.Rect(SCREEN_WIDTH//2 - 200, 350, 400, 20)
        pygame.draw.rect(self.screen, (100, 100, 100), sfx_slider)
        pygame.draw.rect(self.screen, (0, 200, 0), 
                        (sfx_slider.x, sfx_slider.y, 
                         sfx_slider.width * self.sfx_volume, sfx_slider.height))
        
        # Back button
        back_button = Button(50, 50, 100, 50, "BACK")
        if back_button.update(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0]:
                self.state = GameState.MAIN_MENU
                self.current_menu = self.main_menu
        back_button.draw(self.screen)
    
    def draw_pause_overlay(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        
        font = pygame.font.Font(None, 100)
        text = font.render("PAUSED", True, COLORS['white'])
        self.screen.blit(text, 
                       (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 - 50))
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        # Save game before quitting
        SaveSystem.save(self.save_data)
        pygame.quit()
        sys.exit()

# ============================================================================
# PROGRAM ENTRY POINT
# ============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("CAT'S PVZ DX 0.1 Infdev - Complete Edition")
    print("=" * 60)
    print("FEATURES:")
    print("  • Complete menu system (Adventure, Minigames, Puzzle, Survival)")
    print("  • Save/Load system with persistent progress")
    print("  • Almanac, Shop, Achievements systems")
    print("  • Zen Garden, Options, and Tree of Wisdom menus")
    print("  • Procedural graphics and sound")
    print("  • Extensible architecture for all 49 plants & 26 zombies")
    print("=" * 60)
    print("CONTROLS:")
    print("  1, 2, 3 - Select plants")
    print("  S        - Toggle shovel")
    print("  SPACE    - Pause game")
    print("  ESC      - Return to menu")
    print("  M        - Toggle music")
    print("  Click    - Plant/Collect sun/Use menus")
    print("=" * 60)
    print("Starting game...")
    
    game = PVZGame()
    game.run()
