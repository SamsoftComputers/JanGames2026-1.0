#!/usr/bin/env python3
"""
SUPER MARIO 4K - A Complete SMB1-Style Platformer
Single-file Python implementation using Pygame
With authentic Mario OST music synthesis and proper pipe rendering
"""

import pygame
import random
import math
import sys
import array

# Initialize Pygame
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 32
FPS = 60
GRAVITY = 0.8
MAX_FALL_SPEED = 15

# Colors (SMB1 Palette)
SKY_BLUE = (107, 140, 255)
GROUND_BROWN = (139, 69, 19)
BRICK_RED = (200, 76, 12)
BRICK_DARK = (150, 50, 0)
QUESTION_YELLOW = (255, 200, 0)
QUESTION_DARK = (200, 150, 0)
PIPE_GREEN = (0, 168, 0)
PIPE_LIGHT = (0, 228, 0)
PIPE_DARK = (0, 108, 0)
PIPE_SHADOW = (0, 68, 0)
MARIO_RED = (255, 0, 0)
MARIO_SKIN = (255, 200, 150)
GOOMBA_BROWN = (165, 82, 41)
KOOPA_GREEN = (0, 200, 0)
COIN_GOLD = (255, 215, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
CLOUD_WHITE = (255, 255, 255)
BUSH_GREEN = (34, 139, 34)
HILL_GREEN = (50, 180, 50)

# Game States
STATE_MENU = 0
STATE_PLAYING = 1
STATE_GAMEOVER = 2
STATE_WIN = 3
STATE_PAUSED = 4

# =============================================================================
# MARIO OST MUSIC ENGINE - Authentic NES-style synthesis
# =============================================================================

SAMPLE_RATE = 44100

# Note frequencies (A4 = 440Hz standard tuning)
NOTE_FREQS = {
    'C3': 130.81, 'D3': 146.83, 'E3': 164.81, 'F3': 174.61, 'G3': 196.00, 'A3': 220.00, 'B3': 246.94,
    'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'F4': 349.23, 'G4': 392.00, 'A4': 440.00, 'B4': 493.88,
    'C5': 523.25, 'D5': 587.33, 'E5': 659.25, 'F5': 698.46, 'G5': 783.99, 'A5': 880.00, 'B5': 987.77,
    'C6': 1046.50, 'D6': 1174.66, 'E6': 1318.51, 'F6': 1396.91, 'G6': 1567.98,
    'Db3': 138.59, 'Eb3': 155.56, 'Gb3': 185.00, 'Ab3': 207.65, 'Bb3': 233.08,
    'Db4': 277.18, 'Eb4': 311.13, 'Gb4': 369.99, 'Ab4': 415.30, 'Bb4': 466.16,
    'Db5': 554.37, 'Eb5': 622.25, 'Gb5': 739.99, 'Ab5': 830.61, 'Bb5': 932.33,
    'Db6': 1108.73, 'Eb6': 1244.51,
    'R': 0  # Rest
}

def generate_square_wave(frequency, duration_ms, duty_cycle=0.5, volume=0.15):
    """Generate NES-style square wave"""
    if frequency == 0:
        n_samples = int(SAMPLE_RATE * duration_ms / 1000)
        return [0] * n_samples

    n_samples = int(SAMPLE_RATE * duration_ms / 1000)
    samples = []
    period = SAMPLE_RATE / frequency

    for i in range(n_samples):
        phase = (i % period) / period
        val = 1.0 if phase < duty_cycle else -1.0

        # Envelope
        env = 1.0
        attack = int(n_samples * 0.02)
        release = int(n_samples * 0.15)
        if i < attack:
            env = i / attack
        elif i > n_samples - release:
            env = (n_samples - i) / release

        samples.append(int(32767 * volume * val * env))

    return samples

def generate_triangle_wave(frequency, duration_ms, volume=0.2):
    """Generate NES-style triangle wave for bass"""
    if frequency == 0:
        n_samples = int(SAMPLE_RATE * duration_ms / 1000)
        return [0] * n_samples

    n_samples = int(SAMPLE_RATE * duration_ms / 1000)
    samples = []
    period = SAMPLE_RATE / frequency

    for i in range(n_samples):
        phase = (i % period) / period
        if phase < 0.5:
            val = 4 * phase - 1
        else:
            val = 3 - 4 * phase

        env = 1.0
        release = int(n_samples * 0.1)
        if i > n_samples - release:
            env = (n_samples - i) / release

        samples.append(int(32767 * volume * val * env))

    return samples

def generate_noise(duration_ms, volume=0.1):
    """Generate NES-style noise for percussion"""
    n_samples = int(SAMPLE_RATE * duration_ms / 1000)
    samples = []

    lfsr = 1
    for i in range(n_samples):
        bit = ((lfsr >> 0) ^ (lfsr >> 1)) & 1
        lfsr = (lfsr >> 1) | (bit << 14)
        val = 1.0 if (lfsr & 1) else -1.0

        env = 1.0
        decay = n_samples * 0.3
        if i < decay:
            env = 1.0 - (i / decay) * 0.8
        else:
            env = 0.2 * (1.0 - (i - decay) / (n_samples - decay))

        samples.append(int(32767 * volume * val * env))

    return samples

def mix_samples(*sample_lists):
    """Mix multiple sample lists together"""
    max_len = max(len(s) for s in sample_lists)
    mixed = [0] * max_len

    for samples in sample_lists:
        for i, s in enumerate(samples):
            mixed[i] += s

    # Normalize to prevent clipping
    max_val = max(abs(s) for s in mixed) if mixed else 1
    if max_val > 32767:
        scale = 32767 / max_val
        mixed = [int(s * scale) for s in mixed]

    return mixed

def samples_to_sound(samples):
    """Convert sample list to pygame Sound object"""
    arr = array.array('h', samples)
    sound = pygame.mixer.Sound(buffer=arr.tobytes())
    return sound

# =============================================================================
# LEVEL-SPECIFIC OST THEMES
# =============================================================================

# SMB1 Overworld Theme (World 1-1, 1-3, etc.) - Full loop
OVERWORLD_MELODY = [
    # Intro phrase
    ('E5', 125), ('E5', 125), ('R', 125), ('E5', 125), ('R', 125), ('C5', 125), ('E5', 250),
    ('G5', 250), ('R', 250), ('G4', 250), ('R', 250),
    # First section
    ('C5', 250), ('R', 125), ('G4', 250), ('R', 125), ('E4', 250),
    ('R', 125), ('A4', 250), ('B4', 250), ('Bb4', 125), ('A4', 250),
    # Bridge
    ('G4', 166), ('E5', 166), ('G5', 166), ('A5', 250), ('F5', 125), ('G5', 125),
    ('R', 125), ('E5', 250), ('C5', 125), ('D5', 125), ('B4', 250), ('R', 250),
    # Second section (repeat with variation)
    ('C5', 250), ('R', 125), ('G4', 250), ('R', 125), ('E4', 250),
    ('R', 125), ('A4', 250), ('B4', 250), ('Bb4', 125), ('A4', 250),
    # Bridge repeat
    ('G4', 166), ('E5', 166), ('G5', 166), ('A5', 250), ('F5', 125), ('G5', 125),
    ('R', 125), ('E5', 250), ('C5', 125), ('D5', 125), ('B4', 250), ('R', 250),
    # End phrase for clean loop
    ('R', 500),
]

OVERWORLD_BASS = [
    # Intro phrase
    ('D3', 125), ('D3', 125), ('R', 125), ('D3', 125), ('R', 125), ('D3', 125), ('D3', 250),
    ('G3', 250), ('R', 250), ('G3', 250), ('R', 250),
    # First section
    ('G3', 250), ('R', 125), ('E3', 250), ('R', 125), ('C3', 250),
    ('R', 125), ('F3', 250), ('G3', 250), ('Gb3', 125), ('F3', 250),
    # Bridge
    ('E3', 166), ('C4', 166), ('E4', 166), ('F4', 250), ('D4', 125), ('E4', 125),
    ('R', 125), ('C4', 250), ('A3', 125), ('B3', 125), ('G3', 250), ('R', 250),
    # Second section
    ('G3', 250), ('R', 125), ('E3', 250), ('R', 125), ('C3', 250),
    ('R', 125), ('F3', 250), ('G3', 250), ('Gb3', 125), ('F3', 250),
    # Bridge repeat
    ('E3', 166), ('C4', 166), ('E4', 166), ('F4', 250), ('D4', 125), ('E4', 125),
    ('R', 125), ('C4', 250), ('A3', 125), ('B3', 125), ('G3', 250), ('R', 250),
    # End phrase for clean loop
    ('R', 500),
]

# Underground Theme (World 1-2, etc.)
UNDERGROUND_MELODY = [
    ('C4', 150), ('C5', 150), ('A4', 150), ('A5', 150), ('Ab4', 150), ('Ab5', 150), ('R', 150),
    ('Bb4', 150), ('Bb5', 150), ('R', 300),
    ('C4', 150), ('C5', 150), ('A4', 150), ('A5', 150), ('Ab4', 150), ('Ab5', 150), ('R', 150),
    ('Bb4', 150), ('Bb5', 150), ('R', 300),
    ('Eb4', 150), ('Eb5', 150), ('D4', 150), ('D5', 150), ('Db4', 150), ('Db5', 150), ('R', 150),
    ('C4', 150), ('C5', 150), ('R', 300),
    ('Eb4', 150), ('Eb5', 150), ('D4', 150), ('D5', 150), ('Db4', 150), ('Db5', 150), ('R', 150),
    ('C4', 150), ('C5', 150), ('R', 300),
    ('R', 400),
]

UNDERGROUND_BASS = [
    ('C3', 150), ('G3', 150), ('C3', 150), ('G3', 150), ('Ab3', 150), ('Eb3', 150), ('R', 150),
    ('Bb3', 150), ('F3', 150), ('R', 300),
    ('C3', 150), ('G3', 150), ('C3', 150), ('G3', 150), ('Ab3', 150), ('Eb3', 150), ('R', 150),
    ('Bb3', 150), ('F3', 150), ('R', 300),
    ('Eb3', 150), ('Bb3', 150), ('D3', 150), ('A3', 150), ('Db3', 150), ('Ab3', 150), ('R', 150),
    ('C3', 150), ('G3', 150), ('R', 300),
    ('Eb3', 150), ('Bb3', 150), ('D3', 150), ('A3', 150), ('Db3', 150), ('Ab3', 150), ('R', 150),
    ('C3', 150), ('G3', 150), ('R', 300),
    ('R', 400),
]

# Underwater Theme (World 2-2, etc.)
UNDERWATER_MELODY = [
    ('C5', 300), ('E5', 300), ('G5', 300), ('E5', 300),
    ('C5', 300), ('G4', 300), ('R', 300), ('G4', 300),
    ('Ab4', 300), ('C5', 300), ('Eb5', 300), ('C5', 300),
    ('Ab4', 300), ('Eb4', 300), ('R', 300), ('Eb4', 300),
    ('Bb4', 300), ('D5', 300), ('F5', 300), ('D5', 300),
    ('Bb4', 300), ('F4', 300), ('R', 300), ('F4', 300),
    ('C5', 300), ('E5', 300), ('G5', 600),
    ('R', 600),
]

UNDERWATER_BASS = [
    ('C3', 600), ('R', 300), ('G3', 300),
    ('C3', 600), ('R', 300), ('E3', 300),
    ('Ab3', 600), ('R', 300), ('Eb3', 300),
    ('Ab3', 600), ('R', 300), ('C3', 300),
    ('Bb3', 600), ('R', 300), ('F3', 300),
    ('Bb3', 600), ('R', 300), ('D3', 300),
    ('C3', 600), ('G3', 600),
    ('R', 600),
]

# Castle Theme (World 1-4, etc.)
CASTLE_MELODY = [
    ('G4', 150), ('Gb4', 150), ('F4', 150), ('Eb4', 200), ('R', 100),
    ('E4', 150), ('Eb4', 150), ('D4', 150), ('Db4', 200), ('R', 100),
    ('C4', 150), ('Ab4', 300), ('R', 100), ('G4', 150), ('Gb4', 150),
    ('F4', 150), ('Eb4', 300), ('D4', 300), ('Db4', 300),
    ('C4', 150), ('Db4', 150), ('D4', 150), ('Eb4', 200), ('R', 100),
    ('E4', 150), ('F4', 150), ('Gb4', 150), ('G4', 200), ('R', 100),
    ('Ab4', 300), ('A4', 300), ('Bb4', 300), ('B4', 300),
    ('C5', 600), ('R', 400),
]

CASTLE_BASS = [
    ('C3', 300), ('R', 100), ('G3', 200), ('R', 100), ('C3', 300),
    ('R', 100), ('Ab3', 200), ('R', 100), ('C3', 300), ('R', 100),
    ('G3', 200), ('R', 100), ('C3', 300), ('R', 100), ('F3', 300),
    ('R', 100), ('C3', 300), ('R', 100), ('G3', 200), ('R', 100),
    ('C3', 300), ('R', 100), ('Ab3', 200), ('R', 100), ('C3', 300),
    ('R', 100), ('G3', 200), ('R', 100), ('C3', 300), ('R', 100),
    ('Eb3', 300), ('E3', 300), ('F3', 300), ('Gb3', 300),
    ('G3', 600), ('R', 400),
]

# Star Power / Invincibility Theme
STARMAN_MELODY = [
    ('C5', 100), ('D5', 100), ('E5', 100), ('F5', 100), ('G5', 100), ('A5', 100), ('B5', 100), ('C6', 200),
    ('B5', 100), ('A5', 100), ('G5', 100), ('F5', 100), ('E5', 100), ('D5', 100), ('C5', 200),
    ('E5', 100), ('G5', 100), ('C6', 200), ('G5', 100), ('E5', 100),
    ('F5', 100), ('A5', 100), ('D6', 200), ('A5', 100), ('F5', 100),
    ('G5', 100), ('B5', 100), ('E6', 200), ('B5', 100), ('G5', 100),
    ('C6', 400), ('R', 200),
]

STARMAN_BASS = [
    ('C3', 100), ('E3', 100), ('G3', 100), ('C4', 100), ('G3', 100), ('E3', 100), ('C3', 100), ('E3', 200),
    ('G3', 100), ('C4', 100), ('G3', 100), ('E3', 100), ('C3', 100), ('E3', 100), ('G3', 200),
    ('C3', 100), ('E3', 100), ('G3', 200), ('E3', 100), ('C3', 100),
    ('D3', 100), ('F3', 100), ('A3', 200), ('F3', 100), ('D3', 100),
    ('E3', 100), ('G3', 100), ('B3', 200), ('G3', 100), ('E3', 100),
    ('C3', 400), ('R', 200),
]

# Theme mapping for levels (world-stage format)
LEVEL_THEMES = {
    '1-1': 'overworld',
    '1-2': 'underground',
    '1-3': 'overworld',
    '1-4': 'castle',
    '2-1': 'overworld',
    '2-2': 'underwater',
    '2-3': 'overworld',
    '2-4': 'castle',
    '3-1': 'overworld',
    '3-2': 'overworld',
    '3-3': 'overworld',
    '3-4': 'castle',
    '4-1': 'overworld',
    '4-2': 'underground',
    '4-3': 'overworld',
    '4-4': 'castle',
    '5-1': 'overworld',
    '5-2': 'overworld',
    '5-3': 'overworld',
    '5-4': 'castle',
    '6-1': 'overworld',
    '6-2': 'underwater',
    '6-3': 'overworld',
    '6-4': 'castle',
    '7-1': 'overworld',
    '7-2': 'overworld',
    '7-3': 'overworld',
    '7-4': 'castle',
    '8-1': 'overworld',
    '8-2': 'overworld',
    '8-3': 'overworld',
    '8-4': 'castle',
}

# Level Complete Fanfare
FANFARE_MELODY = [
    ('G4', 100), ('C5', 100), ('E5', 100), ('G5', 100), ('C6', 100), ('E6', 100),
    ('G6', 300), ('E6', 300),
    ('Ab4', 100), ('C5', 100), ('Eb5', 100), ('Ab5', 100), ('C6', 100), ('Eb6', 100),
    ('Ab6', 300), ('Eb6', 300),
    ('Bb4', 100), ('D5', 100), ('F5', 100), ('Bb5', 100), ('D6', 100), ('F6', 100),
    ('Bb6', 500),
]

# Death jingle
DEATH_MELODY = [
    ('B4', 200), ('F5', 200), ('R', 100), ('F5', 200), ('F5', 150), ('E5', 150),
    ('D5', 150), ('C5', 400), ('E4', 200), ('R', 100), ('E4', 200), ('C4', 400),
]

# Coin sound
COIN_NOTES = [('B5', 80), ('E6', 200)]

# Jump sound
JUMP_NOTES = [('G4', 30), ('A4', 30), ('B4', 30), ('C5', 30), ('D5', 30)]

# Power-up sound
POWERUP_NOTES = [
    ('G4', 60), ('B4', 60), ('D5', 60), ('G5', 60), ('B5', 60),
    ('A4', 60), ('C5', 60), ('E5', 60), ('A5', 60), ('C6', 60),
    ('B4', 60), ('D5', 60), ('G5', 60), ('B5', 60), ('D6', 100),
]

# Stomp sound
STOMP_NOTES = [('C4', 50), ('G3', 100)]

# 1-UP sound
ONEUP_NOTES = [
    ('E5', 80), ('G5', 80), ('E6', 80), ('C6', 80), ('D6', 80), ('G6', 200),
]

# Bump sound
BUMP_NOTES = [('C3', 60), ('C3', 60)]

# Break block
BREAK_NOTES = [('Bb3', 40), ('G3', 40), ('E3', 40), ('C3', 80)]

def generate_melody_sound(notes, wave_type='square', duty=0.5):
    """Generate sound from note sequence"""
    all_samples = []
    for note, duration in notes:
        freq = NOTE_FREQS.get(note, 0)
        if wave_type == 'square':
            samples = generate_square_wave(freq, duration, duty)
        elif wave_type == 'triangle':
            samples = generate_triangle_wave(freq, duration)
        else:
            samples = generate_square_wave(freq, duration)
        all_samples.extend(samples)
    return samples_to_sound(all_samples)

def generate_theme_track(melody_notes, bass_notes, melody_volume=0.12, bass_volume=0.15):
    """Generate a theme track from melody and bass note sequences"""
    melody_samples = []
    for note, duration in melody_notes:
        freq = NOTE_FREQS.get(note, 0)
        melody_samples.extend(generate_square_wave(freq, duration, 0.5, melody_volume))

    bass_samples = []
    for note, duration in bass_notes:
        freq = NOTE_FREQS.get(note, 0)
        bass_samples.extend(generate_triangle_wave(freq, duration, bass_volume))

    # Pad to same length
    max_len = max(len(melody_samples), len(bass_samples))
    melody_samples.extend([0] * (max_len - len(melody_samples)))
    bass_samples.extend([0] * (max_len - len(bass_samples)))

    # Mix
    mixed = mix_samples(melody_samples, bass_samples)

    # Add fade out at the end for smooth looping (last 500 samples)
    fade_samples = min(500, len(mixed) // 10)
    for i in range(fade_samples):
        fade_factor = 1.0 - (i / fade_samples)
        mixed[-(i + 1)] = int(mixed[-(i + 1)] * fade_factor)

    return samples_to_sound(mixed)

def generate_music_loop():
    """Generate the main overworld theme as a looping track (legacy support)"""
    return generate_theme_track(OVERWORLD_MELODY, OVERWORLD_BASS)


class MusicManager:
    """Manages level-specific music playback with proper looping"""
    def __init__(self):
        self.current_theme = None
        self.current_sound = None
        self.themes = {}
        self.channel = None
        self.enabled = True

    def initialize(self):
        """Generate all theme tracks"""
        try:
            self.themes['overworld'] = generate_theme_track(OVERWORLD_MELODY, OVERWORLD_BASS)
            self.themes['underground'] = generate_theme_track(UNDERGROUND_MELODY, UNDERGROUND_BASS, 0.10, 0.18)
            self.themes['underwater'] = generate_theme_track(UNDERWATER_MELODY, UNDERWATER_BASS, 0.14, 0.12)
            self.themes['castle'] = generate_theme_track(CASTLE_MELODY, CASTLE_BASS, 0.11, 0.16)
            self.themes['starman'] = generate_theme_track(STARMAN_MELODY, STARMAN_BASS, 0.15, 0.12)
            self.channel = pygame.mixer.Channel(0)
            return True
        except Exception as e:
            print(f"Music init warning: {e}")
            self.enabled = False
            return False

    def play_theme(self, theme_name, loops=-1):
        """Play a specific theme by name"""
        if not self.enabled or theme_name not in self.themes:
            return

        # Only restart if different theme
        if self.current_theme == theme_name and self.channel and self.channel.get_busy():
            return

        self.stop()
        self.current_theme = theme_name
        self.current_sound = self.themes[theme_name]
        try:
            self.current_sound.play(loops=loops)
        except Exception:
            pass

    def play_level_theme(self, level_id):
        """Play theme based on level identifier (e.g., '1-1')"""
        theme_name = LEVEL_THEMES.get(level_id, 'overworld')
        self.play_theme(theme_name)

    def stop(self):
        """Stop current music"""
        if self.current_sound:
            try:
                self.current_sound.stop()
            except Exception:
                pass
        self.current_theme = None

    def toggle_mute(self):
        """Toggle music on/off"""
        if self.current_sound:
            if pygame.mixer.get_busy():
                self.stop()
            elif self.current_theme:
                self.play_theme(self.current_theme)

    def is_playing(self):
        """Check if music is currently playing"""
        return pygame.mixer.get_busy()

# Pre-generate sound effects
try:
    SND_JUMP = generate_melody_sound(JUMP_NOTES, 'square', 0.25)
    SND_COIN = generate_melody_sound(COIN_NOTES, 'square', 0.5)
    SND_STOMP = generate_melody_sound(STOMP_NOTES, 'square', 0.25)
    SND_POWERUP = generate_melody_sound(POWERUP_NOTES, 'square', 0.5)
    SND_DEATH = generate_melody_sound(DEATH_MELODY, 'square', 0.5)
    SND_BUMP = generate_melody_sound(BUMP_NOTES, 'triangle')
    SND_BREAK = generate_melody_sound(BREAK_NOTES, 'square', 0.25)
    SND_FLAGPOLE = generate_melody_sound(FANFARE_MELODY, 'square', 0.5)
    SND_ONEUP = generate_melody_sound(ONEUP_NOTES, 'square', 0.5)
    SFX_ENABLED = True
except Exception as e:
    print(f"SFX init warning: {e}")
    SND_JUMP = SND_COIN = SND_STOMP = SND_POWERUP = SND_DEATH = None
    SND_BUMP = SND_BREAK = SND_FLAGPOLE = SND_ONEUP = None
    SFX_ENABLED = False

# Initialize Music Manager (global instance)
MUSIC_MANAGER = MusicManager()
MUSIC_ENABLED = MUSIC_MANAGER.initialize()

def play_sound(sound):
    if sound:
        try:
            sound.play()
        except:
            pass

def start_music(level_id='1-1'):
    """Start music for specific level"""
    if MUSIC_ENABLED:
        MUSIC_MANAGER.play_level_theme(level_id)

def stop_music():
    """Stop current music"""
    if MUSIC_ENABLED:
        MUSIC_MANAGER.stop()

def play_theme(theme_name):
    """Play a specific theme by name"""
    if MUSIC_ENABLED:
        MUSIC_MANAGER.play_theme(theme_name)

# =============================================================================
# SPRITE DRAWING FUNCTIONS
# =============================================================================

def draw_mario(surface, x, y, big=False, facing_right=True, frame=0):
    """Draw Mario sprite"""
    h = 64 if big else 32
    w = 24

    if not facing_right:
        x = x + w

    def px(rx, ry, color):
        rx = rx if facing_right else w - rx - 4
        pygame.draw.rect(surface, color, (x + rx, y + ry, 4, 4))

    # Hat
    for i in range(3, 7):
        px(i*4 - 12, 0, MARIO_RED)

    # Face
    for i in range(2, 7):
        px(i*4 - 8, 4, MARIO_SKIN if i < 5 else MARIO_RED)

    px(8, 8, MARIO_SKIN)
    px(12, 8, MARIO_SKIN)
    px(16, 8, MARIO_SKIN)
    px(4, 8, GOOMBA_BROWN)

    body_y = 12
    if big:
        body_y = 16
        for i in range(2, 5):
            px(i*4, 12, MARIO_RED)

    for i in range(1, 5):
        px(i*4, body_y, MARIO_RED)
        px(i*4, body_y + 4, MARIO_RED)

    if frame % 2 == 0:
        px(0, body_y, MARIO_SKIN)
        px(20, body_y, MARIO_SKIN)
    else:
        px(0, body_y + 4, MARIO_SKIN)
        px(20, body_y + 4, MARIO_SKIN)

    leg_y = body_y + 8
    if big:
        leg_y = body_y + 12
        px(4, body_y + 8, (0, 0, 200))
        px(12, body_y + 8, (0, 0, 200))

    if frame % 4 < 2:
        px(4, leg_y, (0, 0, 200))
        px(12, leg_y, (0, 0, 200))
        px(4, leg_y + 4, GOOMBA_BROWN)
        px(12, leg_y + 4, GOOMBA_BROWN)
    else:
        px(0, leg_y, (0, 0, 200))
        px(16, leg_y, (0, 0, 200))
        px(0, leg_y + 4, GOOMBA_BROWN)
        px(16, leg_y + 4, GOOMBA_BROWN)

def draw_goomba(surface, x, y, frame=0):
    """Draw Goomba enemy"""
    pygame.draw.ellipse(surface, GOOMBA_BROWN, (x + 2, y + 8, 28, 20))
    pygame.draw.ellipse(surface, GOOMBA_BROWN, (x, y, 32, 20))
    pygame.draw.ellipse(surface, WHITE, (x + 6, y + 6, 8, 8))
    pygame.draw.ellipse(surface, WHITE, (x + 18, y + 6, 8, 8))
    pygame.draw.ellipse(surface, BLACK, (x + 8, y + 8, 4, 4))
    pygame.draw.ellipse(surface, BLACK, (x + 20, y + 8, 4, 4))
    if frame % 2 == 0:
        pygame.draw.ellipse(surface, GOOMBA_BROWN, (x, y + 24, 12, 8))
        pygame.draw.ellipse(surface, GOOMBA_BROWN, (x + 20, y + 24, 12, 8))
    else:
        pygame.draw.ellipse(surface, GOOMBA_BROWN, (x + 4, y + 24, 12, 8))
        pygame.draw.ellipse(surface, GOOMBA_BROWN, (x + 16, y + 24, 12, 8))

def draw_koopa(surface, x, y, frame=0, facing_right=True):
    """Draw Koopa Troopa enemy"""
    pygame.draw.ellipse(surface, KOOPA_GREEN, (x + 4, y + 8, 24, 20))
    pygame.draw.ellipse(surface, (255, 255, 200), (x + 8, y + 12, 16, 12))
    hx = x + 20 if facing_right else x - 4
    pygame.draw.ellipse(surface, (255, 220, 150), (hx, y, 16, 16))
    ex = hx + 8 if facing_right else hx + 2
    pygame.draw.circle(surface, BLACK, (ex, y + 6), 2)
    fy = y + 24 + (frame % 2) * 2
    pygame.draw.ellipse(surface, (255, 220, 150), (x + 4, fy, 10, 8))
    pygame.draw.ellipse(surface, (255, 220, 150), (x + 18, fy, 10, 8))

def draw_coin(surface, x, y, frame=0):
    """Draw spinning coin"""
    widths = [12, 8, 4, 8, 12, 8, 4, 8]
    w = widths[frame % 8]
    pygame.draw.ellipse(surface, COIN_GOLD, (x + 10 - w//2, y + 4, w, 24))
    if w > 6:
        pygame.draw.ellipse(surface, (255, 240, 100), (x + 12 - w//4, y + 8, w//2, 16))

def draw_mushroom(surface, x, y):
    """Draw power-up mushroom"""
    pygame.draw.ellipse(surface, MARIO_RED, (x, y, 32, 20))
    pygame.draw.circle(surface, WHITE, (x + 8, y + 8), 4)
    pygame.draw.circle(surface, WHITE, (x + 24, y + 8), 4)
    pygame.draw.circle(surface, WHITE, (x + 16, y + 4), 3)
    pygame.draw.rect(surface, (255, 220, 180), (x + 10, y + 14, 12, 14))
    pygame.draw.circle(surface, BLACK, (x + 12, y + 20), 2)
    pygame.draw.circle(surface, BLACK, (x + 20, y + 20), 2)

def draw_brick(surface, x, y, broken=False):
    """Draw brick block"""
    if broken:
        return
    pygame.draw.rect(surface, BRICK_RED, (x, y, TILE_SIZE, TILE_SIZE))
    pygame.draw.line(surface, BRICK_DARK, (x, y + TILE_SIZE//2), (x + TILE_SIZE, y + TILE_SIZE//2), 2)
    pygame.draw.line(surface, BRICK_DARK, (x + TILE_SIZE//2, y), (x + TILE_SIZE//2, y + TILE_SIZE//2), 2)
    pygame.draw.line(surface, BRICK_DARK, (x + TILE_SIZE//4, y + TILE_SIZE//2), (x + TILE_SIZE//4, y + TILE_SIZE), 2)
    pygame.draw.line(surface, BRICK_DARK, (x + 3*TILE_SIZE//4, y + TILE_SIZE//2), (x + 3*TILE_SIZE//4, y + TILE_SIZE), 2)
    pygame.draw.rect(surface, BRICK_DARK, (x, y, TILE_SIZE, TILE_SIZE), 2)

def draw_question_block(surface, x, y, used=False, frame=0):
    """Draw question block"""
    if used:
        color = (100, 80, 60)
        pygame.draw.rect(surface, color, (x, y, TILE_SIZE, TILE_SIZE))
        pygame.draw.rect(surface, (60, 40, 20), (x, y, TILE_SIZE, TILE_SIZE), 2)
    else:
        bounce = abs(math.sin(frame * 0.1)) * 2
        pygame.draw.rect(surface, QUESTION_YELLOW, (x, y - bounce, TILE_SIZE, TILE_SIZE))
        pygame.draw.rect(surface, QUESTION_DARK, (x, y - bounce, TILE_SIZE, TILE_SIZE), 2)
        font = pygame.font.Font(None, 28)
        text = font.render("?", True, WHITE)
        surface.blit(text, (x + 10, y + 4 - bounce))

def draw_ground(surface, x, y):
    """Draw ground tile"""
    pygame.draw.rect(surface, GROUND_BROWN, (x, y, TILE_SIZE, TILE_SIZE))
    pygame.draw.rect(surface, (100, 50, 10), (x, y, TILE_SIZE, TILE_SIZE), 1)
    for i in range(4):
        px = x + random.Random(x + y + i).randint(4, 28)
        py = y + random.Random(x + y + i * 2).randint(4, 28)
        pygame.draw.circle(surface, (120, 60, 20), (px, py), 2)

def draw_pipe_top(surface, x, y):
    """Draw the top section of a pipe (2 tiles wide with lip)"""
    w = TILE_SIZE * 2
    h = TILE_SIZE

    # Main pipe top body
    pygame.draw.rect(surface, PIPE_GREEN, (x, y, w, h))

    # Lip (overhangs 4 pixels on each side)
    lip_h = 12
    pygame.draw.rect(surface, PIPE_GREEN, (x - 4, y, w + 8, lip_h))

    # Highlights (left side lighter)
    pygame.draw.rect(surface, PIPE_LIGHT, (x - 4, y, 8, lip_h))
    pygame.draw.rect(surface, PIPE_LIGHT, (x, y + lip_h, 8, h - lip_h))

    # Dark edge (right side darker)
    pygame.draw.rect(surface, PIPE_DARK, (x + w - 4, y, 8, lip_h))
    pygame.draw.rect(surface, PIPE_DARK, (x + w - 8, y + lip_h, 8, h - lip_h))

    # Shadow inside top
    pygame.draw.rect(surface, PIPE_SHADOW, (x + 8, y + 2, w - 16, 6))

    # Outlines
    pygame.draw.rect(surface, PIPE_SHADOW, (x - 4, y, w + 8, lip_h), 2)
    pygame.draw.rect(surface, PIPE_SHADOW, (x, y + lip_h, w, h - lip_h), 2)

    # Vertical highlight stripe
    pygame.draw.rect(surface, PIPE_LIGHT, (x + 12, y + lip_h, 6, h - lip_h))

def draw_pipe_body(surface, x, y):
    """Draw a body section of a pipe (2 tiles wide)"""
    w = TILE_SIZE * 2
    h = TILE_SIZE

    # Main body
    pygame.draw.rect(surface, PIPE_GREEN, (x, y, w, h))

    # Highlight left
    pygame.draw.rect(surface, PIPE_LIGHT, (x, y, 8, h))

    # Dark right
    pygame.draw.rect(surface, PIPE_DARK, (x + w - 8, y, 8, h))

    # Outline
    pygame.draw.rect(surface, PIPE_SHADOW, (x, y, w, h), 2)

    # Vertical highlight stripe
    pygame.draw.rect(surface, PIPE_LIGHT, (x + 12, y, 6, h))

def draw_cloud(surface, x, y, size=1):
    """Draw cloud"""
    for i in range(size + 2):
        cx = x + i * 30
        cy = y + (10 if i % 2 == 0 else 0)
        pygame.draw.ellipse(surface, CLOUD_WHITE, (cx, cy, 40, 30))

def draw_bush(surface, x, y, size=1):
    """Draw bush"""
    for i in range(size + 1):
        bx = x + i * 24
        pygame.draw.ellipse(surface, BUSH_GREEN, (bx, y, 32, 24))

def draw_hill(surface, x, y, size=1):
    """Draw background hill"""
    w = 80 + size * 40
    h = 60 + size * 20
    pygame.draw.ellipse(surface, HILL_GREEN, (x, y - h + 20, w, h))

def draw_castle(surface, x, y):
    """Draw castle at end of level"""
    pygame.draw.rect(surface, (150, 150, 150), (x, y, 96, 80))
    pygame.draw.rect(surface, BLACK, (x + 36, y + 48, 24, 32))
    pygame.draw.rect(surface, BLACK, (x + 12, y + 20, 16, 20))
    pygame.draw.rect(surface, BLACK, (x + 68, y + 20, 16, 20))
    for i in range(4):
        pygame.draw.rect(surface, (150, 150, 150), (x + i * 24, y - 16, 20, 20))
    pygame.draw.rect(surface, (150, 150, 150), (x + 32, y - 48, 32, 48))
    pygame.draw.rect(surface, BLACK, (x + 40, y - 36, 16, 16))
    pygame.draw.rect(surface, (100, 100, 100), (x + 46, y - 80, 4, 36))
    pygame.draw.polygon(surface, MARIO_RED, [(x + 50, y - 80), (x + 74, y - 70), (x + 50, y - 60)])

def draw_flagpole(surface, x, y, flag_y=0):
    """Draw end flagpole"""
    pygame.draw.rect(surface, (100, 100, 100), (x + 14, y, 4, 160))
    pygame.draw.circle(surface, (0, 200, 0), (x + 16, y), 8)
    pygame.draw.polygon(surface, (0, 200, 0), [
        (x + 18, y + flag_y),
        (x + 48, y + flag_y + 16),
        (x + 18, y + flag_y + 32)
    ])


# =============================================================================
# GAME CLASSES
# =============================================================================

class Pipe:
    """Represents a complete pipe with proper collision matching SMB1 NES"""
    def __init__(self, x, y, height=2):
        self.x = x
        self.y = y
        self.height = height  # in tiles
        # SMB1 NES: pipes are exactly 2 tiles wide (32 NES pixels = 64 pixels at 2x scale)
        self.width = TILE_SIZE * 2

    def get_rects(self):
        """Return collision rectangles for the pipe - SMB1 accurate"""
        rects = []
        # All sections have the same hitbox size as SMB1: full tile height, 2 tiles wide
        for i in range(self.height):
            rects.append(pygame.Rect(self.x, self.y + i * TILE_SIZE, self.width, TILE_SIZE))
        return rects

    def collides_with(self, rect):
        """Check if rect collides with any part of pipe"""
        for pipe_rect in self.get_rects():
            if rect.colliderect(pipe_rect):
                return True
        return False

    def get_collision_rect(self):
        """Return main bounding box - SMB1 accurate: full pipe dimensions"""
        return pygame.Rect(self.x, self.y, self.width, self.height * TILE_SIZE)

    def draw(self, surface, camera_x):
        sx = self.x - camera_x
        # Draw top
        draw_pipe_top(surface, sx, self.y)
        # Draw body sections
        for i in range(1, self.height):
            draw_pipe_body(surface, sx, self.y + i * TILE_SIZE)


class Entity:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.active = True

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self, level):
        pass

    def draw(self, surface, camera_x):
        pass


class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 24, 32)
        self.big = False
        self.facing_right = True
        self.frame = 0
        self.frame_counter = 0
        self.jump_power = -14
        self.speed = 5
        self.run_speed = 7
        self.invincible = 0
        self.dead = False
        self.win = False
        self.win_timer = 0
        self.flag_slide = False

    def update(self, level, keys):
        if self.dead or self.win:
            if self.dead:
                self.vy += GRAVITY * 0.5
                self.y += self.vy
            elif self.flag_slide:
                self.y += 3
                if self.y > level.ground_y - self.height:
                    self.y = level.ground_y - self.height
                    self.flag_slide = False
                    self.win_timer = 120
            elif self.win_timer > 0:
                self.win_timer -= 1
                self.x += 2
            return

        running = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        current_speed = self.run_speed if running else self.speed

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = -current_speed
            self.facing_right = False
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = current_speed
            self.facing_right = True
        else:
            self.vx *= 0.8
            if abs(self.vx) < 0.5:
                self.vx = 0

        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and self.on_ground:
            self.vy = self.jump_power
            self.on_ground = False
            play_sound(SND_JUMP)

        self.vy += GRAVITY
        if self.vy > MAX_FALL_SPEED:
            self.vy = MAX_FALL_SPEED

        self.x += self.vx
        self.check_horizontal_collisions(level)

        self.y += self.vy
        self.on_ground = False
        self.check_vertical_collisions(level)

        if self.x < 0:
            self.x = 0

        if self.y > SCREEN_HEIGHT:
            self.die()

        if abs(self.vx) > 0.5:
            self.frame_counter += 1
            if self.frame_counter > 5:
                self.frame_counter = 0
                self.frame = (self.frame + 1) % 4
        else:
            self.frame = 0

        if self.invincible > 0:
            self.invincible -= 1

    def check_horizontal_collisions(self, level):
        rect = self.get_rect()

        # Check tiles
        for tile in level.get_nearby_tiles(self.x, self.y):
            if tile.solid and rect.colliderect(tile.get_rect()):
                if self.vx > 0:
                    self.x = tile.x - self.width
                elif self.vx < 0:
                    self.x = tile.x + tile.width
                self.vx = 0
                rect = self.get_rect()  # Refresh rect after position change

        # Check pipes - refresh rect for accurate collision
        rect = self.get_rect()
        for pipe in level.pipes:
            pipe_rect = pipe.get_collision_rect()
            if rect.colliderect(pipe_rect):
                if self.vx > 0:
                    self.x = pipe_rect.left - self.width
                elif self.vx < 0:
                    self.x = pipe_rect.right
                self.vx = 0
                rect = self.get_rect()  # Refresh rect after position change

    def check_vertical_collisions(self, level):
        rect = self.get_rect()

        # Check tiles
        for tile in level.get_nearby_tiles(self.x, self.y):
            if tile.solid and rect.colliderect(tile.get_rect()):
                if self.vy > 0:
                    self.y = tile.y - self.height
                    self.vy = 0
                    self.on_ground = True
                elif self.vy < 0:
                    self.y = tile.y + tile.height
                    self.vy = 0
                    tile.hit_from_below(self, level)
                rect = self.get_rect()  # Refresh rect after position change

        # Check pipes - refresh rect for accurate collision
        rect = self.get_rect()
        for pipe in level.pipes:
            pipe_rect = pipe.get_collision_rect()
            if rect.colliderect(pipe_rect):
                if self.vy > 0:
                    self.y = pipe_rect.top - self.height
                    self.vy = 0
                    self.on_ground = True
                elif self.vy < 0:
                    self.y = pipe_rect.bottom
                    self.vy = 0
                rect = self.get_rect()  # Refresh rect after position change

    def grow(self):
        if not self.big:
            self.big = True
            self.y -= 32
            self.height = 64
            play_sound(SND_POWERUP)

    def shrink(self):
        if self.big:
            self.big = False
            self.height = 32
            self.invincible = 120
            play_sound(SND_DEATH)
        elif self.invincible == 0:
            self.die()

    def die(self):
        if not self.dead:
            self.dead = True
            self.vy = -12
            stop_music()
            play_sound(SND_DEATH)

    def grab_flagpole(self, flagpole_x):
        self.win = True
        self.flag_slide = True
        self.x = flagpole_x
        self.vx = 0
        self.vy = 0
        stop_music()
        play_sound(SND_FLAGPOLE)

    def draw(self, surface, camera_x):
        if self.invincible > 0 and self.invincible % 4 < 2:
            return
        draw_mario(surface, self.x - camera_x, self.y, self.big, self.facing_right, self.frame)


class Enemy(Entity):
    def __init__(self, x, y, enemy_type="goomba"):
        super().__init__(x, y, 32, 32)
        self.enemy_type = enemy_type
        self.vx = -1
        self.frame = 0
        self.frame_counter = 0
        self.squashed = False
        self.squash_timer = 0

    def update(self, level):
        if not self.active:
            return

        if self.squashed:
            self.squash_timer -= 1
            if self.squash_timer <= 0:
                self.active = False
            return

        self.vy += GRAVITY
        if self.vy > MAX_FALL_SPEED:
            self.vy = MAX_FALL_SPEED

        self.x += self.vx
        self.y += self.vy

        rect = self.get_rect()
        for tile in level.get_nearby_tiles(self.x, self.y):
            if tile.solid and rect.colliderect(tile.get_rect()):
                if self.vy > 0:
                    self.y = tile.y - self.height
                    self.vy = 0
                elif self.vx != 0:
                    self.vx = -self.vx

        # Pipe collision
        for pipe in level.pipes:
            if rect.colliderect(pipe.get_collision_rect()):
                self.vx = -self.vx

        if self.y > SCREEN_HEIGHT:
            self.active = False

        self.frame_counter += 1
        if self.frame_counter > 10:
            self.frame_counter = 0
            self.frame = (self.frame + 1) % 2

    def stomp(self):
        self.squashed = True
        self.squash_timer = 30
        play_sound(SND_STOMP)

    def draw(self, surface, camera_x):
        if not self.active:
            return

        sx = self.x - camera_x
        if self.squashed:
            pygame.draw.ellipse(surface, GOOMBA_BROWN, (sx, self.y + 24, 32, 8))
        elif self.enemy_type == "goomba":
            draw_goomba(surface, sx, self.y, self.frame)
        elif self.enemy_type == "koopa":
            draw_koopa(surface, sx, self.y, self.frame, self.vx > 0)


class Coin(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 24, 28)
        self.frame = 0
        self.frame_counter = 0
        self.collected = False
        self.collect_animation = 0

    def update(self, level):
        if self.collected:
            self.collect_animation += 1
            self.y -= 5
            if self.collect_animation > 20:
                self.active = False
            return

        self.frame_counter += 1
        if self.frame_counter > 4:
            self.frame_counter = 0
            self.frame = (self.frame + 1) % 8

    def collect(self):
        if not self.collected:
            self.collected = True
            play_sound(SND_COIN)

    def draw(self, surface, camera_x):
        if not self.active:
            return
        draw_coin(surface, self.x - camera_x, self.y, self.frame)


class Mushroom(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 32, 28)
        self.vx = 2
        self.emerging = True
        self.emerge_y = y
        self.target_y = y - 32

    def update(self, level):
        if not self.active:
            return

        if self.emerging:
            self.y -= 1
            if self.y <= self.target_y:
                self.y = self.target_y
                self.emerging = False
            return

        self.vy += GRAVITY
        if self.vy > MAX_FALL_SPEED:
            self.vy = MAX_FALL_SPEED

        self.x += self.vx
        self.y += self.vy

        rect = self.get_rect()
        for tile in level.get_nearby_tiles(self.x, self.y):
            if tile.solid and rect.colliderect(tile.get_rect()):
                if self.vy > 0:
                    self.y = tile.y - self.height
                    self.vy = 0
                elif self.vx != 0:
                    self.vx = -self.vx

        for pipe in level.pipes:
            if rect.colliderect(pipe.get_collision_rect()):
                if self.vy > 0:
                    self.y = pipe.y - self.height
                    self.vy = 0
                else:
                    self.vx = -self.vx

        if self.y > SCREEN_HEIGHT:
            self.active = False

    def draw(self, surface, camera_x):
        if not self.active:
            return
        draw_mushroom(surface, self.x - camera_x, self.y)


class Tile:
    def __init__(self, x, y, tile_type):
        self.x = x
        self.y = y
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        self.tile_type = tile_type
        self.solid = tile_type in ["ground", "brick", "question", "block"]
        self.used = False
        self.broken = False
        self.frame = 0
        self.content = None
        self.bump_offset = 0

    def get_rect(self):
        return pygame.Rect(self.x, self.y + self.bump_offset, self.width, self.height)

    def hit_from_below(self, player, level):
        if self.tile_type == "question" and not self.used:
            self.used = True
            self.bump_offset = -8
            if self.content == "mushroom":
                mushroom = Mushroom(self.x, self.y)
                level.powerups.append(mushroom)
                play_sound(SND_POWERUP)
            else:
                coin = Coin(self.x + 4, self.y - 32)
                coin.collected = True
                level.coins.append(coin)
                level.score += 100
                play_sound(SND_COIN)

        elif self.tile_type == "brick" and not self.broken:
            if player.big:
                self.broken = True
                self.solid = False
                play_sound(SND_BREAK)
            else:
                self.bump_offset = -4
                play_sound(SND_BUMP)

    def update(self):
        if self.bump_offset < 0:
            self.bump_offset += 2
            if self.bump_offset > 0:
                self.bump_offset = 0
        self.frame += 1

    def draw(self, surface, camera_x):
        sx = self.x - camera_x
        sy = self.y + self.bump_offset

        if self.tile_type == "ground":
            draw_ground(surface, sx, sy)
        elif self.tile_type == "brick" and not self.broken:
            draw_brick(surface, sx, sy)
        elif self.tile_type == "question":
            draw_question_block(surface, sx, sy, self.used, self.frame)
        elif self.tile_type == "block":
            pygame.draw.rect(surface, (100, 80, 60), (sx, sy, TILE_SIZE, TILE_SIZE))
            pygame.draw.rect(surface, (60, 40, 20), (sx, sy, TILE_SIZE, TILE_SIZE), 2)


class Level:
    def __init__(self, level_id='1-1'):
        self.level_id = level_id  # For OST selection (e.g., '1-1', '1-2')
        self.tiles = []
        self.pipes = []  # Separate pipe list
        self.enemies = []
        self.coins = []
        self.powerups = []
        self.decorations = []
        self.width = 0
        self.ground_y = SCREEN_HEIGHT - 64
        self.score = 0
        self.coin_count = 0
        self.time = 400
        self.flagpole_x = 0
        self.castle_x = 0

        self.build_level()

    def build_level(self):
        """Build SMB1 World 1-1 inspired level"""
        level_width = 200
        self.width = level_width * TILE_SIZE

        # Background decorations
        self.decorations.append(("hill", 0, self.ground_y, 2))
        self.decorations.append(("cloud", 100, 60, 1))
        self.decorations.append(("bush", 200, self.ground_y - 24, 1))
        self.decorations.append(("hill", 400, self.ground_y, 1))
        self.decorations.append(("cloud", 500, 80, 2))
        self.decorations.append(("cloud", 900, 50, 1))
        self.decorations.append(("hill", 1000, self.ground_y, 2))
        self.decorations.append(("bush", 1200, self.ground_y - 24, 2))
        self.decorations.append(("cloud", 1500, 70, 1))
        self.decorations.append(("hill", 1800, self.ground_y, 1))
        self.decorations.append(("cloud", 2200, 60, 2))
        self.decorations.append(("bush", 2500, self.ground_y - 24, 1))
        self.decorations.append(("hill", 3000, self.ground_y, 2))
        self.decorations.append(("cloud", 3500, 80, 1))
        self.decorations.append(("cloud", 4000, 50, 2))
        self.decorations.append(("hill", 4500, self.ground_y, 1))
        self.decorations.append(("bush", 5000, self.ground_y - 24, 2))

        # Ground
        for x in range(level_width):
            if x in range(69, 72) or x in range(86, 89):
                continue
            for row in range(2):
                self.tiles.append(Tile(x * TILE_SIZE, self.ground_y + row * TILE_SIZE, "ground"))

        # First question block
        q1 = Tile(16 * TILE_SIZE, self.ground_y - 4 * TILE_SIZE, "question")
        q1.content = "coin"
        self.tiles.append(q1)

        # Brick + question blocks section
        self.tiles.append(Tile(20 * TILE_SIZE, self.ground_y - 4 * TILE_SIZE, "brick"))
        q2 = Tile(21 * TILE_SIZE, self.ground_y - 4 * TILE_SIZE, "question")
        q2.content = "mushroom"
        self.tiles.append(q2)
        self.tiles.append(Tile(22 * TILE_SIZE, self.ground_y - 4 * TILE_SIZE, "brick"))
        q3 = Tile(23 * TILE_SIZE, self.ground_y - 4 * TILE_SIZE, "question")
        q3.content = "coin"
        self.tiles.append(q3)
        self.tiles.append(Tile(24 * TILE_SIZE, self.ground_y - 4 * TILE_SIZE, "brick"))

        # High question block
        q4 = Tile(22 * TILE_SIZE, self.ground_y - 8 * TILE_SIZE, "question")
        q4.content = "coin"
        self.tiles.append(q4)

        # PIPES - Now using proper Pipe class (2 tiles wide)
        # First pipe (2 tiles tall)
        self.pipes.append(Pipe(28 * TILE_SIZE, self.ground_y - 2 * TILE_SIZE, 2))

        # First goomba
        self.enemies.append(Enemy(22 * TILE_SIZE, self.ground_y - TILE_SIZE, "goomba"))

        # Second pipe (3 tiles tall)
        self.pipes.append(Pipe(38 * TILE_SIZE, self.ground_y - 3 * TILE_SIZE, 3))

        # Goombas pair
        self.enemies.append(Enemy(40 * TILE_SIZE, self.ground_y - TILE_SIZE, "goomba"))
        self.enemies.append(Enemy(42 * TILE_SIZE, self.ground_y - TILE_SIZE, "goomba"))

        # Third pipe (4 tiles tall)
        self.pipes.append(Pipe(46 * TILE_SIZE, self.ground_y - 4 * TILE_SIZE, 4))

        # Fourth pipe (4 tiles tall)
        self.pipes.append(Pipe(57 * TILE_SIZE, self.ground_y - 4 * TILE_SIZE, 4))

        # Hidden coin block area
        self.tiles.append(Tile(64 * TILE_SIZE, self.ground_y - 4 * TILE_SIZE, "brick"))
        q5 = Tile(65 * TILE_SIZE, self.ground_y - 4 * TILE_SIZE, "question")
        q5.content = "mushroom"
        self.tiles.append(q5)
        self.tiles.append(Tile(66 * TILE_SIZE, self.ground_y - 4 * TILE_SIZE, "brick"))

        # Brick ceiling section
        for i in range(8):
            self.tiles.append(Tile((77 + i) * TILE_SIZE, self.ground_y - 4 * TILE_SIZE, "brick"))
        for i in range(3):
            self.tiles.append(Tile((80 + i) * TILE_SIZE, self.ground_y - 8 * TILE_SIZE, "brick"))

        q6 = Tile(78 * TILE_SIZE, self.ground_y - 8 * TILE_SIZE, "question")
        q6.content = "coin"
        self.tiles.append(q6)
        q7 = Tile(82 * TILE_SIZE, self.ground_y - 8 * TILE_SIZE, "question")
        q7.content = "coin"
        self.tiles.append(q7)

        self.enemies.append(Enemy(78 * TILE_SIZE, self.ground_y - TILE_SIZE, "goomba"))
        self.enemies.append(Enemy(82 * TILE_SIZE, self.ground_y - TILE_SIZE, "goomba"))

        # Post-gap bricks
        for i in range(4):
            self.tiles.append(Tile((94 + i) * TILE_SIZE, self.ground_y - 4 * TILE_SIZE, "brick"))
        q8 = Tile(95 * TILE_SIZE, self.ground_y - 4 * TILE_SIZE, "question")
        q8.content = "coin"
        self.tiles.append(q8)

        # More question blocks
        for i in range(3):
            q = Tile((106 + i) * TILE_SIZE, self.ground_y - 4 * TILE_SIZE, "question")
            q.content = "coin"
            self.tiles.append(q)

        # Koopa
        self.enemies.append(Enemy(108 * TILE_SIZE, self.ground_y - TILE_SIZE, "koopa"))

        # Brick rows
        for i in range(4):
            self.tiles.append(Tile((118 + i) * TILE_SIZE, self.ground_y - 4 * TILE_SIZE, "brick"))

        # Staircase 1
        for row in range(4):
            for col in range(row + 1):
                self.tiles.append(Tile((134 + col) * TILE_SIZE, self.ground_y - (row + 1) * TILE_SIZE, "block"))

        # Staircase 2 (down)
        for row in range(4):
            for col in range(4 - row):
                self.tiles.append(Tile((139 + col) * TILE_SIZE, self.ground_y - (row + 1) * TILE_SIZE, "block"))

        # Gap area stairs
        for row in range(4):
            for col in range(row + 1):
                self.tiles.append(Tile((148 + col) * TILE_SIZE, self.ground_y - (row + 1) * TILE_SIZE, "block"))
        for row in range(4):
            for col in range(4 - row):
                self.tiles.append(Tile((152 + col) * TILE_SIZE, self.ground_y - (row + 1) * TILE_SIZE, "block"))

        # Final staircase to flagpole
        for row in range(8):
            for col in range(row + 1):
                self.tiles.append(Tile((168 + col) * TILE_SIZE, self.ground_y - (row + 1) * TILE_SIZE, "block"))

        self.flagpole_x = 178 * TILE_SIZE
        self.castle_x = 185 * TILE_SIZE

        # Coins
        coin_positions = [
            (10, 7), (11, 7), (12, 7),
            (30, 5), (31, 5), (32, 5),
            (50, 4), (51, 4),
            (100, 7), (101, 7), (102, 7),
            (145, 8), (146, 8), (147, 8),
        ]
        for cx, cy in coin_positions:
            self.coins.append(Coin(cx * TILE_SIZE + 4, self.ground_y - cy * TILE_SIZE))

        # More goombas
        goomba_positions = [110, 115, 125, 130, 160, 165]
        for gx in goomba_positions:
            self.enemies.append(Enemy(gx * TILE_SIZE, self.ground_y - TILE_SIZE, "goomba"))

    def get_nearby_tiles(self, x, y):
        nearby = []
        for tile in self.tiles:
            if abs(tile.x - x) < 128 and abs(tile.y - y) < 128:
                nearby.append(tile)
        return nearby

    def update(self):
        for tile in self.tiles:
            tile.update()
        for enemy in self.enemies:
            enemy.update(self)
        for coin in self.coins:
            coin.update(self)
        for powerup in self.powerups:
            powerup.update(self)

        self.enemies = [e for e in self.enemies if e.active]
        self.coins = [c for c in self.coins if c.active]
        self.powerups = [p for p in self.powerups if p.active]

    def draw_background(self, surface, camera_x):
        surface.fill(SKY_BLUE)

        for dec_type, dx, dy, size in self.decorations:
            sx = dx - camera_x * 0.5
            if sx > -200 and sx < SCREEN_WIDTH + 200:
                if dec_type == "hill":
                    draw_hill(surface, sx, dy, size)
                elif dec_type == "cloud":
                    draw_cloud(surface, sx, dy, size)
                elif dec_type == "bush":
                    draw_bush(surface, sx + camera_x * 0.5 - camera_x, dy, size)

    def draw(self, surface, camera_x):
        # Draw tiles
        for tile in self.tiles:
            if tile.x - camera_x > -TILE_SIZE and tile.x - camera_x < SCREEN_WIDTH + TILE_SIZE:
                tile.draw(surface, camera_x)

        # Draw pipes
        for pipe in self.pipes:
            if pipe.x - camera_x > -TILE_SIZE * 3 and pipe.x - camera_x < SCREEN_WIDTH + TILE_SIZE:
                pipe.draw(surface, camera_x)

        # Draw flagpole
        if self.flagpole_x - camera_x > -100 and self.flagpole_x - camera_x < SCREEN_WIDTH + 100:
            draw_flagpole(surface, self.flagpole_x - camera_x, self.ground_y - 5 * TILE_SIZE)

        # Draw castle
        if self.castle_x - camera_x > -150 and self.castle_x - camera_x < SCREEN_WIDTH + 150:
            draw_castle(surface, self.castle_x - camera_x, self.ground_y - 80)

        # Draw coins
        for coin in self.coins:
            if coin.x - camera_x > -50 and coin.x - camera_x < SCREEN_WIDTH + 50:
                coin.draw(surface, camera_x)

        # Draw powerups
        for powerup in self.powerups:
            if powerup.x - camera_x > -50 and powerup.x - camera_x < SCREEN_WIDTH + 50:
                powerup.draw(surface, camera_x)

        # Draw enemies
        for enemy in self.enemies:
            if enemy.x - camera_x > -50 and enemy.x - camera_x < SCREEN_WIDTH + 50:
                enemy.draw(surface, camera_x)


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Super Mario 4K - OST Edition")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)

        self.state = STATE_MENU
        self.lives = 3
        self.score = 0
        self.coins = 0
        self.current_level_id = '1-1'  # Track current level for OST

        self.reset_level()

    def reset_level(self):
        self.level = Level(self.current_level_id)
        self.player = Player(64, self.level.ground_y - 64)
        self.camera_x = 0
        self.time = 400
        self.time_counter = 0

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.state == STATE_PLAYING:
                            self.state = STATE_PAUSED
                            stop_music()
                        elif self.state == STATE_PAUSED:
                            self.state = STATE_PLAYING
                            start_music(self.current_level_id)
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        if self.state == STATE_MENU:
                            self.state = STATE_PLAYING
                            self.current_level_id = '1-1'
                            self.reset_level()
                            self.lives = 3
                            self.score = 0
                            self.coins = 0
                            start_music(self.current_level_id)
                        elif self.state == STATE_GAMEOVER or self.state == STATE_WIN:
                            self.state = STATE_MENU
                            stop_music()
                    elif event.key == pygame.K_m:
                        # Mute/unmute toggle
                        if pygame.mixer.get_busy():
                            stop_music()
                        else:
                            start_music()

            if self.state == STATE_PLAYING:
                self.update()

            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

    def update(self):
        keys = pygame.key.get_pressed()

        self.player.update(self.level, keys)
        self.level.update()

        target_x = self.player.x - SCREEN_WIDTH // 3
        if target_x > self.camera_x:
            self.camera_x = target_x
        if self.camera_x < 0:
            self.camera_x = 0
        if self.camera_x > self.level.width - SCREEN_WIDTH:
            self.camera_x = self.level.width - SCREEN_WIDTH

        if not self.player.win and not self.player.dead:
            if abs(self.player.x - self.level.flagpole_x) < 24:
                self.player.grab_flagpole(self.level.flagpole_x)

        if self.player.win and self.player.win_timer == 1:
            self.score += self.time * 50
            self.state = STATE_WIN

        player_rect = self.player.get_rect()
        for enemy in self.level.enemies:
            if not enemy.active or enemy.squashed:
                continue
            enemy_rect = enemy.get_rect()
            if player_rect.colliderect(enemy_rect):
                if self.player.vy > 0 and self.player.y + self.player.height - 10 < enemy.y + enemy.height // 2:
                    enemy.stomp()
                    self.player.vy = -8
                    self.score += 100
                else:
                    self.player.shrink()

        for coin in self.level.coins:
            if not coin.active or coin.collected:
                continue
            if player_rect.colliderect(coin.get_rect()):
                coin.collect()
                self.coins += 1
                self.score += 200

        for powerup in self.level.powerups:
            if not powerup.active or powerup.emerging:
                continue
            if player_rect.colliderect(powerup.get_rect()):
                self.player.grow()
                powerup.active = False
                self.score += 1000

        self.time_counter += 1
        if self.time_counter >= 24:
            self.time_counter = 0
            self.time -= 1
            if self.time <= 0:
                self.player.die()

        if self.player.dead and self.player.y > SCREEN_HEIGHT + 100:
            self.lives -= 1
            if self.lives <= 0:
                self.state = STATE_GAMEOVER
            else:
                self.reset_level()
                start_music(self.current_level_id)

    def draw(self):
        if self.state == STATE_MENU:
            self.draw_menu()
        elif self.state == STATE_PLAYING or self.state == STATE_PAUSED:
            self.draw_game()
            if self.state == STATE_PAUSED:
                self.draw_pause()
        elif self.state == STATE_GAMEOVER:
            self.draw_gameover()
        elif self.state == STATE_WIN:
            self.draw_win()

    def draw_menu(self):
        self.screen.fill(SKY_BLUE)

        title = self.big_font.render("SUPER MARIO 4K", True, WHITE)
        shadow = self.big_font.render("SUPER MARIO 4K", True, BLACK)
        self.screen.blit(shadow, (SCREEN_WIDTH // 2 - title.get_width() // 2 + 3, 103))
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

        draw_mario(self.screen, SCREEN_WIDTH // 2 - 12, 200, True, True, 0)

        instructions = [
            "Press ENTER or SPACE to Start",
            "",
            "Controls:",
            "Arrow Keys or WASD - Move",
            "SPACE or UP - Jump",
            "SHIFT - Run",
            "ESC - Pause  |  M - Mute Music"
        ]

        for i, text in enumerate(instructions):
            txt = self.font.render(text, True, WHITE)
            self.screen.blit(txt, (SCREEN_WIDTH // 2 - txt.get_width() // 2, 300 + i * 35))

        ver = self.font.render("OST Edition - With Authentic NES Music", True, (200, 200, 200))
        self.screen.blit(ver, (SCREEN_WIDTH // 2 - ver.get_width() // 2, 550))

    def draw_game(self):
        self.level.draw_background(self.screen, self.camera_x)
        self.level.draw(self.screen, self.camera_x)
        self.player.draw(self.screen, self.camera_x)
        self.draw_hud()

    def draw_hud(self):
        score_text = self.font.render(f"SCORE: {self.score:06d}", True, WHITE)
        self.screen.blit(score_text, (20, 20))

        draw_coin(self.screen, 250, 12, 0)
        coin_text = self.font.render(f"x {self.coins:02d}", True, WHITE)
        self.screen.blit(coin_text, (285, 20))

        lives_text = self.font.render(f"LIVES: {self.lives}", True, WHITE)
        self.screen.blit(lives_text, (450, 20))

        time_text = self.font.render(f"TIME: {self.time:03d}", True, WHITE)
        self.screen.blit(time_text, (650, 20))

    def draw_pause(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(128)
        self.screen.blit(overlay, (0, 0))

        pause_text = self.big_font.render("PAUSED", True, WHITE)
        self.screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, SCREEN_HEIGHT // 2 - 36))

        resume_text = self.font.render("Press ESC to Resume", True, WHITE)
        self.screen.blit(resume_text, (SCREEN_WIDTH // 2 - resume_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

    def draw_gameover(self):
        self.screen.fill(BLACK)

        go_text = self.big_font.render("GAME OVER", True, MARIO_RED)
        self.screen.blit(go_text, (SCREEN_WIDTH // 2 - go_text.get_width() // 2, SCREEN_HEIGHT // 2 - 80))

        score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2))

        cont_text = self.font.render("Press ENTER to Continue", True, WHITE)
        self.screen.blit(cont_text, (SCREEN_WIDTH // 2 - cont_text.get_width() // 2, SCREEN_HEIGHT // 2 + 80))

    def draw_win(self):
        self.screen.fill(SKY_BLUE)

        draw_castle(self.screen, SCREEN_WIDTH // 2 - 48, SCREEN_HEIGHT // 2)

        win_text = self.big_font.render("COURSE CLEAR!", True, WHITE)
        shadow = self.big_font.render("COURSE CLEAR!", True, BLACK)
        self.screen.blit(shadow, (SCREEN_WIDTH // 2 - win_text.get_width() // 2 + 3, 103))
        self.screen.blit(win_text, (SCREEN_WIDTH // 2 - win_text.get_width() // 2, 100))

        score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 200))

        cont_text = self.font.render("Press ENTER to Continue", True, WHITE)
        self.screen.blit(cont_text, (SCREEN_WIDTH // 2 - cont_text.get_width() // 2, SCREEN_HEIGHT - 100))


if __name__ == "__main__":
    game = Game()
    game.run()
