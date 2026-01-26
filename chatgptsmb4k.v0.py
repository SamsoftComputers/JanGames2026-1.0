import sys
import pygame

# =============================
# CONFIG
# =============================
SCREEN_W, SCREEN_H = 800, 480
FPS = 60
TILE = 32

GRAVITY = 0.6
JUMP_FORCE = -12
MOVE_SPEED = 4

WORLD_W = 2000  # level width in pixels (camera clamps to this)

# Colors (NES-ish)
SKY = (92, 148, 252)
GROUND = (181, 101, 29)
BRICK = (200, 76, 12)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# =============================
# HELPERS
# =============================
def draw_text(
    surf: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    x: int,
    y: int,
    color=WHITE,
    center: bool = True,
    shadow: bool = True,
):
    """Draw text with a tiny shadow (NES-ish)."""
    img = font.render(text, True, color)
    rect = img.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)

    if shadow:
        sh = font.render(text, True, BLACK)
        sh_rect = sh.get_rect()
        if center:
            sh_rect.center = (x + 2, y + 2)
        else:
            sh_rect.topleft = (x + 2, y + 2)
        surf.blit(sh, sh_rect)

    surf.blit(img, rect)


# =============================
# CLASSES
# =============================
class Block(pygame.Rect):
    def draw(self, surf: pygame.Surface, cam_x: int):
        pygame.draw.rect(surf, BRICK, (self.x - cam_x, self.y, self.width, self.height))


class Player:
    def __init__(self):
        self.spawn()

    def spawn(self):
        self.rect = pygame.Rect(100, 300, 24, 32)
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.on_ground = False
        self.dead = False

    def update(self, blocks):
        keys = pygame.key.get_pressed()
        self.vel_x = 0.0

        if keys[pygame.K_LEFT]:
            self.vel_x = -MOVE_SPEED
        if keys[pygame.K_RIGHT]:
            self.vel_x = MOVE_SPEED

        # Jump
        if keys[pygame.K_z] and self.on_ground:
            self.vel_y = JUMP_FORCE
            self.on_ground = False

        # Horizontal
        self.rect.x += int(self.vel_x)
        for b in blocks:
            if self.rect.colliderect(b):
                if self.vel_x > 0:
                    self.rect.right = b.left
                elif self.vel_x < 0:
                    self.rect.left = b.right

        # Vertical
        self.vel_y += GRAVITY
        self.rect.y += int(self.vel_y)
        self.on_ground = False

        for b in blocks:
            if self.rect.colliderect(b):
                if self.vel_y > 0:
                    self.rect.bottom = b.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = b.bottom
                    self.vel_y = 0

        # Fell off the world (simple death)
        if self.rect.top > SCREEN_H + 200:
            self.dead = True

    def draw(self, surf, cam_x):
        pygame.draw.rect(
            surf,
            RED,
            (self.rect.x - cam_x, self.rect.y, self.rect.width, self.rect.height),
        )


class Goomba:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 28, 28)
        self.vel = -1.2
        self.alive = True

    def update(self, blocks):
        if not self.alive:
            return

        self.rect.x += int(self.vel)

        for b in blocks:
            if self.rect.colliderect(b):
                self.vel *= -1
                # Nudge out to avoid sticking
                self.rect.x += int(self.vel * 2)

    def draw(self, surf, cam_x):
        if self.alive:
            pygame.draw.rect(
                surf,
                (150, 75, 0),
                (self.rect.x - cam_x, self.rect.y, 28, 28),
            )


# =============================
# LEVEL BUILD
# =============================
def build_level():
    blocks = []
    # Ground
    for x in range(0, WORLD_W, TILE):
        blocks.append(Block(x, SCREEN_H - TILE, TILE, TILE))

    # Floating bricks
    for x in range(5, 9):
        blocks.append(Block(x * TILE, SCREEN_H - TILE * 4, TILE, TILE))

    # A few more bricks further out
    for x in range(20, 25):
        if x % 2 == 0:
            blocks.append(Block(x * TILE, SCREEN_H - TILE * 6, TILE, TILE))

    enemies = [
        Goomba(500, SCREEN_H - TILE - 28),
        Goomba(900, SCREEN_H - TILE - 28),
        Goomba(1400, SCREEN_H - TILE - 28),
    ]
    return blocks, enemies


# =============================
# GAME STATE MACHINE
# =============================
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Super Mario Bros (Pygame)")
        self.clock = pygame.time.Clock()

        # Fonts
        self.font_title = pygame.font.SysFont("arial", 48, bold=True)
        self.font_big = pygame.font.SysFont("arial", 28, bold=True)
        self.font_ui = pygame.font.SysFont("arial", 20)

        self.state = "menu"
        self.menu_choice = 0  # 0 = start, 1 = quit

        # World
        self.blocks = []
        self.enemies = []
        self.player = Player()
        self.camera_x = 0

        self.reset_world()

    def reset_world(self):
        self.blocks, self.enemies = build_level()
        self.player.spawn()
        self.camera_x = 0

    def clamp_camera(self):
        target = self.player.rect.centerx - SCREEN_W // 2
        self.camera_x = max(0, min(target, WORLD_W - SCREEN_W))

    # ---------- MENU ----------
    def update_menu(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.menu_choice = (self.menu_choice - 1) % 2
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    self.menu_choice = (self.menu_choice + 1) % 2

                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if self.menu_choice == 0:
                        self.reset_world()
                        self.state = "playing"
                    else:
                        pygame.quit()
                        sys.exit()

                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

    def draw_menu(self):
        self.screen.fill(SKY)

        draw_text(
            self.screen,
            "SUPER MARIO BROS",
            self.font_title,
            SCREEN_W // 2,
            140,
            color=WHITE,
        )
        # Required slogan line:
        draw_text(
            self.screen,
            "SMB1 ULTRA MARIO 2D BROS.",
            self.font_big,
            SCREEN_W // 2,
            200,
            color=WHITE,
        )

        # Options
        start_text = "START GAME"
        quit_text = "QUIT"

        y0 = 290
        draw_text(
            self.screen,
            ("> " if self.menu_choice == 0 else "  ") + start_text,
            self.font_big,
            SCREEN_W // 2,
            y0,
            color=WHITE,
        )
        draw_text(
            self.screen,
            ("> " if self.menu_choice == 1 else "  ") + quit_text,
            self.font_big,
            SCREEN_W // 2,
            y0 + 44,
            color=WHITE,
        )

        draw_text(
            self.screen,
            "Arrows/WASD: move menu • Enter/Space: select • Esc: quit",
            self.font_ui,
            SCREEN_W // 2,
            SCREEN_H - 40,
            color=WHITE,
        )
        draw_text(
            self.screen,
            "In-game: LEFT/RIGHT to move • Z to jump • R to restart • Esc for menu",
            self.font_ui,
            SCREEN_W // 2,
            SCREEN_H - 18,
            color=WHITE,
        )

    # ---------- PLAYING ----------
    def update_playing(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = "menu"
                if event.key == pygame.K_r:
                    self.reset_world()

        self.player.update(self.blocks)

        for e in self.enemies:
            e.update(self.blocks)

        # Enemy stomp / damage
        for e in self.enemies:
            if not e.alive:
                continue
            if self.player.rect.colliderect(e.rect):
                # Simple stomp check: falling and player's feet near enemy top
                stomp_zone = e.rect.top + 10
                if self.player.vel_y > 0 and self.player.rect.bottom <= stomp_zone:
                    e.alive = False
                    self.player.vel_y = -6
                else:
                    self.player.dead = True

        self.clamp_camera()

        if self.player.dead:
            self.state = "gameover"

    def draw_playing(self):
        self.screen.fill(SKY)

        for b in self.blocks:
            b.draw(self.screen, self.camera_x)

        for e in self.enemies:
            e.draw(self.screen, self.camera_x)

        self.player.draw(self.screen, self.camera_x)

        # Tiny HUD
        draw_text(
            self.screen,
            "Z: Jump   R: Restart   Esc: Menu",
            self.font_ui,
            10,
            10,
            color=WHITE,
            center=False,
            shadow=True,
        )

    # ---------- GAME OVER ----------
    def update_gameover(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_r, pygame.K_RETURN, pygame.K_SPACE):
                    self.reset_world()
                    self.state = "playing"
                if event.key == pygame.K_ESCAPE:
                    self.state = "menu"

    def draw_gameover(self):
        # Draw last frame behind overlay
        self.draw_playing()

        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.screen.blit(overlay, (0, 0))

        draw_text(
            self.screen,
            "GAME OVER",
            self.font_title,
            SCREEN_W // 2,
            SCREEN_H // 2 - 40,
            color=WHITE,
        )
        draw_text(
            self.screen,
            "Press R / Enter to restart",
            self.font_big,
            SCREEN_W // 2,
            SCREEN_H // 2 + 20,
            color=WHITE,
        )
        draw_text(
            self.screen,
            "Press Esc for menu",
            self.font_big,
            SCREEN_W // 2,
            SCREEN_H // 2 + 60,
            color=WHITE,
        )

    # ---------- LOOP ----------
    def run(self):
        while True:
            self.clock.tick(FPS)
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            if self.state == "menu":
                self.update_menu(events)
                self.draw_menu()
            elif self.state == "playing":
                self.update_playing(events)
                self.draw_playing()
            elif self.state == "gameover":
                self.update_gameover(events)
                self.draw_gameover()

            pygame.display.flip()


def main():
    Game().run()


if __name__ == "__main__":
    main()
