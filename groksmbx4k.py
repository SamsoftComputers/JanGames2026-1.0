# Ultra SMBX - Main Menu + Prototype Game with Level Editor and Episode Simulation
# pygame-ce // macOS FORCED window fix included
# Cat-tuned for @ItsJustaCat00 – jumps higher, dies prettier
# Enhanced with basic level editor and in-memory episode switching (files=off)

import pygame
import sys
import os

# ─── MACOS INVISIBILITY NUKE ─────────────────────────────────
os.environ["SDL_VIDEO_DRIVER"] = "cocoa"  # FORCES window on Apple Silicon/Ventura+
os.environ["SDL_VIDEO_CENTERED"] = "1"  # centers it, no off-screen bullshit

# ─── Init ────────────────────────────────────────────────────
pygame.init()
pygame.display.set_caption("Ultra SMBX")
WIDTH, HEIGHT = 960, 540
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Colors – retro punch
SKY = (135, 206, 235)
GROUND = (140, 80, 20)
PLATFORM = (90, 140, 40)
MARIO_COLOR = (255, 70, 50)
TITLE_COLOR = (255, 215, 0)  # gold
MENU_HIGHLIGHT = (255, 255, 255)
MENU_TEXT = (255, 255, 255)
GRAVITY = 0.65
JUMP_POWER = -13.5
RUN_SPEED = 4.8
MAX_FALL_SPEED = 12

# ─── States ──────────────────────────────────────────────────
STATE_MENU = 0
STATE_GAME = 1
STATE_EDITOR = 2
current_state = STATE_MENU

# ─── Fonts ───────────────────────────────────────────────────
font_title = pygame.font.Font(None, 96)  # BIG ASS TITLE
font_menu = pygame.font.Font(None, 48)  # menu options
font_small = pygame.font.Font(None, 32)  # subtle shit

# ─── Classes ─────────────────────────────────────────────────
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((32, 48), pygame.SRCALPHA)
        pygame.draw.rect(self.image, MARIO_COLOR, (0, 0, 32, 48))
        pygame.draw.circle(self.image, (255, 200, 180), (16, 16), 12)
        self.rect = self.image.get_rect(midbottom=(120, 300))
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.facing_right = True

    def update(self, platforms):
        keys = pygame.key.get_pressed()
        self.vel_x = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.vel_x = -RUN_SPEED
            self.facing_right = False
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.vel_x = RUN_SPEED
            self.facing_right = True
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and self.on_ground:
            self.vel_y = JUMP_POWER
            self.on_ground = False
        self.vel_y += GRAVITY
        if self.vel_y > MAX_FALL_SPEED:
            self.vel_y = MAX_FALL_SPEED
        self.rect.x += self.vel_x
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if self.vel_x > 0:
                    self.rect.right = plat.rect.left
                if self.vel_x < 0:
                    self.rect.left = plat.rect.right
        self.rect.y += self.vel_y
        self.on_ground = False
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if self.vel_y > 0:
                    self.rect.bottom = plat.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = plat.rect.bottom
                    self.vel_y = 0
        if self.rect.top > HEIGHT + 120:
            self.reset()

    def reset(self):
        self.rect.midbottom = (120, 300)
        self.vel_x = self.vel_y = 0

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, color=PLATFORM):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))

# ─── Menu Vars ───────────────────────────────────────────────
menu_options = ["1 PLAYER GAME", "LEVEL EDITOR", "SELECT EPISODE", "QUIT"]
menu_selected = 0
menu_title_y = HEIGHT + 200  # starts offscreen, scrolls in
title_scroll_speed = 1.5

# ─── Groups ──────────────────────────────────────────────────
all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
player = Player()
all_sprites.add(player)

# Hardcoded "episodes" as platform configs (simulating SMBX episodes without files)
episode_configs = [
    # Episode 1: Basic
    [
        Platform(-2000, HEIGHT - 40, 5000, 80, GROUND),
        Platform(220, 380, 180, 32),
        Platform(480, 300, 140, 32),
        Platform(720, 420, 220, 32),
        Platform(1100, 340, 160, 32),
        Platform(1450, 260, 120, 32),
    ],
    # Episode 2: Challenging
    [
        Platform(-2000, HEIGHT - 40, 5000, 80, GROUND),
        Platform(300, 400, 100, 32),
        Platform(500, 350, 120, 32),
        Platform(800, 280, 150, 32),
        Platform(1100, 450, 200, 32),
        Platform(1400, 200, 80, 32),
    ],
    # Episode 3: Advanced
    [
        Platform(-2000, HEIGHT - 40, 5000, 80, GROUND),
        Platform(250, 420, 160, 32),
        Platform(550, 320, 180, 32),
        Platform(850, 400, 140, 32),
        Platform(1150, 250, 200, 32),
        Platform(1500, 350, 120, 32),
    ]
]
current_episode = 0

def load_episode(episode_idx):
    global platforms, all_sprites
    platforms.empty()
    all_sprites.remove([s for s in all_sprites if isinstance(s, Platform)])
    for plat in episode_configs[episode_idx]:
        platforms.add(plat)
        all_sprites.add(plat)

load_episode(current_episode)  # Initial load

# ─── Camera ──────────────────────────────────────────────────
camera_x = 0

# ─── Main Loop ───────────────────────────────────────────────
running = True
while running:
    dt = clock.tick(60) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if current_state in (STATE_GAME, STATE_EDITOR):
                    current_state = STATE_MENU
                    player.reset()
                    camera_x = 0
                else:
                    running = False
            if current_state == STATE_MENU:
                if event.key == pygame.K_UP:
                    menu_selected = (menu_selected - 1) % len(menu_options)
                if event.key == pygame.K_DOWN:
                    menu_selected = (menu_selected + 1) % len(menu_options)
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if menu_selected == 0:  # 1 PLAYER GAME
                        current_state = STATE_GAME
                        player.reset()
                        camera_x = 0
                    elif menu_selected == 1:  # LEVEL EDITOR
                        current_state = STATE_EDITOR
                        player.reset()
                        camera_x = 0
                    elif menu_selected == 2:  # SELECT EPISODE
                        current_episode = (current_episode + 1) % len(episode_configs)
                        load_episode(current_episode)
                    else:  # QUIT
                        running = False
        if current_state == STATE_EDITOR:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                world_x = mouse_pos[0] + camera_x
                world_y = mouse_pos[1]
                if event.button == 1:  # Left click: place platform
                    new_plat = Platform(world_x - 70, world_y - 16, 140, 32)
                    platforms.add(new_plat)
                    all_sprites.add(new_plat)
                    # Add to current episode config for persistence
                    episode_configs[current_episode].append(new_plat)
                elif event.button == 3:  # Right click: remove platform
                    for plat in platforms:
                        plat_rect = plat.rect.move(-camera_x, 0)  # Screen rect
                        if plat_rect.collidepoint(mouse_pos):
                            plat.kill()
                            if plat in episode_configs[current_episode]:
                                episode_configs[current_episode].remove(plat)
                            break

    # ─── MENU UPDATE ───────────────────────────────────────────
    if current_state == STATE_MENU:
        menu_title_y -= title_scroll_speed
        if menu_title_y < HEIGHT * 0.3:
            menu_title_y = HEIGHT * 0.3
            title_scroll_speed *= 0.98  # slow to stop

    # ─── GAME/EDITOR UPDATE ────────────────────────────────────
    elif current_state == STATE_GAME:
        player.update(platforms)
        target_x = player.rect.centerx - WIDTH // 2
        camera_x += (target_x - camera_x) * 0.12
    elif current_state == STATE_EDITOR:
        # Editor camera control with keys
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            camera_x -= RUN_SPEED * 2
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            camera_x += RUN_SPEED * 2
        if camera_x < 0:
            camera_x = 0

    # ─── DRAW ──────────────────────────────────────────────────
    screen.fill(SKY)
    if current_state == STATE_MENU:
        # Title scroll-in
        title_surf = font_title.render("ULTRA", True, TITLE_COLOR)
        screen.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, menu_title_y))
        subtitle_surf = font_title.render("SMBX", True, TITLE_COLOR)
        screen.blit(subtitle_surf, (WIDTH // 2 - subtitle_surf.get_width() // 2, menu_title_y + 90))
        # Menu options
        for i, option in enumerate(menu_options):
            color = MENU_HIGHLIGHT if i == menu_selected else MENU_TEXT
            text_surf = font_menu.render(option, True, color)
            y_pos = HEIGHT * 0.6 + i * 70
            screen.blit(text_surf, (WIDTH // 2 - text_surf.get_width() // 2, y_pos))
        # Subtle prompt
        prompt_surf = font_small.render("↑↓ SELECT ENTER START ESC QUIT", True, (200, 200, 200))
        screen.blit(prompt_surf, (WIDTH // 2 - prompt_surf.get_width() // 2, HEIGHT - 80))
        # Current episode display
        ep_surf = font_small.render(f"Current Episode: {current_episode + 1}", True, (200, 200, 200))
        screen.blit(ep_surf, (WIDTH // 2 - ep_surf.get_width() // 2, HEIGHT - 40))
    else:
        # Game/editor world draw w/ camera
        for sprite in all_sprites:
            if isinstance(sprite, Player) and current_state == STATE_EDITOR:
                continue  # Hide player in editor
            screen.blit(sprite.image, (sprite.rect.x - camera_x, sprite.rect.y))
        # Hints
        if current_state == STATE_GAME:
            esc_surf = font_small.render("ESC: MENU", True, (255, 255, 255))
            screen.blit(esc_surf, (20, 20))
        elif current_state == STATE_EDITOR:
            edit_surf = font_small.render("LEFT CLICK: PLACE | RIGHT CLICK: REMOVE | A/D: SCROLL | ESC: MENU", True, (255, 255, 255))
            screen.blit(edit_surf, (20, 20))

    pygame.display.flip()

pygame.quit()
sys.exit()
