#!/usr/bin/env python3
"""
ULTRA!TETRIS - A Complete Tetris Implementation
By Team Flames / Samsoft / Flames Co.
"""

import pygame
import random
import math
import sys

# Initialize Pygame
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

# Constants
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 640
BLOCK_SIZE = 28
GRID_WIDTH = 10
GRID_HEIGHT = 20
GRID_X = 40
GRID_Y = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (40, 40, 40)
DARK_GRAY = (20, 20, 20)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
PURPLE = (160, 0, 240)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
MENU_BG = (10, 10, 30)
HIGHLIGHT = (80, 80, 180)

# Tetromino shapes and colors
SHAPES = {
    'I': [[(0, 0), (1, 0), (2, 0), (3, 0)],
          [(0, 0), (0, 1), (0, 2), (0, 3)],
          [(0, 0), (1, 0), (2, 0), (3, 0)],
          [(0, 0), (0, 1), (0, 2), (0, 3)]],
    'O': [[(0, 0), (1, 0), (0, 1), (1, 1)],
          [(0, 0), (1, 0), (0, 1), (1, 1)],
          [(0, 0), (1, 0), (0, 1), (1, 1)],
          [(0, 0), (1, 0), (0, 1), (1, 1)]],
    'T': [[(1, 0), (0, 1), (1, 1), (2, 1)],
          [(0, 0), (0, 1), (1, 1), (0, 2)],
          [(0, 0), (1, 0), (2, 0), (1, 1)],
          [(1, 0), (0, 1), (1, 1), (1, 2)]],
    'S': [[(1, 0), (2, 0), (0, 1), (1, 1)],
          [(0, 0), (0, 1), (1, 1), (1, 2)],
          [(1, 0), (2, 0), (0, 1), (1, 1)],
          [(0, 0), (0, 1), (1, 1), (1, 2)]],
    'Z': [[(0, 0), (1, 0), (1, 1), (2, 1)],
          [(1, 0), (0, 1), (1, 1), (0, 2)],
          [(0, 0), (1, 0), (1, 1), (2, 1)],
          [(1, 0), (0, 1), (1, 1), (0, 2)]],
    'J': [[(0, 0), (0, 1), (1, 1), (2, 1)],
          [(0, 0), (1, 0), (0, 1), (0, 2)],
          [(0, 0), (1, 0), (2, 0), (2, 1)],
          [(1, 0), (1, 1), (0, 2), (1, 2)]],
    'L': [[(2, 0), (0, 1), (1, 1), (2, 1)],
          [(0, 0), (0, 1), (0, 2), (1, 2)],
          [(0, 0), (1, 0), (2, 0), (0, 1)],
          [(0, 0), (1, 0), (1, 1), (1, 2)]]
}

SHAPE_COLORS = {
    'I': CYAN,
    'O': YELLOW,
    'T': PURPLE,
    'S': GREEN,
    'Z': RED,
    'J': BLUE,
    'L': ORANGE
}

class SoundGenerator:
    """Generates retro-style sound effects and music"""
    
    def __init__(self):
        self.sample_rate = 44100
        self.sounds = {}
        self.generate_sounds()
        self.music_playing = False
        self.music_channel = None
        
    def generate_wave(self, frequency, duration, wave_type='square', volume=0.3):
        """Generate a waveform"""
        num_samples = int(self.sample_rate * duration)
        samples = []
        
        for i in range(num_samples):
            t = i / self.sample_rate
            if wave_type == 'square':
                value = volume if math.sin(2 * math.pi * frequency * t) > 0 else -volume
            elif wave_type == 'sine':
                value = volume * math.sin(2 * math.pi * frequency * t)
            elif wave_type == 'triangle':
                value = volume * (2 * abs(2 * (t * frequency - math.floor(t * frequency + 0.5))) - 1)
            elif wave_type == 'sawtooth':
                value = volume * (2 * (t * frequency - math.floor(t * frequency)) - 1)
            else:
                value = 0
            
            # Apply envelope
            env = 1.0
            attack = 0.01
            release = 0.1
            if t < attack:
                env = t / attack
            elif t > duration - release:
                env = (duration - t) / release
            
            samples.append(int(value * env * 32767))
        
        return samples
    
    def create_sound(self, samples):
        """Convert samples to pygame Sound"""
        import array
        # Stereo
        stereo_samples = []
        for s in samples:
            stereo_samples.append(s)
            stereo_samples.append(s)
        
        arr = array.array('h', stereo_samples)
        sound = pygame.mixer.Sound(buffer=arr.tobytes())
        return sound
    
    def generate_sounds(self):
        """Generate all game sounds"""
        # Move sound
        move_samples = self.generate_wave(200, 0.05, 'square', 0.2)
        self.sounds['move'] = self.create_sound(move_samples)
        
        # Rotate sound
        rotate_samples = self.generate_wave(400, 0.08, 'square', 0.2)
        self.sounds['rotate'] = self.create_sound(rotate_samples)
        
        # Drop sound
        drop_samples = self.generate_wave(150, 0.15, 'square', 0.3)
        self.sounds['drop'] = self.create_sound(drop_samples)
        
        # Line clear sound
        clear_samples = []
        for freq in [523, 659, 784, 1047]:
            clear_samples.extend(self.generate_wave(freq, 0.1, 'square', 0.3))
        self.sounds['clear'] = self.create_sound(clear_samples)
        
        # Tetris sound (4 lines)
        tetris_samples = []
        for freq in [523, 659, 784, 1047, 1319, 1568]:
            tetris_samples.extend(self.generate_wave(freq, 0.08, 'square', 0.35))
        self.sounds['tetris'] = self.create_sound(tetris_samples)
        
        # Game over sound
        gameover_samples = []
        for freq in [400, 350, 300, 250, 200, 150]:
            gameover_samples.extend(self.generate_wave(freq, 0.15, 'square', 0.3))
        self.sounds['gameover'] = self.create_sound(gameover_samples)
        
        # Menu select sound
        select_samples = self.generate_wave(600, 0.1, 'square', 0.2)
        self.sounds['select'] = self.create_sound(select_samples)
        
        # Menu confirm sound
        confirm_samples = []
        confirm_samples.extend(self.generate_wave(500, 0.08, 'square', 0.25))
        confirm_samples.extend(self.generate_wave(700, 0.12, 'square', 0.25))
        self.sounds['confirm'] = self.create_sound(confirm_samples)
        
        # Level up sound
        levelup_samples = []
        for freq in [400, 500, 600, 800, 1000]:
            levelup_samples.extend(self.generate_wave(freq, 0.06, 'triangle', 0.3))
        self.sounds['levelup'] = self.create_sound(levelup_samples)
    
    def generate_music_loop(self):
        """Generate the iconic Tetris-style music loop (Korobeiniki-inspired)"""
        # DUH DUH DUH style melody
        melody_notes = [
            (659, 0.25), (494, 0.125), (523, 0.125), (587, 0.25), (523, 0.125), (494, 0.125),
            (440, 0.25), (440, 0.125), (523, 0.125), (659, 0.25), (587, 0.125), (523, 0.125),
            (494, 0.375), (523, 0.125), (587, 0.25), (659, 0.25),
            (523, 0.25), (440, 0.25), (440, 0.25), (0, 0.25),
            (587, 0.25), (698, 0.125), (880, 0.25), (784, 0.125), (698, 0.125),
            (659, 0.375), (523, 0.125), (659, 0.25), (587, 0.125), (523, 0.125),
            (494, 0.25), (494, 0.125), (523, 0.125), (587, 0.25), (659, 0.25),
            (523, 0.25), (440, 0.25), (440, 0.25), (0, 0.25)
        ]
        
        music_samples = []
        for freq, dur in melody_notes:
            if freq > 0:
                note = self.generate_wave(freq, dur * 0.9, 'square', 0.25)
                silence = [0] * int(self.sample_rate * dur * 0.1)
                music_samples.extend(note)
                music_samples.extend(silence)
            else:
                silence = [0] * int(self.sample_rate * dur)
                music_samples.extend(silence)
        
        self.sounds['music'] = self.create_sound(music_samples)
        return self.sounds['music']
    
    def play(self, sound_name):
        """Play a sound effect"""
        if sound_name in self.sounds:
            self.sounds[sound_name].play()
    
    def start_music(self):
        """Start background music loop"""
        if 'music' not in self.sounds:
            self.generate_music_loop()
        self.music_channel = self.sounds['music'].play(loops=-1)
        self.music_playing = True
    
    def stop_music(self):
        """Stop background music"""
        if self.music_channel:
            self.music_channel.stop()
        self.music_playing = False


class Tetromino:
    """Represents a falling tetromino piece"""
    
    def __init__(self, shape_type=None):
        if shape_type is None:
            shape_type = random.choice(list(SHAPES.keys()))
        self.shape_type = shape_type
        self.rotation = 0
        self.x = GRID_WIDTH // 2 - 2
        self.y = 0
        self.color = SHAPE_COLORS[shape_type]
    
    def get_blocks(self):
        """Get current block positions"""
        return [(self.x + bx, self.y + by) 
                for bx, by in SHAPES[self.shape_type][self.rotation]]
    
    def rotate(self, direction=1):
        """Rotate the piece"""
        self.rotation = (self.rotation + direction) % 4


class Grid:
    """The game grid"""
    
    def __init__(self):
        self.cells = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    
    def is_valid_position(self, tetromino):
        """Check if tetromino position is valid"""
        for x, y in tetromino.get_blocks():
            if x < 0 or x >= GRID_WIDTH or y >= GRID_HEIGHT:
                return False
            if y >= 0 and self.cells[y][x] is not None:
                return False
        return True
    
    def lock_piece(self, tetromino):
        """Lock the piece into the grid"""
        for x, y in tetromino.get_blocks():
            if 0 <= y < GRID_HEIGHT and 0 <= x < GRID_WIDTH:
                self.cells[y][x] = tetromino.color
    
    def clear_lines(self):
        """Clear completed lines and return count"""
        lines_cleared = 0
        y = GRID_HEIGHT - 1
        while y >= 0:
            if all(self.cells[y][x] is not None for x in range(GRID_WIDTH)):
                del self.cells[y]
                self.cells.insert(0, [None for _ in range(GRID_WIDTH)])
                lines_cleared += 1
            else:
                y -= 1
        return lines_cleared
    
    def is_game_over(self):
        """Check if game is over"""
        return any(self.cells[0][x] is not None for x in range(GRID_WIDTH))


class Game:
    """Main game class"""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("ULTRA!TETRIS")
        self.clock = pygame.time.Clock()
        self.sound = SoundGenerator()
        self.font_large = pygame.font.Font(None, 64)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        self.font_tiny = pygame.font.Font(None, 18)
        
        self.state = 'menu'
        self.menu_selection = 0
        self.menu_items = ['PLAY GAME', 'HOW TO PLAY', 'ABOUT', 'CREDITS', 'COPYRIGHT', 'EXIT']
        
        self.reset_game()
        
        # Generate music
        self.sound.generate_music_loop()
    
    def reset_game(self):
        """Reset game state"""
        self.grid = Grid()
        self.current_piece = Tetromino()
        self.next_piece = Tetromino()
        self.score = 0
        self.level = 1
        self.lines = 0
        self.fall_time = 0
        self.fall_speed = 1000  # ms
        self.game_over = False
        self.paused = False
    
    def draw_block(self, x, y, color, offset_x=GRID_X, offset_y=GRID_Y):
        """Draw a single block with 3D effect"""
        rect = pygame.Rect(offset_x + x * BLOCK_SIZE, offset_y + y * BLOCK_SIZE, 
                          BLOCK_SIZE - 1, BLOCK_SIZE - 1)
        pygame.draw.rect(self.screen, color, rect)
        
        # Highlight
        lighter = tuple(min(255, c + 60) for c in color)
        pygame.draw.line(self.screen, lighter, rect.topleft, rect.topright, 2)
        pygame.draw.line(self.screen, lighter, rect.topleft, rect.bottomleft, 2)
        
        # Shadow
        darker = tuple(max(0, c - 60) for c in color)
        pygame.draw.line(self.screen, darker, rect.bottomleft, rect.bottomright, 2)
        pygame.draw.line(self.screen, darker, rect.topright, rect.bottomright, 2)
    
    def draw_grid(self):
        """Draw the game grid"""
        # Grid background
        grid_rect = pygame.Rect(GRID_X - 2, GRID_Y - 2, 
                               GRID_WIDTH * BLOCK_SIZE + 4, GRID_HEIGHT * BLOCK_SIZE + 4)
        pygame.draw.rect(self.screen, DARK_GRAY, grid_rect)
        pygame.draw.rect(self.screen, WHITE, grid_rect, 2)
        
        # Grid lines
        for y in range(GRID_HEIGHT + 1):
            pygame.draw.line(self.screen, GRAY,
                           (GRID_X, GRID_Y + y * BLOCK_SIZE),
                           (GRID_X + GRID_WIDTH * BLOCK_SIZE, GRID_Y + y * BLOCK_SIZE))
        for x in range(GRID_WIDTH + 1):
            pygame.draw.line(self.screen, GRAY,
                           (GRID_X + x * BLOCK_SIZE, GRID_Y),
                           (GRID_X + x * BLOCK_SIZE, GRID_Y + GRID_HEIGHT * BLOCK_SIZE))
        
        # Locked blocks
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid.cells[y][x]:
                    self.draw_block(x, y, self.grid.cells[y][x])
        
        # Current piece
        if self.current_piece:
            for x, y in self.current_piece.get_blocks():
                if y >= 0:
                    self.draw_block(x, y, self.current_piece.color)
            
            # Ghost piece
            ghost = Tetromino(self.current_piece.shape_type)
            ghost.x = self.current_piece.x
            ghost.y = self.current_piece.y
            ghost.rotation = self.current_piece.rotation
            
            while self.grid.is_valid_position(ghost):
                ghost.y += 1
            ghost.y -= 1
            
            for x, y in ghost.get_blocks():
                if y >= 0:
                    ghost_color = tuple(c // 4 for c in self.current_piece.color)
                    self.draw_block(x, y, ghost_color)
    
    def draw_sidebar(self):
        """Draw score, level, next piece"""
        sidebar_x = GRID_X + GRID_WIDTH * BLOCK_SIZE + 20
        
        # Next piece
        next_text = self.font_medium.render("NEXT", True, WHITE)
        self.screen.blit(next_text, (sidebar_x, 60))
        
        next_box = pygame.Rect(sidebar_x, 95, 120, 80)
        pygame.draw.rect(self.screen, DARK_GRAY, next_box)
        pygame.draw.rect(self.screen, WHITE, next_box, 2)
        
        if self.next_piece:
            for bx, by in SHAPES[self.next_piece.shape_type][0]:
                self.draw_block(bx, by, self.next_piece.color, sidebar_x + 20, 105)
        
        # Score
        score_text = self.font_medium.render("SCORE", True, WHITE)
        self.screen.blit(score_text, (sidebar_x, 200))
        score_val = self.font_medium.render(str(self.score), True, CYAN)
        self.screen.blit(score_val, (sidebar_x, 235))
        
        # Level
        level_text = self.font_medium.render("LEVEL", True, WHITE)
        self.screen.blit(level_text, (sidebar_x, 290))
        level_val = self.font_medium.render(str(self.level), True, GREEN)
        self.screen.blit(level_val, (sidebar_x, 325))
        
        # Lines
        lines_text = self.font_medium.render("LINES", True, WHITE)
        self.screen.blit(lines_text, (sidebar_x, 380))
        lines_val = self.font_medium.render(str(self.lines), True, YELLOW)
        self.screen.blit(lines_val, (sidebar_x, 415))
    
    def draw_menu(self):
        """Draw main menu"""
        self.screen.fill(MENU_BG)
        
        # Title with glow effect
        title = self.font_large.render("ULTRA!TETRIS", True, CYAN)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        
        # Glow
        for i in range(3, 0, -1):
            glow_color = (0, 255 // (i + 1), 255 // (i + 1))
            glow = self.font_large.render("ULTRA!TETRIS", True, glow_color)
            glow_rect = glow.get_rect(center=(SCREEN_WIDTH // 2 + i, 100 + i))
            self.screen.blit(glow, glow_rect)
        
        self.screen.blit(title, title_rect)
        
        # Subtitle
        subtitle = self.font_small.render("DUH DUH DUH", True, PURPLE)
        sub_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(subtitle, sub_rect)
        
        # Menu items
        for i, item in enumerate(self.menu_items):
            color = CYAN if i == self.menu_selection else WHITE
            if i == self.menu_selection:
                # Selection highlight
                highlight_rect = pygame.Rect(SCREEN_WIDTH // 2 - 120, 220 + i * 50 - 5, 240, 40)
                pygame.draw.rect(self.screen, HIGHLIGHT, highlight_rect, border_radius=5)
                pygame.draw.rect(self.screen, CYAN, highlight_rect, 2, border_radius=5)
            
            text = self.font_medium.render(item, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 220 + i * 50 + 10))
            self.screen.blit(text, text_rect)
        
        # Instructions
        inst = self.font_small.render("PRESS SPACE or Z TO SELECT", True, GRAY)
        inst_rect = inst.get_rect(center=(SCREEN_WIDTH // 2, 560))
        self.screen.blit(inst, inst_rect)
        
        # Decorative falling blocks
        t = pygame.time.get_ticks() / 1000
        for i in range(5):
            shape = list(SHAPES.keys())[i]
            color = SHAPE_COLORS[shape]
            x = 30 + i * 90
            y = int((t * 50 + i * 100) % 700) - 50
            for bx, by in SHAPES[shape][0]:
                rect = pygame.Rect(x + bx * 15, y + by * 15, 14, 14)
                pygame.draw.rect(self.screen, tuple(c // 3 for c in color), rect)
    
    def draw_how_to_play(self):
        """Draw how to play screen"""
        self.screen.fill(MENU_BG)
        
        title = self.font_large.render("HOW TO PLAY", True, CYAN)
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 60)))
        
        instructions = [
            "",
            "CONTROLS:",
            "",
            "LEFT/RIGHT - Move piece",
            "DOWN - Soft drop",
            "UP or X - Rotate clockwise",
            "Z - Rotate counter-clockwise", 
            "SPACE - Hard drop",
            "P - Pause",
            "ESC - Return to menu",
            "",
            "GOAL:",
            "",
            "Fill horizontal lines to clear them.",
            "Clear multiple lines for bonus points!",
            "Don't let pieces stack to the top!",
            "",
            "SCORING:",
            "",
            "1 Line = 100 x Level",
            "2 Lines = 300 x Level",
            "3 Lines = 500 x Level", 
            "4 Lines (TETRIS!) = 800 x Level"
        ]
        
        y = 110
        for line in instructions:
            if line.endswith(':'):
                text = self.font_medium.render(line, True, YELLOW)
            else:
                text = self.font_small.render(line, True, WHITE)
            self.screen.blit(text, (60, y))
            y += 22
        
        back = self.font_small.render("PRESS SPACE or Z TO RETURN", True, GRAY)
        self.screen.blit(back, back.get_rect(center=(SCREEN_WIDTH // 2, 600)))
    
    def draw_about(self):
        """Draw about screen"""
        self.screen.fill(MENU_BG)
        
        title = self.font_large.render("ABOUT", True, CYAN)
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 60)))
        
        about_text = [
            "",
            "ULTRA!TETRIS is a modern recreation",
            "of the classic puzzle game that has",
            "captivated players since 1984.",
            "",
            "Originally created by Alexey Pajitnov,",
            "Tetris became one of the most iconic",
            "and influential video games ever made.",
            "",
            "This version features:",
            "",
            "- Classic Tetris gameplay",
            "- Retro-style procedural music",
            "- Ghost piece preview",
            "- Increasing difficulty",
            "- Modern controls",
            "",
            "Built with Python and Pygame",
            "for the ultimate retro experience!"
        ]
        
        y = 110
        for line in about_text:
            text = self.font_small.render(line, True, WHITE)
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
            self.screen.blit(text, rect)
            y += 26
        
        back = self.font_small.render("PRESS SPACE or Z TO RETURN", True, GRAY)
        self.screen.blit(back, back.get_rect(center=(SCREEN_WIDTH // 2, 600)))
    
    def draw_credits(self):
        """Draw credits screen"""
        self.screen.fill(MENU_BG)
        
        title = self.font_large.render("CREDITS", True, CYAN)
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 60)))
        
        credits_text = [
            "",
            "ULTRA!TETRIS",
            "",
            "- - - - - - - - - -",
            "",
            "DEVELOPMENT",
            "Team Flames / Samsoft / Flames Co.",
            "",
            "PROGRAMMING",
            "Flames",
            "",
            "SOUND DESIGN", 
            "Procedural Audio Engine",
            "",
            "MUSIC",
            "Inspired by Korobeiniki",
            "(Traditional Russian Folk Song)",
            "",
            "ORIGINAL TETRIS",
            "Alexey Pajitnov (1984)",
            "",
            "- - - - - - - - - -",
            "",
            "SPECIAL THANKS",
            "The Pygame Community",
            "All Retro Gaming Enthusiasts!"
        ]
        
        y = 95
        for line in credits_text:
            if line == "DEVELOPMENT" or line == "PROGRAMMING" or line == "SOUND DESIGN" or \
               line == "MUSIC" or line == "ORIGINAL TETRIS" or line == "SPECIAL THANKS":
                text = self.font_small.render(line, True, YELLOW)
            elif line == "ULTRA!TETRIS":
                text = self.font_medium.render(line, True, CYAN)
            else:
                text = self.font_small.render(line, True, WHITE)
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
            self.screen.blit(text, rect)
            y += 20
        
        back = self.font_small.render("PRESS SPACE or Z TO RETURN", True, GRAY)
        self.screen.blit(back, back.get_rect(center=(SCREEN_WIDTH // 2, 600)))
    
    def draw_copyright(self):
        """Draw copyright screen"""
        self.screen.fill(MENU_BG)
        
        title = self.font_large.render("COPYRIGHT", True, CYAN)
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 60)))
        
        copyright_text = [
            "",
            "ULTRA!TETRIS",
            "(C) 2025 Team Flames / Samsoft",
            "",
            "- - - - - - - - - -",
            "",
            "This is a fan-made recreation",
            "for educational purposes.",
            "",
            "Tetris (R) is a trademark of",
            "Tetris Holding, LLC.",
            "",
            "The Tetris trade dress is owned",
            "by Tetris Holding, LLC.",
            "",
            "Licensed to The Tetris Company.",
            "",
            "Original Tetris game design",
            "by Alexey Pajitnov.",
            "",
            "- - - - - - - - - -",
            "",
            "This software is provided 'as-is'",
            "without warranty of any kind.",
            "",
            "Made with love for retro gaming!"
        ]
        
        y = 100
        for line in copyright_text:
            if "(C)" in line or "(R)" in line:
                text = self.font_small.render(line, True, YELLOW)
            elif line == "ULTRA!TETRIS":
                text = self.font_medium.render(line, True, CYAN)
            else:
                text = self.font_small.render(line, True, WHITE)
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
            self.screen.blit(text, rect)
            y += 20
        
        back = self.font_small.render("PRESS SPACE or Z TO RETURN", True, GRAY)
        self.screen.blit(back, back.get_rect(center=(SCREEN_WIDTH // 2, 600)))
    
    def draw_game(self):
        """Draw the game screen"""
        self.screen.fill(BLACK)
        
        # Title
        title = self.font_medium.render("ULTRA!TETRIS", True, CYAN)
        self.screen.blit(title, (GRID_X, 15))
        
        self.draw_grid()
        self.draw_sidebar()
        
        # Pause overlay
        if self.paused:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.fill(BLACK)
            overlay.set_alpha(180)
            self.screen.blit(overlay, (0, 0))
            
            pause_text = self.font_large.render("PAUSED", True, CYAN)
            self.screen.blit(pause_text, pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30)))
            
            resume_text = self.font_small.render("Press P to resume", True, WHITE)
            self.screen.blit(resume_text, resume_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20)))
        
        # Game over overlay
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.fill(BLACK)
            overlay.set_alpha(200)
            self.screen.blit(overlay, (0, 0))
            
            go_text = self.font_large.render("GAME OVER", True, RED)
            self.screen.blit(go_text, go_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60)))
            
            final_score = self.font_medium.render(f"Final Score: {self.score}", True, WHITE)
            self.screen.blit(final_score, final_score.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))
            
            restart_text = self.font_small.render("Press SPACE or Z to play again", True, GRAY)
            self.screen.blit(restart_text, restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)))
            
            menu_text = self.font_small.render("Press ESC for menu", True, GRAY)
            self.screen.blit(menu_text, menu_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80)))
    
    def handle_menu_input(self, event):
        """Handle menu input"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.menu_selection = (self.menu_selection - 1) % len(self.menu_items)
                self.sound.play('select')
            elif event.key == pygame.K_DOWN:
                self.menu_selection = (self.menu_selection + 1) % len(self.menu_items)
                self.sound.play('select')
            elif event.key in (pygame.K_SPACE, pygame.K_z, pygame.K_RETURN):
                self.sound.play('confirm')
                selected = self.menu_items[self.menu_selection]
                if selected == 'PLAY GAME':
                    self.state = 'game'
                    self.reset_game()
                    self.sound.start_music()
                elif selected == 'HOW TO PLAY':
                    self.state = 'howto'
                elif selected == 'ABOUT':
                    self.state = 'about'
                elif selected == 'CREDITS':
                    self.state = 'credits'
                elif selected == 'COPYRIGHT':
                    self.state = 'copyright'
                elif selected == 'EXIT':
                    pygame.quit()
                    sys.exit()
    
    def handle_game_input(self, event):
        """Handle game input"""
        if event.type == pygame.KEYDOWN:
            if self.game_over:
                if event.key in (pygame.K_SPACE, pygame.K_z):
                    self.reset_game()
                    self.sound.start_music()
                elif event.key == pygame.K_ESCAPE:
                    self.state = 'menu'
                    self.sound.stop_music()
                return
            
            if event.key == pygame.K_p:
                self.paused = not self.paused
                return
            
            if self.paused:
                return
            
            if event.key == pygame.K_LEFT:
                self.current_piece.x -= 1
                if not self.grid.is_valid_position(self.current_piece):
                    self.current_piece.x += 1
                else:
                    self.sound.play('move')
            
            elif event.key == pygame.K_RIGHT:
                self.current_piece.x += 1
                if not self.grid.is_valid_position(self.current_piece):
                    self.current_piece.x -= 1
                else:
                    self.sound.play('move')
            
            elif event.key == pygame.K_DOWN:
                self.current_piece.y += 1
                if not self.grid.is_valid_position(self.current_piece):
                    self.current_piece.y -= 1
            
            elif event.key in (pygame.K_UP, pygame.K_x):
                self.current_piece.rotate(1)
                if not self.grid.is_valid_position(self.current_piece):
                    # Try wall kicks
                    for kick in [1, -1, 2, -2]:
                        self.current_piece.x += kick
                        if self.grid.is_valid_position(self.current_piece):
                            break
                        self.current_piece.x -= kick
                    else:
                        self.current_piece.rotate(-1)
                else:
                    self.sound.play('rotate')
            
            elif event.key == pygame.K_z:
                self.current_piece.rotate(-1)
                if not self.grid.is_valid_position(self.current_piece):
                    self.current_piece.rotate(1)
                else:
                    self.sound.play('rotate')
            
            elif event.key == pygame.K_SPACE:
                # Hard drop
                while self.grid.is_valid_position(self.current_piece):
                    self.current_piece.y += 1
                    self.score += 2
                self.current_piece.y -= 1
                self.lock_and_spawn()
                self.sound.play('drop')
            
            elif event.key == pygame.K_ESCAPE:
                self.state = 'menu'
                self.sound.stop_music()
    
    def lock_and_spawn(self):
        """Lock current piece and spawn new one"""
        self.grid.lock_piece(self.current_piece)
        
        # Clear lines
        lines = self.grid.clear_lines()
        if lines > 0:
            # Scoring
            points = [0, 100, 300, 500, 800]
            self.score += points[lines] * self.level
            self.lines += lines
            
            if lines == 4:
                self.sound.play('tetris')
            else:
                self.sound.play('clear')
            
            # Level up every 10 lines
            new_level = self.lines // 10 + 1
            if new_level > self.level:
                self.level = new_level
                self.fall_speed = max(100, 1000 - (self.level - 1) * 100)
                self.sound.play('levelup')
        
        # Spawn new piece
        self.current_piece = self.next_piece
        self.next_piece = Tetromino()
        
        # Check game over
        if not self.grid.is_valid_position(self.current_piece):
            self.game_over = True
            self.sound.stop_music()
            self.sound.play('gameover')
    
    def update(self, dt):
        """Update game state"""
        if self.state != 'game' or self.paused or self.game_over:
            return
        
        self.fall_time += dt
        if self.fall_time >= self.fall_speed:
            self.fall_time = 0
            self.current_piece.y += 1
            if not self.grid.is_valid_position(self.current_piece):
                self.current_piece.y -= 1
                self.lock_and_spawn()
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            dt = self.clock.tick(60)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif self.state == 'menu':
                    self.handle_menu_input(event)
                
                elif self.state == 'game':
                    self.handle_game_input(event)
                
                elif self.state in ('howto', 'about', 'credits', 'copyright'):
                    if event.type == pygame.KEYDOWN:
                        if event.key in (pygame.K_SPACE, pygame.K_z, pygame.K_ESCAPE):
                            self.state = 'menu'
                            self.sound.play('confirm')
            
            self.update(dt)
            
            # Draw
            if self.state == 'menu':
                self.draw_menu()
            elif self.state == 'game':
                self.draw_game()
            elif self.state == 'howto':
                self.draw_how_to_play()
            elif self.state == 'about':
                self.draw_about()
            elif self.state == 'credits':
                self.draw_credits()
            elif self.state == 'copyright':
                self.draw_copyright()
            
            pygame.display.flip()
        
        pygame.quit()


if __name__ == '__main__':
    game = Game()
    game.run()
