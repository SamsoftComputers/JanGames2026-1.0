import pygame
import sys
import math

# Initialize Pygame (works with pygame-ce)
pygame.init()

# --- Constants & Configuration ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
TITLE = "Ultra Mario 2D Bros. (1-1)"

# Colors
SKY_BLUE = (92, 148, 252)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (230, 0, 0)
GREEN = (0, 200, 0)
BROWN = (139, 69, 19)
GOLD = (255, 215, 0)
BRICK_COLOR = (179, 58, 58)
PIPE_GREEN = (34, 177, 76)

# Physics
GRAVITY = 0.8
FRICTION = 0.85
ACCELERATION = 0.6
JUMP_FORCE = -16
MAX_SPEED = 6

# Tile/Grid Size
TILE_SIZE = 40

# --- Asset Generation (No external files needed) ---
def create_textures():
    textures = {}

    # Mario (Red square with details)
    mario = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    mario.fill(RED)
    pygame.draw.rect(mario, (0, 0, 255), (10, 20, 20, 20)) # Overalls
    pygame.draw.circle(mario, (255, 200, 150), (20, 10), 8) # Face
    textures['mario'] = mario

    # Ground (Brown with grass top)
    ground = pygame.Surface((TILE_SIZE, TILE_SIZE))
    ground.fill(BROWN)
    pygame.draw.rect(ground, GREEN, (0, 0, TILE_SIZE, 8))
    textures['ground'] = ground

    # Brick
    brick = pygame.Surface((TILE_SIZE, TILE_SIZE))
    brick.fill(BRICK_COLOR)
    pygame.draw.rect(brick, BLACK, (0, 0, TILE_SIZE, TILE_SIZE), 2)
    pygame.draw.line(brick, BLACK, (0, TILE_SIZE//2), (TILE_SIZE, TILE_SIZE//2), 2)
    pygame.draw.line(brick, BLACK, (TILE_SIZE//2, 0), (TILE_SIZE//2, TILE_SIZE//2), 2)
    textures['brick'] = brick

    # Block (Question Box)
    qblock = pygame.Surface((TILE_SIZE, TILE_SIZE))
    qblock.fill(GOLD)
    pygame.draw.rect(qblock, BROWN, (0, 0, TILE_SIZE, TILE_SIZE), 4)
    # Question mark
    font = pygame.font.SysFont('arial', 24, bold=True)
    text = font.render("?", True, BROWN)
    qblock.blit(text, (12, 5))
    textures['qblock'] = qblock
    textures['empty_block'] = brick # Re-use brick for empty for now

    # Pipe (Simple green rects)
    pipe = pygame.Surface((TILE_SIZE, TILE_SIZE))
    pipe.fill(PIPE_GREEN)
    pygame.draw.rect(pipe, (0, 100, 0), (0, 0, TILE_SIZE, TILE_SIZE), 2)
    textures['pipe'] = pipe

    # Goomba (Brown mushroom thing)
    goomba = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    pygame.draw.circle(goomba, BROWN, (TILE_SIZE//2, TILE_SIZE//2 + 5), TILE_SIZE//2 - 2)
    pygame.draw.rect(goomba, BLACK, (10, 30, 8, 8)) # Foot 1
    pygame.draw.rect(goomba, BLACK, (22, 30, 8, 8)) # Foot 2
    textures['goomba'] = goomba

    return textures

TEXTURES = create_textures()
FONT = pygame.font.SysFont('arial', 20)
BIG_FONT = pygame.font.SysFont('arial', 48, bold=True)

# --- Classes ---

class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.centerx + int(SCREEN_WIDTH / 2)
        # Limit scrolling to map size
        x = min(0, x) # Left side
        x = max(-(self.width - SCREEN_WIDTH), x) # Right side
        self.camera = pygame.Rect(x, 0, self.width, self.height)

class Entity(pygame.sprite.Sprite):
    def __init__(self, x, y, texture_name):
        super().__init__()
        self.image = TEXTURES[texture_name]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Block(Entity):
    def __init__(self, x, y, type):
        super().__init__(x, y, type)
        self.type = type

class Enemy(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 'goomba')
        self.vel_x = -2
        self.vel_y = 0
        self.on_ground = False
        self.dead = False
        self.dead_timer = 0

    def update(self, blocks):
        if self.dead:
            self.dead_timer += 1
            if self.dead_timer > 30:
                self.kill()
            return

        self.vel_y += GRAVITY
        
        # Horizontal movement
        self.rect.x += self.vel_x
        hits = pygame.sprite.spritecollide(self, blocks, False)
        for block in hits:
            if self.vel_x > 0:
                self.rect.right = block.rect.left
                self.vel_x = -2
            elif self.vel_x < 0:
                self.rect.left = block.rect.right
                self.vel_x = 2

        # Vertical movement
        self.rect.y += self.vel_y
        hits = pygame.sprite.spritecollide(self, blocks, False)
        self.on_ground = False
        for block in hits:
            if self.vel_y > 0:
                self.rect.bottom = block.rect.top
                self.vel_y = 0
                self.on_ground = True
            elif self.vel_y < 0:
                self.rect.top = block.rect.bottom
                self.vel_y = 0

        # Die if falls off world
        if self.rect.y > SCREEN_HEIGHT + 100:
            self.kill()

    def squash(self):
        self.dead = True
        self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE//2))
        self.rect = self.image.get_rect(center=self.rect.center)
        self.rect.bottom += TILE_SIZE//2

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = TEXTURES['mario']
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.facing_right = True
        self.score = 0
        self.lives = 3
        self.is_dead = False

    def update(self, keys, blocks, enemies):
        if self.is_dead:
            self.rect.y += 5
            return

        # Input
        if keys[pygame.K_LEFT]:
            self.vel_x -= ACCELERATION
            self.facing_right = False
        elif keys[pygame.K_RIGHT]:
            self.vel_x += ACCELERATION
            self.facing_right = True
        else:
            self.vel_x *= FRICTION

        # Speed Cap
        if abs(self.vel_x) > MAX_SPEED:
            self.vel_x = MAX_SPEED if self.vel_x > 0 else -MAX_SPEED
        
        # Avoid infinitesimally small speeds
        if abs(self.vel_x) < 0.1:
            self.vel_x = 0

        # Jump
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = JUMP_FORCE
            self.on_ground = False

        self.vel_y += GRAVITY

        # Horizontal Collisions
        self.rect.x += int(self.vel_x)
        hits = pygame.sprite.spritecollide(self, blocks, False)
        for block in hits:
            if self.vel_x > 0:
                self.rect.right = block.rect.left
                self.vel_x = 0
            elif self.vel_x < 0:
                self.rect.left = block.rect.right
                self.vel_x = 0

        # Vertical Collisions
        self.rect.y += int(self.vel_y)
        self.on_ground = False
        hits = pygame.sprite.spritecollide(self, blocks, False)
        for block in hits:
            if self.vel_y > 0:
                self.rect.bottom = block.rect.top
                self.vel_y = 0
                self.on_ground = True
            elif self.vel_y < 0:
                self.rect.top = block.rect.bottom
                self.vel_y = 0
                # Hit block logic could go here (break brick)

        # Enemy Collisions
        enemy_hits = pygame.sprite.spritecollide(self, enemies, False)
        for enemy in enemy_hits:
            if enemy.dead:
                continue
            
            # Check if jumped on top
            if self.vel_y > 0 and self.rect.bottom < enemy.rect.centery + 10:
                enemy.squash()
                self.vel_y = -8 # Bounce
                self.score += 100
            else:
                self.die()

        # World Boundary
        if self.rect.y > SCREEN_HEIGHT:
            self.die()

    def die(self):
        if not self.is_dead:
            self.is_dead = True
            self.lives -= 1
            self.vel_y = -10 # Death hop
            # Sound effect placeholder

class Level:
    def __init__(self, layout_data):
        self.blocks = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.width = len(layout_data[0]) * TILE_SIZE
        self.height = len(layout_data) * TILE_SIZE
        self.player_spawn = (100, 100)

        row_count = 0
        for row in layout_data:
            col_count = 0
            for tile in row:
                x = col_count * TILE_SIZE
                y = row_count * TILE_SIZE
                
                if tile == 'G':
                    b = Block(x, y, 'ground')
                    self.blocks.add(b)
                elif tile == 'B':
                    b = Block(x, y, 'brick')
                    self.blocks.add(b)
                elif tile == '?':
                    b = Block(x, y, 'qblock')
                    self.blocks.add(b)
                elif tile == 'P':
                    b = Block(x, y, 'pipe')
                    self.blocks.add(b)
                elif tile == 'E':
                    e = Enemy(x, y)
                    self.enemies.add(e)
                elif tile == '@':
                    self.player_spawn = (x, y)
                
                col_count += 1
            row_count += 1

# --- Game States ---

def draw_text(screen, text, font, color, x, y, center=False):
    img = font.render(text, True, color)
    if center:
        rect = img.get_rect(center=(x, y))
        screen.blit(img, rect)
    else:
        screen.blit(img, (x, y))

def main_menu(screen):
    running = True
    clock = pygame.time.Clock()
    selected = 0
    options = ["World 1-1", "World 1-2 (Locked)", "Quit"]

    while running:
        screen.fill(SKY_BLUE)
        
        # Draw Title
        draw_text(screen, "ULTRA MARIO 2D BROS", BIG_FONT, WHITE, SCREEN_WIDTH//2, 150, center=True)
        draw_text(screen, "Press SPACE to Select", FONT, WHITE, SCREEN_WIDTH//2, 200, center=True)

        # Draw Menu
        for i, option in enumerate(options):
            color = GOLD if i == selected else WHITE
            draw_text(screen, option, FONT, color, SCREEN_WIDTH//2, 300 + i * 40, center=True)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "Quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if selected == 0:
                        return "1-1"
                    elif selected == 2:
                        return "Quit"

        pygame.display.flip()
        clock.tick(FPS)

def run_level(screen, level_num):
    # Level Layout (Strings represent tiles)
    # G=Ground, B=Brick, ?=QBlock, P=Pipe, E=Enemy, @=Player Start
    
    # 100 tiles wide roughly
    level_map = [
        "                                                                                                    ",
        "                                                                                                    ",
        "                                                                                                    ",
        "                                                                                                    ",
        "                                                                                                    ",
        "                  ?                                                                                 ",
        "                BB?BB                     ?   ?  ?                                                  ",
        "                                         B?B B?B B?B                                                ",
        "        @                E           E                  E     P    E    P                           ",
        "      BBB               BBBB        BBBB               BBBB  PP   BB   PP     E      E           F  ",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG"
    ]

    level = Level(level_map)
    player = Player(*level.player_spawn)
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)
    
    camera = Camera(level.width, level.height)
    clock = pygame.time.Clock()
    running = True

    while running:
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return # Back to menu

        # Update
        player.update(keys, level.blocks, level.enemies)
        level.enemies.update(level.blocks)
        camera.update(player)

        if player.rect.y > SCREEN_HEIGHT + 200:
            # Respawn logic or Game Over
            if player.lives > 0:
                player.rect.topleft = level.player_spawn
                player.vel_x, player.vel_y = 0, 0
                player.is_dead = False
                camera.camera.x = 0 # Reset camera roughly
            else:
                return # Game Over

        # Draw
        screen.fill(SKY_BLUE)

        for sprite in level.blocks:
            screen.blit(sprite.image, camera.apply(sprite))
        
        for sprite in level.enemies:
            screen.blit(sprite.image, camera.apply(sprite))
        
        screen.blit(player.image, camera.apply(player))

        # HUD
        draw_text(screen, f"MARIO", FONT, WHITE, 50, 20)
        draw_text(screen, f"{player.score:06}", FONT, WHITE, 50, 45)
        
        draw_text(screen, f"WORLD", FONT, WHITE, 400, 20)
        draw_text(screen, f"1-1", FONT, WHITE, 400, 45)

        draw_text(screen, f"LIVES", FONT, WHITE, 700, 20)
        draw_text(screen, f"{player.lives}", FONT, WHITE, 700, 45)

        pygame.display.flip()
        clock.tick(FPS)

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)

    while True:
        choice = main_menu(screen)
        if choice == "Quit":
            break
        elif choice == "1-1":
            run_level(screen, 1)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
