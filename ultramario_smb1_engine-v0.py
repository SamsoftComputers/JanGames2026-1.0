#!/usr/bin/env python3
"""
Cat's Ultra Mario 2D Bros! v1.1
Complete NES-Exact SMB1 Engine (Single File)
All 32 levels (1-1 through 8-4), NES physics, SMB1/SMB3-style OST
Team Flames / Samsoft

Controls:
  Arrow Keys / WASD - Move
  Z / Space - Jump (hold for higher)
  X / Shift - Run/Fire
  Enter - Start/Pause
"""

import pygame
import math
import array
import random

pygame.init()
pygame.mixer.init(22050, -16, 2, 512)

# === NES DISPLAY CONSTANTS ===
SCALE = 3
NES_W, NES_H = 256, 240
W, H = NES_W * SCALE, NES_H * SCALE
T = 16
FPS = 60

screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Cat's Ultra Mario 2D Bros! v1.1")
nes_surface = pygame.Surface((NES_W, NES_H))
clock = pygame.time.Clock()

# === NES-EXACT PHYSICS ===
class Phys:
    WALK_ACCEL = 0.0390625
    RUN_ACCEL = 0.0546875
    RELEASE_DECEL = 0.0546875
    SKID_DECEL = 0.1015625
    WALK_MAX = 1.5625
    RUN_MAX = 2.5
    GRAVITY = 0.4375
    GRAVITY_HOLDING = 0.1875
    GRAVITY_FAST = 0.5625
    MAX_FALL = 4.0
    JUMP_VEL = [-4.0, -4.0, -5.0]
    JUMP_FRAMES = 24
    GOOMBA_SPEED = 0.5
    KOOPA_SPEED = 0.5
    SHELL_SPEED = 3.0

# === NES PALETTE ===
class Pal:
    BLACK = (0, 0, 0)
    WHITE = (252, 252, 252)
    SKY = (92, 148, 252)
    UNDERGROUND = (0, 0, 0)
    UNDERWATER = (60, 188, 252)
    CASTLE = (0, 0, 0)
    MARIO_RED = (228, 0, 88)
    MARIO_TAN = (252, 152, 56)
    MARIO_BROWN = (136, 20, 0)
    BRICK = (172, 80, 36)
    BRICK_DARK = (136, 20, 0)
    QUESTION = (252, 152, 56)
    QUESTION_DARK = (200, 116, 20)
    GROUND = (252, 152, 56)
    GROUND_DARK = (136, 20, 0)
    PIPE = (0, 168, 0)
    PIPE_LIGHT = (0, 228, 0)
    PIPE_DARK = (0, 108, 0)
    CASTLE_GRAY = (188, 188, 188)
    CASTLE_DARK = (116, 116, 116)
    GOOMBA = (172, 80, 36)
    KOOPA_GREEN = (0, 168, 0)
    KOOPA_RED = (228, 0, 88)
    MUSHROOM = (228, 0, 88)
    FIRE = (252, 152, 56)
    STAR = (252, 188, 60)
    COIN = (252, 188, 60)

# === SOUND SYSTEM ===
def make_sound(freq_func, duration, volume=0.3):
    sample_rate = 22050
    samples = int(sample_rate * duration)
    data = array.array("h")
    for i in range(samples):
        t = i / sample_rate
        val = freq_func(t) if callable(freq_func) else 0
        sample = int(max(-1, min(1, val)) * 32767 * volume)
        data.append(sample)
        data.append(sample)
    return pygame.mixer.Sound(buffer=data)

def square_wave(t, freq, duty=0.5):
    if freq <= 0: return 0
    return 1.0 if (t * freq) % 1.0 < duty else -1.0

def triangle_wave(t, freq):
    if freq <= 0: return 0
    phase = (t * freq) % 1.0
    return 4.0 * abs(phase - 0.5) - 1.0

def noise(t):
    n = int(t * 22050) * 1103515245 + 12345
    return ((n >> 16) & 0x7fff) / 16384.0 - 1.0

def note_freq(note):
    if note == 0: return 0
    return 440.0 * (2.0 ** ((note - 69) / 12.0))

SFX = {}
MUSIC = {}
MUSIC_VOL = 0.12

def init_sounds():
    SFX["jump"] = make_sound(lambda t: square_wave(t, 400 + 1200*t, 0.25), 0.15, 0.2)
    SFX["jump_big"] = make_sound(lambda t: square_wave(t, 300 + 1000*t, 0.25), 0.2, 0.2)
    SFX["stomp"] = make_sound(lambda t: square_wave(t, 300 - 200*t, 0.5), 0.1, 0.25)
    SFX["bump"] = make_sound(lambda t: square_wave(t, 200 - 100*t, 0.5), 0.08, 0.2)
    SFX["break"] = make_sound(lambda t: noise(t) * max(0, 1 - t*5), 0.15, 0.3)
    SFX["coin"] = make_sound(lambda t: square_wave(t, 1500 if t < 0.05 else 1200, 0.5), 0.12, 0.2)
    SFX["powerup"] = make_sound(lambda t: square_wave(t, 400 + 600*math.sin(t*40), 0.25), 0.5, 0.2)
    SFX["sprout"] = make_sound(lambda t: square_wave(t, 600 + 400*t, 0.25), 0.25, 0.2)
    SFX["fireball"] = make_sound(lambda t: square_wave(t, 800 - 600*t, 0.5), 0.06, 0.15)
    SFX["kick"] = make_sound(lambda t: square_wave(t, 500 - 300*t, 0.5), 0.08, 0.2)
    SFX["1up"] = make_sound(lambda t: square_wave(t, 600 + 200*math.sin(t*20), 0.25), 0.5, 0.25)
    SFX["pipe"] = make_sound(lambda t: square_wave(t, 100 + 50*math.sin(t*10), 0.5), 0.3, 0.2)
    SFX["die"] = make_sound(lambda t: square_wave(t, 400 - 350*t, 0.25), 0.8, 0.3)
    SFX["flagpole"] = make_sound(lambda t: square_wave(t, 800 + 400*math.sin(t*15), 0.25), 0.8, 0.2)
    SFX["warning"] = make_sound(lambda t: square_wave(t, 600, 0.5) if int(t*8)%2==0 else 0, 0.4, 0.2)
    SFX["firework"] = make_sound(lambda t: noise(t) * max(0, 1 - t*3), 0.3, 0.25)

def make_music(melody, bass, tempo, duration, duty=0.25):
    sample_rate = 22050
    samples = int(sample_rate * duration)
    beat_dur = 60.0 / tempo
    data = array.array("h")
    for i in range(samples):
        t = i / sample_rate
        beat = t / beat_dur
        m_idx = int(beat * 2) % len(melody)
        m_note = melody[m_idx]
        lead = square_wave(t, note_freq(m_note), duty) * 0.25 if m_note else 0
        b_idx = int(beat) % len(bass)
        b_note = bass[b_idx]
        bass_v = triangle_wave(t, note_freq(b_note)) * 0.35 if b_note else 0
        perc = noise(t) * 0.12 if (beat % 1.0) < 0.03 else 0
        sample = max(-1, min(1, (lead + bass_v + perc) * MUSIC_VOL))
        v = int(sample * 32767)
        data.append(v)
        data.append(v)
    return pygame.mixer.Sound(buffer=data)

def init_music():
    # === SMB1 OVERWORLD (Iconic bouncy theme - C major) ===
    # Based on the actual SMB1 melody pattern: E E _ E _ C E _ G _ _ _ G(low)
    MUSIC["overworld"] = make_music(
        # SMB1 main theme melody approximation
        [76, 76, 0, 76, 0, 72, 76, 0, 79, 0, 0, 0, 67, 0, 0, 0,  # E E _ E _ C E _ G _ _ _ G
         72, 0, 0, 67, 0, 0, 64, 0, 0, 69, 0, 71, 0, 70, 69, 0,  # C _ _ G _ _ E _ _ A _ B _ Bb A
         67, 79, 81, 0, 77, 79, 0, 76, 0, 72, 74, 71, 0, 0, 0, 0, # G G# A _ F G _ E _ C D B
         72, 0, 0, 67, 0, 0, 64, 0, 0, 69, 0, 71, 0, 70, 69, 0],
        # Walking bass
        [48, 52, 55, 52, 48, 52, 55, 52, 43, 47, 50, 47, 48, 52, 55, 52,
         45, 48, 52, 48, 43, 47, 50, 47, 48, 52, 55, 52, 43, 47, 50, 47],
        200, 8.0, 0.125  # Fast duty cycle for NES square wave sound
    )
    
    # === SMB3 OVERWORLD (Funkier, syncopated groove) ===
    MUSIC["overworld3"] = make_music(
        # SMB3 World 1 style - more syncopated and playful
        [74, 0, 74, 77, 0, 74, 72, 0, 69, 0, 72, 74, 0, 72, 69, 0,  # D D F# D C A A C D C A
         74, 0, 74, 77, 0, 79, 81, 0, 79, 0, 77, 74, 0, 72, 69, 0,  # D D F# G A G F# D C A
         71, 0, 74, 0, 77, 0, 81, 0, 79, 0, 77, 74, 0, 71, 69, 0,  # B D F# A G F# D B A
         74, 77, 79, 0, 77, 74, 0, 72, 69, 0, 67, 69, 72, 0, 0, 0],
        [50, 0, 50, 57, 0, 57, 50, 0, 45, 0, 45, 52, 0, 52, 45, 0,
         50, 0, 50, 57, 0, 57, 50, 0, 47, 0, 47, 54, 0, 54, 47, 0],
        185, 8.0, 0.25
    )
    
    # === SMB1 UNDERGROUND (Dark chromatic blues) ===
    MUSIC["underground"] = make_music(
        # Underground bass-heavy chromatic theme
        [48, 60, 55, 60, 53, 65, 60, 65, 48, 60, 55, 60, 53, 65, 60, 65,
         50, 62, 57, 62, 55, 67, 62, 67, 48, 60, 55, 60, 53, 65, 60, 65],
        [36, 0, 36, 0, 33, 0, 33, 0, 36, 0, 36, 0, 33, 0, 33, 0,
         38, 0, 38, 0, 35, 0, 35, 0, 36, 0, 36, 0, 33, 0, 33, 0],
        140, 6.0, 0.5
    )
    
    # === SMB3 UNDERGROUND (Groovier bass) ===
    MUSIC["underground3"] = make_music(
        [60, 0, 63, 67, 0, 63, 60, 0, 58, 0, 61, 65, 0, 61, 58, 0,
         60, 0, 63, 67, 70, 0, 67, 63, 60, 0, 58, 55, 0, 58, 60, 0,
         62, 0, 65, 69, 0, 65, 62, 0, 60, 0, 63, 67, 0, 63, 60, 0,
         58, 0, 60, 62, 0, 60, 58, 0, 55, 0, 58, 60, 0, 0, 0, 0],
        [36, 0, 36, 43, 0, 43, 36, 0, 34, 0, 34, 41, 0, 41, 34, 0,
         35, 0, 35, 42, 0, 42, 35, 0, 36, 0, 36, 43, 0, 40, 36, 0],
        150, 6.0, 0.5
    )
    
    # === SMB1 CASTLE (Ominous chromatic) ===
    MUSIC["castle"] = make_music(
        # Chromatic descending menace
        [64, 0, 67, 0, 70, 0, 67, 0, 63, 0, 66, 0, 69, 0, 66, 0,
         62, 0, 65, 0, 68, 0, 65, 0, 64, 0, 67, 0, 70, 0, 67, 0,
         64, 67, 70, 0, 73, 0, 70, 67, 63, 66, 69, 0, 72, 0, 69, 66,
         64, 0, 0, 0, 67, 0, 0, 0, 70, 0, 67, 64, 0, 0, 0, 0],
        [40, 0, 40, 0, 40, 0, 40, 0, 39, 0, 39, 0, 39, 0, 39, 0,
         38, 0, 38, 0, 38, 0, 38, 0, 40, 0, 39, 0, 38, 0, 40, 0],
        130, 6.0, 0.5
    )
    
    # === SMB3 CASTLE (Fortress theme style) ===
    MUSIC["castle3"] = make_music(
        [67, 0, 70, 73, 0, 70, 67, 0, 66, 0, 69, 72, 0, 69, 66, 0,
         65, 0, 68, 71, 0, 74, 71, 68, 67, 0, 70, 73, 76, 0, 73, 70,
         67, 70, 73, 0, 76, 0, 73, 70, 67, 0, 64, 0, 67, 70, 73, 0,
         67, 0, 0, 70, 0, 0, 73, 0, 0, 76, 0, 73, 70, 67, 0, 0],
        [43, 0, 43, 50, 0, 50, 43, 0, 42, 0, 42, 49, 0, 49, 42, 0,
         41, 0, 41, 48, 0, 48, 41, 0, 43, 0, 43, 50, 0, 47, 43, 0],
        140, 6.0, 0.25
    )
    
    # === SMB1 UNDERWATER (Waltz feel) ===
    MUSIC["underwater"] = make_music(
        # Lilting 3/4 underwater theme
        [72, 0, 74, 76, 0, 79, 0, 76, 74, 0, 72, 0, 69, 0, 71, 72,
         74, 0, 76, 0, 79, 81, 0, 79, 76, 0, 74, 72, 0, 69, 67, 0,
         72, 74, 76, 0, 79, 0, 81, 84, 0, 81, 79, 0, 76, 74, 0, 72,
         72, 0, 74, 0, 76, 0, 79, 0, 76, 74, 72, 0, 0, 0, 0, 0],
        [48, 55, 52, 48, 55, 52, 50, 57, 54, 50, 57, 54,
         52, 59, 56, 52, 59, 56, 48, 55, 52, 48, 55, 52,
         50, 57, 54, 50, 57, 54, 48, 55, 52, 48, 52, 48],
        160, 7.0, 0.25
    )
    
    # === SMB3 WATER (World 3 style) ===
    MUSIC["underwater3"] = make_music(
        [72, 76, 79, 0, 84, 0, 79, 76, 72, 0, 69, 72, 76, 0, 79, 0,
         81, 0, 84, 0, 88, 0, 84, 81, 79, 0, 76, 72, 0, 69, 67, 0,
         72, 0, 76, 0, 79, 84, 0, 88, 91, 0, 88, 84, 79, 0, 76, 0,
         72, 76, 79, 84, 0, 79, 76, 72, 0, 69, 67, 0, 0, 0, 0, 0],
        [48, 52, 55, 48, 52, 55, 50, 54, 57, 50, 54, 57,
         52, 56, 59, 52, 56, 59, 48, 52, 55, 48, 52, 55],
        170, 6.0, 0.25
    )
    
    # === STAR POWER (SMB1 invincibility) ===
    MUSIC["star"] = make_music(
        [72, 76, 79, 84, 79, 76, 72, 79, 84, 88, 84, 79, 72, 76, 79, 84,
         74, 77, 81, 86, 81, 77, 74, 81, 86, 89, 86, 81, 74, 77, 81, 86,
         76, 79, 84, 88, 91, 88, 84, 79, 74, 77, 81, 86, 89, 86, 81, 77,
         72, 76, 79, 84, 88, 84, 79, 76, 72, 76, 79, 72, 0, 0, 0, 0],
        [48, 48, 55, 55, 48, 48, 55, 55, 50, 50, 57, 57, 50, 50, 57, 57,
         52, 52, 59, 59, 52, 52, 59, 59, 48, 48, 55, 55, 50, 50, 48, 48],
        300, 4.0, 0.125
    )
    
    # === SMB3 ATHLETIC (Sky/Athletic theme) ===
    MUSIC["athletic"] = make_music(
        [76, 0, 79, 84, 0, 88, 84, 79, 76, 0, 79, 84, 0, 88, 91, 0,
         89, 0, 86, 81, 0, 77, 81, 86, 89, 0, 86, 81, 0, 77, 76, 0,
         76, 79, 81, 84, 0, 86, 89, 0, 91, 0, 89, 86, 84, 0, 81, 79,
         76, 0, 79, 81, 0, 79, 76, 72, 69, 0, 72, 76, 0, 0, 0, 0],
        [52, 0, 52, 59, 0, 59, 52, 0, 54, 0, 54, 61, 0, 61, 54, 0,
         56, 0, 56, 63, 0, 63, 56, 0, 52, 0, 52, 59, 0, 56, 52, 0],
        210, 6.0, 0.125
    )
    
    # === LEVEL COMPLETE (SMB1 fanfare) ===
    MUSIC["level_complete"] = make_music(
        [67, 0, 72, 0, 76, 0, 72, 0, 76, 0, 79, 0, 84, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [43, 0, 48, 0, 52, 0, 48, 0, 52, 0, 55, 0, 60, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        200, 2.0, 0.25
    )
    
    # === CASTLE COMPLETE ===
    MUSIC["castle_complete"] = make_music(
        [64, 67, 72, 0, 76, 79, 84, 0, 88, 0, 84, 0, 88, 0, 91, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [40, 43, 48, 0, 52, 55, 60, 0, 64, 0, 60, 0, 64, 0, 67, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        180, 2.0, 0.25
    )
    
    # === GAME OVER ===
    MUSIC["game_over"] = make_music(
        [72, 0, 0, 0, 67, 0, 0, 0, 64, 0, 0, 0, 60, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [48, 0, 0, 0, 43, 0, 0, 0, 40, 0, 0, 0, 36, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        80, 3.0, 0.5
    )
    
    # === TITLE SCREEN ===
    MUSIC["title"] = make_music(
        [76, 76, 0, 76, 0, 72, 76, 0, 79, 0, 0, 0, 67, 0, 0, 0,
         72, 74, 76, 0, 79, 0, 76, 74, 72, 0, 69, 67, 0, 0, 0, 0],
        [48, 52, 55, 52, 48, 52, 55, 52, 43, 47, 50, 47, 48, 52, 55, 52],
        180, 4.0, 0.125
    )
    
    # === HURRY (Time running out) ===
    MUSIC["hurry"] = make_music(
        [76, 76, 0, 76, 0, 72, 76, 0, 79, 0, 0, 0, 67, 0, 0, 0],
        [48, 52, 55, 52, 48, 52, 55, 52],
        300, 2.0, 0.125
    )

current_music = None
music_channel = None

def play_music(name, loops=-1):
    global current_music, music_channel
    if name == current_music: return
    if music_channel: music_channel.stop()
    if name and name in MUSIC:
        music_channel = pygame.mixer.find_channel(True)
        if music_channel: music_channel.play(MUSIC[name], loops=loops)
    current_music = name

def stop_music():
    global current_music, music_channel
    if music_channel: music_channel.stop()
    current_music = None

def play_sfx(name):
    if name in SFX: SFX[name].play()

def get_level_music(world, stage, underwater=False):
    # Alternate between SMB1 and SMB3 style music
    smb3_worlds = [3, 5, 7]  # Worlds with SMB3-style music
    
    if stage == 4:
        return "castle3" if world in smb3_worlds else "castle"
    if underwater or (world, stage) in [(2,2), (7,2)]:
        return "underwater3" if world in smb3_worlds else "underwater"
    if (world, stage) in [(1,2), (4,2)]:
        return "underground3" if world in smb3_worlds else "underground"
    if stage == 3:  # Athletic levels
        return "athletic"
    return "overworld3" if world in smb3_worlds else "overworld"

# === SPRITE DRAWING ===
def draw_mario(surf, x, y, facing, frame, big=False, fire=False, ducking=False):
    h = 16 if not big else (16 if ducking else 32)
    if fire:
        hat, shirt = Pal.WHITE, Pal.MARIO_RED
    else:
        hat, shirt = Pal.MARIO_RED, Pal.MARIO_TAN
    skin, shoe = Pal.MARIO_TAN, Pal.MARIO_BROWN
    
    if big and not ducking:
        pygame.draw.rect(surf, hat, (x+4, y, 8, 4))
        pygame.draw.rect(surf, hat, (x+2, y+4, 12, 4))
        pygame.draw.rect(surf, skin, (x+2, y+8, 12, 6))
        pygame.draw.rect(surf, Pal.BLACK, (x+5, y+10, 2, 2))
        pygame.draw.rect(surf, shirt, (x+2, y+14, 12, 10))
        if frame % 3 == 0:
            pygame.draw.rect(surf, shoe, (x+2, y+24, 5, 8))
            pygame.draw.rect(surf, shoe, (x+9, y+24, 5, 8))
        elif frame % 3 == 1:
            pygame.draw.rect(surf, shoe, (x+1, y+24, 5, 8))
            pygame.draw.rect(surf, shoe, (x+10, y+24, 5, 8))
        else:
            pygame.draw.rect(surf, shoe, (x+3, y+24, 5, 8))
            pygame.draw.rect(surf, shoe, (x+8, y+24, 5, 8))
    elif big and ducking:
        pygame.draw.rect(surf, hat, (x+4, y, 8, 4))
        pygame.draw.rect(surf, hat, (x+2, y+4, 12, 4))
        pygame.draw.rect(surf, skin, (x+2, y+8, 12, 4))
        pygame.draw.rect(surf, shirt, (x+2, y+12, 12, 4))
    else:
        pygame.draw.rect(surf, hat, (x+4, y, 8, 3))
        pygame.draw.rect(surf, skin, (x+3, y+3, 10, 5))
        pygame.draw.rect(surf, Pal.BLACK, (x+5, y+5, 2, 2))
        pygame.draw.rect(surf, shirt, (x+2, y+8, 12, 4))
        if frame % 3 == 0:
            pygame.draw.rect(surf, shoe, (x+3, y+12, 4, 4))
            pygame.draw.rect(surf, shoe, (x+9, y+12, 4, 4))
        elif frame % 3 == 1:
            pygame.draw.rect(surf, shoe, (x+2, y+12, 4, 4))
            pygame.draw.rect(surf, shoe, (x+10, y+12, 4, 4))
        else:
            pygame.draw.rect(surf, shoe, (x+4, y+12, 4, 4))
            pygame.draw.rect(surf, shoe, (x+8, y+12, 4, 4))

def draw_goomba(surf, x, y, frame, squashed=False):
    if squashed:
        pygame.draw.rect(surf, Pal.GOOMBA, (x+2, y+12, 12, 4))
        return
    pygame.draw.ellipse(surf, Pal.GOOMBA, (x+2, y, 12, 10))
    pygame.draw.rect(surf, Pal.GOOMBA, (x+4, y+8, 8, 4))
    if frame % 2 == 0:
        pygame.draw.rect(surf, Pal.BLACK, (x+2, y+12, 5, 4))
        pygame.draw.rect(surf, Pal.BLACK, (x+9, y+12, 5, 4))
    else:
        pygame.draw.rect(surf, Pal.BLACK, (x+3, y+12, 5, 4))
        pygame.draw.rect(surf, Pal.BLACK, (x+8, y+12, 5, 4))
    pygame.draw.rect(surf, Pal.WHITE, (x+4, y+4, 3, 3))
    pygame.draw.rect(surf, Pal.WHITE, (x+9, y+4, 3, 3))
    pygame.draw.rect(surf, Pal.BLACK, (x+5, y+5, 2, 2))
    pygame.draw.rect(surf, Pal.BLACK, (x+10, y+5, 2, 2))

def draw_koopa(surf, x, y, frame, red=False, shell_only=False, winged=False):
    color = Pal.KOOPA_RED if red else Pal.KOOPA_GREEN
    if shell_only:
        pygame.draw.ellipse(surf, color, (x+2, y+4, 12, 12))
        pygame.draw.rect(surf, Pal.WHITE, (x+6, y+8, 4, 4))
        return
    pygame.draw.ellipse(surf, color, (x+2, y+8, 12, 14))
    pygame.draw.rect(surf, Pal.WHITE, (x+6, y+12, 4, 4))
    pygame.draw.ellipse(surf, Pal.MARIO_TAN, (x+3, y, 10, 10))
    pygame.draw.rect(surf, Pal.WHITE, (x+5, y+2, 3, 3))
    pygame.draw.rect(surf, Pal.BLACK, (x+6, y+3, 1, 2))
    if frame % 2 == 0:
        pygame.draw.rect(surf, Pal.MARIO_TAN, (x+2, y+20, 5, 4))
        pygame.draw.rect(surf, Pal.MARIO_TAN, (x+9, y+20, 5, 4))
    else:
        pygame.draw.rect(surf, Pal.MARIO_TAN, (x+3, y+20, 5, 4))
        pygame.draw.rect(surf, Pal.MARIO_TAN, (x+8, y+20, 5, 4))
    if winged:
        wy = y + 2 + (frame % 2) * 2
        pygame.draw.polygon(surf, Pal.WHITE, [(x-2,wy+4),(x+4,wy),(x+4,wy+6)])
        pygame.draw.polygon(surf, Pal.WHITE, [(x+18,wy+4),(x+12,wy),(x+12,wy+6)])

def draw_piranha(surf, x, y, height=16):
    pygame.draw.rect(surf, Pal.PIPE, (x+5, y+8, 6, height-8))
    pygame.draw.ellipse(surf, Pal.KOOPA_RED, (x+1, y, 14, 12))
    pygame.draw.rect(surf, Pal.WHITE, (x+3, y+4, 10, 3))
    pygame.draw.rect(surf, Pal.WHITE, (x+4, y+4, 2, 5))
    pygame.draw.rect(surf, Pal.WHITE, (x+10, y+4, 2, 5))

def draw_mushroom(surf, x, y, is_1up=False):
    color = Pal.PIPE if is_1up else Pal.MUSHROOM
    pygame.draw.ellipse(surf, color, (x+1, y, 14, 10))
    pygame.draw.rect(surf, Pal.WHITE, (x+5, y+2, 2, 4))
    pygame.draw.rect(surf, Pal.WHITE, (x+9, y+2, 2, 4))
    pygame.draw.rect(surf, Pal.WHITE, (x+4, y+8, 8, 8))

def draw_fire_flower(surf, x, y, frame):
    colors = [Pal.FIRE, Pal.MUSHROOM, Pal.WHITE]
    c = colors[frame % 3]
    pygame.draw.rect(surf, c, (x+4, y, 8, 4))
    pygame.draw.rect(surf, c, (x, y+4, 16, 4))
    pygame.draw.rect(surf, c, (x+4, y+8, 8, 4))
    pygame.draw.rect(surf, Pal.WHITE, (x+6, y+4, 4, 4))
    pygame.draw.rect(surf, Pal.PIPE, (x+6, y+12, 4, 4))

def draw_star(surf, x, y, frame):
    colors = [Pal.STAR, Pal.WHITE, Pal.FIRE]
    c = colors[frame % 3]
    pts = [(x+8,y),(x+10,y+6),(x+16,y+6),(x+11,y+10),(x+14,y+16),(x+8,y+12),(x+2,y+16),(x+5,y+10),(x,y+6),(x+6,y+6)]
    pygame.draw.polygon(surf, c, pts)

def draw_coin(surf, x, y, frame):
    widths = [8, 6, 2, 6]
    w = widths[frame % 4]
    pygame.draw.ellipse(surf, Pal.COIN, (x + 8 - w//2, y+2, w, 12))

def draw_brick(surf, x, y, underground=False):
    color = (100,100,100) if underground else Pal.BRICK
    dark = (60,60,60) if underground else Pal.BRICK_DARK
    pygame.draw.rect(surf, color, (x, y, 16, 16))
    pygame.draw.rect(surf, dark, (x, y+7, 16, 2))
    pygame.draw.rect(surf, dark, (x+7, y, 2, 16))

def draw_question(surf, x, y, frame, used=False):
    if used:
        pygame.draw.rect(surf, Pal.BRICK_DARK, (x, y, 16, 16))
        pygame.draw.rect(surf, Pal.BLACK, (x+2, y+2, 12, 12))
        return
    c = Pal.QUESTION if (frame//8)%2==0 else Pal.QUESTION_DARK
    pygame.draw.rect(surf, c, (x, y, 16, 16))
    pygame.draw.rect(surf, Pal.BLACK, (x+2, y+2, 12, 12))
    pygame.draw.rect(surf, Pal.WHITE, (x+5, y+4, 6, 5))
    pygame.draw.rect(surf, Pal.WHITE, (x+7, y+10, 2, 2))

def draw_ground(surf, x, y):
    pygame.draw.rect(surf, Pal.GROUND, (x, y, 16, 16))
    pygame.draw.rect(surf, Pal.GROUND_DARK, (x, y, 16, 4))
    pygame.draw.rect(surf, Pal.GROUND_DARK, (x+4, y+8, 2, 2))
    pygame.draw.rect(surf, Pal.GROUND_DARK, (x+10, y+12, 2, 2))

def draw_hard(surf, x, y):
    pygame.draw.rect(surf, Pal.CASTLE_GRAY, (x, y, 16, 16))
    pygame.draw.rect(surf, Pal.CASTLE_DARK, (x, y+8, 16, 2))
    pygame.draw.rect(surf, Pal.CASTLE_DARK, (x+8, y, 2, 16))

def draw_pipe_top(surf, x, y, left=True):
    pygame.draw.rect(surf, Pal.PIPE, (x, y, 16, 16))
    if left:
        pygame.draw.rect(surf, Pal.PIPE_LIGHT, (x, y, 4, 16))
    else:
        pygame.draw.rect(surf, Pal.PIPE_DARK, (x+12, y, 4, 16))

def draw_pipe_body(surf, x, y, left=True):
    pygame.draw.rect(surf, Pal.PIPE, (x+(2 if left else 0), y, 14, 16))
    if left:
        pygame.draw.rect(surf, Pal.PIPE_LIGHT, (x+2, y, 4, 16))
    else:
        pygame.draw.rect(surf, Pal.PIPE_DARK, (x+10, y, 4, 16))

def draw_flagpole(surf, x, y, flag_y=0):
    pygame.draw.rect(surf, Pal.CASTLE_GRAY, (x+7, y, 2, 160))
    pygame.draw.circle(surf, Pal.STAR, (x+8, y), 4)
    flag_top = y + 16 + int(flag_y)
    pygame.draw.polygon(surf, Pal.PIPE, [(x+8,flag_top),(x-8,flag_top+8),(x+8,flag_top+16)])

def draw_castle(surf, x, y):
    pygame.draw.rect(surf, Pal.CASTLE_GRAY, (x, y+32, 80, 48))
    for i in range(5):
        pygame.draw.rect(surf, Pal.CASTLE_GRAY, (x+i*16, y+16, 12, 16))
    pygame.draw.rect(surf, Pal.BLACK, (x+32, y+56, 16, 24))
    pygame.draw.rect(surf, Pal.BLACK, (x+8, y+48, 12, 12))
    pygame.draw.rect(surf, Pal.BLACK, (x+60, y+48, 12, 12))

def draw_cloud(surf, x, y):
    pygame.draw.ellipse(surf, Pal.WHITE, (x, y+8, 24, 16))
    pygame.draw.ellipse(surf, Pal.WHITE, (x+16, y, 24, 20))
    pygame.draw.ellipse(surf, Pal.WHITE, (x+32, y+8, 24, 16))

def draw_bush(surf, x, y):
    pygame.draw.ellipse(surf, Pal.PIPE, (x, y+8, 24, 16))
    pygame.draw.ellipse(surf, Pal.PIPE, (x+16, y, 24, 20))
    pygame.draw.ellipse(surf, Pal.PIPE, (x+32, y+8, 24, 16))

def draw_hill(surf, x, y):
    pygame.draw.polygon(surf, (0, 148, 0), [(x, y+48), (x+40, y), (x+80, y+48)])
    pygame.draw.ellipse(surf, (0, 148, 0), (x+20, y+32, 40, 20))

# === ENTITIES ===
class Entity:
    def __init__(self, x, y):
        self.x, self.y = float(x), float(y)
        self.vx, self.vy = 0.0, 0.0
        self.w, self.h = 16, 16
        self.alive = True
        self.on_ground = False
        self.facing = -1
        self.frame = 0
    
    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)
    
    def update(self, level): pass
    def draw(self, surf, cam): pass

class Goomba(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.vx = -Phys.GOOMBA_SPEED
        self.squash_timer = 0
    
    def update(self, level):
        if self.squash_timer > 0:
            self.squash_timer -= 1
            if self.squash_timer <= 0: self.alive = False
            return
        self.frame += 1
        self.vy = min(self.vy + Phys.GRAVITY, Phys.MAX_FALL)
        self.x += self.vx
        self.y += self.vy
        self.on_ground = False
        for tile in level.get_nearby_tiles(self.x, self.y):
            if tile.solid and self.rect.colliderect(tile.rect):
                if self.vy > 0 and self.y + self.h - self.vy <= tile.y:
                    self.y = tile.y - self.h
                    self.vy = 0
                    self.on_ground = True
                elif self.vx != 0:
                    self.vx = -self.vx
        if self.y > NES_H + 32: self.alive = False
    
    def stomp(self):
        self.squash_timer = 30
        play_sfx("stomp")
    
    def draw(self, surf, cam):
        draw_goomba(surf, int(self.x - cam), int(self.y), self.frame//8, self.squash_timer > 0)

class Koopa(Entity):
    def __init__(self, x, y, red=False, winged=False):
        super().__init__(x, y)
        self.h = 24
        self.red, self.winged = red, winged
        self.shell_only = False
        self.shell_moving = False
        self.vx = -Phys.KOOPA_SPEED
        self.shell_timer = 0
    
    def update(self, level):
        self.frame += 1
        if self.shell_only and not self.shell_moving:
            self.shell_timer += 1
            if self.shell_timer > 180:
                self.shell_only = False
                self.h = 24
                self.shell_timer = 0
            return
        if self.shell_moving:
            self.vx = Phys.SHELL_SPEED * self.facing
        elif not self.shell_only:
            self.vx = Phys.KOOPA_SPEED * self.facing
        if not self.winged or self.shell_only:
            self.vy = min(self.vy + Phys.GRAVITY, Phys.MAX_FALL)
        else:
            self.vy = math.sin(self.frame / 20.0) * 1.5
        self.x += self.vx
        self.y += self.vy
        self.on_ground = False
        for tile in level.get_nearby_tiles(self.x, self.y):
            if tile.solid and self.rect.colliderect(tile.rect):
                if self.vy > 0 and self.y + self.h - self.vy <= tile.y:
                    self.y = tile.y - self.h
                    self.vy = 0
                    self.on_ground = True
                elif self.shell_moving:
                    self.facing = -self.facing
                else:
                    self.facing = -self.facing
                    self.x += self.vx
        if self.red and not self.shell_only and self.on_ground:
            test_x = self.x + (self.w if self.facing > 0 else -4)
            has_floor = any(t.solid and t.rect.collidepoint(test_x, self.y + self.h + 4) for t in level.get_nearby_tiles(test_x, self.y + self.h))
            if not has_floor: self.facing = -self.facing
        if self.y > NES_H + 32: self.alive = False
    
    def stomp(self):
        if self.shell_only and not self.shell_moving:
            self.shell_moving = True
            play_sfx("kick")
        else:
            self.shell_only = True
            self.shell_moving = False
            self.h = 16
            self.winged = False
            self.y += 8
            play_sfx("stomp")
    
    def kick(self, direction):
        self.facing = direction
        self.shell_moving = True
        play_sfx("kick")
    
    def draw(self, surf, cam):
        draw_koopa(surf, int(self.x - cam), int(self.y), self.frame//8, self.red, self.shell_only, self.winged)

class PiranhaPlant(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.base_y = y
        self.timer = 0
        self.state = "hidden"
        self.offset = 0
    
    def update(self, level):
        self.timer += 1
        if self.state == "hidden":
            if self.timer > 60:
                self.state = "rising"
                self.timer = 0
        elif self.state == "rising":
            self.offset = min(self.offset + 0.5, 24)
            if self.offset >= 24:
                self.state = "waiting"
                self.timer = 0
        elif self.state == "waiting":
            if self.timer > 90:
                self.state = "lowering"
                self.timer = 0
        elif self.state == "lowering":
            self.offset = max(self.offset - 0.5, 0)
            if self.offset <= 0:
                self.state = "hidden"
                self.timer = 0
        self.y = self.base_y - self.offset
    
    def draw(self, surf, cam):
        if self.offset > 0:
            draw_piranha(surf, int(self.x - cam), int(self.y), int(self.offset))

class Fireball(Entity):
    def __init__(self, x, y, direction):
        super().__init__(x, y)
        self.w, self.h = 8, 8
        self.vx = 4 * direction
    
    def update(self, level):
        self.frame += 1
        self.vy = min(self.vy + Phys.GRAVITY, 3)
        self.x += self.vx
        self.y += self.vy
        for tile in level.get_nearby_tiles(self.x, self.y):
            if tile.solid and self.rect.colliderect(tile.rect):
                if self.vy > 0:
                    self.y = tile.y - self.h
                    self.vy = -3
                else:
                    self.alive = False
        if self.x < 0 or self.x > level.width * T or self.y > NES_H:
            self.alive = False
    
    def draw(self, surf, cam):
        colors = [Pal.FIRE, Pal.MUSHROOM, Pal.STAR]
        pygame.draw.circle(surf, colors[self.frame % 3], (int(self.x - cam + 4), int(self.y + 4)), 4)

class Mushroom(Entity):
    def __init__(self, x, y, is_1up=False):
        super().__init__(x, y)
        self.is_1up = is_1up
        self.vx = 1.0
        self.emerging = True
        self.emerge_y = y
    
    def update(self, level):
        if self.emerging:
            self.y -= 0.5
            if self.emerge_y - self.y >= 16: self.emerging = False
            return
        self.vy = min(self.vy + Phys.GRAVITY, Phys.MAX_FALL)
        self.x += self.vx
        self.y += self.vy
        for tile in level.get_nearby_tiles(self.x, self.y):
            if tile.solid and self.rect.colliderect(tile.rect):
                if self.vy > 0:
                    self.y = tile.y - self.h
                    self.vy = 0
                elif self.vx != 0:
                    self.vx = -self.vx
        if self.y > NES_H + 32: self.alive = False
    
    def draw(self, surf, cam):
        draw_mushroom(surf, int(self.x - cam), int(self.y), self.is_1up)

class FireFlower(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.emerging = True
        self.emerge_y = y
    
    def update(self, level):
        self.frame += 1
        if self.emerging:
            self.y -= 0.5
            if self.emerge_y - self.y >= 16: self.emerging = False
    
    def draw(self, surf, cam):
        draw_fire_flower(surf, int(self.x - cam), int(self.y), self.frame//4)

class Star(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.vx = 1.5
        self.emerging = True
        self.emerge_y = y
    
    def update(self, level):
        self.frame += 1
        if self.emerging:
            self.y -= 0.5
            if self.emerge_y - self.y >= 16: self.emerging = False
            return
        self.vy = min(self.vy + Phys.GRAVITY, Phys.MAX_FALL)
        self.x += self.vx
        self.y += self.vy
        for tile in level.get_nearby_tiles(self.x, self.y):
            if tile.solid and self.rect.colliderect(tile.rect):
                if self.vy > 0:
                    self.y = tile.y - self.h
                    self.vy = -5
                elif self.vx != 0:
                    self.vx = -self.vx
        if self.y > NES_H + 32: self.alive = False
    
    def draw(self, surf, cam):
        draw_star(surf, int(self.x - cam), int(self.y), self.frame//4)

class Coin(Entity):
    def __init__(self, x, y, from_block=False):
        super().__init__(x, y)
        self.from_block = from_block
        self.timer = 30 if from_block else 0
        if from_block: self.vy = -6
    
    def update(self, level):
        self.frame += 1
        if self.from_block:
            self.timer -= 1
            self.vy += 0.3
            self.y += self.vy
            if self.timer <= 0: self.alive = False
    
    def draw(self, surf, cam):
        draw_coin(surf, int(self.x - cam), int(self.y), self.frame//4)

class BrickParticle(Entity):
    def __init__(self, x, y, vx, vy):
        super().__init__(x, y)
        self.vx, self.vy = vx, vy
        self.w, self.h = 8, 8
    
    def update(self, level):
        self.vy += 0.25
        self.x += self.vx
        self.y += self.vy
        if self.y > NES_H + 32: self.alive = False
    
    def draw(self, surf, cam):
        pygame.draw.rect(surf, Pal.BRICK, (int(self.x - cam), int(self.y), 8, 8))

# === TILES ===
class Tile:
    def __init__(self, x, y, tile_type):
        self.x, self.y = x, y
        self.type = tile_type
        self.rect = pygame.Rect(x, y, T, T)
        self.solid = tile_type not in ["empty", "coin", "bg", "flag", "castle_end"]
        self.used = False
        self.bump_offset = 0
        self.contents = None
        self.coin_count = 0
    
    def bump(self, level, player):
        if self.bump_offset > 0: return
        if self.type == "brick":
            if self.contents and not self.used:
                play_sfx("bump")
                self.bump_offset = 4
                if self.contents == "multi_coin":
                    self.coin_count -= 1
                    level.items.append(Coin(self.x, self.y - 16, from_block=True))
                    level.coins += 1
                    play_sfx("coin")
                    if self.coin_count <= 0:
                        self.used = True
                        self.type = "used"
                else:
                    self.used = True
                    self.spawn_contents(level, player)
            elif player.big:
                play_sfx("break")
                self.type = "empty"
                self.solid = False
                for dx, dy in [(-1,-4),(1,-4),(-2,-2),(2,-2)]:
                    level.particles.append(BrickParticle(self.x+4, self.y+4, dx, dy))
            else:
                play_sfx("bump")
                self.bump_offset = 4
        elif self.type == "question" and not self.used:
            play_sfx("bump")
            self.bump_offset = 4
            self.used = True
            self.spawn_contents(level, player)
    
    def spawn_contents(self, level, player):
        if self.contents == "coin" or self.contents is None:
            level.items.append(Coin(self.x, self.y - 16, from_block=True))
            level.coins += 1
            play_sfx("coin")
        elif self.contents == "mushroom":
            if player.big:
                level.items.append(FireFlower(self.x, self.y))
            else:
                level.items.append(Mushroom(self.x, self.y))
            play_sfx("sprout")
        elif self.contents == "star":
            level.items.append(Star(self.x, self.y))
            play_sfx("sprout")
        elif self.contents == "1up":
            level.items.append(Mushroom(self.x, self.y, is_1up=True))
            play_sfx("sprout")
    
    def update(self):
        if self.bump_offset > 0: self.bump_offset -= 1
    
    def draw(self, surf, cam, frame, underground=False):
        x = int(self.x - cam)
        y = int(self.y - self.bump_offset)
        if self.type == "ground": draw_ground(surf, x, y)
        elif self.type == "brick": draw_brick(surf, x, y, underground)
        elif self.type == "question": draw_question(surf, x, y, frame, self.used)
        elif self.type == "used": draw_question(surf, x, y, frame, True)
        elif self.type == "hard": draw_hard(surf, x, y)
        elif self.type == "pipe_tl": draw_pipe_top(surf, x, y, True)
        elif self.type == "pipe_tr": draw_pipe_top(surf, x, y, False)
        elif self.type == "pipe_l": draw_pipe_body(surf, x, y, True)
        elif self.type == "pipe_r": draw_pipe_body(surf, x, y, False)
        elif self.type == "castle_block":
            pygame.draw.rect(surf, Pal.CASTLE_GRAY, (x, y, T, T))
            pygame.draw.rect(surf, Pal.CASTLE_DARK, (x, y, T, 2))
            pygame.draw.rect(surf, Pal.CASTLE_DARK, (x, y, 2, T))

# === PLAYER ===
class Player:
    def __init__(self, x, y):
        self.x, self.y = float(x), float(y)
        self.vx, self.vy = 0.0, 0.0
        self.w, self.h = 14, 16
        self.big = False
        self.fire = False
        self.star_power = 0
        self.facing = 1
        self.on_ground = False
        self.jumping = False
        self.jump_held = False
        self.jump_timer = 0
        self.ducking = False
        self.frame = 0
        self.anim_timer = 0
        self.dead = False
        self.death_timer = 0
        self.win = False
        self.win_timer = 0
        self.invincible = 0
        self.grow_timer = 0
        self.shrink_timer = 0
        self.fireballs = []
        self._fire_pressed = False
    
    @property
    def rect(self):
        h = 16 if not self.big or self.ducking else 32
        return pygame.Rect(int(self.x) + 1, int(self.y) + (32 - h if self.big else 0), self.w, h)
    
    def update(self, keys, level):
        if self.dead:
            self.death_timer += 1
            if self.death_timer < 30: return
            self.vy = min(self.vy + 0.3, 8)
            self.y += self.vy
            return
        if self.win:
            self.win_timer += 1
            return
        if self.grow_timer > 0:
            self.grow_timer -= 1
            return
        if self.shrink_timer > 0:
            self.shrink_timer -= 1
            return
        if self.invincible > 0: self.invincible -= 1
        if self.star_power > 0: self.star_power -= 1
        self.anim_timer += 1
        
        left = keys[pygame.K_LEFT] or keys[pygame.K_a]
        right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        run = keys[pygame.K_x] or keys[pygame.K_LSHIFT]
        jump = keys[pygame.K_z] or keys[pygame.K_SPACE]
        down = keys[pygame.K_DOWN] or keys[pygame.K_s]
        
        self.ducking = down and self.big and self.on_ground
        max_speed = Phys.RUN_MAX if run else Phys.WALK_MAX
        accel = Phys.RUN_ACCEL if run else Phys.WALK_ACCEL
        
        if right and not self.ducking:
            self.facing = 1
            if self.vx < 0:
                self.vx += Phys.SKID_DECEL
            else:
                self.vx = min(self.vx + accel, max_speed)
        elif left and not self.ducking:
            self.facing = -1
            if self.vx > 0:
                self.vx -= Phys.SKID_DECEL
            else:
                self.vx = max(self.vx - accel, -max_speed)
        else:
            if self.vx > 0: self.vx = max(0, self.vx - Phys.RELEASE_DECEL)
            elif self.vx < 0: self.vx = min(0, self.vx + Phys.RELEASE_DECEL)
        
        if jump and self.on_ground and not self.jumping:
            self.jumping = True
            self.jump_held = True
            self.jump_timer = 0
            speed = abs(self.vx)
            if speed < 1: self.vy = Phys.JUMP_VEL[0]
            elif speed < 2: self.vy = Phys.JUMP_VEL[1]
            else: self.vy = Phys.JUMP_VEL[2]
            play_sfx("jump_big" if self.big else "jump")
        if not jump: self.jump_held = False
        
        if self.jumping and self.jump_held and self.jump_timer < Phys.JUMP_FRAMES:
            self.jump_timer += 1
            gravity = Phys.GRAVITY_HOLDING
        elif self.vy < 0 and not self.jump_held:
            gravity = Phys.GRAVITY_FAST
        else:
            gravity = Phys.GRAVITY
        self.vy = min(self.vy + gravity, Phys.MAX_FALL)
        
        self.x += self.vx
        self.y += self.vy
        
        if not self.on_ground: self.frame = 2
        elif abs(self.vx) > 0.5:
            if self.anim_timer % 8 == 0: self.frame = (self.frame + 1) % 3
        else: self.frame = 0
        
        self.on_ground = False
        self.h = 16 if not self.big or self.ducking else 32
        
        for tile in level.get_nearby_tiles(self.x, self.y):
            if not tile.solid: continue
            rect = self.rect
            if not rect.colliderect(tile.rect): continue
            dx = (rect.centerx - tile.rect.centerx) / T
            dy = (rect.centery - tile.rect.centery) / T
            if abs(dx) > abs(dy):
                if self.vx > 0: self.x = tile.rect.left - self.w - 1
                else: self.x = tile.rect.right - 1
                self.vx = 0
            else:
                if self.vy > 0:
                    self.y = tile.rect.top - self.h
                    self.vy = 0
                    self.on_ground = True
                    self.jumping = False
                else:
                    self.y = tile.rect.bottom
                    self.vy = 0
                    tile.bump(level, self)
        
        for item in level.items[:]:
            if isinstance(item, Coin) and not item.from_block:
                if self.rect.colliderect(item.rect):
                    item.alive = False
                    level.coins += 1
                    level.score += 200
                    play_sfx("coin")
        
        if self.fire and run and len(self.fireballs) < 2:
            if keys[pygame.K_x] and not self._fire_pressed:
                self.fireballs.append(Fireball(self.x + (12 if self.facing > 0 else -8), self.y + (8 if self.big else 4), self.facing))
                play_sfx("fireball")
                self._fire_pressed = True
        if not keys[pygame.K_x]: self._fire_pressed = False
        
        for fb in self.fireballs[:]:
            fb.update(level)
            if not fb.alive: self.fireballs.remove(fb)
        
        if self.x < 0: self.x, self.vx = 0, 0
        if self.x < level.camera - 8: self.x = level.camera - 8
        if self.y > NES_H + 16: self.die()
    
    def die(self):
        if not self.dead:
            self.dead = True
            self.death_timer = 0
            self.vy = -8
            play_sfx("die")
            stop_music()
    
    def hurt(self):
        if self.invincible > 0 or self.star_power > 0: return
        if self.fire:
            self.fire = False
            self.invincible = 120
            self.shrink_timer = 45
        elif self.big:
            self.big = False
            self.invincible = 120
            self.shrink_timer = 45
        else:
            self.die()
    
    def power_up(self, item):
        if isinstance(item, Mushroom):
            if item.is_1up:
                play_sfx("1up")
                return "1up"
            elif not self.big:
                self.big = True
                self.grow_timer = 45
                play_sfx("powerup")
        elif isinstance(item, FireFlower):
            if not self.big: self.big = True
            self.fire = True
            self.grow_timer = 45
            play_sfx("powerup")
        elif isinstance(item, Star):
            self.star_power = 600
            play_sfx("powerup")
            play_music("star")
        return None
    
    def draw(self, surf, cam, frame):
        if self.dead and self.death_timer < 30: return
        if self.invincible > 0 and (self.invincible // 4) % 2 == 0: return
        if (self.grow_timer + self.shrink_timer) > 0 and ((self.grow_timer + self.shrink_timer) // 4) % 2 == 0: return
        x, y = int(self.x - cam), int(self.y)
        fire_display = self.fire
        if self.star_power > 0: fire_display = (frame // 4) % 2 == 0
        draw_mario(surf, x, y, self.facing, self.frame, self.big, fire_display, self.ducking)
        for fb in self.fireballs: fb.draw(surf, cam)

# === LEVEL ===
class Level:
    def __init__(self, world, stage, data):
        self.world, self.stage = world, stage
        self.width = len(data[0]) if data else 0
        self.tiles, self.enemies, self.items, self.particles = [], [], [], []
        self.camera = 0
        self.score, self.coins = 0, 0
        self.time = 400 if stage != 4 else 300
        self.underground = (world, stage) in [(1,2),(4,2)]
        self.underwater = (world, stage) in [(2,2),(7,2)]
        self.castle = stage == 4
        self.flagpole_x, self.castle_x, self.flag_y = 0, 0, 0
        self.parse_level(data)
    
    def parse_level(self, data):
        for row_idx, row in enumerate(data):
            for col_idx, char in enumerate(row):
                x, y = col_idx * T, row_idx * T
                tile = None
                if char == '#': tile = Tile(x, y, "ground")
                elif char == 'B': tile = Tile(x, y, "brick")
                elif char == '?':
                    tile = Tile(x, y, "question")
                    tile.contents = "coin"
                elif char == 'M':
                    tile = Tile(x, y, "question")
                    tile.contents = "mushroom"
                elif char == 'S':
                    tile = Tile(x, y, "question")
                    tile.contents = "star"
                elif char == '1':
                    tile = Tile(x, y, "brick")
                    tile.contents = "1up"
                elif char == 'C':
                    tile = Tile(x, y, "brick")
                    tile.contents = "multi_coin"
                    tile.coin_count = 10
                elif char == 'H': tile = Tile(x, y, "hard")
                elif char == '[': tile = Tile(x, y, "pipe_tl")
                elif char == ']': tile = Tile(x, y, "pipe_tr")
                elif char == '{': tile = Tile(x, y, "pipe_l")
                elif char == '}': tile = Tile(x, y, "pipe_r")
                elif char == 'o': self.items.append(Coin(x, y))
                elif char == 'g': self.enemies.append(Goomba(x, y))
                elif char == 'k': self.enemies.append(Koopa(x, y))
                elif char == 'r': self.enemies.append(Koopa(x, y, red=True))
                elif char == 'w': self.enemies.append(Koopa(x, y, winged=True))
                elif char == 'p': self.enemies.append(PiranhaPlant(x, y - 8))
                elif char == 'P': self.flagpole_x = x
                elif char == 'K': self.castle_x = x
                if tile: self.tiles.append(tile)
    
    def get_nearby_tiles(self, x, y):
        tx, ty = int(x // T), int(y // T)
        return [t for t in self.tiles if abs(t.x // T - tx) <= 2 and abs(t.y // T - ty) <= 3]
    
    def update(self, player):
        for tile in self.tiles: tile.update()
        for enemy in self.enemies[:]:
            enemy.update(self)
            if not enemy.alive:
                self.enemies.remove(enemy)
            elif player and not player.dead:
                if player.rect.colliderect(enemy.rect):
                    if player.star_power > 0:
                        enemy.alive = False
                        self.score += 100
                        play_sfx("kick")
                    elif isinstance(enemy, PiranhaPlant):
                        player.hurt()
                    elif player.vy > 0 and player.rect.bottom < enemy.rect.centery + 4:
                        enemy.stomp()
                        player.vy = -4
                        self.score += 100
                    elif isinstance(enemy, Koopa) and enemy.shell_only and not enemy.shell_moving:
                        enemy.kick(1 if player.x < enemy.x else -1)
                        self.score += 100
                    else:
                        player.hurt()
        for item in self.items[:]:
            item.update(self)
            if not item.alive:
                self.items.remove(item)
            elif player and not player.dead and not getattr(item, 'from_block', False):
                if player.rect.colliderect(item.rect):
                    result = player.power_up(item)
                    if result == "1up": pass
                    self.score += 1000
                    item.alive = False
        for p in self.particles[:]:
            p.update(self)
            if not p.alive: self.particles.remove(p)
        if player and not player.dead:
            target = player.x - NES_W // 3
            self.camera = max(self.camera, min(target, self.width * T - NES_W))
            self.camera = max(0, self.camera)
        if player:
            for fb in player.fireballs[:]:
                for enemy in self.enemies:
                    if fb.rect.colliderect(enemy.rect) and not isinstance(enemy, PiranhaPlant):
                        enemy.alive = False
                        fb.alive = False
                        self.score += 100
                        play_sfx("kick")
                        break
    
    def draw(self, surf, frame):
        if self.underground or self.castle: surf.fill(Pal.UNDERGROUND)
        elif self.underwater: surf.fill(Pal.UNDERWATER)
        else:
            surf.fill(Pal.SKY)
            for i in range(10):
                cx = (i * 180 - int(self.camera * 0.3)) % (NES_W + 200) - 50
                draw_cloud(surf, cx, 30 + (i % 3) * 20)
            for i in range(5):
                hx = (i * 300 - int(self.camera * 0.5)) % (NES_W + 400) - 100
                draw_hill(surf, hx, NES_H - 80)
            for i in range(8):
                bx = (i * 200 - int(self.camera * 0.7)) % (NES_W + 300) - 50
                draw_bush(surf, bx, NES_H - 48)
        for tile in self.tiles:
            if -T <= tile.x - self.camera <= NES_W + T:
                tile.draw(surf, self.camera, frame, self.underground)
        if self.flagpole_x > 0: draw_flagpole(surf, int(self.flagpole_x - self.camera), NES_H - 176, self.flag_y)
        if self.castle_x > 0: draw_castle(surf, int(self.castle_x - self.camera), NES_H - 128)
        for item in self.items: item.draw(surf, self.camera)
        for enemy in self.enemies: enemy.draw(surf, self.camera)
        for p in self.particles: p.draw(surf, self.camera)

# === HUD ===
def draw_hud(surf, score, coins, world, stage, time, lives):
    font = pygame.font.Font(None, 16)
    surf.blit(font.render("MARIO", True, Pal.WHITE), (16, 8))
    surf.blit(font.render(f"{score:06d}", True, Pal.WHITE), (16, 18))
    draw_coin(surf, 80, 14, pygame.time.get_ticks() // 100)
    surf.blit(font.render(f"x{coins:02d}", True, Pal.WHITE), (96, 18))
    surf.blit(font.render("WORLD", True, Pal.WHITE), (140, 8))
    surf.blit(font.render(f" {world}-{stage}", True, Pal.WHITE), (140, 18))
    surf.blit(font.render("TIME", True, Pal.WHITE), (200, 8))
    surf.blit(font.render(f" {int(max(0, time)):03d}", True, Pal.WHITE), (200, 18))

# === LEVEL DATA (ALL 32 LEVELS WITH PROPER PIPE HEIGHTS) ===
LEVEL_DATA = {}

# 1-1: Classic first level with SHORT 2-tile pipes Mario can jump over
LEVEL_DATA[(1,1)] = [
"                                                                                                                                                                                                              ",
"                                                                                                                                                                                                              ",
"                                                                                                                                                                                                              ",
"                                                                                                                                                                                                              ",
"                    ?                                                                                                                                                                                         ",
"                                                                                                                                                                                                              ",
"                                                                                                                              BB?B                                                                            ",
"                                                                                                                                                                                                              ",
"            ?B?M?B?                        ?  ?  ?                       ?              B  B               ?B?                               HH                                                        P    K ",
"                                                                                                                           HHH                HHH                                                             ",
"                                                                                                       HHHH                       HHHH               HHHH              HHHH                                   ",
"                                   []              []            []            []     HHHHH         []HHHHH          []  HHHHH    []  []    HHHHH          []                              [][]               ",
"                       g  g        {}    g         {}    g  g    {}     g      {}    HHHHHH         {}HHHHHH         {} HHHHHH    {}  {}   HHHHHH  g   g   {}    g    g    g     g         {}{}    g          ",
"######################################################################################################################################################################################################################################################################",
"######################################################################################################################################################################################################################################################################",
]

# 1-2: Underground with short 2-tile pipes
LEVEL_DATA[(1,2)] = [
"BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
"B                                                                                                                                                                                                            B",
"B                                                                                                                                                                                                            B",
"B                                                                                                                                                                                                            B",
"B                                                                                                                                                                                                            B",
"B                   ?                                                                                                                                                                                        B",
"B                                                                                          BBBBB                                                                                                             B",
"B                                                                                                                                                                                                            B",
"B                     BBMBB                       BB?BBBB                                         B     B                  BB?BB                                                P    K                        B",
"B                                                                                                B       B        []                                      []                                                 B",
"B                                                                                               B         B       {}          g  g                        {}                                                 B",
"B            []                []                 []       []            []        g   g       BBBBBBBBBBBBB      []                        []     g  g   []                                                 B",
"B    g       {}    g           {}      g     g    {}       {}    g       {}                                      {}                        {}            {}                                                  B",
"BBBBBBBBBBBBBBBBBBBBB  BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
"BBBBBBBBBBBBBBBBBBBBB  BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
]

# 1-3: Athletic/Sky level
LEVEL_DATA[(1,3)] = [
"                                                                                                                                                                                                ",
"                                                                                                                                                                                                ",
"                                                                                                                                                                                                ",
"                                                                                                                                                                                                ",
"                                                         ooo                                                                  ooo                                                               ",
"                                               HHH                  HHH         HHH                                 HHH                                                                         ",
"                                                                                                                                    HH                                                          ",
"                   ooo         HHH   HHH                                               HHH       HH                     ooo              HHH                                                    ",
"        HHH                                                               HHH                                 HHH                                                                               ",
"                                                   r                                         r                                         r                         HHH          P    K           ",
"     g       g          HH              HH                    HH               HH                    HH               HH                        HH                                              ",
"                                                                                                                                                                                                ",
"                                                                                                                                                                                                ",
"#########################################################################################################################################################################################",
"#########################################################################################################################################################################################",
]

# 1-4: Castle
LEVEL_DATA[(1,4)] = [
"HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH",
"H                                                                                                                                              H",
"H                                                                                                                                              H",
"H                                              HHHHHH                                                                                          H",
"H                                                                                                                                              H",
"H                                                                      HHHHHH                                                                  H",
"H              HHHHHH                                                                                                                          H",
"H                                        HHH         HHH                              HHHH                                                      H",
"H                            HHH                                HHH                              K                                              H",
"H     HHH           HHH                                                      HHH                                                               H",
"H                                                                                          HH                                                  H",
"H                                                                                                                                              H",
"H                                                                                                                                              H",
"HHHHHHHHHH   HHHHH   HHHHHHHHHH   HHHHHHHHHHHHHHHHHH   HHHHHHH   HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH",
"HHHHHHHHHH   HHHHH   HHHHHHHHHH   HHHHHHHHHHHHHHHHHH   HHHHHHH   HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH",
]

# Generate remaining levels (2-1 through 8-4) with SHORT 2-tile pipes
def generate_level(world, stage):
    width = 200 + world * 15 + stage * 8
    rows = [" " * width for _ in range(15)]
    
    if stage == 4:  # Castle
        rows[0] = "H" * width
        rows[13] = "H" * width
        rows[14] = "H" * width
        for i in range(1, 13):
            rows[i] = "H" + " " * (width - 2) + "H"
        for x in range(20, width - 40, 25):
            for i in range(5):
                if x + i < width - 1:
                    rows[7] = rows[7][:x+i] + "H" + rows[7][x+i+1:]
        for x in range(30, width - 50, 40):
            rows[13] = rows[13][:x] + "   " + rows[13][x+3:]
            rows[14] = rows[14][:x] + "   " + rows[14][x+3:]
        rows[8] = rows[8][:width-15] + "K" + rows[8][width-14:]
    elif stage == 2 and world % 2 == 0:  # Underground
        rows[0] = "B" * width
        rows[13] = "B" * width
        rows[14] = "B" * width
        for i in range(1, 13):
            rows[i] = "B" + " " * (width - 2) + "B"
        for x in range(15, width - 30, 22):
            rows[8] = rows[8][:x] + "BB?BB" + rows[8][x+5:]
        # SHORT pipes (2 tiles) - Mario can easily jump over
        for x in range(30, width - 45, 35):
            rows[11] = rows[11][:x] + "[]" + rows[11][x+2:]
            rows[12] = rows[12][:x] + "{}" + rows[12][x+2:]
        for x in range(20, width - 30, 28):
            rows[12] = rows[12][:x] + "g" + rows[12][x+1:]
        rows[8] = rows[8][:width-14] + "P    K" + rows[8][width-8:]
    elif (world, stage) in [(2,2), (7,2)]:  # Underwater
        rows[13] = "#" * width
        rows[14] = "#" * width
        for x in range(18, width - 30, 28):
            for i in range(5):
                if x + i < width:
                    rows[9] = rows[9][:x+i] + "H" + rows[9][x+i+1:]
        for x in range(22, width - 40, 22):
            rows[4] = rows[4][:x] + "ooo" + rows[4][x+3:]
        rows[8] = rows[8][:width-14] + "P    K" + rows[8][width-8:]
    elif stage == 3:  # Athletic
        rows[13] = "#" * width
        rows[14] = "#" * width
        for x in range(15, width - 35, 18):
            for i in range(3 + x % 2):
                if x + i < width:
                    rows[9 - (x % 3)] = rows[9 - (x % 3)][:x+i] + "H" + rows[9 - (x % 3)][x+i+1:]
        for x in range(25, width - 40, 25):
            rows[5] = rows[5][:x] + "ooo" + rows[5][x+3:]
        for x in range(30, width - 50, 30):
            enemy = "r" if x % 2 == 0 else "w"
            rows[9] = rows[9][:x] + enemy + rows[9][x+1:]
        rows[8] = rows[8][:width-14] + "P    K" + rows[8][width-8:]
    else:  # Overworld
        rows[13] = "#" * width
        rows[14] = "#" * width
        for x in range(18, width - 40, 28):
            rows[8] = rows[8][:x] + "?B?M?" + rows[8][x+5:]
        # SHORT pipes (2 tiles high) - Mario can easily jump over
        for x in range(35, width - 55, 40):
            rows[11] = rows[11][:x] + "[]" + rows[11][x+2:]
            rows[12] = rows[12][:x] + "{}" + rows[12][x+2:]
        # Stairs at end
        for i in range(8):
            for j in range(i + 1):
                if width - 35 + i < width and 12 - j >= 0:
                    rows[12-j] = rows[12-j][:width-35+i] + "H" + rows[12-j][width-34+i:]
        # Enemies
        for x in range(28, width - 45, 22):
            enemy = "g" if x % 2 == 0 else "k"
            rows[12] = rows[12][:x] + enemy + rows[12][x+1:]
        rows[8] = rows[8][:width-14] + "P    K" + rows[8][width-8:]
    
    return rows

# Generate all remaining levels
for w in range(1, 9):
    for s in range(1, 5):
        if (w, s) not in LEVEL_DATA:
            LEVEL_DATA[(w, s)] = generate_level(w, s)

# === GAME STATES ===
class GameState:
    TITLE = 0
    PLAYING = 1
    DYING = 2
    LEVEL_COMPLETE = 3
    GAME_OVER = 4
    PAUSED = 5

# === MAIN GAME ===
class Game:
    def __init__(self):
        self.state = GameState.TITLE
        self.world, self.stage = 1, 1
        self.lives = 3
        self.score, self.coins = 0, 0
        self.level, self.player = None, None
        self.frame, self.timer = 0, 0
        self.title_blink = 0
        self._pause_pressed = False
        self.hurry_played = False
    
    def start_level(self):
        data = LEVEL_DATA.get((self.world, self.stage), LEVEL_DATA[(1, 1)])
        self.level = Level(self.world, self.stage, data)
        self.player = Player(32, NES_H - 64)
        self.state = GameState.PLAYING
        self.hurry_played = False
        play_music(get_level_music(self.world, self.stage, self.level.underwater))
    
    def update(self):
        self.frame += 1
        keys = pygame.key.get_pressed()
        
        if self.state == GameState.TITLE:
            self.title_blink += 1
            if keys[pygame.K_RETURN] or keys[pygame.K_SPACE] or keys[pygame.K_z]:
                self.start_level()
        
        elif self.state == GameState.PLAYING:
            self.player.update(keys, self.level)
            self.level.update(self.player)
            self.score += self.level.score
            self.level.score = 0
            self.coins += self.level.coins
            self.level.coins = 0
            if self.coins >= 100:
                self.coins -= 100
                self.lives += 1
                play_sfx("1up")
            self.level.time -= 1 / 60.0
            if self.level.time <= 0:
                self.player.die()
            elif self.level.time <= 100 and not self.hurry_played:
                play_sfx("warning")
                self.hurry_played = True
                if self.player.star_power <= 0:
                    play_music("hurry")
            if self.level.flagpole_x > 0 and self.player.x >= self.level.flagpole_x - 8 and not self.player.win:
                self.player.win = True
                self.state = GameState.LEVEL_COMPLETE
                play_music("level_complete", loops=0)
                self.timer = 0
            if self.level.castle and self.level.castle_x > 0 and self.player.x >= self.level.castle_x - 8 and not self.player.win:
                self.player.win = True
                self.state = GameState.LEVEL_COMPLETE
                play_music("castle_complete", loops=0)
                self.timer = 0
            if self.player.dead and self.player.y > NES_H + 32:
                self.state = GameState.DYING
                self.timer = 0
            if keys[pygame.K_RETURN] or keys[pygame.K_ESCAPE]:
                if not self._pause_pressed:
                    self.state = GameState.PAUSED
                    self._pause_pressed = True
            else:
                self._pause_pressed = False
        
        elif self.state == GameState.DYING:
            self.timer += 1
            if self.timer > 120:
                self.lives -= 1
                if self.lives <= 0:
                    self.state = GameState.GAME_OVER
                    play_music("game_over", loops=0)
                    self.timer = 0
                else:
                    self.start_level()
        
        elif self.state == GameState.LEVEL_COMPLETE:
            self.timer += 1
            if self.level.flagpole_x > 0:
                self.level.flag_y = min(self.level.flag_y + 2, 128)
            if self.timer > 60 and self.level.time > 0:
                self.level.time -= 2
                self.score += 100
            if self.timer > 180 and self.level.time <= 0:
                self.stage += 1
                if self.stage > 4:
                    self.stage = 1
                    self.world += 1
                    if self.world > 8:
                        self.state = GameState.TITLE
                        self.world, self.stage = 1, 1
                        return
                self.start_level()
        
        elif self.state == GameState.GAME_OVER:
            self.timer += 1
            if self.timer > 300:
                self.state = GameState.TITLE
                self.lives = 3
                self.score, self.coins = 0, 0
                self.world, self.stage = 1, 1
        
        elif self.state == GameState.PAUSED:
            if keys[pygame.K_RETURN] or keys[pygame.K_ESCAPE]:
                if not self._pause_pressed:
                    self.state = GameState.PLAYING
                    self._pause_pressed = True
            else:
                self._pause_pressed = False
    
    def draw(self):
        nes_surface.fill(Pal.SKY)
        
        if self.state == GameState.TITLE:
            nes_surface.fill(Pal.SKY)
            font_big = pygame.font.Font(None, 24)
            font_small = pygame.font.Font(None, 16)
            title = font_big.render("SUPER MARIO BROS.", True, Pal.WHITE)
            nes_surface.blit(title, (NES_W//2 - title.get_width()//2, 50))
            draw_mario(nes_surface, NES_W//2 - 8, 90, 1, self.frame//8, True, False, False)
            if (self.title_blink // 30) % 2 == 0:
                start = font_small.render("PRESS ENTER TO START", True, Pal.WHITE)
                nes_surface.blit(start, (NES_W//2 - start.get_width()//2, 150))
            copy = font_small.render("Cat's Ultra Mario 2D Bros!", True, Pal.WHITE)
            nes_surface.blit(copy, (NES_W//2 - copy.get_width()//2, 190))
            copy2 = font_small.render("Team Flames 2025", True, Pal.WHITE)
            nes_surface.blit(copy2, (NES_W//2 - copy2.get_width()//2, 205))
        
        elif self.state in [GameState.PLAYING, GameState.DYING, GameState.LEVEL_COMPLETE, GameState.PAUSED]:
            self.level.draw(nes_surface, self.frame)
            self.player.draw(nes_surface, self.level.camera, self.frame)
            draw_hud(nes_surface, self.score, self.coins, self.world, self.stage, self.level.time, self.lives)
            if self.state == GameState.PAUSED:
                font = pygame.font.Font(None, 24)
                pause = font.render("PAUSED", True, Pal.WHITE)
                nes_surface.blit(pause, (NES_W//2 - pause.get_width()//2, NES_H//2))
        
        elif self.state == GameState.GAME_OVER:
            nes_surface.fill(Pal.BLACK)
            font = pygame.font.Font(None, 24)
            go = font.render("GAME OVER", True, Pal.WHITE)
            nes_surface.blit(go, (NES_W//2 - go.get_width()//2, NES_H//2))
        
        pygame.transform.scale(nes_surface, (W, H), screen)
        pygame.display.flip()
    
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            self.update()
            self.draw()
            clock.tick(FPS)
        pygame.quit()

# === BOOT ===
if __name__ == "__main__":
    print("Cat's Ultra Mario 2D Bros! v1.1")
    print("Controls: Arrows/WASD=Move, Z/Space=Jump, X/Shift=Run")
    print("Loading sounds...", end=" ", flush=True)
    init_sounds()
    print("OK")
    print("Loading music...", end=" ", flush=True)
    init_music()
    print("OK")
    Game().run()
