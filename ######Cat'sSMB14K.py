#!/usr/bin/env python3
"""
Ultra Mario 4K 1.x - A Super Mario Bros inspired game
Main Menu with World 1-1 through 8-4 level selection
Built with Pygame - All graphics and audio generated inline (no external files)
"""

import pygame
import sys
import random
import math
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict

# Initialize Pygame
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

# Constants
SCREEN_WIDTH = 768  # 256 * 3 (NES resolution scaled 3x)
SCREEN_HEIGHT = 672  # 224 * 3
FPS = 60
TILE_SIZE = 48  # 16 * 3 (NES tile size scaled 3x)
NES_SCALE = 3

# NES Color Palette (Famicom accurate)
NES_PALETTE = {
    'black': (0, 0, 0),
    'white': (252, 252, 252),
    'sky_blue': (92, 148, 252),
    'mario_red': (200, 76, 12),
    'mario_skin': (252, 152, 56),
    'mario_brown': (136, 20, 0),
    'brick_orange': (200, 76, 12),
    'brick_dark': (136, 20, 0),
    'ground_orange': (228, 92, 16),
    'ground_tan': (252, 152, 56),
    'pipe_green': (0, 168, 0),
    'pipe_dark': (0, 120, 0),
    'pipe_light': (128, 208, 16),
    'qblock_orange': (252, 152, 56),
    'qblock_dark': (200, 76, 12),
    'coin_orange': (252, 152, 56),
    'coin_dark': (200, 76, 12),
    'goomba_brown': (172, 124, 0),
    'goomba_dark': (136, 20, 0),
    'goomba_tan': (252, 152, 56),
    'koopa_green': (0, 168, 0),
    'koopa_light': (128, 208, 16),
    'mushroom_red': (200, 76, 12),
    'mushroom_spot': (252, 252, 252),
    'mushroom_tan': (252, 152, 56),
    'star_yellow': (252, 188, 60),
    'fire_red': (228, 0, 32),
    'fire_orange': (252, 152, 56),
    'flag_green': (0, 168, 0),
    'castle_gray': (188, 188, 188),
    'underground_blue': (0, 0, 0),
    'underwater_blue': (60, 100, 252),
    'castle_black': (0, 0, 0),
    'lava_red': (200, 76, 12),
}

# Shorthand colors
BLACK = NES_PALETTE['black']
WHITE = NES_PALETTE['white']
SKY_BLUE = NES_PALETTE['sky_blue']
MARIO_RED = NES_PALETTE['mario_red']
BRICK_COLOR = NES_PALETTE['brick_orange']
GROUND_COLOR = NES_PALETTE['ground_orange']
PIPE_GREEN = NES_PALETTE['pipe_green']
COIN_YELLOW = NES_PALETTE['coin_orange']
BROWN = NES_PALETTE['mario_brown']
YELLOW = NES_PALETTE['star_yellow']
GREEN = NES_PALETTE['pipe_green']
BLUE = NES_PALETTE['sky_blue']
RED = NES_PALETTE['fire_red']
ORANGE = NES_PALETTE['fire_orange']

# World themes (SMB1 accurate)
WORLD_COLORS = {
    1: {'sky': NES_PALETTE['sky_blue'], 'ground': NES_PALETTE['ground_orange'], 'name': 'Overworld', 'type': 'overworld'},
    2: {'sky': NES_PALETTE['black'], 'ground': NES_PALETTE['ground_orange'], 'name': 'Underground', 'type': 'underground'},
    3: {'sky': NES_PALETTE['sky_blue'], 'ground': NES_PALETTE['ground_orange'], 'name': 'Overworld', 'type': 'overworld'},
    4: {'sky': NES_PALETTE['black'], 'ground': NES_PALETTE['ground_orange'], 'name': 'Underground', 'type': 'underground'},
    5: {'sky': NES_PALETTE['sky_blue'], 'ground': NES_PALETTE['ground_orange'], 'name': 'Overworld', 'type': 'overworld'},
    6: {'sky': NES_PALETTE['black'], 'ground': NES_PALETTE['brick_dark'], 'name': 'Night', 'type': 'night'},
    7: {'sky': NES_PALETTE['sky_blue'], 'ground': NES_PALETTE['ground_orange'], 'name': 'Overworld', 'type': 'overworld'},
    8: {'sky': NES_PALETTE['black'], 'ground': NES_PALETTE['brick_dark'], 'name': 'Castle', 'type': 'castle'},
}


class GameState(Enum):
    MAIN_MENU = 1
    LEVEL_SELECT = 2
    PLAYING = 3
    PAUSED = 4
    GAME_OVER = 5
    LEVEL_COMPLETE = 6
    COURSE_CLEAR = 7  # SMB3-style course clear screen
    DEBUG_SELECT = 8  # Debug level select


@dataclass
class Level:
    world: int
    stage: int
    name: str
    unlocked: bool = True


class MusicGenerator:
    """
    Koji Kondo-style SMB1 OST Generator
    Authentic NES 2A03 APU emulation with:
    - 2 Pulse wave channels (12.5%, 25%, 50% duty cycles)
    - 1 Triangle wave channel (bass)
    - 1 Noise channel (percussion)
    Seamless looping, no fade-out
    """

    def __init__(self):
        self.sample_rate = 44100
        self.current_world = 0
        self.current_stage = 1

        # SMB1 accurate tempos (Koji Kondo original BPMs)
        self.OVERWORLD_TEMPO = 200   # Main theme ~200 BPM
        self.UNDERGROUND_TEMPO = 175  # Underground ~175 BPM  
        self.CASTLE_TEMPO = 150       # Castle ~150 BPM
        self.UNDERWATER_TEMPO = 116   # Underwater waltz ~116 BPM (3/4 time)
        self.STARMAN_TEMPO = 240      # Invincibility ~240 BPM

        # NES APU frequency table (A440 tuning)
        self.NOTE = {
            # Octave 2
            'C2': 36, 'D2': 38, 'E2': 40, 'F2': 41, 'G2': 43, 'A2': 45, 'Bb2': 46, 'B2': 47,
            # Octave 3
            'C3': 48, 'Cs3': 49, 'D3': 50, 'Ds3': 51, 'E3': 52, 'F3': 53, 'Fs3': 54, 'G3': 55, 
            'Gs3': 56, 'A3': 57, 'As3': 58, 'Bb3': 58, 'B3': 59,
            # Octave 4
            'C4': 60, 'Cs4': 61, 'D4': 62, 'Ds4': 63, 'E4': 64, 'F4': 65, 'Fs4': 66, 'G4': 67, 
            'Gs4': 68, 'A4': 69, 'As4': 70, 'Bb4': 70, 'B4': 71,
            # Octave 5
            'C5': 72, 'Cs5': 73, 'D5': 74, 'Ds5': 75, 'E5': 76, 'F5': 77, 'Fs5': 78, 'G5': 79, 
            'Gs5': 80, 'A5': 81, 'As5': 82, 'Bb5': 82, 'B5': 83,
            # Octave 6
            'C6': 84, 'D6': 86, 'E6': 88, 'F6': 89, 'G6': 91,
            'R': None  # Rest
        }

    def _note_to_freq(self, note: int) -> float:
        """Convert MIDI note to frequency (A4 = 440Hz)"""
        return 440.0 * (2.0 ** ((note - 69) / 12.0))

    def _generate_pulse_wave(self, freq: float, duration: float, volume: float = 0.15, duty: float = 0.5) -> list:
        """
        NES 2A03 Pulse channel - BYTE ACCURATE
        No envelope fade - raw square wave like real NES APU
        Duty cycles: 12.5%, 25%, 50%, 75%
        """
        n_samples = int(self.sample_rate * duration)
        samples = []
        for i in range(n_samples):
            t = i / self.sample_rate
            phase = (t * freq) % 1.0
            # Raw pulse wave - no envelope shaping
            value = 1.0 if phase < duty else -1.0
            samples.append(int(value * volume * 32767))
        return samples

    def _generate_triangle_wave(self, freq: float, duration: float, volume: float = 0.20) -> list:
        """
        NES 2A03 Triangle channel - BYTE ACCURATE
        4-bit quantized (16 steps), no volume control
        """
        n_samples = int(self.sample_rate * duration)
        samples = []
        for i in range(n_samples):
            t = i / self.sample_rate
            phase = (t * freq) % 1.0
            # 4-bit quantized triangle (16 steps like real NES)
            if phase < 0.5:
                value = phase * 4.0 - 1.0
            else:
                value = 3.0 - phase * 4.0
            # Quantize to 16 levels (NES has 4-bit triangle)
            value = int(value * 8) / 8.0
            samples.append(int(value * volume * 32767))
        return samples

    def _generate_noise(self, duration: float, volume: float = 0.08, mode: int = 0) -> list:
        """
        NES 2A03 Noise channel emulation
        LFSR-based noise generator
        mode 0 = long sequence (white noise), mode 1 = short sequence (metallic)
        """
        n_samples = int(self.sample_rate * duration)
        samples = []
        lfsr = 1
        # Mode determines feedback tap position
        tap = 1 if mode == 0 else 6
        for i in range(n_samples):
            # NES noise envelope - fast decay
            env = max(0, 1.0 - (i / n_samples) * 4)
            # LFSR feedback
            bit = ((lfsr >> 0) ^ (lfsr >> tap)) & 1
            lfsr = (lfsr >> 1) | (bit << 14)
            value = (lfsr & 1) * 2 - 1
            samples.append(int(value * volume * env * 32767))
        return samples

    def _generate_drum_hit(self, drum_type: str, duration: float = 0.05) -> list:
        """Generate NES-style drum sounds using noise channel"""
        if drum_type == 'kick':
            # Bass drum - low pitched noise burst
            return self._generate_noise(duration, 0.12, mode=1)
        elif drum_type == 'snare':
            # Snare - white noise burst
            return self._generate_noise(duration, 0.10, mode=0)
        elif drum_type == 'hat':
            # Hi-hat - short high noise
            return self._generate_noise(duration * 0.5, 0.06, mode=1)
        return self._generate_noise(duration, 0.08)

    def generate_level_music(self, world: int, stage: int) -> Optional[pygame.mixer.Sound]:
        """Generate music for a specific level (world-stage)"""
        try:
            import numpy as np
            # Stage 4 = Castle theme for all worlds
            if stage == 4:
                return self._generate_castle_theme(world)
            # Underground stages (1-2, 4-2)
            elif stage == 2 and world in [1, 4]:
                return self._generate_underground_theme(world)
            # Underwater (2-3, 7-3)
            elif (world == 2 and stage == 3) or (world == 7 and stage == 3):
                return self._generate_underwater_theme()
            # Overworld theme with world variation
            else:
                return self._generate_overworld_theme(world, stage)
        except ImportError:
            return None
        except Exception:
            return None

    def generate_world_music(self, world: int) -> Optional[pygame.mixer.Sound]:
        """Generate default music for a world (stage 1)"""
        return self.generate_level_music(world, 1)

    def _generate_overworld_theme(self, world: int, stage: int) -> Optional[pygame.mixer.Sound]:
        """
        Koji Kondo's SMB1 Ground Theme (Overworld)
        Full 4-channel NES arrangement:
        - Pulse 1: Main melody
        - Pulse 2: Harmony/countermelody  
        - Triangle: Bass line
        - Noise: Percussion
        """
        import numpy as np
        N = self.NOTE
        tempo = self.OVERWORLD_TEMPO
        beat = 60.0 / tempo
        s = beat / 4  # sixteenth note
        e = beat / 2  # eighth note
        q = beat      # quarter note

        # === PULSE 1: Main Melody ===
        melody = [
            # Intro motif (iconic E-E-E C-E G)
            (N['E5'], e), (N['E5'], e), (N['R'], e), (N['E5'], e),
            (N['R'], e), (N['C5'], e), (N['E5'], e), (N['R'], e),
            (N['G5'], q), (N['R'], q), (N['G4'], q), (N['R'], q),
            # Part A
            (N['C5'], q-s), (N['R'], s), (N['G4'], q-s), (N['R'], s),
            (N['E4'], q-s), (N['R'], s), (N['A4'], e), (N['R'], s),
            (N['B4'], e), (N['R'], s), (N['Bb4'], e), (N['A4'], e),
            (N['G4'], e*2/3), (N['E5'], e*2/3), (N['G5'], e*2/3), (N['A5'], e), (N['R'], s),
            (N['F5'], e), (N['G5'], e), (N['R'], s), (N['E5'], e), (N['R'], s),
            (N['C5'], e), (N['D5'], e), (N['B4'], e), (N['R'], e),
            # Part A repeat
            (N['C5'], q-s), (N['R'], s), (N['G4'], q-s), (N['R'], s),
            (N['E4'], q-s), (N['R'], s), (N['A4'], e), (N['R'], s),
            (N['B4'], e), (N['R'], s), (N['Bb4'], e), (N['A4'], e),
            (N['G4'], e*2/3), (N['E5'], e*2/3), (N['G5'], e*2/3), (N['A5'], e), (N['R'], s),
            (N['F5'], e), (N['G5'], e), (N['R'], s), (N['E5'], e), (N['R'], s),
            (N['C5'], e), (N['D5'], e), (N['B4'], e), (N['R'], e),
        ]

        # === PULSE 2: Harmony (thirds below or octave) ===
        harmony = [
            # Intro harmony
            (N['C5'], e), (N['C5'], e), (N['R'], e), (N['C5'], e),
            (N['R'], e), (N['G4'], e), (N['C5'], e), (N['R'], e),
            (N['E5'], q), (N['R'], q), (N['E4'], q), (N['R'], q),
            # Part A harmony  
            (N['G4'], q-s), (N['R'], s), (N['E4'], q-s), (N['R'], s),
            (N['C4'], q-s), (N['R'], s), (N['F4'], e), (N['R'], s),
            (N['G4'], e), (N['R'], s), (N['Fs4'], e), (N['F4'], e),
            (N['E4'], e*2/3), (N['C5'], e*2/3), (N['E5'], e*2/3), (N['F5'], e), (N['R'], s),
            (N['D5'], e), (N['E5'], e), (N['R'], s), (N['C5'], e), (N['R'], s),
            (N['A4'], e), (N['B4'], e), (N['G4'], e), (N['R'], e),
            # Part A repeat harmony
            (N['G4'], q-s), (N['R'], s), (N['E4'], q-s), (N['R'], s),
            (N['C4'], q-s), (N['R'], s), (N['F4'], e), (N['R'], s),
            (N['G4'], e), (N['R'], s), (N['Fs4'], e), (N['F4'], e),
            (N['E4'], e*2/3), (N['C5'], e*2/3), (N['E5'], e*2/3), (N['F5'], e), (N['R'], s),
            (N['D5'], e), (N['E5'], e), (N['R'], s), (N['C5'], e), (N['R'], s),
            (N['A4'], e), (N['B4'], e), (N['G4'], e), (N['R'], e),
        ]

        # === TRIANGLE: Bass line (octave lower) ===
        bass = [
            # Intro bass
            (N['D3'], q), (N['D3'], q), (N['D3'], q), (N['G2'], q),
            (N['G2'], q), (N['R'], q), (N['G2'], q), (N['R'], q),
            # Walking bass pattern
            (N['C3'], q), (N['G3'], q), (N['C3'], q), (N['G3'], q),
            (N['C3'], q), (N['G3'], q), (N['F3'], q), (N['G3'], q),
            (N['C3'], q), (N['G3'], q), (N['C3'], q), (N['G3'], q),
            (N['C3'], q), (N['G3'], q), (N['F3'], q), (N['G3'], q),
            (N['C3'], q), (N['E3'], q), (N['G3'], q), (N['C3'], q),
        ]

        # Calculate total duration
        melody_dur = sum(d for _, d in melody)
        harmony_dur = sum(d for _, d in harmony)
        bass_dur = sum(d for _, d in bass)
        total_duration = max(melody_dur, harmony_dur, bass_dur)
        total_samples = int(self.sample_rate * total_duration)

        left_channel = [0] * total_samples
        right_channel = [0] * total_samples

        # Render Pulse 1 (melody) - 25% duty cycle
        time_pos = 0
        for note, dur in melody:
            if note is not None:
                freq = self._note_to_freq(note)
                wave = self._generate_pulse_wave(freq, dur * 0.95, 0.12, 0.25)
                start = int(time_pos * self.sample_rate)
                for i, s in enumerate(wave):
                    if start + i < total_samples:
                        left_channel[start + i] += s
                        right_channel[start + i] += int(s * 0.8)
            time_pos += dur

        # Render Pulse 2 (harmony) - 12.5% duty cycle for thinner sound
        time_pos = 0
        for note, dur in harmony:
            if note is not None:
                freq = self._note_to_freq(note)
                wave = self._generate_pulse_wave(freq, dur * 0.95, 0.08, 0.125)
                start = int(time_pos * self.sample_rate)
                for i, ss in enumerate(wave):
                    if start + i < total_samples:
                        left_channel[start + i] += int(ss * 0.8)
                        right_channel[start + i] += ss
            time_pos += dur

        # Render Triangle (bass)
        time_pos = 0
        for note, dur in bass:
            if note is not None:
                freq = self._note_to_freq(note)
                wave = self._generate_triangle_wave(freq, dur * 0.90, 0.18)
                start = int(time_pos * self.sample_rate)
                for i, ss in enumerate(wave):
                    if start + i < total_samples:
                        left_channel[start + i] += ss
                        right_channel[start + i] += ss
            time_pos += dur

        # Render Noise (percussion) - kick on 1 and 3, hi-hat on every beat
        num_beats = int(total_duration / beat)
        for beat_num in range(num_beats):
            beat_start = int(beat_num * beat * self.sample_rate)
            # Kick drum on beats 1 and 3
            if beat_num % 4 in [0, 2]:
                kick = self._generate_drum_hit('kick', 0.06)
                for i, ss in enumerate(kick):
                    if beat_start + i < total_samples:
                        left_channel[beat_start + i] += ss
                        right_channel[beat_start + i] += ss
            # Hi-hat on every beat
            hat = self._generate_drum_hit('hat', 0.03)
            for i, ss in enumerate(hat):
                if beat_start + i < total_samples:
                    left_channel[beat_start + i] += ss
                    right_channel[beat_start + i] += ss

        return self._finalize_audio(left_channel, right_channel, total_samples)

    def _generate_underground_theme(self, world: int) -> Optional[pygame.mixer.Sound]:
        """Generate SMB1 underground theme - the iconic bass-driven cave music"""
        import numpy as np
        N = self.NOTE
        tempo = self.UNDERGROUND_TEMPO
        beat_duration = 60.0 / tempo
        s = beat_duration / 4  # sixteenth note

        # SMB1 Underground Theme - syncopated melody with chromatic runs
        melody_notes = [
            # Main riff - C C C - descending chromatic
            (N['C4'], s*2), (N['C4'], s*1), (N['C4'], s*2), (N['R'], s*1),
            (N['C4'], s*2), (N['D4'], s*2), (N['E4'], s*2), (N['C4'], s*2),
            (N['E4'], s*2), (N['F4'], s*1), (N['Fs4'], s*1), (N['G4'], s*4),
            (N['R'], s*2),
            # Repeat with variation
            (N['C5'], s*2), (N['C5'], s*1), (N['C5'], s*2), (N['R'], s*1),
            (N['C5'], s*2), (N['D5'], s*2), (N['E5'], s*2), (N['C5'], s*2),
            (N['E5'], s*2), (N['F5'], s*1), (N['Fs5'], s*1), (N['G5'], s*4),
            (N['R'], s*2),
            # Descending chromatic run
            (N['Gs5'], s*2), (N['G5'], s*2), (N['Fs5'], s*2), (N['F5'], s*2),
            (N['E5'], s*2), (N['Ds5'], s*2), (N['D5'], s*2), (N['C5'], s*2),
            (N['R'], s*4),
            # Bass octave hits
            (N['C4'], s*4), (N['G4'], s*4), (N['C4'], s*4), (N['R'], s*4),
        ]

        # Underground bass - heavy emphasis on C with chromatic movement
        bass_notes = [
            (36, beat_duration), (36, beat_duration), (36, beat_duration), (36, beat_duration),
            (36, beat_duration), (36, beat_duration), (35, beat_duration), (36, beat_duration),
            (36, beat_duration), (36, beat_duration), (36, beat_duration), (36, beat_duration),
            (35, beat_duration), (34, beat_duration), (33, beat_duration), (36, beat_duration),
        ]

        transpose = {1: 0, 4: 0}.get(world, 0)
        total_melody_dur = sum(d for _, d in melody_notes)
        total_bass_dur = sum(d for _, d in bass_notes)
        total_duration = max(total_melody_dur, total_bass_dur)
        total_samples = int(self.sample_rate * total_duration)

        left_channel = [0] * total_samples
        right_channel = [0] * total_samples

        time_pos = 0
        for note, dur in melody_notes:
            if note is not None:
                freq = self._note_to_freq(note + transpose)
                wave = self._generate_pulse_wave(freq, dur * 0.85, 0.11, 0.125)
                start = int(time_pos * self.sample_rate)
                for i, s in enumerate(wave):
                    if start + i < total_samples:
                        left_channel[start + i] += s
                        right_channel[start + i] += int(s * 0.9)
            time_pos += dur

        time_pos = 0
        for note, dur in bass_notes:
            if note is not None:
                freq = self._note_to_freq(note + transpose)
                wave = self._generate_triangle_wave(freq, dur * 0.9, 0.16)
                start = int(time_pos * self.sample_rate)
                for i, s in enumerate(wave):
                    if start + i < total_samples:
                        left_channel[start + i] += s
                        right_channel[start + i] += s
            time_pos += dur

        return self._finalize_audio(left_channel, right_channel, total_samples)

    def _generate_castle_theme(self, world: int) -> Optional[pygame.mixer.Sound]:
        """Generate SMB1 castle/fortress theme - ominous and tense"""
        import numpy as np
        N = self.NOTE
        tempo = self.CASTLE_TEMPO
        beat_duration = 60.0 / tempo
        s = beat_duration / 4  # sixteenth note

        # SMB1 Castle Theme - Minor key, chromatic tension
        # Bowser's Castle uses tritones and diminished patterns
        melody_notes = [
            # Opening arpeggio pattern - A minor feel
            (N['A4'], s*2), (N['C5'], s*2), (N['E5'], s*2), (N['A5'], s*4),
            (N['R'], s*2), (N['Gs5'], s*2), (N['A5'], s*2), (N['R'], s*4),
            # Descending chromatic tension
            (N['E5'], s*3), (N['Ds5'], s*3), (N['D5'], s*3), (N['R'], s*3),
            (N['A4'], s*2), (N['C5'], s*2), (N['E5'], s*2), (N['A5'], s*4),
            (N['R'], s*2),
            # Second phrase - higher register
            (N['C6'], s*2), (N['B5'], s*2), (N['Bb5'], s*2), (N['A5'], s*4),
            (N['R'], s*2), (N['E5'], s*4), (N['F5'], s*2), (N['E5'], s*2),
            (N['R'], s*4),
            # Tritone jump for tension (the "danger" interval)
            (N['A4'], s*2), (N['Ds5'], s*4), (N['A4'], s*2), (N['Ds5'], s*4),
            (N['E5'], s*4), (N['R'], s*4),
            # Resolution phrase
            (N['A4'], s*2), (N['B4'], s*2), (N['C5'], s*2), (N['D5'], s*2),
            (N['E5'], s*4), (N['R'], s*4),
        ]

        # Castle bass - ominous pedal tones with chromatic movement
        bass_notes = [
            (45, beat_duration * 2), (45, beat_duration * 2),  # A pedal
            (44, beat_duration * 2), (45, beat_duration * 2),  # Ab-A
            (45, beat_duration * 2), (45, beat_duration * 2),  # A pedal
            (43, beat_duration * 2), (45, beat_duration * 2),  # G-A
            (45, beat_duration * 2), (42, beat_duration * 2),  # A-Fs (tritone bass)
            (45, beat_duration * 2), (45, beat_duration * 2),  # A pedal
        ]

        # World 8 (final castle) gets extra intensity
        transpose = 0
        vol_mult = 1.3 if world == 8 else 1.0

        total_melody_dur = sum(d for _, d in melody_notes)
        total_bass_dur = sum(d for _, d in bass_notes)
        total_duration = max(total_melody_dur, total_bass_dur)
        total_samples = int(self.sample_rate * total_duration)

        left_channel = [0] * total_samples
        right_channel = [0] * total_samples

        time_pos = 0
        for note, dur in melody_notes:
            if note is not None:
                freq = self._note_to_freq(note + transpose)
                wave = self._generate_pulse_wave(freq, dur * 0.9, 0.09 * vol_mult, 0.125)
                start = int(time_pos * self.sample_rate)
                for i, s in enumerate(wave):
                    if start + i < total_samples:
                        left_channel[start + i] += s
                        right_channel[start + i] += int(s * 0.95)
            time_pos += dur

        time_pos = 0
        for note, dur in bass_notes:
            if note is not None:
                freq = self._note_to_freq(note + transpose)
                wave = self._generate_triangle_wave(freq, dur * 0.95, 0.18 * vol_mult)
                start = int(time_pos * self.sample_rate)
                for i, s in enumerate(wave):
                    if start + i < total_samples:
                        left_channel[start + i] += s
                        right_channel[start + i] += s
            time_pos += dur

        for beat in range(int(total_duration / (beat_duration * 2))):
            start = int(beat * beat_duration * 2 * self.sample_rate)
            wave = self._generate_noise(0.15, 0.04 * vol_mult)
            for i, s in enumerate(wave):
                if start + i < total_samples:
                    left_channel[start + i] += s
                    right_channel[start + i] += s

        return self._finalize_audio(left_channel, right_channel, total_samples)

    def _generate_underwater_theme(self) -> Optional[pygame.mixer.Sound]:
        """Generate SMB1 underwater waltz theme - elegant 3/4 time"""
        import numpy as np
        N = self.NOTE
        tempo = self.UNDERWATER_TEMPO
        beat_duration = 60.0 / tempo
        # Waltz is in 3/4 time
        q = beat_duration  # quarter note
        e = beat_duration / 2  # eighth note
        dq = beat_duration * 1.5  # dotted quarter

        # SMB1 Underwater Theme - Graceful waltz in C major
        melody_notes = [
            # Phrase 1: Rising arpeggio waltz pattern
            (N['E5'], q), (N['E5'], e), (N['E5'], e), (N['E5'], q),
            (N['D5'], q), (N['E5'], q), (N['F5'], q),
            (N['G5'], dq), (N['E5'], dq),
            # Phrase 2: Descending sequence
            (N['C5'], q), (N['D5'], q), (N['E5'], q),
            (N['F5'], q), (N['E5'], q), (N['D5'], q),
            (N['C5'], dq), (N['R'], dq),
            # Phrase 3: Climax
            (N['G5'], q), (N['A5'], q), (N['G5'], q),
            (N['F5'], q), (N['E5'], q), (N['D5'], q),
            (N['E5'], dq), (N['C5'], dq),
            # Phrase 4: Resolution
            (N['E5'], q), (N['D5'], q), (N['C5'], q),
            (N['B4'], q), (N['C5'], q), (N['D5'], q),
            (N['C5'], dq * 2),
        ]

        # Underwater bass - classic waltz "oom-pah-pah" pattern
        bass_notes = [
            (N['C3'], q), (N['G3'], e), (N['G3'], e), (N['G3'], q),
            (N['C3'], q), (N['G3'], e), (N['G3'], e), (N['G3'], q),
            (N['C3'], q), (N['E3'], q), (N['G3'], q),
            (N['F3'], q), (N['A3'], e), (N['A3'], e), (N['A3'], q),
            (N['G3'], q), (N['B3'], e), (N['B3'], e), (N['B3'], q),
            (N['C3'], dq), (N['G3'], dq),
            (N['C3'], q), (N['G3'], e), (N['G3'], e), (N['G3'], q),
            (N['F3'], q), (N['A3'], e), (N['A3'], e), (N['A3'], q),
            (N['C3'], q), (N['E3'], q), (N['G3'], q),
            (N['G3'], q), (N['B3'], q), (N['D4'], q),
            (N['C3'], dq * 2),
        ]

        total_melody_dur = sum(d for _, d in melody_notes)
        total_bass_dur = sum(d for _, d in bass_notes)
        total_duration = max(total_melody_dur, total_bass_dur)
        total_samples = int(self.sample_rate * total_duration)

        left_channel = [0] * total_samples
        right_channel = [0] * total_samples

        time_pos = 0
        for note, dur in melody_notes:
            if note is not None:
                freq = self._note_to_freq(note)
                wave = self._generate_pulse_wave(freq, dur * 0.85, 0.08, 0.5)
                start = int(time_pos * self.sample_rate)
                for i, s in enumerate(wave):
                    if start + i < total_samples:
                        left_channel[start + i] += s
                        right_channel[start + i] += int(s * 0.9)
            time_pos += dur

        time_pos = 0
        for note, dur in bass_notes:
            if note is not None:
                freq = self._note_to_freq(note)
                wave = self._generate_triangle_wave(freq, dur * 0.8, 0.12)
                start = int(time_pos * self.sample_rate)
                for i, s in enumerate(wave):
                    if start + i < total_samples:
                        left_channel[start + i] += s
                        right_channel[start + i] += s
            time_pos += dur

        return self._finalize_audio(left_channel, right_channel, total_samples)

    def _finalize_audio(self, left_channel: list, right_channel: list, total_samples: int) -> Optional[pygame.mixer.Sound]:
        """Normalize and create pygame Sound from channels"""
        import numpy as np
        max_val = max(max(abs(s) for s in left_channel), max(abs(s) for s in right_channel), 1)
        if max_val > 32767:
            scale_factor = 32767 / max_val
            left_channel = [int(s * scale_factor) for s in left_channel]
            right_channel = [int(s * scale_factor) for s in right_channel]

        stereo = np.column_stack((
            np.array(left_channel, dtype=np.int16),
            np.array(right_channel, dtype=np.int16)
        ))
        return pygame.sndarray.make_sound(stereo)


class SoundManager:
    """Handles game audio and OST"""
    def __init__(self):
        self.sounds: Dict[str, Optional[pygame.mixer.Sound]] = {}
        self.music_tracks: Dict[Tuple[int, int], Optional[pygame.mixer.Sound]] = {}
        self.music_generator = MusicGenerator()
        self.current_music_channel: Optional[pygame.mixer.Channel] = None
        self.volume = 0.5
        self.music_volume = 0.3
        self._generate_sounds()

    def _generate_sounds(self):
        """Generate all sound effects"""
        try:
            import numpy as np
            sample_rate = 44100

            # Jump sound - rising arpeggio
            self.sounds['jump'] = self._create_jump_sound(sample_rate)

            # Coin sound - two quick high notes
            self.sounds['coin'] = self._create_coin_sound(sample_rate)

            # Stomp sound - quick low thud
            self.sounds['stomp'] = self._create_stomp_sound(sample_rate)

            # Power-up sound - rising arpeggio
            self.sounds['powerup'] = self._create_powerup_sound(sample_rate)

            # Death sound - falling tone
            self.sounds['death'] = self._create_death_sound(sample_rate)

            # 1-Up sound
            self.sounds['1up'] = self._create_1up_sound(sample_rate)

            # Brick break sound
            self.sounds['break'] = self._create_break_sound(sample_rate)

            # Level complete jingle
            self.sounds['complete'] = self._create_complete_sound(sample_rate)

            # Time warning sound (hurry up!)
            self.sounds['warning'] = self._create_warning_sound(sample_rate)

        except ImportError:
            pass

    def _create_jump_sound(self, sr: int) -> Optional[pygame.mixer.Sound]:
        """Create Mario-style jump sound"""
        try:
            import numpy as np
            duration = 0.15
            n = int(sr * duration)
            t = np.linspace(0, duration, n, False)
            # Frequency sweep from 150 to 400 Hz
            freq = 150 + 250 * (t / duration)
            wave = np.sin(2 * np.pi * freq * t) * 0.3
            # Quick attack, moderate decay
            env = np.exp(-t * 10) * np.minimum(t * 100, 1)
            wave = (wave * env * 32767).astype(np.int16)
            return pygame.sndarray.make_sound(np.column_stack((wave, wave)))
        except:
            return None

    def _create_coin_sound(self, sr: int) -> Optional[pygame.mixer.Sound]:
        """Create coin collection sound"""
        try:
            import numpy as np
            duration = 0.15
            n = int(sr * duration)
            t = np.linspace(0, duration, n, False)
            # Two notes: B5 (988 Hz) then E6 (1319 Hz)
            freq1, freq2 = 988, 1319
            mid = n // 2
            wave = np.zeros(n)
            wave[:mid] = np.sin(2 * np.pi * freq1 * t[:mid])
            wave[mid:] = np.sin(2 * np.pi * freq2 * t[mid:])
            env = np.exp(-t * 8)
            wave = (wave * env * 0.25 * 32767).astype(np.int16)
            return pygame.sndarray.make_sound(np.column_stack((wave, wave)))
        except:
            return None

    def _create_stomp_sound(self, sr: int) -> Optional[pygame.mixer.Sound]:
        """Create enemy stomp sound"""
        try:
            import numpy as np
            duration = 0.1
            n = int(sr * duration)
            t = np.linspace(0, duration, n, False)
            freq = 200 * np.exp(-t * 20)
            wave = np.sin(2 * np.pi * freq * t) * 0.4
            env = np.exp(-t * 15)
            wave = (wave * env * 32767).astype(np.int16)
            return pygame.sndarray.make_sound(np.column_stack((wave, wave)))
        except:
            return None

    def _create_powerup_sound(self, sr: int) -> Optional[pygame.mixer.Sound]:
        """Create power-up sound"""
        try:
            import numpy as np
            duration = 0.5
            n = int(sr * duration)
            t = np.linspace(0, duration, n, False)
            # Rising arpeggio
            notes = [262, 330, 392, 523]  # C E G C
            wave = np.zeros(n)
            segment = n // 4
            for i, freq in enumerate(notes):
                start = i * segment
                end = start + segment
                wave[start:end] = np.sin(2 * np.pi * freq * t[start:end])
            env = np.exp(-t * 2)
            wave = (wave * env * 0.25 * 32767).astype(np.int16)
            return pygame.sndarray.make_sound(np.column_stack((wave, wave)))
        except:
            return None

    def _create_death_sound(self, sr: int) -> Optional[pygame.mixer.Sound]:
        """Create death sound"""
        try:
            import numpy as np
            duration = 0.8
            n = int(sr * duration)
            t = np.linspace(0, duration, n, False)
            # Falling tone
            freq = 400 * np.exp(-t * 2)
            wave = np.sin(2 * np.pi * freq * t) * 0.35
            env = 1 - t / duration
            wave = (wave * env * 32767).astype(np.int16)
            return pygame.sndarray.make_sound(np.column_stack((wave, wave)))
        except:
            return None

    def _create_1up_sound(self, sr: int) -> Optional[pygame.mixer.Sound]:
        """Create 1-up sound"""
        try:
            import numpy as np
            duration = 0.4
            n = int(sr * duration)
            t = np.linspace(0, duration, n, False)
            notes = [330, 392, 523, 659]  # E G C E
            wave = np.zeros(n)
            segment = n // 4
            for i, freq in enumerate(notes):
                start = i * segment
                end = start + segment
                wave[start:end] = np.sin(2 * np.pi * freq * t[start:end])
            env = np.exp(-t * 1.5)
            wave = (wave * env * 0.25 * 32767).astype(np.int16)
            return pygame.sndarray.make_sound(np.column_stack((wave, wave)))
        except:
            return None

    def _create_break_sound(self, sr: int) -> Optional[pygame.mixer.Sound]:
        """Create brick break sound"""
        try:
            import numpy as np
            duration = 0.15
            n = int(sr * duration)
            noise = np.random.uniform(-1, 1, n)
            env = np.exp(-np.linspace(0, duration, n) * 20)
            wave = (noise * env * 0.3 * 32767).astype(np.int16)
            return pygame.sndarray.make_sound(np.column_stack((wave, wave)))
        except:
            return None

    def _create_complete_sound(self, sr: int) -> Optional[pygame.mixer.Sound]:
        """Create level complete jingle"""
        try:
            import numpy as np
            duration = 1.5
            n = int(sr * duration)
            t = np.linspace(0, duration, n, False)
            # Victory fanfare notes
            notes = [(392, 0.2), (392, 0.2), (392, 0.2), (523, 0.6), (466, 0.1), (440, 0.1), (392, 0.4)]
            wave = np.zeros(n)
            pos = 0
            for freq, dur in notes:
                seg_len = int(sr * dur)
                if pos + seg_len > n:
                    seg_len = n - pos
                seg_t = np.linspace(0, dur, seg_len, False)
                wave[pos:pos+seg_len] = np.sin(2 * np.pi * freq * seg_t) * np.exp(-seg_t * 3)
                pos += seg_len
            wave = (wave * 0.25 * 32767).astype(np.int16)
            return pygame.sndarray.make_sound(np.column_stack((wave, wave)))
        except:
            return None

    def _create_warning_sound(self, sr: int) -> Optional[pygame.mixer.Sound]:
        """Create time warning sound (hurry up!)"""
        try:
            import numpy as np
            duration = 0.8
            n = int(sr * duration)
            t = np.linspace(0, duration, n, False)
            # Fast beeping pattern - three quick high-pitched beeps
            freq = 880  # A5 note
            wave = np.zeros(n)
            beep_len = int(sr * 0.1)
            gap_len = int(sr * 0.05)
            positions = [0, beep_len + gap_len, 2 * (beep_len + gap_len)]
            for pos in positions:
                if pos + beep_len <= n:
                    seg_t = np.linspace(0, 0.1, beep_len, False)
                    wave[pos:pos+beep_len] = np.sin(2 * np.pi * freq * seg_t) * np.exp(-seg_t * 5)
            wave = (wave * 0.3 * 32767).astype(np.int16)
            return pygame.sndarray.make_sound(np.column_stack((wave, wave)))
        except:
            return None

    def play(self, sound_name: str):
        """Play a sound effect"""
        if sound_name in self.sounds and self.sounds[sound_name]:
            self.sounds[sound_name].set_volume(self.volume)
            self.sounds[sound_name].play()

    def play_world_music(self, world: int, stage: int = 1):
        """Play background music for a specific world and stage"""
        # Stop current music
        self.stop_music()

        # Cache key is (world, stage) tuple
        cache_key = (world, stage)

        # Generate music if not cached
        if cache_key not in self.music_tracks or self.music_tracks[cache_key] is None:
            self.music_tracks[cache_key] = self.music_generator.generate_level_music(world, stage)

        # Play the track
        if self.music_tracks[cache_key]:
            self.music_tracks[cache_key].set_volume(self.music_volume)
            self.current_music_channel = self.music_tracks[cache_key].play(loops=-1)

    def stop_music(self):
        """Stop background music"""
        if self.current_music_channel:
            self.current_music_channel.stop()
            self.current_music_channel = None


class SpriteCache:
    """Cache for pre-rendered sprites to avoid per-frame generation"""
    _cache = {}

    @classmethod
    def get(cls, key):
        return cls._cache.get(key)

    @classmethod
    def set(cls, key, surface):
        cls._cache[key] = surface
        return surface

    @classmethod
    def clear(cls):
        cls._cache.clear()


class SpriteGenerator:
    """Generates NES-accurate SMB1 sprites (scaled 3x)"""

    @staticmethod
    def _draw_pixel_art(surface, pixels, palette, scale=NES_SCALE):
        """Draw pixel art from a 2D array of palette indices"""
        for y, row in enumerate(pixels):
            for x, color_idx in enumerate(row):
                if color_idx is not None and color_idx in palette:
                    color = palette[color_idx]
                    pygame.draw.rect(surface, color,
                                   (x * scale, y * scale, scale, scale))

    @staticmethod
    def create_mario_sprite(width: int = 24, height: int = 32, facing_right: bool = True,
                            is_big: bool = False, has_fire: bool = False, frame: int = 0) -> pygame.Surface:
        """Create NES-accurate Mario sprite (16x16 small, 16x32 big, scaled 3x)"""
        # Check cache first
        cache_key = f"mario_{is_big}_{has_fire}_{facing_right}_{frame % 3}"
        cached = SpriteCache.get(cache_key)
        if cached:
            return cached.copy()

        # NES Mario color palette
        T = None  # Transparent
        if has_fire:
            R = NES_PALETTE['white']  # Hat/shirt (white for fire)
            O = NES_PALETTE['fire_red']  # Overalls (red for fire)
        else:
            R = NES_PALETTE['mario_red']  # Hat/shirt
            O = NES_PALETTE['mario_brown']  # Overalls (brown in SMB1)
        S = NES_PALETTE['mario_skin']  # Skin
        B = NES_PALETTE['black']  # Black outline

        if is_big:
            # Big Mario - 16x32 pixels
            surface = pygame.Surface((16 * NES_SCALE, 32 * NES_SCALE), pygame.SRCALPHA)
            # Standing frame (NES accurate)
            pixels = [
                [T,T,T,T,T,R,R,R,R,R,R,T,T,T,T,T],
                [T,T,T,T,R,R,R,R,R,R,R,R,R,R,T,T],
                [T,T,T,T,O,O,O,S,S,B,S,T,T,T,T,T],
                [T,T,T,O,S,O,S,S,S,B,S,S,S,T,T,T],
                [T,T,T,O,S,O,O,S,S,S,B,S,S,S,T,T],
                [T,T,T,O,O,S,S,S,S,B,B,B,B,T,T,T],
                [T,T,T,T,T,S,S,S,S,S,S,S,T,T,T,T],
                [T,T,T,T,R,R,O,R,R,R,T,T,T,T,T,T],
                [T,T,T,R,R,R,O,R,R,O,R,R,R,T,T,T],
                [T,T,R,R,R,R,O,O,O,O,R,R,R,R,T,T],
                [T,T,S,S,R,O,S,O,O,S,O,R,S,S,T,T],
                [T,T,S,S,S,O,O,O,O,O,O,S,S,S,T,T],
                [T,T,S,S,O,O,O,O,O,O,O,O,S,S,T,T],
                [T,T,T,T,O,O,O,T,T,O,O,O,T,T,T,T],
                [T,T,T,O,O,O,T,T,T,T,O,O,O,T,T,T],
                [T,T,O,O,O,O,T,T,T,T,O,O,O,O,T,T],
            ]
            # Extend for full 32 height
            for _ in range(16):
                pixels.append([T]*16)
            # Draw only first 16 rows for now (simplified)
            SpriteGenerator._draw_pixel_art(surface, pixels[:16], {T: None, R: R, O: O, S: S, B: B})
        else:
            # Small Mario - 16x16 pixels (NES accurate)
            surface = pygame.Surface((16 * NES_SCALE, 16 * NES_SCALE), pygame.SRCALPHA)
            pixels = [
                [T,T,T,T,T,R,R,R,R,R,T,T,T,T,T,T],
                [T,T,T,T,R,R,R,R,R,R,R,R,R,T,T,T],
                [T,T,T,T,O,O,O,S,S,B,S,T,T,T,T,T],
                [T,T,T,O,S,O,S,S,S,B,S,S,S,T,T,T],
                [T,T,T,O,S,O,O,S,S,S,B,S,S,S,T,T],
                [T,T,T,O,O,S,S,S,S,B,B,B,B,T,T,T],
                [T,T,T,T,T,S,S,S,S,S,S,T,T,T,T,T],
                [T,T,T,T,R,R,O,R,R,T,T,T,T,T,T,T],
                [T,T,T,R,R,R,O,R,R,O,R,R,R,T,T,T],
                [T,T,R,R,R,R,O,O,O,O,R,R,R,R,T,T],
                [T,T,S,S,R,O,S,O,O,S,O,R,S,S,T,T],
                [T,T,S,S,S,O,O,O,O,O,O,S,S,S,T,T],
                [T,T,S,S,O,O,O,O,O,O,O,O,S,S,T,T],
                [T,T,T,T,O,O,O,T,T,O,O,O,T,T,T,T],
                [T,T,T,O,O,O,T,T,T,T,O,O,O,T,T,T],
                [T,T,O,O,O,O,T,T,T,T,O,O,O,O,T,T],
            ]
            SpriteGenerator._draw_pixel_art(surface, pixels, {T: None, R: R, O: O, S: S, B: B})

        if not facing_right:
            surface = pygame.transform.flip(surface, True, False)

        SpriteCache.set(cache_key, surface)
        return surface.copy()

    @staticmethod
    def create_goomba_sprite(frame: int = 0, squished: bool = False) -> pygame.Surface:
        """Create NES-accurate Goomba sprite (16x16 scaled 3x)"""
        walk_frame = frame % 2
        cache_key = f"goomba_{walk_frame}_{'squish' if squished else 'normal'}"
        cached = SpriteCache.get(cache_key)
        if cached:
            return cached.copy()

        T = None  # Transparent
        B = NES_PALETTE['goomba_brown']   # Brown body
        D = NES_PALETTE['brick_dark']      # Dark brown
        S = NES_PALETTE['mario_skin']      # Tan/skin face
        K = NES_PALETTE['black']
        W = NES_PALETTE['white']

        # Squished goomba (flattened)
        if squished:
            surface = pygame.Surface((16 * NES_SCALE, 8 * NES_SCALE), pygame.SRCALPHA)
            pixels = [
                [T,T,T,B,B,B,B,B,B,B,B,B,B,T,T,T],
                [T,B,B,B,K,K,B,B,B,B,K,K,B,B,B,T],
                [B,B,B,W,K,K,B,B,B,B,K,K,W,B,B,B],
                [B,B,B,B,B,S,S,S,S,S,S,B,B,B,B,B],
                [T,B,B,S,S,S,K,K,K,K,S,S,S,B,B,T],
                [T,T,D,D,D,D,D,D,D,D,D,D,D,D,T,T],
                [T,D,D,D,D,D,T,T,T,T,D,D,D,D,D,T],
                [D,D,D,D,T,T,T,T,T,T,T,T,D,D,D,D],
            ]
            SpriteGenerator._draw_pixel_art(surface, pixels, {T: None, B: B, D: D, S: S, K: K, W: W})
            SpriteCache.set(cache_key, surface)
            return surface.copy()

        surface = pygame.Surface((16 * NES_SCALE, 16 * NES_SCALE), pygame.SRCALPHA)

        # NES Goomba pixel art - walking animation
        if walk_frame == 0:
            pixels = [
                [T,T,T,T,T,B,B,B,B,B,B,T,T,T,T,T],
                [T,T,T,B,B,B,B,B,B,B,B,B,B,T,T,T],
                [T,T,B,B,B,B,B,B,B,B,B,B,B,B,T,T],
                [T,B,B,B,B,B,B,B,B,B,B,B,B,B,B,T],
                [T,B,B,K,K,B,B,B,B,B,B,K,K,B,B,T],
                [B,B,B,K,K,B,B,B,B,B,B,K,K,B,B,B],
                [B,B,W,K,K,B,B,B,B,B,B,K,K,W,B,B],
                [B,B,B,B,B,B,S,S,S,S,B,B,B,B,B,B],
                [T,B,B,B,S,S,S,S,S,S,S,S,B,B,B,T],
                [T,T,B,S,S,S,S,S,S,S,S,S,S,B,T,T],
                [T,T,T,S,S,K,K,K,K,K,K,S,S,T,T,T],
                [T,T,T,T,S,S,S,S,S,S,S,S,T,T,T,T],
                [T,T,T,D,D,D,D,D,D,D,D,D,D,T,T,T],
                [T,T,D,D,D,D,D,T,T,D,D,D,D,D,T,T],
                [T,D,D,D,D,T,T,T,T,T,T,D,D,D,D,T],
                [D,D,D,D,T,T,T,T,T,T,T,T,D,D,D,D],
            ]
        else:
            pixels = [
                [T,T,T,T,T,B,B,B,B,B,B,T,T,T,T,T],
                [T,T,T,B,B,B,B,B,B,B,B,B,B,T,T,T],
                [T,T,B,B,B,B,B,B,B,B,B,B,B,B,T,T],
                [T,B,B,B,B,B,B,B,B,B,B,B,B,B,B,T],
                [T,B,B,K,K,B,B,B,B,B,B,K,K,B,B,T],
                [B,B,B,K,K,B,B,B,B,B,B,K,K,B,B,B],
                [B,B,W,K,K,B,B,B,B,B,B,K,K,W,B,B],
                [B,B,B,B,B,B,S,S,S,S,B,B,B,B,B,B],
                [T,B,B,B,S,S,S,S,S,S,S,S,B,B,B,T],
                [T,T,B,S,S,S,S,S,S,S,S,S,S,B,T,T],
                [T,T,T,S,S,K,K,K,K,K,K,S,S,T,T,T],
                [T,T,T,T,S,S,S,S,S,S,S,S,T,T,T,T],
                [T,T,T,D,D,D,D,D,D,D,D,D,D,T,T,T],
                [T,T,D,D,D,D,D,T,T,D,D,D,D,D,T,T],
                [T,T,T,D,D,D,D,T,T,D,D,D,D,T,T,T],
                [T,T,D,D,D,D,T,T,T,T,D,D,D,D,T,T],
            ]

        SpriteGenerator._draw_pixel_art(surface, pixels, {T: None, B: B, D: D, S: S, K: K, W: W})
        SpriteCache.set(cache_key, surface)
        return surface.copy()

    @staticmethod
    def create_koopa_sprite(frame: int = 0, color: str = 'green') -> pygame.Surface:
        """Create NES-accurate Koopa Troopa sprite (16x24 scaled 3x)"""
        cache_key = f"koopa_{color}_{frame % 2}"
        cached = SpriteCache.get(cache_key)
        if cached:
            return cached.copy()

        surface = pygame.Surface((16 * NES_SCALE, 24 * NES_SCALE), pygame.SRCALPHA)

        T = None  # Transparent
        K = NES_PALETTE['black']
        W = NES_PALETTE['white']
        Y = NES_PALETTE['mario_skin']  # Yellow/skin for head and feet

        if color == 'green':
            G = NES_PALETTE['koopa_green']    # Shell dark green
            L = NES_PALETTE['koopa_light']    # Shell light green
        else:
            G = NES_PALETTE['mushroom_red']
            L = NES_PALETTE['fire_orange']

        # NES Koopa Troopa pixel art (16x24) - improved authentic design
        # Frame 0 = walking left foot forward, Frame 1 = walking right foot forward
        if frame % 2 == 0:
            pixels = [
                [T,T,T,T,T,T,T,T,T,T,T,T,T,T,T,T],
                [T,T,T,T,T,T,K,K,K,K,T,T,T,T,T,T],
                [T,T,T,T,T,K,Y,Y,Y,Y,K,T,T,T,T,T],
                [T,T,T,T,K,Y,Y,Y,Y,Y,Y,K,T,T,T,T],
                [T,T,T,T,K,Y,K,Y,Y,K,Y,K,T,T,T,T],
                [T,T,T,T,K,Y,W,K,K,W,Y,K,T,T,T,T],
                [T,T,T,T,T,K,Y,Y,Y,Y,K,T,T,T,T,T],
                [T,T,T,T,T,T,K,K,K,K,T,T,T,T,T,T],
                [T,T,T,T,K,K,G,G,G,G,K,K,T,T,T,T],
                [T,T,T,K,G,G,G,G,G,G,G,G,K,T,T,T],
                [T,T,K,G,G,L,L,G,G,L,L,G,G,K,T,T],
                [T,T,K,G,L,L,L,L,L,L,L,L,G,K,T,T],
                [T,K,G,G,L,W,L,L,L,L,W,L,G,G,K,T],
                [T,K,G,G,L,L,L,L,L,L,L,L,G,G,K,T],
                [T,K,G,G,G,L,L,L,L,L,L,G,G,G,K,T],
                [T,T,K,G,G,G,L,L,L,L,G,G,G,K,T,T],
                [T,T,T,K,G,G,G,G,G,G,G,G,K,T,T,T],
                [T,T,T,T,K,K,G,G,G,G,K,K,T,T,T,T],
                [T,T,T,T,T,K,Y,Y,Y,Y,K,T,T,T,T,T],
                [T,T,T,T,K,Y,Y,K,K,Y,Y,K,T,T,T,T],
                [T,T,T,K,Y,Y,K,T,T,K,Y,Y,K,T,T,T],
                [T,T,K,Y,Y,K,T,T,T,T,K,Y,Y,K,T,T],
                [T,T,K,K,K,T,T,T,T,T,T,K,K,K,T,T],
                [T,T,T,T,T,T,T,T,T,T,T,T,T,T,T,T],
            ]
        else:
            pixels = [
                [T,T,T,T,T,T,T,T,T,T,T,T,T,T,T,T],
                [T,T,T,T,T,T,K,K,K,K,T,T,T,T,T,T],
                [T,T,T,T,T,K,Y,Y,Y,Y,K,T,T,T,T,T],
                [T,T,T,T,K,Y,Y,Y,Y,Y,Y,K,T,T,T,T],
                [T,T,T,T,K,Y,K,Y,Y,K,Y,K,T,T,T,T],
                [T,T,T,T,K,Y,W,K,K,W,Y,K,T,T,T,T],
                [T,T,T,T,T,K,Y,Y,Y,Y,K,T,T,T,T,T],
                [T,T,T,T,T,T,K,K,K,K,T,T,T,T,T,T],
                [T,T,T,T,K,K,G,G,G,G,K,K,T,T,T,T],
                [T,T,T,K,G,G,G,G,G,G,G,G,K,T,T,T],
                [T,T,K,G,G,L,L,G,G,L,L,G,G,K,T,T],
                [T,T,K,G,L,L,L,L,L,L,L,L,G,K,T,T],
                [T,K,G,G,L,W,L,L,L,L,W,L,G,G,K,T],
                [T,K,G,G,L,L,L,L,L,L,L,L,G,G,K,T],
                [T,K,G,G,G,L,L,L,L,L,L,G,G,G,K,T],
                [T,T,K,G,G,G,L,L,L,L,G,G,G,K,T,T],
                [T,T,T,K,G,G,G,G,G,G,G,G,K,T,T,T],
                [T,T,T,T,K,K,G,G,G,G,K,K,T,T,T,T],
                [T,T,T,T,K,Y,Y,T,T,Y,Y,K,T,T,T,T],
                [T,T,T,K,Y,Y,K,T,T,K,Y,Y,K,T,T,T],
                [T,T,K,Y,Y,K,T,T,T,T,K,Y,Y,K,T,T],
                [T,T,K,K,K,T,T,T,T,T,T,K,K,K,T,T],
                [T,T,T,T,T,T,T,T,T,T,T,T,T,T,T,T],
                [T,T,T,T,T,T,T,T,T,T,T,T,T,T,T,T],
            ]

        SpriteGenerator._draw_pixel_art(surface, pixels, {T: None, K: K, W: W, Y: Y, G: G, L: L})
        SpriteCache.set(cache_key, surface)
        return surface.copy()

    @staticmethod
    def create_koopa_shell_sprite(color: str = 'green') -> pygame.Surface:
        """Create NES-accurate Koopa shell sprite (16x16 scaled 3x)"""
        cache_key = f"koopa_shell_{color}"
        cached = SpriteCache.get(cache_key)
        if cached:
            return cached.copy()

        surface = pygame.Surface((16 * NES_SCALE, 16 * NES_SCALE), pygame.SRCALPHA)

        T = None  # Transparent
        K = NES_PALETTE['black']
        W = NES_PALETTE['white']

        if color == 'green':
            G = NES_PALETTE['koopa_green']    # Shell dark green
            L = NES_PALETTE['koopa_light']    # Shell light green
        else:
            G = NES_PALETTE['mushroom_red']
            L = NES_PALETTE['fire_orange']

        # NES Koopa shell pixel art (16x16)
        pixels = [
            [T,T,T,T,T,K,K,K,K,K,K,T,T,T,T,T],
            [T,T,T,K,K,G,G,G,G,G,G,K,K,T,T,T],
            [T,T,K,G,G,G,G,G,G,G,G,G,G,K,T,T],
            [T,K,G,G,G,L,L,G,G,L,L,G,G,G,K,T],
            [T,K,G,G,L,L,L,L,L,L,L,L,G,G,K,T],
            [K,G,G,G,L,W,L,L,L,L,W,L,G,G,G,K],
            [K,G,G,G,L,L,L,L,L,L,L,L,G,G,G,K],
            [K,G,G,G,G,L,L,L,L,L,L,G,G,G,G,K],
            [K,G,G,G,G,G,L,L,L,L,G,G,G,G,G,K],
            [K,G,G,G,G,G,G,G,G,G,G,G,G,G,G,K],
            [T,K,G,G,G,G,G,G,G,G,G,G,G,G,K,T],
            [T,K,G,G,G,G,G,G,G,G,G,G,G,G,K,T],
            [T,T,K,G,G,G,G,G,G,G,G,G,G,K,T,T],
            [T,T,T,K,K,G,G,G,G,G,G,K,K,T,T,T],
            [T,T,T,T,T,K,K,K,K,K,K,T,T,T,T,T],
            [T,T,T,T,T,T,T,T,T,T,T,T,T,T,T,T],
        ]

        SpriteGenerator._draw_pixel_art(surface, pixels, {T: None, K: K, W: W, G: G, L: L})
        SpriteCache.set(cache_key, surface)
        return surface.copy()

    @staticmethod
    def create_brick_sprite() -> pygame.Surface:
        """Create NES-accurate brick block sprite (16x16 scaled 3x)"""
        cache_key = "brick"
        cached = SpriteCache.get(cache_key)
        if cached:
            return cached.copy()

        surface = pygame.Surface((16 * NES_SCALE, 16 * NES_SCALE))

        B = NES_PALETTE['brick_orange']  # Main brick color
        D = NES_PALETTE['brick_dark']     # Dark mortar/shadow
        K = NES_PALETTE['black']          # Black outline

        # NES brick block pixel art
        pixels = [
            [K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K],
            [K,B,B,B,B,B,B,K,K,B,B,B,B,B,B,K],
            [K,B,B,B,B,B,B,K,K,B,B,B,B,B,B,K],
            [K,B,B,B,B,B,B,K,K,B,B,B,B,B,B,K],
            [K,B,B,B,B,B,B,K,K,B,B,B,B,B,B,K],
            [K,B,B,B,B,B,B,K,K,B,B,B,B,B,B,K],
            [K,B,B,B,B,B,B,K,K,B,B,B,B,B,B,K],
            [K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K],
            [K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K],
            [K,B,B,K,K,B,B,B,B,B,B,K,K,B,B,K],
            [K,B,B,K,K,B,B,B,B,B,B,K,K,B,B,K],
            [K,B,B,K,K,B,B,B,B,B,B,K,K,B,B,K],
            [K,B,B,K,K,B,B,B,B,B,B,K,K,B,B,K],
            [K,B,B,K,K,B,B,B,B,B,B,K,K,B,B,K],
            [K,B,B,K,K,B,B,B,B,B,B,K,K,B,B,K],
            [K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K],
        ]

        SpriteGenerator._draw_pixel_art(surface, pixels, {B: B, D: D, K: K})
        SpriteCache.set(cache_key, surface)
        return surface.copy()

    @staticmethod
    def create_question_block_sprite(hit: bool = False, frame: int = 0) -> pygame.Surface:
        """Create NES-accurate question block sprite (16x16 scaled 3x)"""
        cache_key = f"qblock_{hit}_{(frame // 8) % 4}"
        cached = SpriteCache.get(cache_key)
        if cached:
            return cached.copy()

        surface = pygame.Surface((16 * NES_SCALE, 16 * NES_SCALE))

        if hit:
            # Used/empty block
            B = NES_PALETTE['brick_dark']
            K = NES_PALETTE['black']
            pixels = [
                [K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K],
                [K,B,B,B,B,B,B,B,B,B,B,B,B,B,B,K],
                [K,B,B,B,B,B,B,B,B,B,B,B,B,B,B,K],
                [K,B,B,B,B,B,B,B,B,B,B,B,B,B,B,K],
                [K,B,B,B,B,B,B,B,B,B,B,B,B,B,B,K],
                [K,B,B,B,B,B,B,B,B,B,B,B,B,B,B,K],
                [K,B,B,B,B,B,B,B,B,B,B,B,B,B,B,K],
                [K,B,B,B,B,B,B,B,B,B,B,B,B,B,B,K],
                [K,B,B,B,B,B,B,B,B,B,B,B,B,B,B,K],
                [K,B,B,B,B,B,B,B,B,B,B,B,B,B,B,K],
                [K,B,B,B,B,B,B,B,B,B,B,B,B,B,B,K],
                [K,B,B,B,B,B,B,B,B,B,B,B,B,B,B,K],
                [K,B,B,B,B,B,B,B,B,B,B,B,B,B,B,K],
                [K,B,B,B,B,B,B,B,B,B,B,B,B,B,B,K],
                [K,B,B,B,B,B,B,B,B,B,B,B,B,B,B,K],
                [K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K],
            ]
            SpriteGenerator._draw_pixel_art(surface, pixels, {B: B, K: K})
        else:
            # Active question block with ? mark
            O = NES_PALETTE['qblock_orange']  # Orange
            D = NES_PALETTE['qblock_dark']    # Dark orange
            K = NES_PALETTE['black']

            pixels = [
                [K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K],
                [K,O,O,O,O,O,O,O,O,O,O,O,O,O,D,K],
                [K,O,O,O,O,O,O,O,O,O,O,O,O,O,D,K],
                [K,O,O,O,O,D,D,D,D,D,O,O,O,O,D,K],
                [K,O,O,O,D,D,O,O,O,D,D,O,O,O,D,K],
                [K,O,O,O,D,D,O,O,O,D,D,O,O,O,D,K],
                [K,O,O,O,O,O,O,O,D,D,O,O,O,O,D,K],
                [K,O,O,O,O,O,O,D,D,O,O,O,O,O,D,K],
                [K,O,O,O,O,O,D,D,O,O,O,O,O,O,D,K],
                [K,O,O,O,O,O,D,D,O,O,O,O,O,O,D,K],
                [K,O,O,O,O,O,O,O,O,O,O,O,O,O,D,K],
                [K,O,O,O,O,O,D,D,O,O,O,O,O,O,D,K],
                [K,O,O,O,O,O,D,D,O,O,O,O,O,O,D,K],
                [K,O,O,O,O,O,O,O,O,O,O,O,O,O,D,K],
                [K,D,D,D,D,D,D,D,D,D,D,D,D,D,D,K],
                [K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K],
            ]
            SpriteGenerator._draw_pixel_art(surface, pixels, {O: O, D: D, K: K})

        SpriteCache.set(cache_key, surface)
        return surface.copy()

    @staticmethod
    def create_coin_sprite(frame: int = 0) -> pygame.Surface:
        """Create NES-accurate coin sprite (8x16 scaled 3x, 4 frame animation)"""
        anim_frame = (frame // 8) % 4
        cache_key = f"coin_{anim_frame}"
        cached = SpriteCache.get(cache_key)
        if cached:
            return cached.copy()

        surface = pygame.Surface((8 * NES_SCALE, 16 * NES_SCALE), pygame.SRCALPHA)

        T = None
        O = NES_PALETTE['coin_orange']
        D = NES_PALETTE['coin_dark']
        K = NES_PALETTE['black']

        # 4 frames of coin animation (spinning)
        coin_frames = [
            # Frame 0 - full
            [
                [T,T,O,O,O,O,T,T],
                [T,O,D,D,D,D,O,T],
                [O,D,O,D,D,O,D,O],
                [O,D,D,D,D,D,D,O],
                [O,D,O,D,D,O,D,O],
                [O,D,D,D,D,D,D,O],
                [O,D,O,D,D,O,D,O],
                [O,D,D,D,D,D,D,O],
                [O,D,O,D,D,O,D,O],
                [O,D,D,D,D,D,D,O],
                [O,D,O,D,D,O,D,O],
                [O,D,D,D,D,D,D,O],
                [O,D,O,D,D,O,D,O],
                [O,D,D,D,D,D,D,O],
                [T,O,D,D,D,D,O,T],
                [T,T,O,O,O,O,T,T],
            ],
            # Frame 1 - narrower
            [
                [T,T,T,O,O,T,T,T],
                [T,T,O,D,D,O,T,T],
                [T,T,O,D,D,O,T,T],
                [T,T,O,D,D,O,T,T],
                [T,T,O,D,D,O,T,T],
                [T,T,O,D,D,O,T,T],
                [T,T,O,D,D,O,T,T],
                [T,T,O,D,D,O,T,T],
                [T,T,O,D,D,O,T,T],
                [T,T,O,D,D,O,T,T],
                [T,T,O,D,D,O,T,T],
                [T,T,O,D,D,O,T,T],
                [T,T,O,D,D,O,T,T],
                [T,T,O,D,D,O,T,T],
                [T,T,O,D,D,O,T,T],
                [T,T,T,O,O,T,T,T],
            ],
            # Frame 2 - thin line
            [
                [T,T,T,O,O,T,T,T],
                [T,T,T,O,O,T,T,T],
                [T,T,T,O,O,T,T,T],
                [T,T,T,O,O,T,T,T],
                [T,T,T,O,O,T,T,T],
                [T,T,T,O,O,T,T,T],
                [T,T,T,O,O,T,T,T],
                [T,T,T,O,O,T,T,T],
                [T,T,T,O,O,T,T,T],
                [T,T,T,O,O,T,T,T],
                [T,T,T,O,O,T,T,T],
                [T,T,T,O,O,T,T,T],
                [T,T,T,O,O,T,T,T],
                [T,T,T,O,O,T,T,T],
                [T,T,T,O,O,T,T,T],
                [T,T,T,O,O,T,T,T],
            ],
            # Frame 3 - narrower (same as 1)
            [
                [T,T,T,O,O,T,T,T],
                [T,T,O,D,D,O,T,T],
                [T,T,O,D,D,O,T,T],
                [T,T,O,D,D,O,T,T],
                [T,T,O,D,D,O,T,T],
                [T,T,O,D,D,O,T,T],
                [T,T,O,D,D,O,T,T],
                [T,T,O,D,D,O,T,T],
                [T,T,O,D,D,O,T,T],
                [T,T,O,D,D,O,T,T],
                [T,T,O,D,D,O,T,T],
                [T,T,O,D,D,O,T,T],
                [T,T,O,D,D,O,T,T],
                [T,T,O,D,D,O,T,T],
                [T,T,O,D,D,O,T,T],
                [T,T,T,O,O,T,T,T],
            ],
        ]

        SpriteGenerator._draw_pixel_art(surface, coin_frames[anim_frame], {T: None, O: O, D: D, K: K})
        SpriteCache.set(cache_key, surface)
        return surface.copy()

    @staticmethod
    def create_pipe_sprite(height: int = 2) -> pygame.Surface:
        """Create NES-accurate pipe sprite (32x variable height, scaled 3x)"""
        cache_key = f"pipe_{height}"
        cached = SpriteCache.get(cache_key)
        if cached:
            return cached.copy()

        # Pipe is 2 tiles wide (32 NES pixels)
        width = 32 * NES_SCALE
        h = 16 * height * NES_SCALE
        surface = pygame.Surface((width, h))

        G = NES_PALETTE['pipe_green']
        D = NES_PALETTE['pipe_dark']
        L = NES_PALETTE['pipe_light']
        K = NES_PALETTE['black']

        # Draw pipe top (first 16 pixels tall)
        top_pixels = [
            [K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K],
            [K,D,D,D,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,L,L,L,L,K],
            [K,D,D,D,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,L,L,L,L,K],
            [K,D,D,D,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,L,L,L,L,K],
            [K,D,D,D,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,L,L,L,L,K],
            [K,D,D,D,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,L,L,L,L,K],
            [K,D,D,D,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,L,L,L,L,K],
            [K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K],
        ]

        # Draw pipe body (repeating)
        body_pixels = [
            [K,K,K,K,D,D,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,L,L,K,K,K,K],
            [K,K,K,K,D,D,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,G,L,L,K,K,K,K],
        ]

        # Draw top
        for y, row in enumerate(top_pixels):
            for x, c in enumerate(row):
                color = {K: K, D: D, G: G, L: L}.get(c, K)
                pygame.draw.rect(surface, color, (x * NES_SCALE, y * NES_SCALE, NES_SCALE, NES_SCALE))

        # Draw body
        for tile_y in range(height):
            start_y = (8 + tile_y * 16) * NES_SCALE
            for y in range(16):
                row = body_pixels[y % 2]
                for x, c in enumerate(row):
                    color = {K: K, D: D, G: G, L: L}.get(c, K)
                    pygame.draw.rect(surface, color, (x * NES_SCALE, start_y + y * NES_SCALE, NES_SCALE, NES_SCALE))

        SpriteCache.set(cache_key, surface)
        return surface.copy()

    @staticmethod
    def create_ground_tile(world: int = 1) -> pygame.Surface:
        """Create NES-accurate ground/floor tile (16x16 scaled 3x)"""
        cache_key = f"ground_{world}"
        cached = SpriteCache.get(cache_key)
        if cached:
            return cached.copy()

        surface = pygame.Surface((16 * NES_SCALE, 16 * NES_SCALE))

        O = NES_PALETTE['ground_orange']
        T = NES_PALETTE['ground_tan']
        K = NES_PALETTE['black']

        # NES ground block (solid color with pattern)
        pixels = [
            [O,O,O,O,O,O,O,O,O,O,O,O,O,O,O,O],
            [O,T,T,T,T,T,T,T,T,T,T,T,T,T,T,O],
            [O,T,O,O,O,O,O,O,O,O,O,O,O,O,T,O],
            [O,T,O,O,O,O,O,O,O,O,O,O,O,O,T,O],
            [O,T,O,O,O,O,O,O,O,O,O,O,O,O,T,O],
            [O,T,O,O,O,O,O,O,O,O,O,O,O,O,T,O],
            [O,T,O,O,O,O,O,O,O,O,O,O,O,O,T,O],
            [O,T,O,O,O,O,O,O,O,O,O,O,O,O,T,O],
            [O,T,O,O,O,O,O,O,O,O,O,O,O,O,T,O],
            [O,T,O,O,O,O,O,O,O,O,O,O,O,O,T,O],
            [O,T,O,O,O,O,O,O,O,O,O,O,O,O,T,O],
            [O,T,O,O,O,O,O,O,O,O,O,O,O,O,T,O],
            [O,T,O,O,O,O,O,O,O,O,O,O,O,O,T,O],
            [O,T,O,O,O,O,O,O,O,O,O,O,O,O,T,O],
            [O,T,T,T,T,T,T,T,T,T,T,T,T,T,T,O],
            [O,O,O,O,O,O,O,O,O,O,O,O,O,O,O,O],
        ]

        SpriteGenerator._draw_pixel_art(surface, pixels, {O: O, T: T, K: K})
        SpriteCache.set(cache_key, surface)
        return surface.copy()

    @staticmethod
    def create_flagpole_sprite() -> pygame.Surface:
        """Create NES-accurate flagpole (pole only, no flag)"""
        cache_key = "flagpole"
        cached = SpriteCache.get(cache_key)
        if cached:
            return cached.copy()

        # Flagpole is 1 tile wide, 10 tiles tall
        surface = pygame.Surface((16 * NES_SCALE, 160 * NES_SCALE), pygame.SRCALPHA)

        G = NES_PALETTE['pipe_green']
        W = NES_PALETTE['white']

        # Draw flagpole
        pole_x = 7 * NES_SCALE
        pygame.draw.rect(surface, W, (pole_x, 8 * NES_SCALE, 2 * NES_SCALE, 150 * NES_SCALE))

        # Ball on top
        pygame.draw.circle(surface, G, (8 * NES_SCALE, 6 * NES_SCALE), 4 * NES_SCALE)

        SpriteCache.set(cache_key, surface)
        return surface.copy()

    @staticmethod
    def create_flag_sprite() -> pygame.Surface:
        """Create NES-accurate flag (flag banner only)"""
        cache_key = "flag_banner"
        cached = SpriteCache.get(cache_key)
        if cached:
            return cached.copy()

        # Flag banner is roughly 16x16 pixels
        surface = pygame.Surface((16 * NES_SCALE, 16 * NES_SCALE), pygame.SRCALPHA)

        G = NES_PALETTE['pipe_green']

        # Flag (green triangle/pennant shape)
        for y in range(16):
            width = 16 - y if y < 8 else y - 8 + 8
            pygame.draw.rect(surface, G, (0, y * NES_SCALE, width * NES_SCALE, NES_SCALE))

        SpriteCache.set(cache_key, surface)
        return surface.copy()

    @staticmethod
    def create_mushroom_sprite(type: str = 'super') -> pygame.Surface:
        """Create NES-accurate mushroom sprite (16x16 scaled 3x)"""
        cache_key = f"mushroom_{type}"
        cached = SpriteCache.get(cache_key)
        if cached:
            return cached.copy()

        surface = pygame.Surface((16 * NES_SCALE, 16 * NES_SCALE), pygame.SRCALPHA)

        T = None
        W = NES_PALETTE['white']
        S = NES_PALETTE['mushroom_tan']
        K = NES_PALETTE['black']

        if type == 'super':
            R = NES_PALETTE['mushroom_red']
        elif type == '1up':
            R = NES_PALETTE['pipe_green']
        else:
            R = NES_PALETTE['mushroom_red']

        # NES mushroom pixel art
        pixels = [
            [T,T,T,T,T,R,R,R,R,R,R,T,T,T,T,T],
            [T,T,T,R,R,R,R,R,R,R,R,R,R,T,T,T],
            [T,T,R,R,W,W,R,R,R,R,W,W,R,R,T,T],
            [T,R,R,W,W,W,W,R,R,W,W,W,W,R,R,T],
            [T,R,R,W,W,W,W,R,R,W,W,W,W,R,R,T],
            [R,R,R,W,W,W,W,R,R,W,W,W,W,R,R,R],
            [R,R,R,R,W,W,R,R,R,R,W,W,R,R,R,R],
            [R,R,R,R,R,R,R,R,R,R,R,R,R,R,R,R],
            [R,R,R,R,R,R,R,R,R,R,R,R,R,R,R,R],
            [T,R,R,R,R,R,S,S,S,S,R,R,R,R,R,T],
            [T,T,R,R,S,S,S,S,S,S,S,S,R,R,T,T],
            [T,T,T,T,S,S,S,S,S,S,S,S,T,T,T,T],
            [T,T,T,T,S,S,S,S,S,S,S,S,T,T,T,T],
            [T,T,T,T,S,S,S,S,S,S,S,S,T,T,T,T],
            [T,T,T,T,S,S,S,S,S,S,S,S,T,T,T,T],
            [T,T,T,T,T,S,S,S,S,S,S,T,T,T,T,T],
        ]

        SpriteGenerator._draw_pixel_art(surface, pixels, {T: None, R: R, W: W, S: S, K: K})
        SpriteCache.set(cache_key, surface)
        return surface.copy()

    @staticmethod
    def create_star_sprite(frame: int = 0) -> pygame.Surface:
        """Create NES-accurate star (Starman) sprite (16x16 scaled 3x)"""
        anim_frame = (frame // 4) % 4
        cache_key = f"star_{anim_frame}"
        cached = SpriteCache.get(cache_key)
        if cached:
            return cached.copy()

        surface = pygame.Surface((16 * NES_SCALE, 16 * NES_SCALE), pygame.SRCALPHA)

        T = None
        K = NES_PALETTE['black']

        # Color cycling like NES
        star_colors = [
            NES_PALETTE['star_yellow'],
            NES_PALETTE['pipe_green'],
            NES_PALETTE['sky_blue'],
            NES_PALETTE['mushroom_red'],
        ]
        Y = star_colors[anim_frame]

        # NES star pixel art
        pixels = [
            [T,T,T,T,T,T,T,Y,Y,T,T,T,T,T,T,T],
            [T,T,T,T,T,T,T,Y,Y,T,T,T,T,T,T,T],
            [T,T,T,T,T,T,Y,Y,Y,Y,T,T,T,T,T,T],
            [T,T,T,T,T,T,Y,Y,Y,Y,T,T,T,T,T,T],
            [Y,Y,Y,Y,Y,Y,Y,Y,Y,Y,Y,Y,Y,Y,Y,Y],
            [T,Y,Y,Y,Y,Y,Y,Y,Y,Y,Y,Y,Y,Y,Y,T],
            [T,T,Y,Y,Y,K,K,Y,Y,K,K,Y,Y,Y,T,T],
            [T,T,T,Y,Y,K,K,Y,Y,K,K,Y,Y,T,T,T],
            [T,T,T,Y,Y,Y,Y,Y,Y,Y,Y,Y,Y,T,T,T],
            [T,T,T,T,Y,Y,Y,Y,Y,Y,Y,Y,T,T,T,T],
            [T,T,T,T,Y,Y,Y,Y,Y,Y,Y,Y,T,T,T,T],
            [T,T,T,Y,Y,Y,Y,T,T,Y,Y,Y,Y,T,T,T],
            [T,T,Y,Y,Y,Y,T,T,T,T,Y,Y,Y,Y,T,T],
            [T,Y,Y,Y,Y,T,T,T,T,T,T,Y,Y,Y,Y,T],
            [Y,Y,Y,Y,T,T,T,T,T,T,T,T,Y,Y,Y,Y],
            [Y,Y,T,T,T,T,T,T,T,T,T,T,T,T,Y,Y],
        ]

        SpriteGenerator._draw_pixel_art(surface, pixels, {T: None, Y: Y, K: K})
        SpriteCache.set(cache_key, surface)
        return surface.copy()

    @staticmethod
    def create_fire_flower_sprite(frame: int = 0) -> pygame.Surface:
        """Create NES-accurate Fire Flower sprite (16x16 scaled 3x)"""
        anim_frame = (frame // 4) % 4
        cache_key = f"fireflower_{anim_frame}"
        cached = SpriteCache.get(cache_key)
        if cached:
            return cached.copy()

        surface = pygame.Surface((16 * NES_SCALE, 16 * NES_SCALE), pygame.SRCALPHA)

        T = None
        K = NES_PALETTE['black']
        G = NES_PALETTE['pipe_green']
        W = NES_PALETTE['white']

        # Color cycling like NES
        flower_colors = [
            (NES_PALETTE['fire_red'], NES_PALETTE['fire_orange']),
            (NES_PALETTE['fire_orange'], NES_PALETTE['fire_red']),
            (NES_PALETTE['star_yellow'], NES_PALETTE['fire_red']),
            (NES_PALETTE['fire_red'], NES_PALETTE['star_yellow']),
        ]
        R, O = flower_colors[anim_frame]

        # NES fire flower pixel art
        pixels = [
            [T,T,T,T,T,T,R,R,R,R,T,T,T,T,T,T],
            [T,T,T,T,R,R,O,O,O,O,R,R,T,T,T,T],
            [T,T,T,R,O,O,O,W,W,O,O,O,R,T,T,T],
            [T,T,R,O,O,W,W,W,W,W,W,O,O,R,T,T],
            [T,R,O,O,W,W,K,W,W,K,W,W,O,O,R,T],
            [T,R,O,O,W,W,K,W,W,K,W,W,O,O,R,T],
            [R,O,O,O,O,W,W,W,W,W,W,O,O,O,O,R],
            [R,O,O,O,O,O,O,O,O,O,O,O,O,O,O,R],
            [T,R,O,O,O,O,G,G,G,G,O,O,O,O,R,T],
            [T,T,R,R,G,G,G,G,G,G,G,G,R,R,T,T],
            [T,T,T,T,G,G,G,G,G,G,G,G,T,T,T,T],
            [T,T,T,T,G,G,G,G,G,G,G,G,T,T,T,T],
            [T,T,T,T,G,G,G,G,G,G,G,G,T,T,T,T],
            [T,T,T,G,G,G,T,T,T,T,G,G,G,T,T,T],
            [T,T,G,G,G,T,T,T,T,T,T,G,G,G,T,T],
            [T,T,G,G,T,T,T,T,T,T,T,T,G,G,T,T],
        ]

        SpriteGenerator._draw_pixel_art(surface, pixels, {T: None, R: R, O: O, G: G, W: W, K: K})
        SpriteCache.set(cache_key, surface)
        return surface.copy()

    @staticmethod
    def create_coin_block_sprite(frame: int = 0) -> pygame.Surface:
        """Create spinning coin from block sprite"""
        surface = pygame.Surface((16, 24), pygame.SRCALPHA)

        # Animate width for spinning effect
        phase = (frame % 16) / 16.0
        width = int(14 * abs(math.cos(phase * math.pi * 2)))
        width = max(2, width)

        x_offset = (16 - width) // 2

        # Outer edge (darker gold)
        pygame.draw.ellipse(surface, (180, 140, 20), (x_offset, 0, width, 24))
        # Main coin body
        if width > 4:
            pygame.draw.ellipse(surface, COIN_YELLOW, (x_offset + 1, 1, width - 2, 22))
        # Inner highlight
        if width > 8:
            pygame.draw.ellipse(surface, (255, 240, 150), (x_offset + 3, 4, width - 6, 16))

        return surface


class Player(pygame.sprite.Sprite):
    """
    Mario - Nintendo EAD SMB1 Physics Engine
    Based on reverse-engineering of original Famicom ROM
    Physics values from Bisqwit's SMB1 disassembly
    
    Design Philosophy (Miyamoto/Tezuka):
    - Responsive but weighty movement
    - Variable jump height rewards skill
    - Momentum carries through actions
    - "Feel" of controlling a real character
    """
    def __init__(self, x: int, y: int):
        super().__init__()
        # NES dimensions scaled 3x (16x16 small, 16x32 big)
        self.width = 16 * NES_SCALE
        self.height = 16 * NES_SCALE
        self.animation_frame = 0
        self.facing_right = True
        self.is_big = False
        self.has_fire = False

        self.image = SpriteGenerator.create_mario_sprite(
            self.width, self.height, self.facing_right, self.is_big, self.has_fire
        )
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # === SMB1 PHYSICS - FIXED (snappy, responsive) ===
        self.pos_x = float(x)
        self.pos_y = float(y)
        self.vel_x = 0.0
        self.vel_y = 0.0

        # Simple, responsive physics (no lag)
        self.WALK_ACCEL = 0.5            # Snappy acceleration
        self.WALK_MAX = 4.5              # Walk speed
        self.RUN_ACCEL = 0.6             # Run acceleration
        self.RUN_MAX = 8.0               # Run speed
        self.FRICTION = 0.5              # Ground friction
        self.SKID_DECEL = 0.8            # Skid deceleration
        
        # Jump physics - simple and responsive
        self.JUMP_POWER = -13.0          # Base jump velocity
        self.JUMP_POWER_RUN = -14.5      # Running jump (higher)
        self.GRAVITY = 0.6               # Normal gravity
        self.GRAVITY_HOLD = 0.35         # Gravity while holding jump
        self.MAX_FALL = 12.0             # Terminal velocity
        
        # Coyote time and jump buffer
        self.coyote_frames = 0
        self.COYOTE_TIME = 5
        self.jump_buffer = 0
        self.JUMP_BUFFER_TIME = 6
        
        # === STATE ===
        self.on_ground = False
        self.was_on_ground = False
        self.is_jumping = False
        self.jump_held = False
        self.is_skidding = False
        self.is_running = False
        
        # Animation state
        self.walk_frame = 0
        self.walk_timer = 0
        
        # === GAME STATE ===
        self.lives = 3
        self.coins = 0
        self.score = 0
        self.invincible = False
        self.invincible_timer = 0
        self.star_power = False
        self.star_timer = 0
        
        # SMB1 stomp combo (consecutive stomps without landing)
        self.stomp_combo = 0
        self.stomp_scores = [100, 200, 400, 500, 800, 1000, 2000, 4000, 5000, 8000]

    def update_sprite(self):
        """Update Mario's sprite based on current state"""
        self.animation_frame += 1
        self.image = SpriteGenerator.create_mario_sprite(
            self.width, 48 if self.is_big else 32,
            self.facing_right, self.is_big, self.has_fire,
            self.animation_frame // 5
        )

        # Star power color cycling effect (like SMB3)
        if self.star_power:
            # Create color overlay effect
            star_colors = [
                (255, 100, 100, 128),  # Red tint
                (100, 255, 100, 128),  # Green tint
                (100, 100, 255, 128),  # Blue tint
                (255, 255, 100, 128),  # Yellow tint
            ]
            color_idx = (self.animation_frame // 3) % len(star_colors)
            overlay = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
            overlay.fill(star_colors[color_idx])
            self.image.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        # Handle invincibility flashing (damage invincibility)
        elif self.invincible and (self.invincible_timer // 5) % 2 == 0:
            self.image.set_alpha(128)
        else:
            self.image.set_alpha(255)

    def update(self, platforms, sound_manager):
        """
        SMB1 Physics - Simple and Responsive
        """
        keys = pygame.key.get_pressed()
        
        # Input
        self.is_running = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        moving_left = keys[pygame.K_LEFT] or keys[pygame.K_a]
        moving_right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        jump_held = keys[pygame.K_SPACE]
        
        # Track ground state
        was_on_ground = self.on_ground
        
        # Physics values based on run state
        accel = self.RUN_ACCEL if self.is_running else self.WALK_ACCEL
        max_speed = self.RUN_MAX if self.is_running else self.WALK_MAX
        
        self.is_skidding = False
        
        # Horizontal movement
        if moving_right and not moving_left:
            if self.vel_x < -1.0 and self.on_ground:
                self.is_skidding = True
                self.vel_x += self.SKID_DECEL
            else:
                self.vel_x += accel
                if self.vel_x > max_speed:
                    self.vel_x = max_speed
            self.facing_right = True
            
        elif moving_left and not moving_right:
            if self.vel_x > 1.0 and self.on_ground:
                self.is_skidding = True
                self.vel_x -= self.SKID_DECEL
            else:
                self.vel_x -= accel
                if self.vel_x < -max_speed:
                    self.vel_x = -max_speed
            self.facing_right = False
            
        else:
            # Apply friction on ground only
            if self.on_ground:
                if self.vel_x > 0:
                    self.vel_x = max(0, self.vel_x - self.FRICTION)
                elif self.vel_x < 0:
                    self.vel_x = min(0, self.vel_x + self.FRICTION)
        
        # Coyote time
        if was_on_ground and not self.on_ground and self.vel_y >= 0:
            self.coyote_frames = self.COYOTE_TIME
        elif self.coyote_frames > 0:
            self.coyote_frames -= 1
        
        # Gravity - simple variable jump
        if self.is_jumping and self.jump_held and jump_held and self.vel_y < 0:
            self.vel_y += self.GRAVITY_HOLD
        else:
            self.vel_y += self.GRAVITY
            if not jump_held:
                self.jump_held = False
        
        # Terminal velocity
        if self.vel_y > self.MAX_FALL:
            self.vel_y = self.MAX_FALL
        
        # Apply movement
        self.pos_x += self.vel_x
        self.rect.x = int(self.pos_x)
        self._check_collision_x(platforms)
        self.pos_x = float(self.rect.x)
        
        self.pos_y += self.vel_y
        self.rect.y = int(self.pos_y)
        self.on_ground = False
        self._check_collision_y(platforms)
        self.pos_y = float(self.rect.y)
        
        # Timers
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
        
        if self.star_power:
            self.star_timer -= 1
            if self.star_timer <= 0:
                self.star_power = False
        
        # === SCREEN BOUNDS (SMB1: can't go left) ===
        if self.rect.left < 0:
            self.rect.left = 0
            self.pos_x = float(self.rect.x)
            self.vel_x = 0
        
        # Update sprite
        self.update_sprite()

    def jump(self, sound_manager):
        """SMB1 Jump - simple and responsive"""
        can_jump = self.on_ground or self.coyote_frames > 0
        
        if can_jump:
            # Higher jump when running
            if self.is_running and abs(self.vel_x) > 4.0:
                self.vel_y = self.JUMP_POWER_RUN
            else:
                self.vel_y = self.JUMP_POWER
            
            self.on_ground = False
            self.is_jumping = True
            self.jump_held = True
            self.coyote_frames = 0
            sound_manager.play('jump')
            return True
        return False

    def release_jump(self):
        """Release jump button - allows variable jump height"""
        self.jump_held = False

    def shoot_fireball(self, sound_manager) -> Optional['Fireball']:
        """Fire Mario shoots a fireball - SMB1 style (max 2 on screen)"""
        if self.has_fire:
            direction = 1 if self.facing_right else -1
            fireball_x = self.rect.right if self.facing_right else self.rect.left - 8 * NES_SCALE
            fireball_y = self.rect.centery
            sound_manager.play('stomp')  # Use stomp sound for now
            return Fireball(fireball_x, fireball_y, direction)
        return None

    def _check_collision_x(self, platforms):
        """Check horizontal collisions"""
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_x > 0:
                    self.rect.right = platform.rect.left
                elif self.vel_x < 0:
                    self.rect.left = platform.rect.right

    def _check_collision_y(self, platforms):
        """Check vertical collisions"""
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0:
                    # Landing on ground
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                    self.is_jumping = False
                    self.jump_held = False
                    self.stomp_combo = 0  # Reset stomp combo when landing
                elif self.vel_y < 0:
                    # Hit ceiling
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0
                    self.jump_held = False  # Stop variable jump when hitting ceiling

    def take_damage(self, sound_manager):
        """Handle taking damage"""
        if self.invincible or self.star_power:
            return False

        if self.has_fire:
            self.has_fire = False
            self.invincible = True
            self.invincible_timer = 120
        elif self.is_big:
            self.is_big = False
            self.height = 32
            self.invincible = True
            self.invincible_timer = 120
        else:
            sound_manager.play('death')
            return True
        return False

    def power_up(self, type: str, sound_manager):
        """Apply power-up"""
        if type == 'mushroom':
            if not self.is_big:
                self.is_big = True
                self.height = 32 * NES_SCALE
                sound_manager.play('powerup')
            else:
                # Already big, give points
                self.score += 1000
        elif type == 'fireflower':
            if not self.is_big:
                # If small, just become big first
                self.is_big = True
                self.height = 32 * NES_SCALE
            else:
                # If already big, get fire power
                self.has_fire = True
            sound_manager.play('powerup')
        elif type == 'star':
            self.star_power = True
            self.star_timer = 600  # 10 seconds at 60fps
            sound_manager.play('powerup')
        elif type == '1up':
            self.lives += 1
            sound_manager.play('1up')


class Platform(pygame.sprite.Sprite):
    """Platform/ground tile"""
    def __init__(self, x: int, y: int, width: int, height: int, world: int = 1):
        super().__init__()
        self.world = world
        if width == TILE_SIZE and height == TILE_SIZE:
            self.image = SpriteGenerator.create_ground_tile(world)
        else:
            self.image = pygame.Surface((width, height))
            color = WORLD_COLORS.get(world, WORLD_COLORS[1])['ground']
            self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class BrickDebris(pygame.sprite.Sprite):
    """Debris particle when brick breaks - SMB1 style"""
    def __init__(self, x: int, y: int, vel_x: float, vel_y: float):
        super().__init__()
        # Small brick piece
        self.image = pygame.Surface((8 * NES_SCALE // 2, 8 * NES_SCALE // 2))
        self.image.fill(NES_PALETTE['brick_orange'])
        pygame.draw.rect(self.image, NES_PALETTE['brick_dark'], (0, 0, 8, 8), 1)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.gravity = 0.5
        self.lifetime = 60  # Frames before disappearing

    def update(self):
        self.vel_y += self.gravity
        self.rect.x += int(self.vel_x)
        self.rect.y += int(self.vel_y)
        self.lifetime -= 1
        if self.lifetime <= 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()


class Brick(pygame.sprite.Sprite):
    """Breakable brick block - SMB1 style"""
    def __init__(self, x: int, y: int):
        super().__init__()
        self.image = SpriteGenerator.create_brick_sprite()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.contains_coin = random.random() < 0.3
        self.broken = False
        self.bump_offset = 0
        self.bumping = False

    def bump(self):
        """Called when hit from below - creates bump animation"""
        if not self.bumping:
            self.bumping = True
            self.bump_offset = -8

    def break_brick(self):
        """Break the brick into debris pieces"""
        self.broken = True
        debris = []
        # Create 4 debris pieces flying in different directions (SMB1 style)
        debris.append(BrickDebris(self.rect.x, self.rect.y, -3, -10))
        debris.append(BrickDebris(self.rect.x + TILE_SIZE//2, self.rect.y, 3, -10))
        debris.append(BrickDebris(self.rect.x, self.rect.y + TILE_SIZE//2, -2, -6))
        debris.append(BrickDebris(self.rect.x + TILE_SIZE//2, self.rect.y + TILE_SIZE//2, 2, -6))
        return debris

    def update(self):
        """Update bump animation"""
        if self.bumping:
            if self.bump_offset < 0:
                self.bump_offset += 2
            else:
                self.bumping = False
                self.bump_offset = 0


class QuestionBlock(pygame.sprite.Sprite):
    """Question mark block with items"""
    def __init__(self, x: int, y: int, contains: str = 'coin'):
        super().__init__()
        self.animation_frame = 0
        self.hit = False
        self.contains = contains
        self.image = SpriteGenerator.create_question_block_sprite(self.hit, self.animation_frame)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        """Update animation"""
        if not self.hit:
            self.animation_frame += 1
            self.image = SpriteGenerator.create_question_block_sprite(self.hit, self.animation_frame)


class Coin(pygame.sprite.Sprite):
    """Collectible coin"""
    def __init__(self, x: int, y: int):
        super().__init__()
        self.animation_frame = 0
        self.image = SpriteGenerator.create_coin_sprite(self.animation_frame)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.base_y = y

    def update(self):
        """Animate coin"""
        self.animation_frame += 1
        self.image = SpriteGenerator.create_coin_sprite(self.animation_frame)
        # Bob up and down
        self.rect.y = self.base_y + int(math.sin(self.animation_frame * 0.1) * 3)


class Enemy(pygame.sprite.Sprite):
    """
    Nintendo EAD SMB1 Enemy System
    Authentic enemy behaviors from original Famicom game
    
    Enemy Types:
    - Goomba: Walks straight, dies when stomped
    - Green Koopa: Walks straight, becomes shell
    - Red Koopa: Turns at edges (doesn't fall off platforms)
    - Paratroopa: Bouncing Koopa (future)
    """
    def __init__(self, x: int, y: int, enemy_type: str = 'goomba', color: str = 'green'):
        super().__init__()
        self.enemy_type = enemy_type
        self.color = color  # For Koopas: 'green' walks off edges, 'red' turns at edges
        self.animation_frame = 0
        self.facing_right = False
        
        # === SMB1 ENEMY STATES ===
        self.state = 'walking'  # walking, shell, shell_moving, squished, dead, flipped
        self.shell_timer = 0    # Koopa emerges from shell after this
        self.squish_timer = 0   # Goomba squish display time
        self.flip_timer = 0     # Flipped enemy death animation
        
        # === NINTENDO EAD PHYSICS ===
        # Enemy speeds from SMB1 disassembly (scaled 3x)
        if enemy_type == 'goomba':
            self.walk_speed = 1.2       # Goombas are slow
        elif enemy_type == 'koopa':
            self.walk_speed = 1.5       # Koopas slightly faster
        else:
            self.walk_speed = 1.2
            
        self.shell_speed = 10.5         # Kicked shell speed (very fast!)
        self.vel_x = -self.walk_speed   # Start moving left
        self.vel_y = 0
        self.gravity = 0.55             # SMB1 enemy gravity
        self.max_fall = 12.0
        
        # For edge detection (Red Koopa)
        self.check_edge = (enemy_type == 'koopa' and color == 'red')
        
        # Activation (enemies only move when on screen)
        self.active = True
        self.activated = False  # Set true when first seen on screen
        
        # Create initial sprite
        if enemy_type == 'goomba':
            self.image = SpriteGenerator.create_goomba_sprite(0)
        elif enemy_type == 'koopa':
            self.image = SpriteGenerator.create_koopa_sprite(0, color)
        else:
            self.image = SpriteGenerator.create_goomba_sprite(0)
            
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.start_x = x  # Remember spawn position

    def stomp(self):
        """
        Called when Mario stomps this enemy from above
        Returns: 'kill', 'shell', 'kick', or None
        """
        if self.enemy_type == 'goomba':
            # Goomba: squish flat, then disappear
            self.state = 'squished'
            self.squish_timer = 40  # Show squished sprite briefly
            self.vel_x = 0
            self.vel_y = 0
            return 'kill'
            
        elif self.enemy_type == 'koopa':
            if self.state == 'walking':
                # Koopa retreats into shell
                self.state = 'shell'
                self.vel_x = 0
                self.shell_timer = 360  # 6 seconds before emerging (SMB1 accurate)
                # Adjust hitbox for shell
                old_bottom = self.rect.bottom
                old_centerx = self.rect.centerx
                self.image = SpriteGenerator.create_koopa_shell_sprite(self.color)
                self.rect = self.image.get_rect()
                self.rect.bottom = old_bottom
                self.rect.centerx = old_centerx
                return 'shell'
                
            elif self.state == 'shell':
                # Kick stationary shell
                return 'kick'
                
            elif self.state == 'shell_moving':
                # Stop moving shell
                self.state = 'shell'
                self.vel_x = 0
                self.shell_timer = 360
                return 'shell'
                
        return None

    def kick(self, kick_right: bool):
        """Kick shell in a direction"""
        if self.state == 'shell':
            self.state = 'shell_moving'
            self.vel_x = self.shell_speed if kick_right else -self.shell_speed
            self.shell_timer = 0

    def flip(self):
        """
        Enemy hit from below (Mario hit block from underneath)
        SMB1: Enemies on top of blocks get flipped and die
        """
        self.state = 'flipped'
        self.vel_y = -8.0  # Pop up
        self.vel_x = 2.0 if random.random() > 0.5 else -2.0
        self.flip_timer = 120

    def update(self, platforms):
        """Nintendo EAD SMB1 enemy update"""
        if not self.active:
            return
            
        self.animation_frame += 1
        
        # === SQUISHED STATE (Goomba) ===
        if self.state == 'squished':
            self.squish_timer -= 1
            self.image = SpriteGenerator.create_goomba_sprite(0, squished=True)
            if self.squish_timer <= 0:
                self.kill()
            return
            
        # === FLIPPED STATE (hit from below) ===
        if self.state == 'flipped':
            self.vel_y += self.gravity
            self.rect.x += int(self.vel_x)
            self.rect.y += int(self.vel_y)
            # Flip sprite upside down
            if self.enemy_type == 'goomba':
                self.image = pygame.transform.flip(
                    SpriteGenerator.create_goomba_sprite(self.animation_frame // 8),
                    False, True
                )
            else:
                self.image = pygame.transform.flip(
                    SpriteGenerator.create_koopa_sprite(0, self.color),
                    False, True
                )
            if self.rect.top > SCREEN_HEIGHT + 50:
                self.kill()
            return
            
        # === SHELL TIMER (Koopa emerging) ===
        if self.state == 'shell' and self.enemy_type == 'koopa':
            self.shell_timer -= 1
            # Wiggle when about to emerge
            if self.shell_timer < 90:
                wiggle = 2 if (self.shell_timer // 6) % 2 == 0 else -2
                self.rect.x += wiggle
            if self.shell_timer <= 0:
                # Emerge from shell
                self.state = 'walking'
                self.vel_x = -self.walk_speed
                old_bottom = self.rect.bottom
                self.image = SpriteGenerator.create_koopa_sprite(0, self.color)
                self.rect = self.image.get_rect()
                self.rect.bottom = old_bottom
        
        # === UPDATE SPRITE ===
        if self.enemy_type == 'goomba':
            self.image = SpriteGenerator.create_goomba_sprite(self.animation_frame // 8)
        elif self.enemy_type == 'koopa':
            if self.state in ['shell', 'shell_moving']:
                self.image = SpriteGenerator.create_koopa_shell_sprite(self.color)
            else:
                self.image = SpriteGenerator.create_koopa_sprite(self.animation_frame // 8, self.color)
                if self.vel_x > 0:
                    self.image = pygame.transform.flip(self.image, True, False)
        
        # === PHYSICS ===
        # Gravity
        self.vel_y += self.gravity
        if self.vel_y > self.max_fall:
            self.vel_y = self.max_fall
        
        # Horizontal movement
        self.rect.x += int(self.vel_x)
        
        # Check horizontal collisions with platforms
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_x > 0:
                    self.rect.right = platform.rect.left
                    self.vel_x = -abs(self.vel_x)  # Bounce back
                elif self.vel_x < 0:
                    self.rect.left = platform.rect.right
                    self.vel_x = abs(self.vel_x)
        
        # Vertical movement
        self.rect.y += int(self.vel_y)
        
        # Check vertical collisions
        on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    on_ground = True
        
        # === RED KOOPA EDGE DETECTION ===
        if self.check_edge and on_ground and self.state == 'walking':
            # Check if there's ground ahead
            check_x = self.rect.centerx + (16 if self.vel_x > 0 else -16)
            check_y = self.rect.bottom + 4
            has_ground = False
            for platform in platforms:
                if platform.rect.collidepoint(check_x, check_y):
                    has_ground = True
                    break
            if not has_ground:
                # Turn around at edge
                self.vel_x = -self.vel_x
        
        # Remove if fallen off screen
        if self.rect.top > SCREEN_HEIGHT + 100:
            self.kill()


class Pipe(pygame.sprite.Sprite):
    """Green pipe obstacle"""
    def __init__(self, x: int, y: int, height: int = 2):
        super().__init__()
        self.pipe_height = height
        self.image = SpriteGenerator.create_pipe_sprite(height)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.bottom = y


class Flag(pygame.sprite.Sprite):
    """SMB1-style end-of-level flagpole with sliding flag"""
    def __init__(self, x: int, y: int):
        super().__init__()
        self.pole_x = x
        self.ground_y = y

        # Separate pole and flag sprites
        self.pole_sprite = SpriteGenerator.create_flagpole_sprite()
        self.flag_sprite = SpriteGenerator.create_flag_sprite()

        # Pole position (fixed)
        self.pole_rect = self.pole_sprite.get_rect()
        self.pole_rect.x = x
        self.pole_rect.bottom = y

        # Flag position (animated)
        self.flag_rect = self.flag_sprite.get_rect()
        self.flag_rect.x = x + 9 * NES_SCALE  # Offset to right of pole
        self.flag_rect.y = y - 10 * TILE_SIZE + 10 * NES_SCALE  # Start at top of pole

        # For compatibility with sprite group drawing, create combined surface
        self.image = pygame.Surface((32 * NES_SCALE, 160 * NES_SCALE), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.bottom = y

        # Flag animation state
        self.triggered = False
        self.flag_start_y = self.flag_rect.y
        self.flag_target_y = y - TILE_SIZE - 8 * NES_SCALE  # Bottom of pole

        self._update_combined_image()

    def _update_combined_image(self):
        """Redraw combined image with pole and flag at current positions"""
        self.image.fill((0, 0, 0, 0))  # Clear
        # Draw pole (always at same position relative to self.rect)
        self.image.blit(self.pole_sprite, (0, 0))
        # Draw flag at its current animated position
        flag_offset_y = self.flag_rect.y - self.rect.y
        self.image.blit(self.flag_sprite, (9 * NES_SCALE, flag_offset_y + 10 * NES_SCALE))

    def trigger(self):
        """Start the flag descent animation"""
        self.triggered = True

    def update(self):
        """Update flag position (descends when triggered)"""
        if self.triggered and self.flag_rect.y < self.flag_target_y:
            self.flag_rect.y += 4  # Descend speed
            if self.flag_rect.y > self.flag_target_y:
                self.flag_rect.y = int(self.flag_target_y)
            self._update_combined_image()


class Fireball(pygame.sprite.Sprite):
    """Fire Mario's fireball projectile - SMB1 style"""
    def __init__(self, x: int, y: int, direction: int):
        super().__init__()
        self.image = pygame.Surface((8 * NES_SCALE, 8 * NES_SCALE), pygame.SRCALPHA)
        # Draw simple fireball (orange/red)
        pygame.draw.circle(self.image, NES_PALETTE['fire_orange'],
                          (4 * NES_SCALE, 4 * NES_SCALE), 4 * NES_SCALE)
        pygame.draw.circle(self.image, NES_PALETTE['fire_red'],
                          (4 * NES_SCALE, 4 * NES_SCALE), 2 * NES_SCALE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vel_x = 8 * direction  # SMB1 fireball speed
        self.vel_y = 0
        self.gravity = 0.5
        self.bounce_vel = -6  # Bounce velocity
        self.lifetime = 180  # 3 seconds at 60fps

    def update(self, platforms):
        """Update fireball position - bounces off ground"""
        self.vel_y += self.gravity
        self.rect.x += int(self.vel_x)
        self.rect.y += int(self.vel_y)
        self.lifetime -= 1

        # Check ground collision for bounce
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.vel_y = self.bounce_vel  # Bounce!
                    break

        # Remove if out of bounds or expired
        if self.rect.right < -50 or self.rect.left > SCREEN_WIDTH * 5 or self.lifetime <= 0:
            self.kill()


class PowerUp(pygame.sprite.Sprite):
    """Power-up item - Mushroom, Fire Flower, Star, 1-Up"""
    def __init__(self, x: int, y: int, type: str = 'mushroom'):
        super().__init__()
        self.type = type
        self.animation_frame = 0
        self.emerging = True
        self.emerge_y = 0
        self.start_y = y

        if type == 'mushroom':
            self.image = SpriteGenerator.create_mushroom_sprite('super')
            self.vel_x = 2
        elif type == '1up':
            self.image = SpriteGenerator.create_mushroom_sprite('1up')
            self.vel_x = 2
        elif type == 'star':
            self.image = SpriteGenerator.create_star_sprite(self.animation_frame)
            self.vel_x = 3
        elif type == 'fireflower':
            self.image = SpriteGenerator.create_fire_flower_sprite(self.animation_frame)
            self.vel_x = 0  # Fire flowers don't move horizontally
        else:
            self.image = SpriteGenerator.create_mushroom_sprite('super')
            self.vel_x = 2

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vel_y = 0
        self.gravity = 0.5

    def update(self, platforms):
        """Update power-up position"""
        self.animation_frame += 1

        # Update animated sprites
        if self.type == 'star':
            self.image = SpriteGenerator.create_star_sprite(self.animation_frame)
        elif self.type == 'fireflower':
            self.image = SpriteGenerator.create_fire_flower_sprite(self.animation_frame)

        # Emerging animation (pop out of block)
        if self.emerging:
            self.emerge_y += 2
            self.rect.y = self.start_y - self.emerge_y
            if self.emerge_y >= TILE_SIZE:
                self.emerging = False
            return

        # Fire flowers stay in place
        if self.type == 'fireflower':
            return

        # Apply gravity
        self.vel_y += self.gravity

        # Move
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

        # Check collisions
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    if self.type == 'star':
                        self.vel_y = -12  # Stars bounce high
                # Reverse direction on wall collision
                if self.vel_x > 0:
                    if self.rect.right > platform.rect.left and self.rect.left < platform.rect.left:
                        self.rect.right = platform.rect.left
                        self.vel_x *= -1
                elif self.vel_x < 0:
                    if self.rect.left < platform.rect.right and self.rect.right > platform.rect.right:
                        self.rect.left = platform.rect.right
                        self.vel_x *= -1


class BlockCoin(pygame.sprite.Sprite):
    """Coin that pops out of a block"""
    def __init__(self, x: int, y: int):
        super().__init__()
        self.animation_frame = 0
        self.image = SpriteGenerator.create_coin_block_sprite(self.animation_frame)
        self.rect = self.image.get_rect()
        self.rect.centerx = x + TILE_SIZE // 2
        self.rect.bottom = y
        self.vel_y = -12
        self.start_y = y
        self.lifetime = 30

    def update(self):
        """Animate the coin popping out"""
        self.animation_frame += 1
        self.lifetime -= 1

        # Update sprite
        self.image = SpriteGenerator.create_coin_block_sprite(self.animation_frame)

        # Move up then fall
        self.vel_y += 0.8
        self.rect.y += self.vel_y

        # Remove when animation complete
        if self.lifetime <= 0 or self.rect.top > self.start_y:
            self.kill()


class Game:
    """Main game class"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Ultra. Mario 2D Bros")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 72)

        self.sound_manager = SoundManager()
        self.state = GameState.MAIN_MENU
        self.selected_option = 0
        self.selected_level = 0

        # Generate all levels
        self.levels = self._generate_levels()
        self.current_level = None
        self.current_world = 1

        # Sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.question_blocks = pygame.sprite.Group()
        self.power_ups = pygame.sprite.Group()
        self.block_coins = pygame.sprite.Group()
        self.debris = pygame.sprite.Group()
        self.bricks = pygame.sprite.Group()
        self.fireballs = pygame.sprite.Group()

        # Player
        self.player = None
        self.camera_x = 0
        self.animation_frame = 0
        self.level_width = SCREEN_WIDTH * 4  # Default, updated per level

        # Flagpole reference
        self.flag = None
        self.flagpole_touched = False
        self.level_complete_timer = 0

        # Level timer (SMB1 style - 400 time units, decrements every frame at ~0.4 per frame for ~16.7 seconds per 100 units)
        self.level_timer = 400
        self.timer_frame_counter = 0
        
        # Course clear variables (SMB3 style)
        self.course_clear_timer = 0
        self.time_bonus = 0
        self.time_counting = False

        # Menu options
        self.main_menu_options = ["Start Game", "Level Select", "Debug Select", "Quit"]
        
        # Debug mode - all levels unlocked
        self.debug_mode = False

    def _generate_levels(self) -> List[Level]:
        """Generate all levels from 1-1 to 8-4"""
        levels = []
        for world in range(1, 9):
            for stage in range(1, 5):
                level = Level(
                    world=world,
                    stage=stage,
                    name=f"World {world}-{stage}: {WORLD_COLORS[world]['name']}",
                    unlocked=(world == 1 and stage == 1)
                )
                levels.append(level)
        return levels

    def _build_level(self, level: Level):
        """Build SMB1-style level based on world and stage"""
        self.current_world = level.world

        # Clear existing sprites and cache
        self.all_sprites.empty()
        self.platforms.empty()
        self.enemies.empty()
        self.coins.empty()
        self.question_blocks.empty()
        self.power_ups.empty()
        self.block_coins.empty()
        self.bricks.empty()
        self.debris.empty()
        self.fireballs.empty()

        # Start level-specific music (OST varies by world and stage)
        self.sound_manager.play_world_music(level.world, level.stage)

        # Level dimensions (SMB1 style - about 200+ tiles wide)
        LEVEL_WIDTH = 210 * TILE_SIZE  # ~200 tiles like SMB1
        GROUND_Y = SCREEN_HEIGHT - TILE_SIZE - 40  # Leave room for HUD

        # Create player
        self.player = Player(3 * TILE_SIZE, GROUND_Y - TILE_SIZE)
        self.all_sprites.add(self.player)

        # ===== BUILD GROUND =====
        # Ground with gaps (SMB1 1-1 style)
        gap_positions = self._get_level_gaps(level)
        for tile_x in range(int(LEVEL_WIDTH // TILE_SIZE)):
            x = tile_x * TILE_SIZE
            # Check if this is a gap
            is_gap = False
            for gap_start, gap_end in gap_positions:
                if gap_start <= tile_x < gap_end:
                    is_gap = True
                    break

            if not is_gap:
                # Ground tile
                ground = Platform(x, GROUND_Y, TILE_SIZE, TILE_SIZE, level.world)
                self.platforms.add(ground)
                self.all_sprites.add(ground)
                # Sub-ground
                ground2 = Platform(x, GROUND_Y + TILE_SIZE, TILE_SIZE, TILE_SIZE, level.world)
                self.platforms.add(ground2)

        # ===== BUILD BLOCKS AND STRUCTURES =====
        block_row_y = GROUND_Y - 4 * TILE_SIZE  # 4 tiles above ground
        high_row_y = GROUND_Y - 8 * TILE_SIZE   # 8 tiles above ground

        # Add question blocks and brick structures based on level
        structures = self._get_level_structures(level)
        for struct in structures:
            if struct['type'] == 'qblock':
                qblock = QuestionBlock(struct['x'] * TILE_SIZE, struct['y'], struct['contains'])
                self.question_blocks.add(qblock)
                self.platforms.add(qblock)
                self.all_sprites.add(qblock)
            elif struct['type'] == 'brick':
                brick = Brick(struct['x'] * TILE_SIZE, struct['y'])
                self.platforms.add(brick)
                self.bricks.add(brick)
                self.all_sprites.add(brick)
            elif struct['type'] == 'brick_row':
                for i in range(struct['width']):
                    brick = Brick((struct['x'] + i) * TILE_SIZE, struct['y'])
                    self.platforms.add(brick)
                    self.bricks.add(brick)
                    self.all_sprites.add(brick)

        # ===== ADD PIPES =====
        pipes = self._get_level_pipes(level)
        for pipe_data in pipes:
            pipe = Pipe(pipe_data['x'] * TILE_SIZE, GROUND_Y, pipe_data['height'])
            self.platforms.add(pipe)
            self.all_sprites.add(pipe)

        # ===== ADD ENEMIES =====
        enemies = self._get_level_enemies(level)
        for enemy_data in enemies:
            enemy = Enemy(enemy_data['x'] * TILE_SIZE, GROUND_Y - TILE_SIZE, enemy_data['type'])
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)

        # ===== ADD COINS =====
        coin_positions = self._get_level_coins(level)
        for coin_data in coin_positions:
            coin = Coin(coin_data['x'] * TILE_SIZE, coin_data['y'])
            self.coins.add(coin)
            self.all_sprites.add(coin)

        # ===== ADD FLAGPOLE =====
        self.flag = Flag(200 * TILE_SIZE, GROUND_Y)
        self.all_sprites.add(self.flag)
        self.flagpole_touched = False
        self.level_complete_timer = 0

        self.camera_x = 0
        self.level_width = LEVEL_WIDTH
        # Reset timer for new level (SMB1 style: 400 time units)
        self.level_timer = 400
        self.timer_frame_counter = 0

    def _get_level_gaps(self, level: Level) -> List[Tuple[int, int]]:
        """Get gap positions for level (start_tile, end_tile) - SMB1 accurate"""
        # Level-specific gap patterns
        level_gaps = {
            # World 1
            (1, 1): [],
            (1, 2): [(69, 71), (118, 120)],
            (1, 3): [],  # Athletic level - platforms
            (1, 4): [],  # Castle
            # World 2
            (2, 1): [(55, 57), (85, 88)],
            (2, 2): [(40, 42), (90, 93), (140, 143)],
            (2, 3): [],
            (2, 4): [],
            # World 3
            (3, 1): [(60, 63), (100, 102)],
            (3, 2): [(50, 52), (80, 83), (120, 123)],
            (3, 3): [],
            (3, 4): [],
            # World 4
            (4, 1): [(45, 48), (75, 78), (110, 113)],
            (4, 2): [(55, 58), (95, 99), (135, 138)],
            (4, 3): [],
            (4, 4): [],
            # World 5
            (5, 1): [(40, 43), (70, 74), (100, 103), (140, 143)],
            (5, 2): [(50, 54), (90, 94), (130, 134)],
            (5, 3): [],
            (5, 4): [],
            # World 6
            (6, 1): [(45, 49), (80, 84), (115, 119)],
            (6, 2): [(55, 59), (95, 100), (145, 149)],
            (6, 3): [],
            (6, 4): [],
            # World 7
            (7, 1): [(50, 55), (90, 95), (130, 135)],
            (7, 2): [(45, 50), (85, 91), (125, 131)],
            (7, 3): [],
            (7, 4): [],
            # World 8
            (8, 1): [(40, 45), (70, 76), (100, 106), (140, 146)],
            (8, 2): [(50, 56), (90, 97), (130, 137)],
            (8, 3): [(45, 52), (85, 93), (125, 133)],
            (8, 4): [(60, 68), (110, 118)],
        }
        return level_gaps.get((level.world, level.stage), [])

    def _get_level_structures(self, level: Level) -> List[dict]:
        """Get block structures for each level - SMB1 style"""
        structures = []
        ground_y = SCREEN_HEIGHT - TILE_SIZE - 40
        block_y = ground_y - 4 * TILE_SIZE  # Standard block height
        high_y = ground_y - 8 * TILE_SIZE   # High blocks

        w, s = level.world, level.stage

        # ===== WORLD 1 =====
        if w == 1:
            if s == 1:  # Classic 1-1 (SMB1 accurate layout)
                # First ? block with coin
                structures.append({'type': 'qblock', 'x': 16, 'y': block_y, 'contains': 'coin'})
                # Main block formation with mushroom
                structures.append({'type': 'brick', 'x': 20, 'y': block_y})
                structures.append({'type': 'qblock', 'x': 21, 'y': block_y, 'contains': 'mushroom'})
                structures.append({'type': 'brick', 'x': 22, 'y': block_y})
                structures.append({'type': 'qblock', 'x': 23, 'y': block_y, 'contains': 'coin'})
                structures.append({'type': 'brick', 'x': 24, 'y': block_y})
                # High ? block above
                structures.append({'type': 'qblock', 'x': 22, 'y': high_y, 'contains': 'coin'})
                # Block formation after first pipe area
                structures.append({'type': 'qblock', 'x': 78, 'y': block_y, 'contains': 'mushroom'})
                # Brick row with hidden 1-up position
                structures.append({'type': 'brick_row', 'x': 80, 'y': block_y, 'width': 8})
                # High platform section
                structures.append({'type': 'brick_row', 'x': 91, 'y': high_y, 'width': 3})
                structures.append({'type': 'qblock', 'x': 94, 'y': high_y, 'contains': 'coin'})
                # Mid section blocks
                structures.append({'type': 'brick', 'x': 100, 'y': block_y})
                structures.append({'type': 'qblock', 'x': 101, 'y': block_y, 'contains': 'coin'})
                structures.append({'type': 'brick', 'x': 102, 'y': block_y})
                # Star block area (hidden)
                structures.append({'type': 'qblock', 'x': 106, 'y': block_y, 'contains': 'star'})
                # Triple ? blocks
                structures.append({'type': 'qblock', 'x': 109, 'y': block_y, 'contains': 'coin'})
                structures.append({'type': 'qblock', 'x': 110, 'y': block_y, 'contains': 'coin'})
                structures.append({'type': 'qblock', 'x': 111, 'y': block_y, 'contains': 'coin'})
                structures.append({'type': 'qblock', 'x': 110, 'y': high_y, 'contains': 'coin'})
                # Brick formation before pit
                structures.append({'type': 'brick_row', 'x': 118, 'y': block_y, 'width': 3})
                # Long high platform
                structures.append({'type': 'brick_row', 'x': 121, 'y': high_y, 'width': 8})
                # Connected blocks
                structures.append({'type': 'brick_row', 'x': 129, 'y': high_y, 'width': 4})
                structures.append({'type': 'brick', 'x': 129, 'y': block_y})
                structures.append({'type': 'qblock', 'x': 130, 'y': block_y, 'contains': 'coin'})
                structures.append({'type': 'qblock', 'x': 131, 'y': block_y, 'contains': 'coin'})
                structures.append({'type': 'brick', 'x': 132, 'y': block_y})
                # Final section before flag
                structures.append({'type': 'brick_row', 'x': 168, 'y': block_y, 'width': 2})
                structures.append({'type': 'qblock', 'x': 170, 'y': block_y, 'contains': 'coin'})
                structures.append({'type': 'brick', 'x': 171, 'y': block_y})
            elif s == 2:  # Underground
                structures.extend([
                    {'type': 'brick_row', 'x': 10, 'y': block_y, 'width': 6},
                    {'type': 'qblock', 'x': 12, 'y': block_y, 'contains': 'mushroom'},
                    {'type': 'brick_row', 'x': 25, 'y': high_y, 'width': 10},
                    {'type': 'brick_row', 'x': 50, 'y': block_y, 'width': 5},
                    {'type': 'qblock', 'x': 52, 'y': block_y, 'contains': 'coin'},
                    {'type': 'brick_row', 'x': 75, 'y': block_y, 'width': 8},
                    {'type': 'qblock', 'x': 78, 'y': block_y, 'contains': 'fireflower'},
                    {'type': 'brick_row', 'x': 100, 'y': high_y, 'width': 6},
                ])
            elif s == 3:  # Athletic
                structures.extend([
                    {'type': 'brick_row', 'x': 15, 'y': block_y, 'width': 4},
                    {'type': 'brick_row', 'x': 25, 'y': high_y, 'width': 6},
                    {'type': 'qblock', 'x': 27, 'y': high_y, 'contains': 'mushroom'},
                    {'type': 'brick_row', 'x': 40, 'y': block_y, 'width': 5},
                    {'type': 'brick_row', 'x': 55, 'y': high_y, 'width': 8},
                    {'type': 'qblock', 'x': 58, 'y': high_y, 'contains': 'star'},
                    {'type': 'brick_row', 'x': 75, 'y': block_y, 'width': 4},
                ])
            elif s == 4:  # Castle
                structures.extend([
                    {'type': 'brick_row', 'x': 20, 'y': block_y, 'width': 3},
                    {'type': 'brick_row', 'x': 45, 'y': high_y, 'width': 5},
                    {'type': 'qblock', 'x': 47, 'y': high_y, 'contains': 'mushroom'},
                    {'type': 'brick_row', 'x': 70, 'y': block_y, 'width': 4},
                ])

        # ===== WORLDS 2-8 follow similar patterns =====
        elif w == 2:
            structures.extend([
                {'type': 'qblock', 'x': 18, 'y': block_y, 'contains': 'mushroom'},
                {'type': 'brick_row', 'x': 25, 'y': block_y, 'width': 5},
                {'type': 'qblock', 'x': 27, 'y': block_y, 'contains': 'coin'},
                {'type': 'brick_row', 'x': 45, 'y': high_y, 'width': 6},
                {'type': 'qblock', 'x': 47, 'y': high_y, 'contains': 'fireflower'},
                {'type': 'brick_row', 'x': 65, 'y': block_y, 'width': 7},
                {'type': 'qblock', 'x': 68, 'y': block_y, 'contains': 'coin'},
                {'type': 'brick_row', 'x': 95, 'y': block_y, 'width': 4},
                {'type': 'qblock', 'x': 110, 'y': high_y, 'contains': 'star'},
                {'type': 'brick_row', 'x': 130, 'y': block_y, 'width': 6},
            ])
        elif w == 3:
            structures.extend([
                {'type': 'brick_row', 'x': 15, 'y': block_y, 'width': 6},
                {'type': 'qblock', 'x': 17, 'y': block_y, 'contains': 'mushroom'},
                {'type': 'brick_row', 'x': 35, 'y': high_y, 'width': 8},
                {'type': 'qblock', 'x': 38, 'y': high_y, 'contains': 'coin'},
                {'type': 'brick_row', 'x': 60, 'y': block_y, 'width': 5},
                {'type': 'qblock', 'x': 62, 'y': block_y, 'contains': 'fireflower'},
                {'type': 'brick_row', 'x': 90, 'y': block_y, 'width': 6},
                {'type': 'qblock', 'x': 120, 'y': high_y, 'contains': 'star'},
            ])
        elif w == 4:
            structures.extend([
                {'type': 'qblock', 'x': 20, 'y': block_y, 'contains': 'mushroom'},
                {'type': 'brick_row', 'x': 28, 'y': block_y, 'width': 7},
                {'type': 'qblock', 'x': 31, 'y': block_y, 'contains': 'coin'},
                {'type': 'brick_row', 'x': 50, 'y': high_y, 'width': 6},
                {'type': 'qblock', 'x': 52, 'y': high_y, 'contains': 'fireflower'},
                {'type': 'brick_row', 'x': 75, 'y': block_y, 'width': 8},
                {'type': 'qblock', 'x': 100, 'y': block_y, 'contains': 'star'},
                {'type': 'qblock', 'x': 130, 'y': high_y, 'contains': '1up'},
            ])
        elif w == 5:
            structures.extend([
                {'type': 'brick_row', 'x': 18, 'y': block_y, 'width': 5},
                {'type': 'qblock', 'x': 20, 'y': block_y, 'contains': 'mushroom'},
                {'type': 'brick_row', 'x': 40, 'y': high_y, 'width': 7},
                {'type': 'qblock', 'x': 43, 'y': high_y, 'contains': 'fireflower'},
                {'type': 'brick_row', 'x': 65, 'y': block_y, 'width': 6},
                {'type': 'qblock', 'x': 90, 'y': block_y, 'contains': 'star'},
                {'type': 'brick_row', 'x': 115, 'y': high_y, 'width': 5},
            ])
        elif w == 6:
            structures.extend([
                {'type': 'qblock', 'x': 22, 'y': block_y, 'contains': 'mushroom'},
                {'type': 'brick_row', 'x': 30, 'y': block_y, 'width': 8},
                {'type': 'qblock', 'x': 33, 'y': block_y, 'contains': 'coin'},
                {'type': 'brick_row', 'x': 55, 'y': high_y, 'width': 6},
                {'type': 'qblock', 'x': 57, 'y': high_y, 'contains': 'fireflower'},
                {'type': 'brick_row', 'x': 80, 'y': block_y, 'width': 7},
                {'type': 'qblock', 'x': 105, 'y': block_y, 'contains': 'star'},
            ])
        elif w == 7:
            structures.extend([
                {'type': 'brick_row', 'x': 20, 'y': block_y, 'width': 6},
                {'type': 'qblock', 'x': 22, 'y': block_y, 'contains': 'mushroom'},
                {'type': 'brick_row', 'x': 45, 'y': high_y, 'width': 8},
                {'type': 'qblock', 'x': 48, 'y': high_y, 'contains': 'fireflower'},
                {'type': 'brick_row', 'x': 70, 'y': block_y, 'width': 5},
                {'type': 'qblock', 'x': 95, 'y': block_y, 'contains': 'star'},
                {'type': 'qblock', 'x': 125, 'y': high_y, 'contains': '1up'},
            ])
        elif w == 8:
            structures.extend([
                {'type': 'qblock', 'x': 25, 'y': block_y, 'contains': 'mushroom'},
                {'type': 'brick_row', 'x': 35, 'y': block_y, 'width': 9},
                {'type': 'qblock', 'x': 38, 'y': block_y, 'contains': 'fireflower'},
                {'type': 'brick_row', 'x': 60, 'y': high_y, 'width': 7},
                {'type': 'qblock', 'x': 63, 'y': high_y, 'contains': 'star'},
                {'type': 'brick_row', 'x': 85, 'y': block_y, 'width': 8},
                {'type': 'qblock', 'x': 110, 'y': block_y, 'contains': 'mushroom'},
            ])

        # Add end staircase for all levels
        for step in range(8):
            for height in range(step + 1):
                structures.append({
                    'type': 'brick',
                    'x': 185 + step,
                    'y': ground_y - (height + 1) * TILE_SIZE
                })

        return structures

    def _get_level_pipes(self, level: Level) -> List[dict]:
        """Get pipe positions for each level - SMB1 accurate placement"""
        w, s = level.world, level.stage

        # SMB1 1-1 accurate pipe placement
        if w == 1 and s == 1:
            return [
                {'x': 28, 'height': 2},   # First small pipe
                {'x': 38, 'height': 3},   # Second medium pipe
                {'x': 46, 'height': 4},   # Third tall pipe (warp pipe in SMB1)
                {'x': 57, 'height': 4},   # Fourth tall pipe
                {'x': 163, 'height': 2},  # Pipe near end
                {'x': 179, 'height': 2},  # Final pipe before flag
            ]

        # Default pipes for other levels
        base_pipes = [
            {'x': 28, 'height': 2},
            {'x': 38, 'height': 3},
            {'x': 46, 'height': 4},
            {'x': 57, 'height': 4},
        ]

        # Add more pipes based on world
        if w >= 2:
            base_pipes.append({'x': 95, 'height': 2})
        if w >= 3:
            base_pipes.append({'x': 110, 'height': 3})
        if w >= 4:
            base_pipes.append({'x': 125, 'height': 4})
        if w >= 5:
            base_pipes.append({'x': 145, 'height': 3})
        if w >= 6:
            base_pipes.append({'x': 160, 'height': 2})

        # Castle and underground levels have fewer pipes
        if s == 2 or s == 4:
            return base_pipes[:2]

        return base_pipes

    def _get_level_enemies(self, level: Level) -> List[dict]:
        """Get enemy positions for each level - SMB1 accurate placement"""
        w, s = level.world, level.stage
        enemies = []

        # SMB1 1-1 accurate enemy placement
        if w == 1 and s == 1:
            enemies = [
                {'x': 22, 'type': 'goomba'},   # First Goomba
                {'x': 40, 'type': 'goomba'},   # Second Goomba
                {'x': 51, 'type': 'goomba'},   # Near first pipe
                {'x': 52, 'type': 'goomba'},   # Pair of Goombas
                {'x': 80, 'type': 'goomba'},   # After tall pipe
                {'x': 82, 'type': 'goomba'},   # Goomba pair
                {'x': 97, 'type': 'koopa'},    # First Koopa
                {'x': 114, 'type': 'goomba'},  # Before pit
                {'x': 115, 'type': 'goomba'},  # Goomba pair
                {'x': 124, 'type': 'goomba'},  # On high platform
                {'x': 125, 'type': 'goomba'},  # Goomba pair
                {'x': 128, 'type': 'goomba'},  # More Goombas
                {'x': 129, 'type': 'goomba'},  # Goomba pair
                {'x': 174, 'type': 'goomba'},  # Near end
                {'x': 175, 'type': 'goomba'},  # Final pair
            ]
        else:
            # Other levels use procedural placement
            base_count = 4 + w + s
            positions = []
            for i in range(base_count):
                x = 22 + i * (160 // base_count) + random.randint(-3, 3)
                positions.append(x)

            for i, pos in enumerate(positions):
                # Mix of goombas and koopas - more koopas in later worlds
                if w >= 5:
                    enemy_type = 'koopa' if i % 3 == 0 else 'goomba'
                elif w >= 3:
                    enemy_type = 'koopa' if i % 4 == 0 else 'goomba'
                else:
                    enemy_type = 'koopa' if i % 5 == 0 else 'goomba'
                enemies.append({'x': pos, 'type': enemy_type})

        return enemies

    def _get_level_coins(self, level: Level) -> List[dict]:
        """Get floating coin positions for each level"""
        coins = []
        ground_y = SCREEN_HEIGHT - TILE_SIZE - 40
        coin_y = ground_y - 3 * TILE_SIZE

        # Coin patterns vary by level
        w, s = level.world, level.stage

        # Coins in arcs and rows
        if s == 1:  # Overworld - more coins
            for x in [35, 36, 37, 65, 66, 67, 105, 106, 107, 145, 146, 147]:
                coins.append({'x': x, 'y': coin_y})
        elif s == 2:  # Underground
            for x in [30, 31, 55, 56, 80, 81, 110, 111]:
                coins.append({'x': x, 'y': coin_y})
        elif s == 3:  # Athletic
            for x in [25, 50, 75, 100, 125, 150]:
                coins.append({'x': x, 'y': coin_y - TILE_SIZE})
        else:  # Castle
            for x in [40, 70, 100, 130]:
                coins.append({'x': x, 'y': coin_y})

        return coins

    def run(self):
        """Main game loop"""
        running = True
        while running:
            self.clock.tick(FPS)
            self.animation_frame += 1

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                self._handle_event(event)

            self._update()
            self._draw()

            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def _handle_event(self, event):
        """Handle input events based on game state"""
        if event.type == pygame.KEYDOWN:
            if self.state == GameState.MAIN_MENU:
                self._handle_menu_input(event.key)
            elif self.state == GameState.LEVEL_SELECT:
                self._handle_level_select_input(event.key)
            elif self.state == GameState.DEBUG_SELECT:
                self._handle_debug_select_input(event.key)
            elif self.state == GameState.PLAYING:
                self._handle_game_input_down(event.key)
            elif self.state == GameState.PAUSED:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                    self.state = GameState.PLAYING
            elif self.state == GameState.GAME_OVER:
                if event.key == pygame.K_RETURN:
                    self.state = GameState.MAIN_MENU
                    self.sound_manager.stop_music()
            elif self.state == GameState.LEVEL_COMPLETE:
                if event.key == pygame.K_RETURN:
                    self._advance_to_next_level()
            elif self.state == GameState.COURSE_CLEAR:
                if event.key == pygame.K_RETURN and not self.time_counting:
                    self._advance_to_next_level()

        elif event.type == pygame.KEYUP:
            if self.state == GameState.PLAYING:
                self._handle_game_input_up(event.key)

    def _handle_menu_input(self, key):
        """Handle main menu input"""
        if key == pygame.K_UP or key == pygame.K_w:
            self.selected_option = (self.selected_option - 1) % len(self.main_menu_options)
        elif key == pygame.K_DOWN or key == pygame.K_s:
            self.selected_option = (self.selected_option + 1) % len(self.main_menu_options)
        elif key == pygame.K_RETURN:
            if self.selected_option == 0:  # Start Game
                self.selected_level = 0
                self._build_level(self.levels[0])
                self.state = GameState.PLAYING
            elif self.selected_option == 1:  # Level Select
                self.state = GameState.LEVEL_SELECT
            elif self.selected_option == 2:  # Debug Select (all levels unlocked)
                self.debug_mode = True
                self.selected_level = 0
                self.state = GameState.DEBUG_SELECT
            elif self.selected_option == 3:  # Quit
                pygame.quit()
                sys.exit()

    def _handle_debug_select_input(self, key):
        """Handle debug level select input - all levels available"""
        if key == pygame.K_UP or key == pygame.K_w:
            self.selected_level = max(0, self.selected_level - 4)
        elif key == pygame.K_DOWN or key == pygame.K_s:
            self.selected_level = min(len(self.levels) - 1, self.selected_level + 4)
        elif key == pygame.K_LEFT or key == pygame.K_a:
            self.selected_level = max(0, self.selected_level - 1)
        elif key == pygame.K_RIGHT or key == pygame.K_d:
            self.selected_level = min(len(self.levels) - 1, self.selected_level + 1)
        elif key == pygame.K_RETURN:
            # Debug mode - all levels playable
            self._build_level(self.levels[self.selected_level])
            self.state = GameState.PLAYING
        elif key == pygame.K_ESCAPE:
            self.state = GameState.MAIN_MENU

    def _advance_to_next_level(self):
        """Advance to next level after completing current one"""
        # Unlock next level
        if self.selected_level < len(self.levels) - 1:
            self.levels[self.selected_level + 1].unlocked = True
            # Move to next level
            self.selected_level += 1
            self._build_level(self.levels[self.selected_level])
            self.state = GameState.PLAYING
        else:
            # Game complete - return to menu
            self.state = GameState.MAIN_MENU
            self.sound_manager.stop_music()

    def _handle_level_select_input(self, key):
        """Handle level select input"""
        if key == pygame.K_UP or key == pygame.K_w:
            self.selected_level = max(0, self.selected_level - 4)
        elif key == pygame.K_DOWN or key == pygame.K_s:
            self.selected_level = min(len(self.levels) - 1, self.selected_level + 4)
        elif key == pygame.K_LEFT or key == pygame.K_a:
            self.selected_level = max(0, self.selected_level - 1)
        elif key == pygame.K_RIGHT or key == pygame.K_d:
            self.selected_level = min(len(self.levels) - 1, self.selected_level + 1)
        elif key == pygame.K_RETURN:
            level = self.levels[self.selected_level]
            if level.unlocked:
                self._build_level(level)
                self.state = GameState.PLAYING
        elif key == pygame.K_ESCAPE:
            self.state = GameState.MAIN_MENU

    def _handle_game_input_down(self, key):
        """Handle in-game key press - SMB1 style (SPACE = jump, X/Z = fireball)"""
        if self.flagpole_touched:
            return  # No input during flagpole sequence

        if key == pygame.K_SPACE:
            self.player.jump(self.sound_manager)
        elif key == pygame.K_x or key == pygame.K_z:
            # Fire Mario shoots fireballs (max 2 on screen)
            if self.player.has_fire and len(self.fireballs) < 2:
                fireball = self.player.shoot_fireball(self.sound_manager)
                if fireball:
                    self.fireballs.add(fireball)
                    self.all_sprites.add(fireball)
        elif key == pygame.K_ESCAPE or key == pygame.K_p:
            self.state = GameState.PAUSED

    def _handle_game_input_up(self, key):
        """Handle in-game key release - for variable jump height"""
        if key == pygame.K_SPACE:
            self.player.release_jump()

    def _update(self):
        """Update game state"""
        # Handle COURSE_CLEAR time bonus counting
        if self.state == GameState.COURSE_CLEAR:
            if self.time_counting and self.time_bonus > 0:
                # Count down time bonus rapidly (SMB3 style)
                decrement = min(50, self.time_bonus)
                self.time_bonus -= decrement
                self.player.score += decrement
                if self.time_bonus <= 0:
                    self.time_bonus = 0
                    self.time_counting = False
            return
        
        if self.state != GameState.PLAYING:
            return

        # Update player
        self.player.update(self.platforms, self.sound_manager)

        # Update camera (smooth follow, SMB1 style - only moves right)
        target_camera_x = self.player.rect.centerx - SCREEN_WIDTH // 3
        if target_camera_x > self.camera_x:
            self.camera_x += (target_camera_x - self.camera_x) * 0.15
        self.camera_x = max(0, min(self.camera_x, self.level_width - SCREEN_WIDTH))

        # Update enemies
        for enemy in self.enemies:
            enemy.update(self.platforms)

        # Update coins
        for coin in self.coins:
            coin.update()

        # Update question blocks
        for qblock in self.question_blocks:
            qblock.update()

        # Update power-ups
        for powerup in self.power_ups:
            powerup.update(self.platforms)

        # Update block coins (animated coins from blocks)
        for block_coin in self.block_coins:
            block_coin.update()

        # Update fireballs and check enemy hits
        for fireball in list(self.fireballs):
            fireball.update(self.platforms)
            # Check fireball-enemy collision
            for enemy in list(self.enemies):
                if fireball.rect.colliderect(enemy.rect) and enemy.state != 'squished':
                    enemy.kill()
                    fireball.kill()
                    self.player.score += 200
                    self.sound_manager.play('stomp')
                    break

        # Check coin collection
        coin_hits = pygame.sprite.spritecollide(self.player, self.coins, True)
        for coin in coin_hits:
            self.player.coins += 1
            self.player.score += 100
            self.sound_manager.play('coin')
            if self.player.coins >= 100:
                self.player.coins -= 100
                self.player.lives += 1
                self.sound_manager.play('1up')

        # Check power-up collection
        powerup_hits = pygame.sprite.spritecollide(self.player, self.power_ups, False)
        for powerup in powerup_hits:
            # Don't collect if still emerging
            if hasattr(powerup, 'emerging') and powerup.emerging:
                continue
            powerup.kill()
            if powerup.type == 'mushroom':
                self.player.power_up('mushroom', self.sound_manager)
                self.player.score += 1000
            elif powerup.type == 'fireflower':
                self.player.power_up('fireflower', self.sound_manager)
                self.player.score += 1000
            elif powerup.type == '1up':
                self.player.power_up('1up', self.sound_manager)
            elif powerup.type == 'star':
                self.player.power_up('star', self.sound_manager)
                self.player.score += 1000

        # Check enemy collisions - SMB1 1:1 accurate with shell mechanics
        enemy_hits = pygame.sprite.spritecollide(self.player, self.enemies, False)
        for enemy in enemy_hits:
            # Skip squished enemies
            if enemy.state == 'squished':
                continue
                
            if self.player.star_power:
                # Star power kills everything instantly
                enemy.kill()
                self.player.score += 200
                self.sound_manager.play('stomp')
                continue
            
            # SMB1 stomp detection: Mario must be falling AND hit enemy from above
            # The key is Mario's feet must be above enemy's head when collision starts
            is_stomping = (self.player.vel_y > 0 and 
                          self.player.rect.bottom <= enemy.rect.top + 16 * NES_SCALE)
            
            if enemy.state == 'shell' and enemy.vel_x == 0:
                # Stationary shell - can kick from any direction safely
                kick_right = self.player.rect.centerx < enemy.rect.centerx
                enemy.kick(kick_right)
                self.player.score += 400
                self.sound_manager.play('stomp')
            elif is_stomping:
                # SMB1 stomp from above - kill or shell the enemy
                result = enemy.stomp()
                self.player.vel_y = -10  # Bounce up (SMB1 accurate bounce)
                
                # SMB1 combo scoring system
                combo_idx = min(self.player.stomp_combo, len(self.player.stomp_scores) - 1)
                stomp_score = self.player.stomp_scores[combo_idx]
                self.player.stomp_combo += 1
                
                if result == 'kill':
                    self.player.score += stomp_score
                elif result == 'shell':
                    self.player.score += stomp_score
                elif result == 'kick':
                    # Stomped a moving shell - stops it
                    self.player.score += stomp_score
                self.sound_manager.play('stomp')
            else:
                # NOT stomping - Mario takes damage (SMB1: enemies kill on side/bottom contact)
                if enemy.state in ['walking', 'shell_moving']:
                    if self.player.take_damage(self.sound_manager):
                        self.player.lives -= 1
                        if self.player.lives <= 0:
                            self.state = GameState.GAME_OVER
                        else:
                            # Respawn at start of visible area
                            self.player.rect.x = int(self.camera_x) + 100
                            self.player.rect.y = SCREEN_HEIGHT - 200
                            self.player.vel_x = 0
                            self.player.vel_y = 0

        # Check shell-enemy collisions (moving shells kill other enemies) - SMB1 chain scoring
        shell_kill_scores = [100, 200, 400, 800, 1000, 2000, 4000, 8000]  # SMB1 shell chain scores
        for enemy in list(self.enemies):
            if enemy.state == 'shell_moving':
                shell_kills = 0
                for other in list(self.enemies):
                    if other != enemy and enemy.rect.colliderect(other.rect):
                        if other.state not in ['shell_moving', 'squished']:
                            other.kill()
                            # Chain scoring - each subsequent kill worth more
                            score_idx = min(shell_kills, len(shell_kill_scores) - 1)
                            self.player.score += shell_kill_scores[score_idx]
                            shell_kills += 1
                            self.sound_manager.play('stomp')

        # Update bricks (for bump animation)
        for brick in list(self.bricks):
            brick.update()

        # Update debris particles
        for debris_piece in self.debris:
            debris_piece.update()

        # Check brick hits (from below) - SMB1 style breaking
        for brick in list(self.bricks):
            if not brick.broken:
                if (self.player.rect.top <= brick.rect.bottom and
                    self.player.rect.top >= brick.rect.bottom - 10 and
                    self.player.rect.right > brick.rect.left and
                    self.player.rect.left < brick.rect.right and
                    self.player.vel_y < 0):

                    if self.player.is_big:
                        # Big Mario breaks bricks
                        debris_pieces = brick.break_brick()
                        for debris_piece in debris_pieces:
                            self.debris.add(debris_piece)
                            self.all_sprites.add(debris_piece)
                        brick.kill()
                        self.player.score += 50
                        self.sound_manager.play('break')
                    else:
                        # Small Mario just bumps bricks
                        brick.bump()
                        # Check if brick contains a coin (hidden coin block)
                        if brick.contains_coin:
                            brick.contains_coin = False
                            block_coin = BlockCoin(brick.rect.x, brick.rect.y)
                            self.block_coins.add(block_coin)
                            self.all_sprites.add(block_coin)
                            self.player.coins += 1
                            self.player.score += 200
                            self.sound_manager.play('coin')

        # Check question block hits (from below)
        for qblock in self.question_blocks:
            if not qblock.hit:
                if (self.player.rect.top <= qblock.rect.bottom and
                    self.player.rect.top >= qblock.rect.bottom - 10 and
                    self.player.rect.right > qblock.rect.left and
                    self.player.rect.left < qblock.rect.right and
                    self.player.vel_y < 0):

                    qblock.hit = True
                    qblock.image = SpriteGenerator.create_question_block_sprite(True, 0)

                    # Spawn contents based on what the block contains
                    if qblock.contains == 'coin':
                        # Spawn animated coin that pops out
                        block_coin = BlockCoin(qblock.rect.x, qblock.rect.y)
                        self.block_coins.add(block_coin)
                        self.all_sprites.add(block_coin)
                        self.player.coins += 1
                        self.player.score += 200
                        self.sound_manager.play('coin')

                    elif qblock.contains == 'mushroom':
                        # If player is big, give fire flower instead
                        if self.player.is_big:
                            powerup = PowerUp(qblock.rect.x, qblock.rect.y, 'fireflower')
                        else:
                            powerup = PowerUp(qblock.rect.x, qblock.rect.y, 'mushroom')
                        self.power_ups.add(powerup)
                        self.all_sprites.add(powerup)

                    elif qblock.contains == 'fireflower':
                        # Fire flower - if small, becomes mushroom
                        if self.player.is_big:
                            powerup = PowerUp(qblock.rect.x, qblock.rect.y, 'fireflower')
                        else:
                            powerup = PowerUp(qblock.rect.x, qblock.rect.y, 'mushroom')
                        self.power_ups.add(powerup)
                        self.all_sprites.add(powerup)

                    elif qblock.contains == 'star':
                        # Starman - bounces around
                        powerup = PowerUp(qblock.rect.x, qblock.rect.y, 'star')
                        self.power_ups.add(powerup)
                        self.all_sprites.add(powerup)

                    elif qblock.contains == '1up':
                        # 1-Up mushroom (green)
                        powerup = PowerUp(qblock.rect.x, qblock.rect.y, '1up')
                        self.power_ups.add(powerup)
                        self.all_sprites.add(powerup)

        # Check if player fell off
        if self.player.rect.top > SCREEN_HEIGHT:
            self.player.lives -= 1
            if self.player.lives <= 0:
                self.state = GameState.GAME_OVER
            else:
                self.player.rect.x = 100
                self.player.rect.y = SCREEN_HEIGHT - 150
                self.camera_x = 0

        # Update flag animation
        if self.flag:
            self.flag.update()

        # Check if touched flagpole (SMB1 style)
        if self.flag and not self.flagpole_touched:
            flagpole_rect = pygame.Rect(self.flag.pole_x, self.flag.ground_y - 9 * TILE_SIZE, TILE_SIZE // 2, 9 * TILE_SIZE)
            if self.player.rect.colliderect(flagpole_rect):
                self.flagpole_touched = True
                self.flag.trigger()
                self.sound_manager.play('complete')
                self.sound_manager.stop_music()
                # Calculate bonus score based on height (SMB1 style)
                touch_height = self.flag.ground_y - self.player.rect.centery
                if touch_height > 7 * TILE_SIZE:
                    self.player.score += 5000
                elif touch_height > 5 * TILE_SIZE:
                    self.player.score += 2000
                elif touch_height > 3 * TILE_SIZE:
                    self.player.score += 800
                elif touch_height > TILE_SIZE:
                    self.player.score += 400
                else:
                    self.player.score += 100

        # Handle flagpole sequence (Mario slides down, then COURSE CLEAR)
        if self.flagpole_touched:
            self.level_complete_timer += 1
            self.player.vel_x = 0
            self.player.vel_y = 0
            
            # Mario slides down the pole (4 pixels per frame)
            target_y = self.flag.ground_y - TILE_SIZE * 2
            if self.player.rect.bottom < target_y:
                self.player.rect.y += 4
                self.player.pos_y = float(self.player.rect.y)
            
            # Transition to COURSE CLEAR after sliding + brief pause
            # Either: landed and waited, OR failsafe timeout
            has_landed = self.player.rect.bottom >= target_y
            waited_enough = self.level_complete_timer > 60
            failsafe = self.level_complete_timer > 180  # 3 second max
            
            if (has_landed and waited_enough) or failsafe:
                # Store time bonus for COURSE CLEAR screen
                self.time_bonus = self.level_timer * 50
                self.course_clear_timer = 0
                self.time_counting = True
                self.state = GameState.COURSE_CLEAR
                return  # Exit update early

        # Update level timer (SMB1 style: decrements ~2.4 times per second for 400 units over ~167 seconds)
        self.timer_frame_counter += 1
        if self.timer_frame_counter >= 25:  # Every 25 frames (~0.42 sec at 60fps) = decrement 1 time unit
            self.timer_frame_counter = 0
            self.level_timer -= 1
            # Play warning sound when timer is low
            if self.level_timer == 100:
                self.sound_manager.play('warning')
            # Time's up - player dies
            if self.level_timer <= 0:
                self.level_timer = 0
                self.player.lives -= 1
                if self.player.lives <= 0:
                    self.state = GameState.GAME_OVER
                else:
                    # Respawn player
                    self.player.rect.x = 100
                    self.player.rect.y = SCREEN_HEIGHT - 150
                    self.camera_x = 0
                    self.level_timer = 400  # Reset timer on respawn
                    self.timer_frame_counter = 0

    def _draw(self):
        """Draw current frame"""
        if self.state == GameState.MAIN_MENU:
            self._draw_main_menu()
        elif self.state == GameState.LEVEL_SELECT:
            self._draw_level_select()
        elif self.state == GameState.DEBUG_SELECT:
            self._draw_debug_select()
        elif self.state == GameState.PLAYING:
            self._draw_game()
        elif self.state == GameState.PAUSED:
            self._draw_game()
            self._draw_pause_overlay()
        elif self.state == GameState.GAME_OVER:
            self._draw_game_over()
        elif self.state == GameState.LEVEL_COMPLETE:
            self._draw_level_complete()
        elif self.state == GameState.COURSE_CLEAR:
            self._draw_course_clear()

    def _draw_main_menu(self):
        """Draw main menu"""
        # Animated background
        bg_color = (
            int(107 + 20 * math.sin(self.animation_frame * 0.02)),
            int(140 + 20 * math.sin(self.animation_frame * 0.025)),
            255
        )
        self.screen.fill(bg_color)

        # Draw some decorative clouds
        for i in range(5):
            cloud_x = (i * 200 + self.animation_frame * 0.5) % (SCREEN_WIDTH + 100) - 50
            pygame.draw.ellipse(self.screen, WHITE, (cloud_x, 100 + i * 30, 80, 40))
            pygame.draw.ellipse(self.screen, WHITE, (cloud_x + 20, 90 + i * 30, 60, 40))

        # Title with shadow (Super Mario Bros Deluxe style)
        title_line1 = self.title_font.render("ULTRA.", True, WHITE)
        title_shadow1 = self.title_font.render("ULTRA.", True, BLACK)
        title_rect1 = title_line1.get_rect(centerx=SCREEN_WIDTH//2, y=80)
        self.screen.blit(title_shadow1, (title_rect1.x + 4, title_rect1.y + 4))
        self.screen.blit(title_line1, title_rect1)

        title_line2 = self.title_font.render("MARIO 2D BROS", True, WHITE)
        title_shadow2 = self.title_font.render("MARIO 2D BROS", True, BLACK)
        title_rect2 = title_line2.get_rect(centerx=SCREEN_WIDTH//2, y=140)
        self.screen.blit(title_shadow2, (title_rect2.x + 4, title_rect2.y + 4))
        self.screen.blit(title_line2, title_rect2)

        # Copyright notices (SMB Deluxe style)
        copyright1 = self.small_font.render("\u00A9 1985-2026 Nintendo", True, WHITE)
        self.screen.blit(copyright1, (SCREEN_WIDTH//2 - copyright1.get_width()//2, 200))
        copyright2 = self.small_font.render("\u00A9 1999-2026 Samsoft", True, WHITE)
        self.screen.blit(copyright2, (SCREEN_WIDTH//2 - copyright2.get_width()//2, 220))

        # Menu options
        for i, option in enumerate(self.main_menu_options):
            color = YELLOW if i == self.selected_option else WHITE
            text = self.font.render(option, True, color)
            y = 300 + i * 50
            x = SCREEN_WIDTH//2 - text.get_width()//2

            if i == self.selected_option:
                # Animated selector
                offset = int(5 * math.sin(self.animation_frame * 0.1))
                arrow = self.font.render(">", True, YELLOW)
                self.screen.blit(arrow, (x - 30 + offset, y))

            self.screen.blit(text, (x, y))

        # Draw Mario sprite in menu
        mario_sprite = SpriteGenerator.create_mario_sprite(24, 32, True, False, False, self.animation_frame // 10)
        self.screen.blit(mario_sprite, (SCREEN_WIDTH//2 - 100, 350))

        # Footer
        footer = self.small_font.render("Arrow keys to navigate, ENTER to select", True, WHITE)
        self.screen.blit(footer, (SCREEN_WIDTH//2 - footer.get_width()//2, SCREEN_HEIGHT - 50))

        # OST indicator
        ost_text = self.small_font.render("Procedural OST Enabled", True, (150, 255, 150))
        self.screen.blit(ost_text, (SCREEN_WIDTH//2 - ost_text.get_width()//2, SCREEN_HEIGHT - 80))

    def _draw_level_select(self):
        """Draw level selection screen"""
        self.screen.fill((20, 20, 40))

        # Title
        title = self.font.render("SELECT WORLD", True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 30))

        # Draw level grid
        start_x = 80
        start_y = 100
        box_width = 80
        box_height = 50
        padding = 10

        for i, level in enumerate(self.levels):
            world = level.world
            stage = level.stage

            x = start_x + (stage - 1) * (box_width + padding)
            y = start_y + (world - 1) * (box_height + padding)

            # Selection highlight
            if i == self.selected_level:
                glow = int(20 * math.sin(self.animation_frame * 0.1))
                pygame.draw.rect(self.screen, (255, 255, 100 + glow),
                               (x-3, y-3, box_width+6, box_height+6), border_radius=5)

            # World-specific color
            if level.unlocked:
                color = WORLD_COLORS[world]['sky']
            else:
                color = (60, 60, 60)

            pygame.draw.rect(self.screen, color, (x, y, box_width, box_height), border_radius=3)

            # Level number
            text_color = WHITE if level.unlocked else (100, 100, 100)
            text = self.small_font.render(f"{world}-{stage}", True, text_color)
            text_rect = text.get_rect(center=(x + box_width//2, y + box_height//2))
            self.screen.blit(text, text_rect)

            # Lock icon for locked levels
            if not level.unlocked:
                lock = self.small_font.render("X", True, RED)
                self.screen.blit(lock, (x + box_width - 15, y + 5))

        # World names
        for i in range(1, 9):
            y = start_y + (i - 1) * (box_height + padding) + box_height//2 - 10
            name_color = WORLD_COLORS[i]['sky']
            text = self.small_font.render(f"W{i}: {WORLD_COLORS[i]['name']}", True, name_color)
            self.screen.blit(text, (start_x + 4 * (box_width + padding) + 30, y))

        # Selected level info
        selected = self.levels[self.selected_level]
        info = f"Selected: {selected.name}"
        if not selected.unlocked:
            info += " [LOCKED]"
        info_color = WORLD_COLORS[selected.world]['sky'] if selected.unlocked else RED
        info_text = self.font.render(info, True, info_color)
        self.screen.blit(info_text, (SCREEN_WIDTH//2 - info_text.get_width()//2, SCREEN_HEIGHT - 80))

        # Instructions
        instr = self.small_font.render("Arrows to select, ENTER to play, ESC for menu", True, WHITE)
        self.screen.blit(instr, (SCREEN_WIDTH//2 - instr.get_width()//2, SCREEN_HEIGHT - 40))

    def _draw_game(self):
        """Draw the game screen"""
        # Background color based on world
        sky_color = WORLD_COLORS.get(self.current_world, WORLD_COLORS[1])['sky']
        self.screen.fill(sky_color)

        # Draw parallax background elements
        self._draw_background()

        # Draw all sprites with camera offset
        for sprite in sorted(self.all_sprites, key=lambda s: s.rect.y):
            self.screen.blit(sprite.image, (sprite.rect.x - self.camera_x, sprite.rect.y))

        # HUD
        self._draw_hud()

    def _draw_background(self):
        """Draw SMB1-style parallax background elements"""
        world = self.current_world
        ground_y = SCREEN_HEIGHT - TILE_SIZE - 40

        # SMB1 style clouds (white with rounded shapes)
        if world not in [2, 4, 8]:  # Not underground/castle
            # Small cloud pattern repeating
            cloud_positions = [
                (0, 60, 'small'), (200, 80, 'medium'), (450, 50, 'large'),
                (600, 90, 'small'), (850, 70, 'medium')
            ]
            for base_x, y, size in cloud_positions:
                cloud_x = (base_x - self.camera_x * 0.3) % (SCREEN_WIDTH + 400) - 100
                if size == 'small':
                    pygame.draw.ellipse(self.screen, WHITE, (cloud_x, y, 60, 30))
                    pygame.draw.ellipse(self.screen, WHITE, (cloud_x + 15, y - 10, 40, 30))
                elif size == 'medium':
                    pygame.draw.ellipse(self.screen, WHITE, (cloud_x, y, 90, 40))
                    pygame.draw.ellipse(self.screen, WHITE, (cloud_x + 25, y - 15, 60, 40))
                    pygame.draw.ellipse(self.screen, WHITE, (cloud_x + 55, y, 50, 35))
                else:  # large
                    pygame.draw.ellipse(self.screen, WHITE, (cloud_x, y, 120, 50))
                    pygame.draw.ellipse(self.screen, WHITE, (cloud_x + 35, y - 20, 80, 50))
                    pygame.draw.ellipse(self.screen, WHITE, (cloud_x + 80, y, 60, 40))

        # SMB1 style hills (green rounded hills in background)
        if world in [1, 3, 5, 7]:  # Overworld levels
            hill_green = (0, 168, 0)
            hill_dark = (0, 120, 0)
            hill_positions = [(0, 'large'), (350, 'small'), (700, 'medium')]
            for base_x, size in hill_positions:
                hill_x = (base_x - self.camera_x * 0.4) % (SCREEN_WIDTH + 500) - 150
                if size == 'small':
                    # Small hill
                    pygame.draw.polygon(self.screen, hill_green, [
                        (hill_x, ground_y), (hill_x + 40, ground_y - 50),
                        (hill_x + 80, ground_y)
                    ])
                elif size == 'medium':
                    # Medium hill
                    pygame.draw.polygon(self.screen, hill_green, [
                        (hill_x, ground_y), (hill_x + 70, ground_y - 80),
                        (hill_x + 140, ground_y)
                    ])
                else:  # large
                    # Large hill with spots
                    pygame.draw.polygon(self.screen, hill_green, [
                        (hill_x, ground_y), (hill_x + 100, ground_y - 100),
                        (hill_x + 200, ground_y)
                    ])
                    # Add hill spots
                    pygame.draw.circle(self.screen, hill_dark, (int(hill_x + 80), int(ground_y - 60)), 8)
                    pygame.draw.circle(self.screen, hill_dark, (int(hill_x + 100), int(ground_y - 40)), 6)
                    pygame.draw.circle(self.screen, hill_dark, (int(hill_x + 120), int(ground_y - 65)), 5)

        # SMB1 style bushes (same shape as clouds but green)
        if world in [1, 3, 5, 7]:
            bush_green = (0, 168, 0)
            bush_positions = [(100, 'small'), (400, 'medium'), (650, 'small')]
            for base_x, size in bush_positions:
                bush_x = (base_x - self.camera_x * 0.5) % (SCREEN_WIDTH + 400) - 100
                bush_y = ground_y - 10
                if size == 'small':
                    pygame.draw.ellipse(self.screen, bush_green, (bush_x, bush_y, 60, 30))
                else:
                    pygame.draw.ellipse(self.screen, bush_green, (bush_x, bush_y, 90, 40))
                    pygame.draw.ellipse(self.screen, bush_green, (bush_x + 30, bush_y - 10, 50, 35))
                    pygame.draw.ellipse(self.screen, bush_green, (bush_x + 55, bush_y, 50, 35))

        # Castle at end of level
        castle_x = 205 * TILE_SIZE - self.camera_x
        if -200 < castle_x < SCREEN_WIDTH + 200:
            self._draw_castle(castle_x, ground_y)

        # Underground/Castle specific decorations
        if world == 8:  # Castle - lava glow
            glow = int(30 * math.sin(self.animation_frame * 0.05))
            pygame.draw.rect(self.screen, (100 + glow, 20, 0),
                           (0, SCREEN_HEIGHT - 20, SCREEN_WIDTH, 20))

    def _draw_castle(self, x: int, y: int):
        """Draw SMB1-style castle at level end"""
        castle_color = (188, 188, 188)  # Gray
        castle_dark = (100, 100, 100)
        window_color = BLACK

        # Main castle body
        castle_width = 5 * TILE_SIZE
        castle_height = 4 * TILE_SIZE
        pygame.draw.rect(self.screen, castle_color, (x, y - castle_height, castle_width, castle_height))

        # Castle top crenellations
        for i in range(6):
            if i % 2 == 0:
                pygame.draw.rect(self.screen, castle_color,
                               (x + i * (TILE_SIZE - 8), y - castle_height - TILE_SIZE // 2, TILE_SIZE - 8, TILE_SIZE // 2))

        # Castle door (black arch)
        door_width = TILE_SIZE
        door_height = TILE_SIZE * 2
        door_x = x + castle_width // 2 - door_width // 2
        pygame.draw.rect(self.screen, window_color, (door_x, y - door_height, door_width, door_height))
        pygame.draw.ellipse(self.screen, window_color, (door_x, y - door_height - door_width // 2, door_width, door_width))

        # Windows
        window_size = TILE_SIZE // 2
        pygame.draw.rect(self.screen, window_color, (x + TILE_SIZE // 2, y - castle_height + TILE_SIZE // 2, window_size, window_size))
        pygame.draw.rect(self.screen, window_color, (x + castle_width - TILE_SIZE, y - castle_height + TILE_SIZE // 2, window_size, window_size))

    def _draw_hud(self):
        """Draw NES-style HUD"""
        # HUD background (black bar at top like NES)
        pygame.draw.rect(self.screen, BLACK, (0, 0, SCREEN_WIDTH, 40))

        # MARIO text and score
        mario_label = self.small_font.render("MARIO", True, WHITE)
        self.screen.blit(mario_label, (24, 4))
        score_text = self.small_font.render(f"{self.player.score:06d}", True, WHITE)
        self.screen.blit(score_text, (24, 20))

        # Coin counter with cached coin icon
        coin_icon = SpriteGenerator.create_coin_sprite(0)  # Use frame 0 for HUD
        scaled_coin = pygame.transform.scale(coin_icon, (16, 24))
        self.screen.blit(scaled_coin, (180, 10))
        coin_text = self.small_font.render(f"x{self.player.coins:02d}", True, WHITE)
        self.screen.blit(coin_text, (200, 16))

        # World indicator
        level = self.levels[self.selected_level]
        world_label = self.small_font.render("WORLD", True, WHITE)
        self.screen.blit(world_label, (320, 4))
        world_text = self.small_font.render(f"{level.world}-{level.stage}", True, WHITE)
        self.screen.blit(world_text, (328, 20))

        # Time - countdown timer (SMB1 style)
        time_label = self.small_font.render("TIME", True, WHITE)
        self.screen.blit(time_label, (480, 4))
        # Flash timer red when low
        timer_color = RED if self.level_timer <= 100 else WHITE
        time_text = self.small_font.render(f"{self.level_timer:03d}", True, timer_color)
        self.screen.blit(time_text, (488, 20))

        # Lives counter
        lives_label = self.small_font.render("LIVES", True, WHITE)
        self.screen.blit(lives_label, (600, 4))
        lives_text = self.small_font.render(f"x{self.player.lives}", True, WHITE)
        self.screen.blit(lives_text, (608, 20))

        # Star power indicator
        if self.player.star_power:
            star_text = self.small_font.render(f"STAR:{self.player.star_timer // 60}", True, YELLOW)
            self.screen.blit(star_text, (700, 16))

    def _draw_pause_overlay(self):
        """Draw pause screen overlay"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        pause_text = self.title_font.render("PAUSED", True, WHITE)
        self.screen.blit(pause_text, (SCREEN_WIDTH//2 - pause_text.get_width()//2, SCREEN_HEIGHT//2 - 60))

        continue_text = self.font.render("Press P or ESC to continue", True, WHITE)
        self.screen.blit(continue_text, (SCREEN_WIDTH//2 - continue_text.get_width()//2, SCREEN_HEIGHT//2 + 20))

    def _draw_game_over(self):
        """Draw game over screen"""
        self.screen.fill((40, 0, 0))

        title = self.title_font.render("GAME OVER", True, RED)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, SCREEN_HEIGHT//2 - 80))

        score_text = self.font.render(f"Final Score: {self.player.score}", True, WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, SCREEN_HEIGHT//2))

        coins_text = self.font.render(f"Coins Collected: {self.player.coins}", True, YELLOW)
        self.screen.blit(coins_text, (SCREEN_WIDTH//2 - coins_text.get_width()//2, SCREEN_HEIGHT//2 + 40))

        continue_text = self.font.render("Press ENTER to return to menu", True, WHITE)
        self.screen.blit(continue_text, (SCREEN_WIDTH//2 - continue_text.get_width()//2, SCREEN_HEIGHT//2 + 100))

    def _draw_level_complete(self):
        """Draw level complete screen"""
        # Animated background
        bg_brightness = int(20 + 10 * math.sin(self.animation_frame * 0.1))
        self.screen.fill((0, bg_brightness, 0))

        title = self.title_font.render("LEVEL COMPLETE!", True, GREEN)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, SCREEN_HEIGHT//2 - 100))

        level = self.levels[self.selected_level]
        level_text = self.font.render(f"World {level.world}-{level.stage} Cleared!", True, WHITE)
        self.screen.blit(level_text, (SCREEN_WIDTH//2 - level_text.get_width()//2, SCREEN_HEIGHT//2 - 20))

        score_text = self.font.render(f"Score: {self.player.score}", True, YELLOW)
        self.screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, SCREEN_HEIGHT//2 + 30))

        coins_text = self.font.render(f"Coins: {self.player.coins}", True, COIN_YELLOW)
        self.screen.blit(coins_text, (SCREEN_WIDTH//2 - coins_text.get_width()//2, SCREEN_HEIGHT//2 + 70))

        # Show next level unlock
        if self.selected_level < len(self.levels) - 1:
            next_level = self.levels[self.selected_level + 1]
            unlock_text = self.font.render(f"Unlocked: World {next_level.world}-{next_level.stage}!", True, (100, 255, 100))
            self.screen.blit(unlock_text, (SCREEN_WIDTH//2 - unlock_text.get_width()//2, SCREEN_HEIGHT//2 + 120))

        continue_text = self.font.render("Press ENTER to continue", True, WHITE)
        self.screen.blit(continue_text, (SCREEN_WIDTH//2 - continue_text.get_width()//2, SCREEN_HEIGHT//2 + 170))

    def _draw_course_clear(self):
        """Draw SMB3-style COURSE CLEAR screen with time bonus"""
        # Black background with animated border
        self.screen.fill(BLACK)
        
        # Animated border
        border_color = (
            int(128 + 127 * math.sin(self.animation_frame * 0.1)),
            int(128 + 127 * math.sin(self.animation_frame * 0.1 + 2)),
            int(128 + 127 * math.sin(self.animation_frame * 0.1 + 4))
        )
        pygame.draw.rect(self.screen, border_color, (20, 20, SCREEN_WIDTH - 40, SCREEN_HEIGHT - 40), 4)
        
        # Big "COURSE CLEAR" text (SMB3 style)
        clear_font = pygame.font.Font(None, 96)
        course_text = clear_font.render("COURSE", True, WHITE)
        clear_text = clear_font.render("CLEAR!", True, YELLOW)
        
        self.screen.blit(course_text, (SCREEN_WIDTH//2 - course_text.get_width()//2, 80))
        self.screen.blit(clear_text, (SCREEN_WIDTH//2 - clear_text.get_width()//2, 160))
        
        # Level info
        level = self.levels[self.selected_level]
        level_text = self.font.render(f"WORLD {level.world}-{level.stage}", True, (100, 200, 255))
        self.screen.blit(level_text, (SCREEN_WIDTH//2 - level_text.get_width()//2, 260))
        
        # Score display
        score_text = self.font.render(f"SCORE: {self.player.score}", True, WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, 320))
        
        # Time bonus (counts down)
        time_label = self.font.render("TIME BONUS:", True, WHITE)
        self.screen.blit(time_label, (SCREEN_WIDTH//2 - 150, 370))
        
        bonus_text = self.font.render(f"{self.time_bonus}", True, YELLOW)
        self.screen.blit(bonus_text, (SCREEN_WIDTH//2 + 50, 370))
        
        # Coins
        coins_text = self.font.render(f"COINS: {self.player.coins}", True, COIN_YELLOW)
        self.screen.blit(coins_text, (SCREEN_WIDTH//2 - coins_text.get_width()//2, 420))
        
        # Lives
        lives_text = self.font.render(f"LIVES: {self.player.lives}", True, (255, 100, 100))
        self.screen.blit(lives_text, (SCREEN_WIDTH//2 - lives_text.get_width()//2, 460))
        
        # Next level info
        if self.selected_level < len(self.levels) - 1:
            next_level = self.levels[self.selected_level + 1]
            next_text = self.small_font.render(f"NEXT: WORLD {next_level.world}-{next_level.stage}", True, (150, 255, 150))
            self.screen.blit(next_text, (SCREEN_WIDTH//2 - next_text.get_width()//2, 520))
        else:
            complete_text = self.font.render("GAME COMPLETE!", True, (255, 215, 0))
            self.screen.blit(complete_text, (SCREEN_WIDTH//2 - complete_text.get_width()//2, 520))
        
        # Press to continue (only show when time counting done)
        if not self.time_counting:
            continue_text = self.small_font.render("Press ENTER to continue", True, (200, 200, 200))
            self.screen.blit(continue_text, (SCREEN_WIDTH//2 - continue_text.get_width()//2, SCREEN_HEIGHT - 60))

    def _draw_debug_select(self):
        """Draw debug level select - all levels unlocked"""
        self.screen.fill((40, 0, 40))  # Dark purple background
        
        # Title
        title = self.title_font.render("DEBUG SELECT", True, (255, 100, 255))
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 30))
        
        subtitle = self.small_font.render("All levels unlocked - Select any level", True, (200, 150, 255))
        self.screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 90))
        
        # Draw level grid (8 worlds x 4 stages)
        start_x = 80
        start_y = 140
        box_width = 80
        box_height = 50
        spacing_x = 90
        spacing_y = 60
        
        for i, level in enumerate(self.levels):
            row = i // 4
            col = i % 4
            x = start_x + col * spacing_x
            y = start_y + row * spacing_y
            
            # Highlight selected
            if i == self.selected_level:
                pygame.draw.rect(self.screen, YELLOW, (x - 3, y - 3, box_width + 6, box_height + 6), 3)
                color = WHITE
            else:
                color = (150, 150, 200)
            
            # Draw box
            pygame.draw.rect(self.screen, (60, 40, 80), (x, y, box_width, box_height))
            pygame.draw.rect(self.screen, color, (x, y, box_width, box_height), 2)
            
            # Level text
            level_text = self.font.render(f"{level.world}-{level.stage}", True, color)
            text_x = x + box_width//2 - level_text.get_width()//2
            text_y = y + box_height//2 - level_text.get_height()//2
            self.screen.blit(level_text, (text_x, text_y))
        
        # Footer
        footer = self.small_font.render("Arrow keys to select, ENTER to play, ESC for menu", True, WHITE)
        self.screen.blit(footer, (SCREEN_WIDTH//2 - footer.get_width()//2, SCREEN_HEIGHT - 40))


def main():
    """Entry point"""
    print("Ultra Mario 4K 1.x - SMB1 Famicom Engine")
    print("========================================")
    print("All graphics generated inline - no external files!")
    print("Procedural chiptune OST for each world!")
    print("")
    print("Controls (Famicom style):")
    print("  Arrow keys / WASD - Move (with momentum)")
    print("  SPACE - Jump (hold for higher jump)")
    print("  SHIFT - Run")
    print("  P / ESC - Pause")
    print("")
    print("Tips:")
    print("  - Tap SPACE for short hop, hold for full jump")
    print("  - Build speed before jumping for longer jumps")
    print("  - Hit ? blocks from below for power-ups!")
    print("")
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
