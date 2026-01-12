import pygame
import sys
import math
import random

pygame.init()
pygame.mixer.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
TILE_SIZE = 32
GROUND_Y = 13 * TILE_SIZE  # Ground top at y=416
GRAVITY = 0.5
MAX_FALL_SPEED = 8

# Colors
SKY_BLUE = (92, 148, 252)
BLACK = (0, 0, 0)
BROWN = (180, 92, 4)      # Ground/brick
YELLOW = (252, 220, 92)   # Block
GREEN = (0, 168, 0)       # Pipe
RED = (252, 60, 20)       # Mario/enemy
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
ORANGE = (255, 165, 0)
PURPLE = (180, 0, 180)
BLUE = (0, 120, 255)
DARK_GREEN = (0, 100, 0)  # Fixed missing color for Koopa

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ultra Mario 2D Bros")
clock = pygame.time.Clock()
font = pygame.font.SysFont('courier', 24, bold=True)
small_font = pygame.font.SysFont('courier', 16, bold=True)

# Game variables
state = 'title'
current_world = 1
current_level = 1
score = 0
coins = 0
lives = 3
time_left = 400
timer_tick = 0
camera_x = 0
shake_timer = 0
shake_offset = 0
flash_timer = 0
flash_color = WHITE
level_end = 0
high_score = 0
flag_reached = False
flag_pole_x = 0
particles = []

# Groups
enemies = pygame.sprite.Group()
powerups = pygame.sprite.Group()
fireballs = pygame.sprite.Group()
blocks = pygame.sprite.Group()
coins_group = pygame.sprite.Group()

class Particle:
    def __init__(self, x, y, vx, vy, color, lifetime=30):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.lifetime = lifetime
        self.size = random.randint(2, 6)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2
        self.lifetime -= 1
        return self.lifetime > 0
    
    def draw(self, surf):
        pygame.draw.rect(surf, self.color, 
                        (self.x - camera_x - self.size//2, self.y - self.size//2, 
                         self.size, self.size))

class Mario(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.reset()

    def reset(self):
        self.rect = pygame.Rect(TILE_SIZE * 2, GROUND_Y - TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.vx = 0
        self.vy = 0
        self.facing = 1
        self.on_ground = False
        self.crouching = False
        self.state = 'small'  # small, big, fire
        self.jump_timer = 0
        self.invinc_time = 0
        self.fire_timer = 0
        self.climbing = False
        self.climb_score_added = False
        self.walk_frame = 0
        self.animation_timer = 0

    def update(self, keys):
        global state, lives, score, coins, camera_x, level_end, timer_tick, time_left, flag_reached

        if self.climbing:
            self.vy = 2
            self.rect.y += self.vy
            if self.rect.bottom >= GROUND_Y + TILE_SIZE:
                self.climbing = False
                self.vx = 2
                self.facing = 1
                if not self.climb_score_added:
                    flag_height = (GROUND_Y - self.rect.top) // TILE_SIZE
                    add_score = [100, 400, 800, 2000, 5000][min(flag_height // 2, 4)]
                    score += add_score
                    self.climb_score_added = True
            return

        if self.rect.top > HEIGHT + 100:
            self.die()
            return

        accel = 0.3
        max_vx = 4
        friction = 0.92

        if keys[pygame.K_RIGHT]:
            self.vx += accel
            self.facing = 1
        elif keys[pygame.K_LEFT]:
            self.vx -= accel
            self.facing = -1
        else:
            self.vx *= friction

        self.vx = max(-max_vx, min(max_vx, self.vx))

        if keys[pygame.K_DOWN] and self.state != 'small':
            self.crouching = True
        else:
            self.crouching = False

        height = TILE_SIZE if self.state == 'small' or self.crouching else TILE_SIZE * 2
        self.rect.height = height

        if (keys[pygame.K_SPACE] or keys[pygame.K_UP]) and not self.climbing:
            if self.on_ground and self.jump_timer == 0:
                self.vy = -5 # Jump power
                # Big mario jumps higher
                if self.state != 'small': self.vy = -7
                self.jump_timer = 12
                self.on_ground = False
            elif self.jump_timer > 0:
                self.vy -= 0.8
                self.jump_timer -= 1
        else:
            self.jump_timer = 0

        self.vy += GRAVITY
        self.vy = min(self.vy, MAX_FALL_SPEED)

        # Horizontal movement
        self.rect.x += self.vx
        self.hit_horizontal()

        # Vertical movement
        self.rect.y += self.vy
        self.on_ground = False
        self.hit_vertical()

        # Check for flag pole
        if not flag_reached and self.rect.colliderect(pygame.Rect(flag_pole_x - 5, 0, 10, HEIGHT)):
            flag_reached = True
            self.climbing = True
            self.vx = 0
            self.rect.x = flag_pole_x - 8
            self.vy = 0

        # Enemies collision
        for enemy in enemies:
            if self.rect.colliderect(enemy.rect):
                if self.vy > 0 and self.rect.bottom <= enemy.rect.top + 10:
                    self.stomp(enemy)
                else:
                    self.hurt()

        # Powerups collision
        for pu in powerups:
            if self.rect.colliderect(pu.rect):
                pu.collect(self)

        # Fireball shooting
        if keys[pygame.K_LCTRL] and self.state == 'fire' and self.fire_timer == 0:
            fireballs.add(Fireball(self.rect.centerx, self.rect.centery, self.facing * 6))
            self.fire_timer = 20
        if self.fire_timer > 0:
            self.fire_timer -= 1

        if self.invinc_time > 0:
            self.invinc_time -= 1

        # Camera
        camera_x = max(0, self.rect.centerx - WIDTH // 2)
        
        # Animation
        self.animation_timer += 1
        if abs(self.vx) > 0.5 and self.on_ground:
            if self.animation_timer % 10 == 0:
                self.walk_frame = (self.walk_frame + 1) % 3

    def hit_horizontal(self):
        for block in blocks:
            if self.rect.colliderect(block.rect):
                if self.vx > 0:
                    self.rect.right = block.rect.left
                elif self.vx < 0:
                    self.rect.left = block.rect.right
                self.vx = 0

    def hit_vertical(self):
        for block in blocks:
            if self.rect.colliderect(block.rect):
                if self.vy > 0:
                    self.rect.bottom = block.rect.top
                    self.vy = 0
                    self.on_ground = True
                elif self.vy < 0:
                    self.rect.top = block.rect.bottom
                    self.vy = 0
                    block.bump(self)

    def stomp(self, enemy):
        global score
        self.vy = -4
        enemy.stomped()
        score += 100
        color = GREEN if isinstance(enemy, Koopa) else RED
        for _ in range(8):
            particles.append(Particle(enemy.rect.centerx, enemy.rect.centery, 
                                     random.uniform(-2, 2), random.uniform(-4, 0),
                                     color))

    def hurt(self):
        global flash_timer, flash_color, shake_timer
        if self.invinc_time > 0:
            return
        if self.state == 'small':
            self.die()
        else:
            self.state = 'small' if self.state == 'big' else 'big'
            self.invinc_time = 120
            flash_timer = 5
            flash_color = RED
            shake_timer = 10

    def die(self):
        global lives, state
        lives -= 1
        if lives <= 0:
            state = 'game_over'
        else:
            load_level(current_world, current_level)
        flash_timer = 10
        flash_color = RED
        shake_timer = 20

    def power_up(self, type):
        global flash_timer, shake_timer
        if type == 'mushroom' and self.state == 'small':
            self.state = 'big'
            self.rect.y -= TILE_SIZE
            self.rect.height = TILE_SIZE * 2
        elif type == 'flower':
            self.state = 'fire'
        flash_timer = 5
        shake_timer = 5

    def draw(self, surf):
        if self.invinc_time % 4 < 2 and self.invinc_time > 0:
            return # Flicker
        
        color = RED if self.state in ['small', 'big'] else ORANGE
        draw_rect = self.rect.move(-camera_x + shake_offset, 0)
        
        if self.state == 'small':
            pygame.draw.rect(surf, color, draw_rect)
            pygame.draw.rect(surf, color, (draw_rect.x, draw_rect.y - 4, TILE_SIZE, 4)) # Hat
        else:
            body_height = TILE_SIZE * 2
            if self.crouching:
                body_height = int(TILE_SIZE * 1.5)
            
            body_rect = pygame.Rect(draw_rect.x, draw_rect.bottom - body_height, TILE_SIZE, body_height)
            pygame.draw.rect(surf, color, body_rect)
            pygame.draw.rect(surf, color, (body_rect.x, body_rect.y - 4, TILE_SIZE, 4)) # Hat
            
            if abs(self.vx) > 0.5 and self.on_ground and not self.crouching:
                leg_offset = 2 if self.walk_frame == 1 else 4 if self.walk_frame == 2 else 0
                pygame.draw.rect(surf, BLUE, (body_rect.x - 2 + leg_offset * self.facing, 
                                            body_rect.bottom - 4, 4, 4))

class Goomba(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.vx = -1
        self.vy = 0
        self.state = 'alive'
        self.stomp_timer = 0
        
    def update(self):
        if self.state == 'stomped':
            self.stomp_timer -= 1
            if self.stomp_timer <= 0:
                self.kill()
            return
            
        self.rect.x += self.vx
        
        # Check for collisions with blocks
        hits = pygame.sprite.spritecollide(self, blocks, False)
        for block in hits:
            if self.vx > 0:
                self.rect.right = block.rect.left
            elif self.vx < 0:
                self.rect.left = block.rect.right
            self.vx *= -1
        
        # Apply gravity
        self.vy += GRAVITY
        self.rect.y += self.vy
        
        # Check ground collisions
        hits = pygame.sprite.spritecollide(self, blocks, False)
        for block in hits:
            if self.vy > 0 and self.rect.bottom > block.rect.top:
                self.rect.bottom = block.rect.top
                self.vy = 0
        
        if self.rect.top > HEIGHT:
            self.kill()
            
    def stomped(self):
        if self.state == 'alive':
            self.state = 'stomped'
            self.stomp_timer = 20
            self.vx = 0
            self.rect.height = TILE_SIZE // 2
            
    def draw(self, surf):
        if self.state == 'stomped':
            pygame.draw.rect(surf, GRAY, self.rect.move(-camera_x + shake_offset, 0))
        elif self.state == 'alive':
            draw_rect = self.rect.move(-camera_x + shake_offset, 0)
            pygame.draw.rect(surf, RED, draw_rect)
            # Eyes
            pygame.draw.rect(surf, WHITE, (draw_rect.x+4, draw_rect.y+4, 8, 8))
            pygame.draw.rect(surf, WHITE, (draw_rect.x+20, draw_rect.y+4, 8, 8))

class Koopa(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.vx = -1
        self.vy = 0
        self.state = 'walking' # walking, shell, sliding
        self.shell_timer = 0
        
    def update(self):
        if self.state == 'shell':
            self.shell_timer -= 1
            if self.shell_timer <= 0:
                self.state = 'walking'
                self.vx = -1 if self.rect.x < mario.rect.x else 1
            return
            
        self.rect.x += self.vx
        
        hits = pygame.sprite.spritecollide(self, blocks, False)
        for block in hits:
            if self.vx > 0:
                self.rect.right = block.rect.left
            elif self.vx < 0:
                self.rect.left = block.rect.right
            self.vx *= -1
            
        self.vy += GRAVITY
        self.rect.y += self.vy
        
        hits = pygame.sprite.spritecollide(self, blocks, False)
        for block in hits:
            if self.vy > 0:
                self.rect.bottom = block.rect.top
                self.vy = 0
        
        if self.rect.top > HEIGHT:
            self.kill()
            
    def stomped(self):
        if self.state == 'walking':
            self.state = 'shell'
            self.shell_timer = 300
            self.vx = 0
            self.rect.height = TILE_SIZE // 2
            self.rect.y += TILE_SIZE // 2
        elif self.state == 'shell':
            self.state = 'sliding'
            self.vx = 10 if mario.facing > 0 else -10
        elif self.state == 'sliding':
            self.state = 'shell'
            self.vx = 0
            
    def draw(self, surf):
        color = GREEN if self.state == 'walking' else DARK_GREEN
        draw_rect = self.rect.move(-camera_x + shake_offset, 0)
        if self.state == 'shell' or self.state == 'sliding':
            pygame.draw.rect(surf, YELLOW, draw_rect) # Shell interior
            pygame.draw.rect(surf, color, draw_rect, 3)
        else:
            pygame.draw.rect(surf, color, draw_rect)
            pygame.draw.rect(surf, YELLOW, (draw_rect.x+4, draw_rect.y+8, 8, 8)) # Eye

class Mushroom(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.vx = 1.5
        self.vy = 0
        
    def update(self):
        self.rect.x += self.vx
        
        hits = pygame.sprite.spritecollide(self, blocks, False)
        if hits:
            self.vx *= -1
            
        self.vy += GRAVITY
        self.rect.y += self.vy
        
        hits = pygame.sprite.spritecollide(self, blocks, False)
        for block in hits:
            if self.vy > 0:
                self.rect.bottom = block.rect.top
                self.vy = 0
        
        if self.rect.top > HEIGHT:
            self.kill()
            
    def collect(self, mario):
        mario.power_up('mushroom')
        self.kill()
        
    def draw(self, surf):
        draw_rect = self.rect.move(-camera_x + shake_offset, 0)
        pygame.draw.rect(surf, ORANGE, draw_rect) # Cap
        pygame.draw.rect(surf, WHITE, (draw_rect.x + 4, draw_rect.y + 10, TILE_SIZE - 8, TILE_SIZE - 12)) # Stem

class Flower(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.bob_timer = 0
        
    def update(self):
        self.bob_timer += 1
        # Slight bobbing
        
    def collect(self, mario):
        mario.power_up('flower')
        self.kill()
        
    def draw(self, surf):
        draw_rect = self.rect.move(-camera_x + shake_offset, 0)
        pygame.draw.rect(surf, GREEN, (draw_rect.x + TILE_SIZE//2 - 2, draw_rect.y + 8, 4, TILE_SIZE - 8))
        pygame.draw.rect(surf, ORANGE, (draw_rect.x + 4, draw_rect.y + 4, TILE_SIZE - 8, TILE_SIZE - 8))
        pygame.draw.rect(surf, WHITE, (draw_rect.x+10, draw_rect.y+10, 4, 4))

class Fireball(pygame.sprite.Sprite):
    def __init__(self, x, y, vx):
        super().__init__()
        self.rect = pygame.Rect(x - 4, y - 4, 8, 8)
        self.vx = vx
        self.vy = -2
        self.bounce_count = 0
        
    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        self.vy += GRAVITY
        
        # Bounce on ground
        if self.rect.bottom >= GROUND_Y:
            self.rect.bottom = GROUND_Y
            self.vy = -4
            self.bounce_count += 1
            
        # Collisions with enemies
        hits = pygame.sprite.spritecollide(self, enemies, False)
        for enemy in hits:
            enemy.stomped()
            self.kill()
            global score
            score += 100
            break
            
        hits = pygame.sprite.spritecollide(self, blocks, False)
        if hits or self.bounce_count > 4 or self.rect.right < camera_x or self.rect.left > camera_x + WIDTH:
            self.kill()
            
    def draw(self, surf):
        draw_rect = self.rect.move(-camera_x + shake_offset, 0)
        pygame.draw.rect(surf, ORANGE, draw_rect)
        pygame.draw.rect(surf, RED, (draw_rect.x+2, draw_rect.y+2, 4, 4))

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.spin_timer = 0
        
    def update(self):
        self.spin_timer += 1
        if self.rect.top > HEIGHT:
            self.kill()
        
    def collect(self):
        global coins, score
        coins += 1
        score += 200
        self.kill()
        for _ in range(5):
            particles.append(Particle(self.rect.centerx, self.rect.centery,
                                     random.uniform(-2, 2), random.uniform(-3, -1),
                                     YELLOW))
        
    def draw(self, surf):
        draw_rect = self.rect.move(-camera_x + shake_offset, 0)
        width = TILE_SIZE//3
        if (self.spin_timer // 5) % 2 == 0:
            width = TILE_SIZE // 2
        else:
            width = 4
        pygame.draw.rect(surf, YELLOW, (draw_rect.centerx - width//2, draw_rect.y + 8, width, TILE_SIZE - 16))

class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, type, content=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.type = type
        self.content = content
        self.bump_timer = 0
        self.bump_dy = 0
        self.original_y = y
        
    def update(self):
        if self.bump_timer > 0:
            self.bump_timer -= 1
            if self.bump_dy != 0:
                self.rect.y += self.bump_dy
                self.bump_dy += 0.5
                if self.rect.y > self.original_y:
                    self.rect.y = self.original_y
                    self.bump_dy = 0
                
    def bump(self, mario):
        if self.bump_timer == 0:
            self.bump_timer = 10
            self.bump_dy = -4
            
            if self.type == 'question' and self.content:
                release_content(self)
                self.type = 'empty'
                self.content = None
            elif self.type == 'brick':
                if mario.state != 'small':
                    self.kill()
                    global score
                    score += 50
                    for _ in range(4):
                        particles.append(Particle(self.rect.centerx, self.rect.centery,
                                                 random.uniform(-3, 3), random.uniform(-5, -1),
                                                 BROWN))
                
    def draw(self, surf):
        draw_rect = self.rect.move(-camera_x + shake_offset, 0)
        
        if self.type == 'ground':
            pygame.draw.rect(surf, BROWN, draw_rect)
            pygame.draw.rect(surf, BLACK, draw_rect, 1)
        elif self.type == 'brick':
            pygame.draw.rect(surf, BROWN, draw_rect)
            pygame.draw.rect(surf, BLACK, draw_rect, 1)
            pygame.draw.line(surf, (150, 70, 0), (draw_rect.left, draw_rect.centery), (draw_rect.right, draw_rect.centery))
        elif self.type == 'question':
            pygame.draw.rect(surf, YELLOW, draw_rect)
            pygame.draw.rect(surf, BLACK, draw_rect, 1)
            q_text = small_font.render("?", True, BLACK)
            surf.blit(q_text, (draw_rect.x + 10, draw_rect.y + 6))
        elif self.type == 'pipe':
            pygame.draw.rect(surf, GREEN, draw_rect)
            pygame.draw.rect(surf, BLACK, draw_rect, 1)
        elif self.type == 'empty':
            pygame.draw.rect(surf, (150, 120, 50), draw_rect)
            pygame.draw.rect(surf, BLACK, draw_rect, 1)

mario = Mario()

def release_content(block):
    global coins, score
    if block.content == 'coin':
        coin = Coin(block.rect.x, block.rect.top - TILE_SIZE)
        coins_group.add(coin)
        coins += 1
        score += 200
    elif block.content == 'mushroom':
        powerups.add(Mushroom(block.rect.x, block.rect.top - TILE_SIZE))
    elif block.content == 'flower':
        powerups.add(Flower(block.rect.x, block.rect.top - TILE_SIZE))

def load_level(world, level):
    global camera_x, level_end, flag_pole_x, flag_reached
    global enemies, powerups, fireballs, blocks, coins_group, particles
    
    # Cleanup
    enemies.empty()
    powerups.empty()
    fireballs.empty()
    blocks.empty()
    coins_group.empty()
    particles.clear()
    
    camera_x = 0
    flag_reached = False
    mario.reset()
    
    # Difficulty scaling
    gap_width = 3 + world  # Wider pits in later worlds
    enemy_chance = 0.05 + (level * 0.01)
    level_length = 200 + (world * 20)
    
    # Start ground (safe zone)
    for x in range(-TILE_SIZE, 20 * TILE_SIZE, TILE_SIZE):
        blocks.add(Block(x, GROUND_Y, 'ground'))

    x = 20 * TILE_SIZE
    last_feature_x = x
    
    # Procedural Generation Loop
    while x < level_length * TILE_SIZE:
        # Decide what to place
        rng = random.random()
        
        if rng < 0.3 and x > last_feature_x + 150:
            # Create a pit
            pit_size = random.randint(2, gap_width)
            x += pit_size * TILE_SIZE
            last_feature_x = x
        elif rng < 0.6 and x > last_feature_x + 100:
            # Create pipes or structures
            height = random.randint(1, 3)
            # Pipe
            for h in range(height):
                blocks.add(Block(x, GROUND_Y - (h+1)*TILE_SIZE, 'pipe'))
                blocks.add(Block(x + TILE_SIZE, GROUND_Y - (h+1)*TILE_SIZE, 'pipe'))
            
            # Add question block above pipe sometimes
            if random.random() < 0.5:
                content = 'mushroom' if world > 1 else 'coin'
                blocks.add(Block(x, GROUND_Y - (height+2)*TILE_SIZE, 'question', content))
            
            x += 5 * TILE_SIZE
            last_feature_x = x
            
        elif rng < 0.8 and x > last_feature_x + 80:
            # Staircase
            stair_height = random.randint(3, 6)
            for i in range(stair_height):
                blocks.add(Block(x + i*TILE_SIZE, GROUND_Y - (i+1)*TILE_SIZE, 'brick'))
                blocks.add(Block(x + (i+1)*TILE_SIZE, GROUND_Y - (i+1)*TILE_SIZE, 'brick'))
            x += (stair_height + 2) * TILE_SIZE
            last_feature_x = x
        else:
            # Flat ground with potential enemies or blocks
            ground_chunk = random.randint(5, 10)
            for i in range(ground_chunk):
                blocks.add(Block(x + i*TILE_SIZE, GROUND_Y, 'ground'))
                
                # Floating blocks
                if i == ground_chunk // 2 and random.random() < 0.3:
                    b_type = 'question' if random.random() < 0.4 else 'brick'
                    cnt = 'coin' if b_type == 'question' else None
                    blocks.add(Block(x + i*TILE_SIZE, GROUND_Y - 4*TILE_SIZE, b_type, cnt))
                
                # Enemies
                if i > 1 and random.random() < enemy_chance:
                    enemy_type = Goomba if world < 3 or random.random() < 0.7 else Koopa
                    enemies.add(enemy_type(x + i*TILE_SIZE, GROUND_Y - TILE_SIZE))
            
            x += ground_chunk * TILE_SIZE

    # Floor leading to flag
    for i in range(10):
        blocks.add(Block(x + i*TILE_SIZE, GROUND_Y, 'ground'))
        # Blocks for jumping to flag
        if i % 2 == 0:
             blocks.add(Block(x + i*TILE_SIZE, GROUND_Y - (i//2 + 2)*TILE_SIZE, 'brick'))

    # Flag Pole
    flag_pole_x = x + 5 * TILE_SIZE
    # Castle base
    for i in range(15):
        blocks.add(Block(flag_pole_x + 20 + i*TILE_SIZE, GROUND_Y, 'ground'))
        if i < 8 and i > 0:
            blocks.add(Block(flag_pole_x + 20 + i*TILE_SIZE, GROUND_Y - TILE_SIZE, 'brick'))

    level_end = flag_pole_x + 300

def complete_level():
    global state, current_level, current_world, score, time_left, high_score
    score += time_left * 50
    score += coins * 50
    time_left = 400
    high_score = max(high_score, score)
    
    current_level += 1
    if current_level > 4:
        current_level = 1
        current_world += 1
        if current_world > 8:
            state = 'win'
            return
    
    state = 'level_complete'

def show_text(text, x, y, color=WHITE, size='large'):
    if size == 'large':
        text_surf = font.render(text, True, color)
    else:
        text_surf = small_font.render(text, True, color)
    text_rect = text_surf.get_rect(center=(x, y))
    screen.blit(text_surf, text_rect)

def draw_hud():
    score_text = font.render(f"SCORE: {score:06d}", True, WHITE)
    screen.blit(score_text, (20, 20))
    
    coin_text = font.render(f"COINS: {coins:02d}", True, WHITE)
    screen.blit(coin_text, (20, 50))
    
    world_text = font.render(f"WORLD: {current_world}-{current_level}", True, WHITE)
    screen.blit(world_text, (WIDTH - 200, 20))
    
    time_text = font.render(f"TIME: {time_left}", True, WHITE)
    screen.blit(time_text, (WIDTH - 200, 50))
    
    lives_text = font.render(f"LIVES: {lives}", True, WHITE)
    screen.blit(lives_text, (WIDTH // 2 - 50, 20))

def draw_background():
    screen.fill(SKY_BLUE)
    
    # Clouds (parallax)
    for i in range(5):
        cloud_x = (camera_x * 0.5 + i * 350) % (WIDTH + 400) - 200
        pygame.draw.ellipse(screen, WHITE, (cloud_x, 80 + (i%3)*60, 120, 50))
        pygame.draw.ellipse(screen, WHITE, (cloud_x + 40, 70 + (i%3)*60, 80, 50))
    
    # Hills (parallax)
    for i in range(4):
        hill_x = (camera_x * 0.2 + i * 500) % (WIDTH + 600) - 300
        pygame.draw.ellipse(screen, (0, 120, 0), (hill_x, GROUND_Y - 100, 500, 300))

    # Flag pole drawing
    if flag_pole_x > 0:
        pole_x = flag_pole_x - camera_x + shake_offset
        pygame.draw.rect(screen, GRAY, (pole_x - 2, 200, 4, GROUND_Y - 200))
        pygame.draw.rect(screen, RED, (pole_x, 200, 20, 15)) # Ball on top
        
        # Flag
        flag_h = 200
        if flag_reached:
             flag_h = mario.rect.y
        
        pygame.draw.rect(screen, GREEN, (pole_x + 2, flag_h + 15, 18, 12))

# Main Loop
load_level(current_world, current_level)
blink_timer = 0

while True:
    keys = pygame.key.get_pressed()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        if event.type == pygame.KEYDOWN:
            if state == 'title':
                if event.key == pygame.K_RETURN:
                    state = 'playing'
                    # Reset full game
                    current_world = 1
                    current_level = 1
                    score = 0
                    coins = 0
                    lives = 3
                    load_level(current_world, current_level)
            elif state == 'game_over':
                if event.key == pygame.K_RETURN:
                    state = 'title'
            elif state == 'win':
                if event.key == pygame.K_RETURN:
                    state = 'title'
            elif state == 'level_complete':
                if event.key == pygame.K_RETURN:
                    load_level(current_world, current_level)
                    state = 'playing'
    
    if state == 'playing':
        # Timer
        timer_tick += 1
        if timer_tick >= FPS:
            timer_tick = 0
            time_left = max(0, time_left - 1)
            if time_left == 0:
                mario.die()
        
        # Updates
        mario.update(keys)
        enemies.update()
        powerups.update()
        fireballs.update()
        blocks.update()
        coins_group.update()
        
        # Update particles manually
        particles = [p for p in particles if p.update()]
        
        # Coin collection
        for coin in coins_group:
            if mario.rect.colliderect(coin.rect):
                coin.collect()
        
        # Shake
        if shake_timer > 0:
            shake_timer -= 1
            shake_offset = random.randint(-3, 3)
        else:
            shake_offset = 0
            
        # Flash
        if flash_timer > 0:
            flash_timer -= 1
            
    # Drawing
    draw_background()
    
    for block in blocks:
        block.draw(screen)
    
    for enemy in enemies:
        enemy.draw(screen)
    
    for pu in powerups:
        pu.draw(screen)
    
    for fb in fireballs:
        fb.draw(screen)
        
    for coin in coins_group:
        coin.draw(screen)
        
    for particle in particles:
        particle.draw(screen)
        
    mario.draw(screen)
    
    draw_hud()
    
    # Flash overlay
    if flash_timer > 0:
        flash_surf = pygame.Surface((WIDTH, HEIGHT))
        flash_surf.set_alpha(100)
        flash_surf.fill(flash_color)
        screen.blit(flash_surf, (0, 0))
    
    # Overlays
    if state == 'title':
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        show_text("ULTRA MARIO 2D BROS", WIDTH//2, HEIGHT//2 - 60, RED)
        show_text("PRESS ENTER TO START", WIDTH//2, HEIGHT//2 + 20)
        show_text(f"HIGH SCORE: {high_score:06d}", WIDTH//2, HEIGHT//2 + 80)
        
        blink_timer += 1
        if blink_timer % 60 < 30:
            show_text(">", WIDTH//2 - 100, HEIGHT//2 + 20)
            
    elif state == 'level_complete':
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        show_text(f"WORLD {current_world}-{current_level} CLEAR!", WIDTH//2, HEIGHT//2 - 40, GREEN)
        show_text(f"SCORE: {score}", WIDTH//2, HEIGHT//2)
        show_text("PRESS ENTER", WIDTH//2, HEIGHT//2 + 60)
        
    elif state == 'game_over':
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        show_text("GAME OVER", WIDTH//2, HEIGHT//2 - 20, RED)
        show_text("PRESS ENTER", WIDTH//2, HEIGHT//2 + 40)
        
    elif state == 'win':
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        show_text("CONGRATULATIONS!", WIDTH//2, HEIGHT//2 - 60, YELLOW)
        show_text("YOU CLEARED WORLD 8-4!", WIDTH//2, HEIGHT//2, WHITE)
        show_text(f"FINAL SCORE: {score}", WIDTH//2, HEIGHT//2 + 40, GREEN)
        show_text("PRESS ENTER", WIDTH//2, HEIGHT//2 + 100)
    
    pygame.display.flip()
    clock.tick(FPS)
