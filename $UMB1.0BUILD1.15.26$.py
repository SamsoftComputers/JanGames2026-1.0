#!/usr/bin/env python3
"""
Super Mario Bros Style Game Engine
by Flames / Team Flames / Samsoft
Complete single-file implementation with authentic NES physics and audio
"""

import pygame
import array
import random
import math

# =============================================================================
# SOUND ENGINE (User's exact OST, 10 bugs fixed)
# =============================================================================

class SoundEngine:
    def __init__(self):
        pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
        self.sample_rate = 44100
        self.sounds = {}
        self.note_cache = {}
        self.music_queue = []
        self.current_note_index = 0
        self.music_timer = 0
        self.playing_music = False
        self.music_channel = pygame.mixer.Channel(0)

        self.NOTE_FREQS = {
            'C3': 131, 'C#3': 139, 'D3': 147, 'D#3': 156, 'E3': 165,
            'F3': 175, 'F#3': 185, 'G3': 196, 'G#3': 208, 'A3': 220,
            'A#3': 233, 'B3': 247, 'C4': 262, 'C#4': 277, 'D4': 294,
            'D#4': 311, 'E4': 330, 'F4': 349, 'F#4': 370, 'G4': 392,
            'G#4': 415, 'A4': 440, 'A#4': 466, 'B4': 494, 'C5': 523,
            'C#5': 554, 'D5': 587, 'D#5': 622, 'E5': 659, 'F5': 698,
            'F#5': 740, 'G5': 784, 'G#5': 831, 'A5': 880, 'A#5': 932,
            'B5': 988, 'rest': 0
        }

        # Define Tracks (Note, Duration in Seconds) - FULL SMB1 OST
        self.TRACKS = {
            "1-1": [ # Full Overworld Theme
                # Intro
                ('E5', 0.125), ('E5', 0.125), ('rest', 0.125), ('E5', 0.125), 
                ('rest', 0.125), ('C5', 0.125), ('E5', 0.25),
                ('G5', 0.25), ('rest', 0.25), ('G4', 0.25), ('rest', 0.25),
                
                # Part A
                ('C5', 0.375), ('G4', 0.125), ('rest', 0.125), ('E4', 0.25), ('rest', 0.125),
                ('A4', 0.25), ('B4', 0.25), ('A#4', 0.125), ('A4', 0.25),
                ('G4', 0.166), ('E5', 0.166), ('G5', 0.166), 
                ('A5', 0.25), ('F5', 0.125), ('G5', 0.125),
                ('rest', 0.125), ('E5', 0.25), ('C5', 0.125), ('D5', 0.125), ('B4', 0.25),
                ('rest', 0.25),
                
                # Part A repeat
                ('C5', 0.375), ('G4', 0.125), ('rest', 0.125), ('E4', 0.25), ('rest', 0.125),
                ('A4', 0.25), ('B4', 0.25), ('A#4', 0.125), ('A4', 0.25),
                ('G4', 0.166), ('E5', 0.166), ('G5', 0.166), 
                ('A5', 0.25), ('F5', 0.125), ('G5', 0.125),
                ('rest', 0.125), ('E5', 0.25), ('C5', 0.125), ('D5', 0.125), ('B4', 0.25),
                ('rest', 0.25),
                
                # Part B
                ('rest', 0.125), ('G5', 0.125), ('F#5', 0.125), ('F5', 0.125), ('D#5', 0.25),
                ('E5', 0.125), ('rest', 0.125), ('G#4', 0.125), ('A4', 0.125), ('C5', 0.125),
                ('rest', 0.125), ('A4', 0.125), ('C5', 0.125), ('D5', 0.125),
                ('rest', 0.125), ('G5', 0.125), ('F#5', 0.125), ('F5', 0.125), ('D#5', 0.25),
                ('E5', 0.125), ('rest', 0.125), ('C6', 0.125), ('rest', 0.125), ('C6', 0.125), ('C6', 0.25),
                ('rest', 0.375),
                
                # Part B repeat
                ('rest', 0.125), ('G5', 0.125), ('F#5', 0.125), ('F5', 0.125), ('D#5', 0.25),
                ('E5', 0.125), ('rest', 0.125), ('G#4', 0.125), ('A4', 0.125), ('C5', 0.125),
                ('rest', 0.125), ('A4', 0.125), ('C5', 0.125), ('D5', 0.125),
                ('rest', 0.125), ('D#5', 0.25), ('rest', 0.125), ('D5', 0.25),
                ('C5', 0.5), ('rest', 0.5),
                
                # Part C
                ('C5', 0.125), ('C5', 0.125), ('rest', 0.125), ('C5', 0.125),
                ('rest', 0.125), ('C5', 0.125), ('D5', 0.25),
                ('E5', 0.125), ('C5', 0.25), ('A4', 0.125), ('G4', 0.5),
                ('rest', 0.25),
                ('C5', 0.125), ('C5', 0.125), ('rest', 0.125), ('C5', 0.125),
                ('rest', 0.125), ('C5', 0.125), ('D5', 0.125), ('E5', 0.125),
                ('rest', 0.75),
                
                # Part C variation
                ('C5', 0.125), ('C5', 0.125), ('rest', 0.125), ('C5', 0.125),
                ('rest', 0.125), ('C5', 0.125), ('D5', 0.25),
                ('E5', 0.125), ('C5', 0.25), ('A4', 0.125), ('G4', 0.5),
                ('rest', 0.25),
                ('E5', 0.125), ('E5', 0.125), ('rest', 0.125), ('E5', 0.125),
                ('rest', 0.125), ('C5', 0.125), ('E5', 0.25),
                ('G5', 0.25), ('rest', 0.25), ('G4', 0.25), ('rest', 0.25),
            ],
            
            "1-2": [ # Full Underground Theme
                # Main loop (repeats)
                ('C4', 0.1), ('C5', 0.1), ('A3', 0.1), ('A4', 0.1), 
                ('A#3', 0.1), ('A#4', 0.1), ('rest', 0.3),
                ('C4', 0.1), ('C5', 0.1), ('A3', 0.1), ('A4', 0.1), 
                ('A#3', 0.1), ('A#4', 0.1), ('rest', 0.3),
                ('F3', 0.1), ('F4', 0.1), ('D3', 0.1), ('D4', 0.1), 
                ('D#3', 0.1), ('D#4', 0.1), ('rest', 0.3),
                ('F3', 0.1), ('F4', 0.1), ('D3', 0.1), ('D4', 0.1), 
                ('D#3', 0.1), ('D#4', 0.1), ('rest', 0.3),
                
                # Variation
                ('C4', 0.1), ('C5', 0.1), ('A3', 0.1), ('A4', 0.1), 
                ('A#3', 0.1), ('A#4', 0.1), ('rest', 0.3),
                ('C4', 0.1), ('C5', 0.1), ('A3', 0.1), ('A4', 0.1), 
                ('A#3', 0.1), ('A#4', 0.1), ('rest', 0.3),
                ('F3', 0.2), ('F4', 0.2), ('F3', 0.2), ('F4', 0.2),
                ('rest', 0.4),
                
                # Bridge section
                ('D#4', 0.15), ('D4', 0.15), ('C4', 0.3),
                ('rest', 0.2),
                ('D#4', 0.15), ('D4', 0.15), ('C4', 0.3),
                ('rest', 0.2),
                ('D#4', 0.15), ('D4', 0.15), ('C4', 0.15), ('D4', 0.15),
                ('D#4', 0.3), ('rest', 0.2),
                
                # Return to main
                ('C4', 0.1), ('C5', 0.1), ('A3', 0.1), ('A4', 0.1), 
                ('A#3', 0.1), ('A#4', 0.1), ('rest', 0.3),
                ('C4', 0.1), ('C5', 0.1), ('A3', 0.1), ('A4', 0.1), 
                ('A#3', 0.1), ('A#4', 0.1), ('rest', 0.3),
                ('F3', 0.1), ('F4', 0.1), ('D3', 0.1), ('D4', 0.1), 
                ('D#3', 0.1), ('D#4', 0.1), ('rest', 0.3),
                ('F3', 0.1), ('F4', 0.1), ('D3', 0.1), ('D4', 0.1), 
                ('D#3', 0.1), ('D#4', 0.1), ('rest', 0.3),
            ],
            
            "8-4": [ # Full Castle Theme
                # Main arpeggio pattern A
                ('G3', 0.07), ('A#3', 0.07), ('D4', 0.07), ('G4', 0.07), ('A#4', 0.07), ('D5', 0.07),
                ('G3', 0.07), ('A#3', 0.07), ('D4', 0.07), ('G4', 0.07), ('A#4', 0.07), ('D5', 0.07),
                ('G3', 0.07), ('A#3', 0.07), ('D4', 0.07), ('G4', 0.07), ('A#4', 0.07), ('D5', 0.07),
                ('G3', 0.07), ('A#3', 0.07), ('D4', 0.07), ('G4', 0.07), ('A#4', 0.07), ('D5', 0.07),
                
                # Pattern B (diminished)
                ('F#3', 0.07), ('A3', 0.07), ('C4', 0.07), ('F#4', 0.07), ('A4', 0.07), ('C5', 0.07),
                ('F#3', 0.07), ('A3', 0.07), ('C4', 0.07), ('F#4', 0.07), ('A4', 0.07), ('C5', 0.07),
                ('F#3', 0.07), ('A3', 0.07), ('C4', 0.07), ('F#4', 0.07), ('A4', 0.07), ('C5', 0.07),
                ('F#3', 0.07), ('A3', 0.07), ('C4', 0.07), ('F#4', 0.07), ('A4', 0.07), ('C5', 0.07),
                
                # Pattern C
                ('F3', 0.07), ('G#3', 0.07), ('B3', 0.07), ('F4', 0.07), ('G#4', 0.07), ('B4', 0.07),
                ('F3', 0.07), ('G#3', 0.07), ('B3', 0.07), ('F4', 0.07), ('G#4', 0.07), ('B4', 0.07),
                ('F3', 0.07), ('G#3', 0.07), ('B3', 0.07), ('F4', 0.07), ('G#4', 0.07), ('B4', 0.07),
                ('F3', 0.07), ('G#3', 0.07), ('B3', 0.07), ('F4', 0.07), ('G#4', 0.07), ('B4', 0.07),
                
                # Pattern D
                ('E3', 0.07), ('G3', 0.07), ('A#3', 0.07), ('E4', 0.07), ('G4', 0.07), ('A#4', 0.07),
                ('E3', 0.07), ('G3', 0.07), ('A#3', 0.07), ('E4', 0.07), ('G4', 0.07), ('A#4', 0.07),
                ('E3', 0.07), ('G3', 0.07), ('A#3', 0.07), ('E4', 0.07), ('G4', 0.07), ('A#4', 0.07),
                ('E3', 0.07), ('G3', 0.07), ('A#3', 0.07), ('E4', 0.07), ('G4', 0.07), ('A#4', 0.07),
                
                # Back to A
                ('G3', 0.07), ('A#3', 0.07), ('D4', 0.07), ('G4', 0.07), ('A#4', 0.07), ('D5', 0.07),
                ('G3', 0.07), ('A#3', 0.07), ('D4', 0.07), ('G4', 0.07), ('A#4', 0.07), ('D5', 0.07),
                ('G3', 0.07), ('A#3', 0.07), ('D4', 0.07), ('G4', 0.07), ('A#4', 0.07), ('D5', 0.07),
                ('G3', 0.07), ('A#3', 0.07), ('D4', 0.07), ('G4', 0.07), ('A#4', 0.07), ('D5', 0.07),
                
                # Pattern B again
                ('F#3', 0.07), ('A3', 0.07), ('C4', 0.07), ('F#4', 0.07), ('A4', 0.07), ('C5', 0.07),
                ('F#3', 0.07), ('A3', 0.07), ('C4', 0.07), ('F#4', 0.07), ('A4', 0.07), ('C5', 0.07),
                ('F#3', 0.07), ('A3', 0.07), ('C4', 0.07), ('F#4', 0.07), ('A4', 0.07), ('C5', 0.07),
                ('F#3', 0.07), ('A3', 0.07), ('C4', 0.07), ('F#4', 0.07), ('A4', 0.07), ('C5', 0.07),
                
                # Ending phrase
                ('G4', 0.15), ('rest', 0.07), ('G4', 0.15), ('rest', 0.07),
                ('G4', 0.07), ('A4', 0.07), ('A#4', 0.07), ('B4', 0.07),
                ('C5', 0.3), ('rest', 0.2),
                
                # Return to main
                ('G3', 0.07), ('A#3', 0.07), ('D4', 0.07), ('G4', 0.07), ('A#4', 0.07), ('D5', 0.07),
                ('G3', 0.07), ('A#3', 0.07), ('D4', 0.07), ('G4', 0.07), ('A#4', 0.07), ('D5', 0.07),
                ('F#3', 0.07), ('A3', 0.07), ('C4', 0.07), ('F#4', 0.07), ('A4', 0.07), ('C5', 0.07),
                ('F#3', 0.07), ('A3', 0.07), ('C4', 0.07), ('F#4', 0.07), ('A4', 0.07), ('C5', 0.07),
            ]
        }
        
        # Add higher octave notes
        self.NOTE_FREQS['C6'] = 1047
        self.NOTE_FREQS['D6'] = 1175
        self.NOTE_FREQS['E6'] = 1319
        self.NOTE_FREQS['F#5'] = 740

        self.generate_sfx()

    def make_wave(self, freq_start, freq_end, duration, vol, wave_type="square"):
        n_samples = int(self.sample_rate * duration)
        if n_samples == 0:
            n_samples = 1
        
        cache_key = (freq_start, duration, wave_type, vol)
        if freq_start == freq_end and cache_key in self.note_cache:
            return self.note_cache[cache_key]

        buf = array.array('h', [0] * n_samples)
        amplitude = int(32767 * vol)
        
        for i in range(n_samples):
            t = i / n_samples
            freq = freq_start + (freq_end - freq_start) * t
            if freq <= 0:
                freq = 1
            period = self.sample_rate / freq
            if period < 1:
                period = 1
            phase = (i % int(period)) / period
            
            if wave_type == "square":
                val = amplitude if phase < 0.5 else -amplitude
            elif wave_type == "noise":
                val = random.randint(-amplitude, amplitude)
            elif wave_type == "triangle":
                val = int(amplitude * (2 * abs(2 * phase - 1) - 1))
            else:
                val = 0
            
            if i < 100:
                val = int(val * (i / 100))
            elif i > n_samples - 100:
                val = int(val * ((n_samples - i) / 100))
            
            buf[i] = max(-32767, min(32767, int(val)))
            
        snd = pygame.mixer.Sound(buffer=buf)
        if freq_start == freq_end:
            self.note_cache[cache_key] = snd
        return snd

    def generate_sfx(self):
        self.sounds["jump"] = self.make_wave(150, 300, 0.2, 0.15, "square")
        self.sounds["coin"] = self.make_wave(900, 1200, 0.1, 0.1, "square")
        self.sounds["stomp"] = self.make_wave(100, 50, 0.1, 0.15, "noise")
        self.sounds["bump"] = self.make_wave(150, 100, 0.1, 0.15, "square")
        self.sounds["break"] = self.make_wave(200, 100, 0.15, 0.2, "noise")
        self.sounds["die"] = self.make_wave(500, 100, 0.5, 0.2, "square")
        self.sounds["warp"] = self.make_wave(100, 50, 0.8, 0.15, "triangle")
        self.sounds["powerup"] = self.make_wave(200, 600, 0.3, 0.12, "square")
        self.sounds["flagpole"] = self.make_wave(400, 800, 0.8, 0.15, "square")
        self.sounds["clear"] = self.make_wave(523, 784, 0.3, 0.12, "square")  # C5 to G5

    def play(self, name):
        if name in self.sounds:
            self.sounds[name].play()
            
    def play_music(self, track_name, force=False):
        try:
            level_part = int(track_name.split("-")[1])
        except (IndexError, ValueError):
            level_part = 1

        if level_part == 2:
            key = "1-2"
        elif level_part == 4:
            key = "8-4"
        else:
            key = "1-1"
        
        # Don't restart if same track already playing (unless forced)
        if not force and hasattr(self, 'current_track') and self.current_track == key and self.playing_music:
            return
        
        self.music_queue = self.TRACKS.get(key, self.TRACKS["1-1"])
        self.current_note_index = 0
        self.music_timer = 0.01  # Small initial delay
        self.playing_music = True
        self.current_track = key  # Track which music is playing
        
    def stop_music(self):
        self.playing_music = False
        self.music_channel.stop()

    def update_music(self, dt):
        if not self.playing_music or not self.music_queue:
            return
        
        self.music_timer -= dt
        if self.music_timer <= 0:
            note, duration = self.music_queue[self.current_note_index]
            
            if note != 'rest':
                freq = self.NOTE_FREQS.get(note, 440)
                # Cache notes to prevent regenerating
                cache_key = (freq, duration)
                if cache_key not in self.note_cache:
                    self.note_cache[cache_key] = self.make_wave(freq, freq, duration * 0.85, 0.1, "square")
                self.music_channel.play(self.note_cache[cache_key])
            
            self.music_timer = duration
            self.current_note_index += 1
            
            # Loop back to start when track ends
            if self.current_note_index >= len(self.music_queue):
                self.current_note_index = 0


# =============================================================================
# CONSTANTS
# =============================================================================

TILE_SIZE = 16
SCREEN_WIDTH = 256
SCREEN_HEIGHT = 240
SCALE = 3

COLORS = {
    'sky': (92, 148, 252),
    'ground': (200, 76, 12),
    'brick': (200, 76, 12),
    'block': (252, 152, 56),
    'pipe': (0, 168, 0),
    'mario_red': (200, 76, 12),
    'mario_skin': (252, 152, 56),
    'goomba': (148, 80, 48),
    'koopa_green': (0, 168, 0),
    'coin': (252, 188, 60),
    'black': (0, 0, 0),
    'white': (252, 252, 252),
    'underground_bg': (0, 0, 0),
    'castle_bg': (0, 0, 0),
    'lava': (208, 56, 0),
}

GRAVITY = 0.2  # Lower base gravity for floatier feel
GRAVITY_FALL = 0.45  # High gravity when falling or button released
MAX_FALL_SPEED = 4.5
WALK_ACCEL = 0.098
RUN_ACCEL = 0.14
FRICTION = 0.1  # Lower friction = more slidey like SMB1
AIR_FRICTION = 0.02  # Less control in air
MAX_WALK_SPEED = 1.5
MAX_RUN_SPEED = 2.8
JUMP_VELOCITY_WALK = -5.0  # Good jump when walking
JUMP_VELOCITY_RUN = -5.8  # High jump when running (SMB1 style!)
JUMP_HOLD_FRAMES = 20  # Max frames to hold jump for height


# =============================================================================
# BITMAP FONT
# =============================================================================

class BitmapFont:
    def __init__(self):
        self.chars = {}
        self._generate_font()
    
    def _generate_font(self):
        font_data = {
            '0': [0x3C,0x66,0x6E,0x76,0x66,0x66,0x3C,0x00],
            '1': [0x18,0x38,0x18,0x18,0x18,0x18,0x7E,0x00],
            '2': [0x3C,0x66,0x06,0x0C,0x18,0x30,0x7E,0x00],
            '3': [0x3C,0x66,0x06,0x1C,0x06,0x66,0x3C,0x00],
            '4': [0x0C,0x1C,0x3C,0x6C,0x7E,0x0C,0x0C,0x00],
            '5': [0x7E,0x60,0x7C,0x06,0x06,0x66,0x3C,0x00],
            '6': [0x1C,0x30,0x60,0x7C,0x66,0x66,0x3C,0x00],
            '7': [0x7E,0x06,0x0C,0x18,0x30,0x30,0x30,0x00],
            '8': [0x3C,0x66,0x66,0x3C,0x66,0x66,0x3C,0x00],
            '9': [0x3C,0x66,0x66,0x3E,0x06,0x0C,0x38,0x00],
            'A': [0x18,0x3C,0x66,0x66,0x7E,0x66,0x66,0x00],
            'B': [0x7C,0x66,0x66,0x7C,0x66,0x66,0x7C,0x00],
            'C': [0x3C,0x66,0x60,0x60,0x60,0x66,0x3C,0x00],
            'D': [0x78,0x6C,0x66,0x66,0x66,0x6C,0x78,0x00],
            'E': [0x7E,0x60,0x60,0x7C,0x60,0x60,0x7E,0x00],
            'F': [0x7E,0x60,0x60,0x7C,0x60,0x60,0x60,0x00],
            'G': [0x3C,0x66,0x60,0x6E,0x66,0x66,0x3E,0x00],
            'H': [0x66,0x66,0x66,0x7E,0x66,0x66,0x66,0x00],
            'I': [0x7E,0x18,0x18,0x18,0x18,0x18,0x7E,0x00],
            'J': [0x3E,0x0C,0x0C,0x0C,0x0C,0x6C,0x38,0x00],
            'K': [0x66,0x6C,0x78,0x70,0x78,0x6C,0x66,0x00],
            'L': [0x60,0x60,0x60,0x60,0x60,0x60,0x7E,0x00],
            'M': [0x63,0x77,0x7F,0x6B,0x63,0x63,0x63,0x00],
            'N': [0x66,0x76,0x7E,0x7E,0x6E,0x66,0x66,0x00],
            'O': [0x3C,0x66,0x66,0x66,0x66,0x66,0x3C,0x00],
            'P': [0x7C,0x66,0x66,0x7C,0x60,0x60,0x60,0x00],
            'Q': [0x3C,0x66,0x66,0x66,0x6A,0x6C,0x36,0x00],
            'R': [0x7C,0x66,0x66,0x7C,0x6C,0x66,0x66,0x00],
            'S': [0x3C,0x66,0x60,0x3C,0x06,0x66,0x3C,0x00],
            'T': [0x7E,0x18,0x18,0x18,0x18,0x18,0x18,0x00],
            'U': [0x66,0x66,0x66,0x66,0x66,0x66,0x3C,0x00],
            'V': [0x66,0x66,0x66,0x66,0x66,0x3C,0x18,0x00],
            'W': [0x63,0x63,0x63,0x6B,0x7F,0x77,0x63,0x00],
            'X': [0x66,0x66,0x3C,0x18,0x3C,0x66,0x66,0x00],
            'Y': [0x66,0x66,0x66,0x3C,0x18,0x18,0x18,0x00],
            'Z': [0x7E,0x06,0x0C,0x18,0x30,0x60,0x7E,0x00],
            '-': [0x00,0x00,0x00,0x7E,0x00,0x00,0x00,0x00],
            'x': [0x00,0x00,0x66,0x3C,0x18,0x3C,0x66,0x00],
            ' ': [0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00],
        }
        
        for char, data in font_data.items():
            surf = pygame.Surface((8, 8), pygame.SRCALPHA)
            for y, row in enumerate(data):
                for x in range(8):
                    if row & (0x80 >> x):
                        surf.set_at((x, y), COLORS['white'])
            self.chars[char] = surf
    
    def render(self, text, color=None):
        text = str(text).upper()
        width = len(text) * 8
        surf = pygame.Surface((width, 8), pygame.SRCALPHA)
        
        for i, char in enumerate(text):
            if char in self.chars:
                char_surf = self.chars[char]
                surf.blit(char_surf, (i * 8, 0))
        
        return surf


# =============================================================================
# SPRITE RENDERER
# =============================================================================

class SpriteRenderer:
    def __init__(self):
        self.cache = {}
    
    def get_sprite(self, name, frame=0, facing_right=True, big=False):
        key = (name, frame, facing_right, big)
        if key not in self.cache:
            self.cache[key] = self._render_sprite(name, frame, facing_right, big)
        return self.cache[key]
    
    def _render_sprite(self, name, frame, facing_right, big):
        if name == 'mario':
            return self._render_mario(frame, facing_right, big)
        elif name == 'goomba':
            return self._render_goomba(frame)
        elif name == 'koopa':
            return self._render_koopa(frame, facing_right)
        elif name == 'coin':
            return self._render_coin(frame)
        elif name == 'mushroom':
            return self._render_mushroom()
        elif name == 'firebar':
            return self._render_firebar(frame)
        elif name == 'bowser':
            return self._render_bowser(frame, facing_right)
        return pygame.Surface((16, 16), pygame.SRCALPHA)
    
    def _render_mario(self, frame, facing_right, big):
        h = 32 if big else 16
        surf = pygame.Surface((16, h), pygame.SRCALPHA)
        
        if not big:
            # Small Mario (16px tall)
            # Hat
            pygame.draw.rect(surf, COLORS['mario_red'], (3, 0, 10, 3))
            # Hair
            pygame.draw.rect(surf, (80, 48, 0), (2, 3, 3, 2))
            # Face
            pygame.draw.rect(surf, COLORS['mario_skin'], (5, 3, 7, 5))
            pygame.draw.rect(surf, COLORS['mario_skin'], (2, 5, 3, 3))
            # Eye
            pygame.draw.rect(surf, COLORS['black'], (9, 4, 2, 2))
            # Mustache
            pygame.draw.rect(surf, (80, 48, 0), (6, 6, 6, 2))
            # Body/Shirt
            pygame.draw.rect(surf, COLORS['mario_red'], (2, 8, 12, 4))
            # Overall straps
            pygame.draw.rect(surf, (0, 0, 168), (4, 8, 2, 4))
            pygame.draw.rect(surf, (0, 0, 168), (10, 8, 2, 4))
            # Pants
            pygame.draw.rect(surf, (0, 0, 168), (2, 12, 12, 2))
            # Feet
            if frame % 2 == 0:
                pygame.draw.rect(surf, (80, 48, 0), (1, 14, 5, 2))
                pygame.draw.rect(surf, (80, 48, 0), (10, 14, 5, 2))
            else:
                pygame.draw.rect(surf, (80, 48, 0), (2, 14, 5, 2))
                pygame.draw.rect(surf, (80, 48, 0), (9, 14, 5, 2))
        else:
            # Big Mario (32px tall)
            # Hat
            pygame.draw.rect(surf, COLORS['mario_red'], (3, 0, 10, 5))
            # Hair
            pygame.draw.rect(surf, (80, 48, 0), (1, 5, 4, 3))
            # Face
            pygame.draw.rect(surf, COLORS['mario_skin'], (5, 5, 9, 8))
            pygame.draw.rect(surf, COLORS['mario_skin'], (1, 8, 4, 5))
            # Eye
            pygame.draw.rect(surf, COLORS['black'], (10, 6, 2, 3))
            # Mustache
            pygame.draw.rect(surf, (80, 48, 0), (6, 10, 7, 3))
            # Body/Shirt
            pygame.draw.rect(surf, COLORS['mario_red'], (1, 13, 14, 6))
            # Overall straps
            pygame.draw.rect(surf, (0, 0, 168), (3, 13, 3, 6))
            pygame.draw.rect(surf, (0, 0, 168), (10, 13, 3, 6))
            # Belt/button
            pygame.draw.rect(surf, COLORS['coin'], (6, 15, 4, 2))
            # Pants/Overalls
            pygame.draw.rect(surf, (0, 0, 168), (1, 19, 14, 9))
            # Legs separation
            pygame.draw.rect(surf, (0, 0, 0, 0), (7, 24, 2, 8))
            # Feet
            if frame % 2 == 0:
                pygame.draw.rect(surf, (80, 48, 0), (0, 28, 7, 4))
                pygame.draw.rect(surf, (80, 48, 0), (9, 28, 7, 4))
            else:
                pygame.draw.rect(surf, (80, 48, 0), (1, 28, 6, 4))
                pygame.draw.rect(surf, (80, 48, 0), (9, 28, 6, 4))
        
        if not facing_right:
            surf = pygame.transform.flip(surf, True, False)
        
        return surf
    
    def _render_goomba(self, frame):
        surf = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, COLORS['goomba'], (1, 2, 14, 12))
        if frame == 0:
            pygame.draw.ellipse(surf, COLORS['black'], (0, 12, 6, 4))
            pygame.draw.ellipse(surf, COLORS['black'], (10, 12, 6, 4))
        else:
            pygame.draw.ellipse(surf, COLORS['black'], (1, 12, 6, 4))
            pygame.draw.ellipse(surf, COLORS['black'], (9, 12, 6, 4))
        pygame.draw.ellipse(surf, COLORS['white'], (2, 4, 5, 5))
        pygame.draw.ellipse(surf, COLORS['white'], (9, 4, 5, 5))
        pygame.draw.rect(surf, COLORS['black'], (4, 6, 2, 2))
        pygame.draw.rect(surf, COLORS['black'], (10, 6, 2, 2))
        return surf
    
    def _render_koopa(self, frame, facing_right):
        surf = pygame.Surface((16, 24), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, COLORS['koopa_green'], (1, 8, 14, 14))
        pygame.draw.ellipse(surf, (252, 252, 200), (3, 10, 10, 10))
        pygame.draw.ellipse(surf, COLORS['koopa_green'], (2, 0, 10, 10))
        pygame.draw.ellipse(surf, COLORS['white'], (6, 2, 4, 4))
        pygame.draw.rect(surf, COLORS['black'], (8, 3, 2, 2))
        if frame == 0:
            pygame.draw.ellipse(surf, (252, 200, 168), (1, 20, 6, 4))
            pygame.draw.ellipse(surf, (252, 200, 168), (9, 20, 6, 4))
        else:
            pygame.draw.ellipse(surf, (252, 200, 168), (2, 20, 6, 4))
            pygame.draw.ellipse(surf, (252, 200, 168), (8, 20, 6, 4))
        if not facing_right:
            surf = pygame.transform.flip(surf, True, False)
        return surf
    
    def _render_coin(self, frame):
        surf = pygame.Surface((16, 16), pygame.SRCALPHA)
        widths = [10, 6, 2, 6]
        w = widths[frame % 4]
        x = (16 - w) // 2
        pygame.draw.ellipse(surf, COLORS['coin'], (x, 2, w, 12))
        return surf
    
    def _render_mushroom(self):
        surf = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, (228, 0, 0), (0, 0, 16, 12))
        pygame.draw.circle(surf, COLORS['white'], (4, 4), 3)
        pygame.draw.circle(surf, COLORS['white'], (12, 4), 3)
        pygame.draw.rect(surf, COLORS['white'], (4, 10, 8, 6))
        return surf
    
    def _render_firebar(self, frame):
        surf = pygame.Surface((8, 8), pygame.SRCALPHA)
        colors = [(228, 0, 0), (252, 152, 56), (252, 188, 60)]
        c = colors[frame % 3]
        pygame.draw.circle(surf, c, (4, 4), 4)
        return surf
    
    def _render_bowser(self, frame, facing_right):
        surf = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, COLORS['koopa_green'], (4, 8, 24, 20))
        pygame.draw.ellipse(surf, (100, 60, 20), (6, 10, 20, 16))
        for i in range(3):
            pygame.draw.polygon(surf, (252, 152, 56), [(10 + i*6, 10), (13 + i*6, 2), (16 + i*6, 10)])
        pygame.draw.ellipse(surf, COLORS['koopa_green'], (0, 4, 14, 14))
        pygame.draw.ellipse(surf, COLORS['white'], (6, 6, 6, 5))
        pygame.draw.rect(surf, (228, 0, 0), (9, 7, 3, 3))
        if not facing_right:
            surf = pygame.transform.flip(surf, True, False)
        return surf


# =============================================================================
# TILE RENDERER
# =============================================================================

class TileRenderer:
    def __init__(self):
        self.cache = {}
    
    def get_tile(self, tile_type, frame=0):
        key = (tile_type, frame)
        if key not in self.cache:
            self.cache[key] = self._render_tile(tile_type, frame)
        return self.cache[key]
    
    def _render_tile(self, tile_type, frame):
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
        
        if tile_type == 'ground':
            surf.fill(COLORS['ground'])
            pygame.draw.line(surf, COLORS['black'], (0, 8), (16, 8), 1)
            pygame.draw.line(surf, COLORS['black'], (8, 0), (8, 8), 1)
            pygame.draw.line(surf, COLORS['black'], (4, 8), (4, 16), 1)
            pygame.draw.line(surf, COLORS['black'], (12, 8), (12, 16), 1)
        
        elif tile_type == 'brick':
            surf.fill(COLORS['brick'])
            pygame.draw.rect(surf, COLORS['black'], (0, 0, 16, 16), 1)
            pygame.draw.line(surf, COLORS['black'], (0, 7), (16, 7), 1)
            pygame.draw.line(surf, COLORS['black'], (7, 0), (7, 7), 1)
            pygame.draw.line(surf, COLORS['black'], (3, 8), (3, 16), 1)
            pygame.draw.line(surf, COLORS['black'], (11, 8), (11, 16), 1)
        
        elif tile_type == 'castle_brick':
            surf.fill((100, 100, 100))
            pygame.draw.rect(surf, COLORS['black'], (0, 0, 16, 16), 1)
            pygame.draw.line(surf, COLORS['black'], (0, 7), (16, 7), 1)
            pygame.draw.line(surf, COLORS['black'], (7, 0), (7, 7), 1)
            pygame.draw.line(surf, COLORS['black'], (3, 8), (3, 16), 1)
            pygame.draw.line(surf, COLORS['black'], (11, 8), (11, 16), 1)
        
        elif tile_type == 'question':
            colors = [(252, 152, 56), (200, 120, 40)]
            surf.fill(colors[frame % 2])
            pygame.draw.rect(surf, COLORS['black'], (0, 0, 16, 16), 1)
            pygame.draw.rect(surf, COLORS['black'], (5, 3, 6, 2))
            pygame.draw.rect(surf, COLORS['black'], (9, 3, 2, 5))
            pygame.draw.rect(surf, COLORS['black'], (5, 6, 6, 2))
            pygame.draw.rect(surf, COLORS['black'], (6, 11, 4, 2))
        
        elif tile_type == 'used':
            surf.fill((100, 60, 20))
            pygame.draw.rect(surf, COLORS['black'], (0, 0, 16, 16), 1)
        
        elif tile_type == 'pipe_top_left':
            surf.fill(COLORS['pipe'])
            pygame.draw.rect(surf, (0, 100, 0), (0, 0, 4, 16))
            pygame.draw.rect(surf, (100, 220, 100), (12, 0, 4, 16))
            pygame.draw.rect(surf, COLORS['black'], (0, 0, 16, 16), 1)
        
        elif tile_type == 'pipe_top_right':
            surf.fill(COLORS['pipe'])
            pygame.draw.rect(surf, (100, 220, 100), (0, 0, 4, 16))
            pygame.draw.rect(surf, (0, 100, 0), (12, 0, 4, 16))
            pygame.draw.rect(surf, COLORS['black'], (0, 0, 16, 16), 1)
        
        elif tile_type == 'pipe_left':
            surf.fill(COLORS['pipe'])
            pygame.draw.rect(surf, (0, 100, 0), (0, 0, 4, 16))
            pygame.draw.rect(surf, (100, 220, 100), (12, 0, 4, 16))
        
        elif tile_type == 'pipe_right':
            surf.fill(COLORS['pipe'])
            pygame.draw.rect(surf, (100, 220, 100), (0, 0, 4, 16))
            pygame.draw.rect(surf, (0, 100, 0), (12, 0, 4, 16))
        
        elif tile_type == 'flagpole':
            surf.fill(COLORS['sky'])
            surf.set_colorkey(COLORS['sky'])
            pygame.draw.rect(surf, (0, 100, 0), (7, 0, 2, 16))
        
        elif tile_type == 'flagball':
            surf.fill(COLORS['sky'])
            surf.set_colorkey(COLORS['sky'])
            pygame.draw.circle(surf, (0, 200, 0), (8, 8), 6)
        
        elif tile_type == 'lava':
            colors = [(208, 56, 0), (228, 92, 16)]
            surf.fill(colors[frame % 2])
        
        elif tile_type == 'bridge':
            surf.fill(COLORS['sky'])
            surf.set_colorkey(COLORS['sky'])
            pygame.draw.rect(surf, (139, 90, 43), (0, 0, 16, 8))
        
        return surf


# =============================================================================
# ENTITIES
# =============================================================================

class Entity:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.width = 16
        self.height = 16
        self.on_ground = False
        self.facing_right = True
        self.alive = True
        self.frame = 0
        self.frame_timer = 0
    
    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.width = 14
        self.height = 16
        self.big = False
        self.fire = False
        self.star = False
        self.star_timer = 0
        self.invincible_timer = 0
        self.coins = 0
        self.score = 0
        self.lives = 3
        self.dead = False
        self.death_timer = 0
        self.jumping = False
        self.jump_held = False
        self.jump_hold_timer = 0
        self.was_running = False  # Track if running when jump started
        self.walk_frame = 0
        self.walk_timer = 0
        self.win = False
        self.win_timer = 0
    
    @property
    def rect(self):
        # Hitbox extends to feet but inset on sides and top
        return pygame.Rect(self.x + 2, self.y + 2, self.width - 4, self.height - 2)
    
    def update(self, dt, level, keys, sound):
        if self.win:
            self.win_timer += dt
            if self.win_timer < 1:
                # Quick slide down
                self.y += 3
            elif self.win_timer < 2.5:
                # Walk right
                self.vx = 2
                self.x += self.vx
                self.walk_timer += dt
                if self.walk_timer > 0.08:
                    self.walk_timer = 0
                    self.walk_frame = (self.walk_frame + 1) % 3
            # After 2.5 sec, just wait for level transition
            return
        
        if self.dead:
            self.death_timer += dt
            self.vy += GRAVITY_FALL
            self.y += self.vy
            return
        
        if self.star_timer > 0:
            self.star_timer -= dt
            if self.star_timer <= 0:
                self.star = False
        
        if self.invincible_timer > 0:
            self.invincible_timer -= dt
        
        # Running state
        running = keys[pygame.K_z] or keys[pygame.K_LSHIFT]
        max_speed = MAX_RUN_SPEED if running else MAX_WALK_SPEED
        accel = RUN_ACCEL if running else WALK_ACCEL
        
        # Horizontal movement - less control in air (SMB1 style)
        if self.on_ground:
            friction = FRICTION
        else:
            friction = AIR_FRICTION
            accel *= 0.65  # Reduced air control
        
        if keys[pygame.K_LEFT]:
            self.vx -= accel
            self.facing_right = False
        elif keys[pygame.K_RIGHT]:
            self.vx += accel
            self.facing_right = True
        else:
            # Apply friction
            if self.on_ground:
                if self.vx > 0:
                    self.vx = max(0, self.vx - friction)
                elif self.vx < 0:
                    self.vx = min(0, self.vx + friction)
        
        self.vx = max(-max_speed, min(max_speed, self.vx))
        
        # === SMB1-STYLE JUMP ===
        jump_pressed = keys[pygame.K_x] or keys[pygame.K_SPACE]
        
        if jump_pressed:
            if self.on_ground and not self.jump_held:
                # Start jump - velocity depends on running!
                self.was_running = abs(self.vx) > MAX_WALK_SPEED * 0.8
                if self.was_running:
                    self.vy = JUMP_VELOCITY_RUN
                else:
                    self.vy = JUMP_VELOCITY_WALK
                self.on_ground = False
                self.jumping = True
                self.jump_held = True
                self.jump_hold_timer = 0
                sound.play('jump')
            elif self.jumping and self.vy < 0:
                # Holding jump while ascending - use low gravity for higher jump
                self.jump_hold_timer += 1
                if self.jump_hold_timer < JUMP_HOLD_FRAMES:
                    self.vy += GRAVITY  # Low gravity while holding
                else:
                    self.vy += GRAVITY_FALL  # Switch to high gravity after max hold
            else:
                # Falling - use high gravity
                self.vy += GRAVITY_FALL
        else:
            # Jump released
            self.jump_held = False
            if self.vy < 0:
                # Cut jump short - immediately use high gravity
                self.vy += GRAVITY_FALL
                # Optional: add extra downward force for snappier short hops
                if self.vy < -2:
                    self.vy *= 0.85
            else:
                self.vy += GRAVITY_FALL
        
        # Terminal velocity
        if self.vy > MAX_FALL_SPEED:
            self.vy = MAX_FALL_SPEED
        
        # Reset jumping flag when landing
        if self.on_ground:
            self.jumping = False
            self.jump_hold_timer = 0
        
        self.x += self.vx
        self._collide_horizontal(level, sound)
        
        self.y += self.vy
        self.on_ground = False
        self._collide_vertical(level, sound)
        
        if abs(self.vx) > 0.1:
            self.walk_timer += dt
            if self.walk_timer > 0.1:
                self.walk_timer = 0
                self.walk_frame = (self.walk_frame + 1) % 3
        else:
            self.walk_frame = 0
        
        if self.y > level.height * TILE_SIZE:
            self.die(sound)
        
        if self.x < level.camera_lock:
            self.x = level.camera_lock
    
    def _collide_horizontal(self, level, sound):
        for tile in level.get_tiles_near(self):
            if tile['solid'] and self.rect.colliderect(tile['rect']):
                if self.vx > 0:
                    self.x = tile['rect'].left - self.width
                elif self.vx < 0:
                    self.x = tile['rect'].right
                self.vx = 0
    
    def _collide_vertical(self, level, sound):
        for tile in level.get_tiles_near(self):
            if tile['solid'] and self.rect.colliderect(tile['rect']):
                if self.vy > 0:
                    self.y = tile['rect'].top - self.height
                    self.vy = 0
                    self.on_ground = True
                elif self.vy < 0:
                    self.y = tile['rect'].bottom
                    self.vy = 0
                    level.hit_block(tile['grid_x'], tile['grid_y'], self, sound)
    
    def collect_coin(self, sound):
        self.coins += 1
        self.score += 200
        sound.play('coin')
        if self.coins >= 100:
            self.coins = 0
            self.lives += 1
    
    def powerup(self, kind, sound):
        sound.play('powerup')
        if kind == 'mushroom':
            if not self.big:
                self.big = True
                self.height = 32
                self.y -= 16
        elif kind == 'flower':
            if not self.big:
                self.big = True
                self.height = 32
                self.y -= 16
            self.fire = True
        elif kind == 'star':
            self.star = True
            self.star_timer = 10.0
        self.score += 1000
    
    def take_damage(self, sound):
        if self.invincible_timer > 0 or self.star:
            return
        if self.big:
            self.big = False
            self.height = 16
            self.invincible_timer = 2.0
        else:
            self.die(sound)
    
    def die(self, sound):
        self.dead = True
        self.vy = JUMP_VELOCITY_WALK  # Death bounce
        self.lives -= 1
        sound.play('die')
        sound.stop_music()
    
    def draw(self, screen, camera_x, sprites):
        if self.dead and self.death_timer > 3:
            return
        if self.invincible_timer > 0 and int(self.invincible_timer * 10) % 2 == 0:
            return
        sprite = sprites.get_sprite('mario', self.walk_frame, self.facing_right, self.big)
        if self.star and int(pygame.time.get_ticks() / 50) % 2 == 0:
            sprite = sprite.copy()
            sprite.fill((255, 255, 0), special_flags=pygame.BLEND_ADD)
        screen.blit(sprite, (int(self.x - camera_x), int(self.y)))


class Enemy(Entity):
    def __init__(self, x, y, kind='goomba'):
        super().__init__(x, y)
        self.kind = kind
        self.vx = -0.5
        self.stomped = False
        self.stomp_timer = 0
        self.activated = False
        
        if kind == 'goomba':
            self.width = 16
            self.height = 16
            self.hitbox_inset = 3  # Smaller hitbox for fairer collision
        elif kind == 'koopa':
            self.width = 16
            self.height = 24
            self.hitbox_inset = 2
            self.shell = False
            self.shell_vx = 0
        elif kind == 'bowser':
            self.width = 32
            self.height = 32
            self.hitbox_inset = 4
            self.vx = -0.3
        else:
            self.hitbox_inset = 2
    
    @property
    def rect(self):
        # Inset hitbox - smaller on top for easier stomping
        inset = getattr(self, 'hitbox_inset', 2)
        top_inset = inset + 4  # Extra inset on top makes stomping easier
        return pygame.Rect(
            self.x + inset, 
            self.y + top_inset,  # Start lower
            self.width - inset * 2, 
            self.height - top_inset - inset  # Shorter
        )
    
    @property
    def head_rect(self):
        # Top portion for stomp detection
        inset = getattr(self, 'hitbox_inset', 2)
        return pygame.Rect(
            self.x + inset,
            self.y,
            self.width - inset * 2,
            self.height // 2
        )
    
    def update(self, dt, level, player, sound):
        if not self.alive:
            return
        
        if not self.activated:
            if player.x > self.x - SCREEN_WIDTH:
                self.activated = True
            else:
                return
        
        if self.stomped:
            self.stomp_timer += dt
            if self.stomp_timer > 0.5:
                self.alive = False
            return
        
        if self.kind == 'koopa' and self.shell:
            self.x += self.shell_vx
            return
        
        self.vy += GRAVITY_FALL
        if self.vy > MAX_FALL_SPEED:
            self.vy = MAX_FALL_SPEED
        
        self.x += self.vx
        
        for tile in level.get_tiles_near(self):
            if tile['solid'] and self.rect.colliderect(tile['rect']):
                self.vx *= -1
                self.x += self.vx * 2
                break
        
        self.y += self.vy
        for tile in level.get_tiles_near(self):
            if tile['solid'] and self.rect.colliderect(tile['rect']):
                if self.vy > 0:
                    self.y = tile['rect'].top - self.height
                    self.vy = 0
        
        self.frame_timer += dt
        if self.frame_timer > 0.2:
            self.frame_timer = 0
            self.frame = (self.frame + 1) % 2
        
        if self.y > level.height * TILE_SIZE:
            self.alive = False
    
    def stomp(self, player, sound):
        if self.kind == 'goomba':
            self.stomped = True
            sound.play('stomp')
            player.score += 100
            player.vy = -4  # Good bounce to clear the enemy
        elif self.kind == 'koopa':
            if not self.shell:
                self.shell = True
                self.height = 16
                self.y += 8
                player.vy = -4  # Good bounce
                sound.play('stomp')
            else:
                self.shell_vx = 4 if player.x < self.x else -4
                sound.play('bump')
            player.score += 100
    
    def draw(self, screen, camera_x, sprites):
        if not self.alive or not self.activated:
            return
        if self.stomped:
            pygame.draw.ellipse(screen, COLORS['goomba'], (int(self.x - camera_x), int(self.y + 12), 16, 4))
            return
        if self.kind == 'koopa' and self.shell:
            pygame.draw.ellipse(screen, COLORS['koopa_green'], (int(self.x - camera_x), int(self.y), 16, 16))
            return
        sprite = sprites.get_sprite(self.kind, self.frame, self.facing_right)
        screen.blit(sprite, (int(self.x - camera_x), int(self.y)))


class FireBar(Entity):
    def __init__(self, x, y, length=6, speed=2, clockwise=True):
        super().__init__(x, y)
        self.length = length
        self.speed = speed
        self.clockwise = clockwise
        self.angle = 0
    
    def update(self, dt, level, player, sound):
        direction = 1 if self.clockwise else -1
        self.angle += self.speed * direction * dt
        
        for i in range(self.length):
            dist = (i + 1) * 8
            fx = self.x + math.cos(self.angle) * dist
            fy = self.y + math.sin(self.angle) * dist
            fire_rect = pygame.Rect(fx - 4, fy - 4, 8, 8)
            if player.rect.colliderect(fire_rect):
                player.take_damage(sound)
    
    def draw(self, screen, camera_x, sprites):
        pygame.draw.rect(screen, (100, 100, 100), (int(self.x - camera_x - 4), int(self.y - 4), 8, 8))
        frame = int(pygame.time.get_ticks() / 100) % 3
        for i in range(self.length):
            dist = (i + 1) * 8
            fx = self.x + math.cos(self.angle) * dist
            fy = self.y + math.sin(self.angle) * dist
            sprite = sprites.get_sprite('firebar', frame)
            screen.blit(sprite, (int(fx - camera_x - 4), int(fy - 4)))


class Item(Entity):
    def __init__(self, x, y, kind='coin'):
        super().__init__(x, y)
        self.kind = kind
        self.spawn_y = y
        self.spawning = True
        self.spawn_timer = 0
        if kind == 'mushroom':
            self.vx = 1
    
    def update(self, dt, level, sound):
        if not self.alive:
            return
        
        if self.spawning:
            self.spawn_timer += dt
            self.y = self.spawn_y - (self.spawn_timer / 0.5) * 16
            if self.spawn_timer > 0.5:
                self.spawning = False
                self.y = self.spawn_y - 16
            return
        
        if self.kind == 'coin':
            self.frame_timer += dt
            if self.frame_timer > 0.1:
                self.frame_timer = 0
                self.frame = (self.frame + 1) % 4
            return
        
        self.vy += GRAVITY_FALL
        if self.vy > MAX_FALL_SPEED:
            self.vy = MAX_FALL_SPEED
        
        self.x += self.vx
        
        for tile in level.get_tiles_near(self):
            if tile['solid'] and self.rect.colliderect(tile['rect']):
                self.vx *= -1
                break
        
        self.y += self.vy
        for tile in level.get_tiles_near(self):
            if tile['solid'] and self.rect.colliderect(tile['rect']):
                if self.vy > 0:
                    self.y = tile['rect'].top - self.height
                    self.vy = 0
    
    def draw(self, screen, camera_x, sprites):
        if not self.alive:
            return
        sprite = sprites.get_sprite(self.kind, self.frame)
        screen.blit(sprite, (int(self.x - camera_x), int(self.y)))


class Particle:
    def __init__(self, x, y, kind='brick'):
        self.x = x
        self.y = y
        self.kind = kind
        self.alive = True
        self.timer = 0
        
        if kind == 'brick':
            self.pieces = [
                {'x': x, 'y': y, 'vx': -1.5, 'vy': -4},
                {'x': x + 8, 'y': y, 'vx': 1.5, 'vy': -4},
                {'x': x, 'y': y + 8, 'vx': -1, 'vy': -3},
                {'x': x + 8, 'y': y + 8, 'vx': 1, 'vy': -3},
            ]
        elif kind == 'coin_pop':
            self.vy = -6
    
    def update(self, dt):
        self.timer += dt
        if self.kind == 'brick':
            for p in self.pieces:
                p['vy'] += GRAVITY_FALL
                p['x'] += p['vx']
                p['y'] += p['vy']
            if self.timer > 1:
                self.alive = False
        elif self.kind == 'coin_pop':
            self.vy += GRAVITY_FALL * 0.4
            self.y += self.vy
            if self.timer > 0.8:
                self.alive = False
    
    def draw(self, screen, camera_x):
        if self.kind == 'brick':
            for p in self.pieces:
                pygame.draw.rect(screen, COLORS['brick'], (int(p['x'] - camera_x), int(p['y']), 8, 8))
        elif self.kind == 'coin_pop':
            pygame.draw.ellipse(screen, COLORS['coin'], (int(self.x - camera_x), int(self.y), 8, 12))


# =============================================================================
# LEVEL
# =============================================================================

class Level:
    def __init__(self, level_data, level_name="1-1"):
        self.name = level_name
        self.tiles = {}
        self.enemies = []
        self.items = []
        self.particles = []
        self.firebars = []
        self.width = len(level_data[0]) if level_data else 0
        self.height = len(level_data)
        self.player_start = (48, 192)
        self.bg_color = COLORS['sky']
        self.camera_lock = 0
        self.axe_pos = None
        self.bridge_tiles = []
        self.bowser = None
        self.flagpole_x = None  # X position of flagpole for collision
        self.flag_y = 0  # For flag sliding animation
        
        self._parse_level(level_data)
        
        # Set background color based on level type
        if '-2' in level_name:
            self.bg_color = COLORS['underground_bg']  # Underground levels
        elif '-4' in level_name:
            self.bg_color = COLORS['castle_bg']  # Castle levels only
    
    def _parse_level(self, data):
        for y, row in enumerate(data):
            for x, char in enumerate(row):
                if char == '#':
                    self.tiles[(x, y)] = {'type': 'ground', 'solid': True}
                elif char == 'B':
                    self.tiles[(x, y)] = {'type': 'brick', 'solid': True, 'breakable': True}
                elif char == 'b':
                    self.tiles[(x, y)] = {'type': 'castle_brick', 'solid': True}
                elif char == '?':
                    self.tiles[(x, y)] = {'type': 'question', 'solid': True, 'item': 'coin'}
                elif char == 'M':
                    self.tiles[(x, y)] = {'type': 'question', 'solid': True, 'item': 'mushroom'}
                elif char == '[':
                    self.tiles[(x, y)] = {'type': 'pipe_top_left', 'solid': True}
                elif char == ']':
                    self.tiles[(x, y)] = {'type': 'pipe_top_right', 'solid': True}
                elif char == '{':
                    self.tiles[(x, y)] = {'type': 'pipe_left', 'solid': True}
                elif char == '}':
                    self.tiles[(x, y)] = {'type': 'pipe_right', 'solid': True}
                elif char == '|':
                    self.tiles[(x, y)] = {'type': 'flagpole', 'solid': False}
                    if self.flagpole_x is None:
                        self.flagpole_x = x * TILE_SIZE
                        self.flag_y = y * TILE_SIZE
                elif char == '^':
                    self.tiles[(x, y)] = {'type': 'flagball', 'solid': False}
                    if self.flagpole_x is None:
                        self.flagpole_x = x * TILE_SIZE
                elif char == 'L':
                    self.tiles[(x, y)] = {'type': 'lava', 'solid': False, 'deadly': True}
                elif char == '=':
                    self.tiles[(x, y)] = {'type': 'bridge', 'solid': True}
                    self.bridge_tiles.append((x, y))
                elif char == 'A':
                    self.axe_pos = (x * TILE_SIZE, y * TILE_SIZE)
                elif char == 'G':
                    self.enemies.append(Enemy(x * TILE_SIZE, y * TILE_SIZE, 'goomba'))
                elif char == 'K':
                    self.enemies.append(Enemy(x * TILE_SIZE, y * TILE_SIZE - 8, 'koopa'))
                elif char == 'W':
                    self.bowser = Enemy(x * TILE_SIZE, y * TILE_SIZE, 'bowser')
                    self.enemies.append(self.bowser)
                elif char == 'F':
                    self.firebars.append(FireBar(x * TILE_SIZE + 8, y * TILE_SIZE + 8, 5, 2, True))
                elif char == 'f':
                    self.firebars.append(FireBar(x * TILE_SIZE + 8, y * TILE_SIZE + 8, 5, 2, False))
                elif char == 'P':
                    self.player_start = (x * TILE_SIZE, y * TILE_SIZE)
                elif char == 'C':
                    # Floating coin
                    item = Item(x * TILE_SIZE, y * TILE_SIZE, 'coin')
                    item.spawning = False
                    self.items.append(item)
    
    def get_tiles_near(self, entity):
        tiles = []
        x1 = int(entity.x // TILE_SIZE) - 1
        x2 = int((entity.x + entity.width) // TILE_SIZE) + 1
        y1 = int(entity.y // TILE_SIZE) - 1
        y2 = int((entity.y + entity.height) // TILE_SIZE) + 1
        
        for y in range(y1, y2 + 1):
            for x in range(x1, x2 + 1):
                if (x, y) in self.tiles:
                    tile = self.tiles[(x, y)]
                    if tile.get('solid', False):
                        tiles.append({
                            'grid_x': x,
                            'grid_y': y,
                            'solid': True,
                            'rect': pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE),
                            'type': tile['type']
                        })
        return tiles
    
    def hit_block(self, x, y, player, sound):
        if (x, y) not in self.tiles:
            return
        tile = self.tiles[(x, y)]
        
        if tile['type'] in ['brick', 'castle_brick']:
            if player.big and tile.get('breakable'):
                del self.tiles[(x, y)]
                self.particles.append(Particle(x * TILE_SIZE, y * TILE_SIZE, 'brick'))
                sound.play('break')
            else:
                sound.play('bump')
        elif tile['type'] == 'question':
            item_type = tile.get('item', 'coin')
            if item_type == 'coin':
                self.particles.append(Particle(x * TILE_SIZE, y * TILE_SIZE - 16, 'coin_pop'))
                player.collect_coin(sound)
            else:
                item = Item(x * TILE_SIZE, (y - 1) * TILE_SIZE, item_type)
                item.spawn_y = y * TILE_SIZE
                self.items.append(item)
            tile['type'] = 'used'
            tile['item'] = None
            sound.play('bump')
    
    def destroy_bridge(self):
        for x, y in self.bridge_tiles:
            if (x, y) in self.tiles:
                del self.tiles[(x, y)]
    
    def update(self, dt, player, sound):
        for enemy in self.enemies[:]:
            if enemy.alive:
                enemy.update(dt, self, player, sound)
                if not player.dead and not player.win and enemy.alive and enemy.activated:
                    prect = player.rect
                    erect = enemy.rect
                    if prect.colliderect(erect):
                        if player.star:
                            enemy.alive = False
                            player.score += 100
                            sound.play('stomp')
                        elif enemy.kind == 'bowser':
                            player.take_damage(sound)
                        elif enemy.kind == 'koopa' and enemy.shell and enemy.shell_vx == 0:
                            # Can kick stationary shell safely
                            enemy.stomp(player, sound)
                        else:
                            # VERY GENEROUS stomp detection:
                            # If player is falling OR player top is above enemy top = STOMP
                            # Only damage if player is clearly walking into enemy from the side
                            
                            player_is_falling = player.vy > 0
                            player_above = prect.top < erect.top + 4
                            player_mostly_above = prect.centery < erect.centery
                            
                            # Stomp if ANY of these are true
                            if player_is_falling or player_above or player_mostly_above:
                                enemy.stomp(player, sound)
                            else:
                                player.take_damage(sound)
            else:
                self.enemies.remove(enemy)
        
        for firebar in self.firebars:
            firebar.update(dt, self, player, sound)
        
        for item in self.items[:]:
            if item.alive:
                item.update(dt, self, sound)
                if not item.spawning and player.rect.colliderect(item.rect):
                    if item.kind == 'coin':
                        player.collect_coin(sound)
                    else:
                        player.powerup(item.kind, sound)
                    item.alive = False
            else:
                self.items.remove(item)
        
        for particle in self.particles[:]:
            if particle.alive:
                particle.update(dt)
            else:
                self.particles.remove(particle)
        
        if self.axe_pos and not player.dead:
            axe_rect = pygame.Rect(self.axe_pos[0], self.axe_pos[1], 16, 16)
            if player.rect.colliderect(axe_rect):
                self.destroy_bridge()
                self.axe_pos = None
                if self.bowser:
                    self.bowser.alive = False
                player.win = True
                player.score += 5000
                sound.play('flagpole')
        
        # Flagpole collision (1-1 style levels)
        if self.flagpole_x and not player.dead and not player.win:
            flag_rect = pygame.Rect(self.flagpole_x, 0, 16, 15 * TILE_SIZE)
            if player.rect.colliderect(flag_rect):
                player.win = True
                player.score += 2000
                sound.play('flagpole')
        
        if not player.dead:
            px, py = int(player.x // TILE_SIZE), int((player.y + player.height) // TILE_SIZE)
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    tile = self.tiles.get((px + dx, py + dy))
                    if tile and tile.get('deadly'):
                        player.die(sound)
                        return
    
    def draw(self, screen, camera_x, tile_renderer):
        screen.fill(self.bg_color)
        start_x = int(camera_x // TILE_SIZE) - 1
        end_x = start_x + (SCREEN_WIDTH // TILE_SIZE) + 3
        frame = int(pygame.time.get_ticks() / 200) % 4
        
        for y in range(self.height):
            for x in range(start_x, end_x):
                if (x, y) in self.tiles:
                    tile = self.tiles[(x, y)]
                    tile_surf = tile_renderer.get_tile(tile['type'], frame)
                    screen.blit(tile_surf, (x * TILE_SIZE - int(camera_x), y * TILE_SIZE))
        
        if self.axe_pos:
            ax = int(self.axe_pos[0] - camera_x)
            ay = int(self.axe_pos[1])
            pygame.draw.rect(screen, (139, 90, 43), (ax + 6, ay + 4, 4, 12))
            pygame.draw.rect(screen, (192, 192, 192), (ax + 2, ay, 12, 8))
        
        for particle in self.particles:
            particle.draw(screen, camera_x)


# =============================================================================
# HUD
# =============================================================================

class HUD:
    def __init__(self):
        self.font = BitmapFont()
        self.coin_frame = 0
        self.coin_timer = 0
    
    def update(self, dt):
        self.coin_timer += dt
        if self.coin_timer > 0.15:
            self.coin_timer = 0
            self.coin_frame = (self.coin_frame + 1) % 4
    
    def draw(self, screen, player, level_name, time_left):
        screen.blit(self.font.render("MARIO"), (24, 8))
        screen.blit(self.font.render(f"{player.score:06d}"), (24, 16))
        
        coin_widths = [6, 4, 2, 4]
        cw = coin_widths[self.coin_frame]
        pygame.draw.ellipse(screen, COLORS['coin'], (96 + (6 - cw) // 2, 17, cw, 7))
        screen.blit(self.font.render(f"x{player.coins:02d}"), (104, 16))
        
        screen.blit(self.font.render("WORLD"), (144, 8))
        screen.blit(self.font.render(f" {level_name}"), (144, 16))
        
        screen.blit(self.font.render("TIME"), (200, 8))
        screen.blit(self.font.render(f" {max(0, int(time_left)):03d}"), (200, 16))
        
        screen.blit(self.font.render(f"x{player.lives}"), (24, 32))
        
        # Show COURSE CLEAR after flagpole animation
        if player.win and player.win_timer > 2.5:
            self._draw_course_clear(screen, player)
    
    def _draw_course_clear(self, screen, player):
        # Dark semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))
        
        # Simple panel
        panel_w, panel_h = 160, 40
        panel_x = (SCREEN_WIDTH - panel_w) // 2
        panel_y = (SCREEN_HEIGHT - panel_h) // 2
        
        # Panel with black border and blue fill
        pygame.draw.rect(screen, (0, 0, 0), (panel_x - 2, panel_y - 2, panel_w + 4, panel_h + 4))
        pygame.draw.rect(screen, (0, 88, 248), (panel_x, panel_y, panel_w, panel_h))
        pygame.draw.rect(screen, (252, 252, 252), (panel_x + 2, panel_y + 2, panel_w - 4, panel_h - 4), 2)
        
        # "COURSE CLEAR!" text centered
        text = self.font.render("COURSE CLEAR!")
        text_x = (SCREEN_WIDTH - text.get_width()) // 2
        text_y = panel_y + (panel_h - 8) // 2
        screen.blit(text, (text_x, text_y))



# =============================================================================
# LEVEL DATA - NES ACCURATE SMB1
# =============================================================================

def get_level_1_1():
    """World 1-1 - NES Accurate Layout
    Based on original SMB1 NES ROM data
    Features: ? blocks, brick blocks, pipes, goombas, koopa, stairs, flagpole
    """
    return [
        "                                                                                                                                                                                                                                    ",
        "                                                                                                                                                                                                                                    ",
        "                                                                                                                                                                                      ^                                              ",
        "                                                                                                                                                                                      |                                              ",
        "                                                                                                                                                                                      |                                              ",
        "                                                                                                                                                                                      |       ##                                    ",
        "                                                                                                                                                                                      |      ###                                    ",
        "                                                                                                                                                                                      |     ####                                    ",
        "                                                                                                                                                                                      |    #####                                    ",
        "                  ?      ?M?B?                          B  ?B?B?                ?  ?       ?B?                        BB?B?BB               B B B                                     |   ######                                    ",
        "                                                                                                                                                                                      |  #######                                    ",
        "                                                                                                                                                                                      | ########                                    ",
        "   P          G          G       G              G G    []           G       G G                       K  G         G               []      []   G  G  G                               |#########                                    ",
        "####################################  ################  {}####  ##################################  ########################################{}######{}###############################################################                  ",
        "####################################  ################  {}####  ##################################  ########################################{}######{}###############################################################                  ",
    ]


def get_level_1_2():
    """World 1-2 - NES Accurate Underground Layout
    Based on original SMB1 NES ROM data
    Features: brick ceiling, underground theme, pipes, coins, goombas, exit pipe to flagpole
    """
    return [
        "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
        "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
        "                                                                                                                                                                                                                                            ",
        "                                                                                                                                                                                                                                            ",
        "                                                                                                                                                                                                                                            ",
        "          C C C C                                             C C C C                                                                       C C C                                                                                           ",
        "          BBBBBBB                  BBB?BBBB                    BBBBBBB                ?M?                        BBBBBB                     BBBBBBB                                                                                          ",
        "                                                                                                                                                                                                                                            ",
        "                    []                            []                                              []                             []                                                      []                                                  ",
        "                    {}                            {}                                              {}                             {}                                                      {}                                                  ",
        "  P                 {}        G          G        {}            G                G                {}             G               {}              G      G                                {}        ^                                         ",
        "#################  #{}#####################  #####{}##########################  ##################{}#########################  ###{}################################  #####################{}########|##############################################",
        "#################  #{}#####################  #####{}##########################  ##################{}#########################  ###{}################################  #####################{}########|##############################################",
        "#################  #{}#####################  #####{}##########################  ##################{}#########################  ###{}################################  #####################{}########|##############################################",
        "#################  #{}#####################  #####{}##########################  ##################{}#########################  ###{}################################  #####################{}########|##############################################",
    ]


def get_level_8_4():
    """World 8-4 - NES Accurate Final Castle
    Based on original SMB1 NES ROM data
    Features: castle bricks, lava pits, fire bars, bowser, axe, bridge
    """
    return [
        "                                                                                                                                                                                                                            ",
        "                                                                                                                                                                                                                            ",
        "                                                                                                                                                                                                                            ",
        "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        "                                                                                                                                                                                                                           b",
        "                                                                                                                                                                                                                           b",
        "                                                                                                                                                                                                                           b",
        "                                        F                                             f                                       F                                                                                            b",
        "                                        b               bbbbbbbb                      b                                       b               bbbbbbbbbbb                                         =====A                   b",
        "                                        b                                            b                                       b                                                                W                            b",
        "              bbbbb            bbbbb    b           G                G               b           bbbb           bbbbb        b                         G    G                                                              b",
        "  P                 G     G                                                G    G                                                                                                                                          b",
        "bbbbbbbbb  #bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb  #bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb  #bbbbbbbbbbbbbbbbbbbbbb  #bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLb",
        "bbbbbbbbb  #bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb  #bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb  #bbbbbbbbbbbbbbbbbbbbbb  #bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLb",
        "bbbbbbbbb  #bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb  #bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb  #bbbbbbbbbbbbbbbbbbbbbb  #bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLb",
    ]


def get_level_1_3():
    """World 1-3 - NES Accurate Athletic/Treetop Level
    Features: floating platforms, moving lifts, koopas, vertical challenge
    """
    return [
        "                                                                                                                                                                                                                                    ",
        "                                                                                                                                                                                                                                    ",
        "                                                                                                                                                                                        ^                                            ",
        "                                                                                                                                                                                        |                                            ",
        "                                                                                                                                                                                        |                                            ",
        "                                                                                                                                                                                        |      ##                                   ",
        "                 BBB               BBB                  BBB                BBB                  BBB               BBB                  BBB               BBB                            |     ###                                   ",
        "                                                                                                                                                                                        |    ####                                   ",
        "       BBB               BBB                  BBB                 BBB                 BBB                BBB                 BBB                BBB                                     |   #####                                   ",
        "                                                                                                                                                                                        |  ######                                   ",
        "  P           K                K                    K                  K                   K                 K                   K                 K                                    | #######                                   ",
        "####                                                                                                                                                                                    |########                                   ",
        "####                                                                                                                                                                                    |########                                   ",
        "####                                                                                                                                                                                   #|########                                   ",
        "####                                                                                                                                                                                ####|#########                                  ",
    ]


def get_level_1_4():
    """World 1-4 - NES Accurate Castle Level (First Castle)
    Features: lava, fire bars, bowser fight, axe
    """
    return [
        "                                                                                                                                                                                            ",
        "                                                                                                                                                                                            ",
        "                                                                                                                                                                                            ",
        "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        "                                                                                                                                                                                           b",
        "                                                                                                                                                                                           b",
        "                                                                                                                                                                                           b",
        "                            F                                         f                                                                                                                    b",
        "                            b               bbbbbbb                    b                                       bbbbbbbbbbb                                          =====A                  b",
        "                            b                                         b                                                                                         W                          b",
        "            bbbbb           b          G              G               b          bbbbb            bbbbb                              G     G                                                b",
        "  P               G    G                                    G    G                                                                                                                          b",
        "bbbbbbbbb  bbbbbbbbbbbbbbbbbbbbbbbbbb  bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb  bbbbbbbbbbbbbbbbbbbbb  bbbbbbbbbbbbbbbbbbbbbbbbbbbLLLLLLLLLLLLLLLLLLLLLLLLLLLb",
        "bbbbbbbbb  bbbbbbbbbbbbbbbbbbbbbbbbbb  bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb  bbbbbbbbbbbbbbbbbbbbb  bbbbbbbbbbbbbbbbbbbbbbbbbbbLLLLLLLLLLLLLLLLLLLLLLLLLLLb",
        "bbbbbbbbb  bbbbbbbbbbbbbbbbbbbbbbbbbb  bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb  bbbbbbbbbbbbbbbbbbbbb  bbbbbbbbbbbbbbbbbbbbbbbbbbbLLLLLLLLLLLLLLLLLLLLLLLLLLLb",
    ]


def get_level_2_1():
    """World 2-1 - NES Accurate Overworld with more challenge"""
    return [
        "                                                                                                                                                                                                                                    ",
        "                                                                                                                                                                                                                                    ",
        "                                                                                                                                                                                      ^                                              ",
        "                                                                                                                                                                                      |                                              ",
        "                                                                                                                                                                                      |                                              ",
        "                                                                                                                                                                                      |       ##                                    ",
        "                                                                                                                                                                                      |      ###                                    ",
        "                                                                                                                                                                                      |     ####                                    ",
        "                                                                                                                                                                                      |    #####                                    ",
        "               ?M?       BBB?BBB                     ?  ?B?B?                ?M?       ?B?                        BB?BBB?BB               B B B                                       |   ######                                    ",
        "                                                                                                                                                                                      |  #######                                    ",
        "                                                                                                                                                                                      | ########                                    ",
        "   P        G    G    G        G    G        G  G   []          G  G      G  G                     K K  G       G               []      []   G  G  G                                  |#########                                    ",
        "####################################  ################  {}####  ##################################  ########################################{}######{}###############################################################                  ",
        "####################################  ################  {}####  ##################################  ########################################{}######{}###############################################################                  ",
    ]


def get_level_2_2():
    """World 2-2 - NES Accurate Underground"""
    return [
        "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
        "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
        "                                                                                                                                                                                                                                            ",
        "                                                                                                                                                                                                                                            ",
        "                                                                                                                                                                                                                                            ",
        "          C C C C C                                           C C C C C                                                                     C C C C                                                                                         ",
        "          BBBBBBBBB                  BBB?M?BBB                  BBBBBBBBB              ?M?M?                      BBBBBBB                   BBBBBBBBB                                                                                         ",
        "                                                                                                                                                                                                                                            ",
        "                    []                            []                                              []                             []                                                      []                                                  ",
        "                    {}                            {}                                              {}                             {}                                                      {}                                                  ",
        "  P                 {}        G  G       G  G     {}            G    G            G               {}             G   G           {}              G  G   G                                {}        ^                                         ",
        "#################  #{}#####################  #####{}##########################  ##################{}#########################  ###{}################################  #####################{}########|##############################################",
        "#################  #{}#####################  #####{}##########################  ##################{}#########################  ###{}################################  #####################{}########|##############################################",
        "#################  #{}#####################  #####{}##########################  ##################{}#########################  ###{}################################  #####################{}########|##############################################",
        "#################  #{}#####################  #####{}##########################  ##################{}#########################  ###{}################################  #####################{}########|##############################################",
    ]


def get_level_2_3():
    """World 2-3 - NES Accurate Athletic Level"""
    return [
        "                                                                                                                                                                                                                                    ",
        "                                                                                                                                                                                                                                    ",
        "                                                                                                                                                                                        ^                                            ",
        "                                                                                                                                                                                        |                                            ",
        "                                                                                                                                                                                        |                                            ",
        "                                                                                                                                                                                        |      ##                                   ",
        "              BBBBB             BBBBB                BBBBB              BBBBB                BBBBB             BBBBB                BBBBB             BBBBB                             |     ###                                   ",
        "                                                                                                                                                                                        |    ####                                   ",
        "     BBBBB              BBBBB              BBBBB               BBBBB              BBBBB              BBBBB              BBBBB              BBBBB                                        |   #####                                   ",
        "                                                                                                                                                                                        |  ######                                   ",
        "  P          K    K           K    K              K    K             K    K              K    K            K    K              K    K             K                                     | #######                                   ",
        "####                                                                                                                                                                                    |########                                   ",
        "####                                                                                                                                                                                    |########                                   ",
        "####                                                                                                                                                                                   #|########                                   ",
        "####                                                                                                                                                                                ####|#########                                  ",
    ]


def get_level_2_4():
    """World 2-4 - NES Accurate Castle"""
    return [
        "                                                                                                                                                                                            ",
        "                                                                                                                                                                                            ",
        "                                                                                                                                                                                            ",
        "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        "                                                                                                                                                                                           b",
        "                                                                                                                                                                                           b",
        "                                                                                                                                                                                           b",
        "                        F               F                                 f                f                                                                                                b",
        "                        b               b            bbbbbbb              b                b                           bbbbbbbbbbb                                  =====A                  b",
        "                        b               b                                 b                b                                                                    W                          b",
        "        bbbbb           b       bbbbb   b       G              G          b       bbbbb    b         bbbbb                               G     G                                            b",
        "  P           G    G                                                G    G                                                                                                                  b",
        "bbbbbbbbb  bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb  bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb  bbbbbbbbbbbbbbbbbb  bbbbbbbbbbbbbbbbbbbbbbbbbbbLLLLLLLLLLLLLLLLLLLLLLLLLb",
        "bbbbbbbbb  bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb  bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb  bbbbbbbbbbbbbbbbbb  bbbbbbbbbbbbbbbbbbbbbbbbbbbLLLLLLLLLLLLLLLLLLLLLLLLLb",
        "bbbbbbbbb  bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb  bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb  bbbbbbbbbbbbbbbbbb  bbbbbbbbbbbbbbbbbbbbbbbbbbbLLLLLLLLLLLLLLLLLLLLLLLLLb",
    ]


# =============================================================================
# GAME
# =============================================================================

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH * SCALE, SCREEN_HEIGHT * SCALE))
        self.game_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("ULTRA! MARIO 2D BROS. - Samsoft Engine")
        
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "title"  # "title", "game", or "level_select"
        self.title_timer = 0
        self.title_blink = True
        self.level_cursor = 0  # For debug level select
        
        self.sound = SoundEngine()
        self.sprites = SpriteRenderer()
        self.tiles = TileRenderer()
        self.hud = HUD()
        self.font = BitmapFont()
        
        self.levels = {
            "1-1": get_level_1_1, "1-2": get_level_1_2, "1-3": get_level_1_3, "1-4": get_level_1_4,
            "2-1": get_level_2_1, "2-2": get_level_2_2, "2-3": get_level_2_3, "2-4": get_level_2_4,
            "8-4": get_level_8_4
        }
        self.level_order = [
            "1-1", "1-2", "1-3", "1-4",
            "2-1", "2-2", "2-3", "2-4",
            "8-4"
        ]  # Level progression
        self.current_level = "1-1"
        self.time_left = 400
        self.camera_x = 0
        
        # Don't load level yet - wait for title
        self.level = None
        self.player = None
    
    def _load_level(self, name):
        level_func = self.levels.get(name, get_level_1_1)
        self.level = Level(level_func(), name)
        self.player = Player(*self.level.player_start)
        self.camera_x = 0
        self.time_left = 400
        self.sound.play_music(name, force=True)  # Force restart music for new level
    
    def _next_level(self):
        """Go to next level in order"""
        try:
            idx = self.level_order.index(self.current_level)
            next_idx = (idx + 1) % len(self.level_order)
            self.current_level = self.level_order[next_idx]
        except ValueError:
            self.current_level = "1-1"
        self._load_level(self.current_level)
    
    def _start_game(self):
        """Start the game from title screen"""
        self.state = "game"
        self.current_level = "1-1"
        self._load_level(self.current_level)
    
    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            self._handle_events()
            self._update(dt)
            self._draw()
        pygame.quit()
    
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == "game":
                        self.state = "title"
                        self.sound.stop_music()
                    else:
                        self.running = False
                elif self.state == "title":
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_x):
                        self._start_game()
                    elif event.key == pygame.K_d:
                        # Debug mode - open level select
                        self.state = "level_select"
                        self.level_cursor = 0
                elif self.state == "level_select":
                    if event.key == pygame.K_ESCAPE:
                        self.state = "title"
                    elif event.key == pygame.K_UP:
                        self.level_cursor = (self.level_cursor - 1) % len(self.level_order)
                    elif event.key == pygame.K_DOWN:
                        self.level_cursor = (self.level_cursor + 1) % len(self.level_order)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_x):
                        self.current_level = self.level_order[self.level_cursor]
                        self._load_level(self.current_level)
                        self.state = "game"
                elif self.state == "game":
                    if event.key == pygame.K_r:
                        self._load_level(self.current_level)
                    elif event.key == pygame.K_n:
                        # Skip to next level
                        self._next_level()
                    elif event.key == pygame.K_1:
                        self.current_level = "1-1"
                        self._load_level(self.current_level)
                    elif event.key == pygame.K_2:
                        self.current_level = "1-2"
                        self._load_level(self.current_level)
                    elif event.key == pygame.K_3:
                        self.current_level = "1-3"
                        self._load_level(self.current_level)
                    elif event.key == pygame.K_4:
                        self.current_level = "1-4"
                        self._load_level(self.current_level)
                    elif event.key == pygame.K_5:
                        self.current_level = "2-1"
                        self._load_level(self.current_level)
                    elif event.key == pygame.K_6:
                        self.current_level = "2-2"
                        self._load_level(self.current_level)
                    elif event.key == pygame.K_7:
                        self.current_level = "2-3"
                        self._load_level(self.current_level)
                    elif event.key == pygame.K_8:
                        self.current_level = "2-4"
                        self._load_level(self.current_level)
                    elif event.key == pygame.K_9:
                        self.current_level = "8-4"
                        self._load_level(self.current_level)
    
    def _draw_title(self):
        """Draw the SMB1-style title screen"""
        # Sky background
        self.game_surface.fill(COLORS['sky'])
        
        # Ground at bottom (2 rows)
        for x in range(0, SCREEN_WIDTH, TILE_SIZE):
            tile = self.tiles.get_tile('ground', 0)
            self.game_surface.blit(tile, (x, SCREEN_HEIGHT - TILE_SIZE * 2))
            self.game_surface.blit(tile, (x, SCREEN_HEIGHT - TILE_SIZE))
        
        # Decorative pipes
        pipe_tl = self.tiles.get_tile('pipe_top_left', 0)
        pipe_tr = self.tiles.get_tile('pipe_top_right', 0)
        pipe_l = self.tiles.get_tile('pipe_left', 0)
        pipe_r = self.tiles.get_tile('pipe_right', 0)
        
        # Left pipe
        self.game_surface.blit(pipe_tl, (16, SCREEN_HEIGHT - TILE_SIZE * 4))
        self.game_surface.blit(pipe_tr, (32, SCREEN_HEIGHT - TILE_SIZE * 4))
        self.game_surface.blit(pipe_l, (16, SCREEN_HEIGHT - TILE_SIZE * 3))
        self.game_surface.blit(pipe_r, (32, SCREEN_HEIGHT - TILE_SIZE * 3))
        
        # Right pipe (taller)
        self.game_surface.blit(pipe_tl, (SCREEN_WIDTH - 64, SCREEN_HEIGHT - TILE_SIZE * 5))
        self.game_surface.blit(pipe_tr, (SCREEN_WIDTH - 48, SCREEN_HEIGHT - TILE_SIZE * 5))
        self.game_surface.blit(pipe_l, (SCREEN_WIDTH - 64, SCREEN_HEIGHT - TILE_SIZE * 4))
        self.game_surface.blit(pipe_r, (SCREEN_WIDTH - 48, SCREEN_HEIGHT - TILE_SIZE * 4))
        self.game_surface.blit(pipe_l, (SCREEN_WIDTH - 64, SCREEN_HEIGHT - TILE_SIZE * 3))
        self.game_surface.blit(pipe_r, (SCREEN_WIDTH - 48, SCREEN_HEIGHT - TILE_SIZE * 3))
        
        # Decorative bushes
        bush = self.tiles.get_tile('bush', 0)
        self.game_surface.blit(bush, (70, SCREEN_HEIGHT - TILE_SIZE * 3))
        self.game_surface.blit(bush, (86, SCREEN_HEIGHT - TILE_SIZE * 3))
        self.game_surface.blit(bush, (170, SCREEN_HEIGHT - TILE_SIZE * 3))
        
        # Clouds
        cloud = self.tiles.get_tile('cloud', 0)
        self.game_surface.blit(cloud, (30, 30))
        self.game_surface.blit(cloud, (46, 30))
        self.game_surface.blit(cloud, (180, 50))
        self.game_surface.blit(cloud, (196, 50))
        self.game_surface.blit(cloud, (110, 20))
        
        # ===== MAIN LOGO BOX =====
        # Orange/red box background like original SMB
        box_x, box_y = 40, 50
        box_w, box_h = 176, 70
        
        # Black border
        pygame.draw.rect(self.game_surface, COLORS['black'], (box_x - 2, box_y - 2, box_w + 4, box_h + 4))
        # Orange fill
        pygame.draw.rect(self.game_surface, (200, 76, 12), (box_x, box_y, box_w, box_h))
        # Inner highlight
        pygame.draw.rect(self.game_surface, (228, 92, 16), (box_x + 2, box_y + 2, box_w - 4, 2))
        
        # Title text - "ULTRA!" at top
        ultra_text = self.font.render("ULTRA!")
        ultra_x = box_x + (box_w - ultra_text.get_width()) // 2
        self.game_surface.blit(ultra_text, (ultra_x, box_y + 8))
        
        # "MARIO 2D" in middle
        mario_text = self.font.render("MARIO 2D")
        mario_x = box_x + (box_w - mario_text.get_width()) // 2
        self.game_surface.blit(mario_text, (mario_x, box_y + 24))
        
        # "BROS." at bottom
        bros_text = self.font.render("BROS.")
        bros_x = box_x + (box_w - bros_text.get_width()) // 2
        self.game_surface.blit(bros_text, (bros_x, box_y + 40))
        
        # Small TM
        tm_text = self.font.render("TM")
        self.game_surface.blit(tm_text, (box_x + box_w - 20, box_y + 56))
        
        # Copyright text
        copy_text = self.font.render("@2025 SAMSOFT")
        copy_x = (SCREEN_WIDTH - copy_text.get_width()) // 2
        self.game_surface.blit(copy_text, (copy_x, 135))
        
        # "PRESS START" blinking text
        if self.title_blink:
            start_text = self.font.render("PRESS START")
            start_x = (SCREEN_WIDTH - start_text.get_width()) // 2
            self.game_surface.blit(start_text, (start_x, 170))
        
        # "1 PLAYER GAME" option
        player_text = self.font.render("1 PLAYER GAME")
        player_x = (SCREEN_WIDTH - player_text.get_width()) // 2
        self.game_surface.blit(player_text, (player_x, 195))
        
        # Selection cursor (mushroom)
        mushroom = self.sprites.get_sprite('mushroom')
        self.game_surface.blit(mushroom, (player_x - 20, 192))
        
        # Debug mode hint (small text at bottom)
        debug_text = self.font.render("PRESS D FOR DEBUG")
        debug_x = (SCREEN_WIDTH - debug_text.get_width()) // 2
        self.game_surface.blit(debug_text, (debug_x, 220))
    
    def _draw_level_select(self):
        """Draw the debug level select screen"""
        # Dark blue background
        self.game_surface.fill((0, 0, 80))
        
        # Title
        title = self.font.render("DEBUG - LEVEL SELECT")
        title_x = (SCREEN_WIDTH - title.get_width()) // 2
        self.game_surface.blit(title, (title_x, 16))
        
        # Instructions
        inst = self.font.render("UP/DOWN: SELECT  ENTER: PLAY  ESC: BACK")
        inst_x = (SCREEN_WIDTH - inst.get_width()) // 2
        self.game_surface.blit(inst, (inst_x, 32))
        
        # Draw level list
        start_y = 55
        for i, level in enumerate(self.level_order):
            # Highlight selected level
            if i == self.level_cursor:
                # Draw selection box
                pygame.draw.rect(self.game_surface, (0, 88, 248), 
                    (40, start_y + i * 16 - 2, 176, 14))
                # Draw cursor mushroom
                mushroom = self.sprites.get_sprite('mushroom')
                self.game_surface.blit(mushroom, (24, start_y + i * 16 - 2))
            
            # Level name
            level_text = self.font.render(f"WORLD {level}")
            self.game_surface.blit(level_text, (48, start_y + i * 16))
            
            # Level type description
            if '-1' in level and level != '8-4':
                desc = "OVERWORLD"
            elif '-2' in level:
                desc = "UNDERGROUND"
            elif '-3' in level:
                desc = "ATHLETIC"
            elif '-4' in level:
                desc = "CASTLE"
            else:
                desc = "FINAL"
            
            desc_text = self.font.render(desc)
            self.game_surface.blit(desc_text, (140, start_y + i * 16))
    
    def _update(self, dt):
        # Title screen update
        if self.state == "title" or self.state == "level_select":
            self.title_timer += dt
            if self.title_timer > 0.5:
                self.title_timer = 0
                self.title_blink = not self.title_blink
            return
        
        # Game state update
        keys = pygame.key.get_pressed()
        self.sound.update_music(dt)
        self.hud.update(dt)
        
        if self.player.dead:
            self.player.update(dt, self.level, keys, self.sound)
            if self.player.death_timer > 3:
                if self.player.lives > 0:
                    self._load_level(self.current_level)
                else:
                    # Game over - return to title
                    self.state = "title"
                    self.sound.stop_music()
            return
        
        if self.player.win:
            self.player.update(dt, self.level, keys, self.sound)
            if self.player.win_timer > 3.5:
                self._next_level()
            return
        
        self.time_left -= dt
        if self.time_left <= 0:
            self.player.die(self.sound)
        
        self.player.update(dt, self.level, keys, self.sound)
        self.level.update(dt, self.player, self.sound)
        
        target_x = self.player.x - SCREEN_WIDTH // 3
        self.camera_x = max(self.level.camera_lock, min(target_x, self.level.width * TILE_SIZE - SCREEN_WIDTH))
        self.level.camera_lock = self.camera_x
    
    def _draw(self):
        if self.state == "title":
            self._draw_title()
        elif self.state == "level_select":
            self._draw_level_select()
        else:
            self.level.draw(self.game_surface, self.camera_x, self.tiles)
            for item in self.level.items:
                item.draw(self.game_surface, self.camera_x, self.sprites)
            for firebar in self.level.firebars:
                firebar.draw(self.game_surface, self.camera_x, self.sprites)
            for enemy in self.level.enemies:
                enemy.draw(self.game_surface, self.camera_x, self.sprites)
            self.player.draw(self.game_surface, self.camera_x, self.sprites)
            self.hud.draw(self.game_surface, self.player, self.current_level, self.time_left)
        
        scaled = pygame.transform.scale(self.game_surface, (SCREEN_WIDTH * SCALE, SCREEN_HEIGHT * SCALE))
        self.screen.blit(scaled, (0, 0))
        pygame.display.flip()


if __name__ == "__main__":
    game = Game()
    game.run()
