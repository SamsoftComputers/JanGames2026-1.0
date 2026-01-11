#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║              CAT'S ULTRA!PONG HDR 0.1 - Team Flames / Samsoft                 ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  Dynamic Sound Engine • No External Files • Retro Arcade Style                ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import math
import random
import array
from dataclasses import dataclass
from typing import List, Optional, Tuple

import pygame

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════════════════════
LOGICAL_W, LOGICAL_H = 800, 600
FPS = 60
FIXED_DT = 1.0 / FPS

PADDLE_W = 16
PADDLE_H = 96
PLAYER_SPEED = 360.0
AI_SPEED = PLAYER_SPEED * 0.85
BALL_SIZE = 16

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
HIGHLIGHT_GRAY = (192, 192, 192)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)

# ═══════════════════════════════════════════════════════════════════════════════
# DYNAMIC SOUND ENGINE
# ═══════════════════════════════════════════════════════════════════════════════
class SoundEngine:
    """
    Dynamic sound synthesis engine - generates all sounds mathematically.
    No external files needed. Supports multiple waveforms and effects.
    """
    
    SAMPLE_RATE = 44100
    
    def __init__(self):
        self.enabled = False
        self.cache = {}
        
        try:
            pygame.mixer.init(frequency=self.SAMPLE_RATE, size=-16, channels=2, buffer=512)
            self.enabled = True
            self._init_mixer_info()
        except Exception as e:
            print(f"Sound disabled: {e}")
    
    def _init_mixer_info(self):
        """Get actual mixer settings"""
        init = pygame.mixer.get_init()
        if init:
            self.SAMPLE_RATE, _, self.channels = init
        else:
            self.channels = 2
    
    # ═══════════════════════════════════════════════════════════════════════════
    # WAVEFORM GENERATORS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def sine_wave(self, freq: float, duration: float, volume: float = 0.3) -> List[float]:
        """Generate pure sine wave"""
        samples = []
        num_samples = int(self.SAMPLE_RATE * duration)
        for i in range(num_samples):
            t = i / self.SAMPLE_RATE
            samples.append(math.sin(2 * math.pi * freq * t) * volume)
        return samples
    
    def square_wave(self, freq: float, duration: float, duty: float = 0.5, volume: float = 0.3) -> List[float]:
        """Generate square wave with variable duty cycle"""
        samples = []
        num_samples = int(self.SAMPLE_RATE * duration)
        period = self.SAMPLE_RATE / max(1, freq)
        for i in range(num_samples):
            t = (i % period) / period
            samples.append(volume if t < duty else -volume)
        return samples
    
    def triangle_wave(self, freq: float, duration: float, volume: float = 0.3) -> List[float]:
        """Generate triangle wave"""
        samples = []
        num_samples = int(self.SAMPLE_RATE * duration)
        period = self.SAMPLE_RATE / max(1, freq)
        for i in range(num_samples):
            t = (i % period) / period
            if t < 0.5:
                samples.append((4 * t - 1) * volume)
            else:
                samples.append((3 - 4 * t) * volume)
        return samples
    
    def sawtooth_wave(self, freq: float, duration: float, volume: float = 0.3) -> List[float]:
        """Generate sawtooth wave"""
        samples = []
        num_samples = int(self.SAMPLE_RATE * duration)
        period = self.SAMPLE_RATE / max(1, freq)
        for i in range(num_samples):
            t = (i % period) / period
            samples.append((2 * t - 1) * volume)
        return samples
    
    def noise(self, duration: float, volume: float = 0.3) -> List[float]:
        """Generate white noise"""
        samples = []
        num_samples = int(self.SAMPLE_RATE * duration)
        for _ in range(num_samples):
            samples.append(random.uniform(-volume, volume))
        return samples
    
    # ═══════════════════════════════════════════════════════════════════════════
    # EFFECTS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def apply_envelope(self, samples: List[float], attack: float = 0.01, 
                       decay: float = 0.1, sustain: float = 0.7, 
                       release: float = 0.1) -> List[float]:
        """Apply ADSR envelope to samples"""
        n = len(samples)
        a_n = int(attack * self.SAMPLE_RATE)
        d_n = int(decay * self.SAMPLE_RATE)
        r_n = int(release * self.SAMPLE_RATE)
        
        result = []
        for i, s in enumerate(samples):
            if i < a_n:
                env = i / max(1, a_n)
            elif i < a_n + d_n:
                env = 1.0 - (1.0 - sustain) * ((i - a_n) / max(1, d_n))
            elif i > n - r_n:
                env = sustain * ((n - i) / max(1, r_n))
            else:
                env = sustain
            result.append(s * env)
        return result
    
    def apply_pitch_bend(self, samples: List[float], start_freq: float, 
                         end_freq: float, volume: float = 0.3) -> List[float]:
        """Apply pitch bend effect"""
        n = len(samples)
        result = []
        for i in range(n):
            t = i / max(1, n)
            freq = start_freq + (end_freq - start_freq) * t
            phase = i / self.SAMPLE_RATE
            result.append(math.sin(2 * math.pi * freq * phase) * volume)
        return result
    
    def apply_vibrato(self, samples: List[float], rate: float = 5.0, 
                      depth: float = 0.02) -> List[float]:
        """Apply vibrato effect"""
        result = []
        for i, s in enumerate(samples):
            t = i / self.SAMPLE_RATE
            mod = 1.0 + depth * math.sin(2 * math.pi * rate * t)
            result.append(s * mod)
        return result
    
    def mix(self, *sample_lists: List[float]) -> List[float]:
        """Mix multiple sample lists together"""
        if not sample_lists:
            return []
        
        max_len = max(len(s) for s in sample_lists)
        result = [0.0] * max_len
        
        for samples in sample_lists:
            for i, s in enumerate(samples):
                result[i] += s / len(sample_lists)
        
        return result
    
    def concat(self, *sample_lists: List[float]) -> List[float]:
        """Concatenate sample lists"""
        result = []
        for samples in sample_lists:
            result.extend(samples)
        return result
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SOUND CREATION
    # ═══════════════════════════════════════════════════════════════════════════
    
    def samples_to_sound(self, samples: List[float]) -> Optional[pygame.mixer.Sound]:
        """Convert float samples to pygame Sound"""
        if not self.enabled or not samples:
            return None
        
        # Convert to 16-bit integers
        int_samples = [int(max(-32767, min(32767, s * 32767))) for s in samples]
        
        # Make stereo if needed
        if self.channels >= 2:
            stereo = []
            for s in int_samples:
                stereo.extend([s, s])
            int_samples = stereo
        
        return pygame.mixer.Sound(buffer=array.array('h', int_samples))
    
    def generate_beep(self, freq: float, duration_ms: int, 
                      volume: float = 0.3, wave: str = 'square') -> Optional[pygame.mixer.Sound]:
        """Generate a simple beep sound"""
        duration = duration_ms / 1000.0
        
        if wave == 'square':
            samples = self.square_wave(freq, duration, 0.5, volume)
        elif wave == 'sine':
            samples = self.sine_wave(freq, duration, volume)
        elif wave == 'triangle':
            samples = self.triangle_wave(freq, duration, volume)
        elif wave == 'sawtooth':
            samples = self.sawtooth_wave(freq, duration, volume)
        else:
            samples = self.square_wave(freq, duration, 0.5, volume)
        
        samples = self.apply_envelope(samples, 0.005, 0.02, 0.8, 0.05)
        return self.samples_to_sound(samples)
    
    def generate_arpeggio(self, notes: List[float], note_dur_ms: int,
                          volume: float = 0.3, wave: str = 'square') -> Optional[pygame.mixer.Sound]:
        """Generate arpeggio from note list"""
        all_samples = []
        duration = note_dur_ms / 1000.0
        
        for freq in notes:
            if wave == 'square':
                samples = self.square_wave(freq, duration, 0.5, volume)
            elif wave == 'sine':
                samples = self.sine_wave(freq, duration, volume)
            elif wave == 'triangle':
                samples = self.triangle_wave(freq, duration, volume)
            else:
                samples = self.square_wave(freq, duration, 0.5, volume)
            
            samples = self.apply_envelope(samples, 0.005, 0.02, 0.8, 0.1)
            all_samples.extend(samples)
        
        return self.samples_to_sound(all_samples)
    
    def generate_sweep(self, start_freq: float, end_freq: float, 
                       duration_ms: int, volume: float = 0.3) -> Optional[pygame.mixer.Sound]:
        """Generate frequency sweep"""
        duration = duration_ms / 1000.0
        num_samples = int(self.SAMPLE_RATE * duration)
        
        samples = []
        for i in range(num_samples):
            t = i / num_samples
            freq = start_freq + (end_freq - start_freq) * t
            phase = 2 * math.pi * freq * (i / self.SAMPLE_RATE)
            samples.append(math.sin(phase) * volume)
        
        samples = self.apply_envelope(samples, 0.01, 0.05, 0.7, 0.1)
        return self.samples_to_sound(samples)
    
    def generate_explosion(self, duration_ms: int, volume: float = 0.4) -> Optional[pygame.mixer.Sound]:
        """Generate explosion/impact sound"""
        duration = duration_ms / 1000.0
        
        # Noise burst with pitch-down
        noise_samples = self.noise(duration, volume)
        
        # Low frequency thump
        thump = self.sine_wave(60, duration * 0.5, volume * 0.8)
        
        # Mix and envelope
        samples = self.mix(noise_samples[:len(thump)], thump) + noise_samples[len(thump):]
        samples = self.apply_envelope(samples, 0.001, 0.1, 0.3, 0.3)
        
        return self.samples_to_sound(samples)
    
    def generate_powerup(self, volume: float = 0.3) -> Optional[pygame.mixer.Sound]:
        """Generate power-up sound"""
        notes = [523, 659, 784, 1047]  # C5, E5, G5, C6
        all_samples = []
        
        for i, freq in enumerate(notes):
            duration = 0.08
            samples = self.triangle_wave(freq, duration, volume)
            samples = self.apply_envelope(samples, 0.01, 0.02, 0.9, 0.02)
            all_samples.extend(samples)
        
        return self.samples_to_sound(all_samples)
    
    def generate_hit(self, pitch: float = 1.0, volume: float = 0.3) -> Optional[pygame.mixer.Sound]:
        """Generate dynamic hit sound based on pitch multiplier"""
        base_freq = 440 * pitch
        
        # Blend of square and noise
        square = self.square_wave(base_freq, 0.05, 0.25, volume)
        noise_hit = self.noise(0.02, volume * 0.3)
        
        samples = noise_hit + square
        samples = self.apply_envelope(samples, 0.001, 0.02, 0.6, 0.03)
        
        return self.samples_to_sound(samples)
    
    def generate_wall_bounce(self, y_pos: float, max_y: float, 
                             volume: float = 0.25) -> Optional[pygame.mixer.Sound]:
        """Generate wall bounce with pitch based on Y position"""
        # Higher pitch at top, lower at bottom
        pitch_factor = 0.5 + (1.0 - y_pos / max_y) * 1.0
        freq = 300 * pitch_factor
        
        samples = self.triangle_wave(freq, 0.04, volume)
        samples = self.apply_envelope(samples, 0.001, 0.01, 0.7, 0.02)
        
        return self.samples_to_sound(samples)
    
    def generate_paddle_hit(self, ball_speed: float, max_speed: float,
                            hit_offset: float, volume: float = 0.3) -> Optional[pygame.mixer.Sound]:
        """Generate paddle hit with dynamic pitch/tone based on game state"""
        # Base frequency increases with ball speed
        speed_factor = ball_speed / max_speed
        base_freq = 400 + speed_factor * 400
        
        # Pitch variation based on where ball hits paddle
        pitch_mod = 1.0 + hit_offset * 0.3
        freq = base_freq * pitch_mod
        
        # Blend waveforms
        square = self.square_wave(freq, 0.03, 0.25, volume * 0.7)
        tri = self.triangle_wave(freq * 2, 0.02, volume * 0.3)
        
        samples = self.mix(square, tri[:len(square)])
        samples = self.apply_envelope(samples, 0.001, 0.01, 0.8, 0.02)
        
        return self.samples_to_sound(samples)
    
    def generate_score(self, scorer: str, volume: float = 0.3) -> Optional[pygame.mixer.Sound]:
        """Generate score sound - different for player vs AI"""
        if scorer == 'player':
            # Triumphant ascending arpeggio
            notes = [523, 659, 784, 1047]
            all_samples = []
            for freq in notes:
                samples = self.square_wave(freq, 0.1, 0.25, volume)
                samples = self.apply_envelope(samples, 0.01, 0.02, 0.8, 0.05)
                all_samples.extend(samples)
        else:
            # Descending sad tones
            notes = [392, 330, 262]
            all_samples = []
            for freq in notes:
                samples = self.triangle_wave(freq, 0.12, volume)
                samples = self.apply_envelope(samples, 0.01, 0.03, 0.7, 0.08)
                all_samples.extend(samples)
        
        return self.samples_to_sound(all_samples)
    
    def generate_win(self, volume: float = 0.4) -> Optional[pygame.mixer.Sound]:
        """Generate victory fanfare"""
        # Victory melody
        melody = [
            (523, 0.15), (523, 0.15), (523, 0.15), (523, 0.4),
            (415, 0.4), (466, 0.4), (523, 0.2), (466, 0.1), (523, 0.6)
        ]
        
        all_samples = []
        for freq, dur in melody:
            samples = self.square_wave(freq, dur, 0.25, volume * 0.7)
            harmony = self.triangle_wave(freq * 0.5, dur, volume * 0.3)
            mixed = self.mix(samples, harmony)
            mixed = self.apply_envelope(mixed, 0.01, 0.05, 0.8, 0.1)
            all_samples.extend(mixed)
        
        return self.samples_to_sound(all_samples)
    
    def generate_lose(self, volume: float = 0.3) -> Optional[pygame.mixer.Sound]:
        """Generate game over / lose sound"""
        # Sad descending
        melody = [(392, 0.3), (349, 0.3), (330, 0.3), (294, 0.5)]
        
        all_samples = []
        for freq, dur in melody:
            samples = self.triangle_wave(freq, dur, volume)
            samples = self.apply_envelope(samples, 0.02, 0.1, 0.6, 0.15)
            all_samples.extend(samples)
        
        return self.samples_to_sound(all_samples)
    
    def generate_menu_nav(self, volume: float = 0.2) -> Optional[pygame.mixer.Sound]:
        """Generate menu navigation blip"""
        samples = self.square_wave(800, 0.03, 0.125, volume)
        samples = self.apply_envelope(samples, 0.001, 0.01, 0.8, 0.01)
        return self.samples_to_sound(samples)
    
    def generate_menu_select(self, volume: float = 0.3) -> Optional[pygame.mixer.Sound]:
        """Generate menu selection confirm"""
        s1 = self.square_wave(800, 0.04, 0.25, volume)
        s2 = self.square_wave(1200, 0.06, 0.25, volume)
        
        s1 = self.apply_envelope(s1, 0.001, 0.01, 0.9, 0.01)
        s2 = self.apply_envelope(s2, 0.001, 0.01, 0.9, 0.02)
        
        return self.samples_to_sound(s1 + s2)
    
    def play(self, sound: Optional[pygame.mixer.Sound]):
        """Safely play a sound"""
        if sound and self.enabled:
            try:
                sound.play()
            except:
                pass

# ═══════════════════════════════════════════════════════════════════════════════
# VIEW HELPERS
# ═══════════════════════════════════════════════════════════════════════════════
@dataclass
class View:
    scale: float
    rect: pygame.Rect


def compute_view(win_w: int, win_h: int) -> View:
    scale = min(win_w / LOGICAL_W, win_h / LOGICAL_H)
    scaled_w = max(1, int(LOGICAL_W * scale))
    scaled_h = max(1, int(LOGICAL_H * scale))
    off_x = (win_w - scaled_w) // 2
    off_y = (win_h - scaled_h) // 2
    return View(scale=scale, rect=pygame.Rect(off_x, off_y, scaled_w, scaled_h))


def window_to_logical(mx: int, my: int, view: View) -> Optional[Tuple[float, float]]:
    if not view.rect.collidepoint(mx, my):
        return None
    lx = (mx - view.rect.x) / view.scale
    ly = (my - view.rect.y) / view.scale
    return lx, ly


# ═══════════════════════════════════════════════════════════════════════════════
# GAME STATE
# ═══════════════════════════════════════════════════════════════════════════════
@dataclass
class Game:
    player_x: float = 40.0
    ai_x: float = float(LOGICAL_W - 40 - PADDLE_W)
    player_y: float = float(LOGICAL_H / 2 - PADDLE_H / 2)
    ai_y: float = float(LOGICAL_H / 2 - PADDLE_H / 2)
    
    player_score: int = 0
    ai_score: int = 0
    
    ball_speed: float = 300.0
    ball_x: float = 0.0
    ball_y: float = 0.0
    ball_vx: float = 0.0
    ball_vy: float = 0.0
    
    winner: str = ""
    game_state: str = "menu"
    selected: int = 0
    
    fullscreen: bool = False
    accumulator: float = 0.0
    
    # Visual effects
    screen_shake: float = 0.0
    ball_trail: list = None
    
    def __post_init__(self):
        self.ball_trail = []


def reset_ball(state: Game):
    state.ball_x = LOGICAL_W / 2
    state.ball_y = LOGICAL_H / 2
    direction = random.choice([-1, 1])
    angle = random.uniform(-math.pi / 6, math.pi / 6)
    state.ball_vx = state.ball_speed * math.cos(angle) * direction
    state.ball_vy = state.ball_speed * math.sin(angle)
    state.ball_trail = []


def reset_game(state: Game):
    state.player_score = 0
    state.ai_score = 0
    state.ball_speed = 300.0
    state.player_y = LOGICAL_H / 2 - PADDLE_H / 2
    state.ai_y = LOGICAL_H / 2 - PADDLE_H / 2
    state.screen_shake = 0.0
    reset_ball(state)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════
def main():
    pygame.init()
    
    window = pygame.display.set_mode((LOGICAL_W, LOGICAL_H), pygame.RESIZABLE)
    pygame.display.set_caption("Cat's Ultra!Pong HDR 0.1")
    render = pygame.Surface((LOGICAL_W, LOGICAL_H))
    
    clock = pygame.time.Clock()
    
    # Fonts
    font = pygame.font.SysFont("monospace", 48, bold=True)
    small_font = pygame.font.SysFont("monospace", 24, bold=True)
    big_font = pygame.font.SysFont("monospace", 96, bold=True)
    
    # Dynamic Sound Engine
    audio = SoundEngine()
    
    # Pre-generate static sounds
    menu_nav = audio.generate_menu_nav()
    menu_select = audio.generate_menu_select()
    win_sound = audio.generate_win()
    lose_sound = audio.generate_lose()
    
    menu_options = ["Start Game", "How to Play", "Credits", "Quit"]
    prev_selected = -1
    
    state = Game()
    reset_ball(state)
    
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        state.accumulator += dt
        
        # Decay screen shake
        if state.screen_shake > 0:
            state.screen_shake *= 0.9
            if state.screen_shake < 0.5:
                state.screen_shake = 0
        
        win_w, win_h = window.get_size()
        view = compute_view(win_w, win_h)
        
        # Hover detection
        hover_i = -1
        if state.game_state == "menu":
            mp = pygame.mouse.get_pos()
            logical_mouse = window_to_logical(mp[0], mp[1], view)
            if logical_mouse:
                mx, my = logical_mouse
                for i, opt in enumerate(menu_options):
                    opt_text = font.render(opt, True, WHITE)
                    x = LOGICAL_W // 2 - opt_text.get_width() // 2
                    y = 220 + i * 70
                    padding_x, padding_y = 40, 20
                    rect = pygame.Rect(
                        x - padding_x, y - padding_y,
                        opt_text.get_width() + padding_x * 2,
                        opt_text.get_height() + padding_y * 2
                    )
                    if rect.collidepoint((mx, my)):
                        hover_i = i
        
        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if state.game_state == "menu":
                        running = False
                    else:
                        state.game_state = "menu"
                
                if event.key == pygame.K_F11:
                    state.fullscreen = not state.fullscreen
                    if state.fullscreen:
                        window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    else:
                        window = pygame.display.set_mode((LOGICAL_W, LOGICAL_H), pygame.RESIZABLE)
                
                if state.game_state == "menu":
                    if event.key in (pygame.K_w, pygame.K_UP):
                        prev_selected = state.selected
                        state.selected = (state.selected - 1) % len(menu_options)
                    if event.key in (pygame.K_s, pygame.K_DOWN):
                        prev_selected = state.selected
                        state.selected = (state.selected + 1) % len(menu_options)
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        audio.play(menu_select)
                        if state.selected == 0:
                            reset_game(state)
                            state.game_state = "playing"
                        elif state.selected == 1:
                            state.game_state = "howto"
                        elif state.selected == 2:
                            state.game_state = "credits"
                        elif state.selected == 3:
                            running = False
                
                elif state.game_state in ("howto", "credits", "over"):
                    if state.game_state == "over":
                        if event.key == pygame.K_y:
                            reset_game(state)
                            state.game_state = "playing"
                        elif event.key == pygame.K_n:
                            running = False
                        elif event.key == pygame.K_m:
                            state.game_state = "menu"
                    else:
                        if event.key not in (pygame.K_ESCAPE, pygame.K_F11):
                            state.game_state = "menu"
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if state.game_state == "menu" and hover_i != -1:
                        audio.play(menu_select)
                        if hover_i == 0:
                            reset_game(state)
                            state.game_state = "playing"
                        elif hover_i == 1:
                            state.game_state = "howto"
                        elif hover_i == 2:
                            state.game_state = "credits"
                        elif hover_i == 3:
                            running = False
                    elif state.game_state in ("howto", "credits"):
                        state.game_state = "menu"
        
        # Menu nav sound
        if state.game_state == "menu":
            if state.selected != prev_selected:
                audio.play(menu_nav)
                prev_selected = state.selected
        
        # Fixed timestep update
        if state.game_state == "playing":
            while state.accumulator >= FIXED_DT:
                # Player input - MOUSE CONTROL
                mp = pygame.mouse.get_pos()
                logical_mouse = window_to_logical(mp[0], mp[1], view)
                if logical_mouse:
                    _, my = logical_mouse
                    # Center paddle on mouse Y
                    target_y = my - PADDLE_H / 2
                    # Smooth movement toward mouse
                    diff = target_y - state.player_y
                    state.player_y += diff * 0.3  # Smoothing factor
                state.player_y = max(0, min(LOGICAL_H - PADDLE_H, state.player_y))
                
                # AI
                ai_center = state.ai_y + PADDLE_H / 2
                dy = state.ball_y - ai_center
                if abs(dy) > 4:
                    direction = 1 if dy > 0 else -1
                    state.ai_y += direction * AI_SPEED * FIXED_DT
                state.ai_y = max(0, min(LOGICAL_H - PADDLE_H, state.ai_y))
                
                # Ball trail
                state.ball_trail.append((state.ball_x, state.ball_y))
                if len(state.ball_trail) > 10:
                    state.ball_trail.pop(0)
                
                # Ball movement
                state.ball_x += state.ball_vx * FIXED_DT
                state.ball_y += state.ball_vy * FIXED_DT
                
                ball_r = BALL_SIZE // 2
                
                # Wall bounce - DYNAMIC SOUND
                if state.ball_y - ball_r <= 0 or state.ball_y + ball_r >= LOGICAL_H:
                    state.ball_vy = -state.ball_vy
                    state.ball_y = max(ball_r, min(LOGICAL_H - ball_r, state.ball_y))
                    
                    # Dynamic wall bounce sound based on position
                    wall_sound = audio.generate_wall_bounce(state.ball_y, LOGICAL_H)
                    audio.play(wall_sound)
                
                # Paddle collision
                hit_left = (
                    state.ball_x - ball_r <= state.player_x + PADDLE_W
                    and state.ball_x + ball_r >= state.player_x
                    and state.ball_y + ball_r >= state.player_y
                    and state.ball_y - ball_r <= state.player_y + PADDLE_H
                    and state.ball_vx < 0
                )
                hit_right = (
                    state.ball_x + ball_r >= state.ai_x
                    and state.ball_x - ball_r <= state.ai_x + PADDLE_W
                    and state.ball_y + ball_r >= state.ai_y
                    and state.ball_y - ball_r <= state.ai_y + PADDLE_H
                    and state.ball_vx > 0
                )
                
                if hit_left or hit_right:
                    paddle_y_pos = state.player_y if hit_left else state.ai_y
                    center_y = paddle_y_pos + PADDLE_H / 2
                    intersect = (center_y - state.ball_y) / (PADDLE_H / 2)
                    intersect = max(-1.0, min(1.0, intersect))
                    bounce_angle = intersect * (math.pi / 4)
                    
                    current_speed = math.hypot(state.ball_vx, state.ball_vy) * 1.05
                    cos_a = math.cos(bounce_angle)
                    sin_a = math.sin(bounce_angle)
                    
                    if hit_left:
                        state.ball_vx = current_speed * cos_a
                        state.ball_vy = -current_speed * sin_a
                        state.ball_x = state.player_x + PADDLE_W + ball_r + 1
                    else:
                        state.ball_vx = -current_speed * cos_a
                        state.ball_vy = -current_speed * sin_a
                        state.ball_x = state.ai_x - ball_r - 1
                    
                    # DYNAMIC paddle hit sound
                    hit_sound = audio.generate_paddle_hit(
                        current_speed, 720.0, intersect
                    )
                    audio.play(hit_sound)
                    
                    # Screen shake on fast hits
                    if current_speed > 500:
                        state.screen_shake = (current_speed - 500) / 50
                
                # Scoring
                if state.ball_x - ball_r <= 0:
                    state.ai_score += 1
                    score_sound = audio.generate_score('ai')
                    audio.play(score_sound)
                    state.ball_speed = min(state.ball_speed + 20, 720)
                    state.screen_shake = 5
                    reset_ball(state)
                elif state.ball_x + ball_r >= LOGICAL_W:
                    state.player_score += 1
                    score_sound = audio.generate_score('player')
                    audio.play(score_sound)
                    state.ball_speed = min(state.ball_speed + 20, 720)
                    state.screen_shake = 5
                    reset_ball(state)
                
                # Win check
                if state.player_score >= 5:
                    state.game_state = "over"
                    state.winner = "PLAYER"
                    audio.play(win_sound)
                elif state.ai_score >= 5:
                    state.game_state = "over"
                    state.winner = "AI"
                    audio.play(lose_sound)
                
                state.accumulator -= FIXED_DT
        
        # ═══════════════════════════════════════════════════════════════════════
        # DRAW
        # ═══════════════════════════════════════════════════════════════════════
        render.fill(BLACK)
        
        # Apply screen shake
        shake_x = random.randint(-int(state.screen_shake), int(state.screen_shake)) if state.screen_shake else 0
        shake_y = random.randint(-int(state.screen_shake), int(state.screen_shake)) if state.screen_shake else 0
        
        if state.game_state == "menu":
            title_text = big_font.render("Ultra!Pong", True, CYAN)
            render.blit(title_text, (LOGICAL_W / 2 - title_text.get_width() / 2, 80))
            by_text = font.render("By Catsan", True, MAGENTA)
            render.blit(by_text, (LOGICAL_W / 2 - by_text.get_width() / 2, 160))
            
            for i, opt in enumerate(menu_options):
                opt_text = font.render(opt, True, WHITE)
                x = LOGICAL_W // 2 - opt_text.get_width() // 2
                y = 220 + i * 70
                padding_x, padding_y = 40, 20
                bg_rect = pygame.Rect(
                    x - padding_x, y - padding_y,
                    opt_text.get_width() + padding_x * 2,
                    opt_text.get_height() + padding_y * 2
                )
                is_active = (i == state.selected) or (i == hover_i)
                bg_color = HIGHLIGHT_GRAY if is_active else DARK_GRAY
                border_color = CYAN if is_active else GRAY
                pygame.draw.rect(render, bg_color, bg_rect, border_radius=12)
                pygame.draw.rect(render, border_color, bg_rect, width=4, border_radius=12)
                render.blit(opt_text, (x, y))
            
            instr = font.render("W/S Navigate • Space/Enter Select", True, GRAY)
            render.blit(instr, (LOGICAL_W / 2 - instr.get_width() / 2, LOGICAL_H - 60))
        
        elif state.game_state == "howto":
            how_title = big_font.render("How to Play", True, CYAN)
            render.blit(how_title, (LOGICAL_W / 2 - how_title.get_width() / 2, 80))
            lines = [
                "MOUSE  -  Move paddle up/down",
                "AI controls the right paddle",
                "First to 5 points wins",
                "Ball speeds up over time",
                "Esc - Menu | F11 - Fullscreen",
            ]
            for idx, line in enumerate(lines):
                text = font.render(line, True, WHITE)
                render.blit(text, (LOGICAL_W / 2 - text.get_width() / 2, 200 + idx * 60))
            back = font.render("Press any key to return", True, GRAY)
            render.blit(back, (LOGICAL_W / 2 - back.get_width() / 2, LOGICAL_H - 80))
        
        elif state.game_state == "credits":
            lines = ["THANK YOU", "FOR PLAYING"]
            start_y = LOGICAL_H / 2 - 80
            for i, line in enumerate(lines):
                text = big_font.render(line, True, MAGENTA)
                render.blit(text, (LOGICAL_W / 2 - text.get_width() / 2, start_y + i * 90))
            
            copy_text = small_font.render("[C] Samsoft 1999-2026  [C] Atari 1972-2026", True, GRAY)
            render.blit(copy_text, (LOGICAL_W / 2 - copy_text.get_width() / 2, LOGICAL_H - 40))
            
            back = small_font.render("Press any key to return", True, DARK_GRAY)
            render.blit(back, (LOGICAL_W / 2 - back.get_width() / 2, LOGICAL_H - 80))
        
        elif state.game_state in ("playing", "over"):
            # Center line
            dash_h, gap = 20, 10
            for y in range(0, LOGICAL_H, dash_h + gap):
                pygame.draw.rect(render, DARK_GRAY, (LOGICAL_W // 2 - 2 + shake_x, y + shake_y, 4, dash_h))
            
            # Ball trail
            for i, (tx, ty) in enumerate(state.ball_trail):
                alpha = int(255 * (i / len(state.ball_trail)) * 0.3)
                trail_size = int(BALL_SIZE * (i / len(state.ball_trail)))
                trail_surf = pygame.Surface((trail_size, trail_size), pygame.SRCALPHA)
                trail_surf.fill((255, 255, 255, alpha))
                render.blit(trail_surf, (int(tx - trail_size // 2 + shake_x), int(ty - trail_size // 2 + shake_y)))
            
            # Paddles
            pygame.draw.rect(render, CYAN, (state.player_x + shake_x, state.player_y + shake_y, PADDLE_W, PADDLE_H))
            pygame.draw.rect(render, MAGENTA, (state.ai_x + shake_x, state.ai_y + shake_y, PADDLE_W, PADDLE_H))
            
            # Ball
            pygame.draw.rect(render, WHITE, (
                int(state.ball_x - BALL_SIZE // 2 + shake_x),
                int(state.ball_y - BALL_SIZE // 2 + shake_y),
                BALL_SIZE, BALL_SIZE
            ))
            
            # Scores
            player_text = big_font.render(str(state.player_score), True, CYAN)
            ai_text = big_font.render(str(state.ai_score), True, MAGENTA)
            render.blit(player_text, (LOGICAL_W / 4 - player_text.get_width() / 2, 60))
            render.blit(ai_text, (3 * LOGICAL_W / 4 - ai_text.get_width() / 2, 60))
            
            if state.game_state == "over":
                color = CYAN if state.winner == "PLAYER" else MAGENTA
                win_text = big_font.render(f"{state.winner} WINS!", True, color)
                render.blit(win_text, (LOGICAL_W / 2 - win_text.get_width() / 2, LOGICAL_H / 2 - 120))
                restart = font.render("Y - Restart | N - Quit | M - Menu", True, WHITE)
                render.blit(restart, (LOGICAL_W / 2 - restart.get_width() / 2, LOGICAL_H / 2 + 40))
        
        # Present
        window.fill(BLACK)
        scaled = pygame.transform.scale(render, (view.rect.w, view.rect.h))
        window.blit(scaled, view.rect.topleft)
        pygame.display.flip()
    
    pygame.quit()


if __name__ == "__main__":
    main()
