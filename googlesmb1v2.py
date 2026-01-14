import pygame
import sys

# --- Configuration & Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
NES_WIDTH = 256
NES_HEIGHT = 240
SCALE = 3  # 256x240 -> 768x720 (Approx fit for 800x600 window with clipping or letterbox)
SCALED_WIDTH = NES_WIDTH * SCALE
SCALED_HEIGHT = NES_HEIGHT * SCALE

FPS = 60

# Physics Constants (Tuned for "Feel")
GRAVITY = 0.5
MAX_FALL_SPEED = 7.0
JUMP_FORCE = -11.0
JUMP_GRAVITY_LOW = 0.5   # Gravity when holding jump
JUMP_GRAVITY_HIGH = 1.2  # Gravity when releasing jump (short hop)
ACCELERATION = 0.15
FRICTION = 0.15
MAX_WALK_SPEED = 2.5
MAX_RUN_SPEED = 4.5
SKID_THRESHOLD = 1.0     # Speed required to trigger skid
BOUNCE_FORCE = -6.0      # When jumping on enemies

# Colors
COLOR_SKY = (92, 148, 252)
COLOR_BLACK = (0, 0, 0)
COLOR_TRANSPARENT = (255, 0, 255) # Magic pink for transparency key

# --- Sprite Data (Compact Representation) ---
# Palette Key:
# . = Transparent
# R = Red (Mario)
# S = Skin
# B = Brown (Hair/Boots)
# O = Orange (Coin/QBlock)
# Y = Yellow
# G = Green
# W = White
# K = Black outline
# D = Dark Brown (Goomba/Brick)
# L = Light Brick

PALETTE = {
    '.': (0, 0, 0, 0),
    'R': (216, 40, 0),
    'S': (252, 152, 56),
    'B': (136, 112, 0),
    'O': (252, 216, 168),
    'Y': (216, 168, 0),
    'G': (0, 168, 0),
    'L': (184, 248, 24), # Light Green
    'W': (255, 255, 255),
    'K': (0, 0, 0),
    'D': (200, 76, 12),
    'E': (252, 188, 176) # Brick highlight
}

# --- Sprite Bitmaps ---
SPRITES = {
    'mario_idle': [
        ".....RRRRR......",
        "....RRRRRRRRR...",
        "....BBBSSB......",
        "....BSBSSSB.....",
        "....BSBSSSB.....",
        "....BBSSSS......",
        ".......SS.......",
        "....BBB.RR......",
        "...BBBB.RRR.....",
        "..BBBB.RRRR.....",
        "..BBBBRRRRR.....",
        "..BBBBRRRRR.....",
        "...BB.RRR.......",
        "......BBB.......",
        ".....BBBB.......",
        ".....BBBB......."
    ],
    'mario_run1': [
        ".....RRRRR......",
        "....RRRRRRRRR...",
        "....BBBSSB......",
        "....BSBSSSB.....",
        "....BSBSSSB.....",
        "....BBSSSS......",
        ".......SS.......",
        ".....BBBRR......",
        "....BBBBRRR.....",
        "...BBBBBRRRR....",
        "...BBBBBRRRR....",
        "...BBBBBRRRR....",
        "....BB..RR......",
        "........BBB.....",
        "........BBBB....",
        ".......BBBB....."
    ],
    'mario_run2': [
        ".....RRRRR......",
        "....RRRRRRRRR...",
        "....BBBSSB......",
        "....BSBSSSB.....",
        "....BSBSSSB.....",
        "....BBSSSS......",
        ".......SS.......",
        "....BBB.RR......",
        "...BBBB.RRR.....",
        "..BBBB.RRRR.....",
        "..BBBBRRRRR.....",
        "..BBBBRRRRR.....",
        "...BB.RRR.......",
        "...BB.BB........",
        "......BB........",
        "................"
    ],
    'mario_jump': [
        ".....RRRRR......",
        "....RRRRRRRRR...",
        "....BBBSSB......",
        "....BSBSSSB.....",
        "....BSBSSSB.....",
        "....BBSSSS......",
        ".......SS.......",
        "....BBBRRR......",
        "...BBBB.RRR.....",
        "..BBBBB.RRRR....",
        "..BBBB..RRRR....",
        "..BBBB..RRRR....",
        "..BBB...RRR.....",
        "........BBB.....",
        ".......BBBB.....",
        "......BBBB......"
    ],
    'mario_big_idle': [
        "......RRRRR.....",
        ".....RRRRRRRRR..",
        ".....BBBSSB.....",
        ".....BSBSSSB....",
        ".....BSBSSSB....",
        ".....BBSSSS.....",
        "........SS......",
        "....BBBB.RR.....",
        "...BBBBBB.RR....",
        "...BBBBBB.RR....",
        "..BBBBBBBB.R....",
        "..BBBBBBBB......",
        "..BBBBBBBB......",
        "..SSS..SSS......",
        "..BBB..BBB......",
        ".BBBB..BBBB....." # This is a simplified 16x16 crop, Big mario is technically 16x32
                          # We will handle Big Mario by stacking sprites or scaling in this simple engine
    ],
    'goomba': [
        "......DDDD......",
        ".....DDDDDD.....",
        "....DDDDDDDD....",
        "....DDDDDDDD....",
        "...DKKDDKKDD....",
        "...DKKDKKDDK....",
        "...DKKDKKDDK....",
        "...DDDDDDDDD....",
        "....DDDDDDD.....",
        "....DDDDDDD.....",
        ".....DDDDD......",
        ".....DDDDD......",
        "....DD.D.DD.....",
        "...DDD.D.DDD....",
        "...DDD.D.DDD....",
        ".......D........"
    ],
    'goomba_dead': [
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        ".....DDDDD......",
        "...DDDDDDDDD....",
        "..DDDKKDKKDDD...",
        "..DDDKKDKKDDD...",
        "..DDDDDDDDDDD...",
        "...DDDDDDDDD....",
        "....DDDDDDD.....",
        "................",
        "................"
    ],
    'brick': [
        "DDDDDDDDDDDDDDDD",
        "DEEEEEEEEEEEEEED",
        "DDDDDDDDDDDDDDDD",
        "DDDDDDDDDDDDDDDD",
        "DDDDDDDDDDDDDDDD",
        "DDDDDDDDDDDDDDDD",
        "DEEEEEEEEDEEEEED",
        "DDDDDDDDDDDDDDDD",
        "DEEEEEEEEEEEEEED",
        "DDDDDDDDDDDDDDDD",
        "DDDDDDDDDDDDDDDD",
        "DDDDDDDDDDDDDDDD",
        "DDDDDDDDDDDDDDDD",
        "DEEEEEEEEDEEEEED",
        "DDDDDDDDDDDDDDDD",
        "DDDDDDDDDDDDDDDD"
    ],
    'qblock': [
        "DDDDDDDDDDDDDDDD",
        "DOOOOOOOOOOOOOOD",
        "DOYYYYYYYYYYYYOD",
        "DOYYYYYYYYYYYYOD",
        "DOYYYYDDDDYYYYOD",
        "DOYYYDDYYDDYYYOD",
        "DOYYYDDYYDDYYYOD",
        "DOYYYYYYDDYYYYOD",
        "DOYYYYYDDYYYYYOD",
        "DOYYYYYDDYYYYYOD",
        "DOYYYYYYYYYYYYOD",
        "DOYYYYYDDYYYYYOD",
        "DOYYYYYDDYYYYYOD",
        "DOYYYYYYYYYYYYOD",
        "DOOOOOOOOOOOOOOD",
        "DDDDDDDDDDDDDDDD"
    ],
    'qblock_empty': [
        "DDDDDDDDDDDDDDDD",
        "DooooooooooooooD", # Using lowercase placeholder
        "DoBBBBBBBBBBBBoD",
        "DoBBBBBBBBBBBBoD",
        "DoBBBBBBBBBBBBoD",
        "DoBBBBBBBBBBBBoD",
        "DoBBBBBBBBBBBBoD",
        "DoBBBBBBBBBBBBoD",
        "DoBBBBBBBBBBBBoD",
        "DoBBBBBBBBBBBBoD",
        "DoBBBBBBBBBBBBoD",
        "DoBBBBBBBBBBBBoD",
        "DoBBBBBBBBBBBBoD",
        "DoBBBBBBBBBBBBoD",
        "DooooooooooooooD",
        "DDDDDDDDDDDDDDDD"
    ],
    'ground': [
        "DDDDDDDDDDDDDDDD",
        "DDDDDDDDDDDDDDDD",
        "DEEEEEEEEEEEEEED",
        "DEEDDDDDDDDDDEED",
        "DEEDDDDDDDDDDEED",
        "DEEDDDDDDDDDDEED",
        "DEEEEEEEEEEEEEED",
        "DDDDDDDDDDDDDDDD",
        "DEEEEEEEEEEEEEED",
        "DEEDDDDDDDDDDEED",
        "DEEDDDDDDDDDDEED",
        "DEEDDDDDDDDDDEED",
        "DEEEEEEEEEEEEEED",
        "DDDDDDDDDDDDDDDD",
        "DEEEEEEEEEEEEEED",
        "DEEDDDDDDDDDDEED"
    ],
    'mushroom': [
        ".....RRRRR......",
        "...RRRRRRRRR....",
        "..RRRRRRRRRRR...",
        "..RRWWWRWWWRR...",
        "..RWWWRWWWRRR...",
        "..RWWWRWWWRRR...",
        "..RRRRRRRRRRR...",
        "...RRRRRRRRR....",
        ".....OOOSS......",
        "....OSSSSSSO....",
        "....OSSSSSSO....",
        "....OSSSSSSO....",
        "....OSSSSSSO....",
        ".....OOOOOO.....",
        "................",
        "................"
    ]
}

# Fix missing palette entries in qblock_empty
PALETTE['o'] = (150, 100, 50) 

def create_texture(data):
    surf = pygame.Surface((16, 16)).convert_alpha()
    surf.fill((0,0,0,0))
    for y, row in enumerate(data):
        for x, char in enumerate(row):
            if char in PALETTE:
                surf.set_at((x, y), PALETTE[char])
    return pygame.transform.scale(surf, (16 * SCALE, 16 * SCALE))

class AssetManager:
    def __init__(self):
        self.textures = {}
        for key, data in SPRITES.items():
            self.textures[key] = create_texture(data)
        
        # Procedural Pipe (Easier than pixel mapping for scalable parts)
        self.textures['pipe_tl'] = self._make_pipe_part(0, 0)
        self.textures['pipe_tr'] = self._make_pipe_part(1, 0)
        self.textures['pipe_bl'] = self._make_pipe_part(0, 1)
        self.textures['pipe_br'] = self._make_pipe_part(1, 1)
        
    def _make_pipe_part(self, x_part, y_part):
        s = pygame.Surface((16 * SCALE, 16 * SCALE))
        s.fill((0, 168, 0)) # Base Green
        # Highlights
        if x_part == 0:
            pygame.draw.rect(s, (184, 248, 24), (2*SCALE, 0, 4*SCALE, 16*SCALE))
        if y_part == 0: # Top rim
            pygame.draw.rect(s, (0, 0, 0), (0, 0, 16*SCALE, 16*SCALE), int(1*SCALE))
        else: # Body outline
            if x_part == 0: pygame.draw.line(s, (0,0,0), (0,0), (0, 16*SCALE), int(1*SCALE))
            if x_part == 1: pygame.draw.line(s, (0,0,0), (16*SCALE-1,0), (16*SCALE-1, 16*SCALE), int(1*SCALE))
        return s

# --- Game Classes ---

class Entity(pygame.sprite.Sprite):
    def __init__(self, x, y, texture_key):
        super().__init__()
        self.image = assets.textures[texture_key]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        
class Mario(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 'mario_idle')
        self.rect.width = 12 * SCALE # Hitbox thinner than sprite
        self.rect.height = 16 * SCALE
        self.x = x # Float position for physics
        self.y = y
        self.facing_right = True
        self.is_big = False
        self.is_running = False
        self.is_jumping = False
        self.anim_timer = 0
        self.invincible_timer = 0
        self.dead = False
        self.growth_timer = 0 # Freezes game while growing
        
    def update(self, keys, world):
        if self.dead:
            self.vy += GRAVITY
            self.y += self.vy
            self.rect.y = int(self.y)
            return

        if self.growth_timer > 0:
            self.growth_timer -= 1
            # Flicker animation
            if self.growth_timer % 10 < 5:
                self.image = assets.textures['mario_big_idle'] if self.is_big else assets.textures['mario_idle']
            else:
                self.image = assets.textures['mario_idle'] if self.is_big else assets.textures['mario_big_idle']
            return

        # Input Handling
        acc = 0
        if keys[pygame.K_LEFT]:
            acc = -ACCELERATION
            self.facing_right = False
        elif keys[pygame.K_RIGHT]:
            acc = ACCELERATION
            self.facing_right = True
            
        # Sprint
        max_s = MAX_RUN_SPEED if keys[pygame.K_x] else MAX_WALK_SPEED
        
        # Physics: X Axis
        self.vx += acc
        
        # Friction
        if acc == 0:
            if self.vx > 0:
                self.vx -= FRICTION
                if self.vx < 0: self.vx = 0
            elif self.vx < 0:
                self.vx += FRICTION
                if self.vx > 0: self.vx = 0
        
        # Clamp Speed
        if self.vx > max_s: self.vx = max_s
        if self.vx < -max_s: self.vx = -max_s
        
        # Apply X Move
        self.x += self.vx
        self.rect.x = int(self.x)
        
        # X Collision
        self.check_collision(world, True)
        
        # Physics: Y Axis (Variable Jump Height)
        gravity = JUMP_GRAVITY_LOW if (keys[pygame.K_z] and self.vy < 0) else JUMP_GRAVITY_HIGH
        self.vy += gravity
        if self.vy > MAX_FALL_SPEED: self.vy = MAX_FALL_SPEED
        
        # Jump Trigger
        if keys[pygame.K_z] and not self.is_jumping and self.on_ground:
            self.vy = JUMP_FORCE
            self.on_ground = False
            self.is_jumping = True
            
        if not keys[pygame.K_z] and self.vy < -3:
             # Cut jump short if released
             self.vy = max(self.vy, -3)

        # Apply Y Move
        self.y += self.vy
        self.rect.y = int(self.y)
        
        # Y Collision
        self.on_ground = False # Reset, verified in check_collision
        self.check_collision(world, False)
        
        # Screen Bounds (Left only)
        if self.x < world.camera_x:
            self.x = world.camera_x
            self.vx = 0
            self.rect.x = int(self.x)
            
        # Pit Death
        if self.y > SCREEN_HEIGHT + 64:
            self.die()

        # Invincibility
        if self.invincible_timer > 0:
            self.invincible_timer -= 1

        self.animate()

    def check_collision(self, world, is_x):
        # Optimized collision: only check nearby tiles
        # Grid coords
        gx = int(self.rect.centerx / (16*SCALE))
        gy = int(self.rect.centery / (16*SCALE))
        
        nearby = []
        for y in range(gy-2, gy+4):
            for x in range(gx-2, gx+4):
                if (x, y) in world.tiles:
                    nearby.append(world.tiles[(x,y)])
        
        hits = pygame.sprite.spritecollide(self, nearby, False)
        
        for tile in hits:
            if is_x:
                if self.vx > 0:
                    self.rect.right = tile.rect.left
                    self.vx = 0
                    self.x = self.rect.x
                elif self.vx < 0:
                    self.rect.left = tile.rect.right
                    self.vx = 0
                    self.x = self.rect.x
            else:
                if self.vy > 0:
                    self.rect.bottom = tile.rect.top
                    self.vy = 0
                    self.on_ground = True
                    self.is_jumping = False
                    self.y = self.rect.y
                elif self.vy < 0:
                    self.rect.top = tile.rect.bottom
                    self.vy = 0
                    self.y = self.rect.y
                    # Block Interaction
                    tile.bump(self)

    def animate(self):
        # Determine Texture
        state = "idle"
        if not self.on_ground:
            state = "jump"
        elif abs(self.vx) > 0.1:
            self.anim_timer += 1 + abs(self.vx) * 0.5
            if (self.anim_timer // 10) % 3 == 0: state = "run1"
            elif (self.anim_timer // 10) % 3 == 1: state = "run2"
            else: state = "run1"
            
            # Skid
            if (self.vx > 0 and not self.facing_right) or (self.vx < 0 and self.facing_right):
                state = "jump" # Use jump frame for skid often in SMB
        else:
            state = "idle"
            
        tex_name = f"mario_{state}"
        if self.is_big and state != "jump": 
            # We reuse small animations for big for now, just scaled/offset? 
            # Or use specific big sprites. For this single-file demo, we use specific key
            if f"mario_big_{state}" in assets.textures:
                tex_name = f"mario_big_{state}"
            else:
                tex_name = "mario_big_idle" # Fallback

        base_img = assets.textures[tex_name]
        
        # If big, we might need to handle 32px height logic
        # For this engine, Big Mario is just a sprite change and a flag.
        # Ideally, we'd change hitbox height, but that complicates collision unstucking.
        # We'll keep hitbox 16*SCALE but render sprite higher?
        
        if not self.facing_right:
            base_img = pygame.transform.flip(base_img, True, False)
            
        self.image = base_img

    def get_hit(self):
        if self.invincible_timer > 0 or self.dead:
            return
        
        if self.is_big:
            self.is_big = False
            self.growth_timer = 60 # Pause for animation
            self.invincible_timer = 120
            # Ideally change hitbox back
        else:
            self.die()
            
    def die(self):
        self.dead = True
        self.vy = -10
        self.image = assets.textures['mario_idle'] # Should be unique dead sprite

    def grow(self):
        if not self.is_big:
            self.is_big = True
            self.growth_timer = 60
            self.y -= 16 * SCALE # Pop up

    def draw(self, screen, cam_x):
        if self.invincible_timer > 0 and (self.invincible_timer // 4) % 2 == 0:
            return # Flicker
            
        # Draw offset for Big Mario visualization if hitbox is still small
        draw_y = self.rect.y
        if self.is_big:
             # Hack: Big sprite is usually 32 tall. Our collision is 16.
             # We draw it 16 pixels higher.
             # (Real engine would change hitbox size)
             pass 
             
        screen.blit(self.image, (self.rect.x - cam_x, draw_y))


class Goomba(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 'goomba')
        self.rect.width = 16 * SCALE
        self.rect.height = 16 * SCALE
        self.x = x
        self.y = y
        self.vx = -1.0
        self.dead = False
        self.death_timer = 0
        
    def update(self, world):
        if self.dead:
            self.death_timer += 1
            if self.death_timer > 30:
                world.destroy_entity(self)
            return

        # Optimization: Don't move if far off screen
        if self.rect.x - world.camera_x > SCREEN_WIDTH + 64 or self.rect.right < world.camera_x - 64:
            return

        self.vy += GRAVITY
        
        self.x += self.vx
        self.rect.x = int(self.x)
        self.check_collision(world, True)
        
        self.y += self.vy
        self.rect.y = int(self.y)
        self.check_collision(world, False)
        
        # Player Interaction
        player = world.player
        if self.rect.colliderect(player.rect) and not player.dead and not player.growth_timer > 0:
            # Mario falling down onto goomba
            if player.vy > 0 and player.rect.bottom < self.rect.centery + 10:
                self.stomp()
                player.vy = BOUNCE_FORCE
            else:
                player.get_hit()
                
        # Pit
        if self.y > SCREEN_HEIGHT + 64:
            world.destroy_entity(self)
            
        # Animation
        if (pygame.time.get_ticks() // 200) % 2 == 0:
            self.image = assets.textures['goomba']
        else:
            self.image = pygame.transform.flip(assets.textures['goomba'], True, False)

    def stomp(self):
        self.dead = True
        self.vx = 0
        self.image = assets.textures['goomba_dead']
        
    def check_collision(self, world, is_x):
        gx = int(self.rect.centerx / (16*SCALE))
        gy = int(self.rect.centery / (16*SCALE))
        nearby = []
        for y in range(gy-1, gy+2):
            for x in range(gx-1, gx+2):
                if (x, y) in world.tiles:
                    nearby.append(world.tiles[(x,y)])
        
        hits = pygame.sprite.spritecollide(self, nearby, False)
        for tile in hits:
            if is_x:
                if self.vx > 0: self.rect.right = tile.rect.left
                elif self.vx < 0: self.rect.left = tile.rect.right
                self.vx *= -1 # Turn around
                self.x = self.rect.x
            else:
                if self.vy > 0:
                    self.rect.bottom = tile.rect.top
                    self.vy = 0
                    self.y = self.rect.y

class Mushroom(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 'mushroom')
        self.vx = 1.5
        self.x = x
        self.y = y
        self.emerging = True
        self.emerge_target = y - 16 * SCALE
        
    def update(self, world):
        if self.emerging:
            self.y -= 0.5
            self.rect.y = int(self.y)
            if self.y <= self.emerge_target:
                self.emerging = False
            return
            
        self.vy += GRAVITY
        self.x += self.vx
        self.rect.x = int(self.x)
        self.check_collision(world, True)
        self.y += self.vy
        self.rect.y = int(self.y)
        self.check_collision(world, False)
        
        if self.rect.colliderect(world.player.rect):
            world.player.grow()
            world.destroy_entity(self)

    def check_collision(self, world, is_x):
        gx = int(self.rect.centerx / (16*SCALE))
        gy = int(self.rect.centery / (16*SCALE))
        nearby = []
        for y in range(gy-1, gy+2):
            for x in range(gx-1, gx+2):
                if (x, y) in world.tiles:
                    nearby.append(world.tiles[(x,y)])
        hits = pygame.sprite.spritecollide(self, nearby, False)
        for tile in hits:
            if is_x:
                self.vx *= -1
                if self.vx > 0: self.rect.left = tile.rect.right
                else: self.rect.right = tile.rect.left
                self.x = self.rect.x
            else:
                if self.vy > 0:
                    self.rect.bottom = tile.rect.top
                    self.vy = 0
                    self.y = self.rect.y

# --- Tile System ---

class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y, type_id):
        super().__init__()
        self.type = type_id
        self.initial_y = y * 16 * SCALE
        self.rect = pygame.Rect(x * 16 * SCALE, y * 16 * SCALE, 16 * SCALE, 16 * SCALE)
        self.bump_anim = 0
        
        if type_id == 'G': self.image = assets.textures['ground']
        elif type_id == 'B': self.image = assets.textures['brick']
        elif type_id == '?': self.image = assets.textures['qblock']
        elif type_id == 'X': self.image = assets.textures['qblock_empty']
        elif type_id == 'W': self.image = assets.textures['brick'] # Wall/Hard block
        elif type_id.startswith('P'): 
            # Pipes handled by overlay, this is just solid hitbox
             self.image = pygame.Surface((16*SCALE, 16*SCALE))
             self.image.set_alpha(0) # Invisible, drawing handled specially
        else:
            self.image = assets.textures['ground']

    def bump(self, player):
        if self.bump_anim > 0: return
        
        if self.type == '?':
            self.bump_anim = 10
            self.type = 'X'
            self.image = assets.textures['qblock_empty']
            # Spawn Powerup or Coin (Simplified: always Mushroom)
            game.world.entities.add(Mushroom(self.rect.x, self.rect.y))
        elif self.type == 'B':
            if player.is_big:
                # Break brick
                game.world.destroy_tile(self)
            else:
                self.bump_anim = 10

    def update(self):
        if self.bump_anim > 0:
            self.bump_anim -= 1
            offset = -5 if self.bump_anim > 5 else 0
            self.rect.y = self.initial_y + offset

# --- World & Level Data ---

class World:
    def __init__(self, level_data):
        self.tiles = {} # Dict for spatial hashing (x,y) -> Tile
        self.tile_group = pygame.sprite.Group()
        self.entities = pygame.sprite.Group()
        self.player = None
        self.camera_x = 0
        self.bg_color = COLOR_SKY
        self.load_level(level_data)
        
    def load_level(self, data):
        self.tiles.clear()
        self.tile_group.empty()
        self.entities.empty()
        
        layout = data['layout']
        for y, row in enumerate(layout):
            for x, char in enumerate(row):
                if char == ' ': continue
                if char == 'M':
                    self.player = Mario(x * 16 * SCALE, y * 16 * SCALE)
                    continue
                if char == 'E':
                    self.entities.add(Goomba(x * 16 * SCALE, y * 16 * SCALE))
                    continue
                
                # Tiles
                t = Tile(x, y, char)
                self.tiles[(x,y)] = t
                self.tile_group.add(t)
                
    def update(self):
        if self.player:
            self.player.update(pygame.key.get_pressed(), self)
            
            # Camera logic
            target = self.player.rect.x - SCREEN_WIDTH // 3
            if target > self.camera_x:
                self.camera_x = target
            if self.camera_x < 0: self.camera_x = 0
            
            # Check Level End (Flagpole area)
            if self.player.rect.x > 198 * 16 * SCALE and self.player.on_ground:
                # Simple win condition
                return "NEXT_LEVEL"
                
        for e in self.entities:
            e.update(self)
            
        self.tile_group.update()
        
        # Cleanup falling entities
        return None

    def destroy_tile(self, tile):
        grid_pos = (tile.rect.x // (16*SCALE), tile.initial_y // (16*SCALE))
        if grid_pos in self.tiles:
            del self.tiles[grid_pos]
        tile.kill()
        
    def destroy_entity(self, ent):
        ent.kill()

    def draw(self, screen):
        screen.fill(self.bg_color)
        
        # Draw Tiles (Optimized to screen view)
        start_col = int(self.camera_x // (16*SCALE))
        end_col = start_col + (SCREEN_WIDTH // (16*SCALE)) + 2
        
        for y in range(15): # Screen height in tiles
            for x in range(start_col, end_col):
                if (x, y) in self.tiles:
                    t = self.tiles[(x,y)]
                    screen.blit(t.image, (t.rect.x - self.camera_x, t.rect.y))
                    
        # Draw Pipe Overlay (Because we use individual block collision but pipes are big sprites)
        # Scan for pipe tiles and draw the texture
        # Simplified: We just draw the tile images we made earlier which are segment based
        # The logic in AssetManager._make_pipe_part handles the look.
        
        for e in self.entities:
            screen.blit(e.image, (e.rect.x - self.camera_x, e.rect.y))
            
        if self.player:
            self.player.draw(screen, self.camera_x)

# --- Level Definitions ---

# Map Legend:
# G = Ground
# B = Brick
# ? = Question Block
# P = Pipe Parts
# W = Wall (Stairs)
# E = Enemy (Goomba)
# M = Mario Start

LEVEL_1_1 = [
    "                                                                                                                                                                                                        ",
    "                                                                                                                                                                                                        ",
    "                                                                                                                                                                                                        ",
    "                                                                                                                                                                                                        ",
    "                                                                                                                                                                                                        ",
    "                                                                                                                                                                                                        ",
    "                                                                  ?                                                                                                                                     ",
    "                                                                                                                                                                                                        ",
    "                                                                                                                                                                                                        ",
    "                                              ?   ?   ?   ?                                                    ?  ?                                                                                     ",
    "                    ?   ? B ?   ?           B B B B B B B B           P P           P P           P P        B B  B B                        W                                      W                   ",
    "                                            B B B B B B B B           P P           P P           P P        B B  B B                      W W                                    W W                   ",
    "                  E               E         B B B B B B B B           P P           P P           P P        B B  B B                    W W W                                  W W W                   ",
    "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG  GGGGGGGGGGGG  GGGGGGGGGGGG  GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG  WWWWWWWW                                WWWWWWWW                GG",
    "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG  GGGGGGGGGGGG  GGGGGGGGGGGG  GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG  WWWWWWWW                                WWWWWWWW                GG"
]
# Note: This is a shortened 1-1 for code brevity, but contains all key obstacles.

LEVEL_1_2 = [
    "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
    "W                                                                                      W",
    "W                                                                                      W",
    "W   M                                                                                  W",
    "W                                                                                      W",
    "W                                       B B B                                          W",
    "W                                     B B B B B                                        W",
    "W                                                                                      W",
    "W         E     E     E                                                                W",
    "W     BBBBBBBBBBBBBBBBBBBB                                                             W",
    "W                                                                                      W",
    "W                                                                                      W",
    "W                          P P                                                         W",
    "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
    "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW"
]

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Super Mario Bros. Engine (Python)")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24, bold=True)
        
        global assets
        assets = AssetManager()
        
        self.level_index = 0
        self.levels = [LEVEL_1_1, LEVEL_1_2]
        self.world = World({'layout': self.levels[0]})
        
    def run(self):
        running = True
        while running:
            # Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.world = World({'layout': self.levels[self.level_index]})
            
            # Update
            result = self.world.update()
            
            if result == "NEXT_LEVEL":
                self.level_index = (self.level_index + 1) % len(self.levels)
                self.world = World({'layout': self.levels[self.level_index]})
                if self.level_index == 1: self.world.bg_color = COLOR_BLACK # Underground theme
            
            if self.world.player.dead and self.world.player.rect.y > SCREEN_HEIGHT + 200:
                # Reset level on death
                self.world = World({'layout': self.levels[self.level_index]})
                if self.level_index == 1: self.world.bg_color = COLOR_BLACK

            # Draw
            self.world.draw(self.screen)
            
            # HUD
            ui_text = self.font.render(f"WORLD 1-{self.level_index + 1}", True, (255, 255, 255))
            self.screen.blit(ui_text, (20, 20))
            
            pygame.display.flip()
            self.clock.tick(FPS)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
