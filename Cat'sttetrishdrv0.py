import pygame
import random
import math
import sys
import time
from collections import deque
import array
import json
import os

# ==============================================================================
# ULTRA TETRIS: OMEGA ENGINE (PRO EDITION)
# ==============================================================================
# A professional-grade block stacking engine written in pure Python/Pygame.
# 
# FEATURES:
# - Multi-Channel Software Synthesizer (No external assets required)
# - Super Rotation System (SRS) with authentic Wall Kicks
# - 7-Bag Randomizer
# - T-Spin Detection (3-Corner Rule)
# - Heuristic AI Bot
# - Custom GUI Framework (Buttons, Sliders, Toggles)
# - Particle Physics Engine
# - Save/Load System for Settings & High Scores
# - Multiple Visual Themes
# - Retro Game Boy Style Menu
# - NES/Famicom Authentic Timing & Physics
# ==============================================================================

# Initialize PyGame Core
pygame.init()
# Initialize Audio Mixer (44.1kHz, 16-bit, Stereo, 1024 byte buffer for stability)
pygame.mixer.pre_init(44100, -16, 2, 1024)
pygame.mixer.set_num_channels(8)

# ------------------------------------------------------------------------------
# GLOBAL CONSTANTS & CONFIGURATION
# ------------------------------------------------------------------------------

# Version Info
VERSION = "0.1"
AUTHOR = "Samsoft"

# Display Settings
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60

# Gameplay Layout
GRID_WIDTH = 10
GRID_HEIGHT = 20
CELL_SIZE = 32
GRID_OFFSET_X = (SCREEN_WIDTH - (GRID_WIDTH * CELL_SIZE)) // 2
GRID_OFFSET_Y = (SCREEN_HEIGHT - (GRID_HEIGHT * CELL_SIZE)) // 2
SIDEBAR_WIDTH = 250
HOLD_WIDTH = 150

# Save File Path
SAVE_FILE = "ultra_tetris_save.json"

# Basic Colors (R, G, B)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 100, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (40, 40, 40)
LIGHT_GRAY = (200, 200, 200)

# Game Boy Palette
GB_WHITE = (155, 188, 15)
GB_LIGHT = (139, 172, 15)
GB_DARK = (48, 98, 48)
GB_BLACK = (15, 56, 15)

# NES Gravity Table (Frames per grid cell drop)
# Authentic NTSC NES Tetris drop speeds
NES_GRAVITY = {
    0: 48, 1: 43, 2: 38, 3: 33, 4: 28, 5: 23, 6: 18, 7: 13, 8: 8, 9: 6,
    10: 5, 11: 5, 12: 5, 13: 4, 14: 4, 15: 4, 16: 3, 17: 3, 18: 3,
    19: 2, 20: 2, 21: 2, 22: 2, 23: 2, 24: 2, 25: 2, 26: 2, 27: 2, 28: 2,
    29: 1 # The "Kill Screen" - 1 frame per drop
}
# Levels 29+ stay at 1 frame per drop

# ------------------------------------------------------------------------------
# DATA STRUCTURES & TABLES
# ------------------------------------------------------------------------------

# Tetromino Shapes (I, J, L, O, S, T, Z)
# Defined as boolean matrices
SHAPES = [
    # I
    [[0, 0, 0, 0],
     [1, 1, 1, 1],
     [0, 0, 0, 0],
     [0, 0, 0, 0]],
    # J
    [[1, 0, 0],
     [1, 1, 1],
     [0, 0, 0]],
    # L
    [[0, 0, 1],
     [1, 1, 1],
     [0, 0, 0]],
    # O
    [[1, 1],
     [1, 1]],
    # S
    [[0, 1, 1],
     [1, 1, 0],
     [0, 0, 0]],
    # T
    [[0, 1, 0],
     [1, 1, 1],
     [0, 0, 0]],
    # Z
    [[1, 1, 0],
     [0, 1, 1],
     [0, 0, 0]]
]

# SRS Wall Kick Data
# These tables define how pieces "kick" off walls when rotating
WALL_KICKS_JLSTZ = {
    (0, 1): [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],
    (1, 0): [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],
    (1, 2): [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],
    (2, 1): [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],
    (2, 3): [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],
    (3, 2): [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],
    (3, 0): [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],
    (0, 3): [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],
}

WALL_KICKS_I = {
    (0, 1): [(0, 0), (-2, 0), (1, 0), (-2, -1), (1, 2)],
    (1, 0): [(0, 0), (2, 0), (-1, 0), (2, 1), (-1, -2)],
    (1, 2): [(0, 0), (-1, 0), (2, 0), (-1, 2), (2, -1)],
    (2, 1): [(0, 0), (1, 0), (-2, 0), (1, -2), (-2, 1)],
    (2, 3): [(0, 0), (2, 0), (-1, 0), (2, 1), (-1, -2)],
    (3, 2): [(0, 0), (-2, 0), (1, 0), (-2, -1), (1, 2)],
    (3, 0): [(0, 0), (1, 0), (-2, 0), (1, -2), (-2, 1)],
    (0, 3): [(0, 0), (-1, 0), (2, 0), (-1, 2), (2, -1)],
}

# Scoring Table (NES/Classic Style)
SCORES = {
    "SINGLE": 40,
    "DOUBLE": 100,
    "TRIPLE": 300,
    "TETRIS": 1200,
    "SOFT_DROP": 1,
    "HARD_DROP": 2,
    # T-Spin bonuses (Modern extras, usually not in NES but kept for hybrid feel)
    "TSPIN": 400,
    "TSPIN_SINGLE": 800,
    "TSPIN_DOUBLE": 1200,
    "TSPIN_TRIPLE": 1600
}

# ------------------------------------------------------------------------------
# UTILITY CLASSES
# ------------------------------------------------------------------------------

class SettingsManager:
    """Handles saving and loading of game configuration and high scores."""
    
    DEFAULT_SETTINGS = {
        "music_volume": 0.5,
        "sfx_volume": 0.7,
        "theme": "NEON",
        "ai_speed": 0.05,
        "high_scores": [],
        "controls": {
            "left": pygame.K_LEFT,
            "right": pygame.K_RIGHT,
            "rotate_cw": pygame.K_UP,
            "rotate_ccw": pygame.K_z,
            "soft_drop": pygame.K_DOWN,
            "hard_drop": pygame.K_SPACE,
            "hold": pygame.K_LSHIFT,
            "pause": pygame.K_ESCAPE,
            "music_toggle": pygame.K_m
        }
    }

    def __init__(self):
        self.data = self.DEFAULT_SETTINGS.copy()
        self.load()

    def load(self):
        """Loads settings from JSON file with error handling."""
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, 'r') as f:
                    loaded = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    for k, v in loaded.items():
                        if k in self.data:
                            self.data[k] = v
                print("Settings loaded successfully.")
            except (json.JSONDecodeError, OSError) as e:
                print(f"Error loading settings, using defaults: {e}")
                self.data = self.DEFAULT_SETTINGS.copy()

    def save(self):
        """Saves current settings to JSON file."""
        try:
            with open(SAVE_FILE, 'w') as f:
                json.dump(self.data, f, indent=4)
            print("Settings saved.")
        except OSError as e:
            print(f"Error saving settings: {e}")

    def get(self, key):
        return self.data.get(key, self.DEFAULT_SETTINGS.get(key))

    def set(self, key, value):
        self.data[key] = value

    def add_score(self, score, mode="MARATHON"):
        """Adds a high score entry."""
        scores = self.data["high_scores"]
        scores.append({"score": score, "date": time.strftime("%Y-%m-%d"), "mode": mode})
        scores.sort(key=lambda x: x["score"], reverse=True)
        self.data["high_scores"] = scores[:10]  # Keep top 10
        self.save()

# Global Settings Instance
SETTINGS = SettingsManager()

class Theme:
    """Defines color palettes for the game."""
    
    THEMES = {
        "NEON": {
            "bg": (20, 20, 30),
            "grid": (40, 40, 60),
            "text": WHITE,
            "colors": [CYAN, BLUE, ORANGE, YELLOW, GREEN, MAGENTA, RED]
        },
        "RETRO": {
            "bg": GB_WHITE,
            "grid": GB_LIGHT,
            "text": GB_BLACK,
            "colors": [GB_BLACK, GB_BLACK, GB_DARK, GB_DARK, GB_BLACK, GB_BLACK, GB_DARK]
        },
        "PASTEL": {
            "bg": (240, 240, 245),
            "grid": (200, 200, 210),
            "text": (80, 80, 90),
            "colors": [(174, 225, 252), (150, 180, 220), (255, 200, 150), (255, 255, 180), (180, 240, 180), (200, 180, 240), (255, 180, 180)]
        },
        "MATRIX": {
            "bg": BLACK,
            "grid": (0, 50, 0),
            "text": (0, 255, 0),
            "colors": [(0, 255, 0), (0, 200, 0), (0, 150, 0), (20, 255, 20), (0, 255, 50), (50, 255, 50), (0, 180, 0)]
        }
    }

    @staticmethod
    def get_current():
        theme_name = SETTINGS.get("theme")
        return Theme.THEMES.get(theme_name, Theme.THEMES["NEON"])

# ------------------------------------------------------------------------------
# GRAPHICAL USER INTERFACE (GUI) SYSTEM
# ------------------------------------------------------------------------------

class Widget:
    """Base class for all UI elements."""
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.is_hovered = False
        self.is_active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        return False

    def draw(self, surface):
        pass

class Button(Widget):
    """A clickable button with text."""
    def __init__(self, x, y, w, h, text, callback, color=BLUE, style="modern"):
        super().__init__(x, y, w, h)
        self.text = text
        self.callback = callback
        self.color = color
        self.style = style # "modern" or "retro"
        self.font = pygame.font.Font(None, 24) # Use default system font for retro look

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
            if self.callback:
                self.callback()
                return True
        return False

    def draw(self, surface):
        if self.style == "retro":
            # Retro Gameboy Style
            bg_col = GB_WHITE if not self.is_hovered else GB_LIGHT
            fg_col = GB_BLACK
            
            # Hard edges, no alpha
            pygame.draw.rect(surface, fg_col, (self.rect.x, self.rect.y+4, self.rect.w, self.rect.h), 0) # Shadow
            pygame.draw.rect(surface, bg_col, self.rect, 0)
            pygame.draw.rect(surface, fg_col, self.rect, 3) # Thick border
            
            txt_surf = self.font.render(self.text, False, fg_col) # No anti-aliasing
            txt_rect = txt_surf.get_rect(center=self.rect.center)
            surface.blit(txt_surf, txt_rect)
            
        else:
            # Modern Style
            col = tuple(min(c + 40, 255) for c in self.color) if self.is_hovered else self.color
            pygame.draw.rect(surface, (0,0,0,100), (self.rect.x+4, self.rect.y+4, self.rect.w, self.rect.h), border_radius=6)
            pygame.draw.rect(surface, col, self.rect, border_radius=6)
            pygame.draw.rect(surface, WHITE if self.is_hovered else (200,200,200), self.rect, 2, border_radius=6)
            
            txt_surf = self.font.render(self.text, True, WHITE)
            txt_rect = txt_surf.get_rect(center=self.rect.center)
            surface.blit(txt_surf, txt_rect)

class Slider(Widget):
    """A horizontal slider for numeric values."""
    def __init__(self, x, y, w, h, min_val, max_val, initial_val, callback):
        super().__init__(x, y, w, h)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.callback = callback
        self.dragging = False

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
            self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        
        if self.dragging and event.type == pygame.MOUSEMOTION:
            rel_x = event.pos[0] - self.rect.x
            ratio = max(0, min(1, rel_x / self.rect.w))
            self.value = self.min_val + ratio * (self.max_val - self.min_val)
            if self.callback:
                self.callback(self.value)
            return True
        return False

    def draw(self, surface):
        # Track
        pygame.draw.rect(surface, DARK_GRAY, (self.rect.x, self.rect.centery - 4, self.rect.w, 8), border_radius=4)
        
        # Filled part
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        fill_w = int(ratio * self.rect.w)
        pygame.draw.rect(surface, BLUE, (self.rect.x, self.rect.centery - 4, fill_w, 8), border_radius=4)
        
        # Handle
        handle_x = self.rect.x + fill_w
        pygame.draw.circle(surface, WHITE, (handle_x, self.rect.centery), 10)
        pygame.draw.circle(surface, BLACK, (handle_x, self.rect.centery), 10, 1)

class Toggle(Widget):
    """A toggle switch (checkbox)."""
    def __init__(self, x, y, w, text, initial_state, callback):
        super().__init__(x, y, w, 30)
        self.text = text
        self.state = initial_state
        self.callback = callback
        self.font = pygame.font.Font(None, 20)

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
            self.state = not self.state
            if self.callback:
                self.callback(self.state)
            return True
        return False

    def draw(self, surface):
        # Draw Box
        box_rect = pygame.Rect(self.rect.x, self.rect.y, 30, 30)
        pygame.draw.rect(surface, DARK_GRAY, box_rect, border_radius=4)
        pygame.draw.rect(surface, WHITE, box_rect, 2, border_radius=4)
        
        if self.state:
            inner_rect = box_rect.inflate(-8, -8)
            pygame.draw.rect(surface, GREEN, inner_rect, border_radius=2)
            
        # Draw Text
        txt = self.font.render(self.text, True, WHITE)
        surface.blit(txt, (self.rect.x + 40, self.rect.y + 5))

class Label(Widget):
    """Simple text label."""
    def __init__(self, x, y, text, font_size=24, color=WHITE, font_name=None):
        super().__init__(x, y, 0, 0)
        self.text = text
        self.color = color
        self.font = pygame.font.Font(font_name, font_size)

    def draw(self, surface):
        surf = self.font.render(self.text, False, self.color)
        surface.blit(surf, (self.rect.x, self.rect.y))

# ------------------------------------------------------------------------------
# ADVANCED AUDIO ENGINE
# ------------------------------------------------------------------------------

class Oscillator:
    """Generates audio waveforms."""
    def __init__(self, freq, wave_type='square'):
        self.freq = freq
        self.wave_type = wave_type
        self.phase = 0.0

    def generate(self, num_samples, sample_rate, volume):
        if self.freq <= 0: return array.array('h', [0]*num_samples)
        
        period = sample_rate / self.freq
        amplitude = 32767 * volume
        buf = array.array('h', [0] * num_samples)
        
        # Generate entire buffer at once (simulated, pure python loop)
        if self.wave_type == 'square':
            half_period = period / 2
            for i in range(num_samples):
                val = amplitude if (i % period) < half_period else -amplitude
                # Envelope
                if i < 200: val *= (i/200)
                elif i > num_samples - 200: val *= ((num_samples-i)/200)
                buf[i] = int(val)
                
        elif self.wave_type == 'saw':
            for i in range(num_samples):
                val = amplitude * (2 * (i % period) / period - 1)
                if i < 200: val *= (i/200)
                elif i > num_samples - 200: val *= ((num_samples-i)/200)
                buf[i] = int(val)
                
        elif self.wave_type == 'tri':
            for i in range(num_samples):
                val = amplitude * (2 / math.pi) * math.asin(math.sin(2 * math.pi * i / period))
                if i < 200: val *= (i/200)
                elif i > num_samples - 200: val *= ((num_samples-i)/200)
                buf[i] = int(val)
                
        elif self.wave_type == 'noise':
            for i in range(num_samples):
                val = random.uniform(-amplitude, amplitude)
                if i < 200: val *= (i/200)
                elif i > num_samples - 200: val *= ((num_samples-i)/200)
                buf[i] = int(val)
            
        return buf

class SynthEngine:
    """Multi-channel software synthesizer."""
    def __init__(self):
        self.sample_rate = 44100
        self.tempo = 145
        self.playing = False
        self.next_note_time = 0
        self.beat_counter = 0
        
        # Audio Cache to prevent lag
        self.sound_cache = {}
        
        # Musical Data
        self.frequencies = self._generate_freq_table()
        
        # Melody (Tetris Theme A - Korobeiniki)
        self.melody = [
            ('E5', 4), ('B4', 2), ('C5', 2), ('D5', 4), ('C5', 2), ('B4', 2),
            ('A4', 4), ('A4', 2), ('C5', 2), ('E5', 4), ('D5', 2), ('C5', 2),
            ('B4', 6), ('C5', 2), ('D5', 4), ('E5', 4),
            ('C5', 4), ('A4', 4), ('A4', 4), ('REST', 4),
            ('D5', 4), ('F5', 2), ('A5', 4), ('G5', 2), ('F5', 2),
            ('E5', 6), ('C5', 2), ('E5', 4), ('D5', 2), ('C5', 2),
            ('B4', 4), ('B4', 2), ('C5', 2), ('D5', 4), ('E5', 4),
            ('C5', 4), ('A4', 4), ('A4', 4), ('REST', 4)
        ]
        
        # Bass Line
        self.bass = [
            ('E3', 4), ('E3', 4), ('A3', 4), ('A3', 4),
            ('G#3', 4), ('G#3', 4), ('A3', 4), ('A3', 4),
            ('E3', 4), ('E3', 4), ('A3', 4), ('A3', 4),
            ('G#3', 4), ('G#3', 4), ('A3', 4), ('A3', 4),
            ('D3', 4), ('D3', 4), ('A3', 4), ('A3', 4),
            ('C3', 4), ('C3', 4), ('E3', 4), ('E3', 4),
            ('E3', 4), ('E3', 4), ('A3', 4), ('A3', 4),
            ('G#3', 4), ('E3', 4), ('A3', 8)
        ]

        self.mel_idx = 0
        self.bass_idx = 0
        self.timer = 0
        
        # Pre-cache sounds
        self._precache_sounds()

    def _generate_freq_table(self):
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        freqs = {'REST': 0}
        a4 = 440.0
        for i in range(12*8):
            octave = i // 12
            note = notes[i % 12]
            name = f"{note}{octave}"
            semitone_offset = i - 57
            f = a4 * (2 ** (semitone_offset / 12))
            freqs[name] = f
        return freqs

    def _precache_sounds(self):
        """Generates all required sounds at startup to avoid lag."""
        # Calculate duration for a 16th note
        seconds_per_16th = 60.0 / self.tempo / 4.0
        
        # Cache Melody Notes
        unique_melody = set(self.melody)
        for note, length in unique_melody:
            if note == 'REST': continue
            freq = self.frequencies.get(note, 0)
            # Staccato melody (0.9 length)
            duration = length * seconds_per_16th * 0.9
            self._get_cached_sound(freq, duration, 'square')
            
        # Cache Bass Notes
        unique_bass = set(self.bass)
        for note, length in unique_bass:
            if note == 'REST': continue
            freq = self.frequencies.get(note, 0)
            duration = length * seconds_per_16th * 0.9
            self._get_cached_sound(freq, duration, 'tri')

    def _get_cached_sound(self, freq, duration, wave):
        key = (freq, int(duration * 1000), wave) # Key by freq, duration(ms), wave
        if key not in self.sound_cache:
            osc = Oscillator(freq, wave)
            # Generate at standard volume, mix volume controlled by channel
            buf = osc.generate(int(self.sample_rate * duration), self.sample_rate, 0.5)
            self.sound_cache[key] = pygame.mixer.Sound(buffer=buf)
        return self.sound_cache[key]

    def play_note(self, freq, duration, channel_id, wave='square', vol=0.5):
        if freq <= 0: return
        
        master_vol = SETTINGS.get("music_volume")
        if master_vol <= 0: return
        
        # Use cached sound if available, otherwise generate (fallback)
        sound = self._get_cached_sound(freq, duration, wave)
        
        ch = pygame.mixer.Channel(channel_id)
        ch.set_volume(master_vol) # Set volume on channel
        ch.play(sound)

    def update(self, dt):
        if not SETTINGS.get("music_volume") > 0 or not self.playing:
            return

        seconds_per_16th = 60.0 / self.tempo / 4.0
        
        self.timer -= dt
        if self.timer <= 0:
            # Play Melody
            note, length = self.melody[self.mel_idx]
            if note != 'REST':
                freq = self.frequencies.get(note, 0)
                dur = length * seconds_per_16th * 0.9 
                self.play_note(freq, dur, 0, 'square')
            
            # Play Bass (aligned with melody for simplicity in this tick-based system)
            b_note, b_length = self.bass[self.bass_idx]
            if self.beat_counter % b_length == 0:
                 if b_note != 'REST':
                    b_freq = self.frequencies.get(b_note, 0)
                    b_dur = b_length * seconds_per_16th * 0.9
                    self.play_note(b_freq, b_dur, 1, 'tri')
                 self.bass_idx = (self.bass_idx + 1) % len(self.bass)

            # Update Melody Index
            self.timer = length * seconds_per_16th
            self.mel_idx = (self.mel_idx + 1) % len(self.melody)
            
            self.beat_counter += length

    def play_sfx(self, name):
        vol = SETTINGS.get("sfx_volume")
        if vol <= 0: return
        
        # SFX are usually short enough to generate on fly
        if name == 'move':
            self.play_note_raw(300, 0.05, 5, 'tri', vol)
        elif name == 'rotate':
            self.play_note_raw(500, 0.05, 5, 'saw', vol)
        elif name == 'drop':
            self.play_note_raw(150, 0.1, 6, 'noise', vol)
        elif name == 'clear':
            self.play_note_raw(880, 0.1, 6, 'square', vol)
        elif name == 'tetris':
             self.play_note_raw(2000, 0.4, 7, 'square', vol)
        elif name == 'gameover':
            self.play_note_raw(100, 1.0, 7, 'saw', vol)

    def play_note_raw(self, freq, duration, channel, wave, vol):
        # Direct generation for SFX
        osc = Oscillator(freq, wave)
        buf = osc.generate(int(self.sample_rate * duration), self.sample_rate, vol)
        snd = pygame.mixer.Sound(buffer=buf)
        pygame.mixer.Channel(channel).play(snd)

# Global Audio Instance
AUDIO = SynthEngine()

# ------------------------------------------------------------------------------
# PARTICLE SYSTEM
# ------------------------------------------------------------------------------

class Particle:
    def __init__(self, x, y, color, type="spark"):
        self.x = x
        self.y = y
        self.color = color
        self.type = type
        self.life = 1.0
        self.size = random.uniform(3, 6)
        
        angle = random.uniform(0, 6.28)
        speed = random.uniform(1, 5)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        
        if type == "text":
            self.vy = -2
            self.vx = 0
            self.life = 2.0

    def update(self):
        self.x += self.vx
        self.y += self.vy
        
        if self.type == "spark":
            self.vy += 0.2 # Gravity
            self.life -= 0.03
            self.size *= 0.95
        elif self.type == "text":
            self.life -= 0.02

    def draw(self, surface):
        if self.life <= 0: return
        
        if self.type == "spark":
            alpha = int(self.life * 255)
            s = pygame.Surface((int(self.size), int(self.size)), pygame.SRCALPHA)
            s.fill((*self.color, alpha))
            surface.blit(s, (self.x, self.y))
        
        elif self.type == "text":
            pass 

class ParticleManager:
    def __init__(self):
        self.particles = []

    def spawn(self, x, y, color, count=10):
        for _ in range(count):
            self.particles.append(Particle(x, y, color, "spark"))

    def update(self):
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.life > 0]

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)

PARTICLES = ParticleManager()

# ------------------------------------------------------------------------------
# GAMEPLAY LOGIC
# ------------------------------------------------------------------------------

class Tetromino:
    """Represents a falling piece."""
    def __init__(self, shape_idx, x, y):
        self.shape_idx = shape_idx
        self.base_shape = SHAPES[shape_idx]
        self.shape = [row[:] for row in self.base_shape] # Copy
        self.color_idx = shape_idx
        self.x = x
        self.y = y
        self.rotation = 0 # 0, 1, 2, 3
        self.t_spin_type = None # None, 'MINI', 'FULL'

    def get_rotated(self, clockwise=True):
        """Returns a rotated matrix of the shape."""
        rows = len(self.shape)
        cols = len(self.shape[0])
        new = [[0]*rows for _ in range(cols)]
        
        if clockwise:
            for r in range(rows):
                for c in range(cols):
                    new[c][rows-1-r] = self.shape[r][c]
        else:
            for r in range(rows):
                for c in range(cols):
                    new[cols-1-c][r] = self.shape[r][c]
        return new

    def get_blocks(self):
        """Yields world coordinates of occupied blocks."""
        for r, row in enumerate(self.shape):
            for c, val in enumerate(row):
                if val:
                    yield (self.x + c, self.y + r)

class Board:
    """Represents the game grid."""
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[0 for _ in range(width)] for _ in range(height)]

    def check_collision(self, piece, dx=0, dy=0, shape=None):
        if shape is None: shape = piece.shape
        for r, row in enumerate(shape):
            for c, val in enumerate(row):
                if val:
                    nx, ny = piece.x + c + dx, piece.y + r + dy
                    if nx < 0 or nx >= self.width or ny >= self.height:
                        return True
                    if ny >= 0 and self.grid[ny][nx]:
                        return True
        return False

    def lock(self, piece):
        for x, y in piece.get_blocks():
            if 0 <= y < self.height and 0 <= x < self.width:
                self.grid[y][x] = Theme.get_current()["colors"][piece.color_idx]

    def clear_lines(self):
        cleared = []
        for y in range(self.height):
            if all(self.grid[y]):
                cleared.append(y)
        
        for y in cleared:
            self.grid.pop(y)
            self.grid.insert(0, [0]*self.width)
        
        return len(cleared)

    def is_tspin(self, piece):
        """3-Corner Rule for T-Spins."""
        if piece.shape_idx != 5: # Not T piece
            return None
            
        # Check corners relative to center of T (1,1 in 3x3 matrix)
        cx, cy = piece.x + 1, piece.y + 1
        corners = [
            (cx-1, cy-1), (cx+1, cy-1),
            (cx-1, cy+1), (cx+1, cy+1)
        ]
        
        occupied = 0
        for x, y in corners:
            if x < 0 or x >= self.width or y >= self.height or (y >= 0 and self.grid[y][x]):
                occupied += 1
                
        if occupied >= 3:
            return "TSPIN"
        return None

# ------------------------------------------------------------------------------
# ARTIFICIAL INTELLIGENCE
# ------------------------------------------------------------------------------

class Bot:
    """Heuristic AI for auto-play."""
    def __init__(self, board):
        self.board = board
        # Weights (Genetic Algorithm tuned)
        self.w_height = -0.51
        self.w_lines = 0.76
        self.w_holes = -0.36
        self.w_bumpiness = -0.18
        self.w_touch = 0.1

    def evaluate_grid(self, grid):
        heights = self._get_column_heights(grid)
        max_h = max(heights)
        total_h = sum(heights)
        holes = self._count_holes(grid, heights)
        bumpiness = self._get_bumpiness(heights)
        lines = self._count_full_lines(grid)
        
        score = (total_h * self.w_height) + \
                (lines * self.w_lines) + \
                (holes * self.w_holes) + \
                (bumpiness * self.w_bumpiness)
        return score

    def _get_column_heights(self, grid):
        heights = []
        for c in range(GRID_WIDTH):
            h = 0
            for r in range(GRID_HEIGHT):
                if grid[r][c] != 0:
                    h = GRID_HEIGHT - r
                    break
            heights.append(h)
        return heights

    def _count_holes(self, grid, heights):
        holes = 0
        for c in range(GRID_WIDTH):
            if heights[c] == 0: continue
            # Iterate from the block down
            start_row = GRID_HEIGHT - heights[c]
            for r in range(start_row + 1, GRID_HEIGHT):
                if grid[r][c] == 0:
                    holes += 1
        return holes

    def _get_bumpiness(self, heights):
        bump = 0
        for i in range(len(heights) - 1):
            bump += abs(heights[i] - heights[i+1])
        return bump

    def _count_full_lines(self, grid):
        return sum(1 for row in grid if all(row))

    def get_best_move(self, piece):
        """Simulates all moves and returns the best one."""
        best_score = -float('inf')
        best_move = None # (rotation, x_pos)
        
        # Test all 4 rotations
        for rot in range(4):
            # Create a virtual piece for rotation testing
            test_shape = piece.base_shape
            for _ in range(rot):
                # Rotate manual helper
                rows = len(test_shape)
                cols = len(test_shape[0])
                new = [[0]*rows for _ in range(cols)]
                for r in range(rows):
                    for c in range(cols):
                        new[c][rows-1-r] = test_shape[r][c]
                test_shape = new
            
            # Calculate width of piece to know bounds
            min_x = -2
            max_x = GRID_WIDTH
            
            for x in range(min_x, max_x):
                # Check if lateral placement is valid first
                if self._check_collision_sim(test_shape, x, piece.y):
                    continue
                    
                # Drop Simulation
                y = piece.y
                # Hard drop sim
                while not self._check_collision_sim(test_shape, x, y + 1):
                    y += 1
                
                # Lock sim
                sim_grid = [row[:] for row in self.board.grid]
                valid_lock = True
                for r, row in enumerate(test_shape):
                    for c, val in enumerate(row):
                        if val:
                            nx, ny = x + c, y + r
                            if 0 <= ny < GRID_HEIGHT and 0 <= nx < GRID_WIDTH:
                                sim_grid[ny][nx] = 1
                            else:
                                valid_lock = False
                
                if valid_lock:
                    score = self.evaluate_grid(sim_grid)
                    if score > best_score:
                        best_score = score
                        best_move = (rot, x)

        return best_move

    def _check_collision_sim(self, shape, x, y):
        for r, row in enumerate(shape):
            for c, val in enumerate(row):
                if val:
                    nx, ny = x + c, y + r
                    if nx < 0 or nx >= GRID_WIDTH or ny >= GRID_HEIGHT:
                        return True
                    if ny >= 0 and self.board.grid[ny][nx]:
                        return True
        return False

# ------------------------------------------------------------------------------
# GAME STATES & MANAGERS
# ------------------------------------------------------------------------------

class Game:
    """Main Game Application Class."""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(f"Cat's Ultra! Tetris {VERSION}")
        self.clock = pygame.time.Clock()
        
        self.state = "MENU"
        self.theme = Theme.get_current()
        
        # Managers
        self.board = Board(GRID_WIDTH, GRID_HEIGHT)
        self.bot = Bot(self.board)
        
        # Game Vars
        self.bag = []
        self.curr_piece = None
        self.next_piece = None
        self.hold_piece = None
        self.can_hold = True
        
        self.score = 0
        self.lines = 0
        self.level = 1
        self.combo = 0
        
        self.ai_mode = False
        self.ai_timer = 0
        
        # NES Physics Counters (in frames)
        self.frame_counter = 0
        self.das_counter = 0
        self.das_delay = 16
        self.das_repeat = 6
        self.das_direction = 0 # 0=None, -1=Left, 1=Right
        self.drop_timer = 0
        
        # UI
        self.init_ui()
        
    def init_ui(self):
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        
        # Main Menu (Retro Style)
        self.main_menu_ui = [
            Label(cx - 200, 100, "Cat's Ultra! Tetris", 56, GB_BLACK),
            Label(cx - 120, 170, "[C] 1999-2026 Samsoft", 24, GB_DARK),
            Button(cx - 100, cy - 90, 200, 50, "PLAY GAME", lambda: self.start_game(False), GB_DARK, style="retro"),
            Button(cx - 100, cy - 30, 200, 50, "HOW TO PLAY", lambda: self.change_state("HOW_TO_PLAY"), GB_DARK, style="retro"),
            Button(cx - 100, cy + 30, 200, 50, "CREDITS", lambda: self.change_state("CREDITS"), GB_DARK, style="retro"),
            Button(cx - 100, cy + 90, 200, 50, "ABOUT", lambda: self.change_state("ABOUT"), GB_DARK, style="retro"),
            Button(cx - 100, cy + 150, 200, 50, "EXIT GAME", self.quit_game, GB_DARK, style="retro")
        ]
        
        # Settings Menu
        self.settings_ui = [
            Label(cx - 80, 50, "SETTINGS", 48, WHITE),
            Label(cx - 150, 150, "Music Volume", 24),
            Slider(cx + 50, 155, 150, 20, 0.0, 1.0, SETTINGS.get("music_volume"), self.set_music_vol),
            Label(cx - 150, 200, "SFX Volume", 24),
            Slider(cx + 50, 205, 150, 20, 0.0, 1.0, SETTINGS.get("sfx_volume"), self.set_sfx_vol),
            Label(cx - 150, 250, "Visual Theme", 24),
            Button(cx + 50, 245, 150, 30, "Next Theme", self.cycle_theme, MAGENTA),
            Button(cx - 100, 600, 200, 50, "BACK", lambda: self.change_state("MENU"), GRAY)
        ]

        # How To Play Menu
        self.how_to_play_ui = [
            Label(cx - 120, 50, "HOW TO PLAY", 48, GB_BLACK),
            Label(100, 150, "CONTROLS:", 32, GB_DARK),
            Label(100, 200, "Left / Right : Move", 24, GB_BLACK),
            Label(100, 230, "Up / Z       : Rotate", 24, GB_BLACK),
            Label(100, 260, "Down         : Soft Drop", 24, GB_BLACK),
            Label(100, 290, "Space        : Hard Drop", 24, GB_BLACK),
            Label(100, 320, "Shift        : Hold", 24, GB_BLACK),
            Label(100, 350, "ESC          : Pause / Back", 24, GB_BLACK),
            
            Label(100, 420, "SCORING:", 32, GB_DARK),
            Label(100, 470, "Clear lines to score points.", 24, GB_BLACK),
            Label(100, 500, "Multiple lines & T-Spins give bonuses.", 24, GB_BLACK),
            
            Button(cx - 100, 650, 200, 50, "BACK", lambda: self.change_state("MENU"), GB_DARK, style="retro")
        ]

        # Credits Menu
        self.credits_ui = [
            Label(cx - 90, 50, "CREDITS", 48, GB_BLACK),
            Label(cx - 150, 200, "DEVELOPED BY", 32, GB_DARK),
            Label(cx - 120, 250, "Samsoft", 24, GB_BLACK),
            Label(cx - 150, 280, "[C] 1999-2026", 24, GB_BLACK),
            
            Label(cx - 150, 350, "ORIGINAL CONCEPT", 32, GB_DARK),
            Label(cx - 100, 400, "The Tetris Company", 24, GB_BLACK),
            
            Label(cx - 150, 440, "SPECIAL THANKS", 32, GB_DARK),
            Label(cx - 120, 490, "The Tetris Community", 24, GB_BLACK),
            
            Button(cx - 100, 650, 200, 50, "BACK", lambda: self.change_state("MENU"), GB_DARK, style="retro")
        ]

        # About Menu
        self.about_ui = [
            Label(cx - 70, 50, "ABOUT", 48, GB_BLACK),
            Label(cx - 180, 150, "Cat's Ultra! Tetris", 32, GB_DARK),
            Label(cx - 180, 200, "[C] 1999-2026 Samsoft", 24, GB_BLACK),
            Label(cx - 180, 230, "The Tetris Company", 24, GB_BLACK),
            Label(cx - 120, 260, f"v{VERSION}", 24, GB_BLACK),
            
            Label(cx - 180, 340, "FEATURES:", 32, GB_DARK),
            Label(cx - 180, 380, "- Super Rotation System (SRS)", 24, GB_BLACK),
            Label(cx - 180, 410, "- 7-Bag Randomizer", 24, GB_BLACK),
            Label(cx - 180, 440, "- Software Audio Synthesis", 24, GB_BLACK),
            Label(cx - 180, 470, "- Custom GUI Framework", 24, GB_BLACK),
            
            Button(cx - 100, 650, 200, 50, "BACK", lambda: self.change_state("MENU"), GB_DARK, style="retro")
        ]

    def set_music_vol(self, val):
        SETTINGS.set("music_volume", val)
        SETTINGS.save()

    def set_sfx_vol(self, val):
        SETTINGS.set("sfx_volume", val)
        SETTINGS.save()

    def cycle_theme(self):
        themes = list(Theme.THEMES.keys())
        curr = SETTINGS.get("theme")
        try:
            idx = themes.index(curr)
            next_t = themes[(idx + 1) % len(themes)]
        except:
            next_t = "NEON"
        SETTINGS.set("theme", next_t)
        self.theme = Theme.get_current()
        SETTINGS.save()

    def change_state(self, new_state):
        self.state = new_state
        AUDIO.playing = (new_state == "PLAYING" and not self.ai_mode)

    def start_game(self, ai):
        self.ai_mode = ai
        self.board = Board(GRID_WIDTH, GRID_HEIGHT)
        self.bag = []
        self.curr_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.hold_piece = None
        self.can_hold = True
        self.score = 0
        self.lines = 0
        # NES Start Level is typically 0, going up to 29
        self.level = 0 
        self.drop_timer = 0
        self.frame_counter = 0
        self.change_state("PLAYING")
        AUDIO.playing = True

    def new_piece(self):
        if not self.bag:
            self.bag = list(range(7))
            random.shuffle(self.bag)
        return Tetromino(self.bag.pop(), GRID_WIDTH // 2 - 2, 0)

    def get_gravity_speed(self):
        # Return frames per drop for current level
        # Cap at level 29 speed
        lvl = min(self.level, 29)
        return NES_GRAVITY.get(lvl, 1)

    def handle_input(self):
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                self.quit_game()
            
            # UI Handling
            ui_list = []
            if self.state == "MENU": ui_list = self.main_menu_ui
            elif self.state == "SETTINGS": ui_list = self.settings_ui
            elif self.state == "HOW_TO_PLAY": ui_list = self.how_to_play_ui
            elif self.state == "CREDITS": ui_list = self.credits_ui
            elif self.state == "ABOUT": ui_list = self.about_ui
            
            for widget in ui_list:
                widget.handle_event(e)
            
            # Escape key handling
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                if self.state in ["SETTINGS", "HOW_TO_PLAY", "CREDITS", "ABOUT"]:
                    self.change_state("MENU")
                elif self.state == "PLAYING":
                    self.change_state("MENU")

            # Discrete Game Inputs (Rotation, Hold, Hard Drop (Disabled for NES authenticity))
            if self.state == "PLAYING" and not self.ai_mode:
                if e.type == pygame.KEYDOWN:
                    keys = SETTINGS.get("controls")
                    if e.key == keys["hold"]:
                        self.hold()
                    elif e.key == keys["rotate_cw"]:
                        self.rotate(True)
                    elif e.key == keys["rotate_ccw"]:
                        self.rotate(False)
                    # Hard drop removed for NES authenticity
                    # elif e.key == keys["hard_drop"]:
                    #     self.hard_drop()
                
                # DAS State Reset on Key Up
                if e.type == pygame.KEYUP:
                    keys = SETTINGS.get("controls")
                    if e.key == keys["left"] and self.das_direction == -1:
                        self.das_direction = 0
                    elif e.key == keys["right"] and self.das_direction == 1:
                        self.das_direction = 0

    def handle_continuous_input(self):
        """Handles DAS and Soft Drop."""
        if self.state != "PLAYING" or self.ai_mode: return

        keys = pygame.key.get_pressed()
        ctrls = SETTINGS.get("controls")

        # DAS Logic (Horizontal Movement)
        direction = 0
        if keys[ctrls["left"]]: direction = -1
        elif keys[ctrls["right"]]: direction = 1
        
        if direction != 0:
            if direction != self.das_direction:
                # First press, move immediately and reset timer
                self.das_direction = direction
                self.das_counter = 0
                self.move(direction, 0)
            else:
                # Holding direction
                self.das_counter += 1
                # Check for DAS charge (16 frames)
                if self.das_counter >= 16:
                    # After initial charge, move every 6 frames
                    if (self.das_counter - 16) % 6 == 0:
                        self.move(direction, 0)
        else:
            self.das_direction = 0
            self.das_counter = 0

        # Soft Drop (1/2 G - 1 cell every 2 frames)
        if keys[ctrls["soft_drop"]]:
            if self.frame_counter % 2 == 0:
                if self.move(0, 1):
                    self.score += 1 # NES gives 1 point per frame of soft drop? Usually per cell.
                    # Reset gravity timer to prevent double drops
                    self.drop_timer = 0

    def hold(self):
        if not self.can_hold: return
        
        if self.hold_piece is None:
            self.hold_piece = self.curr_piece.shape_idx
            self.curr_piece = self.next_piece
            self.next_piece = self.new_piece()
        else:
            self.hold_piece, self.curr_piece.shape_idx = self.curr_piece.shape_idx, self.hold_piece
            self.curr_piece = Tetromino(self.curr_piece.shape_idx, GRID_WIDTH // 2 - 2, 0)
            
        self.can_hold = False
        AUDIO.play_sfx('move')

    def rotate(self, clockwise):
        # SRS Logic
        old_shape = self.curr_piece.shape
        new_shape = self.curr_piece.get_rotated(clockwise)
        
        if not self.board.check_collision(self.curr_piece, shape=new_shape):
            self.curr_piece.shape = new_shape
            self.curr_piece.rotation = (self.curr_piece.rotation + (1 if clockwise else -1)) % 4
            AUDIO.play_sfx('rotate')
            return

        old_rot = self.curr_piece.rotation
        new_rot = (old_rot + (1 if clockwise else -1)) % 4
        
        type_table = WALL_KICKS_I if self.curr_piece.shape_idx == 0 else WALL_KICKS_JLSTZ
        kicks = type_table.get((old_rot, new_rot), [])
        
        for kx, ky in kicks:
            if not self.board.check_collision(self.curr_piece, kx, -ky, shape=new_shape):
                self.curr_piece.x += kx
                self.curr_piece.y -= ky
                self.curr_piece.shape = new_shape
                self.curr_piece.rotation = new_rot
                AUDIO.play_sfx('rotate')
                return

    def move(self, dx, dy):
        if not self.board.check_collision(self.curr_piece, dx, dy):
            self.curr_piece.x += dx
            self.curr_piece.y += dy
            # SFX for move is usually silent or subtle in NES, but we'll keep for feedback
            if dx != 0: AUDIO.play_sfx('move')
            return True
        return False

    def hard_drop(self):
        # Disabled for NES authenticity, but kept method if needed later
        pass

    def lock(self):
        self.board.lock(self.curr_piece)
        
        # Check T-Spin (Modern bonus, kept for engine richness)
        t_spin = self.board.is_tspin(self.curr_piece)
        
        lines = self.board.clear_lines()
        
        # Scoring (Classic NES Style)
        # 40 * (n + 1)	100 * (n + 1)	300 * (n + 1)	1200 * (n + 1)
        if lines > 0:
            self.lines += lines
            self.combo += 1
            
            base_scores = {1: 40, 2: 100, 3: 300, 4: 1200}
            base = base_scores.get(lines, 0)
            
            # Add score
            self.score += base * (self.level + 1)
            
            # Leveling (NES: roughly every 10 lines, start level logic simplified here)
            if self.lines >= (self.level + 1) * 10:
                self.level += 1
            
            # Effects
            cy = self.curr_piece.y * CELL_SIZE + GRID_OFFSET_Y
            cx = self.curr_piece.x * CELL_SIZE + GRID_OFFSET_X
            PARTICLES.spawn(cx, cy, WHITE, 20)
            
            if lines >= 4: AUDIO.play_sfx('tetris')
            else: AUDIO.play_sfx('clear')
        else:
            self.combo = 0
        
        # Next Piece
        self.curr_piece = self.next_piece
        self.next_piece = self.new_piece()
        self.can_hold = True
        
        if self.board.check_collision(self.curr_piece):
            self.change_state("GAMEOVER")
            AUDIO.play_sfx('gameover')
            SETTINGS.add_score(int(self.score))

    def update_ai(self):
        if not self.ai_mode or self.state != "PLAYING": return
        
        speed = SETTINGS.get("ai_speed")
        self.ai_timer += 1/FPS
        if self.ai_timer < speed: return
        self.ai_timer = 0
        
        move = self.bot.get_best_move(self.curr_piece)
        if move:
            rot, x = move
            current_rot = self.curr_piece.rotation
            diff = (rot - current_rot) % 4
            for _ in range(diff):
                self.rotate(True)
            
            while self.curr_piece.x < x:
                if not self.move(1, 0): break
            while self.curr_piece.x > x:
                if not self.move(-1, 0): break
            
            # AI uses hard drop for speed
            # Use manual drop simulation since hard_drop is disabled
            while self.move(0, 1): pass
            self.lock()
        else:
            while self.move(0, 1): pass
            self.lock()

    def update(self):
        # Fixed time step for 60 FPS authenticity
        dt = self.clock.tick(FPS) / 1000.0
        
        self.handle_input()
        
        if self.state == "PLAYING":
            self.frame_counter += 1
            AUDIO.update(dt) # Audio stays on time-based for smooth playback
            PARTICLES.update()
            
            if self.ai_mode:
                self.update_ai()
            else:
                # Handle DAS and Soft Drop
                self.handle_continuous_input()
                
                # Gravity
                frames_per_drop = self.get_gravity_speed()
                self.drop_timer += 1
                
                if self.drop_timer >= frames_per_drop:
                    if not self.move(0, 1):
                        self.lock()
                    self.drop_timer = 0
        else:
            # Update subsystems even in menu
            AUDIO.update(dt)
            PARTICLES.update()
        
        self.draw()

    def draw_cell(self, x, y, color):
        rect = (x, y, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(self.screen, color, rect)
        light = tuple(min(c+50, 255) for c in color)
        dark = tuple(max(c-50, 0) for c in color)
        pygame.draw.rect(self.screen, light, (x, y, CELL_SIZE, 4))
        pygame.draw.rect(self.screen, light, (x, y, 4, CELL_SIZE))
        pygame.draw.rect(self.screen, dark, (x, y+CELL_SIZE-4, CELL_SIZE, 4))
        pygame.draw.rect(self.screen, dark, (x+CELL_SIZE-4, y, 4, CELL_SIZE))

    def draw(self):
        if self.state == "MENU":
            # Retro Gameboy Background
            self.screen.fill(GB_WHITE)
            
            # Scanlines effect for retro feel
            for y in range(0, SCREEN_HEIGHT, 4):
                pygame.draw.line(self.screen, (140, 170, 15), (0, y), (SCREEN_WIDTH, y))
                
            for w in self.main_menu_ui: w.draw(self.screen)
            
        elif self.state == "SETTINGS":
            self.screen.fill(self.theme["bg"])
            for w in self.settings_ui: w.draw(self.screen)
            
        elif self.state in ["HOW_TO_PLAY", "CREDITS", "ABOUT"]:
            self.screen.fill(GB_WHITE)
            # Scanlines
            for y in range(0, SCREEN_HEIGHT, 4):
                pygame.draw.line(self.screen, (140, 170, 15), (0, y), (SCREEN_WIDTH, y))
            
            ui_list = []
            if self.state == "HOW_TO_PLAY": ui_list = self.how_to_play_ui
            elif self.state == "CREDITS": ui_list = self.credits_ui
            elif self.state == "ABOUT": ui_list = self.about_ui
            
            for w in ui_list: w.draw(self.screen)
            
        elif self.state in ["PLAYING", "GAMEOVER"]:
            self.screen.fill(self.theme["bg"])
            
            # Draw Background Grid
            for i in range(0, SCREEN_WIDTH, 40):
                pygame.draw.line(self.screen, (30,30,40), (i,0), (i,SCREEN_HEIGHT))
            for i in range(0, SCREEN_HEIGHT, 40):
                pygame.draw.line(self.screen, (30,30,40), (0,i), (SCREEN_WIDTH,i))
                
            # Sidebar
            sx = GRID_OFFSET_X + GRID_WIDTH * CELL_SIZE + 20
            pygame.draw.rect(self.screen, self.theme["grid"], (sx, GRID_OFFSET_Y, SIDEBAR_WIDTH, 500), border_radius=10)
            
            # Text info
            font = pygame.font.Font(None, 24)
            lbls = [
                f"SCORE: {int(self.score)}",
                f"LEVEL: {self.level}",
                f"LINES: {self.lines}"
            ]
            for i, l in enumerate(lbls):
                t = font.render(l, True, self.theme["text"])
                self.screen.blit(t, (sx+20, GRID_OFFSET_Y + 20 + i*40))
            
            # Next Piece
            t = font.render("NEXT", True, self.theme["text"])
            self.screen.blit(t, (sx+20, GRID_OFFSET_Y + 150))
            if self.next_piece:
                col = self.theme["colors"][self.next_piece.color_idx]
                for r, row in enumerate(self.next_piece.shape):
                    for c, val in enumerate(row):
                        if val:
                            self.draw_cell(sx+50+c*CELL_SIZE, GRID_OFFSET_Y+200+r*CELL_SIZE, col)

            # Hold Piece
            hx = GRID_OFFSET_X - HOLD_WIDTH - 20
            pygame.draw.rect(self.screen, self.theme["grid"], (hx, GRID_OFFSET_Y, HOLD_WIDTH, 200), border_radius=10)
            t = font.render("HOLD", True, self.theme["text"])
            self.screen.blit(t, (hx+20, GRID_OFFSET_Y+20))
            if self.hold_piece is not None:
                shape = SHAPES[self.hold_piece]
                col = self.theme["colors"][self.hold_piece]
                for r, row in enumerate(shape):
                    for c, val in enumerate(row):
                        if val:
                             self.draw_cell(hx+20+c*CELL_SIZE, GRID_OFFSET_Y+60+r*CELL_SIZE, col)

            # Game Board Frame
            pygame.draw.rect(self.screen, self.theme["grid"], (GRID_OFFSET_X-5, GRID_OFFSET_Y-5, GRID_WIDTH*CELL_SIZE+10, GRID_HEIGHT*CELL_SIZE+10), 5)
            pygame.draw.rect(self.screen, BLACK, (GRID_OFFSET_X, GRID_OFFSET_Y, GRID_WIDTH*CELL_SIZE, GRID_HEIGHT*CELL_SIZE))

            # Board Content
            for y in range(GRID_HEIGHT):
                for x in range(GRID_WIDTH):
                    val = self.board.grid[y][x]
                    if val != 0:
                        self.draw_cell(GRID_OFFSET_X + x*CELL_SIZE, GRID_OFFSET_Y + y*CELL_SIZE, val)

            # Ghost Piece
            if self.curr_piece:
                gy = self.curr_piece.y
                while not self.board.check_collision(self.curr_piece, 0, gy - self.curr_piece.y + 1):
                    gy += 1
                
                for x, y in self.curr_piece.get_blocks():
                    # Shift y to ghost y
                    y = y - self.curr_piece.y + gy
                    pygame.draw.rect(self.screen, (50,50,50), (GRID_OFFSET_X + x*CELL_SIZE, GRID_OFFSET_Y + y*CELL_SIZE, CELL_SIZE, CELL_SIZE), 2)

            # Active Piece
            if self.curr_piece:
                col = self.theme["colors"][self.curr_piece.color_idx]
                for x, y in self.curr_piece.get_blocks():
                    self.draw_cell(GRID_OFFSET_X + x*CELL_SIZE, GRID_OFFSET_Y + y*CELL_SIZE, col)

            PARTICLES.draw(self.screen)

            if self.state == "GAMEOVER":
                s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                s.fill((0,0,0,180))
                self.screen.blit(s, (0,0))
                f = pygame.font.Font(None, 80)
                t = f.render("GAME OVER", True, RED)
                r = t.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
                self.screen.blit(t, r)
                
                f2 = pygame.font.Font(None, 30)
                t2 = f2.render("Press SPACE to Restart", True, WHITE)
                r2 = t2.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 80))
                self.screen.blit(t2, r2)
                
                keys = pygame.key.get_pressed()
                if keys[pygame.K_SPACE]:
                    self.start_game(self.ai_mode)
                elif keys[pygame.K_ESCAPE]:
                    self.change_state("MENU")

        pygame.display.flip()

    def quit_game(self):
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    while True:
        game.update()
