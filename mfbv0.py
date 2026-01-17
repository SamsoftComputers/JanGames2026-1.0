import pygame
import json
import sys
import os
import math
import copy
from enum import Enum

pygame.init()

# --- Constants ---
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
TOOLBAR_HEIGHT = 160
GRID_SIZE = 32
FPS = 60

# Physics Constants
GRAVITY = 0.5
MAX_FALL_SPEED = 12
JM_FORCE = -11       # Jump force
JM_HOLD_GRAV = 0.25  # Lower gravity while holding jump
ACCEL = 0.5
FRICTION = 0.3
MAX_WALK_SPEED = 6
MAX_RUN_SPEED = 10

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
LIGHT_GRAY = (200, 200, 200)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 120, 255)
YELLOW = (255, 255, 0)
PURPLE = (180, 0, 255)
CYAN = (0, 255, 255)
DARK_GRAY = (40, 40, 40)
BACKGROUND_GRAY = (60, 60, 70)
SKY_BLUE = (100, 149, 237)

# --- Enums ---
class Layer(Enum):
    BACKGROUND = 0
    DESTRUCTIBLE = 1
    MAIN = 2
    FOREGROUND = 3
    FGBACKGROUND = 4

class EditorMode(Enum):
    TILE = 0
    BLOCK = 1
    NPC = 2
    BACKGROUND = 3
    PATH = 4
    SECTION = 5
    SETTINGS = 6

class GameState(Enum):
    EDITOR = 0
    PLAY = 1

# --- Setup ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("SMBX Clone - Python Edition")
clock = pygame.time.Clock()

font_small = pygame.font.SysFont("arial", 12)
font_medium = pygame.font.SysFont("arial", 20)
font_large = pygame.font.SysFont("arial", 32)

# --- Classes ---

class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.zoom = 1.0
        self.target = None  # For following player
        
    def update(self, keys, mouse_buttons, mouse_pos):
        # Editor Movement
        if not self.target:
            speed = 10 / self.zoom
            if keys[pygame.K_a]: self.x -= speed
            if keys[pygame.K_d]: self.x += speed
            if keys[pygame.K_w]: self.y -= speed
            if keys[pygame.K_s]: self.y += speed
            
            # Drag Pan
            if mouse_buttons[2]: # Right Click
                rel_x, rel_y = pygame.mouse.get_rel()
                self.x -= rel_x / self.zoom
                self.y -= rel_y / self.zoom
            else:
                pygame.mouse.get_rel() # Clear relative movement
        else:
            # Follow Target (Player)
            # Smooth lerp
            target_x = self.target.rect.centerx - SCREEN_WIDTH / (2 * self.zoom)
            target_y = self.target.rect.centery - SCREEN_HEIGHT / (2 * self.zoom)
            self.x += (target_x - self.x) * 0.1
            self.y += (target_y - self.y) * 0.1

    def world_to_screen(self, pos):
        return (int((pos[0] - self.x) * self.zoom), int((pos[1] - self.y) * self.zoom))

    def screen_to_world(self, pos):
        return (int(pos[0] / self.zoom + self.x), int(pos[1] / self.zoom + self.y))

class GameObject:
    def __init__(self, x, y, id, layer):
        self.x = x
        self.y = y
        self.id = id
        self.layer = layer
        self.width = GRID_SIZE
        self.height = GRID_SIZE
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.color = WHITE

    def update_rect(self):
        self.rect.topleft = (self.x, self.y)

    def draw(self, surface, camera, selected=False):
        screen_pos = camera.world_to_screen((self.x, self.y))
        w = int(self.width * camera.zoom)
        h = int(self.height * camera.zoom)
        
        # Culling
        if (screen_pos[0] > SCREEN_WIDTH or screen_pos[0] + w < 0 or 
            screen_pos[1] > SCREEN_HEIGHT or screen_pos[1] + h < 0):
            return

        draw_rect = pygame.Rect(screen_pos[0], screen_pos[1], w, h)
        pygame.draw.rect(surface, self.color, draw_rect)
        if selected:
            pygame.draw.rect(surface, YELLOW, draw_rect, 2)
        else:
            pygame.draw.rect(surface, (self.color[0]//2, self.color[1]//2, self.color[2]//2), draw_rect, 1)

    def to_dict(self):
        return {"x": self.x, "y": self.y, "id": self.id, "layer": self.layer.value}

class Tile(GameObject):
    def __init__(self, x, y, id, layer=Layer.MAIN):
        super().__init__(x, y, id, layer)
        self.color = self.get_color()
        
    def get_color(self):
        if self.id == 1: return (100, 200, 100) # Grass
        if self.id == 2: return (139, 69, 19)   # Dirt
        if self.id == 3: return (150, 150, 150) # Stone
        if self.id == 4: return (50, 50, 200)   # Water
        return (200, 100, 200)

class Block(GameObject):
    def __init__(self, x, y, id, layer=Layer.MAIN):
        super().__init__(x, y, id, layer)
        self.color = self.get_color()
        self.contains = None

    def get_color(self):
        if self.id == 1: return (255, 215, 0)   # Question Block
        if self.id == 2: return (165, 42, 42)   # Brick
        if self.id == 3: return (192, 192, 192) # Iron
        if self.id == 4: return (255, 100, 100) # Note
        return (100, 100, 100)
    
    def draw(self, surface, camera, selected=False):
        super().draw(surface, camera, selected)
        # Draw question mark for ID 1
        if self.id == 1:
            screen_pos = camera.world_to_screen((self.x, self.y))
            if camera.zoom > 0.5:
                txt = font_small.render("?", True, BLACK)
                surface.blit(txt, (screen_pos[0] + 10 * camera.zoom, screen_pos[1] + 5 * camera.zoom))

class NPC(GameObject):
    def __init__(self, x, y, id):
        super().__init__(x, y, id, Layer.MAIN)
        self.height = GRID_SIZE # Standard height
        self.update_rect()
        self.color = self.get_color()
        self.vel_x = -2
        self.vel_y = 0
        self.on_ground = False

    def get_color(self):
        if self.id == 1: return (139, 0, 0)     # Goomba-ish
        if self.id == 2: return (0, 100, 0)     # Koopa-ish
        return (255, 0, 255)

    def draw(self, surface, camera, selected=False):
        screen_pos = camera.world_to_screen((self.x, self.y))
        w = int(self.width * camera.zoom)
        h = int(self.height * camera.zoom)
        rect = pygame.Rect(screen_pos[0], screen_pos[1], w, h)
        
        if self.id == 1: # Goomba - circle top
            pygame.draw.ellipse(surface, self.color, rect)
        else:
            pygame.draw.rect(surface, self.color, rect)
            
        if selected: pygame.draw.rect(surface, YELLOW, rect, 2)

    def update_physics(self, tiles, blocks):
        # Simple AI physics
        self.vel_y += GRAVITY
        
        # Move X
        self.x += self.vel_x
        self.update_rect()
        for obj in tiles + blocks:
            if obj.layer == Layer.MAIN and self.rect.colliderect(obj.rect):
                if self.vel_x > 0:
                    self.rect.right = obj.rect.left
                    self.vel_x = -self.vel_x
                elif self.vel_x < 0:
                    self.rect.left = obj.rect.right
                    self.vel_x = -self.vel_x
                self.x = self.rect.x
        
        # Move Y
        self.y += self.vel_y
        self.update_rect()
        self.on_ground = False
        for obj in tiles + blocks:
            if obj.layer == Layer.MAIN and self.rect.colliderect(obj.rect):
                if self.vel_y > 0:
                    self.rect.bottom = obj.rect.top
                    self.on_ground = True
                    self.vel_y = 0
                elif self.vel_y < 0:
                    self.rect.top = obj.rect.bottom
                    self.vel_y = 0
                self.y = self.rect.y

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = GRID_SIZE - 4
        self.height = GRID_SIZE - 2
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.facing_right = True
        self.color = RED
        
    def update(self, tiles, blocks):
        keys = pygame.key.get_pressed()
        
        # Horizontal Movement
        target_speed = 0
        accel = ACCEL
        
        if keys[pygame.K_LEFT]:
            target_speed = -MAX_RUN_SPEED if keys[pygame.K_x] else -MAX_WALK_SPEED
            self.facing_right = False
        elif keys[pygame.K_RIGHT]:
            target_speed = MAX_RUN_SPEED if keys[pygame.K_x] else MAX_WALK_SPEED
            self.facing_right = True
        else:
            target_speed = 0
            accel = FRICTION # Decelerate
            
        # Approach target speed
        if self.vel_x < target_speed:
            self.vel_x = min(self.vel_x + accel, target_speed)
        elif self.vel_x > target_speed:
            self.vel_x = max(self.vel_x - accel, target_speed)
            
        # Jump
        if keys[pygame.K_z] and self.on_ground:
            self.vel_y = JM_FORCE
            self.on_ground = False
            
        # Gravity
        grav = GRAVITY
        if keys[pygame.K_z] and self.vel_y < 0:
            grav = JM_HOLD_GRAV # Hold jump to go higher
            
        self.vel_y = min(self.vel_y + grav, MAX_FALL_SPEED)
        
        # --- Physics Loop ---
        # 1. Move X
        self.x += self.vel_x
        self.rect.x = int(self.x)
        
        # Collision X
        for obj in tiles + blocks:
            if obj.layer == Layer.MAIN and self.rect.colliderect(obj.rect):
                if self.vel_x > 0: # Hit left side of block
                    self.rect.right = obj.rect.left
                    self.x = self.rect.x
                    self.vel_x = 0
                elif self.vel_x < 0: # Hit right side of block
                    self.rect.left = obj.rect.right
                    self.x = self.rect.x
                    self.vel_x = 0
                    
        # 2. Move Y
        self.y += self.vel_y
        self.rect.y = int(self.y)
        self.on_ground = False
        
        # Collision Y
        for obj in tiles + blocks:
            if obj.layer == Layer.MAIN and self.rect.colliderect(obj.rect):
                if self.vel_y > 0: # Landing on top
                    self.rect.bottom = obj.rect.top
                    self.y = self.rect.y
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0: # Hitting head
                    self.rect.top = obj.rect.bottom
                    self.y = self.rect.y
                    self.vel_y = 0
        
        # Map Boundaries (Simple respawn if fall)
        if self.y > 2000:
            self.x = 100
            self.y = 100
            self.vel_y = 0
            
    def draw(self, surface, camera):
        screen_pos = camera.world_to_screen((self.x, self.y))
        w = int(self.width * camera.zoom)
        h = int(self.height * camera.zoom)
        
        rect = pygame.Rect(screen_pos[0], screen_pos[1], w, h)
        pygame.draw.rect(surface, self.color, rect)
        
        # Eyes to show direction
        eye_offset = 5 * camera.zoom if self.facing_right else 0
        eye_rect = pygame.Rect(rect.x + eye_offset + 5*camera.zoom, rect.y + 5*camera.zoom, 4*camera.zoom, 8*camera.zoom)
        pygame.draw.rect(surface, BLACK, eye_rect)

class Editor:
    def __init__(self):
        self.state = GameState.EDITOR
        self.tiles = []
        self.blocks = []
        self.npcs = []
        self.level_settings = {"width": 3200, "height": 1200, "start_pos": (100, 300)}
        
        self.camera = Camera()
        self.mode = EditorMode.TILE
        self.selected_id = 1
        self.selected_layer = Layer.MAIN
        
        self.player = None
        self.play_objects = {} # copy of objects for gameplay
        
    def add_object(self, pos):
        grid_x = (pos[0] // GRID_SIZE) * GRID_SIZE
        grid_y = (pos[1] // GRID_SIZE) * GRID_SIZE
        
        # Check occupancy
        for t in self.tiles + self.blocks:
            if t.x == grid_x and t.y == grid_y and t.layer == self.selected_layer:
                return

        if self.mode == EditorMode.TILE:
            self.tiles.append(Tile(grid_x, grid_y, self.selected_id, self.selected_layer))
        elif self.mode == EditorMode.BLOCK:
            self.blocks.append(Block(grid_x, grid_y, self.selected_id, self.selected_layer))
        elif self.mode == EditorMode.NPC:
            self.npcs.append(NPC(grid_x, grid_y, self.selected_id))

    def remove_object(self, pos):
        world_pos = self.camera.screen_to_world(pos)
        r = pygame.Rect(world_pos[0], world_pos[1], 1, 1)
        
        # Reverse lists to click top objects first
        for l in [self.npcs, self.blocks, self.tiles]:
            for obj in reversed(l):
                if obj.rect.collidepoint(world_pos):
                    l.remove(obj)
                    return

    def toggle_play(self):
        if self.state == GameState.EDITOR:
            # Switch to Play
            self.state = GameState.PLAY
            # Deep copy objects so gameplay doesn't mess up editor
            self.play_objects = {
                'tiles': copy.deepcopy(self.tiles),
                'blocks': copy.deepcopy(self.blocks),
                'npcs': copy.deepcopy(self.npcs)
            }
            start_x, start_y = self.level_settings['start_pos']
            self.player = Player(start_x, start_y)
            self.camera.target = self.player
        else:
            # Switch to Editor
            self.state = GameState.EDITOR
            self.camera.target = None
            self.player = None
            
    def update(self):
        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pressed()
        mpos = pygame.mouse.get_pos()
        
        # Global Toggle
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p: self.toggle_play()
                if event.key == pygame.K_ESCAPE and self.state == GameState.PLAY: self.toggle_play()
                
                # Editor Hotkeys
                if self.state == GameState.EDITOR:
                    if event.key == pygame.K_1: self.mode = EditorMode.TILE
                    if event.key == pygame.K_2: self.mode = EditorMode.BLOCK
                    if event.key == pygame.K_3: self.mode = EditorMode.NPC
                    if event.key == pygame.K_q: self.selected_id = max(1, self.selected_id - 1)
                    if event.key == pygame.K_e: self.selected_id += 1
                    # Save/Load
                    if event.key == pygame.K_s and (keys[pygame.K_LCTRL]): self.save_level()
                    if event.key == pygame.K_l and (keys[pygame.K_LCTRL]): self.load_level()
            
            if event.type == pygame.MOUSEWHEEL:
                if event.y > 0: self.camera.zoom = min(2.0, self.camera.zoom + 0.1)
                else: self.camera.zoom = max(0.5, self.camera.zoom - 0.1)

        self.camera.update(keys, mouse, mpos)

        if self.state == GameState.EDITOR:
            # Editor Logic
            if mouse[0] and mpos[1] < SCREEN_HEIGHT - TOOLBAR_HEIGHT: # Left Click
                w_pos = self.camera.screen_to_world(mpos)
                self.add_object(w_pos)
            if mouse[1] and mpos[1] < SCREEN_HEIGHT - TOOLBAR_HEIGHT: # Middle Click (Delete)
                self.remove_object(mpos)
                
        elif self.state == GameState.PLAY:
            # Game Logic
            if self.player:
                self.player.update(self.play_objects['tiles'], self.play_objects['blocks'])
            
            for npc in self.play_objects['npcs']:
                npc.update_physics(self.play_objects['tiles'], self.play_objects['blocks'])

    def draw(self):
        screen.fill(SKY_BLUE)
        
        # Determine what to draw based on state
        draw_tiles = self.tiles if self.state == GameState.EDITOR else self.play_objects['tiles']
        draw_blocks = self.blocks if self.state == GameState.EDITOR else self.play_objects['blocks']
        draw_npcs = self.npcs if self.state == GameState.EDITOR else self.play_objects['npcs']
        
        # Draw World
        for t in draw_tiles: t.draw(screen, self.camera)
        for b in draw_blocks: b.draw(screen, self.camera)
        for n in draw_npcs: n.draw(screen, self.camera)
        
        # Draw Player
        if self.state == GameState.PLAY and self.player:
            self.player.draw(screen, self.camera)
            
        # Draw Start Position in Editor
        if self.state == GameState.EDITOR:
            sx, sy = self.level_settings['start_pos']
            spos = self.camera.world_to_screen((sx, sy))
            pygame.draw.rect(screen, GREEN, (spos[0], spos[1], GRID_SIZE*self.camera.zoom, GRID_SIZE*2*self.camera.zoom), 2)
            
        # UI
        if self.state == GameState.EDITOR:
            self.draw_editor_ui()
        else:
            # Simple HUD
            txt = font_medium.render("PLAY MODE - [P] to Edit", True, WHITE)
            screen.blit(txt, (20, 20))

    def draw_editor_ui(self):
        # Background
        pygame.draw.rect(screen, DARK_GRAY, (0, SCREEN_HEIGHT - TOOLBAR_HEIGHT, SCREEN_WIDTH, TOOLBAR_HEIGHT))
        pygame.draw.line(screen, LIGHT_GRAY, (0, SCREEN_HEIGHT - TOOLBAR_HEIGHT), (SCREEN_WIDTH, SCREEN_HEIGHT - TOOLBAR_HEIGHT), 2)
        
        # Info
        info = f"Mode: {self.mode.name} | ID: {self.selected_id} | Layer: {self.selected_layer.name}"
        screen.blit(font_medium.render(info, True, WHITE), (10, SCREEN_HEIGHT - TOOLBAR_HEIGHT + 10))
        screen.blit(font_small.render("Controls: WASD=Cam, Left=Place, Mid=Del, Right=Pan, P=Play, Q/E=ID+/-, 1-3=Tools", True, LIGHT_GRAY), (10, SCREEN_HEIGHT - 20))
        
        # Palette Preview
        p_x, p_y = 20, SCREEN_HEIGHT - TOOLBAR_HEIGHT + 40
        for i in range(1, 6):
            rect = pygame.Rect(p_x + (i-1)*50, p_y, 40, 40)
            
            # Draw preview based on mode
            if self.mode == EditorMode.TILE:
                c = Tile(0,0,i).get_color()
                pygame.draw.rect(screen, c, rect)
            elif self.mode == EditorMode.BLOCK:
                c = Block(0,0,i).get_color()
                pygame.draw.rect(screen, c, rect)
            elif self.mode == EditorMode.NPC:
                c = NPC(0,0,i).get_color()
                pygame.draw.rect(screen, c, rect)
            
            if i == self.selected_id:
                pygame.draw.rect(screen, YELLOW, rect, 3)
            else:
                pygame.draw.rect(screen, WHITE, rect, 1)
                
            num = font_small.render(str(i), True, WHITE)
            screen.blit(num, (rect.x + 2, rect.y + 2))

    def save_level(self):
        data = {
            "tiles": [t.to_dict() for t in self.tiles],
            "blocks": [b.to_dict() for b in self.blocks],
            "npcs": [n.to_dict() for n in self.npcs],
            "settings": self.level_settings
        }
        with open("level.json", "w") as f:
            json.dump(data, f)
        print("Level Saved!")

    def load_level(self):
        if not os.path.exists("level.json"): return
        with open("level.json", "r") as f:
            data = json.load(f)
            self.tiles = [Tile(d['x'], d['y'], d['id'], Layer(d['layer'])) for d in data['tiles']]
            self.blocks = [Block(d['x'], d['y'], d['id'], Layer(d['layer'])) for d in data['blocks']]
            self.npcs = [NPC(d['x'], d['y'], d['id']) for d in data['npcs']]
            self.level_settings = data.get("settings", self.level_settings)
        print("Level Loaded!")

# --- Main Loop ---
if __name__ == "__main__":
    editor = Editor()
    
    # Pre-populate some ground
    for i in range(0, 30):
        editor.tiles.append(Tile(i * GRID_SIZE, 10 * GRID_SIZE, 1))
    editor.blocks.append(Block(5 * GRID_SIZE, 7 * GRID_SIZE, 1))
    editor.blocks.append(Block(6 * GRID_SIZE, 7 * GRID_SIZE, 2))
    editor.blocks.append(Block(7 * GRID_SIZE, 7 * GRID_SIZE, 2))
    editor.blocks.append(Block(8 * GRID_SIZE, 7 * GRID_SIZE, 1))
    editor.npcs.append(NPC(12 * GRID_SIZE, 9 * GRID_SIZE, 1))

    while True:
        editor.update()
        editor.draw()
        pygame.display.flip()
        clock.tick(FPS)
