#!/usr/bin/env python3
"""
Cat's ! Tetris 1.0X - A SAMSOFT PRODUCTION
All levels to kill screen (Level 29+), Main Menu, All Classic OSTs
Single-file implementation
"""

import pygame
from pygame.locals import *
import random
import math
import array
import copy
import sys

pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

# Display setup
BLOCK_SIZE = 30
COLS, ROWS = 10, 20
SIDE_PANEL = 300
SCREEN_WIDTH = COLS * BLOCK_SIZE + SIDE_PANEL
SCREEN_HEIGHT = ROWS * BLOCK_SIZE + 100
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Cat's ! Tetris 1.0X (c) A SAMSOFT PRODUCTION")
clock = pygame.time.Clock()

# Fonts
try:
    font_small = pygame.font.SysFont("arial", 18)
    font_med = pygame.font.SysFont("arial", 24)
    font_large = pygame.font.SysFont("arial", 36)
    font_title = pygame.font.SysFont("arial", 56, bold=True)
except:
    font_small = pygame.font.Font(None, 20)
    font_med = pygame.font.Font(None, 28)
    font_large = pygame.font.Font(None, 40)
    font_title = pygame.font.Font(None, 60)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (40, 40, 40)
RED = (255, 0, 0)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
PURPLE = (148, 0, 211)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)

# NES Tetris colors per level (cycles every 10 levels)
LEVEL_PALETTES = [
    # Level 0-9 base colors
    [(0, 88, 248), (60, 188, 252)],      # 0 Blue
    [(0, 168, 0), (128, 208, 16)],       # 1 Green  
    [(216, 0, 204), (248, 120, 248)],    # 2 Purple
    [(0, 88, 248), (88, 248, 152)],      # 3 Blue/Cyan
    [(228, 0, 88), (248, 56, 0)],        # 4 Red
    [(88, 248, 152), (104, 136, 252)],   # 5 Cyan
    [(248, 56, 0), (124, 124, 124)],     # 6 Orange
    [(148, 0, 132), (104, 68, 252)],     # 7 Purple alt
    [(0, 88, 248), (248, 56, 0)],        # 8 Blue/Red
    [(248, 56, 0), (0, 168, 68)],        # 9 Orange/Green
]

# Tetromino colors (0 = empty)
PIECE_COLORS = [
    (0, 0, 0),       # 0 Empty
    (0, 255, 255),   # 1 I - Cyan
    (255, 0, 0),     # 2 Z - Red
    (0, 255, 0),     # 3 S - Green
    (255, 255, 0),   # 4 O - Yellow
    (0, 0, 255),     # 5 J - Blue
    (255, 165, 0),   # 6 L - Orange
    (148, 0, 211),   # 7 T - Purple
]

# Base shapes (4x4 matrices)
BASE_SHAPES = [
    # I
    [[0,0,0,0],
     [1,1,1,1],
     [0,0,0,0],
     [0,0,0,0]],
    # Z
    [[1,1,0,0],
     [0,1,1,0],
     [0,0,0,0],
     [0,0,0,0]],
    # S
    [[0,1,1,0],
     [1,1,0,0],
     [0,0,0,0],
     [0,0,0,0]],
    # O
    [[0,1,1,0],
     [0,1,1,0],
     [0,0,0,0],
     [0,0,0,0]],
    # J
    [[1,0,0,0],
     [1,1,1,0],
     [0,0,0,0],
     [0,0,0,0]],
    # L
    [[0,0,1,0],
     [1,1,1,0],
     [0,0,0,0],
     [0,0,0,0]],
    # T
    [[0,1,0,0],
     [1,1,1,0],
     [0,0,0,0],
     [0,0,0,0]],
]

# Wall kick data (SRS)
WALL_KICKS = {
    'JLSTZ': [
        [(0,0), (-1,0), (-1,1), (0,-2), (-1,-2)],  # 0->R
        [(0,0), (1,0), (1,-1), (0,2), (1,2)],      # R->2
        [(0,0), (1,0), (1,1), (0,-2), (1,-2)],     # 2->L
        [(0,0), (-1,0), (-1,-1), (0,2), (-1,2)],   # L->0
    ],
    'I': [
        [(0,0), (-2,0), (1,0), (-2,-1), (1,2)],
        [(0,0), (-1,0), (2,0), (-1,2), (2,-1)],
        [(0,0), (2,0), (-1,0), (2,1), (-1,-2)],
        [(0,0), (1,0), (-2,0), (1,-2), (-2,1)],
    ]
}

# ============== SOUND GENERATION ==============

def generate_wave(freq, duration, waveform='square', volume=0.25):
    """Generate audio waveform"""
    sample_rate = 44100
    samples = int(sample_rate * duration)
    arr = array.array('h', [0] * samples)
    
    for i in range(samples):
        t = i / sample_rate
        phase = 2 * math.pi * freq * t
        
        if waveform == 'square':
            value = 1 if math.sin(phase) > 0 else -1
        elif waveform == 'triangle':
            value = 2 * abs(2 * (t * freq - math.floor(t * freq + 0.5))) - 1
        elif waveform == 'sawtooth':
            value = 2 * (t * freq - math.floor(t * freq + 0.5))
        elif waveform == 'sine':
            value = math.sin(phase)
        elif waveform == 'noise':
            value = random.uniform(-1, 1) * (0.5 if random.random() > 0.5 else 1)
        else:
            value = 1 if math.sin(phase) > 0 else -1
            
        arr[i] = int(value * volume * 32767)
    
    # Fade in/out to prevent clicks
    fade = min(int(sample_rate * 0.01), samples // 4)
    for i in range(fade):
        arr[i] = int(arr[i] * i / fade)
        arr[-i-1] = int(arr[-i-1] * i / fade)
    
    return arr

def generate_chord(freqs, duration, volume=0.15):
    """Generate chord from multiple frequencies"""
    sample_rate = 44100
    samples = int(sample_rate * duration)
    arr = array.array('h', [0] * samples)
    
    for i in range(samples):
        t = i / sample_rate
        value = 0
        for freq in freqs:
            phase = 2 * math.pi * freq * t
            value += (1 if math.sin(phase) > 0 else -1)
        value /= len(freqs)
        arr[i] = int(value * volume * 32767)
    
    fade = min(int(sample_rate * 0.01), samples // 4)
    for i in range(fade):
        arr[i] = int(arr[i] * i / fade)
        arr[-i-1] = int(arr[-i-1] * i / fade)
    
    return arr

# Note frequencies
NOTES = {
    'C3': 130.81, 'D3': 146.83, 'E3': 164.81, 'F3': 174.61, 'G3': 196.00, 'A3': 220.00, 'B3': 246.94,
    'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'F4': 349.23, 'G4': 392.00, 'A4': 440.00, 'B4': 493.88,
    'C5': 523.25, 'D5': 587.33, 'E5': 659.25, 'F5': 698.46, 'G5': 783.99, 'A5': 880.00, 'B5': 987.77,
    'C6': 1046.50,
    'Db4': 277.18, 'Eb4': 311.13, 'Gb4': 369.99, 'Ab4': 415.30, 'Bb4': 466.16,
    'Db5': 554.37, 'Eb5': 622.25, 'Gb5': 739.99, 'Ab5': 830.61, 'Bb5': 932.33,
}

# TYPE A - Korobeiniki (main Tetris theme)
# Game Boy Tetris tempo scale - slower than NES
GB_TEMPO_SCALE = 1.6  # Game Boy runs slower tempo

TYPE_A_MELODY = [
    ('E5', 0.25), ('B4', 0.125), ('C5', 0.125), ('D5', 0.25), ('C5', 0.125), ('B4', 0.125),
    ('A4', 0.25), ('A4', 0.125), ('C5', 0.125), ('E5', 0.25), ('D5', 0.125), ('C5', 0.125),
    ('B4', 0.375), ('C5', 0.125), ('D5', 0.25), ('E5', 0.25),
    ('C5', 0.25), ('A4', 0.25), ('A4', 0.5),
    
    ('D5', 0.375), ('F5', 0.125), ('A5', 0.25), ('G5', 0.125), ('F5', 0.125),
    ('E5', 0.375), ('C5', 0.125), ('E5', 0.25), ('D5', 0.125), ('C5', 0.125),
    ('B4', 0.25), ('B4', 0.125), ('C5', 0.125), ('D5', 0.25), ('E5', 0.25),
    ('C5', 0.25), ('A4', 0.25), ('A4', 0.5),
    
    ('E5', 0.5), ('C5', 0.5), ('D5', 0.5), ('B4', 0.5),
    ('C5', 0.5), ('A4', 0.5), ('Ab4', 0.5), ('B4', 0.5),
    ('E5', 0.5), ('C5', 0.5), ('D5', 0.5), ('B4', 0.5),
    ('C5', 0.25), ('E5', 0.25), ('A5', 0.5), ('Ab5', 1.0),
]

# TYPE B - Russian folk melody variation
TYPE_B_MELODY = [
    ('A4', 0.25), ('E4', 0.25), ('A4', 0.25), ('E4', 0.25),
    ('A4', 0.125), ('B4', 0.125), ('C5', 0.25), ('B4', 0.25),
    ('A4', 0.25), ('G4', 0.25), ('A4', 0.5),
    
    ('E4', 0.25), ('A4', 0.25), ('E4', 0.25), ('A4', 0.25),
    ('G4', 0.125), ('A4', 0.125), ('B4', 0.25), ('A4', 0.25),
    ('G4', 0.25), ('E4', 0.25), ('E4', 0.5),
    
    ('A4', 0.25), ('C5', 0.25), ('E5', 0.25), ('C5', 0.25),
    ('D5', 0.25), ('B4', 0.25), ('C5', 0.25), ('A4', 0.25),
    ('G4', 0.25), ('E4', 0.25), ('G4', 0.25), ('A4', 0.25),
    ('B4', 0.25), ('C5', 0.25), ('D5', 0.25), ('E5', 0.25),
    
    ('C5', 0.5), ('A4', 0.5), ('G4', 0.5), ('E4', 0.5),
]

# TYPE C - Bradinsky / Menuet
TYPE_C_MELODY = [
    ('C5', 0.25), ('E5', 0.25), ('G5', 0.25), ('E5', 0.25),
    ('F5', 0.25), ('E5', 0.25), ('D5', 0.25), ('C5', 0.25),
    ('B4', 0.25), ('D5', 0.25), ('G5', 0.25), ('D5', 0.25),
    ('E5', 0.25), ('D5', 0.25), ('C5', 0.25), ('B4', 0.25),
    
    ('A4', 0.25), ('C5', 0.25), ('E5', 0.25), ('C5', 0.25),
    ('D5', 0.25), ('C5', 0.25), ('B4', 0.25), ('A4', 0.25),
    ('G4', 0.25), ('B4', 0.25), ('D5', 0.25), ('B4', 0.25),
    ('C5', 0.25), ('B4', 0.25), ('A4', 0.25), ('G4', 0.25),
    
    ('C5', 0.5), ('E5', 0.5), ('G5', 1.0),
    ('F5', 0.5), ('D5', 0.5), ('B4', 0.5), ('G4', 0.5),
    ('C5', 1.0), ('C5', 1.0),
]

class SoundManager:
    """Manages all game audio"""
    
    def __init__(self):
        self.music_channel = pygame.mixer.Channel(0)
        self.sfx_channel = pygame.mixer.Channel(1)
        self.music_enabled = True
        self.sfx_enabled = True
        self.current_ost = 0  # 0=A, 1=B, 2=C, 3=Off
        self.ost_names = ["TYPE A", "TYPE B", "TYPE C", "OFF"]
        
        # Generate sound effects
        self.sfx = {
            'move': pygame.mixer.Sound(buffer=generate_wave(200, 0.05, 'square', 0.15).tobytes()),
            'rotate': pygame.mixer.Sound(buffer=generate_wave(400, 0.05, 'square', 0.15).tobytes()),
            'drop': pygame.mixer.Sound(buffer=generate_wave(150, 0.1, 'square', 0.2).tobytes()),
            'lock': pygame.mixer.Sound(buffer=generate_wave(100, 0.15, 'square', 0.2).tobytes()),
            'clear': pygame.mixer.Sound(buffer=generate_wave(880, 0.15, 'square', 0.25).tobytes()),
            'tetris': pygame.mixer.Sound(buffer=generate_chord([523, 659, 784, 1047], 0.5, 0.25).tobytes()),
            'levelup': pygame.mixer.Sound(buffer=generate_chord([440, 554, 659, 880], 0.3, 0.2).tobytes()),
            'gameover': pygame.mixer.Sound(buffer=generate_wave(110, 1.0, 'sawtooth', 0.3).tobytes()),
            'menu': pygame.mixer.Sound(buffer=generate_wave(440, 0.05, 'square', 0.15).tobytes()),
            'select': pygame.mixer.Sound(buffer=generate_wave(660, 0.1, 'square', 0.2).tobytes()),
            'pause': pygame.mixer.Sound(buffer=generate_wave(330, 0.2, 'square', 0.2).tobytes()),
        }
        
        # Generate complete music tracks as single looping sounds
        self.music_tracks = {
            'A': self._generate_full_song(TYPE_A_MELODY),
            'B': self._generate_full_song(TYPE_B_MELODY),
            'C': self._generate_full_song(TYPE_C_MELODY),
        }
        
        self.playing_ost = None
    
    def _generate_full_song(self, melody):
        """Generate complete song as single seamless audio buffer - like original GB"""
        sample_rate = 44100
        volume = 0.22
        
        # Calculate total duration with GB tempo
        total_duration = sum(dur * GB_TEMPO_SCALE for note, dur in melody)
        total_samples = int(sample_rate * total_duration)
        
        # Create single continuous buffer for entire song
        song_buffer = array.array('h', [0] * total_samples)
        
        # Fill buffer with all notes continuously - no gaps, no fades between notes
        sample_pos = 0
        for note, dur in melody:
            if note not in NOTES:
                continue
            
            freq = NOTES[note]
            note_duration = dur * GB_TEMPO_SCALE
            note_samples = int(sample_rate * note_duration)
            
            # Generate this note's samples directly into song buffer
            for i in range(note_samples):
                if sample_pos + i >= total_samples:
                    break
                t = i / sample_rate
                phase = 2 * math.pi * freq * t
                # Square wave - authentic chiptune sound
                value = 1 if math.sin(phase) > 0 else -1
                song_buffer[sample_pos + i] = int(value * volume * 32767)
            
            sample_pos += note_samples
        
        # Only tiny fade at very start and end of entire song to prevent click on loop
        fade_samples = int(sample_rate * 0.005)  # 5ms fade
        for i in range(min(fade_samples, total_samples // 2)):
            song_buffer[i] = int(song_buffer[i] * i / fade_samples)
            song_buffer[-i-1] = int(song_buffer[-i-1] * i / fade_samples)
        
        return pygame.mixer.Sound(buffer=song_buffer.tobytes())
    
    def play_sfx(self, name):
        """Play sound effect"""
        if self.sfx_enabled and name in self.sfx:
            self.sfx_channel.play(self.sfx[name])
    
    def start_music(self):
        """Start playing current OST on loop"""
        if not self.music_enabled or self.current_ost == 3:
            return
        
        track_key = ['A', 'B', 'C'][self.current_ost]
        track = self.music_tracks[track_key]
        
        # Play entire song on infinite loop (-1 = loop forever)
        self.music_channel.play(track, loops=-1)
        self.playing_ost = self.current_ost
    
    def update_music(self):
        """Check if music needs to start/restart"""
        if not self.music_enabled or self.current_ost == 3:
            return
        
        # Start music if not playing or OST changed
        if not self.music_channel.get_busy() or self.playing_ost != self.current_ost:
            self.start_music()
    
    def stop_music(self):
        """Stop music playback"""
        self.music_channel.stop()
        self.playing_ost = None
    
    def cycle_ost(self):
        """Cycle through OST options"""
        self.stop_music()
        self.current_ost = (self.current_ost + 1) % 4
        if self.current_ost != 3:
            self.start_music()
        return self.ost_names[self.current_ost]
    
    def set_ost(self, idx):
        """Set specific OST"""
        self.stop_music()
        self.current_ost = idx % 4
        if self.current_ost != 3:
            self.start_music()

# ============== GAME LOGIC ==============

class TetrisGame:
    """Main Tetris game logic"""
    
    # NES Tetris frame delays per level (frames at 60fps)
    # Level 29+ is the "kill screen" - pieces fall in 1 frame
    LEVEL_SPEEDS = [
        48, 43, 38, 33, 28, 23, 18, 13, 8, 6,  # 0-9
        5, 5, 5, 4, 4, 4, 3, 3, 3, 2,          # 10-19
        2, 2, 2, 2, 2, 2, 2, 2, 2, 1,          # 20-29 (29 = kill screen)
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1,          # 30+
    ]
    
    def __init__(self, start_level=0):
        self.reset(start_level)
    
    def reset(self, start_level=0):
        """Reset game state"""
        self.board = [[0] * COLS for _ in range(ROWS)]
        self.start_level = start_level
        self.level = start_level
        self.score = 0
        self.lines = 0
        self.lines_for_level = 0
        
        self.bag = []
        self.current = None
        self.next_piece_type = None
        self.hold_type = None
        self.can_hold = True
        
        self.drop_timer = 0
        self.lock_timer = 0
        self.lock_delay = 30  # frames before locking
        self.is_locking = False
        
        self.das_timer = 0
        self.das_direction = 0
        self.das_delay = 16  # Initial delay
        self.das_speed = 6   # Auto-repeat speed
        
        self.game_over = False
        self.paused = False
        
        self.stats = {i: 0 for i in range(7)}  # Piece statistics
        self.total_pieces = 0
        
        # Spawn first pieces
        self._refill_bag()
        self.next_piece_type = self._next_type()
        self._spawn_piece()
    
    def _refill_bag(self):
        """Refill piece bag (7-bag randomizer)"""
        self.bag = list(range(7))
        random.shuffle(self.bag)
    
    def _next_type(self):
        """Get next piece type from bag"""
        if not self.bag:
            self._refill_bag()
        return self.bag.pop()
    
    def _spawn_piece(self):
        """Spawn new piece at top"""
        piece_type = self.next_piece_type
        self.next_piece_type = self._next_type()
        
        self.current = {
            'type': piece_type,
            'x': COLS // 2 - 2,
            'y': 0,
            'shape': copy.deepcopy(BASE_SHAPES[piece_type]),
            'color': piece_type + 1,
            'rotation': 0
        }
        
        # Adjust I piece spawn
        if piece_type == 0:
            self.current['y'] = -1
        
        self.stats[piece_type] += 1
        self.total_pieces += 1
        self.can_hold = True
        self.is_locking = False
        self.lock_timer = 0
        
        # Check for game over
        if not self._valid():
            self.game_over = True
    
    def _valid(self, shape=None, dx=0, dy=0):
        """Check if current piece position is valid"""
        shape = shape or self.current['shape']
        for i in range(4):
            for j in range(4):
                if shape[i][j]:
                    x = self.current['x'] + j + dx
                    y = self.current['y'] + i + dy
                    if x < 0 or x >= COLS or y >= ROWS:
                        return False
                    if y >= 0 and self.board[y][x]:
                        return False
        return True
    
    def _rotate(self, shape):
        """Rotate shape 90 degrees clockwise"""
        return [list(row) for row in zip(*shape[::-1])]
    
    def _get_ghost_y(self):
        """Get Y position for ghost piece"""
        ghost_y = self.current['y']
        while self._valid(dy=ghost_y - self.current['y'] + 1):
            ghost_y += 1
        return ghost_y
    
    def move(self, dx):
        """Move piece horizontally"""
        if self._valid(dx=dx):
            self.current['x'] += dx
            if self.is_locking:
                self.lock_timer = 0  # Reset lock timer on move
            return True
        return False
    
    def rotate(self, direction=1):
        """Rotate piece with wall kicks"""
        if self.current['type'] == 3:  # O piece doesn't rotate
            return False
        
        original_shape = self.current['shape']
        original_rotation = self.current['rotation']
        
        # Rotate
        new_shape = copy.deepcopy(original_shape)
        for _ in range(direction if direction > 0 else 3):
            new_shape = self._rotate(new_shape)
        
        new_rotation = (original_rotation + direction) % 4
        
        # Get wall kick data
        kick_table = WALL_KICKS['I'] if self.current['type'] == 0 else WALL_KICKS['JLSTZ']
        kicks = kick_table[original_rotation]
        
        # Try each kick offset
        for dx, dy in kicks:
            if self._valid(shape=new_shape, dx=dx, dy=-dy):
                self.current['shape'] = new_shape
                self.current['x'] += dx
                self.current['y'] -= dy
                self.current['rotation'] = new_rotation
                if self.is_locking:
                    self.lock_timer = 0
                return True
        
        return False
    
    def soft_drop(self):
        """Move piece down one row"""
        if self._valid(dy=1):
            self.current['y'] += 1
            self.score += 1
            self.is_locking = False
            self.lock_timer = 0
            return True
        return False
    
    def hard_drop(self):
        """Instantly drop piece to bottom"""
        drop_distance = 0
        while self._valid(dy=1):
            self.current['y'] += 1
            drop_distance += 1
        self.score += drop_distance * 2
        self._lock_piece()
    
    def hold(self):
        """Hold current piece"""
        if not self.can_hold:
            return False
        
        if self.hold_type is None:
            self.hold_type = self.current['type']
            self._spawn_piece()
        else:
            held = self.hold_type
            self.hold_type = self.current['type']
            self.current = {
                'type': held,
                'x': COLS // 2 - 2,
                'y': 0 if held != 0 else -1,
                'shape': copy.deepcopy(BASE_SHAPES[held]),
                'color': held + 1,
                'rotation': 0
            }
        
        self.can_hold = False
        self.is_locking = False
        self.lock_timer = 0
        return True
    
    def _lock_piece(self):
        """Lock piece into board"""
        for i in range(4):
            for j in range(4):
                if self.current['shape'][i][j]:
                    y = self.current['y'] + i
                    x = self.current['x'] + j
                    if 0 <= y < ROWS and 0 <= x < COLS:
                        self.board[y][x] = self.current['color']
        
        lines_cleared = self._clear_lines()
        self._spawn_piece()
        return lines_cleared
    
    def _clear_lines(self):
        """Clear completed lines and update score"""
        full_rows = [r for r in range(ROWS) if all(self.board[r])]
        
        if not full_rows:
            return 0
        
        # Remove full rows
        for r in sorted(full_rows, reverse=True):
            del self.board[r]
            self.board.insert(0, [0] * COLS)
        
        num_lines = len(full_rows)
        self.lines += num_lines
        self.lines_for_level += num_lines
        
        # NES scoring: base * (level + 1)
        line_scores = [40, 100, 300, 1200]  # 1, 2, 3, 4 lines
        self.score += line_scores[num_lines - 1] * (self.level + 1)
        
        # Level up every 10 lines (or at start_level * 10 + 10 for first level up)
        lines_needed = min(self.start_level * 10 + 10, max(100, self.start_level * 10 - 50))
        if self.level == self.start_level:
            if self.lines_for_level >= lines_needed:
                self.level += 1
                self.lines_for_level = 0
        else:
            if self.lines_for_level >= 10:
                self.level += 1
                self.lines_for_level -= 10
        
        return num_lines
    
    def get_drop_frames(self):
        """Get drop speed in frames for current level"""
        idx = min(self.level, len(self.LEVEL_SPEEDS) - 1)
        return self.LEVEL_SPEEDS[idx]
    
    def update(self):
        """Update game state (called each frame)"""
        if self.game_over or self.paused:
            return None
        
        # Check if piece should lock
        if not self._valid(dy=1):
            if not self.is_locking:
                self.is_locking = True
                self.lock_timer = 0
            else:
                self.lock_timer += 1
                if self.lock_timer >= self.lock_delay:
                    return self._lock_piece()
        else:
            self.is_locking = False
            self.lock_timer = 0
        
        # Gravity
        self.drop_timer += 1
        drop_frames = self.get_drop_frames()
        
        if self.drop_timer >= drop_frames:
            self.drop_timer = 0
            if self._valid(dy=1):
                self.current['y'] += 1
        
        return None
    
    def handle_das(self, keys):
        """Handle Delayed Auto-Shift for horizontal movement"""
        if keys[K_LEFT] and not keys[K_RIGHT]:
            if self.das_direction != -1:
                self.das_direction = -1
                self.das_timer = 0
                self.move(-1)
            else:
                self.das_timer += 1
                if self.das_timer >= self.das_delay:
                    if (self.das_timer - self.das_delay) % self.das_speed == 0:
                        self.move(-1)
        elif keys[K_RIGHT] and not keys[K_LEFT]:
            if self.das_direction != 1:
                self.das_direction = 1
                self.das_timer = 0
                self.move(1)
            else:
                self.das_timer += 1
                if self.das_timer >= self.das_delay:
                    if (self.das_timer - self.das_delay) % self.das_speed == 0:
                        self.move(1)
        else:
            self.das_direction = 0
            self.das_timer = 0

# ============== RENDERING ==============

class Renderer:
    """Handles all game rendering"""
    
    def __init__(self):
        self.board_x = 10
        self.board_y = 50
        self.flash_timer = 0
    
    def get_level_colors(self, level):
        """Get colors for current level"""
        palette_idx = level % 10
        return LEVEL_PALETTES[palette_idx]
    
    def draw_block(self, x, y, color, highlight=False):
        """Draw single block with 3D effect"""
        rect = pygame.Rect(x, y, BLOCK_SIZE - 1, BLOCK_SIZE - 1)
        
        # Main color
        pygame.draw.rect(screen, color, rect)
        
        # Highlight (top-left)
        highlight_color = tuple(min(255, c + 60) for c in color)
        pygame.draw.line(screen, highlight_color, (x, y), (x + BLOCK_SIZE - 2, y), 2)
        pygame.draw.line(screen, highlight_color, (x, y), (x, y + BLOCK_SIZE - 2), 2)
        
        # Shadow (bottom-right)
        shadow_color = tuple(max(0, c - 60) for c in color)
        pygame.draw.line(screen, shadow_color, (x + BLOCK_SIZE - 2, y + 1), 
                        (x + BLOCK_SIZE - 2, y + BLOCK_SIZE - 2), 2)
        pygame.draw.line(screen, shadow_color, (x + 1, y + BLOCK_SIZE - 2), 
                        (x + BLOCK_SIZE - 2, y + BLOCK_SIZE - 2), 2)
        
        if highlight:
            pygame.draw.rect(screen, WHITE, rect, 2)
    
    def draw_board(self, game):
        """Draw the game board"""
        # Board background
        board_rect = pygame.Rect(self.board_x - 2, self.board_y - 2,
                                 COLS * BLOCK_SIZE + 4, ROWS * BLOCK_SIZE + 4)
        pygame.draw.rect(screen, DARK_GRAY, board_rect)
        pygame.draw.rect(screen, GRAY, board_rect, 2)
        
        # Grid and placed pieces
        for r in range(ROWS):
            for c in range(COLS):
                x = self.board_x + c * BLOCK_SIZE
                y = self.board_y + r * BLOCK_SIZE
                
                if game.board[r][c]:
                    color = PIECE_COLORS[game.board[r][c]]
                    self.draw_block(x, y, color)
                else:
                    # Grid lines
                    pygame.draw.rect(screen, (30, 30, 30), 
                                    (x, y, BLOCK_SIZE - 1, BLOCK_SIZE - 1), 1)
    
    def draw_piece(self, game, ghost=False):
        """Draw current piece and ghost"""
        if not game.current:
            return
        
        # Draw ghost piece
        ghost_y = game._get_ghost_y()
        for i in range(4):
            for j in range(4):
                if game.current['shape'][i][j]:
                    x = self.board_x + (game.current['x'] + j) * BLOCK_SIZE
                    y = self.board_y + (ghost_y + i) * BLOCK_SIZE
                    if y >= self.board_y:
                        ghost_color = tuple(c // 4 for c in PIECE_COLORS[game.current['color']])
                        pygame.draw.rect(screen, ghost_color, 
                                        (x, y, BLOCK_SIZE - 1, BLOCK_SIZE - 1), 2)
        
        # Draw current piece
        for i in range(4):
            for j in range(4):
                if game.current['shape'][i][j]:
                    x = self.board_x + (game.current['x'] + j) * BLOCK_SIZE
                    y = self.board_y + (game.current['y'] + i) * BLOCK_SIZE
                    if y >= self.board_y:
                        color = PIECE_COLORS[game.current['color']]
                        self.draw_block(x, y, color, highlight=True)
    
    def draw_preview(self, piece_type, x, y, label):
        """Draw piece preview (next/hold)"""
        # Label
        text = font_small.render(label, True, WHITE)
        screen.blit(text, (x, y - 25))
        
        # Background
        pygame.draw.rect(screen, DARK_GRAY, (x - 5, y - 5, 130, 90))
        pygame.draw.rect(screen, GRAY, (x - 5, y - 5, 130, 90), 2)
        
        if piece_type is None:
            return
        
        shape = BASE_SHAPES[piece_type]
        color = PIECE_COLORS[piece_type + 1]
        
        # Center the piece
        offset_x = 15 if piece_type == 0 else 30
        offset_y = 10 if piece_type == 0 else 20
        
        for i in range(4):
            for j in range(4):
                if shape[i][j]:
                    bx = x + offset_x + j * 20
                    by = y + offset_y + i * 20
                    pygame.draw.rect(screen, color, (bx, by, 18, 18))
                    pygame.draw.rect(screen, WHITE, (bx, by, 18, 18), 1)
    
    def draw_stats(self, game, sound_mgr):
        """Draw game statistics"""
        panel_x = COLS * BLOCK_SIZE + 30
        y = 50
        
        # Score
        score_text = font_large.render("SCORE", True, WHITE)
        screen.blit(score_text, (panel_x, y))
        score_val = font_large.render(f"{game.score:,}", True, CYAN)
        screen.blit(score_val, (panel_x, y + 35))
        
        # Level
        y += 90
        level_text = font_med.render("LEVEL", True, WHITE)
        screen.blit(level_text, (panel_x, y))
        
        # Flash level display if at kill screen
        if game.level >= 29:
            self.flash_timer = (self.flash_timer + 1) % 30
            color = RED if self.flash_timer < 15 else YELLOW
            level_val = font_large.render(f"{game.level}", True, color)
            if game.level == 29:
                kill_text = font_small.render("KILL SCREEN!", True, RED)
                screen.blit(kill_text, (panel_x, y + 55))
        else:
            level_val = font_large.render(f"{game.level}", True, GREEN)
        screen.blit(level_val, (panel_x, y + 22))
        
        # Lines
        y += 80
        lines_text = font_med.render("LINES", True, WHITE)
        screen.blit(lines_text, (panel_x, y))
        lines_val = font_med.render(f"{game.lines}", True, WHITE)
        screen.blit(lines_val, (panel_x, y + 25))
        
        # Next piece
        y += 70
        self.draw_preview(game.next_piece_type, panel_x, y + 25, "NEXT")
        
        # Hold piece
        y += 110
        self.draw_preview(game.hold_type, panel_x, y + 25, "HOLD")
        
        # Music indicator
        y += 110
        ost_text = font_small.render(f"MUSIC: {sound_mgr.ost_names[sound_mgr.current_ost]}", True, GRAY)
        screen.blit(ost_text, (panel_x, y))
        
        # Speed indicator
        y += 25
        frames = game.get_drop_frames()
        speed_text = font_small.render(f"SPEED: {60/frames:.1f} rows/sec", True, GRAY)
        screen.blit(speed_text, (panel_x, y))
    
    def draw_controls(self):
        """Draw control instructions at bottom"""
        y = SCREEN_HEIGHT - 45
        controls = "← → Move  ↑ Rotate  ↓ Soft Drop  SPACE Hard Drop  C Hold  M Music  P Pause  ESC Menu"
        text = font_small.render(controls, True, GRAY)
        screen.blit(text, (10, y))
    
    def draw_game_over(self, game):
        """Draw game over screen"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # Game Over text
        go_text = font_title.render("GAME OVER", True, RED)
        go_rect = go_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
        screen.blit(go_text, go_rect)
        
        # Final stats
        stats = [
            f"Final Score: {game.score:,}",
            f"Level Reached: {game.level}",
            f"Lines Cleared: {game.lines}",
            f"Pieces Placed: {game.total_pieces}",
        ]
        
        for i, stat in enumerate(stats):
            text = font_med.render(stat, True, WHITE)
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + i * 30))
            screen.blit(text, rect)
        
        # Instructions
        inst = font_small.render("Press ENTER to continue or ESC for menu", True, GRAY)
        inst_rect = inst.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150))
        screen.blit(inst, inst_rect)
    
    def draw_pause(self):
        """Draw pause overlay"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        pause_text = font_title.render("PAUSED", True, YELLOW)
        pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(pause_text, pause_rect)
        
        hint = font_small.render("Press P to resume or ESC for menu", True, GRAY)
        hint_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        screen.blit(hint, hint_rect)

# ============== MENU SYSTEM ==============

class Menu:
    """Main menu system"""
    
    def __init__(self, sound_mgr):
        self.sound = sound_mgr
        self.state = 'main'  # main, level_select, options, highscores, howtoplay, credits
        self.selected = 0
        self.start_level = 0
        self.animation_timer = 0
        
        self.main_options = ['PLAY', 'LEVEL SELECT', '[HOW TO PLAY]', 'OPTIONS', 'HIGH SCORES', '[CREDITS]', 'QUIT']
        self.option_items = ['MUSIC TYPE', 'SFX', 'BACK']
        
        # High scores (stored in memory)
        self.high_scores = [
            ('---', 0) for _ in range(10)
        ]
    
    def handle_input(self, event):
        """Handle menu input"""
        if event.type != KEYDOWN:
            return None
        
        if self.state == 'main':
            if event.key == K_UP:
                self.selected = (self.selected - 1) % len(self.main_options)
                self.sound.play_sfx('menu')
            elif event.key == K_DOWN:
                self.selected = (self.selected + 1) % len(self.main_options)
                self.sound.play_sfx('menu')
            elif event.key in (K_RETURN, K_SPACE):
                self.sound.play_sfx('select')
                if self.main_options[self.selected] == 'PLAY':
                    return ('start', self.start_level)
                elif self.main_options[self.selected] == 'LEVEL SELECT':
                    self.state = 'level_select'
                    self.selected = self.start_level
                elif self.main_options[self.selected] == '[HOW TO PLAY]':
                    self.state = 'howtoplay'
                elif self.main_options[self.selected] == 'OPTIONS':
                    self.state = 'options'
                    self.selected = 0
                elif self.main_options[self.selected] == 'HIGH SCORES':
                    self.state = 'highscores'
                elif self.main_options[self.selected] == '[CREDITS]':
                    self.state = 'credits'
                elif self.main_options[self.selected] == 'QUIT':
                    return ('quit', None)
        
        elif self.state == 'level_select':
            if event.key == K_UP:
                self.selected = max(0, self.selected - 5)
                self.sound.play_sfx('menu')
            elif event.key == K_DOWN:
                self.selected = min(29, self.selected + 5)
                self.sound.play_sfx('menu')
            elif event.key == K_LEFT:
                self.selected = max(0, self.selected - 1)
                self.sound.play_sfx('menu')
            elif event.key == K_RIGHT:
                self.selected = min(29, self.selected + 1)
                self.sound.play_sfx('menu')
            elif event.key in (K_RETURN, K_SPACE):
                self.start_level = self.selected
                self.state = 'main'
                self.selected = 0
                self.sound.play_sfx('select')
            elif event.key == K_ESCAPE:
                self.state = 'main'
                self.selected = 1
        
        elif self.state == 'options':
            if event.key == K_UP:
                self.selected = (self.selected - 1) % len(self.option_items)
                self.sound.play_sfx('menu')
            elif event.key == K_DOWN:
                self.selected = (self.selected + 1) % len(self.option_items)
                self.sound.play_sfx('menu')
            elif event.key in (K_RETURN, K_SPACE, K_LEFT, K_RIGHT):
                if self.option_items[self.selected] == 'MUSIC TYPE':
                    self.sound.cycle_ost()
                    self.sound.play_sfx('select')
                elif self.option_items[self.selected] == 'SFX':
                    self.sound.sfx_enabled = not self.sound.sfx_enabled
                    if self.sound.sfx_enabled:
                        self.sound.play_sfx('select')
                elif self.option_items[self.selected] == 'BACK':
                    self.state = 'main'
                    self.selected = 3
            elif event.key == K_ESCAPE:
                self.state = 'main'
                self.selected = 3
        
        elif self.state == 'highscores':
            if event.key in (K_RETURN, K_SPACE, K_ESCAPE):
                self.state = 'main'
                self.selected = 4
        
        elif self.state == 'howtoplay':
            if event.key in (K_RETURN, K_SPACE, K_ESCAPE):
                self.state = 'main'
                self.selected = 2
        
        elif self.state == 'credits':
            if event.key in (K_RETURN, K_SPACE, K_ESCAPE):
                self.state = 'main'
                self.selected = 5
        
        return None
    
    def update_high_scores(self, score, level):
        """Update high scores list"""
        entry = (f"LV{level}", score)
        self.high_scores.append(entry)
        self.high_scores.sort(key=lambda x: x[1], reverse=True)
        self.high_scores = self.high_scores[:10]
    
    def draw(self):
        """Draw menu"""
        screen.fill(BLACK)
        self.animation_timer = (self.animation_timer + 1) % 120
        
        if self.state == 'main':
            self._draw_main_menu()
        elif self.state == 'level_select':
            self._draw_level_select()
        elif self.state == 'options':
            self._draw_options()
        elif self.state == 'highscores':
            self._draw_highscores()
        elif self.state == 'howtoplay':
            self._draw_howtoplay()
        elif self.state == 'credits':
            self._draw_credits()
    
    def _draw_main_menu(self):
        """Draw main menu"""
        # Title with animation
        title_y = 80 + math.sin(self.animation_timer * 0.05) * 5
        
        # Cat's ! text
        cats = font_title.render("Cat's !", True, CYAN)
        cats_rect = cats.get_rect(center=(SCREEN_WIDTH // 2, title_y))
        screen.blit(cats, cats_rect)
        
        # TETRIS text with rainbow effect
        colors = [RED, ORANGE, YELLOW, GREEN, CYAN, BLUE, PURPLE]
        tetris_text = "Tetris"
        x = SCREEN_WIDTH // 2 - 100
        for i, char in enumerate(tetris_text):
            color_idx = (i + self.animation_timer // 10) % len(colors)
            char_surf = font_title.render(char, True, colors[color_idx])
            screen.blit(char_surf, (x + i * 35, title_y + 50))
        
        # Version text
        version = font_med.render("1.0X", True, YELLOW)
        version_rect = version.get_rect(center=(SCREEN_WIDTH // 2, title_y + 100))
        screen.blit(version, version_rect)
        
        # Menu options
        for i, option in enumerate(self.main_options):
            y = 220 + i * 40
            if i == self.selected:
                # Selected item
                color = YELLOW
                prefix = "> "
                suffix = " <"
            else:
                color = WHITE
                prefix = suffix = "  "
            
            text = font_med.render(f"{prefix}{option}{suffix}", True, color)
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
            screen.blit(text, rect)
        
        # Start level indicator
        level_text = font_small.render(f"Start Level: {self.start_level}", True, GRAY)
        screen.blit(level_text, (SCREEN_WIDTH // 2 - 50, 510))
        
        # Footer
        footer = font_small.render("(c) A SAMSOFT PRODUCTION - Press ENTER to select", True, GRAY)
        footer_rect = footer.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
        screen.blit(footer, footer_rect)
        
        # Draw decorative tetris pieces
        self._draw_deco_pieces()
    
    def _draw_deco_pieces(self):
        """Draw decorative falling pieces"""
        t = self.animation_timer
        pieces = [
            (50, (t * 2) % SCREEN_HEIGHT, 0, CYAN),
            (SCREEN_WIDTH - 80, (t * 3 + 100) % SCREEN_HEIGHT, 6, PURPLE),
            (100, (t * 2.5 + 200) % SCREEN_HEIGHT, 4, YELLOW),
            (SCREEN_WIDTH - 130, (t * 2 + 50) % SCREEN_HEIGHT, 2, RED),
        ]
        
        for x, y, piece_type, color in pieces:
            shape = BASE_SHAPES[piece_type]
            for i in range(4):
                for j in range(4):
                    if shape[i][j]:
                        pygame.draw.rect(screen, color, 
                                        (x + j * 15, y + i * 15, 13, 13))
    
    def _draw_level_select(self):
        """Draw level selection grid"""
        title = font_large.render("SELECT STARTING LEVEL", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        screen.blit(title, title_rect)
        
        # Level grid (6 rows x 5 cols = 30 levels)
        grid_x = SCREEN_WIDTH // 2 - 150
        grid_y = 120
        
        for level in range(30):
            row = level // 5
            col = level % 5
            x = grid_x + col * 65
            y = grid_y + row * 55
            
            # Level box
            is_selected = level == self.selected
            is_kill = level >= 29
            
            if is_selected:
                color = YELLOW
                pygame.draw.rect(screen, color, (x - 3, y - 3, 56, 46), 3)
            
            bg_color = RED if is_kill else LEVEL_PALETTES[level % 10][0]
            pygame.draw.rect(screen, bg_color, (x, y, 50, 40))
            
            # Level number
            text_color = WHITE if not is_kill else YELLOW
            num_text = font_med.render(str(level), True, text_color)
            num_rect = num_text.get_rect(center=(x + 25, y + 20))
            screen.blit(num_text, num_rect)
        
        # Kill screen warning
        if self.selected >= 29:
            warn = font_small.render("WARNING: KILL SCREEN - EXTREME DIFFICULTY!", True, RED)
            warn_rect = warn.get_rect(center=(SCREEN_WIDTH // 2, 470))
            screen.blit(warn, warn_rect)
        
        # Instructions
        inst = font_small.render("Arrow keys to select, ENTER to confirm, ESC to cancel", True, GRAY)
        inst_rect = inst.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
        screen.blit(inst, inst_rect)
    
    def _draw_options(self):
        """Draw options menu"""
        title = font_large.render("OPTIONS", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
        screen.blit(title, title_rect)
        
        options_display = [
            ('MUSIC TYPE', self.sound.ost_names[self.sound.current_ost]),
            ('SFX', 'ON' if self.sound.sfx_enabled else 'OFF'),
            ('BACK', ''),
        ]
        
        for i, (label, value) in enumerate(options_display):
            y = 200 + i * 60
            is_selected = i == self.selected
            
            if is_selected:
                color = YELLOW
                prefix = "> "
            else:
                color = WHITE
                prefix = "  "
            
            if value:
                text = font_med.render(f"{prefix}{label}: {value}", True, color)
            else:
                text = font_med.render(f"{prefix}{label}", True, color)
            
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
            screen.blit(text, rect)
        
        inst = font_small.render("ENTER/Arrow keys to change, ESC to return", True, GRAY)
        inst_rect = inst.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
        screen.blit(inst, inst_rect)
    
    def _draw_highscores(self):
        """Draw high scores"""
        title = font_large.render("HIGH SCORES", True, YELLOW)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 60))
        screen.blit(title, title_rect)
        
        for i, (name, score) in enumerate(self.high_scores):
            y = 130 + i * 40
            
            # Rank
            rank_color = [YELLOW, GRAY, ORANGE][i] if i < 3 else WHITE
            rank = font_med.render(f"{i + 1}.", True, rank_color)
            screen.blit(rank, (SCREEN_WIDTH // 2 - 120, y))
            
            # Name/Level
            name_text = font_med.render(name, True, WHITE)
            screen.blit(name_text, (SCREEN_WIDTH // 2 - 70, y))
            
            # Score
            score_text = font_med.render(f"{score:,}", True, CYAN)
            score_rect = score_text.get_rect(right=SCREEN_WIDTH // 2 + 120)
            score_rect.y = y
            screen.blit(score_text, score_rect)
        
        inst = font_small.render("Press ENTER or ESC to return", True, GRAY)
        inst_rect = inst.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
        screen.blit(inst, inst_rect)
    
    def _draw_howtoplay(self):
        """Draw how to play screen"""
        title = font_large.render("HOW TO PLAY", True, CYAN)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        screen.blit(title, title_rect)
        
        controls = [
            ("MOVEMENT", ""),
            ("← →", "Move piece left/right"),
            ("↓", "Soft drop (faster fall)"),
            ("SPACE", "Hard drop (instant)"),
            ("", ""),
            ("ROTATION", ""),
            ("↑ / X", "Rotate clockwise"),
            ("Z", "Rotate counter-clockwise"),
            ("", ""),
            ("OTHER", ""),
            ("C / SHIFT", "Hold piece"),
            ("P", "Pause game"),
            ("M", "Change music"),
            ("ESC", "Return to menu"),
        ]
        
        y = 100
        for key, desc in controls:
            if key in ("MOVEMENT", "ROTATION", "OTHER"):
                # Section header
                text = font_med.render(key, True, YELLOW)
                screen.blit(text, (80, y))
                y += 30
            elif key == "":
                y += 10
            else:
                # Control entry
                key_text = font_small.render(key, True, GREEN)
                screen.blit(key_text, (100, y))
                desc_text = font_small.render(desc, True, WHITE)
                screen.blit(desc_text, (220, y))
                y += 25
        
        # Goal explanation
        y += 20
        goal_title = font_med.render("GOAL", True, YELLOW)
        screen.blit(goal_title, (80, y))
        y += 35
        
        goals = [
            "Fill horizontal lines to clear them and score points.",
            "Clear 4 lines at once for a TETRIS bonus!",
            "Survive as long as possible - speed increases each level.",
            "Level 29 is the KILL SCREEN - max speed challenge!",
        ]
        
        for goal in goals:
            text = font_small.render(goal, True, WHITE)
            screen.blit(text, (100, y))
            y += 22
        
        inst = font_small.render("Press ENTER or ESC to return", True, GRAY)
        inst_rect = inst.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
        screen.blit(inst, inst_rect)
    
    def _draw_credits(self):
        """Draw credits screen"""
        # Title
        title = font_large.render("CREDITS", True, YELLOW)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 60))
        screen.blit(title, title_rect)
        
        y = 140
        
        # Main credits
        credits_data = [
            ("Cat's ! Tetris 1.0X", CYAN, font_large),
            ("", WHITE, font_small),
            ("(C) 1996-2026 The Tetris Company", WHITE, font_med),
            ("", WHITE, font_small),
            ("(C) 1989-2026 Nintendo", WHITE, font_med),
            ("", WHITE, font_small),
            ("(C) 1999-2026 Samsoft", WHITE, font_med),
            ("", WHITE, font_small),
            ("", WHITE, font_small),
            ("ORIGINAL CONCEPT", YELLOW, font_med),
            ("Tetris (C) 1984 Alexey Pajitnov", WHITE, font_small),
            ("", WHITE, font_small),
            ("MUSIC", YELLOW, font_med),
            ("Type A - Korobeiniki (Traditional)", WHITE, font_small),
            ("Type B - Russian Folk Melody", WHITE, font_small),
            ("Type C - Bradinsky", WHITE, font_small),
            ("", WHITE, font_small),
            ("", WHITE, font_small),
            ("SPECIAL THANKS", YELLOW, font_med),
            ("All Tetris fans worldwide", WHITE, font_small),
        ]
        
        for text_str, color, text_font in credits_data:
            if text_str:
                text = text_font.render(text_str, True, color)
                text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
                screen.blit(text, text_rect)
            y += 28
        
        # Animated border tetrominos
        t = self.animation_timer
        for i, color in enumerate([CYAN, RED, GREEN, YELLOW, BLUE, ORANGE, PURPLE]):
            x = 30 + (i * 20 + t * 2) % (SCREEN_WIDTH - 60)
            pygame.draw.rect(screen, color, (x, SCREEN_HEIGHT - 70, 15, 15))
            pygame.draw.rect(screen, color, (SCREEN_WIDTH - x - 15, 110, 15, 15))
        
        inst = font_small.render("Press ENTER or ESC to return", True, GRAY)
        inst_rect = inst.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
        screen.blit(inst, inst_rect)

# ============== MAIN GAME LOOP ==============

def main():
    """Main entry point"""
    sound_mgr = SoundManager()
    menu = Menu(sound_mgr)
    renderer = Renderer()
    game = None
    
    state = 'menu'  # menu, playing, gameover
    
    # Soft drop repeat handling
    soft_drop_held = False
    
    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            
            if state == 'menu':
                result = menu.handle_input(event)
                if result:
                    action, data = result
                    if action == 'start':
                        game = TetrisGame(data)
                        state = 'playing'
                    elif action == 'quit':
                        running = False
            
            elif state == 'playing':
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        sound_mgr.stop_music()
                        state = 'menu'
                        menu.selected = 0
                    elif event.key == K_p:
                        game.paused = not game.paused
                        sound_mgr.play_sfx('pause')
                        if game.paused:
                            sound_mgr.stop_music()
                    elif not game.paused and not game.game_over:
                        if event.key == K_UP or event.key == K_x:
                            if game.rotate(1):
                                sound_mgr.play_sfx('rotate')
                        elif event.key == K_z:
                            if game.rotate(-1):
                                sound_mgr.play_sfx('rotate')
                        elif event.key == K_SPACE:
                            game.hard_drop()
                            sound_mgr.play_sfx('drop')
                        elif event.key == K_c or event.key == K_LSHIFT:
                            if game.hold():
                                sound_mgr.play_sfx('move')
                        elif event.key == K_m:
                            ost = sound_mgr.cycle_ost()
                        elif event.key == K_DOWN:
                            soft_drop_held = True
                
                elif event.type == KEYUP:
                    if event.key == K_DOWN:
                        soft_drop_held = False
            
            elif state == 'gameover':
                if event.type == KEYDOWN:
                    if event.key == K_RETURN:
                        game = TetrisGame(menu.start_level)
                        state = 'playing'
                    elif event.key == K_ESCAPE:
                        state = 'menu'
                        menu.selected = 0
        
        # Update
        if state == 'menu':
            menu.draw()
        
        elif state == 'playing':
            if not game.paused and not game.game_over:
                # Handle held keys
                keys = pygame.key.get_pressed()
                game.handle_das(keys)
                
                # Soft drop
                if soft_drop_held:
                    game.soft_drop()
                
                # Game update
                lines_cleared = game.update()
                if lines_cleared:
                    if lines_cleared == 4:
                        sound_mgr.play_sfx('tetris')
                    else:
                        sound_mgr.play_sfx('clear')
                
                # Check for game over
                if game.game_over:
                    sound_mgr.play_sfx('gameover')
                    sound_mgr.stop_music()
                    menu.update_high_scores(game.score, game.level)
                    state = 'gameover'
                else:
                    # Music plays during active gameplay - auto restarts on unpause
                    sound_mgr.update_music()
            
            # Draw
            screen.fill(BLACK)
            renderer.draw_board(game)
            renderer.draw_piece(game)
            renderer.draw_stats(game, sound_mgr)
            renderer.draw_controls()
            
            if game.paused:
                renderer.draw_pause()
        
        elif state == 'gameover':
            screen.fill(BLACK)
            renderer.draw_board(game)
            renderer.draw_stats(game, sound_mgr)
            renderer.draw_game_over(game)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
