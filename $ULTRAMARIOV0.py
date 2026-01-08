#!/usr/bin/env python3
"""
Super Mario Bros 1-1 Recreation
Complete single-file implementation with synthesized OST
"""

import pygame
import math
import array
import random
from enum import Enum, auto

# Initialize Pygame
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480
TILE_SIZE = 32
FPS = 60
GRAVITY = 0.5
MAX_FALL_SPEED = 12

# Colors
SKY_BLUE = (92, 148, 252)
GROUND_BROWN = (200, 76, 12)
BRICK_RED = (200, 76, 12)
BLOCK_YELLOW = (252, 152, 56)
PIPE_GREEN = (0, 168, 0)
PIPE_DARK = (0, 128, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
MARIO_RED = (228, 0, 0)
MARIO_SKIN = (252, 152, 56)
GOOMBA_BROWN = (172, 80, 36)
KOOPA_GREEN = (0, 168, 0)
COIN_GOLD = (252, 188, 60)
CLOUD_WHITE = (252, 252, 252)
BUSH_GREEN = (0, 200, 0)

# Game States
class GameState(Enum):
    TITLE = auto()
    PLAYING = auto()
    DEAD = auto()
    WIN = auto()
    GAMEOVER = auto()

# Sound Generation
class SoundGenerator:
    def __init__(self):
        self.sample_rate = 44100
        
    def generate_tone(self, frequency, duration, volume=0.3, wave_type='square'):
        num_samples = int(self.sample_rate * duration)
        buf = array.array('h')
        max_amplitude = int(32767 * volume)
        
        for i in range(num_samples):
            t = i / self.sample_rate
            if wave_type == 'square':
                value = max_amplitude if math.sin(2 * math.pi * frequency * t) > 0 else -max_amplitude
            elif wave_type == 'triangle':
                period = 1 / frequency
                value = int(max_amplitude * (2 * abs(2 * ((t / period) % 1) - 1) - 1))
            elif wave_type == 'sine':
                value = int(max_amplitude * math.sin(2 * math.pi * frequency * t))
            else:  # noise
                value = int(random.randint(-max_amplitude, max_amplitude) * 0.5)
            
            # Apply envelope
            attack = 0.01
            release = 0.05
            if t < attack:
                value = int(value * (t / attack))
            elif t > duration - release:
                value = int(value * ((duration - t) / release))
            
            buf.append(value)
            buf.append(value)  # Stereo
        
        return pygame.mixer.Sound(buffer=buf)
    
    def generate_jump_sound(self):
        num_samples = int(self.sample_rate * 0.15)
        buf = array.array('h')
        for i in range(num_samples):
            t = i / self.sample_rate
            freq = 300 + (700 * t / 0.15)
            value = int(8000 * math.sin(2 * math.pi * freq * t) * (1 - t / 0.15))
            buf.append(value)
            buf.append(value)
        return pygame.mixer.Sound(buffer=buf)
    
    def generate_coin_sound(self):
        num_samples = int(self.sample_rate * 0.2)
        buf = array.array('h')
        for i in range(num_samples):
            t = i / self.sample_rate
            freq = 988 if t < 0.1 else 1319
            value = int(10000 * math.sin(2 * math.pi * freq * t) * (1 - t / 0.2))
            buf.append(value)
            buf.append(value)
        return pygame.mixer.Sound(buffer=buf)
    
    def generate_stomp_sound(self):
        num_samples = int(self.sample_rate * 0.1)
        buf = array.array('h')
        for i in range(num_samples):
            t = i / self.sample_rate
            freq = 400 - (300 * t / 0.1)
            value = int(12000 * math.sin(2 * math.pi * freq * t) * (1 - t / 0.1))
            buf.append(value)
            buf.append(value)
        return pygame.mixer.Sound(buffer=buf)
    
    def generate_powerup_sound(self):
        num_samples = int(self.sample_rate * 0.5)
        buf = array.array('h')
        notes = [523, 659, 784, 1047]
        note_duration = 0.125
        for i in range(num_samples):
            t = i / self.sample_rate
            note_idx = min(int(t / note_duration), len(notes) - 1)
            freq = notes[note_idx]
            value = int(8000 * math.sin(2 * math.pi * freq * t) * 0.7)
            buf.append(value)
            buf.append(value)
        return pygame.mixer.Sound(buffer=buf)
    
    def generate_death_sound(self):
        num_samples = int(self.sample_rate * 0.8)
        buf = array.array('h')
        for i in range(num_samples):
            t = i / self.sample_rate
            freq = 600 - (400 * t / 0.8)
            value = int(10000 * math.sin(2 * math.pi * freq * t) * (1 - t / 0.8))
            buf.append(value)
            buf.append(value)
        return pygame.mixer.Sound(buffer=buf)
    
    def generate_brick_break_sound(self):
        num_samples = int(self.sample_rate * 0.15)
        buf = array.array('h')
        for i in range(num_samples):
            t = i / self.sample_rate
            value = int(random.randint(-15000, 15000) * (1 - t / 0.15))
            buf.append(value)
            buf.append(value)
        return pygame.mixer.Sound(buffer=buf)
    
    def generate_bump_sound(self):
        num_samples = int(self.sample_rate * 0.08)
        buf = array.array('h')
        for i in range(num_samples):
            t = i / self.sample_rate
            freq = 200
            value = int(8000 * math.sin(2 * math.pi * freq * t) * (1 - t / 0.08))
            buf.append(value)
            buf.append(value)
        return pygame.mixer.Sound(buffer=buf)
    
    def generate_flagpole_sound(self):
        num_samples = int(self.sample_rate * 1.5)
        buf = array.array('h')
        notes = [392, 392, 392, 392, 349, 392, 440, 392]
        note_len = 0.15
        for i in range(num_samples):
            t = i / self.sample_rate
            note_idx = min(int(t / note_len), len(notes) - 1)
            freq = notes[note_idx]
            env = 0.8 if (t % note_len) < note_len * 0.8 else 0.3
            value = int(8000 * math.sin(2 * math.pi * freq * t) * env)
            buf.append(value)
            buf.append(value)
        return pygame.mixer.Sound(buffer=buf)

# Music Generator - SMB1 Overworld Theme
class MusicGenerator:
    def __init__(self):
        self.sample_rate = 44100
        self.is_playing = False
        
    def generate_overworld_theme(self):
        """Generate the iconic SMB1 overworld theme"""
        # Melody notes (frequency, duration in beats)
        tempo = 200  # BPM
        beat = 60 / tempo
        
        # Simplified overworld melody
        melody = [
            (659, 0.5), (659, 0.5), (0, 0.5), (659, 0.5),
            (0, 0.5), (523, 0.5), (659, 0.5), (0, 0.5),
            (784, 0.5), (0, 1.5), (392, 0.5), (0, 1.5),
            
            (523, 0.75), (0, 0.5), (392, 0.75), (0, 0.5),
            (330, 0.75), (0, 0.5), (440, 0.5), (0, 0.25),
            (494, 0.5), (0, 0.25), (466, 0.5), (440, 0.5),
            
            (392, 0.33), (659, 0.33), (784, 0.33), (880, 0.5),
            (0, 0.25), (698, 0.5), (784, 0.5), (0, 0.25),
            (659, 0.5), (0, 0.25), (523, 0.5), (587, 0.5), (494, 0.5),
            (0, 0.5),
            
            (523, 0.75), (0, 0.5), (392, 0.75), (0, 0.5),
            (330, 0.75), (0, 0.5), (440, 0.5), (0, 0.25),
            (494, 0.5), (0, 0.25), (466, 0.5), (440, 0.5),
            
            (392, 0.33), (659, 0.33), (784, 0.33), (880, 0.5),
            (0, 0.25), (698, 0.5), (784, 0.5), (0, 0.25),
            (659, 0.5), (0, 0.25), (523, 0.5), (587, 0.5), (494, 0.5),
        ]
        
        total_duration = sum(d for _, d in melody) * beat
        num_samples = int(self.sample_rate * total_duration)
        buf = array.array('h')
        
        current_time = 0
        for freq, duration in melody:
            note_samples = int(self.sample_rate * duration * beat)
            for i in range(note_samples):
                t = i / self.sample_rate
                if freq > 0:
                    # Square wave with duty cycle variation
                    duty = 0.25
                    phase = (freq * (current_time + t)) % 1
                    value = 6000 if phase < duty else -6000
                    
                    # Envelope
                    attack = 0.01
                    release = 0.02
                    note_t = t
                    note_dur = duration * beat
                    if note_t < attack:
                        value = int(value * (note_t / attack))
                    elif note_t > note_dur - release:
                        value = int(value * ((note_dur - note_t) / release))
                else:
                    value = 0
                
                buf.append(value)
                buf.append(value)
            current_time += duration * beat
        
        return pygame.mixer.Sound(buffer=buf)

# Sprite Classes
class Mario(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.small_frames = self.create_small_sprites()
        self.big_frames = self.create_big_sprites()
        self.is_big = False
        self.has_fire = False
        self.frames = self.small_frames
        self.frame_index = 0
        self.image = self.frames['stand_right']
        self.rect = self.image.get_rect(topleft=(x, y))
        
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.facing_right = True
        self.running = False
        self.invincible = 0
        self.dead = False
        self.won = False
        self.animation_timer = 0
        
        # Physics constants
        self.walk_speed = 3
        self.run_speed = 5
        self.acceleration = 0.2
        self.deceleration = 0.3
        self.jump_power = -11
        self.run_jump_power = -12
        
    def create_small_sprites(self):
        frames = {}
        # Standing right
        surf = pygame.Surface((24, 32), pygame.SRCALPHA)
        # Head
        pygame.draw.ellipse(surf, MARIO_SKIN, (6, 2, 12, 10))
        # Hat
        pygame.draw.rect(surf, MARIO_RED, (4, 0, 16, 6))
        pygame.draw.rect(surf, MARIO_RED, (2, 4, 6, 4))
        # Body
        pygame.draw.rect(surf, MARIO_RED, (6, 12, 12, 10))
        # Overalls
        pygame.draw.rect(surf, (0, 0, 200), (6, 18, 12, 8))
        # Legs
        pygame.draw.rect(surf, (0, 0, 200), (6, 24, 5, 8))
        pygame.draw.rect(surf, (0, 0, 200), (13, 24, 5, 8))
        frames['stand_right'] = surf
        frames['stand_left'] = pygame.transform.flip(surf, True, False)
        
        # Walking frames
        for i in range(3):
            surf = pygame.Surface((24, 32), pygame.SRCALPHA)
            pygame.draw.ellipse(surf, MARIO_SKIN, (6, 2, 12, 10))
            pygame.draw.rect(surf, MARIO_RED, (4, 0, 16, 6))
            pygame.draw.rect(surf, MARIO_RED, (2, 4, 6, 4))
            pygame.draw.rect(surf, MARIO_RED, (6, 12, 12, 10))
            pygame.draw.rect(surf, (0, 0, 200), (6, 18, 12, 8))
            # Animated legs
            offset = [-2, 0, 2][i]
            pygame.draw.rect(surf, (0, 0, 200), (6 + offset, 24, 5, 8))
            pygame.draw.rect(surf, (0, 0, 200), (13 - offset, 24, 5, 8))
            frames[f'walk_right_{i}'] = surf
            frames[f'walk_left_{i}'] = pygame.transform.flip(surf, True, False)
        
        # Jumping
        surf = pygame.Surface((24, 32), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, MARIO_SKIN, (6, 2, 12, 10))
        pygame.draw.rect(surf, MARIO_RED, (4, 0, 16, 6))
        pygame.draw.rect(surf, MARIO_RED, (2, 4, 6, 4))
        pygame.draw.rect(surf, MARIO_RED, (6, 12, 12, 10))
        pygame.draw.rect(surf, (0, 0, 200), (6, 18, 12, 8))
        pygame.draw.rect(surf, (0, 0, 200), (4, 22, 5, 10))
        pygame.draw.rect(surf, (0, 0, 200), (15, 22, 5, 10))
        frames['jump_right'] = surf
        frames['jump_left'] = pygame.transform.flip(surf, True, False)
        
        # Dead
        surf = pygame.Surface((24, 32), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, MARIO_SKIN, (6, 4, 12, 10))
        pygame.draw.rect(surf, MARIO_RED, (4, 2, 16, 6))
        pygame.draw.rect(surf, MARIO_RED, (6, 14, 12, 10))
        pygame.draw.rect(surf, (0, 0, 200), (8, 20, 8, 8))
        frames['dead'] = surf
        
        return frames
    
    def create_big_sprites(self):
        frames = {}
        # Standing right - Big Mario
        surf = pygame.Surface((24, 64), pygame.SRCALPHA)
        # Head
        pygame.draw.ellipse(surf, MARIO_SKIN, (4, 2, 16, 14))
        # Hat
        pygame.draw.rect(surf, MARIO_RED, (2, 0, 20, 8))
        pygame.draw.rect(surf, MARIO_RED, (0, 6, 8, 6))
        # Body
        pygame.draw.rect(surf, MARIO_RED, (4, 16, 16, 20))
        # Overalls
        pygame.draw.rect(surf, (0, 0, 200), (4, 32, 16, 12))
        # Legs
        pygame.draw.rect(surf, (0, 0, 200), (4, 44, 7, 20))
        pygame.draw.rect(surf, (0, 0, 200), (13, 44, 7, 20))
        frames['stand_right'] = surf
        frames['stand_left'] = pygame.transform.flip(surf, True, False)
        
        # Walking frames
        for i in range(3):
            surf = pygame.Surface((24, 64), pygame.SRCALPHA)
            pygame.draw.ellipse(surf, MARIO_SKIN, (4, 2, 16, 14))
            pygame.draw.rect(surf, MARIO_RED, (2, 0, 20, 8))
            pygame.draw.rect(surf, MARIO_RED, (0, 6, 8, 6))
            pygame.draw.rect(surf, MARIO_RED, (4, 16, 16, 20))
            pygame.draw.rect(surf, (0, 0, 200), (4, 32, 16, 12))
            offset = [-3, 0, 3][i]
            pygame.draw.rect(surf, (0, 0, 200), (4 + offset, 44, 7, 20))
            pygame.draw.rect(surf, (0, 0, 200), (13 - offset, 44, 7, 20))
            frames[f'walk_right_{i}'] = surf
            frames[f'walk_left_{i}'] = pygame.transform.flip(surf, True, False)
        
        # Jumping
        surf = pygame.Surface((24, 64), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, MARIO_SKIN, (4, 2, 16, 14))
        pygame.draw.rect(surf, MARIO_RED, (2, 0, 20, 8))
        pygame.draw.rect(surf, MARIO_RED, (0, 6, 8, 6))
        pygame.draw.rect(surf, MARIO_RED, (4, 16, 16, 20))
        pygame.draw.rect(surf, (0, 0, 200), (4, 32, 16, 12))
        pygame.draw.rect(surf, (0, 0, 200), (2, 42, 7, 22))
        pygame.draw.rect(surf, (0, 0, 200), (15, 42, 7, 22))
        frames['jump_right'] = surf
        frames['jump_left'] = pygame.transform.flip(surf, True, False)
        
        frames['dead'] = frames['stand_right']
        
        return frames
    
    def update(self, keys, tiles, enemies, items):
        if self.dead or self.won:
            return
        
        # Horizontal movement
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.facing_right = True
            max_speed = self.run_speed if (keys[pygame.K_LSHIFT] or keys[pygame.K_z]) else self.walk_speed
            self.vx = min(self.vx + self.acceleration, max_speed)
            self.running = keys[pygame.K_LSHIFT] or keys[pygame.K_z]
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.facing_right = False
            max_speed = self.run_speed if (keys[pygame.K_LSHIFT] or keys[pygame.K_z]) else self.walk_speed
            self.vx = max(self.vx - self.acceleration, -max_speed)
            self.running = keys[pygame.K_LSHIFT] or keys[pygame.K_z]
        else:
            # Deceleration
            if self.vx > 0:
                self.vx = max(0, self.vx - self.deceleration)
            elif self.vx < 0:
                self.vx = min(0, self.vx + self.deceleration)
        
        # Jumping
        if (keys[pygame.K_SPACE] or keys[pygame.K_x]) and self.on_ground:
            jump = self.run_jump_power if self.running and abs(self.vx) > 3 else self.jump_power
            self.vy = jump
            self.on_ground = False
        
        # Apply gravity
        self.vy = min(self.vy + GRAVITY, MAX_FALL_SPEED)
        
        # Move horizontally
        self.rect.x += self.vx
        self.handle_tile_collision(tiles, 'horizontal')
        
        # Move vertically
        self.rect.y += self.vy
        self.handle_tile_collision(tiles, 'vertical')
        
        # Update animation
        self.animation_timer += 1
        if not self.on_ground:
            frame_name = 'jump_right' if self.facing_right else 'jump_left'
        elif abs(self.vx) > 0.5:
            frame = (self.animation_timer // 5) % 3
            direction = 'right' if self.facing_right else 'left'
            frame_name = f'walk_{direction}_{frame}'
        else:
            frame_name = 'stand_right' if self.facing_right else 'stand_left'
        
        self.frames = self.big_frames if self.is_big else self.small_frames
        self.image = self.frames[frame_name]
        
        # Invincibility flicker
        if self.invincible > 0:
            self.invincible -= 1
            if self.invincible % 4 < 2:
                self.image.set_alpha(100)
            else:
                self.image.set_alpha(255)
        else:
            self.image.set_alpha(255)
    
    def handle_tile_collision(self, tiles, direction):
        self.on_ground = False
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if direction == 'horizontal':
                    if self.vx > 0:
                        self.rect.right = tile.rect.left
                    elif self.vx < 0:
                        self.rect.left = tile.rect.right
                    self.vx = 0
                elif direction == 'vertical':
                    if self.vy > 0:
                        self.rect.bottom = tile.rect.top
                        self.vy = 0
                        self.on_ground = True
                    elif self.vy < 0:
                        self.rect.top = tile.rect.bottom
                        self.vy = 0
                        # Hit block from below
                        if hasattr(tile, 'hit_from_below'):
                            tile.hit_from_below(self)
    
    def grow(self):
        if not self.is_big:
            self.is_big = True
            self.rect.height = 64
            self.rect.y -= 32
            self.frames = self.big_frames
    
    def shrink(self):
        if self.is_big:
            self.is_big = False
            self.rect.height = 32
            self.frames = self.small_frames
            self.invincible = 120
    
    def die(self):
        self.dead = True
        self.vy = -10
        self.image = self.frames['dead']

class Goomba(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.frames = self.create_sprites()
        self.frame_index = 0
        self.image = self.frames[0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vx = -1
        self.vy = 0
        self.dead = False
        self.squished = False
        self.squish_timer = 0
        self.animation_timer = 0
        
    def create_sprites(self):
        frames = []
        for i in range(2):
            surf = pygame.Surface((32, 32), pygame.SRCALPHA)
            # Body
            pygame.draw.ellipse(surf, GOOMBA_BROWN, (2, 8, 28, 24))
            # Feet
            offset = 2 if i == 0 else -2
            pygame.draw.ellipse(surf, (100, 50, 20), (2 + offset, 26, 12, 8))
            pygame.draw.ellipse(surf, (100, 50, 20), (18 - offset, 26, 12, 8))
            # Eyes
            pygame.draw.ellipse(surf, WHITE, (6, 10, 8, 10))
            pygame.draw.ellipse(surf, WHITE, (18, 10, 8, 10))
            pygame.draw.ellipse(surf, BLACK, (8, 12, 4, 6))
            pygame.draw.ellipse(surf, BLACK, (20, 12, 4, 6))
            # Eyebrows (angry)
            pygame.draw.line(surf, BLACK, (6, 8), (14, 12), 2)
            pygame.draw.line(surf, BLACK, (26, 8), (18, 12), 2)
            frames.append(surf)
        
        # Squished frame
        surf = pygame.Surface((32, 16), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, GOOMBA_BROWN, (2, 4, 28, 12))
        frames.append(surf)
        
        return frames
    
    def update(self, tiles):
        if self.squished:
            self.squish_timer += 1
            if self.squish_timer > 30:
                self.kill()
            return
        
        if self.dead:
            self.vy += GRAVITY
            self.rect.y += self.vy
            if self.rect.top > 600:
                self.kill()
            return
        
        # Apply gravity
        self.vy = min(self.vy + GRAVITY, MAX_FALL_SPEED)
        
        # Move
        self.rect.x += self.vx
        self.rect.y += self.vy
        
        # Tile collision
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.vy > 0:
                    self.rect.bottom = tile.rect.top
                    self.vy = 0
                elif self.vx > 0:
                    self.rect.right = tile.rect.left
                    self.vx = -self.vx
                elif self.vx < 0:
                    self.rect.left = tile.rect.right
                    self.vx = -self.vx
        
        # Animation
        self.animation_timer += 1
        self.frame_index = (self.animation_timer // 10) % 2
        self.image = self.frames[self.frame_index]
    
    def stomp(self):
        self.squished = True
        self.image = self.frames[2]
        self.rect.height = 16
        self.rect.y += 16
    
    def hit_by_block(self):
        self.dead = True
        self.vy = -5
        self.image = pygame.transform.flip(self.frames[0], False, True)

class Koopa(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.frames = self.create_sprites()
        self.shell_frame = self.create_shell()
        self.frame_index = 0
        self.image = self.frames[0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vx = -1
        self.vy = 0
        self.is_shell = False
        self.shell_moving = False
        self.animation_timer = 0
        
    def create_sprites(self):
        frames = []
        for i in range(2):
            surf = pygame.Surface((32, 48), pygame.SRCALPHA)
            # Shell
            pygame.draw.ellipse(surf, KOOPA_GREEN, (4, 20, 24, 28))
            pygame.draw.ellipse(surf, (0, 128, 0), (8, 24, 16, 20))
            # Head
            pygame.draw.ellipse(surf, (255, 220, 150), (2, 4, 16, 20))
            # Eye
            pygame.draw.ellipse(surf, WHITE, (4, 8, 8, 8))
            pygame.draw.ellipse(surf, BLACK, (6, 10, 4, 4))
            # Feet
            offset = 3 if i == 0 else -3
            pygame.draw.ellipse(surf, (255, 220, 150), (4 + offset, 42, 10, 8))
            pygame.draw.ellipse(surf, (255, 220, 150), (18 - offset, 42, 10, 8))
            frames.append(surf)
        return frames
    
    def create_shell(self):
        surf = pygame.Surface((32, 28), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, KOOPA_GREEN, (2, 2, 28, 24))
        pygame.draw.ellipse(surf, (0, 128, 0), (6, 6, 20, 16))
        return surf
    
    def update(self, tiles):
        # Apply gravity
        self.vy = min(self.vy + GRAVITY, MAX_FALL_SPEED)
        
        # Move
        self.rect.x += self.vx
        self.rect.y += self.vy
        
        # Tile collision
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.vy > 0:
                    self.rect.bottom = tile.rect.top
                    self.vy = 0
                elif self.vx > 0:
                    self.rect.right = tile.rect.left
                    self.vx = -self.vx
                elif self.vx < 0:
                    self.rect.left = tile.rect.right
                    self.vx = -self.vx
        
        # Animation
        if not self.is_shell:
            self.animation_timer += 1
            self.frame_index = (self.animation_timer // 10) % 2
            self.image = self.frames[self.frame_index]
    
    def stomp(self):
        if not self.is_shell:
            self.is_shell = True
            self.vx = 0
            self.image = self.shell_frame
            self.rect.height = 28
            self.rect.y += 20
        elif not self.shell_moving:
            self.shell_moving = True
            self.vx = 6
        else:
            self.shell_moving = False
            self.vx = 0

class Mushroom(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = self.create_sprite()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vx = 2
        self.vy = 0
        self.emerging = True
        self.emerge_y = y
        self.start_y = y + 32
        
    def create_sprite(self):
        surf = pygame.Surface((28, 28), pygame.SRCALPHA)
        # Cap
        pygame.draw.ellipse(surf, RED, (0, 0, 28, 20))
        # White spots
        pygame.draw.ellipse(surf, WHITE, (4, 4, 8, 8))
        pygame.draw.ellipse(surf, WHITE, (16, 4, 8, 8))
        pygame.draw.ellipse(surf, WHITE, (10, 10, 6, 6))
        # Stem
        pygame.draw.rect(surf, (255, 220, 180), (6, 16, 16, 12))
        return surf
    
    def update(self, tiles):
        if self.emerging:
            self.rect.y -= 1
            if self.rect.y <= self.emerge_y:
                self.emerging = False
            return
        
        self.vy = min(self.vy + GRAVITY, MAX_FALL_SPEED)
        self.rect.x += self.vx
        self.rect.y += self.vy
        
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.vy > 0:
                    self.rect.bottom = tile.rect.top
                    self.vy = 0
                elif self.vx > 0:
                    self.rect.right = tile.rect.left
                    self.vx = -self.vx
                elif self.vx < 0:
                    self.rect.left = tile.rect.right
                    self.vx = -self.vx

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y, from_block=False):
        super().__init__()
        self.frames = self.create_sprites()
        self.frame_index = 0
        self.image = self.frames[0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.animation_timer = 0
        self.from_block = from_block
        self.vy = -8 if from_block else 0
        self.lifetime = 30 if from_block else 9999
        
    def create_sprites(self):
        frames = []
        widths = [16, 12, 4, 12]
        for w in widths:
            surf = pygame.Surface((16, 24), pygame.SRCALPHA)
            x_offset = (16 - w) // 2
            pygame.draw.ellipse(surf, COIN_GOLD, (x_offset, 0, w, 24))
            if w > 8:
                pygame.draw.ellipse(surf, (200, 150, 40), (x_offset + 2, 4, w - 4, 16))
            frames.append(surf)
        return frames
    
    def update(self, tiles):
        self.animation_timer += 1
        self.frame_index = (self.animation_timer // 5) % 4
        self.image = self.frames[self.frame_index]
        
        if self.from_block:
            self.vy += 0.5
            self.rect.y += self.vy
            self.lifetime -= 1
            if self.lifetime <= 0:
                self.kill()

class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y, tile_type):
        super().__init__()
        self.tile_type = tile_type
        self.image = self.create_sprite()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.original_y = y
        self.bump_offset = 0
        self.bumping = False
        
    def create_sprite(self):
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
        
        if self.tile_type == 'ground':
            surf.fill(GROUND_BROWN)
            # Brick pattern
            pygame.draw.rect(surf, (160, 60, 8), (0, 0, TILE_SIZE, 2))
            pygame.draw.rect(surf, (160, 60, 8), (0, 15, TILE_SIZE, 2))
            pygame.draw.rect(surf, (160, 60, 8), (15, 0, 2, TILE_SIZE))
            
        elif self.tile_type == 'brick':
            surf.fill(BRICK_RED)
            pygame.draw.rect(surf, (160, 60, 8), (0, 0, TILE_SIZE, 2))
            pygame.draw.rect(surf, (160, 60, 8), (0, 15, TILE_SIZE, 2))
            pygame.draw.rect(surf, (160, 60, 8), (15, 0, 2, 16))
            pygame.draw.rect(surf, (160, 60, 8), (0, 16, TILE_SIZE, 2))
            pygame.draw.rect(surf, (160, 60, 8), (7, 16, 2, 16))
            pygame.draw.rect(surf, (160, 60, 8), (23, 16, 2, 16))
            pygame.draw.rect(surf, BLACK, (0, 0, TILE_SIZE, TILE_SIZE), 1)
            
        elif self.tile_type == 'question':
            surf.fill(BLOCK_YELLOW)
            pygame.draw.rect(surf, (200, 120, 40), (0, 0, TILE_SIZE, TILE_SIZE), 3)
            # Question mark
            font = pygame.font.Font(None, 28)
            text = font.render('?', True, BLACK)
            surf.blit(text, (10, 4))
            
        elif self.tile_type == 'used':
            surf.fill((100, 60, 20))
            pygame.draw.rect(surf, (80, 40, 10), (0, 0, TILE_SIZE, TILE_SIZE), 3)
            
        elif self.tile_type == 'pipe_top_left':
            surf.fill(PIPE_GREEN)
            pygame.draw.rect(surf, PIPE_DARK, (0, 0, 4, TILE_SIZE))
            pygame.draw.rect(surf, (0, 200, 0), (TILE_SIZE - 8, 0, 8, TILE_SIZE))
            
        elif self.tile_type == 'pipe_top_right':
            surf.fill(PIPE_GREEN)
            pygame.draw.rect(surf, (0, 200, 0), (0, 0, 8, TILE_SIZE))
            pygame.draw.rect(surf, PIPE_DARK, (TILE_SIZE - 4, 0, 4, TILE_SIZE))
            
        elif self.tile_type == 'pipe_left':
            surf.fill(PIPE_GREEN)
            pygame.draw.rect(surf, PIPE_DARK, (4, 0, 4, TILE_SIZE))
            pygame.draw.rect(surf, (0, 200, 0), (TILE_SIZE - 4, 0, 4, TILE_SIZE))
            
        elif self.tile_type == 'pipe_right':
            surf.fill(PIPE_GREEN)
            pygame.draw.rect(surf, (0, 200, 0), (0, 0, 4, TILE_SIZE))
            pygame.draw.rect(surf, PIPE_DARK, (TILE_SIZE - 8, 0, 4, TILE_SIZE))
            
        elif self.tile_type == 'flagpole':
            surf.fill(SKY_BLUE)
            surf.set_colorkey(SKY_BLUE)
            pygame.draw.rect(surf, (100, 100, 100), (14, 0, 4, TILE_SIZE))
            
        elif self.tile_type == 'flag':
            surf.fill(SKY_BLUE)
            surf.set_colorkey(SKY_BLUE)
            pygame.draw.polygon(surf, (0, 200, 0), [(4, 0), (4, 20), (28, 10)])
            
        elif self.tile_type == 'castle_brick':
            surf.fill((140, 140, 140))
            pygame.draw.rect(surf, (100, 100, 100), (0, 0, TILE_SIZE, 2))
            pygame.draw.rect(surf, (100, 100, 100), (15, 0, 2, TILE_SIZE))
            
        return surf
    
    def update(self, *args):
        if self.bumping:
            self.bump_offset -= 2 if self.bump_offset > -8 else -2
            if self.bump_offset <= -8:
                self.bumping = False
            self.rect.y = self.original_y + self.bump_offset
        elif self.bump_offset < 0:
            self.bump_offset += 2
            self.rect.y = self.original_y + self.bump_offset

class QuestionBlock(Tile):
    def __init__(self, x, y, contents='coin'):
        super().__init__(x, y, 'question')
        self.contents = contents
        self.used = False
        self.items_group = None
        self.coins_group = None
        
    def hit_from_below(self, mario):
        if self.used:
            self.bumping = True
            return
        
        self.used = True
        self.tile_type = 'used'
        self.image = self.create_sprite()
        self.bumping = True
        
        if self.contents == 'coin':
            if self.coins_group:
                coin = Coin(self.rect.x + 8, self.rect.y - 24, from_block=True)
                self.coins_group.add(coin)
        elif self.contents == 'mushroom':
            if self.items_group:
                mushroom = Mushroom(self.rect.x + 2, self.rect.y)
                self.items_group.add(mushroom)

class BrickBlock(Tile):
    def __init__(self, x, y, has_coin=False):
        super().__init__(x, y, 'brick')
        self.has_coin = has_coin
        self.coins_group = None
        
    def hit_from_below(self, mario):
        self.bumping = True
        if self.has_coin:
            if self.coins_group:
                coin = Coin(self.rect.x + 8, self.rect.y - 24, from_block=True)
                self.coins_group.add(coin)
            self.has_coin = False
        elif mario.is_big:
            self.kill()

# Level Data
LEVEL_1_1 = """
................................................................................F.CCCC
.......................................................?........?...?...?........CCCC
..............................................................................P..CCCC
.............................................................?....................
................................................................................P.....
....................................?..B?B?B......................................P.....
.............................................................................................
..........G......G.G.....................................K........G.G........G...P.....
GGGGGGGGGGGGGGGGGGGGGG....GGGGGGGGGGGGGGGGGGGG..GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG
GGGGGGGGGGGGGGGGGGGGGG....GGGGGGGGGGGGGGGGGGGG..GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG
"""

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Super Mario Bros 1-1')
        self.clock = pygame.time.Clock()
        
        # Sound
        self.sound_gen = SoundGenerator()
        self.music_gen = MusicGenerator()
        
        self.sounds = {
            'jump': self.sound_gen.generate_jump_sound(),
            'coin': self.sound_gen.generate_coin_sound(),
            'stomp': self.sound_gen.generate_stomp_sound(),
            'powerup': self.sound_gen.generate_powerup_sound(),
            'death': self.sound_gen.generate_death_sound(),
            'brick': self.sound_gen.generate_brick_break_sound(),
            'bump': self.sound_gen.generate_bump_sound(),
            'flagpole': self.sound_gen.generate_flagpole_sound(),
        }
        
        self.overworld_music = self.music_gen.generate_overworld_theme()
        
        self.state = GameState.TITLE
        self.score = 0
        self.coins = 0
        self.lives = 3
        self.time = 400
        
        self.reset_level()
        
    def reset_level(self):
        self.all_sprites = pygame.sprite.Group()
        self.tiles = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        self.coins_group = pygame.sprite.Group()
        
        self.mario = Mario(64, 320)
        self.all_sprites.add(self.mario)
        
        self.camera_x = 0
        self.level_width = 0
        self.flagpole_x = 0
        
        self.load_level(LEVEL_1_1)
        
        self.time = 400
        self.time_counter = 0
        
    def load_level(self, level_data):
        lines = level_data.strip().split('\n')
        
        for row, line in enumerate(lines):
            for col, char in enumerate(line):
                x = col * TILE_SIZE
                y = row * TILE_SIZE + 160
                
                if char == 'G':
                    tile = Tile(x, y, 'ground')
                    self.tiles.add(tile)
                    self.all_sprites.add(tile)
                    
                elif char == 'B':
                    tile = BrickBlock(x, y)
                    tile.coins_group = self.coins_group
                    self.tiles.add(tile)
                    self.all_sprites.add(tile)
                    
                elif char == '?':
                    tile = QuestionBlock(x, y, 'coin')
                    tile.items_group = self.items
                    tile.coins_group = self.coins_group
                    self.tiles.add(tile)
                    self.all_sprites.add(tile)
                    
                elif char == 'M':
                    tile = QuestionBlock(x, y, 'mushroom')
                    tile.items_group = self.items
                    tile.coins_group = self.coins_group
                    self.tiles.add(tile)
                    self.all_sprites.add(tile)
                    
                elif char == 'P':
                    # Pipe (simplified)
                    for py in range(2):
                        tile_l = Tile(x, y + py * TILE_SIZE, 'pipe_top_left' if py == 0 else 'pipe_left')
                        tile_r = Tile(x + TILE_SIZE, y + py * TILE_SIZE, 'pipe_top_right' if py == 0 else 'pipe_right')
                        self.tiles.add(tile_l, tile_r)
                        self.all_sprites.add(tile_l, tile_r)
                        
                elif char == 'g':
                    enemy = Goomba(x, y)
                    self.enemies.add(enemy)
                    self.all_sprites.add(enemy)
                    
                elif char == 'K':
                    enemy = Koopa(x, y - 16)
                    self.enemies.add(enemy)
                    self.all_sprites.add(enemy)
                    
                elif char == 'c':
                    coin = Coin(x + 8, y + 4)
                    self.coins_group.add(coin)
                    self.all_sprites.add(coin)
                    
                elif char == 'F':
                    self.flagpole_x = x
                    for fy in range(8):
                        tile = Tile(x, y - fy * TILE_SIZE, 'flagpole')
                        self.all_sprites.add(tile)
                    flag = Tile(x - 12, y - 7 * TILE_SIZE, 'flag')
                    self.all_sprites.add(flag)
                    
                elif char == 'C':
                    tile = Tile(x, y, 'castle_brick')
                    self.tiles.add(tile)
                    self.all_sprites.add(tile)
                
                self.level_width = max(self.level_width, x + TILE_SIZE)
        
        # Add some enemies manually for better gameplay
        enemy_positions = [(400, 352), (600, 352), (900, 352), (1200, 352), (1500, 352)]
        for ex, ey in enemy_positions:
            enemy = Goomba(ex, ey)
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)
    
    def run(self):
        running = True
        music_playing = False
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if self.state == GameState.TITLE:
                        self.state = GameState.PLAYING
                        self.overworld_music.play(-1)
                        music_playing = True
                    elif self.state == GameState.DEAD:
                        self.lives -= 1
                        if self.lives <= 0:
                            self.state = GameState.GAMEOVER
                        else:
                            self.reset_level()
                            self.state = GameState.PLAYING
                            self.overworld_music.play(-1)
                    elif self.state == GameState.GAMEOVER:
                        self.score = 0
                        self.coins = 0
                        self.lives = 3
                        self.reset_level()
                        self.state = GameState.TITLE
                    elif self.state == GameState.WIN:
                        self.state = GameState.TITLE
                        self.reset_level()
                    
                    if event.key == pygame.K_SPACE and self.state == GameState.PLAYING:
                        if self.mario.on_ground:
                            self.sounds['jump'].play()
            
            if self.state == GameState.PLAYING:
                self.update()
            
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
    
    def update(self):
        keys = pygame.key.get_pressed()
        
        # Update Mario
        self.mario.update(keys, self.tiles, self.enemies, self.items)
        
        # Update camera
        target_x = self.mario.rect.centerx - SCREEN_WIDTH // 3
        self.camera_x = max(0, min(target_x, self.level_width - SCREEN_WIDTH))
        
        # Check if Mario fell
        if self.mario.rect.top > 600:
            self.mario.die()
            self.sounds['death'].play()
            self.overworld_music.stop()
            self.state = GameState.DEAD
        
        # Update tiles
        for tile in self.tiles:
            tile.update()
        
        # Update enemies
        for enemy in self.enemies:
            enemy.update(self.tiles)
            
            # Check collision with Mario
            if not self.mario.dead and not self.mario.invincible:
                if self.mario.rect.colliderect(enemy.rect):
                    if isinstance(enemy, Goomba):
                        if self.mario.vy > 0 and self.mario.rect.bottom < enemy.rect.centery + 10:
                            enemy.stomp()
                            self.mario.vy = -8
                            self.score += 100
                            self.sounds['stomp'].play()
                        elif not enemy.squished:
                            self.damage_mario()
                    elif isinstance(enemy, Koopa):
                        if enemy.is_shell and not enemy.shell_moving:
                            enemy.stomp()
                            self.sounds['stomp'].play()
                        elif self.mario.vy > 0 and self.mario.rect.bottom < enemy.rect.centery + 10:
                            enemy.stomp()
                            self.mario.vy = -8
                            self.score += 100
                            self.sounds['stomp'].play()
                        else:
                            self.damage_mario()
        
        # Update items
        for item in self.items:
            item.update(self.tiles)
            if self.mario.rect.colliderect(item.rect) and not item.emerging:
                if isinstance(item, Mushroom):
                    self.mario.grow()
                    self.score += 1000
                    self.sounds['powerup'].play()
                item.kill()
        
        # Update coins
        for coin in self.coins_group:
            coin.update(self.tiles)
            if not coin.from_block and self.mario.rect.colliderect(coin.rect):
                self.coins += 1
                self.score += 200
                self.sounds['coin'].play()
                coin.kill()
            elif coin.from_block:
                self.coins += 1
                self.score += 200
                if coin.lifetime == 29:  # Just spawned
                    self.sounds['coin'].play()
        
        # Check flagpole
        if self.mario.rect.right >= self.flagpole_x and not self.mario.won:
            self.mario.won = True
            self.mario.vx = 0
            self.score += self.time * 50
            self.sounds['flagpole'].play()
            self.overworld_music.stop()
            self.state = GameState.WIN
        
        # Timer
        self.time_counter += 1
        if self.time_counter >= 24:
            self.time_counter = 0
            self.time -= 1
            if self.time <= 0:
                self.mario.die()
                self.sounds['death'].play()
                self.overworld_music.stop()
                self.state = GameState.DEAD
    
    def damage_mario(self):
        if self.mario.is_big:
            self.mario.shrink()
        else:
            self.mario.die()
            self.sounds['death'].play()
            self.overworld_music.stop()
            self.state = GameState.DEAD
    
    def draw(self):
        self.screen.fill(SKY_BLUE)
        
        if self.state == GameState.TITLE:
            self.draw_title()
        elif self.state in (GameState.PLAYING, GameState.WIN):
            self.draw_game()
            self.draw_hud()
            if self.state == GameState.WIN:
                self.draw_win()
        elif self.state == GameState.DEAD:
            self.draw_game()
            self.draw_death()
        elif self.state == GameState.GAMEOVER:
            self.draw_gameover()
        
        pygame.display.flip()
    
    def draw_title(self):
        # Draw decorative elements
        self.draw_clouds()
        self.draw_hills()
        
        # Title
        font_big = pygame.font.Font(None, 72)
        font_small = pygame.font.Font(None, 36)
        
        title = font_big.render('SUPER MARIO BROS', True, WHITE)
        shadow = font_big.render('SUPER MARIO BROS', True, BLACK)
        self.screen.blit(shadow, (SCREEN_WIDTH // 2 - title.get_width() // 2 + 3, 103))
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
        
        subtitle = font_small.render('1-1 Recreation', True, WHITE)
        self.screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 180))
        
        # Instructions
        press = font_small.render('Press any key to start', True, WHITE)
        self.screen.blit(press, (SCREEN_WIDTH // 2 - press.get_width() // 2, 300))
        
        controls = font_small.render('Arrow Keys/WASD: Move | Space/X: Jump | Shift/Z: Run', True, WHITE)
        self.screen.blit(controls, (SCREEN_WIDTH // 2 - controls.get_width() // 2, 400))
    
    def draw_game(self):
        # Draw background elements
        self.draw_clouds()
        self.draw_hills()
        
        # Draw all sprites with camera offset
        for sprite in self.all_sprites:
            draw_x = sprite.rect.x - self.camera_x
            self.screen.blit(sprite.image, (draw_x, sprite.rect.y))
    
    def draw_clouds(self):
        cloud_positions = [(100, 80), (350, 60), (600, 90), (900, 70), (1200, 85)]
        for cx, cy in cloud_positions:
            x = (cx - self.camera_x * 0.3) % (SCREEN_WIDTH + 200) - 100
            # Draw cloud
            pygame.draw.ellipse(self.screen, CLOUD_WHITE, (x, cy, 80, 40))
            pygame.draw.ellipse(self.screen, CLOUD_WHITE, (x + 20, cy - 20, 60, 40))
            pygame.draw.ellipse(self.screen, CLOUD_WHITE, (x + 50, cy, 60, 35))
    
    def draw_hills(self):
        hill_positions = [(50, 380), (400, 360), (800, 370), (1300, 355)]
        for hx, hy in hill_positions:
            x = hx - self.camera_x * 0.5
            if -200 < x < SCREEN_WIDTH + 200:
                pygame.draw.polygon(self.screen, BUSH_GREEN, 
                    [(x, hy + 60), (x + 60, hy), (x + 120, hy + 60)])
    
    def draw_hud(self):
        font = pygame.font.Font(None, 28)
        
        # Score
        score_text = font.render(f'SCORE: {self.score:06d}', True, WHITE)
        self.screen.blit(score_text, (20, 10))
        
        # Coins
        coin_text = font.render(f'COINS: {self.coins:02d}', True, COIN_GOLD)
        self.screen.blit(coin_text, (220, 10))
        
        # World
        world_text = font.render('WORLD 1-1', True, WHITE)
        self.screen.blit(world_text, (400, 10))
        
        # Time
        time_text = font.render(f'TIME: {self.time:03d}', True, WHITE)
        self.screen.blit(time_text, (600, 10))
        
        # Lives
        lives_text = font.render(f'LIVES: {self.lives}', True, WHITE)
        self.screen.blit(lives_text, (720, 10))
    
    def draw_death(self):
        font = pygame.font.Font(None, 48)
        text = font.render('Press any key to continue', True, WHITE)
        self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 200))
    
    def draw_win(self):
        font = pygame.font.Font(None, 64)
        text = font.render('COURSE CLEAR!', True, WHITE)
        self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 150))
        
        font_small = pygame.font.Font(None, 36)
        score_text = font_small.render(f'Time Bonus: {self.time * 50}', True, WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 220))
        
        continue_text = font_small.render('Press any key to continue', True, WHITE)
        self.screen.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, 300))
    
    def draw_gameover(self):
        font = pygame.font.Font(None, 72)
        text = font.render('GAME OVER', True, WHITE)
        self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 180))
        
        font_small = pygame.font.Font(None, 36)
        score_text = font_small.render(f'Final Score: {self.score}', True, WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 260))
        
        restart = font_small.render('Press any key to restart', True, WHITE)
        self.screen.blit(restart, (SCREEN_WIDTH // 2 - restart.get_width() // 2, 340))

if __name__ == '__main__':
    game = Game()
    game.run()
