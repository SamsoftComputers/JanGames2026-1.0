#!/usr/bin/env python3
"""
SPACE INVADERS - Classic Arcade Clone
Python 3.14 Compatible | Mouse Control | No External Files
"""

import pygame
import random
import math
import array

# Initialize Pygame
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("SPACE INVADERS")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)

# Fonts
def get_font(size):
    return pygame.font.Font(None, size)

# Sound generation (beeps and boops - no external files)
def generate_beep(frequency=440, duration=0.1, volume=0.3):
    sample_rate = 22050
    n_samples = int(sample_rate * duration)
    buf = array.array('h', [0] * n_samples)
    for i in range(n_samples):
        t = i / sample_rate
        # Square wave for classic arcade sound
        val = volume * 32767 * (1 if math.sin(2 * math.pi * frequency * t) > 0 else -1)
        # Apply envelope
        envelope = min(1, min(i / 500, (n_samples - i) / 500))
        buf[i] = int(val * envelope)
    sound = pygame.mixer.Sound(buffer=buf)
    return sound

def generate_explosion(duration=0.3, volume=0.4):
    sample_rate = 22050
    n_samples = int(sample_rate * duration)
    buf = array.array('h', [0] * n_samples)
    for i in range(n_samples):
        noise = random.randint(-32767, 32767)
        envelope = (n_samples - i) / n_samples
        buf[i] = int(noise * volume * envelope)
    sound = pygame.mixer.Sound(buffer=buf)
    return sound

def generate_shoot(duration=0.1, volume=0.3):
    sample_rate = 22050
    n_samples = int(sample_rate * duration)
    buf = array.array('h', [0] * n_samples)
    for i in range(n_samples):
        t = i / sample_rate
        freq = 800 - (i / n_samples) * 600
        val = volume * 32767 * math.sin(2 * math.pi * freq * t)
        envelope = (n_samples - i) / n_samples
        buf[i] = int(val * envelope)
    sound = pygame.mixer.Sound(buffer=buf)
    return sound

def generate_invader_move(pitch=0):
    duration = 0.05
    sample_rate = 22050
    n_samples = int(sample_rate * duration)
    buf = array.array('h', [0] * n_samples)
    freq = 80 + pitch * 20
    for i in range(n_samples):
        t = i / sample_rate
        val = 0.2 * 32767 * (1 if math.sin(2 * math.pi * freq * t) > 0 else -1)
        buf[i] = int(val)
    sound = pygame.mixer.Sound(buffer=buf)
    return sound

# Generate sounds
SND_SHOOT = generate_shoot()
SND_EXPLOSION = generate_explosion()
SND_SELECT = generate_beep(660, 0.05)
SND_CONFIRM = generate_beep(880, 0.1)
SND_INVADER_MOVE = [generate_invader_move(i) for i in range(4)]

# Pixel art sprites (drawn programmatically)
def draw_player(surface, x, y, color=GREEN):
    # Classic cannon shape
    pygame.draw.rect(surface, color, (x + 20, y + 10, 10, 10))
    pygame.draw.rect(surface, color, (x + 10, y + 20, 30, 10))
    pygame.draw.rect(surface, color, (x, y + 30, 50, 10))

def draw_invader_a(surface, x, y, color=WHITE, frame=0):
    # Squid-type invader
    if frame == 0:
        pixels = [
            "    XX    ",
            "   XXXX   ",
            "  XXXXXX  ",
            " XX XX XX ",
            " XXXXXXXX ",
            "  X    X  ",
            " X      X ",
        ]
    else:
        pixels = [
            "    XX    ",
            "   XXXX   ",
            "  XXXXXX  ",
            " XX XX XX ",
            " XXXXXXXX ",
            "   X  X   ",
            "  X    X  ",
        ]
    for row, line in enumerate(pixels):
        for col, char in enumerate(line):
            if char == 'X':
                pygame.draw.rect(surface, color, (x + col * 4, y + row * 4, 4, 4))

def draw_invader_b(surface, x, y, color=CYAN, frame=0):
    # Crab-type invader
    if frame == 0:
        pixels = [
            "  X     X  ",
            "   X   X   ",
            "  XXXXXXX  ",
            " XX XXX XX ",
            "XXXXXXXXXXX",
            "X XXXXXXX X",
            "X X     X X",
            "   XX XX   ",
        ]
    else:
        pixels = [
            "  X     X  ",
            "X  X   X  X",
            "X XXXXXXX X",
            "XXX XXX XXX",
            "XXXXXXXXXXX",
            " XXXXXXXXX ",
            "  X     X  ",
            " X       X ",
        ]
    for row, line in enumerate(pixels):
        for col, char in enumerate(line):
            if char == 'X':
                pygame.draw.rect(surface, color, (x + col * 4, y + row * 4, 4, 4))

def draw_invader_c(surface, x, y, color=MAGENTA, frame=0):
    # Octopus-type invader
    if frame == 0:
        pixels = [
            "   XXXX   ",
            " XXXXXXXX ",
            "XXXXXXXXXX",
            "XXX  XX  X",
            "XXXXXXXXXX",
            "  XX  XX  ",
            " XX XX XX ",
            "XX      XX",
        ]
    else:
        pixels = [
            "   XXXX   ",
            " XXXXXXXX ",
            "XXXXXXXXXX",
            "XXX  XX  X",
            "XXXXXXXXXX",
            "  XX  XX  ",
            " XX XX XX ",
            "   X  X   ",
        ]
    for row, line in enumerate(pixels):
        for col, char in enumerate(line):
            if char == 'X':
                pygame.draw.rect(surface, color, (x + col * 4, y + row * 4, 4, 4))

def draw_ufo(surface, x, y):
    pygame.draw.ellipse(surface, RED, (x, y + 5, 50, 15))
    pygame.draw.ellipse(surface, YELLOW, (x + 15, y, 20, 12))

def draw_bunker(surface, x, y, health_grid):
    for row in range(len(health_grid)):
        for col in range(len(health_grid[row])):
            if health_grid[row][col] > 0:
                alpha = health_grid[row][col] / 4
                color = (0, int(255 * alpha), 0)
                pygame.draw.rect(surface, color, (x + col * 4, y + row * 4, 4, 4))

# Game classes
class Player:
    def __init__(self):
        self.x = SCREEN_WIDTH // 2 - 25
        self.y = SCREEN_HEIGHT - 60
        self.width = 50
        self.lives = 3
        self.score = 0

    def update(self, mouse_x):
        self.x = mouse_x - self.width // 2
        self.x = max(0, min(SCREEN_WIDTH - self.width, self.x))

    def draw(self, surface):
        draw_player(surface, self.x, self.y)

class Bullet:
    def __init__(self, x, y, speed=-10):
        self.x = x
        self.y = y
        self.speed = speed
        self.active = True

    def update(self):
        self.y += self.speed
        if self.y < 0 or self.y > SCREEN_HEIGHT:
            self.active = False

    def draw(self, surface):
        color = GREEN if self.speed < 0 else WHITE
        pygame.draw.rect(surface, color, (self.x, self.y, 4, 12))

class Invader:
    def __init__(self, x, y, invader_type):
        self.x = x
        self.y = y
        self.type = invader_type
        self.alive = True
        self.frame = 0
        self.points = {0: 30, 1: 20, 2: 10}[invader_type]

    def draw(self, surface):
        if self.type == 0:
            draw_invader_a(surface, self.x, self.y, WHITE, self.frame)
        elif self.type == 1:
            draw_invader_b(surface, self.x, self.y, CYAN, self.frame)
        else:
            draw_invader_c(surface, self.x, self.y, MAGENTA, self.frame)

class UFO:
    def __init__(self):
        self.active = False
        self.x = 0
        self.y = 50
        self.direction = 1
        self.points = random.choice([50, 100, 150, 300])

    def spawn(self):
        self.active = True
        self.direction = random.choice([-1, 1])
        self.x = -50 if self.direction > 0 else SCREEN_WIDTH
        self.points = random.choice([50, 100, 150, 300])

    def update(self):
        if self.active:
            self.x += self.direction * 3
            if self.x < -50 or self.x > SCREEN_WIDTH:
                self.active = False

    def draw(self, surface):
        if self.active:
            draw_ufo(surface, self.x, self.y)

class Bunker:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        # Health grid for destructible bunker
        self.health = []
        template = [
            "  XXXXXX  ",
            " XXXXXXXX ",
            "XXXXXXXXXX",
            "XXXXXXXXXX",
            "XXXXXXXXXX",
            "XXX    XXX",
        ]
        for row in template:
            health_row = []
            for char in row:
                health_row.append(4 if char == 'X' else 0)
            self.health.append(health_row)

    def damage(self, bx, by):
        local_x = (bx - self.x) // 4
        local_y = (by - self.y) // 4
        if 0 <= local_y < len(self.health) and 0 <= local_x < len(self.health[0]):
            if self.health[local_y][local_x] > 0:
                self.health[local_y][local_x] -= 1
                return True
        return False

    def check_collision(self, bx, by, bw, bh):
        for row in range(len(self.health)):
            for col in range(len(self.health[row])):
                if self.health[row][col] > 0:
                    px = self.x + col * 4
                    py = self.y + row * 4
                    if bx < px + 4 and bx + bw > px and by < py + 4 and by + bh > py:
                        return True
        return False

    def draw(self, surface):
        draw_bunker(surface, self.x, self.y, self.health)

class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        self.player = Player()
        self.bullets = []
        self.enemy_bullets = []
        self.invaders = []
        self.bunkers = []
        self.ufo = UFO()
        self.level = 1
        self.invader_direction = 1
        self.invader_speed = 1
        self.move_timer = 0
        self.move_delay = 30
        self.shoot_timer = 0
        self.ufo_timer = 0
        self.game_over = False
        self.paused = False
        self.move_sound_index = 0

        self.spawn_invaders()
        self.spawn_bunkers()

    def spawn_invaders(self):
        self.invaders = []
        for row in range(5):
            invader_type = 0 if row == 0 else (1 if row < 3 else 2)
            for col in range(11):
                x = 100 + col * 55
                y = 100 + row * 45
                self.invaders.append(Invader(x, y, invader_type))

    def spawn_bunkers(self):
        self.bunkers = []
        for i in range(4):
            x = 100 + i * 180
            self.bunkers.append(Bunker(x, SCREEN_HEIGHT - 150))

    def update(self):
        if self.game_over or self.paused:
            return

        # Move invaders
        self.move_timer += 1
        if self.move_timer >= self.move_delay:
            self.move_timer = 0
            self.move_invaders()

        # UFO
        self.ufo_timer += 1
        if self.ufo_timer > 600 and not self.ufo.active:
            if random.random() < 0.01:
                self.ufo.spawn()
                self.ufo_timer = 0
        self.ufo.update()

        # Enemy shooting
        self.shoot_timer += 1
        if self.shoot_timer > 60:
            self.shoot_timer = 0
            self.enemy_shoot()

        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if not bullet.active:
                self.bullets.remove(bullet)
                continue
            # Check invader collision
            for invader in self.invaders[:]:
                if invader.alive:
                    if (bullet.x > invader.x and bullet.x < invader.x + 40 and
                        bullet.y > invader.y and bullet.y < invader.y + 30):
                        invader.alive = False
                        bullet.active = False
                        self.player.score += invader.points
                        SND_EXPLOSION.play()
                        break
            # Check UFO collision
            if self.ufo.active:
                if (bullet.x > self.ufo.x and bullet.x < self.ufo.x + 50 and
                    bullet.y > self.ufo.y and bullet.y < self.ufo.y + 20):
                    self.player.score += self.ufo.points
                    self.ufo.active = False
                    bullet.active = False
                    SND_EXPLOSION.play()
            # Check bunker collision
            for bunker in self.bunkers:
                if bunker.check_collision(bullet.x, bullet.y, 4, 12):
                    bunker.damage(bullet.x, bullet.y)
                    bullet.active = False
                    break

        # Update enemy bullets
        for bullet in self.enemy_bullets[:]:
            bullet.update()
            if not bullet.active:
                self.enemy_bullets.remove(bullet)
                continue
            # Check player collision
            if (bullet.x > self.player.x and bullet.x < self.player.x + 50 and
                bullet.y > self.player.y and bullet.y < self.player.y + 40):
                self.player.lives -= 1
                bullet.active = False
                SND_EXPLOSION.play()
                if self.player.lives <= 0:
                    self.game_over = True
            # Check bunker collision
            for bunker in self.bunkers:
                if bunker.check_collision(bullet.x, bullet.y, 4, 12):
                    bunker.damage(bullet.x, bullet.y)
                    bullet.active = False
                    break

        # Remove dead invaders
        self.invaders = [inv for inv in self.invaders if inv.alive]

        # Check win condition
        if len(self.invaders) == 0:
            self.level += 1
            self.move_delay = max(5, 30 - self.level * 3)
            self.spawn_invaders()

        # Speed up as invaders die
        alive_count = len(self.invaders)
        if alive_count > 0:
            self.move_delay = max(3, 30 - (55 - alive_count) // 3)

    def move_invaders(self):
        move_down = False
        for invader in self.invaders:
            if invader.x + self.invader_direction * 10 < 20 or \
               invader.x + self.invader_direction * 10 > SCREEN_WIDTH - 60:
                move_down = True
                break

        if move_down:
            self.invader_direction *= -1
            for invader in self.invaders:
                invader.y += 20
                invader.frame = 1 - invader.frame
                if invader.y > SCREEN_HEIGHT - 100:
                    self.game_over = True
        else:
            for invader in self.invaders:
                invader.x += self.invader_direction * 10
                invader.frame = 1 - invader.frame

        # Play movement sound
        if self.invaders:
            SND_INVADER_MOVE[self.move_sound_index].play()
            self.move_sound_index = (self.move_sound_index + 1) % 4

    def enemy_shoot(self):
        if not self.invaders:
            return
        # Find bottom invaders in each column
        columns = {}
        for inv in self.invaders:
            col = inv.x // 55
            if col not in columns or inv.y > columns[col].y:
                columns[col] = inv
        if columns:
            shooter = random.choice(list(columns.values()))
            self.enemy_bullets.append(Bullet(shooter.x + 20, shooter.y + 30, 5))

    def player_shoot(self):
        if len(self.bullets) < 1:
            self.bullets.append(Bullet(self.player.x + 23, self.player.y, -10))
            SND_SHOOT.play()

    def draw(self, surface):
        surface.fill(BLACK)

        # Draw game elements
        self.player.draw(surface)
        for inv in self.invaders:
            inv.draw(surface)
        for bullet in self.bullets + self.enemy_bullets:
            bullet.draw(surface)
        for bunker in self.bunkers:
            bunker.draw(surface)
        self.ufo.draw(surface)

        # Draw UI
        font = get_font(36)
        score_text = font.render(f"SCORE: {self.player.score}", True, WHITE)
        lives_text = font.render(f"LIVES: {self.player.lives}", True, GREEN)
        level_text = font.render(f"LEVEL: {self.level}", True, YELLOW)
        surface.blit(score_text, (10, 10))
        surface.blit(lives_text, (SCREEN_WIDTH - 150, 10))
        surface.blit(level_text, (SCREEN_WIDTH // 2 - 50, 10))

        # Ground line
        pygame.draw.line(surface, GREEN, (0, SCREEN_HEIGHT - 40),
                        (SCREEN_WIDTH, SCREEN_HEIGHT - 40), 2)

        if self.game_over:
            font_big = get_font(72)
            go_text = font_big.render("GAME OVER", True, RED)
            surface.blit(go_text, (SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2 - 50))
            font_small = get_font(36)
            restart_text = font_small.render("Click to return to menu", True, WHITE)
            surface.blit(restart_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 30))

# Menu system
class Menu:
    def __init__(self):
        self.options = ["START GAME", "HOW TO PLAY", "CREDITS", "EXIT"]
        self.selected = 0
        self.state = "main"  # main, howto, credits

    def update(self, mouse_y):
        if self.state == "main":
            # Calculate which option mouse is hovering over
            start_y = 250
            for i in range(len(self.options)):
                opt_y = start_y + i * 60
                if opt_y < mouse_y < opt_y + 50:
                    if self.selected != i:
                        self.selected = i
                        SND_SELECT.play()
                    break

    def click(self):
        SND_CONFIRM.play()
        if self.state == "main":
            if self.selected == 0:
                return "start"
            elif self.selected == 1:
                self.state = "howto"
            elif self.selected == 2:
                self.state = "credits"
            elif self.selected == 3:
                return "exit"
        else:
            self.state = "main"
        return None

    def draw(self, surface):
        surface.fill(BLACK)

        # Title
        font_title = get_font(80)
        title = font_title.render("SPACE INVADERS", True, GREEN)
        surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 80))

        # Draw invader decorations
        draw_invader_a(surface, 150, 100, WHITE, 0)
        draw_invader_b(surface, 600, 100, CYAN, 0)
        draw_invader_c(surface, 100, 150, MAGENTA, 1)
        draw_invader_a(surface, 650, 150, WHITE, 1)

        if self.state == "main":
            font = get_font(48)
            start_y = 250
            for i, option in enumerate(self.options):
                color = YELLOW if i == self.selected else WHITE
                text = font.render(option, True, color)
                x = SCREEN_WIDTH // 2 - text.get_width() // 2
                surface.blit(text, (x, start_y + i * 60))
                if i == self.selected:
                    # Draw selection indicator
                    pygame.draw.polygon(surface, YELLOW, [
                        (x - 30, start_y + i * 60 + 15),
                        (x - 10, start_y + i * 60 + 25),
                        (x - 30, start_y + i * 60 + 35)
                    ])

            # Footer
            font_small = get_font(24)
            footer = font_small.render("(C) 1978 TAITO CORP - PYTHON REMAKE 2026", True, WHITE)
            surface.blit(footer, (SCREEN_WIDTH // 2 - footer.get_width() // 2, 550))

        elif self.state == "howto":
            font = get_font(36)
            instructions = [
                "HOW TO PLAY",
                "",
                "MOUSE: Move left/right",
                "CLICK: Fire laser cannon",
                "",
                "Destroy all invaders before",
                "they reach the bottom!",
                "",
                "Hide behind bunkers for cover.",
                "Shoot the mystery UFO for bonus!",
                "",
                "POINTS:",
                "  Squid   = 30 pts",
                "  Crab    = 20 pts",
                "  Octopus = 10 pts",
                "  UFO     = 50-300 pts",
                "",
                "Click anywhere to return"
            ]
            y = 80
            for line in instructions:
                color = YELLOW if line == "HOW TO PLAY" or line == "POINTS:" else WHITE
                text = font.render(line, True, color)
                surface.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y))
                y += 30

        elif self.state == "credits":
            font = get_font(36)
            credits = [
                "CREDITS",
                "",
                "ORIGINAL GAME",
                "Tomohiro Nishikado (1978)",
                "TAITO CORPORATION",
                "",
                "PYTHON REMAKE",
                "Claude AI (2026)",
                "",
                "SOUND DESIGN",
                "Procedural Beeps & Boops",
                "",
                "SPECIAL THANKS",
                "All Space Invaders fans!",
                "",
                "Click anywhere to return"
            ]
            y = 100
            for line in credits:
                color = YELLOW if line in ["CREDITS", "ORIGINAL GAME",
                         "PYTHON REMAKE", "SOUND DESIGN", "SPECIAL THANKS"] else WHITE
                text = font.render(line, True, color)
                surface.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y))
                y += 32

# Main loop
def main():
    clock = pygame.time.Clock()
    menu = Menu()
    game = None
    state = "menu"

    pygame.mouse.set_visible(True)

    running = True
    while running:
        mouse_x, mouse_y = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if state == "menu":
                    result = menu.click()
                    if result == "start":
                        game = Game()
                        state = "game"
                    elif result == "exit":
                        running = False
                elif state == "game":
                    if game.game_over:
                        state = "menu"
                        menu.state = "main"
                    else:
                        game.player_shoot()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if state == "game":
                        state = "menu"
                        menu.state = "main"
                    elif menu.state != "main":
                        menu.state = "main"

        if state == "menu":
            menu.update(mouse_y)
            menu.draw(screen)
        elif state == "game":
            game.player.update(mouse_x)
            game.update()
            game.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
