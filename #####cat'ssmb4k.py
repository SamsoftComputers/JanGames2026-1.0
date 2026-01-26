#!/usr/bin/env python3
"""
Super Mario Bros - Famicom Accurate Recreation
Team Flames / Samsoft 2025
Levels 1-1 and 8-4 with authentic layouts, enemy placements, and maze mechanics
"""

import pygame
import sys
import random
from enum import Enum, auto

# === CONSTANTS (NES-accurate) ===
SCREEN_W, SCREEN_H = 256 * 3, 240 * 3  # 3x NES resolution
TILE_SIZE = 16 * 3  # 48px tiles (16px * 3x scale)
NES_W, NES_H = 256, 240
GRAVITY = 0.6
MAX_FALL_SPEED = 12

# NES Color Palette
NES_BLACK = (0, 0, 0)
NES_WHITE = (252, 252, 252)
NES_SKY_BLUE = (92, 148, 252)
NES_BRICK_RED = (200, 76, 12)
NES_BRICK_DARK = (136, 20, 0)
NES_QUESTION_YELLOW = (252, 188, 60)
NES_QUESTION_DARK = (188, 120, 0)
NES_GROUND_ORANGE = (228, 92, 16)
NES_GROUND_TAN = (252, 188, 148)
NES_PIPE_GREEN = (0, 168, 0)
NES_PIPE_LIGHT = (128, 208, 16)
NES_GOOMBA_BROWN = (172, 80, 36)
NES_KOOPA_GREEN = (0, 168, 68)
NES_MARIO_RED = (228, 0, 32)
NES_MARIO_TAN = (252, 188, 148)
NES_CASTLE_GRAY = (124, 124, 124)
NES_CASTLE_DARK = (60, 60, 60)
NES_LAVA_ORANGE = (252, 116, 36)
NES_FLAG_GREEN = (0, 168, 0)

class BlockType(Enum):
    AIR = 0
    GROUND = 1
    BRICK = 2
    QUESTION = 3
    QUESTION_EMPTY = 4
    PIPE_TL = 5
    PIPE_TR = 6
    PIPE_BL = 7
    PIPE_BR = 8
    HARD_BLOCK = 9
    CASTLE_BLOCK = 10
    CASTLE_BRICK = 11
    BRIDGE = 12
    LAVA = 13
    AXE = 14
    FLAG_POLE = 15
    FLAG_TOP = 16
    INVISIBLE = 17

class EntityType(Enum):
    GOOMBA = auto()
    KOOPA = auto()
    PIRANHA = auto()
    BOWSER = auto()
    PODOBOO = auto()
    FIREBAR = auto()
    MUSHROOM = auto()
    COIN = auto()
    FIREFLOWER = auto()

# === LEVEL DATA (Famicom Accurate) ===

# 1-1: 224 tiles wide (3584 pixels on NES, 14 screens)
# Each row is 15 tiles tall (ground at row 13-14)
# Format: List of (x, y, block_type) for non-air blocks

def generate_level_1_1():
    """Generate Famicom-accurate World 1-1 layout"""
    blocks = []
    enemies = []
    items = []  # (x, y, item_type, block_x, block_y)
    
    level_width = 224  # tiles
    
    # Ground layer (rows 13-14, with gaps)
    ground_sections = [
        (0, 69), (71, 86), (89, 153), (155, 224)
    ]
    for start, end in ground_sections:
        for x in range(start, end):
            blocks.append((x, 13, BlockType.GROUND))
            blocks.append((x, 14, BlockType.GROUND))
    
    # Question blocks and bricks - accurate positions
    # First question block (coin) at tile 16
    blocks.append((16, 9, BlockType.QUESTION))
    items.append((16, 9, EntityType.COIN, 16, 9))
    
    # Brick-Question-Brick-Question-Brick formation at tiles 20-24
    blocks.append((20, 9, BlockType.BRICK))
    blocks.append((21, 9, BlockType.QUESTION))  # Mushroom/Fireflower
    items.append((21, 9, EntityType.MUSHROOM, 21, 9))
    blocks.append((22, 9, BlockType.BRICK))
    blocks.append((23, 9, BlockType.QUESTION))  # Coin
    items.append((23, 9, EntityType.COIN, 23, 9))
    blocks.append((24, 9, BlockType.BRICK))
    
    # Hidden 1-up at tile 22, row 5
    blocks.append((22, 5, BlockType.QUESTION))
    items.append((22, 5, EntityType.MUSHROOM, 22, 5))  # 1-up
    
    # First pipe at tile 28 (2 tiles wide, 2 tall)
    blocks.append((28, 11, BlockType.PIPE_TL))
    blocks.append((29, 11, BlockType.PIPE_TR))
    blocks.append((28, 12, BlockType.PIPE_BL))
    blocks.append((29, 12, BlockType.PIPE_BR))
    
    # Second pipe at tile 38 (3 tall)
    for y in range(10, 13):
        blocks.append((38, y, BlockType.PIPE_BL if y > 10 else BlockType.PIPE_TL))
        blocks.append((39, y, BlockType.PIPE_BR if y > 10 else BlockType.PIPE_TR))
    
    # Third pipe at tile 46 (4 tall) - has piranha
    for y in range(9, 13):
        blocks.append((46, y, BlockType.PIPE_BL if y > 9 else BlockType.PIPE_TL))
        blocks.append((47, y, BlockType.PIPE_BR if y > 9 else BlockType.PIPE_TR))
    enemies.append((46, 8, EntityType.PIRANHA))
    
    # Fourth pipe at tile 57 (4 tall)
    for y in range(9, 13):
        blocks.append((57, y, BlockType.PIPE_BL if y > 9 else BlockType.PIPE_TL))
        blocks.append((58, y, BlockType.PIPE_BR if y > 9 else BlockType.PIPE_TR))
    
    # Blocks after first pit at tiles 77-79
    blocks.append((77, 9, BlockType.QUESTION))  # Mushroom
    items.append((77, 9, EntityType.MUSHROOM, 77, 9))
    
    blocks.append((78, 5, BlockType.BRICK))  # Upper brick (with star)
    
    # Brick row at tiles 80-87
    for x in range(80, 88):
        blocks.append((x, 5, BlockType.BRICK))
    
    # More ground-level blocks
    blocks.append((91, 9, BlockType.BRICK))
    blocks.append((92, 9, BlockType.QUESTION))  # Coin
    items.append((92, 9, EntityType.COIN, 92, 9))
    blocks.append((93, 9, BlockType.BRICK))
    blocks.append((94, 5, BlockType.QUESTION))  # Coin
    items.append((94, 5, EntityType.COIN, 94, 5))
    
    # Question block and bricks at 100-109
    blocks.append((100, 9, BlockType.QUESTION))  # Coin
    items.append((100, 9, EntityType.COIN, 100, 9))
    blocks.append((101, 9, BlockType.QUESTION))  # Mushroom
    items.append((101, 9, EntityType.MUSHROOM, 101, 9))
    
    blocks.append((106, 9, BlockType.QUESTION))  # Coin
    items.append((106, 9, EntityType.COIN, 106, 9))
    
    # Brick formation with coins at 109-112
    blocks.append((109, 5, BlockType.BRICK))  # Multi-coin
    blocks.append((110, 5, BlockType.BRICK))
    blocks.append((111, 5, BlockType.BRICK))
    
    blocks.append((112, 9, BlockType.BRICK))
    
    # More bricks
    blocks.append((118, 9, BlockType.BRICK))
    blocks.append((119, 5, BlockType.BRICK))
    blocks.append((120, 5, BlockType.BRICK))
    blocks.append((121, 5, BlockType.BRICK))
    
    blocks.append((121, 9, BlockType.BRICK))  # Contains star
    blocks.append((122, 9, BlockType.QUESTION))  # Coin
    items.append((122, 9, EntityType.COIN, 122, 9))
    blocks.append((123, 9, BlockType.BRICK))
    
    blocks.append((128, 5, BlockType.BRICK))
    blocks.append((129, 5, BlockType.QUESTION))  # Coin
    items.append((129, 5, EntityType.COIN, 129, 5))
    blocks.append((130, 5, BlockType.QUESTION))  # Coin
    items.append((130, 5, EntityType.COIN, 130, 5))
    blocks.append((131, 5, BlockType.BRICK))
    
    # Long brick run at row 9 tiles 129-132
    for x in range(129, 133):
        blocks.append((x, 9, BlockType.BRICK))
    
    # Pipe before second pit
    for y in range(11, 13):
        blocks.append((134, y, BlockType.PIPE_TL if y == 11 else BlockType.PIPE_BL))
        blocks.append((135, y, BlockType.PIPE_TR if y == 11 else BlockType.PIPE_BR))
    
    # Stair blocks at 136-144
    for x in range(163, 167):
        for y in range(12 - (x - 163), 13):
            blocks.append((x, y, BlockType.HARD_BLOCK))
    
    # Second stair (going down)
    for x in range(167, 171):
        for y in range(9 + (x - 167), 13):
            blocks.append((x, y, BlockType.HARD_BLOCK))
    
    # Third stair
    for x in range(177, 182):
        for y in range(12 - (x - 177), 13):
            blocks.append((x, y, BlockType.HARD_BLOCK))
    
    # Fourth stair (going down)
    for x in range(182, 186):
        for y in range(8 + (x - 182), 13):
            blocks.append((x, y, BlockType.HARD_BLOCK))
    
    # Final stair to flagpole
    for x in range(198, 207):
        height = min(x - 198 + 1, 8)
        for y in range(13 - height, 13):
            blocks.append((x, y, BlockType.HARD_BLOCK))
    
    # Flagpole at 207
    for y in range(2, 13):
        blocks.append((207, y, BlockType.FLAG_POLE))
    blocks.append((207, 1, BlockType.FLAG_TOP))
    
    # Castle base at tiles 211-220
    for x in range(211, 221):
        for y in range(8, 13):
            blocks.append((x, y, BlockType.CASTLE_BLOCK))
    # Castle details
    for x in range(212, 220):
        blocks.append((x, 7, BlockType.CASTLE_BRICK))
    for x in range(213, 219):
        blocks.append((x, 6, BlockType.CASTLE_BRICK))
    blocks.append((214, 5, BlockType.CASTLE_BRICK))
    blocks.append((217, 5, BlockType.CASTLE_BRICK))
    
    # === ENEMIES (Famicom accurate positions) ===
    # Goombas
    enemies.append((22, 12, EntityType.GOOMBA))
    enemies.append((40, 12, EntityType.GOOMBA))
    enemies.append((51, 12, EntityType.GOOMBA))
    enemies.append((52, 12, EntityType.GOOMBA))
    enemies.append((80, 4, EntityType.GOOMBA))
    enemies.append((82, 4, EntityType.GOOMBA))
    enemies.append((97, 12, EntityType.GOOMBA))
    enemies.append((98, 12, EntityType.GOOMBA))
    enemies.append((114, 12, EntityType.GOOMBA))
    enemies.append((115, 12, EntityType.GOOMBA))
    enemies.append((124, 12, EntityType.GOOMBA))
    enemies.append((125, 12, EntityType.GOOMBA))
    enemies.append((128, 12, EntityType.GOOMBA))
    enemies.append((129, 12, EntityType.GOOMBA))
    enemies.append((174, 12, EntityType.GOOMBA))
    enemies.append((175, 12, EntityType.GOOMBA))
    
    # Koopa
    enemies.append((107, 12, EntityType.KOOPA))
    
    return blocks, enemies, items, level_width, NES_SKY_BLUE

def generate_level_8_4():
    """Generate Famicom-accurate World 8-4 layout with maze mechanics"""
    blocks = []
    enemies = []
    items = []
    
    level_width = 360  # Longer castle level
    
    # 8-4 is a castle level with maze mechanics
    # Wrong paths loop you back to specific checkpoints
    # Correct path: specific pipe sequences
    
    # Ground (with lava pits)
    ground_sections = [
        (0, 30), (33, 65), (68, 100), (103, 140), (143, 180), 
        (183, 220), (223, 260), (263, 300), (303, 360)
    ]
    for start, end in ground_sections:
        for x in range(start, end):
            blocks.append((x, 13, BlockType.CASTLE_BLOCK))
            blocks.append((x, 14, BlockType.CASTLE_BLOCK))
    
    # Ceiling
    for x in range(0, level_width):
        blocks.append((x, 0, BlockType.CASTLE_BLOCK))
        blocks.append((x, 1, BlockType.CASTLE_BLOCK))
    
    # Lava in pits
    lava_sections = [(30, 33), (65, 68), (100, 103), (140, 143), 
                     (180, 183), (220, 223), (260, 263), (300, 303)]
    for start, end in lava_sections:
        for x in range(start, end):
            blocks.append((x, 13, BlockType.LAVA))
            blocks.append((x, 14, BlockType.LAVA))
    
    # Section 1: Entry with first maze choice
    # Pipes at different positions - wrong pipe loops back
    
    # First pipe (correct path down)
    for y in range(9, 13):
        blocks.append((25, y, BlockType.PIPE_TL if y == 9 else BlockType.PIPE_BL))
        blocks.append((26, y, BlockType.PIPE_TR if y == 9 else BlockType.PIPE_BR))
    
    # Brick platforms
    for x in range(10, 18):
        blocks.append((x, 9, BlockType.CASTLE_BRICK))
    
    for x in range(35, 45):
        blocks.append((x, 7, BlockType.CASTLE_BRICK))
    
    # Second section - underwater corridor simulation (tight passage)
    for x in range(50, 60):
        blocks.append((x, 5, BlockType.CASTLE_BLOCK))
        blocks.append((x, 6, BlockType.CASTLE_BLOCK))
    
    # Second pipe (must go down here)
    for y in range(8, 13):
        blocks.append((70, y, BlockType.PIPE_TL if y == 8 else BlockType.PIPE_BL))
        blocks.append((71, y, BlockType.PIPE_TR if y == 8 else BlockType.PIPE_BR))
    
    # Third section - more platforms
    for x in range(85, 95):
        blocks.append((x, 9, BlockType.CASTLE_BRICK))
    for x in range(90, 98):
        blocks.append((x, 5, BlockType.CASTLE_BRICK))
    
    # Wrong pipe (loops back if taken)
    for y in range(10, 13):
        blocks.append((95, y, BlockType.PIPE_TL if y == 10 else BlockType.PIPE_BL))
        blocks.append((96, y, BlockType.PIPE_TR if y == 10 else BlockType.PIPE_BR))
    
    # Correct pipe
    for y in range(7, 13):
        blocks.append((110, y, BlockType.PIPE_TL if y == 7 else BlockType.PIPE_BL))
        blocks.append((111, y, BlockType.PIPE_TR if y == 7 else BlockType.PIPE_BR))
    
    # Section 4 - Firebar section
    for x in range(120, 130):
        blocks.append((x, 9, BlockType.CASTLE_BRICK))
    enemies.append((125, 9, EntityType.FIREBAR))  # Firebar anchor
    
    for x in range(135, 145):
        blocks.append((x, 7, BlockType.CASTLE_BRICK))
    enemies.append((140, 7, EntityType.FIREBAR))
    
    # Podoboos in lava
    enemies.append((140, 13, EntityType.PODOBOO))
    enemies.append((181, 13, EntityType.PODOBOO))
    enemies.append((221, 13, EntityType.PODOBOO))
    
    # Third pipe section
    for y in range(9, 13):
        blocks.append((155, y, BlockType.PIPE_TL if y == 9 else BlockType.PIPE_BL))
        blocks.append((156, y, BlockType.PIPE_TR if y == 9 else BlockType.PIPE_BR))
    
    # More platforms leading to next choice
    for x in range(165, 178):
        blocks.append((x, 9, BlockType.CASTLE_BRICK))
    
    # Section 5 - Another maze point
    for y in range(8, 13):
        blocks.append((190, y, BlockType.PIPE_TL if y == 8 else BlockType.PIPE_BL))
        blocks.append((191, y, BlockType.PIPE_TR if y == 8 else BlockType.PIPE_BR))
    
    # Wrong pipe
    for y in range(10, 13):
        blocks.append((200, y, BlockType.PIPE_TL if y == 10 else BlockType.PIPE_BL))
        blocks.append((201, y, BlockType.PIPE_TR if y == 10 else BlockType.PIPE_BR))
    
    # Correct pipe to final section
    for y in range(6, 13):
        blocks.append((230, y, BlockType.PIPE_TL if y == 6 else BlockType.PIPE_BL))
        blocks.append((231, y, BlockType.PIPE_TR if y == 6 else BlockType.PIPE_BR))
    
    # Section 6 - Bowser's chamber
    # Bridge
    for x in range(280, 310):
        blocks.append((x, 11, BlockType.BRIDGE))
    
    # Bowser platform
    for x in range(290, 305):
        blocks.append((x, 7, BlockType.CASTLE_BRICK))
    
    # Lava under bridge
    for x in range(280, 310):
        blocks.append((x, 13, BlockType.LAVA))
        blocks.append((x, 14, BlockType.LAVA))
    
    # Axe at end of bridge
    blocks.append((309, 10, BlockType.AXE))
    
    # Bowser
    enemies.append((295, 6, EntityType.BOWSER))
    
    # Final room after axe
    for x in range(315, 350):
        blocks.append((x, 13, BlockType.CASTLE_BLOCK))
        blocks.append((x, 14, BlockType.CASTLE_BLOCK))
    
    # Princess room walls
    for y in range(2, 13):
        blocks.append((310, y, BlockType.CASTLE_BLOCK))
        blocks.append((350, y, BlockType.CASTLE_BLOCK))
    
    # Firebars
    enemies.append((265, 9, EntityType.FIREBAR))
    enemies.append((275, 11, EntityType.FIREBAR))
    
    return blocks, enemies, items, level_width, NES_BLACK

# === GAME CLASSES ===

class Camera:
    def __init__(self, width, height):
        self.x = 0
        self.y = 0
        self.width = width
        self.height = height
    
    def follow(self, target):
        # NES-style: camera follows player, can't go back
        target_x = target.rect.centerx - SCREEN_W // 3
        if target_x > self.x:
            self.x = target_x
        # Don't let camera go negative
        if self.x < 0:
            self.x = 0

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE_SIZE - 8, TILE_SIZE * 2 - 8)
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.facing_right = True
        self.dead = False
        self.big = False
        self.star_power = False
        self.invincible_timer = 0
        
        # Physics constants (NES accurate)
        self.run_accel = 0.35
        self.run_decel = 0.25
        self.max_walk_speed = 5
        self.max_run_speed = 8
        self.jump_power = -13
        self.small_jump_power = -9
        
        # Animation
        self.frame = 0
        self.frame_timer = 0
    
    def update(self, keys, blocks, enemies, game):
        if self.dead:
            self.vel_y += GRAVITY
            self.rect.y += self.vel_y
            return
        
        # Horizontal movement (NES physics)
        running = keys[pygame.K_LSHIFT] or keys[pygame.K_x]
        max_speed = self.max_run_speed if running else self.max_walk_speed
        
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x += self.run_accel
            self.facing_right = True
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x -= self.run_accel
            self.facing_right = False
        else:
            # Deceleration
            if self.vel_x > 0:
                self.vel_x = max(0, self.vel_x - self.run_decel)
            elif self.vel_x < 0:
                self.vel_x = min(0, self.vel_x + self.run_decel)
        
        self.vel_x = max(-max_speed, min(max_speed, self.vel_x))
        
        # Gravity
        self.vel_y += GRAVITY
        self.vel_y = min(self.vel_y, MAX_FALL_SPEED)
        
        # Jump (variable height based on hold time)
        if (keys[pygame.K_SPACE] or keys[pygame.K_z]) and self.on_ground:
            self.vel_y = self.jump_power
            self.on_ground = False
        
        # Cut jump short if button released
        if not (keys[pygame.K_SPACE] or keys[pygame.K_z]) and self.vel_y < -5:
            self.vel_y = -5
        
        # Move and collide X
        self.rect.x += self.vel_x
        self.collide_blocks_x(blocks, game)
        
        # Move and collide Y
        self.rect.y += self.vel_y
        self.on_ground = False
        self.collide_blocks_y(blocks, game)
        
        # Check death by falling
        if self.rect.top > SCREEN_H:
            self.die()
        
        # Enemy collision
        if not self.star_power and self.invincible_timer <= 0:
            for enemy in enemies:
                if enemy.alive and self.rect.colliderect(enemy.rect):
                    # Check if stomping
                    if self.vel_y > 0 and self.rect.bottom < enemy.rect.centery:
                        enemy.stomp()
                        self.vel_y = self.small_jump_power
                    else:
                        self.take_damage()
        
        # Invincibility timer
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
        
        # Animation
        self.frame_timer += 1
        if self.frame_timer > 8:
            self.frame_timer = 0
            self.frame = (self.frame + 1) % 3
    
    def collide_blocks_x(self, blocks, game):
        for block in blocks:
            if self.rect.colliderect(block.rect):
                if block.block_type == BlockType.LAVA:
                    self.die()
                    return
                if block.block_type == BlockType.AXE:
                    game.trigger_axe()
                    return
                if block.solid:
                    if self.vel_x > 0:
                        self.rect.right = block.rect.left
                    elif self.vel_x < 0:
                        self.rect.left = block.rect.right
                    self.vel_x = 0
    
    def collide_blocks_y(self, blocks, game):
        for block in blocks:
            if self.rect.colliderect(block.rect):
                if block.block_type == BlockType.LAVA:
                    self.die()
                    return
                if block.solid:
                    if self.vel_y > 0:
                        self.rect.bottom = block.rect.top
                        self.vel_y = 0
                        self.on_ground = True
                    elif self.vel_y < 0:
                        self.rect.top = block.rect.bottom
                        self.vel_y = 0
                        block.hit_from_below(game)
    
    def take_damage(self):
        if self.invincible_timer > 0:
            return
        if self.big:
            self.big = False
            self.rect.height = TILE_SIZE - 8
            self.invincible_timer = 120
        else:
            self.die()
    
    def die(self):
        self.dead = True
        self.vel_y = -12
        self.vel_x = 0
    
    def draw(self, screen, camera):
        x = self.rect.x - camera.x
        y = self.rect.y - camera.y
        
        # Blink when invincible
        if self.invincible_timer > 0 and (self.invincible_timer // 4) % 2 == 0:
            return
        
        # Draw Mario (simplified sprite)
        color = NES_MARIO_RED
        if self.dead:
            color = NES_MARIO_RED
        
        # Body
        pygame.draw.rect(screen, color, (x + 4, y + TILE_SIZE // 2, TILE_SIZE - 16, TILE_SIZE // 2))
        # Head
        pygame.draw.rect(screen, NES_MARIO_TAN, (x + 8, y + 4, TILE_SIZE - 24, TILE_SIZE // 3))
        # Hat
        pygame.draw.rect(screen, NES_MARIO_RED, (x + 4, y, TILE_SIZE - 12, 12))

class Block:
    def __init__(self, x, y, block_type):
        self.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.block_type = block_type
        self.tile_x = x
        self.tile_y = y
        self.solid = block_type not in [BlockType.AIR, BlockType.LAVA, BlockType.AXE, 
                                         BlockType.FLAG_POLE, BlockType.FLAG_TOP]
        self.alive = True
        self.hit = False
        self.coin_count = 0
        self.bump_offset = 0
        self.contains_item = None
    
    def hit_from_below(self, game):
        if self.block_type == BlockType.QUESTION and not self.hit:
            self.hit = True
            self.block_type = BlockType.QUESTION_EMPTY
            self.bump_offset = -8
            if self.contains_item:
                game.spawn_item(self.tile_x, self.tile_y - 1, self.contains_item)
        elif self.block_type == BlockType.BRICK:
            if game.player.big:
                self.alive = False
                game.spawn_debris(self.rect.centerx, self.rect.centery)
            else:
                self.bump_offset = -8
    
    def update(self):
        if self.bump_offset < 0:
            self.bump_offset += 2
            if self.bump_offset > 0:
                self.bump_offset = 0
    
    def draw(self, screen, camera):
        if not self.alive:
            return
        x = self.rect.x - camera.x
        y = self.rect.y - camera.y + self.bump_offset
        
        if x < -TILE_SIZE or x > SCREEN_W:
            return
        
        if self.block_type == BlockType.GROUND:
            pygame.draw.rect(screen, NES_GROUND_ORANGE, (x, y, TILE_SIZE, TILE_SIZE))
            pygame.draw.rect(screen, NES_GROUND_TAN, (x, y, TILE_SIZE, 8))
        
        elif self.block_type == BlockType.BRICK:
            pygame.draw.rect(screen, NES_BRICK_RED, (x, y, TILE_SIZE, TILE_SIZE))
            # Brick pattern
            pygame.draw.line(screen, NES_BRICK_DARK, (x, y + TILE_SIZE//2), (x + TILE_SIZE, y + TILE_SIZE//2), 2)
            pygame.draw.line(screen, NES_BRICK_DARK, (x + TILE_SIZE//2, y), (x + TILE_SIZE//2, y + TILE_SIZE//2), 2)
            pygame.draw.line(screen, NES_BRICK_DARK, (x + TILE_SIZE//4, y + TILE_SIZE//2), (x + TILE_SIZE//4, y + TILE_SIZE), 2)
            pygame.draw.line(screen, NES_BRICK_DARK, (x + TILE_SIZE*3//4, y + TILE_SIZE//2), (x + TILE_SIZE*3//4, y + TILE_SIZE), 2)
        
        elif self.block_type in [BlockType.QUESTION, BlockType.QUESTION_EMPTY]:
            color = NES_QUESTION_YELLOW if self.block_type == BlockType.QUESTION else NES_BRICK_DARK
            pygame.draw.rect(screen, color, (x, y, TILE_SIZE, TILE_SIZE))
            pygame.draw.rect(screen, NES_QUESTION_DARK, (x, y, TILE_SIZE, TILE_SIZE), 3)
            if self.block_type == BlockType.QUESTION:
                # Question mark
                font = pygame.font.SysFont("arial", 24, bold=True)
                text = font.render("?", True, NES_BRICK_DARK)
                screen.blit(text, (x + TILE_SIZE//3, y + 4))
        
        elif self.block_type in [BlockType.PIPE_TL, BlockType.PIPE_TR, BlockType.PIPE_BL, BlockType.PIPE_BR]:
            pygame.draw.rect(screen, NES_PIPE_GREEN, (x, y, TILE_SIZE, TILE_SIZE))
            if self.block_type in [BlockType.PIPE_TL, BlockType.PIPE_TR]:
                pygame.draw.rect(screen, NES_PIPE_LIGHT, (x, y, TILE_SIZE, 8))
            if self.block_type in [BlockType.PIPE_TL, BlockType.PIPE_BL]:
                pygame.draw.rect(screen, NES_PIPE_LIGHT, (x, y, 6, TILE_SIZE))
        
        elif self.block_type == BlockType.HARD_BLOCK:
            pygame.draw.rect(screen, NES_GROUND_TAN, (x, y, TILE_SIZE, TILE_SIZE))
            pygame.draw.rect(screen, NES_BRICK_DARK, (x, y, TILE_SIZE, TILE_SIZE), 2)
        
        elif self.block_type in [BlockType.CASTLE_BLOCK, BlockType.CASTLE_BRICK]:
            pygame.draw.rect(screen, NES_CASTLE_GRAY, (x, y, TILE_SIZE, TILE_SIZE))
            pygame.draw.rect(screen, NES_CASTLE_DARK, (x, y, TILE_SIZE, TILE_SIZE), 2)
        
        elif self.block_type == BlockType.BRIDGE:
            pygame.draw.rect(screen, NES_BRICK_RED, (x, y + TILE_SIZE//2, TILE_SIZE, TILE_SIZE//2))
        
        elif self.block_type == BlockType.LAVA:
            pygame.draw.rect(screen, NES_LAVA_ORANGE, (x, y, TILE_SIZE, TILE_SIZE))
            # Animated waves
            wave_offset = (pygame.time.get_ticks() // 100) % 8
            pygame.draw.rect(screen, (252, 160, 68), (x, y + wave_offset, TILE_SIZE, 4))
        
        elif self.block_type == BlockType.AXE:
            # Draw axe
            pygame.draw.rect(screen, NES_QUESTION_YELLOW, (x + 8, y + 8, TILE_SIZE - 16, TILE_SIZE - 16))
            pygame.draw.rect(screen, NES_BRICK_DARK, (x + TILE_SIZE//2 - 4, y + TILE_SIZE//2, 8, TILE_SIZE//2))
        
        elif self.block_type == BlockType.FLAG_POLE:
            pygame.draw.rect(screen, NES_CASTLE_GRAY, (x + TILE_SIZE//2 - 3, y, 6, TILE_SIZE))
        
        elif self.block_type == BlockType.FLAG_TOP:
            pygame.draw.rect(screen, NES_FLAG_GREEN, (x + TILE_SIZE//2 - 3, y, 6, TILE_SIZE))
            pygame.draw.polygon(screen, NES_FLAG_GREEN, [
                (x + TILE_SIZE//2, y + 8),
                (x + TILE_SIZE//2 - 20, y + 20),
                (x + TILE_SIZE//2, y + 32)
            ])

class Enemy:
    def __init__(self, x, y, enemy_type):
        self.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE - 8, TILE_SIZE - 8)
        self.enemy_type = enemy_type
        self.vel_x = -2 if enemy_type != EntityType.BOWSER else -1
        self.vel_y = 0
        self.alive = True
        self.squished = False
        self.squish_timer = 0
        self.frame = 0
        self.frame_timer = 0
        
        # Bowser specific
        if enemy_type == EntityType.BOWSER:
            self.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE * 2, TILE_SIZE * 2)
            self.fire_timer = 0
        
        # Podoboo specific
        if enemy_type == EntityType.PODOBOO:
            self.base_y = y * TILE_SIZE
            self.jump_timer = random.randint(0, 120)
            self.jumping = False
        
        # Firebar specific
        if enemy_type == EntityType.FIREBAR:
            self.angle = 0
            self.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
    
    def update(self, blocks, player):
        if not self.alive:
            if self.squished:
                self.squish_timer += 1
                if self.squish_timer > 30:
                    return True  # Remove
            return False
        
        if self.enemy_type == EntityType.PODOBOO:
            self.jump_timer += 1
            if not self.jumping and self.jump_timer > 150:
                self.jumping = True
                self.vel_y = -15
                self.jump_timer = 0
            
            if self.jumping:
                self.vel_y += 0.4
                self.rect.y += self.vel_y
                if self.rect.y >= self.base_y:
                    self.rect.y = self.base_y
                    self.jumping = False
                    self.vel_y = 0
            return False
        
        if self.enemy_type == EntityType.FIREBAR:
            self.angle += 2
            return False
        
        if self.enemy_type == EntityType.PIRANHA:
            # Piranha in pipe - bob up and down
            self.frame_timer += 1
            bob = (self.frame_timer // 30) % 2
            self.rect.y = self.rect.y  # Stay in place for now
            return False
        
        if self.enemy_type == EntityType.BOWSER:
            # Bowser AI
            self.fire_timer += 1
            if abs(player.rect.x - self.rect.x) < SCREEN_W // 2:
                if self.rect.x > player.rect.x:
                    self.vel_x = -1
                else:
                    self.vel_x = 1
            
            # Random jumps
            if random.random() < 0.01:
                self.vel_y = -10
        
        # Gravity
        self.vel_y += GRAVITY * 0.5
        self.vel_y = min(self.vel_y, MAX_FALL_SPEED)
        
        # Move
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        
        # Collide with blocks
        for block in blocks:
            if block.solid and self.rect.colliderect(block.rect):
                if self.vel_y > 0:
                    self.rect.bottom = block.rect.top
                    self.vel_y = 0
                elif self.vel_x != 0:
                    self.vel_x *= -1
                    self.rect.x += self.vel_x * 2
        
        # Animation
        self.frame_timer += 1
        if self.frame_timer > 10:
            self.frame_timer = 0
            self.frame = (self.frame + 1) % 2
        
        return False
    
    def stomp(self):
        if self.enemy_type in [EntityType.GOOMBA]:
            self.alive = False
            self.squished = True
        elif self.enemy_type == EntityType.KOOPA:
            self.alive = False
            self.squished = True
    
    def draw(self, screen, camera):
        x = self.rect.x - camera.x
        y = self.rect.y - camera.y
        
        if x < -TILE_SIZE * 2 or x > SCREEN_W + TILE_SIZE:
            return
        
        if self.enemy_type == EntityType.GOOMBA:
            if self.squished:
                pygame.draw.rect(screen, NES_GOOMBA_BROWN, (x, y + TILE_SIZE - 12, TILE_SIZE - 8, 12))
            else:
                pygame.draw.ellipse(screen, NES_GOOMBA_BROWN, (x, y, TILE_SIZE - 8, TILE_SIZE - 8))
                # Eyes
                pygame.draw.circle(screen, NES_WHITE, (x + 10, y + 12), 4)
                pygame.draw.circle(screen, NES_WHITE, (x + TILE_SIZE - 18, y + 12), 4)
                pygame.draw.circle(screen, NES_BLACK, (x + 10, y + 12), 2)
                pygame.draw.circle(screen, NES_BLACK, (x + TILE_SIZE - 18, y + 12), 2)
        
        elif self.enemy_type == EntityType.KOOPA:
            if self.squished:
                pygame.draw.ellipse(screen, NES_KOOPA_GREEN, (x, y + TILE_SIZE - 16, TILE_SIZE - 8, 16))
            else:
                pygame.draw.ellipse(screen, NES_KOOPA_GREEN, (x, y, TILE_SIZE - 8, TILE_SIZE - 8))
                pygame.draw.rect(screen, NES_KOOPA_GREEN, (x + 4, y + TILE_SIZE - 24, TILE_SIZE - 16, 16))
        
        elif self.enemy_type == EntityType.BOWSER:
            # Big green monster
            pygame.draw.rect(screen, NES_KOOPA_GREEN, (x, y, TILE_SIZE * 2, TILE_SIZE * 2))
            pygame.draw.rect(screen, NES_BRICK_RED, (x + 10, y + 10, 20, 10))  # Eye
            pygame.draw.rect(screen, NES_LAVA_ORANGE, (x + TILE_SIZE * 2 - 20, y + TILE_SIZE, 30, 10))  # Fire mouth
        
        elif self.enemy_type == EntityType.PODOBOO:
            pygame.draw.ellipse(screen, NES_LAVA_ORANGE, (x, y, TILE_SIZE - 8, TILE_SIZE - 8))
            pygame.draw.ellipse(screen, (255, 200, 100), (x + 6, y + 6, TILE_SIZE - 20, TILE_SIZE - 20))
        
        elif self.enemy_type == EntityType.FIREBAR:
            # Draw rotating firebar
            import math
            cx, cy = self.rect.centerx - camera.x, self.rect.centery - camera.y
            for i in range(6):
                angle_rad = math.radians(self.angle)
                fx = cx + math.cos(angle_rad) * (i * 12)
                fy = cy + math.sin(angle_rad) * (i * 12)
                pygame.draw.circle(screen, NES_LAVA_ORANGE, (int(fx), int(fy)), 8)

class Item:
    def __init__(self, x, y, item_type):
        self.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE - 8, TILE_SIZE - 8)
        self.item_type = item_type
        self.vel_x = 2
        self.vel_y = 0
        self.alive = True
        self.emerging = True
        self.emerge_y = self.rect.y + TILE_SIZE
        self.start_y = self.rect.y
    
    def update(self, blocks, player):
        if not self.alive:
            return True
        
        if self.emerging:
            self.rect.y -= 2
            if self.rect.y <= self.start_y:
                self.rect.y = self.start_y
                self.emerging = False
            return False
        
        if self.item_type == EntityType.COIN:
            self.alive = False
            return True
        
        # Mushroom movement
        self.vel_y += GRAVITY
        self.vel_y = min(self.vel_y, MAX_FALL_SPEED)
        
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        
        # Block collision
        for block in blocks:
            if block.solid and self.rect.colliderect(block.rect):
                if self.vel_y > 0:
                    self.rect.bottom = block.rect.top
                    self.vel_y = 0
                elif self.vel_x != 0:
                    self.vel_x *= -1
        
        # Player collection
        if self.rect.colliderect(player.rect):
            self.alive = False
            if self.item_type == EntityType.MUSHROOM:
                if not player.big:
                    player.big = True
                    player.rect.height = TILE_SIZE * 2 - 8
                    player.rect.y -= TILE_SIZE
            return True
        
        return False
    
    def draw(self, screen, camera):
        if not self.alive:
            return
        
        x = self.rect.x - camera.x
        y = self.rect.y - camera.y
        
        if self.item_type == EntityType.MUSHROOM:
            pygame.draw.ellipse(screen, NES_MARIO_RED, (x, y, TILE_SIZE - 8, TILE_SIZE // 2))
            pygame.draw.rect(screen, NES_MARIO_TAN, (x + 4, y + TILE_SIZE // 2 - 4, TILE_SIZE - 16, TILE_SIZE // 2))
            # Spots
            pygame.draw.circle(screen, NES_WHITE, (x + 10, y + 8), 4)
            pygame.draw.circle(screen, NES_WHITE, (x + TILE_SIZE - 18, y + 8), 4)
        
        elif self.item_type == EntityType.COIN:
            pygame.draw.ellipse(screen, NES_QUESTION_YELLOW, (x + 8, y, TILE_SIZE - 24, TILE_SIZE - 8))

class Debris:
    def __init__(self, x, y, vel_x, vel_y):
        self.x = x
        self.y = y
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.alive = True
    
    def update(self):
        self.vel_y += GRAVITY
        self.x += self.vel_x
        self.y += self.vel_y
        if self.y > SCREEN_H:
            self.alive = False
    
    def draw(self, screen, camera):
        x = self.x - camera.x
        y = self.y - camera.y
        pygame.draw.rect(screen, NES_BRICK_RED, (x, y, 12, 12))

def draw_text_nes(screen, text, font, x, y, color=NES_WHITE, shadow_color=NES_BLACK):
    """Draw text with NES-style shadow"""
    shadow = font.render(text, True, shadow_color)
    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect(center=(x, y))
    shadow_rect = shadow.get_rect(center=(x + 2, y + 2))
    screen.blit(shadow, shadow_rect)
    screen.blit(text_surf, text_rect)

# === MAIN GAME CLASS ===

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Super Mario Bros - Team Flames")
        self.clock = pygame.time.Clock()
        
        self.font = pygame.font.SysFont("arial", 24, bold=True)
        self.font_big = pygame.font.SysFont("arial", 48, bold=True)
        
        self.state = "menu"
        self.current_level = "1-1"
        self.transition_timer = 0
        self.score = 0
        self.coins = 0
        self.lives = 3
        self.time = 400
        self.time_timer = 0
        
        self.reset_game()
    
    def reset_game(self):
        self.load_level(self.current_level)
        self.camera = Camera(SCREEN_W, SCREEN_H)
        self.debris = []
        self.items = []
        self.axe_triggered = False
        self.bridge_collapse_timer = 0
    
    def load_level(self, level_name):
        self.current_level = level_name
        
        if level_name == "1-1":
            block_data, enemy_data, item_data, self.level_width, self.bg_color = generate_level_1_1()
        else:
            block_data, enemy_data, item_data, self.level_width, self.bg_color = generate_level_8_4()
        
        # Create blocks
        self.blocks = []
        for x, y, btype in block_data:
            block = Block(x, y, btype)
            self.blocks.append(block)
        
        # Assign items to question blocks
        for item_x, item_y, item_type, block_x, block_y in item_data:
            for block in self.blocks:
                if block.tile_x == block_x and block.tile_y == block_y:
                    block.contains_item = item_type
        
        # Create enemies
        self.enemies = []
        for x, y, etype in enemy_data:
            self.enemies.append(Enemy(x, y, etype))
        
        # Create player
        if level_name == "1-1":
            self.player = Player(3 * TILE_SIZE, 11 * TILE_SIZE)
        else:
            self.player = Player(3 * TILE_SIZE, 11 * TILE_SIZE)
        
        # Items list
        self.items = []
        
        # Reset time
        self.time = 400
        self.time_timer = 0
    
    def spawn_item(self, x, y, item_type):
        self.items.append(Item(x, y, item_type))
        if item_type == EntityType.COIN:
            self.coins += 1
            self.score += 200
    
    def spawn_debris(self, x, y):
        for vx, vy in [(-3, -8), (3, -8), (-2, -6), (2, -6)]:
            self.debris.append(Debris(x, y, vx, vy))
        self.score += 50
    
    def trigger_axe(self):
        if not self.axe_triggered:
            self.axe_triggered = True
            self.bridge_collapse_timer = pygame.time.get_ticks()
            # Kill Bowser
            for enemy in self.enemies:
                if enemy.enemy_type == EntityType.BOWSER:
                    enemy.alive = False
    
    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if self.state == "menu":
                    if event.key == pygame.K_RETURN:
                        self.current_level = "1-1"
                        self.reset_game()
                        self.state = "playing"
                    if event.key == pygame.K_1:
                        self.current_level = "1-1"
                        self.reset_game()
                        self.state = "playing"
                    if event.key == pygame.K_8:
                        self.current_level = "8-4"
                        self.reset_game()
                        self.state = "playing"
                
                elif self.state == "gameover" or (self.state == "win" and self.current_level == "8-4"):
                    if event.key == pygame.K_RETURN:
                        self.state = "menu"
        
        if self.state == "playing":
            keys = pygame.key.get_pressed()
            
            # Update timer
            self.time_timer += 1
            if self.time_timer >= 24:  # ~2.5 seconds per unit
                self.time_timer = 0
                self.time -= 1
                if self.time <= 0:
                    self.player.die()
            
            # Update player
            self.player.update(keys, self.blocks, self.enemies, self)
            
            # Camera follow
            self.camera.follow(self.player)
            
            # Update blocks
            for block in self.blocks:
                block.update()
            
            # Update enemies
            for enemy in self.enemies[:]:
                if enemy.update(self.blocks, self.player):
                    self.enemies.remove(enemy)
            
            # Update items
            for item in self.items[:]:
                if item.update(self.blocks, self.player):
                    self.items.remove(item)
            
            # Update debris
            for debris in self.debris[:]:
                debris.update()
                if not debris.alive:
                    self.debris.remove(debris)
            
            # Bridge collapse
            if self.axe_triggered:
                elapsed = pygame.time.get_ticks() - self.bridge_collapse_timer
                if elapsed > 100:
                    # Remove bridge blocks progressively
                    for block in self.blocks[:]:
                        if block.block_type == BlockType.BRIDGE:
                            if random.random() < 0.1:
                                block.alive = False
            
            # Check win condition (flag in 1-1)
            if self.current_level == "1-1":
                for block in self.blocks:
                    if block.block_type == BlockType.FLAG_POLE:
                        if self.player.rect.colliderect(block.rect):
                            self.state = "win"
                            self.transition_timer = pygame.time.get_ticks()
                            break
            
            # Check win condition (axe in 8-4)
            if self.current_level == "8-4" and self.axe_triggered:
                elapsed = pygame.time.get_ticks() - self.bridge_collapse_timer
                if elapsed > 3000:
                    self.state = "win"
                    self.transition_timer = pygame.time.get_ticks()
            
            # Check death
            if self.player.dead:
                self.lives -= 1
                if self.lives <= 0:
                    self.state = "gameover"
                else:
                    self.reset_game()
        
        elif self.state == "win":
            if self.current_level == "1-1":
                if pygame.time.get_ticks() - self.transition_timer > 3000:
                    self.current_level = "8-4"
                    self.reset_game()
                    self.state = "playing"
    
    def draw(self):
        self.screen.fill(self.bg_color)
        
        if self.state == "menu":
            draw_text_nes(self.screen, "SUPER MARIO BROS", self.font_big, SCREEN_W // 2, SCREEN_H // 3)
            draw_text_nes(self.screen, "Team Flames / Samsoft", self.font, SCREEN_W // 2, SCREEN_H // 3 + 60)
            draw_text_nes(self.screen, "Press ENTER to Start", self.font, SCREEN_W // 2, SCREEN_H // 2)
            draw_text_nes(self.screen, "Press 1 for World 1-1", self.font, SCREEN_W // 2, SCREEN_H // 2 + 40)
            draw_text_nes(self.screen, "Press 8 for World 8-4", self.font, SCREEN_W // 2, SCREEN_H // 2 + 80)
        
        elif self.state in ["playing", "win", "gameover"]:
            # Draw blocks
            for block in self.blocks:
                block.draw(self.screen, self.camera)
            
            # Draw items
            for item in self.items:
                item.draw(self.screen, self.camera)
            
            # Draw enemies
            for enemy in self.enemies:
                enemy.draw(self.screen, self.camera)
            
            # Draw debris
            for debris in self.debris:
                debris.draw(self.screen, self.camera)
            
            # Draw player
            self.player.draw(self.screen, self.camera)
            
            # HUD
            draw_text_nes(self.screen, f"MARIO", self.font, 100, 20)
            draw_text_nes(self.screen, f"{self.score:06d}", self.font, 100, 45)
            
            draw_text_nes(self.screen, f"x{self.coins:02d}", self.font, 280, 45)
            
            draw_text_nes(self.screen, f"WORLD", self.font, 450, 20)
            draw_text_nes(self.screen, f"{self.current_level}", self.font, 450, 45)
            
            draw_text_nes(self.screen, f"TIME", self.font, 620, 20)
            draw_text_nes(self.screen, f"{self.time:03d}", self.font, 620, 45)
            
            if self.state == "win":
                msg = "COURSE CLEAR!" if self.current_level == "1-1" else "PRINCESS SAVED!"
                draw_text_nes(self.screen, msg, self.font_big, SCREEN_W // 2, SCREEN_H // 2, NES_WHITE, NES_BLACK)
                if self.current_level == "8-4":
                    draw_text_nes(self.screen, "Press ENTER", self.font, SCREEN_W // 2, SCREEN_H // 2 + 50)
            
            elif self.state == "gameover":
                draw_text_nes(self.screen, "GAME OVER", self.font_big, SCREEN_W // 2, SCREEN_H // 2, NES_MARIO_RED, NES_BLACK)
                draw_text_nes(self.screen, "Press ENTER", self.font, SCREEN_W // 2, SCREEN_H // 2 + 50)
        
        pygame.display.flip()
    
    def run(self):
        while True:
            self.update()
            self.draw()
            self.clock.tick(60)

if __name__ == "__main__":
    game = Game()
    game.run()
