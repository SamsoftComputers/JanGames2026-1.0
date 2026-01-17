#!/usr/bin/env python3
"""
ULTRA!PONG - A Complete NES-Style Pong Game
Features: Main Menu, How to Play, Credits, Play, Exit
NES 8-bit graphics aesthetic with authentic color palette
[C] Mr.Samsoft / 1999-2026 Atari
"""

import pygame
import sys
import random
import math

# Initialize Pygame
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# NES Color Palette (authentic 2C02 PPU colors)
NES_COLORS = {
    'black': (0, 0, 0),
    'dark_gray': (60, 60, 60),
    'gray': (124, 124, 124),
    'white': (252, 252, 252),
    'red': (184, 0, 0),
    'bright_red': (248, 56, 0),
    'orange': (252, 116, 0),
    'yellow': (252, 188, 60),
    'green': (0, 168, 0),
    'bright_green': (88, 216, 84),
    'cyan': (0, 232, 216),
    'blue': (0, 88, 248),
    'bright_blue': (60, 188, 252),
    'purple': (148, 0, 132),
    'pink': (248, 120, 248),
    'brown': (136, 52, 0),
    'tan': (196, 132, 68),
}

# Screen setup (NES resolution scaled up)
NES_WIDTH, NES_HEIGHT = 256, 240
SCALE = 3
SCREEN_WIDTH = NES_WIDTH * SCALE
SCREEN_HEIGHT = NES_HEIGHT * SCALE

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("ULTRA!PONG")
clock = pygame.time.Clock()

# Create NES-sized surface for authentic rendering
nes_surface = pygame.Surface((NES_WIDTH, NES_HEIGHT))


def generate_beep(frequency=440, duration=0.1, volume=0.3):
    """Generate NES-style square wave beep sound"""
    sample_rate = 22050
    n_samples = int(sample_rate * duration)

    buf = []
    for i in range(n_samples):
        t = i / sample_rate
        val = 1 if (t * frequency) % 1 < 0.5 else -1
        envelope = 1.0 - (i / n_samples) * 0.5
        sample = int(val * volume * 32767 * envelope)
        buf.append(sample)

    sound_data = b''
    for sample in buf:
        sample = max(-32768, min(32767, sample))
        sound_data += sample.to_bytes(2, 'little', signed=True) * 2

    return pygame.mixer.Sound(buffer=sound_data)


# Generate sounds
try:
    SFX_PADDLE = generate_beep(440, 0.05, 0.4)
    SFX_WALL = generate_beep(220, 0.05, 0.3)
    SFX_SCORE = generate_beep(880, 0.2, 0.4)
    SFX_SELECT = generate_beep(660, 0.08, 0.3)
    SFX_CONFIRM = generate_beep(523, 0.15, 0.4)
except:
    SFX_PADDLE = SFX_WALL = SFX_SCORE = SFX_SELECT = SFX_CONFIRM = None


def play_sound(sound):
    """Safely play a sound"""
    if sound:
        try:
            sound.play()
        except:
            pass


# NES-style 8x8 pixel font
FONT_DATA = {
    'A': ['  XX  ', ' X  X ', ' X  X ', ' XXXX ', ' X  X ', ' X  X ', ' X  X ', '      '],
    'B': [' XXX  ', ' X  X ', ' X  X ', ' XXX  ', ' X  X ', ' X  X ', ' XXX  ', '      '],
    'C': ['  XXX ', ' X    ', ' X    ', ' X    ', ' X    ', ' X    ', '  XXX ', '      '],
    'D': [' XXX  ', ' X  X ', ' X  X ', ' X  X ', ' X  X ', ' X  X ', ' XXX  ', '      '],
    'E': [' XXXX ', ' X    ', ' X    ', ' XXX  ', ' X    ', ' X    ', ' XXXX ', '      '],
    'F': [' XXXX ', ' X    ', ' X    ', ' XXX  ', ' X    ', ' X    ', ' X    ', '      '],
    'G': ['  XXX ', ' X    ', ' X    ', ' X XX ', ' X  X ', ' X  X ', '  XXX ', '      '],
    'H': [' X  X ', ' X  X ', ' X  X ', ' XXXX ', ' X  X ', ' X  X ', ' X  X ', '      '],
    'I': ['  XXX ', '   X  ', '   X  ', '   X  ', '   X  ', '   X  ', '  XXX ', '      '],
    'J': ['  XXX ', '    X ', '    X ', '    X ', '    X ', ' X  X ', '  XX  ', '      '],
    'K': [' X  X ', ' X  X ', ' X X  ', ' XX   ', ' X X  ', ' X  X ', ' X  X ', '      '],
    'L': [' X    ', ' X    ', ' X    ', ' X    ', ' X    ', ' X    ', ' XXXX ', '      '],
    'M': [' X  X ', ' XXXX ', ' X XX ', ' X  X ', ' X  X ', ' X  X ', ' X  X ', '      '],
    'N': [' X  X ', ' XX X ', ' XX X ', ' X XX ', ' X XX ', ' X  X ', ' X  X ', '      '],
    'O': ['  XX  ', ' X  X ', ' X  X ', ' X  X ', ' X  X ', ' X  X ', '  XX  ', '      '],
    'P': [' XXX  ', ' X  X ', ' X  X ', ' XXX  ', ' X    ', ' X    ', ' X    ', '      '],
    'Q': ['  XX  ', ' X  X ', ' X  X ', ' X  X ', ' X XX ', ' X  X ', '  XX X', '      '],
    'R': [' XXX  ', ' X  X ', ' X  X ', ' XXX  ', ' X X  ', ' X  X ', ' X  X ', '      '],
    'S': ['  XXX ', ' X    ', ' X    ', '  XX  ', '    X ', '    X ', ' XXX  ', '      '],
    'T': [' XXXXX', '   X  ', '   X  ', '   X  ', '   X  ', '   X  ', '   X  ', '      '],
    'U': [' X  X ', ' X  X ', ' X  X ', ' X  X ', ' X  X ', ' X  X ', '  XX  ', '      '],
    'V': [' X  X ', ' X  X ', ' X  X ', ' X  X ', ' X  X ', '  XX  ', '   X  ', '      '],
    'W': [' X  X ', ' X  X ', ' X  X ', ' X  X ', ' X XX ', ' XXXX ', ' X  X ', '      '],
    'X': [' X  X ', ' X  X ', '  XX  ', '   X  ', '  XX  ', ' X  X ', ' X  X ', '      '],
    'Y': [' X  X ', ' X  X ', ' X  X ', '  XX  ', '   X  ', '   X  ', '   X  ', '      '],
    'Z': [' XXXX ', '    X ', '   X  ', '  X   ', ' X    ', ' X    ', ' XXXX ', '      '],
    '0': ['  XX  ', ' X  X ', ' X  X ', ' X  X ', ' X  X ', ' X  X ', '  XX  ', '      '],
    '1': ['   X  ', '  XX  ', '   X  ', '   X  ', '   X  ', '   X  ', '  XXX ', '      '],
    '2': ['  XX  ', ' X  X ', '    X ', '   X  ', '  X   ', ' X    ', ' XXXX ', '      '],
    '3': ['  XX  ', ' X  X ', '    X ', '   X  ', '    X ', ' X  X ', '  XX  ', '      '],
    '4': ['    X ', '   XX ', '  X X ', ' X  X ', ' XXXX ', '    X ', '    X ', '      '],
    '5': [' XXXX ', ' X    ', ' XXX  ', '    X ', '    X ', ' X  X ', '  XX  ', '      '],
    '6': ['  XXX ', ' X    ', ' X    ', ' XXX  ', ' X  X ', ' X  X ', '  XX  ', '      '],
    '7': [' XXXX ', '    X ', '   X  ', '   X  ', '  X   ', '  X   ', '  X   ', '      '],
    '8': ['  XX  ', ' X  X ', ' X  X ', '  XX  ', ' X  X ', ' X  X ', '  XX  ', '      '],
    '9': ['  XX  ', ' X  X ', ' X  X ', '  XXX ', '    X ', '    X ', ' XXX  ', '      '],
    ' ': ['      ', '      ', '      ', '      ', '      ', '      ', '      ', '      '],
    '!': ['   X  ', '   X  ', '   X  ', '   X  ', '   X  ', '      ', '   X  ', '      '],
    '.': ['      ', '      ', '      ', '      ', '      ', '      ', '  X   ', '      '],
    ',': ['      ', '      ', '      ', '      ', '      ', '  X   ', '  X   ', ' X    '],
    ':': ['      ', '  X   ', '      ', '      ', '      ', '  X   ', '      ', '      '],
    '-': ['      ', '      ', '      ', ' XXXX ', '      ', '      ', '      ', '      '],
    '/': ['    X ', '    X ', '   X  ', '  X   ', '  X   ', ' X    ', ' X    ', '      '],
    '(': ['   X  ', '  X   ', ' X    ', ' X    ', ' X    ', '  X   ', '   X  ', '      '],
    ')': ['  X   ', '   X  ', '    X ', '    X ', '    X ', '   X  ', '  X   ', '      '],
    "'": ['  X   ', '  X   ', ' X    ', '      ', '      ', '      ', '      ', '      '],
}


def draw_char(surface, char, x, y, color):
    """Draw a single 8x8 character"""
    char = char.upper()
    if char not in FONT_DATA:
        return

    for row_idx, row in enumerate(FONT_DATA[char]):
        for col_idx, pixel in enumerate(row):
            if pixel == 'X':
                surface.set_at((x + col_idx, y + row_idx), color)


def draw_text(surface, text, x, y, color, centered=False):
    """Draw text using NES-style font"""
    if centered:
        text_width = len(text) * 6
        x = x - text_width // 2

    for i, char in enumerate(text):
        draw_char(surface, char, x + i * 6, y, color)


def draw_big_text(surface, text, x, y, color, centered=False, scale=2):
    """Draw larger text by scaling"""
    if centered:
        text_width = len(text) * 6 * scale
        x = x - text_width // 2

    for i, char in enumerate(text):
        char = char.upper()
        if char not in FONT_DATA:
            continue
        for row_idx, row in enumerate(FONT_DATA[char]):
            for col_idx, pixel in enumerate(row):
                if pixel == 'X':
                    for sy in range(scale):
                        for sx in range(scale):
                            px = x + i * 6 * scale + col_idx * scale + sx
                            py = y + row_idx * scale + sy
                            if 0 <= px < NES_WIDTH and 0 <= py < NES_HEIGHT:
                                surface.set_at((px, py), color)


class Ball:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = NES_WIDTH // 2
        self.y = NES_HEIGHT // 2
        self.dx = random.choice([-2, 2])
        self.dy = random.choice([-1.5, -1, 1, 1.5])
        self.size = 4

    def update(self):
        self.x += self.dx
        self.y += self.dy

        # Top/bottom wall collision
        if self.y <= 16:
            self.y = 16
            self.dy = -self.dy
            play_sound(SFX_WALL)
        elif self.y >= NES_HEIGHT - 16 - self.size:
            self.y = NES_HEIGHT - 16 - self.size
            self.dy = -self.dy
            play_sound(SFX_WALL)

    def draw(self, surface):
        pygame.draw.rect(surface, NES_COLORS['white'],
                        (int(self.x), int(self.y), self.size, self.size))
        surface.set_at((int(self.x), int(self.y)), NES_COLORS['bright_blue'])


class Paddle:
    def __init__(self, x, is_ai=False):
        self.x = x
        self.y = NES_HEIGHT // 2 - 16
        self.width = 4
        self.height = 32
        self.speed = 2
        self.is_ai = is_ai
        self.score = 0

    def update(self, ball=None, mouse_y=None):
        if self.is_ai and ball:
            # AI: follow the ball
            target_y = ball.y - self.height // 2
            if self.y < target_y - 2:
                self.y += self.speed * 0.8
            elif self.y > target_y + 2:
                self.y -= self.speed * 0.8
        elif mouse_y is not None:
            # Mouse control for player - convert screen coords to NES coords
            nes_mouse_y = mouse_y / SCALE
            self.y = nes_mouse_y - self.height // 2

        # Keep paddle in bounds
        if self.y < 16:
            self.y = 16
        if self.y > NES_HEIGHT - 16 - self.height:
            self.y = NES_HEIGHT - 16 - self.height

    def draw(self, surface):
        pygame.draw.rect(surface, NES_COLORS['white'],
                        (self.x, int(self.y), self.width, self.height))
        for i in range(self.height):
            surface.set_at((self.x, int(self.y) + i), NES_COLORS['bright_blue'])


class Game:
    def __init__(self):
        self.state = 'menu'
        self.menu_selection = 0
        self.menu_items = ['PLAY', 'HOW TO PLAY', 'CREDITS', 'EXIT']
        self.frame_count = 0
        self.winning_score = 5  # First to 5 wins!

        # Game objects
        self.ball = Ball()
        self.player = Paddle(16)
        self.opponent = Paddle(NES_WIDTH - 20, is_ai=True)

        # Stars background for menu
        self.stars = [(random.randint(0, NES_WIDTH),
                      random.randint(0, NES_HEIGHT),
                      random.choice([1, 1, 1, 2])) for _ in range(50)]

    def reset_game(self):
        self.ball.reset()
        self.player.y = NES_HEIGHT // 2 - 16
        self.player.score = 0
        self.opponent.y = NES_HEIGHT // 2 - 16
        self.opponent.score = 0

    def draw_border(self, surface):
        """Draw NES-style border"""
        pygame.draw.rect(surface, NES_COLORS['blue'], (0, 0, NES_WIDTH, 16))
        pygame.draw.rect(surface, NES_COLORS['bright_blue'], (0, 14, NES_WIDTH, 2))

        pygame.draw.rect(surface, NES_COLORS['blue'], (0, NES_HEIGHT - 16, NES_WIDTH, 16))
        pygame.draw.rect(surface, NES_COLORS['bright_blue'], (0, NES_HEIGHT - 16, NES_WIDTH, 2))

        # Center dashed line
        for i in range(16, NES_HEIGHT - 16, 8):
            if (i // 8) % 2 == 0:
                pygame.draw.rect(surface, NES_COLORS['gray'],
                               (NES_WIDTH // 2 - 1, i, 2, 4))

    def draw_stars(self, surface):
        """Animated starfield background"""
        for i, (x, y, size) in enumerate(self.stars):
            brightness = abs(math.sin(self.frame_count * 0.05 + i * 0.5))
            if brightness > 0.7:
                color = NES_COLORS['white']
            elif brightness > 0.4:
                color = NES_COLORS['gray']
            else:
                color = NES_COLORS['dark_gray']

            if size == 1:
                surface.set_at((x, y), color)
            else:
                pygame.draw.rect(surface, color, (x, y, 2, 2))

    def draw_menu(self, surface):
        """Draw main menu screen"""
        surface.fill(NES_COLORS['black'])
        self.draw_stars(surface)

        # Title with rainbow effect
        title_colors = [NES_COLORS['red'], NES_COLORS['orange'], NES_COLORS['yellow'],
                       NES_COLORS['green'], NES_COLORS['cyan'], NES_COLORS['blue'],
                       NES_COLORS['purple'], NES_COLORS['pink'], NES_COLORS['red']]

        title = "ULTRA!PONG"
        for i, char in enumerate(title):
            color_idx = (i + self.frame_count // 8) % len(title_colors)
            draw_big_text(surface, char, 48 + i * 16, 40, title_colors[color_idx])

        # Subtitle
        draw_text(surface, "NES EDITION", NES_WIDTH // 2, 75, NES_COLORS['cyan'], centered=True)

        # Menu items
        for i, item in enumerate(self.menu_items):
            y = 110 + i * 20
            if i == self.menu_selection:
                if self.frame_count % 30 < 20:
                    draw_text(surface, ">", NES_WIDTH // 2 - 50, y, NES_COLORS['yellow'])
                draw_text(surface, item, NES_WIDTH // 2, y, NES_COLORS['yellow'], centered=True)
            else:
                draw_text(surface, item, NES_WIDTH // 2, y, NES_COLORS['white'], centered=True)

        # Footer
        draw_text(surface, "USE ARROWS TO SELECT", NES_WIDTH // 2, 200,
                 NES_COLORS['gray'], centered=True)
        draw_text(surface, "PRESS ENTER TO CONFIRM", NES_WIDTH // 2, 212,
                 NES_COLORS['gray'], centered=True)

    def draw_how_to_play(self, surface):
        """Draw how to play screen"""
        surface.fill(NES_COLORS['black'])
        self.draw_stars(surface)

        draw_big_text(surface, "HOW TO PLAY", NES_WIDTH // 2, 20,
                     NES_COLORS['cyan'], centered=True)

        instructions = [
            "PLAYER CONTROLS:",
            "MOUSE - MOVE PADDLE",
            "",
            "RULES:",
            "- FIRST TO 5 WINS",
            "- HIT BALL WITH PADDLE",
            "- DONT LET BALL PASS",
            "",
            "TIPS:",
            "- AIM FOR CORNERS",
            "- WATCH THE BALL SPEED"
        ]

        y = 55
        for line in instructions:
            if line.endswith(':'):
                draw_text(surface, line, 30, y, NES_COLORS['yellow'])
            elif line.startswith('-'):
                draw_text(surface, line, 40, y, NES_COLORS['white'])
            elif line:
                draw_text(surface, line, 40, y, NES_COLORS['bright_green'])
            y += 14

        if self.frame_count % 60 < 40:
            draw_text(surface, "PRESS ESC TO GO BACK", NES_WIDTH // 2, 220,
                     NES_COLORS['gray'], centered=True)

    def draw_credits(self, surface):
        """Draw credits screen"""
        surface.fill(NES_COLORS['black'])
        self.draw_stars(surface)

        draw_big_text(surface, "CREDITS", NES_WIDTH // 2, 30,
                     NES_COLORS['pink'], centered=True)

        credits_text = [
            "",
            "ULTRA!PONG",
            "NES EDITION",
            "",
            "(C) MR.SAMSOFT",
            "",
            "(C) 1999-2026 ATARI",
            "",
            "GRAPHICS:",
            "8-BIT NES STYLE",
            "",
            "SOUND:",
            "SQUARE WAVE SYNTH",
            "",
            "THANK YOU",
            "FOR PLAYING!"
        ]

        y = 50
        for line in credits_text:
            if line in ['ULTRA!PONG', '(C) MR.SAMSOFT', '(C) 1999-2026 ATARI',
                       '8-BIT NES STYLE', 'SQUARE WAVE SYNTH', 'FOR PLAYING!']:
                draw_text(surface, line, NES_WIDTH // 2, y, NES_COLORS['yellow'], centered=True)
            elif line.endswith(':'):
                draw_text(surface, line, NES_WIDTH // 2, y, NES_COLORS['cyan'], centered=True)
            else:
                draw_text(surface, line, NES_WIDTH // 2, y, NES_COLORS['white'], centered=True)
            y += 10

        if self.frame_count % 60 < 40:
            draw_text(surface, "PRESS ESC TO GO BACK", NES_WIDTH // 2, 220,
                     NES_COLORS['gray'], centered=True)

    def draw_game(self, surface):
        """Draw main game screen"""
        surface.fill(NES_COLORS['black'])
        self.draw_border(surface)

        # Draw scores in border
        draw_big_text(surface, str(self.player.score), NES_WIDTH // 4, 2,
                     NES_COLORS['white'], centered=True)
        draw_big_text(surface, str(self.opponent.score), 3 * NES_WIDTH // 4, 2,
                     NES_COLORS['white'], centered=True)

        # Draw game objects
        self.player.draw(surface)
        self.opponent.draw(surface)
        self.ball.draw(surface)

    def draw_game_over(self, surface):
        """Draw game over screen with Y/N prompt"""
        surface.fill(NES_COLORS['black'])
        self.draw_border(surface)

        # Determine winner
        if self.player.score >= self.winning_score:
            winner_text = "YOU WIN!"
            color = NES_COLORS['bright_green']
        else:
            winner_text = "CPU WINS!"
            color = NES_COLORS['red']

        draw_big_text(surface, winner_text, NES_WIDTH // 2, 60, color, centered=True)

        # Final score
        draw_text(surface, "FINAL SCORE", NES_WIDTH // 2, 100,
                 NES_COLORS['white'], centered=True)
        draw_big_text(surface, f"{self.player.score} - {self.opponent.score}",
                     NES_WIDTH // 2, 115, NES_COLORS['yellow'], centered=True)

        # Game over text
        draw_big_text(surface, "GAME OVER", NES_WIDTH // 2, 145,
                     NES_COLORS['cyan'], centered=True)

        # Y/N Prompt
        if self.frame_count % 60 < 40:
            draw_text(surface, "PLAY AGAIN?", NES_WIDTH // 2, 175,
                     NES_COLORS['white'], centered=True)
            draw_text(surface, "Y - RESTART", NES_WIDTH // 2, 190,
                     NES_COLORS['bright_green'], centered=True)
            draw_text(surface, "N - QUIT", NES_WIDTH // 2, 205,
                     NES_COLORS['red'], centered=True)

    def handle_menu_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.menu_selection = (self.menu_selection - 1) % len(self.menu_items)
                play_sound(SFX_SELECT)
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.menu_selection = (self.menu_selection + 1) % len(self.menu_items)
                play_sound(SFX_SELECT)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE, pygame.K_z):
                self.confirm_menu_selection()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check if clicked on a menu item
            mouse_x, mouse_y = event.pos
            nes_y = mouse_y / SCALE
            for i, item in enumerate(self.menu_items):
                item_y = 110 + i * 20
                if item_y <= nes_y <= item_y + 12:
                    self.menu_selection = i
                    self.confirm_menu_selection()
                    break
    
    def confirm_menu_selection(self):
        play_sound(SFX_CONFIRM)
        selected = self.menu_items[self.menu_selection]
        if selected == 'PLAY':
            self.reset_game()
            self.state = 'playing'
        elif selected == 'HOW TO PLAY':
            self.state = 'howto'
        elif selected == 'CREDITS':
            self.state = 'credits'
        elif selected == 'EXIT':
            pygame.quit()
            sys.exit()

    def update_game(self):
        # Get mouse position for player control
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Update player with mouse Y position
        self.player.update(mouse_y=mouse_y)

        # Update AI opponent
        self.opponent.update(ball=self.ball)

        # Update ball
        self.ball.update()

        # Ball-paddle collision (player)
        if (self.ball.x <= self.player.x + self.player.width and
            self.ball.x >= self.player.x and
            self.ball.y + self.ball.size >= self.player.y and
            self.ball.y <= self.player.y + self.player.height):
            self.ball.x = self.player.x + self.player.width
            self.ball.dx = abs(self.ball.dx) * 1.05
            hit_pos = (self.ball.y - self.player.y) / self.player.height
            self.ball.dy = (hit_pos - 0.5) * 4
            play_sound(SFX_PADDLE)

        # Ball-paddle collision (opponent)
        if (self.ball.x + self.ball.size >= self.opponent.x and
            self.ball.x <= self.opponent.x + self.opponent.width and
            self.ball.y + self.ball.size >= self.opponent.y and
            self.ball.y <= self.opponent.y + self.opponent.height):
            self.ball.x = self.opponent.x - self.ball.size
            self.ball.dx = -abs(self.ball.dx) * 1.05
            hit_pos = (self.ball.y - self.opponent.y) / self.opponent.height
            self.ball.dy = (hit_pos - 0.5) * 4
            play_sound(SFX_PADDLE)

        # Scoring
        if self.ball.x < 0:
            self.opponent.score += 1
            play_sound(SFX_SCORE)
            self.ball.reset()
        elif self.ball.x > NES_WIDTH:
            self.player.score += 1
            play_sound(SFX_SCORE)
            self.ball.reset()

        # Check for game over (first to 5)
        if self.player.score >= self.winning_score or self.opponent.score >= self.winning_score:
            self.state = 'gameover'

    def run(self):
        running = True

        while running:
            self.frame_count += 1

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if self.state == 'menu':
                    self.handle_menu_input(event)
                elif self.state in ['howto', 'credits']:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.state = 'menu'
                        play_sound(SFX_SELECT)
                elif self.state == 'playing':
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.state = 'menu'
                        play_sound(SFX_SELECT)
                elif self.state == 'gameover':
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_y:
                            # Y = Restart
                            play_sound(SFX_CONFIRM)
                            self.reset_game()
                            self.state = 'playing'
                        elif event.key == pygame.K_n:
                            # N = Quit to menu
                            play_sound(SFX_SELECT)
                            self.state = 'menu'

            # Update game state
            if self.state == 'playing':
                self.update_game()

            # Draw to NES surface
            nes_surface.fill(NES_COLORS['black'])

            if self.state == 'menu':
                self.draw_menu(nes_surface)
            elif self.state == 'howto':
                self.draw_how_to_play(nes_surface)
            elif self.state == 'credits':
                self.draw_credits(nes_surface)
            elif self.state == 'playing':
                self.draw_game(nes_surface)
            elif self.state == 'gameover':
                self.draw_game_over(nes_surface)

            # Scale up to screen
            pygame.transform.scale(nes_surface, (SCREEN_WIDTH, SCREEN_HEIGHT), screen)

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
        sys.exit()


if __name__ == '__main__':
    game = Game()
    game.run()
