#!/usr/bin/env python3
# miyamotos_vs_tobyfoxes_pvz1_pygame_ce_graphics_updated.py - Enhanced with SMG4 Miyamito face and Annoying Dog zombie heads
# 100% meme-accurate, 0% legal files touched ~ nya nya rawr!! 💥🐾
# Run with: pip install pygame-ce && python this_file.py
import pygame
import random
import sys
import math

# Constants
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 700
LANE_HEIGHT = SCREEN_HEIGHT // 5
GRASS_COLS = 9
TILE_WIDTH = SCREEN_WIDTH // (GRASS_COLS + 2)
HOUSE_WIDTH = TILE_WIDTH
FPS = 60
SUN_DROP_INTERVAL = 10
SUN_VALUE = 25
INITIAL_SUN = 50

# Colors
GREEN_GRASS = (34, 139, 34)
DARK_GREEN = (0, 100, 0)
BROWN_DIRT = (139, 69, 19)
BLUE_SKY = (135, 206, 235)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
DARK_BROWN = (101, 67, 33)
SKIN = (255, 204, 153)
BLUE = (0, 0, 255)
PINK = (255, 192, 203)

class Entity(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name, health=100, max_health=100):
        super().__init__()
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.health = health
        self.max_health = max_health
        self.alive = True
        self.lane = y // LANE_HEIGHT
        self.name = name

    def update_health_bar(self, screen):
        if self.alive:
            bar_width = 50
            bar_height = 8
            fill = (self.health / self.max_health) * bar_width
            pygame.draw.rect(screen, RED, (self.rect.x, self.rect.y - 15, bar_width, bar_height))
            pygame.draw.rect(screen, GREEN_GRASS, (self.rect.x, self.rect.y - 15, fill, bar_height))

    def take_damage(self, dmg):
        self.health -= dmg
        if self.health <= 0:
            self.alive = False
            self.kill()

class Plant(Entity):
    def __init__(self, lane, col, data):
        x = HOUSE_WIDTH + col * TILE_WIDTH + 20
        y = lane * LANE_HEIGHT + 50
        self.data = data
        self.name, self.desc, self.color, self.cost, self.cooldown, health, self.dmg, self.special = data
        super().__init__(x, y, 80, 80, self.name, health, health)
        self.draw_procedural()
        self.shoot_timer = 0
        self.shoot_delay = 90
        self.sun_timer = 0 if 'Sunflower' in self.name else -1
        self.col = col

    def draw_procedural(self):
        # Base stem
        pygame.draw.rect(self.image, (0, 128, 0), (30, 40, 20, 40))  # Stem
        if 'Sunflower' in self.name:
            # Yellow petals
            pygame.draw.circle(self.image, YELLOW, (40, 40), 30)
            for i in range(8):
                angle = i * 45
                dx = 30 * math.cos(math.radians(angle))
                dy = 30 * math.sin(math.radians(angle))
                pygame.draw.circle(self.image, ORANGE, (40 + int(dx), 40 + int(dy)), 10)
            # Face
            pygame.draw.circle(self.image, BROWN_DIRT, (40, 40), 20)
            pygame.draw.circle(self.image, BLACK, (30, 35), 5)
            pygame.draw.circle(self.image, BLACK, (50, 35), 5)
            pygame.draw.arc(self.image, BLACK, (30, 40, 20, 10), 0, math.pi)
        elif 'Peashooter' in self.name:
            pygame.draw.circle(self.image, GREEN_GRASS, (40, 40), 30)
            pygame.draw.circle(self.image, BLACK, (50, 40), 10)  # Mouth
            pygame.draw.circle(self.image, WHITE, (30, 30), 5)
            pygame.draw.circle(self.image, BLACK, (30, 30), 2)
        elif 'Cherry' in self.name:
            pygame.draw.circle(self.image, RED, (30, 40), 25)
            pygame.draw.circle(self.image, RED, (50, 40), 25)
            pygame.draw.line(self.image, BLACK, (30, 20), (40, 10), 3)
            pygame.draw.line(self.image, BLACK, (50, 20), (40, 10), 3)
        elif 'Wall-nut' in self.name:
            pygame.draw.circle(self.image, GRAY, (40, 40), 30)
            pygame.draw.circle(self.image, BLACK, (25, 35), 5)
            pygame.draw.circle(self.image, BLACK, (55, 35), 5)
            pygame.draw.arc(self.image, BLACK, (25, 45, 30, 10), math.pi, 0)
        elif 'Snow' in self.name:
            pygame.draw.circle(self.image, (150, 200, 255), (40, 40), 30)
            pygame.draw.circle(self.image, BLACK, (50, 40), 10)
            pygame.draw.circle(self.image, WHITE, (30, 30), 5)
            pygame.draw.circle(self.image, BLACK, (30, 30), 2)
        elif 'Potato' in self.name:
            pygame.draw.ellipse(self.image, BROWN_DIRT, (20, 30, 40, 40))
            for _ in range(5):
                px = random.randint(20, 60)
                py = random.randint(30, 70)
                pygame.draw.circle(self.image, BLACK, (px, py), 3)

    def update(self, dt, zombies, suns, peas):
        if self.sun_timer >= 0:
            self.sun_timer += dt
            if self.sun_timer > 24:
                self.sun_timer = 0
                sun = Sun(self.rect.centerx, self.rect.centery, falling=False)
                suns.add(sun)
        self.shoot_timer += dt * 60
        if self.shoot_timer > self.shoot_delay:
            self.shoot_timer = 0
            target = next((z for z in zombies if z.lane == self.lane and z.rect.x > self.rect.x and z.alive), None)
            if target:
                if 'Cherry' in self.name:
                    for z in [z for z in zombies if abs(z.rect.centerx - self.rect.centerx) < 150 and abs(z.lane - self.lane) <= 1]:
                        z.take_damage(1000)
                    self.take_damage(1000)
                elif 'Snow' in self.name:
                    pea = Pea(self.rect.right, self.rect.centery, self.lane)
                    pea.slow = True
                    peas.add(pea)
                elif 'Potato' not in self.name and 'Wall' not in self.name and 'Sunflower' not in self.name:
                    pea = Pea(self.rect.right, self.rect.centery, self.lane)
                    peas.add(pea)

class Zombie(Entity):
    def __init__(self, lane, data):
        x = SCREEN_WIDTH + 50
        y = lane * LANE_HEIGHT + 50
        self.name, self.desc, self.color, health, self.speed = data
        super().__init__(x, y, 80, 80, self.name, health, health)
        self.draw_procedural()
        self.eat_timer = 0
        self.eat_delay = 60
        self.slowed = 0
        self.eating = False

    def draw_procedural(self):
        # Base body
        pygame.draw.rect(self.image, (0, 100, 0), (20, 50, 40, 30))  # Pants
        pygame.draw.rect(self.image, (100, 100, 100), (25, 20, 30, 30))  # Shirt
        # Annoying Dog head instead of human head
        # White dog head
        pygame.draw.ellipse(self.image, WHITE, (20, 5, 40, 30))  # Head
        # Ears
        pygame.draw.ellipse(self.image, WHITE, (15, 15, 10, 20))  # Left ear
        pygame.draw.ellipse(self.image, WHITE, (55, 15, 10, 20))  # Right ear
        # Eyes
        pygame.draw.circle(self.image, BLACK, (30, 15), 3)
        pygame.draw.circle(self.image, BLACK, (50, 15), 3)
        # Nose
        pygame.draw.circle(self.image, BLACK, (40, 20), 2)
        # Tongue
        pygame.draw.ellipse(self.image, PINK, (35, 25, 10, 5))
        # Outline
        pygame.draw.ellipse(self.image, BLACK, (20, 5, 40, 30), 1)
        if 'Conehead' in self.name:
            pygame.draw.polygon(self.image, ORANGE, [(40, -10), (20, 5), (60, 5)])
        elif 'Buckethead' in self.name:
            pygame.draw.rect(self.image, GRAY, (25, -10, 30, 15))
        elif 'Gargantuar' in self.name:
            self.image = pygame.transform.scale(self.image, (100, 100))
            self.rect = self.image.get_rect(topleft=self.rect.topleft)

    def update(self, dt, plants, lawnmowers, zombies):
        self.eating = False
        for plant in [p for p in plants if p.lane == self.lane and p.alive]:
            if self.rect.colliderect(plant.rect):
                self.eating = True
                self.eat_timer += dt * 60
                if self.eat_timer > self.eat_delay:
                    self.eat_timer = 0
                    plant.take_damage(20)
                    if 'Potato' in plant.name:
                        self.take_damage(1000)
                        plant.take_damage(1000)
                break
        if not self.eating:
            speed = self.speed * dt * (0.5 if self.slowed > 0 else 1)
            self.rect.x -= speed
        self.slowed = max(0, self.slowed - dt)
        if self.rect.x < HOUSE_WIDTH + TILE_WIDTH:
            for mower in lawnmowers:
                if mower.lane == self.lane and not mower.triggered:
                    mower.trigger(zombies)
        if self.rect.right < HOUSE_WIDTH:
            self.alive = False
            self.kill()
            return True
        return False

class Pea(pygame.sprite.Sprite):
    def __init__(self, x, y, lane):
        super().__init__()
        self.image = pygame.Surface((15, 15), pygame.SRCALPHA)
        pygame.draw.circle(self.image, GREEN_GRASS, (7, 7), 7)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 400
        self.lane = lane
        self.dmg = 25
        self.slow = False

    def update(self, dt, zombies):
        self.rect.x += self.speed * dt
        if self.rect.left > SCREEN_WIDTH:
            self.kill()
            return
        for z in zombies:
            if z.lane == self.lane and z.alive and self.rect.colliderect(z.rect):
                z.take_damage(self.dmg)
                if self.slow:
                    z.slowed = 5
                self.kill()
                return

class Sun(pygame.sprite.Sprite):
    def __init__(self, x, y, falling=True):
        super().__init__()
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(self.image, YELLOW, (20, 20), 20)
        pygame.draw.circle(self.image, ORANGE, (20, 20), 15)
        for i in range(8):
            angle = i * 45
            dx = 25 * math.cos(math.radians(angle))
            dy = 25 * math.sin(math.radians(angle))
            pygame.draw.line(self.image, YELLOW, (20, 20), (20 + int(dx), 20 + int(dy)), 3)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 50 if falling else 0
        self.fall_timer = random.uniform(1, 3) if falling else 0
        self.target_y = y + random.randint(100, 300) if falling else y + 50
        self.lifetime = 10

    def update(self, dt):
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
            return
        if self.fall_timer > 0:
            self.fall_timer -= dt
        elif self.rect.y < self.target_y:
            self.rect.y += self.speed * dt

class SeedPacket(pygame.sprite.Sprite):
    def __init__(self, x, y, data, index):
        super().__init__()
        self.data = data
        self.index = index
        self.base_image = pygame.Surface((80, 100), pygame.SRCALPHA)
        pygame.draw.rect(self.base_image, GRAY, (0, 0, 80, 100), 0, 10)
        pygame.draw.rect(self.base_image, BLACK, (0, 0, 80, 100), 3, 10)
        font = pygame.font.Font(None, 20)
        text = font.render(data[0][:10], True, BLACK)
        self.base_image.blit(text, (5, 80))
        # Mini plant preview
        mini_plant = Plant(0, 0, data)
        mini_img = pygame.transform.scale(mini_plant.image, (50, 50))
        self.base_image.blit(mini_img, (15, 15))
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.cooldown_timer = 0
        self.ready = True

    def update(self, dt):
        if not self.ready:
            self.cooldown_timer -= dt
            if self.cooldown_timer <= 0:
                self.ready = True
                self.image = self.base_image.copy()
            else:
                # Cooldown overlay
                height = (self.cooldown_timer / self.data[4]) * 100
                overlay = pygame.Surface((80, height), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150))
                self.image.blit(overlay, (0, 100 - height))

    def set_cooldown(self):
        self.ready = False
        self.cooldown_timer = self.data[4]

class Lawnmower(pygame.sprite.Sprite):
    def __init__(self, lane):
        super().__init__()
        self.image = pygame.Surface((60, 40), pygame.SRCALPHA)
        pygame.draw.rect(self.image, GRAY, (0, 0, 60, 40))
        pygame.draw.circle(self.image, BLACK, (15, 35), 10)
        pygame.draw.circle(self.image, BLACK, (45, 35), 10)
        pygame.draw.rect(self.image, RED, (10, 5, 40, 20))
        self.rect = self.image.get_rect(topleft=(HOUSE_WIDTH - 60, lane * LANE_HEIGHT + 70))
        self.lane = lane
        self.triggered = False
        self.speed = 600
        self.zombies_ref = None

    def trigger(self, zombies):
        self.triggered = True
        self.zombies_ref = zombies

    def update(self, dt):
        if self.triggered and self.zombies_ref:
            self.rect.x += self.speed * dt
            for z in self.zombies_ref:
                if z.lane == self.lane and z.alive and self.rect.colliderect(z.rect):
                    z.take_damage(10000)
            if self.rect.left > SCREEN_WIDTH:
                self.kill()

class EventText:
    def __init__(self, text, duration=3):
        self.text = text
        self.timer = duration
        self.font = pygame.font.Font(None, 48)
        self.color = WHITE

    def update(self, dt):
        self.timer -= dt
        return self.timer > 0

    def draw(self, screen):
        surf = self.font.render(self.text, True, self.color)
        shadow = self.font.render(self.text, True, BLACK)
        screen.blit(shadow, (SCREEN_WIDTH // 2 - surf.get_width() // 2 + 2, 152))
        screen.blit(surf, (SCREEN_WIDTH // 2 - surf.get_width() // 2, 150))

def draw_lawn(screen):
    screen.fill(BLUE_SKY)
    # House with details
    pygame.draw.rect(screen, BROWN_DIRT, (0, 0, HOUSE_WIDTH, SCREEN_HEIGHT))
    pygame.draw.rect(screen, DARK_BROWN, (10, 100, HOUSE_WIDTH - 20, 400))
    pygame.draw.polygon(screen, RED, [(0, 100), (HOUSE_WIDTH, 100), (HOUSE_WIDTH // 2, 50)])
    pygame.draw.rect(screen, BLUE, (20, 200, 20, 50))  # Window
    pygame.draw.rect(screen, BROWN_DIRT, (20, 300, 40, 200))  # Door
    # Lanes
    for lane in range(5):
        y = lane * LANE_HEIGHT
        for col in range(GRASS_COLS):
            x = HOUSE_WIDTH + col * TILE_WIDTH
            color = GREEN_GRASS if (lane + col) % 2 == 0 else DARK_GREEN
            pygame.draw.rect(screen, color, (x, y, TILE_WIDTH, LANE_HEIGHT))

def get_lane_col(pos):
    col = (pos[0] - HOUSE_WIDTH) // TILE_WIDTH
    lane = pos[1] // LANE_HEIGHT
    if 0 <= col < GRASS_COLS and 0 <= lane < 5:
        return lane, col
    return None, None

def draw_miyamito(screen, x, y, message="Welcome, hero! Design your defense!"):
    # SMG4-style Miyamito: Exaggerated Mario features
    miya_surf = pygame.Surface((200, 300), pygame.SRCALPHA)
    # Head (oval)
    pygame.draw.ellipse(miya_surf, SKIN, (60, 50, 80, 100))
    # Eyes (large ovals with notch)
    pygame.draw.ellipse(miya_surf, WHITE, (75, 70, 20, 30))
    pygame.draw.ellipse(miya_surf, WHITE, (105, 70, 20, 30))
    pygame.draw.circle(miya_surf, BLUE, (85, 85, 10))
    pygame.draw.circle(miya_surf, BLUE, (115, 85, 10))
    # Eyebrows (thick curves)
    pygame.draw.arc(miya_surf, BLACK, (70, 60, 30, 20), math.pi, 0, 5)
    pygame.draw.arc(miya_surf, BLACK, (100, 60, 30, 20), math.pi, 0, 5)
    # Nose (curve)
    pygame.draw.arc(miya_surf, SKIN, (95, 90, 10, 20), 0, math.pi, 10)
    # Mustache (large, covering mouth)
    pygame.draw.ellipse(miya_surf, BLACK, (80, 100, 40, 20))
    # Hat (red with M)
    pygame.draw.rect(miya_surf, RED, (70, 30, 60, 20))
    pygame.draw.rect(miya_surf, RED, (80, 10, 40, 20))
    font = pygame.font.Font(None, 30)
    m_text = font.render("M", True, WHITE)
    miya_surf.blit(m_text, (95, 20))
    # Body (overalls)
    pygame.draw.rect(miya_surf, BLUE, (70, 150, 60, 100))
    pygame.draw.rect(miya_surf, RED, (70, 150, 60, 50))
    # Arms
    pygame.draw.rect(miya_surf, RED, (50, 170, 20, 80))
    pygame.draw.rect(miya_surf, RED, (130, 170, 20, 80))
    # Legs
    pygame.draw.rect(miya_surf, BLUE, (80, 250, 20, 50))
    pygame.draw.rect(miya_surf, BLUE, (100, 250, 20, 50))
    # Speech bubble
    bubble = pygame.Surface((300, 100), pygame.SRCALPHA)
    pygame.draw.ellipse(bubble, WHITE, (0, 0, 300, 100))
    pygame.draw.ellipse(bubble, BLACK, (0, 0, 300, 100), 3)
    font = pygame.font.Font(None, 24)
    text = font.render(message, True, BLACK)
    bubble.blit(text, (20, 40))
    screen.blit(miya_surf, (x, y))
    screen.blit(bubble, (x + 150, y + 50))

def draw_main_menu(screen, font, big_font):
    screen.fill(DARK_GREEN)
    # Title with flair
    title = big_font.render("MIYAMOTOS VS TOBY FOXES", True, YELLOW)
    subtitle = font.render("PvZ1 Meme Edition ~ Nya!", True, WHITE)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
    screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 130))
    # Decorative elements
    for i in range(10):
        px = random.randint(0, SCREEN_WIDTH)
        py = random.randint(200, SCREEN_HEIGHT)
        pygame.draw.circle(screen, YELLOW, (px, py), 5)  # Stars
    # Miyamito character
    draw_miyamito(screen, SCREEN_WIDTH - 300, SCREEN_HEIGHT - 400, "Let's-a go! Design epic battles!")
    # Buttons
    buttons = []
    # Adventure
    adv_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 200, 300, 60)
    pygame.draw.rect(screen, BROWN_DIRT, adv_rect, 0, 10)
    pygame.draw.rect(screen, YELLOW, adv_rect, 3, 10)
    adv_text = font.render("ADVENTURE MODE", True, WHITE)
    screen.blit(adv_text, (adv_rect.centerx - adv_text.get_width() // 2, adv_rect.centery - 15))
    buttons.append(("adventure", adv_rect))
    # Survival
    surv_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 280, 300, 60)
    pygame.draw.rect(screen, BROWN_DIRT, surv_rect, 0, 10)
    pygame.draw.rect(screen, YELLOW, surv_rect, 3, 10)
    surv_text = font.render("SURVIVAL MODE", True, WHITE)
    screen.blit(surv_text, (surv_rect.centerx - surv_text.get_width() // 2, surv_rect.centery - 15))
    buttons.append(("survival", surv_rect))
    # Shop (new)
    shop_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 360, 300, 60)
    pygame.draw.rect(screen, BROWN_DIRT, shop_rect, 0, 10)
    pygame.draw.rect(screen, YELLOW, shop_rect, 3, 10)
    shop_text = font.render("MIYAMITO'S SHOP", True, WHITE)
    screen.blit(shop_text, (shop_rect.centerx - shop_text.get_width() // 2, shop_rect.centery - 15))
    buttons.append(("shop", shop_rect))
    # Quit
    quit_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 440, 300, 60)
    pygame.draw.rect(screen, RED, quit_rect, 0, 10)
    pygame.draw.rect(screen, YELLOW, quit_rect, 3, 10)
    quit_text = font.render("QUIT", True, WHITE)
    screen.blit(quit_text, (quit_rect.centerx - quit_text.get_width() // 2, quit_rect.centery - 15))
    buttons.append(("quit", quit_rect))
    # Credits
    credit = font.render("~ xAI Grok Edition - Procedural Chaos! 🐾 ~", True, YELLOW)
    screen.blit(credit, (SCREEN_WIDTH // 2 - credit.get_width() // 2, SCREEN_HEIGHT - 50))
    return buttons

def draw_shop(screen, font, money=0):
    screen.fill(DARK_BROWN)
    title = font.render("MIYAMITO'S TWIDDYDINKIES SHOP", True, YELLOW)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
    draw_miyamito(screen, 50, 100, "Buy power-ups! Innovation time!")
    # Items (placeholder)
    items = [
        ("Extra Seed Slot", 1000),
        ("Fertilizer Pack", 750),
        ("1-UP Mushroom", 2500)
    ]
    for i, (name, cost) in enumerate(items):
        rect = pygame.Rect(400, 150 + i*80, 600, 60)
        pygame.draw.rect(screen, GRAY, rect, 0, 10)
        text = font.render(f"{name} - {cost} Coins", True, BLACK)
        screen.blit(text, (rect.x + 20, rect.y + 20))
    money_text = font.render(f"Coins: {money}", True, YELLOW)
    screen.blit(money_text, (SCREEN_WIDTH - 200, 50))
    back_text = font.render("Click to back", True, WHITE)
    screen.blit(back_text, (50, SCREEN_HEIGHT - 50))

def main_menu():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("MIYAMOTOS VS TOBY FOXES - PvZ1 PYGAME-CE EDITION")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    big_font = pygame.font.Font(None, 72)
    in_shop = False
    money = 0  # Placeholder
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                if in_shop:
                    in_shop = False
                else:
                    buttons = draw_main_menu(screen, font, big_font)
                    for name, rect in buttons:
                        if rect.collidepoint(pos):
                            if name == "adventure":
                                game_loop(screen, clock, font, small_font=pygame.font.Font(None, 24), rounds=random.randint(8, 15))
                            elif name == "survival":
                                game_loop(screen, clock, font, small_font=pygame.font.Font(None, 24), rounds=999, survival=True)
                            elif name == "shop":
                                in_shop = True
                            elif name == "quit":
                                running = False
        if in_shop:
            draw_shop(screen, font, money)
        else:
            draw_main_menu(screen, font, big_font)
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()
    sys.exit()

def draw_progress_bar(screen, current_wave, rounds, survival, font):
    bar_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, 70, 400, 20)
    pygame.draw.rect(screen, GRAY, bar_rect)
    if not survival:
        fill_width = (current_wave / rounds) * 400
    else:
        fill_width = (current_wave % 10 / 10) * 400  # Cycle every 10 waves
    pygame.draw.rect(screen, GREEN_GRASS, (bar_rect.x, bar_rect.y, fill_width, 20))
    # Flags
    for i in range(1, rounds + 1 if not survival else 11):
        flag_x = bar_rect.x + (i / rounds if not survival else i / 10) * 400 - 10
        pygame.draw.rect(screen, YELLOW, (flag_x, bar_rect.y - 10, 20, 10))
    text = font.render("Progress", True, WHITE)
    screen.blit(text, (bar_rect.x + 150, bar_rect.y - 30))

def game_loop(screen, clock, font, small_font, rounds=10, survival=False):
    # Teams data (updated with Peashooter)
    miyamoto_plants_data = [
        ("Sunflower", "drops golden coins, hums 1-1 theme", YELLOW, 50, 7.5, 100, 0, "sun"),
        ("Peashooter", "jumps on zombies with perfect stomp timing", GREEN_GRASS, 100, 7.5, 100, 25, "shoot"),
        ("Cherry Bomb", "roars before exploding in fire", RED, 150, 50, 100, 1000, "explode"),
        ("Wall-nut", "pulls Master Sword when health < 30%", GRAY, 50, 30, 400, 0, "defend"),
        ("Snow Pea", "freezes zombies with cosmic ice", (150, 200, 255), 175, 7.5, 100, 20, "slow"),
        ("Potato Mine", "hides underground, yells 'HEY!' on trigger", BROWN_DIRT, 25, 30, 100, 1000, "mine")
    ]

    toby_zombies_data = [
        ("Conehead Sans", "teleports short distances, winks a lot", GRAY, 175, 30),
        ("Football Undyne", "charges with spear determination", ORANGE, 300, 80),
        ("Basic Toby", "hoodie flapping, drops 'bad time' notes", (100, 100, 100), 100, 25),
        ("Gargantuar Flowey", "Omega form, 'kill or be killed' speech", PURPLE, 3000, 15),
        ("Buckethead Papyrus", "shouts spaghetti puzzles, tall af", (150, 100, 50), 250, 25)
    ]

    # Groups
    plants = pygame.sprite.Group()
    zombies = pygame.sprite.Group()
    peas = pygame.sprite.Group()
    suns = pygame.sprite.Group()
    packets = pygame.sprite.Group()
    lawnmowers = pygame.sprite.Group()
    events = []

    # Setup packets
    for i, data in enumerate(miyamoto_plants_data):
        packet = SeedPacket(10 + i * 90, 10, data, i)
        packets.add(packet)

    # Lawnmowers
    for lane in range(5):
        mower = Lawnmower(lane)
        lawnmowers.add(mower)

    # Game state
    sun_count = INITIAL_SUN
    selected_packet = None
    shovel_selected = False
    current_wave = 0
    wave_timer = 5
    sun_drop_timer = 0
    wave_duration = 20
    game_over = False
    winner = ""
    paused = False

    events_list = [
        "Miyamoto plants hold the line with perfect platformer timing!",
        "Toby zombies spam bullet hell patterns - plants dodging frantically!",
        "Handsome Squidward cameo - everyone stops to stare 😳",
        "Tanooki Statue activated - invincibility frames go brrrr",
        "MEGALOVANIA remix drops - morale +1000 for zombies",
        "1-UP mushroom spawns - extra life for the lawn!",
        "A HUGE WAVE OF ZOMBIES IS APPROACHING!"
    ]

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                if event.key == pygame.K_p:
                    paused = not paused
            if event.type == pygame.MOUSEBUTTONDOWN:
                if game_over:
                    return
                elif not paused:
                    pos = pygame.mouse.get_pos()
                    for sun in list(suns):
                        if sun.rect.collidepoint(pos):
                            sun_count += SUN_VALUE
                            sun.kill()
                    for packet in packets:
                        if packet.rect.collidepoint(pos) and packet.ready and sun_count >= packet.data[3]:
                            selected_packet = packet.index
                            shovel_selected = False
                    if SCREEN_WIDTH - 100 < pos[0] < SCREEN_WIDTH - 20 and 10 < pos[1] < 60:
                        shovel_selected = not shovel_selected
                        selected_packet = None
                    lane, col = get_lane_col(pos)
                    if lane is not None:
                        if selected_packet is not None:
                            data = miyamoto_plants_data[selected_packet]
                            occupied = any(p for p in plants if p.lane == lane and p.col == col)
                            if not occupied:
                                plant = Plant(lane, col, data)
                                plants.add(plant)
                                sun_count -= data[3]
                                packets.sprites()[selected_packet].set_cooldown()
                                selected_packet = None
                        elif shovel_selected:
                            for plant in list(plants):
                                if plant.lane == lane and plant.col == col:
                                    plant.kill()
                            shovel_selected = False

        if not game_over and not paused:
            sun_drop_timer += dt
            if sun_drop_timer > SUN_DROP_INTERVAL:
                sun_drop_timer = 0
                sun = Sun(random.randint(HOUSE_WIDTH + 100, SCREEN_WIDTH - 100), -20, falling=True)
                suns.add(sun)
            wave_timer -= dt
            if wave_timer <= 0:
                current_wave += 1
                wave_timer = wave_duration
                num_zombies = min(2 + current_wave // 2, 12)
                if survival:
                    num_zombies = min(3 + current_wave, 20)
                for _ in range(num_zombies):
                    lane = random.randint(0, 4)
                    if current_wave < 3:
                        data = toby_zombies_data[2]
                    elif current_wave < 6:
                        data = random.choice(toby_zombies_data[:3])
                    else:
                        data = random.choice(toby_zombies_data)
                    zombie = Zombie(lane, data)
                    zombies.add(zombie)
                if current_wave % 5 == 0:
                    event_text = events_list[-1]
                else:
                    event_text = random.choice(events_list[:-1])
                events.append(EventText(event_text))
            for plant in list(plants):
                plant.update(dt, zombies, suns, peas)
            for zombie in list(zombies):
                if zombie.update(dt, plants, lawnmowers, zombies):
                    game_over = True
                    winner = "ZOMBIES ATE YOUR BRAINS! 💀"
            peas.update(dt, zombies)
            suns.update(dt)
            packets.update(dt)
            lawnmowers.update(dt)
            if not survival and current_wave >= rounds and len(zombies) == 0:
                game_over = True
                winner = "YOU SURVIVED! MIYAMOTO DEFENSE WINS! 🎮"

        draw_lawn(screen)
        plants.draw(screen)
        zombies.draw(screen)
        peas.draw(screen)
        suns.draw(screen)
        lawnmowers.draw(screen)
        # HUD bar
        pygame.draw.rect(screen, DARK_BROWN, (0, 0, SCREEN_WIDTH, 120), 0)
        packets.draw(screen)
        if selected_packet is not None:
            pygame.draw.rect(screen, WHITE, packets.sprites()[selected_packet].rect, 4)
        events = [e for e in events if e.update(dt)]
        for ev in events:
            ev.draw(screen)
        # Sun counter with icon
        sun_icon = Sun(SCREEN_WIDTH - 200, 30, falling=False)
        screen.blit(sun_icon.image, (SCREEN_WIDTH - 220, 20))
        sun_text = font.render(str(sun_count), True, BLACK)
        screen.blit(sun_text, (SCREEN_WIDTH - 170, 30))
        # Progress bar
        draw_progress_bar(screen, current_wave, rounds, survival, font)
        # Shovel
        shovel_color = PINK if shovel_selected else GRAY
        pygame.draw.rect(screen, shovel_color, (SCREEN_WIDTH - 100, 10, 80, 50), 0, 5)
        pygame.draw.rect(screen, BLACK, (SCREEN_WIDTH - 100, 10, 80, 50), 2, 5)
        shovel_surf = small_font.render("SHOVEL", True, BLACK)
        screen.blit(shovel_surf, (SCREEN_WIDTH - 95, 25))
        # Health bars
        for entity in list(plants) + list(zombies):
            entity.update_health_bar(screen)
        if paused:
            pause_surf = font.render("PAUSED - Press P to resume", True, WHITE)
            screen.blit(pause_surf, (SCREEN_WIDTH // 2 - pause_surf.get_width() // 2, SCREEN_HEIGHT // 2))
        if game_over:
            dark = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            dark.fill(BLACK)
            dark.set_alpha(180)
            screen.blit(dark, (0, 0))
            win_surf = font.render(winner, True, GREEN_GRASS if "SURVIVED" in winner else RED)
            screen.blit(win_surf, (SCREEN_WIDTH // 2 - win_surf.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            stats = f"Waves Survived: {current_wave}"
            stats_surf = small_font.render(stats, True, WHITE)
            screen.blit(stats_surf, (SCREEN_WIDTH // 2 - stats_surf.get_width() // 2, SCREEN_HEIGHT // 2))
            restart_text = small_font.render("Click to return to menu ~ nya! 🐾", True, WHITE)
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
        controls = small_font.render("ESC: Menu | P: Pause", True, WHITE)
        screen.blit(controls, (10, SCREEN_HEIGHT - 30))
        pygame.display.flip()

if __name__ == "__main__":
    random.seed()
    main_menu()
