#!/usr/bin/env python3
"""
Cat's Ultra! Tetris 1.x
Classic Tetris with Full Korobeiniki Theme
(C) Samsoft 1999-2026
Tetris (C) 1985 The Tetris Company / Alexey Pajitnov
"""

import pygame
import random
import math
import array

# Initialize
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)

# Display
BLOCK = 30
COLS = 10
ROWS = 20
SIDEBAR = 180
WIDTH = COLS * BLOCK + SIDEBAR
HEIGHT = ROWS * BLOCK
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cat's Ultra! Tetris 1.x")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (80, 80, 80)
DARK = (25, 25, 25)
CYAN = (0, 240, 240)
YELLOW = (240, 240, 0)
PURPLE = (160, 0, 240)
GREEN = (0, 240, 0)
RED = (240, 0, 0)
BLUE = (0, 0, 240)
ORANGE = (240, 160, 0)

# Note frequencies
NOTE_FREQS = {
    'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'F4': 349.23, 'G4': 392.00, 'A4': 440.00, 'B4': 493.88,
    'C5': 523.25, 'D5': 587.33, 'E5': 659.25, 'F5': 698.46, 'G5': 783.99, 'A5': 880.00, 'B5': 987.77,
    'REST': 0
}

# Full Korobeiniki melody (Type A Tetris theme)
KOROBEINIKI_MELODY = [
    ('E5', 1), ('B4', 0.5), ('C5', 0.5), ('D5', 1), ('C5', 0.5), ('B4', 0.5),
    ('A4', 1), ('A4', 0.5), ('C5', 0.5), ('E5', 1), ('D5', 0.5), ('C5', 0.5),
    ('B4', 1.5), ('C5', 0.5), ('D5', 1), ('E5', 1),
    ('C5', 1), ('A4', 1), ('A4', 1), ('REST', 1),
    ('D5', 1), ('F5', 0.5), ('A5', 1), ('G5', 0.5), ('F5', 0.5),
    ('E5', 1.5), ('C5', 0.5), ('E5', 1), ('D5', 0.5), ('C5', 0.5),
    ('B4', 1), ('B4', 0.5), ('C5', 0.5), ('D5', 1), ('E5', 1),
    ('C5', 1), ('A4', 1), ('A4', 1), ('REST', 1),
    ('E4', 2), ('C4', 2), ('D4', 2), ('B4', 2),
    ('C4', 2), ('A4', 2), ('G4', 2), ('B4', 2),
    ('E4', 2), ('C4', 2), ('D4', 2), ('B4', 2),
    ('C4', 1), ('E4', 1), ('A4', 2), ('A4', 1), ('REST', 1),
]

def generate_full_song(melody, tempo=140, volume=0.35):
    sample_rate = 44100
    beat_duration = 60.0 / tempo
    total_beats = sum(duration for _, duration in melody)
    total_samples = int(total_beats * beat_duration * sample_rate)
    buf = array.array('h', [0] * (total_samples * 2))
    
    current_sample = 0
    for note, duration in melody:
        note_samples = int(duration * beat_duration * sample_rate)
        freq = NOTE_FREQS.get(note, 0)
        
        if freq > 0:
            for i in range(note_samples):
                t = i / sample_rate
                attack = min(1.0, i / 800)
                release_start = note_samples - 1500
                release = 1.0 if i < release_start else max(0, (note_samples - i) / 1500)
                envelope = attack * release
                pulse_width = 0.5 + 0.1 * math.sin(2 * math.pi * 3 * t)
                phase = (freq * t) % 1.0
                square = 1.0 if phase < pulse_width else -1.0
                triangle = 2 * abs(2 * ((freq * t) % 1.0) - 1) - 1
                sample = (0.7 * square + 0.3 * triangle) * envelope * volume
                sample_int = int(sample * 32767)
                sample_int = max(-32767, min(32767, sample_int))
                idx = (current_sample + i) * 2
                if idx + 1 < len(buf):
                    buf[idx] = sample_int
                    buf[idx + 1] = sample_int
        current_sample += note_samples
    
    return pygame.mixer.Sound(buffer=buf)

print("Generating Korobeiniki theme...")
TETRIS_THEME = generate_full_song(KOROBEINIKI_MELODY)
print("Theme generated!")

def generate_tone(frequency, duration, volume=0.3):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    buf = array.array('h', [0] * (n_samples * 2))
    for i in range(n_samples):
        t = i / sample_rate
        envelope = min(1.0, min(i / 300, (n_samples - i) / 300))
        val = volume * envelope * (1 if math.sin(2 * math.pi * frequency * t) > 0 else -1)
        sample_int = int(val * 32767)
        buf[i * 2] = sample_int
        buf[i * 2 + 1] = sample_int
    return pygame.mixer.Sound(buffer=buf)

SFX = {
    'clear': generate_tone(880, 0.1, 0.4),
    'drop': generate_tone(150, 0.05, 0.3),
    'move': generate_tone(300, 0.03, 0.15),
    'rotate': generate_tone(400, 0.05, 0.2),
    'gameover': generate_tone(200, 0.5, 0.4),
    'select': generate_tone(600, 0.08, 0.25),
}

music_channel = pygame.mixer.Channel(0)

def play_music():
    music_channel.play(TETRIS_THEME, loops=-1)

def stop_music():
    music_channel.stop()

def pause_music():
    music_channel.pause()

def unpause_music():
    music_channel.unpause()

SHAPES = {
    'I': [[(0,1),(1,1),(2,1),(3,1)], [(2,0),(2,1),(2,2),(2,3)], [(0,2),(1,2),(2,2),(3,2)], [(1,0),(1,1),(1,2),(1,3)]],
    'O': [[(1,0),(2,0),(1,1),(2,1)], [(1,0),(2,0),(1,1),(2,1)], [(1,0),(2,0),(1,1),(2,1)], [(1,0),(2,0),(1,1),(2,1)]],
    'T': [[(1,0),(0,1),(1,1),(2,1)], [(1,0),(1,1),(2,1),(1,2)], [(0,1),(1,1),(2,1),(1,2)], [(1,0),(0,1),(1,1),(1,2)]],
    'S': [[(1,0),(2,0),(0,1),(1,1)], [(1,0),(1,1),(2,1),(2,2)], [(1,1),(2,1),(0,2),(1,2)], [(0,0),(0,1),(1,1),(1,2)]],
    'Z': [[(0,0),(1,0),(1,1),(2,1)], [(2,0),(1,1),(2,1),(1,2)], [(0,1),(1,1),(1,2),(2,2)], [(1,0),(0,1),(1,1),(0,2)]],
    'J': [[(0,0),(0,1),(1,1),(2,1)], [(1,0),(2,0),(1,1),(1,2)], [(0,1),(1,1),(2,1),(2,2)], [(1,0),(1,1),(0,2),(1,2)]],
    'L': [[(2,0),(0,1),(1,1),(2,1)], [(1,0),(1,1),(1,2),(2,2)], [(0,1),(1,1),(2,1),(0,2)], [(0,0),(1,0),(1,1),(1,2)]]
}
COLORS = {'I': CYAN, 'O': YELLOW, 'T': PURPLE, 'S': GREEN, 'Z': RED, 'J': BLUE, 'L': ORANGE}

class Piece:
    def __init__(self, shape_type=None):
        self.type = shape_type or random.choice(list(SHAPES.keys()))
        self.rotation = 0
        self.x = COLS // 2 - 2
        self.y = 0
        self.color = COLORS[self.type]
    
    def blocks(self):
        return [(self.x + dx, self.y + dy) for dx, dy in SHAPES[self.type][self.rotation]]
    
    def rotate(self, direction=1):
        self.rotation = (self.rotation + direction) % 4

class Game:
    def __init__(self):
        self.font_big = pygame.font.Font(None, 52)
        self.font_med = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 28)
        self.font_tiny = pygame.font.Font(None, 22)
        self.state = "menu"
        self.menu_selection = 0
        self.menu_items = ["Play Game", "How to Play", "Credits", "About", "Exit Game"]
        self.high_score = 0
        self.reset()
    
    def reset(self):
        self.grid = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.piece = Piece()
        self.next_piece = Piece()
        self.score = 0
        self.lines = 0
        self.level = 1
        self.fall_time = 0
        self.fall_speed = 500
        self.game_over = False
        self.paused = False
    
    def valid_position(self, piece, dx=0, dy=0, rotation=None):
        rot = rotation if rotation is not None else piece.rotation
        for bx, by in SHAPES[piece.type][rot]:
            x = piece.x + bx + dx
            y = piece.y + by + dy
            if x < 0 or x >= COLS or y >= ROWS:
                return False
            if y >= 0 and self.grid[y][x] is not None:
                return False
        return True
    
    def lock_piece(self):
        for x, y in self.piece.blocks():
            if y >= 0:
                self.grid[y][x] = self.piece.color
        SFX['drop'].play()
        self.clear_lines()
        self.piece = self.next_piece
        self.next_piece = Piece()
        if not self.valid_position(self.piece):
            self.game_over = True
            stop_music()
            SFX['gameover'].play()
            if self.score > self.high_score:
                self.high_score = self.score
    
    def clear_lines(self):
        cleared = 0
        y = ROWS - 1
        while y >= 0:
            if all(self.grid[y][x] is not None for x in range(COLS)):
                del self.grid[y]
                self.grid.insert(0, [None for _ in range(COLS)])
                cleared += 1
            else:
                y -= 1
        if cleared > 0:
            SFX['clear'].play()
            self.lines += cleared
            points = [0, 100, 300, 500, 800]
            self.score += points[cleared] * self.level
            self.level = self.lines // 10 + 1
            self.fall_speed = max(50, 500 - (self.level - 1) * 40)
    
    def move(self, dx):
        if self.valid_position(self.piece, dx=dx):
            self.piece.x += dx
            SFX['move'].play()
    
    def rotate_piece(self, direction=1):
        new_rot = (self.piece.rotation + direction) % 4
        if self.valid_position(self.piece, rotation=new_rot):
            self.piece.rotate(direction)
            SFX['rotate'].play()
        elif self.valid_position(self.piece, dx=1, rotation=new_rot):
            self.piece.x += 1
            self.piece.rotate(direction)
            SFX['rotate'].play()
        elif self.valid_position(self.piece, dx=-1, rotation=new_rot):
            self.piece.x -= 1
            self.piece.rotate(direction)
            SFX['rotate'].play()
    
    def soft_drop(self):
        if self.valid_position(self.piece, dy=1):
            self.piece.y += 1
            self.score += 1
    
    def hard_drop(self):
        while self.valid_position(self.piece, dy=1):
            self.piece.y += 1
            self.score += 2
        self.lock_piece()
    
    def update(self, dt):
        if self.game_over or self.paused:
            return
        self.fall_time += dt
        if self.fall_time >= self.fall_speed:
            self.fall_time = 0
            if self.valid_position(self.piece, dy=1):
                self.piece.y += 1
            else:
                self.lock_piece()
    
    def ghost_y(self):
        ghost_y = self.piece.y
        while self.valid_position(self.piece, dy=ghost_y - self.piece.y + 1):
            ghost_y += 1
        return ghost_y
    
    def draw_block(self, x, y, color, ghost=False):
        rect = pygame.Rect(x * BLOCK, y * BLOCK, BLOCK - 1, BLOCK - 1)
        if ghost:
            pygame.draw.rect(screen, color, rect, 2)
        else:
            pygame.draw.rect(screen, color, rect)
            lighter = tuple(min(c + 50, 255) for c in color)
            pygame.draw.line(screen, lighter, (x*BLOCK, y*BLOCK), (x*BLOCK+BLOCK-2, y*BLOCK), 2)
            pygame.draw.line(screen, lighter, (x*BLOCK, y*BLOCK), (x*BLOCK, y*BLOCK+BLOCK-2), 2)
    
    def draw_text_centered(self, text, font, color, y):
        rendered = font.render(text, True, color)
        screen.blit(rendered, (WIDTH//2 - rendered.get_width()//2, y))
    
    def draw_menu(self):
        screen.fill(BLACK)
        self.draw_text_centered("Cat's Ultra!", self.font_big, CYAN, 50)
        self.draw_text_centered("TETRIS", self.font_big, WHITE, 100)
        self.draw_text_centered("1.x", self.font_small, GRAY, 150)
        
        for i, item in enumerate(self.menu_items):
            y = 210 + i * 42
            if i == self.menu_selection:
                color = YELLOW
                prefix = "> "
            else:
                color = WHITE
                prefix = "  "
            self.draw_text_centered(prefix + item, self.font_med, color, y)
        
        if self.high_score > 0:
            self.draw_text_centered(f"High Score: {self.high_score}", self.font_small, CYAN, HEIGHT - 100)
        
        # Copyright notices
        self.draw_text_centered("(C) Samsoft 1999-2026", self.font_tiny, GRAY, HEIGHT - 55)
        self.draw_text_centered("Tetris (C) 1985 The Tetris Company", self.font_tiny, GRAY, HEIGHT - 35)
    
    def draw_howtoplay(self):
        screen.fill(BLACK)
        self.draw_text_centered("HOW TO PLAY", self.font_big, CYAN, 40)
        
        instructions = [
            "", "LEFT / RIGHT - Move piece", "UP - Rotate clockwise",
            "Z - Rotate counter-clockwise", "DOWN - Soft drop", "SPACE - Hard drop",
            "P - Pause game", "ESC - Return to menu", "",
            "Clear lines to score points!", "Clear 4 lines for a TETRIS!", "",
            "Speed increases every 10 lines.",
        ]
        
        for i, line in enumerate(instructions):
            self.draw_text_centered(line, self.font_small, WHITE if line else GRAY, 100 + i * 30)
        
        self.draw_text_centered("Press ENTER or ESC to return", self.font_tiny, YELLOW, HEIGHT - 40)
    
    def draw_credits(self):
        screen.fill(BLACK)
        self.draw_text_centered("CREDITS", self.font_big, CYAN, 50)
        
        credits_data = [
            ("", WHITE),
            ("Programming", GRAY),
            ("Samsoft / Team Flames", WHITE),
            ("", WHITE),
            ("Music", GRAY),
            ("Korobeiniki (Traditional Russian)", WHITE),
            ("", WHITE),
            ("Original Tetris", GRAY),
            ("Alexey Pajitnov - 1985", WHITE),
            ("", WHITE),
            ("Made with Python & Pygame", WHITE),
            ("", WHITE),
            ("(C) Samsoft 1999-2026", YELLOW),
            ("Tetris (C) 1985 The Tetris Company", GRAY),
        ]
        
        for i, (line, color) in enumerate(credits_data):
            self.draw_text_centered(line, self.font_small, color, 110 + i * 30)
        
        self.draw_text_centered("Press ENTER or ESC to return", self.font_tiny, YELLOW, HEIGHT - 40)
    
    def draw_about(self):
        screen.fill(BLACK)
        self.draw_text_centered("ABOUT", self.font_big, CYAN, 40)
        
        about_data = [
            ("", WHITE),
            ("Cat's Ultra! Tetris 1.x", YELLOW),
            ("", WHITE),
            ("A loving recreation of the", WHITE),
            ("classic puzzle game that has", WHITE),
            ("captivated players since 1985.", WHITE),
            ("", WHITE),
            ("Tetris was created by", WHITE),
            ("Alexey Pajitnov in the USSR.", WHITE),
            ("", WHITE),
            ("The iconic theme 'Korobeiniki'", WHITE),
            ("is a 19th century Russian folk song.", WHITE),
            ("", WHITE),
            ("(C) Samsoft 1999-2026", YELLOW),
            ("Tetris (C) 1985 The Tetris Company", GRAY),
        ]
        
        for i, (line, color) in enumerate(about_data):
            self.draw_text_centered(line, self.font_small, color, 90 + i * 28)
        
        self.draw_text_centered("Press ENTER or ESC to return", self.font_tiny, YELLOW, HEIGHT - 40)
    
    def draw_game(self):
        screen.fill(DARK)
        
        for y in range(ROWS):
            for x in range(COLS):
                pygame.draw.rect(screen, (35, 35, 35), (x*BLOCK, y*BLOCK, BLOCK-1, BLOCK-1), 1)
        
        for y in range(ROWS):
            for x in range(COLS):
                if self.grid[y][x]:
                    self.draw_block(x, y, self.grid[y][x])
        
        ghost_y = self.ghost_y()
        for bx, by in SHAPES[self.piece.type][self.piece.rotation]:
            gx, gy = self.piece.x + bx, ghost_y + by
            if gy >= 0:
                self.draw_block(gx, gy, self.piece.color, ghost=True)
        
        for x, y in self.piece.blocks():
            if y >= 0:
                self.draw_block(x, y, self.piece.color)
        
        sidebar_x = COLS * BLOCK + 10
        pygame.draw.line(screen, GRAY, (COLS*BLOCK, 0), (COLS*BLOCK, HEIGHT), 2)
        
        screen.blit(self.font_small.render("SCORE", True, WHITE), (sidebar_x, 20))
        screen.blit(self.font_med.render(str(self.score), True, CYAN), (sidebar_x, 45))
        screen.blit(self.font_small.render("LEVEL", True, WHITE), (sidebar_x, 100))
        screen.blit(self.font_med.render(str(self.level), True, GREEN), (sidebar_x, 125))
        screen.blit(self.font_small.render("LINES", True, WHITE), (sidebar_x, 180))
        screen.blit(self.font_med.render(str(self.lines), True, YELLOW), (sidebar_x, 205))
        screen.blit(self.font_small.render("NEXT", True, WHITE), (sidebar_x, 280))
        
        for dx, dy in SHAPES[self.next_piece.type][0]:
            pygame.draw.rect(screen, self.next_piece.color, (sidebar_x+20+dx*20, 320+dy*20, 18, 18))
        
        # Copyright in sidebar
        copyright_font = pygame.font.Font(None, 16)
        screen.blit(copyright_font.render("(C) Samsoft", True, GRAY), (sidebar_x, HEIGHT - 45))
        screen.blit(copyright_font.render("1999-2026", True, GRAY), (sidebar_x, HEIGHT - 30))
        
        if self.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            self.draw_text_centered("GAME OVER", self.font_big, RED, HEIGHT//2 - 60)
            self.draw_text_centered(f"Score: {self.score}", self.font_med, WHITE, HEIGHT//2)
            self.draw_text_centered("R = Restart  ESC = Menu", self.font_small, GRAY, HEIGHT//2 + 50)
        
        if self.paused:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            self.draw_text_centered("PAUSED", self.font_big, WHITE, HEIGHT//2 - 20)
            self.draw_text_centered("Press P to continue", self.font_small, GRAY, HEIGHT//2 + 30)
    
    def draw(self):
        if self.state == "menu":
            self.draw_menu()
        elif self.state == "howtoplay":
            self.draw_howtoplay()
        elif self.state == "credits":
            self.draw_credits()
        elif self.state == "about":
            self.draw_about()
        else:
            self.draw_game()
        pygame.display.flip()
    
    def menu_select(self):
        SFX['select'].play()
        if self.menu_selection == 0:
            self.reset()
            self.state = "playing"
            play_music()
        elif self.menu_selection == 1:
            self.state = "howtoplay"
        elif self.menu_selection == 2:
            self.state = "credits"
        elif self.menu_selection == 3:
            self.state = "about"
        elif self.menu_selection == 4:
            return False
        return True

def main():
    clock = pygame.time.Clock()
    game = Game()
    running = True
    
    while running:
        dt = clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if game.state == "menu":
                    if event.key == pygame.K_UP:
                        game.menu_selection = (game.menu_selection - 1) % len(game.menu_items)
                        SFX['move'].play()
                    elif event.key == pygame.K_DOWN:
                        game.menu_selection = (game.menu_selection + 1) % len(game.menu_items)
                        SFX['move'].play()
                    elif event.key == pygame.K_RETURN:
                        running = game.menu_select()
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                
                elif game.state in ["howtoplay", "credits", "about"]:
                    if event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                        game.state = "menu"
                        SFX['select'].play()
                
                elif game.state == "playing":
                    if game.game_over:
                        if event.key == pygame.K_r:
                            game.reset()
                            play_music()
                        elif event.key == pygame.K_ESCAPE:
                            game.state = "menu"
                    elif game.paused:
                        if event.key in (pygame.K_p, pygame.K_ESCAPE):
                            game.paused = False
                            unpause_music()
                    else:
                        if event.key == pygame.K_LEFT:
                            game.move(-1)
                        elif event.key == pygame.K_RIGHT:
                            game.move(1)
                        elif event.key == pygame.K_UP:
                            game.rotate_piece(1)
                        elif event.key == pygame.K_z:
                            game.rotate_piece(-1)
                        elif event.key == pygame.K_DOWN:
                            game.soft_drop()
                        elif event.key == pygame.K_SPACE:
                            game.hard_drop()
                        elif event.key == pygame.K_p:
                            game.paused = True
                            pause_music()
                        elif event.key == pygame.K_ESCAPE:
                            stop_music()
                            game.state = "menu"
        
        if game.state == "playing" and not game.game_over and not game.paused:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_DOWN]:
                game.fall_speed = 50
            else:
                game.fall_speed = max(50, 500 - (game.level - 1) * 40)
        
        if game.state == "playing":
            game.update(dt)
        
        game.draw()
    
    pygame.quit()

if __name__ == "__main__":
    main()
