import sys
import pygame

# =============================
# CONFIG - NES/FAMICOM STYLE
# =============================
SCREEN_W, SCREEN_H = 256 * 2, 240 * 2  # Double NES resolution for modern displays
FPS = 60  # NES runs at ~60.098 FPS
TILE = 16  # NES uses 16x16 tiles

GRAVITY = 0.5
JUMP_FORCE = -10
MOVE_SPEED = 2.5

WORLD_W = 2000

# NES Palette Colors (more authentic)
NES_SKY = (108, 140, 255)        # Sky blue
NES_BROWN = (148, 92, 44)        # Ground brown
NES_BRICK = (180, 80, 56)        # Brick color
NES_PIPE_GREEN = (0, 148, 0)     # Pipe green
NES_WHITE = (252, 252, 252)      # White
NES_BLACK = (0, 0, 0)            # Black
NES_RED = (228, 0, 24)           # Mario red
NES_BLUE = (36, 72, 252)         # Mario blue
NES_GOOMBA = (188, 112, 48)      # Goomba brown
NES_COIN = (252, 216, 0)         # Coin yellow

# =============================
# HELPERS - NES STYLE
# =============================
def draw_text_nes(
    surf: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    x: int,
    y: int,
    color=NES_WHITE,
    bg_color=NES_RED,
    center: bool = True,
    pixelated: bool = True,
):
    """Draw NES-style text with pixelated edges."""
    if pixelated:
        # Create text with sharp edges (no anti-aliasing)
        img = font.render(text, False, color)
    else:
        img = font.render(text, True, color)

    # Only render background if a color is provided
    bg_img = None
    if bg_color is not None:
        if pixelated:
            bg_img = font.render(text, False, bg_color)
        else:
            bg_img = font.render(text, True, bg_color)
    
    rect = img.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    
    # NES style: draw background offset for depth
    if bg_img:
        bg_rect = bg_img.get_rect()
        if center:
            bg_rect.center = (x + 2, y + 2)
        else:
            bg_rect.topleft = (x + 2, y + 2)
        surf.blit(bg_img, bg_rect)
    
    surf.blit(img, rect)

def draw_pixel_border(rect, surf, color, offset_x=0):
    """Draw a pixelated border around a rectangle (NES style)."""
    x, y, w, h = rect.x - offset_x, rect.y, rect.w, rect.h
    
    # Top and bottom
    for i in range(0, w, 2):
        pygame.draw.rect(surf, color, (x + i, y, 2, 2))
        pygame.draw.rect(surf, color, (x + i, y + h - 2, 2, 2))
    
    # Left and right
    for i in range(0, h, 2):
        pygame.draw.rect(surf, color, (x, y + i, 2, 2))
        pygame.draw.rect(surf, color, (x + w - 2, y + i, 2, 2))

def draw_brick_pattern(rect, surf, cam_x):
    """Draw NES-style brick pattern."""
    x, y = rect.x - cam_x, rect.y
    w, h = rect.w, rect.h
    
    # Brick base
    pygame.draw.rect(surf, NES_BRICK, (x, y, w, h))
    
    # Brick pattern (dots)
    dot_color = (200, 100, 72)
    for i in range(0, w, 8):
        for j in range(0, h, 8):
            if (i // 8 + j // 8) % 2 == 0:
                pygame.draw.rect(surf, dot_color, (x + i + 2, y + j + 2, 4, 4))

# =============================
# CLASSES - NES STYLE
# =============================
class Block(pygame.Rect):
    def draw(self, surf: pygame.Surface, cam_x: int):
        # NES-style brick with pattern
        draw_brick_pattern(self, surf, cam_x)
        
        # Add pixelated border
        draw_pixel_border(self, surf, (160, 70, 50), cam_x)

class Cloud:
    """NES-style decorative clouds."""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 0.3
    
    def update(self):
        self.x -= self.speed
        if self.x < -100:
            self.x = WORLD_W + 100
    
    def draw(self, surf, cam_x):
        x = self.x - cam_x
        y = self.y
        
        # NES cloud shape (simple rectangles)
        pygame.draw.rect(surf, NES_WHITE, (x, y, 24, 8))
        pygame.draw.rect(surf, NES_WHITE, (x + 8, y - 8, 16, 8))
        pygame.draw.rect(surf, NES_WHITE, (x + 16, y - 16, 8, 8))

class Coin:
    """NES-style coins."""
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 12, 16)
        self.collected = False
        self.anim_offset = 0
        self.anim_direction = 1
    
    def update(self):
        # Simple up-down animation
        self.anim_offset += self.anim_direction * 0.5
        if abs(self.anim_offset) > 3:
            self.anim_direction *= -1
    
    def draw(self, surf, cam_x):
        if not self.collected:
            x = self.rect.x - cam_x
            y = self.rect.y + self.anim_offset
            
            # NES coin (yellow circle with highlight)
            pygame.draw.circle(surf, NES_COIN, (x + 6, y + 8), 6)
            pygame.draw.circle(surf, (252, 240, 80), (x + 6, y + 8), 4)
            
            # Coin highlight
            pygame.draw.circle(surf, (252, 252, 180), (x + 3, y + 5), 2)

class Player:
    def __init__(self):
        self.spawn()
        self.facing_right = True
        self.walk_anim = 0
        self.jump_anim = 0
    
    def spawn(self):
        self.rect = pygame.Rect(100, 300, 16, 24)  # NES Mario is 16x24
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.on_ground = False
        self.dead = False
        self.invincible = 0
    
    def update(self, blocks):
        if self.invincible > 0:
            self.invincible -= 1
        
        keys = pygame.key.get_pressed()
        self.vel_x = 0.0
        
        if keys[pygame.K_LEFT]:
            self.vel_x = -MOVE_SPEED
            self.facing_right = False
            self.walk_anim += 0.2
        if keys[pygame.K_RIGHT]:
            self.vel_x = MOVE_SPEED
            self.facing_right = True
            self.walk_anim += 0.2
        
        # Reset walk animation when not moving
        if self.vel_x == 0:
            self.walk_anim = 0
        
        # Jump
        if keys[pygame.K_z] and self.on_ground:
            self.vel_y = JUMP_FORCE
            self.on_ground = False
            self.jump_anim = 10
        
        # Horizontal movement with collision
        self.rect.x += int(self.vel_x)
        for b in blocks:
            if self.rect.colliderect(b):
                if self.vel_x > 0:
                    self.rect.right = b.left
                elif self.vel_x < 0:
                    self.rect.left = b.right
        
        # Vertical movement with collision
        self.vel_y += GRAVITY
        self.rect.y += int(self.vel_y)
        self.on_ground = False
        
        for b in blocks:
            if self.rect.colliderect(b):
                if self.vel_y > 0:
                    self.rect.bottom = b.top
                    self.vel_y = 0
                    self.on_ground = True
                    self.jump_anim = 0
                elif self.vel_y < 0:
                    self.rect.top = b.bottom
                    self.vel_y = 0
        
        # Fell off the world
        if self.rect.top > SCREEN_H + 200:
            self.dead = True
    
    def draw(self, surf, cam_x):
        if self.invincible > 0 and self.invincible % 4 < 2:
            return  # Flash when invincible
        
        x = self.rect.x - cam_x
        y = self.rect.y
        
        # NES Mario-style sprite (simplified)
        # Body (red overalls)
        pygame.draw.rect(surf, NES_RED, (x + 4, y + 8, 8, 12))
        
        # Head
        pygame.draw.rect(surf, (255, 200, 160), (x + 4, y, 8, 8))
        
        # Hat (red with M shape)
        pygame.draw.rect(surf, NES_RED, (x + 2, y, 12, 4))
        
        # Overalls straps
        pygame.draw.rect(surf, NES_BLUE, (x + 4, y + 8, 2, 4))
        pygame.draw.rect(surf, NES_BLUE, (x + 10, y + 8, 2, 4))
        
        # Legs (walk animation)
        leg_offset = int(abs(self.walk_anim) % 4) - 2 if self.vel_x != 0 else 0
        pygame.draw.rect(surf, NES_RED, (x + 4, y + 20, 3, 4))
        pygame.draw.rect(surf, NES_RED, (x + 9, y + 20 + leg_offset, 3, 4))
        
        # Arms (jump animation)
        if not self.on_ground:
            arm_y = y + 8 + self.jump_anim // 2
            pygame.draw.rect(surf, (255, 200, 160), (x + 1, arm_y, 3, 4))
            pygame.draw.rect(surf, (255, 200, 160), (x + 12, arm_y, 3, 4))
        
        # Pixelated outline
        outline_color = NES_BLACK
        for i in range(0, 16, 2):
            for j in range(0, 24, 2):
                if (i == 0 or i == 14 or j == 0 or j == 22) and (i + j) % 4 == 0:
                    pygame.draw.rect(surf, outline_color, (x + i, y + j, 2, 2))

class Goomba:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 16, 16)  # NES Goomba is 16x16
        self.vel = -1.0
        self.alive = True
        self.walk_anim = 0
    
    def update(self, blocks):
        if not self.alive:
            return
        
        self.walk_anim += 0.1
        self.rect.x += int(self.vel)
        
        for b in blocks:
            if self.rect.colliderect(b):
                self.vel *= -1
                self.rect.x += int(self.vel * 2)
    
    def draw(self, surf, cam_x):
        if not self.alive:
            return
        
        x = self.rect.x - cam_x
        y = self.rect.y
        
        # NES Goomba body
        pygame.draw.ellipse(surf, NES_GOOMBA, (x + 2, y + 4, 12, 10))
        
        # Head
        pygame.draw.ellipse(surf, NES_GOOMBA, (x, y, 16, 12))
        
        # Feet (walk animation)
        foot_offset = int(self.walk_anim % 4) - 2
        pygame.draw.rect(surf, (120, 60, 20), (x + 3, y + 14, 3, 2))
        pygame.draw.rect(surf, (120, 60, 20), (x + 10, y + 14 + foot_offset, 3, 2))
        
        # Eyes
        pygame.draw.rect(surf, NES_WHITE, (x + 4, y + 4, 3, 3))
        pygame.draw.rect(surf, NES_WHITE, (x + 9, y + 4, 3, 3))
        pygame.draw.rect(surf, NES_BLACK, (x + 5, y + 5, 2, 2))
        pygame.draw.rect(surf, NES_BLACK, (x + 10, y + 5, 2, 2))
        
        # Eyebrows
        pygame.draw.rect(surf, NES_BLACK, (x + 3, y + 3, 5, 1))
        pygame.draw.rect(surf, NES_BLACK, (x + 8, y + 3, 5, 1))

class Bush:
    """NES-style decorative bushes."""
    def __init__(self, x, y, size=3):
        self.x = x
        self.y = y
        self.size = size  # Number of bush segments
    
    def draw(self, surf, cam_x):
        x = self.x - cam_x
        y = self.y
        
        # Bush segments (circles)
        for i in range(self.size):
            radius = 12 - i * 2
            pygame.draw.circle(surf, NES_PIPE_GREEN, 
                             (x + 16 + i * 12, y + 8), radius)
            pygame.draw.circle(surf, (0, 168, 0), 
                             (x + 16 + i * 12, y + 8), radius - 2)

# =============================
# LEVEL BUILD - NES STYLE
# =============================
def build_level():
    blocks = []
    clouds = []
    bushes = []
    coins = []
    
    # Ground with NES-style pattern
    for x in range(0, WORLD_W, TILE):
        blocks.append(Block(x, SCREEN_H - TILE, TILE, TILE))
        # Add ground pattern (dots)
        if x % 32 == 0:
            blocks.append(Block(x, SCREEN_H - TILE * 2, TILE, TILE))
    
    # Question blocks (NES style)
    for x in range(6, 10):
        blocks.append(Block(x * TILE, SCREEN_H - TILE * 5, TILE, TILE))
    
    # Brick platforms
    for x in range(15, 20):
        blocks.append(Block(x * TILE, SCREEN_H - TILE * 7, TILE, TILE))
        coins.append(Coin(x * TILE + 2, SCREEN_H - TILE * 8))
    
    # Pipe (NES style)
    pipe_height = 3
    for x in range(12, 14):
        for y in range(SCREEN_H - TILE * pipe_height, SCREEN_H, TILE):
            blocks.append(Block(x * TILE, y, TILE, TILE))
    
    # Clouds
    clouds.append(Cloud(200, 80))
    clouds.append(Cloud(500, 120))
    clouds.append(Cloud(900, 60))
    clouds.append(Cloud(1200, 100))
    
    # Bushes
    bushes.append(Bush(300, SCREEN_H - TILE - 16, 2))
    bushes.append(Bush(700, SCREEN_H - TILE - 16, 3))
    bushes.append(Bush(1100, SCREEN_H - TILE - 16, 2))
    
    enemies = [
        Goomba(500, SCREEN_H - TILE - 16),
        Goomba(800, SCREEN_H - TILE - 16),
        Goomba(1400, SCREEN_H - TILE - 16),
    ]
    
    return blocks, enemies, clouds, bushes, coins

# =============================
# GAME STATE MACHINE - NES STYLE
# =============================
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("SUPER MARIO BROS. - NES Edition")
        self.clock = pygame.time.Clock()
        
        # NES-style fonts (pixelated)
        try:
            self.font_title = pygame.font.Font(None, 48)
            self.font_big = pygame.font.Font(None, 32)
            self.font_ui = pygame.font.Font(None, 20)
        except:
            self.font_title = pygame.font.SysFont("courier", 48, bold=True)
            self.font_big = pygame.font.SysFont("courier", 32, bold=True)
            self.font_ui = pygame.font.SysFont("courier", 20)
        
        self.state = "menu"
        self.menu_choice = 0
        self.score = 0
        self.lives = 3
        
        # World objects
        self.blocks = []
        self.enemies = []
        self.clouds = []
        self.bushes = []
        self.coins = []
        self.player = Player()
        self.camera_x = 0
        
        self.reset_world()
    
    def reset_world(self):
        self.blocks, self.enemies, self.clouds, self.bushes, self.coins = build_level()
        self.player.spawn()
        self.camera_x = 0
        self.score = 0
    
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
                        self.lives = 3
                        self.reset_world()
                        self.state = "playing"
                    else:
                        pygame.quit()
                        sys.exit()
                
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
    
    def draw_menu(self):
        # NES-style background
        self.screen.fill(NES_SKY)
        
        # Draw clouds in background
        for cloud in self.clouds:
            cloud.draw(self.screen, 0)
        
        # Ground strip at bottom
        pygame.draw.rect(self.screen, NES_BROWN, 
                        (0, SCREEN_H - 40, SCREEN_W, 40))
        
        # Title with NES style
        draw_text_nes(
            self.screen,
            "SUPER MARIO BROS.",
            self.font_title,
            SCREEN_W // 2,
            100,
            color=NES_WHITE,
            bg_color=NES_RED,
        )
        
        # Required slogan
        draw_text_nes(
            self.screen,
            "SMB1 ULTRA MARIO 2D BROS.",
            self.font_big,
            SCREEN_W // 2,
            160,
            color=NES_WHITE,
            bg_color=NES_BLUE,
        )
        
        # Menu options with selection indicator
        options = ["START GAME", "QUIT"]
        y_start = 250
        
        for i, option in enumerate(options):
            color = NES_YELLOW if i == self.menu_choice else NES_WHITE
            prefix = ">" if i == self.menu_choice else " "
            
            draw_text_nes(
                self.screen,
                f"{prefix} {option}",
                self.font_big,
                SCREEN_W // 2,
                y_start + i * 50,
                color=color,
                bg_color=NES_BLACK,
            )
        
        # Instructions (NES style bottom text)
        draw_text_nes(
            self.screen,
            "USE ARROWS/WASD TO SELECT, ENTER TO CONFIRM",
            self.font_ui,
            SCREEN_W // 2,
            SCREEN_H - 60,
            color=NES_WHITE,
            bg_color=NES_BLACK,
        )
    
    # ---------- PLAYING ----------
    def update_playing(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = "menu"
                if event.key == pygame.K_r:
                    self.reset_world()
        
        # Update objects
        self.player.update(self.blocks)
        
        for cloud in self.clouds:
            cloud.update()
        
        for enemy in self.enemies:
            enemy.update(self.blocks)
        
        for coin in self.coins:
            if not coin.collected:
                coin.update()
        
        # Coin collection
        for coin in self.coins:
            if not coin.collected and self.player.rect.colliderect(coin.rect):
                coin.collected = True
                self.score += 100
        
        # Enemy collisions
        for enemy in self.enemies:
            if not enemy.alive:
                continue
            
            if self.player.rect.colliderect(enemy.rect):
                # Stomp check
                if self.player.vel_y > 0 and self.player.rect.bottom <= enemy.rect.top + 10:
                    enemy.alive = False
                    self.player.vel_y = -6
                    self.score += 200
                elif self.player.invincible == 0:
                    self.lives -= 1
                    self.player.invincible = 30
                    if self.lives <= 0:
                        self.player.dead = True
        
        self.clamp_camera()
        
        if self.player.dead:
            self.state = "gameover"
    
    def draw_playing(self):
        # NES-style sky
        self.screen.fill(NES_SKY)
        
        # Draw clouds
        for cloud in self.clouds:
            cloud.draw(self.screen, self.camera_x)
        
        # Draw bushes
        for bush in self.bushes:
            bush.draw(self.screen, self.camera_x)
        
        # Draw blocks
        for b in self.blocks:
            b.draw(self.screen, self.camera_x)
        
        # Draw enemies
        for e in self.enemies:
            e.draw(self.screen, self.camera_x)
        
        # Draw coins
        for coin in self.coins:
            coin.draw(self.screen, self.camera_x)
        
        # Draw player
        self.player.draw(self.screen, self.camera_x)
        
        # NES-style HUD
        pygame.draw.rect(self.screen, NES_BLACK, (0, 0, SCREEN_W, 24))
        
        draw_text_nes(
            self.screen,
            f"MARIO    {self.score:06d}",
            self.font_ui,
            10,
            12,
            color=NES_WHITE,
            bg_color=None,
            center=False,
            pixelated=True,
        )
        
        draw_text_nes(
            self.screen,
            f"× {self.lives}",
            self.font_ui,
            SCREEN_W - 60,
            12,
            color=NES_WHITE,
            bg_color=None,
            center=False,
            pixelated=True,
        )
        
        # Draw small Mario icon next to lives
        pygame.draw.rect(self.screen, NES_RED, (SCREEN_W - 80, 8, 8, 12))
        pygame.draw.rect(self.screen, (255, 200, 160), (SCREEN_W - 80, 4, 8, 4))
    
    # ---------- GAME OVER ----------
    def update_gameover(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_r, pygame.K_RETURN, pygame.K_SPACE):
                    self.lives = 3
                    self.reset_world()
                    self.state = "playing"
                if event.key == pygame.K_ESCAPE:
                    self.state = "menu"
    
    def draw_gameover(self):
        # Draw game behind overlay
        self.draw_playing()
        
        # NES-style dark overlay
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Game over text (NES style)
        draw_text_nes(
            self.screen,
            "GAME OVER",
            self.font_title,
            SCREEN_W // 2,
            SCREEN_H // 2 - 40,
            color=NES_WHITE,
            bg_color=NES_RED,
        )
        
        draw_text_nes(
            self.screen,
            f"SCORE: {self.score:06d}",
            self.font_big,
            SCREEN_W // 2,
            SCREEN_H // 2 + 10,
            color=NES_WHITE,
            bg_color=NES_BLACK,
        )
        
        draw_text_nes(
            self.screen,
            "PRESS ENTER TO RESTART",
            self.font_big,
            SCREEN_W // 2,
            SCREEN_H // 2 + 50,
            color=NES_WHITE,
            bg_color=NES_BLACK,
        )
        
        draw_text_nes(
            self.screen,
            "PRESS ESC FOR MENU",
            self.font_ui,
            SCREEN_W // 2,
            SCREEN_H // 2 + 90,
            color=NES_WHITE,
            bg_color=NES_BLACK,
        )
    
    # ---------- MAIN LOOP ----------
    def run(self):
        while True:
            # Lock to 60 FPS (NES speed)
            self.clock.tick(FPS)
            
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            # State machine
            if self.state == "menu":
                self.update_menu(events)
                self.draw_menu()
            elif self.state == "playing":
                self.update_playing(events)
                self.draw_playing()
            elif self.state == "gameover":
                self.update_gameover(events)
                self.draw_gameover()
            
            # Update display
            pygame.display.flip()

def main():
    # Add NES yellow to global colors
    global NES_YELLOW
    NES_YELLOW = NES_COIN
    
    Game().run()

if __name__ == "__main__":
    main()